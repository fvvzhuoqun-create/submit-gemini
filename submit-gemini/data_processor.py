import torch
import pandas as pd
import numpy as np
from torch_geometric.data import Data
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors

    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    logger.warning("RDKit未安装，将使用简化分子表示")


class DrugCellDataProcessor:
    def __init__(self, drug_smiles_file, drug_target_file, cell_line_file):
        """改进的数据处理器，正确处理药物名称到SMILES的映射"""
        logger.info("初始化数据处理器...")

        # 加载并验证数据
        self.drug_smiles_map = self._load_and_validate_smiles(drug_smiles_file)
        self.drug_targets = self._load_and_validate_targets(drug_target_file)
        self.cell_line_expr = self._load_and_validate_cell_line(cell_line_file)

        # 图结构缓存
        self.graph_cache = {}
        self.atom_feature_dim = 64

        logger.info(f"加载了 {len(self.drug_smiles_map)} 个药物的SMILES信息")
        logger.info(f"加载了 {len(self.drug_targets)} 个药物的目标特征")
        logger.info(f"加载了 {len(self.cell_line_expr)} 个细胞系的表达数据")
        logger.info(f"RDKit可用: {RDKIT_AVAILABLE}")

    def _load_and_validate_smiles(self, file_path):
        """加载并验证SMILES数据"""
        try:
            df = pd.read_csv(file_path)
            logger.info(f"SMILES数据维度: {df.shape}")

            # 检查必要的列
            required_cols = ['drug_id', 'smiles']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"SMILES文件缺少必要的列: {missing_cols}")

            # 创建药物名称到SMILES的映射
            smiles_map = {}
            valid_count = 0

            for _, row in df.iterrows():
                drug_id = str(row['drug_id']).strip()
                smiles = str(row['smiles']).strip()

                # 验证SMILES格式
                if self._validate_smiles(smiles):
                    smiles_map[drug_id] = smiles
                    valid_count += 1
                else:
                    logger.warning(f"药物 {drug_id} 的SMILES格式无效: {smiles}")

            logger.info(f"有效的SMILES映射数量: {valid_count}/{len(df)}")
            return smiles_map

        except Exception as e:
            logger.error(f"加载SMILES文件失败: {e}")
            raise

    def _validate_smiles(self, smiles):
        """验证SMILES字符串格式"""
        if not smiles or pd.isna(smiles):
            return False

        # 基本SMILES格式检查
        if len(smiles) < 2:
            return False

        # 如果RDKit可用，进行更严格的验证
        if RDKIT_AVAILABLE:
            try:
                mol = Chem.MolFromSmiles(smiles)
                return mol is not None
            except:
                return False

        # 简化验证：检查是否包含常见原子
        common_atoms = ['C', 'N', 'O', 'S', 'P', 'F', 'Cl', 'Br', 'I']
        return any(atom in smiles for atom in common_atoms)

    def _load_and_validate_targets(self, file_path):
        """加载并验证药物目标数据"""
        try:
            df = pd.read_csv(file_path)
            logger.info(f"药物目标数据维度: {df.shape}")

            if 'drug_id' not in df.columns:
                raise ValueError("药物目标文件必须包含 'drug_id' 列")

            df.set_index('drug_id', inplace=True)
            return df

        except Exception as e:
            logger.error(f"加载药物目标文件失败: {e}")
            raise

    def _load_and_validate_cell_line(self, file_path):
        """加载并验证细胞系数据"""
        try:
            df = pd.read_csv(file_path)
            logger.info(f"细胞系数据维度: {df.shape}")

            if 'cell_line' not in df.columns:
                raise ValueError("细胞系文件必须包含 'cell_line' 列")

            df.set_index('cell_line', inplace=True)
            return df

        except Exception as e:
            logger.error(f"加载细胞系文件失败: {e}")
            raise

    def get_drug_smiles(self, drug_name):
        """根据药物名称获取SMILES字符串"""
        drug_name = str(drug_name).strip()

        if drug_name in self.drug_smiles_map:
            return self.drug_smiles_map[drug_name]
        else:
            logger.warning(f"未找到药物 '{drug_name}' 的SMILES信息")
            # 返回一个简单的默认SMILES（甲烷）
            return 'C'

    def get_atom_features(self, atom):
        """改进的原子特征提取"""
        if not RDKIT_AVAILABLE:
            return np.random.randn(self.atom_feature_dim)

        try:
            features = []

            # 原子类型 (one-hot)
            atom_types = ['C', 'N', 'O', 'S', 'F', 'Cl', 'Br', 'I', 'P']
            atom_type = atom.GetSymbol()
            features.extend([1 if atom_type == t else 0 for t in atom_types])

            # 度
            features.append(atom.GetDegree())

            # 形式电荷
            features.append(atom.GetFormalCharge())

            # 手性
            features.append(int(atom.GetChiralTag()))

            # 杂化类型
            hybridizations = [
                Chem.rdchem.HybridizationType.SP,
                Chem.rdchem.HybridizationType.SP2,
                Chem.rdchem.HybridizationType.SP3
            ]
            features.extend([1 if atom.GetHybridization() == h else 0 for h in hybridizations])

            # 芳香性
            features.append(int(atom.GetIsAromatic()))

            # 氢原子数量
            features.append(atom.GetTotalNumHs())

            # 原子质量 (归一化)
            features.append(atom.GetMass() / 100.0)

            # 原子在周期表中的周期
            features.append(atom.GetAtomicNum())

            # 如果特征维度不够，用0填充
            if len(features) < self.atom_feature_dim:
                features.extend([0] * (self.atom_feature_dim - len(features)))
            else:
                features = features[:self.atom_feature_dim]

            return np.array(features, dtype=np.float32)

        except Exception as e:
            logger.warning(f"原子特征提取失败: {e}")
            return np.random.randn(self.atom_feature_dim)

    def smiles_to_graph(self, smiles):
        """改进的SMILES到图转换，带有更好的错误处理"""
        cache_key = f"graph_{hash(smiles)}"
        if cache_key in self.graph_cache:
            return self.graph_cache[cache_key]

        try:
            if RDKIT_AVAILABLE:
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    raise ValueError(f"无法从SMILES解析分子: {smiles}")

                # 提取原子特征
                node_features = []
                for atom in mol.GetAtoms():
                    features = self.get_atom_features(atom)
                    node_features.append(features)

                # 提取键信息作为边
                edge_index = []
                for bond in mol.GetBonds():
                    i = bond.GetBeginAtomIdx()
                    j = bond.GetEndAtomIdx()
                    edge_index.append([i, j])
                    edge_index.append([j, i])  # 无向图

                if not edge_index:  # 单原子分子
                    edge_index = [[0, 0]]

                # 优化：先将列表转换为单个numpy数组，再转换为tensor
                node_features_np = np.array(node_features, dtype=np.float32)
                node_features_tensor = torch.from_numpy(node_features_np)

                edge_index_np = np.array(edge_index, dtype=np.int64)
                edge_index_tensor = torch.from_numpy(edge_index_np).t().contiguous()

            else:
                # 简化方案：创建随机图
                num_nodes = max(3, min(20, len(smiles) // 3))
                node_features_tensor = torch.randn(num_nodes, self.atom_feature_dim)
                edge_index_tensor = torch.tensor([[0, 1, 1, 2], [1, 0, 2, 1]], dtype=torch.long)

        except Exception as e:
            logger.warning(f"图转换失败 {smiles}: {e}, 使用降级方案")
            # 降级方案
            node_features_tensor = torch.randn(10, self.atom_feature_dim)
            edge_index_tensor = torch.tensor([[0, 1, 1, 2, 2, 3], [1, 0, 2, 1, 3, 2]], dtype=torch.long)

        result = (edge_index_tensor, node_features_tensor)
        self.graph_cache[cache_key] = result
        return result

    def get_target_features(self, drug_name):
        """获取药物目标特征"""
        drug_name = str(drug_name).strip()
        try:
            if drug_name in self.drug_targets.index:
                # 优化：直接使用torch.from_numpy而不是torch.tensor
                target_values = self.drug_targets.loc[drug_name].values.astype(np.float32)
                return torch.from_numpy(target_values)
            else:
                logger.warning(f"未找到药物 '{drug_name}' 的目标特征")
                target_dim = self.drug_targets.shape[1]
                return torch.zeros(target_dim, dtype=torch.float32)
        except Exception as e:
            logger.warning(f"获取目标特征失败 {drug_name}: {e}")
            target_dim = self.drug_targets.shape[1]
            return torch.zeros(target_dim, dtype=torch.float32)

    def get_cell_line_features(self, cell_line):
        """获取细胞系特征"""
        cell_line = str(cell_line).strip()
        try:
            if cell_line in self.cell_line_expr.index:
                # 优化：直接使用torch.from_numpy而不是torch.tensor
                cell_values = self.cell_line_expr.loc[cell_line].values.astype(np.float32)
                return torch.from_numpy(cell_values)
            else:
                logger.warning(f"未找到细胞系 '{cell_line}' 的表达特征")
                cell_dim = self.cell_line_expr.shape[1]
                return torch.zeros(cell_dim, dtype=torch.float32)
        except Exception as e:
            logger.warning(f"获取细胞系特征失败 {cell_line}: {e}")
            cell_dim = self.cell_line_expr.shape[1]
            return torch.zeros(cell_dim, dtype=torch.float32)

    def process_sample(self, drug1, drug2, cell_line, augment=False):
        """处理单个样本，改进错误处理"""
        try:
            # 获取SMILES字符串
            smiles1 = self.get_drug_smiles(drug1)
            smiles2 = self.get_drug_smiles(drug2)

            logger.debug(f"处理药物对: {drug1}({smiles1[:20]}...) + {drug2}({smiles2[:20]}...)")

            # 转换为图结构
            edge_index1, node_features1 = self.smiles_to_graph(smiles1)
            edge_index2, node_features2 = self.smiles_to_graph(smiles2)

            # 数据增强（可选）
            if augment:
                edge_index1, node_features1 = self.augment_molecular_data((edge_index1, node_features1))
                edge_index2, node_features2 = self.augment_molecular_data((edge_index2, node_features2))

            # 获取目标特征
            target1 = self.get_target_features(drug1)
            target2 = self.get_target_features(drug2)

            # 获取细胞系特征
            cell_expr = self.get_cell_line_features(cell_line)

            return {
                'graph1': (edge_index1, node_features1),
                'graph2': (edge_index2, node_features2),
                'target1': target1,
                'target2': target2,
                'cell_expr': cell_expr,
                'drug1_smiles': smiles1,  # 新增：返回SMILES字符串
                'drug2_smiles': smiles2   # 新增：返回SMILES字符串
            }

        except Exception as e:
            logger.error(f"处理样本失败 ({drug1}, {drug2}, {cell_line}): {e}")
            # 返回一个默认的样本结构
            return self._create_default_sample()

    def _create_default_sample(self):
        """创建默认样本用于错误恢复"""
        node_features = torch.randn(10, self.atom_feature_dim)
        edge_index = torch.tensor([[0, 1, 1, 2], [1, 0, 2, 1]], dtype=torch.long)
        target_dim = self.drug_targets.shape[1]
        cell_dim = self.cell_line_expr.shape[1]

        return {
            'graph1': (edge_index, node_features),
            'graph2': (edge_index, node_features),
            'target1': torch.zeros(target_dim, dtype=torch.float32),
            'target2': torch.zeros(target_dim, dtype=torch.float32),
            'cell_expr': torch.zeros(cell_dim, dtype=torch.float32),
            'drug1_smiles': 'C',  # 默认SMILES
            'drug2_smiles': 'C'   # 默认SMILES
        }

    def augment_molecular_data(self, graph_data):
        """分子图数据增强"""
        edge_index, node_features = graph_data

        # 随机丢弃边
        if torch.rand(1) > 0.5 and edge_index.size(1) > 2:
            keep_ratio = 0.9
            num_edges = edge_index.size(1)
            num_keep = int(num_edges * keep_ratio)
            keep_indices = torch.randperm(num_edges)[:num_keep]
            edge_index = edge_index[:, keep_indices]

        # 随机掩码节点特征
        if torch.rand(1) > 0.5:
            mask_ratio = 0.1
            mask = torch.rand(node_features.size()) > mask_ratio
            node_features = node_features * mask.float()

        return edge_index, node_features