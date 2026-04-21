# Scenario 3 — Chronic disease progression (T2D → HTN → CKD)

**Section heading:** Where on the progression curve is the intervention window?

**The question.** Type 2 diabetes, hypertension, and chronic kidney disease co-occur in a patient's problem list. Which comes first, and — more importantly — where should an intervention be placed to alter the trajectory?

**On a flat table.** Each patient is summarized with three flags: `T2D`, `HTN`, `CKD`. The algorithm returns an undirected triangle in the CPDAG. Six DAGs fit the same conditional-independence pattern. Flat data cannot say whether diabetic nephropathy drives the progression, whether poorly-managed hypertension is the renal driver, or whether all three reflect unmeasured cardiometabolic risk.

**On an object-centric representation.** Each patient is a root object with dated diagnosis sub-objects. For patient P-0412: T2D first recorded at age 54, HTN at age 58, CKD at age 63. That single patient's order is **T2D → HTN → CKD**. Across millions of dated trajectories in a claims database, the distribution of first-diagnosis orderings stabilizes around this sequence. Temporal precedence orients every edge of the triangle.

**What this buys.** Payers and care teams get a *progression graph*, not just a comorbidity list. They can see that glycemic control at age 50 — well before HTN onset — is the highest-leverage intervention point for preventing CKD at age 63. Static "multimorbid" labels collapse that leverage into a single variable.

**Why it matters for RWE.** This is the pattern behind AOK Nordost's cross-sectoral disease-progression work with Xplain Data: the business question ("where do we intervene?") only becomes tractable once the patient is represented as an object carrying dated events, not a row of binary comorbidity flags. The progression DAG is what makes the intervention window visible.
