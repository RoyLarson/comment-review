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

## Reconciliation -- the fold, the turn, `Determined` and `DiffMark`

**Deleted 2026-09-18, `0e2ff82a`.** How one stage's returned copies became the copy chief's own
before the middle was rebuilt. Five modules went together:

| what it did | where it lived |
| --- | --- |
| grouped every ruled mark of a `master_proof` by the addresses it lands on, then ruled each group `settled`, `escalations` or `rereads` | `desk/collator.py`'s `places`, `Placed`, `Reconciled`, `reconcile`, `_outcome`, `_join_moves`, `_touches` |
| the eleven-act fold -- envelope, check, coverage, verify, drift, dropped, assemble, place, reconcile, resolve, order -- returning a `Collated` | `flows/collate.py`, latterly `flows/_collate.py` |
| the turn loop: a batch out, the roles' answers back, the fold run again, the chief's dispositions, the close | `flows/turn.py`, latterly `flows/_turn.py` -- `run_turn`, `refold`, `apply`, `proof_after`, `determined_chief`, `batch_for`, `close` |
| the chief's ruling at a resolved place, as a record of its own | `desk/determined.py` -- `Determined`, `Answer`, `CHIEF`, `ORIGINAL` |
| the answer a role gave to an escalated place, and the batch it rode in | `desk/diff_mark.py` -- `DiffMark`, `DiffInstruction`, `batch_of`, `parse_batch` |

**What replaced it is a place, and a fold over places.** The rules that were branches in those
modules are rows in **three tables** -- `desk/marks/table.py`, `desk/answers/table.py`,
`desk/dispositions/table.py` -- and nothing outside the three names a row, which
`tests/gates/test_tables_name_the_rows.py` holds over the whole tree. A **place**
(`desk/evaluate/place.py`) carries its own base, the marks filed on it, its answers by turn and
the chief's disposition, and comes to one of **six states**: `stands`, `agreed`, `composed`,
`contested`, `unsettlable`, `refused`. Three **passes** (`desk/evaluate/passes.py`) take it there
-- `marks_pass`, `answers_pass`, `dispositions_pass` -- with `pair_moves` giving a move's two
places one state. The **Unit of Work** (`desk/work/fold.py`) evaluates every place and commits or
rolls back whole, emitting events rather than lists. The **bus** (`flows/bus.py`) is the one
entry: `CopiesReturned`, `AnswersReturned`, `DispositionsWritten`, one handler each, and
`collate`, `turn` and `disposition` each send one message.

### What the differential measured before it was deleted

**`tests/test_differential_collate.py` folded one real stage of four roles' copies through both
folds and compared every place.** It went with the old fold, which it could not run without; its
last result, 2026-09-18, over the smoke's own plant:

- **22 addresses compared, and 17 agreed exactly** -- same settled text, same carry-forward.
- **The old fold reported no problems** and determined 9 places; the new fold settled 10 and
  carried 11 forward, refusing nothing and committing.
- **The two unsettlable places were the same two**, `fib.py@a1` and `store.py@b5`.
- **The one advisory was the same one**: `block-context` at `store.py@c5`, where the `correct`
  carries its own change rather than the one its claim derives.
- **Five differences, each explained by a ruling, and no other:**

| address | why |
| --- | --- |
| `fib.py@b1`, `store.py@b1`, `store.py@b3` | rulings `#172` and `#175`: a move's `change` is the snippet it takes and its `raw_text` is the destination's text as it will stand, so the origin keeps what the snippet left behind. The old fold carried one mark under both addresses and settled the origin to the destination's text |
| `fib.py@c12` | ruling `#174`: a place every role cleaned is decided and alters nothing, so the new fold settles it with no text where the old recorded no ruling for it at all |
| `store.py@b8` | rulings `#155` and `#182`: a move a role holds for the human is held at both ends, so the new fold takes the destination out of what it carries and reports the pair as one question. The old fold held the origin alone and carried the destination forward |

**The addresses above are the plant's as it stood that day.** `store.py`'s closing gap was
`b8`; a fifth function was appended to the fixture later the same day, for a contested move the
chief could close, and the closing gap is `b10` from that commit on. The scenario at that row is
unchanged -- a move to the closing gap, held for the human.

### Reading an old artifact

**A `master_proof` written before the rebuild carries three keys nothing reads now** -- `turns`,
`determined` and `unsettlable`. `MasterProof.deserialize` names the keys it wants, so those three
are **neither refused nor read**: the proof loads, and they are dropped. What they held:

