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

!! **AND REMOVING A THING IS NOT A REGRESSION HERE. THIS IS `0.x`, WHICH SAYS SO.** Roy,
2026-08-21: *"my project -- 0 dependencies, 1 user (me), my rules. I would rather drop bad stuff
now and leave no memory while it is easy, rather than leave residues of stuff that will not make
it. Also the v0.X is stating ALL things are subject to shifting. Zero-vers are specifically for
that -- no guarantee of any stability."*

! **A REVIEWER WILL READ A DELETION AS A REVERT, and it is worth knowing why that reading is
wrong.** A code review of 2026-08-21 called the flat-report refusal *"the exact regression commit
1541697 fixed and 2a86573 reverted"* -- true as a description of the diff, and not a defect: the
first commit taught the reader an old shape and the second removed the shape on a ruling. What
IS a defect is failing SILENTLY, and that half was real and fixed.

! So the test for an entry here is not "was something removed" but **"can someone holding an old
artifact still find out what it was"**. That is all this file promises, and all a `0.x` owes.

---

## The LINE address -- `path:start-end`

**Retired as a NAMING at 0.2.4; the reader deleted 2026-08-20.** How this system named a paragraph
before a place was defined:

```
redacted_pkg/billing/rates.py:33-34
```

!! **IT IS TRUE OF ONE FILE STATE ONLY, and this tool EDITS PROSE** -- every prose edit moves the
line numbers of the code below it. Measured 2026-08-18 on a prose-only edit to a single docstring:
**2 of 3 prose paragraphs took a new line address, and 0 of 3 took a new folio.**

!! **AND IT NAMED TWO DIFFERENT THINGS WITH NO WAY TO TELL WHICH.** On a paragraph holding prose,
`33-34` is the lines that prose occupies, inclusive. On an INTERVAL it is the two lines of CODE
that BOUND a gap -- so the same string means "lines 33 through 34" in one case and "between 33 and
34" in the other. Reading the KIND, or the `0L` count, was the only way to know.

! **`foliator.line_address()` survived to read it**, warning on every call, on the same argument
the report reader used: to parse runs already recorded. It was deleted 2026-08-20 with **zero
callers anywhere** -- not in `plugins/`, not in `tests/`, not in `scripts/`. Found by a codegraph
sweep for shipped symbols nothing uses.

## The SPLICE -- how a change reached a file before the compositor

**Deleted 2026-08-21.** Every edit this system made was a line rewrite. `galley.py` held
`splice`, `overlaps`, `splice_range`, `paragraph_matches` and its own `line_endings`, and a
change was a tuple:

```
(start, end, column, replacement)     1-based, inclusive; column 0 = whole lines
```

!! **APPLIED IN DESCENDING ORDER, WHICH IS WHAT MADE THE RANGES MEAN ANYTHING.** A replacement
rarely has the same number of lines as what it replaces, so splicing top-down shifted every range
below the one just written. Overlaps were refused up front so descending order could be exact.

!! **THE `column` WAS ADDED BECAUSE A SPLICE REPLACES WHOLE LINES.** A `patch` on
`z = 3  # trailing` wrote `# reworded` over the statement -- measured 2026-08-18, in the galley a
human is asked to approve. Keeping `line[: column - 1]` wrote the prose and left the code.

!! **AND IT COULD NOT INSERT.** An empty gap has no lines, so its range was `n+1 .. n` and the
arithmetic for landing BETWEEN two code lines was never got right. **8 tests were
`@unittest.expectedFailure`** for exactly that: the insertion between two lines, deleting no code,
the gap above the first line, the gap below the last, and telling the two boundary gaps of a
one-line file apart. All 8 now pass through `galley.reset` -- see
`tests/test_galley.py::TestAnAddIntoAnEmptyGap`.

! **What replaced it**: a page addresses its paragraphs and `compositor.set_page` walks the
reading order, so a change is an ASSIGNMENT to one paragraph. Nothing shifts, so there is no order
to apply in, no overlap to refuse, and no column -- the compositor sets the line of code and joins
what sits beside it.

! **The staleness check went with it.** `paragraph_matches` compared stored text against the
file's lines and needed a case per kind. It is `compositor.transcribes` now, one comparison,
because `leading` made every paragraph contiguous. What the GALLEY checked instead was
`drifted` -- the anchor, per Roy's ruling 2026-08-21: *"the reset should only check if the address
is tied to the anchor line of code - like they claim."* `drifted` itself was later retired -- see
"`galley.drifted` -- the anchor and prose staleness check" below.

