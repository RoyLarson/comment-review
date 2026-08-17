---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across five angles -- currency,
  functionality, duplication, placement, form -- using parallel subagents, and return each finding
  with a proposed verdict (drop / move / compact / correct / keep) for the human to rule on. Use
  this whenever comments or documentation are the subject: after finishing a task that added or
  edited commentary, when a file's comments have drifted from what the code now does, when someone
  says a comment is too long or out of date or "isn't this history", when the same rule seems to be
  explained in several places, when a number or a citation in prose looks stale, when reviewing a
  diff specifically for its prose rather than its logic, before a docs or comment burn-down, or when
  asked whether a module still reads as one module. Trigger on phrasings that never say "comment
  review" -- "these comments are getting out of hand", "does this docstring still match", "is this
  comment still true", "didn't we say this somewhere else", "clean up the narration in this file",
  "why does this file need so much explaining" all mean run this. It is NOT /simplify (which reviews
  code structure and applies its fixes) and NOT /code-review (which hunts correctness bugs) -- this
  one ONLY EVER PROPOSES and never edits anything, not code and not even the comments it rules on,
  because an edit applied is a verdict the human never got to rule on. Run it even when the request
  sounds like an instruction to cut ("cap these", "clean this up"): the deliverable is still the
  verdict list, and applying is a separate step. It is explicitly not a reviewer's job to judge
  whether the code works: code concerns get raised in a line and left, while every verdict returned
  is a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` -> sweep -> 5 reviewers in parallel -> a verdict each -> you decide.

## The subject is the prose, not the program

Every verdict you return is a verdict on a comment. You will still notice code problems -- say so in
one line, in a separate section, and move on: **raise a concern, do not open an investigation**, and
never give a code finding a prose verdict. *The comment says the function reads one field and it
reads three* is yours; *it should not read three* is not. *The comment names a symbol that no longer
exists* is yours; *restore the symbol* is not. *The same rule is restated at a dozen sites* is
yours; *the rule needs an owning type* is not.

! **A reviewer straying into correctness is this skill's worst output, measured.** Twice, reviewers
read a valid `except A, B:` and reported the file "cannot compile" -- wrong, and volunteered while
reviewing prose; once four agreeing reviewers shipped it. If the claim is about whether the code
*runs*, it is not your finding; if you make it anyway you owe it an `ast.parse` first.

## Phase 0 -- Scope, then sweep

`cap` is the most lines one `#` run may take, and `target` defaults to the files in the diff.
! **This skill has no cap of its own and must not invent one:** if the repo publishes one in a
guard or a lint config, use that, say where you got it, and read how it *measures*; otherwise judge
by eye and **report the longest block found**. Scope is a **file list**, not a line range:

```bash
B=$(git merge-base HEAD "${1:-origin/HEAD}" 2>/dev/null) && git diff --name-only "$B"...HEAD
git diff --name-only HEAD          # add this whenever the tree is dirty
```

! **Use the merge-base, never two bare endpoints** -- a two-endpoint diff presents the other
branch's work as yours. If both come back empty, ask; do not fall back to `HEAD~1`, which silently
reviews one commit of a many-commit branch and under-reports with no error. Then review **every
comment and docstring in those files**, not just the changed lines: comment debt is cumulative and
mostly pre-existing, and editing one block routinely breaks an untouched one -- a compacted
docstring orphans the block elsewhere saying "see its docstring". Skip generated code and data
tables; say which. Run the sweep below over the list and paste its report into **every** reviewer
prompt. ! **Nothing it prints is a verdict**: `path` and `dup` are candidates a reviewer must
confirm, and measured precision on an already-clean tree can be zero. It deliberately does **not**
hunt dead symbol names -- a name corpus harvested from a tree suppressed 4 of 7 known-dead symbols,
because a negative assertion elsewhere mentions the name it refutes. Currency does that by hand.

