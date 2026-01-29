import torch
import pandas as pd
import numpy as np
from torch_geometric.data import Data
import logging
from sklearn.preprocessing import StandardScaler

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from rdkit import Chem

    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    logger.warning("RDKit未安装，将使用简化分子表示")


class DrugCellDataProcessor:
    def __init__(self, drug_data_file, drug_target_file, cell_line_file):
        """
        改进的数据处理器
        :param drug_data_file: 包含SMILES和理化性质的完整药物数据 (merged_drug_data_complete.csv)
        :param drug_target_file: 药物靶点信息 (Drug_Target_Protein.csv)
        :param cell_line_file: 细胞系基因表达特征 (cell_ge_1024_features.csv)
        """
        logger.info("初始化数据处理器 (Enhanced)...")

        # 1. 加载药物SMILES和理化性质
        self.drug_smiles_map, self.drug_physchem = self._load_drug_data(drug_data_file)

        # 2. 加载并构建药物靶点矩阵
        self.drug_targets = self._load_and_process_targets(drug_target_file)

        # 3. 加载高维细胞系数据
        self.cell_line_expr = self._load_cell_features(cell_line_file)

        # 图结构缓存
        self.graph_cache = {}
        self.atom_feature_dim = 64

        # 特征维度记录
        self.physchem_dim = self.drug_physchem.shape[1] if self.drug_physchem is not None else 0
        self.target_dim = self.drug_targets.shape[1]
        self.cell_dim = self.cell_line_expr.shape[1]

        logger.info(f"药物数量: {len(self.drug_smiles_map)}")
        logger.info(f"理化特征维度: {self.physchem_dim}")
        logger.info(f"靶点特征维度: {self.target_dim}")
        logger.info(f"细胞系特征维度: {self.cell_dim}")

    def _load_drug_data(self, file_path):
        """加载药物SMILES和理化性质"""
        try:
            df = pd.read_csv(file_path)
            # 使用 drugName 作为 ID
            if 'drugName' not in df.columns:
                raise ValueError("药物数据文件缺少 'drugName' 列")

            # 清理 ID
            df['drugName'] = df['drugName'].astype(str).str.strip()
            df = df.drop_duplicates(subset=['drugName'])
            df.set_index('drugName', inplace=True)

            # 1. 提取 SMILES
            smiles_map = {}
            if 'SMILES' in df.columns:
                for idx, row in df.iterrows():
                    smiles = str(row['SMILES']).strip()
                    if self._validate_smiles(smiles):
                        smiles_map[str(idx)] = smiles

            # 2. 提取并标准化理化性质
            physchem_cols = ['MW', 'logP', 'TPSA', 'HBD', 'HBA', 'RotatableBonds', 'HeavyAtoms']
            # 确保列存在，不存在则填充0
            valid_cols = [c for c in physchem_cols if c in df.columns]
            physchem_df = df[valid_cols].fillna(0).astype(float)

            # 标准化
            scaler = StandardScaler()
            physchem_values = scaler.fit_transform(physchem_df)
            physchem_df = pd.DataFrame(physchem_values, index=physchem_df.index, columns=valid_cols)

            return smiles_map, physchem_df

        except Exception as e:
            logger.error(f"加载药物数据失败: {e}")
            raise

    def _validate_smiles(self, smiles):
        if not smiles or pd.isna(smiles) or len(str(smiles)) < 2:
            return False
        return True

    def _load_and_process_targets(self, file_path):
        """加载靶点数据并构建 Multi-hot 编码"""
        try:
            df = pd.read_csv(file_path)
            # 必需列: csv_drug_name, target_name (或 uniprot_id)
            if 'csv_drug_name' not in df.columns or 'target_name' not in df.columns:
                logger.warning("靶点文件列名不匹配，尝试使用 drug_id 格式")
                # 兼容旧格式逻辑
                if 'drug_id' in df.columns:
                    df.set_index('drug_id', inplace=True)
                    return df

            # 构建透视表: Rows=Drugs, Cols=Targets, Values=1
            # 使用 csv_drug_name 作为药物ID
            df['csv_drug_name'] = df['csv_drug_name'].astype(str).str.strip()
            # 仅保留存在的列
            target_matrix = pd.crosstab(df['csv_drug_name'], df['target_name'])
            # 转换为 float32
            return target_matrix.astype(np.float32)

        except Exception as e:
            logger.error(f"加载靶点数据失败: {e}")
            # 返回空的一个默认矩阵
            return pd.DataFrame()

    def _load_cell_features(self, file_path):
        """加载高维细胞系特征"""
        try:
            df = pd.read_csv(file_path)
            if 'cell_line' not in df.columns:
                raise ValueError("细胞系文件缺少 'cell_line' 列")

            df.set_index('cell_line', inplace=True)
            # 确保全是数值
            return df.select_dtypes(include=[np.number]).astype(np.float32)
        except Exception as e:
            logger.error(f"加载细胞系数据失败: {e}")
            raise

    def get_drug_smiles(self, drug_name):
        drug_name = str(drug_name).strip()
        return self.drug_smiles_map.get(drug_name, 'C')

    def get_physchem_features(self, drug_name):
        """获取药物理化性质"""
        drug_name = str(drug_name).strip()
        if self.drug_physchem is not None and drug_name in self.drug_physchem.index:
            vals = self.drug_physchem.loc[drug_name].values.astype(np.float32)
            return torch.from_numpy(vals)
        else:
            return torch.zeros(self.physchem_dim, dtype=torch.float32)

    def get_target_features(self, drug_name):
        drug_name = str(drug_name).strip()
        if drug_name in self.drug_targets.index:
            vals = self.drug_targets.loc[drug_name].values.astype(np.float32)
            return torch.from_numpy(vals)
        else:
            return torch.zeros(self.target_dim, dtype=torch.float32)

    def get_cell_line_features(self, cell_line):
        cell_line = str(cell_line).strip()
        if cell_line in self.cell_line_expr.index:
            vals = self.cell_line_expr.loc[cell_line].values.astype(np.float32)
            return torch.from_numpy(vals)
        else:
            logger.warning(f"未找到细胞系: {cell_line}")
            return torch.zeros(self.cell_dim, dtype=torch.float32)

    def get_atom_features(self, atom):
        """原子特征提取 (保持不变)"""
        if not RDKIT_AVAILABLE:
            return np.random.randn(self.atom_feature_dim)
        try:
            features = []
            atom_types = ['C', 'N', 'O', 'S', 'F', 'Cl', 'Br', 'I', 'P']
            atom_type = atom.GetSymbol()
            features.extend([1 if atom_type == t else 0 for t in atom_types])
            features.append(atom.GetDegree())
            features.append(atom.GetFormalCharge())
            features.append(int(atom.GetChiralTag()))
            features.append(int(atom.GetIsAromatic()))
            features.append(atom.GetTotalNumHs())
            features.append(atom.GetMass() / 100.0)
            features.append(atom.GetAtomicNum())
            if len(features) < self.atom_feature_dim:
                features.extend([0] * (self.atom_feature_dim - len(features)))
            else:
                features = features[:self.atom_feature_dim]
            return np.array(features, dtype=np.float32)
        except:
            return np.random.randn(self.atom_feature_dim)

    def smiles_to_graph(self, smiles):
        """SMILES转图 (保持不变)"""
        cache_key = f"graph_{hash(smiles)}"
        if cache_key in self.graph_cache:
            return self.graph_cache[cache_key]

        try:
            if RDKIT_AVAILABLE:
                mol = Chem.MolFromSmiles(smiles)
                if mol is None: raise ValueError()

                node_features = [self.get_atom_features(atom) for atom in mol.GetAtoms()]
                edge_index = []
                for bond in mol.GetBonds():
                    i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
                    edge_index += [[i, j], [j, i]]

                if not edge_index: edge_index = [[0, 0]]

                x = torch.from_numpy(np.array(node_features, dtype=np.float32))
                edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
            else:
                x = torch.randn(5, self.atom_feature_dim)
                edge_index = torch.tensor([[0, 1, 1, 2], [1, 0, 2, 1]], dtype=torch.long)
        except:
            x = torch.randn(5, self.atom_feature_dim)
            edge_index = torch.tensor([[0, 1, 1, 2], [1, 0, 2, 1]], dtype=torch.long)

        res = (edge_index, x)
        self.graph_cache[cache_key] = res
        return res

    def process_sample(self, drug1, drug2, cell_line, augment=False):
        """处理单个样本，包含新增的理化特征"""
        try:
            smiles1 = self.get_drug_smiles(drug1)
            smiles2 = self.get_drug_smiles(drug2)

            edge_index1, node_features1 = self.smiles_to_graph(smiles1)
            edge_index2, node_features2 = self.smiles_to_graph(smiles2)

            if augment:
                edge_index1, node_features1 = self.augment_molecular_data((edge_index1, node_features1))
                edge_index2, node_features2 = self.augment_molecular_data((edge_index2, node_features2))

            return {
                'graph1': (edge_index1, node_features1),
                'graph2': (edge_index2, node_features2),
                'target1': self.get_target_features(drug1),
                'target2': self.get_target_features(drug2),
                'physchem1': self.get_physchem_features(drug1),  # 新增
                'physchem2': self.get_physchem_features(drug2),  # 新增
                'cell_expr': self.get_cell_line_features(cell_line),
                'drug1_smiles': smiles1,
                'drug2_smiles': smiles2
            }
        except Exception as e:
            logger.error(f"Error processing {drug1}-{drug2}: {e}")
            return self._create_default_sample()

    def _create_default_sample(self):
        # 创建维度匹配的默认数据
        x = torch.randn(5, self.atom_feature_dim)
        edge = torch.tensor([[0, 1], [1, 0]], dtype=torch.long)
        return {
            'graph1': (edge, x), 'graph2': (edge, x),
            'target1': torch.zeros(self.target_dim), 'target2': torch.zeros(self.target_dim),
            'physchem1': torch.zeros(self.physchem_dim), 'physchem2': torch.zeros(self.physchem_dim),
            'cell_expr': torch.zeros(self.cell_dim),
            'drug1_smiles': 'C', 'drug2_smiles': 'C'
        }

    def augment_molecular_data(self, data):
        return data  # 简化展示