| old key | where the same fact lives |
| --- | --- |
| `turns` -- one record per turn, `{turn, sent, returned, revisit}` | each place's own `answers`, keyed by turn. `flows.bus.turn_of` reads the highest turn any place answered at, so nothing counts turns of its own |
| `determined` -- the chief's ruling per resolved place | the place's `state` and `text`, with its `disposition` where the chief ruled it |
| `unsettlable` -- `{address, roles, query}` per place riding to the human | the place's state, `unsettlable`, and its `asking` |

**A batch written before the rebuild carries a `diff` and no `sides`.** The old batch rendered a
`diff3` conflict per slot; the new one sends `{address, anchor, question, raw_text, sides,
instruction, read_from}`, where `sides` is role -> that role's proposed text and `question` is
`escalation` or `composition`. An old batch handed to `turn` is refused at `flows.answers`, which
reads the question off the slot it was sent with.

**A role's answer file is unchanged in shape.** It was a `DiffMark` -- `{address, anchor,
instruction, reason, change}` -- and an `Answer` reads the same keys, under a `question` the slot
carries rather than the answer. `hold`, `withdraw`, `correct` and `patch` still name the four
answers to an escalation; `check --contract` prints the sets from the tables themselves.


## Historical excerpts relocated from conventions -- 2026-10-27

These excerpts preserve the incidents removed from the operating conventions.
They describe the observations and terminology recorded at those dates, not
current instructions or current measurements. Use conventions.md and lanes.md
for the active rules.

### Test ownership -- 2026-08-24

!! **It does not own `tests/`, and this file said it did until 2026-08-24.** Roy: *"testing's
lane is specifically about building and testing the running agent system that is in the testing
harness branch. If it is backend testing that is on you. If it is vocabulary and system gating
tests that is systems. Running the tests for the agents is the agents responsibility, it is
testing's lane to make the grader and keep the grades."* **A test is owned by the lane that owns
what it makes a claim about** -- the table is in [`lanes.md`](lanes.md), the ruling is
`decision-log.md Process: #5`.

**The cost of the old row is the one it was measured on.** Two `record.py` regressions were
filed to `testing` on 2026-08-24 because they landed in `tests/` -- shipping a backend fix with
nothing able to notice it regress, and parking the test on a lane whose work is a grader on
another branch.


### Vocabulary drift -- 2026-08-23

!! **The cost of waiting is measured.** A rename that stopped at the code left 32 quoted rulings
and 31 uses of a retired word in prose an agent reads, past a green suite, `ty`, `ruff`, the
floor gate, the vocabulary gate and the corpus round trip -- see
[`evidence/rename-left-history-in-the-comments/`](../evidence/rename-left-history-in-the-comments/README.md).
Every gate answered a different question, and the only thing that could have caught it was the
lane that did the renaming saying so on the other side.


### Field necessity and carryovers -- 2026-08-30 and 2026-08-31

**The MEASURED failure is A field that answers neither.** `desk/mark.py` declared
`owes_destination` and **nothing read it**: measured 2026-08-30,
`grep -rn "owes_destination" src/` returned three lines and all three were in the file that
declares it. A flag nobody reads cannot make the system correct and serves no purpose,
and it survived because no plan ever had to say what it was for.

**SUPERSEDED the same day, and the way it was SUPERSEDED is the point.** `f17b712`
gave the flag a reader -- `parse` now runs `_destination_problems` under it, refusing a
`move` whose `claim.to` equals its own address. The grep returns five lines, one of them a
read. **The measurement above stands as of its date and the rule it argues for is
unchanged; what moved is the example.**

**A field does not become necessary by being wired -- It becomes necessary when something
would otherwise be wrong.** Here something was: a move onto its own address reached the
docket as a bare delete, so the flag now answers *what would be incorrect without it*. That
is the answer this section asks for, arriving a plan late rather than never. The three
lines were the honest reading on the day; leaving them uncorrected would make this section
an instance of the rot it exists to forbid.

Roy, 2026-08-31, on why two vestigial fields had to go that day while a third could wait:
**"The others were hurting because you were actively designing them into the system instead
of letting them drop because they were not necessary."*

| | what it was | what happened |
| --- | --- | --- |
| `original_column` | where a trailing comment began on a line that starts with code | I read it in a NEW page type, and reasoned about whether a redacted paragraph could carry it |
| `declares` | which declaration a docstring documents, as an ordinal | I proposed a REPLACEMENT MECHANISM for it, measured that mechanism failing, and filed a ruling request on the strength of it |
| `lines` | how many lines a paragraph stands on | nothing. It sits there, 11 writes and 1 read |

