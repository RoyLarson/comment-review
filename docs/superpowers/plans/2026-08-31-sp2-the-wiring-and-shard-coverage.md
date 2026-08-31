# SP-2: The Wiring and Shard Coverage -- Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give `desk/containers.py` and the collator's source-verification half a production
caller, so the shape a copy must be is stated in ONE place, every refusal in them can fire,
and a role that answered for part of its shard is named.

**Architecture:** Two boundaries, not two competing contracts. A container guards the
**ENVELOPE** -- is this document the shape a copy must be. `flows.collate.problems_in` rules on
the **CONTENTS** -- the per-mark problems that route back to the role that wrote them.
`flows/collate.py` calls both, envelope first, because a document that is not a copy has no
contents to rule on. Shard coverage is a third question and needs no new input: `collate`
already takes the whole binder.

**Tech Stack:** Python 3.11 (floor, annotations EAGER), standard library only under
`src/comment_review/**`, `pytest`, `ruff`, `ty`. Everything through `uv run`.

**Spec:** none, deliberately. Every design question this plan turns on is ruled in
`docs/decision-log.md` -- `Process: #57` (the container errors out, and is wired), `#58`
(the source-verification half is wired into the flow rather than split out), `#62` and its
2026-08-30 qualification (the middle touches no PAGES; a cited evidence file carries no `sha`
and may be read), `#63` (coverage reports rather than refuses) and `#64` (a container is
written through its type). **A spec restating five log entries is a second copy nobody
recomputes.** Read those five with this plan.

**Plan (`P`):** [`docs/plans/0.2.4-the-commands-for-the-middle.md`](../../plans/0.2.4-the-commands-for-the-middle.md)
-- SP-2 delivers `P21`, `P25` and `P27`.

**Lane:** `backend`. No file under `plugins/comment-review/agents/`, `SKILL.md` or
`references/*.md` is touched. `plugins/` is BUILT at release, not during development.

---

## The one design decision this plan makes, stated before its first task

!! **AN ENVELOPE FAILURE IS A `Problem`, NOT A RAISE -- AND THE RUN STILL ERRORS OUT.**
`docs/superpowers/plans/2026-08-30-wire-the-containers.md`, which this plan supersedes,
specified a `MalformedCopy` exception. That reproduces the defect it was written beside.

| | |
| --- | --- |
| `Process: #57` says | a container states what may be contained *"or errors out"* |
| finding #6 measured | `commands/collate.py:135` catches around the whole `collate()` call, so ANY raise discards every `Problem` already computed -- exit 1, **stdout empty**, one role's stripped `read_from` blocking routing for every other role |
| `Problem`'s own docstring quotes Roy | *"the errors should be stacked and capable of being read off correctly so that each can be fixed or sent back to the role"* |

!! **BOTH HOLD IF THE REFUSAL IS A `Problem`.** `commands/collate.py:143-148` already prints
every `Problem` and returns `BROKEN` **without writing the chief copy**. The run errors out;
what changes is that it says everything it found on the way. ! A `Problem` carries `role` and
`address`, which is exactly what routing a malformed copy back needs. An exception carries a
sentence, and `desk/collator.py:402-406` is the ruling that a sentence cannot be routed.

!! **AND NO CHIEF COPY IS EVER FOLDED FROM A PARTIAL SET.** Where any envelope problem exists,
`collate` collects every problem it can from the copies that DID parse and returns early with
an empty `chief`. It does not fold what is left. **A silently partial chief copy -- one role's
rulings missing, nothing saying so -- is the outcome both mechanisms exist to prevent**, and
returning early is what prevents it without discarding the report.

## Global Constraints

- Run everything through `uv run`. Python **3.11** floor; annotations are EAGER.
- `src/comment_review/**` imports the **standard library and nothing else**.
- **No `except` clause in a shipped file holds a tuple literal** -- bind it to a name.
- **ASCII only.** `--` for an em dash.
- **No subjective claims.** If a sentence cannot be falsified by reading the code or running a
  command, it does not belong.
- **`clean` is a RESERVED WORD** -- one of the seven instructions -- never a loose adjective.
- **No sentence may name a symbol, file or test that does not exist at that commit.**
- **NO HEREDOCS AND NO `sed`.** A `PreToolUse` hook refuses them.
- **A fixture is built from the code, never from a literal** -- pages from `page_for`, binders
  from `bind`, copies from `seed`. A literal appears only where malformed IS the input. This is
  the rule the 2026-08-25 suite replacement exists for: a fixture written in the shape the code
  expects can only CONFIRM.
- `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check` must pass. Order:
  **linter, formatter, linter again** -- the formatter can create a lint error.
- `tests/gates/test_build.py::...::test_the_plugin_is_built_from_the_current_source` is
  EXPECTED to fail throughout. **Exactly one failure is correct.**
- Do not `git push`. Do not amend existing commits.

**Green baseline, measured 2026-08-31 at `a46bc51`:** `1 failed, 1381 passed, 1 skipped,
3 xfailed, 90 subtests passed`; `ruff check` clean; `ruff format --check` reports 174 files
already formatted; `ty check` reports zero diagnostics. **A new error is this plan's.**

## What exists, exactly

| symbol | signature | where |
| --- | --- | --- |
| `collate` | `(stage: str, edit_copies: list[dict], binder: dict) -> Collated` | `flows/collate.py:460` |
| `parse_sheet` | `(where: str, data: object) -> tuple[Sheet \| None, list[str]]` | `desk/containers.py:105` |
| `parse_edit_copy` | `(where: str, data: object) -> tuple[EditCopy \| None, list[str]]` | `desk/containers.py:134` |
| `parse_master_proof` | `(where: str, data: object) -> tuple[MasterProof \| None, list[str]]` | `desk/containers.py:187` |
| `_read_from_problem` | `(data: dict) -> str` | `desk/containers.py` |
| `gather` | `(stage: str, edit_copies: list[dict]) -> dict` | `desk/proof.py:40` |
| `verify_report` | `(report: dict, binder: dict, root: Path) -> list[str]` | `desk/collator.py:336` |
| `problems_in` | `(report: dict) -> tuple[list[Problem], int]` | `desk/collator.py:424` |
| `Problem` | `(role, address, message)` | `desk/collator.py:399` |
| `seed` | `(binder: dict, role: str) -> dict` | `flows/distribute.py:80` |

