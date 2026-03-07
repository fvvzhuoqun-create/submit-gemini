import torch
import numpy as np
import time
from tqdm import tqdm
from model import FocalLoss


class ImprovedDrugSynergyTrainer:
    def __init__(self, model, train_loader, val_loader, test_loader, device):
        self.model = model.to(device)
        self.device = device
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.test_loader = test_loader

        # 显式计算权重并移动到 device
        weights = self.calculate_class_weights().to(device)
        self.criterion = FocalLoss(weight=weights)

        self.optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5, weight_decay=0.05)
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=10)

    def calculate_class_weights(self):
        labels = []
        for i, batch in enumerate(self.train_loader):
            labels.extend(batch['labels'].numpy())
            if i > 20: break
        counts = np.bincount(labels)
        return torch.tensor(len(labels) / (len(counts) * counts), dtype=torch.float32)

    def train_epoch(self, epoch):
        self.model.train()
        total_loss = 0
        pbar = tqdm(self.train_loader, desc=f"Epoch {epoch}")
        for batch in pbar:
            # 【修复点】：使用 hasattr(v, 'to') 替代 isinstance，
            # 这样 PyG 的 Batch (图数据) 和常规的 Tensor 都能被正确移动到 GPU，
            # 而字符串列表（SMILES）因为没有 .to 方法会被安全跳过。
            processed_batch = {}
            for k, v in batch.items():
                if hasattr(v, 'to'):
                    processed_batch[k] = v.to(self.device)
                else:
                    processed_batch[k] = v
            batch = processed_batch

            self.optimizer.zero_grad()
            logits = self.model(batch)
            loss = self.criterion(logits, batch['labels'])
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

            total_loss += loss.item()
            pbar.set_postfix({'Loss': f'{loss.item():.4f}'})

        self.scheduler.step()
        return total_loss / len(self.train_loader)

    def train(self, num_epochs):
        print("开始训练...")
        for epoch in range(1, num_epochs + 1):
            start_time = time.time()
            train_loss = self.train_epoch(epoch)
            print(f"Epoch {epoch} 完成 | 耗时: {time.time() - start_time:.1f}s | 平均 Loss: {train_loss:.4f}")

            # 及时清理显存防止爆存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()