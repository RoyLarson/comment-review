---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched -- census every prose block, then
  try to CONFIRM every claim each one makes against the code, across four angles (currency,
  functionality, locality, module coherence) run as parallel subagents -- and return every block
  either as a finding with a proposed verdict (drop / move / compact / correct / keep) or as a named
  acquittal, for the human to rule on. Use this whenever comments or documentation are the subject:
  after finishing a task that added or edited commentary, when a file's comments have drifted from
  what the code now does, when someone says a comment is too long or out of date or "isn't this
  history", when a number or a citation in prose looks stale, when the same rule seems to be
  explained in several places, when reviewing a diff specifically for its prose rather than its
  logic, before a docs or comment burn-down, or when asked whether a module still reads as one
  module. Trigger on phrasings that never say "comment review" -- "these comments are getting out of
  hand", "does this docstring still match", "is this comment still true", "didn't we say this
  somewhere else", "clean up the narration in this file", "why does this file need so much
  explaining" all mean run this. It is NOT /simplify (which reviews code structure and applies its
  fixes) and NOT /code-review (which hunts correctness bugs) -- this one ONLY EVER PROPOSES and never
  edits anything, not code and not even the comments it rules on, because an edit applied is a
  verdict the human never got to rule on. Run it even when the request sounds like an instruction to
  cut ("cap these", "clean this up"): the deliverable is still the verdict list, and it is not a
  reviewer's job to judge whether the code works -- code concerns get raised in a line and left.
---

# comment-review

`/comment-review [cap] [target]` -> census every block -> confirm every claim -> a verdict **or a named
acquittal** each -> the human rules -> a separate pass applies.

## The governing law -- a claim that will not confirm is the finding

Break each block into the claims it makes, then go and get the evidence that settles each one. A claim
you confirm is closed and never reported. **A claim you cannot confirm is the finding**, and "cannot
confirm" is not "I disbelieve it". ! **Unverifiable is a verdict, not a pass**: a claim in a form
nobody can check is worse than the same claim written checkably and wrong -- the wrong one gets fixed
next run, the uncheckable one accumulates, and its terseness reads as authority.

**Every false statement found in a real burn-down was one no assertion touched.** Not the oldest, not
the longest, not the furthest from its code. False clauses sat *inside* blocks whose other sentences
were true, same voice, same indentation; one split a sentence at its comma, the clause the body
asserted true and the clause nothing asserted false. So **look where nothing asserts**, and **rule on
sentences, not on blocks**.

Two independent mechanisms carry that. **Census** -- enumerate every prose block mechanically before
any judgement, because a reviewer reading for smells reads the blocks that *look* wrong; sampling, not
the angles, is what caps a review. Settled: run it, do not re-argue it. **Acquittal** -- every block
the census lists leaves as a **finding** or as an **acquittal naming its reason from the closed list
below**; silence is a gap, not a pass. ! The demand for evidence is the engine and the angles are the
**checklist that stops it being satisfied cheaply** -- a reviewer told only "confirm every claim"
confirms the claims it can think of a check for.

**The subject is the prose, not the program.** Put code problems in a separate section, one line each
-- raise a concern, do not open an investigation -- and never let one take a prose verdict. *The comment
says it reads one field and it reads three* is yours; *it should not read three* is `/simplify`'s.
! Measured: two eval rounds had a reviewer call a valid multi-except clause uncompilable. A claim
about whether the code *runs* owes an `ast.parse`.

## Phase 0 -- scope, then census

**`cap`** -- optional integer, the most lines one `#` run may take; pass it to every reviewer. ! **This
skill has no cap of its own and must not invent one:** a cap published in the repo's own guard beats
both the argument and your judgement -- use it, say where you got it, and read how it *measures*. With
none anywhere, **report the longest block found**. **`target`** -- optional path, default the diff.

```bash
B=$(git merge-base HEAD "${1:-origin/HEAD}" 2>/dev/null) && git diff --name-only "$B"...HEAD
git diff --name-only HEAD          # add this whenever the tree is dirty
```

! **Use the merge-base, never two bare tips** -- `A...B` presents the other branch's work as yours. If
both come back empty, ask; never fall back to `HEAD~1`, which silently reviews one commit of a
many-commit branch. Then review **every comment and docstring in those files, not just the changed
lines**: comment debt is cumulative and mostly pre-existing, and editing one block routinely breaks an
untouched one elsewhere. Skip generated code and data tables, and say which. Run the census over the
list and paste its output into **every** reviewer prompt; it lists the clean blocks too, which is what
makes the pass complete. ! **Nothing it prints is a verdict**, a block with no flag can be the worst
prose in the file, and **a resolved name is not a verified claim**: a citation whose target exists may
still assert what that target denies.

