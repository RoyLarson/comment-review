---
name: comment-review
description: Review the comments and docstrings in the files a change touched, across four angles — ownership-context, block-context, function-context, module-context — using parallel read-only subagents, and return each finding as verdict/location/summary/finding/change for the human to rule on. Use this whenever comments or documentation are the subject: after finishing a task that added or edited commentary, when a file's comments have drifted from what the code now does, when someone says a comment is too long or out of date or "isn't this history", when reviewing a diff specifically for its prose rather than its logic, before a docs or comment burn-down, or when asked to check whether a module still reads as one module. Trigger on phrasings that never say "comment review" — "these comments are getting out of hand", "does this docstring still match", "is this comment still true", "clean up the narration in this file", "why does this file need so much explaining" all mean run this. It is NOT /simplify (which reviews code structure) and NOT /code-review (which hunts correctness bugs). The REVIEWERS never edit; the task agent applies what the human approves, and every applied change passes a residue check against the original prose.
---

# comment-review

`/comment-review [level] [cap] [target] [style]`

**An editorial board for the comments and docstrings a change touched.** Four editors read
the same manuscript from four angles, a copy editor writes one set of edits, a condenser cuts
them to fit, the author approves **that** text, and the page is proofed. Structure and fact
first, then truth, then fit, then the page.

```
1 PROJECT      2 ANNOTATE   3 FIND      4 MARK   5 EDIT   6 COMPACT   7a PRESENT   8 REVIEW
  DETERMINATION             REFERENCES               │                    7b APPLY
                                                     └──── no cap ────────▲
```

| # | stage | who acts | what exists at the end of it |
|---|---|---|---|
| 1 | **PROJECT DETERMINATION** | task agent | language, doc convention, cap and width, project rules, style sheet, and where the name corpus will come from |
| 2 | **ANNOTATE** | `census.py` | every comment run and docstring located, as a node on the prose tree |
| 3 | **FIND REFERENCES** | `census.py` | every reference each node makes, resolved — paths, symbols, counts |
| 4 | **MARK** | 4 reviewers | findings on the nodes — read-only, nothing written |
| 5 | **EDIT** | task agent | one verdict per block and the **full-length** replacement text |
| 6 | **COMPACT** | task agent | that text cut to the cap — **skipped entirely if there is no cap** |
| 7a | **APPROVAL — present** | task agent | the FINAL text in front of the author; **the run stops here** |
| 7b | **APPROVAL — apply** | **author**, then task agent | the approved text on disk, byte-for-byte as approved |
| 8 | **REVIEW** | task agent | the finished page read as a reader would read it |

**This file is the task agent's.** Each reviewer is a named agent carrying its own angle and
reading [`references/reviewer-brief.md`](references/reviewer-brief.md) itself.
[`references/residue-check.md`](references/residue-check.md) loads at stage 5,
[`references/compact.md`](references/compact.md) at stage 6 — **before** the author sees
anything — [`references/apply.md`](references/apply.md) only after approval, and
[`references/review.md`](references/review.md) at stage 8. **Nobody loads all of it**, and no
file restates another.

## The nine verdicts

Everything below this line uses these nine words. A reviewer emits them; **you receive one per
angle per block and must synthesise ONE**, so what matters here is what each obliges *you* to do:

| verdict | the claim is | what you do with it |
|---|---|---|
| `clean` | nothing to report **from this angle** | nothing. Not a pass, and not a claim the block is correct — it is one angle having no finding, including when the block is outside what that angle reads |
| `query` | unsettled | resolve it or escalate it. It blocks every other verdict on that sentence |
| `drop` | true but not worth keeping | delete the sentence |
| `correct` | **FALSE** | apply the true/false pair. **Always before any `patch`** |
| `patch` | **TRUE**, badly worded | apply the rewrite |
| `add` | missing entirely | insert the text at the anchor named with it |
| `move` | true, and **not code's to hold at all** | extract verbatim OUT of the code, to the destination resolved at 1.4 |
| `reanchor` | true and code's to hold, but **attached to the wrong line** | re-attach the block, unchanged, to the declaration it constrains **in the same file** |
| `split` | two claims in one block | re-anchor each fragment to the code it is about |

⚠⚠ **`move` and `reanchor` are separate words because they have different AVAILABILITY.**
`move` takes prose out of the code and needs a destination tree, so 1.4 can rule it UNAVAILABLE
for a whole run. `reanchor` re-attaches a block inside the same file and needs nothing outside
it, so 1.4 never withholds it. ⚠ Which LEVELS carry each is
[`references/reviewer-brief.md`](references/reviewer-brief.md)'s to say, not this file's.

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
  — the AST proof in `apply.md` confirms that rather than being the only thing enforcing it.

