---
name: comment-review
description: Review the comments and docstrings in the files a change touched, across four angles — locality, currency, functionality, module coherence — using parallel read-only subagents, and return each finding as finding/location/summary/change-requirement for the human to rule on. Use this whenever comments or documentation are the subject: after finishing a task that added or edited commentary, when a file's comments have drifted from what the code now does, when someone says a comment is too long or out of date or "isn't this history", when reviewing a diff specifically for its prose rather than its logic, before a docs or comment burn-down, or when asked to check whether a module still reads as one module. Trigger on phrasings that never say "comment review" — "these comments are getting out of hand", "does this docstring still match", "is this comment still true", "clean up the narration in this file", "why does this file need so much explaining" all mean run this. It is NOT /simplify (which reviews code structure) and NOT /code-review (which hunts correctness bugs). The REVIEWERS never edit; the task agent applies what the human approves, and every applied change passes a residue check against the original prose.
---

# comment-review

`/comment-review [level] [cap] [target] [style]`

**An editorial board for the comments and docstrings a change touched.** Four editors read
the same manuscript from four angles, a copy editor writes one set of edits, a condenser cuts
them to fit, the author approves **that** text, and the page is proofed. Structure and fact
first, then truth, then fit, then the page.

```
1 PROJECT      2 ANNOTATE   3 FIND      4 MARK   5 EDIT   6 COMPACT   7 APPROVAL   8 REVIEW
  DETERMINATION             REFERENCES                        │            ▲
                                                              └─ no cap ───┘
```

| # | stage | who acts | what exists at the end of it |
|---|---|---|---|
| 1 | **PROJECT DETERMINATION** | task agent | language, doc convention, cap, project rules, style sheet, name corpus |
| 2 | **ANNOTATE** | `sweep.py` | every comment run and docstring located, as a node on the prose tree |
| 3 | **FIND REFERENCES** | `sweep.py` | every reference each node makes, resolved — paths, symbols, counts |
| 4 | **MARK** | 4 reviewers | findings on the nodes — read-only, nothing written |
| 5 | **EDIT** | task agent | one verdict per block and the **full-length** replacement text |
| 6 | **COMPACT** | task agent | that text cut to the cap — **skipped entirely if there is no cap** |
| 7 | **APPROVAL** | **author**, then task agent | the author rules on the FINAL text; it is then applied |
| 8 | **REVIEW** | task agent | the finished page read as a reader would read it |

**This file is the task agent's.** Each reviewer is a named agent carrying its own angle and
reading [`references/reviewer-brief.md`](references/reviewer-brief.md) itself.
[`references/compact.md`](references/compact.md) loads at stage 6 — **before** the author sees
anything — and [`references/sweep.md`](references/sweep.md) only after approval. **Nobody loads
all of it**, and no file restates another.

## The eight verdicts

Everything below this line uses these eight words. A reviewer emits them; **you receive four
per block and must synthesise ONE**, so what matters here is what each obliges *you* to do:

| verdict | the claim is | what you do with it |
|---|---|---|
| `clean` | checked-and-verified | nothing. One angle declining to find anything, **not** a pass |
| `query` | unsettled | resolve it or escalate it. It blocks every other verdict on that sentence |
| `drop` | true but not worth keeping | delete the sentence |
| `correct` | **FALSE** | apply the true/false pair. **Always before any `patch`** |
| `patch` | **TRUE**, badly worded | apply the rewrite |
| `add` | missing entirely | insert the text at the anchor named with it |
| `move` | true, and not code's to hold | extract verbatim to the destination resolved at 1.4 |
| `split` | two claims in one block | re-anchor each fragment to the code it is about |

⚠⚠ **`correct` and `patch` are the distinction the whole design turns on.** `correct` says the
sentence is wrong; `patch` says it is right and reads badly. Applying a `patch` to a false
sentence polishes the wording of a falsehood and retires the finding — the laundering failure
in its purest form. That is why stage 5 orders them, and why they are separate words.

A reviewer's verdict is only usable if it carries its payload (`correct` carries a pair,
`move` carries a source and destination, `add` carries an anchor). That contract is the reviewers', and
[`references/reviewer-brief.md`](references/reviewer-brief.md) holds it — you enforce it at
stage 5 by refusing a verdict that arrives without one.

## Why the stages are in this order

