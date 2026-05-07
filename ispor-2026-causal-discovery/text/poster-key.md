# Poster storyboard and narrative key

Working frame: this poster should make one disciplined but memorable claim:
flat-table causal discovery asks an algorithm to recover clinical time after we
have thrown clinical time away. Object-centric discovery keeps the patient,
events, relationships, and timestamps together, so temporal precedence can
orient many edges that a CPDAG leaves ambiguous. In the HAPrI MIMIC-IV case,
that representation prioritized hypoalbuminemia as a candidate upstream driver
worth clinician review and confirmatory target-trial/TMLE analysis.

This is not a poster about proving that albumin management prevents pressure
injury. It is a poster about turning messy, time-stamped EHR data into a more
realistic causal-discovery workflow.

## One-line thesis

Flat tables create causal ambiguity; patient objects preserve the clocks that
help resolve it.

## Poster promise

After 60 seconds, the viewer should be able to say:

> Traditional causal discovery often stalls because multiple DAGs are
> observationally indistinguishable. Object analytics keeps EHR events in their
> temporal patient context, uses time as an orientation constraint, and turns a
> discovery graph into testable clinical estimands.

## Abstract-to-poster translation

The abstract has four formal sections. The poster should turn those into a
visual story:

1. Background / objective becomes the tension:
   Flat-table algorithms can learn dependencies, but in healthcare they face
   relational complexity, confounding, and Markov-equivalent DAGs. A CPDAG is
   not a failure; it is the honest output when the data no longer contains
   enough orientation information.

2. Methods becomes the move:
   Represent each ICU admission as a patient object with dated sub-objects
   (labs, medications, procedures, diagnoses, microbiology, transfers). Use
   temporal precedence, relational structure, and pre-index feature windows as
   constraints during search.

3. Results becomes the case:
   In MIMIC-IV v3.1 adult ICU admissions, hypoalbuminemia was prioritized as a
   candidate upstream driver of hospital-acquired pressure injury. Known risks
   such as mechanical ventilation, hemodynamic instability, immobility,
   moisture exposure, and yeast colonization were rediscovered without manual
   feature engineering.

4. Conclusions becomes the handoff:
   The graph is a prioritization device. The next step is clinician review and
   a prespecified target-trial/TMLE or longitudinal g-methods analysis to
   estimate candidate intervention effects.

## Text poster storyboard

### Scene 1: The question

Headline:

> Why did this patient develop HAPrI?

What the viewer should see:

- A small patient timeline: ICU admission, low albumin, ventilation/immobility,
  HAPrI diagnosis.
- A callout: "The EHR already knows what happened first."

Narrative role:

Open with the clinical question, not the algorithm. The deck begins with "why"
as the core of intelligence; the poster should begin the same way, but grounded
in HAPrI.

Takeaway:

> Causal discovery is only clinically useful if it respects the sequence of
> care.

### Scene 2: The flat-table trap

Headline:

> Flattening turns a patient journey into a shadow.

What the viewer should see:

- The new `fig_cpdag_stall_cartoon.svg` or a cropped version.
- A flat row that has X, Y, Z but no usable clocks.
- Three DAGs that imply the same independence pattern.
- A CPDAG with undirected edges.

Narrative role:

This is the technical problem made intuitive. Traditional causal discovery is
not "wrong"; it is being asked to orient arrows after the data have been stripped
of the very structure that helps orient them.

Poster copy:

> In a flat extract, X -> Y -> Z, X <- Y -> Z, and X <- Y <- Z can be
> empirically indistinguishable. The algorithm returns the equivalence class,
> not a single clinical story.

Takeaway:

> A CPDAG is what causal ambiguity looks like when time has been discarded.

### Scene 3: The object-analytics move

Headline:

> Keep the clocks attached.

What the viewer should see:

- The new `fig_temporal_objects_orient.svg`.
- Patient object at left.
- Relative-time guardrail in the middle.
- Candidate DAG at right.

Narrative role:

This is the central methods insight. Object analytics does not merely store data
differently; it changes what constraints are available to discovery. Labs,
medications, procedures, microbiology, and transfers remain attached to the
patient and to event time. That makes temporal precedence a graph-orientation
constraint rather than a covariate buried in a table.

Poster copy:

> Candidate parents are built only from the pre-index window. Post-index
> information is follow-up, downstream care, or leakage.

Takeaway:

> Timestamps are not just features. They are guardrails.

### Scene 4: The HAPrI case

Headline:

> Hypoalbuminemia surfaced where clinicians would want to look: upstream.

What the viewer should see:

- The new `fig_hapri_discovery_handoff.svg`, or a simplified graph-only crop.
- Hypoalbuminemia highlighted in orange.
- Rediscovered HAPrI risks in blue/navy.
- HAPrI outcome at the end of the time flow.

Narrative role:

This is the result, but keep it hypothesis-generating. The most compelling
point is not "the algorithm found albumin"; it is that the algorithm found a
clinically plausible candidate in the right temporal location while also
recovering known risk factors.

Poster copy:

> The algorithm prioritized hypoalbuminemia as a candidate upstream node and
> rediscovered established HAPrI risks without hand-built features.

Takeaway:

> Discovery is strongest when it surprises us plausibly and recovers what we
> already know.

### Scene 5: The albumin trajectory

Headline:

> The signal lives on a relative clock.

What the viewer should see:

- Albumin aligned to HAPrI diagnosis.
- Day 0 marked clearly.
- Pre-index values emphasized.
- Post-index values shown but visually labeled as downstream/follow-up.

Narrative role:

