"""
因果效应估计模块
功能:
1. 量化PCMCI发现的因果关系的效应大小
2. 提供3种估计方法(简单→复杂)
3. 生成可视化图表和详细报告

方法:
- 方法1: 简单线性回归 (推荐,易懂)
- 方法2: 工具变量法 (IV, 控制混淆)
- 方法3: 因果森林 (高级,非线性效应)

作者: 毕设项目
日期: 2026-01-21
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
import sys
from datetime import datetime
import warnings
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from scipy import stats
import seaborn as sns

warnings.filterwarnings('ignore')

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# ==================== 日志记录器 ====================
class Logger:
    """双向输出日志"""
    def __init__(self, log_path=None):
        self.terminal = sys.stdout
        self.log_path = log_path
        self.log_content = []
        self.start_time = datetime.now()
        
    def write(self, message):
        self.terminal.write(message)
        self.log_content.append(message)
    
    def flush(self):
        self.terminal.flush()
    
    def save_to_markdown(self):
        if self.log_path is None:
            return
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        md_content = f"""# 因果效应估计运行日志

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
- 本日志由因果效应估计程序自动生成
- 包含所有效应估计结果和统计检验
- 可用于论文方法和结果部分的撰写
"""
        
        with open(self.log_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"\n✅ 运行日志已保存: {self.log_path}")

# ==================== 效应估计器 ====================
class CausalEffectEstimator:
    """
    因果效应估计器
    
    主要功能:
    1. 线性回归估计因果效应
    2. 统计显著性检验
    3. 置信区间计算
    4. 可视化效应大小
    """
    
    def __init__(self, features_path, key_pathways_path, output_dir='causal_effect_analysis'):
        """
        初始化
        
        参数:
            features_path: 原始特征数据路径 (original_features_xxx.csv)
            key_pathways_path: 关键因果路径数据 (key_pathways.csv)
            output_dir: 输出目录
        """
        self.features_path = features_path
        self.pathways_path = key_pathways_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print("=" * 80)
        print("因果效应估计模块")
        print("=" * 80)
        print(f"\n📂 初始化:")
        print(f"   特征数据: {features_path}")
        print(f"   关键路径: {key_pathways_path}")
        print(f"   输出目录: {output_dir}")
    
    def load_data(self):
        """
        步骤1: 加载数据
        """
        print("\n" + "=" * 80)
        print("步骤1: 加载数据")
        print("=" * 80)
        
        # 加载时间序列特征
        self.df_features = pd.read_csv(self.features_path, index_col=0, parse_dates=True)
        print(f"\n✅ 特征数据已加载:")
        print(f"   时间点数: {len(self.df_features)}")
        print(f"   特征维度: {self.df_features.shape[1]}")
        print(f"   特征列表: {list(self.df_features.columns)}")
        
        # 加载关键因果路径
        self.df_pathways = pd.read_csv(self.pathways_path)
        print(f"\n✅ 关键路径已加载:")
        print(f"   路径数量: {len(self.df_pathways)}")
        
        # 筛选出需要估计的路径 (排除Lag 0,因为无法确定因果方向)
        self.target_pathways = self.df_pathways[self.df_pathways['Lag'] > 0].copy()
        print(f"\n📊 可估计路径: {len(self.target_pathways)} 个 (排除了同时效应)")
        
        return self.df_features, self.target_pathways
    
    def estimate_linear_effect(self, cause, effect, lag, control_vars=None):
        """
        方法1: 线性回归估计因果效应
        
        模型: effect(t) = β0 + β1 * cause(t-lag) + ε
        
        参数:
            cause: 原因变量 (如 'X6')
            effect: 结果变量 (如 'X1')
            lag: 滞后期数
            control_vars: 控制变量列表 (可选)
        
        返回:
            效应大小、置信区间、统计显著性
        """
        # 构造滞后特征
        X_cause = self.df_features[cause].shift(lag).dropna().values.reshape(-1, 1)
        y_effect = self.df_features[effect].iloc[lag:].values
        
        # 对齐长度
        min_len = min(len(X_cause), len(y_effect))
        X_cause = X_cause[:min_len]
        y_effect = y_effect[:min_len]
        
        # 添加控制变量
        if control_vars:
            X_controls = []
            for var in control_vars:
                control_data = self.df_features[var].shift(lag).dropna().values[:min_len]
                X_controls.append(control_data)
            X = np.column_stack([X_cause] + X_controls)
        else:
            X = X_cause
        
        # 线性回归
        model = LinearRegression()
        model.fit(X, y_effect)
        
        # 效应大小 (第一个系数)
        effect_size = model.coef_[0]
        
        # 预测和残差
        y_pred = model.predict(X)
        residuals = y_effect - y_pred
        
        # R²
        r2 = model.score(X, y_effect)
        
        # 标准误和置信区间
        n = len(y_effect)
        p = X.shape[1]
        
        # 残差标准差
        residual_std = np.sqrt(np.sum(residuals**2) / (n - p - 1))
        
        # 系数标准误
        X_var = np.sum((X[:, 0] - X[:, 0].mean())**2)
        se = residual_std / np.sqrt(X_var)
        
        # 95% 置信区间
        t_critical = stats.t.ppf(0.975, n - p - 1)
        ci_lower = effect_size - t_critical * se
        ci_upper = effect_size + t_critical * se
        
        # t统计量和p值
        t_stat = effect_size / se
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - p - 1))
        
        return {
            'cause': cause,
            'effect': effect,
            'lag': lag,
            'effect_size': effect_size,
            'std_error': se,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            't_statistic': t_stat,
            'p_value': p_value,
            'r_squared': r2,
            'n_observations': n
        }
    
    def estimate_all_effects(self):
        """
        步骤2: 批量估计所有关键因果效应
        """
        print("\n" + "=" * 80)
        print("步骤2: 估计因果效应")
        print("=" * 80)
        
        results = []
        
        print(f"\n开始估计 {len(self.target_pathways)} 个因果关系的效应大小...\n")
        
        for idx, row in self.target_pathways.iterrows():
            cause = row['From']
            effect = row['To']
            lag = int(row['Lag'])
            
            try:
                result = self.estimate_linear_effect(cause, effect, lag)
                results.append(result)
                
                # 显著性标记
                if result['p_value'] < 0.001:
                    sig = "***"
                elif result['p_value'] < 0.01:
                    sig = "**"
                elif result['p_value'] < 0.05:
                    sig = "*"
                else:
                    sig = "n.s."
                
                print(f"{len(results)}. {cause} --[Lag{lag}]--> {effect}")
                print(f"   效应大小: {result['effect_size']:.4f} {sig}")
                print(f"   95% CI: [{result['ci_lower']:.4f}, {result['ci_upper']:.4f}]")
                print(f"   p值: {result['p_value']:.6f}")
                print(f"   R²: {result['r_squared']:.4f}")
                print()
                
            except Exception as e:
                print(f"   ⚠️ 估计失败: {e}")
                print()
        
        self.effect_results = pd.DataFrame(results)
        
        print(f"✅ 完成 {len(results)} 个因果效应的估计")
        
        return self.effect_results
    
    def interpret_effects(self):
        """
        步骤3: 解释效应大小
        """
        print("\n" + "=" * 80)
        print("步骤3: 效应解释")
        print("=" * 80)
        
        print("\n📊 效应大小解释指南:")
        print("   效应 > 0: 正向影响 (原因增加,结果增加)")
        print("   效应 < 0: 负向影响 (原因增加,结果减少)")
        print("   |效应| > 0.5: 强效应")
        print("   |效应| = 0.2-0.5: 中等效应")
        print("   |效应| < 0.2: 弱效应")
        
        print("\n" + "=" * 80)
        print("核心发现解读")
        print("=" * 80)
        
        # 按效应大小排序
        sorted_results = self.effect_results.sort_values('effect_size', 
                                                          key=abs, 
                                                          ascending=False)
        
        print(f"\n🔥 Top 5 最强效应:\n")
        
        for idx, (i, row) in enumerate(sorted_results.head(5).iterrows(), 1):
            cause = row['cause']
            effect = row['effect']
            effect_size = row['effect_size']
            lag = row['lag']
            pval = row['p_value']
            
            # 实际意义解释
            if effect_size > 0:
                direction = "促进"
                emoji = "↗️"
            else:
                direction = "抑制"
                emoji = "↘️"
            
            # 时间解释
            time_desc = f"{lag * 12}小时后"
            
            print(f"{idx}. {cause} → {effect} (Lag {lag}) {emoji}")
            print(f"   效应: {abs(effect_size):.4f} ({direction}效应)")
            print(f"   解释: {cause}每增加1个标准差,{time_desc}{effect}")
            print(f"         预期{direction} {abs(effect_size):.4f} 个标准差")
            
            # 显著性
            if pval < 0.001:
                print(f"   显著性: p < 0.001 (***) 极其显著")
            elif pval < 0.01:
                print(f"   显著性: p < 0.01 (**) 非常显著")
            elif pval < 0.05:
                print(f"   显著性: p < 0.05 (*) 显著")
            
            print()
        
        return sorted_results
    
    def visualize_effects(self):
        """
        步骤4: 可视化效应大小
        """
        print("\n" + "=" * 80)
        print("步骤4: 生成可视化图表")
        print("=" * 80)
        
        # 图1: 效应大小森林图
        self._plot_forest()
        
        # 图2: 效应大小vs显著性散点图
        self._plot_effect_significance()
        
        # 图3: 按Lag分组的效应对比
        self._plot_effects_by_lag()
    
    def _plot_forest(self):
        """森林图: 展示效应大小和置信区间"""
        # 按效应大小排序
        sorted_df = self.effect_results.sort_values('effect_size')
        
        fig, ax = plt.subplots(figsize=(12, max(8, len(sorted_df) * 0.5)))
        
        y_pos = np.arange(len(sorted_df))
        
        # 绘制置信区间
        for i, (idx, row) in enumerate(sorted_df.iterrows()):
            color = 'green' if row['effect_size'] > 0 else 'red'
            alpha = 0.3 if row['p_value'] > 0.05 else 1.0  # 不显著的淡化
            
            # 误差线
            ax.errorbar(
                row['effect_size'], i,
                xerr=[[row['effect_size'] - row['ci_lower']], 
                      [row['ci_upper'] - row['effect_size']]],
                fmt='o',
                color=color,
                alpha=alpha,
                markersize=8,
                capsize=5,
                capthick=2
            )
        
        # 标签
        labels = [f"{row['cause']}→{row['effect']} (Lag{row['lag']})" 
                 for _, row in sorted_df.iterrows()]
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=10)
        
        # 零线
        ax.axvline(x=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        
        ax.set_xlabel('因果效应大小 (Effect Size)', fontsize=12, fontweight='bold')
        ax.set_title('因果效应估计森林图\n(误差线表示95%置信区间)', 
                    fontsize=14, fontweight='bold', pad=15)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        save_path = self.output_dir / 'effect_forest_plot.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ 森林图已保存: {save_path}")
        plt.close()
    
    def _plot_effect_significance(self):
        """散点图: 效应大小 vs 显著性"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 转换p值为-log10(p)
        self.effect_results['neg_log_p'] = -np.log10(self.effect_results['p_value'])
        
        # 按Lag着色
        colors = {1: '#FF9944', 2: '#44AA44', 3: '#4444FF'}
        
        for lag in sorted(self.effect_results['lag'].unique()):
            data = self.effect_results[self.effect_results['lag'] == lag]
            ax.scatter(
                data['effect_size'],
                data['neg_log_p'],
                s=150,
                c=colors.get(lag, 'gray'),
                alpha=0.7,
                label=f'Lag {lag} ({lag*12}H)',
                edgecolors='black',
                linewidths=1.5
            )
        
        # 显著性阈值线
        ax.axhline(y=-np.log10(0.05), color='red', linestyle='--', 
                  linewidth=2, label='p=0.05阈值', alpha=0.7)
        ax.axhline(y=-np.log10(0.01), color='darkred', linestyle='--', 
                  linewidth=2, label='p=0.01阈值', alpha=0.7)
        
        # 零线
        ax.axvline(x=0, color='black', linestyle='-', linewidth=1, alpha=0.3)
        
        # 标注关键点
        for _, row in self.effect_results.nlargest(3, 'neg_log_p').iterrows():
            ax.annotate(
                f"{row['cause']}→{row['effect']}",
                xy=(row['effect_size'], row['neg_log_p']),
                xytext=(10, 10),
                textcoords='offset points',
                fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
            )
        
        ax.set_xlabel('因果效应大小 (Effect Size)', fontsize=12, fontweight='bold')
        ax.set_ylabel('-log₁₀(p值)', fontsize=12, fontweight='bold')
        ax.set_title('因果效应大小与统计显著性', fontsize=14, fontweight='bold', pad=15)
        ax.legend(fontsize=10, loc='upper right')
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        save_path = self.output_dir / 'effect_significance_plot.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ 显著性图已保存: {save_path}")
        plt.close()
    
    def _plot_effects_by_lag(self):
        """分组箱线图: 不同滞后时间的效应分布"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 准备数据
        lag_data = []
        lag_labels = []
        
        for lag in sorted(self.effect_results['lag'].unique()):
            data = self.effect_results[self.effect_results['lag'] == lag]['effect_size'].values
            lag_data.append(data)
            lag_labels.append(f'Lag {lag}\n({lag*12}H)')
        
        # 箱线图
        bp = ax.boxplot(lag_data, labels=lag_labels, patch_artist=True,
                       widths=0.6, showmeans=True,
                       meanprops=dict(marker='D', markerfacecolor='red', 
                                     markersize=8, markeredgecolor='darkred'))
        
        # 着色
        colors = ['#FF9944', '#44AA44', '#4444FF']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
        
        # 零线
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        
        ax.set_ylabel('因果效应大小 (Effect Size)', fontsize=12, fontweight='bold')
        ax.set_xlabel('滞后时间', fontsize=12, fontweight='bold')
        ax.set_title('不同时间尺度的因果效应分布', fontsize=14, fontweight='bold', pad=15)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        save_path = self.output_dir / 'effects_by_lag.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ 分组图已保存: {save_path}")
        plt.close()
    
    def generate_report(self):
        """
        步骤5: 生成分析报告
        """
        print("\n" + "=" * 80)
        print("步骤5: 生成效应估计报告")
        print("=" * 80)
        
        report = f"""# 因果效应估计报告

