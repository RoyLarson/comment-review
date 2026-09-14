---
name: comment-review
description: Review the comments and docstrings in the files a change touched, across four editorial roles -- ownership-context, block-context, function-context, module-context -- using parallel read-only subagents, and return each finding as instruction/location/summary/finding/change for the human to rule on. Use this whenever comments or documentation are the subject -- after finishing a task that added or edited commentary, when a file's comments have drifted from what the code now does, when someone says a comment is too long or out of date or "isn't this history", when reviewing a diff specifically for its prose rather than its logic, before a docs or comment burn-down, or when asked to check whether a module still reads as one module. Trigger on phrasings that never say "comment review" -- "these comments are getting out of hand", "does this docstring still match", "is this comment still true", "clean up the narration in this file", "why does this file need so much explaining" all mean run this. It is NOT /simplify (which reviews code structure) and NOT /code-review (which hunts correctness bugs). The REVIEWERS never edit; what the human approves is set in temporary files for them to diff, and every approved change passes a residue check against the original prose.
---

# comment-review

`/comment-review [cap] [target] [style]`

**An editorial board for the comments and docstrings a change touched.** Four editors read
the same manuscript in four editorial roles, the copy chief folds their marks into one set of
edits, a condenser cuts them to fit, the page is set and proofed, and the author approves **that** text.
Structure and fact first, then truth, then fit, then the page.

```
1 PROJECT      2 GATHER    3 FIND       4 MARK       5 COLLATE   6 COMPACT   7a SET       8 REVIEW    7a PRESENT
  DETERMINATION            REFERENCES   4 roles      and CAP                   a galley     reads it    7b WRITE
                                                                              ^
                                                                +---- no cap -+
```

| # | stage | who acts | what exists at the end of it |
|---|---|---|---|
| 1 | **PROJECT DETERMINATION** | task agent | language, doc convention, cap and width, project rules, style sheet, and where the name corpus will come from |
| 2 | **GATHER** | `gather` | every page in scope bound into one BINDER -- each comment run and docstring a paragraph with its address |
| 3 | **FIND REFERENCES** | `referrers` | every tracked file that names a page under review -- the `REFERENCE ONLY` list |
| 4 | **MARK** | 4 reviewers | one filled `edit_copy` per role, checked. Read-only, nothing under the repo written |
| 5 | **COLLATE and DISPOSITION** | `collate`, then the task agent as **copy chief** | the copies folded; what they agreed on stands, what they did not is ruled at max turns; the chief's `edit_copy` holds one mark per resolved place with its **full-length** text |
| 6 | **COMPACT** | task agent | that text cut to the cap -- **skipped entirely if there is no cap** |
| 7a | **APPROVAL -- present** | task agent, then `proof` and the **compositor**, then stage 8 | the final text set as a galley -- a copy of each page, nothing under the repo touched -- read by stage 8, then in front of the author with stage 8's findings and the places only the author can settle; **the run stops here** |
| 7b | **APPROVAL -- write** | **author**, then task agent and `proof` | the approved text set in temporary files for the author to diff and read through, byte-for-byte as approved; nothing under the repo written |
| 8 | **REVIEW** | `comment-review-review` | the galley's pages read as a reader would read them, before the author sees the proposal |

!! **THIS IS THE BASELINE SHAPE, RULED 2026-09-04: every role reads ONCE, the copies fold ONCE,
and nothing goes back to a role except a copy the checker refused.** No revise is pulled
between stages and no batch of disagreements is sent out for a second reading. The `turn`
command exists for that second reading and is the next experiment, run only when you are told
a number of turns above zero -- see stage 5. What the baseline measures is how far one read
per role, one fold and the chief's ruling get on a real codebase.

**This file is the task agent's.** Each reviewer is a named agent carrying its own editorial role and
reading [`references/reviewer-brief.md`](references/reviewer-brief.md) itself.
[`references/residue-check.md`](references/residue-check.md) loads at stage 5,
[`references/compact.md`](references/compact.md) at stage 6 -- **before** the author sees
anything -- [`references/write.md`](references/write.md) only after approval, and
[`references/review.md`](references/review.md) at stage 8. **Nobody loads all of it**, and no
file restates another.

## The seven instructions

Everything below this line uses these seven words. A reviewer emits them; **you receive one or
more per role per paragraph and must emit ONE replacement**, so what matters here is what each
obliges *you* to do.

!! **And you are expected to read the code around where that replacement lands, to verify it.**
An instruction rules on a SENTENCE; a paragraph is only its address, so a paragraph of six sentences can
arrive carrying six. Ruling on them without re-reading the code beside it is how a run replaces
an unfalsifiable claim with a checkably false one -- measured twice in the pass stage 8 rolled
back.

| instruction | the claim is | what you do with it |
|---|---|---|
| `clean` | nothing to report **from this role**, on a paragraph that role READ | nothing. Not a pass, and not a claim the paragraph is correct -- one role having no finding. A paragraph outside what the role reads is `query` |
| `query` | unsettled | resolve it or escalate it. Every other instruction on that sentence waits on it |
| `drop` | true but not worth keeping | delete the sentence |
| `correct` | **FALSE** | apply the true/false pair. **Always before any `patch`** |
| `patch` | **TRUE**, badly worded | apply the rewrite |
| `add` | missing entirely | insert the text at the anchor named with it. Its paragraph is the empty INTERVAL the prose belongs in, so read it as being about that gap and not about a neighbour |
| `move` | true, but **it belongs somewhere else** | re-attach the paragraph, unchanged, at the destination carried with it -- another line in this file, another file, or out of the code entirely |

