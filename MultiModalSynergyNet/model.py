import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool
from torch_geometric.data import Batch
from transformers import AutoModel, AutoTokenizer
import os


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


class QwenDrugSynergyModel(nn.Module):
    """集成Qwen2-1.5B的药物协同预测模型"""

    def __init__(self, gcn_config, target_dim=561, cell_dim=64, qwen_model_path=None, num_classes=2,
                 freeze_qwen_layers=8):
        super().__init__()

        if qwen_model_path is None:
            qwen_model_path = r"C:\Users\fzq11\models\Qwen2-1.5B"

        # 保存特征维度
        self.target_dim = target_dim
        self.cell_dim = cell_dim
        self.gcn_out = gcn_config['out_feats']

        # GCN网络
        self.gcn_drug1 = DrugGCN(**gcn_config)
        self.gcn_drug2 = DrugGCN(**gcn_config)

        # 动态计算总特征维度
        total_molecular_features = self.gcn_out * 2 + self.target_dim * 2 + self.cell_dim
        print(f"特征融合层输入维度: {total_molecular_features}")

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

        # 投影层：将融合特征投影到Qwen输入维度
        self.projection = nn.Linear(256, 1536)  # 修改为1536以匹配Qwen2-1.5B

        # 加载Qwen模型
        self.load_qwen_model(qwen_model_path, freeze_qwen_layers)

        # 分类头
        self.classifier = nn.Sequential(
            nn.Linear(self.qwen_hidden_size, 512),
            nn.LayerNorm(512),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes)
        )

        # 初始化权重
        self.apply(self._init_weights)

    def load_qwen_model(self, model_path, freeze_layers):
        """加载Qwen模型并冻结指定层数"""
        try:
            print(f"正在加载Qwen模型从: {model_path}")
            self.qwen = AutoModel.from_pretrained(
                model_path,
                local_files_only=True,
                trust_remote_code=True,
                dtype=torch.float32  # 改为float32确保兼容性
            )
            self.qwen_hidden_size = self.qwen.config.hidden_size

            # 冻结指定层数 - 适配Qwen2架构
            if freeze_layers > 0:
                # Qwen2使用model.layers而不是encoder.layer
                if hasattr(self.qwen, 'model') and hasattr(self.qwen.model, 'layers'):
                    total_layers = len(self.qwen.model.layers)
                    layers_to_freeze = min(freeze_layers, total_layers)

                    print(f"冻结Qwen模型的前 {layers_to_freeze} 层 (共 {total_layers} 层)")

                    # 冻结嵌入层
                    if hasattr(self.qwen, 'embed_tokens'):
                        for param in self.qwen.embed_tokens.parameters():
                            param.requires_grad = False

                    # 冻结前N层
                    for i in range(layers_to_freeze):
                        for param in self.qwen.model.layers[i].parameters():
                            param.requires_grad = False
                else:
                    print("警告: 无法识别Qwen模型层结构，跳过层冻结")

            print(f"Qwen模型加载成功，隐藏层维度: {self.qwen_hidden_size}")

        except Exception as e:
            print(f"加载Qwen模型失败: {e}")
            # 降级方案：创建虚拟Qwen模型
            self.create_dummy_qwen_model()

    def create_dummy_qwen_model(self):
        """创建虚拟Qwen模型用于测试"""
        print("创建虚拟Qwen模型用于测试...")
        self.qwen_hidden_size = 1536  # 修改为1536

        class DummyQwenModel(nn.Module):
            def __init__(self, hidden_size):
                super().__init__()
                self.config = type('Config', (), {'hidden_size': hidden_size})()
                self.dummy_layer = nn.Linear(hidden_size, hidden_size)

            def forward(self, inputs_embeds=None, attention_mask=None, return_dict=True):
                # 简单的恒等映射
                output = type('Output', (), {})()
                output.last_hidden_state = self.dummy_layer(inputs_embeds)
                return output

        self.qwen = DummyQwenModel(self.qwen_hidden_size)
        print("虚拟Qwen模型创建完成")

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

        # 调试信息：打印每个特征的维度
        if hasattr(self, 'debug') and self.debug:
            print(f"d1: {d1.shape}, d2: {d2.shape}")
            print(f"target1: {target1.shape}, target2: {target2.shape}")
            print(f"cell_expr: {cell_expr.shape}")

        # 特征融合
        molecular_feat = torch.cat([d1, d2, target1, target2, cell_expr], dim=-1)

        # 调试信息：打印融合后的维度
        if hasattr(self, 'debug') and self.debug:
            print(f"molecular_feat: {molecular_feat.shape}")
            print(f"期望维度: {self.gcn_out * 2 + self.target_dim * 2 + self.cell_dim}")

        fused_feat = self.fusion_layer(molecular_feat)  # 输出维度: 256

        # 投影到Qwen输入维度
        projected_feat = self.projection(fused_feat)  # [batch_size, 1536]

        # 准备Qwen输入
        # 将特征视为单个token输入
        inputs_embeds = projected_feat.unsqueeze(1)  # [batch_size, 1, 1536]

        # 创建attention mask (全1，因为只有一个token)
        attention_mask = torch.ones(batch_size, 1, dtype=torch.long, device=device)

        # 通过Qwen模型
        qwen_outputs = self.qwen(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            return_dict=True
        )

        # 取最后一个隐藏状态
        last_hidden_state = qwen_outputs.last_hidden_state  # [batch_size, 1, hidden_size]
        pooled_output = last_hidden_state[:, 0, :]  # [batch_size, hidden_size]

        # 分类
        logits = self.classifier(pooled_output)

        return logits


