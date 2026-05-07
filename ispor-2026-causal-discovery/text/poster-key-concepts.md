# Poster key concepts, math, and wording

This note supports the poster storyboard in `poster-key.md`. It translates the
ISPOR abstract and the ObjectAnalytics/MIMIC deck into poster-safe technical
claims.

High-level message:

> Object-centric causal discovery turns clinical time and relational EHR
> structure into search constraints, then hands candidate edges to confirmatory
> causal estimators.

## Concept map

The poster needs four conceptual layers:

1. Why flat-table discovery stalls:
   observational data often identify an equivalence class of DAGs, represented
   by a CPDAG, not a unique oriented graph.

2. What object analytics preserves:
   the patient object, event families, parent-child relationships, and event
   timestamps.

3. What temporality contributes:
   temporal precedence rules out backwards event edges and defines the
   pre-index feature window.

4. What discovery does next:
   the algorithm prioritizes plausible candidate edges; target-trial emulation,
   TMLE, and longitudinal g-methods estimate effects after design and clinician
   review.

## 1. Flat-table causal discovery and CPDAGs

Classical causal discovery uses conditional-independence information plus
assumptions such as the causal Markov condition, faithfulness, and causal
sufficiency. For variables `V_1, ..., V_p` and a DAG `G`, the Markov
factorization is:

```math
P(V_1,\ldots,V_p) = \prod_{j=1}^p P(V_j \mid Pa_G(V_j)).
```

With observational data alone, multiple DAGs can imply the same conditional
independencies. Two DAGs are Markov-equivalent when they have the same skeleton
and the same unshielded colliders (v-structures). A CPDAG represents the
equivalence class: directed edges are invariant across the class; undirected
edges are not oriented by the independence evidence alone.

Poster translation:

> A CPDAG is not a failed DAG. It is the honest graph when the data do not
> distinguish clinically different arrow directions.

Simple poster example:

```text
X -> Y -> Z
X <- Y -> Z
X <- Y <- Z
```

These have the same skeleton and no unshielded collider, so a flat
cross-sectional representation cannot orient the chain from conditional
independencies alone.

Intuitive takeaway:

> Flat tables make different clinical stories look empirically identical.

## 2. Object-centric EHR representation

Flat extract:

```text
patient_id | ever_low_albumin | ever_ventilated | ever_pressure_injury | ...
```

Object representation:

```text
Patient
  Admissions(hadm_id, admit_time, discharge_time)
  Diagnoses(code, diagnosis_time or index relation)
  Labs(item, value, chart_time)
  Medications(drug, start_time, stop_time)
  Procedures(code, start_time, stop_time)
  Microbiology(organism, specimen_time)
  Transfers(care_unit, in_time, out_time)
```

The key distinction is not storage format. The key distinction is that clinical
events retain:

- the patient/admission object they belong to,
- the event family they come from,
- the timestamp or interval when they occurred,
- the relational context needed to define joins and aggregations.

Poster translation:

> Object analytics keeps the patient journey intact instead of collapsing it
> into one row.

Intuitive takeaway:

> Timestamps are not just columns. They are constraints on what could have
> caused what.

## 3. Temporal precedence and relative time

If event `A` occurs after event `B`, then `A -> B` is inadmissible in a clinical
event graph:

```math
t(A) > t(B) \Rightarrow A \not\to B.
```

For a target/index event at `t = 0`, candidate explanatory features should be
built only from the pre-index window:

```math
X_i = f_i(\{E: t(E) < 0\}), \qquad
Y = I(\text{HAPrI at } t=0).
```

The deck frames this through a relative-time axis:

```math
\tau = t_{\text{event}} - t_{\text{HAPrI diagnosis}}.
```

Interpretation:

- `tau < 0`: candidate causes, pre-outcome confounders, early warning states.
- `tau = 0`: index HAPrI diagnosis.
- `tau > 0`: downstream effects, follow-up care, or leakage if included in
  discovery/prediction.

Poster translation:

> Only pre-index information enters discovery. The post-index region is
> clinically interesting, but it is not allowed to explain the target.

Intuitive takeaway:

> The same lab value has a different causal role before and after diagnosis.

Technical caveat:

Temporal precedence helps orient candidate event edges. It does not remove
confounding, prove intervention effects, or guarantee that every graph edge is
uniquely identified.

## 4. Healthcare confounding and comprehensive patient context

The deck's healthcare challenge is that "everything is correlated to
everything." In ICU EHR data, many variables are severity markers, downstream
responses, shared-cause proxies, or measurement-process artifacts. A narrow flat
extract risks both:

- missing relevant confounders because they live in another table or event
  family, and
- creating spurious associations because the timing of measurement and care is
  collapsed.

