---
name: comment-review
description: Review the comments and docstrings in the files a change touched, across four editorial roles -- ownership-context, block-context, function-context, module-context -- using parallel read-only subagents, and return each finding as verdict/location/summary/finding/change for the human to rule on. Use this whenever comments or documentation are the subject -- after finishing a task that added or edited commentary, when a file's comments have drifted from what the code now does, when someone says a comment is too long or out of date or "isn't this history", when reviewing a diff specifically for its prose rather than its logic, before a docs or comment burn-down, or when asked to check whether a module still reads as one module. Trigger on phrasings that never say "comment review" -- "these comments are getting out of hand", "does this docstring still match", "is this comment still true", "clean up the narration in this file", "why does this file need so much explaining" all mean run this. It is NOT /simplify (which reviews code structure) and NOT /code-review (which hunts correctness bugs). The REVIEWERS never edit; the task agent applies what the human approves, and every applied change passes a residue check against the original prose.
---

# comment-review

`/comment-review [cap] [target] [style]`

**An editorial board for the comments and docstrings a change touched.** Four editors read
the same manuscript in four editorial roles, a copy editor writes one set of edits, a condenser cuts
them to fit, the author approves **that** text, and the page is proofed. Structure and fact
first, then truth, then fit, then the page.

```
1 PROJECT      2 COLLATE   3 FIND       4 MARK   5 APPLY   6 COMPACT   7a PRESENT   8 REVIEW
  DETERMINATION            REFERENCES      ^       5b RE-    6b RE-        7b WRITE
                                           |       REVIEW    REVIEW            ^
                                           |         |         |               |
                                           +---------+---------+               |
                                             back to the roles that ruled      |
                                                             +---- no cap -----+
```

| # | stage | who acts | what exists at the end of it |
|---|---|---|---|
| 1 | **PROJECT DETERMINATION** | task agent | language, doc convention, cap and width, project rules, style sheet, and where the name corpus will come from |
| 2 | **COLLATE** | `census.py` | every place prose can sit gathered into one numbered tree, each comment run and docstring a node on it |
| 3 | **FIND REFERENCES** | `census.py` | every reference each node makes, resolved -- paths, symbols, counts |
| 4 | **MARK** | 4 reviewers, SERIAL | `ownership-context` alone at 4a; the other three at 4c against its resolved placement. Read-only, nothing written |
| 5 | **APPLY** | task agent | one verdict per paragraph and the **full-length** replacement text |
| 5b | **RE-REVIEW** | the roles that ruled | *is this what you meant?* -- answered on the JOINED paragraph |
| 6 | **COMPACT** | task agent | that text cut to the cap -- **skipped entirely if there is no cap** |
| 6b | **RE-REVIEW** | the roles that ruled | *is this still correct after my edits?* -- **stage 6's only reader** |
| 7a | **APPROVAL -- present** | task agent | the FINAL text in front of the author; **the run stops here** |
| 7b | **APPROVAL -- write** | **author**, then task agent | the approved text on disk, byte-for-byte as approved |
| 8 | **REVIEW** | `comment-review-review` | the finished page read as a reader would read it |

!! **5b and 6b are the same mechanism asking DIFFERENT questions**, and
[`references/re-review.md`](references/re-review.md) is the only file that defines either.
Neither runs on every paragraph: the set is the one the join prints as `RE-REVIEW`.

**This file is the task agent's.** Each reviewer is a named agent carrying its own editorial role and
reading [`references/reviewer-brief.md`](references/reviewer-brief.md) itself.
[`references/residue-check.md`](references/residue-check.md) loads at stage 5,
[`references/compact.md`](references/compact.md) at stage 6 -- **before** the author sees
anything -- [`references/write.md`](references/write.md) only after approval, and
[`references/review.md`](references/review.md) at stage 8.
[`references/re-review.md`](references/re-review.md) loads whenever a paragraph goes BACK to the
roles that ruled on it, which is after stage 5 and again after stage 6. **Nobody loads all of
it**, and no file restates another.

## The seven verdicts

Everything below this line uses these seven words. A reviewer emits them; **you receive one or
more per role per paragraph and must emit ONE replacement**, so what matters here is what each
obliges *you* to do.

!! **And you are expected to read the code around where that replacement lands, to verify it.**
A verdict rules on a SENTENCE; a paragraph is only its address, so a paragraph of six sentences can
arrive carrying six. Synthesising them into one comment without re-reading the code beside it is
how a run replaces an unfalsifiable claim with a checkably false one -- measured twice in the
pass stage 8 rolled back.

| verdict | the claim is | what you do with it |
|---|---|---|
| `clean` | nothing to report **from this role**, on a paragraph that role READ | nothing. Not a pass, and not a claim the paragraph is correct -- one role having no finding. A paragraph outside what the role reads is `query` |
| `query` | unsettled | resolve it or escalate it. It paragraphs every other verdict on that sentence |
| `drop` | true but not worth keeping | delete the sentence |
| `correct` | **FALSE** | apply the true/false pair. **Always before any `patch`** |
| `patch` | **TRUE**, badly worded | apply the rewrite |
| `add` | missing entirely | insert the text at the anchor named with it. Its `PARAGRAPH` is the empty INTERVAL the prose belongs in, so read it as being about that gap and not about a neighbour |
| `move` | true, but **it belongs somewhere else** | re-attach the paragraph, unchanged, at the destination carried with it -- another line in this file, another file, or out of the code entirely |

!! **A relocation is ONE judgment, and the DESTINATION carries the rest.** Whether the prose
belongs ten lines down, in another file, or out of the code altogether is payload -- not a
second verdict. The reason it belongs there goes in `REASON`, which every record already
has. **Availability keys on the destination, never on the verdict:** only a destination
OUTSIDE the code needs the tree 1.4 resolved, so only that case can be unavailable. A
relocation into tracked code needs nothing outside it and is never withheld.

A reviewer's verdict is only usable if it carries its payload. That contract is the
reviewers', and [`references/reviewer-brief.md`](references/reviewer-brief.md) holds it -- you
enforce it at stage 5 by refusing a verdict that arrives without one.

## Why the stages are in this order

**1-3 build the pCST** -- a *pseudo* Concrete Syntax Tree: every LINE of the files under
review classified, numbered in order, with every reference it makes already resolved. This
line is code, this PART of a line is code, this line is comment, this line is docstring.
**Pseudo** because a real CST would carry the names and the symbols precisely; this carries
only which lines are which, which is what a reviewer of COMMENTS needs. The places holding
nothing are on it too, because that is where prose is MISSING.

**MARK (4) is separate from APPLY (5)** because a reviewer that fixes what it finds has
destroyed the finding.

**APPLY (5) writes at FULL LENGTH.** Its only job is a
comment that is true, local and load-bearing. Length is not one of its questions, and a run
that returns long correct prose has succeeded.

!! **5b and 6b are what make every stage's output read by somebody who did not write it.** The
join reads MARK, the compact agent reads APPLY's text, the CODE CHECK reads WRITE, stage 8 reads
the finished page -- and 5b and 6b cover the two that write PROSE, which is the only thing here
no mechanical check can judge. ! APPLY still runs the residue check on its own output; 5b is a
second reader, not a replacement for that.

