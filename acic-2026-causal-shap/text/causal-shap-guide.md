# Expert-Augmented Causal SHAP

## A Guide for Epidemiologists and Biostatisticians

*Companion document for the Causal Discovery Playground (Python Shiny App)*

---

## 1. The Problem: Why Standard SHAP Fails with Causal Structure

Suppose you build a machine learning model to predict hospital-acquired pressure injuries (PRI) in the ICU. You compute SHAP values to explain the model. The top-ranked feature is **vasopressor use**. Should you conclude that vasopressors cause pressure injuries?

No. Vasopressors are administered to the sickest patients --- those with hemodynamic instability, sepsis, and prolonged immobility. Vasopressor use is a *consequence of severity*, not a *cause of injury*. The model learned a strong statistical association (sicker patients get vasopressors AND get pressure injuries), and SHAP dutifully reported that association as "importance." But this importance is misleading: it conflates correlation within the causal graph with actual causal contribution.

This is not a bug in SHAP. It is a **topological artifact** that arises whenever features have causal structure. Standard SHAP treats all features as exchangeable --- it averages each feature's marginal contribution across *all possible orderings* of features. But in a causal system, features are not exchangeable. Causes come before effects. Mediators sit between causes and outcomes. When SHAP permutes features in all possible orders --- including causally impossible ones like "Outcome before Treatment" --- variables that sit close to the outcome in the causal graph absorb credit that properly belongs to upstream causes.

**The theoretical correction** was established by Heskes et al. (2020) and Janzing et al. (2020): compute Shapley values under *interventional* rather than *observational* distributions. Standard SHAP asks: "if I *observe* this feature at value x, what prediction do I expect?" Causal SHAP asks: "if I *intervene* to set this feature to value x (Pearl's do-operator), what prediction do I expect?" The difference matters whenever features cause each other --- which is always, in clinical data.

But there is a catch: causal SHAP requires a **known causal DAG**. In practice, fully automated causal discovery (e.g., the PC algorithm) produces partially oriented graphs with ambiguous edges. Our application addresses this through an *expert-augmented* iterative workflow that combines data-driven discovery with domain knowledge to produce a resolved DAG suitable for causal SHAP computation.

---

## 2. Key Definitions

| Term | Definition |
|------|-----------|
| **DAG** | *Directed Acyclic Graph.* A graph where arrows indicate causal direction and no variable causes itself, even indirectly. The standard formalism for encoding causal assumptions in epidemiology. |
| **CPDAG** | *Completed Partially Directed Acyclic Graph.* The output of constraint-based algorithms like PC. Some edges are directed, others remain undirected because data alone cannot resolve them. Represents an entire Markov equivalence class of DAGs. |
| **Topological ordering** | A linear arrangement of DAG nodes such that every cause comes before its effects. A DAG with *p* features has many valid topological orderings --- but far fewer than the *p*! total orderings that standard SHAP considers. |
| **Shapley value** | From cooperative game theory: the average marginal contribution of a feature across all possible orderings. Standard SHAP uses all *p*! orderings. Causal SHAP restricts to topological orderings of the DAG. |
| **Interventional distribution** | The distribution of variables under Pearl's *do*-operator: P(Y \| do(X=x)). Sets X to x and propagates effects downstream through the DAG, rather than conditioning on an observed value. This breaks confounding associations. |
| **Adjustment set** | A set of variables that, when conditioned on, blocks all backdoor (confounding) paths between treatment and outcome while leaving causal paths open. Identified from the DAG using the backdoor criterion. |
| **Shrier-Platt algorithm** | A 6-step graphical procedure for validating adjustment sets by checking whether conditioning blocks all non-causal paths between exposure and outcome. Reference: Shrier & Platt (2008). |
| **Kendall's tau** | A rank correlation coefficient (-1 to +1) measuring agreement between two rankings. Used here to compare Standard vs. Causal SHAP feature rankings and both against ground truth causal effects. |
| **Mediator Inflation Ratio** | The ratio of mediator variable SHAP importance (standard) to mediator SHAP importance (causal). Values > 1 indicate standard SHAP inflates mediator credit relative to causal SHAP. Values < 1 indicate causal SHAP assigns *more* credit to mediators than standard SHAP does. |
| **True total causal effects** | Analytically derived from the structural equations of a known DGP. Used as a ranking benchmark to compare SHAP methods, but note: total causal effects are *not* the same as Shapley values. Even perfect causal SHAP decomposes a *model's prediction*, not the DGP itself. |

