import json
import pandas as pd
from datetime import datetime
import numpy as np

print("=" * 60)
print("抖音数据集分析报告")
print("=" * 60)

# 读取评论数据
print("\n1. 评论数据分析")
print("-" * 60)
with open('data/douyin/search_comments_2025-12-03.json', 'r', encoding='utf-8') as f:
    comments = json.load(f)

print(f"评论总数: {len(comments)}")

# 转换为DataFrame
comments_df = pd.DataFrame(comments)

# 时间戳转换
comments_df['datetime'] = pd.to_datetime(comments_df['create_time'], unit='s')
comments_df['date'] = comments_df['datetime'].dt.date
comments_df['hour'] = comments_df['datetime'].dt.hour

print(f"\n时间范围:")
print(f"  最早: {comments_df['datetime'].min()}")
print(f"  最晚: {comments_df['datetime'].max()}")
print(f"  时间跨度: {comments_df['datetime'].max() - comments_df['datetime'].min()}")

print(f"\n数据字段:")
for col in comments_df.columns:
    print(f"  - {col}")

print(f"\n每小时评论数统计:")
hourly_counts = comments_df.groupby('hour').size()
print(hourly_counts.head(10))

print(f"\n每日评论数统计:")
daily_counts = comments_df.groupby('date').size()
print(daily_counts)

print(f"\n视频ID分布:")
print(f"  唯一视频数: {comments_df['aweme_id'].nunique()}")
print(f"  每个视频的平均评论数: {len(comments_df) / comments_df['aweme_id'].nunique():.2f}")

print(f"\n用户互动统计:")
print(f"  平均点赞数: {comments_df['like_count'].mean():.2f}")
print(f"  平均子评论数: {comments_df['sub_comment_count'].astype(int).mean():.2f}")

# 读取内容数据
print("\n\n2. 内容数据分析")
print("-" * 60)
try:
    with open('data/douyin/search_contents_2025-12-03.json', 'r', encoding='utf-8') as f:
        contents = json.load(f)
    
    print(f"内容总数: {len(contents)}")
    
    if len(contents) > 0:
        contents_df = pd.DataFrame(contents)
        print(f"\n内容数据字段:")
        for col in contents_df.columns:
            print(f"  - {col}")
        
        if 'create_time' in contents_df.columns:
            contents_df['datetime'] = pd.to_datetime(contents_df['create_time'], unit='s')
            print(f"\n内容时间范围:")
            print(f"  最早: {contents_df['datetime'].min()}")
            print(f"  最晚: {contents_df['datetime'].max()}")
except Exception as e:
    print(f"读取内容数据时出错: {e}")

print("\n\n3. 数据质量评估")
print("-" * 60)

# 检查缺失值
print("\n评论数据缺失值:")
missing = comments_df.isnull().sum()
print(missing[missing > 0])

# 检查重复
print(f"\n重复评论数: {comments_df['comment_id'].duplicated().sum()}")

# 检查时间序列连续性
print(f"\n时间序列特征:")
print(f"  时间点总数: {comments_df['datetime'].nunique()}")
print(f"  可以按小时聚合: {'是' if comments_df['datetime'].nunique() > 24 else '否'}")

print("\n\n4. 适用性评估")
print("-" * 60)
print("\n✅ 适合的特征:")
print("  - 有时间戳，可以构建时间序列")
print("  - 有评论内容，可以进行情感分析")
print("  - 有互动数据（点赞、子评论），可以作为传播指标")
print("  - 有视频ID，可以分析不同内容的传播差异")
print("  - 有地理位置，可以作为协变量")

print("\n⚠️  需要注意的问题:")
print("  - 需要确认时间跨度是否足够（PCMCI需要足够的时间点）")
print("  - 需要将评论内容转换为情感分数")
print("  - 需要按时间聚合（小时/天）构建多变量时间序列")
print("  - 需要定义因果变量（如：情感 -> 传播量）")

