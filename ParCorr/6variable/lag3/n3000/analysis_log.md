# PCMCI ParCorr 运行日志

## 运行信息
- 开始时间: 2026-04-16 21:27:42
- 结束时间: 2026-04-16 21:27:43
- 总耗时: 0:00:01.728823

## 运行输出

```
================================================================================
PCMCI 因果发现分析 - B1C - ParCorr
================================================================================

正在加载数据: Datasets\B1C\Gaussian error\6 variable\lag 3\nonlinear_confounded_n3000_vars6_lag3_gaussian.csv
数据形状: (3000, 8)
观测变量: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']

数据集信息:
dataset_type: B1C
noise_type: Gaussian
var_count: 6
lag: 3
sample_size: 3000
output_dir: run_data_parcorr\B1C\Gaussian\6variable\lag3\n3000

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

    Variable X1 has 5 link(s):
        (X1 -2): max_pval = 0.06426, |min_val| =  0.034
        (X3 -1): max_pval = 0.08555, |min_val| =  0.031
        (X4 -2): max_pval = 0.11304, |min_val| =  0.029
        (X4 -3): max_pval = 0.17914, |min_val| =  0.025
        (X2 -1): max_pval = 0.18011, |min_val| =  0.025

    Variable X2 has 3 link(s):
        (X2 -3): max_pval = 0.08073, |min_val| =  0.032
        (X4 -1): max_pval = 0.09497, |min_val| =  0.031
        (X2 -1): max_pval = 0.18826, |min_val| =  0.024

    Variable X3 has 2 link(s):
        (X4 -3): max_pval = 0.06327, |min_val| =  0.034
        (X5 -3): max_pval = 0.11126, |min_val| =  0.029

    Variable X4 has 5 link(s):
        (X5 -2): max_pval = 0.09364, |min_val| =  0.031
        (X5 -3): max_pval = 0.15138, |min_val| =  0.026
        (X1 -2): max_pval = 0.16455, |min_val| =  0.025
        (X6 -3): max_pval = 0.16767, |min_val| =  0.025
        (X1 -3): max_pval = 0.17690, |min_val| =  0.025

    Variable X5 has 2 link(s):
        (X4 -3): max_pval = 0.05150, |min_val| =  0.036
        (X5 -3): max_pval = 0.06892, |min_val| =  0.033

    Variable X6 has 1 link(s):
        (X6 -2): max_pval = 0.04557, |min_val| =  0.037

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

    Variable X1 has 0 link(s):

    Variable X2 has 0 link(s):

    Variable X3 has 1 link(s):
        (X6  0): pval = 0.04985 | val = -0.036 | unoriented link

    Variable X4 has 0 link(s):

    Variable X5 has 0 link(s):

    Variable X6 has 2 link(s):
        (X6 -2): pval = 0.04206 | val =  0.037
        (X3  0): pval = 0.04985 | val = -0.036 | unoriented link
PCMCI 运行完成。

显著因果关系 (p < 0.05):
================================================================================
1. X6 <--> X3 | p=0.049851 | val=-0.0359
2. X3 <--> X6 | p=0.049851 | val=-0.0359
3. X6 --[lag 2]--> X6 | p=0.042064 | val=0.0372

正在生成因果图...
因果图已保存: run_data_parcorr\B1C\Gaussian\6variable\lag3\n3000\pcmci_causal_graph.png
完整结果已保存: run_data_parcorr\B1C\Gaussian\6variable\lag3\n3000\pcmci_results.csv
显著关系已保存: run_data_parcorr\B1C\Gaussian\6variable\lag3\n3000\pcmci_significant_links.csv
数据集信息已保存: run_data_parcorr\B1C\Gaussian\6variable\lag3\n3000\dataset_info.csv

运行完成。
显著关系数量: 3
结果目录: run_data_parcorr\B1C\Gaussian\6variable\lag3\n3000
输出文件包括:
1. pcmci_causal_graph.png
2. pcmci_results.csv
3. pcmci_significant_links.csv
4. dataset_info.csv
5. analysis_log.md

```
