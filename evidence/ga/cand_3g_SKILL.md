---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles —
  currency, functionality, locality, module coherence — using parallel subagents that sweep EVERY
  prose block in those files, and return each finding with a proposed verdict (drop / move /
  compact / correct / keep) for the human to rule on. Use this whenever comments or documentation
  are the subject: after a task that added or edited commentary, when a file's comments have
  drifted from what the code now does, when someone says a comment is too long or out of date or
  "isn't this history", when reviewing a diff for its prose rather than its logic, before a docs
  or comment burn-down, or when asked whether a module still reads as one module. Trigger on
  phrasings that never say "comment review" — "these comments are getting out of hand", "does
  this docstring still match", "is this comment still true", "clean up the narration in this
  file", "why does this file need so much explaining" all mean run this. It is NOT /simplify
  (code structure, and it applies its fixes) and NOT /code-review (correctness bugs) — this one
  ONLY EVER PROPOSES and never edits anything, not code and not even the comments it rules on.
  Run it even when asked to cut ("cap these", "clean this up"): the deliverable is still the
  verdict list, and code concerns get raised in a line and left.
---

# comment-review

`/comment-review [cap] [target]` → enumerate every prose block → 4 reviewers sweep all of them →
a verdict per block → you decide → apply.

## The unit of work is the BLOCK LIST, not the file

Phase 0 numbers every comment run and every docstring in scope. Each reviewer walks that list
start to finish and returns **one line per block** — a finding, or a named acquittal. A block
nobody mentioned is a **gap in the review**, not one that passed: a reviewer told to "find the
comments that need attention" returns its confident dozen and stops, while false clauses sit
*inside* blocks whose other sentences are true, same voice, same indent.

⚠ **What stops this degenerating into "flag everything" is not a rule, it is a RATE.** Two sweeps
of one tree, same block list, same acquittal vocabulary below: one acquitted 47% and one 14%, and
the first was the better review by every measure. Copying the words without the restraint is the
failure mode, so **publish the rate** and treat one under a third as a reviewer that stopped
reading and started listing.

## Spend the finding

You are choosing blocks, not collecting them: for every block you raise you are declining
another. Raise them in this order.

**Tier 1 — a FORMAT failure. A finding on sight, no argument required.** Cheap, numerous and
mechanically visible, and in a tree never swept before they are most of the yield.
- a `#` run longer than the published `cap` (see *Arguments* — never invent one);
- a docstring carrying a **date, a ruling, a quotation, an attribution, a "considered and
  rejected", a claim about tests or callers, or a rationale paragraph** — a format failure **at
  any length**, because a docstring says what the code does and what its arguments are;
- a block wider than the repo's line limit, so a formatter would rewrite it anyway.

