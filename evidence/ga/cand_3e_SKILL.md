---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched -- a mechanical census first, then
  four angles (currency, functionality, locality, module coherence) in parallel -- and return each
  block with either a finding and a proposed verdict (drop / move / compact / correct / keep) or a
  named acquittal, for the human to rule on. Use this whenever comments or documentation are the
  subject: after finishing a task that added or edited commentary, when a file's comments have
  drifted from what the code now does, when someone says a comment is too long or out of date or
  "isn't this history", when a number or a citation in prose looks stale, when the same rule seems
  to be explained in several places, when reviewing a diff specifically for its prose rather than
  its logic, before a docs or comment burn-down, or when asked whether a module still reads as one
  module. Trigger on phrasings that never say "comment review" -- "these comments are getting out of
  hand", "does this docstring still match", "is this comment still true", "didn't we say this
  somewhere else", "clean up the narration in this file", "why does this file need so much
  explaining" all mean run this. It is NOT /simplify (which reviews code structure and applies its
  fixes) and NOT /code-review (which hunts correctness bugs) -- this one ONLY EVER PROPOSES and never
  edits anything. Run it even when the request sounds like an instruction to cut ("cap these",
  "clean this up"): the deliverable is still the verdict list and applying is a separate step.
---

# comment-review

`/comment-review [cap] [target]` -> census -> 4 reviewers -> a ruling on **every** block -> you decide.

The census guarantees every block is SEEN; the acquittal rule that every one is RULED ON. Sampling
-- not the angles -- caps a review: ten passes over one slice all failed by never opening most blocks.

## The subject is the prose, not the program

Every verdict you return is a verdict on a comment. You will still notice code problems -- **raise
the concern in one line, in a separate section, and do not open an investigation.**

| a COMMENT finding | a CODE finding |
|---|---|
| the comment says the function reads one field; it reads three | the function should not read three |
| the comment claims callers `grep` cannot find | the function is dead and should be deleted |

! **A reviewer straying into correctness is this skill's worst output, measured:** twice, reviewers
read a valid `except A, B:` and reported the file "cannot compile" -- wrong, and volunteered while
reviewing prose. If the claim is about whether the code *runs* it is not your finding; make it
anyway and you owe it an `ast.parse` first.

**The governing law -- look where nothing asserts.** Every false statement found in a real burn-down
was one no assertion touched: not the oldest, not the longest, not the furthest from its code. False
clauses sat *inside* blocks whose other sentences were true -- a count, a call-site claim or a
retracted fact beside a passing test is decoration, and decoration survives the change it describes.

## Arguments

**`cap`** -- an integer, optional: the most lines one `#` run may take. Pass it to the census and to
every reviewer. **This skill has no cap of its own and must not invent one:** if the repo publishes
one in a guard or a lint config use that, say where you got it, and read *how it measures*;
otherwise judge by eye and **report the longest block found**. **`target`** -- a path; else the diff.

## Phase 0 -- scope, then census

```bash
B=$(git merge-base HEAD "${1:-origin/HEAD}" 2>/dev/null) && git diff --name-only "$B"...HEAD
git diff --name-only HEAD          # add this whenever the tree is dirty
```

! **Use the merge-base, never two bare tips** -- `A...B` between tips presents the other branch's
work as yours. If both come back empty, ask; do not fall back to `HEAD~1`, which reviews one commit
of a many-commit branch and reports no error. Scope is a **file list, not a line range**: review
every comment and docstring in those files, not just the changed lines -- comment debt is cumulative
and mostly pre-existing. Skip generated code and data tables; paste the census into every prompt.

