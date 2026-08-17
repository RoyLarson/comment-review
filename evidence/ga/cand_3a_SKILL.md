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

`/comment-review [cap] [target]` -> census -> 4 angles -> a verdict per block -> you decide.

## The subject is the prose, not the program

Every verdict you return is a verdict on a comment. You will still notice code problems -- list them
in a separate section, one line each, and **never** give a code concern a prose verdict.

| a COMMENT finding | a CODE finding -- name it and leave it |
|---|---|
| the comment says it reads one field; it reads three | it should not read three fields |
| the comment names a symbol that no longer exists | the symbol should be restored |
| the comment claims callers `grep` cannot find | the function is dead, delete it |

! **A reviewer straying into correctness is where this skill's worst output comes from.** Twice, a
reviewer read a valid `except` form and reported the file "cannot compile" -- wrong, and volunteered
while reviewing prose. If your claim is about whether the code *runs*, it is not your finding.

* **The governing law: LOOK WHERE NOTHING ASSERTS.** Every false statement found in a real
burn-down sat where no test, type or lint rule could reach -- not the oldest prose, not the longest.
False clauses sat *inside* blocks whose other sentences were true, same voice, same indentation; one
split mid-sentence. A green suite is no evidence about prose: a comment beside a deleted thing is
green *because* the thing is gone.

## Arguments

**`cap`** -- an integer, optional: the most lines one `#` run may take, passed to every angle. **This
skill has no cap of its own and must not invent one.** If the repo publishes one in a guard, use
that, say where you got it, and read *how it measures*. With none, report the longest block found.
**`target`** -- a path; defaults to the diff.

## Phase 0 -- scope, then census every block

Scope: `git merge-base` against the upstream or default branch, else `HEAD~1`, else the path named;
add `git diff --name-only HEAD` when the tree is dirty or the range is empty. That gives a **file
list**. Review **all commentary in those files, not just the changed lines** -- comment debt is
cumulative and mostly pre-existing, and the 54-line block that has sat above a four-line expression
for months is the finding worth having.

Then enumerate. Sampling is how a review returns nine findings from a file with ninety blocks.

```python
# census.py <cap> <file>...  -> "path:line kind nlines tags"   (stdlib only, no repo assumptions)
import ast, io, re, sys, tokenize

TAGS = [
    ("date", r"\b(19|20)\d\d[-/]\d\d\b"),
    ("attrib", r"\b(said|says|ruled|ruling|per |his |her |their )\b|[\""][^\""]{15,}"),
    (
        "hist",
        r"\b(used to|no longer|previously|formerly|retired|renamed|was changed|deleted|"
        r"restored|reverted|supersed\w+|until 20|had been|stopped being)\b",
    ),
    (
        "review",
        r"\b([Rr]ound[- ]?\d|finding \w{0,3}\d|Part [AB]\b|fix wave|task[- ]?\d|"
        r"phase \d|review\b|MAJOR|CRITICAL|audit)\b",
    ),
    ("cites", r"[\w./-]+\.(py|md|toml|json|ya?ml|txt)\b|\btest_\w+|TODO/|docs/"),
    ("count", r"\b\d{2,}\b|\b\d+(\.\d+)?%|\b\d+ of \d+\b"),
    (
        "cover",
        r"\b(guard\w*|pinned|asserted|enforced|checked by|covered by|verified|"
        r"the only|nothing asserts)\b",
    ),
    ("meas", r"\b(measured|reproduced|repro\b|simulated|hand-worked)\b"),
]


def blocks(path):
    try:
        src = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        print(f"{path}: unreadable, skipped", file=sys.stderr)
        return []
    lines, out = src.splitlines(), []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        tree = None
    holders = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    for n in ast.walk(tree) if tree else []:
        b = getattr(n, "body", None)
        if not isinstance(n, holders) or not b:
            continue
        e = b[0]
        v = getattr(e, "value", None) if isinstance(e, ast.Expr) else None
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            out.append([e.lineno, "docstring", e.end_lineno - e.lineno + 1])
    run = None  # a run is bounded by CODE, not by blank lines
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if s.startswith("#"):
            run = run or [i, i]
            run[1] = i
        elif s:
            if run:
                out.append([run[0], "comment", run[1] - run[0] + 1])
            run = None
    if run:
        out.append([run[0], "comment", run[1] - run[0] + 1])
    try:  # TRAILING comments are blocks too, and are usually missed
        for t in tokenize.generate_tokens(io.StringIO(src).readline):
            if (
                t.type == tokenize.COMMENT
                and lines[t.start[0] - 1][: t.start[1]].strip()
            ):
                out.append([t.start[0], "trailing", 1])
    except tokenize.TokenError, IndentationError, SyntaxError:
        pass
    return sorted(out)


def census(path, cap):
    lines = (
        open(path, encoding="utf-8", errors="replace").read().splitlines()
        if __import__("os").path.exists(path)
        else []
    )
    for start, kind, n in blocks(path):
        text = "\n".join(lines[start - 1 : start - 1 + n])
        tags = [t for t, p in TAGS if re.search(p, text)]
        if kind == "comment" and cap and n > cap:
            tags.append("over-cap")
        if kind == "docstring" and n > 9:
            tags.append("long-docstring")
        print(f"{path}:{start} {kind} {n} {','.join(tags) or '-'}")


cap = int(sys.argv[1]) if sys.argv[1:] and sys.argv[1].isdigit() else 0
for p in sys.argv[2 if cap else 1 :]:
    census(p, cap)
```

