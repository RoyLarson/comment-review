# Change Log

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

! This file starts at 0.1.2. Earlier work is in `git log` and has no entry here -- the
file existed as a one-line stub until this release.

!! **From 0.2.1 the plugin states its own version.** `plugin.json` carries a `version` field
and `tests/test_release.py` holds it equal to the newest heading here. Before that it carried
none, so the plugin cache named its directory for the COMMIT --
`roy-local/comment-review/7a0945ad3f40/` where an official plugin has `code-simplifier/1.0.0/`
-- and `claude plugin list` reported that hash. **A run could not be attributed to a release**,
which cost a real evidence package its attribution on 2026-08-17. `.claude-plugin/marketplace.json`
still carries no version; `claude plugin tag` validates the two against each other when one is
present.

! **The number does not track breaking changes, and never has.** Roy, 2026-08-16: *"these will
continue to be bugfix versions. I know that is not really how developed systems are supposed to
go but this is mine now."* Every `0.1.x` carried breaking renames and stayed a patch. **Do not
read a released number here as a semver claim.**

!! **Each MINOR bump has its OWN gate, and the gates are named in advance.** Roy, 2026-08-17:
a completed run *"was the justification for going from 0.1.x -> 0.2.x. That is not the gate for
0.3.0."* The number tracks a ladder of capability, one rung at a time. **A rung is not reached
by accumulating changes**, however many or however breaking.

| release | its gate |
| --- | --- |
| `0.2.0` | **cleared 2026-08-17** -- the system made it all the way through a run. No earlier version did: *"the previous tests did not, so I think they still deserved the 0.1.x statements even with significant breaking changes in them."* |
| `0.3.0` | **open, and MEASURED FAILING** -- Roy: *"it runs on my code bases and reliably makes things better."* |
| `0.4.0` | **open** -- Roy: *"verified this works across the other languages claimed."* |

!! **`0.3.0`'s gate is checkable, and it has already been run.** Roy, 2026-08-17: *"reliably
means that the session agent doesn't revert changes after the system runs because the changes
made things wrong/worse -- its words and its evidence."* **A post-run rollback is the failure
signal**, and it is a good one: the operating session states its reason in writing, and the
result is a fact about the tree rather than a score anyone assigns.

! **The one run that reached the end was ROLLED BACK.** `evidence/todo-tool-full-run/`, run 2,
2026-08-17 -- `redacted_corpus` branch `todo-requires-roy` at `REDACTED_SHA_D`, 3333 blocks and 171
holding prose, ~40 edits applied. `ruff check` clean, `ruff format` clean, **the AST proven
unchanged**, 1103 tests passing -- and stage 8 returned *NOT done* with twelve findings. From
that README: *"Every mechanical check said the edit was good. The page was worse than before."*

!! **The confound is DIRECTIONAL, so the two outcomes are not worth the same.** Roy,
2026-08-17: *"the agent that thinks it is easier to revert any bad comments is going to have a
higher discrimination signal than one that thinks it is going to have to accept the edits. The
strength of the signal is that it would accept the changes even though it 'knows' there is an
out."* Knowing it is a test lowers the cost of reverting, which biases toward reverting:

| outcome | what it is worth |
| --- | --- |
| **REVERTED** | weak -- the cheap move, and the one a session being measured is pushed toward |
| **KEPT** | strong -- it accepted the edits while knowing an out was available |

!! **The OPPOSING confound is not captured, and it lands on the same outcome.** Roy: *"what it
doesn't capture is if the agents are doing things to make the workflow follow all the way
through."* A session told the run will reach stage 8 is under pressure to COMPLETE, which
pushes toward keeping -- and toward bending a gate to get there. **The two do not cancel.** Both
bear on KEPT: one makes it informative, the other makes it suspect.

! **Gate-bending leaves a trace, which is why the evidence layout keeps EVERY join output.** A
`refused -> green` pair with no matching change in the underlying finding is a report reworded
to satisfy the parser, not a defect fixed. Read the pair, not the final exit code.

! Where the damage came from is named: **stage 5 was the only stage with no independent
reader.** That is what Roy ruled on the same day -- the joined block goes back to the reviewers
that had findings -- so the fix now targets the measured cause rather than a guess at it.

! **`0.4.0`'s gate is checkable today**, which is why it can sit below an unmeasurable one:
`census.py --languages` prints exactly what the plugin claims, and the claim is per-tier --
`tokenized` resolves docstring owners, `lexical` finds blocks and marks and no owner at all. The
gate is that list, verified, not a general claim about languages. As of `0.2.0` it is **11
families, 1 `tokenized` and 10 `lexical`**, of which **2 have been run** -- python (this repo)
and rust (`startraders`, 2026-08-17).

## [Unreleased]

### The retired report format is DELETED, not shimmed

!! **`verdicts.py` READ THREE SHAPES AND NOW READS ONE.** Roy, 2026-08-20: *"we are not carrying a
backwards compatible shim right now, particularly on a format that was a proof-of-concept
format ... git can recover them if we ever need to figure out how that was done."* A shim under
`plugins/` is copied into someone else's `.claude/`, where an agent reads it as current.

| gone | what it was |
| --- | --- |
| the 0.2.x TEXT report | `--- RECORD` / `BLOCK n \| path:start-end`, keyed by census POSITION |
| the flat JSON `records` list | every record carrying its whole address, superseded by the page envelope |

A report that is not `.json` is now refused BY NAME rather than parsed. `held.py` walks the page
envelope alone -- **612 lines to 186**.

! **WHAT WENT WITH IT, because nothing else ever filled or read it**: `Finding.block` (the census
index -- only the text reader set it), `held.address_of` (whose one job was translating that
index), `record.OPENER` and `record.CODE_CONCERNS`. The shipped tree also stopped needing the
`# noqa: vocabulary` exemption at all -- `held.py` said `BLOCK` because it had to read reports
that spell it that way, and **no shipped file says it now**.

! **THE EVIDENCE PACKAGES WERE CHECKED BEFORE DELETING.** All 8 record files under `evidence/`
are in the flat shape, and none is read by any script, eval or gate. They are records of what
happened, not inputs. `docs/history.md` says what each shape looked like and where the reader is
in the history.

**Tests: 755 to 707.** 41 deleted whose SUBJECT was the retired parser, and `TestCLI`'s fixtures
rewritten as record files -- the gate reads JSON, so its tests feed JSON.

! **AND THE LINE ADDRESS READER WENT WITH IT.** `foliator.line_address()` named a paragraph
`path:start-end` -- retired as a NAMING at 0.2.4, and kept afterwards on the same argument the
report reader used: to parse runs already recorded. A codegraph sweep for shipped symbols nothing
uses found it with **zero callers anywhere** -- not in `plugins/`, not in `tests/`, not in
`scripts/`. 63 lines, and the `warnings` import with them.

! **A DEAD-NAME SWEEP came with it.** Ruff flags an unused import and an unused local; a
module-level constant nobody reads is invisible to it. That is how `record.ANCHOR_SIDE` survived
(filed, [`anchor-side-is-dead`](../TODO/anchor-side-is-dead.md)) and how two constants went dead
in one session with no gate noticing.

### A place is DEFINED now, and that was the weak link

!! **THE PREVIOUS VERSION NEVER DEFINED WHAT A PLACE WAS.** It named one by LINE --
`path:start-end` -- which is true of one file state, and this tool EDITS PROSE: every prose edit
moves the line numbers of the code below it. Nothing owned the definition, so every consumer
re-derived it and they drifted apart in different directions. `docs/addressing.md` is the settled
definition; this is what was wrong before it.

**None of the following was a bug in one place.** Each is the same absent definition surfacing
where a different consumer had guessed:

| symptom | measured on this repo's own shipped scripts |
| --- | --- |
| two blocks answering to ONE address | **28** places, all 28 a docstring sharing a gap with the comment run beneath it |
| lines answering to TWO addresses | **2,303 of 6,775** -- each a code line ending one gap and starting the next |
| lines answering to NONE | **131**, all blanks at the edges of gaps |
| `b` places that did not exist at all | **129** -- `b0` missing in all 13 files, so no file could be given a comment above its module docstring |
| declarations with nowhere to cite a missing docstring | **730** |
| a FRESH census reading as STALE | 3 blocks: a block storing no text was compared against lines that held some |

**After, over 18 files in four languages: 7,436 lines, each with exactly ONE address -- 0 with
none, 0 with more than one, 0 shared.** `addresser.py --check` re-reads that claim on every run.

! The first pass measured PYTHON ONLY and read 6,873 / 0 shared. A comment that opens after a
statement -- legal everywhere but Python -- still took a `b` folio for a line it sat on, because
"shares its line" was computed from a list of KINDS in one place and from `whole_lines` in
another. Two computations of one fact; the same shape as the defect this release is about.

### The rule

**An address is not a span of lines. Every LINE has exactly one address, and a BLOCK is just the
lines that share one.** Ruled by Roy, 2026-08-19. Three series, and every POTENTIAL place has one
too, so prose that is MISSING has somewhere to be cited:

- `@aN` a declaration's documentation (`a0` the module, `a1..aN` in source order) -- empty kind
  `undocumented`
- `@bN` the gap ABOVE code line N -- empty kind `interval`
- `@cN` BESIDE code line N -- empty kind `margin`

! `b` and `c` both count from 0, so `bN` and `cN` name the SAME code line. They did not before:
`c` counted from 1, so `b3` and `c3` named different statements and a reader pairing them
attached a comment one statement too high.

! A place with no lines of its own is at LINE 0. Its EDIT range still says where prose would go.

!! **The path is flattened on `:`, which is what makes an address invertible.** It was `.` until
2026-08-19, and a dot is ordinary in a filename: `a/b.py` and `a.b.py` both read `a.b.py`, so
`a.b.py@a0` named two blocks in two files -- and so did every other address those files had.
`--check` reported them addressed, because it compares only within one path, and `--resolve` then
refused the ambiguity it had certified. Roy: *"lets use an illegal symbol for the separator
then."*

! `:` is the one character Windows forbids that is not shell-special, so an address is safe as a
bare command-line argument where `<`, `>`, `|`, `?`, `*` and `"` are not. Measured over 2,472
source paths in seven corpora: zero hold any of the seven. ! POSIX forbids only `/` and NUL, so a
POSIX checkout can still hold `a:b.py` -- `census.py` reports it as a gap and exits nonzero,
the same channel a language with no record uses. The extension keeps its dot, so `b.py` and
`b.rs` still differ.

### Every address carries its ANCHOR, and 98% of them did not

!! **AN ANCHOR HAS MANY ADDRESSES; AN ADDRESS HAS ONE ANCHOR**, and **the anchor is the LINE OF
CODE -- the exact characters**. Roy, 2026-08-19: *"the anchor isn't the technical symbols and
their precise semantic meaning and code use."*

**Measured against the previous commit: 6,376 of 6,531 blocks in this repo's own shipped scripts
carried an EMPTY anchor -- 98% of the census.** By kind: 3,144 `margin`, 2,923 `interval`, 272
`comment`, 37 `trailing-comment`. Every seeded record repeated it. It is 0 now.

! **It was invisible from both ends at once.** `census.py` printed *"NO COMMENT carries an anchor
at either tier"* as a statement of intent, and `test_record.py` asserted which KEYS are seeded
rather than that either held a value.

! **And it needs no tooling.** Every tier already finds where a comment opens in order to cut
there, so it holds the characters before it. Roy: *"the lexer either knows what is before the
trailing comment and can snag the whole string or it is broken."* Both tiers, eleven languages,
no language server and no build tool.

- **`vocabulary.md` defines LINE OF CODE and ANCHOR.** A line of code is one of four kinds -- a
  statement, an expression, a declaration or an assignment -- which is the enumeration
  `vocabulary.toml` already shipped. ! SUPERSEDED, same day: an earlier commit message called that
  enumeration "the symbol framing today's ruling replaced" and rewrote the shipped `anchor`
  definition without it. Roy: *"I think these are the enumerated set of types for a line of code
  ... so not incorrect, just not clear."* The enumeration is restored and the definition now says
  which line, per series.
