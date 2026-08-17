---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles -- currency,
  functionality, locality, module coherence -- after a mechanical census, and return each finding with
  a proposed verdict (drop / move / compact / correct / keep) for the human to rule on. Use this
  whenever comments or documentation are the subject: after finishing a task that added or edited
  commentary, when a file's comments have drifted from what the code now does, when someone says a
  comment is too long or out of date or "isn't this history", when a number or a citation in prose
  looks stale, when reviewing a diff specifically for its prose rather than its logic, before a docs
  or comment burn-down, or when asked to check whether a module still reads as one module. Trigger on
  phrasings that never say "comment review" -- "these comments are getting out of hand", "does this
  docstring still match", "is this comment still true", "clean up the narration in this file", "why
  does this file need so much explaining" all mean run this. It is NOT /simplify (code structure, and
  it applies its fixes) and NOT /code-review (correctness bugs) -- this one ONLY EVER PROPOSES and
  never edits anything, not code and not even the comments it rules on, because an edit applied is a
  verdict the human never got to rule on. Run it even when the request sounds like an instruction to
  cut ("cap these", "clean this up"): the deliverable is still the verdict list, applying is a
  separate step, and code concerns get raised in a line and left.
---

# comment-review

`/comment-review [cap] [target]` -> census -> 4 reviewers in parallel -> a verdict per block -> you rule.

## The rule that decides this skill's yield -- two things decide a block, one of them for free

- **FORM decides a block with no reading at all** -- a `#` run over the repo's cap, or a docstring
  carrying a date, a ruling, a quotation, a review-round label or a rationale paragraph. Each is a
  finding *at any length and however true it is*, because the defect is the shape, not the content.
  Rule these one line apiece and move on: numerous, cheap, and most of the list. ! **Deliberating
  over a 40-line dated docstring is the measured failure mode** -- it was already decided, and the
  thinking is subtracted from the blocks that needed it.
- **CONTENT decides everything else,** and that is where your whole judgement budget goes: the one-
  and two-line blocks, the short docstrings, the trailing labels. They are the majority of the
  census and the minority of the findings, so **reading them is how you choose, not how you pad.**

### You do not get to acquit by SILENCE -- or by reflex

Every block gets one line back: a finding, or a **named acquittal**; a block nobody mentioned is a
gap in the review, not one that passed. ! **But the acquittal LIST is only vocabulary; the acquittal
RATE is the skill.** Two reviews swept the same 419 blocks with the identical closed list below: one
acquitted 47% and one acquitted 14%, and the first was better by every measure. Reciting the reasons
while acquitting almost nothing is how this skill fails. Under a third of a never-swept file means
you are flagging shape rather than defect; over two thirds, searching rather than reviewing.

**The closed acquittal list** -- if none applies, the block gets a finding. Nothing is acquitted for
being short, true, well written, new, or sitting under a `!`:

- **`label`** -- one or two lines naming the line they sit on and claiming nothing beyond it.
- **`states-the-signature`** -- a short docstring in the present tense matching the name, the
  arguments and the return, citing nothing outside itself.
- **`derivation`** -- a hand-worked calculation whose digits are what stop an assertion being an echo
  of the implementation. Over cap it is a `move` **into the docstring**, never a `compact`.
- **`only-guard`** -- a warning against a plausible wrong move where **nothing goes red** if someone
  makes it. Verify that; if a test does fail, it is a time-saver and the verdict is `compact`.
- **`names-its-expiry`** -- prose naming the condition under which it stops being wanted.

### What earns a SHORT block a finding -- the inclusion list

Short blocks are where a review is won or lost, so this half is closed too. Raise one when it:

1. carries a **date, a ruling, a quotation, or a review-round label** (`finding 6`, `round 2`,
   `task-8.6`, `A6`, `Part B`) -- a pointer into a conversation the reader cannot reach;
2. **narrates history** -- "used to", "the old X", "before this existed", "arrived with", "now dead";
3. names something that **no longer exists** -- a symbol, module, path, flag or test (an obituary);
4. makes a **coverage, reachability or absence claim** -- "guarded by", "the only caller", "read by
   nothing", "already verified upstream", "a test can pin it";
5. asserts a **count or a superlative** with no population -- "thirteen violations", "the one
   consumer", "every template";
6. claims something about **another module's internals**, which nothing in this file can settle;
7. is a **rationale paragraph in a docstring** -- why, rather than what.

