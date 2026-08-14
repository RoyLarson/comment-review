---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles — currency,
  functionality, locality, module coherence — after a mechanical sweep, and return each finding with
  a proposed verdict (drop / move / compact / keep) for the human to rule on. Use this whenever
  comments or documentation are the subject: after finishing a task that added or edited commentary,
  when a file's comments have drifted from what the code now does, when someone says a comment is too
  long or out of date or "isn't this history", when reviewing a diff specifically for its prose rather
  than its logic, before a docs or comment burn-down, or when asked to check whether a module still
  reads as one module. Trigger on phrasings that never say "comment review" — "these comments are
  getting out of hand", "does this docstring still match", "is this comment still true", "clean up the
  narration in this file", "why does this file need so much explaining" all mean run this. It is NOT
  /simplify (which reviews code structure and applies its fixes) and NOT /code-review (which hunts
  correctness bugs) — this one ONLY EVER PROPOSES and never edits anything, not code and not even the
  comments it rules on, because an edit applied is a verdict the human never got to rule on. Run it
  even when the request sounds like an instruction to cut ("cap these", "clean this up"): the
  deliverable is still the verdict list, and applying is a separate step. It is explicitly not a
  reviewer's job to judge whether the code works: code concerns get raised in a line and left, while
  every verdict returned is a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` → sweep → 4 reviewers in parallel → a verdict per finding → you decide.

## The subject is the prose, not the program

**It is not a reviewer's job to decide whether the code works.** Every verdict you return is a verdict
on a comment. You will still notice code problems — say so in a separate section, one line each, and
**never** let a code finding acquire a `drop`/`move`/`compact`/`keep` verdict.

| This is a COMMENT finding | This is a CODE finding |
|---|---|
| the comment says the function reads one field; it reads three | the function should not read three |
| the comment names a symbol that no longer exists | the symbol should be restored |
| the comment claims callers `grep` cannot find | the function is dead and should be deleted |

⚠ **Measured: a reviewer straying into correctness is where this skill's worst output comes from.** In
two eval rounds a reviewer read `except ValueError, TypeError:` and reported the file "cannot compile"
— wrong, and volunteered while reviewing prose. If your claim is about whether the code *runs*, it is
not your finding; if you make it anyway you owe it a `python -c` or an `ast.parse` first.

## The governing law — look where nothing asserts

**Every false statement found in a real burn-down was one no assertion touched.** Not the oldest, not
the longest, not the furthest from its code. Position predicted nothing: false clauses sat *inside*
blocks whose other sentences were true, same voice, same indentation. One split mid-sentence — the
clause before the comma was asserted by the body and true, the clause after was asserted by nothing
and false. So **"look where nothing asserts" beats "look for long blocks."** A count, a call-site
claim or a retracted fact sitting *beside* a passing test is decoration, and decoration is what
survives a change to the thing it describes.

## Arguments

- **`cap`** — an integer, optional: the maximum lines one comment block may run. Pass it to the sweep
  and to every reviewer. **This skill has no cap of its own and must not invent one.** If the repo
  publishes a cap in a guard, use that and say where you got it — read *how it measures*, too. With no
  cap anywhere, review by judgement and **report the longest block found**.
- **`target`** — a path, optional. Defaults to the files in the diff.

## Phase 0 — scope, then sweep

Scope: `git diff --name-only @{upstream}...HEAD` (or `main...HEAD`, or `HEAD~1`); add
`git diff --name-only HEAD` if the tree is dirty or the range is empty. That gives a **file list**. Now
review **all commentary in those files, not just the changed lines** — comment debt is cumulative and
mostly pre-existing, and the 54-line block that has sat above a four-line expression for months is the
finding worth having, which a diff-scoped reviewer never sees.

Then run the mechanical pass and paste its report into all four reviewer prompts:

```bash
python .claude/skills/comment-review/sweep.py --cap 6 --width 104 --repo . <files>
```

It is read-only, always exits 0, and needs nothing but Python files. Per block it reports over-cap runs,
wide lines, **dead-name candidates** (backticked *and bare* identifiers that resolve nowhere), dangling
paths and test citations, counted claims, coverage claims, history markers, negated descriptions,
rationale paragraphs, `Args:`/`Returns:`/`Raises:` that disagree with the signature, and sentences
restated in more than one place.

Three things measurement settled, all preserved in the script — do not "fix" them back. The name corpus
comes from the **AST, never raw text** (built from text it contains the very comments being checked, so
the check always passes), and string constants are harvested from **non-test** files only — a test pins
a deleted field with a negative assertion, which taught one resolver that every dead name was alive and
masked 4 of 7 known ones. A **virtualenv in the tree poisons the corpus**, so every installed package's
methods become "known" and the result depends on what is installed; the sweep skips any directory
holding `pyvenv.cfg`. And the **head** segment of a dotted name must resolve, not any segment: matching
any part lets `Dead.meta` pass on `meta`, which is exactly where a dead name hides.

⚠ **Nothing the sweep emits is a verdict**, and a block with no signal can still be the worst prose in
the file. Signals are *reasons to look*. Equally: **do not re-derive what it already settled** — a
reviewer that spends its budget confirming a file exists has spent it badly.

## Phase 1 — four reviewers, in parallel

Launch **four subagents in one message**. Give each the file list, the sweep report, the `cap`, and one
angle. Each finding returns `file`, `line`, the exact claim, **the exact code or test line that
settles it**, and `CONFIRMED` (both sides read) or `SUSPECTED` (not). Measured: 196 of 202 came back
CONFIRMED once this was asked for, and one reviewer withdrew two candidates rather than pad.

⚠ **Reviewers are READ-ONLY; say so in their prompt.** Four agents editing one file is a race whose
loser's edits vanish, and a reviewer that fixes what it finds has destroyed the finding.

⚠ **Name the writable targets and the read-only reference files separately.** A reviewer handed a
contract document as *reference* returned three proposals editing it, which were applied — landing a
false claim in a skill doc, produced by the pass whose purpose was removing false claims.

⚠ **Before reporting, read the prose immediately around the block.** A deliberate design usually says
so directly above itself. One finding — "this function sums two different units" — was true, and the
line above it explained why, dated; the resulting TODO reopened a decision closed six weeks earlier.
Overlap between angles is signal, not waste: a finding all four report is almost always real, and two
reviewers disagreeing once caught an arithmetic *correction* that was itself wrong.

### Currency — does this describe the program as it is now? (~45% of findings)

Git holds what the code used to be. A comment that narrates its own history does git's job badly.

Flag dated rulings, review-round labels ("fix round 2", "finding B4", "Part B"), "this used to…", "X
was changed to Y", "no longer", "previously" — and the sharpest form, **obituaries**: a name, file,
test or flag that no longer exists anywhere. A reader greps, finds nothing, and reads it as *their*
mistake.

⚠ **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar` is
written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Search a loose stem and triage. Measured on a
real deletion: the identifier grep found ten mentions, all correctly dated tombstones, and **missed an
eleventh written with a hyphen — the only present-tense claim about the dead path in the set.** The
failure is self-concealing: a clean grep reads as a clean file.