- **`record.seeded_problems` refuses a record with no anchor**, and one whose anchor is not the
  census's. Roy: *"an anchor missing in a Record is a broken Record."* Only `address` was checked
  before, though both fields are `SEEDED`.
- **A `b`'s anchor is COPIED from that line's `c`**, never re-cut. Re-cutting answered
  `'    return os  # why'` where the `c` for the same line answered `'    return os'`.
- **The gap at the end of a file takes the line ABOVE it**, because a gap is bounded by code and
  that is the bound it has. Left empty it was 14 blocks, one per file.

### The vocabulary ships the terms reviewers were already reading

**Nine terms a reviewer reads had no definition**, measured against the text each role actually
opens: `address` -- 262 uses, the central term of the release -- `margin`, `interval`,
`undocumented`, `trailing comment`, `intermediate comment`, `series`, and `paragraph` and `page`,
which the shipped text was already using before anything shipped them. All now ship, with `folio`
and `line of code`. 43 definitions to 54.

! **`census` was stale twice over**, defined as *"the numbered tree of every block"*. An address
is an ordinal and an ordinal cannot express containment, so the pCST is a FLAT list -- ruled
2026-08-18 and never carried into the file agents read.

!! **A pCST IS A PAGE AND A BLOCK IS A PARAGRAPH.** Roy, 2026-08-19. `block`'s shipped definition
now reads *"a PARAGRAPH -- the older word"* in place of *"the interval between two lines of
CODE"*, which was only the `b` series: a docstring, a trailing comment and an empty margin are
paragraphs too.

! **It is not only register.** Roy: *"this will make the text document formats read better when we
implement them."* A markdown file has no interval between two lines of code, which is why
`a-prose-file-has-no-blocks` is open; a page made of paragraphs is the model it already fits.

! **And the register got there first.** `paragraph` appears 11 times in the shipped text, every
one meaning the unit of prose -- which is the test `place` failed: its 119 uses meant LOCATION
against a term meaning ADDRESSABLE SLOT, so it was polysemy where this is correct usage that had
no definition.

!! **A PAGE DOES NOT NEST, AND THAT IS WHY THE FLATNESS NEEDED NO APOLOGY.** Roy, 2026-08-19:
*"because it is a flat list of paragraphs."* The pCST was ruled flat because an address is an
ORDINAL and an ordinal cannot express containment -- and `pcst.py` wrote that as a concession,
*pseudo* because a real CST has hierarchy and this does not. Paragraphs run down a leaf and do not
nest, so flat is the shape the thing has rather than the shape the addressing cost. Nothing to
apologise for.

!! **GALLEY -> PAGE -> PROOF is a sequence, and the first draft of this entry collapsed two of
them.** It defined a page as *"the file as a reader meets it"* -- which is the PROOF, already
defined as *"the finished page"*. Two terms, one meaning, inside the entry ruling that the
register is the point. The printing register fixes all three and `galley.py` already states the
first: a galley is text set *"but not yet made into pages"*. So a **page** is ONE FILE, its
paragraphs in order among the code they sit with; a **proof** is a finished page pulled for
checking, which is what stage 8 reads. ! A SECOND draft then split page from census as *the
thing* against *the list of it* -- no distinction at all once a page is itself a flat list. The
axis is SCOPE: measured 2026-08-19, one census covers 14 files and 6,678 paragraphs. `galley` had no
entry in `docs/vocabulary.md` at all and now has one.

! **The RENAME is ~1,935 sites and is its own scope** -- 721 in shipped code, 548 in tests, 368 in
`docs/`, 298 in shipped prose. Filed as `a-block-is-a-paragraph-on-a-page`. It cannot go
piecemeal: `check_vocabulary` refuses a role a term its own text never uses, so `[roles] all`
cannot say `paragraph` until the role files do.

### The shipped prose stops teaching the superseded numbering

!! **`bN` AND `cN` NAME THE SAME CODE LINE**, because both count from 0. `reviewer-brief.md` --
read by four agents every run -- taught the opposite: *"the number means a different statement in
`b` than in `c`"*, with the rule *"code line N carries `b(N-1)` above it and `cN` beside it"*.
That was true while `c` counted from 1 and became an off-by-one the moment the 0-indexing ruling
aligned them. **A reviewer following it cited `c(N+1)` for the line it meant** -- the error the
paragraph itself warned about, inverted.

! **Four sites, not one.** The brief, and three passages in `addresser.py`: its module docstring's
example, the rule paragraph, and `stable()`'s example -- which also still carried the retired
dotted path form.

! **The ambiguity that hid it is the phrase "code line 3"**, which reads as the 3rd to one reader
and as index 3 to another. One half of the pair stayed wrong while the other stayed right, inside
one paragraph, for exactly that reason. The prose now says *"the code line at index N"*.

! **It is gated now.** `TestTheSHIPPEDPROSETeachesTheNumberingTheCodeUSES` measures what `bN` and
`cN` name and then holds both files to that answer. Prose is not executed, so nothing else would
notice it drifting back.

### A held 0.2.x report cannot be replayed, and `convert` now says so

**Replaying held stage-4 output is what made a change cheap to validate** -- 0.2.1 and 0.2.2 were
checked by re-joining one set of reports, about 1.6M tokens of review reused. That stops here for
reports written before 0.2.4, and the reason is structural rather than a bug.

!! **THE OLD FORM DOES NOT CARRY ENOUGH TO NAME A PLACE.** Roy, 2026-08-19: *"is it possible to
convert the old form to the new form at all without the code there next to it? I don't think it
is. There is not enough definition in the old form to make the address."* Both routes are closed:

| the old form offers | why it cannot become an address |
| --- | --- |
| `BLOCK <index>` | a position in ONE census. That census carries no addresses -- **0 of 3,333** on a real held run, because the field postdates it -- and today's census of the same source is a different list: the held one has no `margin` and no `undocumented`, which today's emits one of each per code line and per undocumented declaration. Every index shifts, so `BLOCK 7` names unrelated prose |
| `LOCATION path:start-end` | line numbers, which need the SOURCE to become an ordinal -- and `Finding` does not retain the field at all |

! **It used to fail silently in BOTH directions.** Against a fresh census every held finding
grouped under `""` and matched nothing: 3 of 3 dropped, exit 0. Against the genuine held census
every block keyed on `""` too, so every record matched every finding -- **3,333 blocks and 173
findings produced 29,583 records**, each carrying a verdict, no error raised.

! **The bridge is not dead.** It carries a run held from 0.2.4 on, where a record names a PLACE
rather than a position.

! **And the pre-address reports are recoverable ONE-OFF, from the SOURCE.** Every held run records
its subject hash, so the tree can be checked out, re-censused, and each record placed from the
`LOCATION` line the shipped parser discards. Roy, 2026-08-19: *"that is definitely a one-off
script thing and not worth doing 'right' now."* Filed as
`TODO/held-runs-need-a-one-off-migration.md`.

! **The test class named for this property never called `convert`.**
`TestConvertKeepsAHeldRunReplayable` tests `claim_object`, one field at a time -- which is how a
bridge that carried nothing passed a green suite.

### Both tiers store `raw_lines` the same way, and four of six comment shapes were unwritable

**`raw_lines` is the block's OWN characters** -- its lines whole where it owns them, and from
`original_column` onward on the first line where code comes first. With `anchor` holding the code,
`anchor + raw_lines[0]` reconstructs that line exactly.

!! **THE TWO TIERS STORED DIFFERENT THINGS.** `blocks_lexical` cut at the comment OPENER;
`blocks_stdlib` kept the whole physical line. So `galley.block_matches` could not be written to
satisfy both, and refused a census seconds old on:

| shape | before | after |
| --- | --- | --- |
| trailing `// note` | refused -- the code was cut away | matches |
| trailing `/* note */` | refused | matches |
| indented `    /* why */` | refused -- the INDENTATION was cut away | matches |
| multiline indented `/* one` | refused | matches |
| indented `    // why` | matches | matches |
| column-0 `/* why */` | matches | matches |

**Four of six.** Every block comment not at column 0, and every trailing comment in the ten
lexical languages -- which is what made the `c` series writable in Python alone. Measured
2026-08-19; a `c` edit now writes in Go end to end, keeping the statement and its tab.

! **It also fed CODE to the annotators.** `prose_numbers` reads `raw_lines`, so a Python
`TIMEOUT = 30  # the note says nothing` reported the number 30 as a claim the prose makes. The
lexical tier's own comment says that defect was fixed -- it was fixed on one tier, and
`repeated-literal` counts across the whole census.

! **Storing the whole line in BOTH tiers was the other way out, and is worse**: it satisfies the
staleness check and puts the code in two fields, which is the conflation the anchor was added to
end.

- **`Block.widest` measures the PHYSICAL line again.** It reads `anchor` plus the first stored
  line, because a width rule measures what is on disk. ! It has no caller; corrected rather than
  deleted, since nothing this change made unused.

### An `a` is attached to its declaration's LINE, and the name is dropped

**`anchor` now holds a line of code in all three series.** Roy, 2026-08-19, settling the
definition -- *"anchor -- the line of code that an address is attached to"* -- and then the
consequence: *"drop it -- the line is the anchor."* So `def f():` where it read `f`, and the
census stops carrying declaration names. `--anchor` is asked with the line.

! **One anchor, three addresses**, which is the one-to-many relationship made visible: `def f():`
is the anchor of its own `a`, of the `b` above it and of the `c` beside it.

! **It is copied from that line's `c`, not re-cut**, so a declaration carrying a trailing comment
takes `def f():` and not `def f():  # on a decl`.

!! **A MODULE IS THE ONE ADDRESS WITH NO LINE OF CODE**, and keeps `<module>` -- `co_name` on the
module's code object and the word in every traceback, so it is the language's own name rather than
a placeholder. Every other language gets its declared module name wherever that line sits, once a
language server or CodeGraph gives its tier an `a` series. Anchoring it to the FIRST LINE OF CODE
was tried and made a module's documentation answer to `def f():` -- and to `X=2`.

### The `c` series is WRITABLE

!! **A SPLICE REPLACES WHOLE LINES, so a `patch` on `z = 3  # trailing` wrote `# reworded` over
the statement** -- measured 2026-08-18, in the galley a human is asked to approve. The refusal
that stopped it refused the whole `c` series, so the join admitted an edit at a `c` place and the
galley then discarded every other edit in that file with it.

Roy ruled it 2026-08-19: *"c needs to be writeable. It is the reason c is not an extension of
b."* The census now states `original_column` and `galley.splice` keeps `line[:original_column - 1]`.

!! **A `c` PLACE STARTS AT THE END OF THE CODE, not at the `#`.** Roy: *"c addresses start at the
end of the code on the line."* So the whitespace separating a statement from its trailing comment
belongs to the `c` place: a `margin` and the `trailing-comment` that would replace it carry the
SAME column, an `add` and a `patch` write to the same point, and a `drop` needs no special case.
A `change` carries its own separator, the same way an interval's carries its own indentation.

! It is a little opinionated, and it is the opinion black, ruff, `gofmt` and `cargo fmt` already
hold about that whitespace. Roy: *"it happens to be the same opinionatedness that also sits in
all of the code formatters."*

- **`whole_lines` is gone.** It was a boolean standing in for *where does the prose start*, which
  was enough to REFUSE the write and not enough to make it. `original_column` is the one fact:
  1-based like every other position the census states, `0` where the block owns its lines whole.

### An INTERMEDIATE comment is not censused

