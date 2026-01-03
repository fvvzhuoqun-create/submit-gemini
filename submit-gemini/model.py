import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool
from torch_geometric.data import Batch
import transformers
from transformers import AutoModel, AutoTokenizer


class FocalLoss(nn.Module):
    """Focal Loss用于处理类别不平衡"""

    def __init__(self, alpha=1, gamma=2, reduction='mean'):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss

        if self.reduction == 'mean':
            return torch.mean(focal_loss)
        elif self.reduction == 'sum':
            return torch.sum(focal_loss)
        else:
            return focal_loss


class DrugGCN(nn.Module):
    def __init__(self, in_feats, hidden_size, out_feats, dropout=0.4):
        super(DrugGCN, self).__init__()
        self.conv1 = GCNConv(in_feats, hidden_size)
        self.conv2 = GCNConv(hidden_size, hidden_size)
        self.conv3 = GCNConv(hidden_size, out_feats)
        self.dropout = nn.Dropout(dropout)
        self.batch_norm1 = nn.BatchNorm1d(hidden_size)
        self.batch_norm2 = nn.BatchNorm1d(hidden_size)

        # 残差连接
        self.residual = nn.Linear(in_feats, out_feats) if in_feats != out_feats else nn.Identity()

    def forward(self, x, edge_index):
        # 残差连接
        residual = self.residual(x) if hasattr(self, 'residual') else 0

        x = F.relu(self.batch_norm1(self.conv1(x, edge_index)))
        x = self.dropout(x)
        x = F.relu(self.batch_norm2(self.conv2(x, edge_index)))
        x = self.dropout(x)
        x = self.conv3(x, edge_index)

        # 添加残差连接
        if residual is not None and torch.any(residual != 0):
            x = x + residual[:x.size(0)]  # 确保维度匹配

        return x


class CrossModalAttention(nn.Module):
    """交叉注意力机制用于特征融合"""

    def __init__(self, dim, num_heads=8, dropout=0.3):
        super().__init__()
        self.num_heads = num_heads
        self.dim = dim
        self.head_dim = dim // num_heads

        self.q_linear = nn.Linear(dim, dim)
        self.k_linear = nn.Linear(dim, dim)
        self.v_linear = nn.Linear(dim, dim)
        self.out_linear = nn.Linear(dim, dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, query, key, value):
        batch_size = query.size(0)

        # 线性投影
        Q = self.q_linear(query).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.k_linear(key).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.v_linear(value).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)

        # 计算注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.head_dim ** 0.5)
        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)

        # 应用注意力权重
        attn_output = torch.matmul(attn_weights, V)
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, -1, self.dim)

        return self.out_linear(attn_output.squeeze(1))


def create_drug_synergy_prompt(drug1_smiles, drug2_smiles, cell_pca_features):
    """创建药物协同性预测的提示词"""
    prompt = f"""
作为药物协同性预测专家，请分析以下药物组合：
药物1 SMILES: {drug1_smiles}
药物2 SMILES: {drug2_smiles}
细胞系PCA特征（64维）: {cell_pca_features}

请基于这些信息，预测这两种药物在该细胞系中的协同作用。
考虑以下因素：
- 药物化学结构的互补性
- 靶点通路的潜在交互
- 细胞系特征对药物响应的影响

输出应为协同性概率分析。
"""
    return prompt


