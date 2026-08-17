---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched by trying to CONFIRM every
  claim they make against the code, and reporting the ones that will not confirm -- across five
  angles (existence, behaviour, coverage, placement, reachability) run as parallel subagents,
  each finding returned with its evidence and a proposed verdict (drop / move / compact / keep)
  for the human to rule on. Use this whenever comments or documentation are the subject: after
  finishing a task that added or edited commentary, when a file's comments have drifted from what
  the code now does, when someone says a comment is too long or out of date or "isn't this
  history", when reviewing a diff specifically for its prose rather than its logic, before a docs
  or comment burn-down, or when asked whether a module still reads as one module. Trigger on
  phrasings that never say "comment review" -- "these comments are getting out of hand", "does
  this docstring still match", "is this comment still true", "clean up the narration in this
  file", "why does this file need so much explaining" all mean run this. It is NOT /simplify
  (which reviews code structure and applies its fixes) and NOT /code-review (which hunts
  correctness bugs) -- this one ONLY EVER PROPOSES and never edits anything, not code and not even
  the comments it rules on, because an edit applied is a verdict the human never got to rule on.
  Run it even when the request sounds like an instruction to cut ("cap these", "clean this up"):
  the deliverable is still the verdict list, and applying is a separate step. It is explicitly
  not a reviewer's job to judge whether the code works: code concerns get raised in a line and
  left, while every verdict returned is a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` -> enumerate every prose block -> try to CONFIRM each claim ->
report the ones that will not confirm -> the human rules -> a separate pass applies.

## Verify, do not suspect

A reviewer hunting for smells finds the prose that *looks* wrong. Measured over a full burn-down,
that is not where the wrong prose is: **every false statement found was one that no assertion
touched** -- not the oldest, not the longest, not the furthest from its code. The false clause sat
*inside* a block whose other sentences were true, in the same voice, under the same warning
marker, once splitting one sentence at its comma: the second clause asserted by the body and
true, the first asserted by nothing and false.

So the method is not suspicion. **Break every block into the claims it makes, then go and get the
evidence that settles each one.** A claim you confirm is closed and never reported. **A claim you
cannot confirm is the finding** -- and "cannot confirm" is not "I disbelieve it". ! **Unverifiable
is a verdict, not a pass**: a claim in a form you cannot check is worse than the same claim
written checkably and wrong, because the wrong one gets fixed on the next run while the
uncheckable one accumulates, **and its illegibility reads as confidence.** Measured -- a citation
checker held a tree at zero dangling references for months while two dead artifacts sat in one
file, written as a brace expansion and a bare filename, forms it could not parse.

## The subject is the prose, not the program

**It is not a reviewer's job to decide whether the code works.** Put code problems in a separate
section, one line each -- **raise a concern, do not open an investigation** -- and never let one
take a `drop`/`move`/`compact`/`keep` verdict. "The comment says it reads one field and it reads
three" is yours; "it should not read three fields" is `/simplify`'s. ! Measured: two eval rounds
had a reviewer read a valid multi-except clause and report the file "cannot compile", once with
four agreeing. A claim about whether the code *runs* owes an `ast.parse` first.

## Arguments

- **`cap`** -- integer, optional: the most lines one `#` block may run; pass it to every reviewer.
  **This skill has no cap of its own and must not invent one.** A cap published in a guard beats
  both the argument and your judgement -- use it, say where you got it, and read how it *measures*,
  not just its number. With none anywhere, **report the longest block found**.
- **`target`** -- a path, optional; defaults to the files in the diff.

## Phase 0 -- scope, then sweep

`git diff --name-only @{upstream}...HEAD`, or the repo's own default branch, or `HEAD~1`; add
`git diff --name-only HEAD` if the tree is dirty or the range is empty. Try them in that order
and **say which produced the list** -- a fallback that silently returns fewer files narrows the
very scope this phase exists to build. Review **all the prose in those files, not just the
changed lines**: comment debt is cumulative and mostly pre-existing. Skip generated code and data
tables, and say which. Then enumerate every block and paste the listing into every reviewer
prompt. ! Nothing in it is a verdict, and **a resolved name is not a verified claim**: a citation
whose target exists may still assert what that target denies.

