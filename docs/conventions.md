# Conventions -- the lanes in full, and the agreements between them

How work divides, what each lane may change, and what it must ask for. The path -> lane map is
authoritative in [`lanes.md`](lanes.md); this file holds the reasoning and the agreements.

**A rule lives in exactly one file.** What is here is not in `CLAUDE.md` and not in a TODO.

---

## Session roles -- in full

Roy runs sessions on this repo in parallel, each opened as *"You are the `backend` -- I need you
to ..."*. **The lane scopes what you may change.** If a task touches a file another lane owns,
**name the lane and ask** rather than editing in passing.

### `agents` -- what an agent is TOLD

The four reviewer files, `SKILL.md`, and the reference each stage reads. It owns the WORDING an
agent acts on: what a role's remit is, what it must refuse, what the task agent does between
stages, and how an instruction is expressed.

**It does not own what the tools DO.** A reviewer that needs a different fact from the census
is a `backend` request; the agent file may not describe an output the census does not produce.

### `backend` -- what the Python actually does

`src/comment_review/**`: the lexer, the page, the addresser, the census, the
compositor, the galley, the record, the desk, the collator. It owns the reading, the addressing, the
setting and the checking -- and `docs/addressing.md` and `docs/parsing.md`, which describe them.

**It does not own the agent's instructions.** Changing what the census EMITS is `backend`;
changing what a reviewer is told to DO with it is `agents`.

**And it owns its own tests.** A case in `tests/` asking whether this Python does what it says
is `backend`'s to write and to keep green -- see [`lanes.md`](lanes.md), *`tests/**` -> the lane
that owns what the test ASKS*. Landing a behaviour change with nothing able to notice it regress
is this lane's defect.

### `testing` -- how well the running system does, and what that is scored against

`evals/`, `evidence/`, `corpora/`. The planted hazards and their pass criteria, the test cases,
**the grader**, the grades it keeps, and the pinned corpora. Its work lives on the harness
branch.

!! **It does not own `tests/`, and this file said it did until 2026-08-24.** Roy: *"testing's
lane is specifically about building and testing the running agent system that is in the testing
harness branch. If it is backend testing that is on you. If it is vocabulary and system gating
tests that is systems. Running the tests for the agents is the agents responsibility, it is
testing's lane to make the grader and keep the grades."* **A test is owned by the lane that owns
what it makes a claim about** -- the table is in [`lanes.md`](lanes.md), the ruling is
`decision-log.md Process: #5`.

**The cost of the old row is the one it was measured on.** Two `record.py` regressions were
filed to `testing` on 2026-08-24 because they landed in `tests/` -- shipping a backend fix with
nothing able to notice it regress, and parking the test on a lane whose work is a grader on
another branch.

!! **A test that cannot fail is a defect wherever it lives, not a pass.** See
[`gates.md`](gates.md): *"does the check pass" is not the question; "could the check fail" is.*

It does not own the gates that run in CI -- those are `systems`.

-> [`decision-log.md`](decision-log.md), *Process* #5, which settles that a test is owned by the lane that owns what it makes a claim about.

### `systems` -- whether it installs, and whether the gates bite

`scripts/**` (the dev tools), the manifests, the release, `.gitignore`, `CHANGELOG.md`, and
`docs/gates.md`. It owns `check_shipped_syntax.py`, `check_vocabulary.py`, `todo_tool.py`,
`fetch_corpora.py`, `dead_sweep.py` and the floor-interpreter rules.

!! **A lane that trips a gate fixes its own code. It does not edit the gate to let the code
through.** That is the one crossing this repo has no tolerance for, because a gate edited to
pass is indistinguishable afterwards from a gate that always passed.

**And `systems` owns the backlog as a board.** Roy, 2026-08-23: *"the systems lane can
reassign the owner or split/merge any set of todos appropriately."* Any lane FILES a TODO in
whatever lane owns the thing it found; `systems` decides where each one sits, splits one that
holds two problems, and merges two that hold one.

**Adding a task is any lane's.** Roy, 2026-08-23: *"adding a task can be done by any lane
because that is a result of who found it creates it."*

**What is not any lane's:** ticking a box and rewriting an Objective belong to the lane that
owns the work, because both assert that the work's state or shape has changed. Moving a file
between owners, splitting one that holds two problems, and merging two that hold one are
arrangement, and arrangement is `systems`'.

-> [`decision-log.md`](decision-log.md), *Process*, for what `systems` arranges and what it does not own.

---

## The vocabulary is shared, and crossing is the point

Roy, 2026-08-23: *"any side can and should update the vocab on the other side as soon as a split
or modification is noticed."*

`references/vocabulary.toml` and `docs/vocabulary.md` belong to **no lane**. A lane that renames
something, splits a module, or notices a term drifting **updates the other side in the same
change**. It does not file a TODO and move on, and it does not wait to be asked.

