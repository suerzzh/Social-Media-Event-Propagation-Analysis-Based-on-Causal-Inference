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
    """
    抖音数据优化处理器
    
    功能：将原始的抖音视频和评论数据转换为适合时间序列因果分析的格式
    
    核心思路：
    1. 原始数据是不规则的（随时发布）
    2. 需要转换为规则的时间序列（每隔N小时一个数据点）
    3. 自动找出最合适的时间窗口和分析时段
    """
    
    def __init__(self, time_window='6H'):
        """
        初始化处理器
        
        参数：
            time_window: 时间窗口大小，例如：
                        '1H' = 1小时
                        '6H' = 6小时
                        '1D' = 1天
        
        属性：
            self.df_videos: 存放视频数据的DataFrame
            self.df_comments: 存放评论数据的DataFrame
        """
        self.time_window = time_window
        self.df_videos = None      # 初始化为空，后续加载数据
        self.df_comments = None    # 初始化为空，后续加载数据
        
    # ==================== 步骤1: 加载数据 ====================
    def load_data(self, contents_file, comments_file):
        """
        加载并初步分析数据
        
        参数：
            contents_file: 视频数据JSON文件路径
            comments_file: 评论数据JSON文件路径
        
        返回：
            (df_videos, df_comments): 两个DataFrame对象
        """
        print("=" * 80)
        print("步骤1: 加载并分析数据分布")
        print("=" * 80)
        
        # --- 1.1 读取JSON文件 ---
        # 'r' = 只读模式, 'utf-8' = 使用UTF-8编码（支持中文）
        with open(contents_file, 'r', encoding='utf-8') as f:
            videos = json.load(f)  # 加载JSON → Python列表/字典
        
        with open(comments_file, 'r', encoding='utf-8') as f:
            comments = json.load(f)
        
        # --- 1.2 转换为pandas的DataFrame格式 ---
        # DataFrame = 类似Excel表格的数据结构
        self.df_videos = pd.DataFrame(videos)
        self.df_comments = pd.DataFrame(comments)
        
        # --- 1.3 清洗数据 ---
        self._clean_data()        # 处理时间和数字格式
        
        # --- 1.4 分析数据分布 ---
        self._analyze_distribution()  # 打印统计信息
        
        return self.df_videos, self.df_comments
    
    def _clean_data(self):
        """
        数据清洗：处理时间格式和数字类型
        
        问题场景：
        1. 原始时间是Unix时间戳（如：1640995200）
        2. 有些数字字段可能是字符串或空值
        """
        # --- 处理视频数据 ---
        
        # 转换时间戳为datetime对象
        # unit='s' 表示秒级时间戳
        # 例如：1640995200 → 2022-01-01 00:00:00
        self.df_videos['datetime'] = pd.to_datetime(
            self.df_videos['create_time'], 
            unit='s'
        )
        
        # 定义需要转换为数字的字段
        numeric_fields = [
            'liked_count',      # 点赞数
            'collected_count',  # 收藏数
            'comment_count',    # 评论数
            'share_count'       # 转发数
        ]
        
        # 逐个字段处理
        for field in numeric_fields:
            # pd.to_numeric: 强制转换为数字
            # errors='coerce': 如果转换失败，设为NaN（空值）
            # fillna(0): 把所有NaN填充为0
            self.df_videos[field] = pd.to_numeric(
                self.df_videos[field], 
                errors='coerce'
            ).fillna(0)
        
        # --- 处理评论数据（类似） ---
        self.df_comments['datetime'] = pd.to_datetime(
            self.df_comments['create_time'], 
            unit='s'
        )
        
        self.df_comments['like_count'] = pd.to_numeric(
            self.df_comments['like_count'], 
            errors='coerce'
        ).fillna(0)
    
    def _analyze_distribution(self):
        """
        分析数据的时间分布
        
        目的：了解数据覆盖哪些时间段，哪个月最活跃
        """
        print(f"\n📊 数据时间分布分析:")
        
        # 基本统计
        print(f"   视频数量: {len(self.df_videos)}")
        print(f"   评论数量: {len(self.df_comments)}")
        
        # 时间范围
        # .min() 和 .max() 找出最早和最晚的时间
        print(f"   时间范围: {self.df_videos['datetime'].min()} ~ "
              f"{self.df_videos['datetime'].max()}")
        
        # --- 按月统计 ---
        # .dt.to_period('M'): 把日期转换为月份（如：2024-01）
        self.df_videos['month'] = self.df_videos['datetime'].dt.to_period('M')
        
        # value_counts(): 统计每个月份的出现次数
        # sort_index(): 按月份排序
        monthly_counts = self.df_videos['month'].value_counts().sort_index()
        
        print(f"\n📅 各月份视频分布:")
        for month, count in monthly_counts.items():
            print(f"   {month}: {count} 条视频")
        
        # 找出视频最多的月份
        peak_month = monthly_counts.idxmax()  # idxmax() = 返回最大值的索引
        print(f"\n🔥 数据高峰期: {peak_month} ({monthly_counts.max()} 条视频)")
    
    # ==================== 步骤2: 识别活跃时间段 ====================
    def identify_active_periods(self):
        """
        识别用户活跃的时间段
        
        思路：
        1. 如果连续几天都有发视频 → 算一个活跃期
        2. 如果间隔超过7天 → 算两个不同的活跃期
        
        举例：
        1月1日发视频 → 1月3日发 → 1月5日发 → 算1个活跃期
        2月1日发视频 → 3月15日发（间隔>7天） → 算2个活跃期
        """
        print("\n" + "=" * 80)
        print("步骤2: 识别活跃时间段")
        print("=" * 80)
        
        # --- 2.1 按天统计视频数 ---
        # set_index('datetime'): 把时间列设为索引
        # resample('1D'): 按1天为单位重新采样
        # ['aweme_id'].count(): 统计每天的视频ID数量
        daily_counts = self.df_videos.set_index('datetime')\
                                     .resample('1D')['aweme_id']\
                                     .count()
        
        # 只保留有视频的日期（过滤掉计数为0的）
        active_days = daily_counts[daily_counts > 0]
        
        # 如果没有活跃日期，直接返回
        if len(active_days) == 0:
            print("⚠️  没有找到活跃时间段")
            return None
        
        print(f"✅ 发现 {len(active_days)} 个活跃日期")
        
        # --- 2.2 合并相邻的活跃日期 ---
        active_periods = []      # 存储活跃时间段列表
        current_start = None     # 当前时段的起始日期
        current_end = None       # 当前时段的结束日期
        
        # 遍历每个活跃日期
        for date in active_days.index:
            if current_start is None:
                # 第一个日期：开始一个新时段
                current_start = date
                current_end = date
            
            elif (date - current_end).days <= 7:
                # 如果距离上次 ≤7天：延长当前时段
                current_end = date
            
            else:
                # 如果距离上次 >7天：
                # 1. 保存之前的时段
                active_periods.append((current_start, current_end))
                
                # 2. 开始新时段
                current_start = date
                current_end = date
        
        # 保存最后一个时段
        if current_start is not None:
            active_periods.append((current_start, current_end))
        
        # --- 2.3 打印识别结果 ---
        print(f"\n📍 识别出 {len(active_periods)} 个活跃时间段:")
        
        for i, (start, end) in enumerate(active_periods, 1):
            # 计算时段持续天数
            duration = (end - start).days + 1
            
            # 统计这个时段的视频数
            video_count = len(self.df_videos[
                (self.df_videos['datetime'] >= start) & 
                (self.df_videos['datetime'] <= end)
            ])
            
            print(f"   {i}. {start.date()} ~ {end.date()} "
                  f"({duration}天, {video_count}条视频)")
        
        return active_periods
    
    # ==================== 步骤3: 选择最佳时间段 ====================
    def select_best_period(self, active_periods):
        """
        从多个活跃时段中选择最适合分析的一个
        
        选择标准：数据密度最高的时段
        
        评分公式：
            score = (视频数 + 评论数/10) / 天数
            
            解释：
            - 视频数多 → 分数高
            - 评论数多 → 加分（但权重较低，除以10）
            - 天数长 → 平均后分数低（我们希望数据密集）
        """
        print("\n" + "=" * 80)
        print("步骤3: 选择最佳分析时间段")
        print("=" * 80)
        
        best_period = None   # 存储最佳时段
        best_score = 0       # 最高得分
        
        # --- 遍历每个时段，计算得分 ---
        for start, end in active_periods:
            
            # 统计这个时段的视频数
            video_count = len(self.df_videos[
                (self.df_videos['datetime'] >= start) & 
                (self.df_videos['datetime'] <= end)
            ])
            
            # 统计这个时段的评论数
            comment_count = len(self.df_comments[
                (self.df_comments['datetime'] >= start) & 
                (self.df_comments['datetime'] <= end)
            ])
            
            # 计算持续天数
            duration = (end - start).days + 1
            
            # 计算得分（数据密度）
            score = (video_count + comment_count / 10) / duration
            
            # 如果这个时段得分更高，更新最佳时段
            if score > best_score:
                best_score = score
                best_period = (start, end, video_count, comment_count)
        
        # --- 打印最佳时段信息 ---
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
    
    # ==================== 根据时间段过滤数据 ====================
    def filter_by_period(self, start_date, end_date):
        """
        只保留指定时间段内的数据
        
        参数：
            start_date: 开始日期
            end_date: 结束日期
        
        返回：
            (filtered_videos, filtered_comments): 过滤后的数据
        """
        print("\n🔄 过滤数据到指定时间段...")
        
        # --- 创建布尔掩码（True/False数组） ---
        # 掩码作用：标记哪些行符合条件
        
        # 视频掩码：datetime在[start, end]范围内的为True
        mask_video = (
            (self.df_videos['datetime'] >= start_date) & 
            (self.df_videos['datetime'] <= end_date)
        )
        
        # 使用掩码过滤数据，.copy()创建副本避免修改原数据
        filtered_videos = self.df_videos[mask_video].copy()
        
        # 评论掩码（同理）
        mask_comment = (
            (self.df_comments['datetime'] >= start_date) & 
            (self.df_comments['datetime'] <= end_date)
        )
        
        filtered_comments = self.df_comments[mask_comment].copy()
        
        # 打印过滤结果
        print(f"✅ 过滤后数据量:")
        print(f"   视频: {len(self.df_videos)} → {len(filtered_videos)}")
        print(f"   评论: {len(self.df_comments)} → {len(filtered_comments)}")
        
        return filtered_videos, filtered_comments
    
    # ==================== 步骤4: 自适应调整时间窗口 ====================
    def adaptive_time_window(self, df_videos, df_comments):
        """
        自动选择最合适的时间窗口大小
        
        核心问题：
            用多大的时间窗口来聚合数据？
            
        选项示例：
            1H  = 每1小时一个数据点  → 时间点多，但可能很多空白
            6H  = 每6小时一个数据点  → 平衡
            1D  = 每1天一个数据点    → 时间点少，但数据密集
        
        选择标准：
            1. 保证足够的时间点数（至少30个，最好50+）
            2. 减少空白时间点（非零率要高）
            3. 保持适当的数据密度
        """
        print("\n" + "=" * 80)
        print("步骤4: 自适应时间窗口选择")
        print("=" * 80)
        
        # 🔧 定义要测试的窗口列表
        # 注意：移除了过大的窗口（如'3D', '7D'）防止时间点太少
        windows = ['1H', '3H', '6H', '12H', '1D']
        
        results = []  # 存储每个窗口的测试结果
        
        # --- 测试每个窗口 ---
        for window in windows:
            
            # 按当前窗口重新采样，统计视频数
            temp_features = df_videos.set_index('datetime')\
                                     .resample(window)\
                                     .agg({'aweme_id': 'count'})
            
            # 计算关键指标：
            
            # 1. 非零率 = 有数据的时间点占比
            # 例如：100个时间点中有40个>0，则非零率=40%
            non_zero_ratio = (temp_features['aweme_id'] > 0).sum() / \
                            len(temp_features) * 100
            
            # 2. 平均每个窗口的视频数
            avg_count = temp_features['aweme_id'].mean()
            
            # 3. 活跃时间点数 = 有数据的时间点总数
            time_points = (temp_features['aweme_id'] > 0).sum()
            
            # --- 评分策略（关键！） ---
            # 🔧 新的评分标准：优先保证足够的时间点数
            
            if time_points >= 50:
                # 如果时间点 ≥50: 优先选择，加倍奖励
                score = non_zero_ratio * avg_count * 2.0
                
            elif time_points >= 30:
                # 如果时间点 30-50: 可接受
                score = non_zero_ratio * avg_count * 1.0
                
            else:
                # 如果时间点 <30: 惩罚（不推荐）
                score = non_zero_ratio * avg_count * 0.3
            
            # 保存结果
            results.append({
                'window': window,
                'time_points': len(temp_features),      # 总时间点数
                'active_points': time_points,           # 活跃时间点数
                'non_zero_ratio': non_zero_ratio,       # 非零率
                'avg_count': avg_count,                 # 平均计数
                'score': score                          # 综合得分
            })
            
            # 打印当前窗口的测试结果
            print(f"   {window}: {time_points}个活跃点/"
                  f"{len(temp_features)}总点, "
                  f"{non_zero_ratio:.1f}%非零, "
                  f"平均{avg_count:.2f}条/窗口")
        
        # --- 选择得分最高的窗口 ---
        best = max(results, key=lambda x: x['score'])
        
        print(f"\n✅ 推荐时间窗口: {best['window']}")
        print(f"   活跃时间点: {best['active_points']}")
        print(f"   非零率: {best['non_zero_ratio']:.1f}%")
        print(f"   数据密度: {best['avg_count']:.2f}")
        
        # 🔧 强制检查：如果推荐窗口时间点太少，降级
        if best['active_points'] < 30:
            print(f"\n⚠️  推荐窗口({best['window']})的时间点数"
                  f"({best['active_points']})不足30")
            print(f"   自动降级到更小的时间窗口...")
            
            # 找出所有时间点 ≥30 的窗口
            valid_windows = [r for r in results if r['active_points'] >= 30]
            
            if valid_windows:
                # 选择满足条件的最小窗口（通常是第一个）
                best = valid_windows[0]
                print(f"   ✅ 降级到: {best['window']} "
                      f"({best['active_points']}个时间点)")
            else:
                # 如果都不满足，选择时间点最多的
                best = max(results, key=lambda x: x['active_points'])
                print(f"   ⚠️  所有窗口都不满足30点要求，"
                      f"选择最优: {best['window']} "
                      f"({best['active_points']}个时间点)")
        
        return best['window']
    
    # ==================== 步骤5: 提取特征 ====================
    def extract_features_optimized(self, df_videos, df_comments):
        """
        按时间窗口聚合数据，提取特征
        
        目标：
            把不规则的原始数据 → 规则的时间序列
            
        举例：
            原始: 
                2024-01-01 08:23 发了视频A
                2024-01-01 14:56 发了视频B
                2024-01-01 19:12 发了视频C
            
            聚合后（6小时窗口）:
                2024-01-01 06:00-12:00 → 1条视频
                2024-01-01 12:00-18:00 → 1条视频
                2024-01-01 18:00-24:00 → 1条视频
        """
        print("\n" + "=" * 80)
        print("步骤5: 提取特征(移除空白时间段)")
        print("=" * 80)
        
        # --- 5.1 聚合视频特征 ---
        
        # 设置时间为索引
        df_v = df_videos.set_index('datetime')
        df_c = df_comments.set_index('datetime')
        
        # 按时间窗口重新采样并聚合
        # resample(self.time_window): 按设定的窗口（如'6H'）分组
        # .agg({...}): 对每个分组应用聚合函数
        video_features = df_v.resample(self.time_window).agg({
            'aweme_id': 'count',        # 视频ID → 计数（发布数量）
            'liked_count': 'sum',       # 点赞数 → 求和（总点赞）
            'comment_count': 'sum',     # 评论数 → 求和
            'share_count': 'sum',       # 转发数 → 求和
            'collected_count': 'sum'    # 收藏数 → 求和
        }).rename(columns={
            # 重命名列名，让意义更清晰
            'aweme_id': 'video_count',
            'liked_count': 'total_likes',
            'comment_count': 'total_comments',
            'share_count': 'total_shares',
            'collected_count': 'total_collects'
        })
        
        # --- 5.2 聚合评论特征 ---
        comment_features = df_c.resample(self.time_window).agg({
            'comment_id': 'count',     # 评论数量
            'like_count': 'mean'       # 评论的平均点赞数
        }).rename(columns={
            'comment_id': 'comment_count',
            'like_count': 'avg_comment_likes'
        })
        
        # --- 5.3 合并两个特征表 ---
        # axis=1: 按列合并（横向拼接）
        # fillna(0): 空值填充为0
        features = pd.concat([video_features, comment_features], axis=1).fillna(0)
        
        print(f"\n📊 聚合前数据:")
        print(f"   时间窗口: {self.time_window}")
        print(f"   总时间点: {len(features)}")
        
        # --- 5.4 移除全零行（优化关键！） ---
        
        # 计算每行有多少个非零值
        # (features != 0): 创建布尔DataFrame（True表示非零）
        # .sum(axis=1): 按行求和，得到每行的非零个数
        non_zero_counts = (features != 0).sum(axis=1)
        
        # 只保留至少有1个非零值的行
        features_filtered = features[non_zero_counts > 0].copy()
        
        # 计算移除比例
        zero_ratio = (len(features) - len(features_filtered)) / \
                     len(features) * 100
        
        print(f"\n🔧 移除全零时间窗口:")
        print(f"   原始时间点: {len(features)}")
        print(f"   过滤后: {len(features_filtered)}")
        print(f"   移除比例: {zero_ratio:.1f}%")
        
        # --- 5.5 数据质量检查 ---
        print(f"\n📈 数据质量检查:")
        for col in features_filtered.columns:
            # 计算每个特征的非零率
            non_zero_ratio = (features_filtered[col] != 0).sum() / \
                            len(features_filtered) * 100
            print(f"   {col}: {non_zero_ratio:.1f}% 非零")
        
        return features_filtered
    
    # ==================== 步骤6: 保存优化后的数据 ====================
    def save_optimized_data(self, features, output_dir):
        """
        保存处理后的数据，生成多个文件
        
        输出文件：
        1. PCMCI格式的CSV（用于因果分析）
        2. 特征映射表（解释X1, X2...代表什么）
        3. 原始特征备份
        4. 数据摘要统计
        """
        print("\n" + "=" * 80)
        print("步骤6: 保存优化数据")
        print("=" * 80)
        
        output_path = Path(output_dir)
        
        # --- 6.1 数据标准化 ---
        # 为什么要标准化？
        # 因为不同特征的量级差异很大：
        #   点赞数: 几千
        #   视频数: 几个
        # 标准化后都变成均值0、标准差1的分布
        
        scaler = StandardScaler()
        normalized = pd.DataFrame(
            scaler.fit_transform(features),  # 执行标准化
            index=features.index,            # 保持时间索引
            columns=features.columns         # 保持列名
        )
        
        # --- 6.2 转换为PCMCI格式 ---
        # PCMCI工具要求列名为X1, X2, X3...
        
        n_vars = len(normalized.columns)
        var_names = [f'X{i+1}' for i in range(n_vars)]
        
        df_pcmci = normalized.copy()
        df_pcmci.columns = var_names       # 重命名列
        df_pcmci['time'] = range(len(df_pcmci))  # 添加时间索引列
        
        # --- 6.3 保存主文件 ---
        csv_path = output_path / f"douyin_pcmci_{self.time_window}_optimized.csv"
        df_pcmci.to_csv(csv_path, index=False)
        
        # --- 6.4 保存特征映射 ---
        # 记录X1, X2...分别代表什么
        mapping = {
            'X1': 'video_count (视频发布数量)',
            'X2': 'total_likes (视频总点赞数)',
            'X3': 'total_comments (视频总评论数)',
            'X4': 'total_shares (视频总转发数)',
            'X5': 'total_collects (视频总收藏数)',
            'X6': 'comment_count (评论发布数量)',
            'X7': 'avg_comment_likes (评论平均点赞数)'
        }
        
        # 保存为CSV，encoding='utf-8-sig'确保Excel能正确显示中文
        pd.DataFrame([mapping]).T.to_csv(
            output_path / "feature_mapping.csv",
            encoding='utf-8-sig',
            header=['特征说明']
        )
        
        # --- 6.5 保存原始特征（未标准化） ---
        features.to_csv(
            output_path / f"original_features_{self.time_window}_optimized.csv"
        )
        
        # --- 6.6 保存数据摘要 ---
        # .describe()生成统计信息（均值、标准差、最小值等）
        summary = features.describe()
        summary.to_csv(
            output_path / "data_summary_optimized.csv", 
            encoding='utf-8-sig'
        )
        
        # 打印保存信息
        print(f"\n✅ 文件已保存")
        print(f"   主文件: {csv_path.name}")
        print(f"   时间点数: {len(df_pcmci)}")
        print(f"   特征数: {n_vars}")
        
        return df_pcmci, csv_path
    
    # ==================== 可视化（可选） ====================
    def visualize_timeseries(self, features, output_dir):
        """
        生成时间序列可视化图表
        
        为每个特征生成一个子图，展示其随时间变化的趋势
        """
        try:
            output_path = Path(output_dir)
            
            # --- 配置matplotlib支持中文 ---
            plt.rcParams['font.sans-serif'] = [
                'SimHei',           # 黑体（Windows）
                'Arial Unicode MS', # Mac
                'DejaVu Sans'       # Linux
            ]
            plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
            
            # --- 创建7个子图（7个特征） ---
            # figsize=(14, 18): 图片宽14英寸，高18英寸
            fig, axes = plt.subplots(7, 1, figsize=(14, 18))
            
            # 特征的中文名称
            feature_names = [
                '视频发布数量',
                '视频总点赞数',
                '视频总评论数',
                '视频总转发数',
                '视频总收藏数',
                '评论发布数量',
                '评论平均点赞数'
            ]
            
            # --- 为每个特征绘图 ---
            for i, (col, name) in enumerate(zip(features.columns, feature_names)):
                try:
                    # 绘制折线图
                    axes[i].plot(
                        features.index,      # x轴：时间
                        features[col],       # y轴：特征值
                        linewidth=2,         # 线宽
                        color='steelblue'    # 颜色
                    )
                    
                    # 设置标题和标签
                    axes[i].set_title(
                        f'X{i+1}: {name}', 
                        fontsize=12, 
                        fontweight='bold'
                    )
                    axes[i].set_ylabel('Value', fontsize=10)
                    axes[i].grid(True, alpha=0.3)  # 添加网格
                    
                except Exception as e:
                    print(f"   ⚠️  绘制 {name} 时出错: {e}")
            
            # x轴标签（只在最下面的子图显示）
            axes[-1].set_xlabel('Time', fontsize=10)
            
            # 自动调整子图间距
            plt.tight_layout()
            
            # 保存图片
            viz_path = output_path / f"timeseries_visualization_{self.time_window}.png"
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            print(f"✅ 时间序列图已保存: {viz_path}")
            
            plt.close(fig)  # 关闭图形释放内存
            
        except Exception as e:
            print(f"⚠️  可视化失败: {e}")
            print(f"   但数据处理已完成,可继续使用CSV文件")
            # 即使可视化失败，也不中断程序
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