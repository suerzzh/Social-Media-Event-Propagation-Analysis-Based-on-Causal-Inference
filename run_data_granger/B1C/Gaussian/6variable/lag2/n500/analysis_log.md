# Granger analysis log

## Run info
- Start time: 2026-04-17 20:49:23
- End time: 2026-04-17 20:49:24
- Duration: 0:00:00.839067

## Console output

```
================================================================================
Granger causal discovery analysis - B1C
================================================================================

Loading data: Datasets\B1C\Gaussian error\6 variable\lag 2\nonlinear_confounded_n500_vars6_lag2_gaussian.csv
Data shape: (500, 6)
Observed variables: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']

Dataset info:
dataset_type: B1C
noise_type: Gaussian
var_count: 6
lag: 2
sample_size: 500
tau_max used by Granger: 2
output_dir: run_data_granger\B1C\Gaussian\6variable\lag2\n500

Starting pairwise Granger analysis
tau_max: 2
alpha_level: 0.05
test_key: ssr_ftest
Pairwise Granger analysis completed.

Discovered causal links:
================================================================================
1. X4 --[lag 1]--> X2 | p=0.002403 | stat=9.3089
2. X4 --[lag 2]--> X2 | p=0.005111 | stat=5.3332
3. X1 --[lag 2]--> X3 | p=0.012881 | stat=4.3907
4. X4 --[lag 2]--> X1 | p=0.046243 | stat=3.0931

Generating causal graph...
Causal graph saved to: run_data_granger\B1C\Gaussian\6variable\lag2\n500\granger_causal_graph.png
Full results saved to: run_data_granger\B1C\Gaussian\6variable\lag2\n500\granger_results.csv
Discovered links saved to: run_data_granger\B1C\Gaussian\6variable\lag2\n500\granger_significant_links.csv
Dataset info saved to: run_data_granger\B1C\Gaussian\6variable\lag2\n500\dataset_info.csv

Run completed.
Discovered link count: 4
Results directory: run_data_granger\B1C\Gaussian\6variable\lag2\n500
Output files:
1. granger_causal_graph.png
2. granger_results.csv
3. granger_significant_links.csv
4. dataset_info.csv
5. analysis_log.md

```
