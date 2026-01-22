# PCMCI因果发现分析运行日志

## 运行信息
- **开始时间**: 2026-01-19 11:51:01
- **结束时间**: 2026-01-19 14:48:26
- **总耗时**: 2:57:25.534996

---

## 运行输出

```
================================================================================
PCMCI因果发现分析 - B1C数据集(非线性数据)
================================================================================

📂 正在加载数据: data\TimeGraph\B1C\Gaussian error\6 variable\Lag 4\nonlinear_confounded_n3000_vars6_lag4_gaussian.csv
   数据形状: (3000, 8)
   列名: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'U', 'time']
   ✅ 成功加载 6 个观测变量: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']
   ✅ 数据维度: (3000, 6) (时间点数 × 变量数)

📊 数据集信息:
   数据集类型: B1C
   噪声类型: Gaussian
   变量数: 6
   最大滞后: 4
   样本量: 3000
   输出目录: run_data\B1C\Gaussian\6variable\lag4\n3000

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

    Variable X1 has 6 link(s):
        (X5 -4): max_pval = 0.00200, |min_val| =  0.065
        (X4 -2): max_pval = 0.08000, |min_val| =  0.040
        (X2 -4): max_pval = 0.09000, |min_val| =  0.039
        (X1 -1): max_pval = 0.11800, |min_val| =  0.037
        (X3 -1): max_pval = 0.12000, |min_val| =  0.037
        (X1 -2): max_pval = 0.12000, |min_val| =  0.037

    Variable X2 has 6 link(s):
        (X5 -4): max_pval = 0.03800, |min_val| =  0.044
        (X2 -3): max_pval = 0.03800, |min_val| =  0.043
        (X5 -2): max_pval = 0.05600, |min_val| =  0.041
        (X2 -1): max_pval = 0.08600, |min_val| =  0.039
        (X4 -2): max_pval = 0.12000, |min_val| =  0.037
        (X3 -3): max_pval = 0.13200, |min_val| =  0.036

    Variable X3 has 5 link(s):
        (X5 -3): max_pval = 0.11200, |min_val| =  0.037
        (X4 -3): max_pval = 0.12000, |min_val| =  0.037
        (X4 -2): max_pval = 0.12400, |min_val| =  0.037
        (X1 -4): max_pval = 0.13200, |min_val| =  0.036
        (X3 -4): max_pval = 0.15400, |min_val| =  0.035

    Variable X4 has 3 link(s):
        (X6 -4): max_pval = 0.02200, |min_val| =  0.047
        (X3 -4): max_pval = 0.08600, |min_val| =  0.039
        (X4 -3): max_pval = 0.19200, |min_val| =  0.034

    Variable X5 has 3 link(s):
        (X4 -3): max_pval = 0.01800, |min_val| =  0.049
        (X6 -1): max_pval = 0.05800, |min_val| =  0.041
        (X5 -3): max_pval = 0.19200, |min_val| =  0.034

    Variable X6 has 3 link(s):
        (X6 -2): max_pval = 0.02200, |min_val| =  0.048
        (X4 -3): max_pval = 0.08000, |min_val| =  0.040
        (X5 -1): max_pval = 0.14400, |min_val| =  0.035

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

    Variable X1 has 2 link(s):
        (X5 -4): pval = 0.00200 | val =  0.065
        (X2  0): pval = 0.03400 | val =  0.045 | unoriented link

    Variable X2 has 3 link(s):
        (X1  0): pval = 0.03400 | val =  0.045 | unoriented link
        (X5 -4): pval = 0.03800 | val =  0.044
        (X2 -3): pval = 0.03800 | val =  0.044

    Variable X3 has 0 link(s):

    Variable X4 has 1 link(s):
        (X6 -4): pval = 0.02200 | val =  0.048

    Variable X5 has 2 link(s):
        (X4 -3): pval = 0.01600 | val =  0.049
        (X6 -1): pval = 0.04600 | val =  0.042

    Variable X6 has 1 link(s):
        (X6 -2): pval = 0.02200 | val =  0.048
   ✅ PCMCI运行完成!

🔍 调试信息:
   p_matrix矩阵形状: (6, 6, 5)
   显著关系 (p < 0.05):
      X2 --[Lag0]--> X1 | p=0.034000
      X1 --[Lag0]--> X2 | p=0.034000
      X2 --[Lag3]--> X2 | p=0.038000
      X5 --[Lag3]--> X4 | p=0.016000
      X1 --[Lag4]--> X5 | p=0.002000
      X2 --[Lag4]--> X5 | p=0.038000
      X4 --[Lag4]--> X6 | p=0.022000
      X5 --[Lag1]--> X6 | p=0.046000
      X6 --[Lag2]--> X6 | p=0.022000
   总共发现 9 个显著因果关系 (p < 0.05)

📋 发现的因果关系 (显著性水平: 0.05):
================================================================================
   ✅ 发现 9 个显著的因果关系:

   1. X1 --[4步滞后]--> X5
      p值: 0.002000 | 相关性强度: 0.0645

   2. X5 --[3步滞后]--> X4
      p值: 0.016000 | 相关性强度: 0.0492

   3. X4 --[4步滞后]--> X6
      p值: 0.022000 | 相关性强度: 0.0477

   4. X6 --[2步滞后]--> X6
      p值: 0.022000 | 相关性强度: 0.0477

   5. X2 <--> X1 (同时发生(无方向))
      p值: 0.034000 | 相关性强度: 0.0446

   6. X1 <--> X2 (同时发生(无方向))
      p值: 0.034000 | 相关性强度: 0.0446

   7. X2 --[3步滞后]--> X2
      p值: 0.038000 | 相关性强度: 0.0436

   8. X2 --[4步滞后]--> X5
      p值: 0.038000 | 相关性强度: 0.0440

   9. X5 --[1步滞后]--> X6
      p值: 0.046000 | 相关性强度: 0.0423


📊 正在生成因果图...
   ✅ 因果图已保存: run_data\B1C\Gaussian\6variable\lag4\n3000\pcmci_causal_graph.png

💾 正在保存结果...
   ✅ 结果已保存: run_data\B1C\Gaussian\6variable\lag4\n3000\pcmci_results.csv
   共 180 条关系记录
   其中 9 条显著因果关系 (p < 0.05)
   ✅ 显著关系已单独保存: run_data\B1C\Gaussian\6variable\lag4\n3000\pcmci_significant_links.csv
   ✅ 数据集信息已保存: run_data\B1C\Gaussian\6variable\lag4\n3000\dataset_info.csv

================================================================================
✅ PCMCI分析完成!
================================================================================

📁 结果文件保存在: run_data\B1C\Gaussian\6variable\lag4\n3000
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
