# B1C 数据集说明（TimeGraph）

## 1. 目录结构
- `data/TimeGraph/B1C/`
  - 噪声分布：`Gaussian error/`、`Students t error/`
  - 变量数：`4 variable/`、`6 variable/`、`8 variable/`
  - 最大滞后：`Lag 2/`、`Lag 3/`、`Lag 4/`
  - 样本量：文件名中的 `n500 / n1000 / n3000 / n5000`
  - 真值图：对应配置的 `n5000` 旁有 `_graph.png`

## 2. 文件命名示例
`nonlinear_confounded_n500_vars6_lag3_gaussian.csv`
- `nonlinear_confounded`：非线性 + 存在隐藏混杂 U
- `n500`：样本量（时间序列长度）
- `vars6`：6 个观测变量 X1..X6
- `lag3`：最大滞后 3
- `gaussian`：噪声分布为高斯（另有 `Students t` 厚尾版本）

## 3. 列含义
- `X1...Xk`：观测到的 k 个变量
- `U`：未观测混杂变量（实验时可丢弃，用于模拟隐藏混杂）
- `time`：时间索引（等间隔采样）

示例：
```1:5:data/TimeGraph/B1C/Gaussian error/4 variable/Lag 2/nonlinear_confounded_n500_vars4_lag2_gaussian.csv
X1,X2,X3,X4,U,time
0.0497,-0.0138,0.0648,0.1523,-0.0234,0
-0.0234,0.1579,0.0767,-0.0469,0.0543,1
```

## 4. 生成特性（B1C）
- 非线性：多项式依赖（二次/三次等），挑战线性方法
- 隐藏混杂：U 同时影响多个变量，制造伪相关
- 等间隔采样：无不规则抽样（与 B2/B2C 区分）
- 噪声：高斯或 Student-t（厚尾，鲁棒性测试）

## 5. 推荐使用组合
- **主实验**：`Gaussian error / 6 variable / Lag 2 或 3 / n3000 或 n5000`
  - 理由：非线性 + 混杂，变量数适中，样本量足够；高斯噪声便于基线
- **鲁棒性**：同配置切换 `Students t error`（厚尾噪声）
- **滞后敏感性**：同变量数下比较 Lag=2/3/4
- **混杂对照**：与 `B1` 同配置对比（无 U）评估混杂影响

## 6. 使用示例（Python）
```python
import pandas as pd

path = "data/TimeGraph/B1C/Gaussian error/6 variable/Lag 3/nonlinear_confounded_n3000_vars6_lag3_gaussian.csv"
df = pd.read_csv(path)

# 丢弃 U 列以模拟隐藏混杂场景
df_obs = df.drop(columns=["U"])

# 观测变量与时间
X = df_obs.drop(columns=["time"])
time = df_obs["time"]
```

## 7. 评估建议
- 因果发现：PCMCI/PCMCI+，与 `_graph.png` 真值对比 Precision/Recall/F1
- 滞后识别：检查滞后边的命中率
- 噪声鲁棒性：高斯 vs Student-t
- 样本量敏感性：n500 → n1000 → n3000 → n5000

## 8. 写作要点
- 选择理由：非线性 + 隐藏混杂，最贴近社交媒体传播特征
- 对照设计：B1 vs B1C，量化混杂影响
- 结果呈现：展示因果图对比、滞后识别、噪声与样本量敏感性

