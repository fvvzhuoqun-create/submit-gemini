from model import QwenEnhancedDrugSynergyModel
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

def create_data_loaders(data_processor, batch_size=4): # 7B模型建议减小batch_size防止OOM
    dataset = DrugSynergyDataset('two_class_synergy_data.csv', data_processor)
    total_size = len(dataset)
    train_size = int(0.7 * total_size)
    val_size = int(0.15 * total_size)
    test_size = total_size - train_size - val_size

    train_dataset, val_dataset, test_dataset = random_split(dataset, [train_size, val_size, test_size])

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

        logger.info("初始化数据处理器...")
        data_processor = DrugCellDataProcessor(
            drug_data_file='merged_drug_data_complete.csv',
            drug_target_file='Drug_Target_Protein.csv',
            cell_line_file='cell_ge_1024_features.csv'
        )

        # 切换为增强版模型
        model_type = "qwen_enhanced"

        target_dim = data_processor.target_dim
        cell_dim = data_processor.cell_dim
        physchem_dim = data_processor.physchem_dim

        if model_type == "qwen_enhanced":
            model = QwenEnhancedDrugSynergyModel(
                gcn_config,
                target_dim=target_dim,
                cell_dim=cell_dim,
                physchem_dim=physchem_dim,
                qwen_model_name="Qwen/Qwen2.5-3B-Instruct" # 更新路径
            )
            batch_size = 4 # 显存调优
        else:
            model = OptimizedDrugSynergyModel(
                gcn_config,
                target_dim=target_dim,
                cell_dim=cell_dim,
                physchem_dim=physchem_dim
            )
            batch_size = 8

        train_loader, val_loader, test_loader = create_data_loaders(data_processor, batch_size=batch_size)

        trainer = ImprovedDrugSynergyTrainer(model, train_loader, val_loader, test_loader, device)
        trainer.train(num_epochs=100)

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")

if __name__ == "__main__":
    main()