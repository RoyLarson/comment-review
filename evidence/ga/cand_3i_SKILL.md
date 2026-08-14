---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles — currency,
  functionality, locality, module coherence — over a mechanical census of EVERY prose block in those
  files, returning each block a verdict (drop / move / compact / correct / keep) for the human to
  rule on. Use this whenever comments or documentation are the subject: after a task that added or
  edited commentary, when a file's comments have drifted from what the code now does, when someone
  says a comment is too long or out of date or "isn't this history", when reviewing a diff for its
  prose rather than its logic, before a docs or comment burn-down, or when asked whether a module
  still reads as one module. Trigger on phrasings that never say "comment review" — "these comments
  are getting out of hand", "does this docstring still match", "is this comment still true", "clean
  up the narration in this file", "why does this file need so much explaining" all mean run this. It
  is NOT /simplify (code structure, and it applies its fixes) and NOT /code-review (correctness
  bugs) — this one ONLY EVER PROPOSES and never edits anything, not code and not even the comments
  it rules on, because an edit applied is a verdict the human never got to rule on. Run it even when
  asked to cut ("cap these", "clean this up"): the deliverable is still the verdict list.
---

# comment-review

`/comment-review [cap] [target]` → census every block → 4 angles over the whole list → a verdict per
block → you rule → someone else applies.

## The spend rule — what separates a good review from a long one

**The census is not the report.** Phase 0 numbers every prose block in scope; Phase 1 reads all of them;
Phase 2 *chooses* which to put in front of a human. That last step is the skill.

⭐ **The trait is the ACQUITTAL RATE, not the acquittal vocabulary.** Measured across sixteen independent
sweeps of one 419-block corpus: two reviewers used the identical closed acquittal list below; one
acquitted **47%** of blocks and the other **14%**, and the one that acquitted more was the more accurate
by a wide margin *on the same blocks*. Same words, opposite habit. A reviewer inherits reasons to flag
far more readily than reasons to stop, so the stopping rules come first. **The test for raising a block:
would you bet better than one in five that a careful editor would change something inside it?** Not
"could something be said about it" — everything can. Below that bar, acquit and name the reason.
Calibration, from never-swept trees in a verbose house style: under **15%** raised is a *search*, not a
review — roughly half the blocks in such a tree fail something; over **80%** has stopped discriminating,
and the human redoes the work. **Rank what you raise** and say where your confidence falls off.

### The acquittal list — the only reasons to pass a block over

Closed. And you do not acquit by **silence**: an acquittal is a written verdict naming one of these —
one line, cheap enough to afford total coverage, dear enough to force a decision.

- **`label`** — one or two lines naming the line they sit on and claiming nothing else (`# Kalman gain`,
  `# 0 disables the backoff`), a section banner, a shebang.
- **`states-the-signature`** — a short docstring, present tense, matching the name, arguments and
  return, citing nothing outside itself. Three lines and up is no longer this: it is carrying something,
  and what it carries is what you are here to read.
- **`derivation`** — a hand-worked calculation whose digits stop an assertion being an echo of the
  implementation, and the *first* thing a careless cap deletes. Over cap it is a `move` **into the
  docstring** — a boundary, governed by format not length — never a `compact`. ⚠ Extends to **any
  measurement naming the population it counts over**: one pass deleted eleven and kept the adjectives.
- **`only-guard`** — a warning against a plausible wrong move where **nothing goes red** if someone
  makes it. Verify that; where a test does fail it is a time-saver, not a guard.
