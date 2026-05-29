# PCMCI ParCorr 运行日志

## 运行信息
- 开始时间: 2026-04-16 21:28:30
- 结束时间: 2026-04-16 21:28:32
- 总耗时: 0:00:01.715137

## 运行输出

```
================================================================================
PCMCI 因果发现分析 - B1C - ParCorr
================================================================================

正在加载数据: Datasets\B1C\Gaussian error\6 variable\lag 3\nonlinear_confounded_n1000_vars6_lag3_gaussian.csv
数据形状: (1000, 8)
观测变量: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']

数据集信息:
dataset_type: B1C
noise_type: Gaussian
var_count: 6
lag: 3
sample_size: 1000
output_dir: run_data_parcorr\B1C\Gaussian\6variable\lag3\n1000

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

    Variable X1 has 2 link(s):
        (X1 -2): max_pval = 0.00330, |min_val| =  0.093
        (X3 -3): max_pval = 0.09071, |min_val| =  0.054

    Variable X2 has 1 link(s):
        (X4 -1): max_pval = 0.03536, |min_val| =  0.067

    Variable X3 has 2 link(s):
        (X4 -2): max_pval = 0.09077, |min_val| =  0.054
        (X1 -2): max_pval = 0.14411, |min_val| =  0.046

    Variable X4 has 4 link(s):
        (X2 -1): max_pval = 0.05279, |min_val| =  0.061
        (X5 -2): max_pval = 0.05710, |min_val| =  0.060
        (X4 -1): max_pval = 0.08847, |min_val| =  0.054
        (X1 -2): max_pval = 0.12234, |min_val| =  0.049

    Variable X5 has 3 link(s):
        (X4 -3): max_pval = 0.02689, |min_val| =  0.070
        (X2 -1): max_pval = 0.03147, |min_val| =  0.068
        (X3 -3): max_pval = 0.10709, |min_val| =  0.051

    Variable X6 has 1 link(s):
        (X6 -2): max_pval = 0.02145, |min_val| =  0.073

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
        (X1 -2): pval = 0.00273 | val =  0.095

    Variable X2 has 1 link(s):
        (X4 -1): pval = 0.04484 | val =  0.064

    Variable X3 has 0 link(s):

    Variable X4 has 1 link(s):
        (X5 -2): pval = 0.04211 | val = -0.065

    Variable X5 has 3 link(s):
        (X6  0): pval = 0.00572 | val = -0.088 | unoriented link
        (X2 -1): pval = 0.02669 | val = -0.070
        (X4 -3): pval = 0.03003 | val =  0.069

    Variable X6 has 2 link(s):
        (X5  0): pval = 0.00572 | val = -0.088 | unoriented link
        (X6 -2): pval = 0.01758 | val =  0.075
PCMCI 运行完成。

显著因果关系 (p < 0.05):
================================================================================
1. X1 --[lag 2]--> X1 | p=0.002725 | val=0.0951
2. X5 --[lag 1]--> X2 | p=0.026694 | val=-0.0704
3. X2 --[lag 1]--> X4 | p=0.044837 | val=0.0638
4. X5 --[lag 3]--> X4 | p=0.030026 | val=0.0690
5. X4 --[lag 2]--> X5 | p=0.042113 | val=-0.0647
6. X6 <--> X5 | p=0.005715 | val=-0.0878
7. X5 <--> X6 | p=0.005715 | val=-0.0878
8. X6 --[lag 2]--> X6 | p=0.017585 | val=0.0753

正在生成因果图...
因果图已保存: run_data_parcorr\B1C\Gaussian\6variable\lag3\n1000\pcmci_causal_graph.png
完整结果已保存: run_data_parcorr\B1C\Gaussian\6variable\lag3\n1000\pcmci_results.csv
显著关系已保存: run_data_parcorr\B1C\Gaussian\6variable\lag3\n1000\pcmci_significant_links.csv
数据集信息已保存: run_data_parcorr\B1C\Gaussian\6variable\lag3\n1000\dataset_info.csv

运行完成。
显著关系数量: 8
结果目录: run_data_parcorr\B1C\Gaussian\6variable\lag3\n1000
输出文件包括:
1. pcmci_causal_graph.png
2. pcmci_results.csv
3. pcmci_significant_links.csv
4. dataset_info.csv
5. analysis_log.md

```
