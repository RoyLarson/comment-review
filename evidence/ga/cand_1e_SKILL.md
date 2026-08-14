---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched against an explicit
  checklist of defect classes — ghost names, dangling citations, dated history, stale counts,
  coverage claims, descriptions the code contradicts, misplaced rules, over-length blocks — and
  return every finding with a proposed verdict (drop / move / compact / keep) for the human to
  rule on. Use this whenever comments or documentation are the subject: after finishing a task
  that added or edited commentary, when a file's comments have drifted from what the code now
  does, when someone says a comment is too long or out of date or "isn't this history", when
  reviewing a diff specifically for its prose rather than its logic, before a docs or comment
  burn-down, or when asked to check whether a module still reads as one module. Trigger on
  phrasings that never say "comment review" — "these comments are getting out of hand", "does
  this docstring still match", "is this comment still true", "clean up the narration in this
  file", "why does this file need so much explaining" all mean run this. It is NOT /simplify
  (which reviews code structure and applies its fixes) and NOT /code-review (which hunts
  correctness bugs) — this one ONLY EVER PROPOSES and never edits anything, not code and not
  even the comments it rules on, because an edit applied is a verdict the human never got to
  rule on. Run it even when the request sounds like an instruction to cut ("cap these", "clean
  this up"): the deliverable is still the verdict list, and applying is a separate step. It is
  explicitly not a reviewer's job to judge whether the code works: code concerns get raised in
  a line and left, while every verdict returned is a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` → census the prose blocks → walk each down **one checklist** → rule.

## The subject is the prose, not the program

**It is not a reviewer's job to decide whether the code works.** Every verdict you return is a
verdict on a comment. You will still notice code problems: say so in a separate section, one
line each, and move on. **Raise a concern, do not open an investigation** — and never give a
code finding a `drop`/`move`/`compact`/`keep` verdict.

| This is a COMMENT finding | This is a CODE finding |
|---|---|
| the comment says it reads one field; it reads three | it should not read three |
| the comment names a symbol that no longer exists | the symbol should be restored |
| the comment claims callers `grep` cannot find | the function is dead, delete it |

⚠ Measured: in two eval rounds a reviewer read `except ValueError, TypeError:` and reported the
file "cannot compile" — a claim about the *program*, volunteered while reviewing *prose*, and
wrong. If a claim is about whether the code RUNS, it is not yours; make it anyway and you owe it
a `python -c` first.

## Why one checklist and not several angles

Angles overlap and leave gaps between them, and a reviewer holding one lens reads for what that
lens sees. The checklist inverts it: **you read each block once, and the block is walked past
every class**, so coverage is a property of the list rather than of how many readers you
launched. Split across subagents by **file** if you like — never by class; each gets it all.

## Arguments

- **`cap`** — integer, optional: the most lines one `#` block may run. This skill has no cap of
  its own and must not invent one. A cap the repo publishes (a lint config, a hygiene test)
  wins; read how it *measures*, not just its number. With none, judge — and report the longest.
- **`target`** — a path, optional; defaults to the files in the diff (Phase 0).

## Phase 0 — Scope, then census

Scope: `git diff --name-only @{upstream}...HEAD`, or `<default-branch>...HEAD`, or `HEAD~1`;
add `git diff --name-only HEAD` if the tree is dirty. ⚠ Check which of those returned something:
an empty range and a one-commit range both *succeed* and quietly review less than you meant.
Review **all the prose in those files, not just the changed lines** — comment debt is cumulative
and mostly pre-existing, and a diff-scoped reader never sees the block that has sat above a
four-line expression for months.

Then **enumerate the blocks before reading them**, so "every block" is a list and not a feeling:

```python
"""Print every prose block (a `#` run or a docstring) in each file named on argv."""

import ast, sys
from pathlib import Path

DEFS = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def prose_lines(text):
    out = {i for i, s in enumerate(text.splitlines(), 1) if s.strip().startswith("#")}
    try:
        tree = ast.parse(text)
    except SyntaxError, ValueError:
        return out  # not Python, or unparseable: the `#` runs still stand
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, DEFS) and body and isinstance(body[0], ast.Expr):
            head = body[0]
            if isinstance(getattr(head.value, "value", None), str):
                out.update(range(head.lineno, (head.end_lineno or head.lineno) + 1))
    return out


