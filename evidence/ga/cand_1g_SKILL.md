---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles --
  locality, currency, functionality, module coherence -- and return each finding with a proposed
  verdict (drop / move / compact / keep) for the human to rule on. Use this whenever comments or
  documentation are the subject: after finishing a task that added or edited commentary, when a
  file's comments have drifted from what the code now does, when someone says a comment is too
  long or out of date or "isn't this history", when reviewing a diff specifically for its prose
  rather than its logic, before a docs or comment burn-down, or when asked to check whether a
  module still reads as one module. Trigger on phrasings that never say "comment review" --
  "these comments are getting out of hand", "does this docstring still match", "is this comment
  still true", "clean up the narration in this file", "why does this file need so much
  explaining" all mean run this. It is NOT /simplify (which reviews code structure and applies
  its fixes) and NOT /code-review (which hunts correctness bugs) -- this one ONLY EVER PROPOSES
  and never edits anything, not code and not even the comments it rules on, because an edit
  applied is a verdict the human never got to rule on. Run it even when the request sounds like
  an instruction to cut ("cap these", "clean this up"): the deliverable is still the verdict
  list, and applying is a separate step. It is explicitly not a reviewer's job to judge whether
  the code works: code concerns get raised in a line and left, while every verdict returned is
  a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` -> census every prose block -> verdict each -> you decide -> apply.

**This skill never edits.** Not code, not the comments it rules on, not even when told to
("cap these", "just fix it"). Reply: *"Report only, per the skill -- say the word and I'll
apply the verdicts you accept."* An edit applied is a verdict the human never got to rule on.

**The subject is the prose, not the program.** You will notice code problems; list them in one
line each in a separate section and move on. Never give a code concern a prose verdict.

| a COMMENT finding | a CODE finding -- name it and leave it |
|---|---|
| the comment says it reads one field; it reads three | it should not read three fields |
| the comment names a symbol that no longer exists | the symbol should be restored |
| the comment claims callers `grep` cannot find | the function is dead, delete it |

## Phase 0 -- Census every block. This is the whole method.

Sampling is how a review returns nine findings from a file with ninety blocks. **Enumerate
every docstring and every comment run in the target files, then rule on each one.** A block
absent from your report is a claim that you read it and kept it.

Scope is **whole files, not the diff** -- `git diff --name-only @{upstream}...HEAD`, or
`main...HEAD`, or `HEAD~1`, or the path the human named; if every range is empty add
`git diff --name-only HEAD`, and if git says nothing, ask. Comment debt is cumulative and
pre-existing; the diff says which files are live in their head, not what to read inside them.

Run this to get the census. Stdlib only, no config, no repo assumptions:

```python
# census.py <cap> <file>...  -> "path:line kind nlines tags"
import ast, re, sys

TAGS = [
    ("date", r"\b(19|20)\d\d[-/]\d\d[-/]\d\d\b"),
    ("attributed", r"[\""][^\""]{12,}[\""]|\b(said|ruled|ruling|per )\b"),
    (
        "history",
        r"\b(used to|no longer|until|previously|formerly|retired|renamed|"
        r"was changed|before the fix|deleted|moved (from|out|here)|since)\b",
    ),
    (
        "review",
        r"\b([Rr]ound[- ]?\d|finding \w+|review|fix wave|phase \d|task[- ]\d)\b",
    ),
    ("cites", r"[\w./-]+\.(py|md|toml|json|ya?ml|txt)\b|\btest_\w+"),
    ("counts", r"\b\d+ of \d+\b|\b\d{3,}\b|\b\d+(\.\d+)?%"),
    (
        "coverage",
        r"\b(guard(s|ed)?|pinned|asserted|enforced|checked by|covered by|verified)\b",
    ),
]


def census(path, cap):
    try:
        src = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        print(f"{path}: unreadable, skipped", file=sys.stderr)
        return []
    lines, out = src.splitlines(), []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        tree = None
    for n in ast.walk(tree) if tree else []:
        body = getattr(n, "body", None)
        holder = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        if not isinstance(n, holder) or not body:
            continue
        e = body[0]
        v = getattr(e, "value", None) if isinstance(e, ast.Expr) else None
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            out.append([e.lineno, "docstring", e.end_lineno - e.lineno + 1])
    run = None
    for i, ln in enumerate(lines, 1):  # a run is bounded by CODE, not by blank lines
        s = ln.strip()
        if s.startswith("#"):
            run = run or [i, i]
            run[1] = i
        elif s:
            if run:
                out.append([run[0], "comment", run[1] - run[0] + 1])
            run = None
    if run:
        out.append([run[0], "comment", run[1] - run[0] + 1])
    for start, kind, n in sorted(out):
        text = "\n".join(lines[start - 1 : start - 1 + n])
        tags = [t for t, p in TAGS if re.search(p, text)]
        if kind == "comment" and cap and n > cap:
            tags.append("over-cap")
        prev = lines[start - 2] if start > 1 else ""
        if kind == "comment" and "#" in prev and prev.split("#")[0].strip():
            tags.append("continues-a-trailing-comment")
        print(f"{path}:{start} {kind} {n} {','.join(tags) or '-'}")
    return out


cap = int(sys.argv[1]) if sys.argv[1:] and sys.argv[1].isdigit() else 0
for p in sys.argv[2 if cap else 1 :]:
    census(p, cap)