!! **The cost of waiting is measured.** A rename that stopped at the code left 32 quoted rulings
and 31 uses of a retired word in prose an agent reads, past a green suite, `ty`, `ruff`, the
floor gate, the vocabulary gate and the corpus round trip -- see
[`evidence/rename-left-history-in-the-comments/`](../evidence/rename-left-history-in-the-comments/README.md).
Every gate answered a different question, and the only thing that could have caught it was the
lane that did the renaming saying so on the other side.

**This is one of two standing exceptions to "name the lane and ask"** -- the other is below,
and it is the same principle. Everywhere else, asking is cheap and editing in passing is how a
change nobody reviewed reaches a file nobody owns.

-> [`decision-log.md`](decision-log.md), *Vocabulary*, and [`evidence/rename-left-history-in-the-comments/`](../evidence/rename-left-history-in-the-comments/README.md) for the run that measured the cost.

---

## A one-for-one substitution is not a crossing

Roy, 2026-08-24, on a `backend` change that forces every command in `SKILL.md` to be spelled
differently: *"This doesn't land in the other lane just like a vocabulary change doesn't land
in the other lane. A one for one swap is allowed."*

**A lane may make a mechanical one-for-one swap in another lane's file when its own change
forces it.** What it may not do is change what the instruction **means**.

| | allowed | not allowed |
| --- | --- | --- |
| a command's spelling | `python x/y.py` -> `python -m pkg.y` | adding a flag, changing an argument |
| a renamed symbol | the new name at every site | rewording the sentence around it |
| a moved file | the new path | changing WHEN the stage runs it |

!! **The test is whether a reader's behaviour changes.** If the agent does the same thing for
the same reason and only types something different, it is a substitution. If it would now do
something different, decide differently, or refuse where it did not -- that is the owning
lane's, and the answer is *name the lane and ask*.

**It is the same principle as the vocabulary rule, arriving from the other side.** There, a
lane must update the other side because leaving it stale rots. Here, a lane may update the
other side because leaving it stale BREAKS -- a command that names a path that no longer
exists is not a stylistic lag, it is an instruction that cannot be followed. **In both, the
alternative is filing a TODO and shipping a file that is wrong in the meantime.**

-> [`decision-log.md`](decision-log.md), *Vocabulary*, where the swap was ruled allowed.

---

## How a `P` gets written, and when

A `docs/plans/*.md` entry names the `T` tasks it works, and it is what says when the branch is
finished.

**Where a design deliberately reaches into territory that will later belong somewhere
else, mark it provisional in the code AND in the records.** Necessary now is not correct
forever, and a boundary never written down as temporary calcifies by silence.

---

## What every addition must answer -- necessity, and a purpose named BEFORE the code

Roy, 2026-08-30: *"The constraint on any design is still -- Is this field necessary to
make the system correct, is this change or addition to code serving an actual previously
unidentified purpose. That is what the TODOS and PLANS are for as much as anything they
are identifying the purpose of the pieces before they get implemented."*

**Two questions, asked of every field, flag, function and module before it is written:**

| | |
| --- | --- |
| **necessary** | is this needed to make the system CORRECT |
| **purposeful** | does it serve an actual purpose that is not already served |

**And the answer is written down before the code, not defended after it.** A `T` names
the work and a `P` names the step, and both exist so a piece's purpose is on the record
before anyone implements it. **A purpose first stated in a review is a justification, not
a design** -- it is produced by looking at the code, so it can only ever agree with it.

**The MEASURED failure is A field that answers neither.** `desk/mark.py` declared
`owes_destination` and **nothing read it**: measured 2026-08-30,
`grep -rn "owes_destination" src/` returned three lines and all three were in the file that
declares it. A flag nobody reads cannot make the system correct and serves no purpose,
and it survived because no plan ever had to say what it was for.

**SUPERSEDED the same day, and the way it was SUPERSEDED is the point.** `f17b712`
gave the flag a reader -- `parse` now runs `_destination_problems` under it, refusing a
`move` whose `claim.to` equals its own address. The grep returns five lines, one of them a
read. **The measurement above stands as of its date and the rule it argues for is
unchanged; what moved is the example.**

**A field does not become necessary by being wired -- It becomes necessary when something
would otherwise be wrong.** Here something was: a move onto its own address reached the
docket as a bare delete, so the flag now answers *what would be incorrect without it*. That
is the answer this section asks for, arriving a plan late rather than never. The three
lines were the honest reading on the day; leaving them uncorrected would make this section
an instance of the rot it exists to forbid.

**It is the same standard this repo applies to prose, arriving from the other side.**
`CLAUDE.md` refuses a sentence that cannot be falsified by reading the code; this refuses
a piece of code that cannot be justified by naming what would otherwise be wrong.

