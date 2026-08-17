---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched -- census every prose block, walk
  each past a checklist of defect classes (ghost names, dangling citations, dated history, stale
  counts, coverage claims, descriptions the code contradicts, misplaced rules, over-length blocks) --
  and return every block either as a finding with a proposed verdict (drop / move / compact /
  correct / keep) or as a named acquittal, for the human to rule on. Use this whenever comments or
  documentation are the subject: after a task that added or edited commentary, when a file's comments
  have drifted from what the code now does, when someone says a comment is too long or out of date or
  "isn't this history", when reviewing a diff for its prose rather than its logic, before a docs or
  comment burn-down, or when asked whether a module still reads as one module. Trigger on phrasings
  that never say "comment review" -- "these comments are getting out of hand", "does this docstring
  still match", "is this comment still true", "clean up the narration in this file", "why does this
  file need so much explaining" all mean run this. It is NOT /simplify (which reviews code structure
  and applies its fixes) and NOT /code-review (which hunts correctness bugs) -- this one ONLY EVER
  PROPOSES and never edits anything, not code and not even the comments it rules on. Run it even when
  the request sounds like an instruction to cut ("cap these", "clean this up"): the deliverable is
  still the verdict list, and applying is a separate step. It is explicitly not a reviewer's job to
  judge whether the code works: code concerns get raised in a line and left.
---

# comment-review

`/comment-review [cap] [target]` -> census every block -> checklist -> a verdict or a named acquittal
for **every** block -> you decide.

Two mechanisms carry this skill and they are independent: the **census** guarantees every block is
SEEN, the **acquittal list** that every block is RULED ON. Silence about a block is a gap in the
review, not a pass -- a block absent from your report is a claim you never made.

**The subject is the prose, not the program.** It is not a reviewer's job to decide whether the code
works. You will still notice code problems -- the comment says it reads one field and it reads three;
the function it names is dead. Raise each in one line in a separate section and move on: **raise a
concern, do not open an investigation**, and never give a code concern a prose verdict. ! Measured: a
reviewer read `except ValueError, TypeError:` and reported the file "cannot compile" -- a claim about
the *program*, made while reviewing *prose*, and wrong. If your claim is about whether the code RUNS
it is not yours; make it anyway and you owe it an `ast.parse` first.

## Arguments

- **`cap`** -- integer, optional: the most lines one `#` run may take. **This skill has no cap of its
  own and must not invent one.** A cap the repo publishes (a lint config, a hygiene test) wins -- read
  how it *measures*, not just its number. With none, judge, and report the longest block found.
- **`target`** -- a path, optional; defaults to the files in the diff.

## Phase 0 -- scope, then census

Scope from a **merge base**, never `A...B` between two tips: `git merge-base HEAD @{upstream}` (or the
default branch), then `git diff --name-only <base> HEAD`; fall back to `HEAD~1`, and add
`git diff --name-only HEAD` when the tree is dirty. ! Check which range returned something -- an empty
range and a one-commit range both *succeed* and quietly review less than you meant. Review **all the
prose in those files, not just the changed lines**: comment debt is cumulative and mostly pre-existing,
and the diff says which files are live, not what to read inside them. Then enumerate the blocks:

```python
"""census.py [--cap N] FILE...  ->  path:start-end kind nlines flags"""

import ast, re, sys
from pathlib import Path

HOLDER = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
FLAG = {  # a hit is a reason to LOOK, never a verdict; extend freely, delete nothing
    "date": r"\b(19|20)\d\d([-/]\d\d?){0,2}\b",
    "hist": r"used to|no longer|formerly|previously|renamed|retired|superseded|was changed"
    r"|moved (from|to|out)|reverted|retract|had been|we tried|before the fix",
    "cover": r"guard|pinned|assert|covered|enforc|checked by|proven|mutant|call site|caller"
    r"|test_|tests?/|verified|catches|the only",
    "count": r"(?<![\w.])\d|\b(every|all|each|both|exactly|none|only|single)\b",
    "quote": r"[""\"]|\bsaid\b|\bruled\b|\bdecided\b|\bbecause\b|\brationale\b|\bdeliberat",
    "cite": r"[\w./-]+\.(?:py|md|toml|json|ya?ml|txt|rs|ts|go)\b|docs?/|\bhttps?://",
    "neg": r"\b(not|never|cannot|nothing|must not|does not|doesn't|isn't|instead of)\b",
}


def blocks(src):
    """Every `#` run (bounded by CODE, not by blank lines), trailing note and docstring, as spans."""
    lines, out, run = src.splitlines(), [], []
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if s.startswith("#"):
            run.append(i)
            continue
        if run:
            out.append((run[0], run[-1], "run"))
            run = []
        if s and "#" in ln:
            out.append((i, i, "trail"))
    if run:
        out.append((run[0], run[-1], "run"))
    try:
        tree = ast.parse(src)
    except SyntaxError, ValueError:
        return sorted(out)  # not Python, or unparseable: the `#` runs still stand
    for n in ast.walk(
        tree
    ):  # test HOLDER first: an IfExp also has a `body`, and it is not a list
        if isinstance(n, HOLDER) and n.body and isinstance(n.body[0], ast.Expr):
            b = n.body[0]
            if isinstance(getattr(b.value, "value", None), str):
                out.append((b.lineno, b.end_lineno, "doc"))
    return sorted(out)


