import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, \
    average_precision_score, matthews_corrcoef, cohen_kappa_score
import numpy as np
import time
from tqdm import tqdm
from model import FocalLoss


class ImprovedDrugSynergyTrainer:
    def __init__(self, model, train_loader, val_loader, test_loader, device):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.test_loader = test_loader
        self.device = device

        # --- 修改 1: 强制关闭混合精度训练 (AMP) ---
        # GATv2 在 FP16 下极不稳定，容易导致 0xC0000005 崩溃
        # 我们强制设置为 None，使用 FP32 全精度训练
        self.scaler = None
        print("为了 GATv2 的稳定性，已强制关闭混合精度训练 (使用 FP32)")

        # 计算类别权重
        self.class_weights = self.calculate_class_weights()
        print(f"使用的类别权重: {self.class_weights}")

        # 使用Focal Loss
        self.criterion = FocalLoss(alpha=0.75, gamma=2.0, reduction='mean')

        # 优化器
        self.optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=1e-4,
            weight_decay=0.01,
            betas=(0.9, 0.999)
        )

        # 学习率调度器
        self.scheduler = torch.optim.lr_scheduler.OneCycleLR(
            self.optimizer,
            max_lr=1e-3,
            epochs=100,
            steps_per_epoch=len(train_loader),
            pct_start=0.1,
            div_factor=10,
            final_div_factor=100
        )

        # 早停机制
        self.early_stopping_patience = 15
        self.early_stopping_counter = 0
        self.early_stopping_min_delta = 0.001
        self.best_val_auc = 0.0
        self.best_val_acc = 0.0
        self.best_val_f1 = 0.0
        self.best_epoch = 0

        self.metrics_history = []

    def calculate_class_weights(self):
        """从训练数据集中计算类别权重"""
        all_labels = []
        # 为了速度，只采样部分数据计算权重
        sample_count = 0
        for batch in self.train_loader:
            labels = batch['labels']
            all_labels.extend(labels.numpy())
            sample_count += 1
            if sample_count > 50: break  # 只看前50个batch估算

        class_counts = np.bincount(all_labels)
        total_samples = len(all_labels)
        num_classes = len(class_counts)

        weights = torch.tensor([total_samples / (num_classes * count) for count in class_counts],
                               dtype=torch.float32)
        return weights

    def train(self, num_epochs):
        """训练模型的主方法"""
        print("开始训练...")
        print(f"训练集大小: {len(self.train_loader.dataset)}")
        print(f"验证集大小: {len(self.val_loader.dataset)}")
        print(f"使用损失函数: Focal Loss")

        for epoch in range(num_epochs):
            start_time = time.time()

            # 训练一个epoch
            train_loss, train_metrics = self.train_epoch(epoch)

            # 验证
            val_metrics = self.evaluate(self.val_loader, 'val')

            # 计算epoch时间
            epoch_time = time.time() - start_time

            # --- 修改 2: 每个 Epoch 结束后手动清理显存 ---
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # 记录指标
            epoch_metrics = {
                'epoch': epoch + 1,
                'train_loss': train_loss,
                'epoch_time': epoch_time,
                'learning_rate': self.optimizer.param_groups[0]['lr'],
                **{f'train_{k}': v for k, v in train_metrics.items()},
                **{f'val_{k}': v for k, v in val_metrics.items()}
            }
            self.metrics_history.append(epoch_metrics)

            # 检查早停
            current_val_auc = val_metrics["AUROC"]
            should_save = current_val_auc > self.best_val_auc + self.early_stopping_min_delta

            if should_save:
                self.best_val_auc = current_val_auc
                self.best_val_acc = val_metrics["ACC"]
                self.best_val_f1 = val_metrics["F1"]
                self.best_epoch = epoch + 1
                self.early_stopping_counter = 0
                self.save_best_model(epoch + 1)
                print(f"✓ 发现更好的模型 (AUC: {current_val_auc:.4f}, 提升: {current_val_auc - self.best_val_auc:.4f})")
            else:
                self.early_stopping_counter += 1
                print(
                    f"→ 未提升 AUC: {current_val_auc:.4f} (最佳: {self.best_val_auc:.4f}), 早停计数器: {self.early_stopping_counter}/{self.early_stopping_patience}")

            self.print_epoch_progress(epoch + 1, train_loss, train_metrics, val_metrics, epoch_time)

            if self.early_stopping_counter >= self.early_stopping_patience:
                print(f"\n⚠️ 早停触发! 连续 {self.early_stopping_patience} 个epoch验证AUC未提升")
                break

            if (epoch + 1) % 10 == 0:
                from utils import save_metrics_to_excel
                save_metrics_to_excel(self.metrics_history, f'training_metrics_epoch_{epoch + 1}.xlsx')

        # 训练结束
        print("\n" + "=" * 60)
        print("训练完成，开始最终测试...")
        self.load_best_model()
        test_metrics = self.evaluate(self.test_loader, 'test')

        print("\n最终测试结果:")
        print(f"ACC: {test_metrics['ACC']:.3f}, F1: {test_metrics['F1']:.3f}")
        print(f"AUROC: {test_metrics['AUROC']:.3f}, AUPRC: {test_metrics['AUPRC']:.3f}")

        from utils import save_metrics_to_excel
        save_metrics_to_excel(self.metrics_history, 'training_metrics_final.xlsx')

        return self.metrics_history

    def train_epoch(self, epoch):
        self.model.train()
        total_loss = 0
        all_preds = []
        all_labels = []
        all_probs = []

        pbar = tqdm(self.train_loader, desc=f'Epoch {epoch + 1}', leave=False)

        for batch_idx, batch_data in enumerate(pbar):
            try:
                batch_data = self._safe_move_to_device(batch_data)
                labels = batch_data['labels']

                self.optimizer.zero_grad()

                # --- 修改 3: 移除 AMP 上下文管理器，直接前向传播 ---
                # 原来的 if self.scaler: ... else: ... 被简化为只有 else 分支
                outputs = self.model(batch_data)
                loss = self.criterion(outputs, labels)
                loss.backward()

                # 梯度裁剪依然保留，防止梯度爆炸
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()

                # 更新学习率
                self.scheduler.step()

                total_loss += loss.item()

                # 收集结果
                probs = F.softmax(outputs, dim=-1)
                preds = torch.argmax(outputs, dim=-1)

                all_preds.extend(preds.detach().cpu().numpy())
                all_labels.extend(labels.detach().cpu().numpy())
                all_probs.extend(probs[:, 1].detach().cpu().numpy())

                pbar.set_postfix({'Loss': f'{loss.item():.4f}'})

            except Exception as e:
                print(f"\n警告: 批次 {batch_idx} 训练失败: {e}")
                continue

        avg_loss = total_loss / len(self.train_loader)
        train_metrics = self.calculate_metrics(all_labels, all_preds, all_probs, 'train')
        return avg_loss, train_metrics

    def _safe_move_to_device(self, batch_data):
        processed_batch = {}
        for k, v in batch_data.items():
            if isinstance(v, torch.Tensor):
                processed_batch[k] = v.to(self.device, non_blocking=True)
            else:
                processed_batch[k] = v
        return processed_batch

    def evaluate(self, data_loader, mode='val'):
        self.model.eval()
        all_preds = []
        all_labels = []
        all_probs = []

        with torch.no_grad():
            pbar = tqdm(data_loader, desc=f'{mode.capitalize()}', leave=False)
            for batch_data in pbar:
                try:
                    batch_data = self._safe_move_to_device(batch_data)
                    # 同样移除 AMP
                    outputs = self.model(batch_data)

                    probs = F.softmax(outputs, dim=-1)
                    preds = torch.argmax(outputs, dim=-1)

                    all_preds.extend(preds.cpu().numpy())
                    all_labels.extend(batch_data['labels'].cpu().numpy())
                    all_probs.extend(probs[:, 1].cpu().numpy())
                except Exception:
                    continue

        return self.calculate_metrics(all_labels, all_preds, all_probs, mode)

    def calculate_metrics(self, true_labels, predictions, probabilities, mode):
        metrics = {}
        try:
            metrics['ACC'] = accuracy_score(true_labels, predictions)
            metrics['F1'] = f1_score(true_labels, predictions, average='binary', zero_division=0)
            metrics['PREC'] = precision_score(true_labels, predictions, average='binary', zero_division=0)
            metrics['Recall'] = recall_score(true_labels, predictions, average='binary', zero_division=0)

            if len(set(true_labels)) > 1:
                metrics['AUROC'] = roc_auc_score(true_labels, probabilities)
                metrics['AUPRC'] = average_precision_score(true_labels, probabilities)
            else:
                metrics['AUROC'] = 0.5
                metrics['AUPRC'] = 0.5

            metrics['MCC'] = matthews_corrcoef(true_labels, predictions)
            metrics['KAPPA'] = cohen_kappa_score(true_labels, predictions)
        except Exception:
            # 简化错误处理
            metrics = {'ACC': 0.5, 'F1': 0, 'AUROC': 0.5, 'AUPRC': 0.5, 'PREC': 0, 'Recall': 0, 'MCC': 0, 'KAPPA': 0}

        return metrics

    def print_epoch_progress(self, epoch, train_loss, train_metrics, val_metrics, epoch_time):
        print(f"\nEpoch {epoch}/100 (时间: {epoch_time:.1f}s):")
        print(f"Train Loss: {train_loss:.4f} | ACC: {train_metrics['ACC']:.3f} | AUC: {train_metrics['AUROC']:.3f}")
        print(f"Validation AUC: {val_metrics['AUROC']:.3f} | ACC: {val_metrics['ACC']:.3f}")
        print("-" * 60)

    def save_best_model(self, epoch):
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'best_val_auc': self.best_val_auc
        }, f'best_model_epoch_{epoch}.pth')

    def load_best_model(self):
        try:
            checkpoint = torch.load(f'best_model_epoch_{self.best_epoch}.pth')
            self.model.load_state_dict(checkpoint['model_state_dict'])
        except:
            print("未找到最佳模型文件")