! **To read the mechanism**, it is at `e1a6baf` -- `git show
e1a6baf:plugins/comment-review/skills/comment-review/scripts/galley.py`.

## `galley.drifted` -- the anchor and prose staleness check

**Deleted 2026-08-25.** `drifted(page, census)` compared, for every addressed paragraph, the
anchor and `raw_text` the census recorded against a freshly re-parsed `page` built by reading the
file again and running it through the full lexer -- an anchor that no longer matched refused the
whole file, and (since 2026-08-22) so did prose whose `raw_text` had changed since the census.

! **Why it went**: a sha comparison over the file's text answers the same question -- has this
file changed since the census was taken -- in one comparison, before anything is parsed. Rebuilding
the page and diffing every paragraph did the same job at a much higher cost, for no more
certainty: any change to the file changes its sha, so the anchor-by-anchor and prose-by-prose walk
`drifted` did was answering a question the sha already settles.

! **To read the mechanism**, it is at `0f99805^` -- `git show
0f99805^:src/comment_review/results/galley.py`.

## The `galley` COMMAND -- a second write chain, with its own rules

**Emptied 2026-08-26.** `commands/galley.py` was ~200 lines that took `--census` and `--edits`,
resolved each address to a file through `rows_of(census)`, compared the census's recorded sha
against the file, placed the edits with `galley.reset`, and wrote one draft per page under
`--out`. It kept its own copies of four things `flows/proof_setter.py` also does: the
`--out`/`--repo` disjointness refusal, the per-file containment guard, the staleness comparison,
and the draft loop.

! **Why it went.** Roy, 2026-08-26: *"We have a single entry point for the system? These delegate
through to the commands? Create the galley entry_point function that points to proof_setter and
delete the unused command."* And on the shape: *"there is no reason to go to the galley for
something that proof-setter is supposed to do."* The module is now the OLD NAME for `proof` and
calls `proof.main()`.

!! **THE NAME IS ALL THAT CARRIED OVER.** `galley` took `--census` and `--edits`; `proof` takes
`--binder` and `--notations`. A `SKILL.md` stage still spelled the old flags when this landed, so
the old invocation reaches `proof`'s parser and is refused -- tracked in
`TODO/the-skill-names-commands-that-moved-to-prototype.md`.

! **Where the measurements it was the exemplar for now point.** Three findings were recorded
against this file and are still true of the system: the 2026-08-22 overlap that wrote a draft over
the file under review at exit 0 (`repo.undraftable` is the rule now, in one place), the two copies
of that one rule in two commands, and the 2026-08-25 staleness gap that placed every edit from a
stale census at exit 0. They are cited here rather than at a file that no longer holds the code.

! **To read the mechanism**, it is at `175c4bf` -- `git show
175c4bf:src/comment_review/commands/galley.py`.

! **The stub that was left behind went too, later the same day.** Emptying
`commands/galley.py` down to `return proof.main()` still left a module whose
whole body forwards -- a standing invitation for a reader to file "this module
does nothing." Roy: *"If the alias is forwarded you can drop the file and they
have nothing to complain about."* The alias moved into `__main__.ALIASES`,
which maps `"galley"` to `"proof"` and imports that module directly; the file
is gone. To read it, `git show 1119cb3~1:src/comment_review/commands/galley.py`.

! **The alias itself went 2026-08-28, once the reason for keeping it did.**
`ALIASES` existed for one caller -- `SKILL.md` still typing `galley` at stage
7a -- and it existed to avoid editing that file. Roy, 2026-08-28, on being
told accurate command instructions are this lane's job either way: *"Since we
have determined that correcting commands in the brief and usage instructions
is something you should do can we drop galley as a command? Since it is an
alias and a workaround for not editing the agents files."* `SKILL.md` now
invokes `proof` directly with the flags it actually parses -- `--repo`,
`--docket`, `--out` -- and `__main__.py` no longer carries an `ALIASES` dict
or the resolution step that read it. `test_galley_DELEGATES_to_proof` in
`tests/test_proof_command.py`, which pinned the alias, went with it rather
than being weakened to keep passing.

## Constants that outlived their reader

**Deleted 2026-08-20**, all four found by sweeping the index for shipped names nothing reads:

