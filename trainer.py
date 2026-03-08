import torch
import numpy as np
import time
from tqdm import tqdm
import torch.nn.functional as F
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, average_precision_score, matthews_corrcoef, cohen_kappa_score
)

from model import FocalLoss
# 引入你在 utils.py 中写好的保存 Excel 的函数
from utils import save_metrics_to_excel


class ImprovedDrugSynergyTrainer:
    def __init__(self, model, train_loader, val_loader, test_loader, device):
        self.model = model.to(device)
        self.device = device
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.test_loader = test_loader
        self.criterion = FocalLoss()

        self.optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5, weight_decay=0.05)
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=10)

   

    def train_epoch(self, epoch):
        self.model.train()
        total_loss = 0
        pbar = tqdm(self.train_loader, desc=f"Epoch {epoch} [Train]")
        for batch in pbar:
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

    def evaluate(self, dataloader, epoch, phase="Validation"):
        """新增的评估函数，用于计算所有指标"""
        self.model.eval()
        total_loss = 0

        all_labels = []
        all_preds = []
        all_probs = []

        with torch.no_grad():
            for batch in tqdm(dataloader, desc=f"Epoch {epoch} [{phase}]"):
                processed_batch = {}
                for k, v in batch.items():
                    if hasattr(v, 'to'):
                        processed_batch[k] = v.to(self.device)
                    else:
                        processed_batch[k] = v
                batch = processed_batch

                logits = self.model(batch)
                loss = self.criterion(logits, batch['labels'])
                total_loss += loss.item()

                # 将 logits 转换为概率 (经过 softmax 取正类即 index=1 的概率)
                probs = F.softmax(logits, dim=1)[:, 1]
                # 获取预测类别
                preds = torch.argmax(logits, dim=1)

                # 收集用于计算指标的数据
                all_labels.extend(batch['labels'].cpu().numpy())
                all_preds.extend(preds.cpu().numpy())
                all_probs.extend(probs.cpu().numpy())

        avg_loss = total_loss / len(dataloader)

        # 计算各类指标 (zero_division=0 防止除0警告)
        acc = accuracy_score(all_labels, all_preds)
        f1 = f1_score(all_labels, all_preds, zero_division=0)
        prec = precision_score(all_labels, all_preds, zero_division=0)
        rec = recall_score(all_labels, all_preds, zero_division=0)

        # 对于 ROC 和 PRC，需要模型输出的预测概率，而不是 0/1 标签
        try:
            auroc = roc_auc_score(all_labels, all_probs)
        except ValueError:
            auroc = 0.0  # 防止 batch 内只有一个类别导致报错

        auprc = average_precision_score(all_labels, all_probs)
        mcc = matthews_corrcoef(all_labels, all_preds)
        kappa = cohen_kappa_score(all_labels, all_preds)

        # 打印到控制台
        print(f"\n--- Epoch {epoch} {phase} Results ---")
        print(f"Loss: {avg_loss:.4f} | ACC: {acc:.4f} | F1: {f1:.4f} | PREC: {prec:.4f} | Recall: {rec:.4f}")
        print(f"AUROC: {auroc:.4f} | AUPRC: {auprc:.4f} | MCC: {mcc:.4f} | KAPPA: {kappa:.4f}\n")

        # 返回字典以便保存到 Excel
        return {
            'Epoch': epoch,
            'Phase': phase,
            'Loss': avg_loss,
            'ACC': acc,
            'F1': f1,
            'PREC': prec,
            'Recall': rec,
            'AUROC': auroc,
            'AUPRC': auprc,
            'MCC': mcc,
            'KAPPA': kappa
        }

    def train(self, num_epochs):
        print("开始训练...")
        all_metrics = []  # 用于收集所有 Epoch 的评估结果

        for epoch in range(1, num_epochs + 1):
            start_time = time.time()

            # 1. 训练一个 Epoch
            train_loss = self.train_epoch(epoch)
            print(
                f"Epoch {epoch} 训练阶段完成 | 耗时: {time.time() - start_time:.1f}s | 平均 Train Loss: {train_loss:.4f}")

            # 2. 在验证集上评估
            val_metrics = self.evaluate(self.val_loader, epoch, phase="Validation")
            all_metrics.append(val_metrics)

            # 及时清理显存防止爆存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        # 3. 整个训练结束后，将所有验证指标保存到 Excel
        print("正在将评估指标保存到 Excel...")
        save_metrics_to_excel(all_metrics, filename='training_metrics.xlsx')
        print("训练全部结束！")