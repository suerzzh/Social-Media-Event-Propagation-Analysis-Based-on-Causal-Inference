# Granger analysis log

## Run info
- Start time: 2026-04-17 20:49:34
- End time: 2026-04-17 20:49:35
- Duration: 0:00:00.805943

## Console output

```
================================================================================
Granger causal discovery analysis - B1C
================================================================================

Loading data: Datasets\B1C\Gaussian error\6 variable\lag 2\nonlinear_confounded_n1000_vars6_lag2_gaussian.csv
Data shape: (1000, 6)
Observed variables: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']

Dataset info:
dataset_type: B1C
noise_type: Gaussian
var_count: 6
lag: 2
sample_size: 1000
tau_max used by Granger: 2
output_dir: run_data_granger\B1C\Gaussian\6variable\lag2\n1000

Starting pairwise Granger analysis
tau_max: 2
alpha_level: 0.05
test_key: ssr_ftest
Pairwise Granger analysis completed.

Discovered causal links:
================================================================================
1. X2 --[lag 1]--> X5 | p=0.028229 | stat=4.8281
2. X4 --[lag 1]--> X2 | p=0.035334 | stat=4.4411

Generating causal graph...
Causal graph saved to: run_data_granger\B1C\Gaussian\6variable\lag2\n1000\granger_causal_graph.png
Full results saved to: run_data_granger\B1C\Gaussian\6variable\lag2\n1000\granger_results.csv
Discovered links saved to: run_data_granger\B1C\Gaussian\6variable\lag2\n1000\granger_significant_links.csv
Dataset info saved to: run_data_granger\B1C\Gaussian\6variable\lag2\n1000\dataset_info.csv

Run completed.
Discovered link count: 2
Results directory: run_data_granger\B1C\Gaussian\6variable\lag2\n1000
Output files:
1. granger_causal_graph.png
2. granger_results.csv
3. granger_significant_links.csv
4. dataset_info.csv
5. analysis_log.md

```
