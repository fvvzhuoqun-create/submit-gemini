import pandas as pd
import pubchempy as pcp
import time
import sys
import re


def get_props_from_pubchem(cid):
    """使用PubChemPy获取化合物属性（已使用正确的属性名）"""
    try:
        # 清理CID格式
        if isinstance(cid, str):
            # 处理"CIDsxxxx"格式
            if cid.startswith('CIDs'):
                cid = cid[4:].lstrip('0')
            # 去除可能的非数字字符
            cid = re.sub(r'[^\d]', '', cid)

        # 转换为整数验证
        cid_int = int(cid)
        cid_str = str(cid_int)

        if cid_int <= 0:
            return {'CID': cid, 'logP': None, 'TPSA': None, 'MW': None, 'HBD': None, 'HBA': None,
                    'MolecularFormula': None}

    except (ValueError, TypeError) as e:
        print(f"❌ CID格式错误 {cid}: {str(e)}", file=sys.stderr)
        return {'CID': cid, 'logP': None, 'TPSA': None, 'MW': None, 'HBD': None, 'HBA': None, 'MolecularFormula': None}

    # 使用PubChemPy获取化合物
    try:
        print(f"   正在查询 CID {cid_str}...")
        compound = pcp.Compound.from_cid(cid_str)

        # 调试信息
        print(
            f"   ✅ 成功获取化合物: {compound.iupac_name if hasattr(compound, 'iupac_name') and compound.iupac_name else 'Unknown'}")

        return {
            'CID': cid_str,
            'logP': getattr(compound, 'xlogp', None),  # ✅ 正确属性名
            'TPSA': getattr(compound, 'tpsa', None),  # ✅ 正确属性名
            'MW': getattr(compound, 'molecular_weight', None),  # ✅ 正确属性名
            'HBD': getattr(compound, 'h_bond_donor_count', None),  # ✅ 正确属性名
            'HBA': getattr(compound, 'h_bond_acceptor_count', None),  # ✅ 正确属性名
            'MolecularFormula': getattr(compound, 'molecular_formula', None),  # 新增分子式
            'IUPACName': getattr(compound, 'iupac_name', None),  # 新增IUPAC名称
            'CanonicalSMILES': getattr(compound, 'canonical_smiles', None),  # 新增SMILES
            'InChIKey': getattr(compound, 'inchikey', None),  # 新增InChIKey
            'RotatableBonds': getattr(compound, 'rotatable_bond_count', None),  # 新增可旋转键数
            'HeavyAtoms': getattr(compound, 'heavy_atom_count', None)  # 新增重原子数
        }

    except pcp.PubChemHTTPError as e:
        print(f"❌ PubChem HTTP错误 CID {cid_str}: {str(e)}", file=sys.stderr)
        return {'CID': cid_str, 'logP': None, 'TPSA': None, 'MW': None, 'HBD': None, 'HBA': None,
                'MolecularFormula': None}
    except Exception as e:
        print(f"❌ 获取 CID {cid_str} 失败: {str(e)}", file=sys.stderr)
        return {'CID': cid_str, 'logP': None, 'TPSA': None, 'MW': None, 'HBD': None, 'HBA': None,
                'MolecularFormula': None}


def extract_cids(file_path):
    """从CSV文件中提取CIDs并清理格式"""
    try:
        df = pd.read_csv(file_path)
        cids = []

        if 'cIds' not in df.columns:
            print("❌ 错误: CSV文件中未找到 'cIds' 列")
            return []

        for cids_str in df['cIds'].dropna():
            if isinstance(cids_str, str):
                # 处理"CIDsxxxx"格式
                if cids_str.startswith('CIDs'):
                    num_part = cids_str[4:].lstrip('0')
                    if num_part and num_part.isdigit():
                        cids.append(num_part)
                # 处理纯数字CID
                elif cids_str.isdigit():
                    cids.append(cids_str.lstrip('0'))
                # 处理包含其他字符的情况
                else:
                    # 提取所有数字
                    numbers = re.findall(r'\d+', cids_str)
                    for num in numbers:
                        if num:  # 确保不是空字符串
                            cids.append(num.lstrip('0'))

        unique_cids = list(set([cid for cid in cids if cid]))  # 去重并移除空值
        print(f"📊 原始CID数量: {len(cids)}, 去重后: {len(unique_cids)}")
        return unique_cids

    except Exception as e:
        print(f"❌ 读取文件错误: {str(e)}", file=sys.stderr)
        return []