⚠ **The model is the tree; the implementation depends on nothing.** `scripts/census.py` builds
it from the stdlib alone, at the tier available for each file's language. Both tiers find the
same blocks and differ only in what else they can say:

| tier | needs | answers | cannot answer |
|---|---|---|---|
| `tokenized` | a lexer + AST (Python: the stdlib) | blocks, marks, **docstring** owners | a **comment's** owner |
| `lexical` | a comment-syntax record, nothing else | blocks, marks | any owner; a marker inside an exotic string |

⚠⚠ **NO COMMENT carries an owner, in any language.** A docstring's owner comes free from the
AST; a `#` run's does not, and nothing infers it. So **every ownership-context verdict rests on
a reviewer reading the file** — a judgement no field records and nothing downstream can check.
Treat a placement finding as a CANDIDATE and **say so in your stage 2-3 report**, the same way
an unavailable `move` is said at stage 1 rather than discovered at stage 6.

⚠ **PLACEMENT is what an absent owner weakens, and nothing else.** Block-context and
module-context never ask where a block belongs; function-context asks it only of a body's
comment ORDER, which it reads off the body rather than off a census field. So every angle keeps
every question on any file the census can read — a placement verdict simply rests on the
reviewer. "No parser for this language" reads like "no review" and is not.

⚠⚠ **A block missing from the census is a block nobody reviews, and that outranks ownership.**
An unresolved owner weakens a verdict; an absent block produces none and reports no gap. **Adopt
a richer source of structure only if it misses ZERO blocks.**

Depending on nothing is the point: this skill must run on a fresh checkout, and a tier chosen
by whether some package happens to be importable makes coverage depend on the ambient
environment. **Adding a language is a row of data in `LANGUAGES`** — `python
<skill>/scripts/census.py --languages` lists what is known. A suffix with no record is
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
marks and one verdict per angle that ran. COMPACT needs only the **block's KIND**, the
**original block**, the **edited text**, the **cap** and the **style sheet** — never the
reasoning that produced the edit. That narrower contract is a safety property: an agent that
never saw the argument cannot preserve a sentence because it remembers writing it, and it is
why this may be handed to a **separate subagent** — one that composes, one that condenses.

⚠⚠ **The KIND is in that list because the two kinds obey different rules.** A cap counts lines
in a `#` run; a docstring is governed by FORMAT and long is not a violation. Hand COMPACT a
107-line docstring without its kind and it looks like the same over-length problem as a 7-line
comment run.

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
approval apply. You are the only participant that writes, and only after approval. Reach
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
| `fact-check` | ownership-context, block-context, function-context | `correct` · `query` · `clean` |
| `line` | the same three | + `drop` · `move` · `reanchor` · `split` · `add` |
| `full` | + module-context | + `patch` |
| `proof` | none — stage 8 (REVIEW) only, over files a previous pass edited. ⚠ It has no 7b to complete, so it loads `review.md` directly | — |

⚠⚠ **`ownership-context` runs at every level, including `fact-check`.** The other three check
a claim against the code at their scope; a claim attached to the wrong scope is measured
against the wrong code and `correct`ed into a falsehood.

⚠⚠ **The ladder changes shape and that is the point.** It used to add an ANGLE at each rung;
now `line` adds only VERDICTS, because `ownership-context` already ran at `fact-check`. What it
may emit there is `reviewer-brief.md`'s to say, not this file's.

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

**1.2 Find the repo's published cap and line WIDTH, and read HOW each counts** — matching the
number while counting differently produces a file that claims to comply and does not.

⚠ **Two separate questions, and either may be absent.** A cap bounds the LINES in one `#` run;
a width bounds the CHARACTERS in one line, and they usually live in different files — a
contributing guide, `.editorconfig`, a formatter config. **If the repo publishes neither, say
so and pass neither flag at stages 2-3.** Measured: a run chose a width out of a contributing
guide on its own judgement, and the census then printed `over width (72): 2` as though it were
an established project fact.

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
become `clean`, never `drop`.** Say so HERE, in the stage 1 report, and again at 7a; offer the human the one-line alternative
(create the tree, or name another destination). This matters because the matrix routes
*not-checkable + necessary* to `move`, and a repo that stages prose usually also rules that
prose is MOVED, never deleted — so with no destination those two rules leave the block with no
legal verdict at all — *the matrix* is the checkable/necessary table defined at stage 5, and
it is named here only to explain the consequence. Measured: all three runs hit this, and one
dropped a 40-line history under it. **Keeping true prose in place costs a cap violation you can report. Dropping it costs
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

