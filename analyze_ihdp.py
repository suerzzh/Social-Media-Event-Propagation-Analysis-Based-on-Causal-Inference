import pandas as pd
import numpy as np

# 读取数据
df1 = pd.read_csv('data/ihdp_npci_1.csv', header=None)
df2 = pd.read_csv('data/ihdp_npci_2.csv', header=None)
df3 = pd.read_csv('data/ihdp_npci_3.csv', header=None)

print("=" * 60)
print("IHDP数据集分析报告")
print("=" * 60)

print(f"\n数据集1形状: {df1.shape}")
print(f"数据集2形状: {df2.shape}")
print(f"数据集3形状: {df3.shape}")

print("\n数据集1前5行:")
print(df1.head())

print("\n列结构分析:")
print(f"总列数: {df1.shape[1]}")
print(f"第1列 (Treatment): 唯一值 = {sorted(df1[0].unique())}")
print(f"Treatment分布:\n{df1[0].value_counts().sort_index()}")

print("\n第2-3列 (Outcome) 统计:")
print(df1[[1, 2]].describe())

print("\n第4-5列 (潜在结果) 统计:")
print(df1[[3, 4]].describe())

print("\n连续协变量 (第6-15列) 统计:")
print(df1.iloc[:, 5:15].describe())

print("\n离散协变量 (第16-29列) 唯一值统计:")
for col in range(15, 29):
    unique_vals = df1[col].unique()
    print(f"列{col+1}: 唯一值 = {sorted(unique_vals)}, 分布 = {df1[col].value_counts().to_dict()}")

print("\n" + "=" * 60)
print("关键发现:")
print("=" * 60)

# 检查是否有时间维度
print("\n1. 数据维度:")
print("   - 这是一个横截面数据集（无时间维度）")
print("   - 每行代表一个观测单位（如婴儿）")

print("\n2. 数据结构:")
print("   - 第1列: Treatment (0/1)")
print("   - 第2-3列: 观察到的结果")
print("   - 第4-5列: 真实潜在结果（ground truth）")
print("   - 第6-15列: 10个连续协变量")
print("   - 第16-29列: 14个离散协变量")

print("\n3. 适用性评估:")
print("   ⚠️  注意: IHDP是横截面数据，而你的研究是时间序列问题")
print("   - IHDP适合验证: DoubleML, RDD等横截面因果推断方法")
print("   - IHDP不适合验证: PCMCI（需要时间序列数据）")
print("   - IHDP不适合验证: LSTM时间序列预测")

