from pathlib import Path

import pandas as pd
from shiny import App, reactive, render, ui
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

from causal_shap import (
    SIMCAUSAL_TRUE_TOTAL_EFFECTS,
    compare_shap_rankings,
    comparison_bar_plot_to_base64,
    compute_causal_shap_fast,
    compute_standard_shap,
    dag_from_edges_csv,
    mean_abs_shap,
    mediator_inflation_ratio,
    rank_change_table_html,
    shap_bar_plot_to_base64,
)


APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "data" / "simcausal_many_mediators.csv"
DAG_FILE = APP_DIR / "data" / "ground_truth_edges.csv"
OUTCOME = "AcuteRisk"

PROXY_FEATURES = [
    "ShockIndexProxy",
    "VasopressorProxy",
    "MonitoringProxy",
    "RescueProxy",
    "CompositeScoreProxy",
]

UPSTREAM_FEATURES = [
    "BaselineSeverity",
    "ChronicBurden",
    "SocialRisk",
    "PracticeStyle",
    "Age",
    "TreatmentIntensity",
]


def load_data():
    if not DATA_FILE.exists():
        return pd.DataFrame()
    return pd.read_csv(DATA_FILE)


def fit_model(data, feature_cols):
    train, test = train_test_split(data, test_size=0.30, random_state=42)
    model = GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42)
    model.fit(train[feature_cols], train[OUTCOME])
    r2 = r2_score(test[OUTCOME], model.predict(test[feature_cols]))
    return model, r2


def compute_demo(method, n_perms):
    data = load_data()
    if data.empty:
        raise FileNotFoundError(f"Missing demo data: {DATA_FILE}")
    if OUTCOME not in data.columns:
        raise ValueError(f"Expected outcome column {OUTCOME}")
    if not DAG_FILE.exists() and method in {"causal", "compare"}:
        raise FileNotFoundError(f"Missing DAG file: {DAG_FILE}")

    feature_cols = [col for col in data.select_dtypes("number").columns if col != OUTCOME]
    model, r2 = fit_model(data, feature_cols)
    result = {
        "method": method,
        "r2": r2,
        "n_rows": len(data),
        "n_features": len(feature_cols),
    }

    if method in {"standard", "compare"}:
        standard = compute_standard_shap(model, data, feature_cols)
        result["standard_shap"] = standard
        result["standard_importance"] = mean_abs_shap(standard).to_dict()

    if method in {"causal", "compare"}:
        dag = dag_from_edges_csv(DAG_FILE, feature_cols)
        causal = compute_causal_shap_fast(
            model,
            data,
            dag,
            feature_cols,
            OUTCOME,
            n_perms=n_perms,
            n_background=8,
            n_instances=12,
        )
        result["causal_shap"] = causal
        result["causal_importance"] = mean_abs_shap(causal).to_dict()

    if "standard_shap" in result and "causal_shap" in result:
        result["comparison"] = compare_shap_rankings(
            result["standard_shap"],
            result["causal_shap"],
            SIMCAUSAL_TRUE_TOTAL_EFFECTS,
        )
        result["proxy_shift"] = mediator_inflation_ratio(
            result["standard_shap"],
            result["causal_shap"],
            mediator_vars=PROXY_FEATURES,
            root_cause_vars=UPSTREAM_FEATURES,
        )

    return result


APP_CSS = """
<style>
body {
    background: #f8fafc !important;
    color: #111827 !important;
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}
.page {
    max-width: 1120px;
    margin: 0 auto;
    padding: 28px 22px 52px;
}
.hero {
    margin-bottom: 18px;
    padding-bottom: 18px;
    border-bottom: 1px solid #d1d5db;
}
.hero h1 {
    margin: 0;
    font-size: 2rem;
    line-height: 1.1;
}
.hero p {
    max-width: 820px;
    color: #4b5563;
    margin: 10px 0 0;
}
.grid {
    display: grid;
    grid-template-columns: 320px minmax(0, 1fr);
    gap: 18px;
    align-items: start;
}
.card {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 14px;
}
.card-title {
    font-weight: 750;
    margin-bottom: 10px;
    color: #111827;
}
.note {
    color: #4b5563;
    font-size: 0.92rem;
}
.status {
    margin-top: 12px;
    padding: 10px 12px;
    border-radius: 6px;
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
}
.error {
    margin-top: 12px;
    padding: 10px 12px;
    border-radius: 6px;
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
}
.metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 10px;
}
.metric {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 12px;
    background: #ffffff;
}
.metric .label {
    color: #6b7280;
    font-size: 0.78rem;
}
.metric .value {
    color: #111827;
    font-weight: 800;
    font-size: 1.35rem;
}
img.plot {
    width: 100%;
    height: auto;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background: #ffffff;
}
a {
    color: #2563eb;
    font-weight: 650;
}
@media (max-width: 820px) {
    .grid { grid-template-columns: 1fr; }
}
</style>
"""


