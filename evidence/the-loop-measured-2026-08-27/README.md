# The loop, measured -- 2026-08-27

Four rounds of the editorial roles run over this repo's own source, to measure **the mark shape
and the review loop**. Roy, 2026-08-27: *"more important than the reviews themselves is the
process."*

    binder -> review -> marks -> collate -> revise -> review -> collate -> ... -> alterations

## What this package is evidence FOR

The **process**: what a mark must carry, which places a flow can settle without waking anyone,
whether a second pass converges, and what one review round costs. It is the record behind
`decision-log.md Process: #33` and the open tasks in
[`the-fields-do-not-say-a-mark-may-cite-across`](../../TODO/the-fields-do-not-say-a-mark-may-cite-across.md).

!! **IT IS NOT EVIDENCE ABOUT THE FILES THAT WERE REVIEWED.** The roles read four real modules
and ruled on their prose. Those rulings are not reproduced here, and no judgement any role or any
session formed about this repo's code style is carried into this package. **The subject is the
instrument, not what the instrument was pointed at.** Roy, 2026-08-27, setting the scrub: *"It
doesn't need the opinions of the agents or you about the judgements of this packages code
style."*

## What is here, and how to re-derive it

| file | what |
| --- | --- |
| `measurements.md` | every number, each naming the command that prints it |
| `the-loop.md` | the ten steps as run, and which cost an agent |
| `the-mark.md` | the seven fields, and what each verdict owes |
| `marks.jsonl` | one line per mark -- routing only, no prose |
| `source-roots.json` | where the roles' citations pointed |
| `derive.py` | prints every number in `measurements.md` |

```bash
uv run python evidence/the-loop-measured-2026-08-27/derive.py
```

!! **THE NUMBERS ARE DERIVED, NOT TRANSCRIBED, AND THAT CAUGHT TWO ERRORS.** Writing `derive.py`
before the prose disagreed with figures that had already been quoted into commit messages: a
citation count taken over the four role stems alone **excluded the fan-out agents entirely** (292
across 6 roots, where the full set is 382 across 9), and a consistency figure could not be
reproduced at all until the key was found to be `(role, address)` rather than the claim text.
This repo's own rule -- *a count is safest beside the command that reproduces it* -- is why the
script exists rather than a table.

## What `marks.jsonl` holds, and what it deliberately does not

One line per mark:

    round  role  fanout  address  path  address_carried_path
    verdict  claim_sha  n_sources  has_ran

`claim_sha` is a 12-character digest of the normalised sentence a mark ruled on. **It makes
agreement countable across rounds without reproducing one sentence of anyone's prose**, which is
what lets the raw 919 KB of role output stay out of this tree.

! **`reason` and `change` ARE NOT HERE.** They are where a role argues about the code, at length
and verbatim, and they are the material the scrub is aimed at.

## What cannot be re-derived from this package

| | why |
| --- | --- |
| the wall-clock and token costs | timings of agent runs; nothing in the data records them |
| *the non-overlap is misses, not false positives* | three findings were spot-checked by hand against the source |
| the revise pass catching a regression | read from the role's answer text, which is not carried here |
| whether any individual finding was correct | that is a judgement about the reviewed code, deliberately excluded |

! **The figures in that column are stated in `measurements.md` and marked as not re-derivable
here.** They are kept because they are specific enough to be checked against a NEW run, which is
the only thing that would settle them -- the same standing this repo gives the 31-defect
measurement in `CLAUDE.md`.

## Lane

`evidence/` is `testing`'s. This package was built by the `backend` session that ran the rounds,
at Roy's request, and is filed rather than owned -- *the lane that FOUND it files it; the lane
that OWNS it works it.*
