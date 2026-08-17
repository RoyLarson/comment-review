---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles -- currency,
  functionality, locality, module coherence -- by enumerating EVERY prose block in those files with a
  mechanical sweep and then having parallel subagents rule on each one, returning every finding with a
  proposed verdict (drop / move / compact / correct / keep) for the human to rule on. Use this whenever
  comments or documentation are the subject: after finishing a task that added or edited commentary,
  when a file's comments have drifted from what the code now does, when someone says a comment is too
  long or out of date or "isn't this history", when reviewing a diff specifically for its prose rather
  than its logic, before a docs or comment burn-down, or when asked to check whether a module still
  reads as one module. Trigger on phrasings that never say "comment review" -- "these comments are
  getting out of hand", "does this docstring still match", "is this comment still true", "clean up the
  narration in this file", "why does this file need so much explaining" all mean run this. It is NOT
  /simplify (which reviews code structure and applies its fixes) and NOT /code-review (which hunts
  correctness bugs) -- this one ONLY EVER PROPOSES and never edits anything, not code and not even the
  comments it rules on, because an edit applied is a verdict the human never got to rule on. Run it
  even when the request sounds like an instruction to cut ("cap these", "clean this up"): the
  deliverable is still the verdict list, applying is a separate step, and code concerns get raised in
  a line and left.
---

# comment-review

`/comment-review [cap] [target]` -> enumerate every block -> 4 reviewers walk the whole list -> a
verdict or a named acquittal per block -> you decide.

## The two rules that set this skill's yield

**1. The unit of work is the BLOCK LIST, not the file.** Phase 0 enumerates and numbers every comment
run and every docstring in scope, and each reviewer walks that list start to finish. A block nobody
mentioned is a **gap in the review**, not a block that passed; the report says how many were swept.
That is the difference between a review and a search -- a reviewer told to "find the comments that
need attention" returns its most confident dozen and stops. The measurement is blunt: **every false
statement found in a real burn-down was one no assertion touched**, and position predicted nothing.
False clauses sat *inside* blocks whose other sentences were true, same voice, same indent, under the
same glyph; one split mid-sentence, the clause before the comma asserted by the body and true, the
clause after asserted by nothing and false. So **"look where nothing asserts" beats "look for long
blocks"**, and only a census gets you there: a claim beside a passing test is decoration, and
decoration is what survives a change to what it describes.

**2. You do not get to acquit by SILENCE** -- the counterweight, and what stops a census degenerating
into "flag everything". An acquittal is a *written* verdict naming a reason from the closed list below:
one line, cheap enough to afford total coverage, dear enough to force a decision rather than a shrug.
If none of the five applies, the block gets a finding.

### The acquittal list -- the ONLY reasons to pass a block over

- **`label`** -- a one- or two-line comment naming the line it sits on: a unit, a shape, a step number,
  a section banner (`# Kalman gain`, `# 0 disables the backoff`). It claims nothing beyond that line
  and cites nothing outside itself. A trailing comment that *describes behaviour* is not a label.
- **`states-the-signature`** -- a one- or two-line docstring, present tense, matching the name, the
  arguments and the return, citing nothing outside itself. Three lines or more is no longer this: it
  is carrying something, and what it carries is what you are here to read.
- **`derivation`** -- a hand-worked calculation whose digits are what stop an assertion being an echo
  of the implementation, and the *first* thing a careless cap deletes. Over cap it is a `move` **into
  the docstring** -- which sits at a boundary and has no length cap -- never a `compact`.
- **`only-guard`** -- a warning against a plausible wrong move where **nothing goes red**. Verify that;
  if a test does fail it is a time-saver, not a guard, and it is `compact`.
- **`names-its-expiry`** -- prose stating the condition under which it stops being wanted.

Nothing is acquitted for being short, true, well written, new, or sitting under a `!`.

## The subject is the prose, not the program

**It is not a reviewer's job to decide whether the code works.** Every verdict you return is a verdict
on a comment. You will still notice code problems -- say so in a separate section, one line each.
**Raise a concern, do not open an investigation**, and never let a code finding acquire a verdict.
*The comment says the function reads one field; it reads three* is yours; *the function should not
read three* is not. ! **A reviewer straying into correctness is this skill's worst measured output.**
Twice, one read a modern multi-exception `except` clause and reported the file "cannot compile" --
wrong, and volunteered while reviewing prose; once four agreeing reviewers shipped it. Make such a
claim anyway and you owe it an `ast.parse` first.

**Arguments.** `cap` -- optional integer, the most lines one `#` block may run. **This skill has no cap
of its own and must not invent one**; a cap published in a lint config or a hygiene test is the number,
and read how that guard *counts*. With no cap, judge and **report the longest run found**. `target` --
optional path, defaulting to the files in the diff.

