---
name: comment-review
description: Review the comments and docstrings in the files a change touched, across four editorial roles -- ownership-context, block-context, function-context, module-context -- using parallel read-only subagents, and return each finding as instruction/location/summary/finding/change for the human to rule on. Use this whenever comments or documentation are the subject -- after finishing a task that added or edited commentary, when a file's comments have drifted from what the code now does, when someone says a comment is too long or out of date or "isn't this history", when reviewing a diff specifically for its prose rather than its logic, before a docs or comment burn-down, or when asked to check whether a module still reads as one module. Trigger on phrasings that never say "comment review" -- "these comments are getting out of hand", "does this docstring still match", "is this comment still true", "clean up the narration in this file", "why does this file need so much explaining" all mean run this. It is NOT /simplify (which reviews code structure) and NOT /code-review (which hunts correctness bugs). The reviewers mark a copy; the human reads each changed page as a diff against its original, what they accept is written into the working tree, and a proofreader then reads the finished pages.
---

# comment-review

`/comment-review [cap] [target] [style]`

## What you are doing

You are the task agent and the **copy chief** of an editorial board. The manuscript is the
comments and docstrings in the files a change touched. Four editors each read it in one
editorial role -- the notes editor, the fact-check editor, the line editor and the
developmental editor -- and mark it. You fold their marks into one set of edits, rule where they
differ, have the result set as a proof, and show the author each page beside its original.
The text the author accepts is written into the working tree, and a proofreader then reads
the finished pages.

The author approves quickly and trusts the proposal. You are free on form -- wording,
placement, length -- and every change to what a sentence claims carries the line of code
that settles it.

A helper program does the mechanical work. `<skill>` is the directory holding this file;
take it from the absolute path you were given. Every command runs through
`<skill>/scripts/comment-review.py`, and `--help` after a command's name gives its flags.
Give each run its own `<run-dir>`, and write every file with the command's `--out` flag.

**Your vocabulary.** Read the `[definitions]` entries of
`<skill>/scripts/comment_review/references/vocabulary.toml` whose keys are listed under
`task-agent` in `[roles]`, plus the `all` list. Each of those words carries that one meaning
here.

**What you are given.** `cap` is the most lines one comment paragraph may hold; use the number given,
or the one the repo publishes, and when neither exists the run has no cap. `target` is a path
that sets the scope in place of the diff. `style` is the style sheet from an earlier run.

## The steps

| # | stage | who acts | what exists at the end |
|---|---|---|---|
| 1 | project determination | you | scope, cap, style sheet, run context |
| 2 | gather | `gather`, `topology` | the binder and a verified topology |
| 3 | find references | `referrers` | the `REFERENCE ONLY` list |
| 4 | mark | the four reviewers | four checked edit copies, and each role's freeform copies and findings |
| 5 | collate and rule | `collate`, you, `disposition` | a closed proof, the chief's copy and the freeform drafts |
| 6 | compact, when a cap applies | the condenser | a closed proof whose text fits the cap |
| 7a | set and present | `proof`, then you | the proof pages and the proposal in front of the author |
| 7b | write | the author, then you | the accepted text in the working tree, its code proved unchanged |
| 8 | review | the proofreader | a reading of the finished pages and freeform files |

## What passes between the stages

Each stage hands the next one of these; your vocabulary defines each one:

| structure | made by | read by |
|---|---|---|
| **binder** | `gather` | `topology`, `distribute`, `check`, `collate`, `addresser` |
| **topology** | `topology` | `distribute`, `collate` |
| **edit copy**, one per dispatch | `distribute`, filled with `mark` | `check`, `collate` |
| **master proof** | `collate`, `turn`, `disposition` | `turn`, `disposition`, `proof` |
| **batch** | `collate`, `turn` | the roles, in a turn |
| **dispositions** | you | `disposition` |
| the copy chief's **edit copy**, one mark per resolved place | `collate`, `disposition` | you, when you present |
| **docket** | `proof`, from a closed master proof | the compositor |
| **schedule**, one per page in the docket | `proof` | the compositor |
| **alteration**, one per place in a schedule | `proof` | the compositor |
| **proof**, the pages as set | the compositor, through `proof` | the author, stage 6, stage 7b |
| a role's freeform copies and `findings.json` | the reviewers | you, at stage 5 |
| `freeform/draft/<path>`, one per freeform file changed | you, at stage 5 | stage 7a, the author, stage 7b |
| `freeform/settled_<stage>.json` | you, at stage 5 | you, at the 7a audit and when the author asks why |

