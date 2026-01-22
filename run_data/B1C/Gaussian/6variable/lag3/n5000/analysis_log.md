# PCMCI因果发现分析运行日志

## 运行信息
- **开始时间**: 2026-01-17 08:34:15
- **结束时间**: 2026-01-17 17:30:32
- **总耗时**: 8:56:16.660731

---

## 运行输出

```
================================================================================
PCMCI因果发现分析 - B1C数据集(非线性数据)
================================================================================

📂 正在加载数据: data\TimeGraph\B1C\Gaussian error\6 variable\Lag 3\nonlinear_confounded_n5000_vars6_lag3_gaussian.csv
   数据形状: (5000, 8)
   列名: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'U', 'time']
   ✅ 成功加载 6 个观测变量: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']
   ✅ 数据维度: (5000, 6) (时间点数 × 变量数)

📊 数据集信息:
   数据集类型: B1C
   噪声类型: Gaussian
   变量数: 6
   最大滞后: 3
   样本量: 5000
   输出目录: run_data\B1C\Gaussian\6variable\lag3\n5000

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
        (X1 -2): max_pval = 0.00600, |min_val| =  0.041
        (X6 -2): max_pval = 0.10400, |min_val| =  0.028
        (X2 -2): max_pval = 0.14400, |min_val| =  0.027

    Variable X2 has 5 link(s):
        (X2 -3): max_pval = 0.01600, |min_val| =  0.035
        (X5 -2): max_pval = 0.06400, |min_val| =  0.031
        (X4 -3): max_pval = 0.12400, |min_val| =  0.028
        (X4 -2): max_pval = 0.12400, |min_val| =  0.028
        (X3 -1): max_pval = 0.13800, |min_val| =  0.027

    Variable X3 has 3 link(s):
        (X1 -2): max_pval = 0.08600, |min_val| =  0.029
        (X1 -3): max_pval = 0.10400, |min_val| =  0.028
        (X4 -2): max_pval = 0.16200, |min_val| =  0.026

    Variable X4 has 5 link(s):
        (X5 -2): max_pval = 0.02800, |min_val| =  0.034
        (X5 -3): max_pval = 0.07800, |min_val| =  0.030
        (X4 -3): max_pval = 0.09800, |min_val| =  0.029
        (X3 -3): max_pval = 0.10400, |min_val| =  0.028
        (X1 -2): max_pval = 0.12400, |min_val| =  0.027

    Variable X5 has 5 link(s):
        (X4 -3): max_pval = 0.04400, |min_val| =  0.032
        (X1 -2): max_pval = 0.05000, |min_val| =  0.032
        (X5 -3): max_pval = 0.06000, |min_val| =  0.031
        (X6 -1): max_pval = 0.06200, |min_val| =  0.031
        (X3 -3): max_pval = 0.12400, |min_val| =  0.028

    Variable X6 has 2 link(s):
        (X3 -2): max_pval = 0.01400, |min_val| =  0.037
        (X6 -2): max_pval = 0.12400, |min_val| =  0.028

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

    Variable X1 has 1 link(s):
        (X1 -2): pval = 0.00800 | val =  0.040

    Variable X2 has 2 link(s):
        (X2 -3): pval = 0.01600 | val =  0.035
        (X5 -2): pval = 0.05000 | val =  0.031

    Variable X3 has 0 link(s):

    Variable X4 has 1 link(s):
        (X5 -2): pval = 0.02400 | val =  0.035

    Variable X5 has 2 link(s):
        (X1 -2): pval = 0.04400 | val =  0.032
        (X4 -3): pval = 0.05000 | val =  0.032

    Variable X6 has 1 link(s):
        (X3 -2): pval = 0.01400 | val =  0.037
   ✅ PCMCI运行完成!

🔍 调试信息:
   p_matrix矩阵形状: (6, 6, 4)
   显著关系 (p < 0.05):
      X1 --[Lag2]--> X1 | p=0.008000
      X5 --[Lag2]--> X1 | p=0.044000
      X2 --[Lag3]--> X2 | p=0.016000
      X6 --[Lag2]--> X3 | p=0.014000
      X4 --[Lag2]--> X5 | p=0.024000
   总共发现 5 个显著因果关系 (p < 0.05)

📋 发现的因果关系 (显著性水平: 0.05):
================================================================================
   ✅ 发现 5 个显著的因果关系:

   1. X1 --[2步滞后]--> X1
      p值: 0.008000 | 相关性强度: 0.0404

   2. X6 --[2步滞后]--> X3
      p值: 0.014000 | 相关性强度: 0.0367

   3. X2 --[3步滞后]--> X2
      p值: 0.016000 | 相关性强度: 0.0352

   4. X4 --[2步滞后]--> X5
      p值: 0.024000 | 相关性强度: 0.0346

   5. X5 --[2步滞后]--> X1
      p值: 0.044000 | 相关性强度: 0.0324


📊 正在生成因果图...
   ✅ 因果图已保存: run_data\B1C\Gaussian\6variable\lag3\n5000\pcmci_causal_graph.png

💾 正在保存结果...
   ✅ 结果已保存: run_data\B1C\Gaussian\6variable\lag3\n5000\pcmci_results.csv
   共 144 条关系记录
   其中 5 条显著因果关系 (p < 0.05)
   ✅ 显著关系已单独保存: run_data\B1C\Gaussian\6variable\lag3\n5000\pcmci_significant_links.csv
   ✅ 数据集信息已保存: run_data\B1C\Gaussian\6variable\lag3\n5000\dataset_info.csv

================================================================================
✅ PCMCI分析完成!
================================================================================

📁 结果文件保存在: run_data\B1C\Gaussian\6variable\lag3\n5000
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
