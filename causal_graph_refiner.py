"""
因果图精炼与可视化模块
功能:
1. 从PCMCI结果中提取核心因果关系
2. 生成多层次可视化图表
3. 识别关键传播路径
4. 输出详细分析报告

作者: 毕设项目
日期: 2026-01-21
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
from pathlib import Path
import sys
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 中文字体设置
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
        
        md_content = f"""# 因果图精炼与可视化运行日志

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
- 本日志由因果图精炼程序自动生成
- 包含完整的分析过程和可视化结果
- 可用于论文方法部分的撰写参考
"""
        
        with open(self.log_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"\n✅ 运行日志已保存: {self.log_path}")

# ==================== 因果图精炼器 ====================
class CausalGraphRefiner:
    """
    因果图精炼器
    
    主要功能:
    1. 从PCMCI结果中过滤强因果关系
    2. 按滞后时间分层
    3. 识别关键传播路径
    4. 生成多种可视化图表
    """
    
    def __init__(self, pcmci_results_path, feature_mapping_path, output_dir='causal_graph_analysis'):
        """
        初始化
        
        参数:
            pcmci_results_path: PCMCI结果CSV文件路径
            feature_mapping_path: 特征映射CSV文件路径
            output_dir: 输出目录
        """
        self.results_path = pcmci_results_path
        self.mapping_path = feature_mapping_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print("=" * 80)
        print("因果图精炼与可视化模块")
        print("=" * 80)
        print(f"\n📂 初始化:")
        print(f"   输入文件: {pcmci_results_path}")
        print(f"   输出目录: {output_dir}")
    
    def load_data(self):
        """
        步骤1: 加载PCMCI结果和特征映射
        """
        print("\n" + "=" * 80)
        print("步骤1: 加载数据")
        print("=" * 80)
        
        # 加载PCMCI结果
        self.df_results = pd.read_csv(self.results_path)
        print(f"\n✅ PCMCI结果已加载:")
        print(f"   总关系数: {len(self.df_results)}")
        print(f"   显著关系数: {self.df_results['Causal'].sum()}")
        
        # 加载特征映射
        self.df_mapping = pd.read_csv(self.mapping_path, index_col=0)
        print(f"\n✅ 特征映射已加载:")
        for var, desc in self.df_mapping['特征说明'].items():
            print(f"   {var}: {desc}")
        
        # 只保留因果关系
        self.causal_links = self.df_results[self.df_results['Causal'] == True].copy()
        print(f"\n📊 过滤后:")
        print(f"   保留 {len(self.causal_links)} 个显著因果关系")
        
        return self.causal_links
    
    def analyze_relationship_strength(self, correlation_threshold=0.3):
        """
        步骤2: 分析因果关系强度
        
        参数:
            correlation_threshold: 相关性阈值,只保留强关系
        """
        print("\n" + "=" * 80)
        print("步骤2: 分析因果关系强度")
        print("=" * 80)
        
        # 按相关性强度分类
        self.causal_links['strength'] = self.causal_links['Correlation'].abs()
        
        # 强度分类
        def classify_strength(corr):
            corr = abs(corr)
            if corr >= 0.7:
                return '极强'
            elif corr >= 0.5:
                return '强'
            elif corr >= 0.3:
                return '中等'
            else:
                return '弱'
        
        self.causal_links['strength_level'] = self.causal_links['Correlation'].apply(classify_strength)
        
        # 统计
        print(f"\n📊 因果关系强度分布:")
        strength_counts = self.causal_links['strength_level'].value_counts()
        for level, count in strength_counts.items():
            percentage = count / len(self.causal_links) * 100
            print(f"   {level}: {count} 个 ({percentage:.1f}%)")
        
        # 过滤强关系
        self.strong_links = self.causal_links[
            self.causal_links['strength'] >= correlation_threshold
        ].copy()
        
        print(f"\n🔧 过滤阈值: 相关性 >= {correlation_threshold}")
        print(f"   原始关系: {len(self.causal_links)} 个")
        print(f"   强关系: {len(self.strong_links)} 个")
        print(f"   过滤比例: {(1 - len(self.strong_links)/len(self.causal_links))*100:.1f}%")
        
        return self.strong_links
    
    def analyze_by_lag(self):
        """
        步骤3: 按滞后时间分层分析
        """
        print("\n" + "=" * 80)
        print("步骤3: 滞后时间分层分析")
        print("=" * 80)
        
        # 按Lag分组
        lag_groups = self.strong_links.groupby('Lag')
        
        print(f"\n📊 各滞后阶段的因果关系数量:")
        
        self.lag_analysis = {}
        
        for lag, group in lag_groups:
            count = len(group)
            avg_corr = group['strength'].mean()
            
            if lag == 0:
                lag_name = "同时效应 (Lag 0)"
                meaning = "瞬时传播,用户行为同步发生"
            elif lag == 1:
                lag_name = "短期效应 (Lag 1, 12H)"
                meaning = "快速反馈,互动驱动内容"
            elif lag == 2:
                lag_name = "中期效应 (Lag 2, 24H)"
                meaning = "话题发酵,讨论引导创作"
            elif lag == 3:
                lag_name = "长期效应 (Lag 3, 36H)"
                meaning = "持续影响,优质内容沉淀"
            else:
                lag_name = f"Lag {lag}"
                meaning = "未定义"
            
            self.lag_analysis[lag] = {
                'name': lag_name,
                'meaning': meaning,
                'count': count,
                'avg_correlation': avg_corr,
                'links': group
            }
            
            print(f"\n   {lag_name}:")
            print(f"      关系数量: {count}")
            print(f"      平均相关性: {avg_corr:.3f}")
            print(f"      传播意义: {meaning}")
        
        return self.lag_analysis
    
    def identify_key_pathways(self, top_n=10):
        """
        步骤4: 识别关键传播路径
        
        参数:
            top_n: 保留前N个最强关系
        """
        print("\n" + "=" * 80)
        print("步骤4: 识别关键传播路径")
        print("=" * 80)
        
        # 按相关性排序
        top_links = self.strong_links.nlargest(top_n, 'strength')
        
        print(f"\n🔥 Top {top_n} 最强因果关系:\n")
        
        for idx, (i, row) in enumerate(top_links.iterrows(), 1):
            from_var = row['From']
            to_var = row['To']
            lag = row['Lag']
            corr = row['Correlation']
            pval = row['P_value']
            
            # 获取变量含义
            from_desc = self.df_mapping.loc[from_var, '特征说明']
            to_desc = self.df_mapping.loc[to_var, '特征说明']
            
            if lag == 0:
                arrow = "<-->"
                lag_desc = "同时"
            else:
                arrow = f"--[Lag{lag}]-->"
                lag_desc = f"{lag*12}小时后"
            
            print(f"{idx}. {from_var} {arrow} {to_var}")
            print(f"   {from_desc}")
            print(f"   {to_desc}")
            print(f"   相关性: {corr:.3f} | p值: {pval:.6f}")
            print(f"   传播解释: {from_desc.split('(')[0]} → {lag_desc} → {to_desc.split('(')[0]}")
            print()
        
        # 保存关键路径
        top_links.to_csv(
            self.output_dir / "key_pathways.csv",
            index=False,
            encoding='utf-8-sig'
        )
        print(f"✅ 关键路径已保存: {self.output_dir / 'key_pathways.csv'}")
        
        return top_links
    
    def build_network_graph(self):
        """
        步骤5: 构建网络图对象
        """
        print("\n" + "=" * 80)
        print("步骤5: 构建因果网络图")
        print("=" * 80)
        
        # 创建有向图
        self.G = nx.DiGraph()
        
        # 添加边
        for _, row in self.strong_links.iterrows():
            self.G.add_edge(
                row['From'],
                row['To'],
                weight=abs(row['Correlation']),
                lag=row['Lag'],
                pvalue=row['P_value']
            )
        
        # 网络统计
        print(f"\n📊 网络结构统计:")
        print(f"   节点数: {self.G.number_of_nodes()}")
        print(f"   边数: {self.G.number_of_edges()}")
        print(f"   平均度: {np.mean([d for n, d in self.G.degree()]):.2f}")
        
        # 节点重要性 (度中心性)
        degree_centrality = nx.degree_centrality(self.G)
        
        print(f"\n🎯 节点重要性排名 (度中心性):")
        sorted_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
        for node, centrality in sorted_nodes:
            desc = self.df_mapping.loc[node, '特征说明'].split('(')[0]
            print(f"   {node} ({desc}): {centrality:.3f}")
        
        return self.G
    
    def visualize_full_network(self):
        """
        步骤6a: 可视化完整因果网络
        """
        print("\n" + "=" * 80)
        print("步骤6a: 生成完整因果网络图")
        print("=" * 80)
        
        plt.figure(figsize=(20, 16))
        
        # 使用spring布局
        pos = nx.spring_layout(self.G, k=3, iterations=100, seed=42)
        
        # 按Lag分层绘制边
        colors = {
            0: '#FF4444',  # 红色 - 同时
            1: '#FF9944',  # 橙色 - 短期
            2: '#44AA44',  # 绿色 - 中期
            3: '#4444FF'   # 蓝色 - 长期
        }
        
        labels = {
            0: '同时效应 (Lag 0)',
            1: '短期效应 (12H)',
            2: '中期效应 (24H)',
            3: '长期效应 (36H)'
        }
        
        # 绘制不同lag的边
        for lag in sorted(colors.keys()):
            edges = [(u, v) for u, v, d in self.G.edges(data=True) if d['lag'] == lag]
            if not edges:
                continue
            
            weights = [self.G[u][v]['weight'] * 5 for u, v in edges]
            
            nx.draw_networkx_edges(
                self.G, pos,
                edgelist=edges,
                edge_color=colors[lag],
                width=weights,
                alpha=0.7,
                arrows=True,
                arrowsize=25,
                arrowstyle='->',
                connectionstyle='arc3,rad=0.1',
                label=labels[lag]
            )
        
        # 绘制节点
        node_sizes = [3000 + nx.degree_centrality(self.G)[node] * 5000 
                      for node in self.G.nodes()]
        
        nx.draw_networkx_nodes(
            self.G, pos,
            node_size=node_sizes,
            node_color='lightblue',
            edgecolors='darkblue',
            linewidths=2
        )
        
        # 节点标签
        labels_dict = {node: node for node in self.G.nodes()}
        nx.draw_networkx_labels(
            self.G, pos,
            labels_dict,
            font_size=14,
            font_weight='bold'
        )
        
        plt.legend(fontsize=14, loc='upper left')
        plt.title('抖音核污水事件传播因果网络图\n(节点大小表示重要性)', 
                 fontsize=18, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        save_path = self.output_dir / 'causal_network_full.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ 完整网络图已保存: {save_path}")
        plt.close()
    
    def visualize_by_lag(self):
        """
        步骤6b: 按滞后时间分层可视化
        """
        print("\n" + "=" * 80)
        print("步骤6b: 生成分层因果网络图")
        print("=" * 80)
        
        fig, axes = plt.subplots(2, 2, figsize=(24, 20))
        axes = axes.flatten()
        
        colors = {0: '#FF4444', 1: '#FF9944', 2: '#44AA44', 3: '#4444FF'}
        titles = {
            0: 'Lag 0: 同时效应 (瞬时传播)',
            1: 'Lag 1: 短期效应 (12小时)',
            2: 'Lag 2: 中期效应 (24小时)',
            3: 'Lag 3: 长期效应 (36小时)'
        }
        
        for lag, ax in zip(sorted(colors.keys()), axes):
            # 创建子图
            G_sub = nx.DiGraph()
            
            # 只添加该lag的边
            for u, v, d in self.G.edges(data=True):
                if d['lag'] == lag:
                    G_sub.add_edge(u, v, weight=d['weight'])
            
            if G_sub.number_of_edges() == 0:
                ax.text(0.5, 0.5, f'无 {titles[lag]} 关系', 
                       ha='center', va='center', fontsize=16)
                ax.axis('off')
                continue
            
            # 布局
            pos = nx.spring_layout(G_sub, k=2, iterations=100, seed=42)
            
            # 绘制
            weights = [G_sub[u][v]['weight'] * 5 for u, v in G_sub.edges()]
            
            nx.draw_networkx_edges(
                G_sub, pos,
                width=weights,
                edge_color=colors[lag],
                alpha=0.7,
                arrows=True,
                arrowsize=25,
                arrowstyle='->',
                ax=ax
            )
            
            node_sizes = [3000 for _ in G_sub.nodes()]
            nx.draw_networkx_nodes(
                G_sub, pos,
                node_size=node_sizes,
                node_color='lightblue',
                edgecolors=colors[lag],
                linewidths=3,
                ax=ax
            )
            
            nx.draw_networkx_labels(
                G_sub, pos,
                font_size=12,
                font_weight='bold',
                ax=ax
            )
            
            ax.set_title(titles[lag], fontsize=14, fontweight='bold', pad=10)
            ax.axis('off')
            
            # 添加统计信息
            info_text = f"关系数: {G_sub.number_of_edges()}\n"
            info_text += f"平均相关性: {self.lag_analysis[lag]['avg_correlation']:.3f}"
            ax.text(0.02, 0.98, info_text, 
                   transform=ax.transAxes,
                   fontsize=11,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.suptitle('因果关系分层分析图', fontsize=20, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        save_path = self.output_dir / 'causal_network_by_lag.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ 分层网络图已保存: {save_path}")
        plt.close()
    
    def visualize_key_pathways(self, top_n=15):
        """
        步骤6c: 可视化核心传播路径
        """
        print("\n" + "=" * 80)
        print("步骤6c: 生成核心传播路径图")
        print("=" * 80)
        
        # 获取top关系
        top_links = self.strong_links.nlargest(top_n, 'strength')
        
        # 创建子图
        G_core = nx.DiGraph()
        for _, row in top_links.iterrows():
            G_core.add_edge(
                row['From'],
                row['To'],
                weight=abs(row['Correlation']),
                lag=row['Lag']
            )
        
        plt.figure(figsize=(18, 14))
        
        # 分层布局
        pos = nx.spring_layout(G_core, k=3, iterations=150, seed=42)
        
        # 按lag绘制
        colors = {0: '#FF4444', 1: '#FF9944', 2: '#44AA44', 3: '#4444FF'}
        
        for lag in sorted(colors.keys()):
            edges = [(u, v) for u, v, d in G_core.edges(data=True) if d['lag'] == lag]
            if edges:
                weights = [G_core[u][v]['weight'] * 8 for u, v in edges]
                nx.draw_networkx_edges(
                    G_core, pos,
                    edgelist=edges,
                    edge_color=colors[lag],
                    width=weights,
                    alpha=0.8,
                    arrows=True,
                    arrowsize=30,
                    arrowstyle='->',
                    connectionstyle='arc3,rad=0.15'
                )
        
        # 节点
        node_sizes = [4000 + nx.degree_centrality(G_core)[node] * 6000 
                      for node in G_core.nodes()]
        
        nx.draw_networkx_nodes(
            G_core, pos,
            node_size=node_sizes,
            node_color='#87CEEB',
            edgecolors='#4169E1',
            linewidths=3
        )
        
        # 标签(带变量说明)
        labels = {}
        for node in G_core.nodes():
            desc = self.df_mapping.loc[node, '特征说明'].split('(')[0].strip()
            labels[node] = f"{node}\n{desc}"
        
        nx.draw_networkx_labels(
            G_core, pos,
            labels,
            font_size=11,
            font_weight='bold'
        )
        
        plt.title(f'Top {top_n} 核心传播路径\n(边宽度 = 相关性强度)', 
                 fontsize=18, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        save_path = self.output_dir / 'causal_pathways_core.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ 核心路径图已保存: {save_path}")
        plt.close()
    
    def generate_summary_report(self):
        """
        步骤7: 生成分析报告
        """
        print("\n" + "=" * 80)
        print("步骤7: 生成分析报告")
        print("=" * 80)
        
        report = f"""# 因果图分析报告

