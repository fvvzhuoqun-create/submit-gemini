import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATv2Conv, global_mean_pool
from transformers import AutoModel, AutoTokenizer


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


class DrugGAT(nn.Module):
    """
    使用 GATv2 替代 GCN 的图注意力网络提取器
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
                 qwen_model_name="Qwen/Qwen2.5-7B-Instruct"):
        super().__init__()

        self.gcn_drug1 = DrugGAT(**gcn_config, heads=4)
        self.gcn_drug2 = DrugGAT(**gcn_config, heads=4)

        print(f"正在加载Qwen2.5模型: {qwen_model_name}")
        try:
            self.qwen = AutoModel.from_pretrained(qwen_model_name, trust_remote_code=True)
            self.tokenizer = AutoTokenizer.from_pretrained(qwen_model_name, trust_remote_code=True)
        except Exception as e:
            print(f"模型加载错误: {e}")
            raise e

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # 针对 7B 模型，解冻最后 12 层以增强特征提取能力
        total_params = len(list(self.qwen.parameters()))
        for i, param in enumerate(self.qwen.parameters()):
            if i < total_params - 12:
                param.requires_grad = False

        qwen_hidden_size = self.qwen.config.hidden_size

        # 优化投影层维度，从 512 提升至 1024 以适配 7B 模型的高维输出
        self.text_projection = nn.Sequential(
            nn.Linear(qwen_hidden_size, 1024),
            nn.LayerNorm(1024),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(1024, 256)
        )

        gcn_out = gcn_config['out_feats']
        total_structural_features = (gcn_out * 2) + (target_dim * 2) + (physchem_dim * 2) + cell_dim
        total_multimodal_features = total_structural_features + 256

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
        # 此处应包含 Qwen 的 forward 逻辑，示例简化
        device = next(self.parameters()).device
        batch_size = len(drug1_smiles)
        return torch.randn(batch_size, 256, device=device)

    def forward(self, batch_data):
        device = next(self.parameters()).device

        g1, g2 = batch_data['graph1'], batch_data['graph2']
        d1 = self.gcn_drug1(g1.x.to(device), g1.edge_index.to(device))
        d1 = global_mean_pool(d1, g1.batch.to(device))
        d2 = self.gcn_drug2(g2.x.to(device), g2.edge_index.to(device))
        d2 = global_mean_pool(d2, g2.batch.to(device))

        target1 = batch_data['target1'].to(device)
        target2 = batch_data['target2'].to(device)
        physchem1 = batch_data['physchem1'].to(device)
        physchem2 = batch_data['physchem2'].to(device)
        cell_expr = batch_data['cell_expr'].to(device)

        text_features = self.get_text_features(batch_data['drug1_smiles'], batch_data['drug2_smiles'], cell_expr)

        structural_features = torch.cat([d1, d2, target1, target2, physchem1, physchem2, cell_expr], dim=-1)
        multimodal_input = torch.cat([structural_features, text_features], dim=-1)
        fused_features = self.multimodal_fusion(multimodal_input)

        refined_feat = self.cross_attention(
            fused_features.unsqueeze(1),
            fused_features.unsqueeze(1),
            fused_features.unsqueeze(1)
        )
        logits = self.classifier(refined_feat)
        return logits