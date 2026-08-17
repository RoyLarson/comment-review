---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched -- a mechanical census of every
  prose block first, then four angles (currency, functionality, locality, module coherence) -- and
  return every block with either a finding or a named acquittal, each finding carrying a proposed
  verdict (drop / move / compact / correct / keep) for the human to rule on. Use this whenever
  comments or documentation are the subject: after finishing a task that added or edited commentary,
  when a file's comments have drifted from what the code now does, when someone says a comment is too
  long or out of date or "isn't this history", when reviewing a diff specifically for its prose rather
  than its logic, before a docs or comment burn-down, or when asked to check whether a module still
  reads as one module. Trigger on phrasings that never say "comment review" -- "these comments are
  getting out of hand", "does this docstring still match", "is this comment still true", "clean up the
  narration in this file", "why does this file need so much explaining" all mean run this. It is NOT
  /simplify (which reviews code structure and applies its fixes) and NOT /code-review (which hunts
  correctness bugs) -- this one ONLY EVER PROPOSES and never edits anything, not code and not even the
  comments it rules on, because an edit applied is a verdict the human never got to rule on. Run it
  even when the request sounds like an instruction to cut ("cap these", "clean this up"): the
  deliverable is still the verdict list, and applying is a separate step. Judging whether the code
  works is explicitly not a reviewer's job -- every verdict returned is a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` -> census every block -> 4 reviewers -> **finding or acquittal, per
block** -> you decide -> someone else applies.
**Census** guarantees every block is SEEN. **Acquittal** guarantees every block is RULED ON with a
named reason. They fail differently: a census with no acquittal list over-reports, because a reviewer
holding a long inventory and no way to say *"this one is fine, and here is the word for why"* flags
label comments and signature docstrings to look thorough -- measured, the widest reporter in one
evaluation returned 12% more findings than the best and hit 4% fewer real ones. **Silence is a gap in
the review; a padded list is a different gap.** Say which you are doing at every block.

## The subject is the prose, not the program

**Every verdict is a verdict on a comment.** Code problems go in a separate section, one line each --
**raise a concern, do not open an investigation** -- and never take a prose verdict. *"The comment
says the function reads one field; it reads three"* is yours; *"it should not read three"* is not.
! Reviewers straying into correctness produce this skill's worst output, measured: twice a reviewer
reported a file "cannot compile" over syntax legal in the target Python. If the claim is about
whether the code *runs* it is not your finding; if you make it anyway you owe it an `ast.parse`.

## Arguments and scope

**`cap`** -- integer, optional; max lines a `#` run may occupy. Pass it to the census and to every
reviewer. **This skill has no cap of its own and must not invent one**; if a guard in the repo
publishes one, that guard owns it -- read how it *measures*, not just its number. With no cap, judge
and **report the longest run found**. **`target`** -- a path, optional; defaults to the changed files.
Scope is **whole files, not the diff**: comment debt is cumulative and mostly pre-existing, and the
diff says which files are in the human's head, not what to read inside them.

## Phase 0 -- census

```bash
B=$(git merge-base origin/HEAD HEAD 2>/dev/null || git merge-base master HEAD 2>/dev/null \
    || git rev-parse HEAD~1 2>/dev/null)
git diff --name-only "$B" HEAD 2>/dev/null; git diff --name-only HEAD 2>/dev/null
```

! Use a **merge-base**, never `A...B` between two branch tips: a tip that has moved reports the
*other* branch's additions as your deletions -- measured once at 933 phantom lines. If every ref
fails, review the paths given and say the scope was manual. Then enumerate -- stdlib only, no project
layout assumed, quiet on a missing path, a missing ref, or a tree with no virtualenv:

```python
# usage: python census.py FILE [FILE...]     -- stdlib only, no project layout assumed
import ast, io, re, sys, tokenize
from pathlib import Path

SIG = {  # a hit is a REASON TO LOOK, never a verdict
    "DATE": r"\b(19|20)\d\d\b",
    "QUOTE": r"[\""][^\"""]{12,}[\""]",
    "CITE": r"[\w/.-]+\.(md|toml|py|json|txt|ya?ml)\b|\bsee `",
    "HIST": r"\b(used to|no longer|previously|formerly|retired|originally|reverted|deprecated"
    r"|before the fix|the old |was (renamed|replaced|moved|deleted|added))\b",
    "REVIEW": r"\b(finding|fix wave|round \d|task \d|phase \d|post-merge|review|part [AB])\b",
    "COVER": r"\b(guard(s|ed|ing)?|pinn?ed|assert(s|ed|ion)?|checked by|covered by|enforced by"
    r"|test_\w+|tests?/|only call site|nothing (asserts|checks))\b",
    "COUNT": r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d[\d,]*)\s+\w*\s*"
    r"(tests?|callers?|places?|rows?|files?|modules?|ids?|sites?|lines?|cases?)\b",
    "RULE": r"\b(never|always|must not|do not|don't|may not|forbidden)\b",
    "SEQ": r"\b(now |then |next |first,|finally|we |I )\b",
    "WHY": r"\b(because|why|the reason)\b",
    "NEG": r"\b(not the|is not|are not|never a|no longer)\b",
    "CROSS": r"\b(callers?|consumed by|shared with|imports?|elsewhere)\b",
}
SKIP = (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT)
pack = lambda c: (c[0][0], c[-1][0], "\n".join(x[1] for x in c))