**1–3 build a tree and write nothing.** Every comment run and every docstring is a node,
attached to the declaration it annotates, with every reference it makes already resolved.
Most of the rules further down are consequences of that shape rather than separate
instructions:

- **coverage is a tree walk.** You visited every node or you did not — *"a block nobody
  mentioned is a gap in the mark, not a block that passed"* is the walk being complete, not a
  discipline to remember.
- **the marks are annotations on a node**, so a reviewer receives resolved references instead
  of re-deriving them.
- **the four angles are four visitors over one tree**, which is why their overlap is signal.
- **the edits are applied to NODES**, so "never change a line of code" holds by construction
  — the AST proof in `sweep.md` confirms that rather than being the only thing enforcing it.

⚠ **The model is the tree; the implementation depends on nothing.** `scripts/sweep.py` builds
it from the stdlib alone, at the tier available for each file's language. Both tiers find the
same blocks and differ only in what else they can say:

| tier | needs | answers | cannot answer |
|---|---|---|---|
| `tokenized` | a lexer + AST (Python: the stdlib) | blocks, marks, **docstring** owners | a **comment's** owner |
| `lexical` | a comment-syntax record, nothing else | blocks, marks | any owner; a marker inside an exotic string |

⚠⚠ **NO COMMENT carries an owner, in any language.** A docstring's owner comes free from the
AST; a `#` run's does not, and nothing infers it. So **every locality verdict rests on a
reviewer reading the file** — a judgement no field records and nothing downstream can check.
Treat a placement finding as a CANDIDATE and **say so in your stage 2-3 report**, the same way
an unavailable `move` is said at stage 1 rather than discovered at stage 6.

⚠ **Only LOCALITY is affected.** Currency, functionality and module coherence never ask who
owns a block, so they run identically everywhere — three of the four angles are at full
strength on any file the census can read. "No parser for this language" reads like "no review"
and is not.

⭐ **A structural tier existed and was REMOVED on 2026-08-14, measured.** libcst resolved
owners for 50% of comment blocks and silently missed 13 of 160 that the stdlib found — a
comment inside an expression belongs to no node's `leading_lines`, including a file-header
copyright block. **A block missing from the census is a block nobody reviews**, and that beats
an unresolved owner: the first is silent, the second only weakens a verdict. It was also
Python-only, so it bought nothing for the ten other languages. Numbers and the full argument:
`evidence/tier-measurement.md`. ⚠ Reopen only for a tier that misses **zero** blocks.

Depending on nothing is the point: this skill must run on a fresh checkout, and a tier chosen
by whether some package happens to be importable makes coverage depend on the ambient
environment. **Adding a language is a row of data in `LANGUAGES`** — `python
<skill>/scripts/sweep.py --languages` lists what is known. A suffix with no record is
**reported as unreviewable, never silently skipped.**

**MARK (4) is separate from EDIT (5)** because a reviewer that fixes what it finds has
destroyed the finding. The brief holds that rule and binds the reviewers to it.

**EDIT (5) writes at FULL LENGTH and is not allowed to consider the cap.** Its only job is a
comment that is true, local and load-bearing. Length is not one of its questions, and a run
that returns long correct prose has succeeded.

**COMPACT (6) is a separate pass over that text, and it comes AFTER edit and BEFORE
approval.** Two constraints pin it into exactly this slot:

- **After EDIT**, because prose can only be shortened without losing information once it is
  true. Shortening first is how a false sentence survives — it gets *trimmed around* rather
  than checked, arriving shorter, cleaner, in-cap and strictly harder to falsify.
- ⚠⚠ **Before APPROVAL, because the author must rule on the text that will actually be
  written.** Showing a full-length comment, getting a yes, and then writing a compacted one
  means the author approved something that never reached the file. That is a bait-and-switch,
  and it is worse here than almost anywhere, because this author approves quickly and
  unaudited — the one thing they are relied on for is that what they saw is what lands.

⚠ **The two stages have different inputs, and that is deliberate.** EDIT needs the code, the
marks and the four verdicts. COMPACT needs only the **original block**, the **edited text**,
the **cap** and the **style sheet** — never the reasoning that produced the edit. That
narrower contract is a safety property: an agent that never saw the argument cannot preserve
a sentence because it remembers writing it, and it is why this may be handed to a **separate
subagent** — one that composes, one that condenses. The seam is the input list above.

