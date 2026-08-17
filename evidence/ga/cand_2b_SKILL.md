---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles -- currency,
  functionality, locality, module coherence -- after a mechanical census of every prose block, and
  return each block either a finding with a proposed verdict (drop / move / compact / correct /
  keep) or a named acquittal, for the human to rule on. Use this whenever comments or documentation
  are the subject: after finishing a task that added or edited commentary, when a file's comments
  have drifted from what the code now does, when someone says a comment is too long or out of date
  or "isn't this history", when reviewing a diff for its prose rather than its logic, before a docs
  or comment burn-down, or when asked whether a module still reads as one module. Trigger on
  phrasings that never say "comment review" -- "these comments are getting out of hand", "does this
  docstring still match", "is this comment still true", "clean up the narration in this file", "why
  does this file need so much explaining" all mean run this. It is NOT /simplify (which reviews code
  structure and applies its fixes) and NOT /code-review (which hunts correctness bugs) -- this one
  ONLY EVER PROPOSES and never edits anything, not code and not even the comments it rules on,
  because an edit applied is a verdict the human never got to rule on. Run it even when the request
  sounds like an instruction to cut ("cap these", "clean this up"): the deliverable is still the
  verdict list. Judging whether the code works is not a reviewer's job -- code concerns get one line.
---

# comment-review
`/comment-review [cap] [target]` -> census every block -> 4 reviewers in parallel -> **every block gets
a verdict or a named acquittal** -> you rule -> someone else applies.

## The two mechanisms, and why both
**Census** guarantees every block is SEEN; **acquittal** guarantees every block is RULED ON. A pass
that visits only what a scanner flagged inherits the scanner's blind spots; a pass that reports only
what it disliked leaves the reader unable to tell *clean* from *not looked at*. Silence is a gap in
the review, not a pass. ! **The two errors do not cost the same**: a block reported and then kept
costs one glance, a block never surfaced costs the whole class it belonged to and nothing says so.
When unsure, **report it** -- the closed acquittal list below is short on purpose, and an acquittal
not on it is a finding.

## The subject is the prose, not the program
**Every verdict is a verdict on a comment.** Note code problems in a separate section, one line each
-- **raise a concern, do not open an investigation** -- and never give one a prose verdict. *"The
comment says this reads one field and it reads three"* is yours; *"it should not read three"* is
`/simplify`'s. ! Straying into correctness is where this skill's worst output comes from, measured:
twice a reviewer reported a file "cannot compile" over syntax the target Python permits, and once
four agreeing reviewers shipped it. If the claim is about whether the code RUNS it is not yours.
! **THE GOVERNING LAW, measured across a whole burn-down: every false statement found was one that
NOTHING asserted.** Not the oldest, not the longest, not the furthest from its code -- false clauses
sat inside blocks whose other sentences were true, same voice, under the same warning mark; one
split at a comma, the asserted half true and the unasserted half false. **Search where no test, no
type and no assertion reaches**: prose beside a passing test, a number nothing recomputes, a claim
about callers, a docstring on a function only tests call.

## Arguments and scope
**`cap`** -- optional integer, the most lines one `#` run may occupy; pass it to the census and to
every reviewer. **This skill has no cap of its own and must not invent one.** If the repo publishes
one in a guard, that guard owns it -- read *how it measures*, not just its number, and quote it
rather than recalling it. With no cap anywhere, judge, and **report the longest run found**.
**`target`** -- optional path, defaulting to the changed files.
```bash
B=$(git merge-base origin/HEAD HEAD 2>/dev/null || git merge-base master HEAD 2>/dev/null \
    || git rev-parse HEAD~1 2>/dev/null)
git diff --name-only "$B" HEAD 2>/dev/null; git diff --name-only HEAD 2>/dev/null
```
! Use a **merge-base**, never `A...B` between two branch tips: a tip that has moved reports the
other branch's additions as your deletions -- measured once at 933 phantom lines. If every ref fails,
review the paths given and say the scope was manual. Then review **every comment and docstring in
those files, not just the changed lines** -- comment debt is cumulative and mostly pre-existing, and
the diff says which files are in the human's head, not what to read inside them. **Widen from a file
to a claim**: if a finding is about a symbol, a path, a number or a rule, every file naming it is in
scope for THAT finding -- `grep` decides, not the diff.