class SimpleQwenDrugSynergyModel(nn.Module):
    """简化版Qwen集成模型用于快速实验"""

    def __init__(self, gcn_config, target_dim=561, cell_dim=64, qwen_model_path=None, num_classes=2):
        super().__init__()

        if qwen_model_path is None:
            qwen_model_path = r"C:\Users\fzq11\models\Qwen2-1.5B"

        # 保存特征维度
        self.target_dim = target_dim
        self.cell_dim = cell_dim
        self.gcn_out = gcn_config['out_feats']

        # GCN网络
        self.gcn_drug1 = DrugGCN(**gcn_config)
        self.gcn_drug2 = DrugGCN(**gcn_config)

        # 动态计算总特征维度
        total_features = self.gcn_out * 2 + self.target_dim * 2 + self.cell_dim
        print(f"简化模型特征融合层输入维度: {total_features}")

        # 简化融合层
        self.fusion_layer = nn.Sequential(
            nn.Linear(total_features, 512),
            nn.LayerNorm(512),
            nn.ReLU(),
            nn.Dropout(0.3)
        )

        # 投影层
        self.projection = nn.Linear(512, 1536)  # 修改为1536以匹配Qwen2-1.5B

        # 加载Qwen模型（完全冻结）
        self.load_qwen_model(qwen_model_path)

        # 简化分类头
        self.classifier = nn.Sequential(
            nn.Linear(self.qwen_hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes)
        )

    def load_qwen_model(self, model_path):
        """加载并冻结整个Qwen模型"""
        try:
            print(f"正在加载Qwen模型从: {model_path}")
            self.qwen = AutoModel.from_pretrained(
                model_path,
                local_files_only=True,
                trust_remote_code=True,
                dtype=torch.float32  # 改为float32
            )
            self.qwen_hidden_size = self.qwen.config.hidden_size

            # 冻结整个Qwen模型
            for param in self.qwen.parameters():
                param.requires_grad = False

            print(f"Qwen模型加载成功，隐藏层维度: {self.qwen_hidden_size}")

        except Exception as e:
            print(f"加载Qwen模型失败: {e}")
            # 降级方案
            self.qwen_hidden_size = 1536  # 修改为1536

            class DummyQwenModel(nn.Module):
                def __init__(self, hidden_size):
                    super().__init__()
                    self.config = type('Config', (), {'hidden_size': hidden_size})()
                    self.dummy_layer = nn.Linear(hidden_size, hidden_size)

                def forward(self, inputs_embeds=None, attention_mask=None, return_dict=True):
                    output = type('Output', (), {})()
                    output.last_hidden_state = self.dummy_layer(inputs_embeds)
                    return output

            self.qwen = DummyQwenModel(self.qwen_hidden_size)
            print("使用虚拟Qwen模型")

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
        fused_feat = self.fusion_layer(fused_feat)

        # 投影到Qwen输入维度
        projected_feat = self.projection(fused_feat)
        inputs_embeds = projected_feat.unsqueeze(1)

        # 创建attention mask
        batch_size = batch_data['labels'].shape[0]
        attention_mask = torch.ones(batch_size, 1, dtype=torch.long, device=device)

        # 通过Qwen模型
        qwen_outputs = self.qwen(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            return_dict=True
        )

        # 取最后一个隐藏状态
        last_hidden_state = qwen_outputs.last_hidden_state
        pooled_output = last_hidden_state[:, 0, :]

        # 分类
        logits = self.classifier(pooled_output)

        return logits