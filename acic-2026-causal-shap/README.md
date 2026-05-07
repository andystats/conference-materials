# ACIC 2026 — Expert-Augmented Causal SHAP

**Poster title:** *Expert-Augmented Causal SHAP: Recovering DAG-Consistent Feature Importance via Iterative Causal Discovery and Domain Knowledge*

**Headline:** *SHAP has short memory. Causal SHAP remembers the DAG.*

**Authors:** Pasi · Harrison · Ross · Alderden · Wilson

**Session:** ACIC 2026, Salt Lake City Marriott Downtown · Poster Session 2 · Wed May 13 2026

## What's here

```
acic-2026-causal-shap/
├── index.html                    # Interactive dashboard (7 tabs, React+CDN)
├── README.md                     # This file
├── figures/
│   ├── causal_shap_figure.drawio # Editable causal graph schematic
│   ├── fig1_shap_comparison.png  # Standard vs Causal SHAP bar chart
│   ├── fig2_boundary_curve.png   # When-does-it-matter boundary curve
│   ├── fig3_rank_slope.png       # Feature rank movement slope graph
│   ├── fig4_workflow.png         # 5-step workflow schematic
│   ├── fig5_artifact.png         # Topological artifact schematic
│   └── qr-code.png              # QR linking to the dashboard
├── components/                   # Reusable HTML/JSX snippets (empty, see README)
├── text/
│   ├── abstract.txt              # Accepted abstract text
│   ├── causal-shap-guide.md      # CausalSHAP method guide
│   ├── logistics.txt             # Conference logistics
│   └── notes.txt                 # Working notes on causalShap
├── app/                          # Causal SHAP interactive Python app
│   ├── app.py                    # Streamlit/Shiny app entry point
│   ├── causal_shap.py            # Core causal SHAP implementation
│   ├── requirements.txt          # Python dependencies
│   ├── run_app.bat               # Windows launch script
│   └── data/                     # Simulated + ground truth data
│       ├── ground_truth_edges.csv
│       ├── mimic_expert_dag.csv
│       ├── sample_train.csv
│       ├── simcausal_train.csv
│       └── true_total_effects.json
├── demo/                         # Reproducible simcausal many-mediators demo
│   ├── index.html                # Static teaching page for GitHub Pages
│   ├── causal_shap_simcausal_demo.ipynb
│   ├── simcausal_many_mediators.R
│   ├── run_causal_shap_demo.py
│   └── output/                   # Generated demo data, plots, and summaries
└── poster/                       # Printable poster (42" × 40" landscape)
    ├── ACIC2026_CausalSHAP_Poster.pptx
    ├── ACIC2026_CausalSHAP_Poster.pdf
    ├── build_poster.py           # Regenerates figures + PPTX
    └── export_pdf.py             # PPTX → PDF via PowerPoint COM
```

## Dashboard

Single-file React + Recharts + KaTeX (CDN, no build step). Seven tabs:

1. **The Artifact** — the topological problem, schematic and plain English
2. **The Correction** — observational vs interventional Shapley, toggleable DAG
3. **simcausal Evidence** — interactive bar comparison with role highlighting
4. **Rank Movement** — hoverable slope graph
5. **When It Matters** — boundary-condition slider
6. **The Workflow** — 5-step expandable pipeline
7. **MIMIC-IV + Try It** — expert DAG with vasopressor pathway, install instructions, references

Live at: `https://andystats.github.io/conference-materials/acic-2026-causal-shap/`

## Running the app

```bash
cd app
pip install -r requirements.txt
python app.py
```

Requires Python 3.13+ with `streamlit`, `shap`, `causal-learn`, and dependencies in `requirements.txt`.

## Running the simcausal demo

```bash
Rscript demo/simcausal_many_mediators.R 2500 20260506 demo/output
py -3.13 demo/run_causal_shap_demo.py --output-dir demo/output --n-perms 16 --n-background 8 --n-instances 12
```

The demo lives at `demo/index.html` and the teaching notebook is `demo/causal_shap_simcausal_demo.ipynb`. It generates a DAG with many mediators plus downstream proxy variables that foil standard SHAP, then reruns attribution with the expert DAG using `app/causal_shap.py`.

## Regenerating the poster

```bash
cd poster
python build_poster.py          # regenerate figures + QR + .pptx
python export_pdf.py            # render .pptx to .pdf (requires PowerPoint)
```

Requires `python-pptx`, `qrcode[pil]`, `matplotlib`, and `pywin32`.