Everything else is an acquittal. **Do not raise a short block for being merely improvable**: prose
stating a live constraint about its own line, present tense, citing nothing, is finished work.

## The subject is the prose, not the program

Every verdict you return is a verdict on a comment. You will still notice code problems -- say so, one
line each, in a separate section, and move on: **raise a concern, do not open an investigation.**
*The comment names a symbol that no longer exists* is yours; *restore the symbol* is not. ! **A
reviewer straying into correctness is this skill's worst measured output** -- twice, a reviewer read
a valid multi-exception `except` clause and reported the file "cannot compile", and once four
agreeing reviewers shipped it. If the claim is about whether the code *runs*, you owe it an
`ast.parse` before you make it.

**Arguments.** `cap` -- optional integer, the most lines one `#` run may take. **This skill has no cap
of its own and must not invent one**; a cap published in a lint config or a hygiene test is the
number, and read how it *counts*. With none, judge by eye and **report the longest run found**.
`target` -- optional path, defaulting to the files in the diff.

## Phase 0 -- census, mechanically

Scope is a **file list** -- plus `git diff --name-only HEAD` whenever the tree is dirty:

```bash
B=$(git merge-base HEAD "${1:-origin/HEAD}" 2>/dev/null) && git diff --name-only "$B"...HEAD
```

! **Use the merge-base, never two bare endpoints** -- a two-endpoint diff presents the other branch's
work as yours. If both come back empty, ask; do not fall back to `HEAD~1`, which silently reviews one
commit of a many-commit branch and under-reports with no error. Review **every** block in those
files, not just the changed lines: comment debt is cumulative and mostly pre-existing, and the long
block that has sat above a four-line expression for months is the finding worth having. Skip
generated code, data tables, `.md` and `.txt`. Paste the output -- the block list -- into every prompt.

```python
"""Comment-review census: every block, with the signals that decide it by FORM. Stdlib only."""

import ast, io, re, sys, tokenize  # noqa: E401
from pathlib import Path

ARGS = [a for a in sys.argv[1:] if not a.startswith("-")]
CAP, W = int(ARGS[0]) if ARGS[:1] and ARGS[0].isdigit() else 6, 100
HOLDS = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
BAD = (tokenize.TokenError, IndentationError, SyntaxError, ValueError)
TAGS = {
    "date": r"\b(19|20)\d\d\b",
    "ruling": r"[""]|\bsaid\b|\bruled\b|\bround \d|\bfinding [A-Z]?\d|\btask[- ]\d",
    "history": r"\b(used to|no longer|previously|formerly|renamed|retired|deleted)",
    "coverage": r"\b(guard|assert|pinned|enforc|cover|proven|call site|caller|refus)",
    "counted": r"(?<![\w.])\d|\b(only|every|all|both|each|exactly|single|the one)\b",
    "path": r"[\w./-]*[\w-]\.(py|md|toml|json|ya?ml|txt|cfg)\b",
    "symbol": r"`[A-Za-z_][\w.]*`",
}


def blocks(src):
    """(start, end, kind) per block; a `#` RUN is bounded by CODE, not blank lines."""
    out, run, prev, rows = [], [], -9, src.splitlines()
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except BAD:
        toks = []
    for t in (t for t in toks if t.type == tokenize.COMMENT):
        own = rows[t.start[0] - 1].lstrip().startswith("#")  # trailing = its own
        if run and (t.start[0] != prev + 1 or not own):
            out.append((run[0], run[-1], "comment"))
            run = []
        run.append(t.start[0])
        prev = t.start[0] if own else -9
    out += [(run[0], run[-1], "comment")] if run else []
    try:
        nodes = [n for n in ast.walk(ast.parse(src)) if isinstance(n, HOLDS)]
    except BAD:
        return sorted(out)
    for b in (n.body[:1] for n in nodes if getattr(n, "body", None)):
        v = b[0].value if isinstance(b[0], ast.Expr) else None
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            out.append((b[0].lineno, b[0].end_lineno or b[0].lineno, "doc"))
    return sorted(out)


