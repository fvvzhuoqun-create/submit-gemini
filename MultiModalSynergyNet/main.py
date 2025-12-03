from model import QwenDrugSynergyModel, SimpleQwenDrugSynergyModel, FocalLoss
from trainer import ImprovedDrugSynergyTrainer
from dataset import DrugSynergyDataset
from data_processor import DrugCellDataProcessor
import torch
from torch.utils.data import DataLoader, random_split
from utils import collate_fn
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_environment():
    """设置训练环境"""
    # 禁用可能引起问题的设置
    # os.environ['CUDA_LAUNCH_BLOCKING'] = '0'
    # os.environ['TORCH_CUDNN_V8_API_ENABLED'] = '1'

    # 禁用benchmark以获得更好的兼容性
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"使用设备: {device}")

    if device.type == 'cuda':
        logger.info(f"GPU: {torch.cuda.get_device_name()}")
        logger.info(f"CUDA版本: {torch.version.cuda}")

        # 清空GPU缓存
        torch.cuda.empty_cache()

    return device


def create_data_loaders(data_processor, batch_size=8):
    """创建数据加载器"""
    try:
        # 加载数据集
        dataset = DrugSynergyDataset('data.csv', data_processor)

        # 分割数据集
        total_size = len(dataset)
        train_size = int(0.7 * total_size)
        val_size = int(0.15 * total_size)
        test_size = total_size - train_size - val_size

        train_dataset, val_dataset, test_dataset = random_split(
            dataset, [train_size, val_size, test_size]
        )

        # 优化DataLoader配置
        num_workers = min(4, os.cpu_count())
        logger.info(f"使用 {num_workers} 个数据加载进程")

        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            collate_fn=collate_fn,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True,
            persistent_workers=True if num_workers > 0 else False
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,  # 保持相同batch_size
            collate_fn=collate_fn,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True,
            persistent_workers=True if num_workers > 0 else False
        )

        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            collate_fn=collate_fn,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True,
            persistent_workers=True if num_workers > 0 else False
        )

        logger.info(f"训练集大小: {len(train_dataset)}")
        logger.info(f"验证集大小: {len(val_dataset)}")
        logger.info(f"测试集大小: {len(test_dataset)}")

        return train_loader, val_loader, test_loader

    except Exception as e:
        logger.error(f"创建数据加载器失败: {e}")
        raise


def main():
    """主函数"""
    try:
        # 设置环境
        device = setup_environment()

        # 初始化数据处理器
        logger.info("初始化数据处理器...")
        data_processor = DrugCellDataProcessor(
            'drug_smiles.csv',
            'drug_targets.csv',
            'cell_line.csv'
        )

        # 获取实际的特征维度
        target_dim = data_processor.drug_targets.shape[1]  # 561
        cell_dim = data_processor.cell_line_expr.shape[1]  # 64

        logger.info(f"目标特征维度: {target_dim}")
        logger.info(f"细胞系特征维度: {cell_dim}")

        # 配置模型参数
        gcn_config = {
            'in_feats': 64,
            'hidden_size': 128,
            'out_feats': 256,
            'dropout': 0.1
        }

        # Qwen模型路径
        qwen_model_path = r"C:\Users\fzq11\models\Qwen2-1.5B"

        # 创建数据加载器
        logger.info("创建数据加载器...")
        train_loader, val_loader, test_loader = create_data_loaders(data_processor)

        # 选择模型
        use_simple_model = True  # 先使用简化模型进行测试

        if use_simple_model:
            logger.info("使用简化Qwen集成模型进行训练...")
            model = SimpleQwenDrugSynergyModel(
                gcn_config,
                target_dim=target_dim,
                cell_dim=cell_dim,
                qwen_model_path=qwen_model_path
            )
        else:
            logger.info("使用完整Qwen集成模型...")
            model = QwenDrugSynergyModel(
                gcn_config,
                target_dim=target_dim,
                cell_dim=cell_dim,
                qwen_model_path=qwen_model_path,
                freeze_qwen_layers=8  # 冻结前8层
            )

        # 打印模型参数数量
        total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        logger.info(f"模型可训练参数数量: {total_params:,}")

        # 训练模型
        logger.info("开始训练模型...")
        trainer = ImprovedDrugSynergyTrainer(model, train_loader, val_loader, test_loader, device)
        metrics_history = trainer.train(num_epochs=20)  # 进一步减少epoch数

        # 输出最终结果
        logger.info("\n训练完成!")
        logger.info(f"最佳验证F1: {trainer.best_val_f1:.4f}")
        logger.info(f"最佳验证准确率: {trainer.best_val_acc:.4f}")

        return metrics_history

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        raise


if __name__ == "__main__":
    main()