`collate`'s body loops `edit_copies` calling `problems_in`, `drift_in`, `unruled` and `tally`
per copy (`486-499`), then `gather`s them (`500`) and reconciles. **Read
`flows/collate.py:486-541` before Task 2** -- Tasks 2-6 each change that loop or what precedes
it.

**Measured 2026-08-31, and it is what this plan closes:** `grep -rn "containers" src/
--include=*.py` returns five lines and **every one is prose inside a docstring**.
`verify_report`, `address_problems`, `claim_verbatim_problems` and `source_problems` are
reached only from `tests/test_collator.py`.

---

### Task 1: A container is written through its type

**Files:**
- Modify: `src/comment_review/desk/containers.py`
- Modify: `src/comment_review/flows/distribute.py` (`81, 85, 86, 88, 98, 99`)
- Modify: `src/comment_review/flows/collate.py` (`391, 395, 396, 397, 456, 457`)
- Modify: `src/comment_review/desk/proof.py` (`77, 78, 79`)
- Test: `tests/test_containers.py`

**Interfaces:**
- Produces: `Sheet.seed(path, sha, marks) -> dict`, `EditCopy.seed(role, read_from, sheets)
  -> dict`, `MasterProof.seed(stage, read_from, edit_copies) -> dict`. **Each returns a
  `dict`, not the dataclass** -- these are wire artifacts, and every consumer downstream
  subscripts them. The dataclass is what `parse_*` returns on the way back IN.
- Consumed by: Tasks 2-6, which construct containers through these rather than by literal.

**Why:** `Process: #64`. It is the defect `Mark.seed` closed one layer down, still open one
layer up. `desk/mark.py:329-332` records it: the write half of the round trip did not live with
the read half until 2026-08-30, so renaming a field left another module writing the old key and
**nothing could notice** -- `parse` would find the field absent.

! **`desk/collator.py` WRITES NO CONTAINER.** Its `path`/`sha`/`role`/`alterations` page at
`:1015-1023` is a DOCKET page, a different artifact, and keeps its own spelling. One angle of
the 2026-08-30 review cited it as a producer and was wrong.

- [x] **Step 1: Write the failing test**

```python
def test_a_renamed_field_breaks_the_writer_rather_than_folding_to_a_default():
    """MEASURED 2026-08-30: parse_sheet returns sha='' with problems=[] over a
    dict missing the key, where Mark.seed raises at the point the row is built."""
    row = Sheet.seed(path="m.py", sha="abc", marks=[])
    assert set(row) == {f.name for f in fields(Sheet)}


def test_every_container_the_flows_write_round_trips_through_its_own_parse():
    binder = a_binder_over({"m.py@b1": "# one\n"})
    copy = seed(binder, "block-context")
    parsed, problems = parse_edit_copy("here", copy)
    assert problems == []
    assert parsed is not None
```

! **THE FIRST TEST IS THE ONE THAT BITES.** It reads the field names off the dataclass, so a
rename that reaches `Sheet` and not `Sheet.seed` fails it. A test asserting the four literal
key names would pass a rename that broke both halves together.

- [x] **Step 2: Run both and watch the first fail**

Run: `uv run pytest tests/test_containers.py -k renamed_field -v`
Expected: FAIL -- `Sheet.seed` is not defined.

- [x] **Step 3: Add the three `seed` classmethods**

Each builds its dict from the dataclass's own field names, the way `Mark.seed` does. Read
`desk/mark.py`'s `seed` first and follow it; a second pattern for the same job is the thing
this task exists to remove.

! **`sha` NORMALIZATION MOVES INTO `Sheet.seed`.** `flows/distribute.py:98` folds a null `sha`
to `""` with a walrus and a comment explaining why; `parse_sheet:129-130` does the same on the
way back. Put it in `Sheet.seed` and cite it from the producer, so the rule is stated once.

- [x] **Step 4: Replace every literal at the fifteen producer sites**

`grep -rn '"role":\|"read_from":\|"sheets":\|"marks":\|"edit_copies":\|"stage":' src/comment_review/`
and go through them one at a time. **A site that writes a DOCKET page is not one of these.**

!! **CORRECTED IN EXECUTION, 2026-08-31: NOT EVERY ONE OF THE FIFTEEN IS A PRODUCER, AND
`flows.collate._reconcilable` MUST NOT BE WRITTEN THROUGH THE TYPE.** It FILTERS a copy rather
than building one. `EditCopy.seed` requires every declared field, so a copy carrying no
`read_from` came out holding `{}` -- and `desk.proof.gather` subscripts that key precisely so
an absent one raises. `tests/test_collate_command.py::TestExitCodes::
test_a_copy_missing_read_from_exits_one_not_a_traceback` failed on it, in the one commit it
was written that way.

! **THE TEST IS: DOES THIS SITE BUILD A CONTAINER, OR TRANSFORM ONE?** A field a filter
fabricates is a field the boundary below it can no longer refuse -- and that is the exact
defect `desk/proof.py`'s `MismatchedRoot` docstring records being closed there. `{**copy,
"sheets": sheets}` preserves an absence; a producer cannot.

- [x] **Step 5: Run the tests, then `uv run pytest -q`**

- [x] **Step 6: Run the checks**

```bash
uv run pytest -q
uv run ruff check . && uv run ruff format --check . && uv run ruff check .
uv run ty check
```

Only `test_build` may fail.

- [x] **Step 7: Commit the WORK -- no ticked boxes in this commit**

- [x] **Step 8: Tick the boxes -- in this file, in `TODO/`, and in the plan**

Tick every `- [ ]` step box of this task in
`docs/superpowers/plans/2026-08-31-sp2-the-wiring-and-shard-coverage.md`;
tick `containers-and-verification-are-unwired` **T24** in `TODO/`;
and **tick no `P` step.** `Process: #64` is a ruling this plan implements,
and no step of the release plan names it -- nothing on that side to close.