**The first two were urgent because I was spending design on them.** Not because they
cost anything at rest -- a dead field costs nothing at rest. What they cost was every
decision taken while assuming they were load-bearing: a `RedactedParagraph` argued for, an
anchor-matching scheme invented and measured, a plan step filed as needing a ruling that no
ruling was owed on. **Each of those was work produced by the field rather than by the
PROBLEM.**

**And the third is left in, deliberately.** Roy: *"that thread probably needs pulled a
little more carefully and it isn't hurting yet to leave it in."*


### Value tracing -- 2026-08-31

The former conventions used this trace of the implementation then under review:

```text
lexer     held.declares = ordinal
attach    cues.documents(declares)
Cues      self.addressers[DECLARED].at(ordinal)
at        got = cue_for(self.series, step)
cue_for   return f"{series}{step}"          <- the terminus: it rebuilds `a3`
```

**Roy ran that chain and had the answer before any measurement was taken.** 2026-08-31,
after two sessions of my evidence pointing the other way: *"you tried very hard to convince
me that those were necessary even though I had already followed the full chain on logic
determining they were dead."*

| what I asked | why it answered nothing |
| --- | --- |
| *is it read* | always yes for a field with a reader. One hop, no terminus |
| *does it agree with the address* | the address is computed FROM it -- 11,702 agreements that could not have come out otherwise |
| *does my replacement work* | it did not, and that is a fact about my replacement. Anchor TEXT was never the key; the ordinal already was the cue |

!! **Do not WRITE this rule as a self-check.** An earlier wording of it said *"the test is
not is it dead but AM I REASONING FROM IT"* -- which asks for introspection in the moment,
and Roy named that plainly the same day: *"you are not very good at introspection or seeing
the global shape of the code."* It is the fault `CLAUDE.md` already records for boxes --
**"is this a verifiable checkpoint" is a judgement; "does this box open with implement,
update, delete, or a question" is a reading* -- arriving on a field instead of on a task.
**Trace the chain, which is a reading. Do not ask yourself how you feel about it.**


### Task headings and filing -- 2026-08-30

Roy, 2026-08-30: *"This very thing made an earlier session completely jump a bunch of
steps in a plan ... The task headers made it easy to skip past a set of tasks and start
working on the next section of tasks."*

!! **A new file is the exception and has to earn itself.** MEASURED 2026-08-30: **34 of
159 open TODOs carry three tasks or fewer**, two of them ONE, against a mean of 7.3 over
1,155 tasks. Re-derive with `grep -h "^Progress:" TODO/*.md`. Each was a defensible
filing on the day it was made; what they add up to is a board whose index is longer than
most of the work in it, where a reader scanning `TODO/README.md` cannot tell a SUBJECT
from a single observation.


### Shipped prose -- 2026-09-27

This stood above `NOT_THE_TERM` in `scripts/check_vocabulary.py` until 2026-09-27, when a
comment-review run found nothing there enforcing it and Roy ruled that it lives here.

## Historical excerpts relocated from instructions -- 2026-10-28

These excerpts retain the wording and observations removed from the parent
and limitations guide. They are historical records, not current rules.
The lane-crossing excerpt overlaps the Vocabulary drift entry above; the
current crossing permissions are in conventions.md.

### Generated output -- 2026-09-05

**And `plugins/` is assembled, not written.** `scripts/release.py` deletes it and rebuilds it
from two sources, WHOLESALE -- sub-packages intact, because Roy ruled the shipped tree takes
the same shape as the source: the Python in **`src/comment_review/`** with its launcher, and
the prose an agent reads in **`src/plugin/`** -- `agents/*.md`, `SKILL.md`, `references/*.md`
and `plugin.json`, laid out as the plugin is. **Edit `src/`; all of `plugins/` is output.** It
is rebuilt at release only, so between releases it lags and nothing reddens over that. The
gate that held the two equal per change went on 2026-09-05; Roy: *"It is just noise in the
development."*

### Type-check scope -- observation retained from the parent

!! **`ty` runs bare, covering both trees.** `[tool.ty]` in `pyproject.toml` sets
the scope, not a path typed on the command line. Before that, `tests/` sat outside
every ty run and four real `invalid-argument-type` errors there passed a green
suite, `ruff check`, `ty check` and the floor gate, because nothing was ever
pointed at `tests/`.

### Full quotations -- 2026-08-22