**APPROVAL (7) presents the FINAL text**, takes the ruling, and only then applies.

**REVIEW (8) is the only stage that reads the artifact against itself.** Everything before it
compares prose to code; this asks whether the finished page still reads.

## Three roles

**The HUMAN is the AUTHOR, and is absent.** They approve almost everything, quickly,
unaudited — a direction, not a diff. **So every proposal must be safe to approve blindly.**
Their disagreement is valuable; it is not a safety mechanism and must never be used as one.

⚠⚠ **That makes this an editorial board with an absentee author, and one principle follows:
CONSERVATIVE ON MEANING, FREE ON FORM.** An editor rules on form; the author rules on what a
sentence claims. With the author not reading, you may fix wording, placement and length on your
own judgement — but every change to what a sentence CLAIMS needs evidence in hand, or it is a
`query`. That is why `correct` carries a pair and `patch` carries only a rewrite.

**The TASK AGENT — you.** Run stages 1–3, launch the reviewers, rule, present, and after
approval sweep. You are the only participant that writes, and only after approval. Reach
every block, rule on sentences, **write the replacement text yourself**, and verify what you
write. "compact + correct" is not a finding: it hands back the judgement this review exists
to make.

**The REVIEWERS** are read-only, one angle each, and never see this file.

## Arguments

- **`cap`** — integer, optional; max lines for one `#` run. **This skill has no cap of its
  own** and must not invent one. None given and none published → **no cap**; report the
  longest block left.
- **`target`** — a path; **replaces** the diff scope, never intersects it.
- **`level`** — how deep to edit, declared before starting. Default `full`.

| level | angles | verdicts available |
|---|---|---|
| `fact-check` | currency, functionality | `correct` · `query` · `clean` |
| `line` | + locality | + `drop` · `move` · `split` · `add` |
| `full` | + module coherence | + `patch` |
| `proof` | none — stage 8 (REVIEW) only, over files a previous pass edited | — |

⚠⚠ **If `move` is unavailable (1.4), NO level reaches the cap, and say so up front.** True
rationale with no destination becomes `clean` and stays where it is, so COMPACT must cap prose
it is forbidden to cut. Measured on all three runs: the residual over-cap blocks were almost
entirely this. The cap is reachable again the day the destination tree exists — that is worth
telling the human at stage 1, not at stage 6.

⚠ **A level is a real answer to a file too big for one pass.** Measured: a run over a
4,000-line module left 73 blocks over cap and said plainly *"I ran out of budget, not
justification."* `fact-check` on that file finishes, and finishes with the falsehoods gone —
which is the half that matters. Say which level you ran, in the report.
- **`style`** — a path to a style sheet from a previous run. Optional; see 1.5.

⚠⚠ **THE CAP IS APPLIED IN STAGE 6 AND NOWHERE ELSE** — never while text is being written,
and **never passed to a reviewer**. Length is not an angle; the reason is in the brief.

## Stage 1 — PROJECT DETERMINATION: ground truth

**1.1 Scope from the MERGE BASE** — `git merge-base HEAD <upstream>`, then
`git diff --name-only "$base"..HEAD`. Never `A...B` between two tips, never a `HEAD~1`
fallback; both silently narrow. Add `git diff --name-only HEAD` if dirty.

**1.2 Find the repo's published cap and read HOW it counts** — matching the number while
counting differently produces a file that claims to comply and does not.

⚠ **Then check the guard EXISTS, and if it does not, say what follows.** A convention citing
an absent test publishes a rule enforced by nothing. **Proceed** — an unenforced rule is still
the repo's rule and you have no standing to overrule it — but change two things and say so in
the final report:

- **Treat every citation in scope as unverified**, not as evidence. The prose was written
  against a checker that never ran; measured, three runs found 6, 19 and 8 rotted citations in
  four files each.
- **Expect a high finding rate and do not read it as a defective codebase.** Prose no guard has
  ever measured is defective at a high rate by construction, and that fact belongs in the
  report as a finding about the REPO, above any individual block.

⚠ **Ask which markers the repo exempts from the cap** (`TODO`, `FIXME`, `HACK`, `XXX`, `BUG`
is the common set). An exempt marker neither counts toward the cap nor splits a run — a block
that is in-cap except for a marker is IN CAP. Without this, the cheapest route to green is
deleting the pointer to filed work.

