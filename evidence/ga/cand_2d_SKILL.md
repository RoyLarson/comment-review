---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched -- every block, census-first,
  across currency, functionality, placement and coverage -- and return each one with a proposed
  verdict (drop / move / compact / correct / keep) for the human to rule on. Use this whenever
  comments or documentation are the subject: after finishing a task that added or edited
  commentary, when a file's comments have drifted from what the code now does, when someone says a
  comment is too long or out of date or "isn't this history", when reviewing a diff specifically
  for its prose rather than its logic, before a docs or comment burn-down, or when asked to check
  whether a module still reads as one module. Trigger on phrasings that never say "comment review"
  -- "these comments are getting out of hand", "does this docstring still match", "is this comment
  still true", "clean up the narration in this file", "why does this file need so much explaining"
  all mean run this. It is NOT /simplify (code structure, and it applies its fixes) and NOT
  /code-review (correctness bugs) -- this one ONLY EVER PROPOSES and never edits anything, not code
  and not even the comments it rules on, because an edit applied is a verdict the human never got
  to rule on. Run it even when the request sounds like an instruction to cut ("cap these", "clean
  this up"): the deliverable is still the verdict list, and applying is a separate step. It is not
  a reviewer's job to judge whether the code works: code concerns get raised in a line and left,
  while every verdict returned is a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` -> census every block -> walk each past the checklist -> a finding **or a
named acquittal** for each -> present. You decide; this skill never edits.

## The two mechanisms that decide the yield

1. **Census before judgement.** Phase 0 enumerates and numbers every `#` run and every docstring in
   scope. A reviewer told to "find the comments needing attention" returns its confident dozen and
   stops; the census makes "every block" a list instead of a feeling.
2. **No acquittal by silence.** Every numbered block leaves the review with a finding **or a one-word
   acquittal from the closed list below**. A block nobody mentioned is a gap in the review, not a block
   that passed, and the report says `N swept, M findings, K acquitted`.

Independent and both load-bearing: the first guarantees a block is SEEN, the second that it is RULED ON.
Why neither is optional: **the false clauses sat inside blocks whose other sentences were true**, same
voice, same indent, same warning glyph -- so **"look where nothing asserts" beats "look for long
blocks"**: decoration beside a passing test survives every change to what it describes.

### The acquittal list -- the ONLY reasons to pass a block over

- **`label`** -- one or two lines naming the line they sit on and claiming nothing else.
- **`states-the-signature`** -- a one- or two-line docstring, present tense, matching the name, the
  arguments and the return, citing nothing outside itself. Three lines is no longer this: it carries
  something, and what it carries is what you are here to read.
- **`derivation`** -- hand-worked arithmetic whose digits are what stop an assertion being an echo of the
  implementation. Over cap it is a `move` into the docstring; never a `compact`.
- **`only-guard`** -- a warning against a plausible wrong move where **nothing goes red**. Verify that;
  if a test does fail it is a time-saver, not a guard, and it is `compact`.
- **`names-its-expiry`** -- prose stating the condition under which it stops being wanted.
- Nothing is acquitted for being short, true, well written, new, or sitting under a `!`.

## The subject is the prose, not the program

Every verdict you return is a verdict on a comment. You will notice code problems -- say so, one line
each, in a separate section, and move on: **raise a concern, do not open an investigation**, and never
give a code finding a comment verdict. *The comment names a dead symbol* is yours; *restore the symbol*
is not. ! **A reviewer straying into correctness is this skill's worst measured output** -- twice, one
read a modern multi-exception `except` clause and reported the file "cannot compile"; once four agreeing
reviewers shipped it. A claim about whether the code RUNS owes a `python -c` first.

**Arguments.** `cap` -- optional integer, the most lines one `#` block may run. **This skill has no cap
of its own and must not invent one**: a cap published in a lint config or hygiene test is the number,
and read *how it counts* too. With none, judge and report the longest run. `target` -- optional path,
defaulting to the files in the diff.

## Phase 0 -- scope, then census

Scope with `git merge-base`, never a `A...B` between two tips: `git diff --name-only $(git merge-base
HEAD @{upstream} || git merge-base HEAD main)..HEAD`, else `HEAD~1`; add `git diff --name-only HEAD`
when dirty, and ! check which form returned something -- an empty range succeeds silently. Scope is
**whole files, not the diff**: comment debt is cumulative and mostly pre-existing, and the block that
has sat above a four-line expression for months is the finding worth having.

```python
# sweep.py -- census every prose block, tag its signals. Stdlib only, no repo assumptions, safe
# on a missing or unparseable file. A RUN is bounded by CODE, not blanks.
import ast, io, re, sys, tokenize
from pathlib import Path

CAP, WIDTH = 6, 100
TAGS = [
    (re.compile(p, re.I), t)
    for p, t in [
        (r"\b\d{4}-\d{2}-\d{2}\b|\b20\d\d\b", "dated"),
        (
            r"\b(?:used to|no longer|previously|formerly|renamed|retired|was the|had been|instead of"
            r"|before the fix|retract|until|since|originally|once)\w*\b",
            "history",
        ),
        (
            r"\b(?:guard|assert|pinned|enforc|cover|prov(?:es|en)|test|caught)\w*",
            "coverage",
        ),
        (r"\b(?:all|only|every|exactly|both|never|always|single)\b|\b\d+\b", "counted"),
        (r"[\w./-]*[\w-]\.(?:py|md|toml|json|ya?ml|txt|cfg)\b", "cites-a-path"),
        (r"`[A-Za-z_][\w.]*`|\b[a-z_]+\.[a-z_]+\(", "names-a-symbol"),
        (r"\bnot\b|\bnever\b|\bcannot\b|\bwithout\b", "negation"),
        (
            r"[\""]|\bwhy\b|\bbecause\b|\brather than\b|\bdecision\b",
            "quote-or-rationale",
        ),
    ]
]
HOLDS = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def blocks(src):
    out, run, prev, rows = [], [], -9, src.splitlines()
    try:
        toks = [
            t
            for t in tokenize.generate_tokens(io.StringIO(src).readline)
            if t.type == tokenize.COMMENT
        ]
    except tokenize.TokenError, IndentationError, SyntaxError:
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


for f in [a for a in sys.argv[1:] if not a.startswith("-")]:
    if not Path(f).is_file():
        print(f"# missing: {f}")
        continue
    lines = Path(f).read_text(encoding="utf-8", errors="replace").splitlines()
    for a, b, kind in blocks("\n".join(lines)):
        text, n = "\n".join(lines[a - 1 : b]), b - a + 1
        tags = [f"OVER-CAP:{n}"] if kind == "comment" and n > CAP else []
        tags += [f"docstring:{n}L"] if kind == "docstring" and n > 2 else []
        tags += ["over-width"] if any(len(x) > WIDTH for x in lines[a - 1 : b]) else []
        print(
            f"{f}:{a}-{b}\t{kind}\t{n}L\t{','.join(tags + [t for p, t in TAGS if p.search(text)])}"
        )
```

Paste the block list into every reviewer prompt, then resolve what the sweep only located: every
`cites-a-path` against the tree, every symbol against the names the code DEFINES. ! Four things
measurement settled about that corpus. Build it from the **AST, never raw text** -- text built from the
file contains the comments being checked, so the check always passes. **Exclude `.md`/`.txt` and every
test file**: a doc discussing a deleted symbol vouches for it, and a negative assertion (`assert "x" not
in y`) makes a dead name read as alive -- that masked three real obituaries and 4 of 7 known ghosts. A
**virtualenv poisons it**: skip any directory holding `pyvenv.cfg`. The **head** segment of a dotted
name must resolve, not any segment, or `Dead.meta` passes on `meta`.

! **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar` is
written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Measured: an identifier grep found ten
mentions, all correctly dated tombstones, and missed an eleventh written with a hyphen -- the only
present-tense claim in the set; a clean grep reads like a clean file. ! **A resolved citation is
not a verified one** -- it asserts something *about* its target, so open it or mark the finding
`SUSPECTED`. And **nothing the sweep emits is a verdict**: signals are reasons to look, and a block with
no signal can still be the worst prose in the file.

## Phase 1 -- four reviewers, each over the WHOLE list

Launch four subagents in one message; give each the file list, the sweep output, the `cap`, the
acquittal list, and one angle. **Tell each, in words, to return a line for every numbered block.**
Overlap is signal, not waste -- a finding all four report is almost always real. Each finding carries
`file:line` -- the line of **the offending sentence**, not the top of a forty-line docstring -- the exact
claim, the code or test line that settles it, and `CONFIRMED` (both sides read) or `SUSPECTED` --
measured, 196 of 202 came back CONFIRMED once that was asked for.

! **Reviewers are READ-ONLY; say so**, and name two lists: files UNDER REVIEW, which a proposal may
target, and files given only as REFERENCE, which it never may -- one reviewer handed a contract document
as reference proposed three edits *to the contract*, and they were applied.

### Currency -- does this describe the program as it is now? (~45% of yield)

Git holds what the code used to be; a comment narrating its own history does git's job badly. Walk each
block past: **1 ghost name** -- every symbol, file, flag or constant still exists? **2 dangling
citation** -- the cited test/path/doc resolves? a `file.py:NN` citation never survives a refactor, flag
on sight. **3 dated ruling or review label** -- a date, "finding B4", "fix round 2", "task-8.6"? **4
history narration** -- "used to", "was changed", "we tried". **5 retired mechanism cited as live** -- does
anything still read the gate it describes? **6 retracted fact** -- the source of truth has withdrawn it.
**7 stale count** -- re-derive it, and re-derive the **set** first; a counted claim is unverifiable
unless it names the population it counts over (a pass correcting a false count produced a
differently-false one). **8 quotation or attribution** -- a name and a quotation are provenance, and
provenance lives in the history. **9 drifted copy** -- stated elsewhere too, and the copies disagree.

### Functionality -- does the commentary match what the code does? (~30%)

Read the name, the signature and the docstring, then **read the body**: the flagship false claims are
contradicted two or three lines below themselves. **10 contradicted description.** **11 summary-line
drift** -- the only part most readers see, and it drifts silently because changing a return type does not
change the sentence describing it. **12 signature drift** -- an `Args:`/`Returns:`/`Raises:` entry that
does not exist or is in the wrong shape. **13 name / docstring / body disagreement** -- report the fork
(the docstring grows until the NAME is wrong, or the function shrinks); do not choose it. **14 partial
universal** -- "every X does Y": enumerate the Xs, never reword one without enumerating. **15 inverted
direction or qualifier** -- `<` vs `<=`, mutation, scope word. **16 prose vs a live string** -- a
`warn`/`assert` message that still says what this comment now denies. **17 superlative or collective** --
"the only entry point", "single source of truth", "these constants": resolve against its own file. **18
body comments read as ONE sequence** -- end to end they are the most honest description of the function;
a run that *sequences* ("now I need to...") instead of constraining is a to-do list in the body.

! **Prose that DESCRIBES behaviour is wrong far more often than prose that PROHIBITS**, and they fail
differently: a description disagreeing with the code -> the comment is wrong; a prohibition disagreeing ->
the code broke the rule, file that. **19 negated description** -- a description must be POSITIVE, because
*"NOT the kernel call site"* never lands on a side you can verify.

### Coverage -- does anything read what the prose describes? (~15%)

The class that **licenses deletions**, and disproportionately wrong. "Pinned by X", "guarded by Y",
"asserted in Z", "the only call site", "nothing checks this" -- each authorises the next person to delete
something, so the claim is checked, never read: does the guard exist, and would it fail if the claim
were false? Does the constant have a reader, the function a caller outside the tests, the hazard a live
trigger? For data reached by key rather than name, grep the STRING. The dangerous cell is **claims a
guard / no guard exists**: a deletion justified by coverage nobody can find reads as safe for exactly
that reason. It fails both ways -- a real guard was deleted on a pointer to a test that never existed,
and a comment calling a live config value decorative nearly licensed deleting what three sites read. !
**A citation your checker cannot parse is worse than one it parses and rejects** -- the parseable wrong
one gets fixed, the unparseable one accumulates while reading as terse authority. ! But **an unreachable
hazard is not automatically a `drop`**: a precaution's value is having no trigger; it stays, compacted
in place.

### Placement and shape -- is this prose where its subject is, and in the right form? (~10%)

**20 non-local rule** -- it constrains something else (a rule at the top of a class that really
constrains two literals two hundred lines down). **21 backwards-facing half** -- the block's later half
narrates what came before it. **22 two subjects welded together** -- a live constraint sharing a
paragraph with the story of where it came from; the ordinary case, not a rare one. **23 stranded run** --
after an unconditional `return`, between two statements annotating neither, or belonging to the
declaration four lines down. **24 missing comment** -- a non-obvious constraint nothing states, where
getting it wrong is silent. **25 module docstring vs module** -- reading only the top-of-file prose and
banners: two announced subjects, or a docstring describing a fraction of its file. **26 ownerless rule**
-- one rule re-explained at several sites because no function holds it; report as code shape. Test what
survives: **if this code changed, would the comment become wrong, and would anyone notice?**

Form: **27 over-cap `#` run**, counted by CODE not by blank lines, free markers (`TODO`, `FIXME`,
`HACK`, `XXX`, `BUG`) excluded. **28 over-wide line** -- formatters never reflow comments, so a line cap
is evadable by widening. **29 rationale in a docstring** -- ! **a docstring carrying a date, a ruling, a
quotation or a paragraph of why-the-design-changed is a finding AT ANY LENGTH. It is a FORMAT failure,
not a length one** -- and it is exactly where an evicted `#` block relocates, so a length-only rule
launders history into the one place no cap reaches.

