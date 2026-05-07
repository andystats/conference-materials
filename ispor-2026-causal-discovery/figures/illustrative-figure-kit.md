# Illustrative figure kit

Draft poster figures for the ISPOR 2026 causal-discovery narrative. Each
figure has an editable draw.io source and a matching SVG export. The current
drafts use the simpler ACIC-style visual language: wide comic-strip panels,
large nodes, sparse text, and one dominant accent color per idea.

## Narrative sequence

1. `fig_cpdag_stall_cartoon`
   - Use for: why classic discovery stalls.
   - Caption: Flattening strips away event order. Several DAGs then share the
     same skeleton and no collider, so the honest output is a CPDAG with
     unoriented edges.
   - Technical guardrail: the example uses three chain/fork DAGs with the same
     skeleton and no unshielded collider, so they are Markov-equivalent.

2. `fig_temporal_objects_orient`
   - Use for: the object-analytics move.
   - Caption: Patient objects keep event timestamps attached. Pre-index events
     can become candidate parents; post-index events are excluded as leakage.
   - Technical guardrail: temporality constrains orientation; it does not remove
     confounding or estimate effect size.

3. `fig_hapri_discovery_handoff`
   - Use for: HAPrI case-study close.
   - Caption: Hypoalbuminemia is prioritized as a candidate upstream driver of
     HAPrI, alongside rediscovered known risks. The edge is a hypothesis; the
     effect requires clinician review and target-trial/TMLE confirmation.
   - Technical guardrail: keep the claim as candidate/hypothesis-generating,
     not a proven intervention effect.

## Editing workflow

Open the `.drawio` file in diagrams.net/draw.io, edit the shapes directly, then
export over the matching `.svg` file for website or poster use.

If a revised SVG is going into the scripted poster build, regenerate
`poster/png_cache/` before rebuilding the PowerPoint.
