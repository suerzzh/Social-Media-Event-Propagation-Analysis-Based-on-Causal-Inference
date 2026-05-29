# PCMCI因果发现分析运行日志

## 运行信息
- **开始时间**: 2026-01-16 18:46:39
- **结束时间**: 2026-01-16 18:56:38
- **总耗时**: 0:09:58.983130

---

## 运行输出

```
================================================================================
PCMCI因果发现分析 - B1C数据集(非线性数据)
================================================================================

📂 正在加载数据: data\TimeGraph\B1C\Gaussian error\6 variable\Lag 3\nonlinear_confounded_n1000_vars6_lag3_gaussian.csv
   数据形状: (1000, 8)
   列名: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'U', 'time']
   ✅ 成功加载 6 个观测变量: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']
   ✅ 数据维度: (1000, 6) (时间点数 × 变量数)

📊 数据集信息:
   数据集类型: B1C
   噪声类型: Gaussian
   变量数: 6
   最大滞后: 3
   样本量: 1000
   输出目录: run_data\B1C\Gaussian\6variable\lag3\n1000

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
        (X1 -2): max_pval = 0.00400, |min_val| =  0.092
        (X3 -3): max_pval = 0.11000, |min_val| =  0.063
        (X4 -2): max_pval = 0.15800, |min_val| =  0.059

    Variable X2 has 3 link(s):
        (X4 -1): max_pval = 0.05800, |min_val| =  0.068
        (X3 -3): max_pval = 0.06000, |min_val| =  0.067
        (X1 -3): max_pval = 0.17800, |min_val| =  0.058

    Variable X3 has 4 link(s):
        (X1 -2): max_pval = 0.03400, |min_val| =  0.073
        (X1 -1): max_pval = 0.04800, |min_val| =  0.070
        (X4 -2): max_pval = 0.08000, |min_val| =  0.065
        (X2 -1): max_pval = 0.19800, |min_val| =  0.057

    Variable X4 has 5 link(s):
        (X5 -2): max_pval = 0.07000, |min_val| =  0.066
        (X2 -1): max_pval = 0.07000, |min_val| =  0.066
        (X4 -3): max_pval = 0.11000, |min_val| =  0.063
        (X1 -2): max_pval = 0.14000, |min_val| =  0.060
        (X3 -2): max_pval = 0.15200, |min_val| =  0.060

    Variable X5 has 2 link(s):
        (X4 -3): max_pval = 0.01600, |min_val| =  0.084
        (X3 -3): max_pval = 0.10000, |min_val| =  0.063

    Variable X6 has 4 link(s):
        (X6 -2): max_pval = 0.01400, |min_val| =  0.084
        (X1 -1): max_pval = 0.06800, |min_val| =  0.066
        (X3 -1): max_pval = 0.07000, |min_val| =  0.066
        (X4 -3): max_pval = 0.17200, |min_val| =  0.059

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
        (X1 -2): pval = 0.00200 | val =  0.094
        (X2  0): pval = 0.04800 | val =  0.071 | unoriented link

    Variable X2 has 2 link(s):
        (X3 -3): pval = 0.04800 | val =  0.071
        (X1  0): pval = 0.04800 | val =  0.071 | unoriented link

    Variable X3 has 2 link(s):
        (X1 -2): pval = 0.03200 | val =  0.074
        (X1 -1): pval = 0.04200 | val =  0.072

    Variable X4 has 0 link(s):

    Variable X5 has 2 link(s):
        (X6  0): pval = 0.01200 | val =  0.087 | unoriented link
        (X4 -3): pval = 0.01800 | val =  0.082

    Variable X6 has 2 link(s):
        (X5  0): pval = 0.01200 | val =  0.087 | unoriented link
        (X6 -2): pval = 0.01400 | val =  0.085
   ✅ PCMCI运行完成!

🔍 调试信息:
   p_matrix矩阵形状: (6, 6, 4)
   显著关系 (p < 0.05):
      X1 --[Lag2]--> X1 | p=0.002000
      X2 --[Lag0]--> X1 | p=0.048000
      X3 --[Lag1]--> X1 | p=0.042000
      X3 --[Lag2]--> X1 | p=0.032000
      X1 --[Lag0]--> X2 | p=0.048000
      X2 --[Lag3]--> X3 | p=0.048000
      X5 --[Lag3]--> X4 | p=0.018000
      X6 --[Lag0]--> X5 | p=0.012000
      X5 --[Lag0]--> X6 | p=0.012000
      X6 --[Lag2]--> X6 | p=0.014000
   总共发现 10 个显著因果关系 (p < 0.05)

📋 发现的因果关系 (显著性水平: 0.05):
================================================================================
   ✅ 发现 10 个显著的因果关系:

   1. X1 --[2步滞后]--> X1
      p值: 0.002000 | 相关性强度: 0.0935

   2. X6 <--> X5 (同时发生(无方向))
      p值: 0.012000 | 相关性强度: 0.0866

   3. X5 <--> X6 (同时发生(无方向))
      p值: 0.012000 | 相关性强度: 0.0866

   4. X6 --[2步滞后]--> X6
      p值: 0.014000 | 相关性强度: 0.0847

   5. X5 --[3步滞后]--> X4
      p值: 0.018000 | 相关性强度: 0.0819

   6. X3 --[2步滞后]--> X1
      p值: 0.032000 | 相关性强度: 0.0741

   7. X3 --[1步滞后]--> X1
      p值: 0.042000 | 相关性强度: 0.0723

   8. X2 <--> X1 (同时发生(无方向))
      p值: 0.048000 | 相关性强度: 0.0705

   9. X1 <--> X2 (同时发生(无方向))
      p值: 0.048000 | 相关性强度: 0.0705

   10. X2 --[3步滞后]--> X3
      p值: 0.048000 | 相关性强度: 0.0710


📊 正在生成因果图...
   ✅ 因果图已保存: run_data\B1C\Gaussian\6variable\lag3\n1000\pcmci_causal_graph.png

💾 正在保存结果...
   ✅ 结果已保存: run_data\B1C\Gaussian\6variable\lag3\n1000\pcmci_results.csv
   共 144 条关系记录
   其中 10 条显著因果关系 (p < 0.05)
   ✅ 显著关系已单独保存: run_data\B1C\Gaussian\6variable\lag3\n1000\pcmci_significant_links.csv
   ✅ 数据集信息已保存: run_data\B1C\Gaussian\6variable\lag3\n1000\dataset_info.csv

================================================================================
✅ PCMCI分析完成!
================================================================================

📁 结果文件保存在: run_data\B1C\Gaussian\6variable\lag3\n1000
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
