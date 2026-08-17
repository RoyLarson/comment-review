---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles -- currency,
  functionality, locality, module coherence -- after a mechanical sweep that enumerates EVERY prose
  block, returning each block a verdict (drop / move / compact / correct / keep) or a named
  acquittal for the human to rule on. Use this whenever comments or documentation are the subject:
  after a task that added or edited commentary, when a file's comments have drifted from what the
  code now does, when someone says a comment is too long or out of date or "isn't this history",
  when reviewing a diff for its prose rather than its logic, before a docs or comment burn-down, or
  when asked whether a module still reads as one module. Trigger on phrasings that never say
  "comment review" -- "these comments are getting out of hand", "does this docstring still match",
  "is this comment still true", "clean up the narration in this file", "why does this file need so
  much explaining" all mean run this. It is NOT /simplify (code structure, and it applies its
  fixes) and NOT /code-review (correctness bugs) -- this one ONLY EVER PROPOSES and never edits
  anything, not code and not even the comments it rules on, because an edit applied is a verdict
  the human never got to rule on. Run it even when asked to cut ("cap these", "clean this up"): the
  deliverable is still the verdict list, applying is a separate step, and code concerns get raised
  in a line and left.
---

# comment-review

`/comment-review [cap] [target]` -> sweep -> 4 reviewers -> a verdict or acquittal per block -> you rule.

## The three rules that set this skill's yield

**1. The unit of work is the BLOCK LIST, not the file.** Phase 0 enumerates and numbers every
comment run and every docstring in scope; each reviewer walks that list start to finish. A block
nobody mentioned is a **gap in the review**, not one that passed. A reviewer told to "find the
comments that need attention" returns its most confident dozen and stops.

**2. You do not get to acquit by SILENCE.** An acquittal is a written verdict naming a reason from
the closed list below -- one line, cheap enough to afford total coverage, dear enough to force a
decision rather than a shrug.

**3. And you do not get to acquit by REPORTING EVERYTHING EITHER.** Rules 1 and 2 have a failure
mode and it is the measured one. ! **Sixteen runs of this skill over one six-file slice: raising
the report from 261 blocks to 364 added 103 findings and 2 real defects.** The runs that reported
most were not looking harder; they had stopped ranking. Two swept the SAME 419 blocks with the SAME
acquittal list -- one acquitted 47%, the other 14%, and the first was the better review by every
measure. **The acquittal RATE is the skill; the acquittal LIST is vocabulary.** So: **a finding is
a choice against another finding.** Before adding one, name what it displaces or what it is worth.
Concretely, once the mechanical tier below is spent, **flag between a half and two-thirds of the
census** -- past that you are not more thorough, you are undiscriminating, and the human stops
reading the list, which costs you every real defect on it.

### The acquittal list -- the ONLY reasons to pass a block over

Closed list. If none applies, the block gets a finding.

- **`label`** -- a one- or two-line comment naming the line it sits on and claiming nothing else
  (`# Kalman gain`, `# 0 disables the backoff`), a trailing field comment included.
- **`states-the-signature`** -- a one- or two-line docstring, present tense, matching the name, the
  arguments and the return, citing nothing outside itself. Three lines or more is no longer this:
  it is carrying something, and what it carries is what you are here to read.
- **`derivation`** -- a hand-worked calculation whose digits stop an assertion being an echo of the
  implementation, and the *first* thing a careless cap deletes. Over cap it is a `move` **into the
  docstring** -- which sits at a boundary and has no cap -- never a `compact`.
- **`only-guard`** -- a warning against a plausible wrong move where **nothing goes red** if someone
  makes it. Verify that; if a test does fail it is a time-saver, not a guard, and it is `compact`.
  There is no third category of "warnings".
- **`names-its-expiry`** -- prose stating the condition under which it stops being wanted.
- **`scopes-the-claim`** -- the discriminator or premise without which a reader over-reads the block
  above it, and **why an odd constant or fixture element is shaped that way**, on the element.
- **`intact`** -- true, current, on-subject, local, inside the cap, every name and path resolving. !
  Earned by checking, not by reading; but a block that survives the check has nothing for the
  applying pass to do to it, and proposing a rewrite of it is pure cost.

Nothing is acquitted for being short, true, well written, new, or sitting under a `!`.

## Spend the budget where the answers are -- tier the census first

Not every block costs the same to rule on, and treating them alike is what makes a reviewer run out
of attention two-thirds down the list.

- **Tier A, condemned by rule** -- a `#` run over the published cap; a docstring carrying a date, a
  ruling, a quotation, a "considered and rejected" or a rationale paragraph; a name, path or test
  that resolves nowhere. Report it and move on: **no argument required, no budget spent, no cap on
  the tier.** These are also the most numerous class in most trees.
