---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles --
  currency, functionality, placement, reachability -- using parallel subagents that sweep EVERY
  prose block in those files, and return each finding with a proposed verdict (drop / move /
  compact / keep) for the human to rule on. Use this whenever comments or documentation are the
  subject: after a task that added or edited commentary, when a file's comments have drifted
  from what the code now does, when someone says a comment is too long or out of date or "isn't
  this history", when reviewing a diff for its prose rather than its logic, before a docs or
  comment burn-down, or when asked whether a module still reads as one module. Trigger on
  phrasings that never say "comment review" -- "these comments are getting out of hand", "does
  this docstring still match", "is this comment still true", "clean up the narration in this
  file", "why does this file need so much explaining" all mean run this. It is NOT /simplify
  (code structure, and it applies its fixes) and NOT /code-review (correctness bugs) -- this one
  ONLY EVER PROPOSES and never edits anything, not code and not even the comments it rules on,
  because an edit applied is a verdict the human never got to rule on. Run it even when asked to
  cut ("cap these", "clean this up"): the deliverable is still the verdict list, applying is a
  separate step, and code concerns get raised in a line and left.
---

# comment-review

`/comment-review [cap] [target]` -> enumerate every prose block -> 4 reviewers sweep all of them ->
a verdict per block -> you decide -> apply.

## The rule that decides this skill's yield

**The unit of work is the BLOCK LIST, not the file.** Phase 0 enumerates every comment run and
every docstring in scope and numbers them. Each reviewer walks that list start to finish and
returns **one line per block** -- a finding, or a named acquittal. A block nobody mentioned is a
**gap in the review**, not one that passed; the report says how many were swept.

That is the difference between a review and a search. A reviewer told to "find the comments that
need attention" returns its most confident dozen and stops. The measurement behind the rule is
blunt: in a tree never swept before, defects were neither rare nor concentrated in the obvious
blocks -- **the false clauses sat inside blocks whose other sentences were true, in the same
voice, at the same indent, under the same warning glyph.** Position and length predicted nothing.

! **The counterweight, and what stops this degenerating into "flag everything": you do not get
to acquit by SILENCE.** An acquittal is a written verdict naming a reason below -- one line,
cheap enough to afford total coverage, dear enough to force a decision rather than a shrug.

### The acquittal list -- the ONLY reasons to pass a block over

Closed list. If none applies, the block gets a finding.

- **`label`** -- a one- or two-line comment naming the line it sits on and claiming nothing else
  (`# Kalman gain`, `# 0 disables the backoff`).
- **`states-the-signature`** -- a one- or two-line docstring, present tense, matching the name,
  the arguments and the return, citing nothing outside itself. Three lines or more is no longer
  this: it is carrying something, and what it carries is what you are here to read.
- **`derivation`** -- a hand-worked calculation whose digits are what stop an assertion being an
  echo of the implementation, and the *first* thing a careless cap deletes. Over cap it is a
  `move` **into the docstring** -- which sits at a boundary and has no cap -- never a `compact`.
- **`only-guard`** -- a warning against a plausible wrong move where **nothing goes red** if
  someone makes it. Verify that; if a test does fail it is a time-saver, not a guard.
- **`names-its-expiry`** -- prose stating the condition under which it stops being wanted.

Nothing is acquitted for being short, true, well written, new, or sitting under a `!`.

## The subject is the prose, not the program

You will notice code problems -- say so, one line each, in a separate section, and move on.
**Raise a concern, do not open an investigation**, and never give a code finding a
`drop`/`move`/`compact`/`keep` verdict. *The comment names a symbol that no longer exists* is
yours; *the symbol should be restored* is not. ! **A reviewer straying into correctness is this
skill's worst measured output** -- twice, one read a modern multi-exception `except` clause and
reported the file "cannot compile", and once four agreeing reviewers shipped it.

**Arguments.** `cap` -- optional integer, the most lines one `#` block may run. **This skill has
no cap of its own and must not invent one**; a cap published in a lint config or a hygiene test
is the number, and read how it *counts* too. With no cap, judge and **report the longest run
found**. `target` -- optional path, defaulting to the files in the diff.