**Tier 2 — a MARKED block under the cap.** Short does not mean clean, but it moves the burden: a
block at or under cap is a finding only when it carries one of these marks, each a maintained claim.
- a **date**, or a **review label** — "finding 6", "round 3", "fix round 2", "task 8.6", "MINOR";
- a **quotation or attribution** (quoted words, a person's name, "X ruled"), or a **history
  word** — used to, no longer, previously, until, retired, was the, the old;
- a **coverage or consumer claim** — "guarded by", "enforced by", "one definition, shared with
  Y", "read by nothing", "the only caller", a named test, a cited path;
- a **count**, an arithmetic claim, or a **cross-module** assertion about what another file does;
- a **summary sentence adding a claim the signature does not carry** — which is why a one- or
  two-line docstring is NOT automatically clean.

### Tier 3 — the acquittal list, the ONLY reasons to pass a block over

- **`label`** — a one- or two-line comment naming the line it sits on and claiming nothing else
  (`# Kalman gain`, `# 0 disables the backoff`), a numbered step, a section banner, a shebang.
- **`states-the-signature`** — a short docstring, present tense, matching the name, the arguments
  and the return, **citing nothing outside itself and asserting nothing extra**.
- **`derivation`** — a hand-worked calculation whose digits stop an assertion being an echo of
  the implementation, and the *first* thing a careless cap deletes. Over cap it is a `move`
  **into the docstring** — which sits at a boundary and has no cap — never a `compact`.
- **`only-guard`** — a warning against a plausible wrong move where **nothing goes red** if
  someone makes it (verify that; if a test fails it is a time-saver, not a guard), or prose
  **naming its own expiry** — the condition under which it stops being wanted.

Nothing is acquitted for being short, true, well written, new, or sitting under a `⚠`.

⚠ **Do not spend two findings where one lands.** A one-liner touching the same subject as the
block immediately above or below it is part of that block's finding, not a second one. Raise the
containing region once, at its first line.

## The subject is the prose, not the program

You will notice code problems — say so, one line each, in a separate section, and move on.
**Raise a concern, do not open an investigation**, and never give a code finding a
`drop`/`move`/`compact`/`correct`/`keep` verdict. *The comment names a symbol that no longer
exists* is yours; *the symbol should be restored* is not. ⚠ **A reviewer straying into
correctness is this skill's worst measured output** — twice, one read a modern multi-exception
`except` clause and reported the file "cannot compile". A claim about whether the code *runs*
owes an `ast.parse` first.

**Arguments.** `cap` — optional integer, the most lines one `#` block may run. **This skill has
no cap of its own and must not invent one**; a cap published in a lint config or a hygiene test
is the number, and read how it *counts*. With no cap, judge and **report the longest run found**.
`target` — an optional path, defaulting to the files in the diff.

## Phase 0 — enumerate, mechanically

Scope is **whole files, not the diff**. Resolve a base with `git merge-base HEAD @{upstream}`
(else `main`/`master`, else `HEAD~1`), take `git diff --name-only <base>...HEAD`, add
`git diff --name-only HEAD` when dirty, and drop `.md`/`.txt`. Every block inside those files is
in scope: comment debt is cumulative and mostly pre-existing, and the long block that has sat
above a four-line expression for months is the finding a diff-scoped reviewer never sees.
**Paste the output into every reviewer prompt.**

```python
# sweep.py — list every prose block with its mechanical marks. Generic: stdlib only,
# no repo assumptions, safe on a missing path, a missing ref, or an unparseable file.
import ast, io, re, sys, tokenize
from pathlib import Path

CAP, WIDTH = 6, 100
MARKS = {
    "dated": r"\b\d{4}-\d{2}-\d{2}\b",
    "review-label": r"\b(?:finding|round|task|fix) ?[\d.]|\b(?:MINOR|MAJOR|CRITICAL)\b",
    "history": r"\b(?:used to|no longer|previously|formerly|renamed|retired|was the"
    r"|had been|until |instead of|before the fix|the old)\w*\b",
    "coverage-claim": r"\btest_[a-z0-9_]+|\b(?:guard|assert|pinned|enforc|cover|proven"
    r"|shared with|consumer|only caller|read by)\w*",
    "counted": r"\b(?:all|only|every|exactly|both)\s+\w*\s*\d|\b\d+\s*%",
    "cites-a-path": r"[\w./-]*[\w-]\.(?:py|md|toml|json|ya?ml|txt|cfg)\b",
    "quotes-or-attributes": r'"[^"]{6,}"|\bruled\b|\bhis\b|\bher\b',
    "names-a-symbol": r"`[A-Za-z_][\w.]*`",
}
HOLDS = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def blocks(src):
    """Yield (start, end, kind); a comment RUN is bounded by CODE, not by blank lines."""
    out, run, prev, rows = [], [], -9, src.splitlines()
    try:
        toks = [t for t in tokenize.generate_tokens(io.StringIO(src).readline)]
    except Exception:  # unparseable file: report what tokenized, never crash
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
    except Exception:
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
        marks = [f"TIER1-over-cap:{n}"] if kind == "comment" and n > CAP else []
        marks += ["TIER1-wide"] if any(len(x) > WIDTH for x in lines[a - 1 : b]) else []
        marks += [f"docstring:{n}L"] if kind == "docstring" else []
        marks += [k for k, p in MARKS.items() if re.search(p, text, re.I)]
        print(f"{f}:{a}-{b}\t{kind}\t{n}L\t{','.join(marks) or '-'}")
print(f"# {total} blocks; longest comment run {longest}")
```

Then resolve what it only located: every `cites-a-path` against the tree, every `names-a-symbol`
against the names the code defines — build that corpus from the **AST**, never from raw text
(text contains the comments being checked, so the check always passes), from **non-test** files
only (a test pins a deleted field with a negative assertion, which taught one resolver every dead
name was alive), skipping any directory holding `pyvenv.cfg`. ⚠ **Grep the STEM, not the
identifier.** A dead `foo_bar` is written `foo-bar`, `foo bar`, `FooBar`, or "the barrer": an
identifier grep found ten mentions, all correctly dated tombstones, and missed an eleventh
written with a hyphen — the only present-tense claim in the set. ⚠ And **a resolved citation is
not a verified one**: open the target and read it, or mark the finding `SUSPECTED`.

## Phase 1 — four reviewers, each over the WHOLE list

Launch four subagents in one message. Give each the file list, the sweep output, the `cap`, the
tiers, the acquittal list, and one angle. **Tell each, in words, to return a line for every
numbered block.** Overlap between angles is signal, not waste. ⚠ **Reviewers are READ-ONLY; say
so explicitly**, and **name the files UNDER REVIEW, which a proposal may target, separately from
files given as REFERENCE, which it never may** — one reviewer handed a contract as reference
proposed edits *to the contract*, which were applied. Every finding carries `file:line`, the
claim, the line that settles it, and **`CONFIRMED` (both sides read) or `SUSPECTED`**.

### Currency — does this describe the program as it is now? (~45% of yield)

The largest angle by a distance. Git holds what the code used to be; a comment narrating its own
history is doing git's job badly. Flag dated rulings, review-round labels, "this used to…",
"before the fix", and the sharpest form, **obituaries** — a comment naming a symbol, file, test
or flag that no longer exists. A reader greps the name, finds nothing, and reads that as *their*
mistake. Also here: **a counted claim is unverifiable unless it names the POPULATION it counts
over**, so re-derive the SET before the number — a pass correcting a false count produced a
differently-false one, off by 5×. A worked example is current or it is a lie; run it.

### Functionality — does the commentary match what the code does? (~30%)

Read the name, the signature and the docstring, then **read the body** — the flagship false
claims are contradicted two or three lines below themselves. Flag a documented return shape the
code no longer returns, a `Returns:` whose key and value are the wrong way round, an `Args:` entry
describing a guard on the wrong object, a documented exception nothing raises, a summary
summarising the first four lines of a five-job function.

**Claims about coverage are the class that licenses deletions and are disproportionately wrong.**
"pinned by X", "guarded by Y", "the only call site", "read by nothing": each authorises the next
person to delete something, so the claim is checked, never read. A deletion justified by coverage
nobody can find reads as safe for exactly that reason — a real guard has been dropped on a
pointer to a test that never existed, and a comment calling a live config value decorative nearly
licensed deleting what three sites read. Reachability lives here: does the constant have a
reader, the function a caller outside the tests, the hazard a trigger? ⚠ **An unreachable hazard
is not automatically a `drop`** — a precaution's value is having no trigger.

Then read the body's comments **as one sequence**: individually each may be true, end to end they
are the most honest description of the function. **The tell is grammatical — a comment that
sequences instead of constrains** (*"now I need to…"*). Name the fork, do not resolve it.

⚠ **Prose that DESCRIBES behaviour is wrong far more often than prose that PROHIBITS something,
and the two disagree differently.** A description that disagrees with the code → the comment is
wrong. A prohibition that disagrees → the code broke the rule → file it. And a description must
be **POSITIVE**: *"NOT the kernel call site"* never lands on a side you can verify. ⚠ **Resolve
superlatives against their own file** — a "one definition" naming a single member is a tautology.

### Locality — is this prose where the thing it constrains is? (~15%)

A comment is a claim about the code beside it. Flag one about something else — a rule at the top
of a class really constraining two integer literals two hundred lines down; a block whose later
half turns back to narrate what came before; a run sitting *after* an unconditional `return`; a
trailing comment that **runs on into comment-only lines beneath it** (lift it above the line).
The test for anything that survives: **if this code changed, would the comment become wrong, and
would anyone notice?** Flag the inverse too — a line carrying a non-obvious constraint with no
comment at all, where getting it wrong is silent.

### Module coherence — do the comments say this is one module? (~10%)

Read only the module docstring, the banners and the top-of-file prose. Do they describe *one*
thing? Flag a docstring enumerating unrelated responsibilities, banners reading like chapter
breaks, a drifted usage line, and **one rule re-explained in several places** — none owns it.

## Phase 2 — one verdict per block

Dedup blocks reported by more than one angle, then rule. **Before proposing a CHANGE, read the
prose immediately around it** — a deliberate design usually says so directly above itself; but do
not let a neighbour stop you *reporting*. Then: **is it CHECKABLE** from the code as it stands,
without archaeology? **Is it NECESSARY** — would someone changing this code make a *worse
decision* without it? Not "is it interesting", not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** — a constraint the reader needs | **drop** — it narrates the code |
| **not checkable** | **move** — rationale, unverifiable here | **drop** — history |

⚠ **Truth is not one of the questions, and that is the point.** History that is *correct* reads
as earning its place, and does not; accuracy is why it was never deleted, not a reason to keep
it. The exception is arithmetic — pure arithmetic over committed values is checkable without
judgement, so recompute it rather than rule on it.

**`correct` is the fifth verdict**, for a block that must be FIXED rather than cut: the rule it
states is still wanted and the sentence stating it has gone false — a wrong count, a renamed
symbol, a stale citation. Use it whenever `drop` would lose a live constraint.

**Rule on SENTENCES, not on blocks.** A container of six sentences can hold six verdicts, and the
common shape is a live constraint beside the story of where it came from. ⚠ **A single `keep`
sentence launders every sentence around it** — if you are ruling `keep` because *part* of it is
load-bearing, descend a level. **compact** is what you do to a `keep` or to a `move`'s remainder;
for a `move`, name the destination and send the WHOLE block including the half that stays. ⚠
**Account for every digit you propose deleting**: the most repeated defect a compaction pass
introduces is **a measurement replaced by an adjective**. ⚠ And **a block one line over cap is,
by construction, mostly right**: cut the least checkable line, do not re-author.

## Phase 3 — present. Always.

**This skill never edits. It ends with the verdict list.** Report grouped by verdict, most
consequential first, the replacement inline for every `compact` and `correct`, and the coverage
line: *N swept, M findings, K acquitted*. Then stop. ⚠ **Even when the human names the edit** —
"cap them", "go do it" — the deliverable is the report: *"Report only, per the skill — say the
word and I'll apply the verdicts you accept."* An imperative is not authorization, and **an edit
applied is a verdict never ruled on.** Measured: two runs on near-identical imperative prompts
split, one returning a report and the other a diff.

## Rails for the pass that applies these — you are not that pass, and it runs without this file

- **A block is bounded by CODE, not blank lines** — else 9 lines become 6 + blank + 3.
- **Never change a line of code, a docstring's meaning, or a string literal**; prove it by
  diffing every non-comment line, which caught two cuts that took real code.
- **`count == 1` or refuse the whole file**, with the `old` text built programmatically, its
  width checked as well as its line count, and the file's own line ending preserved. **Extract
  before you cut on a `move`** — the other order lost text three times.
- **Re-read what you wrote**: a pass that cut seven obituaries wrote seven new ones.
- **Every example above is invented; keep it that way.** Quoting a real comment teaches
  recognition of *that comment* rather than the shape, and rots into an obituary of its own.