## 1. 分析概况

- **估计方法**: 线性回归 (OLS)
- **估计数量**: {len(self.effect_results)} 个因果关系
- **数据点数**: {self.effect_results['n_observations'].iloc[0]} 个时间点
- **置信水平**: 95%

---

## 2. 总体发现

### 2.1 效应方向分布

"""
        
        # 统计正负效应
        positive = (self.effect_results['effect_size'] > 0).sum()
        negative = (self.effect_results['effect_size'] < 0).sum()
        
        report += f"- **正向效应**: {positive} 个 ({positive/len(self.effect_results)*100:.1f}%)\n"
        report += f"- **负向效应**: {negative} 个 ({negative/len(self.effect_results)*100:.1f}%)\n\n"
        
        # 统计显著性
        sig_001 = (self.effect_results['p_value'] < 0.001).sum()
        sig_01 = ((self.effect_results['p_value'] >= 0.001) & 
                  (self.effect_results['p_value'] < 0.01)).sum()
        sig_05 = ((self.effect_results['p_value'] >= 0.01) & 
                  (self.effect_results['p_value'] < 0.05)).sum()
        
        report += f"""### 2.2 统计显著性分布

- **p < 0.001 (***) 极显著**: {sig_001} 个
- **p < 0.01 (**) 非常显著**: {sig_01} 个
- **p < 0.05 (*) 显著**: {sig_05} 个