### A carryover starts costing when new design is built onto it, not when it exists

Roy, 2026-08-31, on why two vestigial fields had to go that day while a third could wait:
**"The others were hurting because you were actively designing them into the system instead
of letting them drop because they were not necessary."*

**Three fields, one shape, two answers** -- all of them left over from a design the address
system replaced:

| | what it was | what happened |
| --- | --- | --- |
| `original_column` | where a trailing comment began on a line that starts with code | I read it in a NEW page type, and reasoned about whether a redacted paragraph could carry it |
| `declares` | which declaration a docstring documents, as an ordinal | I proposed a REPLACEMENT MECHANISM for it, measured that mechanism failing, and filed a ruling request on the strength of it |
| `lines` | how many lines a paragraph stands on | nothing. It sits there, 11 writes and 1 read |

**The first two were urgent because I was spending design on them.** Not because they
cost anything at rest -- a dead field costs nothing at rest. What they cost was every
decision taken while assuming they were load-bearing: a `RedactedParagraph` argued for, an
anchor-matching scheme invented and measured, a plan step filed as needing a ruling that no
ruling was owed on. **Each of those was work produced by the field rather than by the
PROBLEM.**

**And the third is left in, deliberately.** Roy: *"that thread probably needs pulled a
little more carefully and it isn't hurting yet to leave it in."*

**A field a current design is being shaped around is a defect right now**, whatever its
reader count says -- and it will be defended, because the design that grew on it is evidence
for it. That is the same trap as *a purpose first stated in a review*, one level up: there,
the code produces the justification; here, the leftover field produces the design that then
justifies it.

### Areas are isolated: an end or the middle reaches down, never across

The packages fall into areas, and each area imports only what this table allows. Isolation
keeps each area's concepts in one place, so work in one area does not have to learn another's
rules. It is required, and `tests/test_areas.py` enforces it: an import across areas fails the
gate unless it is on the gate's known list, and an entry on that list is a defect to remove,
not a permission.

| area | packages | may import |
| --- | --- | --- |
| read end | `binder` | a leaf |
| middle | `desk` | a leaf |
| write end | `docket`, `results` | a leaf |
| neither | `flows`, `commands` | anything -- they run the steps |
| leaf | `machine`, `reading`, `concordance` | nothing above them |

- **Down to a leaf is one definition with several readers; across is two areas that must
  then agree**, and the rule ends up stated twice, with one copy going stale.
- **A flow builds a container from its parts, or hands a container what it needs to build
  itself.** No third module builds another area's container.
- **A type is coupling too.** A function that needs another area's object does not import
  its type: the reading side declares a `Protocol` of exactly what it reads, and `ty`
  checks every caller against it. When `ty` reports a mismatch, the fix belongs on the
  reader's side -- its `Protocol` states what it reads -- never an import of the other
  area's type to make the check pass.

-> [`decision-log.md`](decision-log.md), *Process*.

### Follow the field to what finally consumes it. Counting readers is not that

**Take each read, and ask what the last thing in the chain does with the value.** The test
is mechanical and a stranger can run it. If every terminus reconstructs something the
system already holds, the field is a copy.

    lexer     held.declares = ordinal
    attach    cues.documents(declares)
    Cues      self.addressers[DECLARED].at(ordinal)
    at        got = cue_for(self.series, step)
    cue_for   return f"{series}{step}"          <-- the terminus: it rebuilds `a3`

**Roy ran that chain and had the answer before any measurement was taken.** 2026-08-31,
after two sessions of my evidence pointing the other way: *"you tried very hard to convince
me that those were necessary even though I had already followed the full chain on logic
determining they were dead."*

**And every test I substituted for it was local, which is why each one passed.**

| what I asked | why it answered nothing |
| --- | --- |
| *is it read* | always yes for a field with a reader. One hop, no terminus |
| *does it agree with the address* | the address is computed FROM it -- 11,702 agreements that could not have come out otherwise |
| *does my replacement work* | it did not, and that is a fact about my replacement. Anchor TEXT was never the key; the ordinal already was the cue |

**One hop is the common fault in all three.** Each stops at the first thing that touches
the field and reads the result as an answer about the field.

!! **Do not WRITE this rule as a self-check.** An earlier wording of it said *"the test is
not is it dead but AM I REASONING FROM IT"* -- which asks for introspection in the moment,
and Roy named that plainly the same day: *"you are not very good at introspection or seeing
the global shape of the code."* It is the fault `CLAUDE.md` already records for boxes --
**"is this a verifiable checkpoint" is a judgement; "does this box open with implement,
update, delete, or a question" is a reading* -- arriving on a field instead of on a task.
**Trace the chain, which is a reading. Do not ask yourself how you feel about it.**

