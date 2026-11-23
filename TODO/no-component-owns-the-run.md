# No component owns the run across stages

```
Status:   open
Progress: 0 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-23 (broken review, 2026-11-23)
```

## Objective

From the broken review of comment-review at 6a81c7b0
(feat/0.2.4-what-a-reviewer-is-handed), 2026-11-23. Evidence codes cite the
review's perspective outputs (W workflow, A architecture, D domain, I
implementation, N names, V vocabulary). The solution phase has not run; nothing
below is a recommendation.

Problem 1. No component owns the run across stages [W-F1, A-F1, D-D1, N-N3; V3,
V5, V11]

The stage chain is modelled in Python, run by prose, and the two disagree.
- `desk/topology.py:264-281` `seeded_from_problem`: the stage named in `reads =
  "revise:<stage>"` is parsed into `earlier` and used only in a message. Any binder whose root
  matches and whose revise is non-zero passes. Executed (W): 4c seeded from the original
  checkout gathered with `--revise 1`, skipping 4a entirely; distribute exited 0.
- SKILL.md stage 4 builds root4c by worktree + hand copies of proof4a and freeform drafts
  (rulings #295, #367). A root4c missing proof4a's pages drops 4a's settled changes and every
  command exits 0 (A, static trace).
- `proof` stamps every pull `revise=1`; the revise number a later gather records is whatever the
  agent types (D). `pulls_revise` has no caller; `Kind.ENRICHING` no producer;
  `Stage.carries` is parsed and refused if non-empty (A, I).
- Executed (W): `proof --only` on one 4c place produced a draft that deletes a comment 4a moved,
  with no draft for the destination file. The author's approval can only address the last
  stage's places (D).
- The reviewer brief tells 4c and stage-6 roles that the file they open is the run-start
  original, false at those stages (D, N-N3). The brief's own instruction (run from REPO ROOT,
  no `--repo` on `check`, `reviewer-brief.md:43,:431`) fails at 4c: 19 refusals vs exit 0 with
  `--repo` (W-F2; binder root stored relative to the gather's cwd, ruling #164).
- Contrast (sound): within a stage, `proof` refuses a page whose sha differs from the proof,
  and refuses one end of a move under `--only` (W).
- Board symptoms: stage-4b-is-undefined, containers-and-verification-are-unwired T61/T72,
  move-is-a-composite-mark T56 (4c gather omits moved-into files).

## Tasks

- [ ] T1 | Determine which component owns the run across stages
        > 2026-11-23 Solution phase running; recommendation to follow (broken review)
        > 2026-11-23 Symptom: stage-4b-is-undefined.md
        > 2026-11-23 Symptom: containers-and-verification-are-unwired.md T61, T72
        > 2026-11-23 Symptom: move-is-a-composite-mark.md T56
        > 2026-11-23 Symptom: topology-defects.md T1, T5
        > 2026-11-23 Correction: T61/T72 are Place deserialize, not the run chain
- [ ] T2 | Make a seeded stage start from every earlier stage's settled changes
- [ ] T3 | Make the author's approval reach every stage's places