**1.3 Determine the repo's doc style** - Rewriting docstrings in the wrong style will just
frustrate them - get a template for the appropriate docstring format for use when rewriting the 
docstring.

**1.4 Resolve every `move` destination**, and decide NOW what happens if none resolves. A
verdict pointing at a tree that does not exist is not a verdict.

⚠⚠ **If the destination tree is absent, `move` is UNAVAILABLE for this run — and its blocks
become `clean`, never `drop`.** Say so at stage 7a and offer the human the one-line alternative
(create the tree, or name another destination). This matters because the matrix routes
*not-checkable + necessary* to `move`, and a repo that stages prose usually also rules that
prose is MOVED, never deleted — so with no destination those two rules leave the block with no
legal verdict at all. Measured: all three runs hit this, and one dropped a 40-line history
under it. **Keeping true prose in place costs a cap violation you can report. Dropping it costs
the only copy.**

**1.5 Read the STYLE SHEET if one exists** (`style` argument), and start one if not.

This is the copy-editor's artifact and it is the only thing in this skill that PERSISTS between
runs. It records decisions made for THIS codebase so the next pass does not relitigate them:
the dialect its identifiers use, how domain terms are capitalised, the house citation form, the
docstring convention from 1.3, terms of art with a fixed meaning, and any ruling the human made
last time.

⚠⚠ **Without it, a pass drifts the prose while fixing it.** Measured: one run introduced **14
en-GB spellings** into a codebase whose identifiers are en-US — including *"the event's colour"*
on a function returning a `colorId`. Every angle was satisfied; nothing owned consistency. There
is no fifth reviewer for this, deliberately — consistency is enforced at the SWEEP, against the
sheet, not by another visitor over the tree.

⚠ **It is binding, not advisory.** An edit that departs from the sheet is out of scope in the
same way a code change is. If the sheet is wrong, that is a `query`, not a licence.

**1.6 Build the name corpus from the AST** — every liveness check downstream depends on it.
From the AST never raw text (text contains the comments being checked, so everything passes);
skip directories holding `pyvenv.cfg`; never harvest string constants from tests
(`assert "x" not in y` makes a dead name read alive); exclude `.md`/`.txt`; resolve a dotted
name on its **head** segment only.

## Stages 2–3 — ANNOTATE, then FIND REFERENCES

```bash
python <skill>/scripts/sweep.py --cap N --width N --repo . <paths...>
```

It emits the numbered tree — `N  file:start-end  kind  lines  marks  (owner)` — with each
node's references already resolved, and it prints the tier each file reached. Run it; do not
re-derive its output by hand.

⚠ **Write the census to a path unique to THIS run** and hand the reviewers that path. Measured:
two concurrent reviews shared one scratch filename and the second overwrote the first between
writing and reading it. Four reviewers happened to notice and regenerate their own; nothing in
the document required them to.

**What it guarantees, and why the reviewers depend on it.** A run is bounded by CODE, not
blank lines (else 9 lines becomes 6+3 and passes). A run is matched as ONE joined string,
because prose wraps and a line-local match reports the fragment instead of the claim. Nothing
is truncated — a partial list cannot be used to skip anything. Anything it could not read is
**named**, because a hole in the name corpus turns every symbol defined only there into a
false obituary.

### What counts as ONE block

```python
variable_a = 1234
# ← code ENDS any run above it

# comment_block starts               lines = 1
# TODO: important thing in it        lines = 1   ← a marker is FREE: not counted,
#                and it does NOT split the run
# comment_block continues            lines = 2   ← a blank line does NOT end a run
# comment_block ends                 lines = 3
result = foo_bar(variable_a)  # ← code ENDS the run. One block, 3 lines,
#    OWNED by this statement, not by variable_a
```

Four physical comment lines, **one** node, **three** counted lines. Each of those three
facts is a separate rule, and getting any of them wrong changes what the reviewers see:

- **Only code ends a run.** A blank line does not. Split on blanks and a 9-line block reads
  as `6 + 3` and passes a cap of 6 — the single cheapest way to fake compliance.
- **A work marker is free** (`TODO` `FIXME` `HACK` `XXX` `BUG`, or whatever 1.2 found this
  repo exempts). It does not count toward the cap and it does not split the run. Both halves
  matter: if it counted, the cheapest route to green would be deleting a pointer to filed
  work; if it split, a block could be made compliant by adding one. ⚠ **A marker's
  CONTINUATION lines still count** — only the marker line itself is free.
