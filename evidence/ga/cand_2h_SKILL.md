---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles — currency,
  functionality, locality, module coherence — after a mechanical sweep that enumerates EVERY prose
  block, and return each block a verdict (drop / move / compact / correct / keep) or a named
  acquittal for the human to rule on. Use this whenever comments or documentation are the subject:
  after a task that added or edited commentary, when a file's comments have drifted from what the
  code now does, when someone says a comment is too long or out of date or "isn't this history",
  when reviewing a diff for its prose rather than its logic, before a docs or comment burn-down, or
  when asked whether a module still reads as one module. Trigger on phrasings that never say
  "comment review" — "these comments are getting out of hand", "does this docstring still match",
  "is this comment still true", "clean up the narration in this file", "why does this file need so
  much explaining" all mean run this. It is NOT /simplify (code structure, and it applies its
  fixes) and NOT /code-review (correctness bugs) — this one ONLY EVER PROPOSES and never edits
  anything, not code and not even the comments it rules on, because an edit applied is a verdict
  the human never got to rule on. Run it even when asked to cut ("cap these", "clean this up"): the
  deliverable is still the verdict list, applying is a separate step, and code concerns get raised
  in a line and left.
---

# comment-review

`/comment-review [cap] [target]` → sweep → 4 reviewers → a verdict or acquittal per block → you rule.

## The two rules that decide this skill's yield

**1. The unit of work is the BLOCK LIST, not the file.** Phase 0 enumerates every comment run and
every docstring in scope and numbers them. Each reviewer walks that list start to finish. A block
nobody mentioned is a **gap in the review**, not one that passed; the report says how many were
swept. That is the difference between a review and a search — a reviewer told to "find the comments
that need attention" returns its most confident dozen and stops.

**2. You do not get to acquit by SILENCE.** An acquittal is a written verdict naming a reason from
the closed list below — one line, cheap enough to afford total coverage, dear enough to force a
decision rather than a shrug. This is what stops rule 1 degenerating into "flag everything".

⚠ **Look where nothing asserts.** Every false statement found in a real burn-down was one no
assertion touched — not the oldest, not the longest, not the furthest from its code. The false
clauses sat *inside* blocks whose other sentences were true, same voice, same indent, under the
same warning glyph; one split mid-sentence, the clause before the comma asserted by the body and
true, the clause after asserted by nothing and false. A count, a call-site claim or a retracted
fact sitting *beside* a passing test is decoration, and decoration is what survives a change to
the thing it describes.

### The acquittal list — the ONLY reasons to pass a block over

Closed list. If none applies, the block gets a finding.

- **`label`** — a one- or two-line comment naming the line it sits on and claiming nothing else
  (`# Kalman gain`, `# 0 disables the backoff`).
- **`states-the-signature`** — a one- or two-line docstring, present tense, matching the name, the
  arguments and the return, citing nothing outside itself. Three lines or more is no longer this:
  it is carrying something, and what it carries is what you are here to read.
- **`derivation`** — a hand-worked calculation whose digits stop an assertion being an echo of the
  implementation, and the *first* thing a careless cap deletes. Over cap it is a `move` **into the
  docstring** — which sits at a boundary and has no cap — never a `compact`.
- **`only-guard`** — a warning against a plausible wrong move where **nothing goes red** if
  someone makes it. Verify that; if a test does fail it is a time-saver, not a guard, and it is
  `compact`. There is no third category of "warnings".
- **`names-its-expiry`** — prose stating the condition under which it stops being wanted.

Nothing is acquitted for being short, true, well written, new, or sitting under a `⚠`.

⚠ **A docstring carrying a date, a ruling, a quotation, a "considered and rejected", or a
rationale paragraph is a finding AT ANY LENGTH.** That is a FORMAT failure, not a length one, and
it is exactly where an evicted `#` block relocates. `derivation` does not cover it.

## The subject is the prose, not the program

You will notice code problems — say so, one line each, in a separate section, and move on. **Raise a
concern, do not open an investigation**, and never give a code finding a verdict. *The comment names
a symbol that no longer exists* is yours; *the symbol should be restored* is not.

⚠ **A reviewer straying into correctness is this skill's worst measured output.** Twice a reviewer
read a modern multi-exception `except` clause and reported the file "cannot compile", volunteered
while reviewing prose; once four agreeing reviewers shipped it. If your claim is about whether the
code *runs*, it is not your finding; making it anyway costs you an `ast.parse` first.

