# A mark states its edit up to three times and no field is authoritative

```
Status:   open
Progress: 1 of 3 tasks closed
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

Problem 3. A mark states its edit up to three times and no field is
authoritative [D-D2, N-N8; V12, V13]

- `claim`, `change` and `raw_text` each state the edit; `change`/`raw_text` change meaning for
  `add` and `move` (for `move`, `raw_text` is a different place's text).
- The brief says claim and change "are checked against each other"; nothing checks it.
  Executed probe (D): a `patch` whose `change` contradicts its claim settles on `change` with no
  reason; a `correct` gets only an advisory "for the chief" note. An `add`'s claim keys have no
  reader. `AddMark` carries both `anchor` and `named_anchor` (`claim.anchor` on the wire) (N-N7).
- Contrast (sound): the per-instruction rule tables with agent-facing shapes generated from code
  (`check --contract`, `distribute --shape`) (A, I).

## Tasks

- [ ] T1 | Determine which mark field is authoritative for the edit
        > 2026-11-23 Related: mark-defects.md, mark-holds-spec-and-parse.md
- [x] T2 | Ruled #413: the claim serves agents; no code check | 52ca7d9bb89ade8f8f05e427420286480890f17d | Reconcile
      the brief's claim-against-change check with what the code checks
- [ ] T3 | Determine what reads an add mark's claim keys