This panel makes the result tangible. It shows why relative time matters: albumin
appears low before pressure-injury diagnosis and remains low after. The pre-zero
pattern can motivate a candidate upstream edge; the post-zero pattern cannot be
used as causal evidence.

Poster copy:

> Relative time aligns heterogeneous ICU stays around the target event. Only
> tau < 0 enters discovery.

Takeaway:

> The same lab value means different things before and after the index event.

### Scene 6: The handoff

Headline:

> A discovered edge is not the finish line.

What the viewer should see:

- Discovery -> clinician review -> target-trial protocol -> TMLE/g-methods.
- A clear "candidate, not confirmed" caveat.

Narrative role:

End with rigor. Object-centric discovery creates better candidate graphs and
better candidate estimands. It does not replace design, identification, or
effect estimation.

Poster copy:

> The graph prioritizes candidate edges. Clinicians arbitrate plausibility; a
> target trial defines the estimand; TMLE or longitudinal g-methods estimate the
> effect.

Takeaway:

> Discovery chooses the question. Causal inference answers it.

## Recommended poster layout

Top band:

- Title, authors, affiliations, ISPOR metadata.
- One-line thesis: "Flat tables create causal ambiguity; patient objects
  preserve the clocks that help resolve it."
- Small clinical hook: "Why did this ICU patient develop HAPrI?"

Middle band, three columns:

- Left: "The stall" - CPDAG/equivalence-class cartoon.
- Center: "The reshape" - patient object and relative-time guardrail.
- Right: "The HAPrI signal" - hypoalbuminemia graph plus rediscovered risks.

Bottom band:

- Albumin relative-time chart.
- Discovery-to-inference handoff.
- Caveat box: "Candidate upstream driver, pending clinician review and
  confirmatory target-trial/TMLE analysis."

## Figure sequence

Primary figure set:

1. `fig_cpdag_stall_cartoon.svg`
   - Message: flat discovery returns a CPDAG when arrows are empirically
     indistinguishable.
   - Use: left middle panel.

2. `fig_temporal_objects_orient.svg`
   - Message: object analytics preserves time and relational structure, which
     orients many candidate edges.
   - Use: center middle panel or full-width methods strip.

3. `fig_hapri_discovery_handoff.svg`
   - Message: hypoalbuminemia is a prioritized candidate; confirmation requires
     clinician review and causal estimation.
   - Use: right middle panel or bottom-right handoff.

Supporting figures:

- `fig_albumin_relative_time.svg`
  Use for the concrete HAPrI result. Consider simplifying the visual so the
  first read is "low before diagnosis, still low after."

- `fig_relative_time_guardrail.svg`
  Use if the poster needs a smaller methods inset than the full object figure.

- `fig_discovery_inference_pipeline.svg`
  Use as an alternate handoff panel if space is tight.

## Compelling intuitive takeaways

- The world is not flat; neither are patients.
- A flattened EHR asks the algorithm to infer time after we discarded it.
- CPDAG ambiguity is not an algorithm bug; it is information loss.
- Object analytics keeps the patient journey intact.
- Timestamps are hard constraints, not decorative metadata.
- Relative time turns "before vs after" into a reproducible feature rule.
- Discovery is a triage tool for causal questions, not a substitute for causal
  effect estimation.
- The best discovery result is both plausible enough for clinicians and
  surprising enough to be worth testing.

## Poster-safe language

Use:

- "candidate upstream driver"
- "prioritized for confirmatory analysis"
- "rediscovered established risk factors"
- "temporal and relational constraints orient many otherwise ambiguous edges"
- "hypothesis-generating"
- "target-trial/TMLE confirmation required"

Avoid:

- "proved cause"
- "albumin management prevents HAPrI"
- "the algorithm solved causal discovery"
- "temporal constraints eliminate confounding"
- "fully identified all edges"

## Short copy blocks

Problem:

> Traditional structure-learning algorithms assume a flat table. In EHR data,
> that flattening collapses the patient journey, removes event order, and leaves
> clinically different DAGs inside the same CPDAG.

Method:

> We represent each ICU admission as a temporally ordered patient object. Labs,
> medications, procedures, microbiology, diagnoses, and transfers remain linked
> to the patient and to event time.

Result:

> In MIMIC-IV v3.1 adult ICU admissions, object-centric discovery prioritized
> hypoalbuminemia as a candidate upstream driver of HAPrI and rediscovered known
> risk factors without manual feature engineering.

Caveat:

> The discovery graph prioritizes hypotheses. Clinician review and
> target-trial/TMLE or longitudinal g-methods are required before interpreting a
> candidate edge as an intervention effect.

## Source deck pull-through

High-value deck ideas:

- Slides 03 and 10: "why" motivates causal reasoning and targeted action.
- Slides 07-09 and 33: "the world is not flat" supplies the intuitive metaphor.
- Slides 11 and 14: patient as holistic object; MIMIC contains many event
  families that should remain connected.
- Slides 16, 21, and 23: albumin relative to pressure-ulcer diagnosis and
  relative-time guardrail.
- Slide 19: pressure-ulcer causal graph content, including albumin and yeast
  colonization.
- Slides 24-28: correlation vs causal contribution, Noisy-OR/ICI model, direct
  and higher-level search, time-ordered graph construction.
- Slides 29-30: contrast with flat-column DAG structure learning. Use the idea,
  but soften the claim for the poster.

Avoid direct-publication use unless permissions are confirmed:

- Gartner slide, YouTube screenshot, product screenshots with UI details,
  pressure-injury wound photos, and raw third-party imagery.
