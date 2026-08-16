# Change Log

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

⚠ This file starts at 0.1.2. Earlier work is in `git log` and has no entry here — the
file existed as a one-line stub until this release. Neither
`plugins/comment-review/.claude-plugin/plugin.json` nor `.claude-plugin/marketplace.json`
carries a `version` field, so a version number lives only here and an installed plugin
cannot report which one it is.

⚠ **The PATCH number moves, whatever the change.** Roy, 2026-08-16: *"these will continue to be
bugfix versions. I know that is not really how developed systems are supposed to go but this is
mine now."* So a release carrying breaking renames is still `0.1.x`, and a section headed
**Changed — BREAKING** does not imply a minor bump here. Recorded so nobody reads a released
number as a semver claim, or "corrects" the next one to `0.2.0`.

## [Unreleased]

### Changed — BREAKING

- **The shipped floor is Python 3.11, raised from 3.9.** Roy, 2026-08-16: *"3.9 went end of life
  last year, 3.10 probably goes end of life in 2 months."* The floor had been set BELOW the
  oldest supported Python — 3.9 ended October 2025, 3.10 ends October 2026 — and it blocked two
  design choices in one conversation: `tomllib` and `StrEnum`, both 3.11, both of which PARSE at
  the old floor and fail at import, which `check_shipped_syntax.py` cannot see.

  `FLOOR = (3, 11)` and `target-version = "py311"`. ⚠ The formatter rewrote **nothing** in
  `plugins/` at the new target, so no shipped file changed shape. ⚠ The rule that no `except`
  clause may hold a tuple literal STILL stands: PEP 758's unparenthesised form is 3.14, so a
  repo targeting py314 can still rewrite shipped code into syntax 3.11 rejects.

  Users on 3.9 or 3.10 are no longer supported.

## [0.1.3] — 2026-08-16

⚠ **Released, NOT merged.** Roy: *"do not land — the implications of the changes need to be
worked through."* The branch is `feat/settle-the-vocabulary`; `main` is still 0.1.2.

**Settling the system's own vocabulary.** A twelve-agent collection over the live tree found
nine terms used with a fixed sense and stated nowhere, and fifteen more carrying two or three
senses each. Each was ruled in turn — state the meaning, split the word, or delete the
use — and the ones that changed a published name are below. Terms are settled in order of what
POINTS at them: names living in identifiers, filenames and flags first, because those are the
ones that can dangle. Survey: `docs/vocabulary-usage.md`.

⚠ **It is closed, and closed by COMMAND.** `python scripts/check_vocabulary.py` reports 185
inventory rows with 0 lacking a ruling, and 1590 citations with 0 broken. Every term is
defined, dropped, or declared as deliberate polysemy.

### Changed — BREAKING

- **`reanchor` is gone; there are eight verdicts, not nine.** A relocation is one
  judgment. Whether prose belongs ten lines down, in another file, or out of the code
  entirely is the DESTINATION — which the payload already carried — and the reason it
  belongs there is `FINDING`, a field every record already has. The two-word split was
  encoding in the verdict what the record has fields for. **A report emitting `reanchor`
  is now rejected at the stage-5 gate as a verdict outside the set.**

  Two rules that used to key on the verdict now key on the destination, which is what
  makes the collapse safe rather than lossy:

  - **Availability.** Only a destination OUTSIDE the code needs the tree resolved at 1.4,
    so only that case can be UNAVAILABLE. A relocation into tracked code is never
    withheld. Previously an in-file relocation labelled `move` was converted to `clean`
    and the finding was lost — measured on a real run. That failure mode is removed, not
    documented.
  - **Synthesis order.** A `move` leaving the code is applied at step 2 with `drop`
    ("take out what is leaving"); a `move` staying inside it waits until step 6, because
    it removes nothing.

  `fact-check` carries no relocation verdict, so a true-but-misplaced block is `query`
  there — unchanged, and still never `clean`.

- **`angle` is retired. The four are EDITORIAL ROLES.** The word came from the `/simplify`
  skill, which uses it for the focuses that pass works at; it stopped fitting once these
  became agents with scopes, and it was the most-used term in the tree with no definition
  anywhere — six senses at ~250 sites. Prose now says **editorial role**. Identifiers say
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
  declared at `docs/limitations.md:9`. A comment's line limit is `cap`, already defined — an
  undefined word had been standing in for a defined one at five sites. The reviewer's-runtime
  sense loses the word. ⚠ The twelve-agent vocabulary collection missed this term entirely —
  18 sites, four senses, in neither table — so the survey is a floor, not a census. ⚠ Measured
  while settling it: the budget covers 28 KB of the 224 KB shipped, and not `reviewer-brief.md`
  (18 KB, loaded once per reviewer) or `SKILL.md` (47 KB) — the two largest files a run loads.

