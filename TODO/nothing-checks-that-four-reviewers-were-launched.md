# Nothing checks that four reviewers were LAUNCHED

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session · Roy (⭐ 1 ruling)
Raised:   2026-08-17 (a live run's transcript reads "3 background agents launched" and names
          three roles; the count is unexplained and nothing in the run objected)
```

## Objective

**`⚠⚠ Every verdict is available on every run, and all four roles run every time`** is stated in
`SKILL.md` and enforced by nothing at the moment it matters.

What exists today, and where each check sits:

| check | where | when it fires |
| --- | --- | --- |
| the four agents RESOLVE | `SKILL.md` 1.6 | stage 1, before anything is dispatched |
| every expected reviewer REPORTED | `verdicts.py --reviewers` | stage 5, after the reports are in |
| a report stem is a published role name | `verdicts.py` | stage 5 |

⚠ Nothing between them. **1.6 proves the agents can be dispatched; nothing proves four were.**
The gap is the dispatch itself, and it is the one step the skill cannot inspect: `run_context.py`
runs before it and `verdicts.py` runs after.

⚠⚠ **`--reviewers` catches it LATE and that is the whole cost.** A three-role dispatch is
detected only once three reviewers have read the census and written their reports — on a large
run that is several hundred thousand tokens and twenty minutes before the run learns it was
invalid. And it is only caught at all if the task agent passes `--reviewers`, which is optional.

⚠ Why the invariant is not a formality: `SKILL.md` records that **a single-role run ratifies
falsehoods** — one role reading a false absence claim writes that it is true, where another
refutes it by grep. A three-role run is the same defect, weaker. And the missing role's blocks
are not gaps the join can see: it computes coverage from the reviewers that REPORTED, so three
complete reports read as complete coverage unless `--reviewers` names the fourth.

## Tasks

- [ ] ⭐ Rule on WHERE the check goes. There is no artifact between the packet and the reports
      for a script to read, so the candidates are: (a) the task agent states the four agent
      names in the PROPOSAL and the human sees a short list, (b) `--reviewers` stops being
      optional and defaults to the four editorial roles, (c) a stage-4 line in `SKILL.md`
      requiring the dispatch be re-read and the count stated before waiting on results.
      ⚠ Recommendation: (b) plus (c). (b) costs nothing and removes the optional-ness that lets
      a short dispatch through silently; (c) is the only one that fires BEFORE the tokens are
      spent, and it is prose because there is nothing there to check mechanically.

- [ ] Make `--reviewers` default to the four editorial roles rather than to `""`. Today its
      absence is announced — *"whether every expected reviewer reported was NOT checked"* — and
      an announcement in a wall of output is not a gate. ⚠ Check what this does to a deliberate
      single-role run; if that is a thing anyone does, it needs an explicit way to say so.

- [ ] Say in `SKILL.md` stage 4 that the dispatch is COUNTED, and that four is the number.
      ⚠ It must name the failure: a short dispatch is not detected until stage 5, after the
      reviewers that did run have spent everything.

- [ ] Decide whether a missing role is FATAL at stage 5 or a stated degradation. It is fatal
      today via `--reviewers`. ⚠ Fatal is probably right — the alternative is a proposal that
      reads like a four-role run and is not — but the ruling should be written down rather than
      inherited from an implementation detail.

- [ ] ⚠ Record what actually happened on 2026-08-17, and record it as UNEXPLAINED. The
      transcript shows three agents named and launched. The session's own account addresses a
      vocabulary-encoding question and does not account for the count. Do not write a cause
      into this file that nobody established — the point of the task is that the run had no
      mechanism to notice, whatever the cause was.
