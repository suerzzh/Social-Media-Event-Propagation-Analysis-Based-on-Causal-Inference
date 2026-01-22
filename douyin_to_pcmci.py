"""
抖音数据 → PCMCI时间序列完整处理方案
适用于:基于因果推断的社交媒体事件传播分析

作者:毕设项目
数据:抖音核污水事件相关视频和评论
"""

import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class DouyinToPCMCI:
    """
    将抖音search_contents和search_comments转换为PCMCI时间序列
    """
    
    def __init__(self, time_window='6H'):
        """
        参数:
            time_window: 时间窗口
                - '1H': 1小时 (适合短期分析)
                - '6H': 6小时 (推荐)
                - '12H': 12小时
                - '1D': 1天 (适合长期分析)
        """
        self.time_window = time_window
        self.df_videos = None
        self.df_comments = None
        
    def load_data(self, contents_file, comments_file):
        """
        步骤1: 加载JSON数据
        """
        print("=" * 80)
        print("步骤1: 加载抖音原始数据")
        print("=" * 80)

        # 当前脚本目录
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # data/douyin 目录
        data_dir = os.path.join(base_dir, "data", "douyin")

        # 完整路径
        contents_path = os.path.join(data_dir, contents_file)
        comments_path = os.path.join(data_dir, comments_file)

        # 安全检查（非常重要）
        if not os.path.exists(contents_path):
            raise FileNotFoundError(f"❌ 视频文件不存在: {contents_path}")

        if not os.path.exists(comments_path):
            raise FileNotFoundError(f"❌ 评论文件不存在: {comments_path}")

        # 读取 JSON
        with open(contents_path, "r", encoding="utf-8") as f:
            videos = json.load(f)

        with open(comments_path, "r", encoding="utf-8") as f:
            comments = json.load(f)

        # 转 DataFrame
        self.df_videos = pd.DataFrame(videos)
        self.df_comments = pd.DataFrame(comments)

        print(f"✅ 视频数据: {len(self.df_videos)} 条")
        print(f"✅ 评论数据: {len(self.df_comments)} 条")

        # 数据清洗
        self._clean_data()

        return self.df_videos, self.df_comments

    
    def _clean_data(self):
        """
        数据清洗和类型转换
        """
        print("\n🔄 数据清洗中...")
        
        # 视频数据处理
        # 转换时间戳
        self.df_videos['datetime'] = pd.to_datetime(
            self.df_videos['create_time'], 
            unit='s'
        )
        
        # 转换数值字段(可能是字符串)
        numeric_fields = ['liked_count', 'collected_count', 'comment_count', 'share_count']
        for field in numeric_fields:
            self.df_videos[field] = pd.to_numeric(
                self.df_videos[field], 
                errors='coerce'
            ).fillna(0)
        
        # 评论数据处理
        self.df_comments['datetime'] = pd.to_datetime(
            self.df_comments['create_time'], 
            unit='s'
        )
        self.df_comments['like_count'] = pd.to_numeric(
            self.df_comments['like_count'], 
            errors='coerce'
        ).fillna(0)
        
        print(f"✅ 数据清洗完成")
        print(f"   视频时间范围: {self.df_videos['datetime'].min()} ~ {self.df_videos['datetime'].max()}")
        print(f"   评论时间范围: {self.df_comments['datetime'].min()} ~ {self.df_comments['datetime'].max()}")
    
    def extract_features(self):
        """
        步骤2: 提取时间序列特征
        
        特征设计(7个变量):
        X1: 视频发布数量 - 内容生产强度
        X2: 视频总点赞数 - 内容认可度
        X3: 视频总评论数 - 讨论热度
        X4: 视频总转发数 - 扩散强度
        X5: 视频总收藏数 - 内容价值
        X6: 评论发布数量 - 二次传播强度
        X7: 评论平均点赞数 - 评论质量/共鸣度
        """
        print("\n" + "=" * 80)
        print("步骤2: 提取时间序列特征")
        print("=" * 80)
        
        # 设置时间索引
        df_v = self.df_videos.set_index('datetime')
        df_c = self.df_comments.set_index('datetime')
        
        # 按时间窗口聚合视频特征
        print(f"\n🔄 按 {self.time_window} 时间窗口聚合...")
        
        video_features = df_v.resample(self.time_window).agg({
            'aweme_id': 'count',           # X1: 视频数量
            'liked_count': 'sum',          # X2: 总点赞
            'comment_count': 'sum',        # X3: 总评论
            'share_count': 'sum',          # X4: 总转发
            'collected_count': 'sum'       # X5: 总收藏
        }).rename(columns={
            'aweme_id': 'video_count',
            'liked_count': 'total_likes',
            'comment_count': 'total_comments',
            'share_count': 'total_shares',
            'collected_count': 'total_collects'
        })
        
        # 按时间窗口聚合评论特征
        comment_features = df_c.resample(self.time_window).agg({
            'comment_id': 'count',         # X6: 评论数量
            'like_count': 'mean'           # X7: 平均点赞
        }).rename(columns={
            'comment_id': 'comment_count',
            'like_count': 'avg_comment_likes'
        })
        
        # 合并特征
        features = pd.concat([video_features, comment_features], axis=1)
        
        # 填充缺失值(某些时间窗口可能没有数据)
        features = features.fillna(0)
        
        print(f"\n✅ 特征提取完成:")
        print(f"   时间窗口: {self.time_window}")
        print(f"   时间点数: {len(features)}")
        print(f"   特征维度: {features.shape[1]}")
        print(f"\n📊 特征列表:")
        for i, col in enumerate(features.columns, 1):
            print(f"   X{i}: {col}")
        
        return features
    
    def normalize_features(self, features):
        """
        步骤3: 特征标准化
        
        使用Z-score标准化,使所有特征在同一尺度
        """
        print("\n" + "=" * 80)
        print("步骤3: 特征标准化 (Z-score)")
        print("=" * 80)
        
        scaler = StandardScaler()
        
        normalized = pd.DataFrame(
            scaler.fit_transform(features),
            index=features.index,
            columns=features.columns
        )
        
        print(f"✅ 标准化完成")
        print(f"   均值: ~0, 标准差: ~1")
        
        return normalized, features
    
    def create_pcmci_format(self, normalized_data, output_dir):
        """
        步骤4: 转换为PCMCI格式CSV
        
        格式:
        X1,X2,X3,X4,X5,X6,X7,time
        0.12,-0.45,0.33,0.88,-0.21,0.67,0.11,0
        -0.34,0.56,-0.12,0.23,0.89,-0.33,0.44,1
        ...
        """
        print("\n" + "=" * 80)
        print("步骤4: 生成PCMCI格式文件")
        print("=" * 80)
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        # 重命名列为 X1, X2, X3, ...
        n_vars = len(normalized_data.columns)
        var_names = [f'X{i+1}' for i in range(n_vars)]
        
        df_pcmci = normalized_data.copy()
        df_pcmci.columns = var_names
        
        # 添加时间列(从0开始的整数索引)
        df_pcmci['time'] = range(len(df_pcmci))
        
        # 保存PCMCI格式CSV
        csv_path = output_path / f"douyin_pcmci_{self.time_window}.csv"
        df_pcmci.to_csv(csv_path, index=False)
        
        print(f"\n✅ PCMCI格式文件已保存:")
        print(f"   路径: {csv_path}")
        print(f"   变量数: {n_vars}")
        print(f"   时间点数: {len(df_pcmci)}")
        
        return df_pcmci, var_names, csv_path
    
    def save_metadata(self, features, normalized_data, output_dir):
        """
        步骤5: 保存元数据和原始特征
        """
        print("\n" + "=" * 80)
        print("步骤5: 保存元数据")
        print("=" * 80)
        
        output_path = Path(output_dir)
        
        # 1. 特征映射表
        feature_mapping = {
            'X1': 'video_count (视频发布数量 - 内容生产强度)',
            'X2': 'total_likes (视频总点赞数 - 内容认可度)',
            'X3': 'total_comments (视频总评论数 - 讨论热度)',
            'X4': 'total_shares (视频总转发数 - 扩散强度)',
            'X5': 'total_collects (视频总收藏数 - 内容价值)',
            'X6': 'comment_count (评论发布数量 - 二次传播强度)',
            'X7': 'avg_comment_likes (评论平均点赞数 - 评论质量/共鸣度)'
        }
        
        mapping_df = pd.DataFrame([feature_mapping]).T
        mapping_df.columns = ['特征说明']
        
        mapping_path = output_path / "feature_mapping.csv"
        mapping_df.to_csv(mapping_path, encoding='utf-8-sig')
        print(f"✅ 特征映射已保存: {mapping_path}")
        
        # 2. 原始聚合数据(未标准化)
        original_path = output_path / f"original_features_{self.time_window}.csv"
        features.to_csv(original_path)
        print(f"✅ 原始特征已保存: {original_path}")
        
        # 3. 标准化后的数据
        normalized_path = output_path / f"normalized_features_{self.time_window}.csv"
        normalized_data.to_csv(normalized_path)
        print(f"✅ 标准化特征已保存: {normalized_path}")
        
        # 4. 数据统计摘要
        summary = features.describe()
        summary_path = output_path / "data_summary.csv"
        summary.to_csv(summary_path, encoding='utf-8-sig')
        print(f"✅ 数据摘要已保存: {summary_path}")
        
        # 5. 处理配置信息
        config = {
            '时间窗口': self.time_window,
            '视频数量': len(self.df_videos),
            '评论数量': len(self.df_comments),
            '时间序列长度': len(features),
            '特征维度': len(features.columns),
            '时间范围开始': str(features.index.min()),
            '时间范围结束': str(features.index.max())
        }
        
        config_df = pd.DataFrame([config]).T
        config_df.columns = ['值']
        config_path = output_path / "processing_config.csv"
        config_df.to_csv(config_path, encoding='utf-8-sig')
        print(f"✅ 处理配置已保存: {config_path}")
    
    def visualize_timeseries(self, features, output_dir):
        """
        步骤6: 可视化时间序列
        """
        print("\n" + "=" * 80)
        print("步骤6: 生成可视化图表")
        print("=" * 80)
        
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        matplotlib.rcParams['axes.unicode_minus'] = False
        
        output_path = Path(output_dir)
        
        # 绘制所有特征的时间序列
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
            axes[i].plot(features.index, features[col], linewidth=2)
            axes[i].set_title(f'X{i+1}: {name}', fontsize=12, fontweight='bold')
            axes[i].set_ylabel('数值', fontsize=10)
            axes[i].grid(True, alpha=0.3)
        
        axes[-1].set_xlabel('时间', fontsize=10)
        plt.tight_layout()
        
        viz_path = output_path / "timeseries_visualization.png"
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        print(f"✅ 时间序列图已保存: {viz_path}")
        plt.close()

