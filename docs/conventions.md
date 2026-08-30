# Conventions -- the lanes in full, and the agreements between them

How work divides, what each lane may change, and what it must ask for. The path -> lane map is
authoritative in [`lanes.md`](lanes.md); this file holds the reasoning and the agreements.

! **A rule lives in exactly one file.** What is here is not in `CLAUDE.md` and not in a TODO.

---

## Session roles -- in full

Roy runs sessions on this repo in parallel, each opened as *"You are the `backend` -- I need you
to ..."*. **The lane scopes what you may change.** If a task touches a file another lane owns,
**name the lane and ask** rather than editing in passing.

### `agents` -- what an agent is TOLD

The four reviewer files, `SKILL.md`, and the reference each stage reads. It owns the WORDING an
agent acts on: what a role's remit is, what it must refuse, what the task agent does between
stages, and how an instruction is expressed.

! **It does not own what the tools DO.** A reviewer that needs a different fact from the census
is a `backend` request; the agent file may not describe an output the census does not produce.

### `backend` -- what the Python actually does

`src/comment_review/**`: the lexer, the page, the addresser, the census, the
compositor, the galley, the record, the desk, the collator. It owns the reading, the addressing, the
setting and the checking -- and `docs/addressing.md` and `docs/parsing.md`, which describe them.

! **It does not own the agent's instructions.** Changing what the census EMITS is `backend`;
changing what a reviewer is told to DO with it is `agents`.

! **AND IT OWNS ITS OWN TESTS.** A case in `tests/` asking whether this Python does what it says
is `backend`'s to write and to keep green -- see [`lanes.md`](lanes.md), *`tests/**` -> the lane
that owns what the test ASKS*. Landing a behaviour change with nothing able to notice it regress
is this lane's defect.

### `testing` -- how well the running system does, and what that is scored against

`evals/`, `evidence/`, `corpora/`. The planted hazards and their pass criteria, the test cases,
**the grader**, the grades it keeps, and the pinned corpora. Its work lives on the harness
branch.

!! **IT DOES NOT OWN `tests/`, AND THIS FILE SAID IT DID UNTIL 2026-08-24.** Roy: *"testing's
lane is specifically about building and testing the running agent system that is in the testing
harness branch. If it is backend testing that is on you. If it is vocabulary and system gating
tests that is systems. Running the tests for the agents is the agents responsibility, it is
testing's lane to make the grader and keep the grades."* **A test is owned by the lane that owns
what it makes a claim about** -- the table is in [`lanes.md`](lanes.md), the ruling is
`decision-log.md Process: #5`.

! **THE COST OF THE OLD ROW IS THE ONE IT WAS MEASURED ON.** Two `record.py` regressions were
filed to `testing` on 2026-08-24 because they landed in `tests/` -- shipping a backend fix with
nothing able to notice it regress, and parking the test on a lane whose work is a grader on
another branch.

!! **A test that cannot fail is a defect wherever it lives, not a pass.** See
[`gates.md`](gates.md): *"does the check pass" is not the question; "could the check fail" is.*

! It does not own the gates that run in CI -- those are `systems`.

### `systems` -- whether it installs, and whether the gates bite

`scripts/**` (the dev tools), the manifests, the release, `.gitignore`, `CHANGELOG.md`, and
`docs/gates.md`. It owns `check_shipped_syntax.py`, `check_vocabulary.py`, `todo_tool.py`,
`fetch_corpora.py`, `dead_sweep.py` and the floor-interpreter rules.

!! **A LANE THAT TRIPS A GATE FIXES ITS OWN CODE. It does not edit the gate to let the code
through.** That is the one crossing this repo has no tolerance for, because a gate edited to
pass is indistinguishable afterwards from a gate that always passed.

!! **AND `systems` OWNS THE BACKLOG AS A BOARD.** Roy, 2026-08-23: *"the systems lane can
reassign the owner or split/merge any set of todos appropriately."* Any lane FILES a TODO in
whatever lane owns the thing it found; `systems` decides where each one sits, splits one that
holds two problems, and merges two that hold one.

! **ADDING A TASK IS ANY LANE'S.** Roy, 2026-08-23: *"adding a task can be done by any lane
because that is a result of who found it creates it."* A lane that finds something writes it
down where it belongs, in the file that owns it -- waiting for the owning lane to notice is how
a finding becomes a session transcript.

! **What is NOT any lane's:** ticking a box and rewriting an Objective belong to the lane that
owns the WORK, because both assert that the work's state or shape has changed. Moving a file
between owners, splitting one that holds two problems, and merging two that hold one are
arrangement, and arrangement is `systems`'.

---

## The vocabulary is shared, and crossing is the point

Roy, 2026-08-23: *"any side can and should update the vocab on the other side as soon as a split
or modification is noticed."*

