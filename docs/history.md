# History -- what this system used to DO and stopped doing

!! **STOP. IF YOU ARE CLAUDE, DO NOT READ ON -- ask whether you should.** This file describes
mechanisms and file formats that no longer exist. Reading it puts retired shapes into your context
beside the live ones, where nothing tells them apart. `docs/vocabulary.md` and
`docs/addressing.md` carry the same warning for the same reason.

**What this file is for:** a thing this system used to do is REMOVED rather than shimmed, and the
removal is recorded here with the commit that made it. Roy, 2026-08-20: *"we are not carrying a
backwards compatible shim right now ... git can recover them if we ever need to figure out how
that was done."* So the code is in the history and this says WHERE to look and WHAT you would
find.

! **It is not a changelog.** `CHANGELOG.md` says what each release changed; this says what a
reader of an OLD artifact needs to know to make sense of it. An entry earns its place by being
something someone could still hold in their hand -- a file on disk, a captured run -- and no
longer be able to read.

---

## The reviewer's report: two retired shapes

**Retired 2026-08-20 in `a6da8ad`**, on the branch after 0.2.3. Before that commit, `verdicts.py`
read three shapes; after it, one.

### 1. The 0.2.x TEXT report

The first shape a reviewer returned. Prose with records in it, and the tool ignored everything
around them:

```
--- RECORD
BLOCK       17 | redacted_pkg:billing:rates.py@b47
            # Kept because twenty call sites want this.
VERDICT     correct
SOURCES     redacted_pkg/billing/rates.py:355 | def compute_rates(plan, period):
CLAIM       false: "twenty call sites" / true: "31 callers, all in tests/"
REASON      31 callers and every one is under tests/, so the count is stale
CHANGE      # Kept because 31 callers want this, all of them in tests/.
---
```

!! **A FIELD RAN UNTIL THE NEXT LABEL AT COLUMN 0, and every boundary was a guess.** That is why
it went: a malformed citation was absorbed into the valid one above it, a bare label into the
field above it, a dropped span took the punctuation beside it -- and each of those reported its
error against work that was CORRECT. The replacement is a template a reviewer FILLS, where a
missing field is visibly empty rather than absent.

! **`BLOCK n` keyed by census POSITION**, with the address after a `|` added later. An index is a
position in ONE census, so it is only meaningful against the census the report was written
against -- and a census built today of the same source is a different list. **A report keyed by
index alone cannot be placed at all**, which is why the converter refused rather than guessing.

### 2. The flat JSON `records` list

The template that replaced the text report, and the shape every record file on disk carries
before the page envelope:

```json
{ "record_version": "1", "reviewer": "block-context", "allowed": { ... },
  "records": [ { "address": "redacted_pkg:billing:rates.py@b47", "anchor": "...",
                 "verdict": "correct", "claim": {...}, "reason": "...",
                 "sources": [...], "change": [...] } ],
  "code_concerns": [] }
```

!! **EVERY RECORD REPEATED ITS PAGE'S PATH.** Measured over this repo's own 15 shipped scripts:
**33,228 bytes per reviewer, 132,912 across four** -- more than every `anchor` in the file
combined, and the anchor is the field a reviewer greps. The page envelope that replaced it names
the file once and each record cites the folio alone.

**The current shape**, for contrast:

```json
{ "pages": [ { "page": "redacted_pkg/billing/rates.py",
               "records": [ { "place": "b47", ... } ] } ] }
```

### What went with them

Nothing else ever filled or read these, so they left in the same commit:

| gone | what it was |
| --- | --- |
| `held.parse_report`, `held.convert`, `held.code_concerns`, `held.claim_object` | the text reader and its converter |
| `held.address_of` | translated a census INDEX to an address |
| `Finding.block` | the index itself -- only the text reader set it |
| `record.OPENER`, `record.CODE_CONCERNS` | regexes for the text report's sections |
| 41 tests | their subject was the parser, not the gate |

! **`held.py` went from 612 lines to 186**, and the shipped tree stopped needing the
`# noqa: vocabulary` exemption at all -- that file said `BLOCK` because it had to read reports
that spell it that way, and no shipped file says it now.

### Reading an old artifact

!! **EVERY RECORD FILE UNDER `evidence/` IS IN THE FLAT SHAPE.** All 8 of them, in
`evidence/cycle-0.2.3/records/` and `evidence/comment-review-skill-023-dev-review/records/`. They
are records of what happened, not inputs: no script, eval or gate reads one, which is what made
deleting the reader safe. **If you need to replay one, the reader is at `a6da8ad^`** --
`git show a6da8ad^:plugins/comment-review/skills/comment-review/scripts/held.py`.

! **The older packages under `evidence/todo-tool-full-run/` hold TEXT reports**, and that
package's own `PROVENANCE.md` already says they are unreadable by the current tool and that
bringing them forward is separate work. It was true before this commit too: the converter refused
an index-keyed report, and those reports are index-keyed.
