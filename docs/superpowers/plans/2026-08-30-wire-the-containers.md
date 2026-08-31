# Wire the Containers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give `desk/containers.py` and the collator's source-verification half a production
caller, so the shape a copy must be is stated in ONE place and every refusal in them can
fire.

**Architecture:** A container guards the **ENVELOPE** -- is this document the shape a copy
must be, or does it error out. `flows.collate.problems_in` rules on the **CONTENTS** -- the
per-mark problems that route back to the role that wrote them. Two boundaries, not two
competing contracts. The flow calls both, in that order.

**Tech Stack:** Python 3.11 (floor, annotations EAGER), standard library only under
`src/comment_review/**`, `pytest`, `ruff`, `ty`.

**Spec:** none written; the design is `TODO/containers-and-verification-are-unwired.md`'s
Objective plus `decision-log.md Process: #57` and `#58`. Read both with this plan.

**Scope:** the FIVE wiring tasks of that TODO, T1-T5. Roy, 2026-08-30: *"You can add just the
five that are to be done in this session - no reason to overload the sp plan. We can have
another set of todos to clean the remainder up later."* Its other seventeen tasks are review
findings that live on the same file and stay on the board.

**Why now:** `docs/superpowers/plans/2026-08-30-the-move-composite.md` is BLOCKED on this.
Measured 2026-08-30: `parse_move` would be reached only through `parse_edit_copy`, which has
no production importer, so the move composite's every refusal would ship unreachable.

## Global Constraints

- Run everything through `uv run`. Python **3.11** floor; annotations are EAGER.
- `src/comment_review/**` imports the **standard library and nothing else**.
- **No `except` clause in a shipped file holds a tuple literal** -- bind it to a name.
- **ASCII only.** `--` for an em dash.
- **No subjective claims.** If a sentence cannot be falsified by reading the code or running a
  command, it does not belong.
- **`clean` is a RESERVED WORD** -- one of seven instructions -- never a loose adjective.
- **No sentence may name a symbol, file or test that does not exist at that commit.**
- **NO HEREDOCS AND NO `sed`.** A `PreToolUse` hook refuses them.
- `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check` must pass.
- `tests/gates/test_build.py::...::test_the_plugin_is_built_from_the_current_source` is
  EXPECTED to fail throughout. Exactly one failure is correct.
- Do not `git push`. Do not amend existing commits.

## What exists, exactly

| symbol | signature | where |
| --- | --- | --- |
| `collate` | `(stage: str, edit_copies: list[dict], binder: dict) -> Collated` | `flows/collate.py:460` |
| `parse_edit_copy` | `(where: str, data: object) -> tuple[EditCopy \| None, list[str]]` | `desk/containers.py:134` |
| `parse_master_proof` | `(...) -> tuple[MasterProof \| None, list[str]]` | `desk/containers.py:187` |
| `gather` | `(stage: str, edit_copies: list[dict]) -> dict` | `desk/proof.py:40` |
| `verify_report` | `(report: dict, binder: dict, root: Path) -> list[str]` | `desk/collator.py:336` |
| `problems_in` | `(report: dict) -> tuple[list[Problem], int]` | `desk/collator.py:424` |

`collate`'s body loops `edit_copies` calling `problems_in`, `drift_in`, `unruled` and `tally`
per copy, then `gather`s them into a proof and reconciles. Read `flows/collate.py:486-541`
before Task 1 -- every task here changes that loop or what precedes it.

---

### Task 1: The flow refuses a copy that is not the shape a copy must be

**Files:**
- Modify: `src/comment_review/flows/collate.py` -- the loop at `486-499`
- Test: `tests/test_collate.py`

**Interfaces:**
- Consumes: `desk.containers.parse_edit_copy(where, data)`.
- Produces: `collate` refuses a malformed copy by name before any per-mark work.

**Why:** `Process: #57`. Roy: *"the containers are an explicit statement for what is
contained and what can be contained or errors out."* Today `parse_edit_copy` has no
production importer and `collate` re-derives the shape as it goes.

!! **THE ENVELOPE ERRORS OUT; THE CONTENTS ARE REPORTED.** `parse_edit_copy` answers *is this
document a copy at all*. `problems_in` answers *what did this role write in this slot*, and
its problems route back to that role. **They are not competing contracts** and both run --
the container first, because a document that is not a copy has no contents to rule on.

- [ ] **Step 1: Write the failing test**

