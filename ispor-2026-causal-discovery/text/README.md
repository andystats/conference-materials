# Text

Markdown fragments for the ISPOR 2026 MSR72 poster + companion site.

## Current contents

### Poster planning memos (internal)

- `poster-key.md` — Poster strategy spine. Read this first when deciding what to pull into the webpage or single printed poster.
- `poster-key-concepts.md` — Math, concepts, and references. Source for methods copy, citations, and equations (Markov factorization, Noisy-OR/ICI, relative-time alignment, target-trial → TMLE handoff).

### Methodology briefs

- `cpdag-principle.md` — Why flat-table causal discovery returns an equivalence class (CPDAG); how temporal / relational constraints orient edges.
- `scenarios-overview.md` — Framing for the four RWE scenarios where flat tables stall and object-analytic engines settle the orientation.
- `scenario-1-sepsis.md` — Sepsis → antibiotic → mortality (ICU 3-hour bundle).
- `scenario-2-therapy-switch.md` — Drug switch & adverse event (pharmacovigilance).
- `scenario-3-disease-progression.md` — T2D → HTN → CKD progression (payer trajectory).
- `scenario-4-cancer-lifecourse.md` — Breast-cancer life-course ordering (Xplain canonical).

The scenario briefs feed the four-tab RWE Scenarios gallery in `../index.html`; the poster memos guide figure choices + one-sentence claim language across the webpage and the printed poster.

## Filename convention

`<section>.md` — e.g. `headline.md`, `abstract.md`, `column-left.md`, `fig-hero-caption.md`.