!! **A relocation is ONE judgment, and the DESTINATION carries the rest.** Whether the prose
belongs ten lines down, in another file, or out of the code altogether is payload -- not a
second instruction. The reason it belongs there goes in `reason`, which every mark already
has. **Availability keys on the destination, never on the instruction.** A relocation into
tracked code needs nothing outside it and is never withheld. A destination outside the code --
or in a file this run never gathered -- is not carried yet (`decision-log.md Process: #173`):
`mark` refuses it, and the role files a `human-review-necessary` query naming it instead, which
reaches the author at 7a (`#169`).

A reviewer's instruction is only usable if it carries its payload. That contract is the
reviewers', and [`references/reviewer-brief.md`](references/reviewer-brief.md) holds it --
`check` and `collate` enforce it by refusing a mark that arrives without one.

## Why the stages are in this order

**1-3 build the PAGES** -- one per file: every LINE classified and numbered in order, each
paragraph carrying its address, its anchor, its start and end line and its text. This line is
code, this PART of a line is code, this
line is comment, this line is docstring. It carries only which lines are which, which is
what a reviewer of COMMENTS needs. The places holding nothing are on it too, because that
is where prose is MISSING.

**MARK (4) is separate from COLLATE (5)** because a reviewer that fixes what it finds has
destroyed the finding.

**COLLATE (5) writes at FULL LENGTH.** Its only job is a comment that is true, local and
load-bearing. Length is not one of its questions, and a run that returns long correct prose
has succeeded.

! **Measured 2026-08-17, with no second reading of the prose in the pipeline:** a run reached
stage 8 with ruff clean, the AST PROVEN and 1103 tests green, and stage 8 returned twelve
findings -- two of them the system replacing prose with something CHECKABLY FALSE. **That is
the number this baseline is measured against**, and the reason stage 5 runs the residue check
on its own output and stage 8 reads the page.

**COMPACT (6) is a separate pass over that text.** It comes AFTER the fold and BEFORE approval,
and two constraints pin it into exactly that slot:

- **After COLLATE**, because prose can only be shortened without losing information once it is
  true. Shortening first is how a false sentence survives -- it gets *trimmed around* rather
  than checked, arriving shorter, cleaner, in-cap and strictly harder to falsify.
- !! **Before APPROVAL, because the author must rule on the text that will actually be
  written.** Showing a full-length comment, getting a yes, and then writing a compacted one
  means the author approved something that never reached the file.

**APPROVAL (7) presents the FINAL text and STOPS.** It takes the author's ruling, and applies
that text only if it was approved -- set in temporary files for the author to diff, never over
the real files.

**REVIEW (8) is the only stage that reads the artifact against itself.** Everything before it
compares prose to code; this asks whether the finished page still reads. It reads the galley 7a
sets, before the author sees anything, and its findings go into the proposal.

## Three roles

**The HUMAN is the AUTHOR, and is absent.** They approve almost everything, quickly,
unaudited -- a direction, not a diff. **So every proposal must be safe to approve blindly.**
Their disagreement is valuable; it is not a safety mechanism and must never be used as one.

!! **That makes this an editorial board with an absentee author, and one principle follows:
CONSERVATIVE ON MEANING, FREE ON FORM.** An editor rules on form; the author rules on what a
sentence claims. With the author not reading, you may fix wording, placement and length on your
own judgement -- but every change to what a sentence CLAIMS needs evidence in hand, or it is a
`query`. That is why `correct` must carry the line that settles the claim, and `patch` need not.

**The TASK AGENT -- you.** Run stages 1-3, launch the reviewers, fold their copies, rule at
max turns as the **copy chief**, present, and after approval set the approved text in temporary
files the author diffs (7b). You write nothing under the repo. **Write the replacement text yourself** where the roles
did not agree, and verify what you write. *"Compact + correct"* is an instruction to somebody
else, not the text.

**The REVIEWERS** are read-only, one editorial role each, and never see this file.

## Arguments

- **`cap`** -- integer, optional; max lines for one `#` run. **This skill has no cap of its
  own** and must not invent one. None given and none published -> **no cap**.
- **`target`** -- a path; **replaces** the diff scope, never intersects it.
- **`style`** -- a path to a style sheet from a previous run. Optional; see 1.5.

!! **Every instruction is available on every run.**

**All four roles run, and `ownership-context` is never dropped.** Each of
the other three checks a claim against the code at its own scope, so a run may omit one of them
and still be a review -- but a claim attached to the WRONG scope is measured against the wrong
code and `correct`ed into a falsehood, which none of the three can notice, and
`ownership-context` is the role that reads for that. **Say in the proposal which roles ran.**

!! **THE CAP IS APPLIED IN STAGE 6 AND NOWHERE ELSE** -- never while text is being written,
and **never passed to a reviewer** -- it is not a section of the stage-4 packet, and neither is
`WIDTH`. Length is not an editorial role; the reason is in the brief.

## Stage 1 -- PROJECT DETERMINATION: ground truth

!! **THE FLOOR IS A LOCAL GIT REPOSITORY, and that is the ONLY thing a rule here may assume.**
`git ls-files` answers, and `git show <ref>:<path>` answers for a ref that exists. **Everything
else is checked, not assumed** -- an upstream, a merge base, a clean tree, a cwd at the repo
root. Pass `--repo` to every command that takes one rather than relying on the working directory.

!! **Record the PRE-EDIT REF now, and carry it to stages 6 and 7b.** It is `HEAD` when the tree
holds no uncommitted change to the files in scope, and `git stash create` otherwise -- which
writes a commit object for the current state and leaves the working tree untouched. **It is not
the merge base**, and the two answer different questions: the merge base says what the BRANCH
changed, the pre-edit ref says what THIS RUN changed. Stage 6 reads the ORIGINAL prose from it
and stage 7b's residue check reads it again.

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
say which** -- the gather takes neither number, so a cap you invented would reach stage 6 as a
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

