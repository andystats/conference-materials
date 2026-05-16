# ACIC 2026 Causal SHAP

Primary page:

https://www.tao-rwd.com/acic-2026/causal-shap

Poster:

`poster.pdf`

## Local Demo App

```powershell
cd acic-2026-causal-shap\app
py -3.13 -m pip install -r requirements.txt
py -3.13 -m shiny run --port 8000 app.py
```

Then open:

```text
http://127.0.0.1:8000
```

The app uses the checked-in simcausal demo data in `app/data/` and compares standard SHAP against causal SHAP using the known true DAG.
