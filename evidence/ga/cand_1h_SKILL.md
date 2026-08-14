---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched by walking each file top to
  bottom, block by block, asking the same four questions at every one — locality, currency,
  functionality, module coherence — and returning each finding with a proposed verdict (drop /
  move / compact / keep) for the human to rule on. Use this whenever comments or documentation are
  the subject: after a task that added or edited commentary, when a file's comments have drifted
  from what the code now does, when someone says a comment is too long or out of date or "isn't
  this history", when reviewing a diff for its prose rather than its logic, before a docs or
  comment burn-down, or when asked whether a module still reads as one module. Trigger on
  phrasings that never say "comment review" — "these comments are getting out of hand", "does
  this docstring still match", "is this comment still true", "clean up the narration in this
  file", "why does this file need so much explaining" all mean run this. It is NOT /simplify
  (code structure, applies its fixes) and NOT /code-review (correctness bugs) — this one ONLY
  EVER PROPOSES and never edits anything, not even the comments it rules on, because an edit
  applied is a verdict the human never got to rule on. Run it even when the request sounds like
  an instruction to cut ("cap these", "clean this up"): the deliverable is still the verdict list
  and applying is a separate step. Judging whether the code works is not a reviewer's job.
---

# comment-review

`/comment-review [cap] [target]` → enumerate every prose block → walk it → a verdict each.

## The method: ONE pass, every block, visited exactly once

Do not hunt by category. Categories make you sweep the file once per angle, and every sweep
is a fresh chance to skip a block — the skipped ones are the quiet ones, which is exactly
where a wrong comment survives longest. Instead: **enumerate** every comment run and
docstring mechanically (Phase 1), **walk that list in line order** asking the same short card
at each, and **tick each one off** — visited once, ruled on once. The four angles are not
four passes; they are four questions on the card. Coverage is what this skill optimises: a
reviewer who reads 60% of a file brilliantly loses to one who reads 100% of it adequately,
because the missed 40% is invisible in the report.

## The subject is the prose, not the program

**It is not a reviewer's job to decide whether the code works.** Every verdict you return is
a verdict on a comment; a reviewer who starts debugging has changed the question. You will
still notice code problems — say so in a separate section, one line each. **Raise a concern,
do not open an investigation**, and never give a code finding a `drop`/`move`/`compact`/`keep`
verdict; those four words apply only to prose. The line is sharp and the best findings sit
right on it: *"the comment says the function reads one field; it reads three"* is yours,
*"the function should not read three fields"* is not; *"it names a symbol that no longer
exists"* is yours, *"restore the symbol"* is not.
⚠ **A reviewer straying into correctness is where this skill's worst output comes from,
measured.** In two eval rounds a reviewer read `except ValueError, TypeError:` and reported
the file "cannot compile" — a claim about the *program*, volunteered while reviewing *prose*,
and wrong. If a claim is about whether the code runs it is not your finding, and if you make
it anyway you owe it a `python -c` or an `ast.parse` first.

## Arguments and scope

- **`cap`** — integer, optional: the maximum lines one `#` block may run. **This skill has no
  cap of its own** and must not invent one. If none is given, review by judgement and
  **report the longest block found**, so the number is visible without being asserted.
- **`target`** — a path, optional. Defaults to the files in the diff:
  `git diff --name-only @{upstream}...HEAD` (or `main...HEAD`, or `HEAD~1`); if the tree is
  dirty or the range is empty add `git diff --name-only HEAD`.

Review **all** the commentary in those files, not just the changed lines — the one place this
skill departs from `/simplify`. Comment debt is cumulative and mostly pre-existing: the
54-line block that has sat above a four-line expression for months is the finding worth
having. The diff says which files are live in the human's head; it must not bound what gets
read inside them. Skip generated code and data tables, and say which you skipped.

## Phase 1 — Enumerate the blocks, before reading anything

Run this first: it is the checklist the walk ticks off, and what makes "nothing was skipped"
a fact rather than a hope. Stdlib-only; it assumes nothing about the repo.