**Every tag is a reason to LOOK, and in code prose most of them are a defect on sight:**
`date` / `review` / `attrib` -- a date, a round label, a quoted ruling: the changelog living in the
source. `hist` -- present-tense the rule and lose the past. `cites` -- **resolve every one**; a dead
citation sends the next reader to grep for nothing and reads as *their* mistake. `cover` --
**checked, never read**: this class licenses deletions. `count` -- re-derive it or delete the number.
`over-cap` / `long-docstring` -- shape a reader feels and a linter cannot see.

! **A clean tag line is not a pass**, and no tag is a verdict. The tags find the mechanical half.

## Phase 1 -- four angles over the census

Four subagents in ONE message if the census is large, else yourself one angle at a time. Give each
the file list, the census, and the `cap`. ! **Reviewers are READ-ONLY -- say so in the prompt**; four
agents editing one file is a race whose loser's edits vanish, and a reviewer that fixes what it
finds has destroyed the finding. **Name the files UNDER REVIEW and the files given as REFERENCE
separately** -- a reviewer handed a contract doc as reference once returned edits to it, and they
landed. Each finding returns `file`, `line`, the exact claim, **the code or test line that settles
it**, and `CONFIRMED` (both sides read) or `SUSPECTED`. Overlap between angles is signal.

### Currency -- does this describe the program as it is now? (~45% of findings)

Git holds what the code used to be. A comment narrating its own history does git's job badly. Flag
dated rulings, round labels, "this used to...", "no longer", "previously" -- and the sharpest form,
**obituaries**: a name, file, test or flag that exists nowhere.