**`int x = /* why */ 5;` -- code on BOTH sides -- is ignored, and its line is code.** Roy,
2026-08-19: *"they are not comments that can be systemically and completely verified across code
bases or written consistently on the same file because of line length rules ... all intermediate
comments are ignored. They can be brought up by the agents as code change suggestions."* The same
ruling that keeps a Python type annotation out of the census.

! **It was censused, and it was worse than unwritable.** Measured 2026-08-19:
`f.c@c1 comment text='int x = /* why */ 5;'` -- the statement handed to four reviewers as prose,
with no annotation saying so.

! **The proof got stronger.** `prove_unchanged` called such a file `unprovable` and refused to
compare it; the line is now code and is compared character for character, so a literal beside the
delimiter is caught where before it could not be. A multi-line run CLOSING beside code is still
`unprovable` -- that line is censused and cannot be placed.

### Retired

- **The LINE address.** `addresser.line_address` warns on every call and is read only to parse
  runs already recorded. Roy, 2026-08-18: *"any function method or otherwise that uses that form
  gets a deprecated warning on it now. To make certain it comes out."*
- **The census INDEX in a record.** It went stale the moment an `add` or a `drop` shifted the
  list. Records key on the address; `record.entry_for` is the one lookup.
- **`add`'s `side`.** The address says which side, so a payload stating it again could disagree
  -- and did: an `add` on a `c` address passed the gate carrying `side: above`, and there was no
  `beside` to write instead.
- **Two implementations of one code-line rule.** `census.code_lines` defers to the addresser's.

### Added

- **`docs/addressing.md`** -- the settled definition, with the measurements above.
- **`scripts/pcst.py`** -- a LEAF owning `Block` and the kind sets. `Block` lived in `census.py`
  at the top of the import graph, so the three modules that READ blocks could not import the
  definition of one: 21 untyped `block.get(...)` reads, and two kind sets that landed in
  `galley.py` because it was the deepest module all three could reach.
- **Ask for an address instead of counting it** -- `addresser.py --anchor NAME --series a|b|c`.
  Asking by position is right in Python and wrong in Rust, whose `///` sits before its `fn` where
  Python's docstring sits after.
- **A record carries the `anchor`**, for grepping.
- **A `move`'s destination is RESOLVED.** It was checked for presence and never resolved, so a
  block could be sent to a line number, a description, or a declaration outside the run. The
  destination may hold no prose -- that is what the empty places are for.
- **Front matter is filtered, and an edit on it becomes a `query`.** A licence header, a shebang,
  a coding line: no role can settle one, and a wrong edit is not an editorial mistake. Measured
  over 1,500 files in five corpora -- 12 carried prose above the module docstring, 10 of them the
  same Apache header in every file of the project.

### Fixed while doing it

- **`block_matches` compared a widened address range against the narrower stored text**, refusing
  every prose block in the tree.
- **The `b` place for a docstring-occupied gap had an edit range covering the docstring.** An
  `add` on `b0` would have overwritten the module docstring with a comment. It is an insertion
  above it now. The staleness check is what surfaced it -- a fresh census reading stale.
- **The census listing repeated each file's path on every row** -- 80,912 of 205,753 bytes, and
  the listing is pasted into all five prompts. The file is named once: **205,753 -> 108,553**.


## [0.2.3] -- 2026-08-18

**The gate was the cycle, and the cycle ran.** Everything below is one branch,
`feat/0.2.3-cycle-and-record`, and the release is the gate being met rather than the count of
fixes behind it.

### What the run cost, and what it caught

!! **THE RUN'S REAL YIELD WAS THE DEFECTS IT FOUND IN ITSELF.** Three review passes over the
branch -- one `/simplify`, two `/code-review`, one more `/simplify` -- found eleven, every one
reproduced before it was fixed. The expensive ones:

- **The galley OVERWROTE THE FILE UNDER REVIEW and reported success.** `census.py` emitted an
  absolute `path` when handed absolute arguments, and `out / rel` returns `rel` when `rel` is
  absolute -- so the splice landed on the source, nothing reached `--out`, and the run printed
  that it had worked. Fixed at both layers: a block's path is repo-relative, and the galley
  refuses a target that resolves outside `--out`.
- **The galley DELETED A STATEMENT**, twice over -- a trailing comment, then a block comment
  with code on either side. `whole_lines` is stated by the producer now, because both readers
  that inferred it were wrong in opposite directions.
- **A CRLF file's galley was written in LF**, every line of the diff an ending change; and on a
  mixed file, editing one line converted an untouched one.
- **Three gates were reading a string the tool generates.** REASON-restates-CLAIM could not
  fire on ANY JSON record; `declares_scope` reclassified real work as a boundary report; an
  `add` with an empty anchor passed the join while `record.py --check` refused it.
- **`address_problem` refused findings for the tool disagreeing with itself** -- 3 of 663 prose
  blocks, unfixable by any reviewer, because both sides of the comparison were tool-supplied.
- **`_words` claimed idempotence and was not**, so a whole-block `drop` of any block containing
  `...` or `--` was refused, telling the reviewer to write a remainder already there.
- **A coverage gap was summarised as a pass** -- `STANDS UNCHANGED: N blocks, clean from all
  reviewers`, one line under the list naming those same blocks as unaccounted for.

### One source, one way to copy it

- **The brief's verdict table is GENERATED from `VERDICTS`.** `scripts/render_brief.py` writes
  it; `tests/test_brief_table.py` refuses a brief that has drifted. ! It had drifted: the table
  taught the 0.2.x marker form forty lines under a JSON worked example, `query`'s row never
  named `settles`, and ten of the eleven keys a reviewer must type appeared nowhere as keys.
- **`claim_keys` is the one row the claim keys come from**, where four sites had enumerated
  them from the same traits and two hardcoded the names.
- **`census.address` owns `path:start-end`**, where four sites wrote it out and had already
  diverged on separator and short form.

### Ruled

- **`ownership-context` is NEVER DROPPED; the other three flex.** It rules on the truth of the
  ANCHORING -- is this statement about this code, and about anything in this project -- which
  every other role's verdict presupposes. Its role file and frontmatter state it, and the
  right place for prose is now anywhere in the PROJECT rather than the file.
- **A reduced role set is supported.** `verdicts.py --reviewers` was always set-agnostic; what
  hardcodes four is `SKILL.md`.

### Also

- **`tests/test_shipped_imports.py`** -- a shipped file imports the stdlib and its neighbours
  and nothing else. The rule was previously kept by the repo having no dependency to import;
  planting one passed every gate.
- **`version_problem`** reads `RECORD_VERSION`, which was written by `seed` and read by nothing.
- **`galley.py` refuses a census too old to answer it**, whole, rather than defaulting a
  missing field -- the one default that was tried put the deleted statement back.


!! **0.2.3 HAS A GATE, and it is not "the fixes accumulated".** Roy, 2026-08-17: *"the goal of
0.2.3 is still getting a full reviewer - rereviewer - cycle functional. We are not releasing
until we have that."*

**Two things clear it, and both are required:**

| | |
| --- | --- |
| **the cycle RUNS** | 4 MARK -> 5 APPLY -> 5b RE-REVIEW -> 6 COMPACT -> 6b RE-REVIEW, end to end on a real repo. The pieces exist -- `re-review.md` defines it, `galley.py` gives a round-2 record a census to cite, `SKILL.md` carries 5b and 6b -- and **none of it has been run** |
| **the record is a VALUE** | Roy: *"I think this change also has to be implemented so that the agents aren't working around the tool."* See `TODO/the-record-is-a-parsed-template-and-should-be-a-value.md` |

!! **The second is a release condition because of a cost that leaves no trace.** A reviewer
reshaped a sound finding TWICE to route around characters the checker mishandled -- moving its
ruling onto a differently-bounded span to avoid a parser defect. A refused record is visible; a
finding quietly re-bounded to satisfy a tool is not. **That is the system deciding what can be
FOUND rather than whether it is true**, and it is CONSERVATIVE ON MEANING, FREE ON FORM failing
from the tooling side.

! Everything on `feat/0.2.3-cycle-and-record` since `v0.2.2` -- the galley, `re-review.md`,
5b/6b, D8, D9 in both shapes, the whole-block `drop`, the JSON record -- is **part of 0.2.3,
not a release of its own.** The gate is the cycle working, not the count of fixes behind it.

### !! BOTH CONDITIONS ARE MET, 2026-08-17

**The run is kept: `evidence/cycle-0.2.3/`** -- the packet, both censuses, the four
filled record files, the green join, the edits stage 5 ruled, and both galleys. ! The
5b and 6b answers are in its README and NOWHERE ELSE: a re-review is a message, so
nothing wrote them to disk. ! Its README states what the run did NOT test.

**The record is a value.** `record.py` owns the shape; `--seed` writes one slot per prose block
carrying `block` and `address`, and the reviewer sets `verdict`, `claim`, `reason`, `sources`,
`change`. The record says WHERE, never WHAT: handed the prose a reviewer could produce a
complete admissible ruling without opening the file, and no check could tell that from real
work, while reading the WRONG lines is caught. The conversion of four held reports joined to
output `diff` could not separate from the original join.

**The cycle ran, 4 -> 5 -> 5b -> 6 -> 6b**, over `galley.py`: 110 census blocks, 11 prose, four
roles, **47 findings, stage-5 gate exit 0**. SIX 5b answers over three roles -- 5 HOLD, 1
REVISE -- and two 6b answers, both HOLD.

!! **The REVISE is what shows 5b earns its slot.** A role read its own round-1 correction in the
joined block and found that IT miscounted, filing a full record cited against the galley census.
The round-1 gate had already passed that finding, and stage 8 runs after the write, so nothing
else in the pipeline was positioned to catch it.

!! **THE RUN'S REAL YIELD WAS TWO DEFECTS THAT MADE 5b IMPOSSIBLE**, either alone sufficient,
both in the tree under review and both found by the roles reading it:

- A structural docstring's `raw_lines` was the AST value, so `block_matches` compared unlike
  things -- **6 of 6 docstring blocks refused as stale against an UNMODIFIED file.**
- An interval's `start` and `end` are the two lines of CODE bounding it, and the galley
  replaced both, so an `add` would have DELETED CODE. It never got that far: all 99 intervals
  were refused first, and the lesser fault hid the worse one.

105 of 110 blocks could not be spliced before the fix; 110 of 110 can now.

! **Three things the run measured that are not defects in the pipeline:** a cap had to be
supplied by the operator, because this repo publishes none and stage 6 is skipped without one;
`--repo` does not decide how a path ARGUMENT resolves, so `census.py` read the live file while
`--repo` pointed at a pinned one; and editing a REFERENCE ONLY file during MARK moved a cited
line, which the join correctly reported as an unresolved citation. Joining against a worktree
pinned at the commit the roles read cleared it.

## [0.2.2] -- 2026-08-17

**0.2.1 is broken and stays broken.** Its tag is not moved: another session had already pinned
an evidence package to it, and a tag someone has measured against is a fact about that
measurement. Roy: *"0.2.1 is broken - it is what it is including a broken tag."*

### The frontmatter never parsed

!! **`claude plugin validate` refuses two shipped files, and has since at least v0.2.0.**
`SKILL.md` loaded with EMPTY metadata; `comment-review-block-context.md` loaded with its name
taken from the filename and every other field dropped -- including the description, which is the
text telling a model when to reach for that reviewer. **The symptom was visible in every session
and unread**: that agent showed as *"Agent from comment-review plugin"* in the registry while the
other five showed their own.

The cause is a `: ` inside an unquoted value. YAML ends a plain scalar at colon-space, so
`three kinds of claim: state ...` is a parse error rather than a string. Confirmed against the
real validator with eight one-construct probes -- `?`, `"`, `--` and `()` mid-value all parse;
colon-space does not, in any position. The five agents that parse hold no internal colon-space;
the one that failed held two. `tests/test_frontmatter.py` is the gate, over every shipped file
with a frontmatter fence.

