---
name: comment-review
description: Review the comments and docstrings in the files a change touched, across four editorial roles -- ownership-context, block-context, function-context, module-context -- using parallel read-only subagents, and return each finding as instruction/location/summary/finding/change for the human to rule on. Use this whenever comments or documentation are the subject -- after finishing a task that added or edited commentary, when a file's comments have drifted from what the code now does, when someone says a comment is too long or out of date or "isn't this history", when reviewing a diff specifically for its prose rather than its logic, before a docs or comment burn-down, or when asked to check whether a module still reads as one module. Trigger on phrasings that never say "comment review" -- "these comments are getting out of hand", "does this docstring still match", "is this comment still true", "clean up the narration in this file", "why does this file need so much explaining" all mean run this. It is NOT /simplify (which reviews code structure) and NOT /code-review (which hunts correctness bugs). The reviewers mark a copy; the human reads each changed page as a diff against its original, what they accept is written into the working tree, and a proofreader then reads the finished pages.
---

# comment-review

`/comment-review [cap] [target] [style]`

## What you are doing

You are the task agent and the **copy chief** of an editorial board. The manuscript is the
comments and docstrings in the files a change touched. Four editors each read it in one
editorial role and mark it. You fold their marks into one set of edits, rule where they
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

**What you are given.** `cap` is the most lines one comment paragraph may hold; use the number given,
or the one the repo publishes, and when neither exists the run has no cap. `target` is a path
that sets the scope in place of the diff. `style` is the style sheet from an earlier run.

## The steps

| # | stage | who acts | what exists at the end |
|---|---|---|---|
| 1 | project determination | you | scope, cap, style sheet, run context |
| 2 | gather | `gather`, `topology` | the binder and a verified topology |
| 3 | find references | `referrers` | the `REFERENCE ONLY` list |
| 4 | mark | the four reviewers | four checked edit copies |
| 5 | collate and rule | `collate`, you, `disposition` | a closed proof and the chief's copy |
| 6 | compact, when a cap applies | the condenser | a closed proof whose text fits the cap |
| 7a | set and present | `proof`, then you | the proof pages and the proposal in front of the author |
| 7b | write | the author, then you | the accepted text in the working tree, its code proved unchanged |
| 8 | review | the proofreader | a reading of the finished pages |

## What passes between the stages

Each stage hands the next one of these, and the commands read and write them by name:

| structure | what it holds | made by | read by |
|---|---|---|---|
| **binder** | every page in scope; each paragraph with its address, anchor, lines and text | `gather` | `topology`, `distribute`, `check`, `collate`, `addresser` |
| **topology** | each stage's roles and the pages each dispatch covers | `topology` | `distribute`, `collate` |
| **edit copy** | one dispatch's slots, one per place it was dealt, each holding that role's mark | `distribute`, filled with `mark` | `check`, `collate` |
| **master proof** | every place: its base text, the marks on it, and whether it is settled or carried forward | `collate`, `turn`, `disposition` | `turn`, `disposition`, `proof` |
| **batch** | one slot per carried-forward place, for each role it is put to | `collate`, `turn` | the roles, in a turn |
| **dispositions** | your ruling at each carried-forward place | you | `disposition` |
| **chief's copy** | one mark per resolved place | `collate`, `disposition` | you, when you present |
| **docket** | every alteration to be set, as one schedule per page | `proof`, from a closed proof | the compositor |
| **schedule** | one page's alterations, with the page's path and the sha it was read at | the docket | the compositor |
| **alteration** | one place and what is set there: its replacement text, or its deletion | the schedule | the compositor |
| **proof pages** | the pages as set, each beside the original it was set from | `proof` | the author, stage 6, stage 7b |

`proof` transcribes the closed proof into a docket, and the compositor sets each schedule's
alterations onto a copy of its page. `proof --to-docket <file>` writes the docket out without
setting it.

## The goals of the steps

1. **Project determination** records the facts about this repo that every later stage uses.
2. **Gather** turns each file into a page of numbered places. Every mark cites a place by its
   address, such as `pkg:core.py@b3`.
3. **Find references** lists the files that name the files under review, so the reviewers can
   check what those files say about them.
4. **Mark** gives each paragraph four independent readings. Each role reads alone, so two
   roles that agree corroborate each other.
