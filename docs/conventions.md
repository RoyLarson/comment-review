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
stages, and how a verdict is expressed.

! **It does not own what the tools DO.** A reviewer that needs a different fact from the census
is a `backend` request; the agent file may not describe an output the census does not produce.

### `backend` -- what the Python actually does

`skills/comment-review/scripts/*.py`: the lexer, the page, the addresser, the census, the
compositor, the galley, the record, the desk, the join. It owns the reading, the addressing, the
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

! **This is the ONLY standing exception to *name the lane and ask*.** Everywhere else, asking is
cheap and editing in passing is how a change nobody reviewed reaches a file nobody owns.

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

## Working agreements

- **Name the lane and ask.** A one-line question costs less than a change the owning lane has to
  discover by reading a diff.
- **A finding gets a TODO, in whatever lane owns the thing found.** The lane that FOUND it files
  it; the lane that OWNS it works it.
- **A gate is not a lane's to relax.** See `systems`, above.
- **A ruling is recorded by whoever received it** -- `docs/decision-log.md` for what and when,
  `docs/history.md` for why. Neither is owned.
- **`Owner:` is who ticks the boxes; `Requires-Roy:` is whether a DECISION is owed.** They answer
  different questions and a file may carry both.

! **What this exists to stop is a lane fixing something in passing.** The change is usually small
and usually right, and it lands in a file whose owner never saw it, in a branch about something
else -- so the next person to touch that file reads it as settled.