def runs(src):  # a run is bounded by CODE, not by blank lines
    lines, cur = src.splitlines(), []
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except Exception:
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


def docs(src):  # docstrings by AST, never by regex
    try:
        tree = ast.parse(src)
    except Exception:
        return
    for n in ast.walk(tree):
        b = (
            getattr(n, "body", None)
            if isinstance(
                n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
            )
            else None
        )
        d = b[0] if b and isinstance(b[0], ast.Expr) else None
        if d is not None and isinstance(getattr(d.value, "value", None), str):
            yield (
                d.lineno,
                d.end_lineno or d.lineno,
                d.value.value,
                getattr(n, "name", "MOD"),
            )


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for arg in sys.argv[1:]:
    try:
        src = Path(arg).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"skip {arg}: {e}")
        continue
    out = [(a, b, "#", t, "") for a, b, t in runs(src)]
    out += [(a, b, "DOC", t, nm) for a, b, t, nm in docs(src)]
    print(f"== {arg}: {len(out)} blocks")
    for a, b, kind, text, nm in sorted(out):
        tags = ",".join(k for k, r in SIG.items() if re.search(r, text, re.I))
        print(
            f"  [{a}-{b}] {kind}/{nm} n={b - a + 1} {tags}\n     {' '.join(text.split())[:240]}"
        )
