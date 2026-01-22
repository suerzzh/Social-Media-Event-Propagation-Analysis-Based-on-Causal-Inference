import json
from datetime import datetime

# 读取评论数据
with open('data/douyin/search_comments_2025-12-03.json', 'r', encoding='utf-8') as f:
    comments = json.load(f)

# 读取内容数据
with open('data/douyin/search_contents_2025-12-03.json', 'r', encoding='utf-8') as f:
    contents = json.load(f)

print("=" * 60)
print("快速数据检查")
print("=" * 60)

print(f"\n评论数据: {len(comments)} 条")
print(f"内容数据: {len(contents)} 条")

# 检查时间范围
comment_times = [c['create_time'] for c in comments if 'create_time' in c]
content_times = [c['create_time'] for c in contents if 'create_time' in c]

if comment_times:
    min_time = min(comment_times)
    max_time = max(comment_times)
    time_span = max_time - min_time
    
    print(f"\n评论时间范围:")
    print(f"  最早: {datetime.fromtimestamp(min_time)}")
    print(f"  最晚: {datetime.fromtimestamp(max_time)}")
    print(f"  时间跨度: {time_span/3600:.2f} 小时 ({time_span/86400:.2f} 天)")

if content_times:
    min_time = min(content_times)
    max_time = max(content_times)
    time_span = max_time - min_time
    
    print(f"\n内容时间范围:")
    print(f"  最早: {datetime.fromtimestamp(min_time)}")
    print(f"  最晚: {datetime.fromtimestamp(max_time)}")
    print(f"  时间跨度: {time_span/3600:.2f} 小时 ({time_span/86400:.2f} 天)")

# 检查关键字段
print(f"\n评论数据字段示例:")
if comments:
    print(f"  字段: {list(comments[0].keys())}")

print(f"\n内容数据字段示例:")
if contents:
    print(f"  字段: {list(contents[0].keys())}")

