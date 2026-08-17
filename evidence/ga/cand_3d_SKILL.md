---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles -- currency,
  functionality, locality, module coherence -- after a mechanical census, and return each finding with
  a proposed verdict (drop / move / compact / correct / keep) for the human to rule on. Use this
  whenever comments or documentation are the subject: after finishing a task that added or edited
  commentary, when a file's comments have drifted from what the code now does, when someone says a
  comment is too long or out of date or "isn't this history", when reviewing a diff specifically for
  its prose rather than its logic, before a docs or comment burn-down, or when asked to check whether
  a module still reads as one module. Trigger on phrasings that never say "comment review" -- "these
  comments are getting out of hand", "does this docstring still match", "is this comment still true",
  "clean up the narration in this file", "why does this file need so much explaining" all mean run
  this. It is NOT /simplify (which reviews code structure and applies its fixes) and NOT /code-review
  (which hunts correctness bugs) -- this one ONLY EVER PROPOSES and never edits anything, not code and
  not even the comments it rules on, because an edit applied is a verdict the human never got to rule
  on. Run it even when the request sounds like an instruction to cut ("cap these", "clean this up"):
  the deliverable is still the verdict list, and applying is a separate step. It is explicitly not a
  reviewer's job to judge whether the code works: code concerns get raised in a line and left, while
  every verdict returned is a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` -> census -> 4 reviewers in parallel -> a verdict per block -> you rule.

## The subject is the prose, not the program

**It is not a reviewer's job to decide whether the code works.** Every verdict you return is a verdict
on a comment; note code problems in a separate section, one line each, and never give one a prose
verdict. The best findings look like code findings and are not: *the comment says this reads one field
and it reads three* is yours, *it should not read three* is `/simplify`'s. ! **Measured, straying into
correctness is where this skill's worst output comes from**: twice a reviewer read `except ValueError,
TypeError:` and called the file uncompilable -- wrong, and volunteered while reviewing prose. Any claim
about whether the code RUNS owes an `ast.parse` first.

## Law 1 -- look where nothing asserts

**Every false statement found in a real burn-down was one no assertion touched** -- not the oldest, not
the longest, not the furthest from its code. False clauses sat *inside* blocks whose other sentences
were true, same voice, same indentation; one split mid-sentence, the half before the comma asserted by
the body and true, the half after asserted by nothing and false. **"Look where nothing asserts" beats
"look for long blocks."** A count, a call-site claim or a retracted fact beside a *passing* test is
decoration, and a comment beside a deleted thing is green *because* it is gone.

## * Law 2 -- a finding is SPENT, not free

**You are not filling a list; you are spending a budget.** Sixteen measured runs of this skill over one
fixed slice put a number on it: going from ~260 findings to ~360 bought **+1.5 points of recall** and
cost **19 points of precision**. Recall saturates early; discrimination does not. The sharpest pair: two
runs swept **the same 419 blocks with the same rules and the same vocabulary**; one acquitted **47%**,
one acquitted **14%**, and the one that acquitted more scored higher on both halves of the review's
value. It had kept the reasons to STOP. **The acquittal RATE is the skill; the acquittal LIST is only
vocabulary**, and vocabulary transplants without the restraint that earned it. So:

1. **For every block you raise you are choosing it over one you did not.** Before adding a finding at
   the margin, name the weakest finding already on the list; if you would not trade them, stop.
2. **A review reporting everything it could justify has reported nothing** -- the reader must now do the
   triage the review existed to do, on a list longer than the file.
3. **Expect to acquit about half.** A pass acquitting under a fifth of what it read is not thorough, it
   is refusing to decide; one acquitting four-fifths has stopped reading.

## What a disciplined pass LEAVES ALONE

The acquittal list. Padding is punished exactly as hard as missing, so none of these is a soft call:

- **A comment stating only what the adjacent line does**, present tense, no date, no citation, no
  count, no coverage claim, no universal -- `retries: int  # 0 disables the backoff`. A trailing field
  comment is *exactly* where it belongs and is never misplaced merely for following a statement.
- **A short banner naming what follows**, and **a docstring that is a summary line** plus an
  `Args:`/`Returns:` block that agrees with the signature.
- **A short run that is purely a present-tense constraint on the code it sits on**, checkable, nothing
  stale in it -- including a warning whose whole function is WHERE IT IS, aimed at the next author at
  the point of temptation. Moving that to a doc satisfies every other rule and destroys it.
- **Hand-worked derivations** -- the arithmetic that stops an assertion being an echo of the
  implementation, and the first thing a careless cap deletes. **Premise guards**, **the discriminator
  that scopes a claim**, **why a fixture is shaped oddly**, **a comment naming its own expiry**.