! **Ask which markers the repo exempts from the cap**, and say so in the proposal. The gather
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
An instruction pointing at a tree that does not exist is not an instruction.

!! **The answer may be PER PATH, and a repo that says otherwise is rare.** A convention like
`docs/{pkg}/{module}.md` is available exactly where that tree was actually built -- measured on
one repo, present for `tests/**` and absent for the production package, though the convention
document cited the same path for both. **Write the split into the packet**, one line per scope,
rather than picking the stricter answer for everything: told UNAVAILABLE everywhere, a reviewer
withholds a legal `move` on the half that has a destination; told the tree everywhere, it emits
instructions pointing at a tree that is not there.

**A `move` out of the code is not carried yet, tree or no tree** (`Process: #173`): a paragraph
that belongs outside the code reaches the author as a `human-review-necessary` query naming
where it belongs (`#169`), never a `drop`. A `move` to a destination inside tracked code is
unaffected and always available. Where the tree is absent, say so at stage 1 and again in the
proposal, and offer the human the one-line alternative (create the tree, or name another
destination). This matters because the matrix routes
*not-checkable + necessary* to `move`, and a repo that stages prose usually also rules that
prose is MOVED, never deleted -- so with no destination those two rules leave the paragraph with no
legal instruction at all -- *the matrix* is the checkable/necessary table in the reviewers' brief, and
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
this is structure available for free that the gather cannot ship. It buys exactly two
things, and neither is the binder:

| | with a server | without |
|---|---|---|
| **a paragraph's ANCHOR** | `documentSymbol` -> the declaration on the line after the comment run ends | nothing resolves it |
| **is a name alive** | `workspaceSymbol` / `findReferences`, in **any** language | the Python AST corpus only |

!! **LSP RETURNS NO COMMENTS, so it can never replace the gather.** The nine operations
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
the gather builds it. Do not try to produce it here.

- a server answered at 1.7 -> **`workspaceSymbol`**, which covers every language at once
- no server -> the AST corpus the gather builds at stage 3, Python only
- both -> combine them, and say so

From the AST never raw text (text contains the comments being checked, so everything passes);
skip directories holding `pyvenv.cfg`; never harvest string constants from tests
(`assert "x" not in y` makes a dead name read alive); exclude `.md`/`.txt`; resolve a dotted
name on its **head** segment only.

**1.9 Build the topology and prove it fits, before any page is read.** The topology says
which stage dispatches which role, in what order, and which role is split across how many
shards; it is a determination, so it is decided here -- but it is proved against the binder,
so in time these two commands run right after stage 2 writes `binder.json`:

```bash
python <skill>/scripts/comment-review.py topology --build --binder <run-dir>/binder.json --out <run-dir>/topology.toml \
  --stage 4=ownership-context/<n>,block-context/<n>,function-context/<n>,module-context/<n>
python <skill>/scripts/comment-review.py topology --verify <run-dir>/topology.toml --binder <run-dir>/binder.json
```

**Split each role per file, at most five files a dispatch.** `<n>` is the number of files you
gathered divided by five, rounded up -- 12 files is `/3` -- and `--build` deals the files to the
dispatches in turn, so none holds more than five. Five is a first estimate, and the next run is
the first to test it. That is this release's topology: one stage, the four roles, one revise. A
second stage reading the first's revise (`--stage 4a=... --stage 4c=...`) is a shape the file
can express and a later release may turn to. `--build` writes a topology that fits the binder by construction and verifies it;
`--verify` alone checks one you already hold. **A run against an unverified topology is not a path these
instructions offer.** A bad configuration costs nothing only when it is caught here: `--verify`
exits 1 and names the stage, the kind -- a page two shards of one role claim, or a page no shard
of a role reaches -- and the pages and globs involved. **The fix is to the topology, never to
the tree.** A glob that matches no page is not a fault on its own; only a page nobody covers is.

## Stages 2-3 -- GATHER, then FIND REFERENCES

! `<skill>` below is the directory holding this SKILL.md -- take it from the absolute path you
were given. A relative one resolves against whatever directory you are in, which is not
guaranteed to be the skill's.

```bash
python <skill>/scripts/comment-review.py gather --repo . --out <run-dir>/binder.json <paths...>
```

**One file, and every stage up to the fold reads it.** The BINDER is what those stages'
commands take -- `distribute` seeds each reviewer's copy from it, and `collate`, `turn` and
`disposition` fold against it. A reviewer is handed the binder and its own seeded copy, and nothing else
is made for it: the copy carries each prose paragraph's text in its slot, and the binder is what
the reviewer's `addresser` and `check` calls take.

### What a place is CALLED

!! **AN ADDRESS IS WHAT EVERY MARK CITES**, and it is the only name that survives this run's own
edits -- a prose edit moves the line numbers below it, and an address counts against the CODE.

```
pkg:core.py@a5    a DECLARATION's documentation
pkg:core.py@b3    a GAP between two lines of code
pkg:core.py@f0    the FILE'S OWN matter -- a licence, a shebang, an index
pkg:core.py@c3    the room BESIDE a line of code
```

The path is flattened on `:`, a character no path may hold, so `a/b.py` and `a.b.py` cannot
collide. `docs/addressing.md` is the settled definition.

!! **YOU CANNOT WORK A CUE OUT. ASK.** The four series (`a`, `b`, `c`, `f`) are counted by four
separate addressers, and no number in one tells you a number in another -- nor does a line's
position tell you either.

```bash
python <skill>/scripts/comment-review.py addresser --binder <run-dir>/binder.json --file <path> --line LINE --series a|b|c|f
python <skill>/scripts/comment-review.py addresser --binder <run-dir>/binder.json --resolve <ADDRESS>
```

