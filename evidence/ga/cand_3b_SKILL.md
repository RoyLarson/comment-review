---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles — currency,
  functionality, locality, module coherence — after a mechanical census, and return each finding with
  a proposed verdict (drop / move / compact / correct / keep) for the human to rule on. Use this
  whenever comments or documentation are the subject: after finishing a task that added or edited
  commentary, when a file's comments have drifted from what the code now does, when someone says a
  comment is too long or out of date or "isn't this history", when reviewing a diff specifically for
  its prose rather than its logic, before a docs or comment burn-down, or when asked to check whether
  a module still reads as one module. Trigger on phrasings that never say "comment review" — "these
  comments are getting out of hand", "does this docstring still match", "is this comment still true",
  "clean up the narration in this file", "why does this file need so much explaining" all mean run
  this. It is NOT /simplify (which reviews code structure and applies its fixes) and NOT /code-review
  (which hunts correctness bugs) — this one ONLY EVER PROPOSES and never edits anything, not code and
  not even the comments it rules on, because an edit applied is a verdict the human never got to rule
  on. Run it even when the request sounds like an instruction to cut ("cap these", "clean this up"):
  the deliverable is still the verdict list, and applying is a separate step. It is explicitly not a
  reviewer's job to judge whether the code works: code concerns get raised in a line and left, while
  every verdict returned is a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` → census → triage → 4 angles → a verdict per finding → you decide.

## The subject is the prose, not the program

**It is not a reviewer's job to decide whether the code works.** Every verdict you return is a verdict
on a comment. You will still notice code problems — say so in a separate section, one line each, and
**never** give a code finding a `drop`/`move`/`compact`/`correct`/`keep` verdict.

*The comment says it reads one field; it reads three* is yours; *it should not read three* is not.
*It names a symbol that no longer exists* is yours; *the symbol should be restored* is not. **Raise a
concern, do not open an investigation.** ⚠ Measured: a reviewer read `except ValueError, TypeError:`
and reported the file "cannot compile" — wrong, and volunteered while reviewing prose. A claim about
whether the code RUNS is not yours; make it anyway and you owe it an `ast.parse` first.

**Arguments.** `cap` — optional integer, the most lines one `#` run may take. **This skill has no cap
of its own and must not invent one**; a cap the repo publishes (a lint config, a hygiene test) wins,
and read how it *counts*. With none, judge, and **report the longest run found**. `target` — a path,
defaulting to the files in the diff.

## Phase 0 — census, mechanically

Scope is **whole files, not the diff**: `git diff --name-only $(git merge-base HEAD @{upstream})` (or
`main`, or `HEAD~1`; add `git diff --name-only HEAD` when dirty) yields a FILE LIST, and every block
inside those files is in scope. Comment debt is cumulative and mostly pre-existing — the long block
that has sat above a four-line expression for months is the finding worth having. ⚠ Check which range
returned something: an empty and a one-commit range both *succeed* and review less than you meant.

```python
"""Census every prose block on argv: path, line span, kind, length, signals."""

import ast, io, re, sys, tokenize
from pathlib import Path

CAP, WIDTH = 6, 100
TAGS = [
    (re.compile(p, re.I), t)
    for p, t in [
        (r"\b(?:19|20)\d\d-\d\d-\d\d\b", "dated"),
        (r"\b(?:round \d|finding \w+|wave|review|task[- ]?\d)", "review-label"),
        (
            r"\b(?:used to|no longer|previously|formerly|renamed|retired|was the|had been"
            r"|instead of|before the fix|until|since)\b",
            "history",
        ),
        (
            r"\b(?:guard|assert|pinned|enforc|cover|prov(?:es|en)|tested|test_\w+)",
            "coverage",
        ),
        (r"\b(?:all|only|every|exactly|both|single|the one|sole)\b|\b\d", "counted"),
        (r"[\w./-]*[\w-]\.(?:py|md|toml|json|ya?ml|txt|cfg)\b", "cites-a-path"),
        (r"[“\"][^”\"]{25,}[”\"]", "quotation"),
        (r"`[A-Za-z_][\w.]*`", "names-a-symbol"),
    ]
]
HOLDS = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def blocks(src):
    """(start, end, kind) per block. A `#` RUN is bounded by CODE, not by blank lines."""
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
        )  # a trailing one is its own block
        if run and (t.start[0] != prev + 1 or not own):
            out.append((run[0], run[-1], "comment"))
            run = []
        run.append(t.start[0])
        prev = t.start[0] if own else -9
    if run:
        out.append((run[0], run[-1], "comment"))
    try:
        nodes = list(ast.walk(ast.parse(src)))
    except SyntaxError, ValueError, RecursionError:
        return sorted(out)
    for node in nodes:
        b = getattr(node, "body", []) if isinstance(node, HOLDS) else []
        v = getattr(b[0], "value", None) if b and isinstance(b[0], ast.Expr) else None
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            out.append((b[0].lineno, b[0].end_lineno or b[0].lineno, "docstring"))
    return sorted(out)


