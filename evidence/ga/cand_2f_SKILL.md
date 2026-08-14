---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched — a mechanical census first, then
  four angles (currency, functionality, locality, module coherence) in parallel — and return every
  block with either a finding and a proposed verdict (drop / move / compact / correct / keep) or a
  named acquittal, for the human to rule on. Use this whenever comments or documentation are the
  subject: after finishing a task that added or edited commentary, when a file's comments have
  drifted from what the code now does, when someone says a comment is too long or out of date or
  "isn't this history", when a number or a citation in prose looks stale, when the same rule seems
  to be explained in several places, when reviewing a diff specifically for its prose rather than
  its logic, before a docs or comment burn-down, or when asked whether a module still reads as one
  module. Trigger on phrasings that never say "comment review" — "these comments are getting out of
  hand", "does this docstring still match", "is this comment still true", "didn't we say this
  somewhere else", "why does this file need so much explaining" all mean run this. It is NOT
  /simplify (which reviews code structure and applies its
  fixes) and NOT /code-review (which hunts correctness bugs) — this one ONLY EVER PROPOSES and never
  edits anything, not code and not even the comments it rules on, because an edit applied is a
  verdict the human never got to rule on. Run it even when the request sounds like an instruction to
  cut ("cap these", "clean this up"): the deliverable is still the verdict list, applying is a
  separate step, and code concerns are raised in a line and left rather than given a verdict.
---

# comment-review

`/comment-review [cap] [target]` → census → 4 reviewers → a ruling on **every** block → you decide.

**Two mechanisms, independent.** The census guarantees every block is SEEN; the acquittal rule that it
is RULED ON. Sampling — not the angles — caps a review: ten independent passes over one slice all failed
the same way, by never opening two thirds of the blocks.

## The subject is the prose, not the program

Every verdict you return is a verdict on a comment. You will still notice code problems — **raise the
concern in one line, in a separate section, and do not open an investigation.** *The comment says the
function reads one field and it reads three* is yours; *it should not read three* is not. ⚠ **A reviewer
straying into correctness is this skill's worst output, measured:** twice, reviewers read a valid
`except A, B:` and reported the file "cannot compile" — wrong, and volunteered while reviewing prose. If
the claim is about whether the code *runs*, it is not your finding; if you make it anyway you owe it an
`ast.parse`.

**The governing law — look where nothing asserts.** **Every false statement found in a real burn-down
was one no assertion touched.** Not the oldest, not the longest, not the furthest from its code: false
clauses sat *inside* blocks whose other sentences were true, same voice, same indentation — one split
mid-sentence, the clause before the comma asserted by the body and true, the clause after asserted by
nothing and false. A count, a call-site claim or a retracted fact sitting *beside* a passing test is
decoration, and decoration survives the change.

## Arguments

**`cap`** — an integer, optional: the most lines one `#` run may take. Pass it to the census and to
every reviewer. **This skill has no cap of its own and must not invent one:** if the repo publishes one
in a guard or a lint config use that, say where you got it, and read *how it measures*; otherwise judge
by eye and **report the longest block found**. **`target`** — a path, optional; defaults to the diff.

## Phase 0 — scope, then census

```bash
B=$(git merge-base HEAD "${1:-origin/HEAD}" 2>/dev/null) && git diff --name-only "$B"...HEAD
git diff --name-only HEAD          # add this whenever the tree is dirty
```

⚠ **Use the merge-base, never two bare tips** — `A...B` between two tips presents the other branch's
work as yours. If both come back empty, ask; do not fall back to `HEAD~1`, which silently reviews one
commit of a many-commit branch and reports no error. Scope is a **file list, not a line range**: review
every comment and docstring in those files, not just the changed lines. Comment debt is cumulative and
mostly pre-existing, and the 54-line block sitting above a four-line expression for months is the
finding worth having — a diff-scoped reviewer never sees it. Skip generated code and data tables, then
run the census over the list and paste its report into **every** reviewer prompt.

