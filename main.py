import torch
from torch.utils.data import DataLoader, random_split

from model import QwenEnhancedDrugSynergyModel
from trainer import ImprovedDrugSynergyTrainer
from dataset import DrugSynergyDataset
from data_processor import DrugCellDataProcessor
from utils import collate_fn


def main():
    # 1. 基础配置
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

    # 3. 加载完整数据集并进行划分 (按 8:1:1 比例)
    print("正在加载数据集...")
    full_dataset = DrugSynergyDataset('balanced_synergy_data.csv', processor)

    total_size = len(full_dataset)
    train_size = int(0.8 * total_size)
    val_size = int(0.1 * total_size)
    test_size = total_size - train_size - val_size  # 保证总数一致

    print(f"数据集划分完成 -> 总样本数: {total_size} | 训练集: {train_size} | 验证集: {val_size} | 测试集: {test_size}")

    # 随机划分数据集，使用固定随机种子(seed=42)保证每次运行划分结果一致
    train_dataset, val_dataset, test_dataset = random_split(
        full_dataset,
        [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(42)
    )

    # 4. 创建对应的 DataLoader
    # 【优化项 1】：针对 A40 48GB 显存，大幅提升 batch_size 榨干显卡算力
    batch_size = 16 

    # 【优化项 2】：开启多线程 (num_workers) 和锁页内存 (pin_memory)，加速 CPU 向 GPU 喂数据的速度
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn, num_workers=4, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, collate_fn=collate_fn, num_workers=4, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, collate_fn=collate_fn, num_workers=4, pin_memory=True)

    print("正在初始化大语言模型及GNN网络...")
    model = QwenEnhancedDrugSynergyModel(
        gcn_config=gcn_config,
        qwen_model_name=QWEN_MODEL_NAME,
        target_dim=processor.target_dim,  # 动态传入真实的靶点维度 (1162)
        cell_dim=processor.cell_dim,  # 动态传入真实的细胞系维度 (1024)
        physchem_dim=processor.physchem_dim  # 动态传入真实的理化维度 (7)
    )

    # 5. 初始化 Trainer 并启动训练
    # 此时传入的已经是真实划分好的三个独立的 loader，不再是重复传入 train_loader
    trainer = ImprovedDrugSynergyTrainer(model, train_loader, val_loader, test_loader, device)

    print("所有准备工作完毕，开始训练！")
    trainer.train(num_epochs=50)


if __name__ == '__main__':
    main()