args = sys.argv[1:]
cap = int(args[args.index("--cap") + 1]) if "--cap" in args else 0
for p in [a for a in args if a.endswith(".py")]:
    try:
        src = Path(p).read_text(encoding="utf-8", errors="replace")
    except OSError:
        print(f"{p}: unreadable, skipped", file=sys.stderr)
        continue
    lines = src.splitlines()
    for s, e, kind in blocks(src):
        f = [
            k
            for k, rx in FLAG.items()
            if re.search(rx, "\n".join(lines[s - 1 : e]), re.I)
        ]
        if kind == "run" and cap and e - s + 1 > cap:
            f.append("over-cap")
        print(f"{p}:{s}-{e} {kind} {e - s + 1} {','.join(f) or '-'}")
```

Read-only, stdlib-only, assumes nothing about the repo, skips a path it cannot read. **Tick blocks off
the list**; the census is your denominator: *"380 blocks, 70 acquitted"* is answerable, *"here are some
findings"* is not. ! **A clean flag line is not a pass** -- the flags find the mechanical half, and
the other half, prose describing behaviour the code no longer has, is found only by reading the body
and is wrong far more often. **Prose that PROHIBITS ages better than prose that DESCRIBES.**

## Phase 1 -- walk each block past the checklist

One reader, every class, per block -- not one reader per class: angles overlap and leave gaps between
them, and a reader holding one lens reads for what that lens sees. Split across subagents by **file**
if the census is large, never by class, and tell them: **read, grep, report; never edit.** Report one
finding per offending *sentence*, at that sentence's line -- not the top of a forty-line docstring.

### A. Currency -- does this describe the program as it is now?

1. **Ghost name.** Every symbol, file, flag or constant named here still exists? Stop: it does.
2. **Dangling citation.** Does the cited test / path / doc resolve today? Stop: it resolves. A
   `file.py:NN` citation never survives a refactor -- flag on sight.
3. **Dated ruling or review label.** A date, an id, a round number? Stop: it is a data format.
4. **History narration.** "used to", "was changed", "before the fix", "we tried", "no longer"? Stop:
   it names an expiry condition for the code itself, which is about the future.
5. **Retired mechanism cited as live.** Is that gate / constant / flag still read? Stop: grep finds a
   real reader, config and string literals included.
6. **Retracted fact.** Has the source of truth withdrawn this? Stop: you opened it, it still says so.
7. **Stale count.** Re-derive it: same answer? Stop: it holds. If nothing asserts it, `drop` it.
8. **Quotation or attribution.** Does it quote a person, or record who decided? Stop: never --
   provenance lives in the history.
9. **Drifted copy.** Stated elsewhere too, and do the copies still agree? Stop: this is the owning
   statement, or the others cite it instead of restating it.

! **Grep the STEM, not the identifier** (1, 5, 9): prose does not obey identifier spelling -- a dead
`foo_bar` is written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Measured: an identifier grep
found ten mentions, all correctly dated tombstones, and **missed an eleventh written with a hyphen --
the only present-tense claim about the dead path in the set.** A clean grep reads like a clean file.
! Build the live-name corpus from the **AST**, excluding `.md`/`.txt` and every test file -- a doc
discussing a deleted symbol vouches for it (three obituaries suppressed), and a test's
`assert "x" not in y` makes a dead name read as alive. Skip directories holding `pyvenv.cfg`.

### B. Truth -- does the code do what the prose says?

10. **Contradicted description.** Read the body: does it do this? Stop: it does. ! If the prose is a
    **prohibition**, a disagreement means the CODE broke the rule -- file that instead.
11. **Summary-line drift.** Does the first line still name what the thing does and returns? Stop: it
    does. It is the only part most readers see -- check it every time.
12. **Signature drift.** Does every `Args:` / `Returns:` / `Raises:` entry exist, in that shape?
    Stop: it does, and says something the signature does not.
13. **Name / docstring / body disagreement.** Do the three describe one job? Stop: they do. Renaming
    is a CODE change -- report the fork, do not choose it.
14. **Coverage claim -- the dangerous cell.** "guarded by", "pinned by", "asserted in", "the only call
    site": does that guard exist, and would it fail if the claim were false? Stop: you opened it. This
    class **licenses deletions**, so it is checked, never read.
15. **Partial universal.** "every X does Y" -- enumerate the Xs and check each. Stop: all hold. Never
    keep, compact or reword one without enumerating.
16. **Count with no population.** Does the number name the set it counts over, so a stranger could
    re-derive it? Stop: it names the set and the query or the frozen input.
17. **Reachability.** Is what the prose describes still reached -- the branch, the caller, the config
    key? Stop: you found a live path. (Inside Truth; it is not a fifth angle.)
18. **Inverted direction or qualifier.** Does the stated direction, mutation, scope word or boundary
    (`<` vs `<=`) match the operator in the body? Stop: it matches.
19. **Negated description.** Written as `NOT X` where a positive statement exists? Stop: it is a
    prohibition aimed at the next author. Measured: a compression pass took negation from 17% of the
    lines it removed to **22% of what it wrote back**.

### C. Placement -- is this prose where its subject is?

20. **Non-local rule.** Does it constrain the line it sits on, or a literal 200 lines down? Stop: it
    faces its own declaration. Test: *if this code changed, would the comment become wrong -- and
    would anyone notice?*
21. **Backwards-facing half.** Does the later half narrate what came *before*? Stop: it faces down.
22. **Two subjects welded together.** A live constraint sharing a paragraph with the story of where it
    came from? Stop: one subject. The ordinary case, not a rare one.
23. **Module docstring vs module.** Does the top-of-file prose describe this whole file and only this
    file? Stop: it does. Two announced subjects is a finding about the module.
24. **Stranded or severed run.** Starts mid-clause, sits after an unconditional `return`, or belongs
    to the declaration four lines down? Stop: its subject is the next line.
25. **Missing comment.** A non-obvious constraint nothing states, error silent? Stop: the code says it.
26. **Ownerless rule.** Re-explained at several sites because no function holds it? Stop: one site
    owns it and the rest point there. Report as code shape; do not extract it.
27. **Refactoring drift.** Did the code move and leave this behind, or bring it and stop being true?
    Stop: they moved together. Placement's biggest yield.

### D. Form -- what the block is, not what it says

28. **Over-cap `#` run.** Longer than the cap, counted by CODE not by blank lines? Stop: at or under.
    Free markers (`TODO`, `FIXME`, `HACK`, `XXX`, `BUG`) do not count and do not split a run.
