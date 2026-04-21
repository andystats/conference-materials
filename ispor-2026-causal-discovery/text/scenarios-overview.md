# Scenarios — overview section

**Headline:** Four RWE scenarios where flat tables stall and longitudinal objects settle the orientation.

**Lede (80 words).**
Cross-sectional data gives classic causal-discovery algorithms a conditional-independence pattern — and only that. The output is a Markov-equivalence class (CPDAG): a partially-directed graph where every oriented edge coexists with plausible alternatives. Object-analytic engines like Xplain Data's ObjectAnalytics Database keep the two things a flat table throws away: **event timestamps** and **relational structure**. Once those are preserved, temporal precedence and immutability-at-birth become hard constraints on the search, and the equivalence class often collapses to a single oriented DAG.

**Four worked scenarios.**

1. **Sepsis → antibiotic → mortality.** Flat data: S—A—M CPDAG. Candidate DAGs include mediation, collider, and shared-cause — clinically distinct stories that all fit the same correlations. Add admission-level event times (sepsis dx at t+1h, antibiotic at t+3h, outcome at t+72h) and "time-to-antibiotic" becomes the identifiable estimand.

2. **Drug switch & adverse event.** Flat data cannot tell whether drug A caused the ADR (prompting a switch to B), drug B caused it, or both drugs contributed additively. A therapy-journey object with dated dispense runs rules out drug B — it wasn't started yet — and pins the attribution on drug A.

3. **Chronic disease progression (T2D → HTN → CKD).** Three comorbidity flags produce an undirected triangle. First-diagnosis dates, averaged across millions of patients, reveal a single progression graph and locate the intervention window — glycemic control.

4. **Breast-cancer risk: life-course ordering.** Family history, age at menarche, parity, and HRT all correlate with diagnosis. Treated as a dense undirected CPDAG, they are indistinguishable risk factors. A life-course object with dated milestones plus immutability-at-birth (family history can only be a source) separates the modifiable lever — HRT — from fixed genetic risk.

**Common thread.** An object-analytic engine preserves what a flat table discards: event timestamps, start/stop runs, first-diagnosis dates, and immutability-at-birth. Those constraints shrink the Markov equivalence class to a single oriented DAG, and flagged edges become identifiable estimands for TMLE and longitudinal g-methods downstream.