n = decided = 0
for f in [a for a in ARGS if not a.isdigit()]:
    if not Path(f).is_file():
        print(f"# missing: {f}")
        continue
    rows = Path(f).read_text(encoding="utf-8", errors="replace").splitlines()
    for a, b, kind in blocks("\n".join(rows)):
        body, size = rows[a - 1 : b], b - a + 1
        tags = [k for k, p in TAGS.items() if re.search(p, "\n".join(body), re.I)]
        dated = {"date", "ruling"} & set(tags)
        form = size > CAP if kind == "comment" else bool(dated and size > 2)
        n, decided = n + 1, decided + form
        flags = (["FORM"] if form else []) + tags
        flags += ["wide"] * any(len(x) > W for x in body)
        print(f"{f}:{a}-{b} {kind} {size}L {','.join(flags) or '-'}")
print(f"# {n} blocks; {decided} by FORM; {n - decided} need judgement")
```

Then resolve what it only located: every `cites-a-path` against the tree, every `names-a-symbol`
against the names the code defines -- build that corpus from the **AST**, never from raw text, which
contains the very comments being checked and so always passes. ! **Grep the STEM, not the
identifier**: prose does not obey identifier spelling, so a dead `foo_bar` is written `foo-bar`,
`FooBar`, or "the barrer". Measured -- an identifier grep found ten mentions, all correctly dated
tombstones, and missed an eleventh written with a hyphen, the only present-tense claim in the set; a
clean grep reads like a clean file. ! And **a resolved citation is not a verified one**: it asserts
something *about* its target, so open it and read it, or mark it `SUSPECTED`.

## Phase 1 -- four reviewers, each over the WHOLE list

Launch four subagents in one message with the file list, the census, the `cap`, both closed lists
above, and one angle each. **Tell each, in words, to return a line for every numbered block.**
Overlap between angles is signal: a block all four report is almost always real. ! **Reviewers are
READ-ONLY; say so explicitly**, and **name two lists -- the files UNDER REVIEW, which a proposal may
target, and files given only as REFERENCE, which it never may.** A reviewer that fixes what it finds
has destroyed the finding, and one handed a reference document proposed edits *to it*, which were
applied. Every finding carries `file:line`, the claim, the code or test line that settles it, and
**`CONFIRMED` (both sides read) or `SUSPECTED`** -- measured, 196 of 202 came back CONFIRMED.

### Currency -- does this describe the program as it is now? (~45% of yield)

The largest angle by a distance. Git holds what the code used to be; a comment narrating its own
history is doing git's job badly. Dated rulings, review-round labels, "this used to...", and the
sharpest form, **obituaries** -- a symbol, file, test, flag or config key that no longer exists, so
the reader greps, finds nothing, and reads that as *their* mistake. Also here: **a counted claim is
unverifiable unless it names the population it counts over**, so re-derive the SET before the number
-- a pass correcting a false count produced a differently-false one, off by 5x.

! **Check the other copies before you rule.** A pass edits where it is reading, so it fixes the copy
in front of it and manufactures a disagreement with the copy it never opened, which every
within-file check then passes. Grep the number, the symbol or the phrase -- the STALE copy is it.

### Functionality -- does the commentary match what the code does? (~30%)

Read the name, the signature and the docstring, then **read the body** -- the flagship false claims
are contradicted two or three lines below themselves. Flag a documented return shape the code no
longer returns, a `Returns:` whose key and value are the wrong way round, an `Args:` entry for a
parameter that does not exist, an exception nothing raises, a constant whose name and comment
disagree about what it is.

**Coverage, reachability and absence claims license deletions and are disproportionately wrong.**
"Pinned by X", "the only call site", "nothing reads this", "already verified upstream" -- each one
authorises the next person to delete something, so resolve every one. It fails in both directions: a
real guard has been deleted on a pointer to a test that never existed, and a comment calling a live
config value decorative nearly licensed deleting something three sites read. For data reached by key
rather than by name, **grep the STRING**. ! But **an unreachable hazard is not automatically a
`drop`** -- a precaution's value is having no trigger. ! And **resolve superlatives against their own
file**: "THE only entry point" is refuted 25 lines down often enough to check every time.

! **Prose that DESCRIBES behaviour is wrong far more often than prose that PROHIBITS something.** A
description that disagrees with the code -> the comment is wrong. A prohibition that disagrees -> the
code broke the rule -> file it. A description must also be **POSITIVE**: *"NOT the kernel call site"*
never lands on a side you can verify.

### Locality -- does this comment belong to the line it sits on?

A comment points DOWN for a block on its own lines, AT the declaration for a trailing one. The
finding is a comment about something **else**: a rule at the top of a class really constraining two
literals two hundred lines down, a block whose later half turns back to narrate what came before, a
run stranded after an unconditional `return`, a trailing comment severed mid-clause by the `#` lines
beneath it. The test for anything that survives: **if this code changed, would the comment become
wrong, and would anyone notice?** Flag the inverse too -- a line carrying a non-obvious constraint
with no comment, where getting it wrong is silent. **Refactoring drift is this angle's yield**: moved
code leaves its commentary behind, describing something that left.