## 1. 数据概况

- **原始因果关系数**: {len(self.causal_links)}
- **强因果关系数**: {len(self.strong_links)}
- **网络节点数**: {self.G.number_of_nodes()}
- **网络边数**: {self.G.number_of_edges()}

---

## 2. 因果关系强度分布

"""
        
        # 强度分布
        strength_counts = self.causal_links['strength_level'].value_counts()
        for level, count in strength_counts.items():
            percentage = count / len(self.causal_links) * 100
            report += f"- **{level}**: {count} 个 ({percentage:.1f}%)\n"
        
        report += "\n---\n\n## 3. 滞后时间分析\n\n"
        
        # 各lag分析
        for lag, analysis in self.lag_analysis.items():
            report += f"### {analysis['name']}\n\n"
            report += f"- **关系数量**: {analysis['count']}\n"
            report += f"- **平均相关性**: {analysis['avg_correlation']:.3f}\n"
            report += f"- **传播意义**: {analysis['meaning']}\n\n"
        
        report += "---\n\n## 4. 关键传播路径\n\n"
        
        # Top路径
        top_links = self.strong_links.nlargest(10, 'strength')
        for idx, (_, row) in enumerate(top_links.iterrows(), 1):
            from_desc = self.df_mapping.loc[row['From'], '特征说明']
            to_desc = self.df_mapping.loc[row['To'], '特征说明']
            
            report += f"**{idx}. {row['From']} → {row['To']} (Lag {row['Lag']})**\n\n"
            report += f"- 相关性: {row['Correlation']:.3f}\n"
            report += f"- p值: {row['P_value']:.6f}\n"
            report += f"- 传播路径: {from_desc} → {to_desc}\n\n"
        
        report += "---\n\n## 5. 节点重要性\n\n"
        
        # 节点中心性
        degree_centrality = nx.degree_centrality(self.G)
        sorted_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
        
        for node, centrality in sorted_nodes:
            desc = self.df_mapping.loc[node, '特征说明']
            report += f"- **{node}** ({desc}): {centrality:.3f}\n"
        
        report += "\n---\n\n## 6. 研究发现总结\n\n"
        
        # 自动生成发现
        lag0_count = self.lag_analysis.get(0, {}).get('count', 0)
        lag1_count = self.lag_analysis.get(1, {}).get('count', 0)
        lag2_count = self.lag_analysis.get(2, {}).get('count', 0)
        
        report += f"""