**Arguments.** `cap` — optional integer, the most lines one `#` block may run. **This skill has no
cap of its own and must not invent one**; a cap published in a lint config or a hygiene test is the
number, and read how it *counts* too. With no cap, judge and **report the longest run found**.
`target` — an optional path, defaulting to the files in the diff.

## Phase 0 — enumerate, mechanically

Scope is **whole files, not the diff**. Take the file list from
`git diff --name-only $(git merge-base HEAD @{upstream} || git merge-base HEAD main)..HEAD`, adding
`git diff --name-only HEAD` when the tree is dirty or the range is empty. ⚠ **Use `merge-base`,
never `A...B` between two tips** — the three-dot form drags in the other branch's work. Every block
inside those files is in scope: comment debt is cumulative and mostly pre-existing, and the long
block that has sat above a four-line expression for months is the finding worth having, which a
diff-scoped reviewer never sees. Run this, and **paste its output — the block list — into every
reviewer prompt.**

```bash
python .claude/skills/comment-review/sweep.py --cap 6 --width 100 <files>
```

It is stdlib-only, read-only, always exits 0, assumes nothing about the repo, and survives a missing
path or an unparseable file. Per block it prints `path:start-end kind NL tags` — a comment RUN
bounded by **code, not blank lines** (else 9 lines pass as 6 + blank + 3), a docstring from the AST,
and tags for over-cap, over-width, `docstring:NL`, dated, history, coverage-claim, counted,
cites-a-path, negated, rationale, quotation, names-a-symbol — then the total and the longest run.

Then resolve what it only located: every `cites-a-path` against the tree, every `names-a-symbol`
against the names the code defines. Four things measurement settled about that corpus — do not
"fix" them back:

- Build it from the **AST, never raw text**. A corpus built from text contains the very comments
  being checked, so the check always passes.
- **Exclude `.md` and `.txt`.** A doc discussing a deleted symbol otherwise vouches for it;
  measured, that alone suppressed three real obituaries.
- **Never harvest string constants from tests.** A negative assertion (`assert "x" not in y`)
  makes a dead name read as alive — one resolver so taught masked 4 of 7 known dead names.
- The **head** segment of a dotted name must resolve, not any segment; a **virtualenv poisons the
  corpus**, so skip any directory holding `pyvenv.cfg`.

⚠ **A resolved citation is not a verified one.** A citation asserts something *about* its target,
so open it and read it, or mark the finding `SUSPECTED`. Nothing the sweep emits is a verdict, and
a block with no tag can still be the worst prose in the file — tags are reasons to look. Equally,
**do not re-derive what it settled**: a reviewer confirming a file exists has spent its budget
badly.

## Phase 1 — four reviewers, each over the WHOLE list

Launch four subagents **in one message**. Give each the file list, the sweep output, the `cap`, the
acquittal list, and one angle. **Tell each, in words, to return a line for every numbered block.**
Every finding carries `file:line`, the exact claim, the code or test line that settles it, and
**`CONFIRMED` (both sides read) or `SUSPECTED` (not)** — measured, 196 of 202 came back CONFIRMED
once this was asked for, and one reviewer withdrew two candidates rather than pad.

⚠ **Reviewers are READ-ONLY; say so explicitly**, and **name two lists: the files UNDER REVIEW,
which a proposal may target, and files given only as REFERENCE, which it never may.** A reviewer
that fixes what it finds has destroyed the finding, and one handed a contract document as reference
returned three edits *to the contract*, which were applied. Overlap between angles is signal, not
waste: a finding all four report is almost always real, and on one run the second angle caught an
error the first had just introduced.

### Currency — does this describe the program as it is now? (~45% of yield)

The largest angle by a distance. Git holds what the code used to be; a comment narrating its own
history is doing git's job badly. Flag dated rulings, review-round labels ("fix round 2", "finding
B4", "Part B"), "this used to…", "X was changed to Y", "no longer", "previously" — and the sharpest
form, **obituaries**: a name, file, test or flag that no longer exists anywhere. A reader greps,
finds nothing, and reads it as *their* mistake.