---

## 3. How Causal SHAP Works

### 3.1 Standard SHAP (Recap)

For a prediction model *f* and an instance *x*, the SHAP value for feature *j* is the average marginal contribution of feature *j* across all *p*! orderings of features. For each ordering, the contribution of feature *j* equals:

> f(features before j, including j) - f(features before j, excluding j)

When computing f(coalition of features), variables *not* in the coalition are filled in by sampling from their **marginal** (observational) distribution. This means SHAP implicitly assumes features are independent when computing expectations --- which is wrong when features cause each other.

**Important:** Standard SHAP does *not* treat the treatment/exposure variable specially. The prediction model is fitted as `f(all features) → Outcome`, and Treatment is just another input column alongside Age, BMI, Inflammation, etc. SHAP explains *which features are most predictive* --- not *which features are most causal*. The "Treatment/Exposure" selector in the app's Causal SHAP tab is only used by the Adjustment-Set SHAP method (to identify confounders) and the Export tab (for Shrier-Platt adjustment sets). Standard SHAP ignores it entirely.

### 3.2 DAG-Constrained Shapley Values (Causal SHAP)

Three modifications correct the topological artifact:

1. **Restricted permutations.** Instead of all *p*! orderings, sample only from valid *topological orderings* of the DAG. At each step, uniformly select from nodes with in-degree zero (no unprocessed parents), ensuring causes always come before effects.

2. **Interventional expectations.** When computing f(coalition), variables not in the coalition are sampled from their **interventional** distribution --- conditioned on their parents in the DAG, not on the overall marginal. If a variable's parents are all in the coalition, sample from P(X_j | parents = instance values). If some parents are not in the coalition, propagate forward through the DAG using pre-fitted conditional models.

3. **Conditional structural models.** For each non-root node in the DAG, a small gradient-boosting model is fit to estimate P(X_j | parents(X_j)). These serve as structural equation surrogates, enabling the interventional sampling in step 2.

This is the asymmetric Shapley framework of Heskes et al. (2020): by restricting permutations and using interventional distributions, credit flows along causal pathways rather than being distributed by proximity to the outcome.

### 3.3 Adjustment-Set SHAP

A complementary approach that sidesteps the permutation problem entirely:

1. Use the DAG to identify a valid **adjustment set** --- the confounders that block all backdoor paths between treatment and outcome (via the Shrier-Platt algorithm or disjunctive cause criterion).
2. Fit a restricted prediction model using **only** the adjustment set variables as features.
3. Compute standard SHAP on this restricted model.

Because the feature set is restricted to confounders (no mediators, no colliders, no descendants of treatment), the SHAP values cannot be contaminated by the topological artifact. This approach is simpler and faster than DAG-constrained SHAP, but provides less granular attribution.

---

## 4. Why This Is NOT Circular Reasoning

A natural objection: *"If you learn a DAG from the data, doesn't that already tell you which features are important? Why run SHAP on top? Isn't this circular?"*

No. The DAG and SHAP answer fundamentally different questions:

### 4.1 The DAG encodes qualitative structure, not quantitative effects

The DAG says "Treatment causes Inflammation" but does not say *by how much* or *relative to other features in a specific prediction model*. The DAG describes the **data-generating process**; SHAP describes a **fitted model's behavior**. These are different questions. A road map tells you which roads connect which cities, but does not tell you how much traffic flows on each road.

### 4.2 Same DAG, different models, different SHAP values

Two different ML models (e.g., gradient boosting vs. random forest) fitted to the same data under the same DAG will produce different SHAP values because they learned different functional relationships. The DAG constrains *how* SHAP computes attribution, but does not determine *what* those values are.

### 4.3 The DAG prevents mediator inflation

Without DAG constraints, standard SHAP ranks the mediator Inflammation above Treatment even though Treatment's true total causal effect is nearly 5x larger (11.0 vs. -2.25 in our simulation). The DAG does not "double-count" --- it corrects a specific, well-characterized bias in standard SHAP by ensuring features are evaluated in causally valid orderings.

### 4.4 Analogy: regression adjustment

No one objects that "learning which variables to adjust for from a DAG and then estimating regression coefficients is circular." The DAG tells you *which* variables to include in the adjustment set; the regression tells you *how much* each matters. Causal SHAP works identically: the DAG tells SHAP *which orderings are valid*; SHAP tells you *how much* each feature contributes.

### 4.5 The iterative workflow answers different questions at each step