for arg in sys.argv[1:]:
    try:
        text = Path(arg).read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    runs = []
    for n in sorted(prose_lines(text)):
        if runs and n - runs[-1][-1] <= 2:  # a 2-line gap still reads as one block
            runs[-1].append(n)
        else:
            runs.append([n])
    for r in runs:
        print(f"{arg}:{r[0]}-{r[-1]}\t{len(r)} lines")
```

Keep the list and **tick blocks off**. The census is the report's denominator: *"48 blocks, 31
flagged"* is an answerable claim; *"here are some findings"* is not.

## Phase 1 — The checklist

For **each block in the census**, walk classes 1–31. Report **one finding per offending
sentence**, not one per block — a container of six sentences can hold six verdicts. Give each
finding the line of *that sentence*, **not the first line of the block**, which for a long
docstring is often thirty lines above the defect. Each entry below is a name, `Ask:` the
detection question, and `Stop:` when not to flag.

### A. Currency — does this describe the program as it is now?

1. **Ghost name.** Ask: does every symbol, file, flag or constant named here still exist?
   Stop: it resolves, or the dead name is the *subject* of a deliberate record, not a pointer.
2. **Dangling citation.** Ask: does the cited test / path / doc resolve today?
   Stop: it resolves. A `file.py:NN` citation never survives a refactor — flag on sight.
3. **Dated ruling or review label.** Ask: a date, a finding id, a wave or round number?
   Stop: the date is part of a data format or a runnable command, not the comment's provenance.
4. **History narration.** Ask: "used to", "was changed", "before the fix", "we tried"?
   Stop: it names an expiry condition for the code itself, which is about the future.
5. **Retired mechanism cited as live.** Ask: is the gate/constant/flag it describes still read?
   Stop: `grep` finds a real reader — including config, docs, and string literals.
6. **Retracted fact.** Ask: has the source of truth for this claim since withdrawn it?
   Stop: you opened the source and it still says this.
7. **Stale count.** Ask: is there a number here, and does re-deriving it give that number?
   Stop: you re-derived it and it holds. If nothing asserts it, the verdict is *delete*, not fix.
8. **Quotation or attribution.** Ask: does it quote a person or record who decided?
   Stop: never — a name and a quotation are provenance, and provenance lives in the history.
9. **Drifted copy.** Ask: is this rule stated elsewhere too, and do the copies still agree?
   Stop: this is the owning statement, or the others cite it instead of restating it.

### B. Truth — does the code do what the prose says?

10. **Contradicted description.** Ask: read the body — does it do what this claims? Stop: it
    does. ⚠ If it is a **prohibition**, a disagreement means the CODE broke the rule — file that.
11. **Summary line drift.** Ask: does the first line still name what the thing does and returns?
    Stop: it does. It is the only part most readers see — check it every time.
12. **Signature drift.** Ask: does every `Args:`/`Returns:`/`Raises:` entry exist, in that shape?
    Stop: it does, and it says something the signature does not.
13. **Name / docstring / body disagreement.** Ask: do the three describe one job?
    Stop: they do. Renaming is a CODE change — report the fork, do not choose it.
14. **Coverage claim — the dangerous cell.** Ask: "guarded by", "pinned by", "asserted in" —
    does that guard exist, and would it fail if the claim were false? Stop: you opened it.
15. **Partial universal.** Ask: "every X does Y" — enumerate the Xs and check each one.
    Stop: you enumerated and all hold. Never keep, compact or reword one without enumerating.
16. **Count with no population.** Ask: does the number name the set it counts over, and could a
    stranger re-derive it? Stop: it names the set and the query or the frozen input.
17. **Negated description.** Ask: written as `NOT X` where a positive statement exists?
    Stop: it is a prohibition for the next author, which may be negative.
18. **Inverted direction or qualifier.** Ask: does the stated direction, mutation, scope word or
    boundary (`<` vs `<=`) match the operator in the body? Stop: it matches.
19. **Prose vs a live string.** Ask: does a `warn`/`log`/`assert` message nearby still say what
    this comment now denies? Stop: both name the same reason.

### C. Placement — is this prose where its subject is?

20. **Non-local rule.** Ask: does it constrain the line it sits on, or something else?
    Stop: it annotates its own declaration — a field comment faces its field, not backwards.
21. **Backwards-facing half.** Ask: does the block's later half narrate what came *before* it?
    Stop: it introduces the consecutive declarations underneath it.
22. **Two subjects welded together.** Ask: is a live constraint sharing a paragraph with the
    story of where it came from? Stop: one subject. This is the ordinary case, not a rare one.
23. **Module docstring vs module.** Ask: does the top-of-file prose describe this whole file and
    only this file? Stop: it does. Two announced subjects is a finding about the module.
24. **Stranded or severed run.** Ask: does the run start mid-clause, sit after an unconditional
    `return`, or belong to the declaration four lines down? Stop: its subject is the next line.
25. **Missing comment.** Ask: is there a non-obvious constraint here that nothing states, where
    getting it wrong is silent? Stop: the code says it. Absence is a placement finding.
26. **Ownerless rule.** Ask: is this re-explained at several sites because no function holds it?
    Stop: one site owns it and the rest point there. Report as code shape; do not extract it.

### D. Form — what the block is, not what it says

27. **Over-cap `#` run.** Ask: longer than the cap, counted by CODE and not by blank lines?
    Stop: at or under. Free markers (`TODO`, `FIXME`, `HACK`, `XXX`, `BUG`) do not count.
