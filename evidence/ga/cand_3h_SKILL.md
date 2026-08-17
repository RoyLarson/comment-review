---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles -- currency,
  functionality, locality, module coherence -- after a mechanical census, and return each finding
  with a proposed verdict (drop / move / compact / correct / keep) for the human to rule on. Use
  this whenever comments or documentation are the subject: after finishing a task that added or
  edited commentary, when a file's comments have drifted from what the code now does, when someone
  says a comment is too long or out of date or "isn't this history", when reviewing a diff
  specifically for its prose rather than its logic, before a docs or comment burn-down, or when
  asked to check whether a module still reads as one module. Trigger on phrasings that never say
  "comment review" -- "these comments are getting out of hand", "does this docstring still match",
  "is this comment still true", "clean up the narration in this file", "why does this file need so
  much explaining" all mean run this. It is NOT /simplify (which reviews code structure and applies
  its fixes) and NOT /code-review (which hunts correctness bugs) -- this one ONLY EVER PROPOSES and
  never edits anything, not code and not even the comments it rules on, because an edit applied is
  a verdict the human never got to rule on. Run it even when the request sounds like an instruction
  to cut ("cap these", "clean this up"): the deliverable is still the verdict list, and applying is
  a separate step. It is explicitly not a reviewer's job to judge whether the code works: code
  concerns get raised in a line and left, while every verdict returned is a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` -> census -> 4 reviewers in parallel -> rank -> spend a budget -> you rule.

## The rule that decides this skill's yield: a finding is a CHOICE, not an observation

Every block you raise is one you raised **instead of** another. Two measured facts force this:

- **Recall saturates.** Across sixteen graded runs on one slice, going from 261 findings to 364
  bought **+1.5 points of recall** and cost 19 points of precision. The extra hundred were noise.
- **The same closed acquittal list, run by two reviewers, acquitted 47% and 14% of the same
  blocks.** Identical vocabulary, identical corpus, a 33-point gap in the only number that moved
  the score. **The acquittal RATE is the trait; the list is just words.**

So the deliverable is *ranked*, and it is *bounded*. After the census, state a **budget**: how many
findings you intend to return, and defend it out loud. Absent a reason to differ, a tree that has
never been swept runs **50-65% of its blocks**; one already under a live guard runs far under that.
Then rank every candidate by the ladder below and **spend top-down until the budget is gone.** If a
Tier 3 candidate is worth reporting, say which Tier 2 candidate it displaced.

! **Do not turn the budget into a quota.** Falling short of it is fine and is a finding of its own
("this file is clean"). Padding to reach it is the exact failure the two measurements above name.

## The subject is the prose, not the program

**It is not a reviewer's job to decide whether the code works.** Every verdict you return is a
verdict on a comment. You will still notice code problems -- say so in a separate section, one line
each, and move on. **Raise a concern, do not open an investigation**, and never let a code finding
acquire a `drop`/`move`/`compact`/`correct`/`keep` verdict.

| This is a COMMENT finding | This is a CODE finding |
|---|---|
| the comment says it reads one field; it reads three | it should not read three |
| the comment names a symbol that no longer exists | the symbol should be restored |
| the comment claims callers `grep` cannot find | the function is dead, delete it |

! **A reviewer straying into correctness is this skill's worst measured output.** Twice, one read a
modern multi-exception `except` clause and reported the file "cannot compile"; once four agreeing
reviewers shipped it. If your claim is about whether the code *runs*, it is not your finding -- and
if you make it anyway you owe it an `ast.parse` first.

**Arguments.** `cap` -- optional integer, the most lines one `#` run may take. **This skill has no
cap of its own and must not invent one**; a cap the repo publishes (a lint config, a hygiene test)
is the number, and read how it *counts*. With none, judge and **report the longest run found**.
`target` -- optional path, defaulting to the files in the diff.

## Phase 0 -- census, mechanically

Scope is **whole files, not the diff**. `git merge-base` against the default branch, else
`HEAD~1`; add `git diff --name-only HEAD` when the tree is dirty. That yields a FILE LIST, and
every block in those files is in scope: comment debt is cumulative and mostly pre-existing, and the
long block that has sat above a four-line expression for months is the finding worth having.
Exclude `.md`/`.txt` -- prose files are a different review. Run this and **paste the block list into
every reviewer prompt**; it is the denominator that makes *"253 of 419"* an answerable claim.

