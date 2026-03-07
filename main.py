import torch
from torch.utils.data import DataLoader

from model import QwenEnhancedDrugSynergyModel
from trainer import ImprovedDrugSynergyTrainer
from dataset import DrugSynergyDataset
from data_processor import DrugCellDataProcessor
from utils import collate_fn


def main():
    # 1. 基础配置
    # 注意：如果显存不够跑不起来，请把这里换成 "Qwen/Qwen2.5-0.5B-Instruct"
    QWEN_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

    gcn_config = {
        'in_feats': 64,
        'hidden_size': 128,
        'out_feats': 256
    }

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用的计算设备: {device}")

    # 2. 初始化数据处理器
    # 请确保这三个 csv 文件在你的项目目录下
    print("正在初始化数据处理器...")
    processor = DrugCellDataProcessor(
        'merged_drug_data_complete.csv',
        'Drug_Target_Protein.csv',
        'cell_ge_1024_features.csv'
    )

    # 3. 加载数据集
    print("正在加载数据集...")
    train_dataset = DrugSynergyDataset('two_class_synergy_data.csv', processor)

    # 因为有大模型，batch_size 建议设小一点防止显存爆炸
    train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True, collate_fn=collate_fn)

    print("正在初始化大语言模型及GNN网络...")
    model = QwenEnhancedDrugSynergyModel(
        gcn_config=gcn_config,
        qwen_model_name=QWEN_MODEL_NAME,
        target_dim=processor.target_dim,  # 动态传入真实的靶点维度 (1162)
        cell_dim=processor.cell_dim,  # 动态传入真实的细胞系维度 (1024)
        physchem_dim=processor.physchem_dim  # 动态传入真实的理化维度 (7)
    )

    # 5. 启动训练
    trainer = ImprovedDrugSynergyTrainer(model, train_loader, train_loader, train_loader, device)

    print("所有准备工作完毕，开始训练！")
    trainer.train(num_epochs=50)


if __name__ == '__main__':
    main()