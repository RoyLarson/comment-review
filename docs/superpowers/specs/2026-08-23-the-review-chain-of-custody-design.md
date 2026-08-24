# The review is a chain of custody, and the agents are orchestrating it

Design, 2026-08-23. Ruled with Roy in session; not yet scheduled. Companion to
[`2026-08-23-io-and-the-chain-design.md`](2026-08-23-io-and-the-chain-design.md), which
does the same thing for the read and write paths.

## The problem

**The eight stages are a chain of custody, and the custody is kept by an agent remembering
prose.** Roy, 2026-08-23: *"we are expecting the agents to orchestrate precisely, which is
not what we want them focusing on. We want them focusing on the work, not 'how' to do the
work, or if the work will work out."*

! **AN ORDER WRITTEN IN INSTRUCTIONS IS A CLAIM, NOT A MECHANISM.** It is the same finding as
the I/O spec, one level up: the pipeline's order lives in `SKILL.md`, so an agent can report
having followed it and nothing disagrees.

## The evidence, already measured in the backlog

| file | the custody gap |
| --- | --- |
| [`nothing-checks-that-four-reviewers-were-launched`](../../../TODO/nothing-checks-that-four-reviewers-were-launched.md) | *"1.6 proves the agents CAN be dispatched; nothing proves four WERE."* `run_context.py` runs before the dispatch and `verdicts.py` after -- **no artifact exists at the handoff itself** |
| [`ownership-is-read-first-but-nothing-makes-it-so`](../../../TODO/ownership-is-read-first-but-nothing-makes-it-so.md) | `SKILL.md` says `ownership-context` is read FIRST; the dispatch is parallel. *"Three mechanisms could deliver that, and none did"* |
| [`only-census-got-out-and-the-skill-instructs-a-redirect`](../../../TODO/only-census-got-out-and-the-skill-instructs-a-redirect.md) | only `census.py` has `--out`; `SKILL.md` writes a shell redirect it forbade 200 lines earlier. **Most artifacts have no defined home** |
| [`stage-1-is-re-derived-every-run`](../../../TODO/stage-1-is-re-derived-every-run.md) | ~25 tool calls per run re-establishing the same facts; the style sheet *"has no home"* |

!! **THE FOUR ARE ONE DEFECT.** An artifact with no home cannot be handed over; a handoff with
no artifact cannot be checked; a stage whose inputs are unchecked must trust that the previous
one ran. So the agent carries the pipeline in its head -- and the one thing the skill cannot
inspect is the step where that fails.

## The design: the run directory IS the record

The I/O spec threads a frozen `Doc` through a list of steps. **Here the steps are AGENTS, so
the record lives on disk**: each stage reads named artifacts and writes named artifacts, and
the handoff is a file rather than a message.

```
1  project    ->  style-sheet.md, context.md
2  gather     ->  census.json, census.txt
3  refs       ->  referrers.txt
4a ownership  ->  ownership-context.md
4c three      ->  block-context.md, function-context.md, module-context.md
5  apply      ->  join.txt, record.json
6  compact    ->  compacted.json
7a approve    ->  approved.md            <- the human gate
7b write      ->  applied.patch, proof.txt
8  review     ->  review.md
```

Each stage declares what it CONSUMES and what it PRODUCES. A stage does not start until its
inputs are present and valid.

## What it buys

- **"Were four reviewers dispatched?" becomes "do four files exist."** Checkable at the moment
  it matters, which is precisely the step the backlog says nothing can inspect. Today
  `--reviewers` catches it at stage 5, after the work.
- **`ownership-context` FIRST becomes structural.** It is a different stage producing an
  artifact that 4c consumes -- not a sentence asking four agents to sequence themselves while
  being dispatched in one message.
- **Stage 1 stops being re-derived.** The style sheet has a home because every artifact does.
- **The agent's job collapses to the work**: *given this census and this brief, produce this
  report.* Not remember the order, remember to dispatch four, remember not to redirect.

## Refusal, the third variant

| chain | a refusal means |
| --- | --- |
| read | report a gap, continue |
| write | abort -- nothing is approved |
| **review** | **stop and NAME THE MISSING ARTIFACT** |

! **A STAGE MAY NOT SUBSTITUTE JUDGEMENT FOR A MISSING INPUT.** The backlog already names this
failure in `only-census-got-out...`: *"the current wording lets a run substitute judgement for
the tool's output."* A missing artifact is a stop with a name, never a gap the next stage
reasons around.

## What must be true for this to work

- **Every script that produces an artifact the run keeps takes `--out`.** Today one does.
  That is the enabling change and it is small.
- **An artifact is named by its stage**, so a directory listing IS the custody record -- what
  ran, what it produced, and what is missing.
- **The human gate at 7a stays a gate.** It is the one step that is not an artifact check:
  approval is a person reading the exact text. The chain records that it happened; it does not
  decide it.

## Out of scope

The verdict/record shapes, the reviewer prose, and what each role is told -- this is the
custody of the artifacts between stages, not the content of any of them. The read and write
chains are the companion spec.

## TODOs this bears on

The four in the evidence table, plus
[`a-role-can-reverse-itself-between-runs`](../../../TODO/a-role-can-reverse-itself-between-runs.md)
and
[`the-author-approves-blocks-and-never-sees-the-page`](../../../TODO/the-author-approves-blocks-and-never-sees-the-page.md).