## Phase 0 -- enumerate, mechanically

Scope is **whole files, not the diff**: `git diff --name-only @{upstream}...HEAD` (or
`main...HEAD`, or `HEAD~1`; add `git diff --name-only HEAD` when dirty) yields a FILE LIST, and
every block inside those files is in scope. Comment debt is cumulative and mostly pre-existing --
the long block that has sat above a four-line expression for months is the finding worth having,
and a diff-scoped reviewer never sees it. Run this, and **paste its output -- the block list --
into every reviewer prompt.**

```python
# sweep.py -- list every prose block with its mechanical signals. Generic: stdlib only,
# no repo assumptions, safe on a missing path or an unparseable file.
import ast, io, re, sys, tokenize
from pathlib import Path

CAP, WIDTH = 6, 100
TAGS = [
    (re.compile(p, re.I), t)
    for p, t in [
        (r"\b\d{4}-\d{2}-\d{2}\b", "dated"),
        (
            r"\b(?:used to|no longer|previously|formerly|renamed|retired|was the|had been"
            r"|instead of|before the fix|retract)\w*\b",
            "history",
        ),
        (r"\b(?:guard|assert|pinned|enforc|cover|prov(?:es|en))\w*", "coverage-claim"),
        (r"\b(?:all|only|every|exactly|both)\s+\w*\s*\d|\b\d+\s*%", "counted"),
        (r"[\w./-]*[\w-]\.(?:py|md|toml|json|ya?ml|txt|cfg)\b", "cites-a-path"),
        (r"`[A-Za-z_][\w.]*`", "names-a-symbol"),
    ]
]
HOLDS = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def blocks(src):
    """Yield (start, end, kind); a comment RUN is bounded by CODE, not by blank lines."""
    out, run, prev, rows = [], [], -9, src.splitlines()
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except tokenize.TokenError, IndentationError, SyntaxError:
        toks = []
    for t in (t for t in toks if t.type == tokenize.COMMENT):
        own = rows[t.start[0] - 1].lstrip().startswith("#")  # a trailing one is its own
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


total = longest = 0
for f in [a for a in sys.argv[1:] if not a.startswith("-")]:
    if not Path(f).is_file():
        print(f"# missing: {f}")
        continue
    lines = Path(f).read_text(encoding="utf-8", errors="replace").splitlines()
    for a, b, kind in blocks("\n".join(lines)):
        text, n = "\n".join(lines[a - 1 : b]), b - a + 1
        total += 1
        longest = max(longest, n if kind == "comment" else 0)
        tags = [f"OVER-CAP:{n}"] if kind == "comment" and n > CAP else []
        tags += [f"docstring:{n}L"] if kind == "docstring" and n > 2 else []
        tags += ["over-width"] if any(len(x) > WIDTH for x in lines[a - 1 : b]) else []
        tags += [t for p, t in TAGS if p.search(text)]
        print(f"{f}:{a}-{b}\t{kind}\t{n}L\t{','.join(tags) or '-'}")
print(f"# {total} blocks; longest comment run {longest}")
```

Then resolve what it only located: every `cites-a-path` against the tree, every `names-a-symbol`
against the names the code defines -- build that corpus from the **AST**, since one built from raw
text contains the comments being checked and so always passes. ! **Grep the STEM, not the
identifier.** Prose does not obey identifier spelling, so a dead
`foo_bar` is written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Measured: an identifier grep
found ten mentions, all correctly dated tombstones, and missed an eleventh written with a hyphen
-- the only present-tense claim in the set. A clean grep reads like a clean file. ! And **a
resolved citation is not a verified one**: a citation asserts something *about* its target, so
open it and read it or mark the finding `SUSPECTED`. A reviewer told the paths are confirmed will
not open them, and the check then makes a false claim harder to find rather than easier.

## Phase 1 -- four reviewers, each over the WHOLE list