```python
# save as /tmp/blocks.py; usage: python /tmp/blocks.py FILE [FILE...]
import ast, io, re, sys, tokenize
from pathlib import Path

SIG = {  # cheap triage only — a hit is a REASON TO LOOK, never a verdict
    "DATE": r"\b(19|20)\d\d\b",
    "QUOTED": r"[\"“‘][^\"“”]{12,}[\"”]",
    "HISTORY": r"\b(used to|no longer|previously|formerly|retired|originally|deprecated"
    r"|before the fix|the old |reverted|was (renamed|replaced|moved|deleted))\b",
    "REVIEW": r"\b(finding|fix wave|round \d|task \d|phase \d|post-merge|review)\b",
    "CLAIM": r"\b(test_\w+|guarded|pinned|asserted|checked by|covered by|enforced by|measured"
    r"|shared with|consumed by|callers?|see [`\w./]+)\b|[\w/]+\.(md|toml|py|json)\b",
}
SKIP = (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT)


def pack(cur):
    return cur[0][0], cur[-1][0], "\n".join(c[1] for c in cur)


def runs(src):  # a comment run is bounded by CODE, not by blank lines
    lines, cur = src.splitlines(), []
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except tokenize.TokenError, IndentationError, SyntaxError, ValueError:
        return
    for t in toks:
        if t.type == tokenize.COMMENT:
            own = lines[t.start[0] - 1][: t.start[1]].strip() == ""
            if cur and not (own and cur[-1][2]):
                yield pack(cur)
                cur = []
            cur.append((t.start[0], t.string, own))
        elif cur and t.type not in SKIP:
            yield pack(cur)
            cur = []
    if cur:
        yield pack(cur)


def docs(src):
    try:
        tree = ast.parse(src)
    except SyntaxError, ValueError:
        return
    hold = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    for n in ast.walk(tree):
        b = n.body if isinstance(n, hold) else []
        d = b[0] if b and isinstance(b[0], ast.Expr) else None
        if d is not None and isinstance(getattr(d.value, "value", None), str):
            yield (
                d.lineno,
                d.end_lineno or d.lineno,
                d.value.value,
                getattr(n, "name", "mod"),
            )


for arg in sys.argv[1:]:
    try:
        src = Path(arg).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"skip {arg}: {e}")
        continue
    out = [(a, b, "#", t) for a, b, t in runs(src)]
    out += [(a, b, f'"""{nm}', t) for a, b, t, nm in docs(src)]
    print(f"== {arg}: {len(out)} blocks")
    for a, b, kind, text in sorted(out):
        tags = [k for k, r in SIG.items() if re.search(r, text, re.I)]
        if b - a + 1 > 6 and kind == "#":
            tags.append(f"LONG:{b - a + 1}")
        print(f"  [{a}-{b}] {kind} {' '.join(tags)}")
```

The count it prints is your denominator. **Report it**: "N blocks in M files, all walked."
Tags are triage — they say which to read first, never which to flag. An untagged block still
gets the card; a tagged one still has to fail a question to become a finding.

## Phase 2 — The walk: the card, asked at every block

For each block in line order, ask these four in order, and stop at the first that fails.

### 1. CURRENCY — is every name in it still real?

Do this **mechanically, not by eye** — the largest and cheapest class, and eyeballing it is
how it hides. Extract every identifier, path, test name and count the block mentions, and
check each:

- **a symbol / file / flag / test that no longer exists** is an *obituary* — worse than
  noise, because the reader greps, finds nothing, and reads that as *their* mistake.
- **a cited path** (`docs/x.md`, `tests/y.py`, a config key) — resolve it on disk.
- **a cited test** — "pinned by X" is *licensing future edits*. Grep the name.
- **a count** ("four callers", "three places", "1,200 rows") — recount it.
- **a claim about another module** ("shared with `foo`", "`bar` consumes this") — verify.

⚠ **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead
`foo_bar` gets written as `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Search a loose
stem (`grep -ri "foo.\?bar"`) then triage. Measured on a real deletion: the identifier grep
found ten mentions, all correctly dated tombstones, and **missed an eleventh written with a
hyphen — the only present-tense claim about the dead path in the set.**
Also flag prose doing git's job: dated rulings, review labels ("fix round 2", "finding B4",
"task 8.6"), "this used to…", "X was changed to Y", "before the fix", "the old version",
and quoted rulings or attributions — those belong to a decision log, not to a statement.

