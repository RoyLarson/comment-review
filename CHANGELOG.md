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