**A line can answer with more than one place, and that is not an error** -- `--series f` prints
both of the file's own places, head and foot, since no line tells them apart. Choose by ADDRESS.

!! **`--out`, never a shell redirect.** A worktree-isolated session REFUSES a command carrying
one -- *"too complex to verify that it stays inside the worktree"* -- and the binder is what
every later stage parses, so a redirect makes the run impossible there rather than merely awkward.

! **The gather takes no cap and no width.** The cap belongs to stage 6, and every reviewer's
copy is seeded from the binder -- an over-cap count in it lands in front of the four roles that
must never see it.

!! **Most of the binder is empty places, and nobody owes them a mark.** Every gap between two
lines of code is addressed, empty ones included, because an `add` is a finding about prose that
is MISSING and the mark needs an ADDRESS to carry it. They are ADDRESSABLE, not ACCOUNTABLE: the
binder carries only the places holding prose unless `--include-absent` asks for the rest, and
the collator computes coverage over what the binder carries. Re-measured 2026-08-19: the
gather over its own command is 1,607 paragraphs, 118 of them prose.

! **Give the binder a path unique to THIS run.** Two concurrent reviews sharing one scratch
filename overwrite each other between writing and reading, and nothing downstream can tell.

**A suffix the gather has no record for is named, and the gather EXITS NONZERO** -- every file
handed in is gathered or the run stops, so a file that reaches a reviewer is reviewed like any
other whatever its tier. `python <skill>/scripts/comment-review.py gather --languages` lists what it knows.

! **It builds the page at the TIER available for each file's language.** Both tiers find the
same paragraphs and differ only in what else they can say:

| tier | needs | answers | cannot answer |
|---|---|---|---|
| `tokenized` | a lexer + AST (Python: the stdlib) | paragraphs, **docstring** anchors | a **comment's** anchor |
| `lexical` | a comment-syntax record, nothing else | paragraphs | any anchor; a marker inside an exotic string |

!! **Say in the proposal that every placement is a CANDIDATE.** No comment carries an anchor
at either tier, so every PLACEMENT instruction rests on a reviewer READING the file -- a
judgement no field records and nothing downstream can check.

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

# paragraph starts
# TODO: important thing in it
# paragraph continues
# paragraph ends
result = foo_bar(variable_a)
```

**One paragraph**, bounded by `variable_a = 1234` and `result = ...`. Four physical comment lines,
**three** counted: the marker line is free. The blank is inside the paragraph and is charged
nothing. The example carries no inline notes on purpose -- a `#` note explaining the
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
  is where the gather reads its anchor from.
- **A trailing comment is its own paragraph**, one line, anchored to the code on that line.

### The language server, where 1.7 found one

The gather names every paragraph and the anchor it sits on, and nothing a server says is written
into the binder -- no command attaches it. Use the server yourself where you verify a claim:

- **Anchor** -- `documentSymbol` on a file returns every declaration and its line, which tells
  you whether a paragraph's anchor is the declaration it documents.
- **Liveness** -- for a name a paragraph uses, `workspaceSymbol` answers whether the
  name exists at all, in any language in the workspace. `findReferences` answers whether
  anything uses it, which is the stronger claim a comment usually makes.

! **A server does not settle a claim, it settles a FACT.** "This name exists" is not "this
comment is true" -- the claim stays a candidate a reviewer confirms, exactly as when the AST
answered it. What changes is the cost of checking, not who decides.

!! **Say which servers answered, per language, in the proposal.** Availability is a
property of the machine, so two runs over identical input can resolve different sets. A run
that had no server must not read like one that did -- and any measurement taken with a server
is not comparable to one taken without.

! **Scope by SUBJECT, not by file extension**, and resolve it with the tool
rather than from memory -- this is the INBOUND half of stage 3:

```bash
python <skill>/scripts/comment-review.py referrers --repo . <paths under review...>
```

It prints every tracked file that NAMES one of them -- by path, by stem, or by a
public top-level definition. Those files are the **REFERENCE ONLY** list you hand
the reviewers at stage 4; a config, data or documentation file carrying prose that
justifies a value is a paragraph like any other, and a file left out of scope carries the same
defects as the code -- including rewrites the pass already applied in a `.py` file.

!! **This runs in `target` mode too.** A `target` run has no diff to widen from,
which is exactly why the memory-based rule it replaces could not fire there --
the invocation most likely to be typed by hand was the one with no backlink
discovery at all.

Report the gaps both commands print -- every `NOT CHECKED` and `PASSED OVER` list, and
`NO GIT INDEX` -- then the files, paragraphs and languages the binder covers.

## Stage 4 -- MARK: four reviewers

**Dispatch all four**, by agent name, together or one after another:

| agent | asks |
|---|---|
| `comment-review:comment-review-ownership-context` | does this comment belong to the ANCHOR it sits on? |
| `comment-review:comment-review-block-context` | is every claim in this paragraph true of the code it sits with? |
| `comment-review:comment-review-function-context` | does the commentary match what the function is FOR? |
| `comment-review:comment-review-module-context` | do the comments say this is ONE module? |

**They must read independently, and the topology and the copies are what keep them apart.**
Overlap between roles is signal only if no role saw another's findings: two roles agreeing is
corroboration when they read alone and nothing when the second read the first. Each role reads
the binder and fills its own seeded copy, and nothing a role writes is a path another role is
handed -- so the roles may go out in one message or one after another, and the proposal owes
no note either way. **Never put in a role's prompt anything another role returned**, and never
hand it another role's copy.

Each already carries its own editorial role.

