from model import OptimizedDrugSynergyModel, QwenEnhancedDrugSynergyModel
from trainer import ImprovedDrugSynergyTrainer
from dataset import DrugSynergyDataset
from data_processor import DrugCellDataProcessor
import torch
from torch.utils.data import DataLoader, random_split
from utils import collate_fn
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_data_loaders(data_processor, batch_size=16):
    # 使用新的协同数据文件
    dataset = DrugSynergyDataset('two_class_synergy_data.csv', data_processor)

    total_size = len(dataset)
    train_size = int(0.7 * total_size)
    val_size = int(0.15 * total_size)
    test_size = total_size - train_size - val_size

    train_dataset, val_dataset, test_dataset = random_split(dataset, [train_size, val_size, test_size])

    # ... (DataLoader 配置保持不变) ...
    # 为简洁省略，请保持原有的DataLoader代码
    train_loader = DataLoader(train_dataset, batch_size=batch_size, collate_fn=collate_fn, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, collate_fn=collate_fn, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, collate_fn=collate_fn, shuffle=False)

    return train_loader, val_loader, test_loader


def main():
    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        gcn_config = {
            'in_feats': 64,
            'hidden_size': 128,
            'out_feats': 256,
            'dropout': 0.2
        }

        # 1. 初始化增强版数据处理器
        logger.info("初始化数据处理器 (使用新数据源)...")
        data_processor = DrugCellDataProcessor(
            drug_data_file='merged_drug_data_complete.csv',  # 包含SMILES和理化性质
            drug_target_file='Drug_Target_Protein.csv',  # 包含靶点信息
            cell_line_file='cell_ge_1024_features.csv'  # 包含1024维细胞特征
        )

        # 2. 模型配置
        model_type = "optimized"  # 或 "qwen_enhanced"

        # 动态获取特征维度
        target_dim = data_processor.target_dim
        cell_dim = data_processor.cell_dim
        physchem_dim = data_processor.physchem_dim

        if model_type == "optimized":
            model = OptimizedDrugSynergyModel(
                gcn_config,
                target_dim=target_dim,
                cell_dim=cell_dim,
                physchem_dim=physchem_dim
            )
            batch_size = 16
        elif model_type == "qwen_enhanced":
            model = QwenEnhancedDrugSynergyModel(
                gcn_config,
                target_dim=target_dim,
                cell_dim=cell_dim,
                physchem_dim=physchem_dim
            )
            batch_size = 8

        # 3. 创建数据加载器
        train_loader, val_loader, test_loader = create_data_loaders(data_processor, batch_size=batch_size)

        # 4. 训练
        trainer = ImprovedDrugSynergyTrainer(model, train_loader, val_loader, test_loader, device)
        trainer.train(num_epochs=100)

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")


if __name__ == "__main__":
    main()


"""针对你的项目（药物协同性预测，且提示词为中文），如果我们要选择一个**开源的通用模型**来获得最好的效果，目前的最佳推荐是 **Qwen 2.5 系列** 或 **Llama 3.1 系列**。

综合考虑你的代码现状（中文提示词）和硬件资源（推测能跑1.5B模型），以下是具体的推荐排名和分析：

### 1. 首选推荐：Qwen 2.5-7B-Instruct (通义千问)

这是目前最适合你项目的“版本答案”。

* **推荐理由**：
* **中文能力最强**：Qwen 2.5 在中文语境下的理解、推理和科学术语掌握能力是目前开源模型中的第一梯队。由于你的 `model.py` 中使用的是**中文 Prompt**，使用 Qwen 可以避免语言对齐带来的性能损失。
* **理科能力大幅提升**：相比你现在用的 Qwen2-1.5B，Qwen 2.5 在数学、代码和逻辑推理（Reasoning）上的训练数据大幅增加。这对于理解 SMILES 字符串（化学语言）和生物学通路非常有帮助。
* **无缝迁移**：它与你当前代码中的 Qwen2 架构完全兼容，你几乎不需要修改 `model.py` 中的加载代码（只需改模型路径）。



### 2. 轻量级最佳：Qwen 2.5-3B-Instruct

如果你显存有限（跑不动 7B 模型），那么 **Qwen 2.5-3B** 是 Qwen2-1.5B 的完美替代品。

* **推荐理由**：参数量翻倍但仍属于轻量级，性能却能吊打旧版的 7B 模型。它在保持推理速度的同时，能显著提升对药物分子特征的提取质量。

### 3. 英文环境最强：Llama 3.1-8B-Instruct

如果你愿意将提示词（Prompt）**改为英文**，那么 Llama 3.1 是目前的全球最强 8B 级模型。

* **推荐理由**：
* **世界级基座**：Llama 3.1 的训练数据量极其庞大，生物医药领域的英文文献阅读量远超其他模型。
* **生态丰富**：社区有很多基于 Llama 3 微调的生物学版本（如 Llama-3-OpenBioLLM），如果通用版效果不够，可以无缝切换到这些领域模型。


* **注意**：**必须将提示词翻译成英文**。用中文提示词强行喂给 Llama 3.1，虽然能跑，但效果通常不如 Qwen，因为模型需要分出注意力去处理“翻译/语言对齐”，而非专注于“药物分析”。

### 4. 潜力股：DeepSeek-V2.5 (或 DeepSeek-Lite)

* **推荐理由**：DeepSeek（深度求索）的模型在**逻辑推理**方面表现极佳。对于药物协同这种需要推断“A药物机理 + B药物机理 = ？”的任务，强推理模型往往能挖掘出更深层的特征。

---

### 总结建议

1. **最稳妥方案（保持中文提示词）**：
请下载 **Qwen 2.5-7B-Instruct**。
* 如果显存爆了（OOM），请尝试 **Qwen 2.5-3B-Instruct**。
* 如果还是爆显存，请使用 **4-bit 量化版本**（如 `Qwen2.5-7B-Instruct-GPTQ-Int4`）。


2. **追求上限方案（修改为英文提示词）**：
将 `model.py` 中的提示词改为英文，然后使用 **Llama-3.1-8B-Instruct**。

**预测提升**：
从 `Qwen2-1.5B` 升级到 `Qwen 2.5-7B`，在你的 100 轮训练预测中，**AUC 有望突破 0.90，甚至达到 0.92-0.94**，因为 7B 模型的“世界知识”和“逻辑推理”能力是 1.5B 模型无法比拟的，它能更好地理解“SMILES 字符串”背后隐含的分子结构意义。"""