- **Stage 7b's gate is the CODE CHECK, not "the proof".** The editorial metaphor had already
  given `proof` to stage 8 — in publishing a proof is a trial copy read for errors, which is
  what stage 8 does and why its agent is `PROOFREADER`. 7b's was a logical proof, the same
  spelling and an unrelated word. `proof` now names stage 8's pass and the level named for it,
  and nothing else. "AST proof" went with it: that phrase named the Python branch while being
  used for a gate that also covers every other language.

- **It no longer claims byte identity, because it never had it.** `_residue()` right-strips
  every line and drops blanks before comparing, so the script's own *"compare what remains,
  byte for byte"* and its `PROVEN … code identical` report were both overstated. It compares a
  PROJECTION — for Python the AST with docstrings blanked, otherwise the comment-stripped
  lines — and what it proves is that **the parser reads the file the same**, which should mean
  the code says the same and for Python does. Elsewhere it rests on a lexer built from a data
  row, so where that lexer is unsure it refuses rather than guesses. That is also why line
  endings have always needed a separate check beside it.

- **Reviewers no longer receive a CAP or a WIDTH.** The stage-4 packet had carried both, and
  `run_context.py --check` REFUSED a packet whose `CAP` was blank — enforcing the opposite of
  the rule stated since the import at `SKILL.md:211` ("never passed to a reviewer") and
  `reviewer-brief.md:292` ("You are not given the cap"). The reason is the brief's own: an
  agent that knows the cap writes to the cap, and what survives a length-driven cut is the
  confident assertion, never the evidence that lets a reader test it. `WIDTH` went with it
  under the same existing rule — "Length is not an editorial role" — not a new one.
  **A saved packet with `## CAP` or `## WIDTH` still passes** (unknown sections are ignored);
  what changed is that a packet WITHOUT them now passes, and reviewers are not handed a length
  constraint. The packet is 9 sections, 6 of them prose no oracle settles. The cap still
  reaches stage 6 through `compact.md`'s own input contract, and `census.py --cap` is
  unaffected.

- **The census's `marks` are `annotations`.** `mark` named four things; the metaphor settles
  which keeps it. In publishing, *editorial marks* are what an editor writes on a manuscript —
  delete, transpose, insert, stet — which is a verdict, and what stage 4 emits. The census's
  are mechanical observations about the text. ⚠ The tell was in the numbering: the marks table
  sat inside `SKILL.md`'s **"Stages 2–3 — ANNOTATE, then FIND REFERENCES"**, so they were made
  one stage BEFORE the stage called MARK — and `SKILL.md` already called them *"annotations on
  a node"*.

  | was | now |
  | --- | --- |
  | `block.marks` | `block.annotations` |
  | `mark()` | `annotate()` |
  | the `"marks"` census JSON key | `"annotations"` |

  **A saved census breaks.** The key is a published interface; anything reading one must be
  updated. Work MARKERS (`TODO`, `FIXME`) are untouched, and "marked" in the verdict sense is
  unchanged pending the edit-mark work.

- **Stage 5 is APPLY; stage 7b is WRITE.** `apply` had come to name both — applying a MARK to
  produce replacement text (5), and applying approved text to disk (7b). Applying a mark is
  what stage 5 does, and it is the sense the skill's own verdict table already used
  (*"apply the true/false pair"*), so stage 5 takes the word and 7b takes `WRITE`, which says
  what it alone does: touch a file. **`references/apply.md` is now `references/write.md`** —
  anything loading it by path must be updated. Stage 5's old name `EDIT` is retired.

- **`sweep` is not a term.** Every canonical naming site already said so — `SKILL.md`'s
  pipeline diagram, its stage table, and the reference filename.
  `sweep` was a synonym that outlived `sweep.py`, the module now called `census.py`. Retired
  at 12 sites; the 5 plain-English uses ("do NOT sweep the file") are kept and are no longer
  ambiguous, there being no name left to collide with.