total = 0
for f in [a for a in sys.argv[1:] if not a.startswith("-")]:
    if not Path(f).is_file() or Path(f).suffix != ".py":
        print(f"# skipped: {f}")
        continue
    lines = Path(f).read_text(encoding="utf-8", errors="replace").splitlines()
    for a, b, kind in blocks("\n".join(lines)):
        text, n = "\n".join(lines[a - 1 : b]), b - a + 1
        total += 1
        tags = [f"OVER-CAP:{n}"] if kind == "comment" and n > CAP else []
        tags += ["over-width"] if any(len(x) > WIDTH for x in lines[a - 1 : b]) else []
        tags += [t for p, t in TAGS if p.search(text)]
        print(f"{f}:{a}-{b}\t{kind}\t{n}L\t{','.join(tags) or '-'}")
print(f"# {total} blocks")
```

Paste the census into every reviewer prompt. Then resolve what it only located: every `cites-a-path`
against the tree, every `names-a-symbol` against the names the code DEFINES — build that corpus from
the **AST**, since one built from raw text contains the comments being checked and always passes, and
skip any directory holding `pyvenv.cfg` or an installed package will whitelist a dead name. ⚠ **A
resolved citation is not a verified one**: a citation asserts something *about* its target, so open it
or mark the finding `SUSPECTED`. Correcting a stale path removes the only symptom a machine can see
and leaves the false claim reading as freshly confirmed.

## The triage — this is where the yield is decided

You are spending a budget, not filling a quota. **For every block you raise you are choosing it over
another you did not**, so sort the census into three piles BEFORE any angle reads anything.

- **SWEEP** — every over-cap `#` run, every docstring of three lines or more, every over-width block.
  All four angles read every one, no exceptions.
- **READ** — `#` runs of four to six lines: at the cap, carrying content. Flag on any angle's finding.
- **ACQUIT** — one- to three-line `#` runs and one/two-line docstrings. Acquitted by default.

**The SWEEP pile is where the defects are, and it is not close.** A run past the cap is a paragraph in
a comment's clothing; a docstring past two lines carries something beyond the signature. Both are
where a date, a count and a coverage claim go to hide. A one-line label (`# Kalman gain`, `# 0
disables the backoff`) claims nothing and hides nothing.

⚠ **A short block is un-acquitted — and joins READ — by exactly one of these, and by nothing else:**

- it carries a **date, a review label, a wave/round/finding id, or a quotation**;
- it narrates **history** ("used to", "was changed", "before the fix", "no longer");
- it is a **severed continuation** — a trailing `#` comment whose sentence runs on into the block
  below, or a run that starts mid-clause. Three in one dataclass once ended on "…, no" and "…, a"
  because a neighbouring block was rewritten under them; nothing red fires on a sentence that stops;
