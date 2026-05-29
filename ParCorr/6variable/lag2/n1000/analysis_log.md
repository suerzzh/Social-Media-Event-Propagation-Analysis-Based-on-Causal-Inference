# PCMCI ParCorr 运行日志

## 运行信息
- 开始时间: 2026-04-16 21:29:22
- 结束时间: 2026-04-16 21:29:23
- 总耗时: 0:00:01.133485

## 运行输出

```
================================================================================
PCMCI 因果发现分析 - B1C - ParCorr
================================================================================

正在加载数据: Datasets\B1C\Gaussian error\6 variable\lag 2\nonlinear_confounded_n1000_vars6_lag2_gaussian.csv
数据形状: (1000, 8)
观测变量: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']

数据集信息:
dataset_type: B1C
noise_type: Gaussian
var_count: 6
lag: 2
sample_size: 1000
output_dir: run_data_parcorr\B1C\Gaussian\6variable\lag2\n1000

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

    Variable X1 has 1 link(s):
        (X1 -2): max_pval = 0.00281, |min_val| =  0.095

    Variable X2 has 1 link(s):
        (X4 -1): max_pval = 0.03423, |min_val| =  0.067

    Variable X3 has 2 link(s):
        (X4 -2): max_pval = 0.09907, |min_val| =  0.052
        (X1 -2): max_pval = 0.13028, |min_val| =  0.048

    Variable X4 has 4 link(s):
        (X5 -2): max_pval = 0.05039, |min_val| =  0.062
        (X2 -1): max_pval = 0.05487, |min_val| =  0.061
        (X4 -1): max_pval = 0.07078, |min_val| =  0.057
        (X1 -2): max_pval = 0.14648, |min_val| =  0.046

    Variable X5 has 1 link(s):
        (X2 -1): max_pval = 0.02744, |min_val| =  0.070

    Variable X6 has 1 link(s):
        (X6 -2): max_pval = 0.02057, |min_val| =  0.073

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

    Variable X1 has 1 link(s):
        (X1 -2): pval = 0.00192 | val =  0.098

    Variable X2 has 1 link(s):
        (X4 -1): pval = 0.04300 | val =  0.064

    Variable X3 has 0 link(s):

    Variable X4 has 1 link(s):
        (X5 -2): pval = 0.04278 | val = -0.064

    Variable X5 has 2 link(s):
        (X6  0): pval = 0.00814 | val = -0.084 | unoriented link
        (X2 -1): pval = 0.02364 | val = -0.072

    Variable X6 has 2 link(s):
        (X5  0): pval = 0.00814 | val = -0.084 | unoriented link
        (X6 -2): pval = 0.01670 | val =  0.076
PCMCI 运行完成。

显著因果关系 (p < 0.05):
================================================================================
1. X1 --[lag 2]--> X1 | p=0.001918 | val=0.0982
2. X5 --[lag 1]--> X2 | p=0.023638 | val=-0.0717
3. X2 --[lag 1]--> X4 | p=0.043000 | val=0.0643
4. X4 --[lag 2]--> X5 | p=0.042782 | val=-0.0643
5. X6 <--> X5 | p=0.008139 | val=-0.0839
6. X5 <--> X6 | p=0.008139 | val=-0.0839
7. X6 --[lag 2]--> X6 | p=0.016704 | val=0.0759

正在生成因果图...
因果图已保存: run_data_parcorr\B1C\Gaussian\6variable\lag2\n1000\pcmci_causal_graph.png
完整结果已保存: run_data_parcorr\B1C\Gaussian\6variable\lag2\n1000\pcmci_results.csv
显著关系已保存: run_data_parcorr\B1C\Gaussian\6variable\lag2\n1000\pcmci_significant_links.csv
数据集信息已保存: run_data_parcorr\B1C\Gaussian\6variable\lag2\n1000\dataset_info.csv

运行完成。
显著关系数量: 7
结果目录: run_data_parcorr\B1C\Gaussian\6variable\lag2\n1000
输出文件包括:
1. pcmci_causal_graph.png
2. pcmci_results.csv
3. pcmci_significant_links.csv
4. dataset_info.csv
5. analysis_log.md

```
