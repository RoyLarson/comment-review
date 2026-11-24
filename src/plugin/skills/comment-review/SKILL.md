---
name: comment-review
description: Review the comments and docstrings in the files a change touched, across four editorial roles -- ownership-context, block-context, function-context, module-context -- using read-only subagents in the stages a topology configures, by default ownership-context alone and then the other three in parallel, and return each finding as instruction/location/summary/finding/change for the human to rule on. Use this whenever comments or documentation are the subject -- after finishing a task that added or edited commentary, when a file's comments have drifted from what the code now does, when someone says a comment is too long or out of date or "isn't this history", when reviewing a diff specifically for its prose rather than its logic, before a docs or comment burn-down, or when asked to check whether a module still reads as one module. Trigger on phrasings that never say "comment review" -- "these comments are getting out of hand", "does this docstring still match", "is this comment still true", "clean up the narration in this file", "why does this file need so much explaining" all mean run this. It is NOT /simplify (which reviews code structure) and NOT /code-review (which hunts correctness bugs). The reviewers mark a copy; the human reads each changed page as a diff against its original, what they accept is written into the working tree, and a proofreader then reads the finished pages.
---

# comment-review

`/comment-review [cap] [target] [style]`

## What you are doing

You are the task agent -- the **managing editor** -- and the **copy chief** of an editorial board. The manuscript is the
comments and docstrings in the files a change touched. Four editors each read it in one
editorial role -- the notes editor, the fact-check editor, the line editor and the
developmental editor -- and mark it. You fold their marks into one set of edits, rule where they
differ, have the result set as a proof, and show the author each page beside the manuscript.
The text the author accepts is written into the working tree, and a proofreader then reads
the finished pages.

The author approves quickly and trusts the proposal. You are free on form -- wording,
placement, length -- and every change to what a sentence claims carries the line of code
that settles it.

A helper program does the mechanical work. `<skill>` is the directory holding this file;
take it from the absolute path you were given. Every command runs through
`<skill>/scripts/comment-review.py`, and `--help` after a command's name gives its flags.
Give each run its own `<run-dir>` outside the checkout, since `proof` refuses an `--out` inside
the repo, and write every file with the command's output flag.
`<run-dir>/jacket.json` is the jacket, the run's record; only the commands write it.
`<stage-root>` is the stage's tree, the root `stage open` prints: the repo root for stage `4a`,
and `<run-dir>/root<stage>` for each later stage, holding the manuscript with every earlier
stage's decided changes set.

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
| 2 | gather | `gather`, `topology` | the binder, and the jacket holding a verified topology |
| 3 | find references | `referrers` | the `REFERENCE ONLY` list |
| 4 | mark, in stages `4a` then `4c` | the four reviewers | each stage's checked edit copies, and each role's freeform copies and findings |
| 5 | collate and rule, once per stage | `collate`, you, `disposition`, `stage close` | the stage closed on its proof, and the freeform drafts |
| 6 | compact, when a cap applies | the condenser | stage 6 closed on a proof whose text fits the cap |
| 7a | set and present | `proof`, then you | the proof pages and the proposal in front of the author |
| 7b | write | the author, then you | the accepted text in the working tree, its code proved unchanged |
| 8 | review | the proofreader | a reading of the finished pages and freeform files |

## What passes between the stages

Each stage hands the next one of these; your vocabulary defines each one:

