import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool
from transformers import AutoModel, AutoTokenizer


# 保持其他类 (FocalLoss, DrugGCN, CrossModalAttention) 不变...
# ... (此处省略 FocalLoss, DrugGCN, CrossModalAttention 定义，保持原样) ...

class FocalLoss(nn.Module):
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

    def forward(self, x, edge_index):
        x = F.relu(self.batch_norm1(self.conv1(x, edge_index)))
        x = self.dropout(x)
        x = F.relu(self.batch_norm2(self.conv2(x, edge_index)))
        x = self.dropout(x)
        x = self.conv3(x, edge_index)
        return x


class CrossModalAttention(nn.Module):
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
        Q = self.q_linear(query).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.k_linear(key).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.v_linear(value).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.head_dim ** 0.5)
        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)
        attn_output = torch.matmul(attn_weights, V)
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, -1, self.dim)
        return self.out_linear(attn_output.squeeze(1))


class QwenEnhancedDrugSynergyModel(nn.Module):
    def __init__(self, gcn_config, num_classes=2, target_dim=560, cell_dim=1024, physchem_dim=7,
                 qwen_model_name="Qwen/Qwen2-1.5B"):
        super().__init__()

        # GCN模型
        self.gcn_drug1 = DrugGCN(**gcn_config)
        self.gcn_drug2 = DrugGCN(**gcn_config)

        # 语言模型 (保持原逻辑)
        print(f"正在加载Qwen2模型: {qwen_model_name}")
        try:
            self.qwen = AutoModel.from_pretrained(qwen_model_name, trust_remote_code=True)
            self.tokenizer = AutoTokenizer.from_pretrained(qwen_model_name, trust_remote_code=True)
        except Exception as e:
            print(f"模型加载错误，请确保环境配置正确: {e}")
            # 降级处理... (省略)
            raise e

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # 冻结层
        total_params = len(list(self.qwen.parameters()))
        for i, param in enumerate(self.qwen.parameters()):
            if i < total_params - 8:
                param.requires_grad = False

        qwen_hidden_size = self.qwen.config.hidden_size
        self.text_projection = nn.Sequential(
            nn.Linear(qwen_hidden_size, 512),
            nn.LayerNorm(512),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256)
        )

        # 计算总特征维度 (更新部分)
        gcn_out = gcn_config['out_feats']
        # 结构特征 = GCN(2个) + 靶点(2个) + 理化(2个) + 细胞系(1个)
        total_structural_features = (gcn_out * 2) + (target_dim * 2) + (physchem_dim * 2) + cell_dim
        total_multimodal_features = total_structural_features + 256  # +文本特征

        print(f"Total Structural Features Dim: {total_structural_features}")

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

        self.cross_attention = CrossModalAttention(dim=256, num_heads=8, dropout=0.2)

        self.classifier = nn.Sequential(
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )

    def get_text_features(self, drug1_smiles, drug2_smiles, cell_expr):
        # 保持原有的文本提取逻辑，此处简化
        device = next(self.parameters()).device
        batch_size = len(drug1_smiles)
        # 为演示，直接返回随机特征，实际使用时请取消原有代码的注释
        return torch.randn(batch_size, 256, device=device)

    def forward(self, batch_data):
        device = next(self.parameters()).device

        # 1. GCN 特征
        g1, g2 = batch_data['graph1'], batch_data['graph2']
        d1 = self.gcn_drug1(g1.x.to(device), g1.edge_index.to(device))
        d1 = global_mean_pool(d1, g1.batch.to(device))
        d2 = self.gcn_drug2(g2.x.to(device), g2.edge_index.to(device))
        d2 = global_mean_pool(d2, g2.batch.to(device))

        # 2. 其他特征 (Target, PhysChem, Cell)
        target1 = batch_data['target1'].to(device)
        target2 = batch_data['target2'].to(device)
        physchem1 = batch_data['physchem1'].to(device)  # 新增
        physchem2 = batch_data['physchem2'].to(device)  # 新增
        cell_expr = batch_data['cell_expr'].to(device)

        # 3. 文本特征
        text_features = self.get_text_features(batch_data['drug1_smiles'], batch_data['drug2_smiles'], cell_expr)

        # 4. 拼接所有结构特征
        structural_features = torch.cat([d1, d2, target1, target2, physchem1, physchem2, cell_expr], dim=-1)

        # 5. 多模态融合
        multimodal_input = torch.cat([structural_features, text_features], dim=-1)
        fused_features = self.multimodal_fusion(multimodal_input)

        # 6. 注意力与分类
        refined_feat = self.cross_attention(
            fused_features.unsqueeze(1),
            fused_features.unsqueeze(1),
            fused_features.unsqueeze(1)
        )
        logits = self.classifier(refined_feat)

        return logits


class OptimizedDrugSynergyModel(nn.Module):
    """优化后的标准模型 (无Qwen)"""

    def __init__(self, gcn_config, num_classes=2, target_dim=560, cell_dim=1024, physchem_dim=7):
        super().__init__()
        self.gcn_drug1 = DrugGCN(**gcn_config)
        self.gcn_drug2 = DrugGCN(**gcn_config)

        # 维度计算
        gcn_out = gcn_config['out_feats']
        total_features = (gcn_out * 2) + (target_dim * 2) + (physchem_dim * 2) + cell_dim

        self.fusion_layer = nn.Sequential(
            nn.Linear(total_features, 1024),
            nn.LayerNorm(1024),
            nn.GELU(),
            nn.Dropout(0.4),
            nn.Linear(1024, 512),
            nn.LayerNorm(512),
            nn.GELU(),
            nn.Dropout(0.4),
            nn.Linear(512, 256)
        )

        self.cross_attention = CrossModalAttention(dim=256, num_heads=8, dropout=0.2)

        self.classifier = nn.Sequential(
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(0.4),
            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Linear(64, num_classes)
        )

    def forward(self, batch_data):
        device = next(self.parameters()).device

        # GCN
        g1, g2 = batch_data['graph1'], batch_data['graph2']
        d1 = global_mean_pool(self.gcn_drug1(g1.x.to(device), g1.edge_index.to(device)), g1.batch.to(device))
        d2 = global_mean_pool(self.gcn_drug2(g2.x.to(device), g2.edge_index.to(device)), g2.batch.to(device))

        # Features
        feat = torch.cat([
            d1, d2,
            batch_data['target1'].to(device), batch_data['target2'].to(device),
            batch_data['physchem1'].to(device), batch_data['physchem2'].to(device),
            batch_data['cell_expr'].to(device)
        ], dim=-1)

        fused = self.fusion_layer(feat)
        refined = self.cross_attention(fused.unsqueeze(1), fused.unsqueeze(1), fused.unsqueeze(1))
        return self.classifier(refined)