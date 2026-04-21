"""
ISPOR 2026 MSR72 poster build script.

Produces ISPOR_2026_MSR72_poster_draft_v01.pptx — a single 48" x 36" landscape
slide following the three-band layout from text/poster-key.md.

Run from the poster/ directory:
    python build_poster.py

SVG -> PNG conversion is cached in poster/png_cache/.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

# ----- palette (Boise State) -----
NAVY   = RGBColor(0x00, 0x33, 0xA0)
ORANGE = RGBColor(0xD6, 0x43, 0x09)
BLUE   = RGBColor(0x00, 0x5D, 0xAA)
PURPLE = RGBColor(0x78, 0x3C, 0x96)
INK    = RGBColor(0x3F, 0x44, 0x44)
GRAY   = RGBColor(0xCD, 0xCD, 0xCD)
MUTED  = RGBColor(0x8A, 0x94, 0xA6)
SUBTLE = RGBColor(0x4A, 0x55, 0x68)
BG     = RGBColor(0xFF, 0xFD, 0xF9)
CARD   = RGBColor(0xFF, 0xFF, 0xFF)
CARD2  = RGBColor(0xF6, 0xF8, 0xFC)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
ORANGE_TINT = RGBColor(0xFB, 0xE5, 0xD8)
BLUE_TINT   = RGBColor(0xE6, 0xEE, 0xF9)
PURPLE_TINT = RGBColor(0xF0, 0xE8, 0xF5)

HEAD_FONT = "Georgia"
BODY_FONT = "Calibri"

HERE = os.path.dirname(os.path.abspath(__file__))
PNG  = os.path.join(HERE, "png_cache")
FIG  = os.path.normpath(os.path.join(HERE, "..", "figures"))

def png(name): return os.path.join(PNG, name)
def logo(name): return os.path.join(FIG, name)


# ============================================================================
# Shape helpers
# ============================================================================

def add_text(slide, left, top, width, height, text, *,
             font=BODY_FONT, size=16, bold=False, italic=False,
             color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             line_spacing=1.2):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.margin_top = Emu(0); tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    paras = text.split("\n") if isinstance(text, str) else [text]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        run = p.add_run()
        run.text = para
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
    return tb


def add_rect(slide, left, top, width, height, *,
             fill=None, border=None, border_pt=1.5, rounded=False, arc=0.04):
    shape = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    r = slide.shapes.add_shape(shape, left, top, width, height)
    if rounded:
        r.adjustments[0] = arc
    if fill is None:
        r.fill.background()
    else:
        r.fill.solid()
        r.fill.fore_color.rgb = fill
    if border is None:
        r.line.fill.background()
    else:
        r.line.color.rgb = border
        r.line.width = Pt(border_pt)
    return r


def add_card(slide, left, top, width, height, *, fill=CARD, border=GRAY, border_pt=1.5, accent=None):
    r = add_rect(slide, left, top, width, height, fill=fill, border=border, border_pt=border_pt, rounded=True, arc=0.02)
    if accent:
        bar = add_rect(slide, left, top, Inches(0.18), height, fill=accent, border=None)
    return r


def add_column_header(slide, left, top, width, number, text, accent):
    """Big numbered header with underline."""
    # Number badge
    badge_d = Inches(1.05)
    add_rect(slide, left, top, badge_d, badge_d, fill=accent, border=None, rounded=True, arc=0.5)
    add_text(slide, left, top, badge_d, badge_d,
             number, font=HEAD_FONT, size=44, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    # Title next to badge
    add_text(slide, left + badge_d + Inches(0.3), top, width - badge_d - Inches(0.3), badge_d,
             text, font=HEAD_FONT, size=30, bold=True, color=accent,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    # Accent underline below
    add_rect(slide, left, top + badge_d + Inches(0.1), width, Inches(0.06), fill=accent, border=None)


def add_pic_fit(slide, path, left, top, max_w=None, max_h=None):
    from PIL import Image
    im = Image.open(path)
    nw, nh = im.size
    aspect = nw / nh
    if max_w is not None and max_h is not None:
        h_if_full_w = max_w / aspect
        if h_if_full_w <= max_h:
            return slide.shapes.add_picture(path, left, top, width=max_w)
        else:
            return slide.shapes.add_picture(path, left, top, height=max_h)
    if max_w is not None:
        return slide.shapes.add_picture(path, left, top, width=max_w)
    if max_h is not None:
        return slide.shapes.add_picture(path, left, top, height=max_h)
    return slide.shapes.add_picture(path, left, top)


def add_pic_centered(slide, path, center_x, top, max_w=None, max_h=None):
    """Place a picture constrained by max_w/max_h, horizontally centered on center_x."""
    # First add with provisional left=0 to learn its natural size
    pic = add_pic_fit(slide, path, 0, top, max_w=max_w, max_h=max_h)
    pic.left = int(center_x - pic.width // 2)
    return pic


# ============================================================================
# Build
# ============================================================================

prs = Presentation()
prs.slide_width  = Inches(48)
prs.slide_height = Inches(36)

slide = prs.slides.add_slide(prs.slide_layouts[6])

# Background
add_rect(slide, 0, 0, prs.slide_width, prs.slide_height, fill=BG, border=None)


# ---------------------------------------------------------------------------
# BAND 1 — NAVY TITLE BAR  (y=0 .. 3.2)
# ---------------------------------------------------------------------------

add_rect(slide, 0, 0, prs.slide_width, Inches(3.2), fill=NAVY, border=None)

add_text(slide, Inches(1.0), Inches(0.35), Inches(30), Inches(0.5),
         "ISPOR 2026 · MSR72 · Poster Session 2 · Mon May 18 · Philadelphia",
         size=18, bold=True, color=WHITE)

add_text(slide, Inches(1.0), Inches(0.85), Inches(36), Inches(1.4),
         "Object-Centric Causal Discovery in MIMIC-IV",
         font=HEAD_FONT, size=64, bold=True, color=WHITE,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)

add_text(slide, Inches(1.0), Inches(2.3), Inches(36), Inches(0.8),
         "Hypoalbuminemia prioritized as a candidate upstream driver of hospital-acquired pressure injury, pending confirmatory target-trial / TMLE analysis.",
         size=22, italic=True, color=ORANGE_TINT, line_spacing=1.2)

add_pic_fit(slide, logo("ISPOR_Logo.png"), Inches(40.5), Inches(0.5),
            max_w=Inches(7), max_h=Inches(2.2))


# ---------------------------------------------------------------------------
# BAND 2 — AUTHORS + LOGOS  (y=3.4 .. 5.1)
# ---------------------------------------------------------------------------

add_text(slide, Inches(0.5), Inches(3.4), Inches(47), Inches(0.55),
         "Jenny G. Alderden, PhD, RN, FAAN   (Boise State University)      ·      Michael Haft, PhD   (Xplain Data, Munich)      ·      Andy Wilson, PhD, MStat   (University of Utah)",
         size=22, bold=True, color=INK, align=PP_ALIGN.CENTER)

logo_y = Inches(4.05)
logo_h = Inches(0.95)
add_pic_fit(slide, logo("BoiseState_Logo.png"), Inches(11), logo_y, max_h=logo_h)
add_pic_fit(slide, logo("xplaindata_logo.png"), Inches(22), logo_y, max_h=logo_h)
add_pic_fit(slide, logo("Utah_Logo.jpg"),       Inches(34), logo_y, max_h=logo_h)


# ---------------------------------------------------------------------------
# BAND 3 — MINI ABSTRACT RIBBON  (y=5.3 .. 6.9)
# ---------------------------------------------------------------------------

abs_top = Inches(5.3)
abs_h   = Inches(1.6)
add_card(slide, Inches(0.5), abs_top, Inches(47), abs_h,
         fill=ORANGE_TINT, border=ORANGE, border_pt=2, accent=ORANGE)
add_text(slide, Inches(1.0), abs_top + Inches(0.15), Inches(45), Inches(0.4),
         "ONE-SENTENCE ABSTRACT", size=16, bold=True, color=ORANGE)
add_text(slide, Inches(1.0), abs_top + Inches(0.65), Inches(45), Inches(0.9),
         "Object-centric causal discovery preserves clinical time and relational structure, screens candidate HAPrI drivers in MIMIC-IV v3.1, and hands flagged edges to target-trial emulation with TMLE for confirmation.",
         size=26, color=INK, line_spacing=1.25)


# ---------------------------------------------------------------------------
# BAND 4 — MIDDLE (3 columns)  (y=7.2 .. 20.2, h=13)
# ---------------------------------------------------------------------------

mid_top = Inches(7.2)
mid_h   = Inches(13.0)
col_gap = Inches(0.6)
col_w   = Inches((47 - 2 * 0.6) / 3)          # ≈ 15.27
col_x   = [Inches(0.5),
           Inches(0.5) + col_w + col_gap,
           Inches(0.5) + (col_w + col_gap) * 2]

def render_column(idx, accent, number, title, body, fig_path, fig_max_h):
    x = col_x[idx]
    add_card(slide, x, mid_top, col_w, mid_h, fill=CARD, border=GRAY, border_pt=1.5, accent=accent)
    pad = Inches(0.6)
    # Header (number + title + underline)
    add_column_header(slide, x + pad, mid_top + Inches(0.5), col_w - pad * 2, number, title, accent)
    # Body text (starts below header + underline with comfortable gap)
    body_top = mid_top + Inches(2.0)
    body_h   = Inches(3.4)
    add_text(slide, x + pad, body_top, col_w - pad * 2, body_h,
             body, size=22, color=INK, line_spacing=1.35)
    # Figure: below body text, centered
    fig_top = body_top + body_h + Inches(0.4)
    fig_band_h = mid_h - (fig_top - mid_top) - Inches(0.5)   # leave bottom pad
    center_x = x + col_w // 2
    add_pic_centered(slide, fig_path, center_x, fig_top,
                     max_w=col_w - pad * 2, max_h=min(fig_max_h, fig_band_h))


# Column 1 — Why flat methods stall
render_column(
    0, BLUE, "1", "Why flat stalls",
    "Classic structure learning (PC, GES, LiNGAM, NOTEARS) on a flat EHR table returns the Markov equivalence class — a CPDAG — not an oriented DAG. Clinically distinct stories share the same conditional-independence pattern, so the algorithm cannot tell cause from effect without extra constraints.",
    png("fig_equivalence_class.png"),
    fig_max_h=Inches(6.8),
)

# Column 2 — Object rep + relative-time
render_column(
    1, NAVY, "2", "Object rep + time",
    "Each patient is an object with admissions, labs, medications, procedures, microbiology, and transfers as dated sub-objects. Only events with τ < 0 can be parents of the HAPrI index event at τ = 0; post-index information is excluded as leakage.",
    png("fig_relative_time_guardrail.png"),
    fig_max_h=Inches(6.8),
)

# Column 3 — HAPrI finding
render_column(
    2, ORANGE, "3", "HAPrI finding",
    "Hypoalbuminemia was prioritized as a candidate upstream node for HAPrI. Five known risk factors — mechanical ventilation, hemodynamic instability, immobility, moisture exposure, yeast colonization — were rediscovered without manual feature engineering, supporting clinical plausibility.",
    png("fig_haprI_dag.png"),
    fig_max_h=Inches(6.8),
)


# ---------------------------------------------------------------------------
# BAND 5 — RESULT (albumin + metrics + Noisy-OR + caveat)  (y=20.7 .. 29.0)
# ---------------------------------------------------------------------------

res_top = Inches(20.7)
res_h   = Inches(8.3)

# --- Left: albumin chart card ---
alb_left   = Inches(0.5)
alb_card_w = Inches(19)
add_card(slide, alb_left, res_top, alb_card_w, res_h, accent=ORANGE)
add_text(slide, alb_left + Inches(0.6), res_top + Inches(0.3), alb_card_w - Inches(1.2), Inches(0.55),
         "RESULT  ·  Serum albumin aligned to HAPrI diagnosis",
         size=22, bold=True, color=ORANGE)
add_pic_fit(slide, png("fig_albumin_relative_time.png"),
            alb_left + Inches(0.6), res_top + Inches(1.05),
            max_w=alb_card_w - Inches(1.2), max_h=res_h - Inches(1.8))
add_text(slide, alb_left + Inches(0.6), res_top + res_h - Inches(0.65), alb_card_w - Inches(1.2), Inches(0.45),
         "Illustrative trajectory. Absolute values pending cohort-level analysis.",
         size=15, italic=True, color=MUTED, align=PP_ALIGN.CENTER)

# --- Middle: Headline numbers ---
met_left = alb_left + alb_card_w + Inches(0.5)
met_w    = Inches(9.0)
add_card(slide, met_left, res_top, met_w, res_h, accent=NAVY)
add_text(slide, met_left + Inches(0.5), res_top + Inches(0.3), met_w - Inches(1), Inches(0.55),
         "HEADLINE NUMBERS", size=18, bold=True, color=NAVY)

def metric_block(y, value, value_color, label, sub, value_size=78):
    add_text(slide, met_left + Inches(0.5), y, met_w - Inches(1), Inches(1.35),
             value, font=HEAD_FONT, size=value_size, bold=True, color=value_color,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, met_left + Inches(0.5), y + Inches(1.35), met_w - Inches(1), Inches(0.4),
             label, size=18, bold=True, color=INK, align=PP_ALIGN.CENTER)
    add_text(slide, met_left + Inches(0.5), y + Inches(1.75), met_w - Inches(1), Inches(0.55),
             sub, size=14, italic=True, color=MUTED, align=PP_ALIGN.CENTER, line_spacing=1.25)

metric_block(res_top + Inches(1.0), "5", NAVY, "Rediscovered risks",
             "ventilation · hemodynamic · immobility · moisture · yeast")
metric_block(res_top + Inches(3.4), "3", ORANGE, "Flagged candidates",
             "hypoalbuminemia + albumin & fluid timing")
metric_block(res_top + Inches(5.8), "TMLE", BLUE, "Confirmatory plan",
             "via target-trial emulation", value_size=62)

# --- Right: Noisy-OR + Caveat ---
right_x = met_left + met_w + Inches(0.5)
right_w = prs.slide_width - right_x - Inches(0.5)

# Noisy-OR card (top half)
nor_top = res_top
nor_h   = Inches(4.1)
add_card(slide, right_x, nor_top, right_w, nor_h, accent=BLUE)
add_text(slide, right_x + Inches(0.6), nor_top + Inches(0.3), right_w - Inches(1.2), Inches(0.55),
         "METHODS  ·  Noisy-OR / independent causal influence",
         size=20, bold=True, color=BLUE)
nor_pic = add_pic_centered(
    slide, png("fig_noisy_or_ici.png"),
    right_x + right_w // 2,
    nor_top + Inches(0.95),
    max_w=right_w - Inches(1.2),
    max_h=nor_h - Inches(1.1),
)

# Caveat card (bottom half)
cav_top = nor_top + nor_h + Inches(0.2)
cav_h   = res_h - nor_h - Inches(0.2)
add_card(slide, right_x, cav_top, right_w, cav_h,
         fill=ORANGE_TINT, border=ORANGE, border_pt=3, accent=ORANGE)
add_text(slide, right_x + Inches(0.6), cav_top + Inches(0.3), right_w - Inches(1.2), Inches(0.55),
         "CAVEAT  ·  Read before citing",
         size=20, bold=True, color=ORANGE)
add_text(slide, right_x + Inches(0.6), cav_top + Inches(0.95), right_w - Inches(1.2), cav_h - Inches(1.2),
         "Hypoalbuminemia is a candidate upstream driver, pending clinician review and confirmatory target-trial emulation with TMLE or longitudinal g-methods. The algorithm prioritizes edges for confirmatory analysis; it does not establish cause.",
         size=19, italic=True, color=INK, line_spacing=1.4)


# ---------------------------------------------------------------------------
# BAND 6 — DISCOVERY → INFERENCE PIPELINE  (y=29.5 .. 34.3, h=4.8)
# ---------------------------------------------------------------------------

pipe_top = Inches(29.5)
pipe_h   = Inches(4.8)
pipe_x   = Inches(0.5)
pipe_w   = Inches(47)

add_card(slide, pipe_x, pipe_top, pipe_w, pipe_h, accent=NAVY)
add_text(slide, pipe_x + Inches(0.6), pipe_top + Inches(0.3), pipe_w - Inches(1.2), Inches(0.5),
         "DISCOVERY → INFERENCE  ·  From a prioritized edge to a confirmed intervention effect",
         size=22, bold=True, color=NAVY)

block_count = 4
block_top = pipe_top + Inches(1.0)
block_h   = Inches(3.3)
inner_pad = Inches(0.7)
avail_w   = pipe_w - inner_pad * 2
gap       = Inches(0.35)
block_w   = (avail_w - gap * (block_count - 1)) / block_count

blocks = [
    ("1", "Object representation",
     "Patient as a temporally ordered object. Admissions, labs, medications, procedures, microbiology, transfers — all dated sub-objects.",
     NAVY, BLUE_TINT),
    ("2", "Constrained discovery",
     "Search millions of object-tree projections. Temporal precedence and relational structure orient edges a flat CPDAG leaves ambiguous.",
     NAVY, BLUE_TINT),
    ("3", "Clinician review",
     "Domain experts prune implausible edges and endorse the subset worth confirmatory work. Surviving edges become pre-specified estimands.",
     PURPLE, PURPLE_TINT),
    ("4", "Target trial / TMLE",
     "Emulate the would-be randomized trial; estimate with TMLE or longitudinal g-methods. Doubly robust: consistent if either model is correct.",
     ORANGE, ORANGE_TINT),
]

for i, (n, title, body, accent, tint) in enumerate(blocks):
    x = pipe_x + inner_pad + (block_w + gap) * i
    add_card(slide, x, block_top, block_w, block_h, fill=tint, border=accent, border_pt=2.5, accent=accent)
    # Number circle
    circ_d = Inches(0.95)
    add_rect(slide, x + Inches(0.4), block_top + Inches(0.35), circ_d, circ_d,
             fill=accent, border=None, rounded=True, arc=0.5)
    add_text(slide, x + Inches(0.4), block_top + Inches(0.35), circ_d, circ_d,
             n, font=HEAD_FONT, size=34, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    # Title
    add_text(slide, x + Inches(1.55), block_top + Inches(0.4), block_w - Inches(1.9), Inches(0.9),
             title, font=HEAD_FONT, size=22, bold=True, color=accent,
             anchor=MSO_ANCHOR.MIDDLE)
    # Body
    add_text(slide, x + Inches(0.45), block_top + Inches(1.55), block_w - Inches(0.9), block_h - Inches(1.75),
             body, size=17, color=INK, line_spacing=1.35)
    # Arrow between blocks (except after last)
    if i < block_count - 1:
        ax = x + block_w
        ay = block_top + block_h // 2
        arrow = slide.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW,
            int(ax + Inches(0.03)),
            int(ay - Inches(0.24)),
            int(gap - Inches(0.06)),
            Inches(0.48),
        )
        arrow.fill.solid(); arrow.fill.fore_color.rgb = accent
        arrow.line.fill.background()


# ---------------------------------------------------------------------------
# FOOTER — references + contact  (y=34.6 .. 35.8)
# ---------------------------------------------------------------------------

footer_top = Inches(34.6)
add_rect(slide, Inches(0.5), footer_top, Inches(47), Inches(0.03), fill=GRAY, border=None)

add_text(slide, Inches(0.5), footer_top + Inches(0.2), Inches(47), Inches(0.4),
         "MIMIC-IV v3.1 (Johnson et al., Sci Data 2023)   ·   Spirtes, Glymour & Scheines (2001)   ·   Hernán & Robins AJE (2016)   ·   van der Laan & Rubin IJB (2006)",
         size=14, color=SUBTLE, align=PP_ALIGN.CENTER)

add_text(slide, Inches(0.5), footer_top + Inches(0.65), Inches(47), Inches(0.5),
         "Contact: arw2@utah.edu      ·      Companion dashboard + full references: [QR / URL]      ·      Method on Xplain Data's object-analytic engine      ·      No financial conflicts",
         size=14, bold=True, color=NAVY, align=PP_ALIGN.CENTER)


# ============================================================================
# SAVE
# ============================================================================

out_path = os.path.join(HERE, "ISPOR_2026_MSR72_poster_draft_v01.pptx")
prs.save(out_path)
print(f"Saved: {out_path}")
print(f"Size:  48\" x 36\" landscape")
