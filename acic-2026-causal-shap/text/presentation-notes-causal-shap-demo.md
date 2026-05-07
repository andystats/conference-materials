# Presentation Notes: Expert-Augmented Causal SHAP

## Core Message

Standard SHAP is good at identifying predictive clues. It is not designed to decide whether those clues are causes, mediators, consequences, or proxies.

Causal SHAP keeps the useful part of SHAP, the idea of measuring how much each feature changes a model prediction, but adds a causal rulebook. It only lets features enter the explanation in orders that respect the DAG, and it fills in missing features using parent-child relationships rather than treating all features as exchangeable.

The practical message for the poster is:

> Standard SHAP rewards good clues. Causal SHAP tries to credit causes and causal pathways rather than downstream clues.

## Thirty-Second Version

If a patient is very sick, they may have high lactate, receive vasopressors, get more monitoring, and end up with a high composite score. A prediction model may use that composite score very effectively. Standard SHAP may then rank the composite score as highly important.

That is not wrong as a predictive statement. But it is misleading if the audience hears it as causal importance. The composite score did not cause the illness; it summarized downstream consequences of the illness.

Causal SHAP uses a DAG to prevent downstream variables from jumping ahead of their causes and taking credit too early.

## One-Minute Version

SHAP works by asking: if I add this feature to the model explanation, how much does the prediction change? It repeats that question across many possible feature orderings and averages the result.

The problem is that ordinary SHAP allows causally impossible orderings. A downstream proxy can be considered before the upstream disease process that created it. When that happens, the proxy can absorb credit that clinically belongs to earlier causes or mediators.

Causal SHAP changes the allowed orderings. If the DAG says baseline severity comes before inflammation, and inflammation comes before a monitoring proxy, then causal SHAP respects that order. The downstream proxy only gets credit for what remains after its causal ancestors have already been considered.

So the DAG does not replace feature importance. It defines the question feature importance is allowed to answer.

## How We Simulated the Expert User

Be candid here:

> In the current demo, the expert is an oracle expert. Because this is a simulation, we know the true data-generating DAG. We use that true DAG as the expert-provided causal structure.

What the demo currently does:

- Generate data from a known simcausal DAG.
- Export the true edge list as the expert DAG.
- Label variables as root causes, treatment, mediators, downstream proxies, and outcome.
- Compute analytic total effects from the structural equations.
- Compare standard SHAP and causal SHAP against those known total effects.

What the demo does not yet do:

- It does not simulate a realistic human making partial corrections.
- It does not yet run causal discovery first and ask a simulated expert to resolve ambiguous edges.
- It does not yet evaluate sensitivity to an imperfect expert DAG.

Good phrase:

> This first demo validates the mechanism under an oracle expert. The next step is to degrade that oracle into realistic expert conditions.

## Why This Is Not Circular

Audience concern:

> If we already know the DAG, why do we still need feature importance?

Answer:

The DAG tells us qualitative structure. It says which variables can cause which other variables. It does not tell us how much the fitted model relies on each variable, how strong the pathways are in this sample, or how nonlinear interactions affect predictions.

SHAP measures attribution in a fitted model. The DAG constrains which attributions are causally coherent.

Short version:

> The DAG tells SHAP what stories are allowed. The data and model still determine how large each feature's contribution is.

Analogy:

> This is like regression adjustment. A DAG can tell us which variables belong in an adjustment set, but the regression still estimates the coefficients.

## Demo Talking Points

### Set Up the Failure Mode

In the simulated DAG, we intentionally created downstream proxy variables. These are variables such as a composite score or monitoring proxy that summarize the disease process after it has already unfolded.

They are excellent predictors. That is exactly why they are dangerous in a naive feature-importance plot.

Talking point:

> We are not trying to make standard SHAP fail by adding noise. We are making it fail with variables that are genuinely useful for prediction but causally downstream.

### Standard SHAP Result

Standard SHAP ranks downstream proxies very highly. In the run saved in the repo, downstream proxy variables account for about 51% of total absolute attribution.

