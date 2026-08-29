---
name: conference-support
description: Guide the three-artifact conference workflow — stand-alone figures, interactive HTML companion, and (optional) poster assembly. Use when building or updating materials for a new conference talk/poster that will be linked from a printed poster via QR code on andystats.github.io/conference-materials.
---

# Conference Support

Workflow for producing conference deliverables that land on `andystats.github.io/conference-materials/<slug>/`. Figures and the interactive HTML companion are primary; the poster PPTX is one downstream assembly, not canonical.

## 1. Directory convention

Each conference project lives in `Box/Causal Methods Spring 2026/Sessions/Special projects/<conference-slug>/` and uses:

```
<conference-slug>/
├── README.md          # Deliverable index + scientific invariants
├── materials/         # Source seed: abstract, acceptance letter, templates
├── figures/           # PRIMARY — stand-alone .svg + 300dpi .png rasters
├── dashboard/         # PRIMARY — single-file index.html (React/CDN)
│   ├── index.html
│   └── README.md
└── poster/            # EXAMPLE — PPTX assembly that consumes figures + text
    ├── <conf>_poster.pptx
    ├── CONTENT_MAP.md
    └── tour_script.txt
```

The `figures/` and `dashboard/` folders are what get reviewed, republished, and reused. The `poster/` folder is an illustration: a one-off PPTX assembly that shows how the figures land on a physical print. If the scripted assembly misfires, ship the figures and dashboard and build the PPTX by hand.

## 2. Primacy of figures

Figures are the unit of reuse across the dashboard, the poster, future talks, and papers. Treat them as independent artifacts:

- Hand-authored `.svg` with explicit `width="Nin" height="Min"` on the root `<svg>` so PPTX import respects print dimensions
- No external CSS, no web fonts: keep text in `<text>` with `font-family="Arial, sans-serif"` so rendering is identical across PPTX, browser, and PDF
- Inline `<defs>` for arrow markers etc., no external sprite sheet
- Companion 300-dpi PNG raster for PPTX embedding: `rsvg-convert -d 300 -p 300 fig.svg > fig.png`
- One figure per file, one narrative job per figure
- Palette hex values live in the figure, not in a theme file — figures must render correctly as standalone files

Reference implementations:
- `ispor-2026-causal-discovery/figures/fig_haprI_dag.svg` — 10"×10" DAG with legend, multiple arrow-marker defs, time axis
- `ispor-2026-causal-discovery/figures/fig_equivalence_class.svg` — 6"×4" three-panel schematic
- `ispor-2026-causal-discovery/figures/fig_hero_flatten_vs_object.svg` — 24"×12" paired-panel hero

## 3. Interactive HTML companion pattern

Single-file `dashboard/index.html`. CDN-only; no build step; open directly in a browser to preview.

**Dependencies (CDN-loaded in `<head>` / before the `<script type="text/babel">` block):**

- React 18 + ReactDOM 18 (`unpkg.com/react@18/umd/react.production.min.js`)
- Recharts 2.15 (`unpkg.com/recharts@2.15.0/umd/Recharts.js`)
- KaTeX 0.16 CSS + JS (`cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.*`)
- Babel standalone (`unpkg.com/@babel/standalone/babel.min.js`)
- Google Fonts: Playfair Display (headings), Source Sans 3 (body)

**Component library** — lift verbatim from `Sessions/Week 13/Session 13a/dice-pricefactuals-visualization.html` or the ACIC dashboard:

- `Tex({math, display})` — KaTeX wrapper using `useEffect` + `katex.render`
- `MathBlock({children})` — inset equation box
- `SectionNav({sections, active, onSelect})` — tab chooser with numbered badges
- `PrevNextNav({active, total, onSelect})` — footer step nav
- `GlassCard({children, style})` — frosted-white card
- `InsightBox({children, label, color})` — accent-border callout; **vary the label** across tabs (Observe / Consider / Takeaway / Caveat), don't repeat "Key Insight"
- `SliderControl({label, value, min, max, step, onChange, color, unit, format})` — labeled range input
- `MetricCard({label, value, sub, color})` — headline number card
- `SectionTitle({children, kicker})` / `Para({children})` — typography primitives
- `hexAlpha(hex, a)` helper for gradient backgrounds

**Layout chrome:**

- Header: dark gradient background (`linear-gradient(135deg, #1a202c 0%, #2d3748 100%)` or conference-palette variant) with conference kicker, Playfair title, byline
- Main: single-column, centered, `max-width` per project (see overrides below)
- Footer: centered small muted text with contact line and "illustrative values badged" reminder

**Tab discipline:**

- ≤ 5 tabs total. MVP tabs are must-ship; stretch tabs ship only if MVP fits the build budget
- Tab 1 IS the punchline — what a 30-second scan should take away. Not an overview, not a title slide
- Every unsourced number carries an "illustrative" badge (small pill, accent color, top-right of chart card or beside slider label)
- Use external figure files via `<img src="./figures/fig_*.svg">` rather than inlining SVG markup into JSX (keeps figures as independent artifacts)