- **`names-its-expiry`** — prose stating the condition under which it stops being wanted.
- **`positional`** — a warning addressed to a *person* rather than a description of code (*"anyone
  tempted to 'improve' this back should read these three reasons first"*). Its value is standing where
  the tempting edit happens; moving it into a document is deleting it.
- **`tombstone-that-forbids`** — a dead name that is the *subject of a record* rather than a live
  pointer. Shape-identical to an obituary; ask, never silently drop.

Nothing is acquitted for being short, true, well written, new, or under a `⚠`; a glyph is house style,
not a signal. **`TODO`, `FIXME`, `HACK`, `XXX` and `BUG` are free**: they point at work not done, so
they never count toward a cap or split a run.

## The subject is the prose, not the program

Every verdict you return is a verdict on a comment. You will notice code problems — say so, one line
each, in a separate section. **Raise a concern, do not open an investigation.** *The comment names a
symbol that no longer exists* is yours; *the symbol should be restored* is not. ⚠ **A reviewer straying
into correctness is this skill's worst measured output**: twice, one read a modern multi-exception
`except` clause and reported the file "cannot compile". Claim the code does not *run* and you owe it an
`ast.parse` first.

⭐ **The governing law for where to look: LOOK WHERE NOTHING ASSERTS.** Over a whole-tree burn-down every
false statement found sat where no test, type or lint rule could reach — not the oldest prose, not the
longest, not the furthest from its code. False clauses sat *inside* blocks whose other sentences were
true, same voice, same indent; one split **mid-sentence**. A green suite is no evidence about prose: a
comment beside a deleted thing is green *because* the thing is gone. So **defects concentrate where the
checker has never looked**, and **scope is a syntax class, not a file type** — an obituary in an
`assert` message or a `print()` string is the one place the dead name is shown to a human.
**Arguments:** `cap`, the most lines one `#` run may take — **this skill has no cap of its own and must
not invent one**, a cap published in a lint config or hygiene test is the number, and read how that
guard *counts* as well as what it counts to; with none, judge and **report the longest run found**.
`target` — a path, defaulting to the diff.

## Phase 0 — census, mechanically

Scope is **whole files, not the diff**: comment debt is cumulative and mostly pre-existing, and the long
block that has sat above a four-line expression for months is the finding worth having. Build the file
list from `git merge-base HEAD @{upstream}`, falling back through `master`, `main`, then `HEAD~1` — a
missing ref fails loudly, but the fallback silently shrinks the answer to one commit — then `git diff
--name-only <base>...HEAD`, plus `git diff --name-only HEAD` if the tree is dirty.

```python
# sweep.py — census every prose block and tag it. A comment RUN is bounded by CODE, not by
# blank lines. Generic: stdlib only, no repo assumptions, survives a missing/unparsable file.
import ast, io, re, sys, tokenize
from pathlib import Path

CAP, WIDTH = 6, 100  # a repo that publishes its own cap owns the number
FREE = re.compile(
    r"\b(TODO|FIXME|HACK|XXX|BUG)\b"
)  # work not done: never counted, never splits
TAGS = [
    (re.compile(p, re.I), t)
    for p, t in [
        (
            r"\d{4}-\d{2}-\d{2}|[\"“].{12,}[\"”]|\bround \d|\bfinding \w\d|\b(used to|no longer"
            r"|previously|formerly|renamed|retired|instead of|once |old |deleted|removed|replaced"
            r"|superseded|since \d)\b",
            "history",
        ),
        (
            r"\b(guard|assert|pinned|enforc|cover|proven|checked by|caught by|refus|call site|because"
            r"|so that|the reason|which is why)",
            "coverage-or-rationale",
        ),
        (
            r"\b(all|only|every|exactly|both|each|single|one|two|three)\b[^.]{0,24}\d|\d+ ?%"
            r"|\b\d+ (of|out of) \d",
            "counted",
        ),
        (
            r"[\w./-]*[\w-]\.(py|md|toml|json|ya?ml|txt|cfg)\b|\w+\.py:\d+|`[A-Za-z_][\w.]*`"
            r"|\b[a-z_]{3,}\.[a-z_]{3,}\b|\b[a-z]+_[a-z]+\b|\w+\(\)|\b(Args|Returns|Raises):",
            "cites",
        ),
        (r"\b(never|not|cannot|must not|do not|nothing|neither|without)\b", "negated"),
    ]
]
HOLDS = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def blocks(rows):
    """Yield (start, end, kind) for every comment run and docstring in a file, in line order."""
    out, run, prev, src = [], [], -9, "\n".join(rows)
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
    out += [(run[0], run[-1], "comment")] if run else []
    try:
        nodes = [x for x in ast.walk(ast.parse(src)) if isinstance(x, HOLDS) and x.body]
    except SyntaxError, ValueError:
        return sorted(out)
    for nd in nodes:
        f = nd.body[0]
        v = f.value if isinstance(f, ast.Expr) else None
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            out.append(
                (
                    f.lineno,
                    f.end_lineno or f.lineno,
                    "doc:" + getattr(nd, "name", "mod"),
                )
            )
    return sorted(out)


n = longest = 0
for path in sys.argv[1:]:
    if not Path(path).is_file():
        print(f"# missing: {path}")
        continue
    rows = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    for s, e, kind in blocks(rows):
        body, n, size = rows[s - 1 : e], n + 1, e - s + 1
        text, tags = "\n".join(body), []
        longest = max(longest, size if kind == "comment" else 0)
        if kind == "comment" and size - len(FREE.findall(text)) > CAP:
            tags.append(f"OVER-CAP:{size}")
        tags += ["wide"] if any(len(x) > WIDTH for x in body) else []
        tags += [t for r, t in TAGS if r.search(text)]
        print(f"[{n}] {path}:{s}-{e}\t{kind}\t{size}L\t{','.join(tags) or '-'}")
print(f"# {n} blocks; longest comment run {longest}")
```

Then resolve what it only located: every cited path against the tree, every name against what the code
defines — a corpus built from the **AST, never raw text** (raw text holds the comments being checked, so
the check always passes), from **non-test** files only (a test pins a deleted field with a negative
assertion, which taught one resolver every dead name was alive), skipping any directory holding
`pyvenv.cfg`. The **head** segment of a dotted name must resolve, or `Dead.meta` passes on `meta`. ⚠
**Nothing the census emits is a verdict, and an untagged block can be the worst prose in the file.** ⚠
**A resolved citation is not a verified one**: open it and read it, or mark it `SUSPECTED`.

## Phase 1 — four angles, each over the WHOLE list

Launch four subagents in one message with the file list, the census, the `cap`, the acquittal list and
one angle each. **Tell each, in words, to return a line for every numbered block** — a finding or a
named acquittal. ⚠ **Reviewers are READ-ONLY**, and **name two lists: the files UNDER REVIEW, which a
proposal may target, and files given as REFERENCE, which it never may** — one reviewer handed a contract
document to check code against proposed edits *to the contract*, and they were applied. Overlap is
signal: a finding all four report is almost always real.

### Currency — does this describe the program as it is now? (~45% of yield)

The largest angle by a distance. Git holds what the code used to be; a comment narrating its own history
does git's job badly. Flag dated rulings, review-round labels ("fix round 2", "finding B4", "task 8.6"),
"this used to…", "before the fix", and the sharpest form, **obituaries** — a name, file, test or flag
that no longer exists; the reader greps, finds nothing, and reads that as *their* mistake. Widen once:
**a comment claiming a mechanism — an exemption, a hazard, a caller, a rule — must have that mechanism
still exist.**

⚠ **Grep the STEM, not the identifier.** A dead `foo_bar` gets written `foo-bar`, `foo bar`, `FooBar`,
or "the barrer": measured, an identifier grep found ten mentions, all correctly dated tombstones, and
missed an eleventh written with a hyphen — the only present-tense claim in the set, and a clean grep
reads like a clean file. ⚠ **A counted claim is unverifiable unless it names the POPULATION**: re-derive
the SET before the number — a pass correcting a false count produced a differently-false one, off by 5×;
where nothing asserts a number, **delete rather than correct**. ⚠ **A claim your checker cannot parse is
worse than one it can parse and reject.**

### Functionality — does it match the code, and does anything read it? (~30%)

Read name, signature and docstring, then **read the body** — the flagship false claims are contradicted
two or three lines below themselves. Flag a documented return shape the code no longer returns, a
`Returns:` whose key and value are the wrong way round, an `Args:` entry describing a guard on the wrong
object or naming a parameter that does not exist, a documented exception nothing raises, a summary line
summarising the first job of a five-job function.

**Reachability lives here, not in a fifth agent.** Coverage claims are the class that *licenses
deletions* and are disproportionately wrong — "pinned by X", "guarded by Y", "the only call site",
"nothing asserts this". Grep the cited name every time; the dangerous cell is a comment claiming a guard
that does not exist, whose authorised deletion reads as safe for exactly that reason. It fails both
ways: a real guard was deleted on a pointer to a test that never existed, and a comment calling a live
config value decorative nearly licensed deleting what five sites read. ⚠ **An unreachable hazard is not
automatically a `drop`** — a precaution's value is having no trigger. Here too: **resolve superlatives
and collective nouns against their own file** ("single source of truth", "THE only entry point", "these
constants"), since a "one definition" naming a single member is a tautology and an "only entry point" is
often refuted 25 lines down. **Then read the body's comments as one sequence** — end to end they are the
most honest description of the function in the file, and **the tell is grammatical: a comment that
sequences instead of constrains** (*"now I need to…", "then we…"*) goes nowhere when its line moves,
because it was never about the line. ⚠ **Report the mismatch; do not resolve it** — the docstring grows
until the *name* is wrong, or the function shrinks to what it is called.

### Locality — is this prose where the thing it constrains is?

A comment points DOWN for a block on its own lines, AT the declaration for a trailing one; a field
comment is exactly where it belongs. The finding is a comment about something **else**: a rule at the
top of a class really constraining two literals two hundred lines down; a block whose later half turns
back to narrate what came before; a run sitting after an unconditional `return`, or indented into a
branch, explaining code outside it; a trailing comment running on into comment-only lines beneath it.
Test whatever survives: **if this code changed, would the comment become wrong, and would anyone
notice?** Flag the inverse too — a line carrying a non-obvious constraint with no comment at all.
**Refactoring drift** is this angle's biggest yield:.

### Module coherence — do the comments say this is one module?

Read only the module docstring, the banners and the top-of-file prose. Flag prose announcing two or
three subjects, banners reading like chapter breaks, a docstring that must enumerate unrelated
responsibilities to be accurate or that describes a fraction of its module, and any section named for
the **occasion** that produced it. ⚠ Flag a **partial universal**: an "every X" or "never" in a module
docstring covering N siblings — enumerate the Xs, because the exception is what the sentence was written
before. Also flag **the same rule explained in several modules** — no function owns it, so each site
performing part of it restates the whole (measured, one rule in 8 of 9 files under seven names). Where a
claim appears twice check both: the owner stays right, the copy rots.

## Phase 2 — one verdict per block

Dedup, then rule. **Before proposing a change, read the prose around the block and at its call sites** —
a deliberate design usually says so directly above itself. Read the neighbours before you *change*; do
not let them stop you *reporting*, since a neighbour asserting the same false thing is two findings, not
zero. Then: **is it CHECKABLE** from the code as it stands, without archaeology? **Is it NECESSARY** —
would someone changing this code make a *worse decision* without it? Not "is it interesting", not "is it
true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** — a constraint the reader needs | **drop** — it narrates the code |
| **not checkable** | **move** — rationale, unverifiable here | **drop** — history |

⚠ **Truth is not one of the two questions, and that is the point**: history that is *correct* reads as
earning its place and does not. The exception is arithmetic — pure arithmetic over committed values is
checkable without judgement, so recompute it rather than rule on it. **Rule on SENTENCES, not blocks**:
a container of six sentences holds six verdicts, and the common shape is a live constraint beside the
story of where it came from. ⚠ **A single `keep` sentence launders every sentence around it** — ruling
`keep` because *part* of a block is load-bearing is the signal to descend a level. There is no third
category of "warnings".

**When comment and code disagree, which one moves depends on the kind of claim**, and prose that
DESCRIBES behaviour is wrong far more often than prose that PROHIBITS something. A **description** that
disagrees means the comment is wrong — `correct` it, or `drop`; a **prohibition** that disagrees means
the code broke the rule — file it, and the CODE moves while the prose stays. ⭐ **A description written
as a negation is a FORM defect on its own**: you cannot check "X is not the case" without first
establishing what the code *does* do and arguing backwards, so rewrite it positive. A prohibition may
stay negative, since no positive form keeps its force. Measured, a pass compressing prose took negation
from 17% of removed lines to **22% of what it wrote back**.

**The verdicts are `drop`, `move`, `compact`, `correct`, `keep`.** `correct` is for a block that must be
fixed rather than cut — 82 of them in one real pass, the outcome a four-word vocabulary had no word for.
`compact` is what you do to a `keep` or a `move`'s remainder; propose the replacement inline. For
`move`, name the destination and ⚠ **send the WHOLE block, including the half that stays in the code** —
a document holding only what was discarded reads as deletions, not a record. ⚠ **The tail is not like
the head** — late in a burn-down blocks are one line over, not ten (of one final 48, **27 were over by
exactly one**), so **cut the single least-checkable line; do NOT rewrite a block already true and
on-subject.**

## Phase 3 — present. Always.

**This skill never edits — the orchestrator included. It ends with the verdict list.** Report grouped by
verdict, ranked within each, the replacement inline for every `compact` and `correct`, and a coverage
line: *N swept, M raised, K acquitted, and the rate*. Then stop. ⚠ **Even when the human names the
edit** — "cap them", "go do it" — the deliverable is the report: *"say the word and I'll apply the
verdicts you accept."*

**Rails to hand the pass that applies these**, since it runs without this skill loaded: a block is
bounded by **CODE, not blank lines**, or 9 lines become 6 + blank + 3; **change no code, no string
literal and no docstring's meaning**, proved by diffing every non-comment line; apply with **`count ==
1` or refuse the whole file**, `old` built programmatically, **width** checked as well as line count,
the file's own line ending preserved, and on a `move` **extract before you cut**; then **re-run the
census over your own replacements** — a pass that cut seven obituaries wrote seven new ones. **Every
example above is invented. Keep it that way**: quoting a real comment teaches recognition of *that
comment* rather than the shape, and rots into an obituary of its own.