- **A block belongs to the code BELOW it**, which is what makes locality answerable. The
  block above is about `result`, and a locality finding says so by naming that owner.
- **A trailing comment is its own block**, one line, owned by the line it sits on — and a
  trailing comment whose sentence carries past its own line is a finding in itself.

Marks, and what resolving each one means:

| mark | resolved by |
|---|---|
| `cites-a-path` | tracked in the tree? ⚠ present-but-untracked is **unverifiable**, not dangling |
| `names-a-symbol` | defined in the AST corpus? (head segment; `foo()` normalised) |
| `counted` | re-derive the POPULATION, then count it |
| `coverage-claim` | does the guard exist — **can it fail**, and does it pass with its exemptions OFF? |
| `forbids-a-literal` | grep the forbidden literal across that file |
| `repeated-literal` | where else is this number written? one source at both ends of a round trip? |

⚠⚠ **The last four are where the defects are. Check the CLAIM, not the CITATION.** Resolving
a path *feels* like verification; resolving a claim **is** it.

⚠ **Scope by SUBJECT, not by file extension.** A config, data or documentation file carrying
prose that justifies a value is a node like any other. Measured: one unreviewed config file
held 12 confirmed defects, six of them the same rewrite the pass had already applied in a
`.py` file. Where the change edits a symbol, a path or a number, `git grep` that token and add
every file that NAMES it — the diff decides what changed, not what is in scope.

Report `N blocks, K marks resolved`, the longest run, and the widest line.

## Stage 4 — MARK: four reviewers, in parallel

**Dispatch all four in ONE message** so they run concurrently, by agent name:

| agent | asks |
|---|---|
| `comment-review-locality` | does this belong to the line it sits on? |
| `comment-review-currency` | does this describe the program as it is now? |
| `comment-review-functionality` | does the commentary match what the function is for? |
| `comment-review-module-coherence` | do the comments say this is one module? |

Each already carries its own angle and reads the shared brief itself. **You supply the run
context, and only that:** the numbered census, the stage-1 resolutions, the **docstring
template** from 1.3, the **style sheet** from 1.5, the **level**, and the two lists — **FILES UNDER REVIEW** (the only files a verdict may
target) and **REFERENCE ONLY** (read to settle a claim, never propose a change). Without the
second list a reviewer either treats the whole repo as in scope or stops reading at the
boundary, which disables every cross-file check.

⚠ **The template matters because reviewers write replacement text.** A correct sentence in the
wrong docstring convention is a finding the human has to redo by hand, and they are not
expected to be careful enough to notice.

⚠ **Do not paste the brief or an angle into the prompt.** They are single-sourced on purpose;
a copy in a prompt is a copy that goes stale.

⚠ **REFERENCE ONLY is a SELECTION, not a leftover.** Name the files that settle claims code
cannot: the repo's **decision record** (*"ruled"*, *"rejected"*, *"deferred"* have no code
oracle), any **authority document** holding dated facts, and — where the repo stages prose out
of code — the **extracted/mirror copy** of the files under review. Measured: an invented
ruling with zero entries in the record on its cited date; a retracted fact surviving in two
docstrings and one live constant; and a mirror tree that held the CORRECT text in **3 of 3**
known inversions while the code was backwards. The code still settles code claims — a
disagreement with the mirror is itself a finding.

Overlap between angles is **signal**: a claim one affirms and another refutes is the
highest-value output here. Measured — one angle read a false absence claim and wrote
"CONFIRMED"; another refuted it by grep. A single-angle run ratifies falsehoods.

**Re-review is normal.** An accreted block is layered — a live constraint, an origin story, a
correction to it, a review label — and peeling one reveals the next. Send a block back when
angles contradict, when a citation resolves to a *different* thing than the prose implies, or
when you cannot write the replacement text.

## Stage 5 — EDIT: one verdict, one FULL-LENGTH replacement

⚠⚠ **Resolve the reviewers' evidence yourself.** Open each finding's `SUMMARY` right half
and confirm the quoted line is within a few lines of its citation. A finding whose evidence is
not there is not a finding — send it back. Measured: one graded run had **fabricated 5 of its 7
reviewer reports**, and self-certified `CONFIRMED` ran at **97% across 298 findings** — a label
two runs in three thousand disagree with does not discriminate. **Never grade a review by
reading its report.**