**1.6 Verify the four reviewer agents are DISPATCHABLE**, before anything else depends on
them. They are plugin agents and their names are NAMESPACED — `comment-review:comment-review-*`
— and they resolve only if the plugin was installed **before this session started**.

⚠⚠ **If they do not resolve, say so at stage 1 and say what you will do instead.** Measured on
all three verification runs: every one failed at stage 4 with
`Agent type 'comment-review-ownership-context' not found`, and every one silently improvised the same
fallback. The sanctioned fallback is **four general-purpose agents given the ANGLE FILES
paths from the packet** — never the angle text pasted into a prompt, which goes
stale the moment an angle is edited. Because the packet already carries those
absolute paths, the fallback is a substitution rather than an improvisation.

**1.7 Probe for a LANGUAGE SERVER, once per language in scope.** One `LSP documentSymbol`
call against a representative file of each. Record which answered — that is a fact about
this run and it belongs in the final report.

The server is the user's, not ours: someone reviewing Rust already runs rust-analyzer, so
this is structure available for free that `census.py` cannot ship. It buys exactly two
things, and neither is the census:

| | with a server | without |
|---|---|---|
| **who owns a block** | `documentSymbol` → the declaration on the line after the run ends | nothing resolves it |
| **is a name alive** | `workspaceSymbol` / `findReferences`, in **any** language | the Python AST corpus only |

⚠⚠ **LSP RETURNS NO COMMENTS, so it can never replace `census.py`.** The nine operations
exposed — definition, references, hover, documentSymbol, workspaceSymbol, implementation and
the call-hierarchy three — return no prose at all; `semanticTokens` and `foldingRange`, the
two that would, are not among them. On a Go file a server reports `func F` at line 4 while
nothing has said there is a comment at line 2 to attach to it. **A block must be FOUND before
anything can own it, so stages 2–3 always run.**

⚠ **Absence is reported, never inferred, and there are THREE states — not two.**

| state | how you learn it | what to report |
| --- | --- | --- |
| a server answered | `documentSymbol` returns symbols | the language, and use it at 1.8 |
| no server for this language | `No LSP server available for file type: .ts` | that language has none |
| **no LSP tool at all** | the tool is absent from the registry — there is no call to issue | **no probe was possible** |

⚠⚠ **The third is not the second.** With no LSP tool the probe cannot be made, so "no server
answered" would be an inference, which the rule above forbids. Say a probe was impossible.
Measured: three runs hit this state and all three had to improvise the distinction. This is
additive: with a server you gain owners and cross-language liveness, without one you lose
nothing you had. What you may not do is let a run that had no server read like one that did.

**1.8 Decide where the name corpus comes from** — every liveness check downstream depends on
it. This substep CHOOSES the source; the corpus itself does not exist until stage 3, because
`census.py` builds it. Do not try to produce it here.

- a server answered at 1.7 → **`workspaceSymbol`**, which covers every language at once
- no server → the AST corpus `census.py` emits at stage 3, Python only
- both → combine them, and say so

From the AST never raw text (text contains the comments being checked, so everything passes);
skip directories holding `pyvenv.cfg`; never harvest string constants from tests
(`assert "x" not in y` makes a dead name read alive); exclude `.md`/`.txt`; resolve a dotted
name on its **head** segment only.

## Stages 2–3 — ANNOTATE, then FIND REFERENCES

⚠ `<skill>` below is the directory holding this SKILL.md — take it from the absolute path you
were given, because a relative one does not resolve from a worktree.

```bash
python <skill>/scripts/census.py --repo . <paths...>          # no cap, no width rule
python <skill>/scripts/census.py --cap 6 --width 88 --repo . <paths...>   # both published
```

It emits the numbered tree — `N  file:start-end  kind  lines  marks  (owner)` — with each
node's references already resolved, and it prints the tier counts for the run. ⚠ Those are
AGGREGATED across files, not per file — on a polyglot run you cannot tell which file reached
which tier, which is exactly when it matters. Run it; do not
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
- **A block belongs to the code BELOW it**, which is what makes ownership-context answerable. The
  block above is about `result`, and an ownership-context finding says so by naming that owner.