```python
#!/usr/bin/env python3
"""sweep.py -- enumerate every prose block in a file, for a reviewer to walk end to end."""

import ast, io, sys, tokenize
from pathlib import Path

SKIP = {
    tokenize.COMMENT,
    tokenize.NL,
    tokenize.NEWLINE,
    tokenize.INDENT,
    tokenize.DEDENT,
    tokenize.ENDMARKER,
    tokenize.STRING,
}


def blocks(path):
    """(start, end, kind, text) per # run bounded by CODE (not by blanks), and per docstring."""
    src = Path(path).read_text(encoding="utf-8", errors="replace")
    lines, runs, run = src.splitlines(), [], []
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except Exception:
        return []
    code = {
        r for t in toks if t.type not in SKIP for r in range(t.start[0], t.end[0] + 1)
    }
    for t in toks:
        if t.type != tokenize.COMMENT:
            continue
        if run and not any(r in code for r in range(run[-1] + 1, t.start[0])):
            run.append(t.start[0])
        else:
            runs, run = runs + ([run] if run else []), [t.start[0]]
    runs += [run] if run else []
    out = [
        (
            r[0],
            r[-1],
            "trail" if r[0] in code else "run",
            "\n".join(lines[r[0] - 1 : r[-1]]),
        )
        for r in runs
    ]
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return sorted(out)
    for n in ast.walk(tree):
        if isinstance(
            n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            b = (n.body or [None])[0]
            if isinstance(b, ast.Expr) and isinstance(
                getattr(b.value, "value", None), str
            ):
                out.append((b.lineno, b.end_lineno, "doc", b.value.value))
    return sorted(out)


if __name__ == "__main__":
    for f in sys.argv[1:]:
        for s, e, kind, _ in blocks(f) if Path(f).exists() else []:
            print(f"{f}:{s}-{e} [{kind}] {e - s + 1}ln")
```

Annotate each row with whatever the filesystem settles without judgement: cited paths that do not
resolve, counted claims (a number in prose is unverifiable until someone re-derives the SET it
counts over), coverage words with nothing cited beside them, docstrings carrying a date or a "used
to", runs over `cap`, trailing comments continuing past their own line, over-wide lines. It lists
**the clean blocks too** -- that is what makes the pass complete.

## Phase 1 -- five verification angles, in parallel

Launch **five subagents in one message**, each given the file list, the block listing, the `cap`,
one angle, and both rules below. ! **Reviewers are READ-ONLY; say so in their prompt** -- a
reviewer that fixes what it finds has destroyed the finding. ! **Name the writable targets and
the read-only reference files separately**: a reviewer handed a document as the *contract* to
check code against returns proposals editing that document.

**Rule one -- rule on every block, not on the ones that catch your eye.** Walk the listing, and
report `blocks read / blocks raised` at the top. Calibration: ten reviewers over 59 modules
returned 202 findings, and in a tree nothing has ever checked expect **a third to a half** of the
multi-line blocks to fail an angle, clustered in one or two files rather than spread evenly. Four
findings from a file with ninety blocks is a sampling error, not a clean file; a finding on every
block is the opposite error, since **keep is a real verdict**. **Rule two -- every finding carries
its evidence:** `file:line`, the exact claim, the exact code or test line that settles it, and
`CONFIRMED` (you read both sides) or `SUSPECTED` (you did not). Disguising a `SUSPECTED` as
CONFIRMED is what causes a finding to be withdrawn a week later.

### 1. Existence -- does everything the prose names still exist?

Resolve every backticked or capitalised name, path, test, module and config key. Largest class
measured (~45% of findings) and the cheapest. ! **Grep the STEM, not the identifier**: prose does
not obey identifier spelling, so a dead `foo_bar` is written `foo-bar`, `FooBar`, or "the
barrer". Measured on one deletion, the identifier grep found ten mentions, all correctly dated
tombstones, and **missed an eleventh written with a hyphen -- the only present-tense claim about
the dead path in the set**; a clean grep reads as a clean file, so that failure hides itself.
! **A line number is not a citation** -- a symbol survives a refactor, `foo.py:201` becomes a
blank line. ! A name that resolves may still be **the wrong referent**: when a rule's owner goes,
the next compression reaches for whatever name is near.

### 2. Behaviour -- does the body do what the prose says?