```python
# sweep.py -- every prose block with its mechanical tags. stdlib only, no repo assumptions,
# safe on a missing path, an unparseable file, or a tree with no virtualenv.
import ast, io, re, sys, tokenize
from pathlib import Path

CAP, WIDTH = 6, 100
FREE = re.compile(
    r"\b(TODO|FIXME|HACK|XXX|BUG)\b"
)  # markers point outward: never counted
TAGS = [
    (re.compile(p, re.I), t)
    for p, t in [
        (r"\b\d{4}-\d{2}-\d{2}\b", "dated"),
        (
            r"(finding|round|wave|part [a-z]\b|critical|blocker)\s*[a-z]?\d",
            "review-label",
        ),
        (
            r"\b(used to|no longer|previously|formerly|renamed|retired|retract|before the fix"
            r"|we tried|superseded|reverted|the old )\w*",
            "history",
        ),
        (
            r"\b(guard|assert|pinned|enforc|cover|prov(es|en)|only call|nothing asserts)\w*",
            "coverage",
        ),
        (r"\b(all|only|every|exactly|never|always)\b.{0,20}\d|\b\d+\s?%", "counted"),
        (r"[\w./-]*[\w-]\.(py|md|toml|json|ya?ml|txt|cfg)\b", "cites-a-path"),
        (r"`[A-Za-z_][\w.]*`", "names-a-symbol"),
        (r"[""]|\bsaid\b|\bruled\b|\bconfirmed\b", "quotes-a-person"),
    ]
]
HOLDS = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def blocks(src):
    """(start, end, kind) per block; a `#` RUN is bounded by CODE, never by blank lines."""
    out, run, prev, rows = [], [], -9, src.splitlines()
    try:
        toks = [
            t
            for t in tokenize.generate_tokens(io.StringIO(src).readline)
            if t.type == tokenize.COMMENT
        ]
    except tokenize.TokenError, IndentationError, SyntaxError, ValueError:
        toks = []
    for t in toks:
        own = (
            rows[t.start[0] - 1].lstrip().startswith("#")
        )  # a trailing comment is its own block
        if run and (t.start[0] != prev + 1 or not own):
            out.append((run[0], run[-1], "comment"))
            run = []
        run.append(t.start[0])
        prev = t.start[0] if own else -9
    if run:
        out.append((run[0], run[-1], "comment"))
    try:
        nodes = list(ast.walk(ast.parse(src)))
    except SyntaxError, ValueError:
        return sorted(out)
    for node in nodes:
        b = getattr(node, "body", []) if isinstance(node, HOLDS) else []
        v = getattr(b[0], "value", None) if b and isinstance(b[0], ast.Expr) else None
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            out.append((b[0].lineno, b[0].end_lineno or b[0].lineno, "docstring"))
    return sorted(out)


total = 0
for f in [a for a in sys.argv[1:] if not a.startswith("-")]:
    if not Path(f).is_file():
        print(f"# missing: {f}")
        continue
    lines = Path(f).read_text(encoding="utf-8", errors="replace").splitlines()
    for a, b, kind in blocks("\n".join(lines)):
        body, n = lines[a - 1 : b], b - a + 1
        total += 1
        eff = len([x for x in body if not FREE.search(x)])
        tags = [f"OVER-CAP:{eff}"] if kind == "comment" and eff > CAP else []
        tags += [f"docstring:{n}L"] if kind == "docstring" and n > 3 else []
        tags += ["over-width"] if any(len(x) > WIDTH for x in body) else []
        tags += [t for p, t in TAGS if p.search("\n".join(body))]
        print(f"{f}:{a}-{b}\t{kind}\t{n}L\t{','.join(tags) or '-'}")