```python
"""Census: every comment run and docstring, with candidate flags. Generic; assumes no framework."""

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
    "hist": r"used to|no longer|formerly|previously|renamed|retired|deleted|superseded|reverted"
    r"|was changed|until 20|since 20|originally|round[ -]\d|finding \w?\d|\b[A-F]\d\b",
    "cover": r"guard|pinned|assert|covered|enforc|checked by|refus|call site|caller|test_|tests/"
    r"|coverage|verif|fails if|nothing reads|\bthe only\b|\bthe one\b",
    "count": r"(?<![\w.:])\d{2,}|\b(one|two|three|only|every|all|both|each|exactly|sole)\b",
    "date": r"\b(19|20)\d\d([-/]\d\d?){0,2}\b",
    "neg": r"\b(not|never|cannot|nothing|none|neither|must not|does not|rather than)\b",
    "voice": r"[""!*]|\bsaid\b|\bruled\b|\bdecided\b|\breview\b|\bdeliberately\b|\bmeasured\b",
}


def blocks(
    path,
):  # (line, kind, n_lines, text); a run is bounded by CODE, not by blank lines
    out, runs, prev = [], [], None
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
        tree = ast.parse(src)
    except OSError, SyntaxError, ValueError, IndentationError, tokenize.TokenError:
        return []
    lines = src.splitlines()
    for t in (x for x in toks if x.type == tokenize.COMMENT):
        joined = prev is not None and all(
            not s.strip() for s in lines[prev : t.start[0] - 1]
        )
        runs[-1].append(t) if joined else runs.append([t])
        prev = t.start[0]
    out += [
        (r[0].start[0], "run", len(r), "\n".join(t.string for t in r)) for r in runs
    ]
    out += [
        (n.body[0].lineno, "doc", d.count("\n") + 1, d)
        for n in ast.walk(tree)
        if isinstance(n, DEF) and (d := ast.get_docstring(n, clean=False)) is not None
    ]
    return sorted(out)


root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
names = {p.name for p in root.rglob("*") if p.is_file() and not SKIP & set(p.parts)}
for arg in sys.argv[2:]:
    for line, kind, n, text in blocks(root / arg):
        free = re.sub(r"\b(TODO|FIXME|HACK|XXX|BUG)\b", "", text)  # markers never count
        f = [f"{kind}{n}", f"w{max(map(len, text.splitlines()), default=0)}"]
        f += [k for k, rx in FLAG.items() if re.search(rx, free, re.I)]
        bad = sorted(
            {q for q in CITE.findall(text) if pathlib.Path(q).name not in names}
        )
        print(
            f"{arg}:{line}\t{' '.join(f + (['path:' + ','.join(bad[:3])] if bad else []))}"
        )
print("# every block listed needs a finding or a named acquittal", file=sys.stderr)
```

! **Nothing the census emits is a verdict, and a block with no flag can still be the worst prose in
the file.** Flags are reasons to look; equally, **do not re-derive what it settled.** If you extend
it to resolve dead symbol NAMES: build the corpus from the **AST, never raw text** (raw text holds
the comments being checked, so the check always passes); take string constants from **non-test**
files only (`assert "x" not in y` makes a dead name read alive -- that masked 4 of 7); exclude
`.md`/`.txt`; skip `pyvenv.cfg` trees; and the **head** of a dotted name must resolve.

## Phase 1 -- four reviewers, in parallel

Launch **four subagents in one message**, each with the file list, the census report, the `cap`, and
one angle. Each finding returns `file:line`, the exact claim, **the exact code or test line that
settles it**, and `CONFIRMED` (both sides read) or `SUSPECTED` (not) -- 196 of 202 came back CONFIRMED
once this was asked for, and one reviewer withdrew two rather than pad. Every angle rules on the
blocks the census hands it; none may return "the rest looked fine". Overlap is signal, not waste.

! **Reviewers are READ-ONLY; say so in the prompt** -- four agents editing one file is a race whose
loser's edits vanish, and a reviewer that fixes what it finds has destroyed the finding. **Name the
writable targets and the read-only reference files separately**: a reviewer handed a contract
document as *reference* returned three proposals editing it. ! **Read the prose immediately around
a block before reporting it** -- a deliberate design usually says so directly above itself.

**Every angle carries the same cross-file check.** Before passing a claim, grep the repo for its
SUBJECT -- the number, the symbol, the path, the phrase. A pass edits where it is reading, so it
fixes the copy in front of it and manufactures a disagreement with the copy it never opened.

### Currency -- does this describe the program as it is now? (~45% of findings)

Git holds what the code used to be; a comment narrating its own history does git's job badly. Flag
dated rulings, review-round and finding labels ("fix round 2", "finding B4", "A6", "Part B"), "this
used to...", "X was changed to Y", "no longer", "previously" -- and the sharpest form, **obituaries**:
a name, file, test, flag, config key or *retired internal term* that no longer exists. A renamed
team, lane or subsystem is the one most often missed, because the sentence around it still parses.