Read the name, signature and docstring, then the body, and re-derive the claim. Flag a return
shape the code no longer returns, a `Returns:` in the wrong order, an `Args:` entry for a
parameter that does not exist, a documented exception nothing raises, a mutation described as a
copy, a summary line describing the first four lines of a forty-line function. **Re-do any
arithmetic literally** -- a worked sum can be wrong and still round to the answer a test asserts.

Then read **the body's `#` comments as one sequence, in order.** Individually each may be true;
end to end they are the most honest description of the function in the file. If that narration
describes five jobs while the name and docstring describe one, that is the finding. **The tell is
grammatical: a comment that sequences instead of constrains** -- *"now I need to...", "then we..."*
narrate the author's path, where a comment earning its place says why a line must be as it is and
goes visibly wrong if that line moves. ! **Report the mismatch; do not resolve it**: either the
docstring grows until it tells the truth, at which point the **name** is wrong, or the function
shrinks to its name.

### 3. Coverage -- does the guard it cites exist, and can it fail?

"Pinned by X", "X refuses this", "asserted in Y", "the only caller", "nothing reads this" all
**license a future deletion**, so they are checked, never read. Two failures, and the second is
the one nobody looks for: **the guard does not exist** -- measured, a real check was deleted on
the strength of a pointer to a test that was never written; or **the guard exists and cannot
fail** -- a tautology, an assertion over an empty fixture, an expectation re-derived with the
implementation's own formula, a sum whose three candidate arithmetics all round alike. Measured:
the ONLY test of a headline product invariant compared two byte-identical calls. ! A caller count
is the same claim in disguise: count them, and ask whether any caller is outside the test tree.
! Where nothing can go red, nothing stops the comment rotting.

### 4. Placement -- is this prose where the thing it constrains is?

**Line zoom:** a comment is a claim about the code beside it. Flag a rule stated at the top of a
class that really constrains two literals 200 lines down, or a block whose later half turns back
to narrate what came before. The test: **if this code changed, would the comment become wrong,
and would anyone notice?** Prose that would quietly survive a change to the code it describes is
not local to it. Flag the inverse too -- a non-obvious constraint, silent when got wrong, with no
comment at all.

**File zoom:** read only the module docstring, the banners and the top-of-file commentary and ask
whether they describe one thing. A docstring enumerating unrelated responsibilities, banners
reading like chapter breaks, or a section named for the occasion that produced it -- a review
round, a task number -- is the finding: the membership rule becomes *"it was in that batch"*,
which no future author can apply. Also flag **one rule explained in several modules**: it has no
owning function, so every site performing part of it re-explains the whole -- measured, one rule
in 8 of 9 files under SEVEN names, owned by nothing. **This is why the comments got long**, and a
40-line comment above a four-line expression is usually it -- a code-shape finding with the
comment as evidence, which you report and do not fix.

### 5. Reachability and provenance -- has it a reader, and did its meaning survive?

**Reachability.** Does anything consume the thing this prose describes? Is the hazard it warns of
still triggerable? Does the documented function have a caller that is not a test? Measured
instances no other angle sees: a constant with zero readers whose comment states an invariant and
admits its enforcing test was deleted; an exemption from a rule retired weeks earlier. ! Run it
**inverted** too -- a retracted fact that something still *reads* is the more dangerous half.

**Provenance.** Where a baseline exists -- a previous ref, or the module's own extracted mirror
doc, which needs no ref -- diff each block against it and ask **not whether the new text is
shorter or more plausible, but which version the code actually backs, and what the new text
asserts that the old one did not.** Measured: two passes *removing* false claims inverted two
meanings, one turning "returns a NEW dict, never mutates" into "mutated in place" -- **exactly the
edit the code exists to prevent, with no test failing.** ! The larger half is **deletion**, with
no new text to compare: account for every removed assertion, not only the altered ones.

## Phase 2 -- one verdict per finding

Wait for all five, dedup, then rule. **Before proposing a CHANGE, read the prose immediately
around it** -- a deliberate design usually says so directly above itself. Before *proposing*, not
before *observing*: a block can cite a dated ruling and a task number and still be false. Ask
**is it CHECKABLE** -- could a reader confirm or refute it from the code as it stands, with no
archaeology? -- then **is it NECESSARY** -- would someone changing this code make a **worse
decision** without it? Not "is it interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader needs | **drop** -- it narrates what the code says |
| **not checkable** | **move** -- real rationale, unverifiable here | **drop** -- history |