## Phase 2 -- one verdict per block

Dedup, then rule. **Is it CHECKABLE** from the code as it stands, without archaeology? **Is it
NECESSARY** -- would someone changing this code make a *worse decision* without it? Not "is it
interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader needs | **drop** -- it narrates the code |
| **not checkable** | **move** -- rationale, unverifiable here | **drop** -- history |

! **Truth is not one of the questions, and that is the point.** History that is *correct* reads as
earning its place and does not; accuracy is why it was never deleted, not a reason to keep it.

**Five verdicts, not four.** `keep`, `drop`, `move`, `compact` -- and **`correct`**, for a block that
must survive but says something false. Without it a reviewer files a true-but-stale claim under `keep`
(one real pass had 82 such blocks and nowhere to put them) and the falsehood ships with a passing
verdict. `compact` is what you do to a `keep` or a `move`'s remainder; for a `move`, name the
destination and send the **WHOLE block, including the half that stays in the code** -- a document holding
only what was discarded is a deletion list, not a record.

**Rule on SENTENCES, not on blocks.** ! **A single `keep` sentence launders every sentence around it** --
ruling `keep` because *part* is load-bearing is the signal to descend a level. **Name the repair and
check it separately from the detection**: a stale count is re-derived or deleted, never softened to
"most"; a mis-formatted live citation is reformatted, never dropped. ! **Account for every digit you
propose deleting** -- the commonest defect a compaction pass introduces is a measurement replaced by an
adjective, and it always looks like a legitimate trim. **Before proposing a CHANGE, read the prose
around it**: a deliberate design usually says so directly above itself, and one finding reopened a
decision closed six weeks earlier because the reason sat one line up. Read the neighbours before you
*change*, not before you *report* -- a neighbour asserting the same false thing is two findings.

