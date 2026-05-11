# ACIC 2026 Causal SHAP Demo

This folder is now scoped to one purpose: support the ACIC 2026 live demo where vanilla SHAP is compared against DAG-informed causal SHAP.

The public entry surface is `index.html`. The Shiny app in `app/` is the local interactive companion for the same simcausal demo.

## Poster Specs

Best available 2026-specific source is the SCI presenter email from April 16, 2026, "2026 American Causal Inference Conference (ACIC): Poster Presenter Information":

- Orientation: landscape.
- Maximum size: 42 in x 42 in.
- Recommended size: 42 in x 40 in.
- Setup starts at 3 PM on the day of the poster session.

The public ACIC/CTML poster guideline page also says poster displays are limited to half of one side of a 4 ft x 8 ft tack board, recommends 30 in x 40 in, and caps the maximum dimension at 42 in x 42 in: https://ctml.berkeley.edu/poster-presentation-guidelines

The local `poster/TaoRWD_CausalSHAP_Poster_03.pdf` working copy is 48 in x 36 in by PDF media box, so it is landscape but wider than the 42-inch maximum in the 2026 presenter email. The `poster/` folder is ignored because the public repo surface is now scoped to the demo and local app.

## Demo Narrative

The demo uses simulated observational data with:

- upstream root causes,
- pathophysiologic mediators,
- downstream proxy measurements,
- a continuous outcome, `AcuteRisk`.

The downstream proxies are deliberately predictive but have no directed path into the outcome. Vanilla SHAP therefore gives them high feature importance. Once the known true DAG is supplied, causal SHAP constrains permutations to respect causal ordering and moves attribution upstream.

## Public Page

Open:

```text
https://andystats.github.io/conference-materials/acic-2026-causal-shap/
```

Locally, open `index.html` or serve the repo root:

```powershell
cd C:\Users\wilso\OneDrive\Documents\GitHub\conference-materials
py -3 -m http.server 8000
```

Then visit:

```text
http://127.0.0.1:8000/acic-2026-causal-shap/
```

## Run The App

From this folder:

```powershell
cd app
py -3.13 -m pip install -r requirements.txt
py -3.13 -m shiny run --port 8000 app.py
```

Open:

```text
http://127.0.0.1:8000
```

Suggested demo sequence:

1. Load the default simcausal teaching data.
2. Go to `Causal SHAP`.
3. Run `Standard SHAP only`.
4. Switch to `Compare standard vs causal SHAP`.
5. Keep `Known true DAG` selected and compute again.
6. Use the plot and rank table to show proxies moving down and upstream causes/mediators moving up.

## Regenerate Reference Outputs

From `acic-2026-causal-shap/`:

```powershell
Rscript demo\simcausal_many_mediators.R 2500 20260506 demo\output
py -3.13 demo\run_causal_shap_demo.py --output-dir demo\output --n-perms 16 --n-background 8 --n-instances 12
```

The local app reads the demo outputs in `demo/output/`, so the static page, notebook, and app stay aligned.