```python
"""Census: every `#` run (bounded by CODE, not by blanks) and every docstring, with flags."""

import ast, io, pathlib, re, sys, tokenize  # noqa: E401

SKIP = {
    tokenize.COMMENT,
    tokenize.NL,
    tokenize.NEWLINE,
    tokenize.INDENT,
    tokenize.DEDENT,
    tokenize.ENDMARKER,
    tokenize.STRING,
}
DEF = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
CITE = re.compile(r"[\w./-]+\.(?:py|md|txt|toml|json|ya?ml|cfg|ini|rst)\b")
DROP = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "site-packages",
    "__pycache__",
    "build",
}
FLAG = {  # reasons to LOOK, never verdicts
    "hist": r"used to|no longer|formerly|previously|renamed|retired|deleted|moved to|superseded"
    r"|was changed|until 20|since 20|reverted|retract|round [123]|finding [A-Z]?\d",
    "cover": r"guard|pinned|assert|covered|enforc|checked by|proven|refus|call site|caller"
    r"|verified|catches|goes red|mutant|nothing reads|only test",
    "count": r"(?<![\w.])\d|\b(one|two|three|only|every|all|both|each|exactly|single|none)\b",
    "date": r"\b(19|20)\d\d([-/]\d\d?){0,2}\b",
    "neg": r"\b(not|never|cannot|nothing|none|neither|does not|rather than|instead)\b",
    "quote": r"[""]|\bsaid\b|\bruled\b|\bdecided\b",
    "why": r"\bbecause\b|\bso that\b|\bwhy\b|\brationale\b|\bthe point\b|\bdeliberat|\bintention",
    "mark": r"\b(TODO|FIXME|HACK|XXX|BUG)\b",
}


def blocks(src):
    """(start, end, kind, text) per `#` run and per docstring; [] on anything unparseable."""
    lines, runs, run, out = src.splitlines(), [], [], []
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except Exception:
        return []
    code = {
        r for t in toks if t.type not in SKIP for r in range(t.start[0], t.end[0] + 1)
    }
    for t in (t for t in toks if t.type == tokenize.COMMENT):
        if run and not any(r in code for r in range(run[-1] + 1, t.start[0])):
            run.append(t.start[0])
        else:
            runs, run = runs + ([run] if run else []), [t.start[0]]
    for r in runs + ([run] if run else []):
        out.append(
            (
                r[0],
                r[-1],
                "trail" if r[0] in code else "run",
                "\n".join(lines[r[0] - 1 : r[-1]]),
            )
        )
    try:
        tree = ast.parse(src)
    except SyntaxError, ValueError:
        return sorted(out)
    for n in ast.walk(tree):
        if isinstance(n, DEF) and (d := ast.get_docstring(n, clean=False)) is not None:
            out.append((n.body[0].lineno, n.body[0].end_lineno, "doc", d))
    return sorted(out)


root = pathlib.Path(".").resolve()
known = {p.name for p in root.rglob("*.py") if p.is_file() and not DROP & set(p.parts)}
for arg in (a for a in sys.argv[1:] if pathlib.Path(a).is_file()):
    for s, e, kind, text in blocks(
        pathlib.Path(arg).read_text("utf-8", errors="replace")
    ):
        flags = [
            f"{kind}{e - s + 1}",
            f"w{max((len(x) for x in text.splitlines()), default=0)}",
        ]
        flags += [k for k, rx in FLAG.items() if re.search(rx, text, re.I)]
        gone = sorted(
            {
                c
                for c in CITE.findall(text)
                if pathlib.Path(c).name not in known and not (root / c).exists()
            }
        )
        print(f"{arg}:{s}-{e}", *flags, f"path:{','.join(gone[:3])}" if gone else "")
```

! Add dead-NAME resolution only with these three, all measured: corpus from the **AST, never raw
text**; **exclude `.md`/`.txt` and the test tree** (a doc discussing a deleted symbol vouches for it --
three obituaries suppressed; `assert "x" not in y` makes a dead name read as alive -- 4 of 7 masked);
and skip any directory holding `pyvenv.cfg`, since **a virtualenv poisons the corpus**.

## Phase 1 -- four angles, in parallel

Launch **four subagents in one message**, each with the file list, the census, the `cap`, one angle and
both rules. Overlap between angles is signal, not waste. ! **Reviewers are READ-ONLY; say so in their
prompt** -- one that fixes what it finds has destroyed the finding. ! **Name the writable targets and
the read-only reference files separately**: a reviewer handed a document as the contract returns
proposals editing it. **Rule one -- walk the census end to end and account for every row**, reporting
`blocks read / raised / acquitted` at the top with each acquittal's named reason. **Rule two -- every
finding carries its evidence:** `file:line`, the exact claim, the exact code or test line that settles
it, and `CONFIRMED` (you read both sides) or `SUSPECTED` (you did not).

### Currency -- does this describe the program as it is now? (~45% of findings)

Git holds what the code used to be; a comment narrating its own history does git's job badly. Flag
dated rulings, review-round labels ("round 2", "finding B4"), "this used to...", "X was changed to Y",
"no longer", "previously" -- and the sharpest form, **obituaries**: a name, file, test, flag or config
key that no longer exists, so the reader greps, finds nothing, and reads it as *their* mistake.

! **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar` is
written `foo-bar`, `FooBar`, or "the barrer". Measured on one deletion, the identifier grep found ten
mentions -- all correctly dated tombstones -- and **missed an eleventh written with a hyphen, the only
present-tense claim about the dead path in the set**; a clean grep reads as a clean file, so that
failure hides itself. ! **A line number is not a citation**: `foo.py:201` goes blank, the symbol lives.

