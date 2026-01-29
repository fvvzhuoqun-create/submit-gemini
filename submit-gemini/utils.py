import pandas as pd
import torch
from torch_geometric.data import Data, Batch


def save_metrics_to_excel(epoch_metrics, filename='training_metrics.xlsx'):
    # 处理嵌套字典（如Class_Distribution）
    flattened_metrics = []
    for epoch_metric in epoch_metrics:
        flat_metric = {}
        for key, value in epoch_metric.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat_metric[f"{key}_{sub_key}"] = sub_value
            else:
                flat_metric[key] = value
        flattened_metrics.append(flat_metric)

    df = pd.DataFrame(flattened_metrics)

    try:
        existing_df = pd.read_excel(filename)
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_excel(filename, index=False)
    except FileNotFoundError:
        df.to_excel(filename, index=False)

    print(f"Metrics saved to {filename}")


def collate_fn(batch):
    graph1_list, graph2_list = [], []
    target1_list, target2_list, cell_expr_list, labels_list = [], [], [], []
    drug1_smiles_list, drug2_smiles_list = [], []
    physchem1_list, physchem2_list = [], []  # 新增：理化特征列表
    class_weight_list = []

    for sample in batch:
        e1, x1 = sample['graph1']
        e2, x2 = sample['graph2']
        graph1_list.append(Data(x=x1, edge_index=e1))
        graph2_list.append(Data(x=x2, edge_index=e2))

        target1_list.append(sample['target1'])
        target2_list.append(sample['target2'])

        # 新增：收集理化特征
        # 使用 .get() 提供默认值，防止旧数据报错
        physchem1_list.append(sample.get('physchem1', torch.zeros(7)))
        physchem2_list.append(sample.get('physchem2', torch.zeros(7)))

        cell_expr_list.append(sample['cell_expr'])
        labels_list.append(sample['labels'])

        drug1_smiles_list.append(sample.get('drug1_smiles', 'C'))
        drug2_smiles_list.append(sample.get('drug2_smiles', 'C'))

        class_weight_list.append(sample.get('class_weight', torch.tensor(1.0)))

    return {
        'graph1': Batch.from_data_list(graph1_list),
        'graph2': Batch.from_data_list(graph2_list),
        'target1': torch.stack(target1_list),
        'target2': torch.stack(target2_list),
        'physchem1': torch.stack(physchem1_list),  # 新增：打包理化特征
        'physchem2': torch.stack(physchem2_list),  # 新增：打包理化特征
        'cell_expr': torch.stack(cell_expr_list),
        'labels': torch.stack(labels_list),
        'drug1_smiles': drug1_smiles_list,
        'drug2_smiles': drug2_smiles_list,
        'class_weights': torch.stack(class_weight_list)
    }


def create_safe_collate_fn(processor):
    """创建安全的collate函数，处理异常样本"""

    def safe_collate_fn(batch):
        valid_samples = []
        for sample in batch:
            try:
                # 简单验证必要字段
                if (sample['graph1'][0].dim() == 2 and
                        sample['target1'].dim() == 1):
                    valid_samples.append(sample)
            except Exception as e:
                print(f"警告: 跳过异常样本: {e}")
                continue

        if len(valid_samples) == 0:
            return collate_fn([processor._create_default_sample()])

        return collate_fn(valid_samples)

    return safe_collate_fn