`references/vocabulary.toml` and `docs/vocabulary.md` belong to **no lane**. A lane that renames
something, splits a module, or notices a term drifting **updates the other side in the same
change**. It does not file a TODO and move on, and it does not wait to be asked.

!! **THE COST OF WAITING IS MEASURED.** A rename that stopped at the code left 32 quoted rulings
and 31 uses of a retired word in prose an agent reads, past a green suite, `ty`, `ruff`, the
floor gate, the vocabulary gate and the corpus round trip -- see
[`evidence/rename-left-history-in-the-comments/`](../evidence/rename-left-history-in-the-comments/README.md).
Every gate answered a different question, and the only thing that could have caught it was the
lane that did the renaming saying so on the other side.

! **This is ONE OF TWO standing exceptions to *name the lane and ask*** -- the other is below,
and it is the same principle. Everywhere else, asking is cheap and editing in passing is how a
change nobody reviewed reaches a file nobody owns.

---

## A one-for-one substitution is not a crossing

Roy, 2026-08-24, on a `backend` change that forces every command in `SKILL.md` to be spelled
differently: *"This doesn't land in the other lane just like a vocabulary change doesn't land
in the other lane. A one for one swap is allowed."*

**A lane may make a MECHANICAL one-for-one swap in another lane's file when its own change
forces it. What it may not do is change what the instruction MEANS.**

| | allowed | not allowed |
| --- | --- | --- |
| a command's spelling | `python x/y.py` -> `python -m pkg.y` | adding a flag, changing an argument |
| a renamed symbol | the new name at every site | rewording the sentence around it |
| a moved file | the new path | changing WHEN the stage runs it |

!! **THE TEST IS WHETHER A READER'S BEHAVIOUR CHANGES.** If the agent does the same thing for
the same reason and only types something different, it is a substitution. If it would now do
something different, decide differently, or refuse where it did not -- that is the owning
lane's, and the answer is *name the lane and ask*.

! **IT IS THE SAME PRINCIPLE AS THE VOCABULARY RULE, arriving from the other side.** There, a
lane must update the other side because leaving it stale rots. Here, a lane may update the
other side because leaving it stale BREAKS -- a command that names a path that no longer
exists is not a stylistic lag, it is an instruction that cannot be followed. **In both, the
alternative is filing a TODO and shipping a file that is wrong in the meantime.**

---

## T, P and SP -- what references what, and in which direction

Roy, 2026-08-23. Three kinds of checkbox exist and they are not interchangeable.

| | lives in | is | references |
| --- | --- | --- | --- |
| **T** | `TODO/*.md` | **the goal.** One verifiable checkpoint of work that is wanted | nothing |
| **P** | `docs/plans/*.md` | **a step along the way** to accomplishing one or more Ts | the T tasks it works |
| **SP** | `docs/superpowers/plans/*.md` | **a subplan of a P** -- exact files, TDD steps, a commit per task | the P steps it accomplishes |

!! **THE ARROWS GO ONE WAY: `SP -> P -> T`.** A plan cites the TODOs it works; a superpowers
plan cites the plan steps it delivers. **A TODO takes no DEPENDENCY on a plan** -- nothing in
`TODO/` may wait on a plan, be closed by one, or read its state from one, so a closed plan
leaves the backlog intact.

! **CITING A PLAN AS EVIDENCE IS NOT A DEPENDENCY.** *"14 dead links live in
`docs/plans/0.2.4-*`"* and *"the token appears only at `...md:423`"* are MEASUREMENTS that
happen to land on a plan file, and they are fine. What is forbidden is a T whose state a P
decides. ! The test is whether deleting every plan would leave the TODO still answerable: a
measurement survives it, a dependency does not.

!! **A `P` NAMES THE `T` TASKS IT WORKS, NOT JUST THE FILE.** *"Closes
`some-todo.md` (0/4)"* is not checkable -- a reader cannot tell which of the four it
delivers, and the box cannot be verified by anyone who did not write it. Name the tasks:
*"works tasks 1, 2 and 4 of ..."*. That is what makes a ticked box re-derivable by a
stranger, which is the standard `CLAUDE.md` sets for the release gate.

! **BOTH ARE ADDED AS THE WORK IS FIGURED OUT.** A T appears whenever a finding is made; a P
appears whenever a step towards one becomes clear. Neither list is settled at the start, and
neither is closed by the other being written.

! **AND A `T` IS STILL A VERIFIABLE CHECKPOINT** -- see `CLAUDE.md`, *A box is a claim about
whether work remains*. A ruling, a measurement or a piece of reasoning is not a T, and
wrapping it in a P does not make it one.

---

## How a `P` gets written, and when