print(f"# {total} blocks")
```

! **Nothing the sweep emits is a verdict**, and a block with no tag can still be the worst prose in
the file -- tags are *reasons to look*. Equally, **do not re-derive what it settled.** Then resolve
what it only located: every `cites-a-path` against the tree, every `names-a-symbol` against the
names the code DEFINES -- build that corpus from the **AST**, never from raw text (text built from
the file contains the very comments under test, so the check always passes), skip any directory
holding `pyvenv.cfg`, and never harvest string constants out of tests (one negative assertion
pinning a deleted field taught a resolver that every dead name was alive).

## The ranking ladder -- spend the budget top-down

**Tier 1 -- mechanical, cheap, numerous, and where most of the yield is.** A machine can point at
the block and a human settles it in seconds. Take *all* of these before anything else.

1. **Over the cap**, counted by CODE. If a repo publishes a cap and its baseline is empty, every
   over-cap run in scope is a finding by arithmetic, not by judgement.
2. **A name in prose that resolves nowhere** -- an *obituary*. A reader greps, finds nothing, and
   reads it as *their* mistake.
3. **A citation that does not resolve** -- a path, a test, a doc, a `file.py:NN` line number.
4. **A docstring carrying a date, a ruling, a quotation, an attribution, a review label
   ("finding 4", "round 2", "fix wave A"), or a rationale paragraph.** This is a **FORMAT** failure
   and it is a finding **at any length** -- never flag a docstring merely for being long.
5. **A count that no longer holds**, or that names no population to re-derive it over.

**Tier 2 -- read the code to settle it.** Cheap per block, but one block at a time.

6. **A description the body contradicts** -- a return shape, an `Args:` entry for a vanished
   parameter, a documented exception nothing raises, a summary line covering four of five jobs.
   ! **Prose that DESCRIBES is wrong far more often than prose that PROHIBITS.**
7. **A coverage claim** -- "guarded by X", "pinned by Y", "the only call site". This is the class
   that *licenses deletions* and is disproportionately wrong. Grep the cited name, every time.
8. **History narration in a `#` run** -- "used to", "before the fix", "reverted from", a dated
   ruling, a retracted fact, a "the old X" that no longer exists.
9. **A rule stated in several places at once** -- no function owns it, so each site restates it.
   Check every copy: the owner stays right while the copies rot.
10. **A run that is not about the line it sits on** -- a block whose later half narrates what came
    before, a run after an unconditional `return`, a trailing comment that spills into
    comment-only lines beneath it, a rule at the top of a class constraining two literals 200
    lines down.

**Tier 3 -- judgement, and the first thing the budget cuts.** A true, current, local block that is
merely long, wordy, or explains something a careful reader could infer. Report these only while
budget remains, and expect to be wrong about half the time.

## The acquittal list -- the ONLY reasons to pass a block over

Closed list. If none applies and the block hits a tier, it gets a finding.

- **`label`** -- a one- or two-line comment naming the line it sits on and claiming nothing else.
- **`states-the-signature`** -- a short docstring, present tense, matching the name, the arguments
  and the return, citing nothing outside itself and arguing for nothing.
- **`derivation`** -- hand-worked arithmetic; it is what stops an assertion being an echo of the
  implementation, and the first thing a careless cap deletes. Over cap it is a **move into the
  docstring** -- which sits at a boundary and has no cap -- never a `compact`.
- **`only-guard`** -- a warning against a plausible wrong move where **nothing goes red**. Verify
  that; if a test does fail, it is a time-saver, not a guard.
- **`names-its-expiry`** -- prose stating the condition under which it stops being wanted.

Nothing is acquitted for being short, true, well written, new, or sitting under a `!`.

## Phase 1 -- four reviewers, in parallel

Launch four subagents in one message. Give each the file list, the sweep output, the `cap`, the
acquittal list, the ladder, and one angle. **Currency** (~45% of yield) -- tiers 2, 3, 5, 8: does
this describe the program as it is now? Git holds what the code used to be; a comment narrating its
own history does git's job badly. **Functionality** (~30%) -- tiers 6, 7, and reachability: read
name, signature, docstring, then the **body**; the flagship false claims are contradicted two or
three lines below themselves. **Locality** -- tier 10, plus the inverse: a line carrying a
non-obvious constraint that nothing states, where getting it wrong is silent. **Module coherence** --
tiers 4 and 9 over the module docstring, banners, and top-of-file prose only: do they describe *one*
thing?