**Every number is a citation.** A count in prose is unverifiable unless it names the **set it counts
over**, and re-deriving one means re-deriving the SET first. Measured misses: "the 37 mobility ids"
(35), "left all 1626 other tests green" (3041), a hand-worked division whose inputs had both moved. A
prose pass correcting a false number produced a differently-false one because it re-counted the wrong
population.

### Functionality — does the commentary match what the function is for? (~30%)

Read name, signature and docstring, then the body. Flag disagreement: a return shape the code no longer
returns, a `Returns:` naming fields in the wrong order, an `Args:` entry for a parameter that does not
exist, a documented exception nothing raises, a summary saying "Yield" over a function that returns.
The **summary line** drifts silently, because changing a return type does not change the sentence
describing it.

**Claims about coverage are the class that licenses deletions, and are disproportionately wrong.**
"pinned by X", "guarded by Y", "the only call site", "nothing asserts this" — each authorises the next
person to delete something. Grep the cited name, every time.

| | **the guard exists** | **it does not** |
|---|---|---|
| **the comment claims one** | fine — cite it precisely enough to find | ⚠ **the dangerous cell** |
| **the comment claims none** | a silent constraint — consider saying so | nothing to check |

The dangerous cell: a deletion justified by coverage nobody can find, which reads as safe for exactly
that reason. A real guard has already been dropped in one repo on a pointer to a test never written —
and the inverse also happens: a comment declaring a live config value decorative, licensing the
deletion of something five call sites read.