29. **Over-wide line.** Past the repo's configured width? Stop: none. Read the width, never assume.
30. **A docstring carrying a date, a ruling, a quotation, or a rationale paragraph** -- why the design
    changed rather than what the thing does. ! A **FORMAT** failure, so it is a finding **at any
    length**: "it is short" is not an acquittal. This is where an evicted `#` block relocates.
31. **Derivation stranded in a `#` run.** Hand-worked arithmetic interrupting code? Stop: it is
    already in the docstring. A derivation is KEPT -- moved, never compressed.

### The acquittal list -- every block gets a finding OR one of these, by name

`label` (a bare banner or one-word tag) * `states-the-signature` (a one-line docstring saying exactly
what the name and signature say) * `derivation` (arithmetic that stops an assertion being an echo) *
`only-guard` (a warning against a plausible wrong move that **nothing goes red** for -- mutant-check it;
where a test catches the move it is a time-saver and the verdict is `compact`) * `names-its-expiry` *
`premise-guard` (the assertion that makes the block above it safe) * `discriminator` (the clause that
scopes a claim, without which a reader over-reads it) * `odd-shape` (why a fixture or constant is
shaped oddly, written ON the element) * `deliberate-freeze` * `local-and-current` (present tense on its
own declaration, no citation, no count, no history).
! **There is no acquittal called "it is true", "it is short", or "it is well written."**

## Phase 2 -- one verdict per finding

Dedup findings on the same sentence, then ask two questions in order. **Checkable?** -- could a reader
confirm or refute it from the code as it stands, without archaeology. **Necessary?** -- would someone
changing this code make a *worse decision* without it. Not "is it true", not "is it interesting".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader verifies and needs | **drop** -- the code says it |
| **not checkable** | **move** -- real rationale, unverifiable in place | **drop** -- history |