```

Four choices are load-bearing, each bought with a measured miss, so keep them if you reimplement.
**A run is bounded by CODE, not blank lines**, and a docstring is found by AST, not regex. **The
lines are JOINED before matching** -- prose wraps, and a per-line regex cannot see a citation or a
count crossing a line break. When you resolve a name, **the HEAD segment of a dotted name must
resolve**, not any segment, or every `DeadClass.common_method` obituary is invisible. And build any
name index **from source only** -- never a test tree (`assert "foo" not in x` makes a dead `foo` read
as alive), never `.md`/`.txt` (a doc discussing a deleted symbol vouches for it -- measured to
suppress three real obituaries), never a directory holding `pyvenv.cfg`.
! **Every line the census prints is a CANDIDATE, and its count is your denominator.** A run that
labelled its output "facts a reviewer need not re-derive" measured **95-100% false positives** on
dangling paths, and a reviewer acting on it deleted a live coverage citation. Put the word CANDIDATE
in the reviewer's prompt. Equally, an untagged block is not acquitted by being untagged: the tags say
what to read first, never what to flag.

## Phase 1 -- four reviewers, in parallel

Launch **four subagents in one message**, each with the file list, the `cap`, **the census rows for
its files**, and one angle. Reviewers are **READ-ONLY -- say so in the prompt**: four agents editing
one file is a race whose loser's edits vanish, and a reviewer that fixes what it finds has destroyed
the finding -- and name the writable targets and the read-only reference files separately, because a
reviewer handed a contract document as *reference* returned three proposals editing it. Each finding
returns `file`, `line`, the exact claim, **the exact code or test line that settles it**, and
`CONFIRMED` (both sides read) or `SUSPECTED`; 196 of 202 came back CONFIRMED once this was asked for.
**The governing law:** *every false statement found in a real burn-down was one no assertion
touched* -- not the oldest, not the longest, not the furthest from its code. Position predicted
nothing; false clauses sat inside blocks whose other sentences were true. So **look where nothing
asserts**, and overlap between angles is signal, not waste. ! **Read the prose immediately around a
block before reporting it** -- a deliberate design usually says so directly above itself.

### Currency -- does this describe the program as it is now? (~45% of findings)

Git holds what the code used to be; a comment narrating its own history does git's job badly. Flag
dated rulings, review-round labels ("fix round 2", "finding B4", "Part B"), "this used to...", "no
longer", "previously" -- and the sharpest form, **obituaries**: a name, file, test or flag that
exists nowhere. A reader greps, finds nothing, and reads that as *their* mistake.
! **Grep the STEM, not the identifier.** Prose does not obey identifier spelling: a dead `foo_bar` is
written `foo-bar`, `foo bar`, `FooBar`, "the barrer". Measured on a real deletion, the identifier
grep found ten mentions, all correctly dated tombstones, and **missed an eleventh written with a
hyphen -- the only present-tense claim about the dead path in the set**; a clean grep reads as a clean
file. ! A name backticked BECAUSE it does not exist -- a counterfactual, a rejected alternative, a
misspelling shown as an example -- is not an obituary; telling those apart is reading.
**Every number is a citation.** A count is unverifiable unless it names the SET it counts over, and
re-deriving one means re-deriving the set first (measured misses: "the 37 mobility ids" -- 35; "left
all 1626 other tests green" -- 3041). A pass correcting a false number produced a differently false
one by recounting the wrong population, so the verdict is usually **delete the number**.

### Functionality -- does the commentary match what the function is for? (~30%)

Read name, signature and docstring, then the body. Flag a `Returns:` shape the code no longer
returns, a field order reversed, an `Args:` entry for a vanished parameter, a documented exception
nothing raises, a summary saying "Yield" over a function that returns. The **summary line** drifts
silently: changing a return type does not change the sentence describing it. **Prose that DESCRIBES
behaviour is wrong far more often than prose that PROHIBITS** -- a *description* disagreeing with the
code means the comment is wrong, a *prohibition* disagreeing means the code broke the rule.
**Claims about coverage are the class that licenses deletions, and are disproportionately wrong.**
"pinned by X", "guarded by Y", "the only call site", "nothing asserts this" -- each authorises the
next person to delete something, so grep the cited name every time. **The dangerous cell is a
claimed guard that does not exist**: a deletion justified by coverage nobody can find, which reads as
safe for exactly that reason -- one has been dropped on a pointer to a test never written. The
inverse happens too: a comment calling a live value decorative, licensing a deletion five call sites
read. ! A citation your checker cannot parse is worse than one it can parse and reject; the
unparseable one accumulates and its terseness reads as authority. ! **A universal is a checklist** --
*"every X does Y"*: enumerate the Xs. Fold reachability in here: a comment about a caller, an
exemption or a hazard gets the **mechanism** checked, not read.
**Then read the body's comments as one sequence.** Individually each may be true; end to end they are
the most honest description of the function in the file. The tell is grammatical -- **a comment that
sequences instead of constrains** (*"now I need to...", "then we..."*). Each such step is either **(A)**
not needed for the function to be the function or **(B)** real work at the wrong level; say which.
! **Report the mismatch, do not resolve it** -- either the docstring grows until the *name* is wrong
or the function shrinks to what it is called, and naming the fork is the deliverable.

### Locality -- does this comment belong to the line it sits on?

A block points DOWN; a trailing comment points AT its declaration, and `retries: int  # 0 disables
the backoff` is exactly where it belongs. The finding is a comment about something **else**: a rule
at the top of a class constraining two literals 200 lines down, a block whose later half turns back
to narrate what came before, a block annotating **nothing** between two definitions. Second test:
**if this code changed, would the comment become wrong -- and would anyone notice?** Flag navigation
by direction (*"the constant above"*), rotten at the next reorder -- and the inverse, a line carrying
a non-obvious constraint with **no** comment. **Refactoring drift** is this angle's biggest yield.

### Module coherence -- do the comments say this is one module?

Read only the module docstring, section banners and top-of-file commentary. Flag prose announcing two
or three subjects, banners reading like chapter breaks, a docstring enumerating unrelated
responsibilities to stay accurate, a docstring falsified by a function 100 lines down. Flag **the
same rule explained in several modules** -- no function owns it, so each site re-explains the whole; a
long comment above a short expression is usually this, a code-shape finding, comment as evidence.

## Phase 2 -- a verdict, or a named acquittal, for every block

Dedup, then walk the census in line order; every block leaves in exactly one of two states.
**CHECKABLE?** -- could a reader confirm it from the code as it stands, without archaeology?
**NECESSARY?** -- would someone changing this code make a **worse decision** without it?

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- a constraint the reader verifies | **drop** -- it narrates the code |
| **not checkable** | **move** -- real rationale, unverifiable in place | **drop** -- history |

! **Accuracy is not one of the questions, and that is the point.** *"Moved here from `x.validate`
when that module was deleted"* is true, uncheckable and unnecessary, so it goes. History that is
correct reads as earning its place; accuracy is why it was never deleted, not a reason to keep it.
**A fifth verdict: `correct`.** When a block is on-subject and load-bearing but says something false,
the answer is neither drop nor compact -- it is the true sentence, with the evidence that settles it.
A real pass did this **82 times** under a four-verdict vocabulary and had to misfile every one.
**Rule on sentences, not blocks.** ! **A single `keep` sentence launders every sentence around it** --
a block's most defensible sentence is usually why the whole block survived, so ruling `keep` because
*part* of it is load-bearing is the signal to descend a level.

### The acquittal ledger -- a closed list, and nothing else acquits

A block leaves with a finding, or with **one of these words** beside it. If none fits, it is a
finding; do not invent a sixth.

- **`label`** -- a one-line trailing or field comment naming what a value IS (`# Kalman gain`).
- **`states-the-signature`** -- a short docstring saying what the function returns, and no more.
- **`derivation`** -- a hand-worked calculation or worked example: what stops an assertion being an
  echo of the implementation, and the first thing a careless cap deletes. * Over a `#` cap, **move it
  into the DOCSTRING rather than compacting it** -- a `#` run is capped because it interrupts code.
