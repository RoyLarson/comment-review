# Change Log

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

⚠ This file starts at 0.1.2. Earlier work is in `git log` and has no entry here — the
file existed as a one-line stub until this release. Neither
`plugins/comment-review/.claude-plugin/plugin.json` nor `.claude-plugin/marketplace.json`
carries a `version` field, so a version number lives only here and an installed plugin
cannot report which one it is.

## [Unreleased]

**Settling the system's own vocabulary.** A twelve-agent collection over the live tree found
nine terms used with a fixed sense and stated nowhere, and fifteen more carrying two or three
senses each. Each is being ruled on in turn — state the meaning, split the word, or delete the
use — and the ones that change a published name land here. Terms are settled in order of what
POINTS at them: names living in identifiers, filenames and flags first, because those are the
ones that can dangle. Survey: `docs/vocabulary-usage.md`.

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

### Added

- **Seven terms that were used with a fixed sense and stated nowhere now have one stating
  site, or are gone.** `prose tree` and `node` at `SKILL.md:76`, `the join` at `:526`,
  `detector` in `reviewer-brief.md`, `banner` in `comment-review-module-context.md`.
  **Deleted rather than defined:** `assessability gate` (used once, in frontmatter, and the
  idea was already stated without it) and `acquittal rate` (a measured quantity no site gave a
  denominator for — both uses now name the population instead). No new sections: each
  statement went into a sentence that already described the thing without naming it, so the
  four agent files are unchanged at 101/101/129/120 lines.

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
