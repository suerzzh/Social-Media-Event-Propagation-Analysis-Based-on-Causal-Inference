"""
PCMCI因果发现分析代码 - B1C数据集
修复版本: 正确读取因果关系 + 优化输出目录结构 + 日志输出

基于tigramite官方文档和最佳实践
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
import re
import sys
from datetime import datetime
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 🆕 日志记录器类
class Logger:
    """
    双向输出日志:同时输出到控制台和Markdown文件
    """
    def __init__(self, log_path=None):
        self.terminal = sys.stdout
        self.log_path = log_path
        self.log_content = []
        self.start_time = datetime.now()
        
    def write(self, message):
        """同时写入终端和日志缓冲区"""
        self.terminal.write(message)
        self.log_content.append(message)
    
    def flush(self):
        """刷新终端输出"""
        self.terminal.flush()
    
    def save_to_markdown(self):
        """将日志保存为Markdown文件"""
        if self.log_path is None:
            return
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # 创建Markdown内容
        md_content = f"""# PCMCI因果发现分析运行日志

## 运行信息
- **开始时间**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **结束时间**: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
- **总耗时**: {duration}

---

## 运行输出

```
{''.join(self.log_content)}
```

---

## 日志说明
- 本日志由PCMCI分析程序自动生成
- 包含完整的运行过程和结果输出
- 可用于复现分析过程和结果验证
"""
        
        # 保存到文件
        with open(self.log_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"\n✅ 运行日志已保存: {self.log_path}")
        
# 全局日志对象
logger = None

# 导入tigramite
try:
    from tigramite import data_processing as pp
    from tigramite.pcmci import PCMCI
    from tigramite.independence_tests.parcorr import ParCorr
    from tigramite.independence_tests.gpdc import GPDC
    from tigramite.independence_tests.cmiknn import CMIknn
    from tigramite import plotting as tp
    TIGRAMITE_AVAILABLE = True
    print("✅ Tigramite库已安装")
except ImportError as e:
    TIGRAMITE_AVAILABLE = False
    print("❌ 请先安装tigramite: pip install tigramite")
    print("❌ Tigramite 导入失败,真实错误是:")
    print(e)
    exit(1)

def load_data(data_path):
    """
    加载B1C数据集
    
    参数:
        data_path: 数据文件路径
    
    返回:
        data: 观测变量数据(numpy数组,不包含U和time)
        var_names: 变量名称列表
    """
    print(f"\n📂 正在加载数据: {data_path}")
    
    # 读取CSV文件
    df = pd.read_csv(data_path)
    
    print(f"   数据形状: {df.shape}")
    print(f"   列名: {list(df.columns)}")
    
    # 提取观测变量(丢弃U和time列)
    observed_vars = [col for col in df.columns if col.startswith('X')]
    data = df[observed_vars].values  # 转换为numpy数组
    
    var_names = observed_vars
    
    print(f"   ✅ 成功加载 {len(var_names)} 个观测变量: {var_names}")
    print(f"   ✅ 数据维度: {data.shape} (时间点数 × 变量数)")
    
    return data, var_names

def parse_dataset_info(data_path):
    """
    从数据路径中解析数据集信息 - 修复版本
    使用正则表达式精确匹配,避免子串误匹配问题
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
    
    # 🔧 提取变量数 - 提取数字
    var_count = None
    match = re.search(r'(\d+)\s*[Vv]ariable', path_str)
    if match:
        var_count = match.group(1)  # 只保留数字,如 "6"
    
    # 🔧 提取Lag - 提取数字
    lag = None
    match = re.search(r'[Ll]ag\s*(\d+)', path_str)
    if match:
        lag = match.group(1)  # 只保留数字,如 "2"
    
    # 🔧 修复:使用正则表达式精确匹配样本量
    sample_size = None
    match = re.search(r'_n(\d+)(?:_|\.|/|\\)', path_str)
    if match:
        sample_size = match.group(1)  # 只保留数字,如 "5000"
    else:
        # 备用方案:从长到短匹配
        for n in ['5000', '3000', '1000', '500']:
            if f'n{n}' in path_str:
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
    🔧 优化后的输出目录结构
    格式: run_data/{dataset_type}/{noise_type}/{变量数}variable/lag{数字}/n{样本量}/
    例如: run_data/B1C/Gaussian/6variable/lag2/n5000/
    """
    info = parse_dataset_info(data_path)
    
    base_dir = Path("run_data")
    
    # 构建目录结构: 数据集类型 / 噪声类型 / 变量数 / 滞后数 / 样本量
    subdirs = [
        info['dataset_type'],
        info['noise_type'],
        f"{info['var_count']}variable",  # 例如: 6variable
        f"lag{info['lag']}",              # 例如: lag2
        f"n{info['sample_size']}"         # 例如: n5000
    ]
    
    # 过滤掉Unknown
    subdirs = [d for d in subdirs if 'Unknown' not in d]
    
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
        use_nonlinear: 是否使用非线性检验方法(GPDC)
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
    if use_nonlinear:
        cond_ind_test = GPDC(significance='analytic', gp_params=None)
    else:
        cond_ind_test = ParCorr(significance='analytic')
    
    # 创建PCMCI对象
    pcmci = PCMCI(
        dataframe=dataframe,
        cond_ind_test=cond_ind_test,
        verbosity=1
    )
    
    # 运行PCMCI
    print("\n   正在计算因果关系(这可能需要一些时间)...")
    # 🔧 修复:使用正确的参数名称
    # pc_alpha: PC1阶段的筛选阈值(默认0.2,较宽松)
    # alpha_level: MCI阶段的显著性阈值(通常0.05)
    results = pcmci.run_pcmci(tau_max=tau_max, alpha_level=alpha_level)
    
    print("   ✅ PCMCI运行完成!")
    
    return results, pcmci

def get_significant_links(results, alpha_level=0.05):
    """
    🔧 修复:正确提取显著的因果关系
    使用p_matrix判断显著性,而不是graph矩阵
    
    返回: 显著关系的布尔矩阵 (n_vars, n_vars, tau_max+1)
    """
    p_matrix = results['p_matrix']
    
    # p_matrix < alpha 表示显著
    significant_links = (p_matrix < alpha_level)
    
    return significant_links

def visualize_causal_graph(pcmci, results, var_names, tau_max, alpha_level=0.05, save_path=None):
    """
    可视化因果图
    """
    print(f"\n📊 正在生成因果图...")
    
    if pcmci is None or results is None:
        print("   ❌ 无法可视化:PCMCI结果为空")
        return
    
    val_matrix = results['val_matrix']
    p_matrix = results['p_matrix']
    
    # 🔧 使用p_matrix生成显著性图
    graph = (p_matrix < alpha_level).astype(int)
    
    tp.plot_time_series_graph(
        graph=graph,
        val_matrix=val_matrix,
        var_names=var_names,
    )
    
    plt.title('PCMCI发现的因果图', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"   ✅ 因果图已保存: {save_path}")
    
    plt.show()

def print_causal_relationships(results, var_names, tau_max, alpha_level=0.05):
    """
    🔧 修复:正确打印发现的因果关系
    使用p_matrix判断显著性
    """
    print(f"\n📋 发现的因果关系 (显著性水平: {alpha_level}):")
    print("=" * 80)
    
    if results is None:
        print("   ❌ 无结果可显示")
        return
    
    p_matrix = results['p_matrix']
    val_matrix = results['val_matrix']
    
    # 🔧 使用p_matrix判断显著性
    significant_links = []
    
    for i, var_i in enumerate(var_names):
        for j, var_j in enumerate(var_names):
            for tau in range(0, tau_max + 1):
                # 检查p值是否小于alpha
                if p_matrix[i, j, tau] < alpha_level:
                    pval = p_matrix[i, j, tau]
                    correlation = val_matrix[i, j, tau]
                    link_type = "同时发生(无方向)" if tau == 0 else f"滞后{tau}步"
                    significant_links.append({
                        'from': var_j,  # 注意:j是原因
                        'to': var_i,    # i是结果
                        'lag': tau,
                        'pval': pval,
                        'correlation': correlation,
                        'type': link_type
                    })
    
    if len(significant_links) == 0:
        print("   ⚠️  未发现显著的因果关系")
        print("   可能原因:")
        print("   1. 数据中确实没有因果关系")
        print("   2. 显著性水平设置过高(alpha太小)")
        print("   3. 需要调整PCMCI参数或检验方法")
    else:
        print(f"   ✅ 发现 {len(significant_links)} 个显著的因果关系:\n")
        
        # 按p值排序(最显著的排在前面)
        significant_links.sort(key=lambda x: x['pval'])
        
        for idx, link in enumerate(significant_links, 1):
            if link['lag'] == 0:
                print(f"   {idx}. {link['from']} <--> {link['to']} ({link['type']})")
            else:
                print(f"   {idx}. {link['from']} --[{link['lag']}步滞后]--> {link['to']}")
            print(f"      p值: {link['pval']:.6f} | 相关性强度: {link['correlation']:.4f}")
            print()

def save_results(results, var_names, tau_max, alpha_level, output_dir):
    """
    🔧 修复:保存结果时使用p_matrix判断显著性
    """
    print(f"\n💾 正在保存结果...")
    
    if results is None:
        print("   ❌ 无结果可保存")
        return
    
    p_matrix = results['p_matrix']
    val_matrix = results['val_matrix']
    
    # 创建结果DataFrame
    results_list = []
    
    for i, var_i in enumerate(var_names):
        for j, var_j in enumerate(var_names):
            for tau in range(0, tau_max + 1):
                # 🔧 使用p_matrix判断显著性
                is_causal = (p_matrix[i, j, tau] < alpha_level)
                
                results_list.append({
                    'From': var_j,  # j是原因
                    'To': var_i,    # i是结果
                    'Lag': tau,
                    'P_value': p_matrix[i, j, tau],
                    'Correlation': val_matrix[i, j, tau],
                    'Causal': is_causal,
                    'Type': 'Simultaneous' if tau == 0 else f'Lag{tau}'
                })
    
    df_results = pd.DataFrame(results_list)
    
    # 按是否显著和p值排序
    df_results = df_results.sort_values(['Causal', 'P_value'], ascending=[False, True])
    
    csv_path = output_dir / "pcmci_results.csv"
    df_results.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    # 🔧 统计显著关系数量
    causal_count = df_results['Causal'].sum()
    
    print(f"   ✅ 结果已保存: {csv_path}")
    print(f"   共 {len(df_results)} 条关系记录")
    print(f"   其中 {causal_count} 条显著因果关系 (p < {alpha_level})")
    
    # 额外保存一个只包含显著关系的文件
    if causal_count > 0:
        df_significant = df_results[df_results['Causal'] == True]
        sig_path = output_dir / "pcmci_significant_links.csv"
        df_significant.to_csv(sig_path, index=False, encoding='utf-8-sig')
        print(f"   ✅ 显著关系已单独保存: {sig_path}")

def main():
    """
    主函数
    """
    # 🆕 初始化日志(先输出到临时位置,后面会移动到正确目录)
    global logger
    temp_log_path = Path("temp_pcmci_log.md")
    logger = Logger(temp_log_path)
    sys.stdout = logger
    
    print("=" * 80)
    print("PCMCI因果发现分析 - B1C数据集(非线性数据)")
    print("=" * 80)
    
    # ==================== 步骤1: 选择数据 ====================
    #TimeGraph数据集
    #data_path = Path("data/TimeGraph/B1C/Gaussian error/6 variable/Lag 4/nonlinear_confounded_n3000_vars6_lag4_gaussian.csv")
    data_path = Path("douyin_optimized/n100000/douyin_pcmci_12H_optimized.csv")

    # 如果文件不存在,尝试其他路径
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
            print("   ❌ 未找到数据文件,请检查路径")
            sys.stdout = logger.terminal
            return
    
    # ==================== 步骤2: 加载数据 ====================
    data, var_names = load_data(data_path)
    
    # ==================== 步骤3: 创建输出目录 ====================
    output_dir = create_output_directory(data_path)
    
    # 🆕 更新日志路径到正确的输出目录
    final_log_path = output_dir / "analysis_log.md"
    logger.log_path = final_log_path
    
    info = parse_dataset_info(data_path)
    print(f"\n📊 数据集信息:")
    print(f"   数据集类型: {info['dataset_type']}")
    print(f"   噪声类型: {info['noise_type']}")
    print(f"   变量数: {info['var_count']}")
    print(f"   最大滞后: {info['lag']}")
    print(f"   样本量: {info['sample_size']}")
    print(f"   输出目录: {output_dir}")
    
    # ==================== 步骤4: 运行PCMCI ====================
    if "lag2" in str(data_path).lower() or "Lag 2" in str(data_path):
        tau_max = 2
    elif "lag3" in str(data_path).lower() or "Lag 3" in str(data_path):
        tau_max = 3
    elif "lag4" in str(data_path).lower() or "Lag 4" in str(data_path):
        tau_max = 4
    else:
        tau_max = 3
    
    alpha_level = 0.05
    
    results, pcmci = run_pcmci_analysis(
        data, 
        var_names, 
        tau_max=tau_max, 
        use_nonlinear=True,
        alpha_level=alpha_level
    )
    
    if results is None:
        print("\n❌ PCMCI运行失败,请检查错误信息")
        sys.stdout = logger.terminal
        logger.save_to_markdown()
        return
    
    # ==================== 步骤5: 调试信息 ====================
    p_matrix = results['p_matrix']
    print(f"\n🔍 调试信息:")
    print(f"   p_matrix矩阵形状: {p_matrix.shape}")
    print(f"   显著关系 (p < {alpha_level}):")
    
    causal_count = 0
    for i in range(len(var_names)):
        for j in range(len(var_names)):
            for tau in range(0, tau_max + 1):
                if p_matrix[i, j, tau] < alpha_level:
                    causal_count += 1
                    print(f"      {var_names[j]} --[Lag{tau}]--> {var_names[i]} | p={p_matrix[i,j,tau]:.6f}")
    
    print(f"   总共发现 {causal_count} 个显著因果关系 (p < {alpha_level})")
    
    # ==================== 步骤6: 打印结果 ====================
    print_causal_relationships(results, var_names, tau_max, alpha_level)
    
    # ==================== 步骤7: 可视化 ====================
    visualize_causal_graph(
        pcmci, 
        results, 
        var_names, 
        tau_max,
        alpha_level=alpha_level,
        save_path=output_dir / "pcmci_causal_graph.png"
    )
    
    # ==================== 步骤8: 保存结果 ====================
    save_results(results, var_names, tau_max, alpha_level, output_dir)
    
    # ==================== 步骤9: 保存数据集信息 ====================
    info_df = pd.DataFrame([info])
    info_df.to_csv(output_dir / "dataset_info.csv", index=False, encoding='utf-8-sig')
    print(f"   ✅ 数据集信息已保存: {output_dir / 'dataset_info.csv'}")
    
    print("\n" + "=" * 80)
    print("✅ PCMCI分析完成!")
    print("=" * 80)
    print(f"\n📁 结果文件保存在: {output_dir}")
    print("   1. pcmci_causal_graph.png - 因果图")
    print("   2. pcmci_results.csv - 完整结果数据")
    print("   3. pcmci_significant_links.csv - 仅显著关系")
    print("   4. dataset_info.csv - 数据集信息")
    print("   5. analysis_log.md - 运行日志 🆕")
    print("\n💡 重要提示:")
    print("   - B1C数据集是非线性数据,使用了GPDC非线性检验方法")
    print("   - 使用p_matrix判断显著性,而非graph矩阵")
    print("   - 对比ground truth图评估结果准确性")
    
    # 🆕 恢复标准输出并保存日志
    sys.stdout = logger.terminal
    logger.save_to_markdown()
    
    # 删除临时日志文件
    if temp_log_path.exists():
        temp_log_path.unlink()

if __name__ == "__main__":
    main()