## Calibration

- **A block failing one class usually fails three**, with different verdicts and different lines.
- **Defects cluster where somebody already edited** -- a block cut in half with the falsehood in the
  surviving half; three of four siblings fixed. Find one, sweep that class through the whole file.
- **Prose no guard has ever measured is defective at a high rate**: a tree entering a guard's scope held
  eleven dangling citations against **zero** in the guarded tree, same repo, same authors.
- **Report every block that fails a check and no block that does not.** Padding and pruning cost the
  same, but a tidy short list is the commoner failure: in one measured slice **59% of the prose blocks
  in six files** were rewritten by the next pass, so ten findings there is a miss, not selectivity.
- **A tail is not a head.** Where a cap nearly holds, most remaining runs are over by one: cut the
  single least-checkable line, and **do not re-author a block already true, current and on-subject**.

## Phase 3 -- present. Always.

**This skill never edits. It ends with the verdict list** -- grouped by verdict, most consequential
first, the replacement inline for every `compact` and `correct`, and the coverage line *N swept, M
findings, K acquitted*. Then stop. ! **Even when the human names the edit** -- "cap them", "go do it" --
the deliverable is the report: *"Report only, per the skill -- say the word and I'll apply the verdicts
you accept."* An imperative is not authorization, and **an edit applied is a verdict never ruled on**:
before this rule, two runs on near-identical prompts split, one report, one 846-line diff.

## Rails for the pass that applies these -- you are not that pass

- **A block is bounded by CODE, not blank lines** -- else 9 lines become 6 + blank + 3.
- **Never change code, a docstring's meaning, or a string literal**; prove it by diffing every
  non-comment line, which caught two cuts that ran on and took real code.
- **`count == 1` or refuse the whole file**, `old` text built programmatically, width checked as well as
  line count, the file's own line ending kept. **Extract before you cut** on a `move` -- the other order
  lost the text three times.
- **Grep repo-wide before changing any number, name or path**, config and docs included, and **re-read
  what you wrote**: a pass that cut seven obituaries wrote seven new ones.

**Every example above is invented or anonymised. Keep it that way** -- quoting a real comment teaches
recognition of *that comment* rather than the shape, and rots into an obituary of its own. **Add to the
checklist; never re-partition it.**
