# `results` -- the WRITE END: setting the proposal as text, and proving what it did

**Started 2026-09-07 for `prove_unchanged`, under
[`decision-log.md`](../../decision-log.md) *Process: #104*.** The other three modules carry
their one-line subject below and nothing more yet; sections 4 to 6 are written for
`prove_unchanged` alone. A reader wanting `compositor`, `differences` or `galley` today reads
their module docstrings, which is where their design still lives.

## 1. What this package is for

It turns a ruled proposal into text on a page, sets that text as files a reader can gather like
any tree, and answers whether the setting changed anything but prose.

## 2. What it may import, and what may import it

**The WRITE END.** It reaches DOWN to a leaf -- `machine`, `reading`, `concordance` -- and never
across to `binder` or `desk`. A flow hands it what it needs; a flow is neither end and runs the
steps. See [`conventions.md`](../../conventions.md), *No direct coupling between the ends and
the middle*.

! **One crossing is measured and filed, not fixed:** `results/compositor.py` imports `Page` and
`page_for` from the read end. Recorded in `conventions.md`'s table of four couplings, 2026-08-31.

## 3. Each module: what it owns

| module | owns |
| --- | --- |
| `compositor.py` | sets a page as TEXT, in memory, top to bottom. It decides nothing |
| `differences.py` | renders the difference between two texts, and composes them where disjoint |
| `galley.py` | the proposed text SET AS FILES, so it can be read and gathered like any tree |
| `prove_unchanged.py` | whether the setting changed anything but prose |

## 4. `prove_unchanged` -- the shape

**The gate compares one value: each page's `{cue -> anchor}` mapping, before the setting and
after it.** Equal means the setting changed no code. Anything else is a refusal.

The mapping is `Cues.places`, built by the addresser: `emit(anchor, trigger)` stores
`places[cue] = anchor`, and **the anchor is the line of code verbatim** -- `paragraph.py` says
so at the field, quoting Roy: *"the anchor isn't the technical symbols and their precise
semantic meaning and code use. It is 'the line of code' -- the exact characters in that line of
code."*

### Why the mapping and not the address set

`flows/revise.assert_addresses_held` compares `known_addresses`, which is the address SET. A
code line whose characters change under a stable cue keeps its address, so the set holds and the
mapping does not. The mapping is the stronger of the two and is what this gate takes.

### What moves it, and what does not

MEASURED 2026-09-07 over `src/comment_review/binder/binder.py`, 176 places:

| the edit | the mapping |
| --- | --- |
| a comment's text rewritten in place | holds |
| a comment line deleted outright | holds |
| a comment line added | holds |
| a TRAILING comment rewritten on its own code line | holds |
| one code line's characters changed | moves |
| a code line deleted | moves |
| prose written over a code line | moves |

**Trailing whitespace on a code line does not move it, and that is correct.** The anchor is the
line right-stripped -- `page.py`'s `code_lines` takes a code line's characters from that line's
own `c` place, which the lexer already cut, and the `margin` standing in for one stores
`lines[n - 1].rstrip()`. The `c` *"already states where the code stops"*, so whitespace after
that point is not code by this system's own definition.

**Every code line is carried as some place's anchor.** MEASURED 2026-09-07 over four files in
two languages: 0 code lines missing from the mapping. That is what makes the comparison able to
see a change anywhere in the code rather than only where prose happens to sit.

### Both sides are bound fresh

**The binder the run has carried since stage 2 is never one of the two sides.** It is the
artifact that produced the write, so reading it as the before side would compare the write
against its own input.

[`gates.md`](../../gates.md) holds the measured case for why that is fatal: the round-trip
identity scored **699 of 699 on its first run** while 157 addresses were held by two paragraphs
each, because it rebuilt each file from the line positions it had just read out of that file and
so could not disagree. It began finding things one commit later, when it was made to set from
the cues instead.

### It reads no git, and takes no `--base`

Roy, 2026-09-07: *"The reason it can't be git is because we could be running this on uncommitted
work, to prepare it for a commit. So using git as the source of truth would negate that
ability."*

**File identity is answered upstream and is not this gate's question.**
`flows/proof_setter.py` refuses when `held.sha != recorded`, naming both values, before the
composition. Roy, 2026-08-25: *"the sha is what says the file is still the one the agents
read."* So the sha proves the file is the one the run started from; this gate proves the
identity held across the setting. Neither needs a commit to exist.

### Three outcomes

| | exit | means |
| --- | --- | --- |
| **held** | 0 | the mapping is equal; the setting changed prose only |
| **moved** | nonzero | the mapping differs; WRITE's claim does not hold |
| **no page** | 0 | out of scope, and never counted among the proven |

**A file with no page is out of scope for one of two reasons, and the report says which**,
because they wait on different things:

| out of scope because | comes back in through |
| --- | --- |
| it is CODE in a language with no record yet | a data row on the language table |
| it is NOT CODE -- Markdown, docs, references | its own read, review, resolve and write chain |

!! **NEITHER IS PERMANENT AND NEITHER IS WRITTEN AS THOUGH IT WERE.** Roy, 2026-09-07: *"those
will never have a language but they will be editable eventually."* A doc is not waiting on a
language record and must not be reported as if it were; it is waiting on
[`a-non-code-document-has-no-read-review-resolve-or-write-chain-of-its-own`](../../../TODO/a-non-code-document-has-no-read-review-resolve-or-write-chain-of-its-own.md).
This is the same treatment `CLAUDE.md` records for the empty `a` lists, where *"the list could
never be complete"* was corrected to a deferral naming what it waits on.

## 5. Why it is this way

| the constraint | what produced it |
| --- | --- |
| one comparison, no tiers | the AST proof, the comment-stripping proof and the `unprovable` class each answered a different question per language; the mapping asks one question in every language the gather reads |
| both sides bound fresh | [`gates.md`](../../gates.md)'s 699 of 699 |
| no git | the system runs on uncommitted work being prepared for a commit -- `Process: #104` |
| no line-ending comparison | MEASURED 2026-09-07 on `claude-settings`: comparing a page's endings to an untouched SIBLING file reported `4 unproven` on a clean tree with nothing written, on a repository-wide LF/CRLF mixture |

## 6. What is provisional

!! **THE CODE DOES NOT DO THIS YET.** As of 2026-09-07 `results/prove_unchanged.py` still holds
the AST proof, the comment-stripping proof, `code_fingerprint`, `dominant_ending`, `_sibling`,
`_show` and `_spec`, and `commands/prove_unchanged.py` still requires `--base` and calls
`git show`. This section is the ruling in `Process: #104`, not a description of the tree.

**What the shape rests on**, stated as premises rather than as a list of ways it might fail:

- Every code line is some place's anchor. Measured over four files; it is a property of the
  addresser's trigger walk, not of those files.
- The sha check fires before composition, so file identity is already settled when this runs.
- A page can be bound from bytes alone, without a repository, so neither side needs git.

**Open, and Roy's to settle:** whether this and `flows/revise.assert_addresses_held` become one
check or stay two at different points in the chain. Both bind fresh on both sides; they differ
in what they compare and where they run.