! **READ EACH BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** A box is a claim and ticking
it asserts the claim. Where only part of a box is delivered, leave it open and reword
it to track the remainder -- `CLAUDE.md`'s *superseded in part*.

! **RECOMPUTE EVERY DERIVED COUNT FROM THE BOXES**, never increment one -- each TODO's
`Progress:` and the plan's `Plan-tasks:`. That arithmetic is what a hand edit gets
wrong.

- [x] **Step 9: Commit the ticks, citing the work commit's SHA**

---

### Task 2: The flow parses each edit copy at its boundary, and reports what it refuses

**Files:**
- Modify: `src/comment_review/flows/collate.py` -- the loop at `486-499`
- Test: `tests/test_collate.py`
- Test: `tests/helpers.py` -- add `a_copy_missing_its_sheets()`

**Interfaces:**
- Consumes: `desk.containers.parse_edit_copy(where, data)`, `desk.collator.Problem`.
- Produces: `collate` names a copy that is not the shape a copy must be, as a `Problem` on
  that copy's role, and returns early with an empty `chief` rather than folding a partial set.

**Why:** `P21`, `Process: #57`. Roy: *"the containers are an explicit statement for what is
contained and what can be contained or errors out."* Today `parse_edit_copy` has no production
importer and `collate` re-derives the shape as it goes.

!! **THE ENVELOPE AND THE CONTENTS BOTH RUN, IN THAT ORDER.** `parse_edit_copy` answers *is
this document a copy at all*; `problems_in` answers *what did this role write in this slot*.
Read this plan's own decision section above before writing the refusal.

- [x] **Step 1: Write the failing test**

```python
def test_a_copy_that_is_not_the_shape_of_a_copy_is_named_on_its_role():
    """The ENVELOPE, not the contents -- there are no marks to rule on here."""
    binder = a_binder_over({"m.py@b1": "# one\n"})
    got = collate("4c", [a_copy_missing_its_sheets("block-context")], binder)
    assert [p.role for p in got.problems] == ["block-context"]
    assert "sheets" in got.problems[0].message
    assert got.chief["sheets"] == []


def test_one_malformed_copy_does_not_silence_another_role(tmp_path):
    """Finding #6, arriving from the other side: one role's bad envelope must
    not block routing for every other role."""
    binder = a_binder_over({"m.py@b1": "# one\n"})
    good = copies_over(binder, {"function-context": {"m.py@b1": a_correct("m.py@b1", sentence=None)}})
    got = collate("4c", [a_copy_missing_its_sheets("block-context")] + good, binder)
    assert {p.role for p in got.problems} == {"block-context", "function-context"}


def test_a_well_formed_copy_still_reaches_the_per_mark_checks():
    """A container that refuses too much makes per-mark reporting unreachable,
    which is this plan's own defect arriving from the other side."""
    binder = a_binder_over({"m.py@b1": "# one\n"})
    copies = copies_over(binder, {"block-context": {"m.py@b1": a_correct("m.py@b1", sentence=None)}})
    got = collate("4c", copies, binder)
    assert got.problems != []
```

! **ADD `a_copy_missing_its_sheets(role)` TO `tests/helpers.py`** -- built from `seed()` over a
real binder with the `sheets` key then removed. **Not written as a literal**: a literal here
would also be asserting the shape of a well-formed copy, which is what `seed` is for.

! `a_correct(address, sentence=None)` is the existing helper's malformed case -- check what
`problems_in` reports over it before relying on it, and use whatever the current builder gives.

- [x] **Step 2: Run all three and watch the first two fail**

Run: `uv run pytest tests/test_collate.py -k "shape_of_a_copy or does_not_silence" -v`
Expected: FAIL -- `a_copy_missing_its_sheets` is not defined.

- [x] **Step 3: Parse every copy before the per-copy loop**

Collect `(role, problems)` for each copy that does not parse. Run the existing per-copy loop
over the copies that DID parse, so their problems are reported too. If any envelope problem
exists, return a `Collated` whose `chief` is an empty copy and whose `problems` hold both sets.

! **THE ROLE MAY BE THE THING THAT IS MISSING.** `parse_edit_copy` refuses a copy with no
`role` before it can name one. Use the copy's index in that case -- `Problem` needs a role
string, and `"copy 2"` is routable where `""` is not. **Say in the code which it is.**

! `collate`'s docstring has a `Raises:` block naming `UnnamedRole` and `MismatchedRoot`. This
task removes one reason `UnnamedRole` can fire; **read the block against what still raises**
rather than adding to it.

- [x] **Step 4: Run the tests, then `uv run pytest -q`**
- [x] **Step 5: Run the checks** -- `pytest`, `ruff check`, `ruff format --check`, `ruff check`
  again, `ty check`. Only `test_build` may fail.
- [x] **Step 6: Commit the WORK -- no ticked boxes in this commit**
- [x] **Step 7: Tick the boxes -- in this file, in `TODO/`, and in the plan**

Tick every `- [ ]` step box of this task in
`docs/superpowers/plans/2026-08-31-sp2-the-wiring-and-shard-coverage.md`;
tick `containers-and-verification-are-unwired` **T1** in `TODO/`;
and **tick no `P` step**: `P21`'s verify also needs Tasks 3, 7 and 8.