! **Measured 2026-08-17, with neither in the pipeline:** a run reached stage 8 with ruff clean,
the AST PROVEN and 1103 tests green, and stage 8 returned twelve findings -- two of them the
system replacing prose with something CHECKABLY FALSE -- and the whole pass was rolled back.

! **The filer is the only participant who can answer.** Stage 5 turns several verdicts into one
sentence; when it misreads one, no later reader can tell, because none of them saw the finding.
That is why the question goes back to the role rather than to a fresh reader, and why it is
narrow -- *did your edit survive, is it still correct there, do the other edits break it* --
rather than *is this OK*, which a role will wave through.

**COMPACT (6) is a separate pass over that text.** It comes AFTER edit and BEFORE approval, and
two constraints pin it into exactly that slot:

- **After APPLY**, because prose can only be shortened without losing information once it is
  true. Shortening first is how a false sentence survives -- it gets *trimmed around* rather
  than checked, arriving shorter, cleaner, in-cap and strictly harder to falsify.
- !! **Before APPROVAL, because the author must rule on the text that will actually be
  written.** Showing a full-length comment, getting a yes, and then writing a compacted one
  means the author approved something that never reached the file.

**APPROVAL (7) presents the FINAL text and STOPS.** It takes the author's ruling, and applies
that text only if it was approved.

**REVIEW (8) is the only stage that reads the artifact against itself.** Everything before it
compares prose to code; this asks whether the finished page still reads.

## Three roles

**The HUMAN is the AUTHOR, and is absent.** They approve almost everything, quickly,
unaudited -- a direction, not a diff. **So every proposal must be safe to approve blindly.**
Their disagreement is valuable; it is not a safety mechanism and must never be used as one.

!! **That makes this an editorial board with an absentee author, and one principle follows:
CONSERVATIVE ON MEANING, FREE ON FORM.** An editor rules on form; the author rules on what a
sentence claims. With the author not reading, you may fix wording, placement and length on your
own judgement -- but every change to what a sentence CLAIMS needs evidence in hand, or it is a
`query`. That is why `correct` must carry the line that settles the claim, and `patch` need not.

**The TASK AGENT -- you.** Run stages 1-3, launch the reviewers, rule, present, and after
approval apply. You are the only participant that writes, and only after approval. Reach
every paragraph, rule on sentences, **write the replacement text yourself**, and verify what you
write. *"Compact + correct"* is an instruction to somebody else, not the text.

**The REVIEWERS** are read-only, one editorial role each, and never see this file.

## Arguments

- **`cap`** -- integer, optional; max lines for one `#` run. **This skill has no cap of its
  own** and must not invent one. None given and none published -> **no cap**.
- **`target`** -- a path; **replaces** the diff scope, never intersects it.
- **`style`** -- a path to a style sheet from a previous run. Optional; see 1.5.

!! **Every verdict is available on every run.**

!! **ONE ROLE IS REQUIRED AND THREE ARE OPTIONAL.** `ownership-context` runs at 4a, alone and
first, and is never dropped; `block-context`, `function-context` and `module-context` run at 4c
against its resolved placement. Each of the three checks a claim against the code at its own
scope, so a run may omit any of them and still be a review -- but a claim attached to the WRONG
scope is measured against the wrong code and `correct`ed into a falsehood, which none of the
three can notice. **Say in the proposal which roles ran.**

!! **THE CAP IS APPLIED IN STAGE 6 AND NOWHERE ELSE** -- never while text is being written,
and **never passed to a reviewer** -- it is not a section of the stage-4 packet, and neither is
`WIDTH`. Length is not an editorial role; the reason is in the brief.

## Stage 1 -- PROJECT DETERMINATION: ground truth

!! **THE FLOOR IS A LOCAL GIT REPOSITORY, and that is the ONLY thing a rule here may assume.**
`git ls-files` answers, and `git show <ref>:<path>` answers for a ref that exists. **Everything
else is checked, not assumed** -- an upstream, a merge base, a clean tree, a cwd at the repo
root. Pass `--repo` to every script rather than relying on the working directory.

!! **Record the PRE-EDIT REF now, and carry it to stages 6 and 7b.** It is `HEAD` when the tree
holds no uncommitted change to the files in scope, and `git stash create` otherwise -- which
writes a commit object for the current state and leaves the working tree untouched. **It is not
the merge base**, and the two answer different questions: the merge base says what the BRANCH
changed, the pre-edit ref says what THIS RUN changed. Stage 6 reads the ORIGINAL prose from it
and stage 7b proves against it.

**1.1 Scope from the MERGE BASE** -- `git merge-base HEAD <upstream>`, then
`git diff --name-only "$base"..HEAD`. Never `A...B` between two tips, never a `HEAD~1`
fallback; both silently narrow. Add `git diff --name-only HEAD` if dirty.

! **No upstream, no merge base, detached HEAD -- then there is no diff scope, and you say so
rather than inventing one.** A repo with no remote is inside the floor. Scope from `target`
instead, which REPLACES the diff scope and needs no base; failing that, from
`git diff --name-only HEAD` alone. **Say in the PROPOSAL which of the three you used**, because
the three cover different files and a reader cannot tell them apart from the findings.

**1.2 Find the repo's published cap and line WIDTH, and read HOW each counts** -- matching the
number while counting differently produces a file that claims to comply and does not.

! **Two separate questions, and either may be absent.** A cap bounds the LINES in one `#` run;
a width bounds the CHARACTERS in one line, and each is published where it is published -- a
contributing guide, `.editorconfig`, a formatter config. **Record what the repo published and
say which** -- the census takes neither number, so a cap you invented would reach stage 6 as a
project fact nobody published.

! **Then check the guard EXISTS, and if it does not, say what follows.** A convention citing
an absent test publishes a rule enforced by nothing. **Proceed** -- an unenforced rule is still
the repo's rule and you have no standing to overrule it -- but change two things and say so in
the proposal:

- **Treat every citation in scope as unverified**, not as evidence. The prose was written
  against a checker that never ran.
- **Expect a high finding rate and do not read it as a defective codebase.** Prose no guard has
  ever measured is defective at a high rate by construction, and that fact belongs in the
  report as a finding about the REPO, above any individual paragraph.

! **Ask which markers the repo exempts from the cap**, and say so in the proposal. `census.py`
exempts `TODO`, `FIXME`, `HACK`, `XXX` and `BUG` and takes no flag for any other set, so a repo
that exempts a different one is a fact you REPORT, not one you can pass down.

**1.3 MEASURE the repo's documentation formats. Do not assume one.** Read the docstrings that
are there and record what they actually do, separately for each of:

- **module** docstrings -- the shape this repo puts at the top of a file
- **function and method** docstrings -- google, numpy, sphinx, or a house shape
- **comment** format -- recorded SEPARATELY, and only where the repo is consistent about one

! **Write a TEMPLATE for each, from what is in the tree.** A template is a shape written out
with its slots, not a shape NAMED -- naming a standard the repo does not follow is how a correct
sentence lands in the wrong format. The dispatch packet is a template too.

The templates belong in the STYLE SHEET (1.5), which is what carries them to the reviewers, to
stage 5 and to stage 6.

**1.4 Find the destination tree for prose that leaves the code**, and decide NOW what happens
if there is none. WHERE a paragraph belongs is the reviewers' to say; whether a tree outside the
code exists to receive it is a fact about the repo, and only you can settle it before they run.
A verdict pointing at a tree that does not exist is not a verdict.