| structure | made by | read by |
|---|---|---|
| **binder** | `gather`, `stage open` | `topology`, `check`, `collate` |
| **jacket**, holding the topology | `topology --run`, `stage open`, `stage close` | `stage open`, `collate`, `proof` |
| **edit copy**, one per dispatch | `stage open`, filled with `mark` | `check`, `collate` |
| **master proof** | `collate`, `turn`, `disposition` | `turn`, `disposition`, `stage close`, you when presenting |
| **batch** | `collate`, `turn` | the roles, in a turn |
| **dispositions** | you | `disposition` |
| **docket** | `proof`, from each stage's closed master proof | the compositor |
| **schedule**, one per page in the docket | `proof` | the compositor |
| **alteration**, one per place in a schedule | `proof` | the compositor |
| **proof**, the pages as set | the compositor, through `proof` | the author, stage 6, stage 7b |
| a role's freeform copies and `findings.json` | the reviewers | you, at stage 5 |
| `freeform/draft/<path>`, one per freeform file changed | you, at stage 5 | stage 7a, the author, stage 7b |
| `freeform/decided_<stage>.json` | you, at stage 5 | you, at the 7a audit and when the author asks why |

`proof` transcribes each stage's closed proof into a docket, and the compositor sets each
schedule's alterations onto a copy of its page.

## The goals of the steps

1. **Project determination** records the facts about this repo that every later stage uses.
2. **Gather** turns each Python and Rust file into a page of numbered places, and lists every
   other source file as freeform. Every mark cites a place by its address, such as
   `pkg:core.py@b3`.
3. **Find references** lists the files that name the files under review, so the reviewers can
   check what those files say about them.
4. **Mark** gives each paragraph four independent readings. Each role reads alone, so two
   roles that agree corroborate each other.
5. **Collate** decides what the roles agreed on. You rule on the rest, so every place ends
   with one text that is true of the code beside or below it, at whatever length that takes.
6. **Compact** shortens the paragraphs on pages that run over the cap, keeping every true,
   necessary and checkable sentence. The copy chief holds a freeform comment to the cap at stage 5.
7. **Set and present** puts the final text on copies of the pages, proves the code is
   byte-identical, and gives the author a diff of each page against the manuscript. A freeform file
   is set on a draft, formatted and compiled there, and audited hunk by hunk instead of proved.
   **Write** puts what the author accepted into the working tree.
8. **Review** reads the finished pages as a reader meets them, and catches anything the
   author and the run let through.

The author rules once, on the text that will actually be written.

## How you do the steps

### Stage 1 -- project determination

Work from the git repository at the repo root, and pass `--repo` to every command that takes it.

1. **Pre-edit ref.** Record the commit `git stash create` prints, or `HEAD` when it prints
   nothing, as it does when no tracked file has an uncommitted change. Stage 7b proves the code against it.
2. **Scope.** Use `target` when given. Otherwise take `git merge-base HEAD <upstream>` and list
   `git diff --name-only <base>..HEAD`, plus `git diff --name-only HEAD` for uncommitted work.
   When there is no upstream, scope from `git diff --name-only HEAD`.
   Remove every programmatically generated file or document, including any file
   `.gitattributes` marks `linguist-generated`.
   In the proposal, state which scope you used, and list each file removed with the file it is
   generated from when the repo names one.
3. **Cap and width.** Find what the repo publishes -- a contributing guide, `.editorconfig`, a
   formatter config -- and how it counts. Record where you found each. When the repo cites a test that enforces the cap, confirm
   the test exists, and report whether it does.
4. **Style sheet.** Read `style` when given; otherwise start one. It records the width stage 1
   found, the repo's dialect, the capitalisation of domain terms, its citation form, where the
   repo keeps code concerns -- in `TODO:` comments, or on a board or tracker its own
   instructions name -- asking the author with `AskUserQuestion` when the repo does not say,
   and one template for each documentation format the tree actually uses: module docstring,
   function docstring and,
   where the repo is consistent, comments. Write each template out with its slots, measured
   from the docstrings in the tree.