```python
"""Comment/docstring census: every block, with candidate flags. Generic; assumes no framework."""

import ast, io, pathlib, re, sys, tokenize  # noqa: E401

SKIP = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "site-packages",
    "__pycache__",
    "build",
}
CITE = re.compile(r"[\w./-]+\.(?:py|md|txt|toml|json|ya?ml|cfg|ini|rst)\b")
DEF = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
FLAG = {  # reasons to LOOK, never verdicts
    "hist": r"used to|no longer|formerly|previously|renamed|retired|deleted|moved to|superseded"
    r"|was changed|until 20|since 20|originally|instead of|reverted|round \d|finding \w?\d",
    "cover": r"guard|pinned|assert|covered|enforc|checked by|proven|refus|call site|caller"
    r"|test_|tests/|coverage|verif|fails if|nothing reads",
    "count": r"(?<![\w.])\d|\b(one|two|three|four|five|ten|only|every|all|both|each|exactly"
    r"|single|sole|no other)\b",
    "date": r"\b(19|20)\d\d([-/]\d\d?){0,2}\b",
    "neg": r"\b(not|never|cannot|nothing|none|neither|must not|does not|isn't|rather than)\b",
    "quote": r"[“”]|\bsaid\b|\bruled\b|\bdecided\b",
}


def blocks(path):

    out, runs, prev = [], [], None
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except OSError, tokenize.TokenError, IndentationError, SyntaxError, ValueError:
        return []
    for t in (x for x in toks if x.type == tokenize.COMMENT):
        runs[-1].append(t) if prev == t.start[0] - 1 else runs.append([t])
        prev = t.start[0]
    out += [(r[0].start[0], "run", "\n".join(t.string for t in r)) for r in runs]
    try:
        tree = ast.parse(src)
    except SyntaxError, ValueError:
        return sorted(out)
    for n in ast.walk(tree):
        if isinstance(n, DEF) and (d := ast.get_docstring(n, clean=False)) is not None:
            out.append((n.body[0].lineno, "doc", d))
    return sorted(out)


root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
names = {p.name for p in root.rglob("*") if p.is_file() and not SKIP & set(p.parts)}
count = 0
for arg in sys.argv[2:]:
    for line, kind, text in blocks(root / arg):
        count += 1
        f = [
            f"{kind}{text.count(chr(10)) + 1}",
            f"w{max(map(len, text.splitlines()), default=0)}",
        ]
        f += [k for k, rx in FLAG.items() if re.search(rx, text, re.I)]
        bad = sorted(
            {q for q in CITE.findall(text) if pathlib.Path(q).name not in names}
        )
        f += [f"path:{','.join(bad[:3])}"] if bad else []
        print(f"{arg}:{line}", " ".join(f))
print(f"# {count} blocks — each needs a finding or a named acquittal", file=sys.stderr)
```

⚠ **Nothing the census emits is a verdict, and a block with no flag can still be the worst prose in the
file.** Flags are reasons to look; equally, **do not re-derive what it settled.** If you extend it to
resolve dead symbol NAMES: build the corpus from the **AST, never raw text** (text holds the comments
being checked, so the check always passes); take string constants from **non-test** files only, since
`assert "x" not in y` makes a dead name read alive (that alone masked 4 of 7); exclude `.md`/`.txt`, or
a doc discussing a deleted symbol vouches for it; skip directories holding `pyvenv.cfg`; and the
**head** segment of a dotted name must resolve — matching any part lets `Dead.meta` pass on `meta`.

## Phase 1 — four reviewers, in parallel

Launch **four subagents in one message**, each with the file list, the census report, the `cap`, and one
angle. Each finding returns `file:line`, the exact claim, **the exact code or test line that settles
it**, and `CONFIRMED` (both sides read) or `SUSPECTED` (not). Every angle rules on the blocks the
census gives it; none of them may return "the rest looked fine".

⚠ **Reviewers are READ-ONLY; say so in the prompt** — four agents editing one file is a race whose
loser's edits vanish, and a reviewer that fixes what it finds has destroyed the finding. **Name the
writable targets and the read-only reference files separately**: a reviewer handed a contract document
as *reference* returned three proposals editing it, landing a false claim in a skill doc. ⚠ **Read the
prose immediately around a block before reporting it** — a deliberate design usually says so directly
above itself, and one finding reopened a decision the line above it had closed. Overlap between angles
is signal, not waste.

**Every angle carries the same cross-file check.** Before you pass a claim, grep the repo for its
SUBJECT — the number, the symbol, the path, the distinctive phrase. A pass edits where it is reading, so
it fixes the copy in front of it and manufactures a disagreement with the copy it never opened, and
every within-file angle passes both halves. Report the STALE copy; where a rule is re-explained at N
sites, report that no function owns it; where code and an extracted mirror disagree, the body settles
it, not the majority copy. A relocation is a duplication until the source is gone.

### Currency — does this describe the program as it is now? (~45% of findings)