- ! **Prose whose only fault is that you find it wordy while it is true, current, local and
  on-subject.** That is not a finding, and it is the largest measured source of wasted budget.

## Phase 0 -- scope, then census

**`cap`** is an optional integer, the most lines one comment block may run, passed to the census and to
every reviewer. **This skill has no cap of its own and must not invent one**: if the repo publishes one
in a guard use that, say where you got it, and read *how it measures*; with none anywhere, review by
judgement and **report the longest block found**. **`target`** is an optional path, defaulting to the
diff. Scope with `git merge-base`: `git diff --name-only $(git merge-base HEAD @{upstream} || echo
HEAD~1)`, falling back to `main`/`master`, plus `git diff --name-only HEAD` if the tree is dirty or the
range is empty -- say which command produced the list and how many files it found, since in a worktree
these fail *silently*. Exclude `.md`/`.txt`. Then review **all commentary in those files, not just the
changed lines**: comment debt is cumulative and mostly pre-existing, and the 54-line block above a
four-line expression is the finding worth having, which a diff-scoped reviewer never sees.

Enumerate every prose block mechanically before anyone judges one, and paste the list into all four
reviewer prompts, so a reviewer's budget goes on the blocks and not on finding them. If a `sweep.py`
sits beside this file run that; otherwise this is the whole of it -- stdlib only, no repo assumptions,
exiting 0 on a missing path or a file that will not parse:

```python
import ast, io, sys, tokenize
from pathlib import Path

SKIP = (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT)
HOLD = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)

for arg in sys.argv[1:]:
    try:
        src = Path(arg).read_text(encoding="utf-8", errors="replace")
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
        tree = ast.parse(src)
    except (
        OSError,
        SyntaxError,
        ValueError,
        IndentationError,
        tokenize.TokenError,
    ) as e:
        print(f"skip {arg}: {e}")
        continue
    lines, out, cur = src.splitlines(), [], []
    for t in toks:  # a comment run is bounded by CODE, not by blank lines
        if t.type in SKIP:
            continue
        own = (
            t.type == tokenize.COMMENT
            and lines[t.start[0] - 1][: t.start[1]].strip() == ""
        )
        if cur and not (own and cur[-1][1]):
            out.append((cur[0][0], cur[-1][0], "#"))
            cur = []
        if t.type == tokenize.COMMENT:
            cur.append((t.start[0], own))
    for n in ast.walk(tree):
        b = n.body if isinstance(n, HOLD) else []
        d = b[0] if b and isinstance(b[0], ast.Expr) else None
        if isinstance(getattr(getattr(d, "value", None), "value", None), str):
            out.append((d.lineno, d.end_lineno, '"""'))
    print(f"== {arg}: {len(out)} blocks")
    for a, b, kind in sorted(out):
        print(f"  [{a}-{b}] {kind} n={b - a + 1}")
```

Tag each block as you read it: a date, a quotation, a review label, a count, a coverage claim, a
dangling path, an over-cap run. A richer sweep that resolves NAMES must build its corpus from the **AST,
never raw text** (from text it contains the comments being checked, so it always passes), never from
**tests** (one pinned a deleted field with a negative assertion and taught a resolver every dead name
was alive), and must skip any directory holding `pyvenv.cfg`. ! **Nothing a census emits is a verdict,
in either direction**: an unsignalled block can be the worst prose in the file and a date can be a
version number. Signals are *reasons to look*.

## Phase 1 -- four reviewers, in parallel

Launch **four subagents in one message**. Give each the file list, the census, the `cap`, one angle, and
**Law 2** -- the budget, not only the checklist. Each finding returns `file`, `line`, the exact claim,
**the exact code or test line that settles it**, and `CONFIRMED` (both sides read) or `SUSPECTED`;
measured, 196 of 202 came back CONFIRMED once this was asked for, and one reviewer withdrew two
candidates rather than pad. ! **Reviewers are READ-ONLY, and the prompt must name the writable targets
and the read-only reference files separately** -- a reviewer that fixes what it finds has destroyed the
finding, and one handed a contract document as *reference* returned three proposals editing it. Three
habits every angle needs, because they are where confident reviewers are wrong. **Resolving a citation
is not verifying it** -- a path that exists does not check what the prose says about it; open it.
**Re-derive, do not re-read** -- redo the sum, count the set, list the callers. **Read the prose around a
block before proposing a remedy**: one finding, "this function sums two different units", was true, and
the line above it explained why -- its TODO reopened a settled call.

### Currency -- does this describe the program as it is now? (~45% of findings)