5. **Check and format commands.** Find how the repo proves its code compiles -- its CI config,
   Makefile, `package.json` or `pyproject.toml` -- and record one command per language in scope,
   for example `python -m compileall -q .`, `tsc --noEmit`, `cargo check`, `go build ./...`.
   Stages 7a and 7b run it. Where the project has doctests, record the command that runs them,
   for example `python -m pytest --doctest-modules`; stage 7b runs it. For each freeform language, record the repo's formatter as a command
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
read as a comment, or as the file's matter where it falls inside the front or back matter. Ask
the author about each line with `AskUserQuestion`, showing that comment and its owner, the
anchor it was written for, and offering two answers: move it to the owner's `a` cue, or leave
it where it is. Record each answer in the style sheet. For each `move it`, name the comment and
the owner's `a` cue in the prompt of the `4a` dispatch that holds the page, as a `move` the
author asked for.

Then build the topology into the jacket: two stages, and a third when a cap applies. Stage `4a`
runs `ownership-context` alone, so that where
each paragraph belongs is decided before the others read it; no other role reads its changes, so
you rule on each one at stage 5. Stage `4c` runs the other three roles against that placement.
`<n>` is the places on the gather's `GATHERED` line divided by 100, rounded up, at least 1, and
at most the number of pages and freeform files together. When the binder holds no
page and no freeform file, stop the run and tell the author the scope holds nothing to review. `--build` deals each role's pages so
its dispatches hold near-equal places. `--ref` is the pre-edit ref, and the paths are the ones
you gathered; the jacket records both as the run's.

```bash
python <skill>/scripts/comment-review.py topology --build --binder <run-dir>/binder.json --run <run-dir> \
  --repo . --ref <pre-edit ref> \
  --stage 4a=ownership-context/<n> \
  --stage 4c=block-context/<n>,function-context/<n>,module-context/<n> \
  <paths...>
```

When a cap applies and the binder holds a page, add stage 6, the compaction, to the same
command:

```bash
  --stage 6=block-context --cap 6=<cap> --series 6=b,c --admits 6=patch,drop,add,clean,query
```

`--build` verifies what it writes and exits 0 when the topology fits the binder. On exit 1 it
prints one misfit per line; change the `--stage` value and build again. Once a stage has opened,
the jacket's topology is fixed.

The binder holds only the places that hold prose. To look up any place, ask `addresses`,
which reads the file; each series is counted separately, and `--line <module>` or `<eof>` names
the places no line does, at the head and the foot of the file:

```bash
python <skill>/scripts/comment-review.py addresses find --repo <stage-root> --file <path> --line <n>|<module>|<eof> --series a|b|c|f
python <skill>/scripts/comment-review.py addresses resolve <address> --repo <stage-root>
```

### Stage 3 -- find references

```bash
python <skill>/scripts/comment-review.py referrers --repo . <paths under review...>
```

It prints every tracked file that names a file under review. From these, together with the
repo's decision record, any document holding dated facts, and any mirror copy of the files
under review, choose the `REFERENCE ONLY` list.

### Stage 4 -- mark

Stage 4 runs twice: `4a`, then stages 4 and 5 again for `4c`. `<stage>` is the one running. Open
it: this builds the stage's tree, gathers it into `<run-dir>/binder<stage>.json`, and seeds one
edit copy and one received binder per dispatch:

```bash
python <skill>/scripts/comment-review.py stage open --jacket <run-dir>/jacket.json --stage <stage> --repo .
```

It refuses a stage whose stage before has not closed. It prints the stage's root, which is
`<stage-root>`, then each edit copy, named `<stage>_<role>_<n>.json`, and its received binder,
saved as `copies/binders/<stage>_<role>_<n>.json`, with the count of freeform files dealt to it.
Dispatch one agent per edit copy of the stage, in batches no larger than the number of agents the
session can run at once:

| desk | agent | its question |
|---|---|---|
| notes editor | `comment-review:comment-review-ownership-context` | does this comment belong to the anchor it sits on? |
| fact-check editor | `comment-review:comment-review-block-context` | is every claim in this paragraph true of the code it sits with? |
| line editor | `comment-review:comment-review-function-context` | does the commentary match what the function is for? |
| developmental editor | `comment-review:comment-review-module-context` | do the comments say this is one module? |