- **`HOME` is retired. A comment's placement question has ONE stem: OWN.** The **owner** of a
  comment is the anchor with the best justification for it being attached there. Where several
  candidates compete, it is the site that ENFORCES the constraint — or, where nothing enforces
  it, the code still expected to hold the invariant. `HOME` named that same site under a second
  stem. `anchor` stays the mechanical code position, `ownership` is the relation, and `owner` is
  the anchor that wins it.

  The section that selected it was REPLACED, not renamed. It read *"the correct existing anchor
  point among the sites where the claim is already stated, not the function that implements the
  rule"* — which excludes the enforcing site, and limits the candidates to sites that already
  carry prose. Neither holds now: the enforcing site owns the claim whether or not anything is
  written there today.

- **`Block.owner` is now `Block.anchor`, and the census JSON key with it.** The field holds the
  declaration on the line after a comment run ends. That is a POSITION; ownership is a judgement
  no parser makes, so the name claimed something the census never computed. `census.py --json`
  emits `vars(b)`, so the key changed with the field, and the printed tree's `(owner)` column is
  now `(anchor)`. Anything reading a saved census for `owner` finds nothing.

- **A role's categories of claim are its REMIT.** `own` carried this second relation at
  five sites — *"Owns three kinds of claim"*, *"owns reachability"*, *"the block-context role
  owns quantified claims"* — alongside the placement sense above, and stated it nowhere.
  `verify` was considered and rejected: it already names the ACT of settling one claim against
  the code, and the citation state `UNVERIFIABLE`. A remit is which claims are a role's;
  verification is what the role does to them.

- **Absence left `ownership-context`.** The split between it and `module-context` is PRESENCE:
  prose that EXISTS and sits away from its owner is ownership-context's; documentation that is
  MISSING is module-context's — which is what the verdict shapes already said, `move`/`drop`
  against `add`. The one rule that crossed it (an `add` for a line carrying a non-obvious
  constraint with no comment at all) is deleted from the agent file and the README; the case is
  already covered by `function-context`'s absence question and `module-context`'s surface
  checklist. Ownership-context drops from 101 to 96 lines.

  The brief now also states WHY two roles may reach the same block: **remits overlap by
  design**, because the roles read the same code bottom-up and top-down. Both findings still
  stand, and neither role defers to the other — unchanged, now with a reason attached.

- **The acquittal list and the suppression list are DELETED from the reviewer brief.** The
  acquittal list matched a prose SHAPE and called itself *"the ONLY reasons to pass a block
  over"* — but what decides `clean` is stated per role, and every one of those is a TRUTH
  assertion at that role's scope, so a block true of the code beside it but matching no label
  was `clean` by its role's file and a finding by the brief. Its measurement does not support it
  either: `evidence/ga/` scored ten candidate SKILL.md rewrites on how much of ONE later commit's
  prose rewrite of SIX files they rediscovered, and the search's own conclusion was *"the
  acquittal RATE is the trait; the acquittal LIST is just vocabulary."* The suppression list has
  no provenance in `evidence/` at all and suppressed nothing.

  `reviewer-brief.md` drops 299 → 266 lines. The anti-rationalisation rule survives, moved into
  `clean`'s own section: **nothing is `clean` for being SHORT, TRUE, WELL WRITTEN, NEW, or under
  a `⚠`.** What was inside the lists is held in
  `TODO/the-two-lists-were-tuned-to-one-diff.md` rather than deleted outright.

- **Stage 8 REVIEW no longer edits, and it reads for everything.** It was a proofread that
  repaired damage its own run caused; it is now a verification with two outcomes — the files are
  done, or a section goes to the human as potentially something to fix. A pass that repairs after
  the human approved at 7a puts prose on disk nobody read. It now asks of every comment whether
  it follows the style sheet's template, is still appropriate to the code it is attached to, has
  SENTENCES that are checkable claims, and states the reasons, constraints and worked examples
  that code needs — then whether the file still reads as one page.

  ⚠ It also names nothing outside itself. It referenced other stages at four sites and the
  residue check by name; a stage's file describes that stage's inputs and its job, because
  naming the surrounding machinery tells an agent where to go looking.

- **`referrers.py` no longer withholds anything.** `NOISE_FLOOR` and the `SUPPRESSED` report
  block are deleted: a token naming more than 40 tracked files was printed as a name and a count
  instead of per file. This is an input to a review, and a reader deciding what to open is served
  by the whole list. 203 → 185 lines, and the test is inverted rather than removed — a token
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
  denominator for — both uses now name the population instead). No new sections: each
  statement went into a sentence that already described the thing without naming it, so the
  four agent files are unchanged at 101/101/129/120 lines.

