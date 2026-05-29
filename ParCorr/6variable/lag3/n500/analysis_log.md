# PCMCI ParCorr 运行日志

## 运行信息
- 开始时间: 2026-04-16 21:28:44
- 结束时间: 2026-04-16 21:28:46
- 总耗时: 0:00:01.545502

## 运行输出

```
================================================================================
PCMCI 因果发现分析 - B1C - ParCorr
================================================================================

正在加载数据: Datasets\B1C\Gaussian error\6 variable\lag 3\nonlinear_confounded_n500_vars6_lag3_gaussian.csv
数据形状: (500, 8)
观测变量: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']

数据集信息:
dataset_type: B1C
noise_type: Gaussian
var_count: 6
lag: 3
sample_size: 500
output_dir: run_data_parcorr\B1C\Gaussian\6variable\lag3\n500

开始运行 PCMCI + ParCorr
tau_max: 3
alpha_level: 0.05
条件独立检验: ParCorr

##
## Step 1: PC1 algorithm for selecting lagged conditions
##

Parameters:
independence test = par_corr
tau_min = 1
tau_max = 3
pc_alpha = [0.2]
max_conds_dim = None
max_combinations = 1



## Resulting lagged parent (super)sets:

    Variable X1 has 3 link(s):
        (X4 -2): max_pval = 0.02879, |min_val| =  0.099
        (X1 -2): max_pval = 0.07901, |min_val| =  0.079
        (X3 -3): max_pval = 0.16510, |min_val| =  0.063

    Variable X2 has 3 link(s):
        (X4 -1): max_pval = 0.00324, |min_val| =  0.132
        (X4 -3): max_pval = 0.13708, |min_val| =  0.067
        (X1 -3): max_pval = 0.15193, |min_val| =  0.065

    Variable X3 has 2 link(s):
        (X1 -2): max_pval = 0.00328, |min_val| =  0.132
        (X2 -1): max_pval = 0.13770, |min_val| =  0.067

    Variable X4 has 2 link(s):
        (X4 -1): max_pval = 0.03614, |min_val| =  0.094
        (X1 -3): max_pval = 0.15388, |min_val| =  0.064

    Variable X5 has 3 link(s):
        (X1 -3): max_pval = 0.12603, |min_val| =  0.069
        (X2 -1): max_pval = 0.17757, |min_val| =  0.061
        (X2 -3): max_pval = 0.19849, |min_val| =  0.058

    Variable X6 has 2 link(s):
        (X6 -2): max_pval = 0.03353, |min_val| =  0.096
        (X4 -1): max_pval = 0.13986, |min_val| =  0.067

##
## Step 2: MCI algorithm
##

Parameters:

independence test = par_corr
tau_min = 0
tau_max = 3
max_conds_py = None
max_conds_px = None

## Significant links at alpha = 0.05:

    Variable X1 has 1 link(s):
        (X4 -2): pval = 0.02573 | val =  0.101

    Variable X2 has 1 link(s):
        (X4 -1): pval = 0.00283 | val =  0.135

    Variable X3 has 1 link(s):
        (X1 -2): pval = 0.00607 | val =  0.124

    Variable X4 has 1 link(s):
        (X4 -1): pval = 0.03095 | val = -0.097

    Variable X5 has 1 link(s):
        (X6  0): pval = 0.00371 | val = -0.131 | unoriented link

    Variable X6 has 2 link(s):
        (X5  0): pval = 0.00371 | val = -0.131 | unoriented link
        (X6 -2): pval = 0.04259 | val =  0.092
PCMCI 运行完成。

显著因果关系 (p < 0.05):
================================================================================
1. X3 --[lag 2]--> X1 | p=0.006067 | val=0.1238
2. X1 --[lag 2]--> X4 | p=0.025733 | val=0.1008
3. X2 --[lag 1]--> X4 | p=0.002835 | val=0.1346
4. X4 --[lag 1]--> X4 | p=0.030955 | val=-0.0974
5. X6 <--> X5 | p=0.003712 | val=-0.1310
6. X5 <--> X6 | p=0.003712 | val=-0.1310
7. X6 --[lag 2]--> X6 | p=0.042590 | val=0.0916

正在生成因果图...
因果图已保存: run_data_parcorr\B1C\Gaussian\6variable\lag3\n500\pcmci_causal_graph.png
完整结果已保存: run_data_parcorr\B1C\Gaussian\6variable\lag3\n500\pcmci_results.csv
显著关系已保存: run_data_parcorr\B1C\Gaussian\6variable\lag3\n500\pcmci_significant_links.csv
数据集信息已保存: run_data_parcorr\B1C\Gaussian\6variable\lag3\n500\dataset_info.csv

运行完成。
显著关系数量: 7
结果目录: run_data_parcorr\B1C\Gaussian\6variable\lag3\n500
输出文件包括:
1. pcmci_causal_graph.png
2. pcmci_results.csv
3. pcmci_significant_links.csv
4. dataset_info.csv
5. analysis_log.md

```