- it makes a claim about **another module, another file, or a test** ("the one definition, shared
  with X", "guarded by Y");
- it is **over-width**, or it names a symbol or path that does not resolve.

Nothing is un-acquitted for being interesting, well written, or sitting under a `⚠`; nothing is
acquitted for being short if one of the five fires. **Say how many you acquitted** — a run that
acquits 5% of a tree has not triaged, it has flagged everything, and a report of every block in the
file scores exactly as badly as a report of ten.

## Phase 1 — four angles, in parallel

Launch four subagents in one message; give each the file list, the census, the triage piles, the `cap`
and one angle. Merging angles measurably loses recall — keep them four. Each finding carries
`file:line` **of the offending sentence, not of the block's first line**, the exact claim, the line
that settles it, and `CONFIRMED` (both sides read) or `SUSPECTED` (not).

⚠ **Reviewers are READ-ONLY; say so**, and name two lists: files UNDER REVIEW, which a proposal may
target, and files given only as REFERENCE, which it never may — a reviewer handed a contract document
as reference returned three edits *to the contract*, and they were applied.

### Currency — does this describe the program as it is now? (~45% of yield)

Ask, per block: does every symbol, file, flag and constant named here still exist? Stop when it
resolves — or when the dead name is the deliberate SUBJECT of a record rather than a pointer. Then:
a date, a finding id, a round or wave number, "this used to…", "was changed to", "we tried" —
**all of it is git's job, done badly.** Stop only when the date is part of a data format or a runnable
command. A **quotation or an attribution never survives**: that is provenance, and provenance lives in
the history. The sharpest form is an **obituary** — a reader greps, finds nothing, blames himself.

⚠ **Grep the STEM, not the identifier.** A dead `foo_bar` gets written `foo-bar`, `foo bar`, `FooBar`,
"the barrer". Measured: an identifier grep found ten mentions, all correctly dated tombstones, and
missed an eleventh written with a hyphen — the only present-tense claim in the set. A clean grep reads
exactly like a clean file.

**Every number is a citation.** A count is unverifiable unless it names the SET it counts over, so
re-derive the population before the number; stop only when you re-derived it and it held. A pass
correcting a false count produced a differently-false one, off by 5×, from the wrong population.

### Functionality — does the commentary match what the code does? (~30%)

Read name, signature and docstring, then **read the body** — the flagship false claims are contradicted
two or three lines below themselves. Does the summary line still name what the thing does and returns?
Does every `Args:`/`Returns:`/`Raises:` entry exist, in that shape and that direction? A documented
exception nothing raises, a raise nothing documents? Stop when the body does it.

**Claims about coverage are the class that licenses deletions, and are disproportionately wrong.**
"pinned by X", "guarded by Y", "the only call site", "nothing asserts this" — each authorises the next
person to delete something.

⚠ **The dangerous cell is CLAIMS ONE / DOES NOT EXIST**: a deletion justified by coverage nobody can
find, which reads as safe for exactly that reason. Grep the cited name every time. A real guard was
dropped in one repo on a pointer to a test never written; the inverse also happens, a comment calling
a live config value decorative. Reachability lives here, not in a fifth angle: does
the constant have a reader, the function a caller outside tests, the hazard a trigger? ⚠ But **an
unreachable hazard is not automatically a `drop`** — a precaution's value is having no trigger.

⚠ **Prose that DESCRIBES behaviour is wrong far more often than prose that PROHIBITS.** A description
that disagrees with the code → the comment is wrong. A prohibition that disagrees → the code broke the
rule → file that. And a description must be **POSITIVE**: "NOT the kernel call site" lands on no side
you can check, because the reader must first establish what the code does and argue backwards.

⚠ **Resolve superlatives and collective nouns against their own file.** "single source of truth", "THE
only entry point", "these constants", "every X does Y" — enumerate the Xs. A "one definition" naming
one member is a tautology; an "only entry point" is refuted 25 lines down often enough to always check.

### Locality — does this prose sit where the thing it constrains is?

A block points DOWN; a trailing comment points AT its declaration. Does it constrain the line it sits
on, or something else — a rule at the top of a class really binding two literals two hundred lines
down, a block whose later half turns back to narrate what came before, a run stranded after an
unconditional `return`, a run between two statements annotating neither? Stop when its subject is the
next line. Second test: **if this code changed, would the comment become wrong, and would anyone
notice?** Flag the inverse too — a non-obvious constraint with no comment, where getting it wrong is
silent. **Refactoring drift is this angle's biggest yield**: when code moves, its commentary either
moves with it, stays behind describing something that left, or follows and stops being true.

### Module coherence — do the comments say this is one module?

Read only the module docstring, the banners and the top-of-file prose. Do they describe *one* thing?
Flag a docstring that must enumerate unrelated responsibilities to be accurate, or that describes a
fraction of its module; banners reading like chapter breaks; and **the same rule re-explained in
several places** — no function owns it, so each site performing part of it restates the whole (a
code-shape finding, with the comment as evidence). Where one claim appears in several files, check
every copy: the owner stays right while the copy rots.

## Phase 2 — one verdict per finding

Dedup, then rule. **Before proposing a CHANGE, read the prose immediately around it** — a deliberate
design usually says so directly above itself. Read the neighbours before you *change*, not before you
*report*: a neighbour asserting the same false thing is two findings, not zero. Then: **is it
CHECKABLE** from the code as it stands, without archaeology? **Is it NECESSARY** — would someone
changing this code decide *worse* without it? Not "is it interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** — a constraint the reader needs | **drop** — it narrates the code |
| **not checkable** | **move** — rationale, unverifiable here | **drop** — history |

⚠ **Truth is not one of the questions, and that is the point.** History that is *correct* reads as
earning its place, and does not; accuracy is why it was never deleted, not a reason to keep it. A
fifth verdict, **`correct`**, is for a block that must be FIXED rather than cut: a stale count is
re-derived or deleted, never softened to "most"; a mis-formatted citation is reformatted, never
dropped. A repair keeps the checkability the original had — and detection being right does not make
the repair right, so check the two separately.

**Rule on SENTENCES, not on blocks.** A container of six sentences can hold six verdicts, the common
shape being a live constraint beside the story of where it came from. ⚠ **A single `keep` sentence
launders every sentence around it** — ruling `keep` because *part* is load-bearing means descend.

**compact** is not a sixth verdict — it is what you do to a `keep` or to a `move`'s remainder. For a
`move`, name the destination and send the **WHOLE block, including the half that stays in the code**;
a document holding only what was discarded reads as a deletion list. ⚠ **Account for every digit you
propose deleting** — the most repeated defect a compaction introduces is a measurement replaced by an
adjective. ⚠ **A block one line over cap is by construction mostly right**: cut the least checkable
line, do not re-author.

### What must be KEPT — a spec that only cuts deletes the load-bearing half

- **Hand-worked derivations.** ⭐ Over cap, `move` one into the DOCSTRING (a boundary, so no cap
  reaches it) rather than compacting it — never compress the digits.
- **Premise guards**, **the discriminator that scopes a claim**, **why a fixture or constant is shaped
  oddly** written ON the element, and **a comment naming its own expiry condition**.
- **A warning against a plausible wrong move — ONLY where nothing goes red.** Mutant-check that; where
  a test does fail, it is a time-saver, not a guard, and it is `compact`.
- But **a docstring carrying a date, a ruling, a quotation or a rationale paragraph is a finding at
  ANY LENGTH** — a FORMAT failure, not a length one; long is not by itself a violation.

## Phase 3 — present. Always.

**This skill never edits. It ends with the verdict list** — grouped by verdict, most consequential
first, the replacement inline for every `compact` and `correct`, and a coverage line: *N censused, S
swept, M findings, K acquitted.* Then stop.

⚠ **Even when the human names the edit** — "cap them", "fix these", "go do it" — the deliverable is
the report: *"Report only, per the skill — say the word and I'll apply the verdicts you accept."* An
imperative is not authorization; this review's whole value is the human's disagreement with it, and
**an edit applied is a verdict never ruled on.** Measured: two runs on near-identical prompts split,
one returning a report and the other an 846-line diff.

## Rails for the pass that applies these — you are not it, and it runs without this file loaded

- **A block is bounded by CODE, not blank lines** — else 9 lines become 6 + blank + 3.
- **Never change a line of code, a docstring's meaning, or a string literal**; prove it by diffing
  every non-comment line, which caught two cuts that took real code with them.
- **`count == 1` or refuse the whole file**, the `old` text built programmatically rather than
  transcribed, its width checked as well as its line count, the file's own line ending preserved.
  **Extract before you cut** on a `move` — the other order lost the text three times.
- **Before changing any number, name or path in prose, grep it repo-wide** — the usual outcome
  otherwise is three of four siblings fixed. **Then re-read what you wrote:** a pass that cut seven
  obituaries wrote seven new ones, and wrote over-length blocks while removing over-length blocks.

**Every example above is invented or anonymised. Keep it that way** — quoting a real comment teaches
recognition of *that comment*, not of the shape, and rots into an obituary of its own. **Add to the
triage; never widen it** — a pile is only worth having if something lands outside it.