`proof` transcribes the closed proof into a docket, and the compositor sets each schedule's
alterations onto a copy of its page. `proof --to-docket <file>` writes the docket out without
setting it.

## The goals of the steps

1. **Project determination** records the facts about this repo that every later stage uses.
2. **Gather** turns each Python and Rust file into a page of numbered places, and lists every
   other source file as freeform. Every mark cites a place by its address, such as
   `pkg:core.py@b3`.
3. **Find references** lists the files that name the files under review, so the reviewers can
   check what those files say about them.
4. **Mark** gives each paragraph four independent readings. Each role reads alone, so two
   roles that agree corroborate each other.
5. **Collate** settles what the roles agreed on. You rule on the rest, so every place ends
   with one text that is true of the code beside or below it, at whatever length that takes.
6. **Compact** shortens the paragraphs on pages that run over the cap, keeping every true,
   necessary and checkable sentence. The copy chief holds a freeform comment to the cap at stage 5.
7. **Set and present** puts the final text on copies of the pages, proves the code is
   byte-identical, and gives the author a diff of each page against its original. A freeform file
   is set on a draft, formatted and compiled there, and audited hunk by hunk instead of proved.
   **Write** puts what the author accepted into the working tree.
8. **Review** reads the finished pages as a reader meets them, and catches anything the
   author and the run let through.

The author rules once, on the text that will actually be written.

## How you do the steps

### Stage 1 -- project determination

Work from the git repository at the repo root, and pass `--repo` to every command that takes it.

1. **Pre-edit ref.** Record `HEAD` when the files in scope have no uncommitted change, and
   the commit `git stash create` prints otherwise. Stage 7b proves the code against it.
2. **Scope.** Use `target` when given. Otherwise take `git merge-base HEAD <upstream>` and list
   `git diff --name-only <base>..HEAD`, plus `git diff --name-only HEAD` for uncommitted work.
   When there is no upstream, scope from `git diff --name-only HEAD`. Say in the proposal which
   scope you used.
3. **Cap and width.** Find what the repo publishes -- a contributing guide, `.editorconfig`, a
   formatter config -- and how it counts. Record where you found each, and which work markers
   (`TODO`, `FIXME`, ...) it exempts. When the repo cites a test that enforces the cap, confirm
   the test exists, and report whether it does.
4. **Style sheet.** Read `style` when given; otherwise start one. It records the width stage 1
   found, the repo's dialect, the capitalisation of domain terms, its citation form, and one
   template for each documentation format the tree actually uses: module docstring, function docstring and,
   where the repo is consistent, comments. Write each template out with its slots, measured
   from the docstrings in the tree.
5. **Check and format commands.** Find how the repo proves its code compiles -- its CI config,
   Makefile, `package.json` or `pyproject.toml` -- and record one command per language in scope,
   for example `python -m compileall -q .`, `tsc --noEmit`, `cargo check`, `go build ./...`.
   Stages 7a and 7b run it. For each freeform language, record the repo's formatter as a command
   that rewrites the files it is given, for example `prettier --write`, `gofmt -w`. Record `none`
   where the repo has no such command.
6. **Reviewers.** Confirm the agents `comment-review:comment-review-*` resolve. When they are
   unavailable, dispatch general-purpose agents in their place, giving each the absolute path
   of its role file from the installed plugin, and say so in the proposal.
7. **Language servers.** Where you have an LSP tool, call `documentSymbol` once on one file of
   each language in scope, and record which languages answered. Where you have no LSP tool,
   record that no probe was possible.

### Stage 2 -- gather, and the topology

```bash
python <skill>/scripts/comment-review.py gather --repo . --out <run-dir>/binder.json <paths...>
```

The gather reads the files a reader claims; `gather --languages` lists those languages. It lists
every other source file under `freeform` in the binder, unopened, and prints the first twenty
under `FREEFORM`. A named file that is neither exits nonzero, and a walked one prints under
`PASSED OVER`. When the default scope named it, take it out of the paths, gather again, and report
it as passed over. Report every gap it prints, and the freeform list.