! **Truth is not one of the questions, and that is the point.** *"Moved here from `x.validate` when
that module was deleted"* is accurate, uncheckable, and changes nobody's decision. Accuracy is why
history was never deleted, not a reason to keep it.

Two verdicts sit beside that table. **`correct`** -- the claim is in the right place and needed, and
simply wrong: a count re-derived, a direction inverted, a citation reformatted. Do not force these into
`drop`; one real pass produced 82 of them with nowhere to file them. **`compact`** -- same content,
fewer words: what you do to a `keep`, or to a `move`'s remainder. **Name the repair and check it apart
from the detection**: a stale count is re-derived or deleted, never softened to "most".

**Rule on sentences, not blocks.** ! **A single `keep` sentence launders every sentence around it** --
if you are keeping a block because *part* of it is load-bearing, descend a level; a block's most
defensible sentence is usually why the whole block survived this long. For **move**, name the
destination; ! **it gets the WHOLE block, including the half that stays in the code**. Mark each
finding `CONFIRMED` (you read both the prose and the code that settles it) or `SUSPECTED`: measured,
196 of 202 came back CONFIRMED once this was asked for, and reviewers withdrew weak candidates.

## Calibration -- how hard to press

- **The governing law: look where nothing asserts.** Every false statement found in a real burn-down
  was one no assertion touched -- not the oldest, not the longest, not the furthest from its code.
  False clauses sat *inside* blocks whose other sentences were true, same voice, same indentation.
- **A block failing one class usually fails three**, with different verdicts on different lines, and
  **defects cluster in blocks somebody already edited** -- a block cut in half with the falsehood in
  the surviving half; three of four siblings fixed. Find one, then sweep that class through the file.
- **Prose no guard has ever measured is defective at a high rate.** Measured twice: a tree entering a
  guard's scope for the first time held eleven dangling citations against **zero** in the guarded tree,
  same repo and authors. In one measured slice **59% of the prose blocks in six files** were rewritten
  by the next pass, so ten findings over three thousand lines has not looked.
- **A tail is not a head.** Where a cap already holds and blocks sit one line over, cut the single
  least-checkable line, and **do not re-author a block already true, current and on-subject**.
- **Read the adjacent prose first.** A deliberate design usually says so directly above itself: a
  function reported for summing two units had the reason one line up. **Do not pad** -- `keep` is a
  real verdict, returned *by name*.

## Phase 3 -- present. Always.

**This skill never edits. It ends with the verdict list** -- grouped by verdict, most consequential
first, replacement text inline for every `compact` and `correct`, then code concerns one line each and
the census counts. ! **Even when the human names the edit** -- "cap them",
"fix these", "go do it" -- the deliverable is still the report: *"Report only, per the skill -- say the
word and I'll apply the verdicts you accept."* An imperative is not authorization, and **an edit
applied is a verdict never ruled on.** Measured before this rule: two runs on near-identical prompts
split, one returning a report and the other an 846-line diff. Name which files are under review and
which are reference only -- a reviewer handed one as *reference* returned three proposals editing it.

## Rails for the pass that applies these -- hand them along; you are not that pass

- **Never change a line of code, a docstring's meaning, or a string literal.** Prove it: diff every
  non-comment line against the pre-edit file and confirm zero differences. **Apply on an exact match
  count of 1, or refuse the whole file**, building the `old` text programmatically.
- **Extract before you cut** on a `move` -- the other order lost the text three times. Check each
  replacement's width as well as its line count, and keep the file's own line ending.
- **Grep any number, name or path repo-wide before changing it**, config and docs included, or you get
  three of four siblings fixed. **Then re-read what you wrote** -- a pass that cut seven obituaries
  wrote seven new ones, and wrote over-length blocks while removing over-length blocks.

## A note for whoever edits this file

**Every example above is invented or anonymised. Keep it that way.** Quoting a real comment teaches a
reviewer to recognise *that comment* instead of the shape, and it rots the day someone acts on the
finding -- a hygiene skill carrying its own obituary. **Add to the checklist; do not re-partition it**:
a new class is a numbered row with a detection question AND a stopping rule, and a row without one
licenses flagging everything. Two proposals were measured and **refuted** -- `Provenance` as a
diff-against-history angle (it reverts correct fixes) and `Reachability` as a fifth angle (fold it into
Truth, as class 17).