! **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar`
is written `foo-bar`, `foo bar`, `FooBar`, "the barrer". Measured: an identifier grep found ten
mentions, all correctly dated tombstones, and missed an eleventh written with a hyphen -- the only
present-tense claim about the dead path in the set. A clean grep reads as a clean file.

**Every number is a citation.** A count is unverifiable unless it names the SET it counts over, and
re-deriving one means re-deriving the set first. A pass correcting a false number produced a
differently-false one because it re-counted the wrong population.

### Functionality -- does the commentary match what the function is for? (~30%)

Read name, signature, docstring, then the body. Flag a return shape the code no longer returns, an
`Args:` entry for a vanished parameter, a documented exception nothing raises, a summary saying
"Yield" over a function that returns. The **summary line** drifts silently: changing a return type
does not change the sentence describing it.

**Coverage claims are the class that licenses deletions and are disproportionately wrong.** "pinned
by X", "guarded by Y", "the only call site", "nothing asserts this" -- grep the cited name every
time. The dangerous cell is a deletion justified by coverage nobody can find, which reads as safe
for exactly that reason; a real guard has been dropped on a pointer to a test never written.

**Reachability lives here, not in a fifth angle.** Ask whether anything READS the thing the prose
describes: a constant with no readers whose comment states an invariant, an exemption from a retired
rule, a hazard justifying code nothing can trigger. That prose is not stale -- it is furniture.

**Then read the body's comments as one sequence.** Individually each may be true; end to end they
are the most honest description of the function. A comment that **sequences** ("now I need to...",
"then we...") rather than **constrains** is a to-do list left in the body. ! **Report the mismatch; do
not resolve it** -- the docstring grows until the NAME is wrong, or the function shrinks to its name.

### Locality -- does this comment belong to the line it sits on?

A block points DOWN; a trailing comment points AT its declaration. The finding is a comment about
something **else**: a rule at the top of a class that really constrains two literals 200 lines down;
a block whose later half turns back to narrate what came before; a run left orphaned when its line
moved. Second test: **if this code changed, would the comment become wrong -- and would anyone
notice?** Flag the inverse too: a non-obvious constraint with no comment, where getting it wrong is
silent. **Refactoring drift is this angle's biggest yield.**

### Module coherence -- do the comments say this is one module?

Read only the module docstring, banners and top-of-file prose. Flag prose announcing two or three
subjects, banners reading like chapter breaks, a docstring enumerating unrelated responsibilities to
be accurate, one named for the **occasion** that produced it, and **the same rule re-explained in
several modules** -- that means no function owns it, which is *why* the comments got long.

## Phase 2 -- one verdict per block

**Is it CHECKABLE?** Could a reader confirm or refute it from the code as it stands, without
archaeology? **Is it NECESSARY?** Would someone changing this code make a **worse decision** without
it -- not "is it interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader verifies | **drop** -- the code already says it |
| **not checkable** | **move** -- real rationale, unverifiable here | **drop** -- history |

! **Truth is not one of the questions.** *"Moved here from `x.validate` when that module was
deleted"* is accurate, uncheckable, and changes nobody's decision. Accuracy is why history was never
deleted, not a reason to keep it. **Rule on sentences, not blocks**; ! **a single `keep` sentence
launders every sentence around it** -- if part of a block is load-bearing, descend a level.

| the comment is a... | and it disagrees with the code -> |
|---|---|
| **description** | the comment is wrong -> `drop`, or `correct` it |
| **prohibition** | the code broke the rule -> file it; **the code moves, not the prose** |

**Five verdicts.** `compact` is what you do to a survivor (propose the replacement text inline).
`move` names a destination and ! **gets the WHOLE block, including the half that stays in the
code** -- a doc holding only the discarded half is a deletion list, not a record. `correct` is for a
block that must be FIXED rather than cut: the constraint is real, the sentence stating it is false.

* **A description written as a negation is a FORM defect on its own.** You cannot check "X is not
the case"; rewrite it positive. A **prohibition** may stay negative. Measured: a compressing pass
took negation from 17% of removed lines to 22% of what it wrote back -- compression *concentrates*
negations. And **a docstring carrying a date, a ruling, a quotation or a rationale paragraph is a
finding at ANY length** -- that is a FORMAT failure, not a length one.

### What must be KEPT -- a spec that only says what to cut deletes the load-bearing half

- **Hand-worked derivations** -- what stops an assertion being an echo of the implementation.
  * Over cap, **move one into the DOCSTRING before compacting it**: a `#` run is capped because it
  interrupts code; a docstring sits at a boundary. One 16-line derivation moved that way took a file
  from 10 excess lines to 0 with every digit intact.
- **Premise guards**, and **the discriminator that scopes a claim** without which it is over-read.
- **Why a fixture or constant is shaped oddly**, written ON the element; and **a comment naming its
  own expiry condition**, so the next reader does not have to judge.
- **A warning against a plausible wrong move -- ONLY where nothing goes red.** Where a test does
  catch the move it is a time-saver, not a guard, and it is `compact`. No third category of
  "warnings"; calling one is the laundering failure above.

