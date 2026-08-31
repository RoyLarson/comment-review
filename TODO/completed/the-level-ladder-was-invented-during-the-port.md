# The level ladder was invented during the port and nobody asked for it

```
Status:   COMPLETE 2026-08-16
Progress: 7 of 7 tasks done
Owner:    session * Roy (ruled 2026-08-16)
Raised:   2026-08-15 (Roy: "Where did the 'levels' come from? Those weren't in the
          original format, and I didn't ask for them.")
Re-filed: 2026-08-16 (Roy: "Make certain to todo covers the removal of this
          LEVELS = ('fact-check', 'line', 'full', 'proof')")
```

## Objective

**`level` gates which verdicts a reviewer may emit, and it has no provenance.** Traced with
`git log -S`: the ladder exists at **zero commits** in `redacted_corpus`, on any branch. It
was invented during the 2026-08-14 port, and its whole stated justification was one budget
measurement.

! **It is load-bearing where it exists.** `verdicts.py:281` refuses a verdict outside the level's
set, so at `fact-check` a true-but-misplaced block cannot be `move`d and becomes `query`; at
`line` no reviewer may `patch`. Removing it is not deleting a table -- it is deciding that every
verdict is admissible on every run, and then removing the rules written to work around the
restriction.

! **Ruled NOT a vocabulary question**, which is why it needed a home of its own. This is it.

! **Recorded because it was nearly lost.** It was item 6 of `TODO/README`'s branch status, and
the 2026-08-16 re-derivation dropped it -- nothing else in the tree carried the finding. Filed
here so a status rewrite cannot lose it again.

## Ruling, 2026-08-16

Roy: *"I am 100% certain there are not 'levels' allowed anymore."* The ladder goes ENTIRELY,
`proof` included. Every verdict is available on every run and all four roles run every time.

Removed: `LEVELS` and the `LEVEL` packet section from `run_context.py` (REQUIRED 9 -> 8, and
the checkable answers 3 -> 2); `LEVELS`, `allowed()` and `--level` from `verdicts.py`; the
ladder table and its four notes from `SKILL.md`; two `fact-check` carve-outs from the
ownership-context agent; the `level` definition from `vocabulary.toml`. `reviewer-brief.md`
carried none by the time this ran.

! The three TRUE statements the ladder carried survive in another form:

| was | is |
| --- | --- |
| *"`ownership-context` runs at every level, including `fact-check`"* | *"`ownership-context` is read FIRST"* -- same reason, no ladder |
| *"if `move` is unavailable, NO level reaches the cap"* | *"if `move` is unavailable, the cap is out of reach"* |
| *"every reviewer that RAN, not four: at `fact-check` only three run"* | *"every reviewer that ran"* -- all four always do |

! **A retraction was written and removed on Roy's ruling.** The first draft said *"There is no
`level`: no restricted verdict vocabulary..."*. Roy: *"all of the new agents would never know
the history and have to care that there was such a thing as a level... you care because I
haven't run clear on you."* A statement that something was removed is written for a reader who
knew it existed, and no fresh agent is one. The line now states the fact alone.

## Tasks

- [x] T1 | FINISHED | unknown | * Rule whether the ladder goes entirely or keeps
      one rung. `proof` is the odd one: it carries NO verdicts and exists only
      to run stage 8 over files a previous pass edited -- which stage 8's own
      agent now does directly. `fact-check`, `line` and `full` are the
      restriction proper.

- [x] T2 | FINISHED | unknown | Remove `LEVELS` from
      `sk-scripts/run_context.py:96` and its validation at `:246-247`, and the
      `LEVEL` section from the dispatch packet at `:55`. !
      `tests/test_run_context.py` asserts the packet's section list; a removed
      section is a fixture change, and the last time sections were removed the
      fixture broke by absorbing the body of one heading into the next.

- [x] T3 | FINISHED | unknown | Remove `LEVELS` from
      `sk-scripts/verdicts.py:65-70`, the `allowed()` membership test at `:281`,
      and `--level` at `:438`. ! `--level` has a default of `full`, so a caller
      that never passed it is unaffected; one that passes `--level fact-check`
      breaks at argument parsing, which is the intended failure.

- [x] T4 | FINISHED | unknown | Remove the ladder from `SKILL.md:183-208` -- the
      table, *"`ownership-context` runs at every level"*, *"the ladder changes
      shape and that is the point"*, and *"if `move` is unavailable, NO level
      reaches the cap"*. ! Each of those states something TRUE that has to
      survive in another form: ownership-context runs first because a claim
      attached to the wrong scope gets measured against the wrong code, and an
      unavailable `move` still means COMPACT caps prose that cannot leave.

- [x] T5 | FINISHED | unknown | Remove it from `ref/reviewer-brief.md:5` (*"a
      restricted `level` runs fewer"*) and `:131-136` (*"The LEVEL you were
      given restricts which verdicts you may emit"*). ! That second passage also
      carries the `fact-check` special case for ownership-context, which is the
      same rule as above stated for the reviewer.

- [x] T6 | FINISHED | unknown | Check what else keyed on it. `move`'s
      availability, `query`'s use as the fallback when a relocation verdict is
      not carried, and `clean`'s meaning for a true-but-misplaced block are all
      written against a level. Grep `fact-check` before declaring this done.

- [x] T7 | FINISHED | unknown | ! Fix the dangling recommendation in
      `the-task-agent-emits-the-vocabulary`, which offered `LEVELS = (...)` as
      the idiom to copy for a `--reviewer` selector. If `LEVELS` is deleted,
      that model goes with it -- and since the floor moved to 3.11 on
      2026-08-16, `StrEnum` is available and is what that selector should use. !
      **Closed 2026-08-16 without an edit being needed:** that task shipped as
      `vocabulary.py`'s `Reviewer(StrEnum)`, so the recommendation was never
      taken and `LEVELS` is deleted here. Nothing copied the model.