### 2. LOCALITY — is it about the line it sits on?

A comment points DOWN for a block on its own lines, AT the declaration for a trailing one; a
field comment (`retries: int  # 0 disables the backoff`) is exactly where it belongs. The
finding is a comment about something **else**: a block whose later half turns back to narrate
what came before, a note describing a function further down, a paragraph atop a class that
really constrains two literals two hundred lines away.
Second test: **if this code changed, would the comment become wrong — and would anyone
notice?** A comment that would quietly survive a change to the code it claims to describe is
not local to it. Flag the inverse too: a line carrying a non-obvious constraint with **no**
comment, where getting it wrong is silent. Absence is a locality finding.

### 3. FUNCTIONALITY — does it match what the code does?

**Prose that DESCRIBES behaviour is wrong far more often than prose that PROHIBITS
something.** Weight your attention accordingly: a sentence saying what the function returns,
what it reads, what it skips, or what happens next is the sentence to check against the body.

Read name, signature, docstring, then body. Flag a docstring describing a return shape the
code no longer returns, a `Returns:` naming fields in the wrong order, an `Args:` entry for a
parameter that does not exist, a documented exception nothing raises. The **summary line** is
the part most readers see and it drifts silently — changing a return type does not change the
sentence describing it.
Then read the body's comments **as one sequence**. Individually each may be true; end to end
they are the most honest description of the function in the file. The tell is grammatical:
**a comment that sequences instead of constrains** — *"now I need to…", "oh I should…"*. A
comment earning its place says why a line must be as it is and goes visibly wrong when that
line moves; a run of sequencing comments is a to-do list left in the body — either (A) the
step is not needed for the function to be the function, or (B) it is real work at the wrong
level. Say which.

⚠ **Report the mismatch; do not resolve it.** *"The commentary describes five jobs, the name
and docstring describe one"* has two honest resolutions — the docstring grows until the
**name** is the wrong thing, or the function shrinks to what it is called. Naming the fork
*is* the deliverable.

### 4. COHERENCE — asked once per file, at the module docstring and the banners

Read only the module docstring, section banners, and top-of-file commentary. Do they describe
**one** thing? Flag prose announcing two or three subjects, banners that read like chapter
breaks rather than parts of one argument, a docstring enumerating unrelated responsibilities.
Also flag the same rule explained in several modules: the rule has no owning function, so
each site performs part of it and re-explains the whole. A long comment above a short
expression is usually this. Report it as a code-shape finding with the comment as evidence.

## Phase 3 — One verdict per block

Rule on each finding by asking **two questions, in this order**. **Is it CHECKABLE?** Could a
reader confirm or refute it from the code as it stands, without archaeology? *"The floor is
gated and the ceiling is not"* is checkable; *"this was changed last spring after the
review"* is not. **Is it NECESSARY?** Would someone changing this code make a **worse
decision** without it? Not "is it interesting", not "is it true" — would they get it wrong.

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** — a verifiable constraint | **drop** — it narrates what the code says |
| **not checkable** | **move** — real rationale, unverifiable here | **drop** — history |

⚠ **Truth is not one of the questions, and that is the whole point.** *"Moved here from
`x.validate` when that module was deleted"* is true; the reader needs to know the check lives
**here**, not where it used to. Uncheckable and unnecessary, so it goes — accuracy is why
history was never deleted, never a reason to keep it.
**Rule on sentences, not on blocks.** A container of six sentences can hold six verdicts.
The common shape is a live constraint sitting beside the story of where it came from — the
constraint is checkable and necessary, the origin story is neither, one paragraph. ⚠ **A
single `keep` sentence launders every sentence around it**; a block's most defensible
sentence is usually why the whole block survived this long.