Launch four subagents in one message. Give each the file list, the sweep output, the `cap`, the
acquittal list, and one angle. **Tell each, in words, to return a line for every numbered
block.** Overlap between angles is signal, not waste -- a finding all four report is almost
always real, and on one run the second angle caught an error the first had just introduced.

! **Reviewers are READ-ONLY; say so explicitly**, and **name two lists: the files UNDER REVIEW,
which a proposal may target, and files given only as REFERENCE, which it never may.** A reviewer
that fixes what it finds has destroyed the finding, and one handed a contract document to check
code against proposed edits *to the contract*, which were applied.

Every finding carries `file:line`, the exact claim, the code or test line that settles it, and
**`CONFIRMED` (both sides read) or `SUSPECTED` (not)** -- measured, 196 of 202 came back CONFIRMED.

### Currency -- does this describe the program as it is now? (~45% of yield)

The largest angle by a distance. Git holds what the code used to be; a comment narrating its own
history is doing git's job badly. Flag dated rulings, review-round labels ("fix round 2",
"finding B4"), "this used to...", "before the fix", and the sharpest form, **obituaries** -- a
comment naming a symbol, file, test or flag that no longer exists. A reader greps the name, finds
nothing, and reads that as *their* mistake, not the comment's. Also here: **a counted claim is
unverifiable unless it names the POPULATION it counts over**, so re-derive the SET before the
number -- a pass correcting a false count produced a differently-false one, off by 5x.

### Functionality -- does the commentary match what the code does? (~30%)

Read the name, the signature and the docstring, then **read the body** -- measured, the flagship
false claims are contradicted two or three lines below themselves. Flag a documented return shape
the code no longer returns, a `Returns:` whose key and value are the wrong way round, an `Args:`
entry describing a guard on the wrong object, a documented exception nothing raises, a raise
nothing documents, a summary line summarising the first four lines of a five-job function.

Then read the body's comments **as one sequence**: individually each may be true, but end to end
they are the most honest description of the function in the file. **The tell is grammatical -- a
comment that sequences instead of constrains** (*"now I need to...", "then we..."*). Report the
mismatch and name the fork: the docstring grows until the NAME is wrong, or the function shrinks.

! **Prose that DESCRIBES behaviour is wrong far more often than prose that PROHIBITS something,
and the two disagree differently.** A description that disagrees with the code -> the comment is
wrong. A prohibition that disagrees -> the code broke the rule -> file it. And a description must
be **POSITIVE**: *"NOT the kernel call site"* never lands on a side you can verify, because the
reader must first establish what the code does do and then argue backwards.

! **Resolve superlatives and collective nouns against their own file.** "single source of truth",
"THE only entry point", "these constants", "the table" -- a "one definition" naming a single member
is a tautology, and an "only entry point" is refuted 25 lines down often enough to check always.

### Placement -- is this prose where the thing it constrains is? (~15%)

Locality and module coherence are the same question at two zooms; one reviewer holds both. Small
zoom: a comment is a claim about the code beside it. Flag one about something else -- a rule
at the top of a class really constraining two integer literals two hundred lines down; a block
whose later half turns back to narrate what came before; a run sitting *after* an unconditional
`return` that explains code below the branch; a run between two statements annotating neither; a
trailing comment that **runs on into comment-only lines beneath it** (a formatting finding -- lift
it above the line). The test for anything that survives: **if this code changed, would the comment
become wrong, and would anyone notice?** Flag the inverse too -- a line carrying a non-obvious
constraint with no comment at all, where getting it wrong is silent.

Large zoom: read only the module docstring, the banners and the top-of-file prose. Do they
describe *one* thing? Flag a docstring that must enumerate unrelated responsibilities to be
accurate, banners reading like chapter breaks, and **the same rule re-explained in several
places** -- no function owns it, so each site performing part of it restates the whole. Where one
claim appears in several files, check every copy: the owner stays right while the copy rots.

### Reachability -- does anything read what the prose describes? (~10%)

The angle the other three structurally cannot see, and the one that licenses deletions. "Pinned
by X", "X refuses this", "guarded by Y" is *authorising the next person to delete something*, so
the claim is checked, never read. Per claim: does the constant it annotates have a reader? Does
the function it documents have a caller outside the tests? Is the hazard it warns about still
triggerable? Does the cited guard exist, and could it fail?