! **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar`
is written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Measured on a real deletion the
identifier grep found ten mentions -- all correctly dated tombstones -- and **missed an eleventh
written with a hyphen, the only present-tense claim about the dead path in the set.** A clean grep
reads as a clean file. **Every number is a citation**, unverifiable unless it names the **set it
counts over**, so re-derive the SET first; counts also come with no digit ("both callers").

### Functionality -- does the commentary match what the code does? (~30%)

Read name, signature and docstring, then the body; for every `Args:` / `Returns:` / `Raises:` entry
read the few lines that produce it. Nearly every inversion is refutable inside the same function: a
`Returns:` naming fields in the wrong order, a parameter that does not exist, a documented exception
nothing raises, "Yield" over a function that returns, a hedge promoted to "always". The **summary
line** drifts silently -- changing a return type does not change the sentence about it.

**Prose that DESCRIBES behaviour is wrong far more often than prose that PROHIBITS something.** Rank
by that: a paragraph narrating what the code does is the high-yield target; a rule saying what must
never happen usually still holds. **Claims about coverage and absence license deletions and are
disproportionately wrong** -- "pinned by X", "guarded by Y", "the only call site", "nothing reads
this" each authorise the next person to delete something. Resolve every one, counting string-literal
and dict-key readers no call graph shows.

! **The dangerous cell is a claimed guard that does not exist** -- a deletion justified by coverage
nobody can find reads as safe for exactly that reason, and a real guard has been dropped on a
pointer to a test never written. Where the guard does exist, cite it precisely enough to find. The
mirror is a claimed *absence*: a comment calling a live value decorative, licensing the deletion of
something five call sites read; and an unremarked silent constraint is worth saying out loud.
! **Resolving a citation's target is not verifying its claim** -- read the cited test or file it
`SUSPECTED`. Reachability lives here too: prose describing a branch nothing can reach is a
Functionality finding, not a fifth angle.

**Then read a body's `#` comments as one sequence.** Individually each may be true; end to end they
are the most honest description of the function in the file. The tell is grammatical: a comment that
**sequences** ("now I need to...", "then we...") instead of **constrains** goes nowhere when its line
moves. ! **Report the mismatch; do not resolve it** -- either the docstring grows until it tells the
truth and the *name* becomes wrong, or the function shrinks to what it is called.

### Locality -- does this comment belong to the line it sits on?

**A comment points at the code it is attached to** -- DOWN for a block on its own lines, AT the
declaration for a trailing one; a field comment (`retries: int  # 0 disables the backoff`) is exactly
where it belongs. The finding is a comment about something **else**: a block whose later half
narrates what came before, a rule atop a class that really constrains two literals 200 lines down, a
demonstrative resolving 40 lines away, a block stranded after an unconditional `return`. Second test:
**if this code changed, would the comment become wrong -- and would anyone notice?** Prose that would
quietly survive that change is not local to it, and an unremarked non-obvious constraint is a finding
here too. **Refactoring drift** is this angle's yield: when code moves, its commentary follows and
stops being true, or stays behind.

### Module coherence -- do the comments say this is one module?

Read only the module docstring, the banners and the top-of-file prose. Flag prose announcing two or
three subjects, banners reading like chapter breaks rather than parts of one argument, a docstring
enumerating unrelated responsibilities to be accurate or describing a fraction of its module, and
anything below that contradicts the header. Also flag **the same rule explained in several places**
-- no function owns it, so each site re-explains the whole. A code-shape finding, comment as evidence.

## Phase 2 -- every block gets a finding or a named acquittal

Dedup findings on the same block, then walk the census list. **Silence is a gap in the review, not a
pass** -- a block leaves this phase one of exactly two ways. **A finding**, ruled by two questions in
this order: **is it CHECKABLE?** -- could a reader confirm or refute it from the code as it stands,
without archaeology -- and **is it NECESSARY?** -- would someone changing this code make a **worse
decision** without it, not "is it interesting" and not "is it true".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader verifies and needs | **drop** -- the code says it |
| **not checkable** | **move** -- real rationale, unverifiable in place | **drop** -- history |

Checkable, necessary and **stale** is **correct**, not `drop`: fix it and give the re-derived
population. **Or an acquittal, from this CLOSED list, named in the report:**
`label` (names a thing, asserts nothing), `states-the-signature`, `derivation` (hand-worked
arithmetic that stops an assertion being an echo of the implementation), `only-guard` (the sole
statement of a constraint nothing red catches), `names-its-expiry`. Nothing else acquits, and an
acquittal you have to argue for is a finding. ! **A warning a test DOES catch is a time-saver, not a
guard** -- `compact`, and calling it `only-guard` is the laundering failure below.

! **Truth is not one of the questions, and that is the whole point.** *"Moved here from `x.validate`
when that module was deleted"* is true; the reader needs the check to live **here**, not its travel
history -- accuracy is why it was never deleted, not a reason to keep it. **Rule on sentences, not on
blocks**: a container of six sentences holds six verdicts, the common shape being a live constraint
beside the story of where it came from. ! **A single `keep` sentence launders every sentence around
it** -- ruling `keep` because *part* of a block is load-bearing is the signal to descend a level.

