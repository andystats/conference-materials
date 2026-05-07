# Causal SHAP Interactive App

This folder contains the Python Shiny app used for the ACIC 2026 causal SHAP workflow.

The public GitHub Pages site is static, so it cannot run this app in the browser. To try causal SHAP on your own data, run the app locally and upload a CSV.

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

## Using Your Own CSV

1. Open the `Data` tab.
2. Select `Upload custom CSV`.
3. Upload a CSV with one row per observation and numeric columns for candidate features and outcome.
4. Select variables to include.
5. Use `Discover` to estimate candidate graph structure.
6. Add required and forbidden edges from domain knowledge.
7. Use `Causal SHAP` to compare standard SHAP, DAG-constrained causal SHAP, and adjustment-set SHAP.

## What You Need To Provide

For a meaningful causal SHAP run, the app needs:

- A prediction outcome column.
- Candidate feature columns.
- A DAG source: discovered graph, expert edge list, or ground-truth/simulation graph.
- Enough domain knowledge to rule out impossible directions, especially time-reversed arrows and descendants of the outcome.

## Important Caveat

Causal SHAP does not discover true causes by itself. It explains a fitted prediction model under explicit causal assumptions. If the DAG is wrong, the attribution can be wrong in the direction of the DAG error. Treat the output as DAG-consistent model attribution, not a treatment-effect estimate.
