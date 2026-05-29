# PC analysis log

## Run info
- Start time: 2026-04-17 20:55:42
- End time: 2026-04-17 20:55:43
- Duration: 0:00:00.593515

## Console output

```
================================================================================
PC causal discovery analysis - B1C
================================================================================

Loading data: Datasets\B1C\Gaussian error\6 variable\lag 2\nonlinear_confounded_n3000_vars6_lag2_gaussian.csv
Data shape: (3000, 6)
Observed variables: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6']

Dataset info:
dataset_type: B1C
noise_type: Gaussian
var_count: 6
lag: 2
sample_size: 3000
tau_max used by PC: 2
output_dir: run_data_pc\B1C\Gaussian\6variable\lag2\n3000

Starting time-unrolled PC analysis
Expanded data shape: (2998, 18)
alpha_level: 0.05
indep_test: fisherz
stable: True
PC search completed.

Discovered causal links:
================================================================================
1. X6 --[lag 2]--> X6 | type=Lagged

Generating causal graph...
Causal graph saved to: run_data_pc\B1C\Gaussian\6variable\lag2\n3000\pc_causal_graph.png
Full results saved to: run_data_pc\B1C\Gaussian\6variable\lag2\n3000\pc_results.csv
Discovered links saved to: run_data_pc\B1C\Gaussian\6variable\lag2\n3000\pc_significant_links.csv
Dataset info saved to: run_data_pc\B1C\Gaussian\6variable\lag2\n3000\dataset_info.csv

Run completed.
Discovered link count: 1
Results directory: run_data_pc\B1C\Gaussian\6variable\lag2\n3000
Output files:
1. pc_causal_graph.png
2. pc_results.csv
3. pc_significant_links.csv
4. dataset_info.csv
5. analysis_log.md

```