- **A trailing comment is its own block**, one line, owned by the line it sits on — and a
  trailing comment whose sentence carries past its own line is a finding in itself.

Marks, and what resolving each one means:

| mark | resolved by |
|---|---|
| `cites-a-path` | tracked in the tree? ⚠ present-but-untracked is **unverifiable**, not dangling |
| `names-a-symbol` | `workspaceSymbol` where 1.7 found a server, else the AST corpus (head segment; `foo()` normalised) |
| `counted` | re-derive the POPULATION, then count it |
| `coverage-claim` | does the guard exist — **can it fail**, and does it pass with its exemptions OFF? |
| `forbids-a-literal` | grep the forbidden literal across that file |
| `repeated-literal` | where else is this number written? one source at both ends of a round trip? |

⚠⚠ **The last four are where the defects are. Check the CLAIM, not the CITATION.** Resolving
a path *feels* like verification; resolving a claim **is** it.

### Enrich the census with the language server, where 1.7 found one

The census names every block; the server can say what a block BELONGS to. Do this once, here,
and attach the answer to the node — not in stage 4, where four reviewers would each re-derive
it and could disagree.

- **Owner** — `documentSymbol` on each file in scope returns every declaration and its line.
  A run ending at line N-1 is owned by the declaration at line N. Attach it; the census
  prints owners it has.
- **Liveness** — for each `names-a-symbol` candidate, `workspaceSymbol` answers whether the
  name exists at all, in any language in the workspace. `findReferences` answers whether
  anything uses it, which is the stronger claim a comment usually makes.

⚠ **A server does not settle a claim, it settles a FACT.** "This name exists" is not "this
comment is true" — the mark stays a CANDIDATE a reviewer confirms, exactly as when the AST
answered it. What changes is the cost of checking, not who decides.

⚠⚠ **Say which servers answered, in the stage 2–3 report, per language.** Availability is a
property of the machine, so two runs over identical input can resolve different sets. A run
that had no server must not read like one that did — and any measurement taken with a server
is not comparable to one taken without.

⚠ **Scope by SUBJECT, not by file extension**, and resolve it with the tool
rather than from memory — this is the INBOUND half of stage 3:

```bash
python <skill>/scripts/referrers.py --repo . <paths under review...>
```

It prints every tracked file that NAMES one of them — by path, by stem, or by a
public top-level definition — and suppresses a token too common to discriminate
rather than dumping it. Those files are the **REFERENCE ONLY** list you hand the
reviewers at stage 4; a config, data or documentation file carrying prose that
justifies a value is a node like any other. Measured: one unreviewed config file
held 12 confirmed defects, six of them the same rewrite the pass had already
applied in a `.py` file.

⚠⚠ **This runs in `target` mode too.** A `target` run has no diff to widen from,
which is exactly why the memory-based rule it replaces could not fire there —
the invocation most likely to be typed by hand was the one with no backlink
discovery at all.

Report what the tool prints: `N files, N blocks`, the per-tier counts, the longest run and the
widest line. ⚠ **Pass `--cap` only if the run HAS one — given as an argument or published and found at
1.2 — and `--width` only if 1.2 found one.** Supplying either uninvited makes the census print
an over-cap or over-width count that reads like a project fact and is your own guess.

## Stage 4 — MARK: four reviewers, in parallel

**Dispatch all four in ONE message** so they run concurrently, by agent name:

| agent | asks |
|---|---|
| `comment-review:comment-review-ownership-context` | does this comment belong to the line it sits on? |
| `comment-review:comment-review-block-context` | is every claim in this block true of the code it sits with? |
| `comment-review:comment-review-function-context` | does the commentary match what the function is FOR? |
| `comment-review:comment-review-module-context` | do the comments say this is ONE module? |

Each already carries its own angle and reads the shared brief itself. **You
supply the run context as a PACKET, and the packet is checked before anyone is
dispatched:**

```bash
python <skill>/scripts/run_context.py --template > <run-dir>/context.md
# fill every section, then:
python <skill>/scripts/run_context.py --check <run-dir>/context.md
```

It refuses a section that is absent **or present and blank** — *"no cap
published"* is an answer and must be written; a blank is a question nobody
asked. It then refuses the three answers a machine can settle: `LEVEL` must be
one of the four level names, and `CENSUS` and every `ANGLE FILES` entry must be
an **absolute path that exists**. ⚠ **The other eight are prose it cannot
check**, and passing says nothing about them. Hand every reviewer the one path.
Measured: a run dispatched without a style sheet introduced **14 en-GB
spellings** into a codebase whose identifiers are en-US, and every angle was
satisfied because nothing owned consistency.

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
it was true; another refuted it by grep. A single-angle run ratifies falsehoods.