**Seed every copy of a stage in one command, from the topology 1.9 verified** -- one file per
dispatch, named `<stage>_<role>_<n>.json`, each with a slot already laid down for every prose
paragraph on the pages that dispatch covers:

```bash
python <skill>/scripts/comment-review.py distribute --topology <run-dir>/topology.toml --stage 4 \
  --binder <run-dir>/binder.json --out-dir <run-dir>/copies
```

It prints one line per file it wrote. **Each file is one dispatch, and one dispatch is one
packet**: a role split two ways is two agents of that role, each handed its own copy. The
stage's order comes from the topology and the topology's order from 1.9; you run this once per
stage, and no command sequences the stages for you.

!! **A REVIEWER FILLS A FORM; IT DOES NOT COMPOSE A DOCUMENT.** Each slot arrives carrying the
`address`, the `anchor` and the paragraph's `raw_text`, with `instruction` null, and the
reviewer sets the fields that are its own. **Hand each agent two absolute paths, and it reads
from there: the BINDER and ITS copy**, and tell it to edit that copy in place. Those are the
run's own files, not the installed plugin, and they are the exception to *given, never sent
looking* below: a form and the sheets it is filled against, not a tree. Nothing from the two is
pasted into the prompt.

! **The seeded copy is why coverage is structural.** A paragraph nobody ruled on is a slot with
a null instruction, not an address missing from a list, so nothing downstream reconciles what
was expected against what arrived. A reviewer may still APPEND a mark for any binder address,
and must for an `add` -- an `add` cites the empty INTERVAL prose is missing from, and intervals
get no seeded slot.

!! **Put the BRIEF and each agent's VOCABULARY in its prompt, verbatim.** Paste
[`references/reviewer-brief.md`](references/reviewer-brief.md) whole -- it is the same text for
all four -- then that role's vocabulary: the `[definitions]` entries of
`<skill>/scripts/comment_review/references/vocabulary.toml` whose keys are listed under that
role in `[roles]`, plus the `all` list. ! Do not summarise it, do not trim it to the terms you
think a file uses, and do not tell an agent where the vocabulary lives -- it is given the words,
not a path to go reading. ! Read it fresh from the installed toml every run, never from a copy
staged on disk: a vocabulary one version stale reads perfectly plausible.

!! **`BINDER` POINTS AT `binder.json` FROM STAGE 2.** A reviewer's copy carries each prose
paragraph's text; the binder is what its `addresser` and `check` calls take, and what stage 5
resolves every cited address against. A reviewer reads both from disk; neither is pasted
into a prompt.

**You also supply the run context as a PACKET, with every section filled and none blank** -- a
published non-answer such as *"UNAVAILABLE"* is an answer and must be written; a blank is not.
`REPO ROOT`, `BINDER`, `EDIT COPY` and every `REVIEWER FILES` entry must be an
**absolute path that exists**. The sections are: `REPO ROOT`; `BINDER`; `EDIT COPY`,
the one section that differs per role; `FILES UNDER REVIEW`; `REFERENCE ONLY`; the STYLE
SHEET, templates included; which language servers answered your probe at 1.7, per language --
your answer, not a promise that a reviewer can call one, since a reviewer may have no LSP tool;
the destination
tree from 1.4, per path; and `REVIEWER FILES`, which is yours alone.

Hand every reviewer the one packet. Dispatched without a style sheet, a run drifts the dialect
while fixing the prose, and every role is satisfied because nothing owns consistency.

!! **`REPO ROOT` is what every other path resolves against.** The binder, `FILES UNDER
REVIEW` and every citation a reviewer writes are repo-relative, and a reviewer handed no root
is guessing at a working directory.

!! **Withhold every TASK AGENT ONLY section when you paste the packet.** `REVIEWER FILES` is
one: it names paths inside the installed plugin, which is not the tree under review. It is
checked here because it is YOURS -- the 1.6 fallback reads it.

! **The templates go to the reviewers too, and stages 5 and 6 match their output against them.**
A docstring's format decides which of its lines are structural and which are prose, so a
reviewer that does not know the format cannot tell what a paragraph contains. And a correct
sentence in the wrong format is work the human has to redo by hand.

!! **An agent is GIVEN what it needs, and is never sent looking.** A path into the installed
plugin is an invitation to read its neighbours and act on what it finds there. Nothing from
the installed plugin arrives as a path: the brief and the vocabulary are in the prompt. What
does arrive as a path is the run's own files -- the binder and the role's copy -- because those
are what it reads and fills, and a binder is too large to paste four times.

! **REFERENCE ONLY is a SELECTION, not a leftover.** Name the files that settle claims code
cannot: the repo's **decision record** (*"ruled"*, *"rejected"*, *"deferred"* have no code
oracle), any **authority document** holding dated facts, and -- where the repo stages prose out
of code -- the **extracted/mirror copy** of the files under review. Measured: an invented
ruling with zero entries in the record on its cited date; a retracted fact surviving in two
docstrings and one live constant; and a mirror tree that held the CORRECT text while the code
was backwards. The code still settles code claims -- a
disagreement with the mirror is itself a finding.

**Check each copy when the agent returns**, before the fold:

```bash
python <skill>/scripts/comment-review.py check --edit-copy <run-dir>/copies/<stage>_<role>_<n>.json \
  --binder <run-dir>/binder.json --repo .
```

It names everything the fold would send back -- a slot left null, a mark that will not read, a
claim quoting a sentence that is not in its paragraph, a cite whose line does not match, a
`raw_text` that is not the one the slot was seeded with -- and exits 0 only when there is
nothing. The brief tells each role to run the same command before it returns, so a copy that
still fails here is one the role did not check.