!! **The answer may be PER PATH, and a repo that says otherwise is rare.** A convention like
`docs/{pkg}/{module}.md` is available exactly where that tree was actually built -- measured on
one repo, present for `tests/**` and absent for the production package, though the convention
document cited the same path for both. **Write the split into the packet**, one line per scope,
rather than picking the stricter answer for everything: told UNAVAILABLE everywhere, a reviewer
withholds a legal `move` on the half that has a destination; told the tree everywhere, it emits
verdicts pointing at a tree that is not there.

!! **If the destination tree is absent, only `move` OUT OF THE CODE is unavailable -- and
those paragraphs become `clean`, never `drop`. A `move` to a destination inside tracked code is
unaffected and always available.** Say so at stage 1, and again in the proposal; offer the human the one-line alternative
(create the tree, or name another destination). This matters because the matrix routes
*not-checkable + necessary* to `move`, and a repo that stages prose usually also rules that
prose is MOVED, never deleted -- so with no destination those two rules leave the paragraph with no
legal verdict at all -- *the matrix* is the checkable/necessary table in the reviewers' brief, and
it is named here only to explain the consequence. **Keeping true prose in place costs a cap
violation you can report. Dropping it costs the only copy.**

**1.5 Read the STYLE SHEET if one exists** (`style` argument), and start one if not.

This is the copy-editor's artifact and it is the only thing in this skill that PERSISTS between
runs. It records decisions made for THIS codebase so the next pass does not relitigate them:
the dialect its identifiers use, how domain terms are capitalised, the house citation form, the
**documentation TEMPLATES** measured at **1.3** -- module docstring, function docstring, and the
comment format where there is one -- terms of art with a fixed meaning, and any ruling the human
made last time.

!! **Without it, a pass drifts the prose while fixing it.** A run with no sheet wrote *"the
event's colour"* on a function returning a `colorId`. Every role was satisfied; nothing owned
consistency. There
is no fifth reviewer for this, deliberately -- consistency is enforced at WRITE, against the
sheet, not by another visitor over the tree.

! **It is binding, not advisory.** An edit that departs from the sheet is out of scope in the
same way a code change is. If the sheet is wrong, that is a `query`, not a licence.

**1.6 Verify the four reviewer agents are DISPATCHABLE**, before anything else depends on
them. They are plugin agents and their names are NAMESPACED -- `comment-review:comment-review-*`
-- and they resolve only if the plugin was installed **before this session started**.

!! **If they do not resolve, say so at stage 1 and say what you will do instead.** The failure
arrives at stage 4 as `Agent type 'comment-review-ownership-context' not found`, and improvising
a fallback silently is the reflex. The sanctioned fallback is **four general-purpose agents given the REVIEWER FILES
paths from the packet** -- never the role text pasted into a prompt, which goes
stale the moment a role file is edited. Because the packet already carries those
absolute paths, the fallback is a substitution rather than an improvisation.

**1.7 Probe for a LANGUAGE SERVER, once per language in scope.** One `LSP documentSymbol`
call against a representative file of each. Record which answered -- that is a fact about
this run and it belongs in the proposal.

The server is the user's, not ours: someone reviewing Rust already runs rust-analyzer, so
this is structure available for free that `census.py` cannot ship. It buys exactly two
things, and neither is the census:

| | with a server | without |
|---|---|---|
| **a paragraph's ANCHOR** | `documentSymbol` -> the declaration on the line after the comment run ends | nothing resolves it |
| **is a name alive** | `workspaceSymbol` / `findReferences`, in **any** language | the Python AST corpus only |

!! **LSP RETURNS NO COMMENTS, so it can never replace `census.py`.** The nine operations
exposed -- definition, references, hover, documentSymbol, workspaceSymbol, implementation and
the call-hierarchy three -- return no prose at all; `semanticTokens` and `foldingRange`, the
two that would, are not among them. On a Go file a server reports `func F` at line 4 while
nothing has said there is a comment at line 2 to attach to it. **A paragraph must be FOUND before
anything can anchor it, so stages 2-3 always run.**

! **Absence is reported, never inferred, and there are THREE states -- not two.**

| state | how you learn it | what to report |
| --- | --- | --- |
| a server answered | `documentSymbol` returns symbols | the language, and use it at 1.8 |
| no server for this language | `No LSP server available for file type: .ts` | that language has none |
| **no LSP tool at all** | the tool is absent from the registry -- there is no call to issue | **no probe was possible** |

!! **The third is not the second.** With no LSP tool the probe cannot be made, so "no server
answered" would be an inference, which the rule above forbids. Say a probe was impossible.
This is additive: with a server you gain anchors and cross-language liveness, without one you lose
nothing you had. What you may not do is let a run that had no server read like one that did.

**1.8 Decide where the name corpus comes from** -- every liveness check downstream depends on
it. This substep CHOOSES the source; the corpus itself does not exist until stage 3, because
`census.py` builds it. Do not try to produce it here.

- a server answered at 1.7 -> **`workspaceSymbol`**, which covers every language at once
- no server -> the AST corpus `census.py` emits at stage 3, Python only
- both -> combine them, and say so

From the AST never raw text (text contains the comments being checked, so everything passes);
skip directories holding `pyvenv.cfg`; never harvest string constants from tests
(`assert "x" not in y` makes a dead name read alive); exclude `.md`/`.txt`; resolve a dotted
name on its **head** segment only.

## Stages 2-3 -- COLLATE, then FIND REFERENCES

! `<skill>` below is the directory holding this SKILL.md -- take it from the absolute path you
were given. A relative one resolves against whatever directory you are in, which is not
guaranteed to be the skill's.

```bash
python <skill>/scripts/census.py --repo . --out <run-dir>/census.txt <paths...>
python <skill>/scripts/census.py --json --repo . --out <run-dir>/census.json <paths...>
python <skill>/scripts/census.py --repo . --filtered --out <run-dir>/dispatch.txt <paths...>
```

!! **THREE FILES, AND THE THIRD IS THE ONE A REVIEWER IS HANDED.** `--filtered` prints the
paragraphs holding prose and collapses each run of places holding none into one line --
`227-234  @c1..b7  122-129  no-prose  0L  2-intervals, 6-margins`. **Re-measured 2026-08-19 over
6,828 paragraphs: 397,685 bytes to 159,316, and every reviewer gets an identical copy, so a
four-role run saves 953,476.**

!! **IT IS A PROJECTION, NEVER A RENUMBERING.** Every paragraph keeps the ADDRESS it holds in the
FULL census, because that address is what the join resolves and what a record cites. ! The index
in the first column is a READING AID for a human scanning the listing, and nothing cites it: it
is a position in one census, and the galley is censused again for round 2. The full census
stays on disk and is what stages 5 and 7b read; only the copy pasted into a reviewer's prompt is
narrowed.

!! **DO NOT SHIP THE FILTER WITHOUT STAGE 4's LOOKUP.** A reviewer handed the filtered census
can still see every gap, but the intervals inside a run are no longer individually numbered in
front of it -- so a reviewer needing to place prose at one of them has no address to cite unless
the packet tells it `locator.py` exists. Filtering without that is worse than not filtering.