**Re-review is normal.** An accreted block is layered — a live constraint, an origin story, a
correction to it, a review label — and peeling one reveals the next. Send a block back when
angles contradict, when a citation resolves to a *different* thing than the prose implies, or
when you cannot write the replacement text.

## Stage 5 — EDIT: one verdict, one FULL-LENGTH replacement

⚠⚠ **Run the join before you rule on anything.** It is the gate between MARK and
EDIT:

```bash
python <skill>/scripts/verdicts.py --census <census>.json --level <level> \
  --angles ownership-context,block-context,function-context,module-context \
  --repo . <one report file per angle>
```

⚠⚠ **NAME EACH REPORT FILE AFTER ITS ANGLE** — `ownership-context.md`, `block-context.md`,
`function-context.md`, `module-context.md`. The tool takes an angle from the
report's FILE STEM, and `--angles` compares against those stems, so a report
saved as `report1.md` is an angle nobody expected and every expected angle
reads as missing. Two files with the same stem are refused outright.

⚠ **Pass `--angles` every time, listing the angles this LEVEL ran.** Without it
a reviewer that never reported at all is invisible — "every angle" silently
means "every file I was handed", the easier version of the fabrication below.
The list above is `full`; at `fact-check` it is `ownership-context,block-context,function-context`.

It exits nonzero on a coverage gap, a citation that does not resolve, a quote
not found near its cited line, a verdict the level does not carry, an angle
that did not report, or a payload the verdict table requires and the record
lacks. It also names the blocks where `drop` meets `correct`/`patch` — **a
re-review, never a tie-break** — and prints which blocks STAND UNCHANGED under
the clean-arithmetic.

⚠ **`query` is the one verdict this citation check does not touch.** It carries
no `EVIDENCE` and no `QUOTE`, by construction — there is no line that settles a
claim the reviewer could not settle. Its PAYLOAD is checked instead: a `query`
naming no attempted check, or naming nothing that would settle the claim, is
the one the gate refuses.

⚠⚠ **A finding whose evidence does not resolve is not a finding — except a
`query`, which by construction carries none.** Measured: one graded run had
**fabricated 5 of its 7 reviewer reports** and did not notice until asked to
grade itself; self-certified `CONFIRMED` ran at **97% across 298 findings**.
**Never grade a review by reading its report.**

⚠⚠ **It catches a fabricated FINDING, never a fabricated CLEAN — and the clean
is the cheaper fabrication.** A report reading only `CLEAN 1-N` accounts for
every index, cites nothing, and exits 0 having read no file at all. Nothing
mechanical can separate that from a real pass, because a negative leaves no
artifact. **A green exit here is not evidence that anything was read.**

⚠ **The tool rules on ADMISSIBILITY, not on truth.** It cannot tell a correct
verdict from an incorrect one. Synthesis, and the order below, remain yours.

⚠ **A block that ends mid-clause is a finding, and its verdict is `correct`.** A run whose last
sentence stops mid-air — a severed trailing comment, a `move` that cut a sentence in half — is
neither checkable nor necessary, so the matrix routes it to `drop`, deleting the pointer instead
of repairing it. Restore the sentence.

⚠ **Two findings quoting the same sentence in different files are ONE finding.** A pass edits
where it is reading, fixes the copy in front of it, and manufactures a disagreement with the one
it never opened. Contradicting verdicts trigger a **re-review**, never a tie-break. The join
cannot see this for you — `contradictions()` keys on the census BLOCK index, and the same
sentence copied into two files is two different blocks it can never relate.

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
   sentence that is about to go. ⚠ `reanchor` does NOT belong here: it removes nothing, so it
   waits until the text is settled.
3. **`correct`** — fix truth, on what remains.
4. **`patch`** — fix wording, on text now known to be true. ⚠ Never before step 3.
5. **`add`** — insert at the stated anchors.
6. **`reanchor` and `split`** — re-attach what belongs beside different code, `reanchor` as one
   block and `split` as fragments. Last before `clean`, because the text must be final first.
7. **`clean`** — the null verdict. A block stands unchanged when **every angle that ran**
   returned `clean` and nothing else. ⚠ *Every angle that RAN*, not four: at `fact-check` only
   three run, and requiring four would make a block unblessable at that level.

