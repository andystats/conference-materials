# Poster key from ObjectAnalytics + MIMIC lecture deck

Working frame: the ISPOR abstract is about object-centric causal discovery in
MIMIC-IV for hospital-acquired pressure injury (HAPrI). The poster should make
one disciplined claim: preserving patient objects, event timestamps, and
relational structure lets the discovery engine prioritize clinically plausible
candidate causes that a flat table obscures. Hypoalbuminemia is the featured
candidate upstream driver, not a confirmed causal effect.

## Recommended poster spine

1. Problem: flat EHR extracts collapse clinical time and relationships.
   Classic structure-learning algorithms can recover dependencies, but with a
   flat cross-sectional table they often return a partially oriented equivalence
   class and leave clinically distinct stories unresolved.

2. Representation: patients are objects with time-stamped sub-objects.
   Admissions, diagnoses, medications, procedures, labs, microbiology, and
   transfers stay connected to the patient and to each other. Timestamps become
   hard orientation constraints rather than just more covariates.

3. Case study: HAPrI in MIMIC-IV.
   The deck's strongest concrete evidence is the pressure-ulcer sequence:
   low albumin appears before pressure-ulcer diagnosis, remains low afterwards,
   and sits near the target in the discovered factor graph with known risk
   factors such as immobility, moisture, hemodynamic instability, and mechanical
   ventilation.

4. Algorithmic move: search millions of object-tree projections without
   materializing a massive flat table.
   The deck frames the engine as iterating through direct factors, residuals,
   pruning, second-level effects, and finally a time-ordered graph.

5. Inference handoff: discovery prioritizes edges for confirmatory analysis.
   The poster should end with target-trial emulation and TMLE / longitudinal
   g-methods as the next step for effect estimation.

## What to pull from the deck

Primary pull-through:

- `../figures/objectanalytics-mimic-key-images/key-crops/fig-04-albumin-relative-time.png`
  Use as the basis for a clean "albumin relative to HAPrI diagnosis" chart.
  This is the most poster-relevant slide-derived figure.

- `../figures/objectanalytics-mimic-key-images/key-crops/fig-05-relative-time-axis.png`
  Redraw as the methods hinge: features are built from t < 0, the target is at
  t = 0, and post-zero information is excluded to prevent leakage.

- `../figures/objectanalytics-mimic-key-images/key-crops/fig-03-pressure-ulcer-discovery-graph.png`
  Use as graph-content source. Redraw the graph as a simplified HAPrI DAG with
  hypoalbuminemia highlighted in orange and known risk factors in navy/gray.

- `../figures/objectanalytics-mimic-key-images/key-crops/fig-09-time-ordered-graph-build.png`
  Use for a compressed methods pipeline: object search -> direct factors ->
  indirect factors -> time-ordered graph -> confirmatory estimand.

Secondary pull-through:

- `../figures/objectanalytics-mimic-key-images/key-crops/fig-07-noisy-or-ici-model.png`
  Useful as a math inset or webpage supplement. On the printed poster, use only
  the equation `P(Y=1|X=x)=1-\prod_i(1-c_i x_i)`.

- `../figures/objectanalytics-mimic-key-images/key-crops/fig-10-flat-dag-vs-object-analytics.png`
  Supports the flat-table contrast, but the existing repo hero figure is cleaner:
  `../figures/fig_hero_flatten_vs_object.svg`.

- `../figures/objectanalytics-mimic-key-images/key-crops/fig-01-patient-object-map.png`
  Good conceptual source, but redraw without third-party motifs.

Avoid direct use:

- Slide 04 Gartner hype cycle, slide 02 YouTube screenshot, slide 18 wound
  photographs, slide 33 shadow artwork, and raw product screenshots unless
  rights and publication provenance are confirmed.

## Better illustrative figures to make

1. Hero: "Flat table vs patient object."
   Start from `../figures/fig_hero_flatten_vs_object.svg`. Add a tiny HAPrI
   case tag so the figure is not generic: flat columns on one side; patient root
   with dated labs, diagnoses, ventilation, pressure injury, and transfers on
   the other.

2. Main result: "Hypoalbuminemia prioritized upstream of HAPrI."
   Build a simplified graph with HAPrI as the outcome, hypoalbuminemia as the
   highlighted candidate, and known rediscovered risks grouped around it. Mark
   any unconfirmed or clinician-review edges as dashed.

3. Methods: "Relative-time guardrail."
   One clean axis: negative-time window for candidate features, vertical day 0
   for HAPrI diagnosis, post-zero region grayed out. Caption: "Only pre-index
   information enters discovery."

4. Algorithm: "Discovery to inference handoff."
   Four blocks: object representation -> constrained discovery -> clinician
   review -> target-trial/TMLE estimation. This is the bridge between the deck
   and the ISPOR abstract.

5. Webpage-only: "Noisy-OR contribution model."
   Put the ICI/Noisy-OR derivation on the companion webpage, not the single
   poster, unless the poster has a methods sidebar.

## Suggested single-poster layout

Top band:
- Title and one-sentence claim.
- Hero flat-table vs patient-object figure.
- Mini abstract: "Object-centric causal discovery preserves clinical time and
  relational structure while screening candidate HAPrI drivers in MIMIC-IV."

Middle band:
- Left: why flat methods stall, with CPDAG/equivalence-class visual.
- Center: object representation and relative-time guardrail.
- Right: HAPrI discovered graph with hypoalbuminemia highlighted.

Bottom band:
- Albumin relative-time chart.
- Discovery -> inference pipeline.
- Caveat / next step: candidate edge, clinician review, target-trial emulation,
  TMLE / longitudinal g-methods.

## Copy snippets worth reusing

- "Timestamps are hard constraints, not just additional features."
- "A flattened EHR asks the algorithm to infer time after we have thrown time
  away."
- "The discovery graph is a prioritization device: it surfaces edges worth
  confirmatory causal inference."
- "Hypoalbuminemia is a candidate upstream driver of HAPrI pending target-trial
  emulation and TMLE."
- "Known HAPrI risks were rediscovered without manual feature engineering,
  supporting clinical plausibility."

## Tight caveats

- Do not state that albumin management prevents HAPrI unless confirmatory
  analysis estimates that effect.
- Do not overclaim unique DAG identification. Safer wording: "temporal and
  relational constraints orient many otherwise ambiguous edges."
- Keep MIMIC-IV versioning explicit. The current abstract/page says MIMIC-IV
  v3.1; the deck includes older/general MIMIC counts.
- Treat slide screenshots as internal references. Public poster figures should
  be redrawn in repo-native SVG/PowerPoint.