Roy, 2026-08-24, porting this from `job_board` deliberately: *"put the planning process
into their conventions.md"*, and the reason is his own -- **it is a guardrail against
jumping into the work before the scope exists.** It is here rather than in a TODO because
a rule that only exists where you would go looking after the fact is not a guardrail.

!! **A BRANCH STARTS WITH A PLAN, NOT WITH CODE.** A `docs/plans/*.md` entry names the `T`
tasks it works, and it is what says when the branch is finished. A plan assembled
AFTERWARDS is a description of what happened -- it cannot tell anyone whether the work is
done, because it was written from what got done.

1. **Roy suggests the scope of work.** A sentence or two naming the release or the problem.
2. **The scope is worked out together** -- what it entails, what "done" means, and what is
   outside it.
3. **An agent drafts the `P` steps** for review.
4. **Roy requests modifications until he approves.**
5. **The agent writes the plan file.**
6. **Branch, commit the plan, then start the work.**

!! **STEP 4 IS THE AUTHORING; THE DRAFTING IS STENOGRAPHY.** Roy, 2026-08-24: *"I can't
write it I am not there at all ... I suggest the scope of work. We work together to figure
out what the scope of work entails. You draft the steps in the plan for me to review. I
request modifications until I approve the plan."* ! What cannot be delegated is naming the
scope and approving the result. Those are what make a plan a contract instead of a
suggestion, and neither depends on who types it.

! **A "DONE" THAT CANNOT BE CHECKED IS NOT A GATE.** *"The reviewer works"* is a feeling;
*"a compound citation is either rejected or fully resolved"* is a claim a stranger can
test. This is the same standard the `P` section above sets for naming the `T` tasks a plan
works -- a box a stranger cannot re-derive is not finished, it is asserted.

! **Where a design deliberately reaches into territory that will later belong somewhere
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

!! **AND THE ANSWER IS WRITTEN DOWN BEFORE THE CODE, NOT DEFENDED AFTER IT.** A `T` names
the work and a `P` names the step, and both exist so a piece's purpose is on the record
before anyone implements it. **A purpose first stated in a review is a justification, not
a design** -- it is produced by looking at the code, so it can only ever agree with it.

! **THE MEASURED FAILURE IS A FIELD THAT ANSWERS NEITHER.** `desk/mark.py` declared
`owes_destination` and **nothing read it**: measured 2026-08-30,
`grep -rn "owes_destination" src/` returned three lines and all three were in the file that
declares it. A flag nobody reads cannot make the system correct and serves no purpose,
and it survived because no plan ever had to say what it was for.

!! **SUPERSEDED THE SAME DAY, AND THE WAY IT WAS SUPERSEDED IS THE POINT.** `f17b712`
gave the flag a reader -- `parse` now runs `_destination_problems` under it, refusing a
`move` whose `claim.to` equals its own address. The grep returns five lines, one of them a
read. **The measurement above stands as of its date and the rule it argues for is
unchanged; what moved is the example.**

! **A FIELD DOES NOT BECOME NECESSARY BY BEING WIRED -- IT BECOMES NECESSARY WHEN SOMETHING
WOULD OTHERWISE BE WRONG.** Here something was: a move onto its own address reached the
docket as a bare delete, so the flag now answers *what would be incorrect without it*. That
is the answer this section asks for, arriving a plan late rather than never. ! The three
lines were the honest reading on the day; leaving them uncorrected would make this section
an instance of the rot it exists to forbid.

! **IT IS THE SAME STANDARD THIS REPO APPLIES TO PROSE, ARRIVING FROM THE OTHER SIDE.**
`CLAUDE.md` refuses a sentence that cannot be falsified by reading the code; this refuses
a piece of code that cannot be justified by naming what would otherwise be wrong.

---

## What a box may SAY -- the four openings, and why everything else is a trap

Roy, 2026-08-29: *"the box must declare what it is implementing, updating, deleting or for
Roy explicitly the question that needs to be answered once it becomes part of the critical
path. everything else is prose and is a trap."*

**A box opens with ONE of four things.** Whatever follows is the `Verify:` -- how a stranger
checks it -- and that may carry as many clauses as the one deliverable needs.

| the box declares | it reads |
| --- | --- |
| **implement** | *"Implement X, where ..."* |
| **update** | *"Update X so that ..."* |
| **delete** | *"Delete X ..."* |
| **a question for Roy** | the question itself, asked |

!! **A STATEMENT OF FACT IS NOT A BOX.** *"The last revise IS the 7a draft"* is already true
or false, so nothing in it says when the work is done -- and it stays readable as a task
either way. A bare noun phrase -- *"The composition answer set"* -- names an artifact and no
work at all.