```python
"""Comment-review pre-pass: a block inventory with candidate flags. Assumes no framework."""

import ast, io, pathlib, re, sys, tokenize  # noqa: E401

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
CITE = re.compile(r"[\w./-]+\.(?:py|md|txt|toml|json|ya?ml|cfg|ini|rst)\b")
SKIP = {".git", ".venv", "venv", "node_modules", "site-packages", "__pycache__"}
STOP = set(
    "the and for with this that from have been args returns raises todo fixme hack".split()
)
DEF = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
FLAG = {
    "hist": r"used to|no longer|formerly|previously|renamed|retired|deleted|moved to|superseded",
    "cover": r"guard|pinned|assert|covered|enforce|checked by|proven|refuses|call site|no caller",
    "count": r"(?<![\w.])\d|\b(one|two|three|four|five|ten|only|every|all|both|each|exactly)\b",
    "date": r"\b(19|20)\d\d([-/]\d\d?){0,2}\b",
    "neg": r"\b(not|never|cannot|nothing|none|neither|must not|does not)\b",
    "quote": r"[""]|\bsaid\b|\bruled\b|\bdecided\b",
}


def blocks(path):
    """(start, kind, text) per `#` run -- a blank line does NOT split one -- and per docstring."""
    runs, cur, prev = [], [], None
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except OSError, tokenize.TokenError, IndentationError, SyntaxError, ValueError:
        return []
    for t in toks:
        if t.type != tokenize.COMMENT:
            continue
        cur.append(t) if prev is not None and t.start[0] - prev == 1 else runs.append(
            cur := [t]
        )
        prev = t.start[0]
    out = [(r[0].start[0], "run", "\n".join(t.string for t in r)) for r in runs]
    try:
        tree = ast.parse(src)
    except SyntaxError, ValueError:
        return sorted(out)
    for n in ast.walk(tree):
        if isinstance(n, DEF) and (d := ast.get_docstring(n, clean=False)) is not None:
            out.append((n.body[0].lineno, "doc", d))
    return sorted(out)


def trigrams(text):
    w = [x.lower() for x in WORD.findall(text) if len(x) > 3 and x.lower() not in STOP]
    return {tuple(w[i : i + 3]) for i in range(max(0, len(w) - 2))}


known = {p.name for p in ROOT.rglob("*") if p.is_file() and not SKIP & set(p.parts)}
rows = []
for arg in sys.argv[2:]:
    for line, kind, text in blocks(ROOT / arg):
        flags = [f"{kind}{text.count(chr(10)) + 1}"]
        flags += [f"w{max((len(x) for x in text.splitlines()), default=0)}"]
        flags += [k for k, rx in FLAG.items() if re.search(rx, text, re.I)]
        dead = sorted(
            {q for q in CITE.findall(text) if pathlib.Path(q).name not in known}
        )
        flags += [f"path:{','.join(dead[:3])}"] if dead else []
        rows.append([f"{arg}:{line}", flags, trigrams(text)])
for i, r in enumerate(rows):  # the same claim in two places, where one copy drifts
    for s in rows[i + 1 :]:
        both = r[2] & s[2]
        if len(both) >= 3 and len(both) / min(len(r[2]), len(s[2])) >= 0.34:
            r[1].append(f"dup~{s[0]}")
            s[1].append(f"dup~{r[0]}")
for r in rows:
    print(r[0], " ".join(r[1]))
