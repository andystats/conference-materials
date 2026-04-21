# Why object analytics + longitudinality disambiguates CPDAGs

**The underlying claim.** Object analytics does not replace classical causal discovery. It supplies the two constraints a classical algorithm cannot derive from a flat table:

1. **Event timestamps**, which encode temporal precedence and rule out DAGs in which later events are parents of earlier events.
2. **Relational structure** (patient → admission → lab, or life-course → milestone → outcome), which encodes immutability-at-birth, informative missingness, and parent-child object semantics.

Both constraints act as background knowledge on the search over DAGs. The skeleton stays the same. What changes is how many edges the algorithm can orient.

**The Markov-equivalence problem.** With cross-sectional data, PC, GES, LiNGAM, and NOTEARS all recover the same object: the Markov-equivalence class of the true DAG, represented as a CPDAG (Completed Partially Directed Acyclic Graph). Two DAGs are Markov-equivalent if they share the same skeleton and the same v-structures (unshielded colliders). For every unshielded non-collider in the CPDAG, multiple orientations are still in play. In healthcare problems with many nodes and few colliders, most of the edges in the returned CPDAG come back undirected.

**Why timestamps are not just "more data".** A timestamp is a *hard constraint* on the search, not another covariate. If A occurred at t₁ and B at t₂ > t₁, then any DAG with B → A is inadmissible. Temporal precedence eliminates whole equivalence classes at a stroke. Relational structure does the same thing for immutable traits (family history, sex, ABO type, date of birth): they can only be source nodes.

**What the Xplain Data ObjectAnalytics engine supplies.** It holds the patient as a root object with up to ~50 nested sub-objects (admissions, prescriptions, labs, diagnoses, procedures), each with native timestamps. The causal-discovery search operates on this relational structure directly — temporal precedence is enforced automatically, "ever-exposed" flags are replaced by start/stop runs, and the search runs on events rather than on a flattened rectangle. Release 2.3 added explicit temporal causal graphs with "relative time axis" discovery; release 2.7 added a join method that transfers related records across sibling objects (e.g., prescriptions after a diagnosis).

**Downstream.** Once the CPDAG collapses to an oriented DAG, the candidate causal edges become identifiable estimands. The discovery output becomes a prioritization of edges for confirmatory analysis, each one testable with target-trial emulation and TMLE / longitudinal g-methods. That is the handoff from discovery to inference — and the step that turns a statistical artifact into a policy-relevant effect size.