Poster translation:

> Causal discovery in healthcare needs more context, not just more rows.

Intuitive takeaway:

> The confounder you need may be a dated procedure, a lab trend, a medication
> interval, a transfer, or a missingness pattern.

## 5. Discovery search over object-tree projections

The deck describes an algorithmic workflow:

1. Start with an initial target model.
2. Compute residuals for millions of variables built as projections and
   aggregations along the patient object tree.
3. Select the next best variables.
4. Apply marginal pruning, pairwise pruning, and model-based stepwise pruning.
5. Identify direct factors timewise prior to target.
6. Restart search to identify second- and higher-level factors.
7. Build a graph using time information and variable selection among prior
   nodes.

Poster translation:

> The computational problem shifts from testing many edge orientations in a
> flat graph to searching many clinically meaningful, time-compatible object
> projections.

Intuitive takeaway:

> Time makes the final graph more constrained; the hard part is searching the
> enormous object-derived feature space.

Poster-safe algorithm wording:

- "searched millions of object-tree projections"
- "used temporal precedence and relational structure to constrain candidate
  parents"
- "prioritized a sparse candidate graph"
- "screened candidate dependencies without materializing a massive flat table"

Avoid overclaiming:

- Do not say the graph is automatically the true causal DAG.
- Do not say time makes causal discovery trivial.
- Do not say confounding is solved.

## 6. Independent causal influence / Noisy-OR contribution

The deck uses an independent-causal-influence or Noisy-OR model to interpret
factor contributions in a high-dimensional binary feature space.

Let `X_i` be binary candidate factors and `H_i` hidden binary triggers. If a
factor is present:

```math
P(H_i=1 \mid X_i=1) = c_i, \qquad
P(H_i=1 \mid X_i=0) = 0.
```

The target is triggered if any hidden trigger is active:

```math
Y = 1 \quad \text{if any } H_i = 1.
```

Assuming hidden triggers are conditionally independent:

```math
P(Y=0 \mid X=x) = \prod_i P(H_i=0 \mid X_i=x_i)
```

and therefore:

```math
P(Y=1 \mid X=x) = 1 - \prod_i (1 - c_i x_i).
```

When each `c_i` is small:

```math
P(Y=1 \mid X=x) \approx \sum_{i:x_i=1} c_i.
```

Poster translation:

> For small per-factor contributions, the model behaves approximately
> additively, making a ranked list of candidate contributors interpretable.

Wording guardrail:

In the poster, "contribution" should mean algorithmic contribution within the
discovery model. It should not be described as a confirmed average causal effect
unless confirmed by a separate target-trial/TMLE or longitudinal analysis.

## 7. Correlation versus causal contribution

The deck distinguishes raw association from causal contribution. A factor can
be highly associated with the target because it is:

- a cause,
- a severity marker,
- a downstream response,
- a shared-cause proxy,
- a measurement artifact,
- or a post-index leakage feature.

Poster contrast:

```text
association:
  P(Y=1 | X_i=1) - P(Y=1 | X_i=0)

discovery contribution:
  pre-index, time-compatible, pruned contribution after competing explanations
  are considered
```

Poster translation:

> Association asks "what co-occurs with HAPrI?" Object-centric discovery asks
> "what occurs early enough, in the right patient context, to be worth testing?"

Intuitive takeaway:

> Not every strong signal is upstream.

## 8. HAPrI case-study interpretation

Publication-safe result statement:

> In MIMIC-IV v3.1 adult ICU admissions, object-centric causal discovery
> prioritized hypoalbuminemia as a candidate upstream driver of HAPrI, pending
> clinician review and confirmatory target-trial/TMLE analysis.

Supporting clinical-plausibility statement:

> The algorithm also rediscovered known HAPrI risks, including mechanical
> ventilation, hemodynamic instability, immobility, moisture exposure, and yeast
> colonization, without manual feature engineering.

Albumin trajectory statement:

> Albumin values aligned to HAPrI diagnosis drop before the index event and
> remain low afterwards. The pre-index pattern motivates candidate upstream
> status; the post-index pattern is follow-up/downstream information and is not
> used to explain the target.

Interpretive caveat:

Hypoalbuminemia may be:

- an upstream modifiable driver,
- a marker of critical illness or nutritional/inflammatory burden,
- a mediator on another causal path,
- or a proxy for care processes and measurement intensity.

The poster should frame albumin as a prioritized hypothesis, not as an
intervention recommendation.

## 9. Discovery-to-inference handoff

Discovery output should define candidate estimands. For hypoalbuminemia or an
albumin-management protocol, a confirmatory estimand might be:

```math
\psi = E[Y^{a=1} - Y^{a=0}]
```