! **READ EACH BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** A box is a claim and ticking
it asserts the claim. Where only part of a box is delivered, leave it open and reword
it to track the remainder -- `CLAUDE.md`'s *superseded in part*.

! **RECOMPUTE EVERY DERIVED COUNT FROM THE BOXES**, never increment one -- each TODO's
`Progress:` and the plan's `Plan-tasks:`. That arithmetic is what a hand edit gets
wrong.

- [x] **Step 8: Commit the ticks, citing the work commit's SHA**

---

### Task 3: The master proof is parsed at its own boundary, and its empty-copies hole closes

**Files:**
- Modify: `src/comment_review/flows/collate.py` -- after `gather` at `500`
- Modify: `src/comment_review/desk/containers.py` -- `_read_from_problem`'s `if copies:` guard
- Test: `tests/test_collate.py`, `tests/test_containers.py`

**Interfaces:**
- Consumes: `desk.containers.parse_master_proof`.
- Produces: `collate` names a proof that is not the shape a proof must be, by the same
  report-and-return-early rule as Task 2.

**Why:** `P21` and `Process: #57`, one level up -- `gather` builds the proof and nothing states
what a proof IS before `reconcile` walks it. Plus the hole measured 2026-08-30:
`_read_from_problem` runs only `if copies:`, so with `edit_copies` empty,
`parse_master_proof("p", {"stage": "4c", "edit_copies": [], "read_from": X})` returns
`problems=[]` for `X` in `'oops'`, `None`, `7`, `[]`, `{'root': 7}` and `{'junk': 1}`.

!! **AND THE TWO DICT-SHAPED VALUES ARE CARRIED INTO `MasterProof.read_from` VERBATIM.** Those
are precisely the two `desk/collator.py:467-470` records as the reason `_read_from_problem` was
reused instead of a hand-rolled `isinstance(..., dict) and truthy`. The validator re-acquired
the defect its own comment exists to explain.

! **`{}` STAYS ADMITTED, and the docstring's reasoning for it is sound** -- `gather` itself
produces `{}` for an empty `edit_copies` list. It is the other five values this closes.

! **T7 IS A DIFFERENT DEFECT AND IS NOT THIS TASK.** `parse_master_proof` compares `read_from`
only against `copies[0]`, never 2..N. Wire the parse and close the empty-copies branch here;
leave T7.

- [ ] **Step 1: Write the failing tests**

```python
@pytest.mark.parametrize("junk", ["oops", None, 7, [], {"root": 7}, {"junk": 1}])
def test_an_empty_proof_still_holds_its_read_from_to_a_shape(junk):
    """MEASURED 2026-08-30: all six returned problems=[] and two were carried
    into MasterProof.read_from verbatim."""
    _, problems = parse_master_proof(
        "p", {"stage": "4c", "edit_copies": [], "read_from": junk}
    )
    assert problems != []


def test_an_empty_proof_with_an_empty_read_from_is_still_admitted():
    """gather itself produces this shape; the docstring's reasoning stands."""
    parsed, problems = parse_master_proof(
        "p", {"stage": "4c", "edit_copies": [], "read_from": {}}
    )
    assert problems == [] and parsed is not None
```

- [ ] **Step 2: Run them and watch the first fail on all six values**
- [ ] **Step 3: Drop the `if copies:` guard from `_read_from_problem`'s call site**, keeping
  the `{}` admission. Then parse the proof after `gather` and report as Task 2 does.
- [ ] **Step 4: Run the tests, then `uv run pytest -q`**
- [ ] **Step 5: Run the checks** -- only `test_build` may fail
- [ ] **Step 6: Commit the WORK -- no ticked boxes in this commit**
- [ ] **Step 7: Tick the boxes -- in this file, in `TODO/`, and in the plan**

Tick every `- [ ]` step box of this task in
`docs/superpowers/plans/2026-08-31-sp2-the-wiring-and-shard-coverage.md`;
tick `containers-and-verification-are-unwired` **T2** and **T23** in `TODO/`;
and **tick no `P` step**: `P21`'s verify also needs Tasks 7 and 8.

! **READ EACH BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** A box is a claim and ticking
it asserts the claim. Where only part of a box is delivered, leave it open and reword
it to track the remainder -- `CLAUDE.md`'s *superseded in part*.

! **RECOMPUTE EVERY DERIVED COUNT FROM THE BOXES**, never increment one -- each TODO's
`Progress:` and the plan's `Plan-tasks:`. That arithmetic is what a hand edit gets
wrong.

- [ ] **Step 8: Commit the ticks, citing the work commit's SHA**

---

### Task 4: A refusal prints what the fold already computed