All four roles run on every review, `ownership-context` at `4a` and the other three at `4c`.
Each agent's prompt is its packet, every section filled --
`UNAVAILABLE` is a complete answer. The agent reads each file the packet names from its path:

   - `BRIEF` -- absolute path of [`references/reviewer-brief.md`](references/reviewer-brief.md)
   - `VOCABULARY` -- absolute path of `<skill>/scripts/comment_review/references/vocabulary.toml`;
     the role reads the `[definitions]` entries whose keys are listed under it in `[roles]`, plus
     the `all` list
   - `SKILL DIR` -- absolute path of `<skill>`
   - `REPO ROOT` -- `<stage-root>`, absolute
   - `BINDER` -- absolute path of this agent's received binder
   - `EDIT COPY` -- absolute path of this agent's own copy
   - `FILES UNDER REVIEW` and `REFERENCE ONLY`
   - `STYLE SHEET`, templates included
   - `LANGUAGE SERVERS` -- which languages answered at stage 1
   - `FREEFORM DIR` -- absolute path of `<run-dir>/freeform/<stage>_<role>_<n>`, this agent's own
     directory
   - `FREEFORM SHEET` -- absolute path of [`references/freeform.md`](references/freeform.md), when
     the received binder lists a freeform file

An agent whose received binder lists no page takes a shorter packet: `FREEFORM SHEET` in place of
`BRIEF`, then `VOCABULARY`, `SKILL DIR`, `REPO ROOT`, `BINDER`, `EDIT COPY`, `FILES UNDER
REVIEW`, `REFERENCE ONLY`, `STYLE SHEET` and `FREEFORM DIR`. Its edit copy holds no place and
returns as seeded; `collate` still reads it.

Each agent fills its copy in place and runs `check` on it. An agent dealt a freeform file also
returns the paths of its `findings.json` and its copies. An agent that never returns is
relaunched as a new instance with the same packet. When an agent returns, run the same
check yourself:

```bash
python <skill>/scripts/comment-review.py check --edit-copy <run-dir>/copies/<file> --binder <run-dir>/copies/binders/<file> --repo <stage-root>
```

Exit 0 means the copy is ready to fold. Exit 5 means its only findings are human questions,
which stage 5 asks. Exit 2 is an input that will not read, and no mark can correct it; act on it
as on `collate`'s exit 2, below. On exit 1, send the copy back to its own agent with the lines
`check` printed; the agent corrects its own marks. When a copy still fails on its second
return, stop the stage and report the role and the lines `check` printed.

For each freeform file, confirm the agent's `findings.json` holds that path with its `swept`
list. Send a missing path back to its agent. When it is still missing on the second return, report
that role as unanswered on that file.

Roles in one stage work blind to each other. Stage `4c` starts from what `4a` left: once stage 5
has closed `4a`, `stage open --stage 4c` builds `<run-dir>/root4c` from the manuscript with
`4a`'s decided changes and the files in `<run-dir>/freeform/draft/` set over it.

After stage 7b, remove each `<run-dir>/root<stage>` with `git worktree remove --force
<run-dir>/root<stage>`.

### Stage 5 -- collate, and rule as copy chief

The jacket names the open stage's binder, its root and every copy it dispatched:

```bash
python <skill>/scripts/comment-review.py collate --jacket <run-dir>/jacket.json --stage <stage> \
  --proof-out <run-dir>/<stage>_proof0.json --batch-out <run-dir>/<stage>_batch1.json
```

Act on the exit code first:

| exit | meaning | what you do |
|---|---|---|
| `0` | every place decided | read the decided places against the style sheet and rule on any freeform findings, both below; `<stage>_proof0.json` is the closed proof when no place takes a recast. Then close the stage, below |
| `1` | the round rolled back; each refusal line names `<role> <place>: <reason>`, and any `asks the human` lines are questions still pending | send each refusal line to its role, which withdraws the mark the line names with `mark --withdraw --address <place> --instruction <instruction>` and marks again; re-check and re-run, and ask the questions when the re-run exits `5` |
| `2` | a file could not be read, or a page will not admit: its saved reading no longer matches the installed reader, or its sha or reading disagrees with another input's | where a line ends `regather`, stop the run and report the line, since an opened stage is not gathered again; otherwise correct the invocation. No role is sent a line |
| `3`, `4` | places or moves carried forward -- `composed`, `contested` or `open` -- to the roles each line names, or to `copy-chief` | run the turns and rule on them, below |
| `5` | human questions are owed, and nothing was refused | ask them, below, then re-run with `--human` |
| `6` | a dispatch never returned its copy; each line reads `not returned <copy>: <role>`, and nothing was folded | relaunch that dispatch as a new instance with its packet, then re-run |

Keep the path of the latest committed proof. A closed proof
can come from `collate`, `turn` or `disposition`; use that file wherever
`<closed-proof>` appears below. A refused round supplies no new proof.

A place is decided when every role that read it proposed the same text or answered `clean`, and
a change to it was read by a party besides its proposer: another role, or you. A role whose only
marks there are `outside-my-role` or `unable-to-determine` queries does not count as that party.
`collate` prints each decided place as `decided <place>: original` or `decided <place>: <roles>`.
A change only its proposer read is put to you: it prints as `composed <place>: copy-chief
(composition)`, or for a move `open <origin> -> <destination>: copy-chief (placement)`, and takes
no turn. The lines under `for the chief` name a `correct`
whose change removes words its claim never quoted; weigh that when you rule, and show it to
the author at 7a.

**Human questions.** Each line `asks the human <at>: <role> -- <question>; ask it, ...` is one
question, and `<question>` is the text before `; ask it,`, which the answer repeats exactly.
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

A question reading `approve this <instruction> ... to the file's matter` is a mark that changes an
`f` place, moves text out of one, or moves text into one. Each is asked on its own. Show the
author the text at `<at>` (both ends for a move) and the mark's `change`, and ask whether it goes
ahead. Where the author approves, the mark stands and the role keeps it. Where they refuse, the
role withdraws it and marks the place again without that change.

Send the asking role its `[[answer]]` sections with its copy; it replaces its query with a
mark. Then re-run `collate` with the same inputs plus `--human <run-dir>/human.toml`.

**Turns.** When `collate` writes a batch, run one turn even when you are told no number, so
every role owed a say reads the text composed from the marks before you rule. A place or move
put to `copy-chief` is in no batch; you rule on it below.
Run more turns only when you are told a number above one. Each turn sends `<stage>_batch<t>.json`
to one agent of every role it names, even a role that ran as several dispatches, with the proof
and a path for its answers; checks each returned file with `check --answers <file> --sent
<batch> --role <role>`; and folds them with `turn --proof <last proof> --answers <role>=<file>
... --proof-out <run-dir>/<stage>_proof<t>.json --batch-out <run-dir>/<stage>_batch<t+1>.json`.
A second `--answers` for one role replaces the first. `turn` exits with the codes in the table
above: on `1` each role corrects its answers file, and on `5` you run the same `turn` again with
`--human`. The turns end when a turn writes no batch or the count is reached.

**Ruling.** Rule on every place still carried forward, reading the code beside or below each paragraph
first. Read each composed paragraph whole, and confirm every pronoun, contrast word and pointer in
it still has what it refers to. Rule in this order, because each step builds on the one before:

1. `query` -- resolve what it asks.
2. `move` and `drop` -- decide where the prose lives. A move prints as
   `<placement> <origin> -> <destination>`, and its two ends are *to come*: they wait on the
   placement and take no ruling. Read both ends against their code first: taking a move in says
   the origin reads right without the snippet and the destination reads right with it. Rule the
   placement with a ruling that carries `to`: `taken_in` with `side` the mover, which moves the
   paragraph, or `original`, which withdraws the move from both ends and keeps the paragraph
   where it is. Taking in a move only its mover read also decides each end that reads exactly as
   the move sets it; an end where the mover changed more comes back for its own ruling.