- **`only-guard`** -- a premise guard, or a warning against a plausible wrong move **where nothing
  goes red**. ! Where a test *does* catch the move it is a time-saver, not a guard, and it is
  `compact`. There is no third category of "warnings".
- **`names-its-expiry`** -- it states the condition under which it stops being true. `TODO`/`FIXME`/
  `HACK`/`XXX`/`BUG` are free for the same reason: they point *outward*, at work not done, so they
  never count against a cap and never split a run.

! **An acquittal is not a length exemption in either direction.** A `derivation` still fails if its
numbers no longer hold; a 40-line docstring is not a finding for being 40 lines. And **a docstring
carrying a date, a ruling, a quotation or a rationale paragraph is a finding at ANY length** -- that
is a FORMAT failure, not a length one, and it is exactly where an evicted `#` block relocates.
**A `#` comment is governed by LENGTH** -- it interrupts code, so its cost is the screen space between
the line above and the line below. **A docstring is governed by FORMAT** -- a summary, then
`Args:`/`Returns:`/`Raises:` only where they say something the signature does not; if the repo states
a docstring style, it wins, so read the guard before ruling a docstring long.
* **A description written as a negation is a FORM defect on its own.** You cannot check "X is not
the case" against the code -- establish what it *does* do and argue backwards, then rewrite it
positive; a *prohibition* may stay negative, since no positive form keeps its force. Measured: a
compressing pass took negation from 17% of removed lines to **22% of what it wrote back**.
Four shapes no line counter can see: a **trailing** comment running on into comment-only lines below
it (a FORMATTING finding -- lift the whole thing above the line); a block split by an inserted
statement, where only the half still discussing what came *before* is the finding; **the wrong half
surviving** a shortening -- check what SURVIVED, not what went; and **refactoring drift**.
For **move**, name the destination and **copy the WHOLE block there, including the part that stays in
the code** -- a destination holding only the discarded half reads as a list of dead things. For
**compact**, propose the replacement: prefer *"X must be Y because Z breaks"* over *"this used to be
W."* ! **A block one line over cap is, by construction, mostly correct** -- measured on a burn-down
tail, 27 of the last 48 were over by exactly one. Cut the least-checkable line; **do not rewrite a
block that is already true, current and on-subject.** ! **Changing one copy of a paired value is the
commonest defect a prose pass CREATES**, because a pass edits where it is reading; before proposing a
number or a name, grep it -- the second copy never appears in your diff. ! And **"a clean tree" from a
reviewer who has only read guarded code is not evidence**: defects concentrate where nothing checks.

## Phase 3 -- present. Always.

**This skill never edits.** Report grouped by verdict, most consequential first, replacement text
inline for every `compact` and `correct`, and the ledger line -- *N blocks censused, M findings, K
acquitted, longest run L* -- so a reader tells "clean" from "not looked at". Then stop.
! **Even when the human names the edit** -- "cap them", "fix these", "go do it" -- the deliverable is
the report: *"Report only, per the skill -- say the word and I'll apply the verdicts you accept."* The
review's value is the human's disagreement with it, and **an edit applied is a verdict never ruled
on.** Measured: two runs on near-identical imperative prompts split, one returning a report, one an
846-line diff.

## Rails for the pass that applies these -- you are not that pass

**A block is bounded by CODE, not blank lines**, or a 9-line block becomes 6 + blank + 3. **Build the
`old` string programmatically and require `count == 1`**, or refuse the whole file -- a near-miss must
be a loud refusal, never an edit landing somewhere plausible. **Never change a line of code, a type
annotation, or a string literal**; prove it with an AST diff, docstrings blanked, and run the proof
on the commit you *doubt*. **Extract before you cut** for `move`, and preserve each file's own line
endings. **Re-read the result against these same rules**: a pass that cut seven obituaries wrote
seven new ones, and one defect survived three passes as a severed sentence welded to the line below.

`/simplify` reviews code structure and applies what it finds; `/code-review` hunts correctness bugs.
This one reviews prose and only ever proposes: `/simplify` ends in a diff, this ends in questions.
**Every example above is invented and every measurement anonymised. Keep it that way** -- quoting a
real comment teaches a reviewer to recognise *that comment* instead of the shape, and it rots into a
hygiene skill carrying its own obituary.
