import torch
import pandas as pd
import numpy as np
import logging
from utils import collate_fn
from data_processor import DrugCellDataProcessor

logger = logging.getLogger(__name__)


class DrugSynergyDataset(torch.utils.data.Dataset):
    def __init__(self, data_file, data_processor, augment=False):
        self.data = self._load_and_validate_data(data_file)
        self.processor = data_processor
        self.augment = augment

        # 统计信息
        self._print_dataset_info()

    def _load_and_validate_data(self, data_file):
        """加载并验证数据集"""
        try:
            df = pd.read_csv(data_file)
            logger.info(f"加载数据集: {df.shape}")

            # 检查必要的列
            required_cols = ['Drug1', 'Drug2', 'Cell_line', 'classification']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"数据文件缺少必要的列: {missing_cols}")

            # 清理数据
            df = df.dropna(subset=required_cols)
            logger.info(f"清理后数据量: {len(df)}")

            return df

        except Exception as e:
            logger.error(f"加载数据文件失败: {e}")
            raise

    def _print_dataset_info(self):
        """打印数据集信息"""
        print(f"数据集大小: {len(self.data)}")
        print("数据列名:", self.data.columns.tolist())

        # 统计类别分布
        if 'classification' in self.data.columns:
            class_counts = self.data['classification'].value_counts()
            print("类别分布:")
            for class_name, count in class_counts.items():
                print(f"  {class_name}: {count} ({count / len(self.data) * 100:.2f}%)")

            # 计算类别权重
            self.class_weights = self.calculate_class_weights()
            print(f"类别权重: {self.class_weights}")
        else:
            print("警告: 数据集中未找到'classification'列")
            self.class_weights = {'synergy': 1.0, 'antagonism': 1.0}

        # 打印前几行数据用于调试
        print("前几行数据:")
        print(self.data.head())

    def calculate_class_weights(self):
        """计算类别权重用于处理不平衡数据"""
        class_counts = self.data['classification'].value_counts()
        total_samples = len(self.data)
        num_classes = len(class_counts)

        weights = {}
        for class_name, count in class_counts.items():
            # 使用逆频率加权
            weights[class_name] = total_samples / (num_classes * count)

        return weights

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        try:
            row = self.data.iloc[idx]

            # 处理样本
            processed = self.processor.process_sample(
                row['Drug1'],
                row['Drug2'],
                row['Cell_line'],
                augment=self.augment
            )

            # 处理标签
            classification = row['classification']
            label_map = {'synergy': 1, 'antagonism': 0, 'Synergy': 1, 'Antagonism': 0}
            label = label_map.get(classification, 0)

            processed['labels'] = torch.tensor(label, dtype=torch.long)

            # 添加类别权重信息
            processed['class_weight'] = torch.tensor(
                self.class_weights.get(classification, 1.0),
                dtype=torch.float32
            )

            return processed

        except Exception as e:
            logger.error(f"获取样本 {idx} 失败: {e}")
            # 返回一个默认样本
            return self._create_default_sample()

    def _create_default_sample(self):
        """创建默认样本"""
        default_sample = self.processor._create_default_sample()
        default_sample['labels'] = torch.tensor(0, dtype=torch.long)
        default_sample['class_weight'] = torch.tensor(1.0, dtype=torch.float32)
        return default_sample