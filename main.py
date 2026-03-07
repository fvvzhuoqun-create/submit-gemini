import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATv2Conv, global_mean_pool
from transformers import AutoModel, AutoTokenizer

class FocalLoss(nn.Module):
    # 修改：将 alpha 替换为 weight 接收类别权重
    def __init__(self, weight=None, gamma=2.0, reduction='mean'):
        super().__init__()
        self.weight = weight
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        # 修改：将 weight 参数传递给 F.cross_entropy，实现类别加权
        ce_loss = F.cross_entropy(inputs, targets, weight=self.weight, reduction='none')
        pt = torch.exp(-ce_loss)
        # 修改：移除外层乘以标量 alpha 的逻辑，权重已在上面生效
        focal_loss = ((1 - pt) ** self.gamma) * ce_loss
        
        if self.reduction == 'mean':
            return torch.mean(focal_loss)
        elif self.reduction == 'sum':
            return torch.sum(focal_loss)
        else:
            return focal_loss

class DrugGAT(nn.Module):
    """
    使用 GATv2 的图注意力网络提取器，提取分子图级别的空间结构信息
    """
    def __init__(self, in_feats, hidden_size, out_feats, dropout=0.2, heads=4):
        super(DrugGAT, self).__init__()
        self.dropout = dropout

        self.conv1 = GATv2Conv(in_feats, hidden_size, heads=heads, dropout=dropout, concat=True)
        self.batch_norm1 = nn.BatchNorm1d(hidden_size * heads)

        self.conv2 = GATv2Conv(hidden_size * heads, hidden_size, heads=heads, dropout=dropout, concat=True)
        self.batch_norm2 = nn.BatchNorm1d(hidden_size * heads)

        self.conv3 = GATv2Conv(hidden_size * heads, out_feats, heads=1, concat=False, dropout=dropout)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = self.batch_norm1(x)
        x = F.elu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)

        x = self.conv2(x, edge_index)
        x = self.batch_norm2(x)
        x = F.elu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)

        x = self.conv3(x, edge_index)
        return x

class QwenEnhancedDrugSynergyModel(nn.Module):
    """
    将多模态连续特征全部转化为 LLM 的 "Soft Tokens"，利用 Qwen 进行深层特征交互与分类
    """
    def __init__(self, gcn_config, num_classes=2, target_dim=560, cell_dim=1024, physchem_dim=7,
                 qwen_model_name="Qwen/Qwen2.5-3B-Instruct"):
        super().__init__()

        # 1. 药物分子图特征提取器
        self.gcn_drug1 = DrugGAT(**gcn_config, heads=4)
        self.gcn_drug2 = DrugGAT(**gcn_config, heads=4)

        print(f"正在加载Qwen模型: {qwen_model_name}")
        try:
            # 禁用告警和输出设置，直接加载核心模型
            self.qwen = AutoModel.from_pretrained(qwen_model_name, trust_remote_code=True)
            self.tokenizer = AutoTokenizer.from_pretrained(qwen_model_name, trust_remote_code=True)
        except Exception as e:
            print(f"模型加载错误: {e}")
            raise e

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # 获取 Qwen 隐藏层维度 (例如 3072 或 4096，视具体模型参数量而定)
        qwen_hidden_size = self.qwen.config.hidden_size
        gcn_out = gcn_config['out_feats']

        # 2. 特征 Token 投影层 (Feature-to-Token Projections)
        # 将各种维度的连续特征映射到与 Qwen 内部 Embedding 相同的维度
        self.proj_gcn = nn.Linear(gcn_out, qwen_hidden_size)
        self.proj_target = nn.Linear(target_dim, qwen_hidden_size)
        self.proj_physchem = nn.Linear(physchem_dim, qwen_hidden_size)
        self.proj_cell = nn.Linear(cell_dim, qwen_hidden_size)

        # 冻结 Qwen 大部分参数，仅微调最后 12 层注意力块 (可调节参数以控制显存)
        total_params = len(list(self.qwen.parameters()))
        for i, param in enumerate(self.qwen.parameters()):
            if i < total_params - 12:
                param.requires_grad = False

        # 3. 最终池化特征的 MLP 分类器
        self.classifier = nn.Sequential(
            nn.Linear(qwen_hidden_size, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes)
        )

    def forward(self, batch_data):
        device = next(self.parameters()).device

        # --- 第1步：提取 GCN 分子图连续特征 ---
        g1, g2 = batch_data['graph1'], batch_data['graph2']
        d1 = self.gcn_drug1(g1.x.to(device), g1.edge_index.to(device))
        d1 = global_mean_pool(d1, g1.batch.to(device))  # [Batch, gcn_out]
        d2 = self.gcn_drug2(g2.x.to(device), g2.edge_index.to(device))
        d2 = global_mean_pool(d2, g2.batch.to(device))  # [Batch, gcn_out]

        # 提取其他模态连续特征
        target1 = batch_data['target1'].to(device)      # [Batch, target_dim]
        target2 = batch_data['target2'].to(device)      # [Batch, target_dim]
        physchem1 = batch_data['physchem1'].to(device)  # [Batch, physchem_dim]
        physchem2 = batch_data['physchem2'].to(device)  # [Batch, physchem_dim]
        cell_expr = batch_data['cell_expr'].to(device)  # [Batch, cell_dim]

        # --- 第2步：将多模态特征投影为 Qwen 认识的 "Soft Tokens" ---
        # unsqueeze(1) 作用是添加一个长度为 1 的序列维度 (Sequence Length = 1)
        token_d1 = self.proj_gcn(d1).unsqueeze(1)               # [Batch, 1, Hidden_Size]
        token_d2 = self.proj_gcn(d2).unsqueeze(1)               # [Batch, 1, Hidden_Size]
        token_t1 = self.proj_target(target1).unsqueeze(1)       # [Batch, 1, Hidden_Size]
        token_t2 = self.proj_target(target2).unsqueeze(1)       # [Batch, 1, Hidden_Size]
        token_p1 = self.proj_physchem(physchem1).unsqueeze(1)   # [Batch, 1, Hidden_Size]
        token_p2 = self.proj_physchem(physchem2).unsqueeze(1)   # [Batch, 1, Hidden_Size]
        token_c  = self.proj_cell(cell_expr).unsqueeze(1)       # [Batch, 1, Hidden_Size]

        # --- 第3步：拼接形成 Token 序列 ---
        # 此时的输入相当于一篇只有 7 个 "词" 组成的序列
        inputs_embeds = torch.cat([
            token_d1, token_d2, token_t1, token_t2, token_p1, token_p2, token_c
        ], dim=1)  # 最终形状：[Batch, 7, Hidden_Size]

        # --- 第4步：送入 Qwen 进行基于自注意力的深度特征对齐与交互 ---
        # 绕过词表嵌入层 (Embedding)，直接输入向量序列
        qwen_outputs = self.qwen(inputs_embeds=inputs_embeds)
        
        # 获取 LLM 最后一层的输出隐藏状态：[Batch, 7, Hidden_Size]
        last_hidden_state = qwen_outputs.last_hidden_state

        # 对 7 个 Token 的最终状态进行平均池化，融合为单向量
        pooled_output = last_hidden_state.mean(dim=1)  # [Batch, Hidden_Size]

        # --- 第5步：经过 MLP 分类器进行预测 ---
        logits = self.classifier(pooled_output)
        
        return logits