! **No test replaces `claude plugin validate`**, and CLAUDE.md now puts it in the release gate:
it is the parser the runtime uses. The new test gates the one cause that is known; the validator
is what finds the next one.

### The plugin states its own version

`plugin.json` carries `version`, and `tests/test_release.py` holds all three copies equal --
`pyproject.toml`, the newest heading here, and the manifest. See the note at the top of this
file for what it cost to lack it.

### Fixed -- the join

- **A malformed `SOURCES` citation was glued onto the entry above it.** `CITE` fails on
  `b.py | text` exactly as it fails on a wrapped verbatim tail, so the bad line joined the good
  entry's needle; that entry then failed its own lookup and the tool **reported the error against
  a CORRECT citation while never naming the broken one**. `PATHISH` splits the two on whitespace,
  which a PEP 604 union in a cited line (`-> str | None:`) does not survive.
- **Brackets defeated the CLAIM-covers-CHANGE check.** `_words` stripped sentence punctuation and
  not `()[]{}`, so a `CLAIM` naming `the CLI` could not cover a `CHANGE` editing `the CLI)`. The
  only way through was to quote the bracket inside the claim -- arbitrary from a reviewer's side,
  because the same phrase ending a sentence works.
- **The WORK LIST is printed on a refusal**, labelled PROVISIONAL, where it used to be withheld.
  The reasoning for withholding stands and is now in the heading; what it cost was the run's only
  readable summary, exactly while someone iterates on refusals. Measured: five joins over one
  report set printed it once, on the fifth.
- `verdicts.py` gained the `sys.path` shim its three sibling importers carry. Invisible from the
  documented invocation, because a script's own directory is already on the path.
- `546 blocks, 48 prose` was stale and written in TWO places with nothing comparing them.
  Re-measured 2026-08-17: **642 and 76**, corrected here and in `SKILL.md`.

### Fixed -- the brief

- !! **"A blank line ends it" was never what the parser did.** The brief taught the rule whose
  opposite was 0.2.0's worst defect. A field ends at the next LABEL; a blank line is content.
  Every run since 0.2.0 was written under a constraint the code did not have.
- The brief now says that **N records on one block each read oddly alone, and that this is the
  format working.** A reviewer merged three coordinated edits twice trying to keep a paragraph
  readable, and was correctly refused both times.

### Fixed -- prose the ASCII sweep falsified

Four sites claimed a character the sweep had removed, including one comment that had the
character it was explaining swept out from under it. ! One `!!` survived the sweep entirely, in a
file that was untracked when it ran -- the sweep walks `git ls-files`.

## [0.2.1] -- 2026-08-17

A bugfix release. **`0.3.0`'s gate is untouched by it** -- nothing here was measured against a
run on Roy's codebases, which is what that rung asks for.

### The shipped tree is ASCII

!! **Nothing under `plugins/` holds a character outside ASCII**, and
`tests/test_shipped_cli_encoding.py` is the gate. Roy, 2026-08-17: *"there is a reasonable
chance that this would be run on an ascii only computer."* A plugin is copied onto a machine
whose console encoding nobody here chose, and prose that is ASCII cannot be corrupted by any of
them. The sweep ran repo-wide -- 11,589 characters over 140 files -- and the gate covers what
SHIPS, because a file under `docs/` or `evidence/` is read here and never copied out.

| was | count | is now |
| --- | --- | --- |
| em dash, U+2014 | 6,956 | `--` |
| warning sign, U+26A0 (doubled for the stronger note) | 2,126 | `!`, and `!!` |
| section sign, U+00A7 | 616 | `stage 3`, spelled out |
| arrow, U+2192 | 547 | `->` |
| box drawing, ellipsis, curly quotes, math signs | 1,343 | `-|+^`, `...`, `"'`, `>=` `<=` `!=` `~` |

! **A transliteration library was measured and rejected.**
`unicodedata.normalize("NFKD", ...)` DELETES a character with no compatibility decomposition
rather than transliterating it: 11,085 of the 11,589 would have vanished, every em dash and
every warning sign among them, and U+2260 (not equal) becomes `=`. The two highest-count
characters also needed a decision no library holds -- what `!!` means here, and that the
section sign is a STAGE.

! **A character a program NEEDS is written as a `\uXXXX` escape**, so behaviour
is unchanged and the source is still ASCII. `re` resolves such an escape inside a raw
pattern, which is how `CALLFORM` still matches an ellipsis -- a literal `...` there
would match any three characters instead -- and the fixture proving git octal-escapes a
non-ASCII path still writes one into the filename it creates.

! **Captured runs are exempt.** `evidence/*-full-*` is the record of what a run produced, and
rewriting one edits that record -- the same exclusion `pyproject.toml` already gives ruff.

### Fixed

- **A list ordinal is not a value.** Loosening `NUMBER` to find a sentence-final number also
  admitted the `1.` of a numbered list, so two files that number their steps cross-reported
  `repeated-literal` at every ordinal. `prose_numbers` now takes the block's raw lines, which
  is what separates a line-opening ordinal from a sentence-final number once the run is joined.
- **`prove_unchanged` quoted a spec git was never asked for.** The failure named
  `<base>:<rel>` while `_show` ran `<base>:./<rel>`, which resolves differently under `--repo`
  on a subdirectory -- the misdirection the `./` fix existed to remove. Both now read the spec
  from `_spec()`.
- **`code_names` rows are classified, not all called unreadable.** A polyglot corpus has a row
  per non-Python file, so `generator_split` reported six tracked files as unreadable and told
  the reader to wait for a list that can never empty. `NO_HARVESTER` and `WALKED_TREE` name the
  two gaps that are not read failures.
- **A failed `--clean` no longer reports the tree removed.** `rm <name>` printed
  unconditionally and nothing counted the failure, so a locked pack file exited 0 and the
  documented refetch passed its pin check against the stale checkout.
- **`grade_hazards` stopped calling a positional-only run ungraded.** A worktree touching only
  D3 and D12 examined both and routed both to NEEDS-EYES; the summary said nothing was graded.
- **The GA score no longer depends on the order of a candidate's findings.** Closest-first was
  still per-finding greedy: the same two findings scored f2 0.5 or 1.0 depending on their order
  in the JSON. `_max_hits` is a maximum matching, whose cardinality is a property of the
  eligibility graph.
- **The CLI encoding gate reaches `evidence/ga/`.** It said "wherever it lives" and listed
  three directories; widening it found two argparse programs with no guard.
- Comment fixed where it named `onexc` and the code passes `onerror`.

## [0.2.0] -- 2026-08-17

**Group A of the coherence design** -- `docs/superpowers/specs/2026-08-17-review-process-coherence-design.md`
-- plus a day of rulings on what each field of the record is FOR. The unit of review is settled
in all four places that stated it differently: `SKILL.md`, the join, the census and the record.

! **A report written for 0.1.7 is refused by this gate.** Every field but `VERDICT` and `REASON`
changed name, meaning, or both.

! **Known defect, shipped knowingly:** `verdicts.py` assumes ROUND ONE and cannot admit a
re-review record -- see `TODO/re-review-is-ordered-everywhere-and-defined-nowhere.md`. The
0.1.7 run cleared re-reviews outside the gate and this one will too.

### Changed -- BREAKING

- **The record is SIX fields in a CHAIN OF CUSTODY:**
  `BLOCK VERDICT CLAIM REASON SOURCES CHANGE`. Roy: *"that is a clear chain of custody on the
  reasoning and the required actions."* The ruling, what must change, why, the evidence the why
  rests on, the result -- each field answers the question the one above it raises. `SOURCES` sat
  between `VERDICT` and `CLAIM`, which put the evidence before the thing it was evidence FOR.

- **`CLAIM` is the SPEC and `CHANGE` is the RESULT.** `CLAIM` says what must change and from
  what to what; `CHANGE` is that edit already made, written out **with the surrounding block**,
  which is what stage 5 substitutes. Roy: *"the change is what allows the apply section to apply
  the claim appropriately."*

  | verdict | `CLAIM` | `CHANGE` |
  | --- | --- | --- |
  | `correct` | `false: ... / true: ...` | the result, with its block |
  | `patch` | `from: ... / to: ...` | the result, with its block |
  | `move` | `from: ... / to: ...` (PLACES) | BOTH blocks: `to:`, and `from:` unless the whole block moves |
  | `add` | `missing: ...` + anchor and side | the text added in |
  | `drop` | `drop: ...` | the block with it removed |

  `clean` and `query` carry neither -- a query says the claim is unsettled, so it proposes no
  text to apply. ! `correct` keeps `false:`/`true:` where `patch` and `move` take `from:`/`to:`:
  that pair ASSERTS the sentence is wrong, which is the whole difference between the two
  verdicts, and a neutral from/to would erase it.

- **`BLOCK` carries its ADDRESS and the ORIGINAL TEXT** -- `<index> | path:start-end`, then the
  block's text as the file reads it now, on the lines below. All three checked against the
  census. Roy: *"this allows the reviewer to have most the context and most of the time all of
  the context it needs to understand."* A record can now be read on its own; stage 5 and any
  re-review previously had to hold the census open beside it. ! `clean` owes neither -- a role
  returns `clean` on most of the census (1159 blocks on one measured run).

- **`SOURCE` -> `SOURCES`**, the plural naming what it always did: one entry per place examined,
  `file:line | verbatim`, every citation resolved and every verbatim half checked.

- **`LOCATION` retires because it was AMBIGUOUS.** Roy: *"it could also have meant where this
  should go in the case of move or add. Or on a granular level which sentence are we talking
  about specifically."* One field carried four subjects; each now has its own home -- where the
  prose sits (`BLOCK`), where the reviewer looked (`SOURCES`), where it should go (`CLAIM`'s
  `to:`), and which sentence exactly, which is DERIVED from `BLOCK`'s original against `CHANGE`.
  ! That is the gain, and it is not resolvability: a field whose subject is unknown can only be
  checked for whether it resolves, because nothing says which of the four to check it against.

- **`SUMMARY` splits**, its quoted half into `CLAIM` and its derived half into `REASON`, which
  is what `FINDING` was. ! A checker cannot verify both halves of one field.

- **A contradiction is two verdicts on ONE SENTENCE, keyed on the DIFF.** The check keyed on the
  census BLOCK index while a verdict rules on a sentence, so any `drop` in a block collided with
  any `correct` in it. Measured on a live run: **8 blocks flagged, 2 genuine.** It now keys on
  the difference between `BLOCK`'s original and `CHANGE` -- two roles are rivals when their EDITS
  collide, whatever each of them said.

- **`move` leaves the contradiction set.** A relocation and a truth fix COMPOSE -- the synthesis
  order applies every `move` at step 2 and every `correct` at step 3. ! The `correct` is applied
  AT THE DESTINATION, and may leave a vacuous comment, which is the accepted outcome.

- **`prose tree` retires; the census builds a `pCST`.** The two named one thing once the census
  enumerated intervals.

### Added

- **The CLAIM and the EDIT are checked against each other** (`edit_problem`), authorised by Roy
  *"as a backstop to the Apply agent not doing its due diligence"*. Every span the edit REMOVES
  must lie inside the sentence `CLAIM` names. Nothing read the two accounts of one edit together
  before: one check confirmed the claimed sentence was in the block, another confirmed `CHANGE`
  existed, and neither noticed a reviewer that reasoned about one sentence and rewrote another.
  A `CHANGE` word-identical to the original is refused too.
  - ! It governs ONE FINDING and must never be turned on stage 5's synthesis -- a synthesised
    block composes several findings, so no single `CLAIM` names everything it changes.
  - ! It checks ONE ROUND. Roy: *"this catches the 'first' round of edit reviews, it will not
    catch the next N rounds required to make it correct."* A green gate is not a correct block.
  - ! It forces a rule the brief now states: **one finding's `CHANGE` makes one finding's
    edit.** Stage 5 cannot compose records that have already been merged.
