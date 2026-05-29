# PCMCI因果发现分析运行日志

## 运行信息
- **开始时间**: 2026-01-16 18:44:01
- **结束时间**: 2026-01-16 18:45:34
- **总耗时**: 0:01:33.449300

---

## 运行输出

```
================================================================================
PCMCI因果发现分析 - B1C数据集(非线性数据)
================================================================================

📂 正在加载数据: data\TimeGraph\B1C\Gaussian error\6 variable\Lag 3\nonlinear_confounded_n500_vars6_lag3_gaussian.csv
   数据形状: (500, 8)
   列名: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'U', 'time']
   ✅ 成功加载 6 个观测变量: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']
   ✅ 数据维度: (500, 6) (时间点数 × 变量数)

📊 数据集信息:
   数据集类型: B1C
   噪声类型: Gaussian
   变量数: 6
   最大滞后: 3
   样本量: 500
   输出目录: run_data\B1C\Gaussian\6variable\lag3\n500

🔍 开始运行PCMCI因果发现...
   最大滞后 (tau_max): 3
   显著性水平 (alpha): 0.05
   检验方法: GPDC (非线性)

   正在计算因果关系(这可能需要一些时间)...

##
## Step 1: PC1 algorithm for selecting lagged conditions
##

Parameters:
independence test = gp_dc
tau_min = 1
tau_max = 3
pc_alpha = [0.2]
max_conds_dim = None
max_combinations = 1



## Resulting lagged parent (super)sets:

    Variable X1 has 3 link(s):
        (X4 -2): max_pval = 0.04800, |min_val| =  0.104
        (X1 -2): max_pval = 0.07200, |min_val| =  0.098
        (X3 -3): max_pval = 0.13000, |min_val| =  0.087

    Variable X2 has 4 link(s):
        (X4 -1): max_pval = 0.02800, |min_val| =  0.112
        (X1 -2): max_pval = 0.11000, |min_val| =  0.092
        (X4 -3): max_pval = 0.12600, |min_val| =  0.088
        (X1 -3): max_pval = 0.13600, |min_val| =  0.086

    Variable X3 has 1 link(s):
        (X1 -2): max_pval = 0.00000, |min_val| =  0.158

    Variable X4 has 3 link(s):
        (X4 -1): max_pval = 0.12600, |min_val| =  0.088
        (X5 -3): max_pval = 0.14600, |min_val| =  0.085
        (X2 -1): max_pval = 0.15600, |min_val| =  0.085

    Variable X5 has 4 link(s):
        (X2 -3): max_pval = 0.06800, |min_val| =  0.100
        (X1 -2): max_pval = 0.11400, |min_val| =  0.090
        (X4 -1): max_pval = 0.13800, |min_val| =  0.086
        (X1 -3): max_pval = 0.18000, |min_val| =  0.082

    Variable X6 has 3 link(s):
        (X6 -1): max_pval = 0.06000, |min_val| =  0.101
        (X4 -1): max_pval = 0.15200, |min_val| =  0.085
        (X6 -2): max_pval = 0.16800, |min_val| =  0.083

##
## Step 2: MCI algorithm
##

Parameters:

independence test = gp_dc
tau_min = 0
tau_max = 3
max_conds_py = None
max_conds_px = None

## Significant links at alpha = 0.05:

    Variable X1 has 2 link(s):
        (X4 -2): pval = 0.04200 | val =  0.107
        (X2  0): pval = 0.04400 | val =  0.105 | unoriented link

    Variable X2 has 2 link(s):
        (X4 -1): pval = 0.03400 | val =  0.111
        (X1  0): pval = 0.04400 | val =  0.105 | unoriented link

    Variable X3 has 1 link(s):
        (X1 -2): pval = 0.00000 | val =  0.154

    Variable X4 has 0 link(s):

    Variable X5 has 1 link(s):
        (X6  0): pval = 0.01000 | val =  0.125 | unoriented link

    Variable X6 has 1 link(s):
        (X5  0): pval = 0.01000 | val =  0.125 | unoriented link
   ✅ PCMCI运行完成!

🔍 调试信息:
   p_matrix矩阵形状: (6, 6, 4)
   显著关系 (p < 0.05):
      X2 --[Lag0]--> X1 | p=0.044000
      X3 --[Lag2]--> X1 | p=0.000000
      X1 --[Lag0]--> X2 | p=0.044000
      X1 --[Lag2]--> X4 | p=0.042000
      X2 --[Lag1]--> X4 | p=0.034000
      X6 --[Lag0]--> X5 | p=0.010000
      X5 --[Lag0]--> X6 | p=0.010000
   总共发现 7 个显著因果关系 (p < 0.05)

📋 发现的因果关系 (显著性水平: 0.05):
================================================================================
   ✅ 发现 7 个显著的因果关系:

   1. X3 --[2步滞后]--> X1
      p值: 0.000000 | 相关性强度: 0.1537

   2. X6 <--> X5 (同时发生(无方向))
      p值: 0.010000 | 相关性强度: 0.1246

   3. X5 <--> X6 (同时发生(无方向))
      p值: 0.010000 | 相关性强度: 0.1246

   4. X2 --[1步滞后]--> X4
      p值: 0.034000 | 相关性强度: 0.1107

   5. X1 --[2步滞后]--> X4
      p值: 0.042000 | 相关性强度: 0.1065

   6. X2 <--> X1 (同时发生(无方向))
      p值: 0.044000 | 相关性强度: 0.1052

   7. X1 <--> X2 (同时发生(无方向))
      p值: 0.044000 | 相关性强度: 0.1052


📊 正在生成因果图...
   ✅ 因果图已保存: run_data\B1C\Gaussian\6variable\lag3\n500\pcmci_causal_graph.png

💾 正在保存结果...
   ✅ 结果已保存: run_data\B1C\Gaussian\6variable\lag3\n500\pcmci_results.csv
   共 144 条关系记录
   其中 7 条显著因果关系 (p < 0.05)
   ✅ 显著关系已单独保存: run_data\B1C\Gaussian\6variable\lag3\n500\pcmci_significant_links.csv
   ✅ 数据集信息已保存: run_data\B1C\Gaussian\6variable\lag3\n500\dataset_info.csv

================================================================================
✅ PCMCI分析完成!
================================================================================

📁 结果文件保存在: run_data\B1C\Gaussian\6variable\lag3\n500
   1. pcmci_causal_graph.png - 因果图
   2. pcmci_results.csv - 完整结果数据
   3. pcmci_significant_links.csv - 仅显著关系
   4. dataset_info.csv - 数据集信息
   5. analysis_log.md - 运行日志 🆕

💡 重要提示:
   - B1C数据集是非线性数据,使用了GPDC非线性检验方法
   - 使用p_matrix判断显著性,而非graph矩阵
   - 对比ground truth图评估结果准确性

```

---

## 日志说明
- 本日志由PCMCI分析程序自动生成
- 包含完整的运行过程和结果输出
- 可用于复现分析过程和结果验证