!! **A shortened quotation is not a shorter rule; it is a different ONE.** Roy, 2026-08-22:
*"I am pretty certain that the session cut out the important part when it shortened it."* And
nothing marks a cut: this tree writes `--` for an em-dash because of the ASCII rule, so an
elision and a dash are spelled the same. **When a ruling is quoted here, quote all of it** -- the
commit that first recorded it is the source, and `git log -S` finds it.

### Lane crossing -- superseded parent summary

**Four lanes own this repo, and a TODO's `Owner:` is one of them.** Roy runs sessions in
parallel, each opened as *"You are the `backend` -- I need you to ..."*, and **the lane scopes
what you may change.** If a task touches a file another lane owns, **name the lane and ask**.

| lane | owns, in one line |
| --- | --- |
| `agents` | **What an agent is TOLD, and how the roles hand off** |
| `backend` | **What the Python actually does** |
| `testing` | **How well the running system does, and what that is scored against** |
| `systems` | **Whether it installs, and whether the gates still bite** |

!! **The vocabulary is shared and crossing is the point.** Roy, 2026-08-23: *"any side can and
should update the vocab on the other side as soon as a split or modification is noticed."* It is
the ONE standing exception to *name the lane and ask*, and the cost of waiting is measured --
`evidence/rename-left-history-in-the-comments/`.

**And a lane that trips A gate fixes its own code**, never the gate. A gate edited to pass is
indistinguishable afterwards from one that always passed.

### Role-file measurements -- 2026-08-18

**The four editorial roles, measured 2026-08-18:**

| agent file (`plugins/comment-review/agents/`) | lines |
| --- | --- |
| `comment-review-ownership-context.md` | 111 |
| `comment-review-block-context.md` | 117 |
| `comment-review-function-context.md` | 124 |
| `comment-review-module-context.md` | 130 |

!! **THREE OF THE FOUR HAD GROWN, AND THAT IS THE EVIDENCE, NOT THE DEFECT.**
`ownership-context` 91 -> 111, `block-context` 110 -> 117, `module-context` 128 -> 130. Roy,
2026-08-18: *"I have allowed expansion on those files just because of this"* -- because the
rules added paid in one of the two currencies above. **A replaces-one rule that was live would
have refused all three**, so the file was describing a policy it was not running, and the growth
is what proves it.

### Shared-file measurements -- August and September 2026

!! **THE TWO LARGEST FILES A RUN LOADS AS CONTEXT HAVE NO BUDGET.** A reviewer loads its role
file plus the brief, and **the brief is read FIVE times** -- by the four reviewers and by the
task agent. Roy, 2026-08-18. So a line there costs five times a line in a role file, and the
numbers above budget the ROLE files only -- the smallest part of what a run actually costs.

| | 2026-08-16 | 2026-08-18 | 2026-09-12 | 2026-09-14 | |
| --- | ---: | ---: | ---: | ---: | --- |
| `reviewer-brief.md` | 11,579 | 23,397 | 38,090 | 37,754 | paid FIVE times |
| `SKILL.md` | 45,257 | 62,531 | 60,037 | 62,242 | paid once, by the task agent |

The 2026-09-12 column is each file's stored blob, `git show HEAD:<path> | wc -c`, after five
commits (7d2e1834 to 3b0314e6). The brief grew 1,964 bytes: what a role answers in a turn and
the `f` run a role may act on, net of the blank-line rule it dropped. `SKILL.md` grew 2,128: the
turn run between `collate` and `disposition`, and exit 7's row.

The 2026-09-14 column is the same measure at ebe58e91, against 37,288 and 60,383 at a22eb0ec:
the brief's 466 bytes and `SKILL.md`'s 1,859 bought stage 8's read of the proof before 7a, 7a's
questions on a held move and a correct that drops words, `disposition`'s printed lines, 7b's
temporary files, a per-file split of each role, and a role that fills its one copy itself and
calls LSP only when it holds the tool, net of the annotation table and prose that went.

!! **THE BRIEF HAS MORE THAN DOUBLED IN TWO DAYS, WHICH IS THIS WARNING COMING TRUE.** Every
addition was argued on its own and none was weighed against the file, because nothing measures
it -- the four role files are counted line by line while the thing costing four times as much
is not. ! Re-measure it whenever it is edited and say what the growth bought, the same
discipline the role table gets. ! Larger files ship -- `census.py` is 31 KB -- but
are EXECUTED, never read into a prompt.

The August shared-file units were not stated in the source and remain
unverified. The September columns explicitly measure stored bytes; the
role-file table above measures lines. These are dated records, not current
measurements.