## 4. Poster-as-example

PPTX assembly at 56"×36" or similar conference-size canvas is fragile. Scripted assembly via `python-pptx` / `lxml` works but is often tripped by font coercion, canvas-resize stretch, or master-theme leakage. Budget for it generously and do not let poster assembly block the dashboard.

When building the PPTX:
- Insert rasterized (300-dpi PNG) versions of the figures, not the SVGs directly (Office SVG support varies)
- Use the conference's own template (Boise State Better Poster, ISPOR template, etc.) as the starting file; resize the canvas only via `ppt/presentation.xml` `<p:sldSz>` and re-author shape coordinates fresh (do not scale-multiply — it stretches embedded images)
- Keep all text in the template's default font; enumerate every `<a:rPr>` and explicitly set `typeface` so mixed-font artifacts don't slip in
- Verify dimensions in LibreOffice (`Format → Slide properties`) before exporting PDF

If the scripted assembly produces something that fails an eye-check at full scale, hand-assemble from the figures. The figures are the canonical representation of the science; the PPTX is a convenience.

## 5. Publishing flow

Source edits live in the Box project folder. Publishing happens in the GitHub repo:

1. Finish the dashboard in `Box/.../<conference-slug>/dashboard/index.html`; smoke-test locally with `python -m http.server 8000`
2. Create `~/Documents/GitHub/conference-materials/<slug>/figures/` (use a URL-safe slug — lowercase, hyphens, no spaces)
3. `cp` the dashboard `index.html` into the new `<slug>/` folder
4. `cp` the SVG figures into the new `<slug>/figures/` folder (PNGs are for the poster; don't publish them)
5. Add a `.card` entry to `conference-materials/index.html` under the `<section>` with `<h2>Current</h2>`; put the most recent conference first. Copy the ACIC card as the template — all fields (`.card-kicker`, `.card-title`, `.card-sub`, `.card-meta`) are positional
6. Commit with a one-line imperative message matching existing repo style, push. GitHub Pages deploy takes ≤ 1 minute
7. Verify the live URL in Chrome + Safari before generating the QR code

The live dashboard URL is `https://andystats.github.io/conference-materials/<slug>/`. The QR on the printed poster points at this URL.

## 6. Scientific-integrity invariants (default; override per project in the project README)

- **"Illustrative" badge** on every unsourced number. Prefer no number to an unsourced number.
- **Hypothesis-generating verbs only** for surfaced/flagged findings: *candidate, prioritized, surfaced, flagged, rediscovered, consistent with*. Forbidden: *caused, proved, established, demonstrated, ruled out confounding*.
- **Commercial neutrality:** third-party tools appear in the byline and in one neutral methods line; do not name products in body copy; do not use the word "platform" in acknowledgments.
- **Accent colors** are reserved for emphasis (e.g., two headline words, one outcome node). Do not decorate with them.
- **Red is avoided on posters** (ISPOR and many venues discourage it, also colorblindness-friendly). Express danger/outcome semantics via shape and stroke weight.

When a project inherits a brand palette (Boise State, Utah, etc.), distinguish brand-emphasis (two accent words, one node) from brand-decoration (don't).

## 7. Per-project overrides

Each new conference project sets these knobs in its own README; this skill ships defaults only:

| Knob | Default | Examples of override |
|---|---|---|
| Dashboard `max-width` | 920 px | 1100 px for ISPOR 2026 |
| Palette (`COLORS` object) | tao-rwd | Boise State (ISPOR), ACIC neutrals |
| Print canvas | 42"×40" landscape | 56"×36" (ISPOR), 48"×36" (ACIC) |
| MVP tab count | 3 | 3 for ISPOR, 7 for ACIC (longer-form) |
| Forbidden-word list | inherited from §6 | project-specific additions (e.g., no "19.6%") |
| QR URL | `andystats.github.io/conference-materials/<slug>/` | custom domains optional |

## 8. Reference implementations

- **ACIC 2026 (Causal SHAP)** — `Box/.../acic-2026-causal-shap/` and `github.com/andystats/conference-materials/acic-2026-causal-shap/`. 7 tabs, 920 px, tao-rwd-adjacent palette.
- **ISPOR 2026 (HAPrI)** — `Box/.../ispor-2026-causal-discovery/` and `github.com/andystats/conference-materials/ispor-2026-haprI/`. 3 MVP + 2 stretch tabs, 1100 px, Boise State palette, strict hedging invariants.
- **Session 13a (course)** — `Box/.../Sessions/Week 13/Session 13a/dice-pricefactuals-visualization.html`. Most evolved single-file companion; source of the component library.

## 9. Non-goals

- This skill does not generate the figures themselves; figures are hand-authored. The skill just enforces standards once they exist.
- The skill does not own QR code generation; QR happens after the live URL resolves (use any qrencode tool with the URL, ECC-H, high-res square).
- The skill does not own voice-checking with co-authors; that's a project-specific step that belongs in the project README checklist.