## Phase 0 -- enumerate, mechanically

Scope is **whole files, not the diff**. Get the file list with
`git diff --name-only $(git merge-base HEAD @{upstream} 2>/dev/null || echo HEAD~1) HEAD`, and add
`git diff --name-only HEAD` when the tree is dirty. ! **Use `merge-base`, never `A...B` between two
tips** -- the three-dot form between branch tips silently picks a different set. Every block inside
those files is in scope: comment debt is cumulative and mostly pre-existing, and the long block that
has sat above a four-line expression for months is the finding worth having, which a diff-scoped
reviewer never sees. Run `python .claude/skills/comment-review/sweep.py <files>`, then **paste its
output -- the numbered block list -- into every reviewer prompt.** It is stdlib-only, assumes nothing
about the repo, and exits 0 on a missing path or an unparseable file; per block it prints `file:a-b`,
kind, length, and tags: over-cap runs, docstrings over two lines, over-wide lines, dates, history and
review-round markers, coverage claims, absolutes, counts, cited paths, symbols, negations, quotations.

Then resolve what it only located: every `cites-a-path` against the tree, every `names-a-symbol`
against the names the code defines. Four things measurement settled about that corpus -- do not "fix"
them back. Build it from the **AST, never raw text** (text-built, it contains the very comments being
checked, so the check always passes). **Exclude `.md`/`.txt` and every test file**: a doc discussing a
deleted symbol vouches for it (measured -- three real obituaries suppressed), and a test pinning a
dead field with a negative assertion (`assert "x" not in y`) makes it read as alive. A **virtualenv in
the tree poisons the corpus** -- skip any directory holding `pyvenv.cfg`. And the **head** segment of a
dotted name must resolve, not any segment, or `Dead.meta` passes on `meta`.

! **Nothing the sweep emits is a verdict**, and a block with no tag can still be the worst prose in the
file -- which is why every block is walked, not just the tagged ones. ! And **a resolved citation is not
a verified one**: it asserts something *about* its target, so read the target or mark it `SUSPECTED`.

## Phase 1 -- four reviewers, each over the WHOLE list

Launch four subagents in one message. Give each the file list, the sweep output, the `cap`, the
acquittal list, and one angle. **Tell each, in words, to return one line for every numbered block** --
a finding or a named acquittal. Overlap between angles is signal, not waste: a finding all four report
is almost always real, and on one run a second angle caught an error the first had just introduced.
Every finding carries `file:line`, the exact claim, **the exact code or test line that settles it**,
and `CONFIRMED` (both sides read) or `SUSPECTED` (not). Measured: 196 of 202 came back CONFIRMED once
this was asked for, and one reviewer withdrew two candidates rather than pad.

! **Reviewers are READ-ONLY; say so explicitly**, and **name two lists: the files UNDER REVIEW, which
a proposal may target, and files given only as REFERENCE, which it never may.** Four agents editing one
file is a race whose loser's edits vanish; a reviewer that fixes what it finds has destroyed the
finding; and one handed a contract document as reference proposed three edits *to the contract*, which
were applied -- a false claim landing in a doc, from the pass whose purpose was removing them.

### Currency -- does this describe the program as it is now? (~45% of findings)

The largest angle by a distance. Git holds what the code used to be; a comment narrating its own
history does git's job badly. Flag dated rulings, review-round labels ("fix round 2", "finding B4",
"task 8.6", "(A6)", "v3"), "this used to...", "before the fix", "no longer" -- and the sharpest form,
**obituaries**: a name, file, test or flag that no longer exists anywhere, where a reader greps, finds
nothing, and reads it as *their* mistake.