28. **Over-wide line.** Ask: any line past the repo's configured width (read it, never assume)?
    Stop: none — formatters never reflow comments, so a line cap is evadable by widening.
29. **Rationale paragraph in a docstring.** Ask: is the body explaining *why the design changed*
    rather than what the thing does? Stop: it documents behaviour, arguments or a constraint.
    ⚠ A docstring is governed by FORMAT, not length — never flag one just for being long.
30. **History relocated, not removed.** Ask: did narrative move from a `#` run into a docstring
    where no cap reaches it? Stop: what moved is a derivation or a live constraint.
31. **Derivation stranded in a `#` run.** Ask: is hand-worked arithmetic interrupting code?
    Stop: it is already in the docstring. A derivation is KEPT — moved, never compressed.

## Calibration — how hard to press

- **A block failing one class usually fails three.** Do not stop at the first: the verdicts
  differ (a stale count is `drop`, a mislocated rule is `move`) and so do the lines. Over ~15
  lines, report the offending sentences separately — one finding pinned to the top of a forty-line
  docstring points at the one paragraph that was probably fine.
- **Defects cluster in blocks somebody already edited** — a block cut in half with the falsehood
  in the surviving half; obituaries cleared from a docstring and left four hundred lines down;
  three of four siblings fixed. Find one, then sweep that whole class in that file.
- **A tail is not a head.** Where a cap already holds and blocks sit one line over, cut the
  single least-checkable line. **Do not re-author a block that is already true, current and
  on-subject** — a +1 run is by construction mostly correct.
- **Prose no guard has ever measured is defective at a high rate.** The first tree scanned held
  eleven dangling citations against **zero** in the guarded tree — same repo, same rule. A pass
  returning ten findings over three thousand lines of prose has not looked.
- **Read the adjacent prose first.** A deliberate design usually says so directly above itself:
  a function reported for summing two units had the reason one line up, and the finding reopened
  a decision closed six weeks earlier. **Do not pad** — `keep` is a real verdict.

⚠ **Grep the STEM, not the identifier** (classes 1, 5, 9). Prose does not obey identifier
spelling: a dead `foo_bar` gets written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Search a
loose stem and triage. Measured: an identifier grep found ten mentions, all correctly dated
tombstones, and **missed an eleventh written with a hyphen — the only present-tense claim about
the dead path in the set.** A clean grep reads exactly like a clean file.

## What must be KEPT — a checklist that only cuts deletes the load-bearing half

- **Hand-worked derivations** — the arithmetic that stops an assertion being an echo. Over cap?
  Move it into the docstring (class 31); never compress it.
- **Premise guards**, **the discriminator that scopes a claim**, and **why a fixture or constant
  is shaped oddly** written ON the element it explains.