⚠ **Load [`references/residue-check.md`](references/residue-check.md) before you write anything**
— the check is defined there, and this is the first stage that owes it. Stages 6 and 7b re-run
the same check against the same original; none of them may check against the previous edit.

Then emit the replacement and run the residue check on **the whole synthesised block once** —
not once per verdict. The check compares against the original, and the original was one block.

**Three rules that resolve the common collisions:**

- **Any `correct` outranks every `clean`.** Three angles finding nothing does not soften one
  angle finding a falsehood; they were not looking for the same thing.
- **`correct` and `patch` on the same sentence:** correct first, then re-read the patch against
  the corrected text. Usually it no longer applies.
- **`drop` against `correct` OR `patch` on the same sentence is a contradiction**, not a merge —
  one angle says it should not exist and another says it should exist and be fixed. Send it back
  for re-review. ⚠ **Do not let the synthesis order decide it.** Step 2 applies `drop` before
  step 3 and 4, so deletion would win silently — and if the dropped sentence carries a fact the
  survivor does not, that is a meaning change made on an absent author's behalf, which
  CONSERVATIVE ON MEANING forbids.

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

If there is a cap, and only once **every** block from stage 5 is CORRECT,
dispatch `comment-review:comment-review-compact` with the narrow input contract
below and the absolute path of [`references/compact.md`](references/compact.md).

⚠⚠ **This pass is not yours to run.** You wrote the text; an agent that never
saw the argument cannot preserve a sentence because it remembers writing it.
The narrow contract is only a safety property if the reader is different from
the writer. If the agent does not resolve, use the same fallback as 1.6 — a
general-purpose agent given the path — and **say in the report that you ran it
yourself** if you had to.

⚠ **Nothing is on disk yet.** This pass condenses the PROPOSED text, not a file — the author
has not ruled and nothing has been applied. That is the whole reason this stage sits here: what
you hand to stage 7a is what will be written.

⚠ **Do not fold it back into stage 5.** Compaction decisions depend on the final state of the
whole tree — a `move` that relocates prose between blocks, an owner that collapses N
restatements into one — and none of that is settled until every block is edited. `compact.md`
carries the argument and the per-block procedure.

## Stage 7a — APPROVAL: present the FINAL text, then stop

Grouped by verdict, most consequential first, in **five parts**
(`VERDICT / LOCATION / SUMMARY / FINDING / CHANGE`) — the reviewer record minus the fields only
the join reads — replacement text inline
for every `correct` / `patch` / `add`. State the **level** you ran, **raised / clean**, and the
longest block that will remain. **The proposal ends here** — nothing further is written until
the author rules.

⚠⚠ **What you show IS what gets written.** If stage 6 ran, show the COMPACTED text — never the
full-length version with a note that it will be shortened. The author rules once, quickly, and
on the assumption that the text in front of them is the text that lands.

**Hand back the STYLE SHEET**, updated with every decision this run made — the sheet is how the
next pass avoids re-deciding, and it is worthless if it stays in your head.

⚠ **Approval IS authorization.** "Yes", "do it", "continue" → load `references/apply.md` and
apply. Never-edit binds reviewers, not you acting on an approval.

## Stage 7b — APPROVAL: apply what was approved

On approval, load [`references/apply.md`](references/apply.md) and follow it. It carries the
residue check and the apply rails. Do not apply from memory.

⚠ **Stage 7b writes the APPROVED text verbatim.** It does not shorten, re-word or re-judge —
every one of those questions was settled upstream, and re-opening one here writes something
the author never saw.

## Stage 8 — REVIEW: the finished page

On completion of 7b, dispatch `comment-review:comment-review-review` with the
list of changed files, the style sheet, and the absolute path of
[`references/review.md`](references/review.md).

⚠⚠ **This pass is not yours to run either**, and for the same reason: a reader
who remembers intending each edit reads the page they meant to write. If the
agent does not resolve, fall back as at 1.6 and say so.

It is the only stage that reads the finished ARTIFACT against itself rather than prose against code,
so it is the only one that can see damage the editing caused.

⚠ **Fix only what THIS pass created.** A defect that predates the run is a finding for the next
one, reported separately.

## What this skill is not

`/simplify` reviews code structure and applies its fixes. `/code-review` hunts correctness
bugs. This reviews prose and writes nothing until the human approves. A defect noticed anyway
is **named and left**.