!! **A COPY THE CHECK REFUSES GOES BACK TO ITS OWN ROLE WITH THE LINES IT PRINTED, never
repaired by you.** A mark you fixed is a finding you authored. Send it back once with the
reasons; a role that returns it still failing is reported in the proposal as a role that did
not answer, and the fold runs without that copy.

Overlap between roles is **signal**: a claim one affirms and another refutes is carried
forward by the fold for the chief to rule on, never tie-broken by count. ! **A single-role run
ratifies falsehoods** -- one role reading a false absence claim writes that it is true, where
another refutes it by grep.

## Stage 5 -- COLLATE and CAP: one mark per place, at FULL LENGTH

!! **Run THE COLLATOR before you rule on anything** -- it reads every copy against the binder
and against the others', refuses what it cannot verify, and folds what the roles agreed on. It
is the gate between MARK and the chief's ruling:

```bash
python <skill>/scripts/comment-review.py collate --stage 4 --binder <run-dir>/binder.json --repo . \
  --topology <run-dir>/topology.toml \
  --edit-copy <run-dir>/copies/4_ownership-context_1.json --edit-copy <run-dir>/copies/4_block-context_1.json \
  --edit-copy <run-dir>/copies/4_function-context_1.json --edit-copy <run-dir>/copies/4_module-context_1.json \
  --out <run-dir>/chief0.json --proof-out <run-dir>/proof0.json --batch-out <run-dir>/batch1.json
```

Pass one `--edit-copy` for every file `distribute` printed -- a role split three ways is three.

**Read its exit code, and act on it before reading anything else:**

| exit | it means | what you do |
|---|---|---|
| `0` | every place the roles marked resolved on its own | go on; `chief0.json` is the chief's copy |
| `1` BROKEN | a copy broke a rule, or the set cannot be reconciled -- nothing written | every line it printed names a role and a place; send each back to that role, re-check, re-run |
| `2` UNREADABLE | a file is not what it says | fix the invocation |
| `3` REREADS, `4` ESCALATIONS | places carried forward -- the roles did not agree | **rule at max turns**, below |
| `5` DRIFT, `6` COVERAGE | a returned `raw_text` is not the seeded one, or a role left places unruled | the chief's copy is written; the printed places go back to their role once; say in the proposal what was left short |
| `7` `CARRIED_AND_UNRULED` | places carried forward, and a role left a place unruled | the printed unruled places go back to their role once, as for `6`; the carried-forward places are what a `3` or `4` asks of you |

Every line that opens with a role reads `<role> <place>: <reason>`, the place `(the copy)` for a
problem with the whole copy. **That is your work list for sending
back**, and a task agent reads it rather than the copies.

The lines under `for the chief -- each correct below drops words its claim never named:` are not
on that list, and no exit code reads them. Each reads `<role> <place>: its change drops '<word>',
which its claim never names` -- a `correct` whose change removes words beyond the clause its
claim quotes, a deletion no role argued for. Where the place is carried forward, rule on it
knowing that; where it settled, it goes to the author at 7a.

!! **A finding whose evidence does not resolve is not a finding.** Only `clean` is exempt,
because it cites no claim. **Never grade a review by reading its copy** -- self-reported
confidence has been measured not to discriminate a real finding from a fabricated one.

!! **It catches a fabricated FINDING, never a fabricated CLEAN -- and the clean is the easier
fabrication.** A copy reading `clean` on every slot accounts for every address, cites nothing,
and exits 0 having read no file at all. Nothing mechanical can separate that from a real pass,
because a negative leaves no artifact. **A green exit here is not evidence that anything was
read.**

! **The tool rules on ADMISSIBILITY, not on truth.** It cannot tell a correct instruction from
an incorrect one. The ruling at max turns, and the order below, remain yours.

**What the fold settles on its own.** A place every role read `clean` STANDS. A place one role
marked and no other role marked against is that role's mark, taken in. A place two or more roles
marked with byte-identical `change` text is their agreement, taken in -- agreement is the TEXT
alone, whatever instruction each used. Each is a `stet` on the master proof, and the chief's
copy carries the mark that stands.

**What it carries forward, and prints as `escalated` or `re-read`, one line each with the roles
that marked it:** two or more marks ruling on ONE sentence with different answers (an
escalation); marks on different sentences of one paragraph that could be composed, a lone mark
other roles marked against, every place an `add` touches, and every end of a `move` in a cycle
(a re-read). !! **A CONFLICT IS ON ONE SENTENCE. Two marks on two different sentences COMPOSE**,
and the fold composes them and carries the composition forward for a reading.

**What it sets aside:** a place any role marked `query` with the shape `human-review-necessary`.
It is UNSETTLABLE by the roles or by you, rides on the master proof, and is put to the author at
7a. A `query` of the other two shapes is that role abstaining from the place.

### A turn, when you are told to run turns

How many turns a run takes is what you are told, and the baseline is told none. Told a number
above zero, run up to that many turns between `collate` and `disposition`. Each turn sends the
last batch out and folds what comes back:

1. **Send each role the batch.** Every role the batch names gets the batch's absolute path, its
   own role name, the master proof the batch went out with, and a path to write its answers to.
2. **Check each role's answers when it returns**, before the fold. A file the check refuses goes
   back to its role with the lines it printed, as a copy does at stage 4:

   ```bash
   python <skill>/scripts/comment-review.py check --answers <run-dir>/answers1_<role>.json \
     --sent <run-dir>/batch1.json --role <role> --proof <run-dir>/proof0.json --repo .
   ```

3. **Fold them**, with one `--answers` for every role the batch named:

   ```bash
   python <skill>/scripts/comment-review.py turn --proof <run-dir>/proof0.json --binder <run-dir>/binder.json \
     --sent <run-dir>/batch1.json --answers block-context=<run-dir>/answers1_block-context.json \
     --answers function-context=<run-dir>/answers1_function-context.json \
     --proof-out <run-dir>/proof1.json --batch-out <run-dir>/batch2.json --repo .
   ```