The gather also prints one line on stderr for each detached documentation it read, in the form
`warning: <path>:<line>: detached documentation (owner on line <n>)`, or `(owner: module)` when
the owner is the module. The documentation starts at `<line>` and is
read as a comment. Ask the author about each line with `AskUserQuestion`, showing that comment
and its owner, the anchor it was written for, and offering two answers: move it to the owner's
`a` cue, or leave it where it is. Record each answer in the style sheet, and continue the
run whatever the answer is.

Then build the topology: one stage, `4`, with every role split so each dispatch holds five
files at most. `<n>` is the number of pages and freeform files together, divided by five, rounded
up.

```bash
python <skill>/scripts/comment-review.py topology --build --binder <run-dir>/binder.json --out <run-dir>/topology.toml \
  --stage 4=ownership-context/<n>,block-context/<n>,function-context/<n>,module-context/<n>
```

`--build` verifies what it writes and exits 0 when the topology fits the binder. On exit 1 it
prints one misfit per line; change the `--stage` value and build again.

To look up a place, ask the addresser; each series is counted separately:

```bash
python <skill>/scripts/comment-review.py addresser --binder <run-dir>/binder.json --file <path> --line <n> --series a|b|c|f
python <skill>/scripts/comment-review.py addresser --binder <run-dir>/binder.json --resolve <address>
```

### Stage 3 -- find references

```bash
python <skill>/scripts/comment-review.py referrers --repo . <paths under review...>
```

It prints every tracked file that names a file under review. From these, together with the
repo's decision record, any document holding dated facts, and any mirror copy of the files
under review, choose the `REFERENCE ONLY` list.

### Stage 4 -- mark

Seed one edit copy and one received binder per dispatch:

```bash
python <skill>/scripts/comment-review.py distribute --topology <run-dir>/topology.toml --stage 4 \
  --binder <run-dir>/binder.json --out-dir <run-dir>/copies
```

It prints each edit copy, named `4_<role>_<n>.json`, and its received binder,
saved as `copies/binders/4_<role>_<n>.json`, with the count of freeform files dealt to it.
Dispatch one agent per edit copy:

| desk | agent | its question |
|---|---|---|
| notes editor | `comment-review:comment-review-ownership-context` | does this comment belong to the anchor it sits on? |
| fact-check editor | `comment-review:comment-review-block-context` | is every claim in this paragraph true of the code it sits with? |
| line editor | `comment-review:comment-review-function-context` | does the commentary match what the function is for? |
| developmental editor | `comment-review:comment-review-module-context` | do the comments say this is one module? |

All four roles run on every review. Each agent's prompt holds, in this order:

1. [`references/reviewer-brief.md`](references/reviewer-brief.md), pasted whole.
2. That role's vocabulary: the `[definitions]` entries of
   `<skill>/scripts/comment_review/references/vocabulary.toml` whose keys are listed under the
   role in `[roles]`, plus the `all` list, read fresh from that file.
3. The packet, every section filled -- `UNAVAILABLE` is a complete answer:
   - `REPO ROOT` -- absolute path
   - `BINDER` -- absolute path of this agent's received binder
   - `EDIT COPY` -- absolute path of this agent's own copy
   - `FILES UNDER REVIEW` and `REFERENCE ONLY`
   - `STYLE SHEET`, templates included
   - `LANGUAGE SERVERS` -- which languages answered at stage 1
   - `FREEFORM DIR` -- absolute path of `<run-dir>/freeform/4_<role>_<n>`, this agent's own
     directory
   - `FREEFORM COPIES` -- the paths a later stage starts from, below
   - `FREEFORM SHEET` -- [`references/freeform.md`](references/freeform.md), pasted whole when the
     received binder lists a freeform file

An agent whose received binder lists no page takes a shorter prompt: `references/freeform.md` pasted
whole in place of the brief, then its vocabulary, then a packet of `REPO ROOT`, `FILES UNDER REVIEW`,
`REFERENCE ONLY`, `STYLE SHEET`, `FREEFORM DIR` and `FREEFORM COPIES`. It has no edit copy, so it has
no `check` to run.

Each agent fills its copy in place and runs `check` on it. An agent dealt a freeform file also
returns the paths of its `findings.json` and its copies. When an agent returns, run the same
check yourself:

```bash
python <skill>/scripts/comment-review.py check --edit-copy <run-dir>/copies/<file> --binder <run-dir>/copies/binders/<file> --repo .
```

Exit 0 means the copy is ready to fold. Exit 5 means its only findings are human questions,
which stage 5 asks. On any other exit, send the copy back to its own agent with the lines
`check` printed; the agent corrects its own marks. When a copy still fails on its second
return, fold without it and report that role as unanswered.