Git holds what the code used to be; a comment narrating its own history does git's job badly. Flag dated
rulings, review-round labels ("fix round 2", "finding B4", "Part B"), quotations and attributed rulings,
"this used to...", "X was changed to Y", "no longer", "previously" -- and the sharpest form,
**obituaries**: a name, file, test or flag that no longer exists anywhere. A reader greps, finds
nothing, and reads it as *their* mistake. ! **Grep the STEM, not the identifier**, because prose does
not obey identifier spelling: a dead `foo_bar` is written `foo-bar`, `foo bar`, `FooBar`, or "the
barrer". Measured on a real deletion, the identifier grep found ten mentions, all correctly dated
tombstones, and **missed an eleventh written with a hyphen -- the only present-tense claim about the dead
path in the set.** A clean grep reads as a clean file.

**Every number is a citation**, unverifiable unless it names the **set it counts over** -- so re-derive
the SET first. Measured misses: "the 37 mobility ids" (35), "all 1626 other tests green" (3041); a pass
correcting a false number produced a differently false one by re-counting the wrong population. ! **The
acquittal this angle owes: a dead name that is the SUBJECT of the record, not a pointer.** *"The X
column was removed; do not re-add it"* is the only surviving reason not to -- an obituary sends a reader
looking, that tells them not to go. Same for a date in a version string or a sample size.

### Functionality -- does the commentary match what the function is for? (~30%)

Read name, signature and docstring, then the body. Flag disagreement: a return shape the code no longer
returns, a `Returns:` naming fields in the wrong order, an `Args:` entry for a parameter that is gone, a
documented exception nothing raises, a summary saying "Yield" over a function that returns. The
**summary line** drifts silently, because changing a return type does not change the sentence describing
it. **Coverage claims are the class that licenses deletions, and are disproportionately wrong** --
"pinned by X", "guarded by Y", "the only call site", "nothing asserts this". Each authorises the next
person to delete something, so grep the cited name every time and check the cited guard CAN fail; a real
guard has been dropped on a pointer to a test never written. ! **A citation nothing can parse is worse
than a parseable wrong one** -- a brace expansion, a bare `test_thing`, a line number (`x.py:201`): the
parseable one is fixed next run, the unparseable one accumulates and its terseness reads as authority.

**A universal is a CHECKLIST, not a sentence** -- "every X does Y", "always", "never", "all N". Tick the
Xs off: one review's largest hole was a module-level "LOUD, NEVER SILENT" false for two of seven paths,
passed by every angle because each path made it look true.
**Reachability lives here, not in a fifth angle:** does anything still READ the thing the prose
describes? A constant with zero readers whose comment states an invariant, an exemption from a rule
retired months ago, a hazard justifying live code nothing can still trigger. Not stale -- furniture.

**Then read the body's comments as one sequence.** Individually each may be true; end to end they are
the most honest description of the function in the file. A run of *"now I need to...", "oh I should...",
"this other thing should also..."* is a to-do list left in the body: those comments **sequence** instead
of **constrain**, so they go nowhere when their line moves. Say which each step is -- **(A)** not needed
for the function to be the function, or **(B)** real work at the wrong level -- and ! **report the
mismatch, do not resolve it**: the docstring grows until it tells the truth, at which point the *name*
is wrong, or the function shrinks to what it is called. Naming that fork is the deliverable.

### Locality -- does this comment belong to the line it sits on?

A comment points DOWN for a block on its own lines, AT the declaration for a trailing one. The finding
is a comment about something **else**: a block whose later half turns back to narrate what came before,
a rule at the top of a class that really constrains two literals two hundred lines down, a `#` run
between two declarations that annotates no statement at all. **Direction words** -- "above", "below",
"the next function" -- break on any reorder, and the fix is to delete the word, not correct it. Second
test: **if this code changed, would the comment become wrong -- and would anyone notice?** Prose that
would quietly survive a change to the code it describes is not local to it; flag the inverse too, a line
carrying a non-obvious constraint with no comment. **Refactoring drift** is the biggest yield here: when
code moves, its commentary stays behind describing what left, or follows and goes false.

### Module coherence -- do the comments say this is one module?

Read only the module docstring, section banners and top-of-file commentary. Flag prose announcing two or
three subjects, banners reading like chapter breaks rather than parts of one argument, a docstring
enumerating unrelated responsibilities to be accurate or describing a fraction of its module, and a
section named for the **occasion** that produced it -- nobody can apply "it was in that batch" as a
membership rule. **Does the file contradict its own headline?** Read that claim LAST, against everything
under it; an overclaim is written when the file is small and never revisited. Also flag **one rule
explained in several modules**: it has no owning function, so every site re-explains the whole -- usually
the real cause of a long comment above a short expression.

## Phase 2 -- one verdict per block