5. **Collate** settles what the roles agreed on. You rule on the rest, so every place ends
   with one text that is true of the code beside it, at whatever length that takes.
6. **Compact** shortens the paragraphs that run over the cap, keeping every true, necessary
   and checkable sentence.
7. **Set and present** puts the final text on copies of the pages, proves the code is
   byte-identical, and gives the author a diff of each page against its original.
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
4. **Style sheet.** Read `style` when given; otherwise start one. It records the repo's
   dialect, the capitalisation of domain terms, its citation form, and one template for each
   documentation format the tree actually uses: module docstring, function docstring and,
   where the repo is consistent, comments. Write each template out with its slots, measured
   from the docstrings in the tree.
5. **Reviewers.** Confirm the agents `comment-review:comment-review-*` resolve. When they are
   unavailable, dispatch general-purpose agents in their place, giving each the absolute path
   of its role file from the installed plugin, and say so in the proposal.
6. **Language servers.** Where you have an LSP tool, call `documentSymbol` once on one file of
   each language in scope, and record which languages answered. Where you have no LSP tool,
   record that no probe was possible.

### Stage 2 -- gather, and the topology

```bash
python <skill>/scripts/comment-review.py gather --repo . --out <run-dir>/binder.json <paths...>
```

The gather reads every file handed to it and exits nonzero naming any language it has no
record for; `gather --languages` lists the ones it reads. Report every gap it prints.

Then build the topology: one stage, `4`, with every role split so each dispatch holds five
files at most. `<n>` is the number of files divided by five, rounded up.

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

Seed one edit copy per dispatch:

```bash
python <skill>/scripts/comment-review.py distribute --topology <run-dir>/topology.toml --stage 4 \
  --binder <run-dir>/binder.json --out-dir <run-dir>/copies
```

It prints each file it wrote, named `4_<role>_<n>.json`. Dispatch one agent per file, by name:

| agent | its question |
|---|---|
| `comment-review:comment-review-ownership-context` | does this comment belong to the anchor it sits on? |
| `comment-review:comment-review-block-context` | is every claim in this paragraph true of the code it sits with? |
| `comment-review:comment-review-function-context` | does the commentary match what the function is for? |
| `comment-review:comment-review-module-context` | do the comments say this is one module? |

All four roles run on every review. Each agent's prompt holds, in this order:

1. [`references/reviewer-brief.md`](references/reviewer-brief.md), pasted whole.
2. That role's vocabulary: the `[definitions]` entries of
   `<skill>/scripts/comment_review/references/vocabulary.toml` whose keys are listed under the
   role in `[roles]`, plus the `all` list, read fresh from that file.
3. The packet, every section filled -- `UNAVAILABLE` is a complete answer:
   - `REPO ROOT` -- absolute path
   - `BINDER` -- absolute path
   - `EDIT COPY` -- absolute path of this agent's own copy
   - `FILES UNDER REVIEW` and `REFERENCE ONLY`
   - `STYLE SHEET`, templates included
   - `LANGUAGE SERVERS` -- which languages answered at stage 1

Each agent fills its copy in place and runs `check` on it. When an agent returns, run the same
check yourself:

```bash
python <skill>/scripts/comment-review.py check --edit-copy <run-dir>/copies/<file> --binder <run-dir>/binder.json --repo .
```

Exit 0 means the copy is ready to fold. Exit 5 means its only findings are human questions,
which stage 5 asks. On any other exit, send the copy back to its own agent with the lines
`check` printed; the agent corrects its own marks. When a copy still fails on its second
return, fold without it and report that role as unanswered.

### Stage 5 -- collate, and rule as copy chief

```bash
python <skill>/scripts/comment-review.py collate --stage 4 --binder <run-dir>/binder.json --repo . \
  --topology <run-dir>/topology.toml --edit-copy <each copy distribute printed> \
  --out <run-dir>/chief0.json --proof-out <run-dir>/proof0.json --batch-out <run-dir>/batch1.json
```

Act on the exit code first:

| exit | meaning | what you do |
|---|---|---|
| `0` | every place settled | `proof0.json` is the closed proof; go to stage 6 or 7a |
| `1` | the round rolled back; each line names `<role> <place>: <reason>` | send each line to its role, which withdraws with `mark --withdraw --address <place>` and marks again; re-check and re-run |
| `2` | a file could not be read | correct the invocation |
| `3`, `4` | places carried forward -- `composed`, `contested` or `open` | rule on them, below |
| `5` | human questions are owed | ask them, below, then re-run with `--human` |

A place is settled when every role that read it proposed the same text or answered `clean`;
`collate` prints each as `stet <place>`. The lines under `for the chief` name a `correct`
whose change removes words its claim never quoted; weigh that when you rule, and show it to
the author at 7a.

**Human questions.** Each line `asks the human <at>: <role> -- <question>` is one question.
Ask it with `AskUserQuestion`, showing the paragraph at `<at>` (both ends for a move) and the
query's `attempted` text from the role's copy. Record each answer in `<run-dir>/human.toml`:

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

**Ruling.** Rule on every place still carried forward, reading the code beside each paragraph
first. Rule in this order, because each step builds on the one before:

1. `query` -- resolve what it asks.
2. `move` and `drop` -- settle where the prose lives. For a move, decide the placement, then
   rule both ends from it.
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
`{"address", "answer", "side", "reason", "prose"}`, with a `reason` on each, then close the
proof:

```bash
python <skill>/scripts/comment-review.py disposition --proof <last proof written> \
  --dispositions <run-dir>/dispositions.json --out <run-dir>/chief.json --proof-out <run-dir>/final.json
```

It names any carried-forward place still unruled, and writes when every place has a ruling.
`final.json` is the closed proof.

### Stage 6 -- compact, when a cap applies

Stage 6 runs as a second stage over the proof pages. Set them from the closed proof into
`<run-dir>/proof4` (the `proof` command in stage 7a), then gather them as revise 1:

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
<run-dir>/binder6.json --revise <run-dir>/proof4 --out-dir <run-dir>/copies`. The copy holds
only the comment paragraphs over the cap. Dispatch `comment-review:comment-review-compact` on
it, with [`references/compact.md`](references/compact.md) pasted whole, the style sheet and the
cap. Then check, `collate --stage 6` and rule as in stage 5. The closed proof this produces is
the one stage 7a sets.

### Stage 7a -- set and present

```bash
python <skill>/scripts/comment-review.py proof --repo . --proof <run-dir>/final.json --out <run-dir>/proof
```

Use a fresh `--out` directory each time. `proof` prints one `<path> -> <draft>` line per page
it set. It reads each drafted page back and proves its code byte-identical to the original.
When it refuses, it prints what refused and where; read that, fix the input, and set again.

Present to the author, grouped by instruction, most consequential first. For each mark on
`chief.json` show `INSTRUCTION / PARAGRAPH / CLAIM / REASON / CHANGE`, with the replacement
text inline. Then give:

- one command per page, to read it beside its original: `git diff --no-index <path> <draft>`
- the count of places raised and places clean
- which places you ruled, and how
- the longest paragraph that will remain
- the scope source, the roles that ran, and the language servers that answered
- the updated style sheet, holding every decision this run made

Close by asking the author to accept all of it, accept the places they name by address, or
accept none.

### Stage 7b -- write

Load [`references/write.md`](references/write.md) and follow it. For an author who accepts
all of it, copy each `<draft>` over its `<path>`. For an author who names places, set those
places alone and copy what that prints:

```bash
python <skill>/scripts/comment-review.py proof --repo . --proof <run-dir>/final.json \
  --only <address> --only <address> --out <run-dir>/accepted
```

Then prove the code in every page you wrote is unchanged from the pre-edit ref:

```bash
python <skill>/scripts/comment-review.py prove_unchanged --base <pre-edit ref> --repo . <paths written>
```

`git diff` now shows the author exactly what the run changed.

### Stage 8 -- review

Dispatch `comment-review:comment-review-review` with the pages written at 7b and the style
sheet, and paste [`references/review.md`](references/review.md) into its prompt whole. Bring
its findings to the author: each page reported done, and each section it names as something
to fix.

## What to expect from the other agents

**The four reviewers** each return their edit copy filled in place, one mark per paragraph
they read, and a clean `check` or exit 5. A mark carries one of seven instructions:

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

**The proofreader** returns each page as done or with the sections to bring to the author,
and lists separately every defect that predates this run.
