# PCMCI因果发现分析运行日志

## 运行信息
- **开始时间**: 2026-01-17 18:39:29
- **结束时间**: 2026-01-17 18:42:30
- **总耗时**: 0:03:00.322061

---

## 运行输出

```
================================================================================
PCMCI因果发现分析 - B1C数据集(非线性数据)
================================================================================

📂 正在加载数据: data\TimeGraph\B1C\Gaussian error\6 variable\Lag 4\nonlinear_confounded_n500_vars6_lag4_gaussian.csv
   数据形状: (500, 8)
   列名: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'U', 'time']
   ✅ 成功加载 6 个观测变量: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']
   ✅ 数据维度: (500, 6) (时间点数 × 变量数)

📊 数据集信息:
   数据集类型: B1C
   噪声类型: Gaussian
   变量数: 6
   最大滞后: 4
   样本量: 500
   输出目录: run_data\B1C\Gaussian\6variable\lag4\n500

🔍 开始运行PCMCI因果发现...
   最大滞后 (tau_max): 4
   显著性水平 (alpha): 0.05
   检验方法: GPDC (非线性)

   正在计算因果关系(这可能需要一些时间)...

##
## Step 1: PC1 algorithm for selecting lagged conditions
##

Parameters:
independence test = gp_dc
tau_min = 1
tau_max = 4
pc_alpha = [0.2]
max_conds_dim = None
max_combinations = 1



## Resulting lagged parent (super)sets:

    Variable X1 has 7 link(s):
        (X4 -2): max_pval = 0.04200, |min_val| =  0.099
        (X1 -4): max_pval = 0.09200, |min_val| =  0.093
        (X1 -2): max_pval = 0.09200, |min_val| =  0.093
        (X3 -3): max_pval = 0.10200, |min_val| =  0.091
        (X3 -4): max_pval = 0.12600, |min_val| =  0.088
        (X2 -4): max_pval = 0.14000, |min_val| =  0.087
        (X6 -4): max_pval = 0.16000, |min_val| =  0.085

    Variable X2 has 4 link(s):
        (X4 -1): max_pval = 0.01400, |min_val| =  0.112
        (X1 -2): max_pval = 0.11400, |min_val| =  0.090
        (X1 -3): max_pval = 0.13400, |min_val| =  0.087
        (X4 -3): max_pval = 0.16600, |min_val| =  0.084

    Variable X3 has 3 link(s):
        (X1 -2): max_pval = 0.00400, |min_val| =  0.144
        (X3 -4): max_pval = 0.16600, |min_val| =  0.084
        (X4 -4): max_pval = 0.18800, |min_val| =  0.083

    Variable X4 has 5 link(s):
        (X6 -4): max_pval = 0.01400, |min_val| =  0.114
        (X4 -1): max_pval = 0.04600, |min_val| =  0.099
        (X3 -4): max_pval = 0.12200, |min_val| =  0.089
        (X2 -1): max_pval = 0.15200, |min_val| =  0.086
        (X5 -3): max_pval = 0.16600, |min_val| =  0.084

    Variable X5 has 4 link(s):
        (X2 -3): max_pval = 0.10200, |min_val| =  0.092
        (X1 -2): max_pval = 0.11000, |min_val| =  0.090
        (X2 -4): max_pval = 0.15600, |min_val| =  0.086
        (X1 -3): max_pval = 0.17800, |min_val| =  0.083

    Variable X6 has 5 link(s):
        (X6 -4): max_pval = 0.03600, |min_val| =  0.102
        (X1 -4): max_pval = 0.04000, |min_val| =  0.101
        (X6 -1): max_pval = 0.06000, |min_val| =  0.097
        (X4 -1): max_pval = 0.12600, |min_val| =  0.088
        (X1 -1): max_pval = 0.19400, |min_val| =  0.082

##
## Step 2: MCI algorithm
##

Parameters:

independence test = gp_dc
tau_min = 0
tau_max = 4
max_conds_py = None
max_conds_px = None

## Significant links at alpha = 0.05:

    Variable X1 has 3 link(s):
        (X2  0): pval = 0.01400 | val =  0.113 | unoriented link
        (X1 -4): pval = 0.03200 | val =  0.102
        (X4 -2): pval = 0.04200 | val =  0.099

    Variable X2 has 2 link(s):
        (X1  0): pval = 0.01400 | val =  0.113 | unoriented link
        (X4 -1): pval = 0.01400 | val =  0.113

    Variable X3 has 1 link(s):
        (X1 -2): pval = 0.00200 | val =  0.154

    Variable X4 has 3 link(s):
        (X6 -4): pval = 0.01400 | val =  0.116
        (X4 -1): pval = 0.03200 | val =  0.103
        (X3 -4): pval = 0.04000 | val =  0.100

    Variable X5 has 2 link(s):
        (X6  0): pval = 0.00800 | val =  0.129 | unoriented link
        (X2 -3): pval = 0.04600 | val =  0.098

    Variable X6 has 4 link(s):
        (X5  0): pval = 0.00800 | val =  0.129 | unoriented link
        (X6 -4): pval = 0.03200 | val =  0.102
        (X1 -4): pval = 0.03600 | val =  0.102
        (X6 -1): pval = 0.04000 | val =  0.101
   ✅ PCMCI运行完成!

🔍 调试信息:
   p_matrix矩阵形状: (6, 6, 5)
   显著关系 (p < 0.05):
      X1 --[Lag4]--> X1 | p=0.032000
      X2 --[Lag0]--> X1 | p=0.014000
      X3 --[Lag2]--> X1 | p=0.002000
      X6 --[Lag4]--> X1 | p=0.036000
      X1 --[Lag0]--> X2 | p=0.014000
      X5 --[Lag3]--> X2 | p=0.046000
      X4 --[Lag4]--> X3 | p=0.040000
      X1 --[Lag2]--> X4 | p=0.042000
      X2 --[Lag1]--> X4 | p=0.014000
      X4 --[Lag1]--> X4 | p=0.032000
      X6 --[Lag0]--> X5 | p=0.008000
      X4 --[Lag4]--> X6 | p=0.014000
      X5 --[Lag0]--> X6 | p=0.008000
      X6 --[Lag1]--> X6 | p=0.040000
      X6 --[Lag4]--> X6 | p=0.032000
   总共发现 15 个显著因果关系 (p < 0.05)

📋 发现的因果关系 (显著性水平: 0.05):
================================================================================
   ✅ 发现 15 个显著的因果关系:

   1. X3 --[2步滞后]--> X1
      p值: 0.002000 | 相关性强度: 0.1544

   2. X6 <--> X5 (同时发生(无方向))
      p值: 0.008000 | 相关性强度: 0.1287

   3. X5 <--> X6 (同时发生(无方向))
      p值: 0.008000 | 相关性强度: 0.1287

   4. X2 <--> X1 (同时发生(无方向))
      p值: 0.014000 | 相关性强度: 0.1129

   5. X1 <--> X2 (同时发生(无方向))
      p值: 0.014000 | 相关性强度: 0.1129

   6. X2 --[1步滞后]--> X4
      p值: 0.014000 | 相关性强度: 0.1127

   7. X4 --[4步滞后]--> X6
      p值: 0.014000 | 相关性强度: 0.1156

   8. X1 --[4步滞后]--> X1
      p值: 0.032000 | 相关性强度: 0.1021

   9. X4 --[1步滞后]--> X4
      p值: 0.032000 | 相关性强度: 0.1030

   10. X6 --[4步滞后]--> X6
      p值: 0.032000 | 相关性强度: 0.1022

   11. X6 --[4步滞后]--> X1
      p值: 0.036000 | 相关性强度: 0.1016

   12. X4 --[4步滞后]--> X3
      p值: 0.040000 | 相关性强度: 0.0997

   13. X6 --[1步滞后]--> X6
      p值: 0.040000 | 相关性强度: 0.1007

   14. X1 --[2步滞后]--> X4
      p值: 0.042000 | 相关性强度: 0.0991

   15. X5 --[3步滞后]--> X2
      p值: 0.046000 | 相关性强度: 0.0979


📊 正在生成因果图...
   ✅ 因果图已保存: run_data\B1C\Gaussian\6variable\lag4\n500\pcmci_causal_graph.png

💾 正在保存结果...
   ✅ 结果已保存: run_data\B1C\Gaussian\6variable\lag4\n500\pcmci_results.csv
   共 180 条关系记录
   其中 15 条显著因果关系 (p < 0.05)
   ✅ 显著关系已单独保存: run_data\B1C\Gaussian\6variable\lag4\n500\pcmci_significant_links.csv
   ✅ 数据集信息已保存: run_data\B1C\Gaussian\6variable\lag4\n500\dataset_info.csv

================================================================================
✅ PCMCI分析完成!
================================================================================

📁 结果文件保存在: run_data\B1C\Gaussian\6variable\lag4\n500
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