- **A field may run onto CONTINUATION LINES**, indented, ended by a blank line. `CHANGE` is a
  whole block by construction and those lines were previously SKIPPED -- a multi-line `CHANGE`
  arrived holding only its first line, and nothing said so.
- **`continues-a-trailing-comment`**, at BOTH tiers. A trailing comment closes its run, so a
  sentence wrapped onto the next line becomes a second block anchored to the code below it --
  correct by the block definition and wrong about the prose. ! Stamped rather than re-cut:
  merging would renumber every census. **A mid-clause ending on a stamped block is not a
  `correct`.**
- **`REASON` must not merely restate `CLAIM`** -- equality only, since a `REASON` that quotes the
  claim and then explains it is doing its job.
- **`SKILL.md` says a role may file several verdicts on one block**, and that the synthesiser
  reads the code around where the replacement lands.

### Fixed

- **`FINDING` and `QUOTE` were still named in four places** in the shipped reviewer brief, after
  both fields had been renamed. A reviewer following those lines emitted a field the parser
  discards without saying so.
- **`ruled_text` kept the whitespace INSIDE quotes** -- `false: "  the budget is 3 "` matched
  nothing in a block that plainly contained it.

### Ruled, not yet built

- **Re-review round two reads the JOINED RESOLVED BLOCK**, not the contradiction. Roy: *"sending
  the joined resolved block back to the reviewers that had comments does help, because each can
  say yes my edits made it and are correct and the other edits do not negate that or cause mine
  to be wrong."* Three questions: did my edit survive, is it still correct there, do the others
  break it. ! This is the SAME mechanism as stage 5's missing independent reader; the two TODOs
  are now one. ! `verdicts.py` cannot admit such a record -- the blocker named at the top.


## [0.1.7] -- 2026-08-17

Almost every entry below came from RUNNING the skill rather than reading it. Two
real runs -- one against a personal project, one against a larger tree -- found
defects a full day of reading the same files had not.

### Changed -- BREAKING

- **Every interval between two lines of code is a block**, empty ones included.
  A block was defined as an interval on 2026-08-15 and the census still
  enumerated from PROSE, so an interval with nothing in it had no index -- which
  is why `add` never fit the finding record. `add` says a constraint exists in
  code and NOWHERE in prose, a finding ABOUT an empty interval, and it had to
  borrow a neighbouring block's index and read as being about that block's text.

  ! **ADDRESSABLE is not ACCOUNTABLE.** A reviewer owes a record on blocks that
  HOLD PROSE; an empty interval exists to be cited. Owing one on all of them
  would have made `CLEAN 1-N` -- the cheapest fabrication there is -- nine parts
  in ten true. Rulings made along the way, all recorded in the TODO: the file
  boundary counts as a bound, `start`/`end` are the bounding code lines so a
  zero-width gap still resolves, and docstring/trailing-comment coexist with
  intervals rather than becoming them.

  Measured: `census.py` over itself is 546 blocks, 48 of them prose, against 44
  before; `--json` is 177,615 bytes against 36,777.

- **Stage 2 is COLLATE**, not ANNOTATE -- ruled by Roy. ANNOTATE meant adding
  notes and stage 2 adds none; it gathers every position in the file into one
  numbered, ordered tree. It also pointed at two stages, since `annotate.py`
  performs stage 3. ! `annotation` is unaffected: it was ruled in for two
  reasons and only one was the stage name.

- **`census.py --out PATH` writes the report**, because a shell redirect is
  REFUSED in a worktree-isolated harness and the run then has no census at all.

- **A `query` NAMES which of three shapes it is, and carries EVIDENCE.** Roy:
  *"Is the query one of the three variants of query -- which one and why"*, then
  *"It must contain everything to say it was looked at and this is why it is
  query."* `evidence_problem` exempts `clean` alone now -- the brief had always
  required a query's citations and the gate had always waived them, which was
  the one place the two actively contradicted. On top of that, `payload_problem`
  refuses a `query` whose `CHANGE` does not name one of the brief's three shapes
  in the brief's own words. ! The named shape is stripped before the
  attempted-check word search, because the pattern matches "checkout" and the
  shape would otherwise satisfy the check it accompanies.

- **`add` needs a side and the anchor NAMED IN BACKTICKS.** The check accepted
  the bare word "anchor", so `add an anchor comment` passed while
  ``above `retry_budget` `` failed for not using the word.

- **A report file's stem must be a PUBLISHED role name.** It was taken as a role
  name on sight, so `ownershp-context.md` became a reviewer called
  `ownershp-context` and every line below named a role that does not exist.
  Checked against `Reviewer`.

- **The dispatch packet gains `REPO ROOT`**, checked like `CENSUS`. Roy: the
  agents *"could get the full path to the root directory they are supposed to
  work in"*. The census, `FILES UNDER REVIEW` and every citation are
  repo-relative and nothing said what to.

- **`REVIEWER FILES` is TASK AGENT ONLY and is withheld from reviewers.** Roy,
  distinguishing it from the above: that *"is not the same as giving them reason
  to search the plugin folder in `.claude/`"*. `SKILL.md` already said a path
  into the installed plugin is an invitation to read its neighbours, while the
  packet carrying those paths was headed *"Handed to every reviewer"*.

### Added

- **`CODE CONCERNS` is parsed, attributed and echoed.** Roy: *"told you you
  can't stop coding agents from trying coding."* `reviewer-brief.md` had always
  given code problems a section and `verdicts.py` contained the string zero
  times, so a reviewer that filed one exactly where the brief says had hidden
  it. ! Printed whether or not the gate refuses -- the run that proved this
  stopped at stage 5, and the defect would have died with the refusal.

- **The WORK LIST**: every block needing a ruling with the verdicts held on it,
  which `contradictions` had been computing and discarding. Withheld when the
  gate refuses.

- **A third state in the join.** A block covered only by `clean` and
  `query -- outside my role` is neither STANDS nor NEEDS A RULING: nothing is
  asked of stage 5, and no role certified it either. Measured: one run read
  1159 blocks as work when 76 carried a verdict.

### Fixed

- **`outside my role` owes a showing.** Quote the line that fixes the block's
  subject and say what about that subject your remit does not reach, in your own
  role's words -- never naming another role. *"Not mine"* is an admission.

- **`FINDING` is checked, and holds one thing.** It doubled as the diagnostic
  slot for a malformed record, keyed on a `block=-1` sentinel that three
  consumers each filtered separately. `parse_report` returns
  `(findings, malformed)`; every verdict but `clean` now states why it was made.

- **`QUERY_ATTEMPTED` is derived from the verbs a reviewer is instructed in.** A
  run refused 65 of 65 module-context queries reading *"resolved the enclosing
  definition at ..."* -- `resolve` was in `QUERY_SETTLES` and missing here, so
  reports that were substantively complete were lexically refused.

- **`MIN_NEEDLE` is 1.** The 12-character floor inverted on short code lines --
  `x = 1`, `pass`, `return` -- where its only route through was to quote MORE
  than was read.

- **The `move` destination can be available PER PATH.** A repo that built the
  tree for some packages and not others had one answer imposed on all of them.

- **One message protects INDEPENDENCE, not speed.** The file gave the weak
  reason, and a run dispatched 2 + 2 on the strength of it.

- **block-context searches by WHOLE NAME.** A count of `_block(` swept in
  `compose_block(` and the enumeration was off by two in a report that named its
  population correctly. Both halves look done, which is the trap.

- **`docs/vocabulary.md` said 44 shipped definitions; there are 43.**


## [0.1.6] -- 2026-08-16

Roy read the shipped prose line by line and ruled on it. Almost every entry below
started as a quoted sentence and a short verdict.

### Changed -- BREAKING

- **`census.py` loses `--cap` and `--width`.** Measured: `--json` carries no cap or width
  information at all, so the flags changed ONLY the text census -- which is the file handed to
  the four reviewers. `run_context.py` omits CAP and WIDTH from the dispatch packet on purpose
  and `SKILL.md` says the cap is *"never passed to a reviewer"*; the census printed
  `over cap (6): 0` in its first eight lines. Roy: *"why does census.py get a cap argument at
  all?"* The over-cap count fed no decision -- stage 6 works from stage 5's PROPOSED text.

- **An agent is GIVEN what it needs and is never sent looking.** All six agents opened by being
  told to read their brief or procedure *at a path* -- an absolute path into the installed
  plugin, handed to an agent with file tools. Roy: *"then the agents go looking where the
  plugins are installed ... and they see stuff they are not supposed to see and take actions that
  they are not supposed to take."* The brief and each procedure are now pasted into the prompt,
  as the vocabulary already was. **No agent file names a path, and no dispatch hands one over.**

- **The synthesis order settles PLACEMENT first.** In-code `move` was applied LAST, after
  `correct` and `patch`, so text was corrected at an anchor another role had already called
  wrong. Roy: *"moves first."* Step 2 is now every `move` and every `drop`. Seven steps become
  six.

### Added

- **The join prints a WORK LIST.** `contradictions()` computed the per-block grouping, used it
  for one boolean and discarded it -- while stage 5's task is *"four reviewers rule on the same
  block ... must emit ONE"*. Roy: *"give the agent the tool."* `by_block()` is now shared, and a
  passing run prints `PER BLOCK -- what you hold, in census order`, marking blocks out for
  re-review. ! Withheld when anything is fatal: the gate has just refused the report.

- **The join flags `move` against `correct`/`patch`,** not only `drop`. A claim ruled on at an
  anchor another role calls wrong was measured against the wrong code, and that pair passed in
  silence.

- **`module-context` owns module-level CONSTANTS and RUNTIME.** Roy: *"constants at the top of
  the file are also part of their purview ... any runtime things are also its purview -- like what
  happens under the `if __name__ == '__main__':`"*. A missing why is `add`; a constant the
  module does not need at module level is a CODE CONCERN.

### Fixed

- **The stage-5 join could not run as documented.** `SKILL.md` invoked
  `verdicts.py --census <census>.json` and `verdicts.py` calls `json.loads` on it, while stages
  2-3 gave only text-census commands and `--json` appeared nowhere else. A run following the
  file reached the join and got `CANNOT PARSE ... as JSON`.

- **`MIN_NEEDLE` refused true findings.** A 12-character floor rejected `x = 1`, `pass` and
  `return` -- real short lines -- and the only route through was to quote MORE than was read,
  which is the fabrication the check exists to stop. Roy: *"that is why I dropped the 12
  character limit in the other files."* It is now **1**: a zero-length quote is not a quote.

- **Six unfalsifiable claims** replaced with checkable ones -- *"your highest-value work"*,
  *"the most dangerous prose in a test file"*, *"reads badly"*, *"the best findings here"*.
  ! Two were introduced earlier the same day while cutting anecdotes: the replacement reached
  for an adjective where the anecdote had carried a measurement.

- **Five unmeasured rankings** -- *"the most common structural finding"*, *"the last four are
  where the defects are"*, *"the only form of this finding that ever gets fixed"*. Roy on the
  last: *"really, are you certain we built all this to just use 4 unrelated things?"*

- **Nine cross-role references removed from the agent files.** Roy: *"the agents do not need to
  know about each other."* Every one was answerable from the role's own remit. ! One survived a
  case-sensitive sweep -- `Block-Context` in title case -- and was caught by Roy reading.

- **`cap` carried three meanings**, `run` two, and the census called its own output `marks`.
  `cap` is a NUMBER, so a block is OVER or UNDER it; `block` is what CODE bounds and a
  `comment run` is the prose inside it; the census emits ANNOTATIONS, because a MARK is
  editorial and stage 4 emits those. ! `check_vocabulary.py` caught the `cap` collision on its
  own: the term had been distributed to a role whose only use of the word was an invented
  example about rounding.