```python
def test_a_copy_that_is_not_the_shape_of_a_copy_is_refused_by_name():
    """The ENVELOPE, not the contents -- there are no marks to rule on here."""
    binder = a_binder_over({"m.py@b1": "# one\n"})
    with pytest.raises(MalformedCopy) as caught:
        collate("4c", [{"role": "block-context", "read_from": {"root": "."}}], binder)
    assert "sheets" in str(caught.value)


def test_a_well_formed_copy_still_reaches_the_per_mark_checks():
    """The container must not swallow what `problems_in` exists to report."""
    binder = a_binder_over({"m.py@b1": "# one\n"})
    copies = copies_over(binder, {"block-context": {"m.py@b1": a_mark_missing_its_reason()}})
    got = collate("4c", copies, binder)
    assert got.problems != []
```

! The second test is the one that matters. A container that refuses too much would make the
per-mark reporting unreachable, which is the defect this plan exists to remove, arriving from
the other side.

! **ADD `a_mark_missing_its_reason()` TO `tests/helpers.py`** -- one filled mark whose
`reason` is absent, so `problems_in` has something to report. Build it from `seed()` over a
real binder and then fill it, never from a literal: a fixture written in the shape the code
expects can only CONFIRM, which is why this repo replaced its whole suite on 2026-08-25.

- [ ] **Step 2: Run both and watch the first fail**

Run: `uv run pytest tests/test_collate.py -k shape_of_a_copy -v`
Expected: FAIL -- `MalformedCopy` is not raised and not defined.

- [ ] **Step 3: Add the refusal**

Define `MalformedCopy` in `desk/containers.py` beside the parses. In `collate`, before the
per-copy loop, parse each copy and raise naming the copy's role and the problems.

! **BIND THE EXCEPTION TUPLE TO A NAME** if you catch more than one type anywhere -- no
`except` in a shipped file holds a tuple literal.

! `collate`'s docstring has a `Raises:` block naming `UnnamedRole` and `MismatchedRoot`. Add
this one. A raise a caller is not told about is the defect `commands/collate.py` was measured
hitting on 2026-08-30.

- [ ] **Step 4: Run the tests** -- both PASS. Then `uv run pytest -q`.

- [ ] **Step 5: Run the checks**

```bash
uv run pytest -q
uv run ruff check . && uv run ruff format --check . && uv run ruff check .
uv run ty check
```

Only `test_build` may fail.

- [ ] **Step 6: Commit the WORK -- no ticked boxes in this commit**

- [ ] **Step 7: Tick the boxes this task closes**

`containers-and-verification-are-unwired` **T1**. Read that task's own verify text before
ticking -- not its title.

- [ ] **Step 8: Commit the ticks, citing the work commit's SHA**

---

### Task 2: The master proof is parsed at its own boundary

**Files:**
- Modify: `src/comment_review/flows/collate.py` -- after `gather` at line 500
- Test: `tests/test_collate.py`

**Interfaces:**
- Consumes: `desk.containers.parse_master_proof`.
- Produces: `collate` refuses a proof that is not the shape a master proof must be.

**Why:** `Process: #57`, the same rule one level up. `gather` builds the proof and nothing
states what a proof IS before `reconcile` walks it.

!! **MEASURED 2026-08-30, AND IT IS WHY THIS IS NOT COSMETIC:** `parse_master_proof` compares
`read_from` only against `copies[0]`, never copies 2..N, so a proof holding `block-context`
from revise 0 and `function-context` from revise 1 returns `(MasterProof, [])` while
`desk.proof.gather` raises `MismatchedRoot` on the identical input. **The two disagree**, and
the docstring claims the parse refuses *"the disagreement `gather` itself refuses"*.

! **THAT DEFECT IS `containers-and-verification-are-unwired` T7 AND IS NOT THIS TASK.** Wire
the parse here; T7 fixes what it checks. Do not fix both in one task -- the wiring must be
reviewable on its own.

- [ ] **Step 1: Write the failing test**

```python
def test_a_proof_that_is_not_the_shape_of_a_proof_is_refused_by_name():
    binder = a_binder_over({"m.py@b1": "# one\n"})
    with pytest.raises(MalformedProof):
        collate("4c", copies_whose_gather_yields_no_edit_copies(binder), binder)
```

Add `copies_whose_gather_yields_no_edit_copies` to `tests/helpers.py`, built from `bind()`
and `seed()` over a real binder rather than a literal.

- [ ] **Step 2: Run it and watch it fail**
- [ ] **Step 3: Parse the proof after `gather`, raise `MalformedProof` naming the problems**
- [ ] **Step 4: Run the tests, then `uv run pytest -q`**
- [ ] **Step 5: Run the checks** (`pytest`, `ruff check`, `ruff format --check`, `ruff check`
  again, `ty check`) -- only `test_build` may fail
- [ ] **Step 6: Commit the WORK -- no ticked boxes in this commit**
- [ ] **Step 7: Tick the boxes** -- `containers-and-verification-are-unwired` **T2**, reading
  its verify text first
- [ ] **Step 8: Commit the ticks, citing the work commit's SHA**

---

### Task 3: Source verification runs in production

