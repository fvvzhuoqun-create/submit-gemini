from model import OptimizedDrugSynergyModel, SimpleDrugSynergyModel, FocalLoss, QwenEnhancedDrugSynergyModel
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
    # 设置离线模式，优先使用本地模型
    os.environ['TRANSFORMERS_OFFLINE'] = '0'  # 设为0允许回退到在线
    os.environ['HF_HUB_OFFLINE'] = '0'

    os.environ['CUDA_LAUNCH_BLOCKING'] = '0'
    os.environ['TORCH_CUDNN_V8_API_ENABLED'] = '1'
    torch.backends.cudnn.benchmark = True

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"使用设备: {device}")

    if device.type == 'cuda':
        logger.info(f"GPU: {torch.cuda.get_device_name()}")
        logger.info(f"CUDA版本: {torch.version.cuda}")

        # 检查GPU内存
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024 ** 3
        logger.info(f"GPU内存: {gpu_memory:.1f} GB")

    return device


def create_data_loaders(data_processor, batch_size=16):  # 减小batch size以适应Qwen模型
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
            batch_size=batch_size,
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

        # 配置模型参数 - 调整dropout以防止过拟合
        gcn_config = {
            'in_feats': 64,
            'hidden_size': 128,
            'out_feats': 256,
            'dropout': 0.2  # 增加dropout
        }

        # 初始化数据处理器
        logger.info("初始化数据处理器...")
        data_processor = DrugCellDataProcessor(
            'drug_smiles.csv',
            'drug_targets.csv',
            'cell_line.csv'
        )

        # 选择模型
        model_type = "qwen_enhanced"  # 可选: "simple", "optimized", "qwen_enhanced"

        if model_type == "simple":
            logger.info("使用简化模型进行训练...")
            model = SimpleDrugSynergyModel(gcn_config)
            batch_size = 16
        elif model_type == "optimized":
            logger.info("使用优化后的DrugSynergy模型...")
            model = OptimizedDrugSynergyModel(gcn_config)
            batch_size = 16
        elif model_type == "qwen_enhanced":
            logger.info("使用Qwen增强的DrugSynergy模型...")
            model = QwenEnhancedDrugSynergyModel(gcn_config)
            batch_size = 8  # Qwen模型使用更小的batch size
        else:
            raise ValueError(f"未知的模型类型: {model_type}")

        # 创建数据加载器
        logger.info("创建数据加载器...")
        train_loader, val_loader, test_loader = create_data_loaders(data_processor, batch_size=batch_size)

        # 打印模型参数数量
        total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        logger.info(f"模型可训练参数数量: {total_params:,}")

        # 训练模型
        logger.info("开始训练模型...")
        trainer = ImprovedDrugSynergyTrainer(model, train_loader, val_loader, test_loader, device)
        metrics_history = trainer.train(num_epochs=100)

        # 输出最终结果
        logger.info("\n训练完成!")
        logger.info(f"最佳验证AUC: {trainer.best_val_auc:.4f}")
        logger.info(f"最佳验证准确率: {trainer.best_val_acc:.4f}")
        logger.info(f"最佳验证F1: {trainer.best_val_f1:.4f}")
        logger.info(f"最佳epoch: {trainer.best_epoch}")

        return metrics_history

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        # 提供更详细的错误信息
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        raise


if __name__ == "__main__":
    main()