# FGES-style analysis log

## Run info
- Start time: 2026-04-17 20:51:50
- End time: 2026-04-17 20:51:51
- Duration: 0:00:01.232648

## Console output

```
================================================================================
FGES-style causal discovery analysis - B1C
================================================================================

Loading data: Datasets\B1C\Gaussian error\6 variable\lag 3\nonlinear_confounded_n3000_vars6_lag3_gaussian.csv
Data shape: (3000, 6)
Observed variables: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']

Dataset info:
dataset_type: B1C
noise_type: Gaussian
var_count: 6
lag: 3
sample_size: 3000
tau_max used by FGES-style search: 3
output_dir: run_data_fges\B1C\Gaussian\6variable\lag3\n3000

Starting FGES-style score-based analysis
Backend: causal-learn GES
Expanded data shape: (2997, 24)
score_func: local_score_BIC
GES score: 128964.27919828716
Score-based search completed.

Discovered causal links:
================================================================================
No links were discovered by FGES-style search.

Generating causal graph...
Causal graph saved to: run_data_fges\B1C\Gaussian\6variable\lag3\n3000\fges_causal_graph.png
Full results saved to: run_data_fges\B1C\Gaussian\6variable\lag3\n3000\fges_results.csv
Discovered links saved to: run_data_fges\B1C\Gaussian\6variable\lag3\n3000\fges_significant_links.csv
Dataset info saved to: run_data_fges\B1C\Gaussian\6variable\lag3\n3000\dataset_info.csv

Run completed.
Discovered link count: 0
Results directory: run_data_fges\B1C\Gaussian\6variable\lag3\n3000
Output files:
1. fges_causal_graph.png
2. fges_results.csv
3. fges_significant_links.csv
4. dataset_info.csv
5. analysis_log.md

```