Merging these into one reviewer measurably lost recall. Overlap between them is signal, not waste.

! **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar`
is written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Measured: an identifier grep found ten
mentions, all correctly dated tombstones, and missed an eleventh written with a hyphen -- the only
present-tense claim in the set. A clean grep reads exactly like a clean file.

! **Reviewers are READ-ONLY; say so.** Name two lists: files UNDER REVIEW, which a proposal may
target, and files given as REFERENCE, which it never may. A reviewer that fixes what it finds has
destroyed the finding; one handed a contract document to check code against proposed edits *to the
contract*, and they were applied. Every finding carries `file:line` -- **the line of the offending
SENTENCE, not the first line of a forty-line block** -- the exact claim, the code or test line that
settles it, and `CONFIRMED` (both sides read) or `SUSPECTED` (not).

## Phase 2 -- one verdict per finding

Dedup, then rule. **Before proposing a CHANGE, read the prose immediately around it** -- a
deliberate design usually says so directly above itself. Read the neighbours before you *change*;
do not let them stop you *reporting*. Then two questions. **Is it CHECKABLE** from the code as it
stands, without archaeology? **Is it NECESSARY** -- would someone changing this code make a *worse
decision* without it? Not "is it interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader needs | **drop** -- it narrates the code |
| **not checkable** | **move** -- rationale, unverifiable here | **drop** -- history |

! **Truth is not one of the questions, and that is the point.** History that is *correct* reads as
earning its place, and does not; accuracy is why it was never deleted, not a reason to keep it.

A fifth verdict, **`correct`**, for a block that must be FIXED rather than cut: a stale count is
re-derived or deleted, never softened to "most"; a mis-formatted live citation is reformatted,
never dropped. **Detection can be right and the repair wrong** -- rule on them separately. **compact**
is not a verdict of its own: it is what you do to a `keep` or to a `move`'s remainder. For a
**move**, name the destination and send the **WHOLE block, including the half that stays in the
code** -- a document holding only what was discarded reads as a deletion list, not a record.

**Rule on SENTENCES, not on blocks.** ! **A single `keep` sentence launders every sentence around
it** -- if you are ruling `keep` because *part* is load-bearing, descend a level. A live constraint
sharing a paragraph with the story of where it came from is the ordinary case, not a rare one.

! **Account for every digit you propose deleting.** The most repeated defect a compaction pass
introduces is **a measurement replaced by an adjective**, and it always looks like a legitimate
trim. ! And **a block one line over cap is by construction mostly right** -- cut the least
checkable line, do not re-author.

## Phase 3 -- present. Always.

**This skill never edits. It ends with the verdict list** -- grouped by verdict, most consequential
first, the replacement inline for every `compact`, and a coverage line: *N blocks swept, M
findings, budget was B*. Then stop.

! **Even when the human names the edit** -- "cap them", "fix these", "go do it" -- the deliverable is
the report: *"Report only, per the skill -- say the word and I'll apply the verdicts you accept."*
An imperative is not authorization; this review's whole value is the human's disagreement with it,
and **an edit applied is a verdict never ruled on.** Measured before this rule: two runs on
near-identical prompts split, one returning a report and the other an 846-line diff.

## Rails for the pass that applies these

You are not that pass; the applier usually runs without this skill loaded.

- **A block is bounded by CODE, not blank lines** -- else 9 lines become 6 + blank + 3.
- **Never change a line of code, a docstring's meaning, or a string literal.** Prove it by diffing
  every non-comment line; that caught two cuts that ran on and took real code.
- **`count == 1` or refuse the whole file**, with the `old` text built programmatically rather than
  transcribed, its width checked as well as its line count, and the file's own line ending kept.
- **Extract before you cut** on a `move`; the other order lost the text three times.
- **Re-read what you wrote.** A pass that cut seven obituaries wrote seven new ones, the same one
  twice in one file, and wrote over-length blocks while removing over-length blocks.

**Every example above is invented or anonymised. Keep it that way** -- quoting a real comment
teaches recognition of *that comment* rather than the shape, and rots into an obituary of its own.