!! **THE PROOF THAT A BOX WAS MALFORMED IS THAT IT COULD BE SUPERSEDED IN PART.** A box
naming one deliverable cannot be half-overtaken. `0.2.4`'s **T6.1** named four answers as the
closed set and **T6.3** named four outcomes; `decision-log.md Process: #49` then added a
SECOND question to the revise step, and each box was left half-right -- correct for a
conflict, wrong for a composition. Both were retired whole, which took the conflict half's
only specification with them and had to be carried back as T6.12-T6.14.

!! **AND A PROSE BOX CAN BE TICKED OVER A HALF THAT WAS NEVER REACHABLE.** `0.2.4`'s **T4.3**
reads *"A scope-declaring `query` is a boundary report and does not block the other roles"* --
an assertion, not work -- and carries its own note: *"THE SECOND CLAUSE IS NOT VERIFIED BY
WHAT LANDED."* It is `[x]`.

! **MEASURED 2026-08-29 on `docs/plans/0.2.4-the-mark-and-the-collator.md`: 38 of 67 boxes are
prose, 25 name an action, and NONE poses a question** -- so the decisions that plan waits on
are not visible as boxes anywhere in it.

! **THE RULE IS MECHANICAL, WHICH IS THE WHOLE POINT.** *"Is this a verifiable checkpoint"*
is a judgement and was already written down; *"does this box open with implement, update,
delete, or a question"* is a reading, and a stranger can run it down a file. `CLAUDE.md`
states the symptom -- *"the tell is that it cannot be finished"* -- and this states the
cause.

---

## Where a finding goes -- a TASK first, a FILE only when nothing holds it

Roy, 2026-08-30: *"Every finding gets a TODO task - only open new files if the todo
truely doesn't have a good home. For general fixes a new TODO can be made per module.
When there are multiple dependencies where it is a design objective that needs the todos
that can be split into a new file"*

**`CLAUDE.md` says every finding gets a TODO, *"an existing one it fits, or its own."*
This is the test for WHICH -- and the default is the task.**

| the finding | where it goes |
| --- | --- |
| fits an open TODO's subject | **a task on that file** |
| a general fix with no obvious file | **a per-MODULE TODO**, opened once and added to |
| a design objective whose several dependencies each need their own tasks | **its own file** |

!! **A NEW FILE IS THE EXCEPTION AND HAS TO EARN ITSELF.** MEASURED 2026-08-30: **34 of
159 open TODOs carry three tasks or fewer**, two of them ONE, against a mean of 7.3 over
1,155 tasks. Re-derive with `grep -h "^Progress:" TODO/*.md`. ! Each was a defensible
filing on the day it was made; what they add up to is a board whose index is longer than
most of the work in it, where a reader scanning `TODO/README.md` cannot tell a SUBJECT
from a single observation.

!! **AND THE COST IS PAID BY WHOEVER WORKS THE MODULE, NOT BY WHOEVER FILED.** Four
separate files each holding one `desk/collator.py` defect are four things to find, four
Objectives saying the same thing about one module, and four closes. That is why
[`collator-defects`](../TODO/collator-defects.md) exists and carries a standing note that
the four are superseded into it **in one pass** rather than closed by hand one at a time.

! **THE TELL THAT A FILE IS WARRANTED IS DEPENDENCY, NOT SIZE.** Tasks that must land
**TOGETHER** -- because they block each other, or because none of them is finished until
all of them are -- are a design objective and may have their own file. Tasks that merely
share a module are a module TODO. **A single observation is never a file.**

! **TOGETHER, NOT MERELY IN AN ORDER.** Roy, 2026-08-30, correcting this sentence's first
wording. Almost any set of tasks has an order somebody would prefer, so *"they must land
in an order"* is a test nearly everything passes -- and a test nearly everything passes
is what put 34 single-observation files on this board. **What earns a file is that
landing one without the others leaves the objective unmet.**

! **AND A FILE OPENED IN ERROR IS SUPERSEDED, NOT DELETED.** `CLAUDE.md`'s rule covers a
filing mistake as much as work overtaken: move the tasks to their home, then
`complete --superseded` with an outcome naming where they went.

---

## Working agreements

- **Name the lane and ask.** A one-line question costs less than a change the owning lane has to
  discover by reading a diff.
- **A finding gets a TODO TASK, in whatever lane owns the thing found.** The lane that FOUND it
  files it; the lane that OWNS it works it. **A new FILE only when nothing holds it** -- see
  *Where a finding goes*, above.
- **A gate is not a lane's to relax.** See `systems`, above.
- **A ruling is recorded by whoever received it** -- `docs/decision-log.md` for what and when,
  `docs/history.md` for why. Neither is owned.
- **`Owner:` is who ticks the boxes; `Requires-Roy:` is whether a DECISION is owed.** They answer
  different questions and a file may carry both.

! **What this exists to stop is a lane fixing something in passing.** The change is usually small
and usually right, and it lands in a file whose owner never saw it, in a branch about something
else -- so the next person to touch that file reads it as settled.