def main():
    """
    主处理流程
    """
    print("=" * 80)
    print("抖音数据 → PCMCI时间序列转换器")
    print("毕设项目:基于因果推断的社交媒体事件传播分析")
    print("=" * 80)
    
    # ========== 配置参数 ==========
    # 📌 修改这里的文件路径
    contents_file = "search_contents_2025-12-03.json"
    comments_file = "search_comments_2025-12-03.json"
    
    # 输出目录
    output_dir = "douyin_processed"
    
    # 时间窗口设置
    # 推荐: '6H' (6小时) 或 '12H' (12小时)
    # 注意: 你的数据时间跨度较短,可能需要更小的时间窗口如 '1H'
    time_window = '1H'  # 根据数据量调整
    
    # ========== 创建处理器 ==========
    processor = DouyinToPCMCI(time_window=time_window)
    
    # ========== 执行处理流程 ==========
    try:
        # 步骤1: 加载数据
        df_videos, df_comments = processor.load_data(contents_file, comments_file)
        
        # 步骤2: 提取特征
        features = processor.extract_features()
        
        # 步骤3: 标准化
        normalized, original = processor.normalize_features(features)
        
        # 步骤4: 生成PCMCI格式
        df_pcmci, var_names, csv_path = processor.create_pcmci_format(
            normalized, 
            output_dir
        )
        
        # 步骤5: 保存元数据
        processor.save_metadata(original, normalized, output_dir)
        
        # 步骤6: 可视化
        processor.visualize_timeseries(original, output_dir)
        
        # ========== 完成提示 ==========
        print("\n" + "=" * 80)
        print("✅ 数据处理完成!")
        print("=" * 80)
        
        print(f"\n📁 输出文件列表:")
        print(f"   1. {csv_path.name} - PCMCI输入文件 ⭐")
        print(f"   2. feature_mapping.csv - 特征说明")
        print(f"   3. original_features_{time_window}.csv - 原始特征")
        print(f"   4. normalized_features_{time_window}.csv - 标准化特征")
        print(f"   5. data_summary.csv - 数据统计摘要")
        print(f"   6. processing_config.csv - 处理配置")
        print(f"   7. timeseries_visualization.png - 时间序列图")
        
        print(f"\n📌 下一步操作:")
        print(f"   1. 检查时间序列图,确认数据质量")
        print(f"   2. 将 {csv_path.name} 用于PCMCI分析")
        print(f"   3. 参考 feature_mapping.csv 解释因果关系")
        
        print(f"\n💡 PCMCI运行命令:")
        print(f"   修改PCMCI代码中的数据路径为:")
        print(f"   data_path = Path('{csv_path}')")
        
        return df_pcmci, var_names
        
    except FileNotFoundError as e:
        print(f"\n❌ 文件未找到: {e}")
        print("   请检查JSON文件路径是否正确")
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()