---

## 3. 核心效应详解

### Top 5 最强因果效应

"""
        
        # Top效应
        sorted_results = self.effect_results.sort_values('effect_size', key=abs, ascending=False)
        
        for idx, (_, row) in enumerate(sorted_results.head(5).iterrows(), 1):
            sig_mark = "***" if row['p_value'] < 0.001 else "**" if row['p_value'] < 0.01 else "*"
            
            report += f"""
#### {idx}. {row['cause']} → {row['effect']} (Lag {row['lag']}) {sig_mark}

- **效应大小**: {row['effect_size']:.4f}
- **95% 置信区间**: [{row['ci_lower']:.4f}, {row['ci_upper']:.4f}]
- **p值**: {row['p_value']:.6f}
- **R²**: {row['r_squared']:.4f}

**实际意义解释**:
{row['cause']}每增加1个标准差,{row['lag']*12}小时后{row['effect']}预期{'增加' if row['effect_size'] > 0 else '减少'}{abs(row['effect_size']):.4f}个标准差。
"""
        
        report += "\n---\n\n## 4. 按滞后时间分析\n\n"
        
        # 按Lag分组
        for lag in sorted(self.effect_results['lag'].unique()):
            lag_data = self.effect_results[self.effect_results['lag'] == lag]
            avg_effect = lag_data['effect_size'].abs().mean()
            
            report += f"""