**When comment and code disagree the verdict depends on the kind of claim:** a **description** that
disagrees is wrong -> `correct` or `drop`; a **prohibition** that disagrees is right and **the code
broke the rule** -> file it, and the code moves, not the prose. * **A description written as a
negation is a FORM defect on its own** -- you cannot check "X is not the case" without establishing
what the code does do and arguing backwards, so restate it positive; a prohibition may stay negative.
**Then ask whether what survives is longer than it needs to be** -- `compact` is what you do to a
`keep`. For **move**, name the destination; ! **it gets the WHOLE block, including the part that
stays in the code**, or the document holds only what nobody kept.

! **A `#` run is governed by LENGTH -- it interrupts code -- but a DOCSTRING is governed by FORMAT.**
A date, a ruling, a quotation or a rationale paragraph in a docstring is a finding **at any length**,
and length alone is not one; an evicted `#` block relocates into the docstring beside it, where
nothing measures it. **`TODO`/`FIXME`/`HACK`/`XXX`/`BUG` are free**, never counted against a cap.

### Calibration -- spend a budget, do not fill a quota

**A hit and a false finding do not cost the same.** Against a real burn-down one correctly raised
block is worth roughly **six** wrongly raised ones -- so the bar is *"would I put this above one in
six?"*, not *"am I sure?"*. Both failure modes are real. **Too tidy** is the commoner one: in one
measured slice **59% of the prose blocks in six files** were rewritten by the next pass, so a
ten-finding report on a file of that shape is a miss, not selectivity -- and ! *"this tree looks
fine"* from a reviewer who has only read guarded code is not evidence. **Too long** costs just as
certainly past the point where signal runs out: sixteen measured reviews of one slice, raising the
report from ~260 blocks to ~360, bought **+1.5% recall** and lost a fifth of the precision.

So: **report every flagged block you cannot acquit BY NAME, and stop there.** The acquittal RATE is
the trait that separated the measured reviews, not the acquittal vocabulary -- two reviews using the
identical closed list acquitted 47% and 14% of the same 419 blocks and scored 33 points apart.
! **The tail is not like the head:** near a cap most remaining blocks are one line over, so cut the
least checkable line and **do not re-author a block already true and on subject.**

### What a length rule cannot see, and what must be kept

If the repo enforces a cap with a test, **that test owns the cap -- this skill does not re-litigate
it.** Run this for the three things a line counter cannot see. **A trailing comment that carries
past its own line**: one line after a declaration is the good form, but running on into comment-only
lines beneath it makes the eye go back to find where the sentence started (! a FORMATTING finding,
not a locality one -- lift the whole comment ABOVE the line). **A block split by an inserted
statement**: only the half that still talks about what came before is the finding. **The wrong half
surviving**: check what SURVIVED -- cutting the constraint and keeping the narration passes the cap.

Conversely, a spec that only says what to CUT deletes the load-bearing half. Keep **hand-worked
derivations** (* move one into the DOCSTRING rather than compacting it -- a `#` run is capped because
it interrupts code, a docstring sits at a boundary), **premise guards**, **the discriminator that
scopes a claim**, and **why a constant or fixture is shaped oddly**, on the element itself.

## Phase 3 -- present. Always.

**This skill never edits. It ends with the verdict list**, grouped by verdict, most consequential
first, with replacement text inline for every `compact` and `correct`, and the acquittals named so
the human can see what was ruled on and disagree. ! **Even when the human names the edit** -- "cap
them", "fix these", "go do it" -- the deliverable is the report: *"Report only, per the skill -- say
the word and I'll apply the verdicts you accept."* **An edit applied is a verdict never ruled on**:
two runs on near-identical imperative prompts split, one report and one an 846-line diff.

Hand these rails to the pass that applies the verdicts -- you are not it, and each cost something on
a real 43-file run. **A block is bounded by CODE, not blank lines**, else a 9-line block becomes
6+blank+3. **Never change a line of code, a docstring's meaning, or a string literal** -- prove it by
diffing every non-comment line against the pre-edit file. **Apply with `count == 1` or refuse the
file**; **extract before you cut** on a `move`; preserve each file's line ending; **re-read what you
wrote** -- a pass that cut seven obituaries wrote seven.

`/simplify` reviews code structure and applies what it finds; `/code-review` hunts correctness bugs;
this one reviews prose and **only ever proposes**. ! **Every example above is invented or anonymised
-- keep it that way.** Quoting a real comment teaches a reviewer to recognise *that comment* instead
of the shape, and it rots: the day someone acts on the finding, this file cites a comment that no
longer exists -- a hygiene skill carrying its own obituary.