- **Tier B, the judgement tier** -- everything with a claim in it: counts, coverage claims,
  superlatives, descriptions of behaviour, every block inside the cap. The review is won or lost
  here, so this is where all of rule 3's budget goes. **Tier C** is the acquittal list -- a line each.

! **A docstring is governed by FORMAT and a `#` run by LENGTH, so the same prose gets opposite
verdicts by container.** A docstring carrying a date or a rationale paragraph is Tier A at *any*
length -- but that is a rule about what a docstring may CARRY, and it does not reach one that merely
states what the function does. ! And a Tier A hit **does not travel**: a run one line over cap is by
construction mostly correct (on one measured tail, 27 of 48 runs were over by exactly one). Cut the
single least checkable line; **do not re-author a block already true, current and on-subject.**

## The subject is the prose, not the program

You will notice code problems -- say so, one line each, in a separate section, and move on. **Raise a
concern, do not open an investigation**, and never give a code finding a verdict. *The comment names
a symbol that no longer exists* is yours; *the symbol should be restored* is not. ! **A reviewer
straying into correctness is this skill's worst measured output.** Twice a reviewer read a modern
multi-exception `except` clause and reported the file "cannot compile", volunteered while reviewing
prose; once four agreeing reviewers shipped it. If your claim is about whether the code *runs*, it
is not your finding; making it anyway costs you an `ast.parse` first.

**Arguments.** `cap` -- optional integer, the most lines one `#` block may run. **This skill has no
cap of its own and must not invent one**; a cap published in a lint config or a hygiene test is the
number, and read how it *counts* too -- free markers, blank lines, continuation lines. With no cap
anywhere, judge and **report the longest run found**. `target` -- a path, defaulting to the diff.

## Phase 0 -- enumerate, mechanically

Scope is **whole files, not the diff**. Take the file list from
`git diff --name-only $(git merge-base HEAD @{upstream} || git merge-base HEAD main)..HEAD`, adding
`git diff --name-only HEAD` when the tree is dirty or the range is empty. ! **Use `merge-base`,
never `A...B` between two tips.** Comment debt is cumulative and mostly pre-existing: the long
block that has sat above a four-line expression for months is the finding worth having, and a
diff-scoped reviewer never sees it. Run this and **paste its output into every reviewer prompt**:

```bash
python .claude/skills/comment-review/sweep.py --cap 6 --width 100 <files>
```

Stdlib only, read-only, always exits 0, assumes nothing about the repo, survives a missing path or
an unparseable file. Per block it prints `path:start-end kind NL tags` -- a comment RUN bounded by
**code, not blank lines** (else 9 lines pass as 6 + blank + 3), a docstring from the AST, and tags
for over-cap, over-width, `docstring:NL`, dated, history, coverage-claim, counted, cites-a-path,
negated, rationale, quotation, names-a-symbol.

Then resolve what it only located: every `cites-a-path` against the tree, every `names-a-symbol`
against the names the code defines. Four things measurement settled -- do not "fix" them back. Build
the corpus from the **AST, never raw text** (text-built, it contains the comments being checked).
**Exclude `.md`/`.txt`** -- a doc discussing a deleted symbol vouches for it, suppressing three real
obituaries on one slice. **Never harvest string constants from tests** -- a negative assertion
(`assert "x" not in y`) makes a dead name read as alive. The **head** segment of a dotted name must
resolve, not any segment, and a **virtualenv poisons the corpus** (skip any dir with `pyvenv.cfg`).

! **The resolver's own false positives are known; do not report them.** A package-relative path
that resolves from the repo root, gitignored derived data, a mirror doc absent only because you are
in a worktree, a dotfile-rooted path, and a test cited by module stem are all noise -- and so is a
backticked name that does not exist **because that is the sentence's point**: a counterfactual, a
misspelling used as an example, a rejected alternative. Those three moves produce good comments. !
**A resolved citation is not a verified one** -- it asserts something *about* its target, so open
the target and read it, or mark the finding `SUSPECTED`. And nothing the sweep emits is a verdict:
a block with no tag can still be the worst prose in the file.

## Phase 1 -- four reviewers, each over the WHOLE list