The workflow is: **discover skeleton** (data-driven, answers "what is associated with what?") -> **expert resolves edges** (domain knowledge, answers "which way does causation flow?") -> **compute causal SHAP** (model-specific, answers "how much does each feature contribute to this model's predictions?") -> **review attributions** (do they make clinical sense?) -> **refine DAG if needed** (revisit structural assumptions).

This is not circular because each step answers a distinct question. Discovery identifies associations. Expert resolution determines causal direction. SHAP quantifies prediction-model attribution. Review provides clinical validation. This is the same logic behind any iterative scientific process --- hypothesis, test, revise --- applied to model interpretation.

---

## 5. The Application: Tab-by-Tab User Guide

### Tab 1: Data

**Purpose:** Load a dataset and select variables for analysis.

Three built-in dataset options:
- **Simcausal** (default): 500 observations, 12 variables with a known ground-truth DAG and structural equations. Ideal for validation because true causal effects are known analytically.
- **MIMIC-IV PRI**: 22,717 ICU patients, 33 clinical variables. Binary outcome: hospital-acquired pressure injury (`pri`). Key treatment variable: `Vasopressors`.
- **Upload CSV**: Bring your own data.

After loading, select which numeric variables to include in discovery and analysis. The app shows a data preview with row count, column count, and number of numeric columns.

### Tab 2: Discover

**Purpose:** Run causal discovery algorithms to learn a DAG from data.

Three algorithms (all from the `causal-learn` library):

| Algorithm | Type | Key Assumption | Output |
|-----------|------|---------------|--------|
| **PC** | Constraint-based | Faithfulness | CPDAG (some edges undirected) |
| **DirectLiNGAM** | Functional causal model | Linear with non-Gaussian errors | Fully directed DAG |
| **GES** | Score-based (BIC) | No specific distributional assumption | CPDAG |

**Expert constraints** (domain knowledge):
- *Forbidden edges*: edges that cannot exist (e.g., `pri,age` --- the outcome cannot cause demographics)
- *Required edges*: edges that must exist (e.g., `Treatment,Outcome`)
- Format: `Source,Target` (one per line)

Constraints are **hard-enforced** after discovery. The algorithms receive constraints as soft hints during search, but the app then post-processes the adjacency matrix to guarantee all required edges are present and all forbidden edges are removed. The results panel confirms enforcement: "✓ Enforced N required edge(s)".

**Post-processing**: "Enforce DAG" removes cycles if the discovered graph contains them (common with undirected edges that get arbitrarily oriented). Required edges are *protected* during cycle removal --- the algorithm will preferentially remove non-required edges to break cycles.

**Key insight**: Different algorithms can produce very different graphs from the same data. In our experiments, PC and GES showed only ~20% edge agreement. Always validate with domain expertise.

### Tab 3: Graph

**Purpose:** Visualize and inspect the discovered causal graph.

- Interactive network visualization (drag nodes, zoom, pan)
- **Node Inspector**: click any variable to see its parents (direct causes) and children (direct effects)
- **Edge List**: all discovered directed edges
- **Quick Constraint**: select edges to add as forbidden or required, then re-run discovery

### Tab 4: Export

**Purpose:** Identify adjustment sets and export the DAG.

- **Adjustment Set Identification**: specify Treatment and Outcome variables, then the app identifies three types of adjustment sets:
  - *Traditional confounders*: variables that are common parents of both treatment and outcome
  - *Disjunctive cause criterion* (VanderWeele & Shpitser, 2011): any cause of treatment OR outcome, excluding descendants of treatment
  - *Minimal sufficient set*: smallest set that blocks all backdoor paths
- Each set is validated using the **Shrier-Platt 6-step algorithm**
- **DAGitty Export**: copy code for dagitty.net to share and further analyze your DAG

### Tab 5: Evaluate

**Purpose:** Compare the discovered graph to ground truth (simcausal data only).

Metrics reported:
- Precision, Recall, F1 (directed edges)
- F1 (skeleton --- ignoring edge direction)
- Edge classification: Correct, Reversed, Spurious, Missed
- Treatment Pathway Analysis: did discovery correctly identify the Treatment-to-Outcome path?

### Tab 6: Causal SHAP

**Purpose:** Compute and compare standard vs. causally-constrained feature attributions.

