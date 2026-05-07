#!/usr/bin/env python
"""Run the simcausal many-mediators causal SHAP demo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import shap
from scipy.stats import kendalltau, spearmanr
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


REPO_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = REPO_ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from causal_shap import compute_causal_shap_fast, dag_from_edges_csv, mean_abs_shap


ROLE_COLORS = {
    "Root cause": "#1f77b4",
    "Treatment": "#2ca02c",
    "Mediator": "#ff7f0e",
    "Downstream proxy": "#d62728",
    "Outcome": "#4b5563",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / "demo" / "output"),
        help="Directory containing simcausal outputs and receiving analysis outputs.",
    )
    parser.add_argument("--n-perms", type=int, default=16, help="Topological permutations for causal SHAP.")
    parser.add_argument("--n-background", type=int, default=8, help="Background draws per intervention.")
    parser.add_argument("--n-instances", type=int, default=12, help="Evaluation rows for causal SHAP.")
    parser.add_argument("--seed", type=int, default=20260506, help="Random seed.")
    return parser.parse_args()


def standard_shap_values(model: GradientBoostingRegressor, x_train: pd.DataFrame, seed: int) -> pd.DataFrame:
    background = x_train.sample(min(200, len(x_train)), random_state=seed)
    evaluation = x_train.sample(min(250, len(x_train)), random_state=seed + 1)
    explainer = shap.Explainer(model, background)
    values = explainer(evaluation)
    return pd.DataFrame(values.values, columns=x_train.columns)


def rank_series(values: pd.Series) -> pd.Series:
    return values.rank(ascending=False, method="min").astype(int)


def summarize_by_role(rankings: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for method, column in [
        ("Standard SHAP", "standard_shap"),
        ("Causal SHAP", "causal_shap"),
        ("True total effect", "true_abs_total_effect"),
    ]:
        total = rankings[column].sum()
        for role, group in rankings.groupby("role", dropna=False):
            mass = group[column].sum()
            rows.append(
                {
                    "method": method,
                    "role": role,
                    "attribution_mass": mass,
                    "share": mass / total if total else 0.0,
                }
            )
    return pd.DataFrame(rows)


def draw_dag(edges: pd.DataFrame, roles: pd.DataFrame, output_file: Path) -> None:
    graph = nx.DiGraph()
    for row in edges.itertuples(index=False):
        graph.add_edge(getattr(row, "_0"), row.to, coefficient=row.coefficient)

    role_map = dict(zip(roles["node"], roles["role"]))
    layers = {
        "Root cause": 0,
        "Treatment": 1,
        "Mediator": 2,
        "Downstream proxy": 3,
        "Outcome": 4,
    }
    grouped = {layer: [] for layer in layers}
    for node in graph.nodes:
        grouped.setdefault(role_map.get(node, "Mediator"), []).append(node)

    pos = {}
    for role, x in layers.items():
        nodes = sorted(grouped.get(role, []))
        if not nodes:
            continue
        y_values = np.linspace(1, -1, len(nodes))
        for y, node in zip(y_values, nodes):
            pos[node] = (x, y)

    plt.figure(figsize=(13, 7))
    node_colors = [ROLE_COLORS.get(role_map.get(node, ""), "#9ca3af") for node in graph.nodes]
    nx.draw_networkx_edges(graph, pos, alpha=0.22, arrows=True, arrowsize=12, width=1.0)
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=1800, edgecolors="white", linewidths=1.0)
    nx.draw_networkx_labels(graph, pos, font_size=8, font_weight="semibold")
    legend_handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markersize=10, label=role)
        for role, color in ROLE_COLORS.items()
        if role != "Outcome"
    ]
    legend_handles.append(
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=ROLE_COLORS["Outcome"], markersize=10, label="Outcome")
    )
    plt.legend(handles=legend_handles, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.08))
    plt.axis("off")
    plt.title("simcausal DAG: upstream causes, mediators, and downstream predictive proxies", fontsize=14, weight="bold")
    plt.tight_layout()
    plt.savefig(output_file, dpi=180, bbox_inches="tight")
    plt.close()


def draw_feature_plot(rankings: pd.DataFrame, output_file: Path) -> None:
    plot_df = rankings.copy()
    plot_df["max_display"] = plot_df[["standard_shap", "causal_shap", "true_abs_total_effect_scaled"]].max(axis=1)
    plot_df = plot_df.sort_values("max_display", ascending=False).head(16).iloc[::-1]

    y = np.arange(len(plot_df))
    height = 0.24
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(y + height, plot_df["standard_shap"], height=height, color="#9ca3af", label="Standard SHAP")
    ax.barh(y, plot_df["causal_shap"], height=height, color="#2563eb", label="Causal SHAP")
    ax.barh(
        y - height,
        plot_df["true_abs_total_effect_scaled"],
        height=height,
        color="#10b981",
        label="True total effect (scaled)",
    )

    labels = [f"{row.feature}  [{row.role}]" for row in plot_df.itertuples()]
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Relative importance")
    ax.set_title("Standard SHAP rewards proxy descendants; causal SHAP moves attribution upstream", weight="bold")
    ax.legend(loc="lower right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=180, bbox_inches="tight")
    plt.close()


def draw_role_plot(role_summary: pd.DataFrame, output_file: Path) -> None:
    methods = ["Standard SHAP", "Causal SHAP", "True total effect"]
    roles = ["Root cause", "Treatment", "Mediator", "Downstream proxy"]
    pivot = (
        role_summary.pivot_table(index="method", columns="role", values="share", fill_value=0.0)
        .reindex(index=methods, columns=roles, fill_value=0.0)
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    bottom = np.zeros(len(pivot))
    x = np.arange(len(pivot))
    for role in roles:
        values = pivot[role].values
        ax.bar(x, values, bottom=bottom, label=role, color=ROLE_COLORS[role], width=0.6)
        bottom += values

    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Share of total absolute attribution")
    ax.set_title("Causal knowledge suppresses attribution to downstream proxies", weight="bold")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=180, bbox_inches="tight")
    plt.close()


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)
    np.random.seed(args.seed)

    output_dir = Path(args.output_dir).resolve()
    data_file = output_dir / "simcausal_many_mediators.csv"
    edge_file = output_dir / "ground_truth_edges.csv"
    role_file = output_dir / "node_roles.csv"
    truth_file = output_dir / "true_total_effects.csv"

    missing = [p for p in [data_file, edge_file, role_file, truth_file] if not p.exists()]
    if missing:
        missing_text = "\n".join(str(p) for p in missing)
        raise FileNotFoundError(f"Missing simcausal output. Run simcausal_many_mediators.R first:\n{missing_text}")

    data = pd.read_csv(data_file)
    edges = pd.read_csv(edge_file)
    roles = pd.read_csv(role_file)
    truth = pd.read_csv(truth_file)

    outcome = "AcuteRisk"
    feature_names = [col for col in data.columns if col != outcome]
    x = data[feature_names]
    y = data[outcome]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.30, random_state=args.seed)
    model = GradientBoostingRegressor(
        n_estimators=240,
        max_depth=3,
        learning_rate=0.045,
        min_samples_leaf=12,
        subsample=0.85,
        random_state=args.seed,
    )
    model.fit(x_train, y_train)
    pred = model.predict(x_test)

    print("Computing standard SHAP...", flush=True)
    standard = standard_shap_values(model, x_train, args.seed)
    standard_imp = mean_abs_shap(standard).rename("standard_shap")

    dag = dag_from_edges_csv(edge_file, node_list=feature_names + [outcome])
    causal_input = x_train.copy()
    causal_input[outcome] = y_train.values
    # Use a deterministic row order while keeping the stochastic intervention
    # sampler seeded for reproducible teaching outputs.
    causal_input = causal_input.sample(min(900, len(causal_input)), random_state=args.seed)
    print(
        "Computing causal SHAP "
        f"({args.n_instances} rows, {args.n_perms} permutations, {args.n_background} background draws)...",
        flush=True,
    )
    causal = compute_causal_shap_fast(
        model,
        causal_input,
        dag,
        feature_names,
        outcome,
        n_perms=args.n_perms,
        n_background=args.n_background,
        n_instances=args.n_instances,
    )
    causal_imp = mean_abs_shap(causal).rename("causal_shap")

    rankings = (
        pd.DataFrame({"feature": feature_names})
        .merge(standard_imp.reset_index().rename(columns={"index": "feature"}), on="feature", how="left")
        .merge(causal_imp.reset_index().rename(columns={"index": "feature"}), on="feature", how="left")
        .merge(truth[["feature", "true_total_effect", "true_abs_total_effect", "role"]], on="feature", how="left")
    )
    rankings[["standard_shap", "causal_shap", "true_abs_total_effect"]] = rankings[
        ["standard_shap", "causal_shap", "true_abs_total_effect"]
    ].fillna(0.0)
    truth_scale = rankings["causal_shap"].sum() / rankings["true_abs_total_effect"].sum()
    rankings["true_abs_total_effect_scaled"] = rankings["true_abs_total_effect"] * truth_scale
    rankings["standard_rank"] = rank_series(rankings["standard_shap"])
    rankings["causal_rank"] = rank_series(rankings["causal_shap"])
    rankings["truth_rank"] = rank_series(rankings["true_abs_total_effect"])
    rankings["standard_rank_error"] = (rankings["standard_rank"] - rankings["truth_rank"]).abs()
    rankings["causal_rank_error"] = (rankings["causal_rank"] - rankings["truth_rank"]).abs()
    rankings = rankings.sort_values(["causal_rank", "standard_rank"]).reset_index(drop=True)

    tau_standard = kendalltau(
        rankings["standard_rank"],
        rankings["truth_rank"],
    ).statistic
    tau_causal = kendalltau(
        rankings["causal_rank"],
        rankings["truth_rank"],
    ).statistic
    rho_standard = spearmanr(
        rankings["standard_shap"],
        rankings["true_abs_total_effect"],
    ).statistic
    rho_causal = spearmanr(
        rankings["causal_shap"],
        rankings["true_abs_total_effect"],
    ).statistic

    role_summary = summarize_by_role(rankings)
    proxy_standard = float(
        role_summary.loc[
            (role_summary["method"] == "Standard SHAP") & (role_summary["role"] == "Downstream proxy"),
            "share",
        ].iloc[0]
    )
    proxy_causal = float(
        role_summary.loc[
            (role_summary["method"] == "Causal SHAP") & (role_summary["role"] == "Downstream proxy"),
            "share",
        ].iloc[0]
    )

    rankings.to_csv(output_dir / "shap_feature_rankings.csv", index=False)
    role_summary.to_csv(output_dir / "role_attribution_summary.csv", index=False)

    draw_dag(edges, roles, output_dir / "dag_many_mediators.png")
    draw_feature_plot(rankings, output_dir / "standard_vs_causal_shap.png")
    draw_role_plot(role_summary, output_dir / "role_attribution_shift.png")

    summary = {
        "seed": args.seed,
        "n_rows": int(len(data)),
        "n_features": int(len(feature_names)),
        "model": "GradientBoostingRegressor",
        "test_r2": float(r2_score(y_test, pred)),
        "test_mae": float(mean_absolute_error(y_test, pred)),
        "n_perms": args.n_perms,
        "n_background": args.n_background,
        "n_instances": args.n_instances,
        "kendall_tau_standard_vs_truth": float(tau_standard),
        "kendall_tau_causal_vs_truth": float(tau_causal),
        "spearman_r_standard_vs_truth": float(rho_standard),
        "spearman_r_causal_vs_truth": float(rho_causal),
        "mean_rank_error_standard": float(rankings["standard_rank_error"].mean()),
        "mean_rank_error_causal": float(rankings["causal_rank_error"].mean()),
        "downstream_proxy_share_standard": proxy_standard,
        "downstream_proxy_share_causal": proxy_causal,
        "top_standard": rankings.sort_values("standard_shap", ascending=False).head(5)["feature"].tolist(),
        "top_causal": rankings.sort_values("causal_shap", ascending=False).head(5)["feature"].tolist(),
        "top_truth": rankings.sort_values("true_abs_total_effect", ascending=False).head(5)["feature"].tolist(),
    }
    with open(output_dir / "demo_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Causal SHAP simcausal demo complete")
    print(f"Rows/features: {summary['n_rows']}/{summary['n_features']}")
    print(f"Test R^2: {summary['test_r2']:.3f}; MAE: {summary['test_mae']:.3f}")
    print(
        "Kendall tau vs true rank: "
        f"standard={summary['kendall_tau_standard_vs_truth']:.3f}, "
        f"causal={summary['kendall_tau_causal_vs_truth']:.3f}"
    )
    print(
        "Downstream proxy attribution share: "
        f"standard={summary['downstream_proxy_share_standard']:.3f}, "
        f"causal={summary['downstream_proxy_share_causal']:.3f}"
    )
    print("Top standard SHAP:", ", ".join(summary["top_standard"]))
    print("Top causal SHAP:", ", ".join(summary["top_causal"]))
    print("Top true total effects:", ", ".join(summary["top_truth"]))
    print(f"Outputs written to {output_dir}")


if __name__ == "__main__":
    main()