Launch four subagents **in one message**. Give each the file list, the sweep output, the `cap`, the
acquittal list, the tiers, and one angle. **Tell each, in words, to return a line for every numbered
block**, and to rank its findings so the weakest can be cut. Every finding carries `file:line`, the
exact claim, the code or test line that settles it, and **`CONFIRMED` (both sides read) or
`SUSPECTED` (not)**. ! **Reviewers are READ-ONLY; say so explicitly**, and **name two lists: the
files UNDER REVIEW, which a proposal may target, and files given only as REFERENCE, which it never
may.** A reviewer that fixes what it finds has destroyed the finding, and one handed a contract
document as reference returned three edits *to the contract*, which were applied. Overlap between
angles is signal: a finding all four report is almost always real.

### Currency -- does this describe the program as it is now? (~45% of yield)

The largest angle by a distance. Git holds what the code used to be; a comment narrating its own
history is doing git's job badly. Flag dated rulings, review-round labels ("fix round 2", "finding
B4", "Part B"), "this used to...", "before the fix", "no longer" -- and the sharpest form,
**obituaries**: a name, file, test or flag that no longer exists anywhere. A reader greps, finds
nothing, and reads it as *their* mistake.

! **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar`
is written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Measured on a real deletion, the
identifier grep found ten mentions, all correctly dated tombstones, and **missed an eleventh
written with a hyphen -- the only present-tense claim in the set.** A clean grep reads clean.

**Every number is a citation.** A count is unverifiable unless it names the **population it counts
over**, so re-derive the SET before the number: "the 37 mobility ids" (35), "left all 1626 other
tests green" (3041). A pass correcting a false count produced a differently-false one, off by 5x,
because it re-counted the wrong population. ! **A count spelled "the one X" carries no digit** and
is invisible to every locator.

### Functionality -- does the commentary match what the code does? (~30%)

Read name, signature and docstring, then **read the body** -- the flagship false claims are
contradicted two or three lines below themselves. Flag a return shape the code no longer returns, a
`Returns:` whose key and value are the wrong way round, an `Args:` entry for a parameter that does
not exist or that guards the wrong object, a documented exception nothing raises, a raise nothing
documents, a summary line summarising the first four lines of a five-job function. The **summary
line** drifts silently: changing a return type does not change the sentence describing it.

! **Prose that DESCRIBES behaviour is wrong far more often than prose that PROHIBITS something.**
A description disagreeing with the code -> the comment is wrong. A prohibition disagreeing -> the
code broke the rule -> file it; the code moves, not the prose. ! **"Every X does Y" is a CHECKLIST:
enumerate the Xs before ruling.** The reviewer that got a universal right enumerated its subjects;
the one that got the next universal wrong edited the sentence. A guarantee true of five of seven
subjects passes every angle in this file unless someone counts.

**Reachability lives here, not in a fifth angle.** Claims about coverage are the class that
*licenses deletions* and are disproportionately wrong: "pinned by X", "guarded by Y", "the only
call site", "nothing asserts this" each authorise the next person to delete something. ! **The
dangerous cell is a claimed guard that does not exist** -- a deletion justified by coverage nobody
can find, which reads as safe for exactly that reason. Its opposite, a real constraint nothing
states, is a finding too, just a cheaper one.
Per claim: does the annotated constant have a reader? does the documented function have a caller
outside the tests? is the hazard still triggerable? For data reached by key, grep the STRING. It
fails both ways -- a real guard was deleted on a pointer to a test that never existed, and a comment
calling a live config value "decorative" nearly licensed deleting what three sites read. ! **An
unreachable hazard is not automatically a `drop`**: a precaution's value is having no trigger.
**Then read the body's comments as one sequence** -- individually each may be true; end to end they
are the most honest description of the function. The tell is grammatical: a comment that
**sequences** ("now I need to...", "then we...") instead of **constrains**. Report the mismatch and
name the fork -- the docstring grows until the *name* is wrong, or the function shrinks.

### Locality -- does this comment belong to the line it sits on?

A comment points DOWN for a block on its own lines, AT the declaration for a trailing one. The
finding is a comment about something **else**: a rule at the top of a class that really constrains
two literals two hundred lines down; a block whose later half turns back to narrate what came
before; a run sitting *after* an unconditional `return`, or between two statements annotating
neither; a trailing comment whose sentence continues into the comment-only lines beneath it, which
the next edit will truncate mid-clause. The test for anything that survives: **if this code changed,
would the comment become wrong -- and would anyone notice?** **Refactoring drift** is the biggest
yield here -- commentary either moves with its code, stays behind describing what left, or follows
and stops being true.

### Module coherence -- do the comments say this is one module?

Read only the module docstring, the section banners, and the top-of-file prose. Flag prose
announcing two or three subjects, banners reading like chapter breaks rather than parts of one
argument, a docstring that must enumerate unrelated responsibilities to be accurate, one describing
a fraction of its module, and any section named for the **occasion** that produced it. Also flag
**the same rule explained in several places** -- no function owns it, so each site performing part
of it re-explains the whole; check every copy, because the owner stays right while the copy rots. A
long comment above a short expression is usually this: a code-shape finding, comment as evidence.

## Phase 2 -- one verdict per block

Dedup blocks reported by more than one angle, then rule. **Before proposing a change, read the prose
immediately around it** -- a deliberate design usually says so directly above itself. Do not let a
neighbour stop you *reporting* what you saw; do let it stop you *changing* it. Then two questions.
**Is it CHECKABLE** from the code as it stands, without archaeology? **Is it NECESSARY** -- would
someone changing this code make a *worse decision* without it? Not "is it interesting".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader needs | **drop** -- the code says it |
| **not checkable** | **move** -- rationale, unverifiable here | **drop** -- history |

! **Truth is not one of the questions, and that is the point.** History that is *correct* reads as
earning its place and does not; accuracy is the reason it was never deleted, not a reason to keep
it. The exception is arithmetic -- a claim that is pure arithmetic over committed values is
checkable without judgement, so recompute it rather than rule on it.

**A fifth verdict: `correct`.** A block that is on-subject, local and load-bearing but says
something *false* is neither `keep` nor `drop` -- it is a fix, and it needs its replacement text
written out. `compact` is likewise not a category of its own: it is what you do to a `keep`, or to
the remainder a `move` leaves. ! **Neither is a place to file a block you could not rule on.**

**Rule on SENTENCES, not on blocks.** A container of six sentences can hold six verdicts, and the
common shape is a live constraint beside the story of where it came from. ! **A single `keep`
sentence launders every sentence around it** -- if you are ruling `keep` because *part* of the block
is load-bearing, descend a level. But descending is about **precision, not volume**: it splits one
verdict into two, it does not turn one acquittal into six findings.

For a **move**, name the destination and send the **WHOLE block, including the half that stays** --
a doc holding only what was discarded reads as a deletion list, and the destination is usually
unguarded, so what lands there is checked by nothing ever again. ! **Account for every digit you
propose deleting**: the most repeated defect a compaction pass introduces is **a measurement
replaced by an adjective**, and it always looks like a legitimate trim. ! **A description written
as a negation is a FORM defect on its own** -- rewrite it positive; a *prohibition* may stay
negative, no positive form keeps its force.

### Calibration -- report the rate, not just the list

State it in the report and check it against yourself: **N swept, M findings, K acquitted by reason.**
The two failure modes do not look alike. A tidy short list looks like restraint: in one measured
slice **half the prose blocks in six files** were rewritten by the next pass, so a ten-finding report
on a file of that shape is a miss. A long list looks like rigour and is the more common failure --
see rule 3. If your acquittal rate is under a third you have stopped reading and started matching
patterns; ask each flagged block what a reader would DO with it. ! **"This tree looks fine" from a
reviewer who has only read guarded code is not evidence**: a tree entering a guard's scope for the
first time held 11 dangling citations against 0 in the guarded one -- same repo, same period.

## Phase 3 -- present. Always.

**This skill never edits. It ends with the verdict list.** Report grouped by verdict, most
consequential first, the replacement text inline for every `compact` and every `correct`, then the
coverage line. Then stop. ! **Even when the human names the edit** -- "cap them", "go do it" -- the
deliverable is the report: *"Report only, per the skill -- say the word and I'll apply the verdicts
you accept."* An imperative is not authorization, and **an edit applied is a verdict never ruled
on.** Measured: two runs on near-identical prompts split, one report, one 846-line diff.

## Rails for the pass that applies these -- you are not it, and it runs without this file loaded

- **A block is bounded by CODE, not blank lines** -- else 9 lines become 6 + blank + 3.
- **Never change a line of code, a docstring's meaning, or a string literal**; prove it by diffing
  every non-comment line, which caught two cuts that ran one line too far into real code.
- **Extract before you cut** on a `move` -- the other order lost the text three times.
- **`count == 1` or refuse the whole file**, with the `old` text built programmatically rather than
  transcribed from `Read` output, its width checked as well as its line count, and the file's own
  line ending preserved, or a 3-line prose edit lands as a whole-file diff.
- **Re-read what you wrote**, sweeping your own replacements. A pass that cut seven obituaries
  wrote seven new ones, and wrote over-length blocks while removing over-length blocks.

**Every example above is invented or anonymised. Keep it that way** -- quoting a real comment teaches
a reviewer to recognise *that comment* instead of the shape, and it rots into an obituary of its own
the day someone acts on the finding.