! **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar` is
written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Measured on a real deletion, the identifier
grep found ten mentions, all correctly dated tombstones, and **missed an eleventh written with a
hyphen -- the only present-tense claim in the set**; a clean grep reads clean. **Every number is a
citation** too: a count is unverifiable unless it names the
**population it counts over**, so re-derive the SET before the number. Measured misses: "the 37
mobility ids" (35), "left all 1626 other tests green" (3041) -- and a pass correcting a false count
produced a differently-false one, off by 5x, because it re-counted the wrong population.

### Functionality -- does the commentary match what the code does? (~30%)

Read the name, the signature and the docstring, then **read the body** -- the flagship false claims are
contradicted two or three lines below themselves. Flag a return shape the code no longer returns, a
`Returns:` whose fields are in the wrong order, an `Args:` entry for a parameter that does not exist, a
documented exception nothing raises, a raise nothing documents, a summary saying "Yield" over a
function that returns. The **summary line** drifts silently -- changing a return type does not change
the sentence describing it.

! **Prose that DESCRIBES behaviour is wrong far more often than prose that PROHIBITS something, and
the two disagree differently** -- see the Phase 2 table. ! **Resolve superlatives and collective nouns
against their own file**: "single source of truth", "THE only entry point", "these constants", "the
table" -- a "one definition" naming a single member is a tautology, and an "only entry point" is
refuted 25 lines down often enough to check always.

**Reachability lives here, not in a fifth angle.** Claims about coverage are the class that *licenses
deletions* and are disproportionately wrong: "pinned by X", "guarded by Y", "the only call site",
"nothing asserts this" each authorise the next person to delete something, so **grep the cited name,
every time**. The dangerous cell is a claimed guard that does not exist -- a deletion justified by
coverage nobody can find, which reads as safe for exactly that reason; a real guard has been dropped
on a pointer to a test never written, and a comment calling a live config value decorative nearly
licensed deleting what five sites read. So per claim: does the constant it annotates have a reader?
Does the documented function have a caller outside the tests? Is the hazard still triggerable? For
data reached by key, **grep the STRING**. ! But **an unreachable hazard is not automatically a
`drop`** -- a precaution's value is having no trigger. ! **A citation your checker cannot parse is
worse than one it can parse and reject** (a brace expansion, a bare `test_thing`, a line-number
citation): the parseable wrong one gets fixed next run, the unparseable one accumulates and its
terseness reads as authority.

**Then read the body's comments as one sequence.** Individually each may be true; end to end they are
the most honest description of the function in the file. **The tell is grammatical -- a comment that
sequences instead of constrains** (*"now I need to...", "oh I should...", "then we..."*): it goes nowhere
when its line moves, because it was never about the line. Say which each step is -- **(A)** not needed
for the function to be the function, or **(B)** real work at the wrong level. ! **Report the mismatch;
do not resolve it** -- either the docstring grows until it tells the truth, at which point the *name*
is wrong, or the function shrinks to what it is called, and naming that fork is the deliverable.

### Locality -- does this comment belong to the line it sits on?

A comment points DOWN for a block on its own lines, AT the declaration for a trailing one. The finding
is a comment about something **else**: a rule stated at the top of a class that really constrains two
integer literals two hundred lines down; a block whose later half turns back to narrate what came
before; a run sitting *after* an unconditional `return`; a run between two statements annotating
neither; a trailing comment that runs on into comment-only lines beneath it (lift it above the line).
Second test: **if this code changed, would the comment become wrong -- and would anyone notice?** A
comment that would quietly survive a change to the code it describes is not local to it. Flag the
inverse too: a line carrying a non-obvious constraint with no comment, where getting it wrong is
silent. **Refactoring drift** is this angle's biggest yield -- when code moves, its commentary stays
behind describing what left, or follows and stops being true.

### Module coherence -- do the comments say this is one module?

Read only the module docstring, the section banners and the top-of-file commentary. Do they describe
*one* thing? Flag prose announcing two or three subjects, banners reading like chapter breaks rather
than parts of one argument, a docstring enumerating unrelated responsibilities to be accurate, one
describing a fraction of its module, and any section named for the **occasion** that produced it (a
review round, a task number) -- a membership rule no future author can apply. Also flag **the same rule
explained in several modules**: no function owns it, so every site performing part of it re-explains
the whole; where one claim appears in several files, check every copy, because the owner stays right
while the copy rots. A long comment above a short expression is usually this -- report it as a
code-shape finding with the comment as evidence.

## Phase 2 -- one verdict per block

Dedup blocks reported by more than one angle, then rule. **Before proposing a CHANGE, read the prose
immediately around it** -- a deliberate design usually says so directly above itself, and one finding
reopened a decision closed six weeks earlier because the dated line above it went unread. But do not
let the neighbours stop you *reporting*: a neighbour asserting the same false thing is two findings,
not zero. Then two questions, in order. **Is it CHECKABLE** from the code as it stands, without
archaeology? **Is it NECESSARY** -- would someone changing this code make a *worse decision* without
it? Not "is it interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader verifies and needs | **drop** -- the code says it |
| **not checkable** | **move** -- real rationale, unverifiable in place | **drop** -- history |

! **Truth is not one of the questions, and that is the point.** *"Moved here from `x.validate` when
that module was deleted"* is true; the reader needs the check to live **here**, not its travel history.
Accuracy is the reason it was never deleted, not a reason to keep it. The exception is arithmetic -- a
claim that is pure arithmetic over committed values is checkable without judgement, so recompute it.

**`correct` is the fifth verdict, and it is not optional.** A block that is on-subject, local and
necessary but says something *false* is neither `keep` nor `drop`: it needs its claim replaced with the
true one, inline, citing the line that settles it. A real pass had 82 such blocks and a four-verdict
vocabulary with nowhere to file them, so they all went out as `keep`.

**When comment and code DO disagree, the verdict depends on which kind of claim it is:**

| the comment is a... | and it disagrees with the code -> |
|---|---|
| **description** | the comment is wrong -> `correct` it, or `drop` |
| **prohibition** | the code broke the rule -> file it; **the code moves, not the prose** |

* **A description written as a negation is a FORM defect on its own** -- rewrite it positive: *"! NOT
the kernel call site"* -> *"asserts on `session_set_equivalents` directly"*. A **prohibition** may stay
negative; no positive form keeps its force. Measured: a pass that compressed prose took negation from
17% of removed lines to **22% of what it wrote back** -- compressing *concentrates* negations.

* **A docstring carrying a date, a ruling, a quotation or a rationale paragraph is a finding at ANY
LENGTH.** It is a FORMAT failure, not a length one. A `#` run is capped because it interrupts code; a
docstring sits at a boundary, so long is not by itself a violation -- but "long is allowed" was read as
"rationale is allowed", and a docstring is then exactly where an evicted `#` block relocates.