- **A docstring's anchor is the declaration it sits INSIDE.** `SKILL.md` said every block
  belongs to the code BELOW it, which is true of `#` runs and wrong for docstrings -- and
  `ownership-context` is dispatched to rule on exactly that.

- **Six summaries disagreed with the sites they summarise**, every one drifting in the summary
  while the detail stayed right: the `move` payload, `clean` versus `query` in a Return section,
  *"the eight verdicts"* in four agent files, `APPROVAL ... only then applies`, *"if `move` is
  unavailable"*, and a collision rule that had not caught up with the widened gate.

- **Two dangling references a reader cannot resolve** -- `at 1.4` in an agent file that never
  reads `SKILL.md`, and `LANGUAGES` naming a tuple inside `census.py` that the task agent may
  not open.

- **`FORMATTING` was an undeclared verdict word.** `verdicts.py` makes an unknown verdict FATAL,
  so a reviewer following that instruction would have killed the run. It is a `move` to the line
  above. Roy: *"I definitely didn't want a formatting category."*

- **Three stale counts and one stale floor** -- *"the eleven questions this packet asks"* (nine),
  *"the other eight are prose"* twice (six), and *"the 3.9 floor this script promises"* (3.11).
  ! The one count that had NOT drifted is the one a test asserts.

### Changed

- **The checkable/necessary matrix moved to `reviewer-brief.md`.** It decides a VERDICT, and
  verdicts are the reviewers' -- but it sat in the task agent's file alone, so the four roles
  that emit `drop` and `move` had never been given the test their verdicts are judged by. Roy:
  *"sends back to the other agents -- not makes the determination itself."*

- **The environment floor is stated once: a LOCAL GIT REPOSITORY.** Everything else is checked --
  an upstream, a merge base, a clean tree, a cwd at the repo root.

- **Run statistics removed from the shipped prose.** Roy's discriminator: does the number teach
  a reviewer to CHECK a number, or only report what happened here? ! A number inside an INVENTED
  example stays, because it teaches that a number in prose is a checkable claim.

- **`SKILL.md` 784 -> 733 lines** across the sweep, with nothing removed that anyone acts on.


## [0.1.5] -- 2026-08-16

### Changed -- BREAKING

- **The `level` ladder is REMOVED ENTIRELY. Every verdict is available on every run, and all
  four roles run every time.** Roy: *"I am 100% certain there are not 'levels' allowed
  anymore."* ! **This is a behaviour change, not a rename.** `verdicts.py` refused a verdict
  outside the level's set, so at `fact-check` a true-but-misplaced block could not be `move`d
  and became `query`.

  The ladder had no provenance: traced with `git log -S`, it exists at **zero commits** in the
  project it was ported from. It was invented during the port.

  Removed from `run_context.py` (`LEVELS`, the `LEVEL` packet section and its validation --
  `REQUIRED` 9 -> 8, the answers a machine can settle 3 -> 2), `verdicts.py` (`LEVELS`,
  `allowed()`, `--level`), `SKILL.md` (the table, its four notes, the `level` argument),
  `vocabulary.toml`, and two `fact-check` carve-outs in the ownership-context agent.

  ! Three TRUE statements the ladder carried survive in another form: `ownership-context` is
  read FIRST (same reason, no ladder); an unavailable `move` still puts blocks over the cap;
  and *"every reviewer that ran"* needs no carve-out now that all four always do.

- **`split` collapses into `move`. There are SEVEN verdicts, not eight.** Roy: *"how is that
  different than a move or drop? Would we ever split a sentence? Does that even make sense?"* It
  is `move` at a different granularity, and `SKILL.md`'s synthesis step already handled the two
  in ONE step -- *"`move` as one block and `split` as fragments"* -- while `verdicts.py` checked
  its payload by counting **two anchors**, so a `split` record was N `move` payloads in one
  record.

  ! It was also the only verdict whose subject was the **block**. Once *"a verdict rules on a
  SENTENCE, not on a block"* opened the verdicts section, a block holding two unrelated notes IS
  two sentences with different anchors: each gets `move`, and the block splitting is the OUTCOME
  rather than the judgement. That is the argument that collapsed `reanchor` in 0.1.3 -- a
  relocation is ONE judgment and the destination is payload -- applied a second time.

  A block whose sentences belong in different places is **one `move` per sentence**, which is
  expressible now that every block carries a record and coverage counts a set. **A report
  emitting `split` is rejected at the stage-5 gate as a verdict outside the set.**

  ! `drop`, `patch` and `add` were examined at the same time and STAY. Roy: *"everything else we
  have come up with has had a valid use case."*

### Fixed

- **The stage-7b gate was invoked with the wrong ref, and failed correct runs.** `write.md` ran
  `prove_unchanged.py --base <merge-base>`. The merge base answers what the BRANCH changed; 7b
  proves what WRITE changed. On a branch that edits code and comments together -- the case this
  skill exists for -- the branch's own code changes are still in that diff. Reproduced, WRITE
  having touched only a comment:

  ```
  --base <merge-base>     FAIL   a.py: executable code DIFFERS (ast proof)
  --base <pre-edit-ref>   PROVEN a.py: reads the same (ast)
  ```

  ! `write.md`'s next rail reads *"A `FAIL` is a stop, not a note ... restore the file"*, so the
  documented procedure was to **discard a correct edit** on every review of a branch that
  changed code. The script was right throughout -- `--base`'s own help says *"ref holding the
  pre-edit text"* -- and only the prose naming the ref was wrong.

  **Fixed by naming the ref once.** Stage 1.1 records a PRE-EDIT REF -- `HEAD` when nothing in
  scope is uncommitted, `git stash create` otherwise -- and stages 6 and 7b both use it.
  `compact.md` carried the same bug, and `original` is defined as *"the text as it stood when
  THIS RUN began"*, which is the pre-edit ref and never the merge base.

- **`cap` carried three meanings, one of them foreign.** It is defined as *"The published line
  limit a comment run may not exceed"* -- a NUMBER -- and was also used for the STATE of
  complying with it (*"the cap is out of reach"*), as a VERB (*"COMPACT must cap prose"*), and
  in `function-context`'s invented example as an unrelated rounding ceiling. Every site now
  uses `cap` only as the number, with a block described as OVER or UNDER it.

  ! The collision had reached an agent's prompt: `check_vocabulary.py` went from 0 drifted to 1
  the moment the example was fixed, reporting *"function-context is given 'cap', never uses
  it"*. That role had been handed the `cap` definition for no reason but a word used in a
  foreign sense.

- **The census now ERRORS when a file handed to it is not censused.** A file it cannot read or
  parse, or whose suffix has no language record, is named and the run exits nonzero. Roy: *"I
  want a strong line -- all blocks are resolved or the program errors."* The reviewers are handed
  the CENSUS rather than the file list, so a gap there was invisible downstream.

- **Stale counts and refs in the shipped prose.** `verdicts.py` printed *"is not one of the
  eight"* when there are seven verdicts -- it now lists `VERDICTS` itself and cannot go stale
  again. `run_context.py` claimed *"the eleven questions this packet asks"* (nine) and *"the
  other eight are prose"* twice (six). `prove_unchanged.py` cited *"the 3.9 floor this script
  promises"* when the floor is 3.11. ! The one count that had NOT drifted is the one a test
  asserts against `len(REQUIRED)`.

### Changed

- **`census.py` is split into three modules, each announcing ONE subject.** Roy: *"I don't think
  census.py would pass the module-context pass."* `repo.py` answers what the checkout says (git,
  the filesystem, the exception tuples) and was already a shared layer nobody had declared --
  two other scripts imported it *from* `census.py`. `annotate.py` is stage 3, the resolution a
  reviewer would otherwise do by hand. `census.py` keeps stage 2 and composes the three.
  ! The cut was decided by a dependency, not by taste.

- **The shipped Python's own prose, rewritten to say what the code does.** Roy: *"I don't want
  the system picking up bad cues from the documentation in the code."* Comment and docstring
  lines stating what the code does NOT do went from **136 / 697 (20%) to 51 / 778 (6%)** across
  all eight scripts. The residue is deliberate: each survivor names an OUTPUT, a refusal aimed
  at the next editor, or a state distinction the code turns on.

- **Quoted run statistics removed from the shipped prose.** Roy's discriminator: does the number
  teach a reviewer to CHECK a number, or only report what happened here? Ten went, including
  *"5 of 7 reviewer reports FABRICATED"*, *"14 en-GB spellings"* (twice), *"2 of 28 authored
  docstrings"* and *"548 blocks"* -- Roy, on the last: an agent may go looking for that number of
  blocks. ! A number inside an INVENTED example STAYS, because it teaches that a number in prose
  is a checkable claim.

- **The environment floor is stated once: a LOCAL GIT REPOSITORY.** `git ls-files` answers and
  `git show <ref>:<path>` answers for a ref that exists. Everything else is CHECKED -- an
  upstream, a merge base, a clean tree, a cwd at the repo root. With no upstream, scope from
  `target`, else `git diff --name-only HEAD`, and NAME which of the three was used.

- **`docs/limitations.md` asks a fourth question, and its example rule generalised.** The fourth
  is *"is the REASON true in a fresh checkout?"* -- a rule can be right with a reason fitted to
  this repo's harness. The invented-example rule became *"an example carries the SHAPE and
  nothing else"*, whose second case is that an example must not reuse a settled term in a
  foreign sense. ! Nothing automated catches that: `vocabulary_sweep.py` skips words already
  settled, and `check_vocabulary.py` compares distribution against usage, never usage against
  meaning.



## [0.1.4] -- 2026-08-16

**One source for the vocabulary, emitted to each agent.** 0.1.3 settled what every term MEANS.
This carries the terms to the agents that use them, and takes the definitions back out of the
prose that used to state them in passing.

### Changed -- BREAKING

- **The reviewer record's opener is `--- RECORD`, not `--- FINDING`.** `FINDING` was the opener
  AND one of the eight fields, so the word named the container and one row of it. Roy, reading
  the brief's own example: *"is it the emitted full table or is it the row in the table?"* A
  report emitting `--- FINDING` now parses to nothing and every block it covered is a coverage
  gap.

- **Every block is a RECORD, `clean` included; the `CLEAN` range list is gone.** A report reading
  only `CLEAN 1-N` accounted for every index, cited nothing, and exited 0 having read no file --
  the cheapest fabrication, and one `verdicts.py`'s own docstring described as uncatchable. A
  `clean` record carries a BLOCK, a VERDICT and a LOCATION, and the LOCATION is resolved against
  the tree, so covering N blocks costs N records that each name a real prose range. `CLEAN_LINE`
  and `_expand` are deleted; `coverage_gaps` now takes who REPORTED rather than who declared a
  range, so a report that parses to nothing shows every block missing instead of vanishing.

- **A block outside your role is `query`, not `clean`.** Decided when the three `query` shapes
  were written and contradicted in three files since. `clean` certifies, and a role that did not
  read the block has certified nothing.

- **`referrers.py` withholds nothing.** `NOISE_FLOOR` and the `SUPPRESSED` report are deleted:
  a token naming more than 40 tracked files was printed as a name and a count instead of per
  file. Roy: *"We are not going for an 'optimization based comment review'."* The test is
  inverted rather than removed -- a token naming 41 files is asserted to appear per file.

- **The CODE CHECK's second kind is `stripped`, not `residue`**, so a report line reads
  `PROVEN sample.go: reads the same (stripped)`. Two things wore `residue` and they operate on
  opposite material: one takes the comments OUT of the code, the other asks what is left OF the
  comments after an edit. The prose check keeps the word.

### Added

- **`references/vocabulary.toml`** -- 45 definitions written ONCE, and a per-role list of keys.
  **`scripts/vocabulary.py --reviewer <role>`** prints the block the task agent pastes into that
  agent's prompt, verbatim. Roy: *"No summarizing no duplication. The task agent already has to
  run python commands. this is just one more."* Which terms a role gets was MEASURED from the
  text that role actually reads, not judged.

