import pandas as pd
import pubchempy as pcp
import time
import sys
import re
import os  # 新增：用于检查文件是否存在

def get_props_from_pubchem(cid):
    """使用PubChemPy获取化合物属性"""
    cid_str = str(cid)
    try:
        # 清理CID格式
        if isinstance(cid, str):
            if cid.startswith('CIDs'):
                cid = cid[4:].lstrip('0')
            cid = re.sub(r'[^\d]', '', cid)

        cid_int = int(cid)
        cid_str = str(cid_int)

        if cid_int <= 0:
            raise ValueError("CID non-positive")

    except (ValueError, TypeError):
        # 静默失败，仅返回空结构，避免刷屏
        return {'CID': cid_str, 'logP': None, 'TPSA': None, 'MW': None, 'Status': 'Format Error'}

    try:
        # 使用PubChemPy获取化合物
        compound = pcp.Compound.from_cid(cid_str)
        
        return {
            'CID': cid_str,
            'IUPACName': getattr(compound, 'iupac_name', None),
            'MolecularFormula': getattr(compound, 'molecular_formula', None),
            'MW': getattr(compound, 'molecular_weight', None),
            'logP': getattr(compound, 'xlogp', None),
            'TPSA': getattr(compound, 'tpsa', None),
            'HBD': getattr(compound, 'h_bond_donor_count', None),
            'HBA': getattr(compound, 'h_bond_acceptor_count', None),
            'RotatableBonds': getattr(compound, 'rotatable_bond_count', None),
            'HeavyAtoms': getattr(compound, 'heavy_atom_count', None),
            'CanonicalSMILES': getattr(compound, 'canonical_smiles', None),
            'InChIKey': getattr(compound, 'inchikey', None),
            'Status': 'Success' # 标记成功状态
        }

    except Exception as e:
        # 捕获所有网络或解析错误
        return {'CID': cid_str, 'logP': None, 'MW': None, 'Status': 'Network/API Error'}

def extract_cids(file_path):
    """从CSV文件中提取CIDs"""
    if not os.path.exists(file_path):
        print(f"❌ 错误: 文件 {file_path} 不存在")
        return []
        
    try:
        df = pd.read_csv(file_path)
        cids = []

        if 'cIds' not in df.columns:
            print("❌ 错误: CSV文件中未找到 'cIds' 列")
            return []

        print("正在解析 CIDs...")
        for cids_str in df['cIds'].dropna():
            cids_str = str(cids_str)
            numbers = re.findall(r'\d+', cids_str)
            for num in numbers:
                if num:
                    cids.append(num.lstrip('0'))

        unique_cids = list(set([cid for cid in cids if cid]))
        print(f"📊 原始CID数量: {len(cids)}, 去重后: {len(unique_cids)}")
        return unique_cids

    except Exception as e:
        print(f"❌ 读取文件错误: {str(e)}", file=sys.stderr)
        return []

def save_batch(results, output_file, is_first_batch):
    """分批保存数据到CSV"""
    if not results:
        return

    df_batch = pd.DataFrame(results)
    
    # 定义列顺序
    column_order = ['CID', 'IUPACName', 'MolecularFormula', 'MW', 'logP', 'TPSA', 'HBD', 'HBA', 
                   'RotatableBonds', 'HeavyAtoms', 'CanonicalSMILES', 'InChIKey', 'Status']
    
    # 确保所有列都存在
    for col in column_order:
        if col not in df_batch.columns:
            df_batch[col] = None
            
    df_batch = df_batch[column_order]

    # 追加模式写入 ('a')
    mode = 'w' if is_first_batch else 'a'
    header = is_first_batch # 只有第一批次写入表头
    
    try:
        df_batch.to_csv(output_file, mode=mode, header=header, index=False, encoding='utf-8-sig')
    except PermissionError:
        print(f"\n❌ 无法写入文件 {output_file}，请确保文件未被打开！")

def main():
    input_file = "Drug_Data_filtered.csv"
    output_file = "Drug_Physical_Properties_PubChemPy.csv"
    BATCH_SIZE = 50  # 每处理50个保存一次

    print("=" * 50)
    print("🔬 PubChemPy 化合物属性获取工具 (防崩溃版)")
    print("=" * 50)

    cids = extract_cids(input_file)
    if not cids: return

    # 如果文件已存在，询问是否覆盖
    if os.path.exists(output_file):
        print(f"⚠️  警告: 输出文件 {output_file} 已存在，程序将覆盖它。")
        time.sleep(2) # 给用户一点反应时间

    print(f"\n🚀 开始处理 {len(cids)} 个化合物...")
    print(f"💾 数据将每 {BATCH_SIZE} 条自动保存一次至 {output_file}")
    
    results_buffer = []
    total = len(cids)
    processed_count = 0
    start_time_all = time.time()
    
    # 标记是否为第一次写入（用于控制表头）
    is_first_write = True

    try:
        for i, cid in enumerate(cids, 1):
            # 获取数据
            res = get_props_from_pubchem(cid)
            results_buffer.append(res)
            processed_count += 1
            
            # --- 优化输出：不在每一行都换行打印 ---
            # 使用 \r 回车符覆盖当前行，避免控制台刷屏
            status_symbol = "✅" if res['Status'] == 'Success' else "⚠️"
            elapsed = time.time() - start_time_all
            avg_speed = processed_count / elapsed if elapsed > 0 else 0
            
            sys.stdout.write(f"\r[{i}/{total}] 处理 CID: {cid} {status_symbol} | 速度: {avg_speed:.2f} 个/秒")
            sys.stdout.flush()

            # --- 分批保存逻辑 ---
            if len(results_buffer) >= BATCH_SIZE:
                save_batch(results_buffer, output_file, is_first_write)
                results_buffer = [] # 清空缓存
                is_first_write = False # 后续批次不再写入表头
                
                # 稍微暂停，避免请求过于频繁被封IP
                time.sleep(1) 

            # 基础限流
            time.sleep(0.2)

        # 循环结束，保存剩余的数据
        if results_buffer:
            save_batch(results_buffer, output_file, is_first_write)
            
        print(f"\n\n✅ 所有任务完成！结果已保存至: {output_file}")

    except KeyboardInterrupt:
        print("\n\n🛑 用户手动停止！正在保存已获取的数据...")
        if results_buffer:
            save_batch(results_buffer, output_file, is_first_write)
        print("✅ 数据已安全保存。")
        
    except Exception as e:
        print(f"\n\n❌ 发生意外错误: {str(e)}")
        if results_buffer:
            save_batch(results_buffer, output_file, is_first_write)
        print("✅ 崩溃前的数据已保存。")

if __name__ == "__main__":
    main()