## Phase 2b -- ACQUIT, out loud, and count it

! **This is the half that does not survive being copied, and it decides the review.** Two reviews
using the same angles, the same words and the same census swept the same blocks: one acquitted 47%
and was right about 78% of what it raised; the other acquitted 14% and was right about half. Same
vocabulary, opposite instrument. **Reasons to STOP are as load-bearing as reasons to flag, and they
are the ones a reader of this file skims.**

So: **every block gets an explicit `raise` or `acquit`, and you report both counts.** Acquit on one
of these named reasons, and no other -- write the reason beside the block:

- **COMPLIES** -- inside the cap, no date, no ruling, no round label, no unresolved citation, no
  counted claim, no coverage claim. It is already the shape the rule asks for.
- **MECHANICAL** -- a banner, a shebang, a step label (`# 1) same pattern`), a one-line restatement
  of the signature. Nothing to be wrong about.
- **LOCAL AND TERSE** -- a trailing annotation on the thing it annotates, one line, checkable at a
  glance. Rewriting it moves noise around.
- **CHECKED ELSEWHERE** -- the claim is asserted by a guard you found and read. Cite it.
- **DELIBERATE, AND IT SAYS SO** -- the design is stated directly above itself. ! Read the prose
  immediately around a block before raising it: one finding -- "this sums two different units" -- was
  true, and the line above explained why, dated; the TODO it produced reopened a closed decision.

! **The budget is the point.** Every block you raise is one you chose over another you did not.
Raising a block whose only fault is that it is *long* while a false coverage claim three lines down
goes unread is the trade this phase exists to stop. If your raise-rate is above ~70% of blocks
censused, you are not reviewing, you are transcribing.

! **And do not pad the other way.** In one measured slice **59% of the prose blocks in six files**
were rewritten by the next pass, so a ten-finding report on a file of that shape is a miss, not
selectivity. **`keep` is a real verdict**; a review returning mostly `keep` is a good one.

! **The tail is not like the head.** Where a cap is nearly met, most remaining blocks are one line
over: cut the single least-checkable line, and **do NOT rewrite a block already true, current and
on-subject.** ! **"This tree looks fine" from a reviewer who has only read guarded code is not
evidence** -- a tree entering a guard's scope held 11 dangling citations against 0 in the guarded
tree, same repo, same authors, same period.

## Phase 3 -- present. Always.

**This skill never edits. It ends with the verdict list.** Report grouped by verdict, most
consequential first, with proposed replacement text inline for every `compact` and `correct`; then
the census totals (blocks read, raised, acquitted, longest found); then code concerns, one line
each; then stop. ! **Even when the human names the edit** -- "cap them", "fix these", "go do it" --
the deliverable is the report: *"Report only, per the skill -- say the word and I'll apply the
verdicts you accept."* **An edit applied is a verdict never ruled on.** Before this rule, two runs
on near-identical prompts split: one returned a report, the other an 846-line diff.

**Rails for the pass that applies these** -- it usually runs without this skill loaded:

- A comment block is bounded by **CODE, not blank lines**, or a 9-line block becomes 6 + blank + 3.
- **Change no code, no string literal, no docstring's meaning.** Prove it: diff every non-comment
  line against the pre-edit file and confirm zero differences. That caught two cuts that ran one
  line too far and took real code with them.
- **Extract before you cut** on a `move`; the other order loses the text on any interruption.
- **Apply with `count == 1` or refuse the whole file**, with `old` built programmatically rather
  than transcribed. Check each replacement's **width** as well as its line count, and preserve the
  file's own line ending, or a 3-line prose edit lands as a whole-file diff.
- **Re-read what you wrote.** A pass that cut seven obituaries wrote seven new ones, the same one
  twice in one file, and wrote over-length blocks while removing over-length blocks.

`/simplify` reviews code structure and applies what it finds. `/code-review` hunts correctness bugs.
This one reviews prose and **only ever proposes**. **Every example here is invented or anonymised.
Keep it that way** -- quoting a real comment teaches recognition of *that comment* rather than the
shape, and it rots into an obituary the day someone acts on the finding.
