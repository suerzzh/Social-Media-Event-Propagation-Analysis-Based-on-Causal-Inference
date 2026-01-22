"""
PCMCI因果发现验证代码
用于验证PCMCI方法在B1C数据集上的表现

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体（如果需要显示中文）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 尝试导入tigramite
try:
    from tigramite import data_processing as pp
    from tigramite.pcmci import PCMCI
    from tigramite.independence_tests import ParCorr, GPDC, CMIknn
    from tigramite.plotting import plot_graph
    TIGRAMITE_AVAILABLE = True
    print("✅ Tigramite库已安装")
except ImportError:
    TIGRAMITE_AVAILABLE = False
    print("❌ 请先安装tigramite: pip install tigramite")

def load_b1c_data(data_path):
    """
    加载B1C数据集
    
    参数:
        data_path: 数据文件路径
    
    返回:
        data: 观测变量数据（DataFrame，只包含X1-X6，不包含U和time）
        var_names: 变量名称列表
    """
    print(f"\n📂 正在加载数据: {data_path}")
    
    # 读取CSV文件
    df = pd.read_csv(data_path)
    
    print(f"   数据形状: {df.shape}")
    print(f"   列名: {list(df.columns)}")
    
    # 提取观测变量（丢弃U和time列）
    # 注意：U是混杂变量，在实际研究中你看不到，所以要丢弃
    observed_vars = [col for col in df.columns if col.startswith('X')]
    data = df[observed_vars].values  # 转换为numpy数组
    
    # 变量名称
    var_names = observed_vars
    
    print(f"   ✅ 成功加载 {len(var_names)} 个观测变量: {var_names}")
    print(f"   ✅ 数据维度: {data.shape} (时间点数 × 变量数)")
    
    return data, var_names

def run_pcmci(data, var_names, tau_max=3, alpha_level=0.05):
    """
    运行PCMCI因果发现
    
    参数:
        data: 时间序列数据 (n_samples, n_vars)
        var_names: 变量名称列表
        tau_max: 最大滞后（对应数据集的Lag）
        alpha_level: 显著性水平（0.05表示95%置信度）
    
    返回:
        results: PCMCI结果字典
        pcmci: PCMCI对象（用于后续分析）
    """
    print(f"\n🔍 开始运行PCMCI因果发现...")
    print(f"   最大滞后 (tau_max): {tau_max}")
    print(f"   显著性水平 (alpha): {alpha_level}")
    
    if not TIGRAMITE_AVAILABLE:
        print("❌ Tigramite未安装，无法运行PCMCI")
        return None, None
    
    # 创建数据处理器
    # 这一步将数据转换为tigramite可以处理的格式
    dataframe = pp.DataFrame(data, var_names=var_names)
    
    # 选择独立性检验方法
    # ParCorr: 偏相关检验（适合线性关系）
    # 对于非线性数据，可以使用GPDC或CMIknn
    cond_ind_test = ParCorr(significance='analytic')
    
    # 创建PCMCI对象
    pcmci = PCMCI(
        dataframe=dataframe,
        cond_ind_test=cond_ind_test,
        verbosity=1  # 显示详细信息
    )
    
    # 运行PCMCI
    # 这一步会：
    # 1. 识别条件独立性
    # 2. 构建因果图
    # 3. 估计因果关系
    print("\n   正在计算因果关系...")
    results = pcmci.run_pcmci(tau_max=tau_max, alpha_level=alpha_level)
    
    print("   ✅ PCMCI运行完成！")
    
    return results, pcmci

def visualize_results(pcmci, results, var_names, tau_max, save_path=None):
    """
    可视化PCMCI结果
    
    参数:
        pcmci: PCMCI对象
        results: PCMCI结果
        var_names: 变量名称
        tau_max: 最大滞后
        save_path: 保存路径（可选）
    """
    print(f"\n📊 正在生成可视化结果...")
    
    if pcmci is None or results is None:
        print("   ❌ 无法可视化：PCMCI结果为空")
        return
    
    # 提取显著的关系
    # q_matrix: p值矩阵，值越小越显著
    # val_matrix: 相关系数矩阵
    q_matrix = results['q_matrix']
    val_matrix = results['val_matrix']
    
    # 创建图形
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # 图1: 因果图（有向图）
    print("   正在绘制因果图...")
    link_matrix = pcmci.return_significant_links(
        pq_matrix=q_matrix,
        val_matrix=val_matrix,
        alpha_level=0.05
    )
    
    plot_graph(
        fig_axes=[axes[0]],
        val_matrix=val_matrix,
        link_matrix=link_matrix,
        var_names=var_names,
        link_colorbar_label='MCI',
        node_colorbar_label='auto-MCI',
        tau_max=tau_max
    )
    axes[0].set_title('PCMCI发现的因果图', fontsize=14, fontweight='bold')
    
    # 图2: 相关性热力图
    print("   正在绘制相关性热力图...")
    # 计算平均相关性（跨所有滞后）
    avg_corr = np.mean(np.abs(val_matrix), axis=2)
    sns.heatmap(
        avg_corr,
        xticklabels=var_names,
        yticklabels=var_names,
        annot=True,
        fmt='.3f',
        cmap='RdYlBu_r',
        center=0,
        ax=axes[1],
        cbar_kws={'label': '平均|相关性|'}
    )
    axes[1].set_title('变量间平均相关性', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"   ✅ 图片已保存: {save_path}")
    
    plt.show()

def print_causal_relationships(results, var_names, tau_max, alpha_level=0.05):
    """
    打印发现的因果关系
    
    参数:
        results: PCMCI结果
        var_names: 变量名称
        tau_max: 最大滞后
        alpha_level: 显著性水平
    """
    print(f"\n📋 发现的因果关系 (显著性水平: {alpha_level}):")
    print("=" * 80)
    
    if results is None:
        print("   ❌ 无结果可显示")
        return
    
    q_matrix = results['q_matrix']
    val_matrix = results['val_matrix']
    
    # 找出所有显著的关系
    significant_links = []
    
    for i, var_i in enumerate(var_names):
        for j, var_j in enumerate(var_names):
            for tau in range(1, tau_max + 1):
                # q值小于alpha_level表示显著
                if q_matrix[i, j, tau] < alpha_level:
                    correlation = val_matrix[i, j, tau]
                    significant_links.append({
                        'from': var_i,
                        'to': var_j,
                        'lag': tau,
                        'correlation': correlation,
                        'p_value': q_matrix[i, j, tau]
                    })
    
    if len(significant_links) == 0:
        print("   ⚠️  未发现显著的因果关系")
        print("   可能原因:")
        print("   1. 数据中确实没有因果关系")
        print("   2. 显著性水平设置过高（alpha太小）")
        print("   3. 需要调整PCMCI参数")
    else:
        print(f"   ✅ 发现 {len(significant_links)} 个显著的因果关系:\n")
        
        # 按相关性排序
        significant_links.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        for idx, link in enumerate(significant_links, 1):
            direction = "→" if link['correlation'] > 0 else "←"
            print(f"   {idx}. {link['from']} --[{link['lag']}步滞后]--> {link['to']}")
            print(f"      相关性: {link['correlation']:.4f}")
            print(f"      p值: {link['p_value']:.6f}")
            print()

def save_results_to_file(results, var_names, tau_max, output_path):
    """
    将结果保存到文件
    
    参数:
        results: PCMCI结果
        var_names: 变量名称
        tau_max: 最大滞后
        output_path: 输出文件路径
    """
    print(f"\n💾 正在保存结果到文件...")
    
    if results is None:
        print("   ❌ 无结果可保存")
        return
    
    q_matrix = results['q_matrix']
    val_matrix = results['val_matrix']
    
    # 创建结果DataFrame
    results_list = []
    
    for i, var_i in enumerate(var_names):
        for j, var_j in enumerate(var_names):
            for tau in range(1, tau_max + 1):
                results_list.append({
                    'From': var_i,
                    'To': var_j,
                    'Lag': tau,
                    'Correlation': val_matrix[i, j, tau],
                    'P_Value': q_matrix[i, j, tau],
                    'Significant': q_matrix[i, j, tau] < 0.05
                })
    
    df_results = pd.DataFrame(results_list)
    df_results.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"   ✅ 结果已保存: {output_path}")
    print(f"   共 {len(df_results)} 条关系记录")
    print(f"   其中 {df_results['Significant'].sum()} 条显著关系")

def parse_dataset_info(data_path):
    """
    从数据路径中解析数据集信息
    
    参数:
        data_path: 数据文件路径
    
    返回:
        dataset_info: 包含数据集信息的字典
    """
    path_str = str(data_path)
    
    # 提取数据集类型（B1C, A1, A1C等）
    dataset_type = None
    for ds_type in ['B1C', 'B1', 'A1C', 'A1', 'A2C', 'A2', 'C1C', 'C1', 'C2C', 'C2', 'D1C', 'D1', 'D2C', 'D2', 'D3C', 'D3']:
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
        # 提取混合比例
        if '30_70' in path_str or 'gaussian_30_laplace_70' in path_str:
            noise_type = 'Gaussian30_Laplace70'
        elif '50_50' in path_str or 'gaussian_50_laplace_50' in path_str:
            noise_type = 'Gaussian50_Laplace50'
        elif '70_30' in path_str or 'gaussian_70_laplace_30' in path_str:
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
    
    参数:
        data_path: 数据文件路径
    
    返回:
        output_dir: 输出目录路径
    """
    # 解析数据集信息
    info = parse_dataset_info(data_path)
    
    # 创建目录结构: run_data/数据集类型/噪声类型/变量数_Lag_样本量
    base_dir = Path("run_data")
    
    # 构建子目录路径
    subdirs = [
        info['dataset_type'],
        info['noise_type'],
        f"{info['var_count']}_{info['lag']}_{info['sample_size']}"
    ]
    
    # 过滤掉Unknown的目录
    subdirs = [d for d in subdirs if d != 'Unknown']
    
    # 创建完整路径
    output_dir = base_dir
    for subdir in subdirs:
        output_dir = output_dir / subdir
    
    # 创建目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir

