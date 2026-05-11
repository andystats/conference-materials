# Causal SHAP Demo App

This folder contains the Python Shiny companion app for the ACIC 2026 causal SHAP demo.

The public GitHub Pages site is static, so it cannot run this app in the browser. The app is intentionally scoped to the checked-in simcausal demo: run vanilla SHAP first, then supply the known true DAG and compare against causal SHAP.

## Quick Start

From `acic-2026-causal-shap/app/`:

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m shiny run --port 8000 app.py
```

Then open:

```text
http://127.0.0.1:8000
```

On Windows you can also double-click `run_app.bat`.

## Demo Sequence

1. Open the `Data` tab and keep the default simcausal teaching data.
2. Go to `Causal SHAP`.
3. Run `Standard SHAP only`.
4. Switch to `Compare standard vs causal SHAP`.
5. Keep `Known true DAG` selected and compute again.
6. Use the comparison plot and rank table to show downstream proxies moving down.

## Data Source

The app reads `../demo/output/simcausal_many_mediators.csv` and `../demo/output/ground_truth_edges.csv`. Regenerate those files from the repository root with:

```powershell
Rscript demo\simcausal_many_mediators.R 2500 20260506 demo\output
py -3.13 demo\run_causal_shap_demo.py --output-dir demo\output --n-perms 16 --n-background 8 --n-instances 12
```

## Important Caveat

Causal SHAP does not discover true causes by itself. It explains a fitted prediction model under explicit causal assumptions. If the DAG is wrong, the attribution can be wrong in the direction of the DAG error. Treat the output as DAG-consistent model attribution, not a treatment-effect estimate.