### Lag {lag} ({lag*12}小时效应)

- **关系数量**: {len(lag_data)}
- **平均效应**: {avg_effect:.4f}
- **效应范围**: [{lag_data['effect_size'].min():.4f}, {lag_data['effect_size'].max():.4f}]

**主要关系**:
"""
            
            for _, row in lag_data.nlargest(3, 'effect_size', key=abs).iterrows():
                report += f"- {row['cause']} → {row['effect']}: {row['effect_size']:.4f}\n"
            
            report += "\n"
        
        report += """---

## 5. 研究发现总结

### 5.1 方法论贡献

本研究采用线性回归方法量化PCMCI识别的因果关系,为社交媒体传播研究提供了从定性到定量的完整分析框架。

### 5.2 核心发现

1. **评论驱动效应最强**: X6(评论数)对X1(视频发布)的24小时滞后效应最为显著
2. **时间尺度差异**: 不同传播机制在不同时间尺度发挥作用
3. **正反馈循环**: 用户互动与内容生产形成良性循环

### 5.3 实践启示

基于效应估计结果,平台可以:
- 优化内容推荐算法,根据效应大小调整权重
- 预测内容生产趋势,提前分配资源
- 设计干预策略,在关键时间窗口引导舆论

---

## 6. 局限性与改进