For each freeform file, confirm the agent's `findings.json` holds that path with its `swept`
list. Send a missing path back to its agent. When it is still missing on the second return, report
that role as unanswered on that file.

Roles in one stage work blind to each other. A role in a later stage starts from what the stage
before left: settle that stage's findings as stage 5 says, copy `<run-dir>/freeform/draft/` to
`<run-dir>/freeform/base_<stage>/`, and hand those paths in `FREEFORM COPIES`, because a revise root
holds pages only and that stage's binder lists no freeform file.

### Stage 5 -- collate, and rule as copy chief

Repeat `--edit-copy` and `--received-binder` for each pair, keeping the binder
paths in the same order as the copy paths.

```bash
python <skill>/scripts/comment-review.py collate --stage 4 --binder <run-dir>/binder.json --repo . \
  --topology <run-dir>/topology.toml \
  --edit-copy <one returned copy> --received-binder <its received binder> \
  --out <run-dir>/chief0.json --proof-out <run-dir>/proof0.json --batch-out <run-dir>/batch1.json
```

Act on the exit code first:

| exit | meaning | what you do |
|---|---|---|
| `0` | every place settled | `proof0.json` is the closed proof; settle any freeform findings, below, then go to stage 6 or 7a |
| `1` | the round rolled back; each line names `<role> <place>: <reason>` | send each line to its role, which withdraws with `mark --withdraw --address <place>` and marks again; re-check and re-run |
| `2` | a file could not be read | correct the invocation |
| `3`, `4` | places carried forward -- `composed`, `contested` or `open` | rule on them, below |
| `5` | human questions are owed | ask them, below, then re-run with `--human` |

Keep the path of the latest committed proof and the chief's copy. A closed proof
can come from `collate`, `turn` or `disposition`; use that file wherever
`<closed-proof>` appears below. A refused round supplies no new proof.

A place is settled when every role that read it proposed the same text or answered `clean`;
`collate` prints each as `stet <place>`. The lines under `for the chief` name a `correct`
whose change removes words its claim never quoted; weigh that when you rule, and show it to
the author at 7a.

**Human questions.** Each line `asks the human <at>: <role> -- <question>` is one question.
Ask it with `AskUserQuestion`, showing the paragraph at `<at>` (both ends for a move) and the
query's `attempted` text from the role's copy. A query whose `settles` reads `code concern` is
a code concern: offer the author three answers -- `add a TODO` (first, as the default),
`not a concern` and `leave it` -- and record the one chosen; the role knows what each asks of
it. Record each answer in `<run-dir>/human.toml`:

```toml
[[answer]]
role = "<role>"
at = "<place or move>"
question = "<question>"
answer = "<the human's answer>"
```

Send the asking role its `[[answer]]` sections with its copy; it replaces its query with a
mark. Then re-run `collate` with the same inputs plus `--human <run-dir>/human.toml`.

**Turns.** Run turns only when you are told a number above zero. Each turn sends `batch<t>.json`
to every role it names, with the proof and a path for its answers; checks each returned file
with `check --answers <file> --sent <batch> --role <role> --repo .`; and folds them with
`turn --proof <last proof> --answers <role>=<file> ... --proof-out <run-dir>/proof<t>.json
--batch-out <run-dir>/batch<t+1>.json --repo .`. `turn` exits with the same codes. The turns
end when a turn writes no batch or the count is reached.

**Ruling.** Rule on every place still carried forward, reading the code beside or below each paragraph
first. Rule in this order, because each step builds on the one before:

1. `query` -- resolve what it asks.
2. `move` and `drop` -- settle where the prose lives. A move prints as
   `<placement> <origin> -> <destination>`, and its two ends are *to come*: they wait on the
   placement and take no ruling. Read both ends against their code first: taking a move in says
   the origin reads right without the snippet and the destination reads right with it. Rule the
   placement with a ruling that carries `to`: `taken_in` with `side` the mover, which moves the
   paragraph, or `original`, which keeps it where it is.
3. `correct` -- fix what is false, against the code at the place the prose now sits.
4. `patch` -- improve the wording of text now known to be true.
5. `add` -- insert new text at its anchor.

Each ruling is one of two answers:

| answer | use it when | it carries |
|---|---|---|
| `taken_in` | one side is right | `side`: the role whose text stands, or `original` to keep the paragraph as it was |
| `recast` | you write the paragraph yourself | `prose`: your paragraph, as raw text |

