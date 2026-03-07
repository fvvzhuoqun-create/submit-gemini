import pandas as pd
import torch
from torch_geometric.data import Data, Batch

def save_metrics_to_excel(epoch_metrics, filename='training_metrics.xlsx'):
    df = pd.DataFrame(epoch_metrics)
    try:
        existing_df = pd.read_excel(filename)
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_excel(filename, index=False)
    except FileNotFoundError:
        df.to_excel(filename, index=False)
    print(f"Metrics saved to {filename}")

def collate_fn(batch):
    graph1_list, graph2_list = [], []
    for sample in batch:
        e1, x1 = sample['graph1']
        e2, x2 = sample['graph2']
        graph1_list.append(Data(x=x1, edge_index=e1))
        graph2_list.append(Data(x=x2, edge_index=e2))

    res = {
        'graph1': Batch.from_data_list(graph1_list),
        'graph2': Batch.from_data_list(graph2_list),
        'target1': torch.stack([s['target1'] for s in batch]),
        'target2': torch.stack([s['target2'] for s in batch]),
        'physchem1': torch.stack([s['physchem1'] for s in batch]),
        'physchem2': torch.stack([s['physchem2'] for s in batch]),
        'cell_expr': torch.stack([s['cell_expr'] for s in batch]),
        'labels': torch.stack([s['labels'] for s in batch]),
        # 这里的关键：直接保留为 List，不要用 torch.stack
        'drug1_smiles': [s['drug1_smiles'] for s in batch],
        'drug2_smiles': [s['drug2_smiles'] for s in batch]
    }
    return res

def create_safe_collate_fn(processor):
    def safe_collate_fn(batch):
        valid_samples = []
        for sample in batch:
            try:
                if sample['graph1'][0].dim() == 2 and sample['target1'].dim() == 1:
                    valid_samples.append(sample)
            except Exception:
                continue
        if len(valid_samples) == 0:
            return collate_fn([processor._create_default_sample()])
        return collate_fn(valid_samples)
    return safe_collate_fn