### What a place is CALLED

!! **AN ADDRESS IS WHAT EVERY RECORD CITES**, and it is the only name that survives this run's own
edits -- a prose edit moves the line numbers below it, and an address counts against the CODE.

```
pkg:core.py@a5    a DECLARATION's documentation
pkg:core.py@b3    a GAP -- or, at `b0`, the file's own front matter
pkg:core.py@c3    the room BESIDE a line of code
```

The path is flattened on `:`, a character no path may hold, so `a/b.py` and `a.b.py` cannot
collide. `docs/addressing.md` is the settled definition.

!! **YOU CANNOT WORK A FOLIO OUT. ASK.** The three series are counted by three separate
foliators, and no number in one tells you a number in another -- nor does a line's position tell
you either.

```bash
python <skill>/scripts/addresser.py --census <FULL CENSUS> --anchor LINE --series a|b|c
python <skill>/scripts/addresser.py --census <CENSUS> --resolve <ADDRESS>
python <skill>/scripts/locator.py --census <FULL CENSUS> --at path:LINE
```

! **An anchor answers with SEVERAL places and that is not an error** -- an anchor has many
addresses and an address has one anchor, so two identical lines of code are two anchors spelled
alike. Choose by ADDRESS.

!! **`--out`, never a shell redirect.** A worktree-isolated session REFUSES a command carrying
one -- *"too complex to verify that it stays inside the worktree"* -- and the JSON census is what
stage 5 parses, so a redirect makes the run impossible there rather than merely awkward.

! **The census takes no cap and no width.** The cap belongs to stage 6, and the reviewers are
handed this file -- printing an over-cap count here puts it in front of the four roles that must
never see it.

!! **TWO census files, and the JSON one is not optional.** The reviewers are handed the TEXT
census; **the stage-5 join reads the JSON census and parses it as JSON**, so a run that wrote
only the text one fails at stage 5 with `CANNOT PARSE ... as JSON`.

It emits the numbered tree -- `N  file:start-end  kind  lines  annotations  (anchor)` -- with each
node's references already resolved, and it prints the tier counts for the run.

!! **Most of that tree is `interval` paragraphs, and nobody owes them a record.** Every gap
between two lines of code is numbered, empty ones included, because an `add` is a finding about
prose that is MISSING and the record needs an ADDRESS to carry it. They are ADDRESSABLE,
not ACCOUNTABLE: `verdicts.py` computes coverage over the paragraphs that hold prose and says both
counts on its first line. Re-measured 2026-08-19: `census.py` over itself is 1,607 paragraphs, 118 of them prose.

! Those tier counts are
AGGREGATED across files, not per file -- on a polyglot run you cannot tell which file reached
which tier, which is exactly when it matters. Run it; do not
re-derive its output by hand.

! **Give both files a path unique to THIS run**, and hand the reviewers the text one. Two
concurrent reviews sharing one scratch filename overwrite each other between writing and
reading, and nothing downstream can tell.

**A suffix the census has no record for is named, and the census EXITS NONZERO** -- every file
handed in is censused or the run stops, so a file that reaches a reviewer is reviewed like any
other whatever its tier. `python <skill>/scripts/census.py --languages` lists what it knows.

! **It builds the tree at the TIER available for each file's language.** Both tiers find the
same paragraphs and differ only in what else they can say:

| tier | needs | answers | cannot answer |
|---|---|---|---|
| `tokenized` | a lexer + AST (Python: the stdlib) | paragraphs, annotations, **docstring** anchors | a **comment's** anchor |
| `lexical` | a comment-syntax record, nothing else | paragraphs, annotations | any anchor; a marker inside an exotic string |

!! **Carry the census's CANDIDATE line into the proposal.** It prints that no comment
carries an anchor at either tier, so every PLACEMENT verdict rests on a reviewer READING the
file -- a judgement no field records and nothing downstream can check.

**What it guarantees, and why the reviewers depend on it.** A paragraph is bounded by CODE, not
blank lines (else 9 lines becomes 6+3 and passes). Its comment run is matched as ONE joined
string,
because prose wraps and a line-local match reports the fragment instead of the claim. Nothing
is truncated -- a partial list cannot be used to skip anything. Anything it could not read is
**named**, because a hole in the name corpus turns every symbol defined only there into a
false obituary.

### What counts as ONE paragraph

! **A COMMENT RUN is the prose INSIDE a paragraph** -- the contiguous comment lines between the
two code lines that bound it. It is always written with its qualifier, because `run` alone
means one invocation of this skill.

!! **A paragraph is the interval between two lines of CODE.** The lines of code above and below
define it; what is written between them does not. Only code is a boundary -- not a blank line,
not a work marker, not a change of subject. Everything between one code line and the next is
one paragraph, however much or little that is.

```python
variable_a = 1234

# comment_block starts
# TODO: important thing in it
# comment_block continues
# comment_block ends
result = foo_bar(variable_a)
```

**One paragraph**, bounded by `variable_a = 1234` and `result = ...`. Four physical comment lines,
**three** counted: the marker line is free. The blank is inside the paragraph and is charged
nothing. ! The example carries no inline annotations on purpose -- a `#` note explaining the
example would be a comment sitting inside the very interval it describes, and would be counted.

Three rules people state separately all follow from the one definition, and getting any of them
wrong changes what the reviewers see:

- **Only code ends a paragraph.** A blank line does not. Split on blanks and a 9-line paragraph reads
  as `6 + 3` and passes a cap of 6 -- the quickest way to fake compliance.
- **A work marker does not split a paragraph** (`TODO` `FIXME` `HACK` `XXX` `BUG`, or whatever
  1.2 found this repo exempts) -- otherwise a paragraph could be made compliant by adding one.
- **A COMMENT paragraph belongs to the code BELOW it**, which is what makes it answerable at all:
  the paragraph above is about `result`, and a finding says so by naming that anchor. ! **A
  DOCSTRING belongs to the declaration it sits INSIDE** -- the `def` or `class` above it, which
  is where the census reads its anchor from.
- **A trailing comment is its own paragraph**, one line, anchored to the code on that line.

Annotations, and what resolving each one means:

| annotation | resolved by |
|---|---|
| `cites-a-path` | tracked in the tree? ! present-but-untracked is **unverifiable**, not dangling |
| `names-a-symbol` | `workspaceSymbol` where 1.7 found a server, else the AST corpus (head segment; `foo()` normalised) |
| `counted` | re-derive the POPULATION, then count it |
| `coverage-claim` | does the guard exist -- and **can it fail**? |
| `forbids-a-literal` | grep the forbidden literal across that file |
| `repeated-literal` | where else is this number written? one source at both ends of a round trip? |
| `narrative-in-docstring` | is the date, review label or *"used to"* a claim about HISTORY rather than about the code now? |
| `continues-a-trailing-comment` | read it WITH the trailing comment above it -- the split is the census's, so a mid-clause ending here is not a `correct` |

!! **Every row is a question a reviewer must answer, and none of them is answered by the
census.** It says a path is cited; whether the claim about it is true is the reviewer's, and
`reviewer-brief.md` holds that contract.

### Enrich the census with the language server, where 1.7 found one

The census names every paragraph; the server can say what a paragraph BELONGS to. Do this once, here,
and attach the answer to the node -- not in stage 4, where four reviewers would each re-derive
it and could disagree.