**Files:**
- Modify: `src/comment_review/flows/collate.py`
- Modify: `src/comment_review/commands/collate.py` -- it must supply a root
- Test: `tests/test_collate.py`

**Interfaces:**
- Consumes: `desk.collator.verify_report(report, binder, root)`.
- Produces: a mark whose `sources` citation does not resolve is reported by a RUN OF THE
  FLOW, not only by calling the function.

**Why:** `Process: #58`. Roy: *"the source-verification side needs to be wired into the flow -
same as 1) the flow coordinates the things in the modules do."* MEASURED 2026-08-30:
`verify_report` has ONLY test callers -- six call sites, all in `tests/test_collator.py`.

- [ ] **Step 0: RULED -- read this, then proceed**

`verify_report` READS FILES: `source_problems` calls `_lines(root, path, cache)` to check a
citation resolves. That looked like a contradiction with `Process: #62`, *"the middle touches
no files"*, and this task was held until Roy answered it on 2026-08-30.

**IT IS NOT A CONTRADICTION, AND THE TEST IS THE `sha`.** Roy: *"a sources citation points at
evidence, which may be any file. Reading evidence isn't editing a page ... They are also not
sha'd because the evidence pages are not modifying data."*

| | carries a `sha` | the middle may |
| --- | --- | --- |
| a page under review | **yes** -- it will be written | never touch it |
| a cited evidence file | **no** -- nothing writes it | read it |

! **AND THE ROLES ALREADY GREP EVIDENCE** during their own review, so this adds no kind of
access the run did not have. `#62` is qualified in the decision log; `#58` stands. Proceed.

- [ ] **Step 1: Write the failing test**

! **ADD `a_correct_citing(cite: str)` TO `tests/helpers.py`** -- a `correct` mark whose
`sources` holds one citation with that `cite` string. `a_correct` already exists; build on it
rather than writing a second builder for the same instruction.

```python
def test_a_citation_that_does_not_resolve_is_reported_by_a_RUN(tmp_path):
    """Not by calling verify_report -- by running the flow, which is the gap."""
    binder = a_binder_over({"m.py@b1": "# one\n"})
    copies = copies_over(binder, {"block-context": {
        "m.py@b1": a_correct_citing("nowhere.py:99"),
    }})
    got = collate("4c", copies, binder, root=tmp_path)
    assert any("nowhere.py" in str(p) for p in got.problems)
```

- [ ] **Step 2: Run it and watch it fail**

- [ ] **Step 3: Give `collate` a `root` and call `verify_report`**

`collate`'s signature becomes `(stage, edit_copies, binder, root)`. **Read every caller
first** -- `grep -rn "collate(" src/ tests/`. `commands/collate.py` must supply it; the binder
names the tree it was censused from in `read_from`, and the command already resolves a repo.

! Where `verify_report`'s findings land is a decision this task must make and state: they are
strings today, and `Collated.problems` holds `Problem(role, address, message)`. **Say in the
code which they are and why** -- a source-verification finding names a mark, so it has a role
and an address.

- [ ] **Step 4: Run the tests, then `uv run pytest -q`**
- [ ] **Step 5: Run the checks** (`pytest`, `ruff check`, `ruff format --check`, `ruff check`
  again, `ty check`) -- only `test_build` may fail
- [ ] **Step 6: Commit the WORK -- no ticked boxes in this commit**
- [ ] **Step 7: Tick the boxes** -- `containers-and-verification-are-unwired` **T3**. Verify
  by running `grep -rn "verify_report" src/`, which must return a caller outside
  `desk/collator.py`
- [ ] **Step 8: Commit the ticks, citing the work commit's SHA**

---

### Task 4: One definition of a well-formed copy survives

**Files:**
- Modify: `src/comment_review/flows/collate.py`, `src/comment_review/desk/collator.py`
- Test: `tests/test_collate.py`

**Interfaces:**
- Produces: no two places in `src/` decide what a well-formed edit copy is.

**Why:** `Process: #57`. MEASURED 2026-08-30: `desk/collator.py` hand-rolls `isinstance`
checks with its own definition of a valid copy while `containers.py` declares one -- **two
definitions, one of them reached by nothing**. Tasks 1 and 2 gave the declaration a caller;
this removes the duplicate.

!! **READ BEFORE CUTTING, AND CUT ONLY WHAT THE CONTAINER NOW ANSWERS.** A hand-rolled check
that guards something `parse_edit_copy` does NOT check is load-bearing and stays. `grep -rn
"isinstance" src/comment_review/desk/collator.py src/comment_review/flows/collate.py` and go
through them one at a time.

! **A GUARD THAT CANNOT FIRE IS NOT AUTOMATICALLY DEAD.** This repo's rule, from
`TODO/galley-refusals-cannot-fire.md`: a guard at the boundary and a guard at the point of
use is defensible depth. **What is not defensible is prose claiming a guard is load-bearing
when the enforcement is upstream.** Where you keep one, say which it is.

