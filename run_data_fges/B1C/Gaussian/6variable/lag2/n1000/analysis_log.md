# FGES-style analysis log

## Run info
- Start time: 2026-04-17 20:51:27
- End time: 2026-04-17 20:51:27
- Duration: 0:00:00.660045

## Console output

```
================================================================================
FGES-style causal discovery analysis - B1C
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
tau_max used by FGES-style search: 2
output_dir: run_data_fges\B1C\Gaussian\6variable\lag2\n1000

Starting FGES-style score-based analysis
Backend: causal-learn GES
Expanded data shape: (998, 18)
score_func: local_score_BIC
GES score: 32175.620555283087
Score-based search completed.

Discovered causal links:
================================================================================
1. X1 --[lag 2]--> X1 | type=Lagged

Generating causal graph...
Causal graph saved to: run_data_fges\B1C\Gaussian\6variable\lag2\n1000\fges_causal_graph.png
Full results saved to: run_data_fges\B1C\Gaussian\6variable\lag2\n1000\fges_results.csv
Discovered links saved to: run_data_fges\B1C\Gaussian\6variable\lag2\n1000\fges_significant_links.csv
Dataset info saved to: run_data_fges\B1C\Gaussian\6variable\lag2\n1000\dataset_info.csv

Run completed.
Discovered link count: 1
Results directory: run_data_fges\B1C\Gaussian\6variable\lag2\n1000
Output files:
1. fges_causal_graph.png
2. fges_results.csv
3. fges_significant_links.csv
4. dataset_info.csv
5. analysis_log.md

```