class QwenEnhancedDrugSynergyModel(nn.Module):
    def __init__(self, gcn_config, num_classes=2, qwen_model_name=r"C:\Users\fzq11\models\Qwen2-1.5B"):
        super().__init__()

        # 原有GCN模型
        self.gcn_drug1 = DrugGCN(**gcn_config)
        self.gcn_drug2 = DrugGCN(**gcn_config)

        # Qwen2语言模型 - 使用本地缓存
        print(f"正在加载Qwen2模型: {qwen_model_name}")
        try:
            self.qwen = AutoModel.from_pretrained(
                qwen_model_name,
                local_files_only=True,
                trust_remote_code=True
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                qwen_model_name,
                local_files_only=True,
                trust_remote_code=True
            )
            print("✓ Qwen2模型加载成功！")
        except Exception as e:
            print(f"✗ Qwen2模型加载失败: {e}")
            print("正在尝试在线下载...")
            # 如果本地没有，尝试在线下载
            try:
                self.qwen = AutoModel.from_pretrained(
                    qwen_model_name,
                    trust_remote_code=True
                )
                self.tokenizer = AutoTokenizer.from_pretrained(
                    qwen_model_name,
                    trust_remote_code=True
                )
                print("✓ Qwen2模型在线下载成功！")
            except Exception as e2:
                print(f"✗ 所有加载方式都失败: {e2}")
                raise

        # 如果tokenizer没有pad_token，设置为eos_token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # 冻结Qwen的大部分层，只微调后面几层
        total_params = len(list(self.qwen.parameters()))
        trainable_layers = 8  # 稍微增加可训练层数
        for i, param in enumerate(self.qwen.parameters()):
            if i < total_params - trainable_layers:
                param.requires_grad = False

        # 文本特征投影层
        qwen_hidden_size = self.qwen.config.hidden_size
        print(f"Qwen2隐藏层维度: {qwen_hidden_size}")

        self.text_projection = nn.Sequential(
            nn.Linear(qwen_hidden_size, 512),
            nn.LayerNorm(512),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256)
        )

        # 计算总特征维度
        gcn_out = gcn_config['out_feats']
        target_dim = 560  # 假设目标特征维度为560
        cell_dim = 64  # 假设细胞特征维度为64
        total_structural_features = gcn_out * 2 + target_dim * 2 + cell_dim
        total_multimodal_features = total_structural_features + 256  # 文本特征维度

        # 多模态融合层
        self.multimodal_fusion = nn.Sequential(
            nn.Linear(total_multimodal_features, 1024),
            nn.LayerNorm(1024),
            nn.GELU(),
            nn.Dropout(0.4),
            nn.Linear(1024, 512),
            nn.LayerNorm(512),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256)
        )

        # 交叉注意力机制
        self.cross_attention = CrossModalAttention(dim=256, num_heads=8, dropout=0.2)

        # 分类器
        self.classifier = nn.Sequential(
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )

        # 初始化权重
        self.apply(self._init_weights)
        print(f"Qwen增强模型初始化完成，可训练参数: {sum(p.numel() for p in self.parameters() if p.requires_grad):,}")

    def _init_weights(self, module):
        """权重初始化"""
        if isinstance(module, nn.Linear):
            torch.nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                torch.nn.init.constant_(module.bias, 0)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.constant_(module.bias, 0)
            torch.nn.init.constant_(module.weight, 1.0)

    def get_text_features(self, drug1_smiles, drug2_smiles, cell_expr):
        """使用Qwen提取文本特征，增强稳定性"""
        batch_size = len(drug1_smiles)

        try:
            prompts = []

            # 为每个样本创建提示词
            for i in range(batch_size):
                # 将细胞特征转换为字符串表示（取前10个值作为示例）
                cell_features_str = ", ".join([f"{x:.3f}" for x in cell_expr[i][:10].cpu().numpy()])
                prompt = create_drug_synergy_prompt(
                    drug1_smiles[i],
                    drug2_smiles[i],
                    cell_features_str
                )
                prompts.append(prompt)

            # Tokenize
            inputs = self.tokenizer(
                prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )

            # 移动到模型所在设备
            device = next(self.qwen.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}

            # 前向传播
            with torch.no_grad():  # Qwen大部分层是冻结的
                outputs = self.qwen(**inputs)

            # 使用[CLS] token或最后一层的平均池化
            if hasattr(outputs, 'last_hidden_state'):
                text_features = outputs.last_hidden_state.mean(dim=1)  # 平均池化
            else:
                text_features = outputs.pooler_output

            return self.text_projection(text_features)

        except Exception as e:
            print(f"警告: 文本特征提取失败: {e}, 使用随机特征")
            # 返回随机特征作为降级方案
            return torch.randn(batch_size, 256, device=next(self.parameters()).device)

    def forward(self, batch_data):
        device = next(self.parameters()).device

        # 原有的GCN特征提取
        g1 = batch_data['graph1']
        g2 = batch_data['graph2']

        d1 = self.gcn_drug1(g1.x.to(device), g1.edge_index.to(device))
        d1 = global_mean_pool(d1, g1.batch.to(device))

        d2 = self.gcn_drug2(g2.x.to(device), g2.edge_index.to(device))
        d2 = global_mean_pool(d2, g2.batch.to(device))

        target1 = batch_data['target1'].to(device)
        target2 = batch_data['target2'].to(device)
        cell_expr = batch_data['cell_expr'].to(device)

        # 获取文本特征
        drug1_smiles = batch_data['drug1_smiles']
        drug2_smiles = batch_data['drug2_smiles']
        text_features = self.get_text_features(drug1_smiles, drug2_smiles, cell_expr)

        # 结构特征融合
        structural_features = torch.cat([d1, d2, target1, target2, cell_expr], dim=-1)

        # 多模态特征融合
        multimodal_input = torch.cat([structural_features, text_features], dim=-1)
        fused_features = self.multimodal_fusion(multimodal_input)

        # 使用自注意力进一步提炼特征
        refined_feat = self.cross_attention(
            fused_features.unsqueeze(1),
            fused_features.unsqueeze(1),
            fused_features.unsqueeze(1)
        )

        # 分类
        logits = self.classifier(refined_feat)

        return logits


