# Scenario 2 — Drug switch & adverse event

**Section heading:** A pharmacovigilance question the flat table cannot answer.

**The question.** A patient was dispensed drug A, then drug B, and recorded an adverse drug reaction (ADR). Which drug caused it?

**On a flat table.** Each row carries `drug_A`, `drug_B`, and `ADR` as binary flags. The discovery algorithm returns a CPDAG consistent with three clinically distinct stories:

- **A caused the ADR**, which prompted a switch to B. (A → ADR → B)
- **B caused the ADR**; the switch from A predates the event. (A ← ADR ← B)
- **Both drugs contribute additively**, meeting at ADR as a collider. (A → ADR ← B)

The regulator would reach different conclusions under each. The flat table offers no way to choose.

**On an object-centric representation.** The patient is the root object. The therapy-journey sub-object carries dispense runs with start and stop dates. For patient P-2041: drug A dispensed continuously from day 0 to day 120, ADR onset recorded at day 120, drug B first dispensed at day 140.

Temporal precedence does the work. Drug B was not yet started when the ADR was logged; the additive and reverse-causation DAGs are falsified directly by the dispense dates. The CPDAG collapses to **A → ADR → switch-to-B**.

**What this buys.** The attribution becomes defensible: ADR onset occurred while only drug A had ever been dispensed. The switch to B is downstream of the ADR, not causally upstream of it. The estimand of interest — probability of an ADR conditional on an incident drug-A regimen — is identifiable from dated dispense data.

**Why it matters for RWE.** Xplain Data's therapy-journey module treats prescriptions as dated sub-objects of the patient, precisely so that the direction of the drug→ADR edge is resolvable. A summarized "ever-exposed" column, in contrast, destroys the information needed to distinguish cause from coincidence.