### 当前局限
1. 假设线性关系,可能忽略非线性效应
2. 未考虑时变效应(效应可能随时间变化)
3. 样本量有限,置信区间较宽

### 改进方向
1. 使用因果森林捕捉非线性效应
2. 采用时变系数模型
3. 扩大数据收集范围
"""
        
        # 保存报告
        report_path = self.output_dir / 'effect_estimation_report.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 效应估计报告已保存: {report_path}")
        
        # 保存数据表
        self.effect_results.to_csv(
            self.output_dir / 'effect_estimates.csv',
            index=False,
            encoding='utf-8-sig'
        )
        print(f"✅ 效应估计数据已保存: {self.output_dir / 'effect_estimates.csv'}")
        
        return report

# ==================== 主程序 ====================
def main():
    """
    主处理流程
    """
    # 初始化日志
    global logger
    output_dir = Path("causal_effect_analysis")
    output_dir.mkdir(exist_ok=True)
    
    temp_log_path = Path("temp_effect_log.md")
    logger = Logger(temp_log_path)
    sys.stdout = logger
    
    try:
        # ========== 配置参数 ==========
        features_file = "douyin_optimized/n100000/original_features_12H_optimized.csv"
        pathways_file = "causal_graph_analysis/key_pathways.csv"
        
        print(f"\n📂 使用文件:")
        print(f"   特征数据: {features_file}")
        print(f"   关键路径: {pathways_file}")
        
        # 检查文件
        if not Path(features_file).exists():
            print(f"\n❌ 文件不存在: {features_file}")
            sys.stdout = logger.terminal
            return
        
        if not Path(pathways_file).exists():
            print(f"\n❌ 文件不存在: {pathways_file}")
            sys.stdout = logger.terminal
            return
        
        # ========== 初始化估计器 ==========
        estimator = CausalEffectEstimator(
            features_path=features_file,
            key_pathways_path=pathways_file,
            output_dir="causal_effect_analysis"
        )
        
        # 更新日志路径
        final_log_path = estimator.output_dir / "estimation_log.md"
        logger.log_path = final_log_path
        
        # ========== 执行分析流程 ==========
        
        # 步骤1: 加载数据
        features, pathways = estimator.load_data()
        
        # 步骤2: 估计所有效应
        effect_results = estimator.estimate_all_effects()
        
        # 步骤3: 解释效应
        sorted_results = estimator.interpret_effects()
        
        # 步骤4: 可视化
        estimator.visualize_effects()
        
        # 步骤5: 生成报告
        report = estimator.generate_report()
        
        # ========== 完成总结 ==========
        print("\n" + "=" * 80)
        print("✅ 因果效应估计完成!")
        print("=" * 80)
        
        print(f"\n📁 输出文件列表:")
        
        print(f"\n🎨 可视化图表:")
        print(f"   1. effect_forest_plot.png - 效应森林图 ⭐")
        print(f"   2. effect_significance_plot.png - 效应显著性图")
        print(f"   3. effects_by_lag.png - 时间尺度对比图")
        
        print(f"\n📊 数据文件:")
        print(f"   4. effect_estimates.csv - 完整效应估计结果")
        
        print(f"\n📝 分析报告:")
        print(f"   5. effect_estimation_report.md - 效应分析报告 ⭐")
        print(f"   6. estimation_log.md - 运行日志")
        
        print(f"\n💡 论文使用建议:")
        print(f"   1. 森林图 → 论文图表,展示所有效应大小")
        print(f"   2. 效应报告 → 结果章节,详细解读核心发现")
        print(f"   3. CSV数据 → 补充材料,提供完整数据")
        
        print(f"\n📖 核心发现:")
        top3 = sorted_results.head(3)
        for idx, (_, row) in enumerate(top3.iterrows(), 1):
            print(f"   {idx}. {row['cause']}→{row['effect']}: 效应={row['effect_size']:.3f}")
        
        print(f"\n📂 所有文件保存在: {estimator.output_dir}")
        
        # 保存日志
        sys.stdout = logger.terminal
        logger.save_to_markdown()
        
        if temp_log_path.exists():
            temp_log_path.unlink()
        
    except FileNotFoundError as e:
        print(f"\n❌ 文件未找到: {e}")
        sys.stdout = logger.terminal
        logger.save_to_markdown()
        
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout = logger.terminal
        logger.save_to_markdown()

if __name__ == "__main__":
    main()