class OptimizedDrugSynergyModel(nn.Module):
    """优化后的药物协同预测模型（原有版本）"""

    def __init__(self, gcn_config, num_classes=2):
        super().__init__()

        # GCN网络
        self.gcn_drug1 = DrugGCN(**gcn_config)
        self.gcn_drug2 = DrugGCN(**gcn_config)

        # 计算总特征维度
        gcn_out = gcn_config['out_feats']
        target_dim = 560  # 假设目标特征维度为560
        cell_dim = 64  # 假设细胞特征维度为64
        total_molecular_features = gcn_out * 2 + target_dim * 2 + cell_dim

        # 特征融合层
        self.fusion_layer = nn.Sequential(
            nn.Linear(total_molecular_features, 1024),
            nn.LayerNorm(1024),
            nn.GELU(),
            nn.Dropout(0.4),
            nn.Linear(1024, 512),
            nn.LayerNorm(512),
            nn.GELU(),
            nn.Dropout(0.4),
            nn.Linear(512, 256)
        )

        # 交叉注意力机制
        self.cross_attention = CrossModalAttention(dim=256, num_heads=8, dropout=0.2)

        # 分类头
        self.classifier = nn.Sequential(
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(0.4),
            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )

        # 初始化权重
        self.apply(self._init_weights)

    def _init_weights(self, module):
        """权重初始化"""
        if isinstance(module, nn.Linear):
            torch.nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                torch.nn.init.constant_(module.bias, 0)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.constant_(module.bias, 0)
            torch.nn.init.constant_(module.weight, 1.0)

    def forward(self, batch_data):
        device = next(self.parameters()).device
        batch_size = batch_data['labels'].shape[0]

        # GCN前向传播
        g1 = batch_data['graph1']
        g2 = batch_data['graph2']

        d1 = self.gcn_drug1(g1.x.to(device), g1.edge_index.to(device))
        d1 = global_mean_pool(d1, g1.batch.to(device))

        d2 = self.gcn_drug2(g2.x.to(device), g2.edge_index.to(device))
        d2 = global_mean_pool(d2, g2.batch.to(device))

        target1 = batch_data['target1'].to(device)
        target2 = batch_data['target2'].to(device)
        cell_expr = batch_data['cell_expr'].to(device)

        # 特征融合
        molecular_feat = torch.cat([d1, d2, target1, target2, cell_expr], dim=-1)
        fused_feat = self.fusion_layer(molecular_feat)  # 输出维度: 256

        # 使用自注意力进一步提炼特征
        refined_feat = self.cross_attention(
            fused_feat.unsqueeze(1),
            fused_feat.unsqueeze(1),
            fused_feat.unsqueeze(1)
        )

        # 分类
        logits = self.classifier(refined_feat)

        return logits


class SimpleDrugSynergyModel(nn.Module):
    """简化模型用于快速实验和调试"""

    def __init__(self, gcn_config, num_classes=2):
        super().__init__()
        self.gcn_drug1 = DrugGCN(**gcn_config)
        self.gcn_drug2 = DrugGCN(**gcn_config)

        # 计算总特征维度
        total_features = gcn_config['out_feats'] * 2 + 560 * 2 + 64

        # 简化但有效的分类器
        self.classifier = nn.Sequential(
            nn.Linear(total_features, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )

    def forward(self, batch_data):
        device = next(self.parameters()).device

        # GCN前向传播
        g1, g2 = batch_data['graph1'], batch_data['graph2']
        d1 = self.gcn_drug1(g1.x.to(device), g1.edge_index.to(device))
        d1 = global_mean_pool(d1, g1.batch.to(device))

        d2 = self.gcn_drug2(g2.x.to(device), g2.edge_index.to(device))
        d2 = global_mean_pool(d2, g2.batch.to(device))

        # 特征融合
        target1 = batch_data['target1'].to(device)
        target2 = batch_data['target2'].to(device)
        cell_expr = batch_data['cell_expr'].to(device)

        fused_feat = torch.cat([d1, d2, target1, target2, cell_expr], dim=-1)
        logits = self.classifier(fused_feat)

        return logits