`turn` exits the codes in the table above, and each asks of you what it asks after `collate`,
except that a place carried forward while a turn is left goes out in the next turn rather than
to your ruling. The next turn reads `proof1.json` and sends `batch2.json`; a turn that carries
nothing forward writes no batch, and there is no next turn to run. The last proof a turn wrote
is the one `disposition` closes.

### Ruling at max turns -- you are the copy chief

!! **THE BASELINE RUNS NO TURN.** `batch1.json` is what a turn would send back to the roles;
leave it. Every place still carried forward -- after `collate` in the baseline, after the last
turn otherwise -- is yours to rule now, once, and there are two rulings:

| answer | when | what it carries |
|---|---|---|
| `taken_in` | one side is right | `side`: the role whose text stands, or `original` to let the paragraph stand as it was -- the author is a side |
| `recast` | no side is right | `prose`: your own paragraph, as raw text, over every side |

Write them to `<run-dir>/dispositions.json` as a list -- `[{"address", "answer", "side", "reason",
"prose"}]`, `reason` owed on every one -- then close the proof:

```bash
python <skill>/scripts/comment-review.py disposition --proof <run-dir>/proof0.json --binder <run-dir>/binder.json \
  --repo . --dispositions <run-dir>/dispositions.json --out <run-dir>/chief.json --proof-out <run-dir>/final.json
```

`--proof` is the last proof written: `proof0.json` when no turn ran, the last turn's otherwise.

**`disposition` refuses a carried-forward place with no ruling, by name and with its roles, and writes
nothing** -- rule it and run again. Otherwise it prints what it wrote -- `<out>: the chief's
copy, <n> places` and `<proof-out>: the proof closed at turn <t> -- <n> determined, <m>
unsettlable` -- then one line per ruling, `<answer> <place>: <side> (<how>, turn <t>)`, then one
entry per unsettlable place: `unsettlable <place>: <role> asks the human -- <reason>`, with an
indented `and ...` line for a move's drop or add held there. A move held at both ends is one
entry, `unsettlable <origin> and <destination>: ...`, whose last line reads `and <role>'s move
drops the paragraph at <origin> and adds it at <destination>, one move -- <reason>`.
`chief.json` is the chief's `edit_copy`, one mark per resolved
place, and it is what stages 6 and 7 read. ! `--stage` is `4` throughout: the four roles ran
in one stage.

!! **A `taken_in` is a ruling, not a count.** Any `correct` outranks every `clean`: three roles
finding nothing does not soften one role finding a falsehood, because they were not looking for
the same thing. **Two placement marks naming different destinations: `ownership-context`'s
governs** -- that is the precedence the role holds, not a tie-break.

!! **Before you take a side or recast, read the code the paragraph sits with.** Rule in this
order, because each step depends on the one above being settled:

1. **`query`** -- resolve it or escalate it. An unresolved claim cannot be corrected, patched or
   dropped, because you would be editing something nobody has read.
2. **Every `move`, and every `drop`** -- settle WHERE the prose lives before touching what it
   says. ! **Placement comes first because a claim is measured against the code it sits with**
   -- correct it where it does not belong and you have corrected it against the wrong code.
3. **`correct`** -- fix truth, on what remains, **at the anchor it now sits on**. !! A `correct`
   that travelled with a `move` is applied AT THE DESTINATION and re-derived there, never against
   the code the prose left.
4. **`patch`** -- fix wording, on text now known to be true. ! **Never before step 3:** a
   `patch` on a false sentence polishes the wording of a falsehood and retires the finding.
   That is laundering, and this order is what prevents it.
5. **`add`** -- insert at the stated anchors.

! **`drop` against `correct` or `patch` on the same sentence is a contradiction**, not a merge --
one role says the sentence should not exist and another says it should exist and be fixed.
Nothing composes those; it is a `taken_in` or a `recast`. !! **`move` against either of them
COMPOSES.** Relocation and a truth fix are a SEQUENCE, and the fold composes them.

! **Two marks quoting the same sentence in different files are ONE finding.** A pass edits where
it is reading, fixes the copy in front of it, and manufactures a disagreement with the one it
never opened. The collator cannot see this for you -- it keys on the ADDRESS, and the same
sentence copied into two files is two different paragraphs it can never relate.

! **Load [`references/residue-check.md`](references/residue-check.md) before you recast
anything** -- the check is defined there, and this is the first stage that owes it. Stages 6
and 7b re-run the same check against the same original; none of them may check against the
previous edit. Run it on **the whole paragraph once** -- not once per mark. The check compares
against the original, and the original was one paragraph. ! A `taken_in` text was written by a
role that never ran it; run it over that too.

!! **THE SENTENCE YOU PROPOSE TO KEEP IS A FINDING YOU HAVE NOT RAISED.** Before any `patch`
or `move`, verify the retained clause against the code: a path it cites is tracked -- present but
untracked is unverifiable, not dangling -- a name it uses is in the name corpus, and a count
re-derives from its population. The reviewer keeps the
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

! **A paragraph that ends mid-clause is a finding, and its instruction is `correct`.** A run whose last
sentence stops mid-air -- a severed trailing comment, a `move` that cut a sentence in half -- is
neither checkable nor necessary, so the matrix routes it to `drop`, deleting the pointer instead
of repairing it. Restore the sentence.

! **Length is not your question at this stage.** A paragraph that is true, local and load-bearing
is finished here however long it is; COMPACT shortens it only if a cap applies. A run that
returns mostly `clean` is a good outcome, not a lazy one.

