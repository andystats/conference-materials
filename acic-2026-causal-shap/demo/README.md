# simcausal Causal SHAP Demo

This folder contains a reproducible teaching demo for the ACIC 2026 causal SHAP poster.

The demo is intentionally built to make ordinary predictive SHAP look plausible but causally wrong. The simulated DAG has upstream causes, pathophysiologic mediators, and downstream proxy measurements. The proxy variables are highly predictive because they summarize the mediators, but they have no directed path into the outcome. Standard SHAP tends to reward those proxies. Causal SHAP uses the expert DAG to push attribution back toward the variables that carry total causal effects.

## Files

```
demo/
├── causal_shap_simcausal_demo.ipynb  # teaching notebook
├── simcausal_many_mediators.R        # R/simcausal data generator
├── run_causal_shap_demo.py           # Python SHAP analysis runner
├── README.md
└── output/                           # generated when the demo is run
```

## Run

From `acic-2026-causal-shap/`:

```powershell
Rscript demo\simcausal_many_mediators.R 2500 20260506 demo\output
py -3.13 demo\run_causal_shap_demo.py --output-dir demo\output --n-perms 16 --n-background 8 --n-instances 12
```

Or open and run:

```powershell
py -3.13 -m ipykernel install --user --name python313 --display-name "Python 3.13"
jupyter notebook demo\causal_shap_simcausal_demo.ipynb
```

The Python runner imports `app/causal_shap.py`, so the demo stays aligned with the interactive app rather than maintaining a second causal SHAP implementation. On this workstation, use Python 3.13 for the demo; the default Python 3.14 install currently has an unstable NumPy wheel.

## Generated Outputs

- `simcausal_many_mediators.csv` - observed synthetic training data
- `ground_truth_edges.csv` - expert DAG edge list with linear coefficients
- `node_roles.csv` - root, mediator, proxy, and outcome labels
- `true_total_effects.csv` - analytic total effects from the linear DAG
- `shap_feature_rankings.csv` - standard SHAP, causal SHAP, and truth-aligned ranks
- `role_attribution_summary.csv` - attribution mass by role
- `standard_vs_causal_shap.png` - feature-level comparison plot
- `role_attribution_shift.png` - role-level attribution shift plot
- `dag_many_mediators.png` - teaching DAG diagram
- `demo_summary.json` - compact run summary for slides or poster text