This is expected. A proxy close to the outcome can summarize many earlier causes and mediators.

Talking point:

> Standard SHAP is answering the predictive question honestly: what helped the model predict? The problem is that the answer is easy to overread as causal.

### Causal SHAP Result

After adding the expert DAG, downstream proxy attribution falls from about 51% to about 12%. Attribution shifts toward baseline severity, chronic burden, inflammation, perfusion deficit, and other upstream or mediating variables.

Rank agreement with the known total-effect ordering improves in this run:

- Kendall tau vs truth: 0.22 for standard SHAP.
- Kendall tau vs truth: 0.44 for causal SHAP.

Talking point:

> The important result is not that causal SHAP exactly recovers the structural equations. It is that it suppresses credit to descendants that should not receive upstream causal credit.

### What Causal SHAP Is Recovering

Causal SHAP is still explaining the fitted prediction model, not directly estimating the true causal effect of a treatment.

Use this distinction:

- True total effects describe the data-generating system.
- SHAP values describe the fitted model's prediction function.
- Causal SHAP aligns the model explanation with the causal ordering.

Talking point:

> Causal SHAP is not a replacement for causal effect estimation. It is a way to make model explanations less causally incoherent.

## Suggested Slide Flow

### Slide 1: Problem

Title idea:

> Predictive importance is not causal importance

Talk track:

Clinical models often include variables that are causes, consequences, treatments, mediators, and proxies all at once. Standard SHAP treats them as exchangeable model inputs. That is fine for model debugging, but it can mislead clinical interpretation.

### Slide 2: Simple DAG Example

Use:

> Baseline severity -> inflammation -> lactate -> monitoring score -> model prediction

Talk track:

The monitoring score is a strong clue. But it comes after the disease process. If SHAP lets it enter first, it can absorb credit from the upstream process.

### Slide 3: How SHAP Works

Talk track:

SHAP averages how much a feature changes predictions when it is added to different partial feature sets. Ordinary SHAP averages over all possible orders. Causal SHAP averages only over orders that respect the DAG.

### Slide 4: The simcausal Demo

Talk track:

We generated a DAG with root causes, treatment intensity, multiple mediators, and downstream proxies. The proxies were designed to be highly predictive but to have no directed path into the outcome.

### Slide 5: Standard SHAP Gets Fooled

Talk track:

The composite proxy and monitoring proxy rise to the top. This is predictable: they summarize the disease pathway. The problem is interpretive, not computational.

### Slide 6: Causal SHAP Reallocates Credit

Talk track:

When we provide the expert DAG, attribution shifts away from downstream proxies and back toward earlier severity and mediator variables. Proxy attribution falls from about 51% to 12%.

### Slide 7: Expert-Augmented Workflow

Talk track:

In real data, we usually do not know the true DAG. The workflow is not fully automated causal discovery. It is discovery plus expert constraints: forbid impossible edges, require known temporal or clinical edges, resolve ambiguous directions, then compute causal SHAP.

### Slide 8: What This Does and Does Not Claim

Talk track:

This does not prove the true causal graph in observational data. It does not turn SHAP into a treatment-effect estimator. It gives us a way to make feature attribution conditional on explicit causal assumptions, instead of silently relying on causally impossible feature orderings.

### Slide 9: Future Directions

Talk track:

The next step is to move from oracle-expert simulations to realistic expert-in-the-loop settings, then evaluate how robust the attribution is when the expert DAG is partial or imperfect.

## Future Directions

### 1. Simulate Realistic Expert Users

Create several expert conditions:

- Oracle expert: true DAG.
- Tier expert: only knows temporal ordering, such as baseline before treatment before labs before outcome.
- Partial expert: knows a subset of required and forbidden edges.
- Noisy expert: gets most major directions right but misses edges or adds plausible false edges.
- Clinical-role expert: labels variables as baseline, treatment, mediator, proxy, or outcome without specifying every edge.

Goal:

> Quantify how much causal SHAP improves as expert knowledge becomes more complete and how badly it degrades when expert knowledge is wrong.