app_ui = ui.page_fluid(
    ui.HTML(APP_CSS),
    ui.div(
        ui.div(
            ui.h1("ACIC 2026 causal SHAP demo"),
            ui.p(
                "Run ordinary SHAP, then rerun attribution with the known true DAG. "
                "The point is to show how downstream proxy credit changes when the "
                "feature-importance procedure is constrained by causal structure."
            ),
            ui.p(
                ui.a(
                    "Live project page",
                    href="https://www.tao-rwd.com/acic-2026/causal-shap",
                    target="_blank",
                ),
                " | ",
                ui.a("Poster PDF", href="../poster.pdf", target="_blank"),
            ),
            class_="hero",
        ),
        ui.div(
            ui.div(
                ui.div(
                    ui.div("Controls", class_="card-title"),
                    ui.input_radio_buttons(
                        "method",
                        "Attribution run",
                        choices={
                            "standard": "Standard SHAP only",
                            "compare": "Compare standard vs causal SHAP",
                            "causal": "Causal SHAP only",
                        },
                        selected="standard",
                    ),
                    ui.input_slider(
                        "n_perms",
                        "Causal SHAP permutations",
                        min=8,
                        max=80,
                        value=16,
                        step=8,
                    ),
                    ui.input_action_button(
                        "compute",
                        "Run attribution",
                        class_="btn-primary",
                        width="100%",
                    ),
                    ui.output_ui("run_status"),
                    class_="card",
                ),
                ui.div(
                    ui.div("Data", class_="card-title"),
                    ui.output_ui("data_summary"),
                    class_="card",
                ),
            ),
            ui.div(
                ui.div(
                    ui.div("Comparison", class_="card-title"),
                    ui.output_ui("plot_output"),
                    class_="card",
                ),
                ui.div(
                    ui.div("Rank Movement", class_="card-title"),
                    ui.output_ui("rank_output"),
                    class_="card",
                ),
                ui.div(
                    ui.div("Metrics", class_="card-title"),
                    ui.output_ui("metrics_output"),
                    class_="card",
                ),
            ),
            class_="grid",
        ),
        class_="page",
    ),
)


def server(input, output, session):
    result_store = reactive.Value(None)
    data = load_data()

    @output
    @render.ui
    def data_summary():
        if data.empty:
            return ui.HTML(f'<div class="error">Missing {DATA_FILE}</div>')
        return ui.HTML(
            f"""
            <div class="note">
                <strong>{len(data):,}</strong> simulated rows<br>
                <strong>{data.shape[1] - 1}</strong> predictors plus {OUTCOME}<br>
                Known true DAG: {"yes" if DAG_FILE.exists() else "missing"}<br>
                Downstream proxies: {", ".join(PROXY_FEATURES)}
            </div>
            """
        )

    @output
    @render.ui
    @reactive.event(input.compute)
    def run_status():
        try:
            result = compute_demo(input.method(), input.n_perms())
        except Exception as exc:
            result_store.set(None)
            return ui.HTML(f'<div class="error">{exc}</div>')
        result_store.set(result)
        label = {
            "standard": "Standard SHAP",
            "causal": "Causal SHAP",
            "compare": "Standard and causal SHAP",
        }[result["method"]]
        return ui.HTML(f'<div class="status">{label} complete.</div>')

    @output
    @render.ui
    def plot_output():
        result = result_store.get()
        if result is None:
            return ui.HTML('<div class="note">Run attribution to show the plot.</div>')

        image = None
        if "standard_importance" in result and "causal_importance" in result:
            image = comparison_bar_plot_to_base64(
                result["standard_importance"],
                result["causal_importance"],
                title="Standard SHAP vs causal SHAP",
            )
        elif "standard_importance" in result:
            image = shap_bar_plot_to_base64(
                result["standard_importance"],
                title="Standard SHAP",
            )
        elif "causal_importance" in result:
            image = shap_bar_plot_to_base64(
                result["causal_importance"],
                title="Causal SHAP",
                color="#2563eb",
            )

        if not image:
            return ui.HTML('<div class="error">Plot generation failed.</div>')
        return ui.HTML(f'<img class="plot" src="data:image/png;base64,{image}" alt="SHAP comparison plot">')

    @output
    @render.ui
    def rank_output():
        result = result_store.get()
        if result is None:
            return ui.HTML("")
        comparison = result.get("comparison")
        if not comparison:
            return ui.HTML('<div class="note">Run the comparison mode to show rank movement.</div>')
        return ui.HTML(rank_change_table_html(comparison["rank_changes"]))

    @output
    @render.ui
    def metrics_output():
        result = result_store.get()
        if result is None:
            return ui.HTML("")

        metric_items = [
            ("Rows", f'{result["n_rows"]:,}'),
            ("Predictors", str(result["n_features"])),
            ("Held-out R2", f'{result["r2"]:.3f}'),
        ]

        comparison = result.get("comparison", {})
        if "tau_vs_truth_standard" in comparison:
            metric_items.append(("Tau vs truth, standard", f'{comparison["tau_vs_truth_standard"]:.3f}'))
        if "tau_vs_truth_causal" in comparison:
            metric_items.append(("Tau vs truth, causal", f'{comparison["tau_vs_truth_causal"]:.3f}'))

        proxy_shift = result.get("proxy_shift", {})
        if "mediator_inflation" in proxy_shift:
            metric_items.append(("Proxy inflation", f'{proxy_shift["mediator_inflation"]:.2f}x'))
        if "root_cause_boost" in proxy_shift:
            metric_items.append(("Upstream boost", f'{proxy_shift["root_cause_boost"]:.2f}x'))

        cards = "".join(
            f"""
            <div class="metric">
                <div class="label">{label}</div>
                <div class="value">{value}</div>
            </div>
            """
            for label, value in metric_items
        )
        return ui.HTML(f'<div class="metrics">{cards}</div>')


app = App(app_ui, server)