**Configuration (left panel):**
- *Outcome variable*: which variable to predict (e.g., `Outcome` for simcausal, `pri` for MIMIC-IV)
- *Treatment / Exposure*: which variable to focus on for adjustment-set analysis
- *Prediction model*: Gradient Boosting (default), Random Forest, or Linear/Logistic
- *SHAP method*: Compare All (recommended), Standard only, Causal only, or Adjustment-Set only
- *Permutations*: number of topological orderings to sample (20--200; higher = more accurate but slower)
- *DAG source*: Discovered (from Tab 2), Expert (pre-specified for MIMIC-IV), or Ground Truth (simcausal only)

**Output (right panel):**
- **Comparison bar plot**: side-by-side Standard vs. Causal SHAP importance
- **Rank Change table**: which features moved up or down between standard and causal rankings
- **Metrics cards**: Kendall's tau (Std vs Causal), tau vs Truth (if ground truth available), Mediator Inflation Ratio

---

## 6. Results from Validation

### 6.1 Causal Discovery (Simcausal, n=500, 12 variables)

| Algorithm | Edges Found | Ground Truth Edges | Time | Cycles Removed |
|-----------|------------|-------------------|------|---------------|
| PC | 19 | 28 | 0.09s | 3 |
| DirectLiNGAM | 29 | 28 | 0.11s | 0 |
| GES | 19 | 28 | 1.86s | 2 |

### 6.2 Feature Rankings: Standard vs. Causal SHAP

Using the PC-discovered DAG (default settings, 50 permutations):

| Feature | Standard SHAP Rank | Causal SHAP Rank | Change | True Total Effect |
|---------|-------------------|-----------------|--------|-----------------|
| Inflammation | 1 | 1 | --- | -2.25 |
| Oxygenation | 2 | 3 | -1 | 0.50 |
| Comorbidity | 3 | 5 | -2 | -4.38 |
| HR | 4 | 9 | -5 | -0.03 |
| Treatment | 5 | 4 | +1 | **11.00** |
| Age | 6 | 10 | -4 | -0.10 |
| Creatinine | 7 | 6 | +1 | 0.00 |
| SBP | 8 | 7 | +1 | 0.00 |
| BMI | 9 | 8 | +1 | -0.23 |
| Glucose | 10 | 2 | **+8** | 0.00 |
| Sex | 11 | 11 | --- | 0.00 |

### 6.3 Summary Metrics

| Metric | 50 perms (fast) | 500 perms (accurate) |
|--------|----------------|---------------------|
| Kendall's tau (Std vs Causal) | 0.418 | ~0.4 |
| tau vs Truth (Standard) | 0.520 | ~0.5 |
| tau vs Truth (Causal) | 0.289 | ~0.5 |
| Mediator Inflation Ratio | 0.80x | ~0.8x |

### 6.4 Interpretation: An Honest Finding

Standard SHAP ranked the mediator Inflammation first and the dominant true cause Treatment fifth. This is the topological artifact at work: Inflammation sits between Treatment and Outcome in the DAG, so it absorbs credit that belongs to Treatment. Causal SHAP substantially rearranges rankings (tau = 0.42 between the methods), and the Mediator Inflation Ratio of 0.80x confirms that standard SHAP inflates mediator importance by ~25%.

**However:** When we increased permutations to 500 (reducing Monte Carlo noise), both methods converged to **tau vs truth ~ 0.5**. Standard SHAP and causal SHAP performed *equally well* at recovering the true causal ranking in this simulation.

This is surprising but interpretable:

1. **The simcausal DGP has a strong direct effect.** Treatment → Outcome has a direct coefficient of +5, the largest of any variable. Standard SHAP catches this direct association just fine. The mediator inflation problem is most severe when treatment has *no* direct effect and works *entirely* through mediators --- then standard SHAP gives Treatment zero credit. That's not the case here.

2. **The bottom half of the ranking is noise.** Four features (SBP, Glucose, Creatinine, Sex) have true causal effect = 0.0, and three more (Oxygenation, BMI, Age, HR) have effects < 0.5 in magnitude. Neither method can reliably distinguish among these near-zero effects, so their relative ordering is random. This scrambling of the bottom half caps tau at ~0.5 for *any* method.

3. **Total causal effects ≠ Shapley values.** The "truth" benchmark is total causal effects from structural equations, but Shapley values decompose a *model's prediction*, not the DGP itself. Even perfect causal SHAP would not match total effects exactly, because some of Treatment's +11 effect flows through Inflammation and Oxygenation, which still receive credit as mediators in the Shapley decomposition.

**The causal SHAP correction is real** (it rearranges rankings and deflates mediators) but **its improvement over standard SHAP depends on the causal structure** of the specific DGP.

