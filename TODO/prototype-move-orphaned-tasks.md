# The 2026-08-25 prototype move orphaned task sites across a quarter of the backlog

```
Status:   open
Progress: 0 of 4 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-08-28 (2026-08-28, after a third separate task was found pointing at a
          module that no longer runs -- the P3 implementer declining to tick two of
          them, having 'never read or ran' the prototype code they name)
```

## Objective

**MEASURED 2026-08-28: 25 open TODOs carry at least one UNCHECKED task naming a module that moved
to `prototype/` on 2026-08-25.** `record.py`, `verdicts.py`, `desk.py`, `held.py`,
`run_context.py`, `vocabulary.py`.

    a-block-is-a-paragraph-on-a-page            a-coverage-gap-should-go-back-to-the-reviewer
    a-malformed-page-drops-its-records          assertions-that-gate-a-substring
    code-concerns-cannot-carry-a-proposed-change   computed-and-never-read
    correcting-one-copy-strands-the-reference-copy docstrings-need-their-own-address-series
    docstrings-that-contradict-themselves       evidence-still-names-places-by-line
    front-half-undetermined                     held-runs-need-a-one-off-migration
    language-rows-in-toml                       no-mark-for-let-it-stand
    one-stem-four-jobs                          ownership-is-read-first-but-nothing-makes-it-so
    record-and-verdicts-disagree                record-verdict-desk-findings
    stage-4b-is-undefined                       stale-claims-after-the-envelope
    the-census-is-mostly-intervals-nobody-rules-on  the-emitted-vocabulary-can-collide-with-the-repo
    verdicts-is-the-join                        versioning-at-v1
    vocabulary-gate-is-red

!! **THE NUMBER IS A CANDIDATE SET, NOT A DEFECT COUNT, and T1 is what separates them.** A task
saying *"make `record.py:453` use `filled()`"* names a SITE that no longer runs -- its
verification cannot be performed by anyone. A task saying *"`verdicts.py` did it this way"* is a
CITATION, and citing a captured record is legitimate. **Only the first kind is broken**, and which
is which needs a per-file read.

## Why it went unnoticed

The move was one commit. `prototype/` *"is a record of how it worked. Nothing imports it, nothing
ships it, it does not run"* -- so **every gate stayed green**: nothing imports the moved modules,
so no test broke, no type check failed, no build gate fired. **The only artifacts that pointed at
them were prose, and nothing reads prose.**

! That is this repo's own recurring shape -- see
[`evidence/rename-left-history-in-the-comments/`](../evidence/rename-left-history-in-the-comments/README.md),
where a rename left 32 quoted rulings and 31 uses of a retired word past a green suite, `ty`,
`ruff`, the floor gate, the vocabulary gate and the corpus round trip.

## How it surfaced, which is the argument for the sweep

**Three separate sessions hit it one at a time, each thinking it was a one-off:**

| when | which | how it showed |
| --- | --- | --- |
| 2026-08-28 | `record-and-verdicts-disagree` T4 | ticked, then UNTICKED -- its verify named routing in a module that does not run |
| 2026-08-28 | `the-emitted-vocabulary-can-collide` T5 | triage found its target file moved; the task now waits on another TODO |
| 2026-08-28 | `record-and-verdicts-disagree` T5, T6 | the P3 implementer **refused to tick them**, having *"never read or ran"* the prototype code they name |

!! **THE THIRD IS WHY THIS IS FILED.** An implementer declining a box because it could not verify
what the box asks is the system working -- and it is also the third time in one day, which makes
it a property of the backlog rather than of any one file.

## What a ticked box is supposed to mean

`CLAUDE.md`: a ticked box must be **re-derivable by a stranger**, including someone who did none
of the work. **A task whose site is in `prototype/` cannot be re-derived by anyone** -- there is
nothing to run and nothing to change. It is not merely stale; it is unfalsifiable, which is the
one property this repo refuses in a comment and should refuse in a checkbox.

## Tasks

- [ ] T1 | Measure which of the 25 are SITES and which are CITATIONS. A task
      saying 'make `record.py:453` use `filled()`' names a site that no longer
      runs; one saying '`verdicts.py` did it this way' is a citation and is
      fine. Verify: every one of the 25 is labelled site or citation, and the
      count of each is recorded here.
- [ ] T2 | Re-anchor every SITE onto the live module that inherited its subject,
      or say plainly that the work no longer has one. Verify: no unchecked task
      in `TODO/` names a `prototype/` path as the place to change, and each re-
      anchored task's verification can be run by a stranger.
- [ ] T3 | Close what the move already settled. Some of these tasks describe
      defects in code that was REPLACED rather than moved, so the defect is gone
      with it. Verify: each such file is completed with an outcome naming the
      work that replaced it, not marked superseded -- a defect fixed by other
      work is an ordinary completion.
- [ ] T4 | Say how this is prevented. The move was a single commit on 2026-08-25
      and nothing swept the backlog after it. Verify: either a gate refuses an
      unchecked task naming a `prototype/` path, or `docs/conventions.md` states
      that moving a module means sweeping `TODO/` in the same change -- and
      whichever is chosen is the one that exists.