### Module coherence -- do the comments say this is one module?

Read only the module docstring, the banners and the top-of-file prose. Do they describe *one* thing,
and does anything 25 lines below contradict them? Flag a docstring that must enumerate unrelated
responsibilities to be accurate, banners reading like chapter breaks, and **the same rule
re-explained in several places** -- no function owns it, so each site performing part of it restates
the whole. A long comment above a short expression is usually this; report it as code shape, with
the comment as evidence.

## Phase 2 -- one verdict per block

Dedup, then rule. **Before proposing a CHANGE, read the prose immediately around it** -- a deliberate
design usually says so directly above itself; but do not let a neighbour stop you *reporting*, since
one asserting the same false thing is two findings, not zero. Then two questions. **Is it CHECKABLE**
from the code as it stands, without archaeology? **Is it NECESSARY** -- would someone changing this
code make a *worse decision* without it? Not "is it interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader needs | **drop** -- it narrates the code |
| **not checkable** | **move** -- rationale, unverifiable here | **drop** -- history |

A stale or false block that is still load-bearing is **correct**, not `drop`: give the replacement
and the re-derived evidence, since a correction without a re-derived population is how one wrong
number becomes a differently wrong one. ! **Truth is not one of the questions, and that is the
point.** History that is *correct* reads as earning its place, and does not. **Rule on SENTENCES, not
on blocks** -- a container of six sentences can hold six verdicts, the common shape being a live
constraint beside the story of where it came from. ! **A single `keep` sentence launders every
sentence around it**: ruling `keep` because *part* of a block is load-bearing means descend a level.

**compact** is what you do to a `keep` or to a `move`'s remainder, not a fifth verdict; for a `move`,
name the destination and send the **WHOLE block, including the half that stays in the code**, or the
document holds only what nobody kept and reads as a list of discarded things. ! **Account for every
digit you propose deleting** -- the most repeated defect a compaction pass introduces is a measurement
replaced by an adjective, and it always looks like a legitimate trim. ! **A block one line over cap
is, by construction, mostly right**: cut the least checkable line, do not re-author. **`TODO`,
`FIXME`, `HACK`, `XXX`, `BUG` are free** -- a cap that counts them makes deleting the pointer to real
work the cheapest way to green.

## Phase 3 -- present. Always.

**This skill never edits. It ends with the verdict list**, grouped by verdict, most consequential
first, the replacement inline for every `compact` and `correct`, and a coverage line: *N swept, M
findings, K acquitted, acquittal rate R%*. Then stop. ! **Even when the human names the edit** --
"cap them", "fix these", "go do it" -- the deliverable is still the report: *"Report only, per the
skill -- say the word and I'll apply the verdicts you accept."* An imperative is not authorization;
this review's whole value is the human's disagreement with it, and **an edit applied is a verdict
never ruled on.** Measured: two runs on near-identical prompts split, one report, one 846-line diff.

Hand these rails to the pass that applies the verdicts -- you are not it, and it usually runs without
this skill loaded. **A block is bounded by CODE, not blank lines**, else a 9-line block becomes
6 + blank + 3. **Never change a line of code, a docstring's meaning, or a string literal** -- prove it
by diffing every non-comment line, which caught two cuts that took real code with them. **Apply with
`count == 1` or refuse the whole file**, the `old` text built programmatically rather than
transcribed, its width checked as well as its line count, and the file's own line ending kept.
**Extract before you cut** on a `move` -- the other order lost the text three times. And **re-read
what you wrote**: a pass that cut seven obituaries wrote seven new ones.

`/simplify` reviews code structure and applies what it finds; `/code-review` hunts correctness bugs;
this one reviews prose and **only ever proposes**. ! **Every example above is invented or anonymised
-- keep it that way.** Quoting a real comment teaches recognition of *that comment* rather than the
shape, and it rots into an obituary of its own; measurements cost nothing to anonymise.