1. **瞬时传播占主导**: {lag0_count} 个同时效应关系,表明用户互动高度同步
2. **短期反馈明显**: {lag1_count} 个12小时滞后关系,内容生产快速响应热度
3. **中期发酵显著**: {lag2_count} 个24小时滞后关系,话题讨论引导创作方向

**核心传播机制**:
- 情绪驱动的瞬时级联效应
- 互动数据驱动的内容生产循环
- 优质讨论的持续影响力
"""
        
        # 保存报告
        report_path = self.output_dir / 'analysis_report.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 分析报告已保存: {report_path}")
        
        return report
    
    def export_network_data(self):
        """
        步骤8: 导出网络数据(供其他工具使用)
        """
        print("\n" + "=" * 80)
        print("步骤8: 导出网络数据")
        print("=" * 80)
        
        # 导出边列表
        edges_data = []
        for u, v, d in self.G.edges(data=True):
            edges_data.append({
                'Source': u,
                'Target': v,
                'Weight': d['weight'],
                'Lag': d['lag'],
                'P_value': d['pvalue']
            })
        
        edges_df = pd.DataFrame(edges_data)
        edges_path = self.output_dir / 'network_edges.csv'
        edges_df.to_csv(edges_path, index=False, encoding='utf-8-sig')
        print(f"✅ 边列表已保存: {edges_path}")
        
        # 导出节点列表
        nodes_data = []
        degree_centrality = nx.degree_centrality(self.G)
        
        for node in self.G.nodes():
            nodes_data.append({
                'Node': node,
                'Label': self.df_mapping.loc[node, '特征说明'],
                'Degree': self.G.degree(node),
                'Centrality': degree_centrality[node]
            })
        
        nodes_df = pd.DataFrame(nodes_data)
        nodes_path = self.output_dir / 'network_nodes.csv'
        nodes_df.to_csv(nodes_path, index=False, encoding='utf-8-sig')
        print(f"✅ 节点列表已保存: {nodes_path}")
        
        return edges_df, nodes_df

# ==================== 主程序 ====================
def main():
    """
    主处理流程
    """
    # 初始化日志
    global logger
    output_dir = Path("causal_graph_analysis")
    output_dir.mkdir(exist_ok=True)
    temp_log_path = Path("temp_causal_graph_log.md")
    logger = Logger(temp_log_path)
    sys.stdout = logger

    try:
        # ========== 配置参数 ==========
        # 📌 修改为你的实际文件路径
        #pcmci_results = "douyin_optimized/n100000/douyin_pcmci_12H_optimized.csv"  # PCMCI结果
        #feature_mapping = "douyin_optimized/n100000/feature_mapping.csv"          # 特征映射
        
        # 如果文件路径不同,可以这样设置:
        pcmci_results = "run_data/n1000/pcmci_significant_links.csv"
        feature_mapping = "douyin_optimized/n100000/feature_mapping.csv"
        
        # ========== 初始化精炼器 ==========
        refiner = CausalGraphRefiner(
            pcmci_results_path=pcmci_results,
            feature_mapping_path=feature_mapping,
            output_dir="causal_graph_analysis"
        )
        
        # 更新日志路径
        final_log_path = refiner.output_dir / "refinement_log.md"
        logger.log_path = final_log_path
        
        # ========== 执行分析流程 ==========
        
        # 步骤1: 加载数据
        causal_links = refiner.load_data()
        
        # 步骤2: 分析关系强度
        strong_links = refiner.analyze_relationship_strength(correlation_threshold=0.3)
        
        # 步骤3: 按滞后时间分层
        lag_analysis = refiner.analyze_by_lag()
        
        # 步骤4: 识别关键路径
        key_pathways = refiner.identify_key_pathways(top_n=10)
        
        # 步骤5: 构建网络图
        G = refiner.build_network_graph()
        
        # 步骤6: 可视化
        print("\n" + "=" * 80)
        print("步骤6: 生成可视化图表")
        print("=" * 80)
        
        refiner.visualize_full_network()
        refiner.visualize_by_lag()
        refiner.visualize_key_pathways(top_n=15)
        
        # 步骤7: 生成报告
        report = refiner.generate_summary_report()
        
        # 步骤8: 导出数据
        edges_df, nodes_df = refiner.export_network_data()
        
        # ========== 完成总结 ==========
        print("\n" + "=" * 80)
        print("✅ 因果图精炼完成!")
        print("=" * 80)
        
        print(f"\n📁 输出文件列表:")
        print(f"\n🎨 可视化图表:")
        print(f"   1. causal_network_full.png - 完整因果网络图 ⭐")
        print(f"   2. causal_network_by_lag.png - 分层网络图")
        print(f"   3. causal_pathways_core.png - 核心传播路径图")
        
        print(f"\n📊 数据文件:")
        print(f"   4. key_pathways.csv - 关键传播路径数据")
        print(f"   5. network_edges.csv - 网络边列表")
        print(f"   6. network_nodes.csv - 网络节点列表")
        
        print(f"\n📝 分析报告:")
        print(f"   7. analysis_report.md - 完整分析报告 ⭐")
        print(f"   8. refinement_log.md - 运行日志")
        
        print(f"\n💡 使用建议:")
        print(f"   1. 将可视化图表插入论文的【结果】章节")
        print(f"   2. 参考 analysis_report.md 撰写结果解读")
        print(f"   3. key_pathways.csv 可用于进一步分析")
        print(f"   4. network数据可导入Gephi等专业工具")
        
        print(f"\n📂 所有文件保存在: {refiner.output_dir}")
        
        # 保存日志
        sys.stdout = logger.terminal
        logger.save_to_markdown()
        
        if temp_log_path.exists():
            temp_log_path.unlink()
        
    except FileNotFoundError as e:
        print(f"\n❌ 文件未找到: {e}")
        print("\n请检查以下路径是否正确:")
        print(f"   1. PCMCI结果文件路径")
        print(f"   2. 特征映射文件路径")
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
