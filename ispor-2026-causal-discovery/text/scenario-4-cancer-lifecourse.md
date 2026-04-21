# Scenario 4 — Breast-cancer risk: life-course ordering

**Section heading:** Separating policy levers from fixed risk.

**The question.** Family history, age at menarche, parity, and hormone-replacement therapy (HRT) all associate with breast-cancer (BC) diagnosis. Which of those is a *modifiable* risk factor worth a clinical guideline, and which are fixed features of biology?

**On a flat table.** Each woman contributes one row with `family_hx`, `menarche` (age), `parity`, `HRT`, and `BC` (outcome). Classic discovery returns a dense, largely undirected CPDAG. Many DAGs fit. Without a way to encode *when* each variable was set, the algorithm cannot tell an immutable trait (family history, determined at conception) from a policy-lever decision (HRT, initiated decades later).

**On an object-centric representation.** The patient is the root object. Life-course events carry dates:

- **Family history** — immutable, effective at birth.
- **Menarche** — a developmental event, age 12 for patient 4012.
- **First birth** (parity) — age 28.
- **HRT start** — age 48.
- **BC diagnosis** — age 52.

The object engine carries two constraints the flat table destroys. **Temporal precedence**: an event at age 48 cannot cause an event at age 12. **Immutability-at-birth**: family history is a source node; no downstream event can point into it. Together these rules orient the entire life-course DAG.

**What this buys.** Only HRT is a modifiable late event in the chain. The other edges point outward from genetic and developmental nodes — they cannot absorb credit that belongs to the one lever a clinician can actually pull. The flat-table causal claim that "HRT doubles BC risk" becomes an identifiable candidate effect for TMLE once the DAG is oriented.

**Why it matters for RWE.** Xplain Data's canonical cancer-risk demonstration uses exactly this life-course object model. The point is not that the algorithm "discovers" HRT — everyone knows it correlates with BC — but that it produces a DAG in which the HRT → BC effect is *identifiable*, separable from the fixed-at-birth genetic background, and therefore targetable by a downstream causal estimator.
