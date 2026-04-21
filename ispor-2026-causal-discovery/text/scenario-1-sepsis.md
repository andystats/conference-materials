# Scenario 1 — Sepsis → antibiotic → mortality

**Section heading:** The 3-hour-bundle question.

**The question.** Are early broad-spectrum antibiotics a *mediator* that protects septic patients from death, or a *marker of severity* handed out preferentially to the sickest?

**On a flat table.** A cross-sectional extract has one row per admission with binary flags for sepsis (S), broad-spectrum antibiotic given (A), and mortality (M). A classic discovery algorithm (PC, GES, LiNGAM, NOTEARS) returns a CPDAG over {S, A, M}. Three DAGs fit the same conditional-independence pattern:

- **Mediation:** S → A → M — antibiotics are a protective treatment.
- **Collider:** S → A ← M — dying patients are over-treated; the correlation is bias.
- **Shared cause:** S ← A → M — implausible clinically, but not ruled out by the CPDAG.

Without time, the algorithm cannot choose.

**On an object-centric representation.** The admission is the root object. Sub-objects — ED arrival, sepsis diagnosis, antibiotic order, discharge/death — carry timestamps. For admission 10012: ED at t=0, sepsis dx at t+1h, antibiotic at t+3h, outcome at t+72h. Temporal precedence fires: S precedes A (you cannot dose what you have not diagnosed), A precedes M (the order event is complete before the outcome is observed). The CPDAG collapses to the single oriented DAG **S → A → M**.

**What this buys.** "Time-to-antibiotic" — the door-to-drug interval — becomes the identifiable estimand. That is the estimand the Surviving Sepsis Campaign's 3-hour bundle is built around, and it is the estimand TMLE or longitudinal g-methods can target once the DAG is oriented.

**Why it matters for RWE.** Antibiotic-mortality associations in claims and EHR data are notoriously confounded by severity. Preserving the admission as an object with timed events is the difference between a statistical curiosity and a policy-relevant effect size.