Then, for what survives: is it longer than it needs to be? Verdict **compact** — same
content, fewer words; not a fifth category but what you do to a `keep`, or to the remainder a
`move` leaves behind. For **move**, name the destination (if the repo stages extracted prose —
a per-module doc tree, a decision log — send it there). For **compact**, propose the text:
prefer *"X must be Y because Z breaks"* over *"this used to be W."* Do not pad — **keep** is a
real verdict and a review returning mostly `keep` is a good outcome.

### The dangerous cell — a claimed guard that does not exist

A comment claiming coverage that is real is fine if it cites precisely enough to find. One
claiming coverage that is **not** real is the dangerous cell: a deletion gets justified by a
guard nobody can find, and reads as safe for exactly that reason. Coverage claims are
disproportionately wrong and are the class that *licenses deletions* — a real guard has been
deleted on the strength of a pointer to a test that was never written. Grep the cited name,
every time. (A load-bearing constraint with **no** claimed guard is the opposite finding.)

## Comments and docstrings are governed differently

**A `#` comment is governed by LENGTH** — it interrupts the code, so its cost is the screen
space between the line above and the line below. **A docstring is governed by FORMAT, not
length** — it sits at a boundary and is *supposed* to carry explanation.

| | `#` comment | docstring |
|---|---|---|
| too long | a finding | **not** a finding on its own |
| summary line does not summarise | n/a | a finding — `"""Yield …"""` on one returning a tuple |
| carries history / describes the wrong code | a finding | a finding |
| documents a parameter that does not exist | n/a | a finding |

**Do not propose `compact` on a docstring for being long**; propose it when the body carries
something that fails a card question. And **if the repo publishes its own cap or hygiene
rule — a lint config, a hygiene test, a baseline file, a contributing guide — use it and say
where you got it.** It beats the argument and your judgement both. Read the guard for how it
*measures*, not just its number: matching a number while counting differently produces a
file that claims to comply and does not.

## Four things a length rule structurally cannot see

- **A trailing comment carrying past its own line**, on into comment-only lines beneath it.
  ⚠ **A FORMATTING finding, not a locality one** — lift the whole thing above the line.
- **A block split by an inserted statement.** The split is not the finding; the half that
  **still talks about what came before** is.
- **The wrong half surviving** — deleting the constraint and keeping the narration passes the
  cap and makes the comment worse. Check what SURVIVED, not what went.
- **Refactoring drift** — moved code leaves its commentary behind, or drags it somewhere it is
  no longer true.

## Phase 4 — Present. Always.

**This skill never edits. It ends with the verdict list**, grouped by verdict, most
consequential first, with proposed replacement text inline for every `compact`. Open with the
coverage line from Phase 1 — blocks enumerated, walked, files skipped. Then stop.

⚠ **Even when the human names the edit** — "cap them", "fix these", "go do it" — the
deliverable is the report. Say so in one line: *"Report only, per the skill — say the word
and I'll apply the verdicts you accept."* Do not treat an imperative as authorization. That
is a ruling: this review's value is the human's disagreement with it, and **an edit applied
is a verdict never ruled on.** Measured, before the rule: two runs given near-identical
imperative prompts split, one returning a report and one an 846-line diff.

## Rails for the pass that applies these

You are not that pass. Hand these along; it usually runs without this skill loaded. **A
comment block is bounded by CODE, not by blank lines** — otherwise a 9-line block becomes 6+3
and passes any cap. **Never change a line of code, a docstring's meaning, or a string
literal**; prove it by diffing every non-comment line against the pre-edit file. **Extract
before you cut** when the verdict is `move` — destination first, verbatim, then remove the
source; the other order loses the text on any interruption, and did, three times. **Re-read
what you wrote**: a pass that cut seven obituaries wrote seven new ones, one twice in a file.
`/simplify` reviews code structure and applies what it finds; `/code-review` hunts correctness
bugs. This one reviews prose and **only ever proposes** — notice a defect, name it and leave it.
⚠ **Every example in this file is invented. Keep it that way when you edit it.** Quoting a
real comment teaches a reviewer to recognise *that comment* instead of the shape, and it rots:
the day someone acts on the finding, this file cites a comment that no longer exists — a
hygiene skill carrying its own obituary. Measurements anonymise free; keep those.