or, for a dynamic longitudinal treatment strategy:

```math
\psi(d) = E[Y^{d}].
```

Target-trial protocol elements to name:

- eligibility criteria,
- time zero,
- treatment strategies or dynamic regimes,
- grace period,
- follow-up,
- outcome definition,
- baseline and time-varying confounders,
- censoring and competing events.

TMLE / longitudinal g-methods role:

> Estimate the prespecified effect after the target trial has been emulated.

Poster translation:

> Discovery chooses the question; causal inference answers it.

## 10. Poster-safe concept language

Use:

- "candidate upstream driver"
- "prioritized for confirmatory analysis"
- "rediscovered established risk factors"
- "temporal and relational constraints orient many edges"
- "pre-index features"
- "relative-time guardrail"
- "hypothesis-generating"
- "clinician review and target-trial emulation are required next steps"

Use carefully:

- "causal contribution" - define as model contribution, not final effect.
- "oriented graph" - qualify as candidate/sparse/discovery graph.
- "direct effect" - use only in the context of the discovery algorithm, not as
  a formal causal estimand unless separately identified.

Avoid:

- "proved cause"
- "confirmed causal effect"
- "albumin management prevents HAPrI"
- "temporal constraints solve confounding"
- "the true DAG"
- "fully identified all causal relationships"

## Compact poster equations

CPDAG / Markov equivalence:

```text
same skeleton + same unshielded colliders => same CPDAG
```

Temporal exclusion:

```math
t(A) > t(B) \Rightarrow A \not\to B
```

Relative time:

```math
\tau = t_{\text{event}} - t_{\text{HAPrI diagnosis}}
```

Pre-index features:

```math
X_i = f_i(\{E: \tau(E) < 0\})
```

Noisy-OR:

```math
P(Y=1 \mid X=x) = 1 - \prod_i (1 - c_i x_i)
```

Confirmatory estimand:

```math
\psi(d) = E[Y^d]
```

## References

- Johnson A, Bulgarelli L, Pollard T, Gow B, Moody B, Horng S, Celi LA, Mark R.
  MIMIC-IV version 3.1. PhysioNet. 2024.
  https://physionet.org/content/mimiciv/3.1/

- Johnson AEW, Bulgarelli L, Shen L, et al. MIMIC-IV, a freely accessible
  electronic health record dataset. Scientific Data. 2023;10:1.
  https://www.nature.com/articles/s41597-022-01899-x

- Spirtes P, Glymour C, Scheines R. Causation, Prediction, and Search. MIT
  Press, 2001 edition.
  https://mitpress.mit.edu/9780262527927/causation-prediction-and-search/

- Verma T, Pearl J. Equivalence and synthesis of causal models. UAI 1990.
  https://dblp.org/rec/conf/uai/VermaP90

- Chickering DM. Optimal structure identification with greedy search. Journal of
  Machine Learning Research. 2002;3:507-554.
  https://www.jmlr.org/papers/v3/chickering02b.html

- Shimizu S, Hoyer PO, Hyvarinen A, Kerminen A. A linear non-Gaussian acyclic
  model for causal discovery. Journal of Machine Learning Research.
  2006;7:2003-2030.
  https://www.jmlr.org/papers/v7/shimizu06a.html

- Zheng X, Aragam B, Ravikumar PK, Xing EP. DAGs with NO TEARS: continuous
  optimization for structure learning. NeurIPS 2018.
  https://papers.nips.cc/paper/8157-dags-with-no-tears-continuous-optimization-for-structure-learning

- Maier M, Marazopoulou K, Arbour D, Jensen D. A sound and complete algorithm
  for learning causal models from relational data. UAI 2013.
  https://arxiv.org/abs/1309.6843

- Hernan MA, Robins JM. Using big data to emulate a target trial when a
  randomized trial is not available. American Journal of Epidemiology.
  2016;183(8):758-764.
  https://academic.oup.com/aje/article-abstract/183/8/758/1739860

- van der Laan MJ, Rubin D. Targeted maximum likelihood learning. International
  Journal of Biostatistics. 2006;2(1).
  https://www.degruyterbrill.com/document/doi/10.2202/1557-4679.1043

- Kirkland-Walsh H, Teleten O, Wilson M, et al. Pressure injuries in critical
  care patients in US hospitals: results of the International Pressure Ulcer
  Prevalence Survey. Critical Care Nurse. 2022.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9200225/

- Anthony D, Reynolds T, Russell L. An evaluation of serum albumin and the
  sub-scores of the Waterlow score in pressure ulcer risk assessment. Journal of
  Tissue Viability. 2011.
  https://pubmed.ncbi.nlm.nih.gov/21665474/
