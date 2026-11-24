# "Would the fold refuse this?" has no single owner

```
Status:   open
Progress: 2 of 3 tasks closed
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

Problem 2. "Would the fold refuse this?" has no single owner [A-F3, I-F1, I-F2,
W-F5; V36]

Each entry point assembles its own admission checks, and they disagree.
- Executed (I): a copy with an altered sheet sha, or an altered `stage`, passes `check` (exit 0,
  "0 thing(s) the fold would send back") and `collate` refuses it (exit 1). `check` is what the
  agents use to validate their own copies. `flows/bus.py:~365-378` documents the gap itself.
- Executed (W): "every dispatch returned" is enforced only when the optional
  `collate --topology` is passed; without it one of three 4c copies folded to a closed proof at
  exit 0. What a stage admits comes from the topology row only with `--topology`; otherwise the
  copy's own field binds (A).
- `verify.py` keeps `x` / `admitted_x` pairs to serve two of the assemblies; three plain
  versions are called only from tests (I; board item 6, computed-and-never-read T21).
- The underlying invariant "this page is read the way it was gathered" (path, sha, reading
  context) is copied by value into every artifact and re-admitted at ~17 sites; `regather`
  appears 46 times; `_reading_contexts` switches on five types plus raw dict (I-F2).
- Reconciled disagreement: W reports check and collate agreed in every run; I reports they
  disagree. Both hold: W's runs used untampered copies; the disagreement is on copies whose
  sha/stage/admits fields were altered, and on a missing dispatch without `--topology`.
- Contrast (sound): turn answers share one validator, `answers_of`, in check and the turn (A).

## Tasks

- [x] T1 | flows.verify.admit owns fold admission | c0b134dd1a8dfa0b93b5fbcadbc7b73748afd935 | Determine
      which component owns fold admission
        > 2026-11-23 Solution phase running; recommendation to follow (broken review)
        > 2026-11-23 Symptom: computed-and-never-read.md T21
        > 2026-11-23 Symptom: one-obvious-way.md T3
- [x] T2 | One admit; tamper table agrees; one injected rule refuses at all four | c0b134dd1a8dfa0b93b5fbcadbc7b73748afd935 | Make
      one admission rule decide a copy for both the check and the collate
      commands
- [ ] T3 | Make what a stage admits independent of whether --topology is passed
        > 2026-11-23 Jacket path done in beafb27d; closes with the old flags' deletion