- **`scripts/check_vocabulary.py`** — the two vocabulary documents hold their shape: every
  `file:line` citation resolves, and every inventory row carries a ruling. Both checks exist
  because each failure had already happened silently — one deletion stranded 29 citations past
  the end of their files, and six rows read `UNDEFINED` for terms settled a day earlier because
  each term appears twice and only one copy was maintained.

- **`scripts/vocabulary_sweep.py`** — terms of art in the shipped tree the inventory does not
  list. An input, not a gate. Raw frequency was tried and discarded (it ranks `here` and
  `because` above every real term); what works is DOUBLE USE — a word in the prose AND bound as a
  module-level name in a script, which is the shape `budget`, `own`, `label`, `signature`,
  `residue` and `statement` each had.

- **The editorial metaphor is a rule in `CLAUDE.md`**, not only a description. A new term comes
  from publishing — what would an editor, a copy desk or a proofreader call this? — and a
  candidate is checked against the register before it is proposed, not after.

### Changed

- **`DOC CONVENTION` is measured, not named, and it is three things.** Stage 1.3 now reads the
  docstrings that exist and records the **module** format, the **function** format, and — kept
  separate — the **comment** format where the repo is consistent about one, writing a template
  out rather than naming the nearest standard. Naming a standard the repo does not follow is
  how a correct sentence lands in the wrong format. ⚠ Its place in the reviewer packet had been
  justified by *"reviewers write replacement text"*, which is false; the real reason is that a
  docstring's format decides which of its lines are structural and which are prose. The
  templates live in the STYLE SHEET, which carries them to the reviewers, to stage 5 and to
  stage 6.

- **`statement`, `expression`, `declaration` and `assignment` name CODE.** They classify an
  ANCHOR; an OWNER is a judgement about which anchor best justifies the comment and is never a
  syntactic kind. The prose units are `sentence` and `clause`. ⚠ `signature` was one of these
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
  not a shape NAMED* — 19 sites across 5 files and no definition until now. The ORIGINAL is *the
  text as it stood when THIS RUN began*, which makes it relative to the run: a file this run
  edits is the next run's original.

### Fixed

- **Stage 7b no longer tells the applying agent to cut.** `references/write.md` was headed
  *"Shorten by TRUTH here — never by LENGTH"* and opened *"This pass cuts, and it can cut a
  lot"*, four lines above its own *"Write the APPROVED text verbatim. Every question of truth,
  placement and length was settled upstream."* It had contradicted itself since the initial
  import. An agent following the first half would re-cut text the author had already approved —
  the exact failure the 7a/7b split, and compacting-before-approval, exist to prevent.

- **`evals/generator_split.py` runs again.** It did `import sweep` against a directory with no
  `sweep.py`, so the script could not start; the five attributes it uses are in `census.py`.
  `evals/grade_hazards.py` cited the same dead module.

- **A second harness leak, in `function-context`.** *"Run the guard with its EXEMPTIONS OFF"*
  rested on two measurements that `evidence/findings.md` files under **"More of my own errors"** —
  a session mis-invoking ruff on this repo's own config while doing documentation cleanup. Nothing
  bypasses a reviewer here, so the rule did not transfer. Deleted with its two dependants;
  `function-context` 129 → 122 lines. The rule the section exists for is untouched: does the guard
  exist, and would it FAIL if the claim were false.

- **`SKILL.md`'s stage table listed stage 8's actor as the task agent** while `:756` dispatches
  `comment-review-review`, and `:190` still called it *"stage 8's PROOF PASS"*, a name retired
  when 7b's gate became the CODE CHECK.

## [0.1.2] — 2026-08-15

### Changed — BREAKING

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
- **`ownership-context`** — claim homes (where one proposition is stated at several sites,
  which site is its home), duplication, and the assessability gate the other three depend on.
- **`block-context`** — constraints checked against the line that enforces them (value,
  direction, units, boundary) and worked examples, which are executed rather than read.
- **`function-context`** — the one-function test, and reading a body's comments in the order
  the body performs them.
- **`module-context`** — walking the module's exposed surface as a checklist.
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
  — never `clean`.
- **`SKILL.md` no longer restates rules that `references/reviewer-brief.md` owns** — the
  `query`/`reanchor` rule and the `move`/`reanchor` rule each had two statements that could
  drift apart.
- **The site-home cell no longer offers `move`** for relocating a claim within a file.
  Mislabelling an in-file relocation as `move` was measured converting the finding to `clean`
  and losing it.
- **A forward reference in `comment-review-block-context.md` names its target section**
  instead of pointing 42 lines away with "below".
