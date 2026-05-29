# PCMCI因果发现分析运行日志

## 运行信息
- **开始时间**: 2026-01-16 17:31:58
- **结束时间**: 2026-01-16 18:40:26
- **总耗时**: 1:08:28.249223

---

## 运行输出

```
================================================================================
PCMCI因果发现分析 - B1C数据集(非线性数据)
================================================================================

📂 正在加载数据: data\TimeGraph\B1C\Gaussian error\6 variable\Lag 2\nonlinear_confounded_n3000_vars6_lag2_gaussian.csv
   数据形状: (3000, 8)
   列名: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'U', 'time']
   ✅ 成功加载 6 个观测变量: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']
   ✅ 数据维度: (3000, 6) (时间点数 × 变量数)

📊 数据集信息:
   数据集类型: B1C
   噪声类型: Gaussian
   变量数: 6
   最大滞后: 2
   样本量: 3000
   输出目录: run_data\B1C\Gaussian\6variable\lag2\n3000

🔍 开始运行PCMCI因果发现...
   最大滞后 (tau_max): 2
   显著性水平 (alpha): 0.05
   检验方法: GPDC (非线性)

   正在计算因果关系(这可能需要一些时间)...

##
## Step 1: PC1 algorithm for selecting lagged conditions
##

Parameters:
independence test = gp_dc
tau_min = 1
tau_max = 2
pc_alpha = [0.2]
max_conds_dim = None
max_combinations = 1



## Resulting lagged parent (super)sets:

    Variable X1 has 4 link(s):
        (X4 -2): max_pval = 0.05800, |min_val| =  0.040
        (X1 -2): max_pval = 0.08400, |min_val| =  0.038
        (X3 -1): max_pval = 0.10400, |min_val| =  0.037
        (X1 -1): max_pval = 0.10600, |min_val| =  0.037

    Variable X2 has 3 link(s):
        (X5 -2): max_pval = 0.04400, |min_val| =  0.042
        (X2 -1): max_pval = 0.06800, |min_val| =  0.040
        (X4 -2): max_pval = 0.10400, |min_val| =  0.037

    Variable X3 has 1 link(s):
        (X4 -2): max_pval = 0.10200, |min_val| =  0.037

    Variable X4 has 0 link(s):

    Variable X5 has 1 link(s):
        (X6 -1): max_pval = 0.04400, |min_val| =  0.042

    Variable X6 has 3 link(s):
        (X6 -2): max_pval = 0.01800, |min_val| =  0.048
        (X5 -1): max_pval = 0.14400, |min_val| =  0.035
        (X3 -1): max_pval = 0.19400, |min_val| =  0.034

##
## Step 2: MCI algorithm
##

Parameters:

independence test = gp_dc
tau_min = 0
tau_max = 2
max_conds_py = None
max_conds_px = None

## Significant links at alpha = 0.05:

    Variable X1 has 1 link(s):
        (X2  0): pval = 0.02400 | val =  0.046 | unoriented link

    Variable X2 has 2 link(s):
        (X1  0): pval = 0.02400 | val =  0.046 | unoriented link
        (X5 -2): pval = 0.04200 | val =  0.042

    Variable X3 has 0 link(s):

    Variable X4 has 0 link(s):

    Variable X5 has 1 link(s):
        (X6 -1): pval = 0.03600 | val =  0.043

    Variable X6 has 1 link(s):
        (X6 -2): pval = 0.01800 | val =  0.048
   ✅ PCMCI运行完成!

🔍 调试信息:
   p_matrix矩阵形状: (6, 6, 3)
   显著关系 (p < 0.05):
      X2 --[Lag0]--> X1 | p=0.024000
      X1 --[Lag0]--> X2 | p=0.024000
      X2 --[Lag2]--> X5 | p=0.042000
      X5 --[Lag1]--> X6 | p=0.036000
      X6 --[Lag2]--> X6 | p=0.018000
   总共发现 5 个显著因果关系 (p < 0.05)

📋 发现的因果关系 (显著性水平: 0.05):
================================================================================
   ✅ 发现 5 个显著的因果关系:

   1. X6 --[2步滞后]--> X6
      p值: 0.018000 | 相关性强度: 0.0481

   2. X2 <--> X1 (同时发生(无方向))
      p值: 0.024000 | 相关性强度: 0.0458

   3. X1 <--> X2 (同时发生(无方向))
      p值: 0.024000 | 相关性强度: 0.0458

   4. X5 --[1步滞后]--> X6
      p值: 0.036000 | 相关性强度: 0.0426

   5. X2 --[2步滞后]--> X5
      p值: 0.042000 | 相关性强度: 0.0421


📊 正在生成因果图...
   ✅ 因果图已保存: run_data\B1C\Gaussian\6variable\lag2\n3000\pcmci_causal_graph.png

💾 正在保存结果...
   ✅ 结果已保存: run_data\B1C\Gaussian\6variable\lag2\n3000\pcmci_results.csv
   共 108 条关系记录
   其中 5 条显著因果关系 (p < 0.05)
   ✅ 显著关系已单独保存: run_data\B1C\Gaussian\6variable\lag2\n3000\pcmci_significant_links.csv
   ✅ 数据集信息已保存: run_data\B1C\Gaussian\6variable\lag2\n3000\dataset_info.csv

================================================================================
✅ PCMCI分析完成!
================================================================================

📁 结果文件保存在: run_data\B1C\Gaussian\6variable\lag2\n3000
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
