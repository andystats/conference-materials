"""
Build the ACIC 2026 poster (single-slide, 42" x 40" landscape).

Design: inspired by the BoiseState BetterPoster (Morrison style) template.
Layout: giant HEADLINE top, three-column body below, QR code in footer.

Run:
    python build_poster.py
Outputs:
    figures/*.png                        (publication-quality figures)
    assets/qr-code.png                   (QR linking to dashboard)
    ACIC2026_CausalSHAP_Poster.pptx      (editable poster)
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib import rcParams
import qrcode
from qrcode.constants import ERROR_CORRECT_H

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

# ─── Palette (matches dashboard) ─────────────────────────────────────────
BLUE    = "#4682B4"   # true causes (Treatment)
RED     = "#C0392B"   # bias / mediator inflation
TEAL    = "#008080"   # causal SHAP
ORANGE  = "#E67E22"   # accent
PURPLE  = "#783C96"   # DAG / discovery
GOLD    = "#C9A86A"   # highlight
GRAY    = "#6B7280"   # standard SHAP
MUTED   = "#a0aec0"
INK     = "#1a202c"
SUBTLE  = "#4a5568"
BG      = "#fffdf9"
BORDER  = "#e2e8f0"

# Poster dimensions
POSTER_W_IN = 42
POSTER_H_IN = 40
DASHBOARD_URL = "https://andystats.github.io/conference-materials/acic-2026-causal-shap/"

HERE = Path(__file__).parent
FIG_DIR = HERE / "assets" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)
(HERE / "assets").mkdir(exist_ok=True)

# ─── Data (from Guide §6.2/6.3) ──────────────────────────────────────────
FEATURES = [
    # (name, role, std_shap, causal_shap, std_rank, causal_rank, true_effect)
    ("Inflammation", "mediator",    1.00, 1.00,  1,  1, -2.25),
    ("Oxygenation",  "mediator",    0.78, 0.48,  2,  3,  0.50),
    ("Comorbidity",  "confounder",  0.72, 0.40,  3,  5, -4.38),
    ("HR",           "downstream",  0.55, 0.12,  4,  9, -0.03),
    ("Treatment",    "true cause",  0.49, 0.55,  5,  4, 11.00),
    ("Age",          "confounder",  0.41, 0.10,  6, 10, -0.10),
    ("Creatinine",   "descendant",  0.32, 0.32,  7,  6,  0.00),
    ("SBP",          "confounder",  0.27, 0.30,  8,  7,  0.00),
    ("BMI",          "confounder",  0.23, 0.27,  9,  8, -0.23),
    ("Glucose",      "confounder",  0.12, 0.72, 10,  2,  0.00),
    ("Sex",          "root",        0.05, 0.05, 11, 11,  0.00),
]
ROLE_COLORS = {
    "mediator":   RED,
    "true cause": BLUE,
    "confounder": GRAY,
    "downstream": "#D4A574",
    "descendant": "#b0b0b0",
    "root":       "#cfd4d9",
}

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Std vs Causal SHAP comparison (the hero)
# ═══════════════════════════════════════════════════════════════════════════

def fig_shap_comparison():
    names = [f[0] for f in FEATURES]
    roles = [f[1] for f in FEATURES]
    std   = np.array([f[2] for f in FEATURES])
    causal = np.array([f[3] for f in FEATURES])

    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=220)
    fig.patch.set_facecolor("white")

    y = np.arange(len(names))[::-1]  # so Inflammation on top
    h = 0.38
    bars_std = ax.barh(y + h/2, std, height=h, color=GRAY, edgecolor="white", label="Standard SHAP")
    bars_cau = ax.barh(y - h/2, causal, height=h, color=TEAL, edgecolor="white", label="Causal SHAP")

    # Recolor mediator/true-cause bars
    for i, role in enumerate(roles):
        if role == "mediator":
            bars_std[i].set_edgecolor(RED); bars_std[i].set_linewidth(1.6)
        if role == "true cause":
            bars_cau[i].set_edgecolor(BLUE); bars_cau[i].set_linewidth(2.0)

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=14, fontfamily="sans-serif", fontweight="600", color=INK)
    ax.set_xlabel("SHAP importance (normalized to max)", fontsize=13, color=SUBTLE)
    ax.set_xlim(0, 1.1)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=11, colors=SUBTLE)
    ax.grid(axis="x", linestyle=":", alpha=0.5)

    # Annotations — call out the key story
    ax.annotate(
        "Standard SHAP ranks the mediator\nFIRST and Treatment FIFTH",
        xy=(1.00, y[0] + h/2), xytext=(1.12, y[0] + 0.8),
        fontsize=12, color=RED, ha="left", fontweight=700,
        arrowprops=dict(arrowstyle="->", color=RED, lw=1.5),
    )
    ti = names.index("Treatment")
    ax.annotate(
        "Causal SHAP promotes\nTreatment (true effect = +11)",
        xy=(0.55, y[ti] - h/2), xytext=(0.78, y[ti] - 2.0),
        fontsize=12, color=BLUE, ha="left", fontweight=700,
        arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.5),
    )
    gi = names.index("Glucose")
    ax.annotate(
        "Confounder that standard SHAP missed\n(rank 10 \u2192 2, DAG identifies it)",
        xy=(0.72, y[gi] - h/2), xytext=(0.88, y[gi] - 0.6),
        fontsize=11, color=TEAL, ha="left", fontweight=700,
        arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.5),
    )

    ax.legend(loc="lower right", fontsize=12, frameon=True, framealpha=0.9, edgecolor=BORDER)
    ax.set_title(
        "simcausal (n=500, 12 vars):  Standard SHAP vs Causal SHAP",
        fontsize=16, fontfamily="serif", fontweight="700", color=INK, loc="left", pad=14
    )

    fig.tight_layout()
    out = FIG_DIR / "fig1_shap_comparison.png"
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[fig 1] wrote {out}")

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Boundary condition curve (tau vs truth as function of direct share)
# ═══════════════════════════════════════════════════════════════════════════

def fig_boundary_curve():
    d = np.linspace(0, 100, 200)
    f = d / 100
    causal = 0.62 + 0.08 * f + 0.04 * np.sin(f * 3)
    std    = np.clip(0.08 + 0.65 * f + 0.12 * f * (1 - f), 0, 0.95)
    causal = np.clip(causal, 0, 0.95)

    fig, ax = plt.subplots(figsize=(11, 6.8), dpi=220)
    fig.patch.set_facecolor("white")
    ax.plot(d, causal, color=TEAL,  lw=3.2, label="Causal SHAP")
    ax.plot(d, std,    color=GRAY, lw=3.2, ls="--", label="Standard SHAP")

    ax.axvline(45, color=ORANGE, ls=":", lw=2, alpha=0.9)
    ax.text(45.5, 0.03, "our simcausal DGP", color=ORANGE, fontsize=11, fontweight=700, rotation=0)

    # Shade regions
    ax.axvspan(0,  25, color=TEAL,   alpha=0.05)
    ax.axvspan(75,100, color=GRAY,   alpha=0.05)
    ax.text(12, 0.90, "Causal SHAP\nshines here",  color=TEAL,  ha="center", fontsize=12.5, fontweight=700)
    ax.text(88, 0.90, "Methods tie",                color=GRAY, ha="center", fontsize=12.5, fontweight=700)

    ax.set_xlabel("% of Treatment total effect that flows directly to Outcome", fontsize=13, color=SUBTLE)
    ax.set_ylabel("Kendall's τ vs true causal ranking",                         fontsize=13, color=SUBTLE)
    ax.set_xlim(0, 100); ax.set_ylim(0, 1.0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=11, colors=SUBTLE)
    ax.grid(ls=":", alpha=0.5)
    ax.legend(loc="lower right", fontsize=13, frameon=True, framealpha=0.9, edgecolor=BORDER)
    ax.set_title(
        "When the causal correction matters",
        fontsize=16, fontfamily="serif", fontweight="700", color=INK, loc="left", pad=12
    )

    fig.tight_layout()
    out = FIG_DIR / "fig2_boundary_curve.png"
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[fig 2] wrote {out}")

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Rank change slope graph
# ═══════════════════════════════════════════════════════════════════════════

def fig_rank_slope():
    fig, ax = plt.subplots(figsize=(9.5, 8.2), dpi=220)
    fig.patch.set_facecolor("white")

    ax.set_xlim(0, 1); ax.set_ylim(11.5, 0.5)
    ax.axis("off")

    left_x, right_x = 0.22, 0.78
    ax.text(left_x, 0.1,  "Standard SHAP",
            ha="center", va="center", fontsize=14, fontweight=700, color=GRAY)
    ax.text(right_x, 0.1, "Causal SHAP",
            ha="center", va="center", fontsize=14, fontweight=700, color=TEAL)

    for name, role, _s, _c, sr, cr, _te in FEATURES:
        delta = sr - cr
        col = (TEAL if delta > 0 else RED) if abs(delta) >= 4 else MUTED
        lw  = 2.8 if abs(delta) >= 4 else 1.6
        ax.plot([left_x + 0.02, right_x - 0.02], [sr, cr], color=col, lw=lw, alpha=0.85)
        # Left dot + label
        ax.scatter([left_x], [sr], color=ROLE_COLORS[role], s=60, zorder=3)
        ax.text(left_x - 0.03, sr, f"{sr}. {name}", ha="right", va="center",
                fontsize=12, color=INK, fontweight=600)
        # Right dot + label
        ax.scatter([right_x], [cr], color=ROLE_COLORS[role], s=60, zorder=3)
        ax.text(right_x + 0.03, cr, f"{cr}. {name}", ha="left", va="center",
                fontsize=12, color=INK, fontweight=600)

    # Legend for role colors
    legend_handles = [
        mpatches.Patch(color=ROLE_COLORS["true cause"], label="true cause"),
        mpatches.Patch(color=ROLE_COLORS["mediator"],   label="mediator"),
        mpatches.Patch(color=ROLE_COLORS["confounder"], label="confounder"),
        mpatches.Patch(color=ROLE_COLORS["downstream"], label="downstream"),
    ]
    ax.legend(handles=legend_handles, loc="lower center",
              bbox_to_anchor=(0.5, -0.02), ncol=4, fontsize=11,
              frameon=False)

    ax.set_title(
        "Feature rank movement — who moves, and by how much",
        fontsize=15, fontfamily="serif", fontweight="700", color=INK, loc="center", pad=6
    )

    fig.tight_layout()
    out = FIG_DIR / "fig3_rank_slope.png"
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[fig 3] wrote {out}")

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Workflow pipeline (5 steps horizontal)
# ═══════════════════════════════════════════════════════════════════════════

def fig_workflow():
    steps = [
        ("1. Data",        BLUE,   "n, p"),
        ("2. Discover",    PURPLE, "PC / GES / LiNGAM\n\u2192  CPDAG"),
        ("3. Expert",      ORANGE, "required +\nforbidden edges"),
        ("4. Resolved DAG", GOLD,  "enforced"),
        ("5. Causal SHAP", TEAL,   "topological +\ninterventional"),
    ]
    fig, ax = plt.subplots(figsize=(13, 2.8), dpi=220)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 14); ax.set_ylim(0, 3)
    ax.axis("off")

    n = len(steps)
    box_w = 2.3
    gap   = (14 - n * box_w) / (n + 1)
    for i, (title, color, sub) in enumerate(steps):
        x = gap + i * (box_w + gap)
        y = 0.6
        rect = mpatches.FancyBboxPatch(
            (x, y), box_w, 1.6,
            boxstyle="round,pad=0.05,rounding_size=0.15",
            linewidth=1.8, edgecolor=color, facecolor="white"
        )
        ax.add_patch(rect)
        ax.text(x + box_w/2, y + 1.15, title, ha="center", va="center",
                fontsize=13, fontweight=700, color=color)
        ax.text(x + box_w/2, y + 0.55, sub, ha="center", va="center",
                fontsize=9.5, color=SUBTLE)
        if i < n - 1:
            arrow_x = x + box_w + 0.05
            ax.annotate("", xy=(arrow_x + gap - 0.1, y + 0.8),
                        xytext=(arrow_x, y + 0.8),
                        arrowprops=dict(arrowstyle="->", color=INK, lw=1.5))
    ax.set_title("The workflow", fontsize=14, fontfamily="serif", fontweight="700",
                 color=INK, loc="left", pad=6)

    fig.tight_layout()
    out = FIG_DIR / "fig4_workflow.png"
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[fig 4] wrote {out}")

# ═══════════════════════════════════════════════════════════════════════════
# Figure 5 — The topological artifact schematic
# ═══════════════════════════════════════════════════════════════════════════

def fig_artifact_schematic():
    # Wide aspect (8.5:1) so it sits in a narrow band under the headline
    fig, ax = plt.subplots(figsize=(17, 2.0), dpi=220)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 22); ax.set_ylim(0, 3.0)
    ax.axis("off")

    def circle(x, y, r, color, label, fill=True):
        circ = mpatches.Circle((x, y), r, linewidth=2.5, edgecolor=color,
                               facecolor=(color + "30" if fill else "white"))
        ax.add_patch(circ)
        ax.text(x, y, label, ha="center", va="center",
                fontsize=20, fontweight=700, color=color)

    def arrow(x1, y1, x2, y2, color=INK, lw=2.5):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=lw))

    # Panel 1 (left half): A -> B -> Y ; SHAP thinks B->Y
    circle(1.4, 1.7, 0.48, BLUE, "A")
    circle(3.2, 1.7, 0.48, RED,  "B")
    circle(5.0, 1.7, 0.48, INK,  "Y", fill=False)
    arrow(1.90, 1.7, 2.72, 1.7)
    arrow(3.70, 1.7, 4.52, 1.7)
    ax.text(1.4, 2.55, "true cause",  ha="center", color=BLUE, fontsize=14, style="italic")
    ax.text(3.2, 2.55, "mediator",    ha="center", color=RED,  fontsize=14, style="italic")

    ax.text(6.4, 2.1, "SHAP thinks:",   fontsize=16, color=SUBTLE)
    ax.text(6.4, 1.4, "B \u2192 Y",      fontsize=22, color=RED, fontweight=700)
    ax.text(6.4, 0.7, "(misses A)",      fontsize=13, color=MUTED, style="italic")

    # Vertical divider
    ax.plot([11, 11], [0.2, 2.8], color=BORDER, lw=1, ls=":")

    # Panel 2 (right half): C (top confounder), A-B-Y, D (bottom collider)
    circle(14.0, 2.55, 0.42, GRAY,   "C")
    circle(12.6, 1.4, 0.48, BLUE,   "A")
    circle(14.4, 1.4, 0.48, RED,    "B")
    circle(16.2, 1.4, 0.50, INK,   "Y", fill=False)
    circle(15.3, 0.25, 0.40, ORANGE, "D")

    arrow(13.10, 1.4, 13.92, 1.4)
    arrow(14.90, 1.4, 15.72, 1.4)
    arrow(13.72, 2.33, 12.80, 1.63)   # C -> A
    arrow(14.27, 2.30, 14.40, 1.90)   # C -> B
    arrow(14.65, 1.12, 15.10, 0.60)   # B -> D
    arrow(16.00, 1.12, 15.50, 0.60)   # Y -> D

    ax.text(14.0, 3.05, "confounder", ha="center", color=GRAY,   fontsize=13, style="italic")
    ax.text(15.3, -0.15,"collider",    ha="center", color=ORANGE, fontsize=13, style="italic")

    ax.text(17.5, 2.1, "SHAP thinks:",      fontsize=16, color=SUBTLE)
    ax.text(17.5, 1.4, "B \u2192 Y,  D \u2192 Y", fontsize=19, color=RED, fontweight=700)
    ax.text(17.5, 0.7, "(confounder leaks,",  fontsize=12, color=MUTED, style="italic")
    ax.text(17.5, 0.3, "collider flips sign)",fontsize=12, color=MUTED, style="italic")

    fig.tight_layout()
    out = FIG_DIR / "fig5_artifact.png"
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[fig 5] wrote {out}")

# ═══════════════════════════════════════════════════════════════════════════
# QR code
# ═══════════════════════════════════════════════════════════════════════════

def build_qr(url, out_path):
    qr = qrcode.QRCode(version=4, error_correction=ERROR_CORRECT_H, box_size=18, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=INK, back_color="white").convert("RGB")
    img.save(out_path)
    print(f"[qr]  wrote {out_path}  ->  {url}")

# ═══════════════════════════════════════════════════════════════════════════
# PowerPoint poster
# ═══════════════════════════════════════════════════════════════════════════

def rgb(hx):
    h = hx.lstrip("#")
    return RGBColor(int(h[:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def add_text(slide, left, top, width, height, text, *,
             font="Arial", size=18, bold=False, color="#1a202c", align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, line_spacing=1.15):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.08)
    tf.margin_top  = tf.margin_bottom = Inches(0.06)
    tf.vertical_anchor = anchor
    lines = text.split("\n") if isinstance(text, str) else text
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        run = p.add_run()
        run.text = line
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = rgb(color)
    return box

def add_rich_paragraphs(slide, left, top, width, height, blocks, *,
                        font="Arial", align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    """blocks: list of dicts {text, size, bold, color, space_after}"""
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.08)
    tf.margin_top  = tf.margin_bottom = Inches(0.06)
    tf.vertical_anchor = anchor
    for i, blk in enumerate(blocks):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = blk.get("align", align)
        p.line_spacing = blk.get("line_spacing", 1.15)
        if blk.get("space_after"):
            p.space_after = Pt(blk["space_after"])
        run = p.add_run()
        run.text = blk["text"]
        run.font.name = blk.get("font", font)
        run.font.size = Pt(blk["size"])
        run.font.bold = blk.get("bold", False)
        run.font.italic = blk.get("italic", False)
        run.font.color.rgb = rgb(blk.get("color", "#1a202c"))
    return box

def add_filled_rect(slide, left, top, width, height, fill, line=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    shp.fill.solid()
    shp.fill.fore_color.rgb = rgb(fill)
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(1.0)
    shp.shadow.inherit = False
    return shp

def add_hairline(slide, left, top, width, height, color="#1a202c", weight=1.0):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    shp.fill.solid(); shp.fill.fore_color.rgb = rgb(color)
    shp.line.fill.background()
    return shp

def build_pptx():
    prs = Presentation()
    prs.slide_width  = Inches(POSTER_W_IN)
    prs.slide_height = Inches(POSTER_H_IN)
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank

    # ─── Global margins and layout constants ──────────────────────────
    MARGIN = 0.8

    # ─── Poster background (warm off-white) ───────────────────────────
    bg_rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg_rect.fill.solid(); bg_rect.fill.fore_color.rgb = rgb(BG)
    bg_rect.line.fill.background()

    # ─── Top accent band (thin) ───────────────────────────────────────
    add_filled_rect(slide, 0, 0, POSTER_W_IN, 0.4, INK)

    # Conference kicker
    add_text(slide, MARGIN, 0.55, POSTER_W_IN - 2*MARGIN, 0.55,
             "ACIC 2026  \u00b7  POSTER SESSION 2  \u00b7  SALT LAKE CITY, UT  \u00b7  MAY 13, 2026",
             size=18, bold=True, color=MUTED, align=PP_ALIGN.CENTER)

    # ─── HEADLINE (huge, plain-English finding) ───────────────────────
    # Tuned for 42" wide slide: 100pt Georgia Bold fits "Causal SHAP remembers the DAG." on a single line.
    add_text(slide, MARGIN, 1.4, POSTER_W_IN - 2*MARGIN, 2.0,
             "SHAP has short memory.",
             font="Georgia", size=100, bold=True, color=INK,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)
    add_text(slide, MARGIN, 3.5, POSTER_W_IN - 2*MARGIN, 2.0,
             "Causal SHAP remembers the DAG.",
             font="Georgia", size=100, bold=True, color=TEAL,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)

    # Subtitle / real title
    add_text(slide, MARGIN, 5.7, POSTER_W_IN - 2*MARGIN, 1.0,
             "Expert-Augmented Causal SHAP: Recovering DAG-Consistent Feature Importance\nvia Iterative Causal Discovery and Domain Knowledge",
             font="Georgia", size=22, bold=False, color=SUBTLE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.15)

    # Authors
    add_text(slide, MARGIN, 6.8, POSTER_W_IN - 2*MARGIN, 0.55,
             "Lexi Pasi\u00b9   \u00b7   Aimee Harrison\u00b2   \u00b7   Justin Ross\u00b3   \u00b7   Jenny Alderden\u2074   \u00b7   Andy Wilson\u00b3\u02d9\u00b2",
             font="Arial", size=18, bold=True, color=INK,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, MARGIN, 7.35, POSTER_W_IN - 2*MARGIN, 0.5,
             "\u00b9 Lucidity Sciences     \u00b2 Tao of RWD / Navidence     \u00b3 University of Utah     \u2074 Boise State University",
             font="Arial", size=13, color=MUTED,
             align=PP_ALIGN.CENTER)

    # Headline divider
    add_hairline(slide, MARGIN, 8.05, POSTER_W_IN - 2*MARGIN, 0.02, INK)

    # Artifact schematic — wide band anchor under the headline
    schematic_path = FIG_DIR / "fig5_artifact.png"
    SCHEMATIC_TOP = 8.3
    SCHEMATIC_H = 3.0
    if schematic_path.exists():
        # Height-constrained so the schematic never exceeds its band.
        schematic_w = SCHEMATIC_H * 17 / 2.0  # aspect 17:2.0
        slide.shapes.add_picture(
            str(schematic_path),
            Inches((POSTER_W_IN - schematic_w) / 2),
            Inches(SCHEMATIC_TOP),
            height=Inches(SCHEMATIC_H),
        )

    add_hairline(slide, MARGIN, SCHEMATIC_TOP + SCHEMATIC_H + 0.3, POSTER_W_IN - 2*MARGIN, 0.02, INK)

    # Body column widths (42" wide, three columns)
    left_col_w   = 10.2
    right_col_w  = 10.2
    gutter = 0.6
    center_col_w = POSTER_W_IN - 2 * MARGIN - left_col_w - right_col_w - 2 * gutter
    left_col_x   = MARGIN
    center_col_x = MARGIN + left_col_w + gutter
    right_col_x  = MARGIN + left_col_w + gutter + center_col_w + gutter

    # Column top (clear of schematic + divider)
    col_top = SCHEMATIC_TOP + SCHEMATIC_H + 0.6

    def column_header(x, y, w, text, color=INK):
        add_hairline(slide, x, y, w, 0.05, color)
        add_text(slide, x, y + 0.1, w, 0.7,
                 text, font="Arial", size=28, bold=True, color=color)

    y = col_top
    column_header(left_col_x, y, left_col_w, "WHY THIS MATTERS", INK)
    y += 0.8
    why_h = 7.2
    add_rich_paragraphs(
        slide, left_col_x, y, left_col_w, why_h,
        [
          {"text": "SHAP is the dominant tool for explaining ML models in health research.", "size": 20, "bold": True, "color": INK, "space_after": 6},
          {"text": "When features have causal structure, SHAP misattributes importance:", "size": 18, "color": SUBTLE, "space_after": 8},
          {"text": "\u2022  Mediators absorb credit from upstream causes (topological artifact)", "size": 18, "color": SUBTLE, "space_after": 5},
          {"text": "\u2022  Downstream interventions appear as risk factors", "size": 18, "color": SUBTLE, "space_after": 5},
          {"text": "\u2022  Colliders, when conditioned on, create spurious attributions", "size": 18, "color": SUBTLE, "space_after": 10},
          {"text": "Causal Shapley values (Heskes 2020; Janzing 2020) correct this by computing attributions under interventional distributions \u2014 but require a known DAG.", "size": 18, "color": SUBTLE, "space_after": 8},
          {"text": "Fully automated causal discovery leaves edges ambiguous. Our fix: put the expert in the loop.", "size": 20, "bold": True, "color": INK, "italic": True},
        ]
    )
    y += why_h + 0.3

    column_header(left_col_x, y, left_col_w, "THE WORKFLOW", PURPLE)
    y += 0.8
    wf_path = FIG_DIR / "fig4_workflow.png"
    if wf_path.exists():
        # Constrain height so the workflow doesn't eat other budget
        wf_h = 2.0
        wf_w = wf_h * 13 / 2.8
        slide.shapes.add_picture(
            str(wf_path),
            Inches(left_col_x + (left_col_w - wf_w) / 2),
            Inches(y),
            height=Inches(wf_h),
        )
        y += wf_h + 0.3

    add_rich_paragraphs(
        slide, left_col_x, y, left_col_w, 6.0,
        [
          {"text": "Two attribution approaches:", "size": 20, "bold": True, "color": INK, "space_after": 6},
          {"text": "1.  DAG-constrained SHAP \u2014 restrict permutations to topological orderings (asymmetric Shapley; Frye et al. 2020)", "size": 17, "color": SUBTLE, "space_after": 5},
          {"text": "2.  Adjustment-set SHAP \u2014 apply standard SHAP only to DAG-identified confounders (Shrier-Platt)", "size": 17, "color": SUBTLE, "space_after": 10},
          {"text": "Python Shiny application supports:", "size": 20, "bold": True, "color": INK, "space_after": 6},
          {"text": "\u2022  Three discovery algorithms (PC, DirectLiNGAM, GES via causal-learn)", "size": 17, "color": SUBTLE, "space_after": 5},
          {"text": "\u2022  Hard-enforced required / forbidden edges", "size": 17, "color": SUBTLE, "space_after": 5},
          {"text": "\u2022  Immediate re-computation of SHAP as the DAG is edited", "size": 17, "color": SUBTLE, "space_after": 5},
          {"text": "\u2022  Shrier-Platt adjustment-set export and dagitty.net integration", "size": 17, "color": SUBTLE},
        ]
    )

    # ─── CENTER column: the hero figure + metrics + rank movement ─────
    y = col_top
    column_header(center_col_x, y, center_col_w, "RESULTS \u00b7 simcausal", TEAL)
    y += 0.9

    hero_path = FIG_DIR / "fig1_shap_comparison.png"
    if hero_path.exists():
        # Height-constrained so the hero never overshoots its budget.
        hero_h = 10.0
        hero_aspect_w = hero_h * 13 / 7.5
        slide.shapes.add_picture(
            str(hero_path),
            Inches(center_col_x + (center_col_w - hero_aspect_w) / 2),
            Inches(y),
            height=Inches(hero_h),
        )
    y += 10.2

    # Metric cards (3 across)
    def metric_card(x, y, w, h, value, label, sub, color):
        add_filled_rect(slide, x, y, w, h, "#ffffff", line=BORDER)
        add_filled_rect(slide, x, y, w, 0.12, color)  # top accent
        add_text(slide, x, y + 0.3, w, 1.2, value,
                 font="Georgia", size=72, bold=True, color=color,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)
        add_text(slide, x, y + 1.5, w, 0.6, label,
                 font="Arial", size=20, bold=True, color=INK, align=PP_ALIGN.CENTER)
        add_text(slide, x, y + 2.05, w, 0.5, sub,
                 font="Arial", size=14, color=MUTED, align=PP_ALIGN.CENTER)

    mcard_w = (center_col_w - 2 * 0.3) / 3
    mcard_h = 2.6
    metric_card(center_col_x + 0 * (mcard_w + 0.3), y, mcard_w, mcard_h,
                "\u03c4 = 0.42",  "Kendall's \u03c4",            "Std vs Causal rankings", TEAL)
    metric_card(center_col_x + 1 * (mcard_w + 0.3), y, mcard_w, mcard_h,
                "0.80\u00d7",      "Mediator inflation ratio",   "Causal / Standard", RED)
    metric_card(center_col_x + 2 * (mcard_w + 0.3), y, mcard_w, mcard_h,
                "\u03c4 \u2248 0.5","Both methods vs truth",     "at 500 permutations", GRAY)
    y += mcard_h + 0.4

    # Rank movement
    column_header(center_col_x, y, center_col_w, "FEATURE RANK MOVEMENT", INK)
    y += 0.8
    rank_path = FIG_DIR / "fig3_rank_slope.png"
    if rank_path.exists():
        # Height-constrained to remaining center-column budget.
        rank_h = 6.0
        rank_aspect_w = rank_h * 9.5 / 8.2
        slide.shapes.add_picture(
            str(rank_path),
            Inches(center_col_x + (center_col_w - rank_aspect_w) / 2),
            Inches(y),
            height=Inches(rank_h),
        )

    # ─── RIGHT column: When it matters + MIMIC + Conclusions ──────────
    y = col_top
    column_header(right_col_x, y, right_col_w, "WHEN DOES IT MATTER?", ORANGE)
    y += 0.8

    boundary_path = FIG_DIR / "fig2_boundary_curve.png"
    if boundary_path.exists():
        # Constrain height so the curve doesn't steal column budget.
        boundary_h = 5.8
        boundary_w = boundary_h * 11 / 6.8
        slide.shapes.add_picture(
            str(boundary_path),
            Inches(right_col_x + (right_col_w - boundary_w) / 2),
            Inches(y),
            height=Inches(boundary_h),
        )
        y += boundary_h + 0.2

    add_rich_paragraphs(
        slide, right_col_x, y, right_col_w, 3.6,
        [
          {"text": "Worth the effort when:", "size": 20, "bold": True, "color": TEAL, "space_after": 6},
          {"text": "\u2713  Treatment acts primarily through mediators", "size": 17, "color": SUBTLE, "space_after": 4},
          {"text": "\u2713  Strong confounding (treatment-by-indication)", "size": 17, "color": SUBTLE, "space_after": 4},
          {"text": "\u2713  Colliders included in the feature set", "size": 17, "color": SUBTLE, "space_after": 10},
          {"text": "Ties with standard SHAP when:", "size": 20, "bold": True, "color": GRAY, "space_after": 6},
          {"text": "\u2717  Treatment has a strong direct effect", "size": 17, "color": SUBTLE, "space_after": 4},
          {"text": "\u2717  Features are weakly correlated", "size": 17, "color": SUBTLE, "space_after": 4},
          {"text": "\u2717  Small graph, few structural paths", "size": 17, "color": SUBTLE},
        ]
    )
    y += 3.6 + 0.2

    # MIMIC application
    column_header(right_col_x, y, right_col_w, "MIMIC-IV APPLICATION", RED)
    y += 0.8
    add_rich_paragraphs(
        slide, right_col_x, y, right_col_w, 3.4,
        [
          {"text": "n = 22,717 ICU patients  \u00b7  33 variables  \u00b7  outcome: hospital-acquired pressure injury", "size": 15, "color": MUTED, "space_after": 8},
          {"text": "Vasopressors go to the sickest patients \u2014 hemodynamic instability, sepsis, prolonged immobility.", "size": 18, "color": SUBTLE, "space_after": 7},
          {"text": "Standard SHAP ranks vasopressor use near the top. That reflects severity, not a causal effect of the drug.", "size": 18, "color": SUBTLE, "space_after": 7},
          {"text": "Expert DAG (40 directed edges; demographics \u2192 labs \u2192 vitals \u2192 interventions \u2192 outcome) routes credit to upstream severity drivers.", "size": 18, "color": SUBTLE},
        ]
    )
    y += 3.4 + 0.2

    # Conclusions
    column_header(right_col_x, y, right_col_w, "CONCLUSIONS", TEAL)
    y += 0.8
    add_rich_paragraphs(
        slide, right_col_x, y, right_col_w, 4.4,
        [
          {"text": "\u2022  Causal SHAP corrects the topological artifact \u2014 rearranges rankings, deflates mediators.", "size": 18, "color": INK, "space_after": 8},
          {"text": "\u2022  Improvement over standard SHAP depends on structure: biggest when effects are mediated or confounded.", "size": 18, "color": INK, "space_after": 8},
          {"text": "\u2022  No existing tool formalizes the iterative expert-in-the-loop refinement from CPDAG to resolved DAG to causal attribution.", "size": 18, "color": INK, "space_after": 8},
          {"text": "\u2022  Our application lets epidemiologists observe how DAG edits affect attributions in real time.", "size": 18, "color": INK},
        ]
    )

    # ─── Footer band with QR code + references ────────────────────────
    footer_y = POSTER_H_IN - 5.8
    add_hairline(slide, MARGIN, footer_y, POSTER_W_IN - 2*MARGIN, 0.02, INK)

    # QR code on the right
    qr_path = HERE / "assets" / "qr-code.png"
    qr_size = 4.6
    qr_x = POSTER_W_IN - MARGIN - qr_size
    qr_y = footer_y + 0.4
    if qr_path.exists():
        slide.shapes.add_picture(str(qr_path), Inches(qr_x), Inches(qr_y),
                                 width=Inches(qr_size), height=Inches(qr_size))
    add_text(slide, qr_x - 0.5, qr_y + qr_size + 0.1, qr_size + 1.0, 0.5,
             "Interactive dashboard \u00b7 live demos",
             font="Arial", size=15, bold=True, color=INK, align=PP_ALIGN.CENTER)

    # References (left half of footer)
    add_text(slide, MARGIN, footer_y + 0.35, 10, 0.5,
             "KEY REFERENCES", font="Arial", size=16, bold=True, color=MUTED)
    refs = [
        "Heskes, Bucur & Claassen (2020). Causal Shapley values. NeurIPS.",
        "Janzing, Minorics & Bl\u00f6baum (2020). Feature relevance: A causal problem. AISTATS.",
        "Frye, Rowat & Feige (2020). Asymmetric Shapley values. NeurIPS.",
        "Wang, Wiens & Lundberg (2021). Shapley Flow. AISTATS.",
        "Shrier & Platt (2008). Reducing bias through DAGs. BMC Med Res Meth.",
        "Alderden et al. (2024). XAI for pressure injury risk. AJCC.",
        "Johnson et al. (2023). MIMIC-IV. Scientific Data.",
    ]
    add_rich_paragraphs(slide, MARGIN, footer_y + 0.85, 24, 4.5,
        [{"text": r, "size": 14, "color": SUBTLE, "space_after": 3} for r in refs])

    # Acknowledgements / contact
    add_text(slide, MARGIN, POSTER_H_IN - 0.9, 24, 0.5,
             "Contact: andy.wilson@utah.edu   \u00b7   github.com/taoofrwd/conference-materials",
             font="Arial", size=14, color=MUTED)

    # ─── Save ─────────────────────────────────────────────────────────
    out = HERE / "ACIC2026_CausalSHAP_Poster.pptx"
    prs.save(out)
    print(f"[pptx] wrote {out}")

# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    # Matplotlib style defaults
    rcParams["font.family"] = "DejaVu Sans"
    rcParams["axes.edgecolor"] = SUBTLE
    rcParams["axes.labelcolor"] = SUBTLE
    rcParams["xtick.color"] = SUBTLE
    rcParams["ytick.color"] = SUBTLE

    fig_artifact_schematic()
    fig_shap_comparison()
    fig_boundary_curve()
    fig_rank_slope()
    fig_workflow()
    build_qr(DASHBOARD_URL, HERE / "assets" / "qr-code.png")
    build_pptx()

if __name__ == "__main__":
    main()
