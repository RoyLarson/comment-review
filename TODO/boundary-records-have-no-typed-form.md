# Records crossing boundaries have no single typed form

```
Status:   open
Progress: 0 of 5 tasks closed
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

Problem 5. Records crossing boundaries have no single typed form [D-D3, D-D4,
D-D5, I-F3, I-F4, I-F5, I-F8; V6, V8, V31]

- Address: an `Address` value type exists and nothing carries it; every consumer re-parses the
  string; three resolvers turn the path half back into a file; series letters are exported as
  string aliases with `Series` member names (against Process #34) (I-F3). Most
  `one-obvious-way` address tasks are symptoms.
- Edit copy: the typed `EditCopy`/`Sheet` drops null slots, so `fill`, `withdraw`, slot lookup
  and distribute counts walk the raw dict by hand (D-D3, I-F5).
- Refusal reasons: at least seven record shapes plus `"role: why"` strings the desk writes and
  `fold._by_role` splits back with `partition(": ")`; #353 decided a flow returns reasons, not
  their shape (I-F4, D-D4). Four `Refused` classes (V31).
- Derived state trusted: turn and disposition decide from the saved `state`/`owed`, the fold
  re-derives them, nothing compares; places and moves share a string key namespace
  (`"origin -> destination"`) told apart by an empty `to` (D-D4).
- `Paragraph` is filled over several steps; `address == ""` means both "leading" and "not yet
  addressed"; ~20 sites re-filter `if b.address` (D-D5). Answers table keyed `(Question, str)`
  with a union row type forces three runtime guards in two places (I-F8).
- Contrast (sound): the Docket's three typed levels; `CARRIED`/`SETTLED` named once (A, D).

## Tasks

- [ ] T1 | Determine the typed form an address takes across boundaries
        > 2026-11-23 Symptoms: most one-obvious-way.md address tasks (T1-T8, T25)
- [ ] T2 | Determine the typed form an edit copy takes across boundaries
- [ ] T3 | Determine the typed form a refusal reason takes across boundaries
        > 2026-11-23 Related: exception-hierarchy.md; one-obvious-way.md T23
- [ ] T4 | Determine which state turn and disposition trust, the saved or the
      re-derived
- [ ] T5 | Separate a leading paragraph from a not-yet-addressed one
