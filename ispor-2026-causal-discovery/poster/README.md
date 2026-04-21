# Poster (48" × 36" landscape)

Single printed poster for ISPOR 2026 MSR72.

## Build

```bash
# From this directory
python build_poster.py
```

Produces `ISPOR_2026_MSR72_poster_draft_vNN.pptx` — a single 48×36 landscape slide assembled from the figures in `../figures/`.

Rasterized PNGs used as intermediate image assets are cached in `png_cache/`.

## Workflow

1. Edit a figure upstream: `../figures/fig_*.drawio` → **File → Export As → SVG** over the matching `fig_*.svg`.
2. Regenerate the PNG cache:
   ```bash
   python -c "
   from svglib.svglib import svg2rlg
   from reportlab.graphics import renderPM
   import os
   for s in sorted(os.listdir('../figures')):
       if not s.endswith('.svg'): continue
       name = os.path.splitext(s)[0]
       renderPM.drawToFile(svg2rlg('../figures/' + s), 'png_cache/' + name + '.png', fmt='PNG', dpi=300)
   "
   ```
3. Rebuild the PPTX:
   ```bash
   python build_poster.py
   ```
4. Open the PPTX in PowerPoint for final visual QA and tweaks (the script lays out shapes geometrically; PowerPoint is where you hand-polish alignment, kerning, and last-minute copy edits).

## Git

The generated `.pptx` and `png_cache/` are gitignored (large binaries, derived artifacts). Only `build_poster.py` and this README are tracked. Re-run the build to regenerate locally.

## Layout (v0.1)

- **Title band** (navy): conference meta + title + one-sentence claim + ISPOR logo
- **Authors + logos** (Alderden / Haft / Wilson)
- **Mini-abstract** (orange ribbon)
- **Middle band, three columns**: Why flat stalls · Object rep + τ-guardrail · HAPrI finding (each with figure + takeaway)
- **Result band**: albumin relative-time chart (left) · headline numbers 5/3/TMLE (center) · Noisy-OR methods + caveat (right stack)
- **Pipeline band**: 4 inline blocks — Object rep → Constrained discovery → Clinician review → Target trial / TMLE
- **Footer**: references + contact
