---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles --
  locality, currency, functionality, module coherence -- using four parallel subagents, and
  return each finding with a proposed verdict (drop / move / compact / keep) for the human to
  rule on. Use this whenever comments or documentation are the subject: after finishing a task
  that added or edited commentary, when a file's comments have drifted from what the code now
  does, when someone says a comment is too long or out of date or "isn't this history", when
  reviewing a diff specifically for its prose rather than its logic, before a docs or comment
  burn-down, or when asked to check whether a module still reads as one module. Trigger on
  phrasings that never say "comment review" -- "these comments are getting out of hand", "does
  this docstring still match", "is this comment still true", "clean up the narration in this
  file", "why does this file need so much explaining" all mean run this. It is NOT /simplify
  (which reviews code structure and applies its fixes) and NOT /code-review (which hunts
  correctness bugs) -- this one ONLY EVER PROPOSES and never edits anything, not code and not
  even the comments it rules on, because an edit applied is a verdict the human never got to
  rule on. Run it even when the request sounds like an instruction to cut ("cap these", "clean
  this up"): the deliverable is still the verdict list, and applying is a separate step. It is
  explicitly not a reviewer's job to judge whether the code works: code concerns get raised in
  a line and left, while every verdict returned is a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` -> sweep -> 4 reviewers in parallel -> a verdict per finding ->
you decide -> apply.

## The subject is the prose, not the program

**It is not a reviewer's job to decide whether the code works.** Every verdict you return is a
verdict on a comment. You will still notice code problems; say so in a separate section, one
line each. **Raise a concern, do not open an investigation**, and never let a code finding
acquire a `drop`/`move`/`compact`/`keep` verdict -- those four words apply only to prose. The
best findings here look like code findings and are not: *"the comment says it reads one field;
it reads three"* is checkable against the file and yours to rule on, while *"it should not read
three fields"* is a design change belonging to `/simplify` or the owner -- **name it and leave.**
! **A reviewer straying into correctness is where this skill's worst output comes from,
measured**: in two eval rounds a reviewer read `except ValueError, TypeError:` and reported the
file "cannot compile" -- a claim about the *program*, volunteered while reviewing *prose*, and
wrong (PEP 758 permits it in Python 3.14). Once, four agreeing reviewers shipped it. Make such a
claim anyway and you owe it an `ast.parse` first.

* **The governing law, and it beats every other search heuristic: LOOK WHERE NOTHING ASSERTS.**
Measured over a whole-tree burn-down, every false statement found sat where no test, type or
lint rule could reach -- not the oldest prose, not the longest, not the furthest from its code.
False clauses sat *inside* blocks whose other sentences were true, in the same voice, under the
same marker; one split **mid-sentence**, the clause before the comma asserted by nothing and
false, the clause after it asserted by the body and true. A green suite is no evidence about
prose: a comment beside a deleted thing is green *because* the thing is gone.

## Arguments

**`cap`** -- an integer, optional: the most lines one comment block may run, passed to every
reviewer. **This skill has no cap of its own** and must not invent one; with no cap, review by
judgement and **report the longest block found**. **`target`** -- a path; defaults to the diff.

## Phase 0 -- scope, then sweep

Run `git diff --name-only @{upstream}...HEAD` (or `main...HEAD`, or `HEAD~1`); if the tree is
dirty or the range is empty, add `git diff --name-only HEAD`. That gives a **list of files**.
Review **every comment and docstring in those files, not just the changed lines** -- the one
place this skill deliberately departs from `/simplify`. Comment debt is cumulative and mostly
pre-existing: the 54-line block that has sat above a four-line expression for months is the
finding worth having, and a diff-scoped reviewer never sees it. The diff says which files are
live in the human's head; it must not bound what gets read inside them. Skip files with no
commentary worth reviewing and say which, then **paste the sweep's report into all four prompts**:

```
python .claude/skills/comment-review/sweep.py --cap N --width N --root . <files>
```

It locates every prose block and flags what needs a symbol table and a filesystem rather than
judgement: over-cap runs, over-wide lines, dates, history markers, review-round labels,
quotations, counted claims, coverage claims, dangling paths, line-number citations, ghost
symbols, `Args:` entries for parameters that do not exist, documented exceptions nothing raises,
summary lines that disagree with the body. Obituaries alone were **19% of findings** (18 of 96)
in two never-guarded trees. ! **Nothing it emits is a verdict** -- `ghost` and `counted` are
CANDIDATES for Phase 2, the rest facts about the filesystem -- and it is a floor, not a ceiling:
it cannot see an inverted meaning, a claim the code contradicts, or an ownerless rule.

## Phase 1 -- four reviewers, in parallel

Launch **four subagents in a single message**, each given the file list, the sweep report, the
`cap` if there is one, and one angle. Each returns findings with `file`, `line`, a one-line
`summary`, and the concrete cost. ! **Reviewers are READ-ONLY -- say so explicitly in the
prompt.** Four agents editing one file is a race whose loser's edits vanish silently, and a
reviewer that fixes what it finds has destroyed the finding. **Name two lists in every prompt:
the files UNDER REVIEW (a proposal may target these) and the files given as REFERENCE (never a
proposal target).** A reviewer handed a skill document as a contract to check a script against
reasonably proposed edits to it, and they were applied -- a false claim landing in a doc, from
the pass that removes false claims.

**Every finding is `CONFIRMED` (the reviewer read both the prose and the code or test that
settles it, and quotes the line) or `SUSPECTED`.** On a real pass 196 of 202 came back CONFIRMED
and one reviewer withdrew two candidates rather than pad the list, while a finding filed without
reading the function cost a withdrawn TODO. **Before reporting a defect, read the prose
immediately around it**: a deliberate design usually says so directly above itself. **If the
repo publishes its own cap, use it, say where you got it, and read that guard for how it
*measures*, not just its number.** Overlap between angles is signal: a finding all four report
is almost always real, and a second angle is the only check on the orchestrator's own errors.

### Locality -- does this comment belong to the line it sits on?

A comment is a claim about the code beside it. Flag one really about something else: a rule at
the top of a class that constrains two integer literals 200 lines down, a note about a schedule
that stops being true the moment the schedule moves, a block whose later half turns back to
narrate what came before -- usually the seam where two notes were merged, or where one was split
and half ended up facing backwards. **A comment points at the code it is attached to** -- DOWN
for a block on its own lines, AT the declaration for a trailing one, so a field comment
annotating the thing on its own line is exactly where it belongs. Second test, for whatever
survives the first: **if this code changed, would the comment become wrong -- and would
anyone notice?** A comment that would quietly survive a change to the code it claims to describe
is not local to it. Flag the inverse too: a line carrying a non-obvious constraint with no
comment at all, where getting it wrong is silent. And **refactoring drift** belongs here, since
no length rule sees it: when code moves, its commentary stays behind describing what left, or
follows and stops being true in its new home.

### Currency -- does this describe the program as it is now?

Git holds what the code used to be and why it changed; a comment narrating its own history is
doing git's job badly and costs the reader every time. Flag dated rulings, review-round labels
("fix round 2", "finding B4", "task 8.6", "v3"), "this used to...", "the old X", "before the fix",
and -- the sharpest form -- **obituaries**: a comment naming a symbol, file, test or flag that no
longer exists, worse than noise because the reader greps, finds nothing, and reads that as
*their* mistake. Obituaries are objectively checkable, so **check them** -- the sweep does the
first pass, you triage. Same for cited paths and tests: "pinned by tests/x.py" is *licensing
future edits* on that evidence, and a real guard has been deleted on the strength of a pointer
to a test that was never written.

! **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead
`foo_bar` gets written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Measured, an identifier
grep found ten mentions, all correctly dated tombstones, and **missed an eleventh written with a
hyphen -- the only present-tense claim about the dead path in the set.** The failure is
self-concealing; a clean grep reads as a clean file. ! **And a claim written in a form your
checker cannot parse is worse than the same claim written parseably and wrong** -- the parseable
one is caught next run, while the unparseable one accumulates (a brace expansion, a bare test
name, a `file.py:214` line number) and its terseness reads as confidence. **Unverifiable and
verified-correct look identical**, so report the form as well as the claim. ! And **a guarded
tree is clean because it is guarded, which is no sample of what unguarded code does**: as two
trees entered scope, 11 dangling citations against 0 in the tree the check had read all along.

### Functionality -- does the commentary match what the function is for?

Read the name, the signature, the docstring, then the body. Flag where they disagree: a
docstring describing a return shape the code no longer returns, a `Returns:` naming fields in
the wrong order, an `Args:` entry for a parameter that does not exist, a documented exception
nothing raises. The **summary line** is worth checking every time -- it is the only part most
readers see, and it drifts silently, because changing a return type does not change the sentence
describing it. **Then ask whether anything READS the thing the prose describes.** Nothing else
asks this, and the quietest findings are here: a constant with zero readers repo-wide whose
comment states an invariant and says the enforcing test was deleted; an exemption from a rule
retired months ago; a function documented as called by a module whose only caller is a test; a
hazard justifying live code that nothing can still trigger. Prose about something unreachable is
not stale -- it is furniture. Then the harder version: **is the comment describing logic that
wants to be a function?** A long comment above a short expression is the classic tell; report it
as a finding about the *code shape*, with the comment as evidence.

**Now read the body's comments as one sequence, in order.** Individually each may be accurate;
end to end they narrate what the function *actually does*, more honestly than its docstring:

```python
def build_foo_bar(*args):
    """Building a FooBar"""
    created = FooBar(*args)
    # oh I should set this other thing up
    global set_foobar
    set_foobar = FooBar
    # This other thing should also happen
    send_foo_bar_to_other(created)
    # I should also send back those extra args
    return FooBar, ["..."]
```

Every comment is true. Together they say the function builds, publishes a global, performs I/O,
and returns a second value the name never hinted at. **The tell is grammatical and cheap to
spot: a comment that sequences instead of constrains.** *"Now I need to...", "oh I should...", "then
we..."* narrate the author's path. A comment earning its place says why a line must be the way it
is and goes wrong if that line moves; a sequencing comment goes nowhere when its line moves,
because it was never about the line. Say which of two each step is:
**(A) not needed for the function to be the function** -- remove the global and the send and it
still builds a `FooBar`; or **(B) at the wrong level**, real work belonging to the caller.
! **Report the mismatch; do not resolve it**:
the finding is *"the running commentary describes five jobs, the name and docstring describe
one"*, which has two honest resolutions -- the docstring grows until it tells the truth, at which
point the **name** is what is wrong, or the function shrinks to what it is called. Naming that
fork *is* the deliverable. Last: **narration of intent hides a mismatch that narration of effect
would expose** -- that final comment sits above a return of `FooBar`, the class, not `created`,
and a comment saying what the author meant reads as confirmation, so the eye stops there.

### Module coherence -- do the comments say this is one module?

Read only the module docstring, the section banners and the top-of-file commentary. Do they
describe one thing? Flag prose announcing two or three subjects, banners reading like chapter
breaks, a docstring enumerating unrelated responsibilities to be accurate, and any file or
section named for the **occasion** that produced it (a review round, a task number) -- a
membership rule no future author can apply. Also flag **the same rule
explained in several modules**: the commonest structural finding in a long-commented codebase,
and *why* the comments got long -- nobody could state the rule once, because no function held it,
so every site that performs part of it re-explains the whole. Measured, one rule appeared in 8
of 9 files under seven names with no owner. Report it with the comment as evidence.

## Phase 2 -- one verdict per finding

Wait for all four, dedup findings pointing at the same block, then rule on each survivor. **Is
it CHECKABLE?** Could a reader confirm or refute it from the code as it stands, without
archaeology? **Is it NECESSARY?** Would someone changing this code make a **worse decision**
without it -- not "is it interesting", not "is it true", but would they get it wrong?

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader verifies | **drop** -- it narrates the code |
| **not checkable** | **move** -- real rationale, unverifiable here | **drop** -- history |

! **Truth is not one of the questions, and that is the point.** *"Moved here from `x.validate`
when that module was deleted"* is true, and the reader needs to know the check lives **here** --
not where it used to. Uncheckable and unnecessary, so it goes: history that is *correct* reads
as *earning its place* and does not. **Rule on sentences, not on blocks** -- a container of six
sentences can hold six verdicts, and the common shape is a live constraint sitting beside the
story of where it came from. ! **A single `keep` sentence launders every sentence around it.**
Ruling `keep` on a block because *part* of it is load-bearing is the signal to descend a level:
a block's most defensible sentence is usually why the whole block survived this long, so this is
the default outcome rather than a rare one.

**Split description from prohibition -- a comment that disagrees with its code has two fixes.**

| the comment and the code disagree, and the comment is... | what moves |
|---|---|
| a **description** | the comment is wrong -> drop or fix it |
| a **prohibition** | the code broke the rule -> the CODE moves; file it, keep the comment |

! **And a DESCRIPTION written as a negation cannot be checked at all.** You cannot verify "X is
not the case" against code; you must establish what it *does* do and argue backwards. Rewrite it
positively -- *"! NOT the kernel call site"* -> *"asserts on `session_set_equivalents` directly"*.
A **prohibition** may stay negative: *"never call `soft_trim` here, or the expectation moves
with the code"* has no positive form that keeps its force. ! Measured on a pass trying to fix
exactly this: removed prose was 17% negated, what was written back was **22%**. Compressing
CONCENTRATES negations unless you resolve them deliberately. And **a counted claim must name the
POPULATION it counts over, or it is unverifiable** -- re-derive the SET before the number: a
correction shipped as MEASURED once had both halves of its population wrong, and was off by 5x.

**Then, for anything that survives, ask whether it is longer than it needs to be** -> **compact**,
not a fifth verdict but what you do to a `keep`, or to the remainder a `move` leaves. Propose the
replacement text; keep the constraint and what breaks without it; prefer *"X must be Y because Z
breaks otherwise"* over *"this used to be W."* ! Check what SURVIVED, not what went -- deleting
the constraint and keeping the narration passes any cap and makes the comment worse. For
**move**, name the destination, and ! it gets the **whole block, including the part that stays
in the code**: a doc holding only the discarded half is a list of deletions, not a record.

### What must be KEPT

A spec that only says what to cut deletes the load-bearing half. Each of these survived a pass:

- **Hand-worked derivations** -- the arithmetic that makes an assertion a check rather than an
  echo of the implementation. * **When one is over cap, MOVE IT INTO THE DOCSTRING before
  compacting it**: a `#` block is capped by LENGTH because it interrupts code, while a docstring
  sits at a boundary and is governed by FORMAT. One 16-line derivation moved that way took a
  file from 10 excess lines to 0 **with every digit intact**. Try this first.
- **Premise guards**, and **the discriminator that scopes a claim** without which it is over-read.
- **Why a fixture is shaped oddly**, written ON the element rather than above the block: a field
  comment forms no run at all, so the cap stops deciding how much a fixture may explain.
  Likewise **deliberate freezes** ("hand-copied and FROZEN; re-syncing destroys the isolation")
  and **a comment naming its own expiry condition** ("if X is true now, delete this and close
  Y") -- the rare comment about the future that earns its place.
- **A warning where NOTHING GOES RED.** ! Only there: a warning against a move that *does* break
  a test is a time-saver, not a guard, so cut it to a pointer. Mutant-check both ways, and do not
  promote "warnings" to a third category -- that is the laundering failure above, renamed.
- **A long docstring, for being long** -- propose `compact` only when its body carries something
  that fails an angle: history, a quotation, a claim about callers or coverage.

**And the tail is not like the head.** Late in a burn-down the blocks are one line over, not ten:
of a final 48, **27 were exactly one line over cap**, and such a block is by construction mostly
correct. **Cut the single least checkable line; do NOT rewrite a block already true, current and
on-subject.** Do not pad the list: **keep** is a real verdict, and a review returning mostly
`keep` is a good outcome.

## Phase 3 -- present. Always.

**This skill never edits. It ends with the verdict list.** Report grouped by verdict, most
consequential first, with the proposed replacement inline for every `compact`. Then stop.
! **Even when the human names the edit** -- "cap them", "fix these", "go do it" -- the deliverable
is the report: *"Report only, per the skill -- say the word and I'll apply the verdicts you
accept."* This review's whole value is the human's disagreement with it, and **an edit applied is
a verdict never ruled on**. Before this rule, two runs on near-identical prompts split, one
returning a report and the other an 846-line diff.

**Rails to hand the pass that applies the accepted verdicts**, since it usually runs without this
skill loaded: a comment block is bounded by **CODE, not blank lines**, or a cap is evadable as
6+3; write a `move`'s destination verbatim **before** removing the source; apply with **`count ==
1` or refuse the whole file**, `old` built programmatically rather than transcribed; check each
replacement's **width** as well as its line count, and **preserve the file's own line ending**
from the raw bytes; **change no code, no string literal and no
docstring's meaning**, proved by diffing every non-comment line against the pre-edit file, then
by the diff's SHAPE, where a line-ending flip shows up and no test does; and **run the sweep over
your own replacements**, because a pass that cut seven obituaries wrote seven new ones.

`/simplify` reviews code structure and applies what it finds; `/code-review` hunts correctness
bugs; this one reviews prose and **only ever proposes**. **Every example above is invented. Keep
it that way** -- quoting a real comment teaches recognition of *that comment* rather than the
shape, and it rots into an obituary the day someone acts on the finding.