3. `correct` -- fix what is false, against the code at the place the prose now sits.
4. `patch` -- improve the wording of text now known to be true.
5. `add` -- insert new text at its anchor.

Each ruling is one of two answers:

| answer | use it when | it carries |
|---|---|---|
| `taken_in` | one side is right | `side`: the role whose text stands, or `original` to keep the paragraph as it was; at an end of an agreed move, `original` is refused, below |
| `recast` | you write the paragraph yourself | `prose`: your paragraph, as raw text; empty `prose` drops the paragraph whole |

A `correct` outranks any number of `clean`s. Verify every clause you keep: each path it cites is tracked,
each name exists, and each count re-derives.

**The style sheet.** Then read every decided place against the style sheet: its dialect, its
review labels, the width stage 1 recorded, and its templates. Where a place breaks one,
`recast` it into line with the sheet, keeping every claim it makes, and name the style-sheet
entry in the `reason`. A decided place takes only a `recast`. Write these with your other
rulings, and run `disposition` for them even when `collate` exited `0`.

Write the rulings to `<run-dir>/dispositions.json` as a list of entries in the shape `check
--contract` prints under `chief`, with `"to"` added on a placement ruling (`address` the origin,
`to` the destination), then close the proof:

```bash
python <skill>/scripts/comment-review.py disposition --proof <last proof written> \
  --dispositions <run-dir>/dispositions.json --proof-out <run-dir>/<stage>_final.json
```

A `recast` of an `f` place asks the author first: `disposition` exits `5` and prints the
question. Ask it with `AskUserQuestion`, showing the paragraph and your prose, record the
answer in `<run-dir>/human.toml` with `role = "copy-chief"`, and run `disposition` again with
`--human <run-dir>/human.toml`. Where the author refuses, change the ruling.

It names any move or carried-forward place still unruled, and writes when every one has a ruling.
A placement ruling moves the paragraph or keeps it, and each end it did not decide is then read
as an ordinary place; when `disposition` exits `3` or `4`, those ends are carried forward. Rule
them from the code at each end, and run `disposition` again with the proof it just wrote and a
dispositions file holding only those rulings: that proof already carries the earlier ones, and a
ruling on a place it no longer carries forward is refused. Use a
fresh output filename for each ruling round. Its proof becomes `<closed-proof>`
once it exits `0`.

At an end of an agreed move, a ruling that puts back the end's text from before the move --
`taken_in original`, or a `recast` to that text -- is refused, naming the move: an agreed move
stands whole, so rule the move's text there or a further change to it.

**Freeform findings.** Read each role's `findings.json` from its path, and diff each of its copies
against the file it copied:

```bash
git diff --no-index -U0 <base> <FREEFORM DIR>/<path>
```

`<base>` is the file at `<stage-root>/<path>`. The command exits
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

Write the result to `<run-dir>/freeform/decided_<stage>.json`, a list of the findings' own shape with
`roles` added to each, naming every role whose change stands in it, and `at` the line in the
draft, holding only the changes that stand. A run with no pages prints `0 places` at `collate` and
carries on.

**Closing the stage.** Record the closed proof as the stage's:

```bash
python <skill>/scripts/comment-review.py stage close --jacket <run-dir>/jacket.json --stage <stage> --proof <closed-proof>
```

It refuses a proof that has not closed, that is another stage's, or that did not fold every copy
the stage dispatched. Then go on to `4c`, or after `4c` to stage 6 when the topology holds it, or
to 7a.

### Stage 6 -- compact, when a cap applies

Stage 6 runs as a third stage over every page in scope, when stage 2 gave the topology its row.
Open it once `4c` has closed:

```bash
python <skill>/scripts/comment-review.py stage open --jacket <run-dir>/jacket.json --stage 6 --repo .
```