- **Anchor** -- `documentSymbol` on each file in scope returns every declaration and its line.
  A run ending at line N-1 is ANCHORED to the declaration at line N. Attach it; the census
  prints anchors it has.
- **Liveness** -- for each `names-a-symbol` candidate, `workspaceSymbol` answers whether the
  name exists at all, in any language in the workspace. `findReferences` answers whether
  anything uses it, which is the stronger claim a comment usually makes.

! **A server does not settle a claim, it settles a FACT.** "This name exists" is not "this
comment is true" -- the annotation stays a CANDIDATE a reviewer confirms, exactly as when the AST
answered it. What changes is the cost of checking, not who decides.

!! **Say which servers answered, per language, in the proposal.** Availability is a
property of the machine, so two runs over identical input can resolve different sets. A run
that had no server must not read like one that did -- and any measurement taken with a server
is not comparable to one taken without.

! **Scope by SUBJECT, not by file extension**, and resolve it with the tool
rather than from memory -- this is the INBOUND half of stage 3:

```bash
python <skill>/scripts/referrers.py --repo . <paths under review...>
```

It prints every tracked file that NAMES one of them -- by path, by stem, or by a
public top-level definition. Those files are the **REFERENCE ONLY** list you hand
the reviewers at stage 4; a config, data or documentation file carrying prose that
justifies a value is a node like any other, and a file left out of scope carries the same
defects as the code -- including rewrites the pass already applied in a `.py` file.

!! **This runs in `target` mode too.** A `target` run has no diff to widen from,
which is exactly why the memory-based rule it replaces could not fire there --
the invocation most likely to be typed by hand was the one with no backlink
discovery at all.

Report what the tool prints: `N files, N paragraphs`, the per-tier counts, and any paragraph whose
KIND it could not resolve.

## Stage 4 -- MARK: ownership first, then the other three

!! **IT IS SERIAL, IN TWO ROUNDS, AND THE ORDER IS THE POINT.**

| | who | why |
|---|---|---|
| **4a** | `comment-review:comment-review-ownership-context`, ALONE | it settles WHERE each paragraph belongs |
| **4c** | the other three, in ONE message | they measure a claim against the code at their own scope |

**One role REQUIRED, three OPTIONAL.** Roy, 2026-08-19: *"ownership-context has to run, else
verdicts are made on statements that are not in the 'right' place. The other three are optional
and only run after ownership-context has had its say."*

! **A claim attached to the wrong scope is measured against the wrong code**, and the other three
have no way to notice: `block-context` checks a claim against the code it sits with, so a
misfiled note is verified against the passage it was misfiled into and stamped TRUE. The trade
reached this long before this system measured it -- a house places the notes before the checker
works the copy.

| agent | asks |
|---|---|
| `comment-review:comment-review-ownership-context` | does this comment belong to the ANCHOR it sits on? |
| `comment-review:comment-review-block-context` | is every claim in this paragraph true of the code it sits with? |
| `comment-review:comment-review-function-context` | does the commentary match what the function is FOR? |
| `comment-review:comment-review-module-context` | do the comments say this is ONE module? |

!! **THE THREE AT 4c GO IN ONE MESSAGE, AND THAT IS WHAT PROTECTS INDEPENDENCE -- not speed.**
Overlap between roles is signal ONLY if no role saw another's findings: two roles agreeing is
corroboration when they read alone and nothing when the second read the first. A second
dispatch runs concurrently too; what it risks is a prompt carrying what the first pair
returned. **If you dispatch those three in more than one message, say so in the proposal** --
the run is still usable, and a reader has to know the overlap was not blind.

! **4a is NOT an exception to that.** `ownership-context` reads before any of the three exist,
so nothing it saw can have come from them; what the three receive is its resolved PLACEMENT, not
its findings.

!! **RUNNING THE THREE WITHOUT 4a IS NOT A REDUCED RUN, IT IS AN UNSOUND ONE**, and the report
must say which roles ran either way. Dropping any of the three narrows what was asked; dropping
`ownership-context` leaves the rest resting on an assumption nobody made.

Each already carries its own editorial role.

!! **Put the BRIEF and each agent's VOCABULARY in its prompt, verbatim.** Paste
[`references/reviewer-brief.md`](references/reviewer-brief.md) whole -- it is the same text for
all four -- then one command per agent, pasted as it comes:

```bash
python <skill>/scripts/vocabulary.py --reviewer ownership-context
```

`--roles` lists the six that have one. ! Do not summarise it, do not trim it to the terms you
think a file uses, and do not tell an agent where the vocabulary lives -- it is given the words,
not a path to go reading.

!! **Run it and paste the OUTPUT. Never stage it through a file.** A redirect puts an artifact
between the command and the prompt, and the artifact can be from the previous run -- which is the
failure you will not see, because **a vocabulary one version stale reads perfectly plausible**.
Measured 2026-08-17: a run redirected all four to disk, the plugin was updated mid-session, and
the files on disk were then a version behind the script that had just been fixed. Nothing about
them looked wrong. ! This is the opposite instruction from the CENSUS, which is a file BY
DESIGN and needs a path unique to this run -- the census is too large to paste and is read once,
where the vocabulary is small and is pasted four times.

!! **`CENSUS` POINTS AT THE FILTERED FILE**, `dispatch.txt` from stage 2 -- not the full census
and not the JSON. That is the copy a reviewer reads, and it is four copies of it per run. The
full census stays on disk for stages 5 and 7b, which resolve every address a reviewer cites
against it.

**You also supply the run context as a PACKET, and the packet is checked before anyone is
dispatched:**

```bash
python <skill>/scripts/run_context.py --template > <run-dir>/context.md
# fill every section, then:
python <skill>/scripts/run_context.py --check <run-dir>/context.md
```

It refuses a section that is absent **or present and blank** -- a published
non-answer such as *"UNAVAILABLE"* is an answer and must be written; a blank is
refused. It then refuses the three answers a machine can settle: `REPO ROOT`, `CENSUS` and
every `REVIEWER FILES` entry must be an **absolute path that exists**.
! **The rest are prose it cannot check**, and passing says nothing about them. Hand every
reviewer the one path. Dispatched without a style sheet, a run drifts the dialect while fixing
the prose, and every role is satisfied because nothing owns consistency.

!! **`REPO ROOT` is what every other path resolves against.** The census, `FILES UNDER
REVIEW` and every citation a reviewer writes are repo-relative, and a reviewer handed no root
is guessing at a working directory.

!! **Withhold every TASK AGENT ONLY section when you paste the packet.** `REVIEWER FILES` is
one: it names paths inside the installed plugin, which is not the tree under review, and the
template marks it so the withholding is visible while you fill it. It is checked here because
it is YOURS -- the 1.6 fallback reads it.

! **The templates go to the reviewers too, and stages 5 and 6 match their output against them.**
A docstring's format decides which of its lines are structural and which are prose, so a
reviewer that does not know the format cannot tell what a paragraph contains. And a correct
sentence in the wrong format is work the human has to redo by hand.

!! **An agent is GIVEN what it needs, and is never sent looking.** A path into the installed
plugin is an invitation to read its neighbours and act on what it finds there. Nothing a
reviewer needs arrives as a path: the brief and the vocabulary are in the prompt, the census
and the file lists come through the packet.

