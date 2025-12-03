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

        # 禁用混合精度训练以避免cuDNN错误
        self.scaler = None

        # 计算类别权重
        self.class_weights = self.calculate_class_weights()
        print(f"使用的类别权重: {self.class_weights}")

        # 使用Focal Loss
        self.criterion = FocalLoss(alpha=0.75, gamma=2.0, reduction='mean')

        # 优化器 - 调整参数
        self.optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=1e-4,  # 适当的学习率
            weight_decay=0.01,  # 权重衰减
            betas=(0.9, 0.999)
        )

        # 改进的学习率调度器
        self.scheduler = torch.optim.lr_scheduler.OneCycleLR(
            self.optimizer,
            max_lr=1e-4,  # 降低学习率
            epochs=50,  # 改为50个epoch
            steps_per_epoch=len(train_loader),
            pct_start=0.1,
            div_factor=10,
            final_div_factor=100
        )

        # 移除了早停机制相关变量
        self.best_val_f1 = 0.0
        self.best_val_acc = 0.0
        self.best_epoch = 0

        self.metrics_history = []

    def calculate_class_weights(self):
        """从训练数据集中计算类别权重"""
        all_labels = []
        for batch in self.train_loader:
            labels = batch['labels']
            all_labels.extend(labels.numpy())

        class_counts = np.bincount(all_labels)
        total_samples = len(all_labels)
        num_classes = len(class_counts)

        # 使用逆频率加权
        weights = torch.tensor([total_samples / (num_classes * count) for count in class_counts],
                               dtype=torch.float32)
        return weights

    def train(self, num_epochs):
        """训练模型的主方法"""
        print("开始训练...")
        print(f"训练集大小: {len(self.train_loader.dataset)}")
        print(f"验证集大小: {len(self.val_loader.dataset)}")
        print(f"使用损失函数: Focal Loss")
        print("注意: 早停机制已被取消，将训练完整周期")
        print("使用标准精度训练（混合精度已禁用）")

        for epoch in range(num_epochs):
            start_time = time.time()

            # 训练一个epoch
            train_loss, train_metrics = self.train_epoch(epoch)

            # 验证
            val_metrics = self.evaluate(self.val_loader, 'val')

            # 计算epoch时间
            epoch_time = time.time() - start_time

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

            # 保存最佳模型（不移除保存最佳模型的逻辑，但不再使用早停）
            current_val_f1 = val_metrics["F1"]
            if current_val_f1 > self.best_val_f1:
                self.best_val_f1 = current_val_f1
                self.best_val_acc = val_metrics["ACC"]
                self.best_epoch = epoch + 1
                self.save_best_model(epoch + 1)
                print(f"✓ 发现更好的模型 (F1: {current_val_f1:.4f})")

            # 打印详细进度
            self.print_epoch_progress(epoch + 1, train_loss, train_metrics, val_metrics, epoch_time)

            # 每10个epoch保存一次指标到Excel
            if (epoch + 1) % 10 == 0:
                from utils import save_metrics_to_excel
                save_metrics_to_excel(self.metrics_history, f'training_metrics_epoch_{epoch + 1}.xlsx')

        # 训练结束后进行最终测试
        print("\n" + "=" * 60)
        print("训练完成，开始最终测试...")

        # 加载最佳模型进行测试
        self.load_best_model()
        test_metrics = self.evaluate(self.test_loader, 'test')

        print("\n最终测试结果:")
        print(f"ACC: {test_metrics['ACC']:.3f}, F1: {test_metrics['F1']:.3f}, "
              f"PREC: {test_metrics['PREC']:.3f}, Recall: {test_metrics['Recall']:.3f}")
        print(f"AUROC: {test_metrics['AUROC']:.3f}, AUPRC: {test_metrics['AUPRC']:.3f}, "
              f"MCC: {test_metrics['MCC']:.3f}, KAPPA: {test_metrics['KAPPA']:.3f}")

        # 保存最终指标
        from utils import save_metrics_to_excel
        save_metrics_to_excel(self.metrics_history, 'training_metrics_final.xlsx')
        print("Metrics saved to training_metrics_final.xlsx")

        return self.metrics_history

    def train_epoch(self, epoch):
        self.model.train()
        total_loss = 0
        all_preds = []
        all_labels = []
        all_probs = []

        # 使用tqdm创建进度条
        pbar = tqdm(self.train_loader, desc=f'Epoch {epoch + 1}', leave=False)

        for batch_idx, batch_data in enumerate(pbar):
            batch_data = {k: v.to(self.device, non_blocking=True) if isinstance(v, torch.Tensor) else v
                          for k, v in batch_data.items()}
            labels = batch_data['labels'].to(self.device, non_blocking=True)

            self.optimizer.zero_grad()

            # 标准精度训练（禁用混合精度）
            outputs = self.model(batch_data)
            loss = self.criterion(outputs, labels)
            loss.backward()

            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()

            # 更新学习率
            self.scheduler.step()

            total_loss += loss.item()

            # 收集预测结果
            probs = F.softmax(outputs, dim=-1)
            preds = torch.argmax(outputs, dim=-1)

            all_preds.extend(preds.detach().cpu().numpy())
            all_labels.extend(labels.detach().cpu().numpy())
            all_probs.extend(probs[:, 1].detach().cpu().numpy())

            # 更新进度条描述
            current_loss = loss.item()
            current_lr = self.optimizer.param_groups[0]['lr']
            pbar.set_postfix({
                'Loss': f'{current_loss:.4f}',
                'LR': f'{current_lr:.2e}'
            })

        avg_loss = total_loss / len(self.train_loader)
        train_metrics = self.calculate_metrics(all_labels, all_preds, all_probs, 'train')

        return avg_loss, train_metrics

    def evaluate(self, data_loader, mode='val'):
        self.model.eval()
        all_preds = []
        all_labels = []
        all_probs = []

        with torch.no_grad():
            pbar = tqdm(data_loader, desc=f'{mode.capitalize()}', leave=False)

            for batch_idx, batch_data in enumerate(pbar):
                batch_data = {k: v.to(self.device, non_blocking=True) if isinstance(v, torch.Tensor) else v
                              for k, v in batch_data.items()}
                labels = batch_data['labels'].to(self.device, non_blocking=True)

                outputs = self.model(batch_data)

                probs = F.softmax(outputs, dim=-1)
                preds = torch.argmax(outputs, dim=-1)

                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                all_probs.extend(probs[:, 1].cpu().numpy())

        return self.calculate_metrics(all_labels, all_preds, all_probs, mode)

    def calculate_metrics(self, true_labels, predictions, probabilities, mode):
        metrics = {}
        metrics['ACC'] = accuracy_score(true_labels, predictions)
        metrics['F1'] = f1_score(true_labels, predictions, average='binary', zero_division=0)
        metrics['PREC'] = precision_score(true_labels, predictions, average='binary', zero_division=0)
        metrics['Recall'] = recall_score(true_labels, predictions, average='binary', zero_division=0)

        # 检查是否有正负样本，避免计算AUC时出错
        if len(set(true_labels)) > 1:
            metrics['AUROC'] = roc_auc_score(true_labels, probabilities)
            metrics['AUPRC'] = average_precision_score(true_labels, probabilities)
        else:
            metrics['AUROC'] = 0.0
            metrics['AUPRC'] = 0.0

        metrics['MCC'] = matthews_corrcoef(true_labels, predictions)
        metrics['KAPPA'] = cohen_kappa_score(true_labels, predictions)

        # 添加类别分布信息
        unique, counts = np.unique(true_labels, return_counts=True)
        for i, (cls_val, count) in enumerate(zip(unique, counts)):
            metrics[f'Class_Distribution_{cls_val}'] = count

        return metrics

    def print_epoch_progress(self, epoch, train_loss, train_metrics, val_metrics, epoch_time):
        """按照期望格式打印epoch进度"""
        print(f"\nEpoch {epoch}/100 (时间: {epoch_time:.1f}s):")
        print(f"Train Loss: {train_loss:.4f} | ACC: {train_metrics['ACC']:.3f} | "
              f"F1: {train_metrics['F1']:.3f} | AUROC: {train_metrics['AUROC']:.3f}")

        print(f"Validation Results:")
        print(f"ACC: {val_metrics['ACC']:.3f}, F1: {val_metrics['F1']:.3f}, "
              f"PREC: {val_metrics['PREC']:.3f}, Recall: {val_metrics['Recall']:.3f}")
        print(f"AUROC: {val_metrics['AUROC']:.3f}, AUPRC: {val_metrics['AUPRC']:.3f}, "
              f"MCC: {val_metrics['MCC']:.3f}, KAPPA: {val_metrics['KAPPA']:.3f}")
        print("-" * 60)

    def save_best_model(self, epoch):
        """保存最佳模型"""
        model_path = f'best_model_epoch_{epoch}.pth'
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'best_val_acc': self.best_val_acc,
            'best_val_f1': self.best_val_f1,
            'class_weights': self.class_weights,
            'metrics': self.metrics_history[-1] if self.metrics_history else {}
        }, model_path)
        print(f"保存最佳模型到: {model_path} (验证F1: {self.best_val_f1:.4f})")

    def load_best_model(self):
        """加载最佳模型"""
        try:
            checkpoint = torch.load(f'best_model_epoch_{self.best_epoch}.pth')
            self.model.load_state_dict(checkpoint['model_state_dict'])
            print(f"加载最佳模型 (epoch {self.best_epoch})")
        except FileNotFoundError:
            print("未找到保存的最佳模型，使用当前模型进行测试")