Git holds what the code used to be; a comment narrating its own history does git's job badly. Flag dated
rulings, review-round labels ("fix round 2", "finding B4", "Part B"), "this used to…", "X was changed to
Y", "no longer", "previously" — and the sharpest form, **obituaries**: a name, file, test, flag or
config key that no longer exists. A reader greps, finds nothing, and reads it as *their* fault.

⚠ **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar` is
written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Measured on a real deletion, the identifier
grep found ten mentions — all correctly dated tombstones — and **missed an eleventh written with a
hyphen, the only present-tense claim about the dead path in the set.** A clean grep reads as a clean
file, so the failure is self-concealing.

**Every number is a citation**, unverifiable unless it names the **set it counts over** — so re-derive
the SET before the number. Counts also come with no digit ("the one consumer", "both callers"), so treat
every definite-singular as one. Measured: one pass tests green" (3041); a pass correcting a false number
produced a differently-false one by re-counting the wrong population. If the number is not load-bearing,
that is a `drop`, not a `correct`.

### Functionality — does the commentary match what the code does? (~30%)

Read name, signature and docstring, then the body; for every `Args:` / `Returns:` / `Raises:` entry read
the few lines that produce it. Nearly every inversion is refutable inside the same function: a `Returns:
{a: b}` over a body writing `{b: a}`, a parameter that does not exist, a documented exception nothing
raises, a summary saying "Yield" over a function that returns, a hedge promoted to "always". The
**summary line** drifts silently — changing a return type does not change the sentence describing it.

**Claims about coverage and absence license deletions and are disproportionately wrong.** "pinned by X",
"guarded by Y", "the only call site", "nothing asserts this" — each authorises the next person to delete
something. Resolve every one, counting string-literal and dict-key readers no call graph shows. ⚠ **The
dangerous cell is a claimed guard that does not exist:** a deletion justified by coverage nobody can
find reads as safe for exactly that reason, and a real guard has already been dropped in one repo on a
pointer to a test never written. A claimed *absence* is the mirror — a comment calling a live value
decorative, licensing the deletion of something five call sites read.

⚠ **Resolving a citation's target is not verifying its claim** — read the cited test or file it
`SUSPECTED`. Reachability lives here too — prose describing a branch nothing can reach is a
Functionality finding, not a fifth angle.

**Then read a body's `#` comments as one sequence.** Individually each may be true; end to end they are
the most honest description of the function in the file. The tell is grammatical: a comment that
**sequences** ("now I need to…", "then we…") instead of **constrains** narrates the author's path and
goes nowhere when its line moves. ⚠ **Report the mismatch; do not resolve it** — either the docstring
grows until it tells the truth, at which point the *name* is wrong, or the function shrinks to what it
is called, and naming that fork is the deliverable.

### Locality — does this comment belong to the line it sits on?

A comment points DOWN for a block on its own lines, AT the declaration for a trailing one; a field
comment (`retries: int  # 0 disables the backoff`) is exactly where it belongs. The finding is a comment
about something **else**: a block whose later half narrates what came before, a rule atop a class that
really constrains two literals 200 lines down, a demonstrative resolving 40 lines away, a block stranded
after an unconditional `return`. Second test: **if this code changed, would the comment become wrong —
and would anyone notice?** Prose that would quietly survive a change to the code it describes is not
local to it, and an unremarked non-obvious constraint is a finding here too. **Refactoring drift** is
this angle's yield: when code moves, its commentary follows and stops being true, or stays behind.

### Module coherence — do the comments say this is one module?

Read only the module docstring, the banners and the top-of-file prose. Flag prose announcing two or
three subjects, banners reading like chapter breaks rather than parts of one argument, a docstring
enumerating unrelated responsibilities to be accurate or describing a fraction of its module, and
anything below that contradicts the header. Report it as a code-shape finding, comment as evidence.

## Phase 2 — every block gets a finding or a named acquittal

Dedup findings on the same block, then walk the census list. **Silence is a gap in the review, not a
pass** — a block leaves this phase one of exactly two ways.

**A finding**, ruled by four questions. **On subject?** — local to the code beside it, about the program
as it is now. **True?** — of the code, resolved. **Checkable?** — could a reader confirm it from the
tree as it stands, without archaeology? **Necessary?** — would someone changing this code make a *worse
decision* without it; not "is it interesting", and not "is it true".

| | **checkable** | **not checkable** |
|---|---|---|
| **true, on subject, necessary** | **keep** — a verified constraint | **move** — real rationale |
| **stale, false, or not necessary** | **correct** if load-bearing, else **drop** | **drop** — history |