! **REFERENCE ONLY is a SELECTION, not a leftover.** Name the files that settle claims code
cannot: the repo's **decision record** (*"ruled"*, *"rejected"*, *"deferred"* have no code
oracle), any **authority document** holding dated facts, and -- where the repo stages prose out
of code -- the **extracted/mirror copy** of the files under review. Measured: an invented
ruling with zero entries in the record on its cited date; a retracted fact surviving in two
docstrings and one live constant; and a mirror tree that held the CORRECT text while the code
was backwards. The code still settles code claims -- a
disagreement with the mirror is itself a finding.

**And you SEED each reviewer's report before dispatching it.** One file per role, named for
the role, with a slot already laid down for every prose paragraph:

```bash
for role in ownership-context block-context function-context module-context; do
  python <skill>/scripts/record.py --seed --census <run-dir>/census.json \
    --reviewer "$role" --out <run-dir>/"$role".json
done
```

!! **A REVIEWER FILLS A TEMPLATE; IT DOES NOT COMPOSE A DOCUMENT.** Each slot arrives carrying
the `address` and the `anchor`, and the reviewer sets only the five that are its
own. **Hand each agent the absolute path to ITS file and no other**, and tell it to edit that
file in place. It is the one path a reviewer is given, and the exception to *given, never sent
looking* above: it is being given a form, not a tree.

! **The seeded file is why coverage is structural.** A paragraph nobody ruled on is a slot with a
null verdict, not an address missing from a list, so nothing downstream reconciles what was
expected against what arrived.

! **A reviewer may APPEND a record for any census ADDRESS, and must for an `add`** -- an `add`
cites the empty INTERVAL prose is missing from, and intervals get no seeded slot. The brief
tells the reviewer this; you need it to read the count `--check` prints, which counts slots
and not findings.

**Check each file when the agent returns**, before the join:

```bash
python <skill>/scripts/record.py --check <run-dir>/<role>.json --census <run-dir>/census.json
```

! It separates INCOMPLETE from MALFORMED and exits differently on each: a reviewer part-way
through its paragraphs is not in error, a record whose shape is wrong is. **Send a malformed file
back to its own reviewer rather than repairing it** -- a record you fixed is a finding you
authored.

Overlap between roles is **signal**: a claim one affirms and another refutes goes back for
re-review, never to a tie-break. ! **A single-role run ratifies falsehoods** -- one role reading
a false absence claim writes that it is true, where another refutes it by grep.

**Re-review is normal.** An accreted paragraph is layered -- a live constraint, an origin story, a
correction to it, a review label -- and peeling one reveals the next. Send a paragraph back when
roles contradict, when a citation resolves to a *different* thing than the prose implies, or
when you cannot write the replacement text.

!! **[`references/re-review.md`](references/re-review.md) is what a re-review IS**, and it is
the only file that says. Load it before sending anything back: it carries what the role is
given, the three questions it answers about the JOINED paragraph, the return shape, the channel,
and when the rounds stop. ! The subject is never the finding -- *"do you stand by your verdict"*
returns the verdict already filed.

!! **WHICH PARAGRAPHS go back: every paragraph carrying a CONFLICTING mark, and `query` conflicts with
nothing.** Ruled 2026-08-17. That is exactly the set `verdicts.py` prints as `RE-REVIEW`, so
read the tool's list rather than deriving your own.

!! **A CONFLICT IS ON ONE SENTENCE. Two marks on two different sentences COMPOSE and are not a
conflict**, however much they share a paragraph. Ruled 2026-08-17. `contradictions()` already keys
on the edited SPAN rather than the address for exactly this reason -- and it was paid for:
measured on a live run, one of eight flagged collisions was two roles ruling on two different
clauses of one docstring, and a whole re-review round went on establishing that. A paragraph of six
sentences can carry six verdicts and still hold no conflict at all.

! `query` sets neither trait and can never enter the set; `move` is absent by ruling, because
relocation and a truth fix compose.

! **One case is DELIBERATELY wider than the sentence rule**: where the edited span cannot be
computed at all, the paragraph is flagged rather than passed. Silence there would hide a real
collision behind an unreadable record, so the set is *conflicts, plus what could not be read*.

! **This is the NARROW model, taken on cost, and it is marked *for now*.** The alternative is
every paragraph two or more roles filed on -- the *"reviewers that had comments"* model. Measured on
a live run: **51 of 150 paragraphs** had two or more roles converge against **8** flagged as
conflicts. ! The two numbers are not the same measurement: 51 counts roles converging on a
PARAGRAPH, and the 8 already applies the sentence rule, so widening would cost less than six-fold
but more than nothing.

## Stage 5 -- APPLY: one verdict, one FULL-LENGTH replacement

!! **Run THE JOIN before you rule on anything** -- `verdicts.py`, which reads every
reviewer's report against the census and against the others', and refuses what it cannot
verify. It is the gate between MARK and APPLY:

```bash
python <skill>/scripts/verdicts.py --census <census>.json \
  --reviewers ownership-context,block-context,function-context,module-context \
  --repo . <one report file per role>
```

!! **NAME EACH REPORT FILE AFTER ITS ROLE** -- `ownership-context.json`,
`block-context.json`, `function-context.json`, `module-context.json`, which is what stage 4
seeded. The tool takes the role name from the report's FILE STEM, and `--reviewers` compares
against those stems, so a report saved as `report1.json` is a role nobody expected and every
expected role reads as missing. Two files with the same stem are refused outright.

! **The SUFFIX chooses the reader**, and only `.json` is the shipped shape. Anything else is
read by the DEPRECATED 0.2.x text parser, which is kept so a run already captured on disk stays
usable -- `record.py --convert` carries one forward. A report saved as `.md` today is not
refused; it is read by the parser whose boundary guesses this format exists to retire.

! **Pass `--reviewers` every time, listing all four roles.** Without it a
reviewer that never reported at all is invisible -- "every reviewer" silently
means "every file I was handed", the easier version of the fabrication below.

It exits nonzero on a coverage gap, a citation that does not resolve, a quote
not found near its cited line, a verdict outside the seven, a role
that did not report, or a payload the verdict table requires and the record
lacks. It also names the paragraphs where `drop` meets `correct`/`patch` -- **a
re-review, never a tie-break** -- and the paragraphs where `move` meets either, since a claim
ruled on at the wrong anchor was measured against the wrong code. !! **It then prints your
WORK LIST: every paragraph needing a ruling, with the verdicts held on it.** That is the grouping
stage 5 works from -- read it rather than rebuilding it from the report files.

! **It reports THREE states, not two.** A paragraph every role returned `clean` on STANDS. A paragraph
carrying a substantive verdict NEEDS A RULING. A paragraph covered only by `clean` and
`query -- outside my role` is neither: nothing is asked of you, and no role certified it either,
because a role returns `query` rather than `clean` on a paragraph it never read. Measured: on one
run 1159 paragraphs read as work when 76 carried a verdict.

! **`query` is checked TWICE, and carries evidence like every other verdict.** Its citations
resolve as any other's do; on top of that its payload must NAME which of the brief's three
shapes it is -- in the brief's own words -- and name the check it attempted. A `query` that
names no shape is refused, and so is one that names no check.