- **A deliberate freeze** — prose whose absence invites a "helpful" re-sync that breaks it.
- **A warning where NOTHING GOES RED**, and ⚠ only there: mutant-check it. A warning against a
  move the suite already refuses is a time-saver, not a guard, and gets cut to a pointer.
- **A comment naming its own expiry condition**, and **a live citation in the wrong FORM** —
  reformat that one; deleting it destroys real coverage.

## Phase 2 — One verdict per finding

Dedup findings pointing at the same sentence, then rule on each survivor. **Is it CHECKABLE?**
Could a reader confirm or refute it from the code as it stands, without archaeology? **Is it
NECESSARY?** Would someone changing this code make a **worse decision** without it — not "is it
interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** — a constraint the reader needs | **drop** — the code already says it |
| **not checkable** | **move** — real rationale, unverifiable here | **drop** — history |

⚠ **Truth is not one of the questions, and that is the point.** History that is *correct* reads
as earning its place, and does not. Accuracy is why it was never deleted, not a reason to keep.

⚠ **A single `keep` sentence launders every sentence around it.** Ruling `keep` on a block
because *part* of it is load-bearing is the signal to descend a level: a block's most defensible
sentence is usually why the whole block survived this long.

**Name the repair, and check it separately from the detection.** Detection can be right and the
repair wrong — a stale count is re-derived or deleted, never softened to "most"; a mis-formatted
citation is reformatted, never dropped. A repair keeps the checkability the original had.

Then, for anything surviving: is it longer than it needs to be? That is **compact** — not a
fifth verdict but what you do to a `keep`, or to the remainder a `move` leaves behind. For
**move**, name the destination; ⚠ **it gets the WHOLE block, including the half that stays in
the code** — a document holding only what was discarded reads as a deletion list, not a record.

Mark every finding `CONFIRMED` (you read both the prose and the code or guard that settles it)
or `SUSPECTED` (you did not). Measured: labelling this way had reviewers withdraw their own weak
candidates rather than pad, and an unlabelled finding once drove a TODO that had to be retracted.

## Phase 3 — Present. Always.

**This skill never edits. It ends with the verdict list** — grouped by verdict, most consequential
first, the replacement inline for every `compact`, and the census counts so coverage is visible.

⚠ **Even when the human names the edit** — "cap them", "fix these", "go do it" — the deliverable
is the report: *"Report only, per the skill — say the word and I'll apply the verdicts you
accept."* An imperative is not authorization. The review's value is the human's disagreement with
it, and **an edit applied is a verdict never ruled on**. Measured before this rule: two runs on
near-identical prompts split, one returning a report and the other an 846-line diff. Reviewers
are **READ-ONLY** — say so, and name which files are under review and which are reference only.

## Rails for the pass that applies these

- **Never change code, a docstring's meaning, or a string literal.** Prove it: diff every
  non-comment line against the pre-edit file and confirm zero differences.
- **Apply on an exact match count of 1, or refuse the whole file** — a near-miss must be a loud
  refusal, never an edit landing somewhere plausible. Build the `old` text programmatically.
- **Before changing any number, name or path in prose, grep it repo-wide** — including config,
  docs and other trees. The usual outcome otherwise is three of four siblings fixed.
- **Extract before you cut** when the verdict is `move`; the other order lost the text to an
  interruption three times. Check the replacement's width as well as its line count, and keep each
  file's own line ending, or a three-line prose edit becomes a whole-file diff.
- **Re-read what you wrote.** A pass that cut seven ghost names wrote seven new ones — the same
  one twice in one file — and wrote over-length blocks while removing over-length blocks.

## A note for whoever edits this file

**Every example above is invented. Keep it that way.** Quoting a real comment teaches a reviewer
to recognise *that comment* instead of the shape, and it rots: the day someone acts on the finding
this file cites a comment that no longer exists — a hygiene skill carrying its own ghost name.
Measurements are worth keeping and cost nothing to anonymise. **Add to the checklist; do not
re-partition it** — a new class is a numbered row with a detection question AND a stopping rule,
and a row without the stopping rule licenses flagging everything.