Each received binder and edit copy holds only the comment paragraphs over the
cap. Dispatch `comment-review:comment-review-compact` with its edit copy and
received binder, `references/compact.md` pasted whole, the style sheet, the
cap, the helper script's path, `<run-dir>/root6` as the proof pages root and the repo root
as the manuscript. Check the copy against its received binder, then run `collate --jacket
<run-dir>/jacket.json --stage 6`, rule as in stage 5 and close the stage: no other role
reads the condenser's changes, so each one is put to you.

### Stage 7a -- set and present

```bash
python <skill>/scripts/comment-review.py proof --jacket <run-dir>/jacket.json --repo . --out <run-dir>/proof
```

It refuses until every stage has closed. It sets every stage's closed proof over the manuscript,
in stage order, and writes one draft per page any stage changed, carrying every stage's changes.

Use a fresh `--out` directory each time. `proof` prints one `<path> -> <draft>` line per page
it set. It reads each drafted page back and proves its code byte-identical to the manuscript.
When it refuses, it prints what refused and where; read that, fix the input, and set again.

**Code concerns.** Where the repo keeps code concerns outside its comments, list each one the
author answered `add a TODO`, with its place and the role's question, so the author can file
it.

**Freeform files.** Check the drafts stage 5 wrote, in this order:

1. `git worktree add <run-dir>/freeform-build <pre-edit ref>`, run the stage 1 check command there,
   and keep its result as the baseline.
2. Copy each draft over its `<path>` in the worktree, run the formatter on those paths, and run the
   check command again.
3. Copy the formatted files back over the drafts.

The check passes when the second run passes everything the baseline passed. When it fails
something the baseline passed, hold the run at this stage: edit the draft until it passes, and run
steps 2 and 3 again. When the failure comes from code no finding touched, bring the author the output
and the files it names. A language with no formatter or no check command, one whose command cannot run in the
worktree, or one whose baseline passes nothing is reported as not verified. Once the check passes
or is reported, remove the worktree with `git worktree remove --force <run-dir>/freeform-build`.

Then audit each draft:

```bash
git diff --no-index -U0 <path> <run-dir>/freeform/draft/<path>
```

Every changed line belongs to a decided finding, and every decided finding has its change. Any
other change holds the run at this stage: edit the draft until the change is gone, and audit it
again. Nothing is presented until the audit passes. The command exits 1 when the files differ.

Present to the author, grouped by instruction, most consequential first. Use each stage's
closed proof's decided text and the drafts for the proposed result. For each decided place, follow
its filed references to the reviewer marks in the proof and read any disposition on the place.
Use those for the instruction, paragraph, claim and reason. Show the decided change from the
draft inline.
Show each freeform draft whole. When the author asks why a change was made, answer from
`decided_<stage>.json`.
Then give:

- one command per page and per drafted freeform file, to read it beside the manuscript:
  `git diff --no-index <path> <draft>`
- the count of places raised and places clean, and `N swept, M raised` per freeform file
- which places you ruled, and how
- the longest paragraph that will remain
- the scope source, the roles that ran, and the language servers that answered
- for freeform files: the check baseline and result, the formatter, the hunks audited, and each
  language not verified
- the updated style sheet, holding every decision this run made

The author may edit a freeform draft line by line. Close by asking the author to accept all of
it, accept the places they name, each as `<stage>:<address>`, and the freeform files they name by
path, or accept none.

### Stage 7b -- write

Load [`references/write.md`](references/write.md) and follow it. It proves the accepted
drafts' code unchanged in a temporary worktree, runs the repo's check on them there, and writes
them into the working tree. `git diff <pre-edit ref>` then shows the author exactly what the run changed.

### Stage 8 -- review

Dispatch `comment-review:comment-review-review` with the pages and freeform files written at 7b,
the style sheet, the absolute paths of `<skill>` and the repo root, and paste [`references/review.md`](references/review.md) into its prompt
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