!! **A finding whose evidence does not resolve is not a finding.** Only `clean`
is exempt, because it cites no claim. **Never grade a review by reading its
report** -- self-reported confidence has been measured not to discriminate a real
finding from a fabricated one.

!! **It catches a fabricated FINDING, never a fabricated CLEAN -- and the clean
is the easier fabrication.** A report reading only `CLEAN 1-N` accounts for
every address, cites nothing, and exits 0 having read no file at all. Nothing
mechanical can separate that from a real pass, because a negative leaves no
artifact. **A green exit here is not evidence that anything was read.**

! **The tool rules on ADMISSIBILITY, not on truth.** It cannot tell a correct
verdict from an incorrect one. Synthesis, and the order below, remain yours.

! **A paragraph that ends mid-clause is a finding, and its verdict is `correct`.** A run whose last
sentence stops mid-air -- a severed trailing comment, a `move` that cut a sentence in half -- is
neither checkable nor necessary, so the matrix routes it to `drop`, deleting the pointer instead
of repairing it. Restore the sentence.

! **Two findings quoting the same sentence in different files are ONE finding.** A pass edits
where it is reading, fixes the copy in front of it, and manufactures a disagreement with the one
it never opened. Contradicting verdicts trigger a **re-review**, never a tie-break. The join
cannot see this for you -- `contradictions()` keys on the ADDRESS, and the same
sentence copied into two files is two different paragraphs it can never relate.

!! **Whether a TRUE sentence earns its place is a VERDICT, and verdicts are theirs.** The
CHECKABLE/NECESSARY matrix that settles it is in `reviewer-brief.md`, and every reviewer is
handed it. A paragraph whose place no verdict settles goes BACK for re-review; you do not rule it
here.

### Synthesising one comment out of N verdicts

Four reviewers rule on the same paragraph, so you hold several recommendations and must emit **one**
replacement. Apply them in this order. It is not arbitrary -- each step depends on the one above
being settled:

1. **`query`** -- resolve it or escalate it. An unresolved claim cannot be corrected, patched or
   dropped, because you would be editing something nobody has read.
2. **Every `move`, and every `drop`** -- settle WHERE the prose lives before touching what it
   says. A `move` out of the code and a `drop` take out what is leaving; a `move` inside the
   code re-attaches what belongs beside different code, and a paragraph whose sentences belong in
   different places is several `move`s, one per sentence. ! **Placement comes first because a
   claim is measured against the code it sits with** -- correct it where it does not belong and
   you have corrected it against the wrong code.
3. **`correct`** -- fix truth, on what remains, **at the anchor it now sits on**. !! A `correct` that travelled with a `move` is applied AT THE DESTINATION and re-derived there, never against the code the prose left. ! It may leave a VACUOUS comment, and that is the accepted outcome: another pass drops it, which is cheaper than a correction that was true only where the prose used to be.
4. **`patch`** -- fix wording, on text now known to be true. ! **Never before step 3:** a
   `patch` on a false sentence polishes the wording of a falsehood and retires the finding.
   That is laundering, and this order is what prevents it.
5. **`add`** -- insert at the stated anchors.
6. **`clean`** -- the null verdict, and **the join already did this one.** The paragraphs it printed
   as `STANDS UNCHANGED` are exactly those every reviewer that ran returned `clean` on. Read
   that number; do not re-derive the set.

! **Load [`references/residue-check.md`](references/residue-check.md) before you write anything**
-- the check is defined there, and this is the first stage that owes it. Stages 6 and 7b re-run
the same check against the same original; none of them may check against the previous edit.

Then emit the replacement and run the residue check on **the whole synthesised paragraph once** --
not once per verdict. The check compares against the original, and the original was one paragraph.

**Four rules that resolve the common collisions:**

- **Two placement verdicts on one paragraph, naming different destinations:**
  `ownership-context`'s destination governs. Both findings stand; only the destination is
  decided. ! This is the PRECEDENCE that role already holds, not a tie-break -- the rules below
  break no ties.
- **Any `correct` outranks every `clean`.** Three roles finding nothing does not soften one
  role finding a falsehood; they were not looking for the same thing.
- **`correct` and `patch` on the same sentence:** correct first, then re-read the patch against
  the corrected text. Usually it no longer applies.
- **`drop` against `correct` OR `patch` on the same sentence is a contradiction**, not a merge --
  one role says the sentence should not exist and another says it should exist and be fixed.
  Nothing composes those. The join prints it as `RE-REVIEW`; send the paragraph back.
- !! **`move` against either of them COMPOSES, and is not a contradiction.** Ruled 2026-08-17.
  Relocation and a truth fix are a SEQUENCE: the synthesis order applies every `move` at step 2
  and every `correct` at step 3, which is what applies the correction AT THE DESTINATION.
  Measured on a live run: **5 of the 8 paragraphs the old set flagged were this shape**, and a
  re-review round was spent on each establishing it was not a rivalry.
  ! This paragraph used to name `move` alongside `drop`; the ruling removed it from the join's
  set and left the sentence here, so the skill and its own gate disagreed. See
  `TODO/move-and-correct-compose.md`.

! **Dedup on the SENTENCE RULED ON, not the paragraph**, before any of this -- the half of `CLAIM`
that quotes the existing prose (`drop:`, `false:`, `from:`), never the whole `CLAIM`. Two roles
fixing one sentence propose different edits, so their `CLAIM`s differ while their subject does
not; the join keys on that half for the same reason.

!! **THE SENTENCE YOU PROPOSE TO KEEP IS A FINDING YOU HAVE NOT RAISED.** Before any `patch`
or `move`, verify the retained clause the way stage 3 resolves an annotation. The reviewer keeps the
load-bearing-*sounding* clause -- which is the claim, which is what is wrong -- and cuts the
**provenance** around it: the date, the pointer, the grepable name.

```
before:  # Retry budget is 3, not the 5 the config advertises -- `Backoff.next()`
         # halves it for idempotent verbs, and `docs/retries.md` records why.
         # Raising it re-opens the thundering-herd incident.
after:   # Retry budget is 3, not the 5 the config advertises.
```

If the budget is not 3, it was wrong before and is wrong after -- but the cut took the two
things that let a reader find out: the symbol that computes it, and the document that records
why. Shorter, cleaner, in-cap, and **strictly harder to falsify than what it replaced.** A
paragraph trimmed around an unchecked claim is **laundered, not reviewed**. ! **`move` has no truth check on its
path** -- "write the destination verbatim" copies a falsehood somewhere harder to find.

! **Length is not your question at this stage.** A paragraph that is true, local and load-bearing
is finished here however long it is; COMPACT shortens it only if a cap applies. A run that
returns mostly `clean` is a good outcome, not a lazy one.

**Two shapes a length rule cannot express.** A comment claiming *"pinned by X"* **licenses
future edits** -- ! the dangerous cell is a deletion justified by coverage nobody can find,
which reads as safe for exactly that reason. Grep the cited name, every time. And a rule
**stated in several places with no owning definition** is why the comments got long.

**A `#` comment is governed by LENGTH; a docstring by FORMAT.** Long is not a violation; what
fails is a body carrying what is not documentation -- a date, a quotation, a retraction, a
rationale paragraph, a claim about callers or coverage -- **at any length**. ! **Acquit on
KIND, never on LENGTH**: a two-line docstring whose summary runs on is still a finding.

