# evidence -- what this system is measured against

**The prose defects the tool is scored on, and the runs scored against them.** Probe reports over
real codebases, the triage that ranked them, `ga/ground_truth.py` and the candidate rewrites it
scores, plus captured end-to-end runs.

! **Nothing here describes this system's own behaviour** -- that is [`docs/`](../docs/). A
measurement of the tool's OWN prose is a `docs/` document however much it reads like a finding;
the vocabulary survey was filed here once for exactly that reason and moved.

## !! THE TERMS CHANGED ON 2026-08-23 AND NOTHING HERE WAS REWRITTEN

**Every file in this directory is a record of a run that happened, so it keeps the words that were
current when it was captured.** Renaming inside a captured run would make it describe something
that never happened.

**From `326af1a` (2026-08-23) onward, the shipped tree says:**

| what these files say | what the system says now |
| --- | --- |
| `foliator.py` | `addresser.py` |
| `folio` | `cue` |
| `foliation`, `Foliation` | `cues`, `Cues` |
| `foliate()` | `cue()` |
| `folio_of` | `cue_of` |
| `leaf` (of a page or a place) | retired -- there is no leaf in the model |
| `block` | `paragraph` |
| `pCST`, `prose tree` | `page` |

! **The ADDRESSES themselves are unchanged.** A `path@b3` written before that commit resolves
today, because only the names of the machinery moved and never the address strings. What will not
resolve is a command line: `foliator.py --census ... --anchor` is `addresser.py` with the same
flags.

! **Why each word moved** is in [`docs/history.md`](../docs/history.md); **what was decided and
when** is in [`docs/decision-log.md`](../docs/decision-log.md).

## Older shapes, already noted where they live

- **Record files here are all in the FLAT shape**, and the reader for the retired one is at
  `a74a037^`. `docs/history.md` says how to replay one.
- **`todo-tool-full-run/` holds TEXT reports**, which the current tool cannot read; that package's
  own `PROVENANCE.md` says so and says that bringing them forward is separate work.
