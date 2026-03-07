import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATv2Conv, global_mean_pool
from transformers import AutoModel, AutoTokenizer


class FocalLoss(nn.Module):
    def __init__(self, weight=None, gamma=2.0, reduction='mean'):
        super().__init__()
        # 使用 register_buffer 确保权重随模型移动到同一设备
        self.register_buffer('weight', weight)
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, weight=self.weight, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = ((1 - pt) ** self.gamma) * ce_loss
        return focal_loss.mean() if self.reduction == 'mean' else focal_loss.sum()


class DrugGAT(nn.Module):
    def __init__(self, in_feats, hidden_size, out_feats, dropout=0.2, heads=4):
        super(DrugGAT, self).__init__()
        self.conv1 = GATv2Conv(in_feats, hidden_size, heads=heads, dropout=dropout, concat=True)
        self.batch_norm1 = nn.BatchNorm1d(hidden_size * heads)
        self.conv2 = GATv2Conv(hidden_size * heads, hidden_size, heads=heads, dropout=dropout, concat=True)
        self.batch_norm2 = nn.BatchNorm1d(hidden_size * heads)
        self.conv3 = GATv2Conv(hidden_size * heads, out_feats, heads=1, concat=False, dropout=dropout)

    def forward(self, x, edge_index):
        x = F.dropout(F.elu(self.batch_norm1(self.conv1(x, edge_index))), p=0.2, training=self.training)
        x = F.dropout(F.elu(self.batch_norm2(self.conv2(x, edge_index))), p=0.2, training=self.training)
        return self.conv3(x, edge_index)


class QwenEnhancedDrugSynergyModel(nn.Module):
    def __init__(self, gcn_config, num_classes=2, target_dim=560, cell_dim=1024, physchem_dim=7,
                 qwen_model_name="Qwen/Qwen2.5-3B-Instruct"):
        super().__init__()
        self.gcn_drug1 = DrugGAT(**gcn_config)
        self.gcn_drug2 = DrugGAT(**gcn_config)

        # 【优化项 3】：开启 bfloat16 半精度加载，激活 A40 的 Tensor Core 加速计算
        self.qwen = AutoModel.from_pretrained(
            qwen_model_name, 
            trust_remote_code=True,
            torch_dtype=torch.bfloat16
        )
        self.tokenizer = AutoTokenizer.from_pretrained(qwen_model_name, trust_remote_code=True)
        if self.tokenizer.pad_token is None: self.tokenizer.pad_token = self.tokenizer.eos_token

        # 【修复警告1】：手动关闭缓存机制
        self.qwen.config.use_cache = False

        # 【优化项 4】：A40 显存充足，注释掉梯度检查点以换取约 30% 的前向传播速度提升
        # self.qwen.gradient_checkpointing_enable()

        # 【修复警告2】：强制输入层要求梯度，防止 PyTorch 报错
        self.qwen.enable_input_require_grads()

        # 冻结部分参数，仅微调最后 12 层以平衡效果与显存
        for param in self.qwen.parameters(): param.requires_grad = False
        for param in list(self.qwen.parameters())[-120:]: param.requires_grad = True

        q_hid = self.qwen.config.hidden_size
        # 特征投影层 (确保将投影层转换为 bfloat16 以匹配 Qwen)
        self.proj_gcn = nn.Linear(gcn_config['out_feats'], q_hid, dtype=torch.bfloat16)
        self.proj_target = nn.Linear(target_dim, q_hid, dtype=torch.bfloat16)
        self.proj_physchem = nn.Linear(physchem_dim, q_hid, dtype=torch.bfloat16)
        self.proj_cell = nn.Linear(cell_dim, q_hid, dtype=torch.bfloat16)

        self.classifier = nn.Sequential(
            nn.Linear(q_hid, 256, dtype=torch.bfloat16), nn.LayerNorm(256, dtype=torch.bfloat16), nn.GELU(), nn.Dropout(0.3),
            nn.Linear(256, num_classes, dtype=torch.bfloat16)
        )

    def forward(self, batch_data):
        device = next(self.parameters()).device

        # 1. 提取图结构特征
        d1 = global_mean_pool(self.gcn_drug1(batch_data['graph1'].x, batch_data['graph1'].edge_index),
                              batch_data['graph1'].batch)
        d2 = global_mean_pool(self.gcn_drug2(batch_data['graph2'].x, batch_data['graph2'].edge_index),
                              batch_data['graph2'].batch)

        # 将图特征转为 bfloat16 以匹配 Qwen 精度
        d1 = d1.to(torch.bfloat16)
        d2 = d2.to(torch.bfloat16)
        
        # 将外部特征转为 bfloat16
        t1 = batch_data['target1'].to(torch.bfloat16)
        t2 = batch_data['target2'].to(torch.bfloat16)
        p1 = batch_data['physchem1'].to(torch.bfloat16)
        p2 = batch_data['physchem2'].to(torch.bfloat16)
        ce = batch_data['cell_expr'].to(torch.bfloat16)

        # 2. 构造 Soft Tokens (7个连续特征)
        soft_tokens = torch.stack([
            self.proj_gcn(d1), self.proj_gcn(d2),
            self.proj_target(t1), self.proj_target(t2),
            self.proj_physchem(p1), self.proj_physchem(p2),
            self.proj_cell(ce)
        ], dim=1)  # [Batch, 7, Hidden]

        # 3. 提取文本 Token 的基础 Embedding（【关键提速点】：不跑整个模型，瞬间完成）
        smiles_text = [f"Drug1: {s1}, Drug2: {s2}" for s1, s2 in
                       zip(batch_data['drug1_smiles'], batch_data['drug2_smiles'])]
        text_inputs = self.tokenizer(smiles_text, return_tensors="pt", padding=True, truncation=True,
                                     max_length=128).to(device)
        text_embeds = self.qwen.get_input_embeddings()(text_inputs.input_ids)

        # 4. 拼接输入 Qwen (Soft Tokens + Text Tokens)
        full_embeds = torch.cat([soft_tokens, text_embeds], dim=1)

        # 5. 生成对应的注意力掩码 Attention Mask (7个软Token都是有效的，设为1)
        batch_size = full_embeds.shape[0]
        soft_tokens_mask = torch.ones((batch_size, 7), dtype=torch.long, device=device)
        full_attention_mask = torch.cat([soft_tokens_mask, text_inputs.attention_mask], dim=1)

        # 6. 大模型只在这里真正前向传播一次！
        outputs = self.qwen(inputs_embeds=full_embeds, attention_mask=full_attention_mask).last_hidden_state

        # 平均池化后分类
        return self.classifier(outputs.mean(dim=1)).to(torch.float32) # 最后转回 float32 计算 Loss