print(f"# {len(rows)} blocks", file=sys.stderr)
```

## Phase 1 -- Five reviewers, in parallel

Launch them **in a single message**, each with the file list, the sweep report, the `cap`, and one
angle. ! **Reviewers are READ-ONLY -- say so in the prompt.** Four agents editing one file is a race
whose loser's edits vanish, and a reviewer that fixes what it finds has destroyed the finding. Name
two lists: files **under review** (a proposal may target these) and files given as **reference**
(never a target). Overlap between angles is signal, not waste. Each finding returns `file:line`,
the claim, the code or test line that settles it, and `CONFIRMED` or `SUSPECTED` -- did you read
both sides.

### Currency -- does this describe the program as it is now? (~45% of yield)

Dated rulings, review-round labels, "this used to...", "X was changed to Y" -- and the sharpest form,
**obituaries**: prose naming a symbol, file, test, flag or config key that no longer exists, so the
reader greps for it, finds nothing, and reads that as *their* mistake.

- **Grep the STEM, not the identifier**, because prose does not obey identifier spelling: a dead
  `foo_bar` appears as `foo-bar`, `FooBar`, or "the barrer". Measured on a real deletion, the
  identifier grep found ten mentions -- all correctly dated tombstones -- and missed an eleventh
  written with a hyphen, the only present-tense claim about the dead path in the set. A clean grep
  reads as a clean file, so the failure is self-concealing. A bare lowercase word is a symbol too.
- **A citation asserts something about its target; resolving the target is not verifying the
  assertion.** Read the cited test, or file it `SUSPECTED`. A real guard has been deleted on a
  pointer to a test that was never written -- and a pass once repaired a citation's path while
  leaving the false claim under it, destroying the only visible symptom. A moved path can change
  MEANING too: a `TODO` now filed under `completed/` is evidence for something it says is finished.

### Functionality -- does the commentary match what the code does? (~30% of yield)

Read the name, the signature, the docstring, then the body; for every `Args:` / `Returns:` /
`Raises:` entry read the few lines that produce it. Nearly every inversion found here was refutable
inside the same function -- a `Returns: {a: b}` over a body writing `{b: a}`, a scope word quietly
widened, a hedge promoted to `always`.

- **Coverage and absence claims license deletions and are disproportionately wrong.** "pinned by
  X", "exactly one call site", "nothing reads this". Resolve every one; count the real call sites,
  including string-literal and dict-key readers no call graph shows. An absence claim is the
  cheapest to falsify and the most authoritative-looking -- grep it however deliberate it reads.
- **A counted claim must name its POPULATION and the query that regenerates it**, so re-derive the
  set before the number. Counts also come with no digit -- "the one consumer", "the only entry
  point", "both callers" -- so treat every definite-singular as a count. A number no assertion reads
  will rot again: if it is not load-bearing that is a `drop`, not a correction.
- **Read a body's `#` comments as one sequence.** Individually each may be true; end to end they are
  the most honest description of the function in the file. The tell is grammatical: a comment that
  **sequences** ("now I need to...", "then we...") instead of **constrains** narrates the author's path
  and goes nowhere when its line moves. Report the mismatch -- *the running commentary describes five
  jobs, the name describes one* -- and name the fork: a truer docstring, at which point the NAME is
  wrong, or a smaller function. Choosing between them is a design change.
- ! **Authoring is not reviewing.** A docstring newly written on a definition that had none is a
  claim with no predecessor, so nothing compares it to anything; 2 of 28 such were false on arrival.

### Duplication -- is this claim stated anywhere else, and do the copies still agree?

**The highest-yield angle nobody was running**, and it is *one definition per rule* applied to
prose. A pass edits where it is reading, so it fixes the copy in front of it and manufactures a
disagreement with the copy it never opened -- and every within-file angle passes both halves, since
the edited copy is now correct and the stale copy has no diff, so nothing opens it. For every claim
you would otherwise pass, **grep the repo for its SUBJECT -- the number, the symbol, the path, the
distinctive phrase -- before ruling**; one `git grep 1705` costs a second.

| shape | what to report |
|---|---|
| two copies, one edited | the STALE one, and that the pass opened the gap |
| a rule re-explained at N sites | no function owns it; each site restates the whole |
| a justification copied across a file | true where it came from; re-derive it here, or drop it |
| code and its extracted mirror disagree | the body settles it, not the majority copy |

**A relocation is a duplication until the source is gone**, which makes an extracted mirror doc the
cheapest baseline available. ! And **a claim moved out of the code is unguarded where it lands**:
prose instructing a CALLER stops working once only a document nobody opens holds it.

### Placement -- does this prose sit where the thing it constrains sits?