- **`edit mark`** is defined, and emitted to the four editorial roles: *"What you emit on a
  sentence: the VERDICT together with its payload. The preferred action -- what WOULD improve or
  correct the prose if it were applied. A mark is not the action; marking and applying are
  different stages and different actors."* The brief had used the term without ever stating it.

- **A DRIFT check.** `scripts/check_vocabulary.py` verifies that every term a role is given
  appears in the text that role reads, and every term it reads is given. The role -> files
  mapping is DERIVED from the agent files rather than listed, so it cannot go stale the way the
  term lists did. It found 26 drifted terms on the day it was written.

### Changed

- **The prose stops defining terms it uses.** Three groups: whole statements whose only job was
  a definition; definitions carried as a clause inside a working sentence; and the verdict
  table's "use it when" column, which is a definition while its "payload" column is a rule. The
  test Roy set: *"a definition says what a word means and is emitted; a rule says what to do
  about it and stays."*

- **The two survey documents are deleted.** `vocabulary-usage.md` (2,331 lines) and
  `vocabulary-inventory.md` (329) were the apparatus for FINDING the terms -- a twelve-agent
  collection, per-bundle tables, and 1,590 `file:line` citations into a tree since rewritten.
  `docs/vocabulary.md` (106 lines) keeps the settled state: the task agent's terms, the one term
  kept with no shipped use, and every retired word.

- **`reviewer-brief.md` 265 -> 201 lines**, the file every reviewer loads once per run.

### Fixed

- **A rule that primed every role to count.** It told all four how to report a count, in a file
  where the only number a role has is the census index range they are all handed identically.
  Roy: *"They shouldn't have anything that indicates that something is worth counting."* ! It
  demonstrated its own defect first: rewriting rather than deleting it, four exchanges went on
  WHICH ROLES COUNT instead of ruling on blocks.

- **The coverage rule was told to the wrong reader.** *"A block nobody mentioned is a gap in the
  review, not a block that passed"* is a CROSS-ROLE fact; one reviewer sees only its own report.
  Out of the brief and out of both scripts' output headers, which now state what they printed.

- **A third harness leak.** The existence-grep trap primed all four roles with a trap only one
  can meet; it now sits in `block-context` and states the failure in order rather than asserting
  the rule.


## [0.1.3] -- 2026-08-16

! **Held back when it was cut.** Roy: *"do not land -- the implications of the changes need to
be worked through."* Those implications became 0.1.4, and both releases landed on `main`
together.

**Settling the system's own vocabulary.** A twelve-agent collection over the live tree found
nine terms used with a fixed sense and stated nowhere, and fifteen more carrying two or three
senses each. Each was ruled in turn -- state the meaning, split the word, or delete the
use -- and the ones that changed a published name are below. Terms are settled in order of what
POINTS at them: names living in identifiers, filenames and flags first, because those are the
ones that can dangle. The settled state: `docs/vocabulary.md`.

! **It is closed, and closed by COMMAND.** `python scripts/check_vocabulary.py` reports 185
inventory rows with 0 lacking a ruling, and 1590 citations with 0 broken. Every term is
defined, dropped, or declared as deliberate polysemy.

### Changed -- BREAKING

- **The shipped floor is Python 3.11, raised from 3.9.** Roy, 2026-08-16: *"3.9 went end of life
  last year, 3.10 probably goes end of life in 2 months."* The floor had been set BELOW the
  oldest supported Python -- 3.9 ended October 2025, 3.10 ends October 2026 -- and it blocked two
  design choices in one conversation: `tomllib` and `StrEnum`, both 3.11, both of which PARSE at
  the old floor and fail at import, which `check_shipped_syntax.py` cannot see.

  `FLOOR = (3, 11)` and `target-version = "py311"`. ! The formatter rewrote **nothing** in
  `plugins/` at the new target, so no shipped file changed shape. ! The rule that no `except`
  clause may hold a tuple literal STILL stands: PEP 758's unparenthesised form is 3.14, so a
  repo targeting py314 can still rewrite shipped code into syntax 3.11 rejects.

  Users on 3.9 or 3.10 are no longer supported.

- **`reanchor` is gone; there are eight verdicts, not nine.** A relocation is one
  judgment. Whether prose belongs ten lines down, in another file, or out of the code
  entirely is the DESTINATION -- which the payload already carried -- and the reason it
  belongs there is `FINDING`, a field every record already has. The two-word split was
  encoding in the verdict what the record has fields for. **A report emitting `reanchor`
  is now rejected at the stage-5 gate as a verdict outside the set.**

  Two rules that used to key on the verdict now key on the destination, which is what
  makes the collapse safe rather than lossy:

  - **Availability.** Only a destination OUTSIDE the code needs the tree resolved at 1.4,
    so only that case can be UNAVAILABLE. A relocation into tracked code is never
    withheld. Previously an in-file relocation labelled `move` was converted to `clean`
    and the finding was lost -- measured on a real run. That failure mode is removed, not
    documented.
  - **Synthesis order.** A `move` leaving the code is applied at step 2 with `drop`
    ("take out what is leaving"); a `move` staying inside it waits until step 6, because
    it removes nothing.

  `fact-check` carries no relocation verdict, so a true-but-misplaced block is `query`
  there -- unchanged, and still never `clean`.

- **`angle` is retired. The four are EDITORIAL ROLES.** The word came from the `/simplify`
  skill, which uses it for the focuses that pass works at; it stopped fitting once these
  became agents with scopes, and it was the most-used term in the tree with no definition
  anywhere -- six senses at ~250 sites. Prose now says **editorial role**. Identifiers say
  **reviewer**, because `role` alone would also cover the task agent and the absent author,
  who are roles in `SKILL.md`'s own cast.

  | was | now |
  | --- | --- |
  | `verdicts.py --angles` | `verdicts.py --reviewers` |
  | the packet's `## ANGLE FILES` section | `## REVIEWER FILES` |
  | "the four angles", "from this angle" | "the four editorial roles", "from this role" |

  A saved dispatch packet with an `## ANGLE FILES` heading now fails `run_context.py --check`
  with that section reported missing, and a scripted `--angles` invocation fails at argument
  parsing. Both are the intended failure: no alias is accepted, because a script whose own
  rule is that nothing degrades quietly should not answer to a name it no longer uses.

- **`budget` meant four things; now it means one.** Roy's ruling: **the only real budget is
  what a shipped instruction file costs everyone to load**, measured in lines per file and
  declared at `docs/limitations.md:9`. A comment's line limit is `cap`, already defined -- an
  undefined word had been standing in for a defined one at five sites. The reviewer's-runtime
  sense loses the word. ! The twelve-agent vocabulary collection missed this term entirely --
  18 sites, four senses, in neither table -- so the survey is a floor, not a census. ! Measured
  while settling it: the budget covers 28 KB of the 224 KB shipped, and not `reviewer-brief.md`
  (18 KB, loaded once per reviewer) or `SKILL.md` (47 KB) -- the two largest files a run loads.

- **Stage 7b's gate is the CODE CHECK, not "the proof".** The editorial metaphor had already
  given `proof` to stage 8 -- in publishing a proof is a trial copy read for errors, which is
  what stage 8 does and why its agent is `PROOFREADER`. 7b's was a logical proof, the same
  spelling and an unrelated word. `proof` now names stage 8's pass and the level named for it,
  and nothing else. "AST proof" went with it: that phrase named the Python branch while being
  used for a gate that also covers every other language.

- **It no longer claims byte identity, because it never had it.** `_residue()` right-strips
  every line and drops blanks before comparing, so the script's own *"compare what remains,
  byte for byte"* and its `PROVEN ... code identical` report were both overstated. It compares a
  PROJECTION -- for Python the AST with docstrings blanked, otherwise the comment-stripped
  lines -- and what it proves is that **the parser reads the file the same**, which should mean
  the code says the same and for Python does. Elsewhere it rests on a lexer built from a data
  row, so where that lexer is unsure it refuses rather than guesses. That is also why line
  endings have always needed a separate check beside it.

- **Reviewers no longer receive a CAP or a WIDTH.** The stage-4 packet had carried both, and
  `run_context.py --check` REFUSED a packet whose `CAP` was blank -- enforcing the opposite of
  the rule stated since the import at `SKILL.md:211` ("never passed to a reviewer") and
  `reviewer-brief.md:292` ("You are not given the cap"). The reason is the brief's own: an
  agent that knows the cap writes to the cap, and what survives a length-driven cut is the
  confident assertion, never the evidence that lets a reader test it. `WIDTH` went with it
  under the same existing rule -- "Length is not an editorial role" -- not a new one.
  **A saved packet with `## CAP` or `## WIDTH` still passes** (unknown sections are ignored);
  what changed is that a packet WITHOUT them now passes, and reviewers are not handed a length
  constraint. The packet is 9 sections, 6 of them prose no oracle settles. The cap still
  reaches stage 6 through `compact.md`'s own input contract, and `census.py --cap` is
  unaffected.

- **The census's `marks` are `annotations`.** `mark` named four things; the metaphor settles
  which keeps it. In publishing, *editorial marks* are what an editor writes on a manuscript --
  delete, transpose, insert, stet -- which is a verdict, and what stage 4 emits. The census's
  are mechanical observations about the text. ! The tell was in the numbering: the marks table
  sat inside `SKILL.md`'s **"Stages 2-3 -- ANNOTATE, then FIND REFERENCES"**, so they were made
  one stage BEFORE the stage called MARK -- and `SKILL.md` already called them *"annotations on
  a node"*.

  | was | now |
  | --- | --- |
  | `block.marks` | `block.annotations` |
  | `mark()` | `annotate()` |
  | the `"marks"` census JSON key | `"annotations"` |

  **A saved census breaks.** The key is a published interface; anything reading one must be
  updated. Work MARKERS (`TODO`, `FIXME`) are untouched, and "marked" in the verdict sense is
  unchanged pending the edit-mark work.

- **Stage 5 is APPLY; stage 7b is WRITE.** `apply` had come to name both -- applying a MARK to
  produce replacement text (5), and applying approved text to disk (7b). Applying a mark is
  what stage 5 does, and it is the sense the skill's own verdict table already used
  (*"apply the true/false pair"*), so stage 5 takes the word and 7b takes `WRITE`, which says
  what it alone does: touch a file. **`references/apply.md` is now `references/write.md`** --
  anything loading it by path must be updated. Stage 5's old name `EDIT` is retired.

- **`sweep` is not a term.** Every canonical naming site already said so -- `SKILL.md`'s
  pipeline diagram, its stage table, and the reference filename.
  `sweep` was a synonym that outlived `sweep.py`, the module now called `census.py`. Retired
  at 12 sites; the 5 plain-English uses ("do NOT sweep the file") are kept and are no longer
  ambiguous, there being no name left to collide with.

- **`HOME` is retired. A comment's placement question has ONE stem: OWN.** The **owner** of a
  comment is the anchor with the best justification for it being attached there. Where several
  candidates compete, it is the site that ENFORCES the constraint -- or, where nothing enforces
  it, the code still expected to hold the invariant. `HOME` named that same site under a second
  stem. `anchor` stays the mechanical code position, `ownership` is the relation, and `owner` is
  the anchor that wins it.

  The section that selected it was REPLACED, not renamed. It read *"the correct existing anchor
  point among the sites where the claim is already stated, not the function that implements the
  rule"* -- which excludes the enforcing site, and limits the candidates to sites that already
  carry prose. Neither holds now: the enforcing site owns the claim whether or not anything is
  written there today.

- **`Block.owner` is now `Block.anchor`, and the census JSON key with it.** The field holds the
  declaration on the line after a comment run ends. That is a POSITION; ownership is a judgement
  no parser makes, so the name claimed something the census never computed. `census.py --json`
  emits `vars(b)`, so the key changed with the field, and the printed tree's `(owner)` column is
  now `(anchor)`. Anything reading a saved census for `owner` finds nothing.

