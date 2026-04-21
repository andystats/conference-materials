# Poster key concepts and math

This note pulls the deck's math into a poster-ready conceptual framework. The
high-level message is: object-centric causal discovery turns clinical time and
relational structure into search constraints, then hands candidate edges to
confirmatory causal estimators.

## Core concepts

### Object-centric EHR representation

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

The key distinction is not storage format. It is that events retain their parent
object and timestamp. This lets the algorithm forbid orientations that violate
clinical time.

### DAG factorization

For variables `V_1, ..., V_p` and a DAG `G`, the Markov factorization is:

```math
P(V_1,\ldots,V_p) = \prod_{j=1}^p P(V_j \mid Pa_G(V_j)).
```

Classical causal discovery uses conditional-independence patterns plus
assumptions such as the causal Markov condition, faithfulness, and causal
sufficiency to recover structure.

### Markov equivalence

With observational data alone, multiple DAGs can imply the same conditional
independencies. Two DAGs are Markov-equivalent when they have the same skeleton
and the same unshielded colliders (v-structures). A CPDAG represents the whole
equivalence class: directed edges are invariant across the class; undirected
edges are not oriented by the independence information alone.

Poster wording:

> Flat-table discovery often returns an equivalence class; time-stamped objects
> add constraints that orient otherwise ambiguous edges.

### Temporal constraints

If event `A` occurs after event `B`, then `A -> B` is inadmissible for the
clinical event graph:

```math
t(A) > t(B) \Rightarrow A \not\to B.
```

For an index event at `t = 0`, candidate explanatory features should be built
only from the pre-index window:

```math
X_i = f_i(\{E: t(E) < 0\}), \qquad Y = I(\text{HAPrI at } t=0).
```

This is both a causal-orientation constraint and a leakage guardrail.

### Relative-time alignment

The deck aligns each patient to the target diagnosis:

```math
\tau = t_{\text{event}} - t_{\text{HAPrI diagnosis}}.
```

Features with `\tau < 0` can be candidate causes or pre-outcome confounders.
Features with `\tau > 0` are downstream effects, follow-up care, or leakage if
included in prediction/discovery.

### Independent causal influence / Noisy-OR model

Slide 25 uses an independent-causal-influence model. Let `X_i` be binary
candidate factors and `H_i` hidden binary triggers. If the factor is present:

```math
P(H_i=1 \mid X_i=1) = c_i, \qquad P(H_i=1 \mid X_i=0) = 0.
```

The target is triggered if any hidden trigger is active:

```math
Y = 1 \quad \text{if any } H_i = 1.
```

Assuming the hidden triggers are conditionally independent:

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

Poster interpretation: the `c_i` values act like additive contributions for
prevalent binary factors, which makes the model interpretable in high-dimensional
object-derived feature spaces.

### Correlation versus causal contribution

The deck distinguishes raw target probability from causal contribution. A factor
may be strongly associated with the target because it is downstream, a severity
marker, or a shared-cause proxy. The object-centric search tries to separate:

```text
association:        P(Y=1 | X_i=1) - P(Y=1 | X_i=0)
causal contribution: pre-index, time-compatible, pruned contribution after
                     competing explanations are considered
```

Use "causal contribution" carefully on the poster: in this draft it means
algorithmic contribution within the discovery model, not a finalized causal
effect estimate.

### Discovery-to-inference handoff

Discovery output should define candidate estimands. For hypoalbuminemia, a
confirmatory estimand might be an average causal effect under a target-trial
protocol:

```math
\psi = E[Y^{a=1} - Y^{a=0}]
```

or under dynamic longitudinal regimes:

```math
\psi(d) = E[Y^{d}]
```

where `d` is an albumin-management or nutrition/volume-management rule. TMLE or
longitudinal g-methods can estimate these effects after the target trial,
eligibility criteria, time zero, treatment strategies, follow-up, outcome,
confounders, and censoring rules are specified.

## Poster-safe concept language

- "candidate upstream driver" rather than "cause"
- "prioritized for confirmatory analysis" rather than "proved"
- "temporal and relational constraints orient many edges" rather than "solve
  causal discovery"
- "only pre-index information enters discovery" rather than "the algorithm knows
  causality"
- "clinician review and target-trial emulation are required next steps"

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

- van der Laan MJ, Rubin D. Targeted maximum likelihood learning. International
  Journal of Biostatistics. 2006;2(1).
  https://www.degruyterbrill.com/document/doi/10.2202/1557-4679.1043

- Hernan MA, Robins JM. Using big data to emulate a target trial when a
  randomized trial is not available. American Journal of Epidemiology.
  2016;183(8):758-764.
  https://academic.oup.com/aje/article-abstract/183/8/758/1739860

- Kirkland-Walsh H, Teleten O, Wilson M, et al. Pressure injuries in critical
  care patients in US hospitals: results of the International Pressure Ulcer
  Prevalence Survey. Critical Care Nurse. 2022.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9200225/

- Anthony D, Reynolds T, Russell L. An evaluation of serum albumin and the
  sub-scores of the Waterlow score in pressure ulcer risk assessment. Journal of
  Tissue Viability. 2011.
  https://pubmed.ncbi.nlm.nih.gov/21665474/