It fails in both directions -- a real guard has been deleted on a pointer to a test that never
existed, and a comment calling a live config value "decorative" nearly licensed deleting
something three sites read. **Line-number citations rot silently**: a symbol survives a refactor,
a line number does not. **A claim in a form your checker cannot parse is worse than the same
claim written parseably and wrong** -- the parseable one gets fixed, the unparseable one
accumulates while reading as terse authority. For data reached by key rather than by name, **grep
the STRING**. ! But **an unreachable hazard is not automatically a `drop`** -- a precaution's
value is having no trigger, and prose stopping a specific future edit stays, compacted in place.

## Phase 2 -- one verdict per block

Dedup blocks reported by more than one angle, then rule. **Before proposing a CHANGE, read the
prose immediately around it** -- a deliberate design usually says so directly above itself. Read
the neighbours before you *change*, but do not let them stop you *reporting*: a neighbour
asserting the same false thing is two findings, not zero. Then two questions, in order. **Is it
CHECKABLE** from the code as it stands, without archaeology? **Is it NECESSARY** -- would someone
changing this code make a *worse decision* without it? Not "is it interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader needs | **drop** -- it narrates the code |
| **not checkable** | **move** -- rationale, unverifiable here | **drop** -- history |

! **Truth is not one of the questions, and that is the point.** History that is *correct* reads as
earning its place, and does not; accuracy is the reason it was never deleted, not a reason to keep
it. The exception is arithmetic -- a claim that is pure arithmetic over committed values is
checkable without judgement, so recompute it rather than rule on it.

**Rule on SENTENCES, not on blocks.** A container of six sentences can hold six verdicts, and the
common shape is a live constraint beside the story of where it came from. ! **A single `keep`
sentence launders every sentence around it** -- if you are ruling `keep` because *part* of it is
load-bearing, descend a level. That is the default outcome for any comment mixing a rule with its
origin, and mixing those two is the house style you are here to undo.

**compact** is not a fifth verdict -- it is what you do to a `keep` or to a `move`'s remainder;
for a `move`, name the destination and send the WHOLE block including the half that stays. !
**Account for every digit you propose deleting**: name what in the working tree the removed
sentence was the only record of. The most repeated defect a compaction pass introduces is **a
measurement replaced by an adjective**, and it always looks like a legitimate trim -- right up to
the case where the deleted number contradicted the sentence that survived it. ! And **a block one
line over cap is, by construction, mostly right** (on one tail, 27 of 48 runs were over by exactly
one): cut the least checkable line, do not re-author.

## Phase 3 -- present. Always.

**This skill never edits. It ends with the verdict list.** Report grouped by verdict, most
consequential first, the replacement inline for every `compact`, and a coverage line: *N swept,
M findings, K acquitted*. Then stop. ! **Even when the human names the edit** -- "cap
them", "go do it" -- the deliverable is the report: *"Report only, per the skill -- say the word
and I'll apply the verdicts you accept."* An imperative is not authorization; this review's whole
value is the human's disagreement with it, and **an edit applied is a verdict never ruled on.**
Measured before this rule: two runs on near-identical prompts split, one report, one diff.

## Rails for the pass that applies these

You are not that pass; the applier usually runs without this skill loaded.

- **A block is bounded by CODE, not blank lines** -- else 9 lines become 6 + blank + 3.
- **Never change a line of code, a docstring's meaning, or a string literal**; prove it by
  diffing every non-comment line, which caught two cuts that took real code.
- **`count == 1` or refuse the whole file**, with the `old` text built programmatically, its
  width checked as well as its line count, and the file's own line ending preserved. **Extract
  before you cut on a `move`** -- the other order lost text three times.
- **Re-read what you wrote.** A pass that cut seven obituaries wrote seven new ones.
- **Every example above is invented; keep it that way.** Quoting a real comment teaches
  recognition of *that comment* rather than the shape, and rots into an obituary of its own.