- **A role's categories of claim are its REMIT.** `own` carried this second relation at
  five sites -- *"Owns three kinds of claim"*, *"owns reachability"*, *"the block-context role
  owns quantified claims"* -- alongside the placement sense above, and stated it nowhere.
  `verify` was considered and rejected: it already names the ACT of settling one claim against
  the code, and the citation state `UNVERIFIABLE`. A remit is which claims are a role's;
  verification is what the role does to them.

- **Absence left `ownership-context`.** The split between it and `module-context` is PRESENCE:
  prose that EXISTS and sits away from its owner is ownership-context's; documentation that is
  MISSING is module-context's -- which is what the verdict shapes already said, `move`/`drop`
  against `add`. The one rule that crossed it (an `add` for a line carrying a non-obvious
  constraint with no comment at all) is deleted from the agent file and the README; the case is
  already covered by `function-context`'s absence question and `module-context`'s surface
  checklist. Ownership-context drops from 101 to 96 lines.

  The brief now also states WHY two roles may reach the same block: **remits overlap by
  design**, because the roles read the same code bottom-up and top-down. Both findings still
  stand, and neither role defers to the other -- unchanged, now with a reason attached.

- **The acquittal list and the suppression list are DELETED from the reviewer brief.** The
  acquittal list matched a prose SHAPE and called itself *"the ONLY reasons to pass a block
  over"* -- but what decides `clean` is stated per role, and every one of those is a TRUTH
  assertion at that role's scope, so a block true of the code beside it but matching no label
  was `clean` by its role's file and a finding by the brief. Its measurement does not support it
  either: `evidence/ga/` scored ten candidate SKILL.md rewrites on how much of ONE later commit's
  prose rewrite of SIX files they rediscovered, and the search's own conclusion was *"the
  acquittal RATE is the trait; the acquittal LIST is just vocabulary."* The suppression list has
  no provenance in `evidence/` at all and suppressed nothing.

  `reviewer-brief.md` drops 299 -> 266 lines. The anti-rationalisation rule survives, moved into
  `clean`'s own section: **nothing is `clean` for being SHORT, TRUE, WELL WRITTEN, NEW, or under
  a `!`.** What was inside the lists is held in
  `TODO/the-two-lists-were-tuned-to-one-diff.md` rather than deleted outright.

- **Stage 8 REVIEW no longer edits, and it reads for everything.** It was a proofread that
  repaired damage its own run caused; it is now a verification with two outcomes -- the files are
  done, or a section goes to the human as potentially something to fix. A pass that repairs after
  the human approved at 7a puts prose on disk nobody read. It now asks of every comment whether
  it follows the style sheet's template, is still appropriate to the code it is attached to, has
  SENTENCES that are checkable claims, and states the reasons, constraints and worked examples
  that code needs -- then whether the file still reads as one page.

  ! It also names nothing outside itself. It referenced other stages at four sites and the
  residue check by name; a stage's file describes that stage's inputs and its job, because
  naming the surrounding machinery tells an agent where to go looking.

- **`referrers.py` no longer withholds anything.** `NOISE_FLOOR` and the `SUPPRESSED` report
  block are deleted: a token naming more than 40 tracked files was printed as a name and a count
  instead of per file. This is an input to a review, and a reader deciding what to open is served
  by the whole list. 203 -> 185 lines, and the test is inverted rather than removed -- a token
  naming 41 files is now asserted to appear per file.

- **The CODE CHECK's second kind is `stripped`, not `residue`.** `code_fingerprint` returns
  `ast`, `stripped` or `unprovable`, so a report line now reads
  `PROVEN sample.go: reads the same (stripped)`. Two things wore `residue` and they operate on
  opposite material: one takes the comments OUT of the code and compares what remains, the other
  asks what is left OF the comments after an edit. The prose check keeps the word.

### Added

- **Seven terms that were used with a fixed sense and stated nowhere now have one stating
  site, or are gone.** `prose tree` and `node` at `SKILL.md:76`, `the join` at `:526`,
  `detector` in `reviewer-brief.md`, `banner` in `comment-review-module-context.md`.
  **Deleted rather than defined:** `assessability gate` (used once, in frontmatter, and the
  idea was already stated without it) and `acquittal rate` (a measured quantity no site gave a
  denominator for -- both uses now name the population instead). No new sections: each
  statement went into a sentence that already described the thing without naming it, so the
  four agent files are unchanged at 101/101/129/120 lines.

- **`scripts/check_vocabulary.py`** -- the two vocabulary documents hold their shape: every
  `file:line` citation resolves, and every inventory row carries a ruling. Both checks exist
  because each failure had already happened silently -- one deletion stranded 29 citations past
  the end of their files, and six rows read `UNDEFINED` for terms settled a day earlier because
  each term appears twice and only one copy was maintained.

- **`scripts/vocabulary_sweep.py`** -- terms of art in the shipped tree the inventory does not
  list. An input, not a gate. Raw frequency was tried and discarded (it ranks `here` and
  `because` above every real term); what works is DOUBLE USE -- a word in the prose AND bound as a
  module-level name in a script, which is the shape `budget`, `own`, `label`, `signature`,
  `residue` and `statement` each had.

- **The editorial metaphor is a rule in `CLAUDE.md`**, not only a description. A new term comes
  from publishing -- what would an editor, a copy desk or a proofreader call this? -- and a
  candidate is checked against the register before it is proposed, not after.

### Changed

- **`DOC CONVENTION` is measured, not named, and it is three things.** Stage 1.3 now reads the
  docstrings that exist and records the **module** format, the **function** format, and -- kept
  separate -- the **comment** format where the repo is consistent about one, writing a template
  out rather than naming the nearest standard. Naming a standard the repo does not follow is
  how a correct sentence lands in the wrong format. ! Its place in the reviewer packet had been
  justified by *"reviewers write replacement text"*, which is false; the real reason is that a
  docstring's format decides which of its lines are structural and which are prose. The
  templates live in the STYLE SHEET, which carries them to the reviewers, to stage 5 and to
  stage 6.

- **`statement`, `expression`, `declaration` and `assignment` name CODE.** They classify an
  ANCHOR; an OWNER is a judgement about which anchor best justifies the comment and is never a
  syntactic kind. The prose units are `sentence` and `clause`. ! `signature` was one of these
  words: the CODE CHECK's `code_signature` is now `code_fingerprint`, because the value it
  returns is an `ast.dump` or a comment-stripped text, not a signature.

- **`walk` is retired from the prose; a name the module docstring never accounts for is an
  OMISSION.** An editor READS a manuscript and CHECKS a list. `## Walk the census` is now
  `## Read the census end to end`, and *"coverage is a tree walk"* is *"coverage is a COMPLETE
  READ"*. OMISSION pairs with OBITUARY on the next line of the same list: an omission is in the
  CODE and absent from the prose, an obituary is in the PROSE and absent from the code.

- **`detector` is deleted; the word is `annotation`.** It was stated only inside the suppression
  list, and everything it supported went with that list.

- **`template` and `original` are stated.** A template is *a shape written out with its slots,
  not a shape NAMED* -- 19 sites across 5 files and no definition until now. The ORIGINAL is *the
  text as it stood when THIS RUN began*, which makes it relative to the run: a file this run
  edits is the next run's original.

### Fixed

- **Stage 7b no longer tells the applying agent to cut.** `references/write.md` was headed
  *"Shorten by TRUTH here -- never by LENGTH"* and opened *"This pass cuts, and it can cut a
  lot"*, four lines above its own *"Write the APPROVED text verbatim. Every question of truth,
  placement and length was settled upstream."* It had contradicted itself since the initial
  import. An agent following the first half would re-cut text the author had already approved --
  the exact failure the 7a/7b split, and compacting-before-approval, exist to prevent.

- **`evals/generator_split.py` runs again.** It did `import sweep` against a directory with no
  `sweep.py`, so the script could not start; the five attributes it uses are in `census.py`.
  `evals/grade_hazards.py` cited the same dead module.

- **A second harness leak, in `function-context`.** *"Run the guard with its EXEMPTIONS OFF"*
  rested on two measurements that `evidence/findings.md` files under **"More of my own errors"** --
  a session mis-invoking ruff on this repo's own config while doing documentation cleanup. Nothing
  bypasses a reviewer here, so the rule did not transfer. Deleted with its two dependants;
  `function-context` 129 -> 122 lines. The rule the section exists for is untouched: does the guard
  exist, and would it FAIL if the claim were false.

- **`SKILL.md`'s stage table listed stage 8's actor as the task agent** while `:756` dispatches
  `comment-review-review`, and `:190` still called it *"stage 8's PROOF PASS"*, a name retired
  when 7b's gate became the CODE CHECK.

## [0.1.2] -- 2026-08-15

### Changed -- BREAKING

- **The four reviewer agents are renamed for the scope each checks.** Anything dispatching
  them by their namespaced IDs must be updated:

  | was | now | asks |
  | --- | --- | --- |
  | `comment-review:comment-review-locality` | `comment-review:comment-review-ownership-context` | does this comment belong to the line it sits on? |
  | `comment-review:comment-review-currency` | `comment-review:comment-review-block-context` | is every claim in this block true of the code it sits with? |
  | `comment-review:comment-review-functionality` | `comment-review:comment-review-function-context` | does the commentary match what the function is for? |
  | `comment-review:comment-review-module-coherence` | `comment-review:comment-review-module-context` | do the comments say this module is one set of ideas? |

  `ownership-context` is a rewrite rather than a rename: `locality` asked whether prose sat
  in the right place, and the replacement asks first whether the prose is assessable where
  it sits at all.

- **`verdicts.py --angles` takes the new names.** It matches a declared angle against each
  report file's stem, so report files must be named for the new angles.

### Added

- **Each agent states what its own `clean` asserts.** `clean` is one of the nine verdicts
  and means "nothing to report from this angle"; what that claims differs per angle, and
  each agent file now says which.
- **`ownership-context`** -- claim homes (where one proposition is stated at several sites,
  which site is its home), duplication, and the assessability gate the other three depend on.
- **`block-context`** -- constraints checked against the line that enforces them (value,
  direction, units, boundary) and worked examples, which are executed rather than read.
- **`function-context`** -- the one-function test, and reading a body's comments in the order
  the body performs them.
- **`module-context`** -- walking the module's exposed surface as a checklist.
- **`truthy` is defined** in `references/reviewer-brief.md`: a sentence states one checkable
  proposition about the code it is attached to. It is a property of form, not of truth.
- **A placement precedence rule.** `ownership-context` and `function-context` can both reach
  a comment that is true but misplaced. Both findings stand, and where they name different
  destinations, `ownership-context`'s governs. Neither angle defers to the other; resolving
  the disagreement is the task agent's, not a reviewer's.
- **A line budget for the four agent files** in `docs/limitations.md`, so a rule added to one
  replaces another rather than accumulating.

### Fixed

- **`ownership-context` now runs at every level, including `fact-check`.** The other three
  measure a claim against the code at their scope, so a claim attached to the wrong scope was
  being measured against the wrong code and corrected into a falsehood.
- **`reanchor`'s availability depends on the level**, not only on whether a destination tree
  resolved. At `fact-check` the verdict set carries no `reanchor`, and the finding is `query`
  -- never `clean`.
- **`SKILL.md` no longer restates rules that `references/reviewer-brief.md` owns** -- the
  `query`/`reanchor` rule and the `move`/`reanchor` rule each had two statements that could
  drift apart.
- **The site-home cell no longer offers `move`** for relocating a claim within a file.
  Mislabelling an in-file relocation as `move` was measured converting the finding to `clean`
  and losing it.
- **A forward reference in `comment-review-block-context.md` names its target section**
  instead of pointing 42 lines away with "below".