**Files:**
- Modify: `src/comment_review/commands/collate.py:133-141`
- Test: `tests/test_collate_command.py` (or wherever the command's tests live -- `grep -rn
  "commands.collate\|collate_main" tests/` first)

**Interfaces:**
- Produces: a `MismatchedRoot` refusal prints every `Problem` the per-copy pass found before it
  exits `BROKEN`.

**Why:** finding #6's remainder. Tasks 2 and 3 turn the shape failures into `Problem`s, which
dissolves the `KeyError` half at its root. **`MismatchedRoot` is what is left and cannot become
a `Problem`**: two copies censused from different revises answer to different address spaces,
so there is no `Collated` from them with any meaning -- an `a0` in one tells nothing about the
`a0` in the other (`desk/proof.py:27-31`).

!! **SO THE REFUSAL STAYS AND STOPS BEING SILENT.** `collate` must hand the accumulated
problems back with the refusal. Two shapes are available and this task picks one and says why:
an exception carrying them, or splitting `collate` so the per-copy pass returns before the
fold. **Prefer whichever leaves `collate`'s signature alone**; a fourth argument here would
collide with SP-3's `Stage`.

- [ ] **Step 1: Write the failing test**

```python
def test_a_refusal_still_prints_the_problems_the_pass_found(tmp_path, capsys):
    """MEASURED 2026-08-30 by running the real CLI: exit 1, stdout EMPTY, and
    one role's disagreeing read_from blocked routing for the other."""
    # one copy with a correct missing its reason, one censused from another root
    ...
    assert code == BROKEN
    out = capsys.readouterr()
    assert "block-context" in out.out          # the routable problem
    assert "REFUSED" in out.err                # and the refusal
```

! **THIS PLAN CANNOT GIVE YOU THE FIXTURE LINES**, because the second copy has to be censused
from a genuinely different root. Build it with `bind()` over a second `tmp_path` tree -- **not
by editing a `read_from` dict by hand**, which would test a shape rather than the situation.

- [ ] **Step 2: Run it and watch stdout come back empty**
- [ ] **Step 3: Make the refusal carry the problems, and print them before the REFUSED line**
- [ ] **Step 4: Run the tests, then `uv run pytest -q`**
- [ ] **Step 5: Run the checks** -- only `test_build` may fail
- [ ] **Step 6: Commit the WORK -- no ticked boxes in this commit**
- [ ] **Step 7: Tick the boxes -- in this file, in `TODO/`, and in the plan**

Tick every `- [ ]` step box of this task in
`docs/superpowers/plans/2026-08-31-sp2-the-wiring-and-shard-coverage.md`;
tick `collate-command-defects` **T17** in `TODO/`;
and **tick no `P` step.** Finding #6 is a review finding this plan carries,
not a step of the release plan.

! **READ EACH BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** A box is a claim and ticking
it asserts the claim. Where only part of a box is delivered, leave it open and reword
it to track the remainder -- `CLAUDE.md`'s *superseded in part*.

! **RECOMPUTE EVERY DERIVED COUNT FROM THE BOXES**, never increment one -- each TODO's
`Progress:` and the plan's `Plan-tasks:`. That arithmetic is what a hand edit gets
wrong.

- [ ] **Step 8: Commit the ticks, citing the work commit's SHA**

---

### Task 5: Source verification runs in production

**Files:**
- Modify: `src/comment_review/flows/collate.py`
- Modify: `src/comment_review/commands/collate.py` -- it must supply a root
- Test: `tests/test_collate.py`
- Test: `tests/helpers.py` -- add `a_correct_citing(address, cite)`

**Interfaces:**
- Consumes: `desk.collator.verify_report(report, binder, root)`.
- Produces: `collate`'s signature becomes `(stage, edit_copies, binder, root)`. A mark whose
  `sources` citation does not resolve is reported **by a run of the flow**, not only by calling
  the function.

**Why:** `P25`, `Process: #58`. Roy: *"the source-verification side needs to be wired into the
flow - same as 1) the flow coordinates the things in the modules do."* MEASURED 2026-08-31:
`verify_report` has only test callers.

- [ ] **Step 0: RULED -- read this, then proceed**

`verify_report` READS FILES: `source_problems` calls `_lines(root, path, cache)` to check a
citation resolves. That looked like a contradiction with `Process: #62`, *"the middle touches
no files"*, and the predecessor plan's Task 3 was held until Roy answered it on 2026-08-30.

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

```python
def test_a_citation_that_does_not_resolve_is_reported_by_a_RUN(tmp_path):
    """Not by calling verify_report -- by running the flow, which is the gap."""
    binder = a_binder_over({"m.py@b1": "# one\n"})
    copies = copies_over(binder, {"block-context": {
        "m.py@b1": a_correct_citing("m.py@b1", "nowhere.py:99"),
    }})
    got = collate("4c", copies, binder, root=tmp_path)
    assert any("nowhere.py" in p.message for p in got.problems)


def test_a_claim_quoting_a_sentence_absent_from_its_paragraph_is_reported(tmp_path):
    """The other half of verify_report, and neither is refusable by parse --
    which imports no binder, no page and no filesystem."""
    binder = a_binder_over({"m.py@b1": "# one\n"})
    copies = copies_over(binder, {"block-context": {
        "m.py@b1": a_correct("m.py@b1", sentence="a sentence that is not there"),
    }})
    got = collate("4c", copies, binder, root=tmp_path)
    assert got.problems != []
```

! **ADD `a_correct_citing(address, cite)` TO `tests/helpers.py`** -- built on the existing
`a_correct`, not as a second builder for the same instruction.

- [ ] **Step 2: Run both and watch them fail**

- [ ] **Step 3: Give `collate` a `root` and call `verify_report`**

**Read every caller first** -- `grep -rn "collate(" src/ tests/`. `commands/collate.py` must
supply it; the binder names the tree it was censused from in `read_from`, and the command
already resolves a repo.

! **THE TESTS TASKS 2, 3 AND 4 WROTE ARE CALLERS TOO**, and this step is what updates them. A
run of `uv run pytest -q` after Step 3 that reports collection errors rather than failures is
this, not a mistake.

! **WHERE `verify_report`'s FINDINGS LAND IS THIS TASK'S DECISION AND MUST BE STATED IN THE
CODE.** They are strings today and `Collated.problems` holds `Problem(role, address, message)`.
A source-verification finding names a mark, so it has both a role and an address.

- [ ] **Step 4: Run the tests, then `uv run pytest -q`**
- [ ] **Step 5: Run the checks** -- only `test_build` may fail
- [ ] **Step 6: Commit the WORK -- no ticked boxes in this commit**
- [ ] **Step 7: Tick the boxes -- in this file, in `TODO/`, and in the plan**

Tick every `- [ ]` step box of this task in
`docs/superpowers/plans/2026-08-31-sp2-the-wiring-and-shard-coverage.md`;
tick `containers-and-verification-are-unwired` **T3** in `TODO/`;
and tick **`P25`** in `docs/plans/0.2.4-the-commands-for-the-middle.md`.
**It closes HERE and nowhere else in this plan**: its verify is *"collate
runs `address_problems`, `claim_verbatim_problems` and `source_problems`
over every ruled mark"*, which is this task entire.

