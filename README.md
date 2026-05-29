# 基于因果推断的社交媒体事件传播分析

本项目为本科毕业设计，将时序因果发现方法应用于社交媒体事件传播分析，以抖音平台数据为研究对象，系统比较多种因果推断算法在合成数据集上的表现，并将最优方法迁移至真实传播数据，量化各传播指标之间的因果效应。

---

## 研究内容

1. **合成数据验证**：在 B1C 6变量合成数据集上，对比 PCMCI(GPDC)、ParCorr、LPCMCI、FGES、Granger、Kernel Granger、PC 共 7 种因果发现方法，以 Precision / Recall / F1 为指标评估各方法的结构恢复能力。
2. **真实数据分析**：将表现最优的方法应用于抖音事件传播数据，发现传播变量间的因果图结构，分析同时效应、短期效应、中期效应和长期效应。
3. **因果效应估计**：对发现的因果关系，使用简单线性回归、工具变量法（IV）和因果森林三种方法量化效应大小。

---

## 项目结构

```
.
├── data/                          # 原始数据
│   └── TimeGraph/A1C/Gaussian/    # 合成数据生成脚本
│
├── run_data/                      # PCMCI + GPDC 运行结果
├── run_data_granger/              # Granger 因果运行结果
├── run_data_fges/                 # FGES 运行结果
├── run_data_pc/                   # PC 算法运行结果
├── run_data_lpcmci/               # LPCMCI 运行结果
├── run_data_kernel_granger/       # Kernel Granger 运行结果
├── ParCorr/                       # ParCorr 运行结果
│
├── causal_graph_analysis/         # 因果图精炼与可视化输出
├── causal_effect_analysis/        # 因果效应估计输出
├── prediction_analysis/           # 预测分析输出
├── method_comparison_analysis/    # 多方法对比汇总报告
├── douyin_optimized/              # 抖音数据预处理输出
│
├── pcmci_analysis_b1c.py          # B1C 数据集 PCMCI 分析
├── pcmci_optimized.py             # PCMCI / LPCMCI 通用分析入口
├── pcmci_validation.py            # PCMCI 结果验证
├── run_lpcmci_b1c.py              # B1C 数据集 LPCMCI 批量运行
├── run_kernel_granger_b1c.py      # B1C 数据集 Kernel Granger 批量运行
├── b1c_method_comparison.py       # GPDC vs ParCorr 对比
├── b1c_all_methods_comparison.py  # 全方法对比表生成
├── causal_graph_refiner.py        # 因果图精炼与可视化
├── causal_effect_estimation.py    # 因果效应估计（3种方法）
├── douyin_data_optimizer.py       # 抖音数据稀疏性优化
├── douyin_to_pcmci.py             # 抖音数据转 PCMCI 格式
└── analyze_douyin_data.py         # 抖音数据探索分析
```

---

## 方法说明

| 方法 | 类型 | 说明 |
|------|------|------|
| PCMCI + GPDC | 时序因果发现 | 基于高斯过程距离相关的条件独立检验，本项目主方法 |
| PCMCI + ParCorr | 时序因果发现 | 基于偏相关的条件独立检验，计算效率高 |
| LPCMCI | 时序因果发现 | 支持潜在混杂变量的 PCMCI 扩展 |
| FGES | 结构学习 | 基于评分的快速贪婪等价搜索 |
| Granger | 时序因果 | 经典 Granger 因果检验 |
| Kernel Granger | 时序因果 | 核方法扩展的非线性 Granger 因果 |
| PC | 结构学习 | 经典 PC 算法 |

---

## 环境依赖

Python 3.8+，主要依赖如下：

```bash
pip install tigramite pandas numpy matplotlib scikit-learn networkx scipy seaborn
```

GPDC 检验需要额外安装 GPy：

```bash
pip install GPy
```

> 若 GPDC 不可用，程序会自动降级为 CMIknn。

---

## 快速开始

### 1. 在 B1C 合成数据集上运行 PCMCI 分析

```bash
python pcmci_analysis_b1c.py
```

### 2. 运行全方法对比实验（需先完成各方法的批量运行）

```bash
python b1c_all_methods_comparison.py
```

对比结果输出至 `method_comparison_analysis/b1c_all_methods_report.md`。

### 3. 对抖音数据进行预处理

```bash
python douyin_data_optimizer.py
```

### 4. 在抖音数据上运行 PCMCI 分析

```bash
python pcmci_optimized.py --dataset generic
```

### 5. 精炼因果图并生成可视化

```bash
python causal_graph_refiner.py
```

### 6. 估计因果效应

```bash
python causal_effect_estimation.py
```

---

## 主要结果

### B1C 合成数据集方法对比（lag2/lag3 × n500/n1000/n3000 共同设置）

| 排名 | 方法 | 平均 F1 |
|------|------|---------|
| 1 | GPDC | 0.1365 |
| 2 | ParCorr | 0.0741 |
| 3 | FGES | 0 |
| 4 | Granger | 0 |
| 5 | Kernel Granger | 0 |
| 6 | LPCMCI | 0 |
| 7 | PC | 0 |

GPDC 在小样本（n=500）下表现最优，在 lag2/n500 设置下 F1 达到 0.333。

### 抖音传播数据因果图

- 发现 7 个传播节点，43 条因果边
- 同时效应（Lag 0）最强，平均相关性 0.596
- 短期效应（Lag 1，约 12H）平均相关性 0.351
- 中期效应（Lag 2，约 24H）平均相关性 0.391

---

## 数据说明

- **B1C 合成数据集**：来自 TimeGraph 基准，包含 6 个观测变量（X1~X6）和 1 个潜在混杂变量（U），具有已知真值因果结构，用于方法评估。
- **抖音数据**：真实社交媒体事件传播数据，包含多个传播指标的时间序列，数据文件较大，未包含在本仓库中。

---

## 引用

本项目使用了以下开源工具：

- [Tigramite](https://github.com/jakobrunge/tigramite) — PCMCI / LPCMCI 框架
- [py-causal](https://github.com/bd2kccd/py-causal) — FGES 实现
- [NetworkX](https://networkx.org/) — 图结构分析

---

## 作者

本项目为本科毕业设计，作者：suerzzh