⚠ **A block that ends mid-clause is a finding, and its verdict is `correct`.** A run whose last
sentence stops mid-air — a severed trailing comment, a `move` that cut a sentence in half — is
neither checkable nor necessary, so the matrix routes it to `drop`, deleting the pointer instead
of repairing it. Restore the sentence.

⚠ **Two findings quoting the same sentence in different files are ONE finding.** A pass edits
where it is reading, fixes the copy in front of it, and manufactures a disagreement with the one
it never opened. Contradicting verdicts trigger a **re-review**, never a tie-break.

**Is it CHECKABLE?** confirmable from the code as it stands. **Is it NECESSARY?** would
someone changing this code make a **worse decision** without it? Those two questions decide
whether a TRUE sentence earns its place:

| | **necessary** | **not necessary** |
|---|---|---|
| **checkable** | it stays | **drop** — it narrates what the code already says |
| **not checkable** | **move** — real rationale, unverifiable in place | **drop** — history |

⚠ **The matrix only runs on sentences you have already established are TRUE.** A false claim is
not a point on it — it is `correct`, and correcting it comes first. Read generally, *"truth is
not one of the questions"* acquits a falsehood, which is measured twice in independent runs.
The rule applies to history that is TRUE-but-useless and nowhere else.

### Synthesising one comment out of N verdicts

Four reviewers rule on the same block, so you hold several recommendations and must emit **one**
replacement. Apply them in this order. It is not arbitrary — each step depends on the one above
being settled:

1. **`query`** — resolve it or escalate it. An unresolved claim cannot be corrected, patched or
   dropped, because you would be editing something nobody has read.
2. **`drop` and `move`** — take out what is leaving. Doing this first stops you correcting a
   sentence that is about to go.
3. **`correct`** — fix truth, on what remains.
4. **`patch`** — fix wording, on text now known to be true. ⚠ Never before step 3.
5. **`add`** — insert at the stated anchors.
6. **`split`** — re-anchor whatever belongs beside different code.
7. **`clean`** — the null verdict. A block whose four angles all returned `clean`, and nothing
   else, stands unchanged.

Then emit the replacement and run the residue check on **the whole synthesised block once** —
not once per verdict. The check compares against the original, and the original was one block.

**Three rules that resolve the common collisions:**

- **Any `correct` outranks every `clean`.** Three angles finding nothing does not soften one
  angle finding a falsehood; they were not looking for the same thing.
- **`correct` and `patch` on the same sentence:** correct first, then re-read the patch against
  the corrected text. Usually it no longer applies.
- **`drop` and `correct` on the same sentence is a contradiction**, not a merge — one angle says
  it should not exist and another says it should exist and be true. Send it back for re-review.

⚠ **Dedup on the CLAIM, not the block**, before any of this.

⚠⚠ **THE SENTENCE YOU PROPOSE TO KEEP IS A FINDING YOU HAVE NOT RAISED.** Before any `patch`
or `move`, verify the retained clause the way stage 3 resolves a mark. The reviewer keeps the
load-bearing-*sounding* clause — which is the claim, which is what is wrong — and cuts the
**provenance** around it: the date, the pointer, the grepable name.

```
before:  # Retry budget is 3, not the 5 the config advertises — `Backoff.next()`
         # halves it for idempotent verbs, and `docs/retries.md` records why.
         # Raising it re-opens the thundering-herd incident.
after:   # Retry budget is 3, not the 5 the config advertises.
```

If the budget is not 3, it was wrong before and is wrong after — but the cut took the two
things that let a reader find out: the symbol that computes it, and the document that records
why. Shorter, cleaner, in-cap, and **strictly harder to falsify than what it replaced.** A
block trimmed around an unchecked claim is **laundered, not reviewed**. ⚠ **`move` has no truth check on its
path** — "write the destination verbatim" copies a falsehood somewhere harder to find.

⚠ **Length is not your question at this stage.** A block that is true, local and load-bearing
is finished here however long it is; COMPACT shortens it only if a cap applies. A run that
returns mostly `clean` is a good outcome, not a lazy one.