**Or an acquittal, from this closed list, named in the report:** `label` (names a thing, asserts
nothing), `states-the-signature`, `derivation` (hand-worked arithmetic that stops an assertion being an
echo of the implementation), `only-guard` (the sole statement of a constraint nothing red catches),
`names-its-expiry`. Nothing else acquits, and an acquittal you have to argue for is a finding. ⚠ **A
warning a test DOES catch is a time-saver, not a guard** — `compact`, and calling it `only-guard` is the
laundering failure below.

⚠ **Truth is not one of the four, and that is the point.** *"Moved here from `x.validate` when that
module was deleted"* is true; the reader needs the check to live **here**, not its travel history —
accuracy is why it was never deleted, not a reason to keep it. **Rule on sentences, not on blocks**: a
container of six sentences holds six verdicts, the common shape being a live constraint beside the story
of where it came from. ⚠ **A single `keep` sentence launders every sentence around it** — ruling `keep`
because *part* of a block is load-bearing is the signal to descend a level, and a block's most
defensible sentence is usually why the whole block survived this long, so that is the normal outcome.

**When comment and code disagree, the verdict depends on the kind of claim:** a **description** that
disagrees is wrong → `correct` or `drop`; a **prohibition** that disagrees is right and **the code broke
the rule** → file it, and the code moves, not the prose. ⭐ **A description written as a negation is a
FORM defect on its own** — you cannot check "X is not the case" without establishing what the code does
do and arguing backwards, so restate it positive. A prohibition may stay negative; no positive form
keeps its force. **Then ask whether what survives is longer than it needs to be** — `compact` is what
you do to a `keep`, not a sixth verdict. For **move**, name the destination; ⚠ **it gets the WHOLE
block, including the part that stays in the code**, or the document holds only what nobody kept and
reads as a list of discarded things. For **correct**, give the replacement and the re-derived
population.

⚠ **A `#` run is governed by LENGTH — it interrupts code — but a DOCSTRING is governed by FORMAT.** A
date, a ruling, a quotation or a rationale paragraph in a docstring is a finding **at any length**, and
length alone is not one. An evicted `#` block relocates into the docstring beside it, where nothing
measures it, and a length-only rule lets a reviewer `keep` every rationale docstring in the file — watch
for that migration by name. **`TODO`, `FIXME`, `HACK`, `XXX`, `BUG` are free** and never counted against
a cap: each points at work not done, and counting them makes deleting the pointer the way to green.

**Report every block that fails a check, and no block that does not** — padding and pruning cost the
same. But a tidy short list is the more common failure: in one measured slice **59% of the prose blocks
in six files** were rewritten by the next pass, so a ten-finding report on a file of that shape is a
miss, not selectivity. ⚠ **The tail is not like the head:** where a cap is nearly met most remaining
blocks are one line over — 27 of 48 on one burn-down — so cut the least checkable line and **do not
re-author a block already true, current and on subject.** ⚠ **"This tree looks fine" from a reviewer who
has only read guarded code is not evidence:** a tree entering a guard's scope for the first time held 11
dangling citations against 0 in the guarded tree.

## Phase 3 — present. Always.

**This skill never edits. It ends with the verdict list**, grouped by verdict, most consequential first,
with replacement text inline for every `compact` and `correct`, and the acquittals listed by name so the
human can see what was ruled on and disagree. Then stop. ⚠ **Even when the human names the edit** — "cap
them", "fix these", "go do it" — the deliverable is the report: *"Report only, per the skill — say the
word and I'll apply the verdicts you accept."* Its whole value is the human's disagreement with it, and
**an edit applied is a verdict never ruled on**: two runs on near-identical imperative prompts split,
one returning a report and one an 846-line diff.

Hand these rails to the pass that applies the verdicts — you are not it, and each cost something on a
real 43-file run. **A block is bounded by CODE, not blank lines**, else a 9-line block becomes
6+blank+3. **Never change a line of code, a docstring's meaning, or a string literal** — prove it by
diffing every non-comment line against the pre-edit file. **Apply with `count == 1` or refuse the
file**, the old string built programmatically; **extract before you cut** on a `move`; and **re-read the
whole enclosing block** — a pass that cut seven obituaries wrote seven.

`/simplify` reviews code structure and applies what it finds; `/code-review` hunts correctness bugs;
this one reviews prose and **only ever proposes**. ⚠ **Every example above is invented or anonymised —
keep it that way.** Quoting a real comment teaches a reviewer to recognise *that comment* instead of the
shape, and it rots: the day someone acts on the finding, this file cites a comment that no longer exists
— a hygiene skill carrying its own obituary. Measurements cost nothing to anonymise.