- [ ] **Step 1: Write the failing test**

```python
def test_one_definition_decides_what_a_copy_is():
    """MEASURED 2026-08-30: two definitions, one reached by nothing."""
    got = collate("4c", [a_copy_missing_its_sheets()], binder)  # must refuse identically
    ...
```

! **ADD `a_copy_missing_its_sheets()` TO `tests/helpers.py`** -- one edit copy with a
`role` and a `read_from` and no `sheets` key at all.

! This test is the one place this plan cannot give you exact code, because what it asserts
depends on which duplicates you find in Step 2. **Write it after the grep, and make it fail
before you cut.** A test written after the cut can only agree with you.

- [ ] **Step 2: Enumerate the duplicates and record them in the report**
- [ ] **Step 3: Delete only those the container now answers for**
- [ ] **Step 4: Run the tests, then `uv run pytest -q`**
- [ ] **Step 5: Run the checks** -- only `test_build` may fail
- [ ] **Step 6: Commit the WORK -- no ticked boxes in this commit**
- [ ] **Step 7: Tick the boxes** -- `containers-and-verification-are-unwired` **T4**
- [ ] **Step 8: Commit the ticks, citing the work commit's SHA**

---

### Task 5: The prose states what each boundary refuses and what it reports

**Files:**
- Modify: `src/comment_review/desk/containers.py`, `src/comment_review/desk/collator.py`

**Interfaces:**
- Produces: no sentence in either file claims a consumer that `grep -rn` does not show.

**Why:** `Process: #57`. Both files carry prose written while they had no production caller.
MEASURED 2026-08-30: `containers.py` claimed consumers had stopped re-deriving keys when
nothing imported it, and `collator.py`'s groupings have been wrong three times.

- [ ] **Step 1: Fix every claim about a consumer**

`grep -rn "containers" src/` and `grep -rn "verify_report" src/` now return real callers.
Every sentence in either file that describes who calls it must match that output.

! **THE ENVELOPE/CONTENTS SPLIT IS STATED ONCE, NOT IN BOTH FILES.** Pick the file that owns
it and cite from the other. A rule in two places is a rule that will disagree with itself.

- [ ] **Step 2: Delete the provisional notes this plan made false**

`grep -rn "PROVISIONAL\|provisional" src/comment_review/` -- some were written against the
unwired state. A provisional note whose condition has passed is a stale claim.

- [ ] **Step 3: Run the checks** -- `pytest`, `ruff check`, `ruff format --check`, `ruff
  check` again, `ty check`, and `uv run python scripts/check_vocabulary.py`
- [ ] **Step 4: Commit the WORK -- no ticked boxes in this commit**
- [ ] **Step 5: Tick the boxes** -- `containers-and-verification-are-unwired` **T5**, and
  reread T1-T4's verify text to confirm each still holds after this task's prose changes
- [ ] **Step 6: Commit the ticks, citing the work commit's SHA**

---

## Ticking is its own step, in every task

**Every task ends in FOUR BOXES:**

    check  ->  commit the WORK  ->  tick  ->  commit the TICKS

!! **THE TICK COMMIT IS SECOND AND SEPARATE.** A box asserts the work is DONE, and the work
is not done until it is committed -- so a tick in the same commit asserts a completion that
has not happened yet. Citing the work's SHA is what makes the box re-derivable by a stranger.

!! **READ EACH BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** Not its title. Measured on this repo
2026-08-30: three boxes were ticked against verifies they did not meet -- `P21` with two of
three clauses unmet, and `no-command-for-the-middle` T1 against a chain that does not run.
**Not ticking what is done and ticking what is not are the same error.**

! **A TICK MAP IS OWED BEFORE TASK 1 RUNS.** This plan names only
`containers-and-verification-are-unwired` T1-T5. The wiring also closes tasks on
`collate-flow-defects`, `collator-defects` and `binder-defects`, and nobody has mapped which.
Produce that map first, the way
`.superpowers/sdd/2026-08-30-sp1-the-containers-and-the-collate-flow/tick-map.md` was
produced for the move plan.

## Not in scope

- **The other seventeen tasks** on `containers-and-verification-are-unwired` -- review
  findings that live on the same file. Roy, 2026-08-30: *"We can have another set of todos to
  clean the remainder up later."* ! **T7 is the one to watch**: `parse_master_proof` checking
  only `copies[0]`, which Task 2 wires without fixing.
- **The move composite** -- `docs/superpowers/plans/2026-08-30-the-move-composite.md`, which
  is BLOCKED on this plan and becomes executable when it lands.
- **Deleting drift** -- that is the move plan's Task 2, under `Process: #62`.