### 6.5 When Does Causal SHAP Matter Most?

Causal SHAP provides the greatest correction over standard SHAP when:

1. **Treatment operates entirely through mediators** (no direct effect on outcome). Standard SHAP will rank Treatment near zero and give all credit to mediators. Causal SHAP correctly traces credit back to the upstream cause.

2. **Strong confounding is present.** When a confounder simultaneously drives both treatment and outcome, standard SHAP conflates the confounder's predictive association with its causal role. The DAG-constrained approach separates these.

3. **Colliders are conditioned on.** When a descendant of both treatment and outcome is included as a feature, standard SHAP may open a spurious pathway. Causal SHAP's topological ordering prevents this.

4. **The causal graph is complex** with many mediator chains. The more causal structure the data has, the more standard SHAP's exchangeability assumption distorts attributions.

The **MIMIC-IV vasopressor pathway** is a more realistic test case: vasopressors are a confounder (treatment-by-indication), the effect is heavily mediated through hemodynamic pathways, and the expert DAG encodes 40 edges of clinical knowledge. This is where causal SHAP's correction should be most pronounced.

---

## 7. Quick Start: 5-Minute Crash Course

### Step 1: Install Python 3.13

Download from [python.org](https://www.python.org/downloads/). **Important**: Python 3.14 has numpy compatibility issues on Windows; use 3.13.

### Step 2: Install dependencies

Open a terminal (Mac: Terminal; Windows: Command Prompt) and run:

```
pip install causal-learn shap scikit-learn matplotlib scipy shiny pandas numpy networkx pyvis
```

### Step 3: Run the app

Navigate to the `causal_discovery_app` folder and run:

```
python -m shiny run app.py
```

Open your browser to **http://127.0.0.1:8000**

### Step 4: Run causal discovery

- The app loads with the simcausal dataset (500 obs, 12 vars) by default
- Click the **Discover** tab
- Leave PC Algorithm selected (default)
- Click **Run Discovery**
- You should see: "Discovery complete --- 19 edges found"

### Step 5: Compute Causal SHAP

- Click the **Causal SHAP** tab
- Leave defaults: Outcome = `Outcome`, Treatment = `Treatment`, Compare All
- Click **Compute SHAP** (this takes 2--3 minutes)
- Wait for "SHAP computation complete"

### Step 6: Read the results

**What to look for:**
- The **comparison bar chart** shows Standard SHAP (gray) vs. Causal SHAP (blue) side by side
- The **Rank Change table** shows which features moved --- look for Inflammation (the mediator) being demoted and Treatment (the true cause) being promoted
- The **Kendall's tau** metric below quantifies how much the rankings changed

**The key finding:** Standard SHAP ranks features by *proximity to the outcome* in the causal graph. Causal SHAP re-ranks features by *causal contribution* --- correcting the topological artifact.

---

## 8. The Datasets

### 8.1 Simcausal (Validation Dataset)

Generated via R's `simcausal` package with known structural equations:

**Root variables:**
- Age ~ Normal(65, 12)
- Sex ~ Bernoulli(0.48)
- Comorbidity ~ Gamma(2, 1)

**Intermediate variables:**
- BMI = 26 + 0.05 Age - 2 Sex + noise
- SBP = 90 + 0.5 Age + 0.8 BMI + 3 Comorbidity + noise
- Treatment ~ Bernoulli(logistic(-2 + 0.02 Age + 0.3 Comorbidity + 0.01 SBP + 0.005 Glucose))

**Mediators:**
- Inflammation = 5 - 2 Treatment + 1.5 Comorbidity + 0.1 BMI + noise
- Oxygenation = 95 + 3 Treatment - 0.05 HR - 0.5 Inflammation + noise

**Outcome:**
- Outcome = 50 + **5 Treatment** - 2 Inflammation + 0.5 Oxygenation - 0.1 Age - 1 Comorbidity + noise

**True total causal effects** (computed by path analysis):

| Feature | Total Effect on Outcome | Pathway |
|---------|------------------------|---------|
| Treatment | **+11.0** | +5 direct, +4 via Inflammation, +1.5 via Oxygenation, +0.5 via chain |
| Comorbidity | -4.38 | -1 direct, -3 via Inflammation, -0.38 via chain |
| Inflammation | -2.25 | -2 direct, -0.25 via Oxygenation |
| Oxygenation | +0.50 | direct only |
| BMI | -0.23 | via Inflammation pathway |
| Age | -0.10 | direct |
| HR | -0.03 | via Oxygenation |
| SBP, Glucose, Creatinine, Sex | 0.00 | no causal path to Outcome |

The ground truth DAG has 28 directed edges.

### 8.2 MIMIC-IV PRI (Real-World Application)

- **Source:** MIMIC-IV (Johnson et al., 2023), a freely accessible EHR dataset
- **Sample:** 22,717 ICU patients, 33 clinical variables
- **Outcome:** Hospital-acquired pressure injury (`pri`, binary)
- **Key challenge:** Vasopressors create a confounded pathway --- sicker patients receive vasopressors AND develop pressure injuries. Standard SHAP will rank Vasopressors highly, but this reflects disease severity, not a causal effect of the drug.
- **Expert DAG:** 40 edges encoding temporal ordering (demographics -> admission labs -> ICU vitals -> interventions -> outcome) and clinical pathophysiology
- **Clinical context:** See Alderden et al. (2024) for the original PRI prediction model

---

## 9. Software Landscape

### What exists

**Python:** `fast-causal-shap` (PyPI v0.3.0, Jan 2026; Ng et al., IJCNN 2025). Takes an external JSON DAG as input and adjusts SHAP values. Small proof-of-concept (~9KB). The causal graph is modular --- any DAG can be supplied.

**R:** `shapcf` (GitHub, GPL-3, in review; Koh). Shapley values for causal forests via the `grf` package. Provides local (SVCF) and global (SFICF) feature importance for heterogeneous treatment effects. Includes epidemiologically relevant example datasets.

### The gap we fill

No existing tool formalizes the **iterative, expert-in-the-loop** refinement process:

1. Data-driven skeleton discovery (PC/GES -> CPDAG)
2. Expert resolution of ambiguous edges (domain knowledge, temporal ordering)
3. Causal SHAP computation with the resolved DAG
4. Sensitivity analysis over alternative DAG specifications
5. Interactive visualization of how DAG structure changes attributions

Our Python Shiny application provides all five steps in a single interactive environment, with immediate visual feedback at each stage.

---

## 10. References

1. Heskes T, Bucur IG, Claassen T (2020). Causal Shapley values: Exploiting causal knowledge to explain individual predictions of complex models. *NeurIPS* 33.
2. Janzing D, Minorics L, Blobaum P (2020). Feature relevance quantification in explainable AI: A causal problem. *AISTATS*.
3. Wang J, Wiens J, Lundberg S (2021). Shapley Flow: A graph-based approach to interpreting model predictions. *AISTATS*.
4. Frye C, Rowat C, Feige I (2020). Asymmetric Shapley values: Incorporating causal knowledge into model-agnostic explainability. *NeurIPS* 33.
5. Lundberg SM, Lee S-I (2017). A unified approach to interpreting model predictions. *NeurIPS* 30.
6. Ng WY, Wang LR, Liu S, Fan X (2025). Causal SHAP: Feature attribution with dependency awareness through causal discovery. *IJCNN*.
7. Koh H (in review). Principled feature importance and explanations for causal forests via Shapley values. R package `shapcf`.
8. Shrier I, Platt RW (2008). Reducing bias through directed acyclic graphs. *BMC Medical Research Methodology* 8:70.
9. VanderWeele TJ, Shpitser I (2011). A new criterion for confounder selection. *Biometrics* 67(4):1406--1413.
10. Textor J et al. (2016). Robust causal inference using directed acyclic graphs: The R package dagitty. *International Journal of Epidemiology* 45(6):1887--1894.
11. Pearl J (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.
12. Spirtes P, Glymour C, Scheines R (2000). *Causation, Prediction, and Search* (2nd ed.). MIT Press.
13. Johnson AEW et al. (2023). MIMIC-IV, a freely accessible electronic health record dataset. *Scientific Data* 10:1.
14. Alderden J et al. (2024). Explainable Artificial Intelligence for Early Prediction of Pressure Injury Risk. *American Journal of Critical Care*.
15. Molak A (2023). *Causal Inference and Discovery in Python*. Packt Publishing.
16. Shimizu S et al. (2006). A Linear Non-Gaussian Acyclic Model for Causal Discovery. *JMLR* 7:2003--2030.
17. Chickering DM (2002). Optimal Structure Identification With Greedy Search. *JMLR* 3:507--554.
18. Zheng X, Aragam B, Ravikumar P, Xing EP (2018). DAGs with NO TEARS: Continuous optimization for structure learning. *NeurIPS*.