Two zooms, one angle; report both, and do not let the coarse zoom crowd out the fine one.
**At the line**, a comment points DOWN for a block on its own lines and AT the declaration for a
trailing one, so a field comment after a statement is exactly where it belongs. The finding is a
comment about something **else**: a rule atop a class that really constrains two literals 200 lines
down, a demonstrative resolving 40 lines away, a block stranded after an unconditional `return`, a
trailing comment severed mid-clause by the `#` lines under it (its sentence ends on a comma or an
open paren and the next line's subject is a different declaration). Second test: **if this code
changed, would the comment become wrong -- and would anyone notice?** Prose that would quietly
survive a change to the code it describes is not local to it, and a line carrying a non-obvious
constraint with no comment at all is a placement finding too. **At the module**, read only the
module docstring, the banners and the top-of-file prose: do they describe one thing, and does
anything 25 lines below contradict them? A docstring that must enumerate unrelated
responsibilities to be accurate is describing two modules.

### Form -- is the sentence checkable at all?

**A DESCRIPTION must be positive**: "! NOT the kernel call site" cannot be checked, because the
reader must establish what the code *does* do and argue backwards -- restate it as what is true.
**A PROHIBITION may be negative** -- "never call this here, or the expectation moves with the code"
has no positive form that keeps its force, so keep it. That splits the disagreement cell, which
from outside looks identical either way: a **description** contradicting the code is wrong -> drop
or correct it; a **prohibition** contradicting the code is right and **the code broke the rule** ->
file it, and the code moves. And a block that compaction left asserting nothing -- a "ONE definition"
claim naming one of its pair, a sentence welded to a stray fragment -- is a finding though every word
in it is true.

## Phase 2 -- One verdict per finding

Dedup findings on the same block, then ask three questions of each survivor. **On subject?** -- local
to the code beside it, and about the program as it is now. **True?** -- of the code, resolved.
**Checkable?** -- could a reader confirm it from the tree as it stands, without archaeology?

| | **checkable** | **not checkable** |
|---|---|---|
| **on subject, true** | **keep** -- a verifiable constraint | **move** -- rationale, unverifiable here |
| **stale or false** | **correct** if load-bearing, else **drop** | **drop** -- history |

! **Accurate history reads as earning its place, and does not.** "Moved here from `x.validate` when
that module was deleted" is true; the reader needs to know the check lives HERE, not where it used
to. Accuracy is why it was never deleted, not a reason to keep it. **Rule on sentences, not on
blocks** -- a container of six sentences holds six verdicts, and the common shape is a live
constraint beside the story of where it came from. ! **A single `keep` sentence launders every
sentence around it**: ruling `keep` because *part* of a block is load-bearing is the signal to
descend a level, and since a block's most defensible sentence is usually why the whole block
survived this long, that is the default outcome, not a rare one.

Then ask whether what survives is longer than it needs to be -- **compact** is what you do to a
`keep`, not a fifth verdict. For **move**, name the destination; ! **it gets the WHOLE block,
including the part that stays in the code**, or the document holds only what nobody kept and reads
as a list of discarded things. For **correct**, give the replacement and the evidence: a correction
with no re-derived population is how one wrong number becomes a differently wrong one. Do not pad
the list -- **keep** is a real verdict. ! **A block one line over cap is, by construction, mostly
right**: on one burn-down tail 27 of 48 remaining runs were exactly one over, so cut the least
checkable line rather than re-authoring a block that is already true, current and on subject.

**A `#` comment is governed by LENGTH** -- it interrupts code, so its cost is screen space -- while
**a docstring is governed by FORMAT**, so do not propose `compact` on one merely for being long.
! A repo's own docstring rule beats that sentence, and a `#` block relocated into a docstring to
duck a line cap is the same prose somewhere nothing measures; watch for that migration by name. The
docstring check worth running every time is the **summary line**: the only part most readers see,
drifting silently because changing a return type does not change the sentence describing it.
**`TODO`, `FIXME`, `HACK`, `XXX`, `BUG` are free** and never counted against a cap -- each points at
work not done, and a cap that counts them makes deleting the pointer the cheapest way to green.

## Phase 3 -- Present. Always.

**This skill never edits. It ends with the verdict list**, grouped by verdict, most consequential
first, with the replacement text inline for every `compact` and `correct`. Then stop. ! **Even
when the human names the edit** -- "cap them", "fix these", "go do it" -- the deliverable is still
the report: *"Report only, per the skill -- say the word and I'll apply the verdicts you accept."*
This review's whole value is the human's disagreement with it, and **an edit applied is a verdict
never ruled on**. Measured before this rule: two runs on near-identical imperative prompts split,
one returning a report and one an 846-line diff.

Hand these rails to the pass that applies the verdicts -- you are not it, and each cost something on
a real 43-file run. **A block is bounded by CODE, not blank lines**, else a 9-line block becomes
6 + blank + 3. **Never change a line of code, a docstring's meaning, or a string literal** -- prove
it by comparing every non-comment line against the pre-edit file, which caught two cuts that took
real code. **Apply with `count == 1` or refuse the whole file**, with the proposer extracting the
old text programmatically rather than transcribing it. **Extract before you cut** on a `move`; the
other order lost the text three times. And **re-read the whole enclosing block, not the edited
line** -- a pass that cut seven obituaries wrote seven new ones, the same one twice in one file.

`/simplify` reviews code structure and applies what it finds; `/code-review` hunts correctness bugs.
This one reviews prose and **only ever proposes**: `/simplify` ends in a diff, this ends in a list
of questions. **And every example above is invented -- keep it that way.** Quoting a real comment
teaches a reviewer to recognise *that comment* instead of the shape, and it rots: the day someone
acts on the finding, this file cites a comment that no longer exists, a hygiene skill carrying its
own obituary. Measurements are worth keeping and cost nothing to anonymise.