! **READ EACH BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** A box is a claim and ticking
it asserts the claim. Where only part of a box is delivered, leave it open and reword
it to track the remainder -- `CLAUDE.md`'s *superseded in part*.

! **RECOMPUTE EVERY DERIVED COUNT FROM THE BOXES**, never increment one -- each TODO's
`Progress:` and the plan's `Plan-tasks:`. That arithmetic is what a hand edit gets
wrong.

- [ ] **Step 8: Commit the ticks, citing the work commit's SHA**

---

### Task 6: Shard coverage, from the binder

**Files:**
- Modify: `src/comment_review/flows/collate.py`
- Test: `tests/test_collate.py`

**Interfaces:**
- Consumes: `desk.collator.known_addresses(binder)`.
- Produces: a role whose copies do not between them carry the binder's whole address set is
  named as a `Problem` on that role, and the places that DID come back still settle.

**Why:** `P27`, `Process: #63`, and `containers-and-verification-are-unwired` T6.
`flows.fan_out.fan:116-129` refuses `OverlappingShards` and `UncoveredPage` at the **dispatch**;
**nothing reads the return.** A partitioned role that answered for three of the four files in
its shard is invisible today.

!! **THE UNIT IS THE ADDRESS, NOT THE PAGE, AND THAT IS T6's WORDING RATHER THAN `P27`'s.**
`P27` names files; T6 names the address set, and measures the stronger case: *"a copy whose
`sheets` is `[]`, one whose sheets are not objects, one whose `marks` is a string, and one that
kept 1 of its 4 seeded slots are each reported by name; today all four give `problems == []`
against a binder carrying `m.py@b1..b4`."* **A dropped page is a dropped address set**, so the
address check answers `P27` and T6 both; a page check answers only `P27`.

!! **IT NEEDS NO NEW INPUT, WHICH IS WHY IT IS IN THIS PLAN AND `P26` IS NOT.** `collate`
already takes the WHOLE binder -- `base_texts(binder)` needs every address, so it cannot be a
shard -- and `known_addresses` is already written.

! **T6's OWN WORDING SAYS "THE BINDER'S ADDRESS SET" AND THAT IS TRUE PER ROLE, NOT PER COPY.**
Under fan-out a single copy carries only its shard. Compare the UNION across a role's copies;
comparing one copy against the binder reports every fan-out shard as incomplete.

! **THIS IS NOT `P28`.** Both reach for `known_addresses`, which is used only by
`flows/revise.py` today. `P28` asks whether an address reaching the DOCKET was one the binder
carried; this asks whether a role RETURNED the addresses it was given. Same helper, different
question, and `P28` is SP-4's.

! **STAGE COVERAGE IS NOT THIS TASK.** A role that returned NOTHING leaves nothing behind to be
missing from -- `flows/distribute.py:80-86` stamps a copy with `role`, `read_from` and `sheets`
and no dispatch identity. `P26` takes the `Stage` and is SP-3's; see the plan's SP table.

! **REPORTED, NOT REFUSED.** `Process: #63`: a missing answer routes back to the role that owes
it, and the places that came back still settle. **This is the one place in the plan where the
run does NOT return early** -- an incomplete shard is a fact about one role's coverage, not a
statement that the documents are malformed.

- [ ] **Step 1: Write the failing test**

!! **`collate` TAKES A `root` BY THE TIME THIS TASK RUNS.** Task 5 changed the signature to
`(stage, edit_copies, binder, root)`. Every call below passes it; a three-argument call written
from this plan's earlier tasks is a `TypeError` here.

```python
def test_a_role_that_answered_for_part_of_its_shard_is_named(tmp_path):
    """fan refuses an uncovered page at DISPATCH; nothing reads the RETURN."""
    binder = a_binder_over({"one.py@b1": "# one\n", "two.py@b1": "# two\n"})
    copies = copies_over(binder, {"block-context": {"one.py@b1": a_clean("one.py@b1")}})
    short = [_without_sheet(copies[0], "two.py")]
    got = collate("4c", short, binder, root=tmp_path)
    assert any("two.py" in p.message and p.role == "block-context" for p in got.problems)


def test_a_copy_that_kept_one_of_its_four_seeded_slots_is_named(tmp_path):
    """T6's own measured case: today all four of its shapes give problems == []
    against a binder carrying m.py@b1..b4."""
    binder = a_binder_over({f"m.py@b{i}": f"# {i}\n" for i in range(1, 5)})
    copies = copies_over(binder, {"block-context": {"m.py@b1": a_clean("m.py@b1")}})
    got = collate("4c", [_keeping_only(copies[0], ["m.py@b1"])], binder, root=tmp_path)
    assert [p.role for p in got.problems] == ["block-context"]


def test_two_shards_of_one_role_cover_the_binder_between_them(tmp_path):
    """Compared per COPY this reports every fan-out shard as incomplete."""
    binder = a_binder_over({"one.py@b1": "# one\n", "two.py@b1": "# two\n"})
    got = collate("4c", list(fan(binder, a_two_shard_stage())), binder, root=tmp_path)
    assert got.problems == []


def test_the_places_that_did_come_back_still_settle(tmp_path):
    """Process: #63 -- coverage reports; it does not void the round.

    One page answered, one not: the answered place reaches the chief's copy and
    the missing one is a problem, in the SAME run.
    """
    binder = a_binder_over({"one.py@b1": "# one\n", "two.py@b1": "# two\n"})
    copies = copies_over(binder, {"block-context": {"one.py@b1": a_correct("one.py@b1")}})
    got = collate("4c", [_without_sheet(copies[0], "two.py")], binder, root=tmp_path)
    assert got.problems != [] and got.chief["sheets"] != []
```