Invisible to any counter: a **trailing comment carrying past its own line** (a `move` to the
line above); a **paragraph split by an inserted statement**, where only the half still
talking about what came before is the finding; **the wrong half surviving** -- check what
SURVIVED, not what went; **refactoring drift**.

## Stage 5b -- RE-REVIEW: is this what you meant?

**Every paragraph the join printed as `RE-REVIEW` goes back to the roles that ruled on it**, once
you have written its replacement. Load
[`references/re-review.md`](references/re-review.md); it carries the payload, the three
questions, the return shape, the channel and the stop rule, and this section does not restate
them.

!! **SET A GALLEY FIRST, and census it.** The joined paragraph is on no disk and in no census, so
nothing can address it -- `address_problem` refuses a record whose ADDRESS matches no census
entry, which is every round-2 record until this runs:

```bash
python <skill>/scripts/galley.py --repo . --census <run-dir>/census.json \
  --edits <run-dir>/edits.json --out <run-dir>/galley
python <skill>/scripts/census.py --json --repo <run-dir>/galley \
  --out <run-dir>/galley-census.json <the same paths, under the galley>
```

`--edits` is `{"<address>": "<your replacement paragraph>"}` -- the same address the record
carries, so nothing between stage 5 and the galley converts. **Nothing under the repo is
touched**; a galley is a copy and it is discarded with the run.

! **A round-2 record is an ORDINARY record** citing the galley census, so it joins exactly as a
round-1 record does. Run `verdicts.py` against `galley-census.json` for it.

!! **Do not carry a round-1 index into round 2.** A replacement whose line count differs shifts
every paragraph below it, so the same prose holds different indices in the two censuses. They relate
by PATH and CONTENT, and you are the only participant holding both.

! **`galley.py` REFUSES rather than guesses.** It exits nonzero and NAMES what refused --
**read that, rather than the list you remember**: this section carried three of the seven
reasons and was wrong about the set for two releases, in the same way the RE-REVIEW set is
`verdicts.py`'s to print and not this file's to derive.

!! **One of them is not about your edits.** A census taken before the fields the galley needs
is refused WHOLE, before any paragraph is read, because every per-field default is a guess about a
file this tool is about to overwrite -- and the one default that was tried put a deleted
statement back. Re-run `census.py` and set the galley again. ! It is `CANNOT USE`, not
`REFUSED`, and it exits **2**: nothing was wrong with the proposal.

## Stage 6 -- COMPACT: only if there is a cap

**If no cap applies, the run SKIPS this stage entirely.** Say so: the prose is correct, and
absent a cap "long" is not a defect.

If there is a cap, and only once **every** paragraph from stage 5 is CORRECT,
dispatch `comment-review:comment-review-compact` with the narrow input contract
below, and paste [`references/compact.md`](references/compact.md) into its prompt
whole.

!! **This pass is not yours to run.** You wrote the text; an agent that never
saw the argument cannot preserve a sentence because it remembers writing it.
The narrow contract is only a safety property if the reader is different from
the writer. If the agent does not resolve, use the same fallback as 1.6 -- a
general-purpose agent given the path -- and **say in the proposal that you ran it
yourself** if you had to.

! **Nothing is on disk yet.** This pass condenses the PROPOSED text, not a file -- the author
has not ruled and nothing has been applied. That is the whole reason this stage sits here: what
you hand to stage 7a is what will be written.

! **Do not fold it back into stage 5.** Compaction decisions depend on the final state of the
whole tree -- a `move` that relocates prose between paragraphs, an owner that collapses N
restatements into one -- and none of that is settled until every paragraph is edited. `compact.md`
carries the argument and the per-paragraph procedure.

## Stage 6b -- RE-REVIEW: is this still correct after my edits?

**Runs only if stage 6 ran**, and over the paragraphs it actually shortened. Same mechanism as 5b,
same file, **different question**: 5b asks whether the synthesis carried the finding, 6b asks
whether shortening broke it. ! A single *"is this still right"* prompt collapses them and
answers neither.

!! **NOTHING ELSE READS STAGE 6's OUTPUT BEFORE THE AUTHOR DOES.** Stage 7a presents it and
rules on nothing; the CODE CHECK runs at 7b and reads only executable code; stage 8 runs after
the write. **Skip 6b and the compacted text reaches the author read by nobody but the agent that
wrote it.** ! Measured 2026-08-17: on one run the compact pass came under the cap by writing
98-column lines and flagged that itself -- nothing else was positioned to catch it.

!! **A paragraph stage 6 must edit that NO role ruled on goes to ALL FOUR, as a fresh paragraph.** A
paragraph every role returned `clean` on can still be over the cap; shortening it is an edit with no
verdict behind it, and neither 5b nor 6b reaches it because there is no filer to ask. It comes
back with verdicts. ! It is the only path by which stage 6 originates work, and it runs the
opposite way to everything else: every other finding travels 4 -> 5, this one travels 6 -> 4.

! **Set a galley of the COMPACTED text and census it**, exactly as 5b does. The text stage 6
hands on is again on no disk, and it is not the text 5b addressed.

## Stage 7a -- APPROVAL: present the FINAL text, then stop

Grouped by verdict, most consequential first, in **five parts**
(`VERDICT / PARAGRAPH / CLAIM / REASON / CHANGE`) -- the reviewer record minus the fields only
the join reads -- replacement text inline
for every `correct` / `patch` / `add`. State **raised / clean** and the
longest paragraph that will remain. **The proposal ends here** -- nothing further is written until
the author rules.

!! **What you show IS what gets written.** If stage 6 ran, show the COMPACTED text -- never the
full-length version with a note that it will be shortened. The author rules once, quickly, and
on the assumption that the text in front of them is the text that lands.

**Hand back the STYLE SHEET**, updated with every decision this run made -- the sheet is how the
next pass avoids re-deciding, and it is worthless if it stays in your head.

! **Approval IS authorization.** "Yes", "do it", "continue" -> load `references/write.md` and
apply. Never-edit binds reviewers, not you acting on an approval.

## Stage 7b -- WRITE: put the approved text on disk

On approval, load [`references/write.md`](references/write.md) and follow it. It carries the
residue check and the write rails. Do not write from memory.

! **Stage 7b writes the APPROVED text verbatim.** It does not shorten, re-word or re-judge --
every one of those questions was settled upstream, and re-opening one here writes something
the author never saw.

## Stage 8 -- REVIEW: the finished page

On completion of 7b, dispatch `comment-review:comment-review-review` with the
list of changed files and the style sheet, and paste
[`references/review.md`](references/review.md) into its prompt whole.

!! **This pass is not yours to run either**, and for the same reason: a reader
who remembers intending each edit reads the page they meant to write. If the
agent does not resolve, fall back as at 1.6 and say so.

! **NOTHING is fixed here.** Stage 8 reads and reports; the author decides what follows. A
defect that predates the run is reported SEPARATELY from damage this pass caused, because the
two need different answers.

## What this skill is not

`/simplify` reviews code structure and applies its fixes. `/code-review` hunts correctness
bugs. This reviews prose and writes nothing until the human approves. A defect noticed anyway
is **named and left**.