A `correct` outranks any number of `clean`s. Where two placements name different destinations,
`ownership-context`'s governs. Verify every clause you keep: each path it cites is tracked,
each name exists, and each count re-derives.

Write the rulings to `<run-dir>/dispositions.json` as a list of
`{"address", "answer", "side", "reason", "prose"}`, with a `reason` on each and `"to"` added on
a placement ruling (`address` the origin, `to` the destination), then close the proof:

```bash
python <skill>/scripts/comment-review.py disposition --proof <last proof written> \
  --dispositions <run-dir>/dispositions.json --out <run-dir>/chief.json --proof-out <run-dir>/final.json
```

It names any move or carried-forward place still unruled, and writes when every one has a ruling.
A placement ruling moves the paragraph or keeps it, and each end is then read as an ordinary
place; when `disposition` exits `3` or `4`, those ends are carried forward. Rule them from the
code at each end, and run `disposition` again with the proof it just wrote. Use a
fresh output filename for each ruling round. Its proof becomes `<closed-proof>`
once it exits `0`.

**Freeform findings.** Read each role's `findings.json` from its path, and diff each of its copies
against the file it copied:

```bash
git diff --no-index -U0 <base> <FREEFORM DIR>/<path>
```

`<base>` is the file's `base_<stage>` copy at a later stage and `<path>` otherwise. The command exits
1 when the files differ. Then, working from `references/freeform.md`:

1. Match each hunk to a finding, and each finding but a `query` to a hunk. A hunk belongs to the
   finding whose comment its old-side lines fall within. An insertion, `-N,0`, belongs to the `add`
   whose `at` is line N or N+1. Send anything unmatched back to its role.
2. Open every `source` and confirm it says what the finding claims. Send a finding whose source
   fails back to its role.
3. Ask each `human-review-necessary` query as a human question, above. Settle it from the answer,
   writing the edit a role would have made. A query of either other shape defers, as on a page.
4. Copy the base of each file with a change that stands to `<run-dir>/freeform/draft/<path>`, unless
   a stage before already drafted it.
5. Take the changes to one comment together, `correct` before `patch`, and rule as above: one side's
   text, the original, or your own. Write the result into the draft. Two roles changing one comment
   end as one edit.
6. Read each edit against the code around it, and hold it to the cap.
7. Read each freeform file for a comment over the cap that no finding reached, and shorten it in
   the draft as a `patch`.

Anything sent back that still fails on its second return is left out, and its role is reported as
unanswered on that finding.

Write the result to `<run-dir>/freeform/settled_<stage>.json`, a list of the findings' own shape with
`roles` added to each, naming every role whose change stands in it, and `at` the line in the
draft, holding only the changes that stand. A run with no pages prints `0 places` at `collate` and
carries on.

### Stage 6 -- compact, when a cap applies

Stage 6 runs as a second stage over the proof pages, and a run with no pages skips it. Set them
from the closed proof into `<run-dir>/proof4` with `proof --repo . --proof <closed-proof> --out
<run-dir>/proof4`, then gather them as revise 1, naming pages alone, because a revise root holds
no freeform file:

```bash
python <skill>/scripts/comment-review.py gather --repo <run-dir>/proof4 --revise 1 --out <run-dir>/binder6.json <paths...>
```

Add this stage to `topology.toml`, with `cap` set to the run's cap:

```toml
[[stage]]
name = "6"
kind = "editorial"
reads = "revise:4"
cap = <cap>
series = ["b", "c"]
admits = ["patch", "drop", "add", "clean", "query"]
  [[stage.dispatch]]
  role = "block-context"
```

Seed it with `distribute --topology <run-dir>/topology.toml --stage 6 --binder
<run-dir>/binder6.json --revise <run-dir>/proof4 --out-dir <run-dir>/copies`.
Each received binder and edit copy holds only the comment paragraphs over the
cap. Dispatch `comment-review:comment-review-compact` with its edit copy and
received binder, `references/compact.md` pasted whole, the style sheet and the
cap. Check the copy against its received binder, then run `collate --stage 6`
with the received binders paired with the copies and rule as in stage 5. The
closed proof this produces is the one stage 7a sets.

### Stage 7a -- set and present

```bash
python <skill>/scripts/comment-review.py proof --repo <stage-root> --proof <closed-proof> --out <run-dir>/proof
```