! **Truth is not one of the two questions, and that is the point.** *"Moved here from
`x.validate` when that module was deleted"* is true; the reader needs the check to live **here**,
not its travel history. Accuracy is why it was never deleted, not a reason to keep it.

! **Two verdicts are missing from that table and you must use them by name.** **correct** -- the
claim is false and the true version is worth stating; a bulk pass once applied 82 of these under
a vocabulary with no word for it. And **restore** -- the block is a fragment a previous edit
severed mid-sentence, so it is neither checkable nor necessary, which routes it to `drop` and
deletes the pointer instead of putting the sentence back.

**When comment and code disagree, grammar decides which is wrong:** a **description** that
disagrees means the comment is wrong; a **prohibition** that disagrees means the *code* broke the
rule, so file it and the code moves. * A description written as a negation is a FORM defect in
itself -- "X is not the case" cannot be verified, only argued backwards from what the code does,
which is how negated descriptions rot unnoticed. Rewrite it positively; a prohibition may stay
negative, since no positive form keeps its force.

**Rule on sentences, not on blocks.** ! **A single `keep` sentence launders every sentence around
it**, so ruling `keep` because *part* of a block is load-bearing is the signal to descend a
level. **Then, for whatever survives:** is it longer than it needs to be? That is **compact**,
not a category but what you do to a `keep`. For **move**, name the destination and send the
**whole** block, including the part that stays in the code. ! A `move` may relocate a
*description*; it must not relocate an **instruction to callers**, which stops working the moment
it leaves the file.

## What is NOT a finding -- suppress these

- **A docstring being long** -- `#` comments are governed by LENGTH, docstrings by FORMAT.
- **A hand-worked derivation** -- the arithmetic that stops an assertion being an echo of the
  implementation. * Over cap, the first move is relocation into the DOCSTRING, not compaction.
- **A one-line trailing field comment** (`retries: int  # 0 disables the backoff`). Only one
  running on into lines beneath it is a finding, and that is FORMATTING, not placement.
- **A `TODO`/`FIXME`/`HACK`/`XXX`/`BUG` marker**: it points outward at work not done, so deleting
  it to get back under a cap is the cheapest wrong fix available.
- **A comment naming its own expiry condition**, or **a warning where nothing goes red** -- prose
  is the only guard there; a warning against a move that **does** break a test is merely a
  time-saver, and there is no third category. **A block one line over cap** is mostly correct by
  construction: cut its least checkable line, do not re-author what is already true and current.

## Phase 3 -- present. Always.

**This skill never edits -- the orchestrator included. It ends with the verdict list.** Report
grouped by verdict, most consequential first, with the replacement text inline for every
`compact` and `correct`. Then stop. ! **Even when the human names the edit** -- "cap them", "fix
these", "go do it" -- the deliverable is the report: *"Report only, per the skill -- say the word
and I'll apply the verdicts you accept."* Do not treat an imperative as authorization: this
review's value is the human's disagreement with it, and **an edit applied is a verdict never
ruled on**. Measured -- two runs on near-identical imperative prompts split, one returning a
report and one an 846-line diff.

Hand these rails to whoever applies the verdicts: **a block is bounded by CODE, not by blank
lines**, or a 9-line block becomes 6+3 and passes; **never change a line of code, a docstring's
meaning, a string literal or an annotation** -- prove it with an AST diff against the pre-edit
file, string literals included since prose hides in them, run on the file most likely to fail it;
build the `old` text programmatically and apply on `count == 1` or refuse the whole file;
**extract before you cut** on a `move`; and **re-read what you wrote** -- a pass that cut seven
obituaries wrote seven new ones, the same one twice in one file.

`/simplify` reviews code structure and applies what it finds; `/code-review` hunts correctness
bugs; this one verifies prose and **only ever proposes**, ending in questions, not a diff.
! **Every example above is invented and every measurement anonymised -- keep it that way.** Quoting
a real comment teaches a reviewer to recognise *that comment* instead of the shape, and the day
someone acts on the finding this file cites something that no longer exists.