| gone | what it was for |
| --- | --- |
| `record.OPENER` | counted `--- RECORD` openers, to catch a record that never closed |
| `record.CODE_CONCERNS` | found the text report's last section |
| `record.PATHISH` | told a MALFORMED citation from the WRAPPED TAIL of the entry above -- a question only the text report could ask, since a `SOURCES` entry there ran across lines |
| `record.ANCHOR_SIDE` | matched `above`/`below` in an `add`'s payload. The concept was removed on purpose: the ADDRESS says which side |

! **RUFF CANNOT SEE ANY OF THESE.** It flags an unused import and an unused local; a module-level
constant nobody reads is invisible to it. `ANCHOR_SIDE` survived long enough to be found by a
review agent READING the file, and three more went dead inside a single session with no gate
noticing.

## The reviewer's report: two retired shapes

**Retired 2026-08-20 in `2a86573`**, on the branch after 0.2.3. Before that commit, `verdicts.py`
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
deleting the reader safe. **If you need to replay one, the reader is at `2a86573^`** --
`git show 2a86573^:plugins/comment-review/skills/comment-review/scripts/held.py`.

! **The older packages under `evidence/todo-tool-full-run/` hold TEXT reports**, and that
package's own `PROVENANCE.md` already says they are unreadable by the current tool and that
bringing them forward is separate work. It was true before this commit too: the converter refused
an index-keyed report, and those reports are index-keyed.

## `foliator.py`, `folio`, `Foliation` -- the words the addressing scheme was built under

Renamed 2026-08-23 in `3f661d6`. An artifact written before that date says `folio` where the
system now says `cue`, and names a module that no longer exists. **Nothing about the SCHEME
changed** -- the same places, the same series letters, the same `path@...` shape, and the corpus
round trip returned the same three numbers over the same 3,153 files before and after. Only the
words moved:

| was | is |
| --- | --- |
| `foliator.py` | `addresser.py` |
| `folio` -- the `@` half | `cue` |
| `Foliation` -- every place on one page | `Cues` |
| `foliate()` -- the walk | `cue()` |
| `folio_of` | `cue_of` |
| `folio(series, step)` -- build one from its parts | `cue_for(series, step)` |

! **`cue_for` is not a straight rename.** `foliate()` and `folio(series, step)` both mapped onto
`cue`, in one module, where Python keeps the last definition -- so it had to be split, and it was
named for its direction: `cue_for` BUILDS a cue, `cue_of` takes one apart.

### Why the words went

!! **`folio` was wrong about its own referent.** A folio numbers a leaf or a page; the `@` half
names a POSITION WITHIN a page -- `b3` is the fourth gap. `references/vocabulary.toml` shipped the
error as a definition -- *"a leaf's number in publishing, which is what it is here"* -- and agents
were given it. ! A **cue** is the mark in the text saying a note belongs at this point: it carries
no content, only the position, which is exactly what the `@` half asserts.

! **`leaf` went with it, and had been contradicting itself.** One shipped definition said
paragraphs run DOWN a leaf (a leaf is the page); another said the numbering was *"of LEAVES, which
is what a place is"* (a leaf is the place). A leaf is one SHEET carrying TWO pages, so it could be
neither -- and a file has no verso, so there is no leaf in this model at all.

!! **`foliator` was a name that had been RIGHT and PREMATURE.** It was `addresser.py` until
2026-08-20, when Roy ruled the name wrong on the grounds that the module *"supplies the folio and
flattens the path, and addresses nothing."* ! The observation underneath was true and the
diagnosis was not. Roy, 2026-08-23: *"My frustration when I made the ruling was that it wasn't
being used as an addresser. It was something that was included because I stated it needed to be
included and then the rest of the program continued working in trying to use lines as the
address."* **The name promised addressing the system was not yet doing**, so renaming the module
treated a true observation as a naming defect, and the line-based addressing it was really about
survived another two days.

! **What settled it was the round trip, not an argument.** Roy: *"it reliably round-trips the
stuff after being entirely decomposed in the system without knowing anything about the original
lines."* A page is taken apart into places and set back from the places alone.

### Reading an old artifact

! **A record or census written before `3f661d6` is still readable** -- the addresses in it are
unchanged, because only the NAMES of the machinery moved and never the `path@...` strings
themselves. What will not resolve is a reference to the module: `foliator.py --census ... --anchor`
is now `addresser.py` with the same flags.

! **`TODO/completed/`, `CHANGELOG.md`, `docs/plans/` and `evidence/` keep the old words on
purpose**, each for its own reason -- see `evidence/README.md` for the one that needed a note
saying from which commit the terms changed.