-> [`decision-log.md`](decision-log.md), *Process*.

---

## A task list is not split by a heading, ever.

Roy, 2026-08-30: *"This very thing made an earlier session completely jump a bunch of
steps in a plan ... The task headers made it easy to skip past a set of tasks and start
working on the next section of tasks."*

**Every task in a file lives under ONE `## Tasks`.** A second heading holding more tasks
is not a formatting choice; it is a way to lose them.

**And it costs twice, with the expensive half first.** A reader -- a session, an agent
-- treats a heading as a boundary and starts at the one it can see, **so the group above
is never worked.** That has happened. The cheap half is arithmetic: a counter that scopes
to `## Tasks` reports fewer tasks than a counter that reads the document, and the
finished work in the other section is exactly what falls in the gap.

**The fix is never A BETTER COUNTER.** A heading that groups tasks is legible to a
human and invisible to everything else. If a group needs explaining, the explanation is
PROSE ABOVE the list or a dated note -- **the tasks stay in one block, in one order**.

---

## Where a finding goes -- a task first, a file only when nothing holds it

| the finding | where it goes |
| --- | --- |
| fits an open TODO's subject | **a task on that file** |
| a general fix with no obvious file | **a per-MODULE TODO**, opened once and added to |
| a design objective whose several dependencies each need their own tasks | **its own file** |

!! **A new file is the exception and has to earn itself.** MEASURED 2026-08-30: **34 of
159 open TODOs carry three tasks or fewer**, two of them ONE, against a mean of 7.3 over
1,155 tasks. Re-derive with `grep -h "^Progress:" TODO/*.md`. Each was a defensible
filing on the day it was made; what they add up to is a board whose index is longer than
most of the work in it, where a reader scanning `TODO/README.md` cannot tell a SUBJECT
from a single observation.

**And the cost is paid by whoever works the module, not by whoever filed.** Four
separate files each holding one `desk/collator.py` defect are four things to find, four
Objectives saying the same thing about one module, and four closes.

**The tell that A file is warranted is dependency, not size.** Tasks that must land
**TOGETHER** -- because they block each other, or because none of them is finished until
all of them are -- are a design objective and may have their own file. Tasks that merely
share a module are a module TODO. **A single observation is never a file.**

**TOGETHER, not merely in an order.** Roy, 2026-08-30, correcting this sentence's first
wording. Almost any set of tasks has an order somebody would prefer, so *"they must land
in an order"* is a test nearly everything passes -- and a test nearly everything passes
is what put 34 single-observation files on this board. **What earns a file is that
landing one without the others leaves the objective unmet.**

**AND A file opened in error is SUPERSEDED, not deleted.** `CLAUDE.md`'s rule covers a
filing mistake as much as work overtaken: move the tasks to their home, then
`complete --superseded` with an outcome naming where they went.

-> [`decision-log.md`](decision-log.md), *Process*.

---

## Shipped prose states what the code does now

**A quotation is not an exemption, and there is nothing to exempt.** Roy, 2026-08-23: *"It
simply isn't necessary to know the history to understand the code. It is a bad habit to think
it needs it."* A shipped file states what the code does now. A ruling quoted in the words it was
made in is history, and history is in the git commits for whoever wants it.

**A citation is the same prose one indirection along.** Pointing a comment at an entry that
holds the old wording keeps the history in reach of the code, which is the thing the rule exists
to stop. The comment states the rule and the reason it is that way; neither needs a date, an
attribution or a link.

**The cost of the alternative is the mechanism `README.md`'s *Why* records:** a dead term is a
context anchor, and quotation marks do not stop a word reaching an LLM's attention. A human
reads the marks and discounts the word, which is exactly the imprecision an agent does not
share.

This stood above `NOT_THE_TERM` in `scripts/check_vocabulary.py` until 2026-09-27, when a
comment-review run found nothing there enforcing it and Roy ruled that it lives here.

## Working agreements

- **Name the lane and ask.** A one-line question costs less than a change the owning lane has to
  discover by reading a diff.
- **A filed finding goes to whatever lane owns the thing found.** The lane that found it files
  it; the lane that owns it works it. **A new file only when nothing holds it** -- see *Where a
  finding goes*, above.
- **A gate is not a lane's to relax.** See `systems`, above.
- **A ruling is recorded by whoever received it** -- `docs/decision-log.md` for what and when,
  `docs/history.md` for why. Neither is owned.
- **`Owner:` is who ticks the boxes; `Requires-Roy:` is whether a DECISION is owed.** They answer
  different questions and a file may carry both.

**What this exists to stop is a lane fixing something in passing.** The change is usually small
and usually right, and it lands in a file whose owner never saw it, in a branch about something
else -- so the next person to touch that file reads it as settled.