def main():
    input_file = "Drug_Data_filtered.csv"
    output_file = "Drug_Physical_Properties_PubChemPy.csv"

    print("=" * 50)
    print("🔬 PubChemPy 化合物属性获取工具")
    print("=" * 50)

    print("正在从文件中提取CIDs...")
    cids = extract_cids(input_file)

    if not cids:
        print("❌ 未找到有效的CIDs，程序退出")
        return

    print(f"找到 {len(cids)} 个唯一CID")
    print(f"前10个CID: {cids[:10]}")

    # 测试单个CID
    print("\n" + "=" * 30)
    print("🧪 测试单个CID (2244 - 阿司匹林)")
    print("=" * 30)
    test_result = get_props_from_pubchem("2244")
    print(f"测试结果:")
    for key, value in test_result.items():
        print(f"  {key}: {value}")

    if test_result['logP'] is not None:
        print("✅ 测试成功！")
    else:
        print("❌ 测试失败，请检查网络连接或PubChem服务状态")

    print("\n" + "=" * 50)
    print("🚀 开始批量获取化合物属性...")
    print("=" * 50)

    results = []
    total = len(cids)

    for i, cid in enumerate(cids, 1):
        print(f"\n[{i}/{total}] 处理 CID: {cid}")
        start_time = time.time()

        res = get_props_from_pubchem(cid)
        results.append(res)

        elapsed_time = time.time() - start_time
        success = any(v is not None for k, v in res.items() if k != 'CID')

        status = "✅ 成功" if success else "❌ 失败"
        print(f"   状态: {status} | 耗时: {elapsed_time:.2f}秒")

        # 遵守API速率限制
        if i < total:  # 最后一个不需要等待
            time.sleep(0.3)  # 稍微增加等待时间避免被限制

    # 保存结果
    df_results = pd.DataFrame(results)

    # 重新排列列的顺序，让基本信息在前
    column_order = ['CID', 'IUPACName', 'MolecularFormula', 'MW', 'logP', 'TPSA', 'HBD', 'HBA', 'RotatableBonds',
                    'HeavyAtoms', 'CanonicalSMILES', 'InChIKey']
    existing_columns = [col for col in column_order if col in df_results.columns]
    other_columns = [col for col in df_results.columns if col not in existing_columns]
    df_results = df_results[existing_columns + other_columns]

    df_results.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n✅ 结果已保存至: {output_file}")

    # 统计信息
    print("\n" + "=" * 50)
    print("📊 获取结果统计")
    print("=" * 50)

    stats = {
        'CID': df_results['CID'].notna().sum(),
        'IUPAC名称': df_results['IUPACName'].notna().sum(),
        '分子式': df_results['MolecularFormula'].notna().sum(),
        '分子量': df_results['MW'].notna().sum(),
        'LogP': df_results['logP'].notna().sum(),
        'TPSA': df_results['TPSA'].notna().sum(),
        '氢键供体': df_results['HBD'].notna().sum(),
        '氢键受体': df_results['HBA'].notna().sum(),0
        '可旋转键': df_results['RotatableBonds'].notna().sum(),
        '重原子数': df_results['HeavyAtoms'].notna().sum()
    }

    for prop, count in stats.items():
        percentage = (count / total) * 100
        print(f"{prop}: {count}/{total} ({percentage:.1f}%)")

    # 显示一些成功获取的示例
    success_df = df_results.dropna(subset=['MW']).head(5)
    if not success_df.empty:
        print(f"\n📋 成功获取的示例 (前5个):")
        print(success_df[['CID', 'IUPACName', 'MW', 'logP']].to_string(index=False))


if __name__ == "__main__":
    main()