**Two shapes a length rule cannot express.** A comment claiming *"pinned by X"* **licenses
future edits** -- ! the dangerous cell is a deletion justified by coverage nobody can find,
which reads as safe for exactly that reason. Grep the cited name, every time. And a rule
**stated in several places with no owning definition** is why the comments got long.

**A `#` comment is governed by LENGTH; a docstring by FORMAT.** Long is not a violation; what
fails is a body carrying what is not documentation -- a date, a quotation, a retraction, a
rationale paragraph, a claim about callers or coverage -- **at any length**. **Acquit on what
a body carries, never on its length**: a two-line docstring whose summary runs on is still a
finding.

Invisible to any counter: a **trailing comment carrying past its own line** (a `move` to the
line above); a **paragraph split by an inserted statement**, where only the half still
talking about what came before is the finding; **the wrong half surviving** -- check what
SURVIVED, not what went; **refactoring drift**.

## Stage 6 -- COMPACT: only if there is a cap

**If no cap applies, the run SKIPS this stage entirely.** Say so: the prose is correct, and
absent a cap "long" is not a defect.

If there is a cap, and only once **every** paragraph on the chief's copy is CORRECT,
dispatch `comment-review:comment-review-compact` with the narrow input contract
below, and paste [`references/compact.md`](references/compact.md) into its prompt
whole. Its input is each mark's `change` on `chief.json`, and its output replaces that
`change` -- nothing else on the copy moves.

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
restatements into one -- and none of that is settled until every paragraph is ruled. `compact.md`
carries the argument and the per-paragraph procedure.

**Stage 8 is the one reader of stage 6's output before the author.** Stage 7a presents it and
rules on nothing; stage 8 reads the galley 7a sets from it, and what it finds goes to the author
with the proposal.

## Stage 7a -- APPROVAL: present the FINAL text, then stop

**Set the proposal as a GALLEY first** -- a copy of each page with the chief's marks applied,
nothing under the repo touched -- and prove it changed no code:

```bash
python <skill>/scripts/comment-review.py proof --repo . --copy <run-dir>/chief.json --out <run-dir>/galley
```

**`--out` must not already exist**, and it holds only the pages `proof` lists as drafted, one
`<path> -> <draft>` line each, and no other file of `--repo`; a galley is discarded with the run. ! **`proof` REFUSES rather than guesses.**
It exits nonzero and NAMES what refused -- an input that fails to read prints `CANNOT READ`,
one that does not match its shape prints `CANNOT READ THE COPY: <reason>`, and a bad `--out`
prints `REFUSED: --out <reason>` -- each at exit **2**. A refusal further into the chain exits **1**: a
moved address space prints `REFUSED: the address space moved -- <reason>`, and a step on one page
prints `REFUSED at <step>: <where> -- <reason>`. Read what it printed, rather than a list you remember.

**`proof`'s re-read of each page it drafts is the compile step.** It reads the drafted page back
and refuses one whose text at a place is not the text approved for it, so a docstring a role set
at the wrong indentation is refused here, by name.

**Then dispatch stage 8 on the proof** (below), and present once its findings are back.

Then present, grouped by instruction, most consequential first, in **five parts**
(`INSTRUCTION / PARAGRAPH / CLAIM / REASON / CHANGE`) -- the mark minus the fields only the
collator reads -- replacement text inline for every `correct` / `patch` / `add`, and the galley's
diff for the whole page, which this prints:

```bash
python <skill>/scripts/comment-review.py taken_in --original . --revise <run-dir>/galley
```

State **raised / clean**, which places you ruled at max turns and how, and the longest paragraph
that will remain.

!! **THE UNSETTLABLE PLACES ARE THE AUTHOR'S, AND THIS IS WHERE THEY ARE ASKED.** `disposition` printed
each one with the role that raised it and its reason; put every one to the author here, after
everything else, as the questions they are. Nothing is proposed for them but a held move: an
entry naming a move's drop and its add is one move, put to the author as the paragraph leaving
its origin and arriving at its destination, with the text it carries -- the `change` of that
place's `add` in `final.json`'s `unsettlable` list -- and approved or refused whole.

Put each settled `correct` from stage 5's `for the chief` list to the author here too, with the
words its change drops.

**The proposal ends here** -- nothing further is written until the author rules.

!! **What you show IS what gets written.** If stage 6 ran, show the COMPACTED text -- never the
full-length version with a note that it will be shortened. The author rules once, quickly, and
on the assumption that the text in front of them is the text that lands.

**Hand back the STYLE SHEET**, updated with every decision this run made -- the sheet is how the
next pass avoids re-deciding, and it is worthless if it stays in your head.

**Approval is the go-ahead for 7b.** "Yes", "do it", "continue" -> load `references/write.md`
and follow it. You edit nothing under the repo either: 7b sets the approved text in temporary
files.

## Stage 7b -- WRITE: set the approved text for the author to diff

On approval, load [`references/write.md`](references/write.md) and follow it. It sets the
approved text in temporary files with `proof`, for the author to diff, and puts nothing over the
real files; it carries the residue check and the write rails. Do not write from memory.

! **Stage 7b writes the APPROVED text verbatim.** It does not shorten, re-word or re-judge --
every one of those questions was settled upstream, and re-opening one here writes something
the author never saw.

## Stage 8 -- REVIEW: the proof, before the author sees it

Once 7a has set the galley, and before you present, dispatch
`comment-review:comment-review-review` with the proof -- the galley directory and the `<draft>`
pages `proof` listed -- and the style sheet, and paste [`references/review.md`](references/review.md) into its
prompt whole. Its findings go into the proposal at 7a.

The read holds for a blanket approval only: where the author approves some changes and not
others, the pages 7b sets are pages stage 8 never read.

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