## Phase 0 -- the census
```bash
python .claude/skills/comment-review/prose_census.py $FILES --root . --cap "$CAP"
```
`prose_census.py` ships beside this file: read-only, always exits 0, needs no project layout. For
**every** block it prints `file:line`, `kind` (comment | docstring), line count, and flags:
`over-cap`, `history`, `date`, `quote`, `count`, `coverage`, `universal`, `sequencing`, `negation`,
`rationale`, `direction`, `dead-path?`, `dead-test?`, `dead-name?`. Four choices each cost a
measured miss -- keep them if you reimplement it:

- **a block is bounded by CODE, not by blank lines**, or a 9-line run reads as 6 + blank + 3, and
  **docstrings come from the AST**, comment runs from `tokenize` -- a regex finds neither reliably;
- **lines are JOINED before matching**: prose wraps, and a per-line regex cannot see a citation or a
  count that crosses a line break;
- **the name index is built from the AST of non-test source only** -- a test pinning a deleted field
  with `assert "x" not in y` makes the strongest evidence a name is dead read as proof it is alive --
  and any directory holding `pyvenv.cfg` is skipped, or the result depends on what is installed;
- **the HEAD segment of a dotted name must resolve**, not any segment: matching any part lets
  `DeadClass.meta` pass on `meta`, which is exactly where a dead name hides.
! **Every line it prints is a CANDIDATE, and nothing it prints is a verdict.** A run that labelled
its output "facts a reviewer need not re-derive" measured 95-100% false positives on dangling paths,
and a reviewer acting on it deleted a live coverage citation. Equally, **a block with no flags can
be the worst prose in the file** -- flags are reasons to look first, not the population to look at.

## Phase 1 -- four reviewers, in parallel
Launch **four subagents in one message**, each with the file list, the `cap`, any published repo
prose rules, **the census rows for its files**, and one angle. ! **Reviewers are READ-ONLY -- say so
in the prompt**, and name the writable targets and the read-only reference files separately: four
agents editing one file is a race whose loser's edits vanish, a reviewer that fixes what it finds
has destroyed the finding, and one handed a contract document as *reference* returned three edits to
it, landing a false claim in the doc whose purpose was removing false claims.
Each finding returns `file`, `line`, the exact claim quoted, **the exact code, grep result or
arithmetic that settles it**, and `CONFIRMED` (both sides read) or `SUSPECTED` (not). Measured: 196
of 202 came back CONFIRMED once this was asked for. Overlap between angles is signal -- a finding all
four report is almost always real. Three habits every angle needs:

- **Resolving a citation is not verifying it.** A path or constant that EXISTS does not check what
  the prose SAYS about it. Open the target, or mark it SUSPECTED.
- **Re-derive; do not re-read.** Redo the sum, count the set, list the callers. One stale arithmetic
  and its own correction both rounded to the same answer, so nothing objected for a year.
- **Read the prose around a block before proposing a REMEDY** -- not before reporting it, since the
  deliberate-design note can itself be the false one. A function reported for mixing units did so
  deliberately per the line above it, and the remedy would have reopened a settled call.

### Currency -- does this describe the program as it is now? (~45% of findings)
Git holds what the code used to be; a comment narrating its own history does git's job badly. Flag
dates, review-round labels ("fix round 2", "finding C3", "Part B"), quotations, attributed rulings,
"this used to...", "X was changed to Y", "retired", "no longer" -- and the sharpest form, **obituaries**:
prose naming a symbol, file, test, flag or config key that no longer exists. The reader greps, finds
nothing, and reads it as *their* mistake.