```

**Every tag is a defect on sight in code prose**, and together they are most of the yield:

- `date` / `review` / `attributed` -- a date, a review-round label, or a quoted ruling is the
  changelog living in the source. Git holds it better. Almost always **drop** or **move**.
- `history` -- "used to", "no longer", "until X": present-tense the rule and lose the past.
- `cites` -- **resolve every one.** A path, a module, a test name, a backticked symbol. A dead
  citation sends the next reader to grep for nothing, and reads as *their* mistake.
- `coverage` -- "guarded by", "asserted in", "pinned by". This class **licenses deletions**, so
  it is checked, never read: a real guard has been deleted on a pointer to a test never written.
- `counts` -- "4 modules import it", "1665 of 1665", "10.4%". Re-derive it or delete the number.
- `over-cap` / `continues-a-trailing-comment` -- shape findings a reader feels and a linter can't.

Where the repo publishes its own cap (a lint config, a hygiene test), **use it and say where
you got it**; read how it *measures*, not just its number. Otherwise review by judgement and
report the longest block found -- visible without having been asserted.

! **A clean tag line is not a pass.** The tags find the mechanical half. The other half --
prose that describes behaviour the code no longer has -- needs the four angles below, and is the
half that is wrong most often. Prose that *prohibits* something ages far better than prose that
*describes* something; weight your reading accordingly.

## Phase 1 -- Four angles over the census

Run them as four parallel read-only subagents if the census is large; otherwise yourself, one
angle at a time over the whole list. Tell subagents explicitly: **read, grep, report; never
edit.** Overlap between angles is signal, not waste.

**Locality -- is this a claim about the line it sits on?** A rule stated atop a class that really
constrains two literals 200 lines down; a block whose later half turns back to narrate what came
before. Test: *if this code changed, would the comment become wrong -- and would anyone notice?*
A trailing field comment (`retries: int  # 0 disables backoff`) is exactly where it belongs.
Absence counts too: a non-obvious constraint with no comment, where getting it wrong is silent.

**Currency -- does this describe the program as it is now?** The largest class, and the most
mechanical. Obituaries -- a symbol, file, test or flag named in prose that exists nowhere -- lead
it. ! **Grep the STEM, not the identifier**: prose writes a dead `foo_bar` as `foo-bar`,
`FooBar`, or "the barrer". An identifier grep returns clean and you report the file clean --
the failure is self-concealing. Measured once: ten tombstones found, the eleventh missed, and
the missed one was the only present-tense claim about the dead path in the set.

**Functionality -- does the commentary match what the function is for?** Name, signature,
docstring, then body. Flag a documented return shape the code no longer returns, an `Args:`
entry for a vanished parameter, a raised exception nothing raises, a summary line that
summarises the first four lines only. Then read the body's comments **as one sequence**: end to
end they are the most honest description of the function in the file. When they narrate five
jobs and the name promises one, report the mismatch -- *the docstring grows until the name is
wrong, or the function shrinks to its name* -- and let the owner choose. The tell is
grammatical: a comment that **sequences** ("now I need to...", "then we...") instead of
**constrains** ("read before attribution: the parse must arrive first") is a to-do list left in
the body. Watch for narration of *intent* -- it reads as confirmation, so the eye stops there.

**Module coherence -- do the docstring and banners say this is one module?** Read only the top of
file and the section banners. Flag prose that has to enumerate unrelated responsibilities to be
accurate, and banners that read like chapters of a book rather than parts of one argument. Also
flag one rule re-explained in several modules: that means no function owns it, which is *why*
the comments got long. Report it as a code-shape finding with the comment as evidence.

## Phase 2 -- One verdict per block, ruled on sentences

Dedup, then ask two questions in order. **Checkable?** -- could a reader confirm or refute it
from the code as it stands, without archaeology. **Necessary?** -- would someone changing this
code make a *worse decision* without it. Not "is it true", not "is it interesting".

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** -- verifiable, and needed | **drop** -- the code already says it |
| **not checkable** | **move** -- real rationale, unverifiable in place | **drop** -- history |

! **Truth is not one of the questions.** *"Moved here from `x.validate` when that module was
deleted"* is accurate, uncheckable, and changes nobody's decision -- so it goes. Accuracy is why
history was never deleted, not a reason to keep it.

**Rule on sentences, not blocks.** A live constraint sitting beside the story of where it came
from is the ordinary case, and a single `keep` sentence launders every sentence around it -- if
you are keeping a block because *part* of it is load-bearing, descend a level.

**compact** is what you do to a survivor, not a fifth verdict. For **move**, name the
destination -- a per-module doc tree, a decision log, an architecture doc; staging somewhere
provisional beats deciding a final home under time pressure. For **compact**, propose the
replacement text and keep the constraint plus what breaks without it.

! **A docstring is governed by FORMAT, not length** -- long is not itself a finding. A `#`
comment is governed by length, because it interrupts code. Both are fully in scope.

Do not pad. **keep** is a real verdict; a review returning mostly `keep` is a good outcome.

## Phase 3 -- Present. Always.

Report grouped by verdict, most consequential first, replacement text inline for every
`compact`, then a one-line-each section of code concerns, then stop. Include the census totals:
blocks read, blocks with a verdict, longest block found. Then hand the applying pass these:

- **Never change a line of code, a docstring's meaning, or a string literal.** Prove it -- diff
  every non-comment line against the pre-edit file and confirm zero differences.
- **Extract before you cut** on a `move`: write the destination verbatim first, and copy the
  whole block including the half that stays, or the doc reads as a list of discarded things.
- **Re-read what you wrote.** A pass that cut seven obituaries wrote seven new ones. Check your
  own replacements against the cap and the currency rule before reporting done.

## For whoever edits this file

**Every example here is invented. Keep it that way.** A real comment quoted here teaches the
shape of *that comment*, and rots the day someone acts on the finding -- a hygiene skill
carrying its own obituary. Anonymised measurements carry the lesson at no such cost.