`<stage-root>` is the root the closed proof's binder was gathered from: the repo
root for stage 4, or the proof pages root for stage 6. Keep the drafts from every
stage; when a later stage drafts a page again, its draft is the one to present
and write. Pages unchanged by that stage keep their earlier drafts.

Use a fresh `--out` directory each time. `proof` prints one `<path> -> <draft>` line per page
it set. It reads each drafted page back and proves its code byte-identical to the original.
When it refuses, it prints what refused and where; read that, fix the input, and set again.

**Freeform files.** Check the drafts stage 5 wrote, in this order:

1. `git worktree add <run-dir>/freeform-build <pre-edit ref>`, run the stage 1 check command there,
   and keep its result as the baseline.
2. Copy each draft over its `<path>` in the worktree, run the formatter on those paths, and run the
   check command again.
3. Copy the formatted files back over the drafts, then `git worktree remove --force
   <run-dir>/freeform-build`.

The check passes when the second run passes everything the baseline passed. When it fails
something the baseline passed, hold the run at this stage: edit the draft until it passes, and run
the check again. When the failure comes from code no finding touched, bring the author the output
and the files it names. A language with no formatter or no check command, one whose command cannot run in the
worktree, or one whose baseline passes nothing is reported as not verified.

Then audit each draft:

```bash
git diff --no-index -U0 <path> <run-dir>/freeform/draft/<path>
```

Every changed line belongs to a settled finding, and every settled finding has its change. Any
other change holds the run at this stage: edit the draft until the change is gone, and audit it
again. Nothing is presented until the audit passes. The command exits 1 when the files differ.

Present to the author, grouped by instruction, most consequential first. Use the
closed proof's decided text and the drafts for the proposed result. The chief's
copy supplies `INSTRUCTION / PARAGRAPH / CLAIM / REASON`; show the current
`CHANGE` from the draft inline. A turn writes a proof without refreshing the
chief's copy, so check its entries against the closed proof before presenting.
Show each freeform draft whole. When the author asks why a change was made, answer from
`settled_<stage>.json`.
Then give:

- one command per page and per drafted freeform file, to read it beside its original:
  `git diff --no-index <path> <draft>`
- the count of places raised and places clean, and `N swept, M raised` per freeform file
- which places you ruled, and how
- the longest paragraph that will remain
- the scope source, the roles that ran, and the language servers that answered
- for freeform files: the check baseline and result, the formatter, the hunks audited, and each
  language not verified
- the updated style sheet, holding every decision this run made

The author may edit a freeform draft line by line. Close by asking the author to accept all of
it, accept the places they name by address and the freeform files they name by path, or accept
none.

### Stage 7b -- write

Load [`references/write.md`](references/write.md) and follow it. It compiles the accepted
drafts in a temporary worktree, writes them into the working tree, and proves their code
unchanged. `git diff` then shows the author exactly what the run changed.

### Stage 8 -- review

Dispatch `comment-review:comment-review-review` with the pages and freeform files written at 7b
and the style sheet, and paste [`references/review.md`](references/review.md) into its prompt
whole.

Bring its findings to the author, who chooses for each page and freeform file: done, a new comment-review round
with the findings as its input, or an immediate fix. Start the round or make the fix only on
the author's answer.

## What to expect from the other agents

**The four reviewers** each return their edit copy filled in place, one mark per paragraph
they read, a clean `check` or exit 5, and for a freeform file the paths of their findings and
copies. A mark carries one of seven instructions:

| instruction | the reviewer found | its payload |
|---|---|---|
| `clean` | nothing to report from its role | -- |
| `query` | a claim it could not settle | the question, what it attempted, what would settle it |
| `drop` | a sentence that is true and unneeded | the sentence |
| `correct` | a false sentence | the false clause, the true clause, the source that settles it |
| `patch` | a true sentence, badly worded | the old wording and the new |
| `add` | prose that is missing | the text and the anchor it belongs to |
| `move` | prose that belongs at another place | the text and its destination address |

A `query` shaped `human-review-necessary` is a question for the author, which you ask at
stage 5. Two marks on the same sentence in different files are one finding; rule them
together.

**The condenser** returns its edit copy, checked, each over-cap paragraph patched shorter,
marked `clean` with what holds it at length, or holding a question for the author.

**The proofreader** returns each page and freeform file as done or with the sections to bring to the author,
and lists separately every defect that predates this run.
