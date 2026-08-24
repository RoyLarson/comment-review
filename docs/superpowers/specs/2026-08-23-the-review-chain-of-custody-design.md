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

### !! IT IS A LOG, NOT A LIST, AND THAT IS THE DIFFERENCE FROM THE OTHER TWO

Roy, 2026-08-23: *"the chain of custody steps must be more flexible than what the other steps
need. The reason is that we don't KNOW the number of steps or the order of the steps. We know
we need to pick it up from when the first agent does the gather, and drop it off when the
review is ready for the human."*

| chain | shape | why |
| --- | --- | --- |
| read, write | a KNOWN LIST | the steps are fixed and the order IS the design |
| custody | a LOG | the steps vary by run -- a reduced role set, a re-run of one role, a second compact pass |

**What is fixed is the two ENDPOINTS and the preconditions, not the sequence.** Custody opens
when the first agent gathers and closes when the review is ready for a human. Between them the
log records what was received, what was produced, by whom and when; it does not prescribe how
many entries there are.

! **WHICH IS WHY A FIXED STAGE TABLE WOULD BE WRONG HERE.** `SKILL.md` already supports a
reduced role set -- three of the four are OPTIONAL, `ownership-context` is not -- so a run with
three reports is valid and a run with five entries for one role is a re-run, not a fault. A
list cannot express that; a log can.

A typical run's artifacts, as an ILLUSTRATION and not a schema:

```
style-sheet.md, context.md        census.json, census.txt      referrers.txt
ownership-context.md              block-context.md ...          join.txt, record.json
compacted.json                    approved.md   <- human        applied.patch, proof.txt
review.md
```

Each entry declares what it CONSUMED and what it PRODUCED. A step does not start until the
inputs it names are present and valid -- **the precondition is per-step and declared by the
step, not read off a global order.**

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

## !! THE PATTERN IS ALREADY PROVEN HERE, ON THE WORK ITSELF

**This repo's own tracking system is a chain of custody, and it works.** The design below is
that board applied to artifacts instead of tasks -- not a new invention.

| tracking (`conventions.md`) | this design |
| --- | --- |
| **T** -- the goal, one verifiable checkpoint | the artifact that must exist |
| **P** -- a step towards it | a step in the chain |
| **SP** -- a subplan of a step | a sub-chain |
| arrows one way, `SP -> P -> T` | a step declares its inputs and never reaches forward |
| *"re-derivable by a stranger"* | the order is DATA you can print |
| the boxes ARE the state | the manifest IS the custody record |

!! **AND THE SHAPE MATCHES, WHICH IS THE PART THAT SETTLES IT.** `TODO/` is a LOG -- open
ended, entries added as work is figured out, state per entry, endpoints that matter.
`docs/plans/` is a LIST, because a release scope IS a fixed set of steps. That is exactly the
read/write-versus-custody split above, and it was arrived at independently.

! **SO THE RULES THAT WILL HOLD ARE PREDICTABLE**, because their tracking equivalents are the
load-bearing ones: *name the T tasks, not the file*; *a box is a verifiable checkpoint*;
*counts are recomputed, never written by hand*. Their chain forms are **assert the chain IS
the list**, **a refusal names its step**, and **the manifest is recomputed from the pages
rather than asserted**.

!! **THE FAILURE MODE TRANSFERS TOO, AND IT WAS MEASURED ALL DAY 2026-08-23.** A box that is
not a checkpoint makes the count lie -- `leading-owns-the-space-between` read `0 of 10` with
nine settled, `python-cannot-read-python` `0 of 31` with no task in it. **The code form is a
step that is not in the chain**: `lossless` exists, nothing calls it, and the run reports
success. Same defect, same invisibility, one level down.

## !! THE WRITE-BACK IS A SECOND CUSTODY, AND IT NEEDS TO BE TRANSACTIONAL

Roy, 2026-08-23: *"the write of the reviewed text to the original file is another chain of
custody because it needs to be solid. It would suck to have it start the write and fail on
half of the pages and not know. Git is there for recovery but recovery of the entire system
can be expensive when just another retry is necessary or a complete rewind."*

! **THIS IS NOT THE COMPOSITOR'S WRITE.** That one sets ONE page and the I/O spec's write chain
covers it. This is 7b putting MANY approved pages onto the real files, and its failure mode is
different in kind: **a partial write leaves the tree in a state no page describes.**

**What it needs that the other chains do not:**

| property | why |
| --- | --- |
| **per-page state** | `pending`, `written`, `verified`, `failed` -- so the run knows WHICH half succeeded |
| **resumable** | a retry re-attempts the failed pages only |
| **a rewind that is a choice** | git is the floor, not the plan. Rewinding the whole tree to fix one page is the expensive answer to a cheap problem |

! **THE MANIFEST IS THE CUSTODY RECORD.** One entry per page: its address, its approved text,
its state, and the proof that ran on it. A crash leaves a manifest that says exactly where it
stopped, so the next run resumes rather than re-deciding.

!! **AND A HALF-WRITE MUST BE LOUD.** The current failure is silent: `draft` writes and the
proof arrives afterwards. Under a manifest, the run that stops mid-way leaves `written` pages
with no `verified` beside them -- which is a state a person can read and a check can refuse,
rather than a tree that merely looks finished.

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
