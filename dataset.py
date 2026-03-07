import torch
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class DrugSynergyDataset(torch.utils.data.Dataset):
    def __init__(self, data_file, data_processor, augment=False):
        try:
            self.data = pd.read_csv(data_file)
            # 清除空缺数据的行
            self.data = self.data.dropna(subset=['Drug1', 'Drug2', 'Cell_line', 'classification'])
        except Exception as e:
            logger.error(f"加载数据文件失败: {e}")
            raise

        self.processor = data_processor
        self.augment = augment

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        try:
            row = self.data.iloc[idx]

            # 处理样本，拿到所有特征
            processed = self.processor.process_sample(
                row['Drug1'],
                row['Drug2'],
                row['Cell_line'],
                augment=self.augment
            )

            # 更稳健的标签提取逻辑
            label_str = str(row['classification']).lower().strip()
            label = 1 if 'synergy' in label_str else 0
            processed['labels'] = torch.tensor(label, dtype=torch.long)

            return processed

        except Exception as e:
            logger.error(f"获取样本 {idx} 失败: {e}")
            return self._create_default_sample()

    def _create_default_sample(self):
        default_sample = self.processor._create_default_sample()
        default_sample['labels'] = torch.tensor(0, dtype=torch.long)
        return default_sample