**Every number is a citation.** A count is unverifiable unless it names the SET it counts over, so
re-derive the population before the number, and treat every definite-singular ("the one consumer",
"both callers") as a count with no digit -- one pass correcting a false number produced a
differently-false one by re-counting the wrong population. ! Then **grep the repo for the claim's
subject before ruling**: a pass fixes the copy in front of it and manufactures a disagreement with the
copy it never opened, after which every within-file check passes both halves.

### Functionality -- does the commentary match what the code does? (~30%)

Read name, signature and docstring, then the body, and re-derive the claim. Flag a return shape the
code no longer returns, a `Returns:` in the wrong order, an `Args:` entry for a parameter that does
not exist, a documented exception nothing raises, a mutation described as a copy, a summary line
describing the first four lines of a forty-line function. The **summary line** drifts silently, since
changing a return type does not change the sentence describing it. **Re-do any arithmetic literally**
-- a worked sum can be wrong and still round to the answer a test asserts.

**Claims about coverage license deletions and are disproportionately wrong.** "pinned by X", "guarded
by Y", "the only call site", "nothing reads this" -- grep every one. Two failures, the second the one
nobody looks for: **the guard does not exist** (a real check was deleted on a pointer to a test never
written), or **the guard exists and cannot fail** -- a tautology, an assertion over an empty fixture,
an expectation re-derived with the implementation's own formula. **Reachability
belongs here, not in an angle of its own:** does anything consume what this prose describes, is the
hazard still triggerable, has the function a caller outside the test tree? ! Inverted too -- a
retracted fact something still *reads* is the worse half.

**Then read the body's `#` comments as one sequence.** Individually each may be true; end to end they
are the most honest description of the function in the file. The tell is grammatical: a comment that
**sequences** ("now I need to...", "then we...") instead of **constrains** narrates the author's path and
goes nowhere when its line moves. ! **Report the mismatch; do not resolve it** -- either the docstring
grows until it tells the truth, at which point the *name* is wrong, or the function shrinks to it.

### Locality -- does this comment belong to the line it sits on?

A comment points DOWN for a block on its own lines and AT the declaration for a trailing one, so a
field comment is exactly where it belongs. The finding is a comment about something **else**: a rule
atop a class that really constrains two literals 200 lines down, a block whose later half turns back
to narrate what came before, a demonstrative resolving 40 lines away, a block stranded after an
unconditional `return`. Second test: **if this code changed, would the comment become wrong -- and
would anyone notice?** Prose that would quietly survive a change to the code it describes is not local
to it; flag the inverse too, a line carrying a non-obvious constraint with no comment at all.
**Refactoring drift is this angle's biggest yield** -- moved code either takes its commentary along or
leaves it behind describing something that left.

### Module coherence -- do the comments say this is one module?

Read only the module docstring, the banners and the top-of-file prose. Flag prose announcing two or
three subjects, banners reading like chapter breaks, a section named for the occasion that produced it
(a review round, a task number -- the membership rule becomes "it was in that batch"), a docstring
enumerating unrelated responsibilities to be accurate, or one describing a fraction of its module.
Also flag **one rule explained in several modules**: it has no owning function, so every site
re-explains the whole -- measured, one rule in 8 of 9 files under seven names. **This is why the
comments got long**, and a long comment above a short expression is usually it: a code-shape finding
you report and do not fix.

## Phase 2 -- one verdict, or one named acquittal, per block

Wait for all four, dedup blocks, then rule. **Before proposing a CHANGE, read the prose immediately
around it** -- a deliberate design usually says so directly above itself. Before *proposing*, not
before *observing*: a block can cite a dated ruling and still be false. Ask **is it CHECKABLE** --
could a reader confirm or refute it from the code as it stands, with no archaeology? -- then **is it
NECESSARY** -- would someone changing this code make a **worse decision** without it? Not "is it
interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader needs | **drop** -- it narrates what the code says |
| **not checkable** | **move** -- real rationale, unverifiable here | **drop** -- history |