⚠ **A citation your checker cannot parse is worse than one it can parse and reject.** A brace
expansion, a bare `test_thing`, a line-number citation (`x.py:201`): the parseable wrong one gets
fixed on the next run; the unparseable one accumulates, and its terseness reads as authority.

**Then read the body's comments as one sequence.** Individually each may be true; end to end they are
the most honest description of the function in the file. A run of *"now I need to…", "oh I should…",
"this other thing should also…"* is a to-do list left in the body: those comments **sequence** instead
of **constrain**, so they go nowhere when their line moves. Say which each step is — **(A)** not needed
for the function to be the function, or **(B)** real work at the wrong level. ⚠ **Report the mismatch;
do not resolve it.** Either the docstring grows until it tells the truth, at which point the *name* is
wrong, or the function shrinks to what it is called; naming that fork is the deliverable.

### Locality — does this comment belong to the line it sits on?

A comment points DOWN for a block on its own lines, AT the declaration for a trailing one. A field
comment (`retries: int  # 0 disables the backoff`) is exactly where it belongs.

The finding is a comment about something **else**: a block whose later half turns back to narrate what
came before, a rule stated at the top of a class that really constrains two literals two hundred lines
down. Second test: **if this code changed, would the comment become wrong — and would anyone notice?**
A comment that would quietly survive a change to the code it describes is not local to it. Flag the
inverse too: a line carrying a non-obvious constraint with no comment, where getting it wrong is
silent. **Refactoring drift** is this angle's biggest yield — when code moves, its commentary either
moves with it, stays behind describing something that left, or follows and stops being true.

### Module coherence — do the comments say this is one module?

Read only the module docstring, section banners, and top-of-file commentary. Flag prose announcing two
or three subjects, banners that read like chapter breaks rather than parts of one argument, a docstring
enumerating unrelated responsibilities to be accurate, or a docstring describing a fraction of its
module. Also flag **the same rule explained in several modules** — that means the rule has no owning
function, and each site that performs part of it re-explains the whole. A long comment above a short
expression is usually this. Report it as a code-shape finding with the comment as evidence.

## Phase 2 — one verdict per finding

Wait for all four, dedup blocks, then rule on each survivor.

**Is it CHECKABLE?** Could a reader confirm or refute it from the code as it stands, without
archaeology? **Is it NECESSARY?** Would someone changing this code make a **worse decision** without
it — not "is it interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** — a constraint the reader verifies and needs | **drop** — the code says it |
| **not checkable** | **move** — real rationale, unverifiable in place | **drop** — history |

⚠ **Truth is not one of the questions, and that is the point.** *"Moved here from `x.validate` when
that module was deleted"* is true; the reader needs the check to live **here**, not its travel history.
Accuracy is the reason it was never deleted, not a reason to keep it.

**When comment and code DO disagree, the verdict depends on which kind of claim it is:**

| the comment is a… | and it disagrees with the code → |
|---|---|
| **description** | the comment is wrong → `drop` or fix it |
| **prohibition** | the code broke the rule → file a TODO; **the code moves, not the prose** |

⭐ **A description written as a negation is a FORM defect on its own.** You cannot check "X is not the
case" against the code — you must establish what the code *does* do and argue backwards. Rewrite it
positive: *"⚠ NOT the kernel call site"* → *"asserts on `session_set_equivalents` directly"*. A
**prohibition** may stay negative; no positive form keeps its force. Measured: a pass that compressed
prose took negation from 17% of removed lines to **22% of what it wrote back** — compressing
*concentrates* negations unless you look for them.

**Rule on sentences, not on blocks.** A container of six sentences can hold six verdicts. ⚠ **A single
`keep` sentence launders every sentence around it** — if you are ruling `keep` because *part* of the
block is load-bearing, descend a level. A block's most defensible sentence is usually why the whole
block survived this long.