def main():
    """
    主函数：完整的PCMCI验证流程
    """
    print("=" * 80)
    print("PCMCI因果发现验证 - B1C数据集")
    print("=" * 80)
    
    # ==================== 步骤1: 选择数据 ====================
    # 推荐配置：6变量，Lag 3，n3000，Gaussian error
    data_path = Path("data/TimeGraph/B1C/Gaussian error/6 variable/Lag 3/nonlinear_confounded_n3000_vars6_lag3_gaussian.csv")
    
    # 如果文件不存在，尝试其他路径
    if not data_path.exists():
        print(f"⚠️  文件不存在: {data_path}")
        print("   尝试查找其他可用文件...")
        
        # 尝试4变量版本
        alt_path = Path("data/TimeGraph/B1C/Gaussian error/4 variable/Lag 2/nonlinear_confounded_n1000_vars4_lag2_gaussian.csv")
        if alt_path.exists():
            data_path = alt_path
            print(f"   ✅ 找到替代文件: {alt_path}")
        else:
            print("   ❌ 未找到数据文件，请检查路径")
            return
    
    # ==================== 步骤2: 加载数据 ====================
    data, var_names = load_b1c_data(data_path)
    
    # ==================== 步骤3: 运行PCMCI ====================
    # 从文件路径中提取Lag信息
    if "lag2" in str(data_path).lower() or "Lag 2" in str(data_path):
        tau_max = 2
    elif "lag3" in str(data_path).lower() or "Lag 3" in str(data_path):
        tau_max = 3
    elif "lag4" in str(data_path).lower() or "Lag 4" in str(data_path):
        tau_max = 4
    else:
        tau_max = 3  # 默认值
    
    results, pcmci = run_pcmci(data, var_names, tau_max=tau_max, alpha_level=0.05)
    
    if results is None:
        print("\n❌ PCMCI运行失败，请检查错误信息")
        return
    
    # ==================== 步骤4: 打印结果 ====================
    print_causal_relationships(results, var_names, tau_max)
    
    # ==================== 步骤5: 创建分类输出目录 ====================
    output_dir = create_output_directory(data_path)
    
    # 打印数据集信息
    info = parse_dataset_info(data_path)
    print(f"\n📊 数据集信息:")
    print(f"   数据集类型: {info['dataset_type']}")
    print(f"   噪声类型: {info['noise_type']}")
    print(f"   变量数: {info['var_count']}")
    print(f"   最大滞后: {info['lag']}")
    print(f"   样本量: {info['sample_size']}")
    print(f"   输出目录: {output_dir}")
    
    # ==================== 步骤6: 可视化 ====================
    visualize_results(
        pcmci, 
        results, 
        var_names, 
        tau_max,
        save_path=output_dir / "pcmci_causal_graph.png"
    )
    
    # ==================== 步骤7: 保存结果 ====================
    save_results_to_file(
        results,
        var_names,
        tau_max,
        output_dir / "pcmci_results.csv"
    )
    
    # ==================== 步骤8: 保存数据集信息 ====================
    info_df = pd.DataFrame([info])
    info_df.to_csv(output_dir / "dataset_info.csv", index=False, encoding='utf-8-sig')
    print(f"   ✅ 数据集信息已保存: {output_dir / 'dataset_info.csv'}")
    
    print("\n" + "=" * 80)
    print("✅ PCMCI验证完成！")
    print("=" * 80)
    print(f"\n📁 结果文件保存在: {output_dir}")
    print("   1. pcmci_causal_graph.png - 因果图可视化")
    print("   2. pcmci_results.csv - 详细结果数据")
    print("   3. dataset_info.csv - 数据集信息")
    print("\n💡 下一步:")
    print("   1. 查看生成的因果图，理解发现的因果关系")
    print("   2. 分析pcmci_results.csv中的显著关系")
    print("   3. 对比ground truth图（如果有）评估准确性")
    print("   4. 尝试不同的参数设置，观察结果变化")

if __name__ == "__main__":
    main()