! **Truth is not one of the two questions, and that is the point.** *"Moved here from `x.validate`
when that module was deleted"* is true, and the reader needs the check to live **here**, not its
travel history -- accuracy is why it was never deleted, not a reason to keep it. ! **Two verdicts are
missing from that table and you must use them by name.** **correct** -- the claim is false and the
true version is worth stating; one real pass applied 82 of these under a four-verdict vocabulary with
nowhere to file them. And **restore** -- a fragment a previous edit severed mid-sentence is neither
checkable nor necessary, so the table routes it to `drop`, deleting the pointer instead of putting
the sentence back. **compact** is not a category either: it is what you do to a `keep`, or to the
remainder a `move` leaves. For **move**, name the destination; ! **it gets the WHOLE block, including
the part that stays in the code**, or the document holds only what nobody kept and reads as a
deletion list -- and a `move` may relocate a *description*, never an **instruction to callers**.

**When comment and code disagree, grammar decides which is wrong:** a **description** that disagrees
means the comment is wrong -> `drop` or `correct`; a **prohibition** that disagrees means the *code*
broke the rule -> file it, and the code moves, not the prose. * **A description written as a negation
is a FORM defect on its own** -- "X is not the case" cannot be checked, only argued backwards from
what the code does; rewrite it positive. A prohibition may stay negative, since no positive form
keeps its force. Measured: a pass that compressed prose took negation from 17% of removed lines to
**22% of what it wrote back** -- compaction *concentrates* negations unless you look for them. ! **A
single `keep` sentence launders every sentence around it**: ruling `keep` because *part* of a block
is load-bearing is the signal to descend a level, and since a block's most defensible sentence is
usually why the whole block survived this long, that is the default outcome, not a rare one.

### The closed acquittal list -- the only reasons a block may leave unraised

`label` (a one-line name for the lines under it) * `states-the-signature` (a summary saying what the
signature says, and nothing more) * `derivation` (hand-worked arithmetic -- what stops an assertion
being an echo of the implementation, and the first thing a careless cap deletes) * `only-guard` (a
warning where nothing goes red; where a test *does* catch the move it is a time-saver, and that is
`compact`) * `names-its-expiry` (it states the condition under which it stops being true) * `marker`
(`TODO`/`FIXME`/`HACK`/`XXX`/`BUG` -- it points outward at work not done, so deleting it to get under a
cap is the cheapest wrong fix available) * `field-comment` (a one-line trailing comment on a
declaration). Anything else is a finding. ! **A block one line over cap is mostly right by
construction** -- cut its least checkable line; do not re-author what is already true and current.
! **A docstring is governed by FORMAT, not length**, and that cuts both ways: do not propose `compact`
on one merely for being long -- **but a docstring carrying a date, a ruling, a quotation or a rationale
paragraph is a finding at any length**, since that is where an evicted `#` block relocates.

**Calibration.** Report **every block that fails a check and no block that does not** -- padding and
pruning cost the same. A tidy short list is a failure mode: in one measured slice **59% of the prose
blocks in six files** were rewritten by the next pass, so a ten-finding report on a file of that shape
is a miss, not selectivity. ! **"This tree looks fine" from a reviewer who has only read guarded code
is not evidence**: an unguarded tree held 11 dangling citations against 0 in the guarded one -- defects
concentrate where the checker cannot see.

## Phase 3 -- present. Always.

**This skill never edits -- the orchestrator included. It ends with the verdict list**, grouped by
verdict, most consequential first, with replacement text inline for every `compact` and `correct`,
and the acquittal tally beside it. Then stop. ! **Even when the human names the edit** -- "cap them",
"fix these", "go do it" -- the deliverable is the report: *"Report only, per the skill -- say the word
and I'll apply the verdicts you accept."* Do not read an imperative as authorization: this review's
whole value is the human's disagreement with it, and **an edit applied is a verdict never ruled on**.
Measured: two runs on near-identical imperative prompts split, one returning a report, one a diff.

Hand these rails to the pass that applies the verdicts -- you are not it. **A block is bounded by CODE,
not by blank lines** (else 9 lines become 6 + blank + 3). **Never change a line of code, a docstring's
meaning, a string literal or an annotation** -- prove it with an AST diff, which caught two cuts that
took real code. **Extract before you cut** on a `move`; **build the `old` text programmatically and
apply on `count == 1` or refuse the file**; **re-read the enclosing block afterwards** -- a pass that
cut seven obituaries wrote seven new ones, the same one twice in one file. ! **Every example above is
invented and every measurement anonymised -- keep it that way**: quoting a real comment teaches a
reviewer to recognise *that comment* instead of the shape, and it rots.
