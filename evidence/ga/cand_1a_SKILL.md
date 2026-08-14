---
name: comment-review
description: >-
  Review the comments and docstrings in the files a change touched, across four angles —
  locality, currency, functionality, module coherence — using four parallel subagents, and
  return each finding with a proposed verdict (drop / move / compact / correct / keep) for the
  human to rule on. Use this whenever comments or documentation are the subject: after finishing
  a task that added or edited commentary, when a file's comments have drifted from what the code
  now does, when someone says a comment is too long or out of date or "isn't this history", when
  reviewing a diff specifically for its prose rather than its logic, before a docs or comment
  burn-down, or when asked to check whether a module still reads as one module. Trigger on
  phrasings that never say "comment review" — "these comments are getting out of hand", "does
  this docstring still match", "is this comment still true", "clean up the narration in this
  file", "why does this file need so much explaining" all mean run this. It is NOT /simplify
  (which reviews code structure and applies its fixes) and NOT /code-review (which hunts
  correctness bugs) — this one ONLY EVER PROPOSES and never edits anything, not code and not
  even the comments it rules on, because an edit applied is a verdict the human never got to
  rule on. Run it even when the request sounds like an instruction to cut ("cap these", "clean
  this up"): the deliverable is still the verdict list, and applying is a separate step. It is
  explicitly not a reviewer's job to judge whether the code works: code concerns get raised in a
  line and left, while every verdict returned is a verdict on a comment.
---

# comment-review

`/comment-review [cap] [target]` → enumerate every block → flag mechanically → 4 reviewers →
a verdict per block → you decide → someone else applies.

## The subject is the prose, not the program

**Every verdict is a verdict on a comment.** Say code problems in one line each, in a separate
section — **raise a concern, do not open an investigation**, and never give a code finding a prose
verdict. *"The comment names a symbol that no longer exists"* is yours; *"the symbol should be
restored"* is not. *"It claims callers `grep` cannot find"* is yours; *"the function is dead,
delete it"* is not.

⚠ Reviewers straying into correctness produce this skill's worst output, measured: twice a
reviewer reported a file "cannot compile" over syntax legal in the target Python. If the claim is
about whether the code *runs* it is not your finding, and if you make it anyway you owe it an
`ast.parse` first.

## Arguments

- **`cap`** — integer, optional; max lines a `#` run may occupy. Pass it to every reviewer. **This
  skill has no cap of its own.** If a guard in the repo publishes one, that guard owns it — read
  how it *measures*, not just its number. With no cap, judge, and **report the longest run found**.
- **`target`** — a path, optional. Defaults to the changed files.

## Phase 0 — Enumerate every block, then flag it

Scope is **whole files, not the diff**. Comment debt is cumulative and mostly pre-existing; the
diff says which files are in the human's head, not what to read inside them.

```bash
B=$(git merge-base origin/HEAD HEAD 2>/dev/null || git merge-base master HEAD 2>/dev/null \
    || git rev-parse HEAD~1 2>/dev/null)
git diff --name-only "$B" HEAD 2>/dev/null; git diff --name-only HEAD 2>/dev/null
```

⚠ Use a **merge-base**, never `A...B` between two branch tips: a tip that has moved reports the
*other* branch's additions as your deletions — measured once at 933 phantom lines. If every ref
fails, review the paths given and say the scope was manual. Then run the scanner: generic, no
project layout, quiet on a missing path, a missing ref, or a tree with no virtualenv.

```bash
python .claude/skills/comment-review/prose_scan.py $FILES --root . --cap "$CAP"
```

`prose_scan.py` ships beside this file. For **every** prose block it prints `file`, `line`,
`lines`, `kind` (comment | docstring) and `flags`, where a flag is one of: `over-cap`,
`dead-name?`, `dead-path?`, `count`, `history`, `date`, `coverage-claim`, `sequencing`,
`phantom-arg`, `summary-verb`. Four of its choices are load-bearing, each bought with a measured
miss — keep them if you reimplement it:

- **a block is bounded by CODE, not blank lines**, and a docstring is found by AST, not by regex;
- **the lines are JOINED before matching**, because prose wraps and a per-line regex cannot see a
  citation or a count that crosses a line break;
- **the HEAD segment of a dotted name must resolve** — allowing any segment makes every
  `DeadClass.common_method` obituary invisible, and `` `f()` `` must match as well as `` `f` ``;
- **the name index is built from source only**, never a test tree or a virtualenv (trap 3), and
  the count pattern allows adjectives between the number and its noun (*"four passing tests"*).

### Reading Phase 0 — six traps, all measured

1. **Every line is a CANDIDATE.** A run that labelled its output "facts a reviewer need not
   re-derive" measured **95–100% false positives** on dangling paths, and a reviewer acting on it
   *deleted a live coverage citation*. Put the word CANDIDATE in the reviewer's prompt.
2. **Resolving a citation is not verifying it** — and repairing a path removes the only visible
   tell of a block that the file it names flatly denies. **Read the target, or mark it SUSPECTED.**
3. **The name index must exclude tests and any virtualenv.** `assert "foo" not in x` makes `foo`
   resolve: the strongest evidence a name is dead is what marks it alive.
4. **Grep the stem, not the identifier.** Prose writes `foo_bar` as `foo-bar`, `foo bar`, `FooBar`,
   "the barrer". An identifier grep once found ten dated tombstones and missed the hyphenated
   eleventh — the only present-tense claim in the set. A clean grep reads as a clean file.
5. **A name backticked BECAUSE it does not exist is not an obituary** — a counterfactual, a
   misspelling shown as an example, a rejected alternative. Telling those apart is reading.
6. **Over-report; never tune for precision.** A false positive costs one glance, a structural false
   negative costs the class. Order the report by how dirty each file is: a reviewer who sees three
   false hits in a row stops reading the section.

## Phase 1 — Four reviewers, in parallel

Launch **four subagents in one message**, each with the file list, the `cap`, the **Phase 0
inventory for its files**, and one angle. Reviewers are **READ-ONLY — say so in the prompt**: four
agents editing one file is a race whose loser's edits vanish, and a reviewer that fixes what it
finds has destroyed the finding.

**Every block in the inventory gets an answer, flagged or not.** The governing law, measured:
*every false statement found was one no assertion touched* — not the oldest, not the longest, not
the furthest from its code. Position predicts nothing, so a pass that visits only flagged blocks
inherits the flags' blind spots. Overlap between angles is signal, not waste.

### Locality — does this comment belong to the line it sits on?

A block points DOWN; a trailing comment points AT its declaration, and `retries: int  # 0 disables
the backoff` is exactly where it belongs. The finding is a comment about something **else**: a rule
at the top of a class that constrains two literals 200 lines down; a block whose later half turns
back to narrate what came before; a block annotating **nothing**, between two definitions. Second
test: **if this code changed, would the comment become wrong — and would anyone notice?**

⚠ Flag navigation by direction (*"the constant above"*, *"the rule below"*): true today, rotten at
the next reorder — name the symbol instead. Flag the inverse too: a line carrying a non-obvious
constraint with **no** comment, where getting it wrong is silent.

### Currency — does this describe the program as it is now?

Flag dated rulings, review-round labels (*"finding 6"*, *"fix round 2"*), *"this used to…"*, and —
sharpest — **obituaries**: a name, file, test or flag that no longer exists. A reader greps, finds
nothing, and reads that as *their* mistake. **A comment claiming a MECHANISM — an exemption, a
hazard, a caller, a guard — gets the mechanism checked, not read.** That is where deletions are
licensed. Two forms the scanner cannot settle:

- a **number** with no named population and no way to regenerate it. A count in prose that no
  assertion reads will rot again, so the verdict is usually **delete the number**, not update it.
- a **retraction whose antecedent is gone** — *"the fact is unchanged, only where it lives"* with
  no *where it used to live* left anywhere in the file.

### Functionality — does the commentary match what the function is for?

Read name, signature, docstring, then body. Flag a `Returns:` shape the code no longer returns, a
field order reversed, an `Args:` entry for a vanished parameter, a documented exception nothing
raises, a summary describing only the first four lines.

Then **read the body's comments as one sequence and ask what they describe.** Individually each may
be true; end to end they are the most honest description of the function in the file. The tell is
grammatical — **a comment that sequences instead of constrains** (*"now I need to…", "then we…"*).
One earning its place says why a line must be as it is and goes visibly wrong if the line moves.
Each such step is either **(A)** not needed for the function to be the function or **(B)** real work
at the wrong level; say which. ⚠ **Report the mismatch, do not resolve it** — *"the commentary
describes five jobs, the name describes one"* resolves either by growing the docstring until the
**name** is the wrong thing, or by shrinking the function. Naming the fork *is* the deliverable.

⚠ **A universal is a checklist.** *"Every X does Y"*, *"failures are never swallowed"* — enumerate
the Xs. A partial universal passes every other angle, and on an ingestion path it is a false safety
guarantee. ⚠ **Prose that DESCRIBES behaviour is wrong far more often than prose that PROHIBITS**,
and the two take different verdicts: a *description* that disagrees with the code means the comment
is wrong; a *prohibition* that disagrees means the code broke the rule — a code finding.

### Module coherence — do the comments say this is one module?

Read only the module docstring, section banners and top-of-file commentary. Flag prose announcing
two or three subjects, banners that read like chapter breaks, and a docstring falsified by a
function 100 lines down. Flag the same rule explained in several modules: no function owns it, so
each site re-explains the whole. Structural, and worth naming even though the fix is not prose.

## Phase 2 — One verdict per block

Dedup, then ask two questions. **CHECKABLE?** — could a reader confirm it from the code as it
stands, without archaeology? **NECESSARY?** — would someone changing this code make a **worse
decision** without it?

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | **keep** — a constraint the reader can verify | **drop** — it narrates the code |
| **not checkable** | **move** — real rationale, unverifiable in place | **drop** — history |

⚠ **Accuracy is not one of the questions.** *"Moved here from `x.validate` when that module was
deleted"* is true, uncheckable and unnecessary, so it goes. History that is *correct* reads as
*earning its place*; accuracy is why it was never deleted, not a reason to keep it.

**A fifth verdict: `correct`.** When a block is on-subject and load-bearing but says something
false, the answer is neither drop nor compact — it is the true sentence, with the evidence that
settles it. A real pass did this **82 times** under a four-verdict vocabulary and had to file every
one as something else.

**Rule on sentences, not blocks.** ⚠ **A single `keep` sentence launders every sentence around it**
— a block's most defensible sentence is usually why the whole block survived, so ruling `keep`
because *part* of it is load-bearing is the signal to descend a level.

For **move**, name the destination and **copy the WHOLE block there, including the part that stays
in the code**; a destination holding only the discarded half reads as a list of dead things, and no
later pass can judge it. For **compact**, propose the replacement — keep the constraint and what
breaks without it; prefer *"X must be Y because Z breaks otherwise"* over *"this used to be W."*

⚠ **A block one line over cap is, by construction, mostly correct.** Measured on a burn-down tail,
27 of the last 48 over-cap runs were over by exactly one. Cut the single least-checkable line; **do
not rewrite a block that is already true, current and on-subject.**

⚠ **`TODO`, `FIXME`, `HACK`, `XXX`, `BUG` are free** — they point *outward*, at work not done, so
they never count against a cap and never split a run. Otherwise the cheapest way back to green is
deleting the pointer to filed work.

Do not pad. **keep** is a real verdict; a review returning mostly `keep` is a good outcome.

⚠ **The dangerous cell**: a comment claiming a guard that does not exist licenses a deletion, and
reads as safe for exactly that reason. Cite a claimed guard precisely enough to find, or say there
is none. Its sibling: a rule **stated in several places with no owner**, each site performing part
of it and re-explaining the whole — that is why the comments got long, and it is a code-shape
finding with the comment as evidence.

⚠ **Changing one copy of a paired value is the commonest defect a prose pass CREATES**, because a
pass edits where it is reading. Before proposing any number, `git grep` the number; before
proposing a name, grep the name. The second copy never appears in your diff.

## Comments and docstrings are governed differently

**A `#` comment is governed by LENGTH** — it interrupts code, so its cost is the screen space
between the line above and the line below. **A docstring is governed by FORMAT** — a summary line,
then `Args:`/`Returns:`/`Raises:` only where they say something the signature does not. ⚠ **If the
repo states a docstring style, it wins**: some allow only a summary plus a couple of clarifying
lines and no rationale paragraph at all. Read the guard before ruling a docstring long.

So: over-length is a finding on a `#` run and only a style question on a docstring; a summary that
does not summarise (`"""Yield …"""` on a function returning a tuple) and a documented parameter
that does not exist are docstring-only; carrying history, a date or a quotation, and describing the
wrong code, are findings on both.

Four shapes no line counter can see: a **trailing** comment running on into comment-only lines
below it (a FORMATTING finding — lift the whole thing above the line); a block split by an inserted
statement, where only the half still discussing what came *before* is the finding; **the wrong half
surviving** a shortening — check what SURVIVED, not what went; and **refactoring drift**, commentary
left behind describing code that moved away.

## Phase 3 — Present. Always.

**This skill never edits.** Report grouped by verdict, most consequential first, replacement text
inline for every `compact` and `correct`, and the inventory count — *N blocks read, M findings* —
so a reader can tell "clean" from "not looked at". Then stop.

⚠ **Even when the human names the edit** — "cap them", "fix these", "go do it" — the deliverable is
the report: *"Report only, per the skill — say the word and I'll apply the verdicts you accept."*
The review's value is the human's disagreement with it, and **an edit applied is a verdict never
ruled on**. Measured: two runs on near-identical imperative prompts split, one returning a report
and the other an 846-line diff; neither human knew which was coming.

## Rails for the pass that applies these

- **A block is bounded by CODE, not blank lines** — else a 9-line block becomes 6 + blank + 3.
- **Build the `old` string programmatically and require `count == 1`**, or refuse the whole file. A
  near-miss must be a loud refusal, never an edit landing somewhere plausible.
- **Never change a line of code, a type annotation, or a string literal.** Prove it with an AST
  diff, docstrings blanked, against the pre-edit file. ⚠ Run the proof on the commit you *doubt* —
  measured, it was announced for a commit already clean while the one that silently changed four
  files got none.
- **Re-read the result as prose.** The one defect that survived three review passes was a severed
  sentence: the edit landed exactly as proposed, every mechanical check passed, and the stump was
  welded to the line below.
- **Extract before you cut** for `move`, and **re-check your own replacements** against the cap and
  the currency rule — a pass that cut seven obituaries wrote seven new ones, one of them twice.

## What this skill is not

`/simplify` reviews code structure and applies what it finds; `/code-review` hunts correctness
bugs. This one reviews prose and only ever proposes: `/simplify` ends in a diff, this ends in a
list of questions.

**Every example above is invented and every measurement anonymised. Keep it that way.** Quoting a
real comment teaches a reviewer to recognise *that comment* instead of the shape, and it rots: the
day someone acts on the finding, this file cites something that no longer exists — a hygiene skill
carrying its own obituary.
