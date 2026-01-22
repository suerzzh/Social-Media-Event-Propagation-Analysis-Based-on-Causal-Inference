"""
PCMCI因果发现分析代码 - B1C数据集
参考tigramite标准用法，针对非线性数据优化

基于tigramite官方文档和最佳实践
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 导入tigramite
try:
    from tigramite import data_processing as pp
    from tigramite.pcmci import PCMCI
    #from tigramite.independence_tests import ParCorr, GPDC, CMIknn
    from tigramite.independence_tests.parcorr import ParCorr
    from tigramite.independence_tests.gpdc import GPDC
    from tigramite.independence_tests.cmiknn import CMIknn
    from tigramite import plotting as tp
    TIGRAMITE_AVAILABLE = True
    print("✅ Tigramite库已安装")
except ImportError as e:
    TIGRAMITE_AVAILABLE = False
    print("❌ 请先安装tigramite: pip install tigramite")
    print("❌ Tigramite 导入失败，真实错误是：")
    print(e)
    exit(1)

def load_data(data_path):
    """
    加载B1C数据集
    
    参数:
        data_path: 数据文件路径
    
    返回:
        data: 观测变量数据（numpy数组，不包含U和time）
        var_names: 变量名称列表
    """
    print(f"\n📂 正在加载数据: {data_path}")
    
    # 读取CSV文件
    df = pd.read_csv(data_path)
    
    print(f"   数据形状: {df.shape}")
    print(f"   列名: {list(df.columns)}")
    
    # 提取观测变量（丢弃U和time列）
    observed_vars = [col for col in df.columns if col.startswith('X')]
    data = df[observed_vars].values  # 转换为numpy数组
    
    var_names = observed_vars
    
    print(f"   ✅ 成功加载 {len(var_names)} 个观测变量: {var_names}")
    print(f"   ✅ 数据维度: {data.shape} (时间点数 × 变量数)")
    
    return data, var_names

def parse_dataset_info(data_path):
    """
    从数据路径中解析数据集信息
    """
    path_str = str(data_path)
    
    # 提取数据集类型
    dataset_type = None
    for ds_type in ['B1C', 'B1', 'A1C', 'A1', 'A2C', 'A2', 'C1C', 'C1', 'C2C', 'C2', 
                    'D1C', 'D1', 'D2C', 'D2', 'D3C', 'D3']:
        if ds_type in path_str:
            dataset_type = ds_type
            break
    
    # 提取噪声类型
    noise_type = None
    if 'Gaussian' in path_str or 'gaussian' in path_str.lower():
        noise_type = 'Gaussian'
    elif 'Students t' in path_str or 'students t' in path_str.lower() or 'student' in path_str.lower():
        noise_type = 'Students_t'
    elif 'laplace' in path_str.lower():
        if '30_70' in path_str or 'gaussian_30_laplace_70' in path_str:
            noise_type = 'Gaussian30_Laplace70'
        elif '50_50' in path_str:
            noise_type = 'Gaussian50_Laplace50'
        elif '70_30' in path_str:
            noise_type = 'Gaussian70_Laplace30'
        else:
            noise_type = 'Mixed'
    else:
        noise_type = 'Unknown'
    
    # 提取变量数
    var_count = None
    for var_num in ['4 variable', '6 variable', '8 variable', '4 Variable', '6 Variable', '8 Variable']:
        if var_num in path_str:
            var_count = var_num.replace('Variable', 'variable').replace(' ', '_')
            break
    
    # 提取Lag
    lag = None
    if 'lag2' in path_str.lower() or 'Lag 2' in path_str or 'lag 2' in path_str:
        lag = 'Lag2'
    elif 'lag3' in path_str.lower() or 'Lag 3' in path_str or 'lag 3' in path_str:
        lag = 'Lag3'
    elif 'lag4' in path_str.lower() or 'Lag 4' in path_str or 'lag 4' in path_str:
        lag = 'Lag4'
    
    # 提取样本量
    sample_size = None
    for n in ['n500', 'n1000', 'n3000', 'n5000']:
        if n in path_str:
            sample_size = n
            break
    
    return {
        'dataset_type': dataset_type or 'Unknown',
        'noise_type': noise_type,
        'var_count': var_count or 'Unknown',
        'lag': lag or 'Unknown',
        'sample_size': sample_size or 'Unknown'
    }

def create_output_directory(data_path):
    """
    根据数据路径创建分类的输出目录
    """
    info = parse_dataset_info(data_path)
    
    base_dir = Path("run_data")
    
    subdirs = [
        info['dataset_type'],
        info['noise_type'],
        f"{info['var_count']}_{info['lag']}_{info['sample_size']}"
    ]
    
    subdirs = [d for d in subdirs if d != 'Unknown']
    
    output_dir = base_dir
    for subdir in subdirs:
        output_dir = output_dir / subdir
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir

def run_pcmci_analysis(data, var_names, tau_max=3, use_nonlinear=True, alpha_level=0.05):
    """
    运行PCMCI因果发现分析
    
    参数:
        data: 时间序列数据 (n_samples, n_vars)
        var_names: 变量名称列表
        tau_max: 最大滞后
        use_nonlinear: 是否使用非线性检验方法（GPDC），True用于非线性数据，False用于线性数据
        alpha_level: 显著性水平
    
    返回:
        results: PCMCI结果字典
        pcmci: PCMCI对象
    """
    print(f"\n🔍 开始运行PCMCI因果发现...")
    print(f"   最大滞后 (tau_max): {tau_max}")
    print(f"   显著性水平 (alpha): {alpha_level}")
    print(f"   检验方法: {'GPDC (非线性)' if use_nonlinear else 'ParCorr (线性)'}")
    
    # 创建数据处理器
    dataframe = pp.DataFrame(data, var_names=var_names)
    
    # 选择独立性检验方法
    # B1C数据集是非线性数据，应该使用GPDC（非线性检验）
    if use_nonlinear:
        # GPDC: 基于高斯过程回归的独立性检验，适合非线性关系
        cond_ind_test = GPDC(significance='analytic', gp_params=None)
    else:
        # ParCorr: 偏相关检验，只适合线性关系
        cond_ind_test = ParCorr(significance='analytic')
    
    # 创建PCMCI对象
    pcmci = PCMCI(
        dataframe=dataframe,
        cond_ind_test=cond_ind_test,
        verbosity=1
    )
    
    # 运行PCMCI
    print("\n   正在计算因果关系（这可能需要一些时间）...")
    results = pcmci.run_pcmci(tau_max=tau_max, alpha_level=alpha_level)
    
    print("   ✅ PCMCI运行完成！")
    
    return results, pcmci

def visualize_causal_graph(pcmci, results, var_names, tau_max, save_path=None):
    """
    可视化因果图
    """
    print(f"\n📊 正在生成因果图...")
    
    if pcmci is None or results is None:
        print("   ❌ 无法可视化：PCMCI结果为空")
        return
    
    #q_matrix = results['q_matrix']
    graph = results['graph']
    val_matrix = results['val_matrix']
    
    # 获取显著的关系
   # link_matrix = pcmci.return_significant_links(
   #     pq_matrix=q_matrix,
   #     val_matrix=val_matrix,
   #     alpha_level=0.05
   # )
    
    # 绘制因果图
    #fig, axes = plt.subplots(1, 1, figsize=(14, 10))
    
    #tp.plot_time_series_graph(
    #    fig_axes=[axes],
    #    val_matrix=val_matrix,
    #    graph=link_matrix,
    #    var_names=var_names,
    #    link_colorbar_label='MCI',
    #    node_colorbar_label='auto-MCI',
    #    link_width=link_matrix,
    #    node_size=0.05,
    #    tau_max=tau_max
    #)
    tp.plot_time_series_graph(
        #fig_axes=axes,
        graph=graph,              # ✅ 用 graph
        val_matrix=val_matrix,
        var_names=var_names,
        #tau_max=tau_max
    )
    
    plt.title('PCMCI发现的因果图', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"   ✅ 因果图已保存: {save_path}")
    
    plt.show()

def print_causal_relationships(results, var_names, tau_max, alpha_level=0.05):
    """
    打印发现的因果关系
    """
    print(f"\n📋 发现的因果关系 (显著性水平: {alpha_level}):")
    print("=" * 80)
    
    if results is None:
        print("   ❌ 无结果可显示")
        return
    
    graph = results['graph']
    val_matrix = results['val_matrix']
    
    # 找出所有显著的关系（包括tau=0的同时关系）
    significant_links = []
    
    for i, var_i in enumerate(var_names):
        for j, var_j in enumerate(var_names):
            # 检查所有tau（包括0，即同时发生的关系）
            for tau in range(0, tau_max + 1):
                if graph[i, j, tau] == 1:
                    correlation = val_matrix[i, j, tau]
                    link_type = "同时发生（无方向）" if tau == 0 else f"滞后{tau}步"
                    significant_links.append({
                        'from': var_i,
                        'to': var_j,
                        'lag': tau,
                        'correlation': correlation,
                        'type': link_type
                    })
    
    if len(significant_links) == 0:
        print("   ⚠️  未发现显著的因果关系")
        print("   可能原因:")
        print("   1. 数据中确实没有因果关系")
        print("   2. 显著性水平设置过高（alpha太小）")
        print("   3. 需要调整PCMCI参数或检验方法")
    else:
        print(f"   ✅ 发现 {len(significant_links)} 个显著的因果关系:\n")
        
        # 按相关性排序
        significant_links.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        for idx, link in enumerate(significant_links, 1):
            if link['lag'] == 0:
                print(f"   {idx}. {link['from']} <--> {link['to']} ({link['type']})")
            else:
                print(f"   {idx}. {link['from']} --[{link['lag']}步滞后]--> {link['to']}")
            print(f"      相关性强度: {link['correlation']:.4f}")
            print()

def save_results(results, var_names, tau_max, output_dir):
    """
    保存结果到文件
    """
    print(f"\n💾 正在保存结果...")
    
    if results is None:
        print("   ❌ 无结果可保存")
        return
    
    #q_matrix = results['q_matrix']
    graph = results['graph']
    val_matrix = results['val_matrix']
    
    # 创建结果DataFrame
    results_list = []
    
    for i, var_i in enumerate(var_names):
        for j, var_j in enumerate(var_names):
            # 包括tau=0（同时发生的关系）
            for tau in range(0, tau_max + 1):
                results_list.append({
                    'From': var_i,
                    'To': var_j,
                    'Lag': tau,
                    'Correlation': val_matrix[i, j, tau],
                    'Causal': graph[i, j, tau] == 1,
                    'Type': 'Simultaneous' if tau == 0 else f'Lag{tau}'
                })
    
    df_results = pd.DataFrame(results_list)
    csv_path = output_dir / "pcmci_results.csv"
    df_results.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"   ✅ 结果已保存: {csv_path}")
    print(f"   共 {len(df_results)} 条关系记录")
    #print(f"   其中 {df_results['Significant'].sum()} 条显著关系")
    print(f"   其中 {df_results['Causal'].sum()} 条因果关系")

def main():
    """
    主函数
    """
    print("=" * 80)
    print("PCMCI因果发现分析 - B1C数据集（非线性数据）")
    print("=" * 80)
    
    # ==================== 步骤1: 选择数据 ====================
    # 推荐配置：6变量，Lag 3，n3000，Gaussian error
    data_path = Path("data/TimeGraph/B1C/Gaussian error/6 variable/Lag 2/nonlinear_confounded_n500_vars6_lag2_gaussian.csv")
    
    # 如果文件不存在，尝试其他路径
    if not data_path.exists():
        print(f"⚠️  文件不存在: {data_path}")
        print("   尝试查找其他可用文件...")
        
        alt_paths = [
            Path("data/TimeGraph/B1C/Gaussian error/4 variable/Lag 2/nonlinear_confounded_n1000_vars4_lag2_gaussian.csv"),
            Path("data/TimeGraph/B1C/Gaussian error/6 variable/lag 3/nonlinear_confounded_n3000_vars6_lag3_gaussian.csv"),
            Path("data/TimeGraph/B1C/Gaussian error/6 variable/Lag 2/nonlinear_confounded_n1000_vars6_lag2_gaussian.csv"),
        ]
        
        data_path = None
        for alt_path in alt_paths:
            if alt_path.exists():
                data_path = alt_path
                print(f"   ✅ 找到替代文件: {alt_path}")
                break
        
        if data_path is None:
            print("   ❌ 未找到数据文件，请检查路径")
            return
    
    # ==================== 步骤2: 加载数据 ====================
    data, var_names = load_data(data_path)
    
    # ==================== 步骤3: 创建输出目录 ====================
    output_dir = create_output_directory(data_path)
    
    info = parse_dataset_info(data_path)
    print(f"\n📊 数据集信息:")
    print(f"   数据集类型: {info['dataset_type']}")
    print(f"   噪声类型: {info['noise_type']}")
    print(f"   变量数: {info['var_count']}")
    print(f"   最大滞后: {info['lag']}")
    print(f"   样本量: {info['sample_size']}")
    print(f"   输出目录: {output_dir}")
    
    # ==================== 步骤4: 运行PCMCI ====================
    # 从文件路径中提取Lag信息
    if "lag2" in str(data_path).lower() or "Lag 2" in str(data_path):
        #tau_max = 2
        #tau_max = 1  这是验证用的
        tau_max = 2
    elif "lag3" in str(data_path).lower() or "Lag 3" in str(data_path):
        #tau_max = 3
        #tau_max = 1  这是验证用的
        tau_max = 3
    elif "lag4" in str(data_path).lower() or "Lag 4" in str(data_path):
        #tau_max = 4
        #tau_max = 1  这是验证用的
        tau_max = 4
    else:
        #tau_max = 3  # 默认值
        #tau_max = 1  这是验证用的
        tau_max = 3
    
    # B1C是非线性数据，使用GPDC（非线性检验方法）
    results, pcmci = run_pcmci_analysis(
        data, 
        var_names, 
        tau_max=tau_max, 
        use_nonlinear=True,  # 使用非线性检验方法
        alpha_level=0.05
    )
    
    if results is None:
        print("\n❌ PCMCI运行失败，请检查错误信息")
        return
    
    # ==================== 步骤5: 调试 - 检查graph矩阵 ====================
    # 检查graph矩阵的结构和值
    graph = results['graph']
    print(f"\n🔍 调试信息:")
    print(f"   graph矩阵形状: {graph.shape}")
    print(f"   graph矩阵中值为1的位置:")
    causal_count = 0
    for i in range(len(var_names)):
        for j in range(len(var_names)):
            for tau in range(0, tau_max + 1):
                if graph[i, j, tau] == 1:
                    causal_count += 1
                    print(f"      graph[{i},{j},{tau}] = 1  →  {var_names[i]} --[Lag{tau}]--> {var_names[j]}")
    print(f"   总共发现 {causal_count} 个因果关系（在graph矩阵中）")
    
    # ==================== 步骤6: 打印结果 ====================
    print_causal_relationships(results, var_names, tau_max)
    
    # ==================== 步骤6: 可视化 ====================
    visualize_causal_graph(
        pcmci, 
        results, 
        var_names, 
        tau_max,
        save_path=output_dir / "pcmci_causal_graph.png"
    )
    
    # ==================== 步骤7: 保存结果 ====================
    save_results(results, var_names, tau_max, output_dir)
    
    # ==================== 步骤8: 保存数据集信息 ====================
    info_df = pd.DataFrame([info])
    info_df.to_csv(output_dir / "dataset_info.csv", index=False, encoding='utf-8-sig')
    print(f"   ✅ 数据集信息已保存: {output_dir / 'dataset_info.csv'}")
    
    print("\n" + "=" * 80)
    print("✅ PCMCI分析完成！")
    print("=" * 80)
    print(f"\n📁 结果文件保存在: {output_dir}")
    print("   1. pcmci_causal_graph.png - 因果图")
    print("   2. pcmci_results.csv - 详细结果数据")
    print("   3. dataset_info.csv - 数据集信息")
    print("\n💡 重要提示:")
    print("   - B1C数据集是非线性数据，使用了GPDC非线性检验方法")
    print("   - 如果结果与预期不符，可以尝试调整参数或检验方法")
    print("   - 对比ground truth图评估结果准确性")

if __name__ == "__main__":
    main()