**Then ask: is what survives longer than it needs to be?** If so the verdict is **compact** — same
content, fewer words. Compact is not a fifth category; it is what you do to a `keep`, or to the
remainder a `move` leaves behind. For **move**, name the destination; if the repo stages extracted
prose somewhere, send it there. ⚠ **The destination gets the WHOLE block, including the half that
stays in the code** — a doc holding only what was discarded reads as a deletion list, not a record.

### What must be KEPT — a spec that only says what to cut deletes the load-bearing half

- **Hand-worked derivations.** They are what stop an assertion being an echo of the implementation, and
  they are the first thing a careless cap deletes. ⭐ **Move one into the DOCSTRING rather than
  compacting it** — a `#` run is capped because it interrupts code; a docstring sits at a boundary. One
  16-line derivation moved that way took a file from 10 excess lines to 0 with every digit intact.
- **Premise guards** — the assertion that makes the block above it safe — and **the discriminator that
  scopes a claim**, without which a reader over-reads it.
- **Why a fixture or a constant is shaped oddly**, on the element rather than above the section; and a
  comment **naming its own expiry condition**, so the next reader does not have to judge.
- **A warning against a plausible wrong move — ONLY where nothing goes red.** ⚠ Where a test *does*
  catch the move, the comment is a time-saver, not a guard, and it is `compact`. There is no third
  category of "warnings"; calling one is the laundering failure above.

### Calibration

Report **every block that fails a check, and no block that does not.** Padding and pruning cost the
same. A tidy-looking short list is a failure mode: in one measured slice **59% of the prose blocks in
six files** were rewritten by the next pass, so a ten-finding report on a file of that shape is a miss,
not selectivity. Equally, `keep` is a real verdict and a review returning mostly `keep` is a good one.

⚠ **The tail is not like the head.** Where a cap is nearly met, most remaining blocks are one line
over: cut the single least-checkable line, and **do NOT rewrite a block that is already true, current
and on-subject.** A block one line over cap is by construction mostly correct.

⚠ **"This tree looks fine" from a reviewer who has only read guarded code is not evidence.** Measured
twice: a tree entering a guard's scope for the first time held 11 dangling citations against 0 in the
guarded tree — same repo, same authors, same period. Defects concentrate where the checker cannot see.

## Phase 3 — present. Always.

**This skill never edits. It ends with the verdict list.** Report grouped by verdict, most consequential
first, with proposed replacement text inline for every `compact`; then stop.

⚠ **Even when the human names the edit** — "cap them", "fix these", "go do it" — the deliverable is the
report: *"Report only, per the skill — say the word and I'll apply the verdicts you accept."* This
review's whole value is the human's disagreement with it. **An edit applied is a verdict never ruled
on.** Measured before this rule: two runs given near-identical imperative prompts split, one returning
a report and the other an 846-line diff.

## Rails for the pass that applies these

You are not that pass. Hand these along, because that pass usually runs without this skill loaded.

- **A comment block is bounded by CODE, not by blank lines** — otherwise a 9-line block becomes 6+3.
- **Never change a line of code, a docstring's meaning, or a string literal.** Prove it: diff every
  non-comment line against the pre-edit file and confirm zero differences. That caught two cuts that
  ran one line too far and took real code with them.
- **Extract before you cut** when the verdict is `move`. The other order loses the text on any
  interruption — three times, before this became the rule.
- **Apply with `count == 1` or refuse the whole file.** Have the agent build the `old` string
  programmatically rather than transcribing it from `Read` output; the two batches that did had zero
  misses. Check each replacement's **width** as well as its line count, and preserve each file's own
  line ending, or a 3-line prose edit lands as a whole-file diff.
- **Re-read what you wrote.** A pass that cut seven obituaries wrote seven new ones, the same one twice
  in one file, and wrote over-length blocks while removing over-length blocks.

## What this skill is not, and a note for whoever edits it

`/simplify` reviews code structure and applies what it finds. `/code-review` hunts correctness bugs.
This one reviews prose and **only ever proposes**; when a reviewer notices a defect anyway, **name it
and leave it.** `/simplify` ends in a diff; this ends in a list of questions.

**Every example above is invented or anonymised. Keep it that way.** Quoting a real comment teaches a
reviewer to recognise *that comment* instead of the shape, and it rots: the day someone acts on the
finding, this file cites a comment that no longer exists — a hygiene skill carrying its own obituary.