Wait for all four, dedup blocks, then rule on each survivor. **Is it CHECKABLE?** Could a reader confirm
or refute it from the code as it stands, without archaeology? **Is it NECESSARY?** Would someone
changing this code make a **worse decision** without it -- not "is it interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader verifies and needs | **drop** -- the code says it |
| **not checkable** | **move** -- real rationale, unverifiable in place | **drop** -- history |

! **Truth is not one of the questions, and that is the point.** *"Moved here from `x.validate` when that
module was deleted"* is true; the reader needs the check to live **here**, not its travel history, and
accuracy is why it was never deleted rather than a reason to keep it. **When comment and code DO
disagree, the verdict turns on which kind of claim it is.** A **description** that disagrees is wrong
prose -> `correct` it, or `drop`. A **prohibition** that disagrees means the CODE broke the rule -> file
it; the code moves, not the prose. **`correct` is the fifth verdict and it exists so `drop` is never the
only exit**: a block stating a real constraint with one wrong number, one dead name or one inverted
clause must be FIXED, because cutting it loses the constraint to save the error. Propose the text.

* **A description written as a negation is a FORM defect on its own.** You cannot check "X is not the
case" against the code -- you must establish what it *does* do and argue backwards. Rewrite it positive:
*"! NOT the kernel call site"* -> *"asserts on `session_set_equivalents` directly"*. A **prohibition**
may stay negative. Measured: a compressing pass took negation from 17% of removed lines to **22%**.

**Rule on sentences, not on blocks** -- a container of six sentences can hold six verdicts. ! **A single
`keep` sentence launders every sentence around it**: ruling `keep` because *part* of a block is
load-bearing is the signal to descend a level, and a block's most defensible sentence is usually why the
whole block survived this long. **Then ask whether what survives is longer than it needs to be** ->
**compact**, what you do to a `keep` or a `move`'s remainder, not a verdict of its own. For **move**,
name the destination, and ! **it gets the WHOLE block, including the half that stays in the code** -- a
doc holding only what was discarded reads as a deletion list, not a record.

### `#` and `"""` are governed differently

**A `#` comment is governed by LENGTH** -- it interrupts code, so its cost is the screen space between
the lines either side of it, and a run is bounded by CODE, not blank lines. Work markers (`TODO`,
`FIXME`, `HACK`, `XXX`, `BUG`) point *outward* at work not done; where the repo exempts them they
neither spend the budget nor split a run, so never call a block over-cap for a marker line. **A
docstring is governed by FORMAT, not length**, so never propose `compact` on one merely for running
long. ! **But this is where a burn-down silently undoes itself**: prose evicted from a `#` run relocates
into a docstring and nothing notices. A docstring **body carrying a date, a quotation, an attributed
ruling, a review-round or finding label, a "considered and rejected", a rationale paragraph, a
measurement story, or a claim about callers or coverage is a finding at ANY length** -- a FORMAT failure,
not a length one, and its verdict is `move`. * Conversely, **move a hand-worked derivation INTO the
docstring rather than compacting it**: one moved that way took a file from 10 excess lines to 0.

! **The tail is not like the head.** Near a cap most remaining blocks are one line over -- of one
burn-down's last 48, **27 were over by exactly one**. Cut the least-checkable line; do NOT rewrite a
block already true, current and on-subject. ! And **a guarded tree looking clean is no sample of
unguarded code**: one entering scope held 11 dangling citations against 0 in the long-guarded tree.

## Phase 3 -- present. Always.

**This skill never edits. It ends with the verdict list**, grouped by verdict, most consequential first,
with proposed replacement text inline for every `compact` and every `correct`; then stop. ! **Even when
the human names the edit** -- "cap them", "fix these", "go do it" -- the deliverable is the report:
*"Report only, per the skill -- say the word and I'll apply the verdicts you accept."* This review's
whole value is the human's disagreement with it, and **an edit applied is a verdict never ruled on**:
before this rule, two runs on near-identical prompts split, one returning a report and one an 846-line
diff.

Hand these rails to the pass that DOES apply the verdicts, since it usually runs without this skill
loaded. A block is bounded by **CODE, not blank lines**, or a cap is evadable as 6+3. **Change no line
of code, no docstring's meaning and no string literal -- and prove it** by diffing every non-comment line
against the pre-edit file on every commit. **Extract before you cut** on a `move` and do not sever a
sentence; the other order lost the text three times. **Match exactly one occurrence or refuse the whole
file**, and **re-read what you wrote** -- a pass that cut seven obituaries wrote seven new.

`/simplify` reviews code structure and applies what it finds; `/code-review` hunts correctness bugs.
This one reviews prose and **only ever proposes** -- a defect noticed anyway is **named and left**.
**Every example above is invented or anonymised. Keep it that way**: quoting a real comment teaches
recognition of *that comment* rather than the shape, and it rots into its own obituary.