! **`a_two_shard_stage()` GOES IN `tests/helpers.py`** -- a `Stage` with two `Dispatch` rows for
one role, their `paths` globs splitting the two pages. `tests/test_fan_out.py` already builds
stages; take its pattern rather than a second one.

! **BUILD THE SHORT COPY BY REMOVING FROM A REAL `seed()` OUTPUT**, not by writing one with a
single sheet. The two are the same document, and only one of them proves the copy came from a
binder that held every page. Add `_without_sheet(copy, path)` and `_keeping_only(copy,
addresses)` to `tests/helpers.py` as removals over a seeded copy.

! **THE THIRD TEST IS THE ONE THAT KEEPS THIS HONEST.** `unruled` and `tally` are keyed by role
and clobber under fan-out today (finding #9) -- **do not copy that pattern here**, and this
test is what proves you did not.

- [ ] **Step 2: Run both and watch the first fail**
- [ ] **Step 3: Add the per-role coverage comparison**
- [ ] **Step 4: Run the tests, then `uv run pytest -q`**
- [ ] **Step 5: Run the checks** -- only `test_build` may fail
- [ ] **Step 6: Commit the WORK -- no ticked boxes in this commit**
- [ ] **Step 7: Tick the boxes -- in this file, in `TODO/`, and in the plan**

Tick every `- [ ]` step box of this task in
`docs/superpowers/plans/2026-08-31-sp2-the-wiring-and-shard-coverage.md`;
tick `containers-and-verification-are-unwired` **T6** in `TODO/`;
and tick **`P27`** in `docs/plans/0.2.4-the-commands-for-the-middle.md`.
**It closes HERE**: its verify is *"a partitioned role that answered for
three of the four files in its shard is named"*, and this task's address
check answers it. ! **Read `P27`'s own wording against what shipped** -- it
says FILES where T6 says the address set, and the address check is the one
that landed.

! **READ EACH BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** A box is a claim and ticking
it asserts the claim. Where only part of a box is delivered, leave it open and reword
it to track the remainder -- `CLAUDE.md`'s *superseded in part*.

! **RECOMPUTE EVERY DERIVED COUNT FROM THE BOXES**, never increment one -- each TODO's
`Progress:` and the plan's `Plan-tasks:`. That arithmetic is what a hand edit gets
wrong.

- [ ] **Step 8: Commit the ticks, citing the work commit's SHA**

---

### Task 7: One definition of a well-formed copy survives

**Files:**
- Modify: `src/comment_review/flows/collate.py`, `src/comment_review/desk/collator.py`
- Test: `tests/test_collate.py`

**Interfaces:**
- Produces: no two places in `src/` decide what a well-formed edit copy is.

**Why:** `P21`, `Process: #57`. MEASURED 2026-08-30: `desk/collator.py` hand-rolls `isinstance`
checks with its own definition of a valid copy while `containers.py` declares one -- **two
definitions, one of them reached by nothing.** Tasks 2 and 3 gave the declaration a caller;
this removes the duplicate.

!! **READ BEFORE CUTTING, AND CUT ONLY WHAT THE CONTAINER NOW ANSWERS.** A hand-rolled check
guarding something `parse_edit_copy` does NOT check is load-bearing and stays. `grep -rn
"isinstance" src/comment_review/desk/collator.py src/comment_review/flows/collate.py` and go
through them one at a time.

! **A GUARD THAT CANNOT FIRE IS NOT AUTOMATICALLY DEAD.** From
`TODO/galley-refusals-cannot-fire.md`: a guard at the boundary and a guard at the point of use
is defensible depth. **What is not defensible is prose claiming a guard is load-bearing when
the enforcement is upstream.** Where you keep one, say which it is.

- [ ] **Step 1: Enumerate the duplicates and record them in the report**

This step comes first, and the test comes after it. **This plan cannot give you the test**,
because what it asserts depends on which duplicates the grep finds. A test written after the
cut can only agree with you -- so write it against the enumeration, and make it fail.

- [ ] **Step 2: Write the failing test over one duplicate you found, and run it**
- [ ] **Step 3: Delete only those the container now answers for**
- [ ] **Step 4: Run the tests, then `uv run pytest -q`**
- [ ] **Step 5: Run the checks** -- only `test_build` may fail
- [ ] **Step 6: Commit the WORK -- no ticked boxes in this commit**
- [ ] **Step 7: Tick the boxes -- in this file, in `TODO/`, and in the plan**

Tick every `- [ ]` step box of this task in
`docs/superpowers/plans/2026-08-31-sp2-the-wiring-and-shard-coverage.md`;
tick `containers-and-verification-are-unwired` **T4** in `TODO/`;
and **tick no `P` step**: `P21`'s third clause -- *"every field declared is
one the code reads"* -- is Task 8's prose pass.

! **READ EACH BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** A box is a claim and ticking
it asserts the claim. Where only part of a box is delivered, leave it open and reword
it to track the remainder -- `CLAUDE.md`'s *superseded in part*.

! **RECOMPUTE EVERY DERIVED COUNT FROM THE BOXES**, never increment one -- each TODO's
`Progress:` and the plan's `Plan-tasks:`. That arithmetic is what a hand edit gets
wrong.

- [ ] **Step 8: Commit the ticks, citing the work commit's SHA**

---

### Task 8: The prose states what each boundary refuses and what it reports

**Files:**
- Modify: `src/comment_review/desk/containers.py`, `src/comment_review/desk/collator.py`,
  `src/comment_review/flows/collate.py`

**Interfaces:**
- Produces: no sentence in any of the three claims a consumer that `grep -rn` does not show.

**Why:** `P21`, `Process: #57`. All three carry prose written while the containers had no
production caller. MEASURED 2026-08-30: `containers.py` claimed consumers had stopped
re-deriving keys when nothing imported it, and `collator.py`'s groupings have been wrong three
times.

- [ ] **Step 1: Fix every claim about a consumer**

`grep -rn "containers" src/` and `grep -rn "verify_report" src/` now return real callers. Every
sentence in any of the three files describing who calls it must match that output.

! **THE ENVELOPE/CONTENTS SPLIT IS STATED ONCE, NOT IN THREE FILES.** Pick the file that owns
it and cite from the others. A rule in three places is a rule that will disagree with itself.

- [ ] **Step 2: Delete the provisional notes this plan made false**

`grep -rn "PROVISIONAL\|provisional" src/comment_review/` -- some were written against the
unwired state. A provisional note whose condition has passed is a stale claim.

- [ ] **Step 3: Reread every sentence Task 1 made false**

The fifteen producer sites carried comments explaining their literals -- the `sha`
normalization, COPIED-NOT-ALIASED, `checked: dict = data`. Some now describe code that moved
into a `seed`.

- [ ] **Step 4: Run the checks** -- `pytest`, `ruff check`, `ruff format --check`, `ruff check`
  again, `ty check`, and `uv run python scripts/check_vocabulary.py`
- [ ] **Step 5: Commit the WORK -- no ticked boxes in this commit**
- [ ] **Step 6: Tick the boxes -- in this file, in `TODO/`, and in the plan**

Tick every `- [ ]` step box of this task in
`docs/superpowers/plans/2026-08-31-sp2-the-wiring-and-shard-coverage.md`;
tick `containers-and-verification-are-unwired` **T5** in `TODO/`, rereading
T1-T4's verify text to confirm each still holds after this task's prose;
and tick **`P21`** in `docs/plans/0.2.4-the-commands-for-the-middle.md`.
**It closes HERE, and it is the box this repo has already ticked once
against a verify it did not meet** -- see the untick note in the step's own
text. Read all three clauses: the type matches what `seed` builds over a real
tree, the chief's copy parses as an ordinary `EditCopy` proved by a test that
CALLS `_chief_copy`, and every field declared is one the code reads.

! **READ EACH BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** A box is a claim and ticking
it asserts the claim. Where only part of a box is delivered, leave it open and reword
it to track the remainder -- `CLAUDE.md`'s *superseded in part*.

! **RECOMPUTE EVERY DERIVED COUNT FROM THE BOXES**, never increment one -- each TODO's
`Progress:` and the plan's `Plan-tasks:`. That arithmetic is what a hand edit gets
wrong.

- [ ] **Step 7: Commit the ticks, citing the work commit's SHA**

---

## Ticking is its own step, in every task

**Every task ends in FOUR BOXES:**

    check  ->  commit the WORK  ->  tick  ->  commit the TICKS

!! **THE TICK COMMIT IS SECOND AND SEPARATE.** A box asserts the work is DONE, and the work is
not done until it is committed -- so a tick in the same commit asserts a completion that has
not happened yet. Citing the work's SHA is what makes the box re-derivable by a stranger.

!! **AND THE TICK STEP TICKS THREE PLACES, NAMED ONE BY ONE IN EVERY TASK: THIS FILE, `TODO/`,
AND THE PLAN.** Roy, 2026-08-31, on a draft where only Task 8 reached the plan: *"Please add
the commit tick commit steps in the middle for both the plan and the SP plan."*

! **A `P` STEP CLOSES IN THE TASK THAT COMPLETES IT, NOT AT THE END.** `P25` closes at Task 5,
`P27` at Task 6, `P21` at Task 8 -- and the five tasks that close no `P` step **say so, and
say why**. A tick step that finds nothing to tick is still a step a stranger can check; one
that is silent about the plan is indistinguishable from one that forgot it.

! **THAT IS WHY A CLOSING SECTION WOULD NOT DO.** `CLAUDE.md`: *"Not a closing section, not a
final task that ticks everything -- one step per unit, in the unit."* A plan box has no tool
behind it -- nothing asks for a SHA, nothing refuses -- so the ordering a TODO task gets for
free is the ordering a plan box only gets from an explicit step.

!! **READ EACH BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** Not its title. Measured on this repo
2026-08-30: three boxes were ticked against verifies they did not meet -- `P21` with two of its
three clauses unmet, and `no-command-for-the-middle` T1 against a chain that does not run.
**Not ticking what is done and ticking what is not are the same error.**

! **A TICK MAP IS OWED BEFORE TASK 1 RUNS.** This plan names its `containers-and-verification-
are-unwired` and `collate-command-defects` tasks task by task. It also closes tasks on
`collate-flow-defects` and `collator-defects` that nobody has mapped. Produce that map first.

## Not in scope

- **`P26`, stage coverage** -- it needs the `Stage`, and so does `distribute`, whose
  `Stage.reads` has no reader at all (`staged-chain-untested` T4). Both land in SP-3 where the
  topology system is built, because `P32` has the agent VERIFY before it distributes and a
  consumer wired here would read an unverified configuration.
- **`P28`, address integrity over the docket** -- SP-4. `desk.collator.docket_from` has no
  caller outside `tests/`, so the check would cover a path no run takes.
- **`containers-and-verification-are-unwired` T7** -- `parse_master_proof` comparing
  `read_from` only against `copies[0]`. Task 3 wires that parser without fixing it.
- **The chief's copy is parsed by nothing** (finding #7). Ruled out of SP-2 by Roy 2026-08-31:
  the shape is still moving -- the move composite deletes `change`, and `recast` gives the
  chief a third act -- so a parse written now pins a shape two later SPs change. It lands in
  SP-4, where `docket_from` transcribes the copy and cannot avoid parsing what it transcribes.
- **`unruled` and `tally` clobbering under fan-out** (finding #9). Task 6 must not copy the
  pattern; fixing it is not this plan's.
- **The move composite** -- `docs/superpowers/plans/2026-08-30-the-move-composite.md`, which is
  BLOCKED on this plan and becomes executable when it lands.
