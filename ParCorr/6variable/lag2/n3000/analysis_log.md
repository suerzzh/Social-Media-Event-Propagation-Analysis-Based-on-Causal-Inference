# PCMCI ParCorr 运行日志

## 运行信息
- 开始时间: 2026-04-16 21:29:32
- 结束时间: 2026-04-16 21:29:33
- 总耗时: 0:00:00.972589

## 运行输出

```
================================================================================
PCMCI 因果发现分析 - B1C - ParCorr
================================================================================

正在加载数据: Datasets\B1C\Gaussian error\6 variable\lag 2\nonlinear_confounded_n3000_vars6_lag2_gaussian.csv
数据形状: (3000, 8)
观测变量: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']

数据集信息:
dataset_type: B1C
noise_type: Gaussian
var_count: 6
lag: 2
sample_size: 3000
output_dir: run_data_parcorr\B1C\Gaussian\6variable\lag2\n3000

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

    Variable X1 has 4 link(s):
        (X1 -2): max_pval = 0.06003, |min_val| =  0.034
        (X3 -1): max_pval = 0.08664, |min_val| =  0.031
        (X4 -2): max_pval = 0.10443, |min_val| =  0.030
        (X2 -1): max_pval = 0.18219, |min_val| =  0.024

    Variable X2 has 2 link(s):
        (X4 -1): max_pval = 0.09342, |min_val| =  0.031
        (X2 -1): max_pval = 0.18548, |min_val| =  0.024

    Variable X3 has 0 link(s):

    Variable X4 has 2 link(s):
        (X5 -2): max_pval = 0.08675, |min_val| =  0.031
        (X1 -2): max_pval = 0.17996, |min_val| =  0.025

    Variable X5 has 0 link(s):

    Variable X6 has 1 link(s):
        (X6 -2): max_pval = 0.04437, |min_val| =  0.037

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

    Variable X1 has 0 link(s):

    Variable X2 has 0 link(s):

    Variable X3 has 1 link(s):
        (X6  0): pval = 0.04653 | val = -0.036 | unoriented link

    Variable X4 has 0 link(s):

    Variable X5 has 0 link(s):

    Variable X6 has 2 link(s):
        (X6 -2): pval = 0.04098 | val =  0.037
        (X3  0): pval = 0.04653 | val = -0.036 | unoriented link
PCMCI 运行完成。

显著因果关系 (p < 0.05):
================================================================================
1. X6 <--> X3 | p=0.046530 | val=-0.0364
2. X3 <--> X6 | p=0.046530 | val=-0.0364
3. X6 --[lag 2]--> X6 | p=0.040977 | val=0.0373

正在生成因果图...
因果图已保存: run_data_parcorr\B1C\Gaussian\6variable\lag2\n3000\pcmci_causal_graph.png
完整结果已保存: run_data_parcorr\B1C\Gaussian\6variable\lag2\n3000\pcmci_results.csv
显著关系已保存: run_data_parcorr\B1C\Gaussian\6variable\lag2\n3000\pcmci_significant_links.csv
数据集信息已保存: run_data_parcorr\B1C\Gaussian\6variable\lag2\n3000\dataset_info.csv

运行完成。
显著关系数量: 3
结果目录: run_data_parcorr\B1C\Gaussian\6variable\lag2\n3000
输出文件包括:
1. pcmci_causal_graph.png
2. pcmci_results.csv
3. pcmci_significant_links.csv
4. dataset_info.csv
5. analysis_log.md

```
