# Granger analysis log

## Run info
- Start time: 2026-04-17 20:49:09
- End time: 2026-04-17 20:49:10
- Duration: 0:00:01.149905

## Console output

```
================================================================================
Granger causal discovery analysis - B1C
================================================================================

Loading data: Datasets\B1C\Gaussian error\6 variable\lag 3\nonlinear_confounded_n500_vars6_lag3_gaussian.csv
Data shape: (500, 6)
Observed variables: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']

Dataset info:
dataset_type: B1C
noise_type: Gaussian
var_count: 6
lag: 3
sample_size: 500
tau_max used by Granger: 3
output_dir: run_data_granger\B1C\Gaussian\6variable\lag3\n500

Starting pairwise Granger analysis
tau_max: 3
alpha_level: 0.05
test_key: ssr_ftest
Pairwise Granger analysis completed.

Discovered causal links:
================================================================================
1. X4 --[lag 1]--> X2 | p=0.002383 | stat=9.3241
2. X4 --[lag 2]--> X2 | p=0.005071 | stat=5.3413
3. X4 --[lag 3]--> X2 | p=0.005210 | stat=4.3013
4. X1 --[lag 2]--> X3 | p=0.013212 | stat=4.3648
5. X1 --[lag 3]--> X3 | p=0.022444 | stat=3.2231
6. X4 --[lag 2]--> X1 | p=0.047054 | stat=3.0755

Generating causal graph...
Causal graph saved to: run_data_granger\B1C\Gaussian\6variable\lag3\n500\granger_causal_graph.png
Full results saved to: run_data_granger\B1C\Gaussian\6variable\lag3\n500\granger_results.csv
Discovered links saved to: run_data_granger\B1C\Gaussian\6variable\lag3\n500\granger_significant_links.csv
Dataset info saved to: run_data_granger\B1C\Gaussian\6variable\lag3\n500\dataset_info.csv

Run completed.
Discovered link count: 6
Results directory: run_data_granger\B1C\Gaussian\6variable\lag3\n500
Output files:
1. granger_causal_graph.png
2. granger_results.csv
3. granger_significant_links.csv
4. dataset_info.csv
5. analysis_log.md

```
