# Names reach four persisted layers before their meaning settles

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-11-23 (broken review, 2026-11-23)
```

## Objective

From the broken review of comment-review at 6a81c7b0
(feat/0.2.4-what-a-reviewer-is-handed), 2026-11-23. Evidence codes cite the
review's perspective outputs (W workflow, A architecture, D domain, I
implementation, N names, V vocabulary). The solution phase has not run; nothing
below is a recommendation.

Problem 9. Names reach four persisted layers before their meaning settles [N-N1,
N-N2, N-N4, N-N6, N-N9..N13; V1, V2, V4, V23, V25, V26]

- ~30 open rename tasks across 9 TODO files: a name is written into Python, the JSON wire, CLI
  flags and agent prose, with nothing translating between the layers (N-N2).
- The write chain is one job with five names; `compositor` names three things; two docstrings
  disagree on whether the galley rules (N-N1). `proof` means five things (V1).
- `desk` holds no desks (in SKILL.md a desk is a role's seat); `desk/proof` holds the mark
  model; `fold` is central and defined nowhere (N-N4). `Refused` x4, `Place` x2, `Source` x3
  (N-N6). `Series` member names match neither the letters nor the words agents are taught
  (N-N10). `ruling` keeps the judicial register (N-N12). The stage-8 proofreader agent is
  `comment-review-review` (N-N9).
- Contrast (sound): `prove_unchanged`, `referrers`, `gather`, `distribute`, `collate`,
  `MasterProof`, docket/schedule/alteration, `recast`, `query`, `cue`, `disposition`.

## Tasks

- [ ] T1 | Determine where a name's meaning settles before it reaches a
      persisted layer
        > 2026-11-23 Symptom: the-roles-are-named-for-what-they-read.md
        > 2026-11-23 Symptom: shape-is-three-words.md
        > 2026-11-23 Symptom: row-was-never-retired.md
        > 2026-11-23 Symptom: settle-carries-two-meanings.md
        > 2026-11-23 Symptom: task-agent-vocabulary-home.md T9
- [ ] T2 | Determine what carries a renamed term across the Python, wire, CLI,
      prose layers
        > 2026-11-23 Related: vocabulary-has-one-source.md T2
