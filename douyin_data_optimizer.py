"""
抖音数据稀疏性优化处理器 - 完整版
功能:
1. 识别数据高峰期
2. 只保留活跃时间段
3. 移除全零时间窗口
4. 自适应时间窗口调整
5. 输出运行日志.md
6. 智能路径识别
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import matplotlib
import sys
import re
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# ==================== 日志记录器 ====================
class Logger:
    """双向输出日志:同时输出到控制台和Markdown文件"""
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
        
        md_content = f"""# 抖音数据优化处理运行日志

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
- 本日志由抖音数据优化程序自动生成
- 包含完整的数据处理过程和优化策略
- 可用于复现处理流程和结果验证
"""
        
        with open(self.log_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"\n✅ 运行日志已保存: {self.log_path}")

# ==================== 辅助函数 ====================
def extract_dataset_name(file_path):
    """
    从文件路径中智能提取数据集名称
    例如: data/douyin/n100/xxx.json -> n100
    """
    path = Path(file_path)
    
    for parent in path.parents:
        dir_name = parent.name
        
        # 匹配 nXXX 格式
        if re.match(r'^n\d+$', dir_name):
            return dir_name
        
        # 匹配其他常见格式
        if dir_name in ['december', 'november', 'august', 'test', 'sample']:
            return dir_name
    
    # 默认使用文件名第一部分
    filename_parts = path.stem.split('_')
    if filename_parts:
        return filename_parts[0]
    
    return 'default'

def create_smart_output_dir(contents_file, base_dir='douyin_optimized'):
    """
    智能创建输出目录
    格式: douyin_optimized/{dataset_name}/
    """
    dataset_name = extract_dataset_name(contents_file)
    output_dir = Path(base_dir) / dataset_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir, dataset_name

# ==================== 主处理类 ====================
class DouyinDataOptimizer:
    """抖音数据优化处理器"""
    
    def __init__(self, time_window='6H'):
        self.time_window = time_window
        self.df_videos = None
        self.df_comments = None
        
    def load_data(self, contents_file, comments_file):
        """步骤1: 加载数据"""
        print("=" * 80)
        print("步骤1: 加载并分析数据分布")
        print("=" * 80)
        
        with open(contents_file, 'r', encoding='utf-8') as f:
            videos = json.load(f)
        with open(comments_file, 'r', encoding='utf-8') as f:
            comments = json.load(f)
        
        self.df_videos = pd.DataFrame(videos)
        self.df_comments = pd.DataFrame(comments)
        
        self._clean_data()
        self._analyze_distribution()
        
        return self.df_videos, self.df_comments
    
    def _clean_data(self):
        """数据清洗"""
        self.df_videos['datetime'] = pd.to_datetime(self.df_videos['create_time'], unit='s')
        numeric_fields = ['liked_count', 'collected_count', 'comment_count', 'share_count']
        for field in numeric_fields:
            self.df_videos[field] = pd.to_numeric(self.df_videos[field], errors='coerce').fillna(0)
        
        self.df_comments['datetime'] = pd.to_datetime(self.df_comments['create_time'], unit='s')
        self.df_comments['like_count'] = pd.to_numeric(self.df_comments['like_count'], errors='coerce').fillna(0)
    
    def _analyze_distribution(self):
        """分析数据时间分布"""
        print(f"\n📊 数据时间分布分析:")
        print(f"   视频数量: {len(self.df_videos)}")
        print(f"   评论数量: {len(self.df_comments)}")
        print(f"   时间范围: {self.df_videos['datetime'].min()} ~ {self.df_videos['datetime'].max()}")
        
        self.df_videos['month'] = self.df_videos['datetime'].dt.to_period('M')
        monthly_counts = self.df_videos['month'].value_counts().sort_index()
        
        print(f"\n📅 各月份视频分布:")
        for month, count in monthly_counts.items():
            print(f"   {month}: {count} 条视频")
        
        peak_month = monthly_counts.idxmax()
        print(f"\n🔥 数据高峰期: {peak_month} ({monthly_counts.max()} 条视频)")
    
    def identify_active_periods(self):
        """步骤2: 识别活跃时间段"""
        print("\n" + "=" * 80)
        print("步骤2: 识别活跃时间段")
        print("=" * 80)
        
        daily_counts = self.df_videos.set_index('datetime').resample('1D')['aweme_id'].count()
        active_days = daily_counts[daily_counts > 0]
        
        if len(active_days) == 0:
            print("⚠️  没有找到活跃时间段")
            return None
        
        print(f"✅ 发现 {len(active_days)} 个活跃日期")
        
        active_periods = []
        current_start = None
        current_end = None
        
        for date in active_days.index:
            if current_start is None:
                current_start = date
                current_end = date
            elif (date - current_end).days <= 7:
                current_end = date
            else:
                active_periods.append((current_start, current_end))
                current_start = date
                current_end = date
        
        if current_start is not None:
            active_periods.append((current_start, current_end))
        
        print(f"\n📍 识别出 {len(active_periods)} 个活跃时间段:")
        for i, (start, end) in enumerate(active_periods, 1):
            duration = (end - start).days + 1
            video_count = len(self.df_videos[
                (self.df_videos['datetime'] >= start) & 
                (self.df_videos['datetime'] <= end)
            ])
            print(f"   {i}. {start.date()} ~ {end.date()} ({duration}天, {video_count}条视频)")
        
        return active_periods
    
    def select_best_period(self, active_periods):
        """步骤3: 选择最佳时间段"""
        print("\n" + "=" * 80)
        print("步骤3: 选择最佳分析时间段")
        print("=" * 80)
        
        best_period = None
        best_score = 0
        
        for start, end in active_periods:
            video_count = len(self.df_videos[
                (self.df_videos['datetime'] >= start) & 
                (self.df_videos['datetime'] <= end)
            ])
            comment_count = len(self.df_comments[
                (self.df_comments['datetime'] >= start) & 
                (self.df_comments['datetime'] <= end)
            ])
            
            duration = (end - start).days + 1
            score = (video_count + comment_count / 10) / duration
            
            if score > best_score:
                best_score = score
                best_period = (start, end, video_count, comment_count)
        
        if best_period:
            start, end, v_count, c_count = best_period
            duration = (end - start).days + 1
            print(f"✅ 最佳时间段:")
            print(f"   时间范围: {start.date()} ~ {end.date()}")
            print(f"   持续时间: {duration} 天")
            print(f"   视频数量: {v_count}")
            print(f"   评论数量: {c_count}")
            print(f"   数据密度: {(v_count + c_count) / duration:.1f} 条/天")
        
        return best_period
    
    def filter_by_period(self, start_date, end_date):
        """根据时间段过滤数据"""
        print("\n🔄 过滤数据到指定时间段...")
        
        mask_video = (self.df_videos['datetime'] >= start_date) & (self.df_videos['datetime'] <= end_date)
        filtered_videos = self.df_videos[mask_video].copy()
        
        mask_comment = (self.df_comments['datetime'] >= start_date) & (self.df_comments['datetime'] <= end_date)
        filtered_comments = self.df_comments[mask_comment].copy()
        
        print(f"✅ 过滤后数据量:")
        print(f"   视频: {len(self.df_videos)} → {len(filtered_videos)}")
        print(f"   评论: {len(self.df_comments)} → {len(filtered_comments)}")
        
        return filtered_videos, filtered_comments
    
    def adaptive_time_window(self, df_videos, df_comments):
        """步骤4: 自适应调整时间窗口 - 优化版本"""
        print("\n" + "=" * 80)
        print("步骤4: 自适应时间窗口选择")
        print("=" * 80)
        
        # 🔧 修改测试窗口列表,移除过大的窗口
        windows = ['1H', '3H', '6H', '12H', '1D']
        results = []
        
        for window in windows:
            temp_features = df_videos.set_index('datetime').resample(window).agg({'aweme_id': 'count'})
            non_zero_ratio = (temp_features['aweme_id'] > 0).sum() / len(temp_features) * 100
            avg_count = temp_features['aweme_id'].mean()
            time_points = (temp_features['aweme_id'] > 0).sum()
            
            # 🔧 新的评分标准:优先保证足够的时间点数
            # 时间点数 > 50: 优先选择
            # 时间点数 30-50: 可接受
            # 时间点数 < 30: 惩罚
            if time_points >= 50:
                score = non_zero_ratio * avg_count * 2.0  # 加倍奖励
            elif time_points >= 30:
                score = non_zero_ratio * avg_count * 1.0
            else:
                score = non_zero_ratio * avg_count * 0.3  # 惩罚
            
            results.append({
                'window': window,
                'time_points': len(temp_features),
                'active_points': time_points,
                'non_zero_ratio': non_zero_ratio,
                'avg_count': avg_count,
                'score': score
            })
            
            print(f"   {window}: {time_points}个活跃点/{len(temp_features)}总点, {non_zero_ratio:.1f}%非零, 平均{avg_count:.2f}条/窗口")
        
        # 选择最佳窗口
        best = max(results, key=lambda x: x['score'])
        
        print(f"\n✅ 推荐时间窗口: {best['window']}")
        print(f"   活跃时间点: {best['active_points']}")
        print(f"   非零率: {best['non_zero_ratio']:.1f}%")
        print(f"   数据密度: {best['avg_count']:.2f}")
        
        # 🔧 强制检查:如果推荐窗口导致时间点 < 30,降级到更小窗口
        if best['active_points'] < 30:
            print(f"\n⚠️  推荐窗口({best['window']})的时间点数({best['active_points']})不足30")
            print(f"   自动降级到更小的时间窗口...")
            
            # 强制选择时间点 >= 30 的最大窗口
            valid_windows = [r for r in results if r['active_points'] >= 30]
            if valid_windows:
                best = valid_windows[0]  # 选择最小的满足条件的窗口
                print(f"   ✅ 降级到: {best['window']} ({best['active_points']}个时间点)")
            else:
                # 如果都不满足,选择时间点最多的
                best = max(results, key=lambda x: x['active_points'])
                print(f"   ⚠️  所有窗口都不满足30点要求,选择最优: {best['window']} ({best['active_points']}个时间点)")
        
        return best['window']
    
    def extract_features_optimized(self, df_videos, df_comments):
        """步骤5: 提取特征(移除全零时间窗口)"""
        print("\n" + "=" * 80)
        print("步骤5: 提取特征(移除空白时间段)")
        print("=" * 80)
        
        df_v = df_videos.set_index('datetime')
        df_c = df_comments.set_index('datetime')
        
        video_features = df_v.resample(self.time_window).agg({
            'aweme_id': 'count',
            'liked_count': 'sum',
            'comment_count': 'sum',
            'share_count': 'sum',
            'collected_count': 'sum'
        }).rename(columns={
            'aweme_id': 'video_count',
            'liked_count': 'total_likes',
            'comment_count': 'total_comments',
            'share_count': 'total_shares',
            'collected_count': 'total_collects'
        })
        
        comment_features = df_c.resample(self.time_window).agg({
            'comment_id': 'count',
            'like_count': 'mean'
        }).rename(columns={
            'comment_id': 'comment_count',
            'like_count': 'avg_comment_likes'
        })
        
        features = pd.concat([video_features, comment_features], axis=1).fillna(0)
        
        print(f"\n📊 聚合前数据:")
        print(f"   时间窗口: {self.time_window}")
        print(f"   总时间点: {len(features)}")
        
        # 移除全零行
        non_zero_counts = (features != 0).sum(axis=1)
        features_filtered = features[non_zero_counts > 0].copy()
        
        zero_ratio = (len(features) - len(features_filtered)) / len(features) * 100
        
        print(f"\n🔧 移除全零时间窗口:")
        print(f"   原始时间点: {len(features)}")
        print(f"   过滤后: {len(features_filtered)}")
        print(f"   移除比例: {zero_ratio:.1f}%")
        
        # 数据质量检查
        print(f"\n📈 数据质量检查:")
        for col in features_filtered.columns:
            non_zero_ratio = (features_filtered[col] != 0).sum() / len(features_filtered) * 100
            print(f"   {col}: {non_zero_ratio:.1f}% 非零")
        
        return features_filtered
    
    def save_optimized_data(self, features, output_dir):
        """步骤6: 保存优化后的数据"""
        print("\n" + "=" * 80)
        print("步骤6: 保存优化数据")
        print("=" * 80)
        
        output_path = Path(output_dir)
        
        # 标准化
        scaler = StandardScaler()
        normalized = pd.DataFrame(
            scaler.fit_transform(features),
            index=features.index,
            columns=features.columns
        )
        
        # 转换为PCMCI格式
        n_vars = len(normalized.columns)
        var_names = [f'X{i+1}' for i in range(n_vars)]
        
        df_pcmci = normalized.copy()
        df_pcmci.columns = var_names
        df_pcmci['time'] = range(len(df_pcmci))
        
        # 保存PCMCI文件
        csv_path = output_path / f"douyin_pcmci_{self.time_window}_optimized.csv"
        df_pcmci.to_csv(csv_path, index=False)
        
        # 保存特征映射
        mapping = {
            'X1': 'video_count (视频发布数量)',
            'X2': 'total_likes (视频总点赞数)',
            'X3': 'total_comments (视频总评论数)',
            'X4': 'total_shares (视频总转发数)',
            'X5': 'total_collects (视频总收藏数)',
            'X6': 'comment_count (评论发布数量)',
            'X7': 'avg_comment_likes (评论平均点赞数)'
        }
        pd.DataFrame([mapping]).T.to_csv(
            output_path / "feature_mapping.csv",
            encoding='utf-8-sig',
            header=['特征说明']
        )
        
        # 保存原始特征
        features.to_csv(output_path / f"original_features_{self.time_window}_optimized.csv")
        
        # 保存数据摘要
        summary = features.describe()
        summary.to_csv(output_path / "data_summary_optimized.csv", encoding='utf-8-sig')
        
        print(f"\n✅ 文件已保存")
        print(f"   主文件: {csv_path.name}")
        print(f"   时间点数: {len(df_pcmci)}")
        print(f"   特征数: {n_vars}")
        
        return df_pcmci, csv_path
    
    def visualize_timeseries(self, features, output_dir):
        """生成时间序列可视化"""
        try:
            output_path = Path(output_dir)
            
            # 确保matplotlib配置正确
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            fig, axes = plt.subplots(7, 1, figsize=(14, 18))
            
            feature_names = [
                '视频发布数量',
                '视频总点赞数',
                '视频总评论数',
                '视频总转发数',
                '视频总收藏数',
                '评论发布数量',
                '评论平均点赞数'
            ]
            
            for i, (col, name) in enumerate(zip(features.columns, feature_names)):
                try:
                    axes[i].plot(features.index, features[col], linewidth=2, color='steelblue')
                    axes[i].set_title(f'X{i+1}: {name}', fontsize=12, fontweight='bold')
                    axes[i].set_ylabel('Value', fontsize=10)  # 使用英文避免字体问题
                    axes[i].grid(True, alpha=0.3)
                except Exception as e:
                    print(f"   ⚠️  绘制 {name} 时出错: {e}")
            
            axes[-1].set_xlabel('Time', fontsize=10)
            plt.tight_layout()
            
            viz_path = output_path / f"timeseries_visualization_{self.time_window}.png"
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            print(f"✅ 时间序列图已保存: {viz_path}")
            plt.close(fig)
            
        except Exception as e:
            print(f"⚠️  可视化失败: {e}")
            print(f"   但数据处理已完成,可继续使用CSV文件")
            # 即使可视化失败,也不中断程序
            try:
                plt.close('all')
            except:
                pass

# ==================== 主程序 ====================
def main():
    """主处理流程"""
    # 初始化日志
    global logger
    temp_log_path = Path("temp_douyin_optimization_log.md")
    logger = Logger(temp_log_path)
    sys.stdout = logger
    
    print("=" * 80)
    print("抖音数据稀疏性优化处理器")
    print("=" * 80)
    
    # ========== 配置 ==========
    contents_file = "data/douyin/n100000/search_contents_2026-01-21.json"
    comments_file = "data/douyin/n100000/search_comments_2026-01-21.json"
    
    # 智能创建输出目录
    output_dir, dataset_name = create_smart_output_dir(contents_file)
    
    print(f"\n📂 数据集信息:")
    print(f"   数据集名称: {dataset_name}")
    print(f"   输出目录: {output_dir}")
    
    # 更新日志路径
    final_log_path = output_dir / "optimization_log.md"
    logger.log_path = final_log_path
    
    # ========== 执行优化 ==========
    try:
        optimizer = DouyinDataOptimizer(time_window='6H')
        
        # 步骤1-3
        df_videos, df_comments = optimizer.load_data(contents_file, comments_file)
        active_periods = optimizer.identify_active_periods()
        
        if not active_periods:
            print("\n❌ 未找到活跃时间段")
            sys.stdout = logger.terminal
            logger.save_to_markdown()
            return
        
        best_period = optimizer.select_best_period(active_periods)
        if not best_period:
            print("\n❌ 无法选择最佳时间段")
            sys.stdout = logger.terminal
            logger.save_to_markdown()
            return
        
        start_date, end_date, _, _ = best_period
        
        # 步骤4-6
        filtered_videos, filtered_comments = optimizer.filter_by_period(start_date, end_date)
        
        # 🔧 先显示过滤后的数据统计
        print(f"\n📊 过滤后数据统计:")
        print(f"   视频数: {len(filtered_videos)}")
        print(f"   评论数: {len(filtered_comments)}")
        print(f"   时间跨度: {(end_date - start_date).days + 1} 天")
        
        best_window = optimizer.adaptive_time_window(filtered_videos, filtered_comments)
        optimizer.time_window = best_window
        
        features = optimizer.extract_features_optimized(filtered_videos, filtered_comments)
        
        # 🔧 更详细的警告和建议
        if len(features) < 20:
            print(f"\n❌ 严重警告: 时间点数({len(features)})少于20,PCMCI无法有效运行!")
            print(f"   建议:")
            print(f"   1. 扩大数据收集范围(更长时间或更多关键词)")
            print(f"   2. 或手动设置更小的时间窗口(如1H或3H)")
            print(f"\n   是否继续保存数据? 这些数据可能不适合PCMCI分析")
        elif len(features) < 30:
            print(f"\n⚠️  警告: 时间点数({len(features)})少于30")
            print(f"   PCMCI可以运行,但结果可能不够稳定")
            print(f"   建议: tau_max 设置为 1")
        elif len(features) < 50:
            print(f"\n✅ 时间点数({len(features)})在可接受范围")
            print(f"   建议: tau_max 设置为 1-2")
        else:
            print(f"\n✅ 时间点数({len(features)})充足,适合PCMCI分析")
            print(f"   建议: tau_max 可设置为 2-3")
        
        df_pcmci, csv_path = optimizer.save_optimized_data(features, output_dir)
        
        # 可视化
        print("\n" + "=" * 80)
        print("步骤7: 生成时间序列可视化")
        print("=" * 80)
        #optimizer.visualize_timeseries(features, output_dir)
        
        # 完成总结
        print("\n" + "=" * 80)
        print("✅ 数据优化完成!")
        print("=" * 80)
        
        print(f"\n📊 优化效果:")
        print(f"   数据集: {dataset_name}")
        print(f"   优化后时间段: {start_date.date()} ~ {end_date.date()}")
        print(f"   优化后时间点: {len(features)}")
        print(f"   最终时间窗口: {optimizer.time_window}")
        
        print(f"\n📁 输出文件:")
        print(f"   1. {csv_path.name} - PCMCI输入文件 ⭐")
        print(f"   2. feature_mapping.csv - 特征说明")
        print(f"   3. original_features_{optimizer.time_window}_optimized.csv")
        print(f"   4. data_summary_optimized.csv")
        print(f"   5. timeseries_visualization_{optimizer.time_window}.png")
        print(f"   6. optimization_log.md - 运行日志 🆕")
        
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