**Two shapes a length rule cannot express.** A comment claiming *"pinned by X"* **licenses
future edits** — ⚠ the dangerous cell is a deletion justified by coverage nobody can find,
which reads as safe for exactly that reason. Grep the cited name, every time. And a rule
**stated in several places with no owning definition** is why the comments got long.

**A `#` comment is governed by LENGTH; a docstring by FORMAT.** Long is not a violation; what
fails is a body carrying what is not documentation — a date, a quotation, a retraction, a
rationale paragraph, a claim about callers or coverage — **at any length**. ⚠ **Acquit on
KIND, never on LENGTH**: a two-line docstring whose summary runs on is still a finding.

Invisible to any counter: a **trailing comment carrying past its own line** (a FORMATTING
finding — lift it above); a **block split by an inserted statement**, where only the half still
talking about what came before is the finding; **the wrong half surviving** — check what
SURVIVED, not what went; **refactoring drift**.

## Stage 6 — COMPACT: only if there is a cap

**If no cap applies, the run SKIPS this stage entirely.** Say so: the prose is correct, and
absent a budget "long" is not a defect.

If there is a cap, and only once **every** block from stage 5 is CORRECT, load
[`references/compact.md`](references/compact.md) and cut the edited text to fit.

⚠ **Nothing is on disk yet.** This pass condenses the PROPOSED text, not a file — the author
has not ruled and the sweep has not run. That is the whole reason this stage sits here: what
you hand to stage 7a is what will be written.

⚠ **Do not fold it back into stage 5.** Compaction decisions depend on the final state of the
whole tree — a `move` that relocates prose between blocks, an owner that collapses N
restatements into one — and none of that is settled until every block is edited. `compact.md`
carries the argument and the per-block procedure.

## Stage 7a — APPROVAL: present the FINAL text, then stop

Grouped by verdict, most consequential first, in the four-part format, replacement text inline
for every `correct` / `patch` / `add`. State the **level** you ran, **raised / clean**, and the
longest block that will remain. **The mark ends here.**

⚠⚠ **What you show IS what gets written.** If stage 6 ran, show the COMPACTED text — never the
full-length version with a note that it will be shortened. The author rules once, quickly, and
on the assumption that the text in front of them is the text that lands.

**Hand back the STYLE SHEET**, updated with every decision this run made — the sheet is how the
next pass avoids re-deciding, and it is worthless if it stays in your head.

⚠ **Approval IS authorization.** "Yes", "do it", "continue" → load `references/sweep.md` and
apply. Never-edit binds reviewers, not you acting on an approval.

## Stage 7b — APPROVAL: apply what was approved

On approval, load [`references/sweep.md`](references/sweep.md) and follow it. It carries the
residue check and the apply rails. Do not apply from memory.

⚠ **The sweep writes the APPROVED text verbatim.** It does not shorten, re-word or re-judge —
every one of those questions was settled upstream, and re-opening one here writes something
the author never saw.

## Stage 8 — REVIEW: the finished page

The last pass, over the **finished file**, reading it as a reader would rather than as a list of
blocks. Everything before this examined prose against code; this examines the **artifact against
itself**, and it is the only stage that can see damage the editing caused.

Read each changed file end to end and look for exactly this:

- **a block that is no longer a proposition** — a sentence ending mid-clause, a hanging clause
  under a deleted line, a contrast marker whose contrast went. Measured repeatedly, and it
  passes every mechanical check there is: it is not stale, not misplaced, not false — it is
  ungrammatical, and nothing upstream asks whether the prose still parses.
- **runs that merged** — an `add` landing next to an existing block across a blank line makes
  one longer run. A compliant edit producing a violation, visible only here.
- **the same sentence now in two places**, because a `move` landed beside one that already said
  it.
- **drift against the style sheet** — dialect, capitalisation, citation form.

⚠ **Fix only what THIS pass created.** A defect you find that predates the run is a finding for
the next one, not a licence to reopen the sweep. Say which is which.

⚠ **The proof pass is not the residue check.** The residue check is inbound and per-block —
*did this block lose something?* This asks *does the finished page read?* A pass can satisfy the
first everywhere and fail the second, and that is the common case, because each edit was
defensible alone.

## What this skill is not

`/simplify` reviews code structure and applies its fixes. `/code-review` hunts correctness
bugs. This reviews prose and writes nothing until the human approves. A defect noticed anyway
is **named and left**.