### 2. Discovery Plus Expert Correction

Run causal discovery first, then simulate expert correction:

- Start with PC, GES, or DirectLiNGAM output.
- Apply temporal constraints.
- Forbid impossible arrows, such as outcome causing age.
- Require high-confidence clinical arrows.
- Compare causal SHAP before and after expert correction.

Goal:

> Show that the value comes from the combination of data-driven discovery and domain knowledge, not from pretending discovery alone can solve the DAG.

### 3. DAG Uncertainty and Sensitivity Analysis

Instead of one final DAG, maintain a small set of plausible DAGs.

Report:

- Features that remain important across plausible DAGs.
- Features whose attribution is DAG-sensitive.
- Features that are only important under implausible causal structures.

Good phrase:

> We should report attribution stability, not just attribution magnitude.

### 4. Better Human Interface

Build an expert review screen that asks targeted questions:

- Can this variable occur before that variable?
- Could this variable plausibly cause the outcome?
- Is this variable a measurement, intervention, mediator, or proxy?
- Should descendants of treatment be excluded from this analysis?

Goal:

> Make causal review easy enough that a domain expert can contribute without needing to edit a DAG by hand.

### 5. Real-World Clinical Application

Apply the workflow to MIMIC-IV or another clinical dataset.

Key reporting distinction:

- Standard SHAP: what the model uses predictively.
- Expert-DAG causal SHAP: what remains important after respecting clinical ordering.
- Sensitivity analysis: which conclusions depend on uncertain edges.

### 6. Compare Against Simpler Alternatives

Benchmark causal SHAP against:

- Excluding downstream proxies before modeling.
- Adjustment-set SHAP.
- SHAP after residualizing downstream proxies.
- Model refitting with only baseline variables.
- Mediation-aware grouped feature importance.

Goal:

> Show when causal SHAP adds value beyond simpler preprocessing or feature restrictions.

### 7. Clarify Estimand Language

Avoid implying that causal SHAP directly estimates causal effects.

Use:

> DAG-consistent model attribution

Be careful with:

> causal effect

Best framing:

> Causal SHAP decomposes model predictions under causal assumptions. It is an explanation estimand, not a treatment-effect estimand.

## Likely Questions and Answers

### Is standard SHAP wrong?

No. It is answering a predictive question. The problem is that people often interpret predictive importance as causal importance.

### Does causal SHAP prove causality?

No. It depends on the DAG. It makes causal assumptions explicit and then computes attribution under those assumptions.

### Why not just remove downstream variables?

Sometimes that is the right choice. But in many prediction settings, downstream variables are part of the deployed model. Causal SHAP helps explain how much of their apparent importance is proxy credit versus residual contribution.

### What happens if the expert DAG is wrong?

Causal SHAP can be wrong in the direction of the DAG error. That is why future work should include noisy-expert simulations and DAG sensitivity analysis.

### Are true total effects the same as causal SHAP?

No. True total effects describe the structural data-generating process. Causal SHAP describes the fitted model's prediction function under DAG-respecting interventions. Agreement with true effects is a validation benchmark, not an identity.

### Why use causal discovery if experts are needed anyway?

Discovery helps identify candidate structure and disagreements. Experts resolve directions and rule out impossible edges. The goal is not automation; it is a disciplined workflow for combining statistical signal and domain knowledge.

## Phrases To Use

- "Predictive importance is not causal importance."
- "Standard SHAP rewards clues; causal SHAP tries to respect causes."
- "The DAG defines the explanation question, not the answer."
- "This is model attribution under causal assumptions."
- "The current simulation uses an oracle expert; the next step is noisy and partial experts."
- "We should report attribution stability across plausible DAGs."

## Phrases To Avoid

- "Causal SHAP discovers the true causes."
- "SHAP estimates causal effects."
- "The expert DAG solves the problem."
- "Standard SHAP is wrong."
- "The DAG tells us feature importance."

## Closing Line

The goal is not to replace clinical judgment with SHAP. The goal is to stop pretending model explanations are causally neutral when the features themselves live inside a causal system.