⚠ **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar`
is written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Measured on a real deletion, the
identifier grep found ten mentions, all correctly dated tombstones, and **missed an eleventh
written with a hyphen — the only present-tense claim about the dead path in the set.** The failure
is self-concealing: a clean grep reads as a clean file.

**Every number is a citation.** A count in prose is unverifiable unless it names the **population
it counts over**, so re-derive the SET before the number. Measured misses: "the 37 mobility ids"
(35), "left all 1626 other tests green" (3041), a hand-worked division whose inputs had both moved;
a pass correcting a false count produced a differently-false one, off by 5×.

### Functionality — does the commentary match what the code does? (~30%)

Read name, signature and docstring, then **read the body** — the flagship false claims are
contradicted two or three lines below themselves. Flag a return shape the code no longer returns, a
`Returns:` whose key and value are the wrong way round, an `Args:` entry for a parameter that does
not exist or that guards the wrong object, a documented exception nothing raises, a raise nothing
documents, a summary line summarising the first four lines of a five-job function. The **summary
line** drifts silently: changing a return type does not change the sentence describing it.

**Claims about coverage are the class that licenses deletions, and are disproportionately wrong.**
"Pinned by X", "guarded by Y", "the only call site", "nothing asserts this" — each authorises the
next person to delete something, so the claim is checked, never read.

| | **the guard exists** | **it does not** |
|---|---|---|
| **the comment claims one** | fine — cite it precisely enough to find | ⚠ **the dangerous cell** |
| **the comment claims none** | a silent constraint — consider saying so | nothing to check |

**Reachability lives here, not in a fifth angle.** Per claim: does the annotated constant have a
reader? does the documented function have a caller outside the tests? is the hazard still
triggerable? For data reached by key rather than by name, grep the STRING. It fails both ways — a
real guard was deleted on a pointer to a test that never existed, and a comment calling a live
config value "decorative" nearly licensed deleting what three sites read. ⚠ **An unreachable hazard
is not automatically a `drop`**: a precaution's value is having no trigger. ⚠ **A citation your
checker cannot parse is worse than one it can parse and reject** — a bare `test_thing`, a
line-number citation (`x.py:201`). The parseable wrong one gets fixed next run; the unparseable one
accumulates, and its terseness reads as authority.

⚠ **Prose that DESCRIBES behaviour is wrong far more often than prose that PROHIBITS something.**
A description disagreeing with the code → the comment is wrong. A prohibition disagreeing → the
code broke the rule → file it, the code moves and not the prose. ⚠ **Resolve superlatives and
collective nouns against their own file**: "single source of truth", "THE only entry point",
"these constants" — a "one definition" naming a single member is a tautology, and an "only entry
point" is refuted 25 lines down often enough to check always.

**Then read the body's comments as one sequence.** Individually each may be true; end to end they
are the most honest description of the function. The tell is grammatical — a comment that
**sequences** ("now I need to…", "then we…") instead of **constrains**. Report the mismatch and
name the fork: the docstring grows until the *name* is wrong, or the function shrinks.

### Locality — does this comment belong to the line it sits on?

A comment points DOWN for a block on its own lines, AT the declaration for a trailing one. The
finding is a comment about something **else**: a rule at the top of a class that really constrains
two literals two hundred lines down; a block whose later half turns back to narrate what came
before; a run sitting *after* an unconditional `return`, or between two statements annotating
neither. The test for anything that survives: **if this code changed, would the comment become
wrong — and would anyone notice?**
Flag the inverse too: a line carrying a non-obvious constraint with no comment, where getting it
wrong is silent. **Refactoring drift** is this angle's biggest yield — when code moves, its
commentary either moves with it, stays behind describing something that left, or follows and stops
being true.

### Module coherence — do the comments say this is one module?

Read only the module docstring, the section banners, and the top-of-file prose. Flag prose
announcing two or three subjects, banners reading like chapter breaks rather than parts of one
argument, a docstring that must enumerate unrelated responsibilities to be accurate, and a
docstring describing a fraction of its module. Also flag **the same rule explained in several
modules** — the rule has no owning function, so each site performing part of it re-explains the
whole; check every copy, because the owner stays right while the copy rots. A long comment above a
short expression is usually this: report it as a code-shape finding with the comment as evidence.

## Phase 2 — one verdict per block

Dedup blocks reported by more than one angle, then rule. **Before proposing a change, read the
prose immediately around it** — a deliberate design usually says so directly above itself; but do
not let a neighbour stop you *reporting*: one asserting the same false thing is two findings, not
zero. Then two questions. **Is it CHECKABLE** from the code as it stands, without archaeology?
**Is it NECESSARY** — would someone changing this code make a *worse decision* without it? Not
"is it interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** — a constraint the reader needs | **drop** — the code says it |
| **not checkable** | **move** — rationale, unverifiable here | **drop** — history |

⚠ **Truth is not one of the questions, and that is the point.** History that is *correct* reads as
earning its place and does not; accuracy is the reason it was never deleted, not a reason to keep
it. The exception is arithmetic — a claim that is pure arithmetic over committed values is
checkable without judgement, so recompute it rather than rule on it.

**A fifth verdict: `correct`.** A block that is on-subject, local and load-bearing but says
something *false* is neither `keep` nor `drop` — it is a fix, and it needs its replacement text
written out. Without it a real pass had 82 such blocks nowhere to file, laundered into `keep`.
`compact` is likewise not a category of its own: it is what you do to a `keep`, or to the
remainder a `move` leaves behind.

**Rule on SENTENCES, not on blocks.** A container of six sentences can hold six verdicts, and the
common shape is a live constraint beside the story of where it came from. ⚠ **A single `keep`
sentence launders every sentence around it** — if you are ruling `keep` because *part* of the block
is load-bearing, descend a level. A block's most defensible sentence is usually why the whole block
survived this long.

For a **move**, name the destination and send the **WHOLE block, including the half that stays** —
a doc holding only what was discarded reads as a deletion list, not a record. ⚠ **Account for every
digit you propose deleting**: the most repeated defect a compaction pass introduces is **a
measurement replaced by an adjective**, and it always looks like a legitimate trim. ⚠ **A
description written as a negation is a FORM defect on its own** — rewrite it positive; a
*prohibition* may stay negative, no positive form keeps its force. Measured: a compressing pass
took negation from 17% of removed lines to 22% of what it wrote back.

### Calibration

**Report every block that fails a check, and no block that does not.** Padding and pruning cost the
same. A tidy short list is a failure mode: in one measured slice **59% of the prose blocks in six
files** were rewritten by the next pass, so a ten-finding report on a file of that shape is a miss,
not selectivity. ⚠ **The tail is not like the head** — where a cap is nearly met most remaining
blocks are one line over (on one tail, 27 of 48), so cut the least checkable line and **do not
re-author a block already true, current and on-subject**. ⚠ **Defects concentrate where the checker
cannot see**: a tree entering a guard's scope for the first time held 11 dangling citations against
0 in the guarded tree — same repo, same authors, same period.

## Phase 3 — present. Always.

**This skill never edits. It ends with the verdict list.** Report grouped by verdict, most
consequential first, the replacement text inline for every `compact` and every `correct`, and a
coverage line: *N swept, M findings, K acquitted by reason*. Then stop.

⚠ **Even when the human names the edit** — "cap them", "fix these", "go do it" — the deliverable is
the report: *"Report only, per the skill — say the word and I'll apply the verdicts you accept."*
An imperative is not authorization, and **an edit applied is a verdict never ruled on.** Measured
before this rule: two runs on near-identical prompts split, one report, one 846-line diff.

## Rails for the pass that applies these

You are not that pass; the applier usually runs without this skill loaded.

- **A block is bounded by CODE, not blank lines** — else 9 lines become 6 + blank + 3.
- **Never change a line of code, a docstring's meaning, or a string literal**; prove it by diffing
  every non-comment line, which caught two cuts that ran one line too far into real code.
- **Extract before you cut** on a `move` — the other order lost the text three times.
- **`count == 1` or refuse the whole file**, with the `old` text built programmatically rather than
  transcribed from `Read` output, its width checked as well as its line count, and the file's own
  line ending preserved, or a 3-line prose edit lands as a whole-file diff.
- **Re-read what you wrote.** A pass that cut seven obituaries wrote seven new ones, and wrote
  over-length blocks while removing over-length blocks.

**Every example above is invented or anonymised. Keep it that way.** Quoting a real comment teaches
a reviewer to recognise *that comment* instead of the shape, and it rots: the day someone acts on
the finding, this file cites a comment that no longer exists — its own obituary.
