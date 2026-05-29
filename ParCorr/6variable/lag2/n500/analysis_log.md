# PCMCI ParCorr 运行日志

## 运行信息
- 开始时间: 2026-04-16 21:29:07
- 结束时间: 2026-04-16 21:29:08
- 总耗时: 0:00:01.210063

## 运行输出

```
================================================================================
PCMCI 因果发现分析 - B1C - ParCorr
================================================================================

正在加载数据: Datasets\B1C\Gaussian error\6 variable\lag 2\nonlinear_confounded_n500_vars6_lag2_gaussian.csv
数据形状: (500, 8)
观测变量: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']

数据集信息:
dataset_type: B1C
noise_type: Gaussian
var_count: 6
lag: 2
sample_size: 500
output_dir: run_data_parcorr\B1C\Gaussian\6variable\lag2\n500

开始运行 PCMCI + ParCorr
tau_max: 2
alpha_level: 0.05
条件独立检验: ParCorr

##
## Step 1: PC1 algorithm for selecting lagged conditions
##

Parameters:
independence test = par_corr
tau_min = 1
tau_max = 2
pc_alpha = [0.2]
max_conds_dim = None
max_combinations = 1



## Resulting lagged parent (super)sets:

    Variable X1 has 2 link(s):
        (X4 -2): max_pval = 0.02662, |min_val| =  0.100
        (X1 -2): max_pval = 0.06617, |min_val| =  0.083

    Variable X2 has 1 link(s):
        (X4 -1): max_pval = 0.00265, |min_val| =  0.135

    Variable X3 has 2 link(s):
        (X1 -2): max_pval = 0.00261, |min_val| =  0.135
        (X2 -1): max_pval = 0.15011, |min_val| =  0.065

    Variable X4 has 2 link(s):
        (X4 -1): max_pval = 0.02346, |min_val| =  0.102
        (X5 -2): max_pval = 0.19872, |min_val| =  0.058

    Variable X5 has 1 link(s):
        (X2 -1): max_pval = 0.15391, |min_val| =  0.064

    Variable X6 has 2 link(s):
        (X6 -2): max_pval = 0.03134, |min_val| =  0.097
        (X4 -1): max_pval = 0.11647, |min_val| =  0.071

##
## Step 2: MCI algorithm
##

Parameters:

independence test = par_corr
tau_min = 0
tau_max = 2
max_conds_py = None
max_conds_px = None

## Significant links at alpha = 0.05:

    Variable X1 has 2 link(s):
        (X4 -2): pval = 0.01653 | val =  0.108
        (X1 -2): pval = 0.04313 | val =  0.091

    Variable X2 has 1 link(s):
        (X4 -1): pval = 0.00373 | val =  0.130

    Variable X3 has 1 link(s):
        (X1 -2): pval = 0.00509 | val =  0.126

    Variable X4 has 1 link(s):
        (X4 -1): pval = 0.01974 | val = -0.105

    Variable X5 has 1 link(s):
        (X6  0): pval = 0.00404 | val = -0.129 | unoriented link

    Variable X6 has 2 link(s):
        (X5  0): pval = 0.00404 | val = -0.129 | unoriented link
        (X6 -2): pval = 0.04039 | val =  0.092
PCMCI 运行完成。

显著因果关系 (p < 0.05):
================================================================================
1. X1 --[lag 2]--> X1 | p=0.043127 | val=0.0911
2. X3 --[lag 2]--> X1 | p=0.005094 | val=0.1260
3. X1 --[lag 2]--> X4 | p=0.016530 | val=0.1079
4. X2 --[lag 1]--> X4 | p=0.003729 | val=0.1303
5. X4 --[lag 1]--> X4 | p=0.019742 | val=-0.1050
6. X6 <--> X5 | p=0.004036 | val=-0.1293
7. X5 <--> X6 | p=0.004036 | val=-0.1293
8. X6 --[lag 2]--> X6 | p=0.040389 | val=0.0924

正在生成因果图...
因果图已保存: run_data_parcorr\B1C\Gaussian\6variable\lag2\n500\pcmci_causal_graph.png
完整结果已保存: run_data_parcorr\B1C\Gaussian\6variable\lag2\n500\pcmci_results.csv
显著关系已保存: run_data_parcorr\B1C\Gaussian\6variable\lag2\n500\pcmci_significant_links.csv
数据集信息已保存: run_data_parcorr\B1C\Gaussian\6variable\lag2\n500\dataset_info.csv

运行完成。
显著关系数量: 8
结果目录: run_data_parcorr\B1C\Gaussian\6variable\lag2\n500
输出文件包括:
1. pcmci_causal_graph.png
2. pcmci_results.csv
3. pcmci_significant_links.csv
4. dataset_info.csv
5. analysis_log.md

```