- ! **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar`
  is written `foo-bar`, `foo bar`, `FooBar`, "the barrer". Measured on one deletion, the identifier
  grep found ten mentions, all correctly dated tombstones, and **missed an eleventh written with a
  hyphen -- the only present-tense claim in the set.** A clean grep reads as a clean file.
- ! **A dead name is not always an obituary.** Where the dead thing is the SUBJECT -- "the X column
  was removed, do not re-add it" -- the line is the only surviving reason. Ask: does it send a reader
  looking, or tell them not to go? A name backticked *because* it does not exist is the same case.
- **Every number is a citation.** "the 37 ids", "eight callers", "all 1626 other tests".
  **Re-derive the POPULATION first, then the count** -- most are wrong at the set, not the number,
  and one correction of a false number produced a differently false one, direction right and
  magnitude out by 5x. A number nothing recomputes will rot again: usually **delete the number**.
  And **a label of provenance** -- "measured", "authored", "shipped" -- is a claim about a decision,
  which no code can settle: check the record or mark it SUSPECTED.

### Functionality -- does the commentary match what the thing is for? (~30%)
Read name, signature, docstring, then body. Flag a `Returns:` shape the code no longer returns, a
mapping documented backwards, an `Args:` entry for a vanished parameter, a documented exception
nothing raises, a summary describing only the first four lines. The **summary line** drifts
silently, because changing a return type does not change the sentence describing it.

1. **Is it a COVERAGE claim?** "pinned by X", "guarded by Y", "the only call site", "nothing reads
   this". This class **licenses deletions** and is disproportionately wrong, so it is never read --
   it is checked, for what it ASSERTS. A real guard has been deleted on a pointer to a test nobody
   wrote, and a live config value was called decorative one edit before five call sites read it.
   ! Check the cited guard CAN fail: one exercised where an earlier gate returns first passes
   whether it exists, is broken, or is deleted. A citation a checker cannot parse (a brace
   expansion, a bare `test_thing`, a line number) is worse than a parseable wrong one: it never
   gets fixed, and its terseness reads as authority.
2. **Is it a UNIVERSAL?** "every X", "always", "never", "all N". A universal is a CHECKLIST --
   enumerate the Xs. The largest hole measured was a module-level "LOUD, NEVER SILENT" false for two
   of seven paths; every angle passed it, because each individual path made it look true.
3. **Is it a DESCRIPTION or a PROHIBITION?** ! **Prose that DESCRIBES behaviour is wrong far more
   often than prose that PROHIBITS.** A description disagreeing with the code means the comment is
   wrong -> `correct` or `drop`; a prohibition disagreeing means the CODE broke the rule -> file it,
   leave the prose alone. And a description written as a NEGATION is a form defect by itself: you
   cannot check "X is not the case" without establishing what the code does and arguing backwards.
   Rewrite it positive. A prohibition may stay negative; no positive form keeps its force.
4. **Does the running commentary describe one job, or five?** Read the body's `#` comments in order,
   end to end: individually true, together they are the most honest description of the function in
   the file. The tell is grammatical -- **a comment that SEQUENCES instead of CONSTRAINS** ("now I
   need to...", "then we..."). Say which each step is: **(A)** not needed for the function to be the
   function, or **(B)** real work at the wrong level. ! **Report the fork, do not resolve it** --
   either the docstring grows until the NAME is wrong, or the function shrinks to what it is called.
   ! Prefer a claim about the value produced over one about what was meant: narration of INTENT
   hides a mismatch that narration of EFFECT would expose, because it reads as confirmation.
5. **Reachability lives here, not in a fifth angle**: a docstring on a function nothing calls
   describes behaviour nobody can observe -- a finding, with the caller list as evidence.

### Locality -- does this comment belong to the line it sits on?
A block points DOWN at the code under it; a trailing comment points AT its own line, and
`retries: int  # 0 disables the backoff` is exactly where it belongs -- never report one as misplaced
merely for following a statement. The finding is a comment about something **else**: a rule at the
top of a class that constrains two literals 200 lines down, a block whose later half turns back to
narrate what came before, a block annotating **nothing** between two definitions. Second test: **if
this code changed, would the comment become wrong -- and would anyone notice?** Prose that would
quietly survive a change to the code it describes is not local to it.

! Flag navigation by direction ("the constant above", "the rule below") -- true today, rotten at the
next reorder; the fix is to DELETE the direction word, not correct it, or it is re-armed rather than
fixed. ! Flag a **severed continuation**: a trailing comment whose sentence ran on to a line since
rewritten now ends mid-clause, and nothing goes red -- not the formatter, not the type checker, not a
cap. **Refactoring drift** is this angle's biggest yield: when code moves, its commentary either
moves with it, stays behind describing what left, or follows and stops being true. Flag the inverse
too -- a line carrying a non-obvious constraint with **no** comment, where getting it wrong is
silent. ! **The keep this angle must protect: a comment whose whole function is WHERE IT IS.** A
warning aimed at the next author, at the point of temptation, is load-bearing *because* it
interrupts; moving it to a doc satisfies every other rule and destroys it. Compact, never relocate.

### Module coherence -- do the comments say this is one module?
Read the module docstring, the section banners and the top-of-file commentary, and ask whether they
describe one thing. Flag prose announcing two or three subjects, banners reading like chapter breaks
rather than parts of one argument, a docstring enumerating unrelated responsibilities to stay
accurate or describing a fraction of its module, and a section named for the OCCASION that produced
it -- nobody can apply "it was in that batch" as a membership rule. Two more, and **give this angle
the whole file, not a block**; its yield collapses when starved. **Does the file contradict its own
headline?** "Single source of truth for X" twenty-five lines above a note explaining that X
deliberately lives elsewhere -- read the headline LAST, against everything under it, because an
overclaim is written first, when the file is small, and never revisited. **Is the same rule
explained in several modules?** Then no function owns it and every site re-explains the whole:
**the structural cause of long comments**, a code-shape finding with the comment as evidence.

## Phase 2 -- one ruling per block
Dedup findings on the same block, then rule on **every block in the census**, including the ones
nobody flagged. Two questions. **CHECKABLE?** -- could a reader confirm or refute it from the code as
it stands, without archaeology? **NECESSARY?** -- would someone changing this code make a **worse
decision** without it? Not "is it interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader verifies | **drop** -- it narrates the code |
| **not checkable** | **move** -- real rationale, unverifiable here | **drop** -- history |

! **Accuracy is not one of the questions.** *"Moved here from `x.validate` when that module was
deleted"* is true; the reader needs the check to live HERE, not its travel history. History that is
*correct* reads as earning its place, and that is why it was never deleted.

**Five verdicts.** `drop`, `move`, `compact`, `keep` -- and **`correct`**, for a block on-subject and
load-bearing that says something false: the answer is neither dropping nor shortening it, it is the
true sentence plus the evidence that settles it. A real pass did this **82 times** under a
four-verdict vocabulary and had to file every one as something else.

**Rule on sentences, not on blocks.** A container of six sentences holds six verdicts, and the
common shape is a live constraint beside the story of where it came from. ! **A single `keep`
sentence launders every sentence around it** -- ruling `keep` because *part* of a block is
load-bearing is the signal to descend a level, and since a block's most defensible sentence is
usually why the whole block survived, that is the default outcome, not a rare one. **Then: is what
survives longer than it needs to be?** If so, **compact** -- same content, fewer words, replacement
proposed. For **move**, name the destination, and ! **it gets the WHOLE block, including the half
that stays in the code**: a doc holding only the discarded half is a deletion list, not a record.

### The closed acquittal list -- the only reasons a block gets no finding
Name one of these, by name, or report the block:

- **`label`** -- a mechanical or navigational marker carrying no claim: a shebang, a pragma, a
  section banner, a `TODO`/`FIXME`/`HACK`/`XXX`/`BUG` pointer at filed work.
- **`states-the-signature`** -- a field or parameter annotation that says what the declaration beside
  it means and nothing more, and would go visibly wrong if that declaration changed.
- **`derivation`** -- a hand-worked calculation: what stops an assertion being an echo of the
  implementation, and the first thing a careless cap deletes. * Move one into the DOCSTRING rather
  than compacting it -- a `#` run is capped because it interrupts code, a docstring sits at a edge.
- **`only-guard`** -- a warning against a plausible wrong move where **nothing goes red**. ! Where a
  test *does* catch the move it is a time-saver, not a guard, and it is `compact`. There is no third
  category of "warnings"; calling one is the laundering failure above.
- **`names-its-expiry`** -- it states the condition under which it stops being true.

! **A block one line over cap is, by construction, mostly correct**: cut the single least-checkable
line, and do NOT re-author prose already true, current and on-subject. Of the last 48 over-cap runs
in one burn-down, 27 were over by exactly one. ! **Changing one copy of a paired value is the
commonest defect a prose pass CREATES**, because a pass edits where it is reading: before proposing
a number `git grep` it, before proposing a name grep it -- the second copy never enters your diff.

## Comments and docstrings are governed differently
**A `#` comment is governed by LENGTH** -- it interrupts code, so its cost is the screen space
between the line above and the line below, and a run is bounded by CODE, not by blank lines.
**A docstring is governed by FORMAT, not length**: a summary line, then `Args:`/`Returns:`/`Raises:`
only where they say something the signature does not -- so never propose `compact` on a docstring
merely for running long, and if the repo states a style, it wins. ! **But "uncapped" is not
"anything goes", and this is where a burn-down silently undoes itself**: prose evicted from a `#`
run relocates into a docstring and nothing notices. A docstring body carrying **a date, a quotation,
an attributed ruling, a review-round label, a "considered and rejected", a rationale paragraph, a
measurement story, or a claim about callers or coverage is a finding at ANY length** -- a FORMAT
failure, not a length one, and its verdict is `move`. Two shapes no line counter sees: a **trailing**
comment running on into comment-only lines below it (lift the whole thing above the line), and **the
wrong half surviving** a shortening -- check what SURVIVED, not what went.

## Phase 3 -- present. Always.
**This skill never edits -- not the code, not the comments, at any phase.** Report grouped by
verdict, most consequential first, replacement text inline for every `compact` and `correct`, and
the census arithmetic -- *N blocks read, M findings, N-M acquitted, by reason* -- so a reader can tell
"clean" from "not looked at". Then stop.

! **Even when the human names the edit** -- "cap them", "fix these", "go do it" -- the deliverable is
the report: *"Report only, per the skill -- say the word and I'll apply the verdicts you accept."*
This review's value IS the human's disagreement with it, and **an edit applied is a verdict never
ruled on**. Measured before this rule, two runs on near-identical imperative prompts split, one
returning a report and the other an 846-line diff; neither human knew which was coming. ! And
**"this tree looks fine" from a reviewer who has only read guarded code is not evidence**: a tree
entering a guard's scope for the first time held 11 dangling citations against 0 in the guarded
tree -- same repo, same authors, same period. Defects concentrate where the checker cannot see.

## Rails for the pass that applies these
You are not that pass; hand these along, because it usually runs without this skill loaded.

- **Extract before you cut** on a `move` -- the other order loses the text on any interruption, and
  did, three times. **Build the `old` string programmatically and require `count == 1`**, or refuse
  the whole file: a near-miss must be a loud refusal, never an edit landing somewhere plausible.
- **Never change a line of code, a type annotation, a docstring's meaning, or a string literal -- and
  PROVE it**, with an AST diff against the pre-edit file, on the commit you *doubt*. Of four
  prose-only commits audited later, the one that skipped this had changed three string literals.
- **Re-read the result as prose, and re-check it against your own rules.** A pass that cut seven
  obituaries wrote seven new ones; the defect that survived three reviews was a severed sentence.

## What this is not, and a note for whoever edits it
`/simplify` reviews code structure and applies what it finds; `/code-review` hunts correctness bugs.
This one reviews prose and **only ever proposes** -- a defect noticed anyway gets **named and left**.
**Every example above is invented and every measurement anonymised. Keep it that way.** Quoting a
real comment teaches a reviewer to recognise *that comment* instead of the shape, and it rots: the
day someone acts on the finding, this file cites something gone -- a hygiene skill carrying its own
obituary. Anonymised measurements keep: *"an identifier grep found ten and missed the hyphenated
eleventh"* is the whole lesson.
