---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles -- currency,
  functionality, locality, module coherence -- after a mechanical census, and return each block with
  either a finding and a proposed verdict (drop / correct / move / compact / keep) or a named
  acquittal, for the human to rule on. Use this whenever comments or documentation are the subject:
  after a task that added or edited commentary, when a file's comments have drifted from what the
  code now does, when someone says a comment is too long or out of date or "isn't this history",
  when a number or a citation in prose looks stale, when the same rule seems to be explained in
  several places, when reviewing a diff for its prose rather than its logic, before a docs or
  comment burn-down, or when asked whether a module still reads as one module. Trigger on phrasings
  that never say "comment review" -- "these comments are getting out of hand", "does this docstring
  still match", "is this comment still true", "clean up the narration in this file", "why does this
  file need so much explaining" all mean run this. It is NOT /simplify (code structure, and it
  applies its fixes) and NOT /code-review (correctness bugs) -- this one ONLY EVER PROPOSES and never
  edits anything, not code and not even the comments it rules on, because an edit applied is a
  verdict the human never got to rule on. Run it even when asked to cut ("cap these", "clean this
  up"): the deliverable is still the verdict list, applying is a separate step, and code concerns
  are raised in a line and left rather than given a verdict.
---

# comment-review

`/comment-review [cap] [target]` -> census -> 4 reviewers -> a ruling on **every** block -> you decide.

**Two mechanisms, independent.** The census guarantees every block is SEEN; the acquittal rule that
it is RULED ON. Sampling -- not the angles -- is what caps a review: ten independent passes over one
slice failed the same way, by never opening two thirds of the blocks.

! **But a report is a BUDGET, not a bucket.** Measured across sixteen full runs on one slice: going
from 261 findings to 364 bought **+1.5 points of recall** and cost 19 points of precision. Two runs
swept the same 419 blocks with the same acquittal list; one acquitted 47% and one 14%, and the
disciplined one won. **The acquittal RATE is the skill; the LIST is only vocabulary.** Choose
better, not more -- every block you raise is one you chose over another.

## The subject is the prose, not the program

Every verdict you return is a verdict on a comment. You will still notice code problems -- **raise
the concern in one line, in a separate section, and do not open an investigation.** *The comment
says the function reads one field and it reads three* is yours; *it should not read three* is not.
! **A reviewer straying into correctness is this skill's worst measured output:** twice, reviewers
read a valid multi-exception `except` and reported the file "cannot compile". If the claim is about
whether the code *runs*, it is not your finding; if you make it anyway you owe it an `ast.parse`.

**The governing law -- look where nothing asserts.** Every false statement found in a real burn-down
was one no assertion touched. Not the oldest, not the longest, not the furthest from its code: false
clauses sat *inside* blocks whose other sentences were true, same voice, same indentation -- one
split mid-sentence, the clause before the comma asserted by the body and true, the clause after
asserted by nothing and false. A count, a call-site claim or a retracted fact sitting *beside* a
passing test is decoration, and decoration is what survives a change to the thing it describes.

**Arguments.** `cap` -- an integer, optional: the most lines one `#` run may take; pass it to the
census and to every reviewer. **This skill has no cap of its own and must not invent one:** if the
repo publishes one in a guard or a lint config, use that, say where you got it, and read *how it
measures*; otherwise judge by eye and **report the longest run found**. `target` -- a path, optional;
defaults to the files in the diff.

## Phase 0 -- scope, then census

```bash
B=$(git merge-base HEAD "${1:-origin/HEAD}" 2>/dev/null) && git diff --name-only "$B"...HEAD
git diff --name-only HEAD          # add this whenever the tree is dirty
```

! **Use the merge-base, never two bare tips** -- `A...B` between tips presents the other branch's
work as yours. If both come back empty, ask; do not fall back to `HEAD~1`, which silently reviews
one commit of a many-commit branch and reports no error. Scope is a **file list, not a line range**:
review every comment and docstring in those files. Comment debt is cumulative and mostly
pre-existing, and the long block that has sat above a four-line expression for months is the finding
worth having -- a diff-scoped reviewer never sees it. Skip generated code and data tables; paste the
census report into **every** reviewer prompt.

```python
"""Census every comment run and docstring, with candidate flags. Stdlib only, no repo assumptions."""

import ast, io, pathlib, re, sys, tokenize  # noqa: E401

CAP = 6
DEF = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
FLAG = {  # reasons to LOOK, never verdicts
    "hist": r"used to|no longer|formerly|previously|renamed|retired|deleted|moved to|superseded"
    r"|was changed|until 20|since 20|originally|reverted|round \d|finding \w?\d",
    "cover": r"guard|pinned|assert|covered|enforc|checked by|proven|refus|call site|caller"
    r"|test_|tests/|verif|fails if|nothing reads|read by|written by",
    "count": r"(?<![\w.])\d|\b(one|two|three|both|only|every|all|each|exactly|single|sole|never"
    r"|always|no other)\b",
    "date": r"\b(19|20)\d\d([-/]\d\d?){0,2}\b",
    "quote": r"[""]|\bsaid\b|\bruled\b|\bdecided\b",
    "cite": r"[\w./-]+\.(?:py|md|txt|toml|json|ya?ml|cfg|ini|rst)\b|`[A-Za-z_][\w.]*`",
}


def blocks(path):
    """Yield (line, kind, text). A comment RUN is bounded by CODE, not by blank lines."""
    out, runs, prev = [], [], None
    try:
        src = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except OSError, tokenize.TokenError, IndentationError, SyntaxError, ValueError:
        return []
    for t in (x for x in toks if x.type == tokenize.COMMENT):
        runs[-1].append(t) if prev == t.start[0] - 1 else runs.append([t])
        prev = t.start[0]
    out += [(r[0].start[0], "run", "\n".join(t.string for t in r)) for r in runs]
    try:
        for n in ast.walk(ast.parse(src)):
            if (
                isinstance(n, DEF)
                and (d := ast.get_docstring(n, clean=False)) is not None
            ):
                out.append((n.body[0].lineno, "doc", d))
    except SyntaxError, ValueError:
        pass
    return sorted(out)


for arg in sys.argv[1:]:
    if not pathlib.Path(arg).is_file():
        print(f"# missing: {arg}")
        continue
    for line, kind, text in blocks(arg):
        n = text.count("\n") + 1
        tags = [f"{kind}{n}L"] + (
            [f"OVER-CAP:{n}"] if kind == "run" and n > CAP else []
        )
        tags += [k for k, rx in FLAG.items() if re.search(rx, text, re.I)]
        print(f"{arg}:{line}", " ".join(tags))
```

! **Nothing the census emits is a verdict, and a block with no flag can still be the worst prose in
the file.** Flags are reasons to look. If you extend it to resolve dead symbol NAMES: build the
corpus from the **AST, never raw text** (text holds the comments being checked, so the check always
passes); take string constants from **non-test** files only, since `assert "x" not in y` makes a
dead name read alive (that alone masked 4 of 7); skip directories holding `pyvenv.cfg`; and the
**head** segment of a dotted name must resolve -- matching any part lets `Dead.meta` pass on `meta`.

## The two closed lists -- what stops, and what never starts

**Acquittals.** A block leaves the review one of two ways: a finding, or an acquittal named from
this list. You do not get to acquit by silence, an acquittal you have to argue for is a finding, and
nothing acquits for being short, true, well written, new, or sitting under a `!`.

- **`label`** -- one or two lines naming the line they sit on and claiming nothing else.
- **`states-the-signature`** -- a short docstring, present tense, matching name, arguments and
  return, citing nothing outside itself. Three lines or more is carrying something; read it.
- **`derivation`** -- hand-worked arithmetic, the thing that stops an assertion being an echo of the
  implementation. Over cap it is a `move` **into the docstring**, never a `compact`.
- **`only-guard`** -- a warning against a plausible wrong move where **nothing goes red**. Verify
  that; if a test does fail it is a time-saver, not a guard.
- **`names-its-expiry`** -- prose stating when it stops being wanted.

**Suppressions -- signals measured to be mostly noise. Never spend a finding on these alone.**
Each was counted on a real tree; together they turn a 260-finding report into a 360-finding one.

- **a cited path that will not resolve** -- 84 hits, 4 real: worktrees, gitignored runtime data, a
  house style that omits the package prefix.
- **a bare `test_thing` with no path** -- 8 of 8 false. Rule the FORM once per file, not per hit.
- **`!` / `*` callout glyphs** -- 45 on six files, 0 real. House style, not an author panicking.
- **a date that is a command-line argument** -- 4 of 4 false. A runnable example is documentation.
- **`no longer` / `as before` in a present-tense spec** -- only `used to`, `previously` and
  `retracted` carry the tense that makes a retraction.
- **a backticked name that exists *because* it does not** -- counterfactuals, misspellings quoted as
  examples, rejected alternatives, third-party names.
- **a precaution with no current trigger** -- a precaution's value *is* having no trigger.
- ! Suppressed means **"not a finding on that ground"** -- the block is still read for what it says.

## Phase 1 -- four reviewers, in parallel

Launch **four subagents in one message**, each with the file list, the census report, the `cap`, both
lists above, and one angle. Each finding returns `file:line`, the exact claim, **the code or test
line that settles it**, and `CONFIRMED` (both sides read) or `SUSPECTED` (not).

! **Reviewers are READ-ONLY; say so in the prompt** -- one that fixes what it finds has destroyed the
finding. **Name the writable targets and the read-only reference files separately**: a reviewer
handed a contract document as *reference* returned three proposals editing it. ! **Read the prose
around a block before proposing a CHANGE** -- a deliberate design usually says so directly above
itself. Before *reporting*, no: a neighbour asserting the same false thing is two findings, not zero.

### Currency -- does this describe the program as it is now? (~45% of findings)

Git holds what the code used to be; a comment narrating its own history does git's job badly. Flag
dated rulings, review-round labels ("fix round 2", "finding B4"), "this used to...", "X was changed to
Y" -- and the sharpest form, **obituaries**: a name, file, test, flag or config key that no longer
exists. A reader greps, finds nothing, and reads it as *their* fault.

! **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar`
is written `foo-bar`, `foo bar`, `FooBar`, or "the barrer". Measured, an identifier grep found ten
mentions -- all correctly dated tombstones -- and **missed an eleventh written with a hyphen, the only
present-tense claim in the set.** A clean grep reads as a clean file; the failure is self-concealing.

**Every number is a citation**, unverifiable unless it names the **set it counts over** -- re-derive
the SET before the number, and treat every definite singular ("the one consumer", "both callers") as
a count with no digit. ! **Redo any arithmetic you can see**: three retracted divisions in one file
all rounded to the same answer and all three were wrong.

### Functionality -- does the commentary match what the code does? (~30%)

Read name, signature and docstring, then **read the body**; for every `Args:` / `Returns:` /
`Raises:` entry read the two-to-four lines that produce it. Nearly every inversion is refutable
inside the same function: a `Returns: {a: b}` over a body writing `{b: a}`, "mutated in place" three
lines above `after = dict(x); return after`, a parameter that does not exist, an exception nothing
raises, a hedge promoted to "always". The **summary line** drifts silently -- changing a return type
does not change the sentence describing it.

* **A claim of the form "every X does Y" is a CHECKLIST: enumerate the Xs.** This is the largest
hole measured -- a module bullet promising every pass writes its failures to one file was false for
two of seven passes, and *every* angle passed it, because the sentence is true of the pass in front
of you. The reviewer that got the matching case right **enumerated the subjects**; the one that got
it wrong **edited the sentence**.

**Claims about coverage and absence license deletions and are disproportionately wrong.** "pinned by
X", "guarded by Y", "the only call site", "nothing asserts this" -- each authorises the next person
to delete something. Resolve every one, counting string-literal and dict-key readers no call graph
shows, and ask whether anything **outside the tests** reaches it. ! The dangerous cell is a claimed
guard that does not exist: a deletion justified by coverage nobody can find reads as safe for
exactly that reason. ! **Resolving a citation's target is not verifying its claim** -- open it, or
file the finding `SUSPECTED`. Reachability lives here, not in a fifth angle.

**Then read a body's `#` comments as one sequence.** Individually each may be true; end to end they
are the most honest description of the function in the file. The tell is grammatical: a comment that
**sequences** ("now I need to...", "then we...") instead of **constrains** narrates the author's path.
! Report the mismatch; do not resolve it -- the docstring grows until the *name* is wrong, or the
function shrinks to what it is called, and naming that fork is the deliverable.

### Locality -- does this comment belong to the line it sits on?

A comment points DOWN for a block on its own lines, AT the declaration for a trailing one. The
finding is a comment about something **else**: a block whose later half narrates what came before, a
rule atop a class that really constrains two literals 200 lines down, a demonstrative resolving 40
lines away, a run stranded after an unconditional `return` or inside a branch that returns before
reaching what it explains. * **A trailing comment that runs on into comment-only lines beneath it is
a finding on sight** -- the continuation now describes the *next* declaration, the class a
cap-enforcement pass manufactures and no linter sees. Second test: **if this code changed, would the
comment become wrong -- and would anyone notice?**

### Module coherence -- do the comments say this is one module?

Read only the module docstring, the banners and the top-of-file prose. Flag prose announcing two or
three subjects, banners reading like chapter breaks rather than parts of one argument, a docstring
enumerating unrelated responsibilities to be accurate or describing a fraction of its module, and
anything below that contradicts the header. Where a rule is re-explained at N sites, no function
owns it. **Where a claim appears in several files the body settles it, not the majority copy.**

## Phase 2 -- one ruling per block

Dedup findings on the same block, then rule. **On subject?** -- local, and about the program as it is
now. **True?** -- of the code, resolved. **Checkable?** -- from the tree as it stands, without
archaeology. **Necessary?** -- would someone changing this code decide *worse* without it?

| | **checkable** | **not checkable** |
|---|---|---|
| **true, on subject, necessary** | **keep** -- a verified constraint | **move** -- real rationale |
| **stale, false, or not necessary** | **correct** if load-bearing, else **drop** | **drop** -- history |

! **Truth is not the deciding question, and that is the point.** *"Moved here from `x.validate` when
that module was deleted"* is true; the reader needs the check to live **here**, not its travel
history. **Rule on sentences, not on blocks**: six sentences hold six verdicts, the common shape
being a live constraint beside the story of where it came from. ! **A single `keep` sentence
launders every sentence around it** -- ruling `keep` because *part* of a block is load-bearing is the
signal to descend a level.

**When comment and code disagree, the verdict depends on the kind of claim.** A **description** that
disagrees is wrong -> `correct` or `drop`. A **prohibition** that disagrees is right and **the code
broke the rule** -> file it; the code moves, not the prose. Description is wrong far more often than
prohibition -- weight your attention that way. * **A description written as a negation is a FORM
defect on its own**: you cannot check "X is not the case" without first establishing what the code
does do. A prohibition may stay negative.

**`compact` is what you do to a `keep`, not a sixth verdict.** For **move**, name the destination; !
it gets the **WHOLE block, including the part that stays in the code**. For **correct**, give the
replacement and the re-derived population. ! **Account for every digit you delete**: name what in
the working tree the removed sentence was the only record of. The commonest damage a compaction pass
does is **a measurement replaced by an adjective**, and it always looks like a legitimate trim.

! **A `#` run is governed by LENGTH -- it interrupts code -- but a DOCSTRING is governed by FORMAT.** A
date, a ruling, a quotation or a rationale paragraph in a docstring is a finding **at any length**,
and length alone is not one. Watch for the migration: an evicted `#` block relocates into the
docstring beside it, where nothing measures it. **`TODO`, `FIXME`, `HACK`, `XXX`, `BUG` are free**
and never counted against a cap -- counting them makes deleting the pointer the cheapest way to green.

! **The tail is not like the head.** Where a cap is nearly met, most remaining blocks are one line
over -- 27 of 48 on one burn-down -- so cut the single least checkable line and **do not re-author a
block already true, current and on subject.**

## Phase 3 -- present. Always.

**This skill never edits. It ends with the verdict list**, grouped by verdict, most consequential
first, with replacement text inline for every `compact` and `correct`, and a coverage line -- *N
swept, M findings, K acquitted by name*. Then stop. ! **Even when the human names the edit** -- "cap
them", "fix these", "go do it" -- the deliverable is the report: *"Report only, per the skill -- say
the word and I'll apply the verdicts you accept."* Its whole value is the human's disagreement with
it, and **an edit applied is a verdict never ruled on**: two runs on near-identical imperative
prompts split, one returning a report and one an 846-line diff.

Hand these rails to the pass that applies the verdicts -- you are not it, and each cost something on
a real 43-file run. **A block is bounded by CODE, not blank lines**, else a 9-line block becomes
6+blank+3. **Never change a line of code, a docstring's meaning, or a string literal** -- prove it by
diffing every non-comment line against the pre-edit file. **Apply with `count == 1` or refuse the
file**, the old string built programmatically; **extract before you cut** on a `move`; and **re-read
the whole enclosing block afterwards** -- a pass that cut seven obituaries wrote seven new ones.

! **Every example above is invented or anonymised -- keep it that way.** Quoting a real comment
teaches recognition of *that comment* rather than the shape, and it rots into an obituary of its own.