**Rule on SENTENCES, not on blocks.** A container of six sentences can hold six verdicts, and the
common shape is a live constraint beside the story of where it came from. ! **A single `keep` sentence
launders every sentence around it** -- ruling `keep` because *part* of the block is load-bearing is the
signal to descend a level, and that is the default outcome for any comment mixing a rule with its
origin.

**compact** is not a fifth category -- it is what you do to a `keep`, or to the remainder a `move`
leaves. For a `move`, name the destination and send the **WHOLE block, including the half that stays
in the code**; a doc holding only what was discarded reads as a deletion list, not a record. !
**Account for every digit you propose deleting**: the most repeated defect a compaction pass
introduces is **a measurement replaced by an adjective**, and it always looks like a legitimate trim.

### What must be KEPT, and how much to report

A spec that only says what to cut deletes the load-bearing half. The five acquittals are the list,
plus **premise guards** (the assertion that makes the block above it safe), **the discriminator that
scopes a claim** without which a reader over-reads it, **why a fixture or constant is shaped oddly**
written ON the element, and **deliberate freezes**. There is no third category of "warnings".

**Report every block that fails a check, and no block that does not** -- but the two errors do not cost
the same. Missing a real defect costs several times what one over-eager finding costs, because a
missed block is invisible while an over-eager one is argued down in review. In one measured slice
**59% of the prose blocks in six files** were rewritten by the next pass, so a ten-finding report on a
file of that shape is a miss, not selectivity. Equally, `keep` is a real verdict and a review whose
acquittals outnumber its findings is a good one -- provided every acquittal is *named*. ! **The tail is
not like the head**: where a cap is nearly met most remaining blocks are one line over (on one tail, 27
of 48), so cut the least-checkable line and **do NOT rewrite a block already true and on-subject.** !
And **"this tree looks fine" from a reviewer who has only read guarded code is not evidence** -- a tree
entering a guard's scope for the first time held 11 dangling citations against 0 in the guarded one.

## Phase 3 -- present. Always.

**This skill never edits. It ends with the verdict list.** Report grouped by verdict, most
consequential first, the replacement inline for every `compact` and every `correct`, and a coverage
line: *N swept, M findings, K acquitted by reason*. Then stop. ! **Even when the human names the
edit** -- "cap them", "go do it" -- the deliverable is still the report: *"Report only, per the skill --
say the word and I'll apply the verdicts you accept."* An imperative is not authorization; this
review's whole value is the human's disagreement with it, and **an edit applied is a verdict never
ruled on.** Measured: two runs on near-identical prompts split, one report, one 846-line diff.

## Rails for the pass that applies these -- it usually runs without this skill loaded

- **A block is bounded by CODE, not blank lines** -- else a 9-line run passes a cap of 6 as 6+blank+3.
- **Never change a line of code, a docstring's meaning, or a string literal**, proved by diffing every
  non-comment line against the pre-edit file; that caught two cuts that took real code.
- **Extract before you cut** on a `move` -- the other order lost the text three times.
- **Apply with `count == 1` or refuse the whole file**, with `old` built programmatically rather than
  transcribed from `Read` output; check each replacement's **width** as well as its line count, and
  preserve the file's own line ending, or a 3-line prose edit lands as a whole-file diff.
- **Re-read what you wrote** -- run the sweep over your own replacements. A pass that cut seven
  obituaries wrote seven new ones, the same one twice in one file.

`/simplify` reviews code structure and applies what it finds; `/code-review` hunts correctness bugs;
this one reviews prose and **only ever proposes**. **Every example above is invented or anonymised.
Keep it that way** -- quoting a real comment teaches recognition of *that comment* rather than the
shape, and rots into an obituary of its own the day someone acts on the finding.
