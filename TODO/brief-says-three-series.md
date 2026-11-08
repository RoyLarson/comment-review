# The brief says three series, and the addresser answers four

```
Status:   open
Progress: 7 of 10 tasks closed
Owner:    agents
Requires-Roy: false
Raised:   2026-08-29 (found sweeping reviewer-brief.md against its consumers on
          feat/the-mark-and-the-collator, 2026-08-29)
```

## Objective

`reviewer-brief.md:69` says *"The three series are counted by three separate addressers"* and
`:221` offers a `--series` flag naming only `a`, `b` and `c`. `reading/series.py`'s `ADDRESSED`
is `('a', 'b', 'c', 'f')` and `SKILL.md:378` says four -- so a role cannot resolve the `@f0`
place the same brief tells it to cite at `:74`.

## Tasks

- [x] T1 | Ruled #274: any role may mark an f place; each mark asks the human | faf59d1f | Decide
      what a role is told about the f series, and make reviewer-brief.md:69
      agree with SKILL.md:378
- [ ] T2 | Fix the --series a\|b\|c example at reviewer-brief.md:221 to the set
      the addresser command actually accepts
- [x] T3 | Ruled #274: an f place is citable by any role, not read-only | faf59d1f | Reconcile
      with reviewer-brief.md:74-79, which calls @f0 the file's own matter,
      filtered out of the census and not a place a role rules on -- if that
      still holds, say which of the four a role may cite and which it may only
      read
- [x] T4 | a role may act on an f run it reads as a comment | 7627b266 | Update
      reviewer-brief.md:67-72 and :88-97 so a role may act on an f run it reads
      as a comment
        > 2026-09-11 what the brief says is ruled in Addressing 25
        > 2026-09-11 Addressing 26: expected to be matter, may not be
- [x] T5 | RULED Addressing: #25 -- move to a b place, human asked first | dd5dc235 | Decide
      which instructions an f place takes, and whether a licence or a shebang
      keeps any protection
- [x] T6 | SKILL.md asks the author before an f move or correction | f279f3a1 | Update
      SKILL.md so the task agent asks the human before a move out of the f
      series goes ahead
        > 2026-09-12 Roy 2026-09-12: goes with T7's plan, not set 4
- [x] T7 | collate raises each f correction on ASKS_THE_HUMAN | f279f3a1 | Implement
      a workflow that raises each correction to an f place to the human on its
      own for approval
        > 2026-09-11 Addressing 26, Roy: that probably needs its own workflow
        > 2026-09-12 Roy 2026-09-12: its own plan and branch, not set 4
        > 2026-09-12 reviewer-brief :86-90 states the routing since 7627b266
        > 2026-11-04 Per #274, every mark on an f place raises this query
        > 2026-11-07 #287: backend -- the desk raises an f correction as a collate exit
        > 2026-11-07 #289: raised on ASKS_THE_HUMAN, a pause; no new exit code
- [x] T8 | #287: the desk raises it as a collate exit code | 4c9bf66d | Decide
      at which stage each correction to an f place is raised to the human, and
      what the human is shown
- [ ] T9 | Make the other roles mark against an f-to-b move the human accepted,
      per #274
- [ ] T10 | Update reviewer-brief.md so any role may mark an f place it looks
      up, per #274
