# The master proof, and reconciliation -- Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the middle of the chain the container it never had -- one stage's marks, gathered --
and make reconciliation turn them into a docket.

**Architecture:** A role is handed the `binder` and returns an `edit_copy` holding `sheets`, one per
page. A stage's `edit_copies` gather onto a `master_proof`. Reconciliation reads that and emits
settled alterations, escalations, and re-reads. Which roles run when moves out of a source literal
into a run-scoped topology file.

**Tech Stack:** Python 3.11 floor, standard library only in `src/comment_review/`, `pytest` + `ruff`
+ `ty` as pinned dev dependencies, all through `uv run`.

**Spec:**
[`docs/superpowers/specs/2026-08-29-the-master-proof-and-reconciliation-design.md`](../specs/2026-08-29-the-master-proof-and-reconciliation-design.md)

**Delivers:** **P7** (T7.1-T7.10) and **P4** (T4.1-T4.6) of
[`docs/plans/0.2.4-the-mark-and-the-collator.md`](../../plans/0.2.4-the-mark-and-the-collator.md).
**Works** [`master-proof-and-edit-copy`](../../../TODO/master-proof-and-edit-copy.md) T1-T5,
[`topology-is-a-source-edit`](../../../TODO/topology-is-a-source-edit.md) T1-T5,
[`collate-buckets-a-move-at-one-end`](../../../TODO/collate-buckets-a-move-at-one-end.md) T1-T3.

**Not in this plan:** T5.3 and P6. Both read reconciliation's output, which does not exist until
Task 12 lands. They get their own plan.

## Global Constraints

- **Everything through `uv run`.** Python 3.11 is the floor `plugins/` ships against.
- **Standard library only** in `src/comment_review/`. No `except` clause holds a tuple literal --
  bind it to a name (`READ_ERRORS`, `PARSE_ERRORS`).
- **No test takes its expectation from the code under test** -- `Vocabulary: #23`. An INPUT may come
  from reality (a real page through `page_for`, a real binder, the 706 recorded marks); an
  EXPECTATION may come from shipped prose, a recorded run, or a literal a human checked.
- **ASCII only in prose**, `--` for an em-dash. No subjective claims -- write what is measured,
  enforced or observed.
- **Never write `verdict` for the field.** It is `instruction` -- `Vocabulary: #17`, and
  `scripts/check_vocabulary.py` refuses it.
- **An enum member gets no second name** -- `Process: #38`. Write `Instruction.CORRECT`, never
  `CORRECT = Instruction.CORRECT`. Membership is asked of a companion frozenset, never of the class
  (`x in SomeEnum` raises `TypeError` on 3.11).
- **`plugins/` is BUILT from `src/`.** Run `uv run python scripts/build_plugin.py` and commit what it
  writes.
- **NO heredocs and NO `sed`.** A `PreToolUse` hook refuses them. Use `Write`/`Edit`, or `Write` a
  `.py` script and run it with `uv run python`. Commit messages go to a file, then
  `git commit -F <file>`.
- **A script that rewrites a source file** passes `newline=""`, deletes `__pycache__` after, and sets
  `PYTHONDONTWRITEBYTECODE=1` on subprocesses. A same-second restore of identical byte length
  otherwise leaves CPython running stale bytecode.
- **Gates, all green before every commit:** `uv run pytest -q`, `uv run ruff check .`,
  `uv run ty check src/comment_review/`, `uv run python scripts/build_plugin.py --check`,
  `uv run python scripts/check_shipped_syntax.py`, `uv run python scripts/check_vocabulary.py`.

### How every task ends: two commits, never one

!! **THE WORK IS ONE COMMIT AND THE TICKS ARE ANOTHER.** Roy, 2026-08-29: *"make certain that the
superpowers plan marks off its own work and marks off the other plans tasks at the appropriate
point. No out of sync edits. the pair is its own commit - separate from the work."*

**Three places are ticked, together, in that second commit:**

| | |
| --- | --- |
| this file | the task's own `- [ ] **Step N**` boxes |
| `docs/plans/0.2.4-the-mark-and-the-collator.md` | the `T` numbers the task delivers |
| `TODO/*.md` | via `scripts/todo_tool.py check`, which recomputes the counts |

! **NEVER HAND-EDIT A `Progress:` LINE OR A `TODO/README.md` ROW** -- the tool owns those, and the
arithmetic is the thing a hand edit gets wrong.

!! **WHY THIS IS A RULE AND NOT A HABIT. MEASURED 2026-08-28 on the previous SP: 69 boxes across 12
FINISHED tasks were never ticked**, because every dispatch named the release plan and the TODOs and
never the SP's own steps. The plan read `0 of 93` while eleven tasks had landed -- **a plan that
cannot say what it delivered**, which is the defect `CLAUDE.md` names when it rules that the boxes
ARE the state.

! **AND SPLITTING THE COMMIT IS WHAT MAKES A DRIFT VISIBLE.** With ticks folded into the work, a
half-finished tick is indistinguishable from a half-finished task. Separated, `git show` on the tick
commit is the whole claim, and any of the three missing from it is plain.

! **ONLY TICK WHAT YOU RAN.** A box whose verification you did not perform stays open, and the report
says why -- the P3 implementer declining two boxes it could not verify is the system working.

---

## File structure

| file | responsibility |
| --- | --- |
| `src/comment_review/flows/marks.py` | seeds an `edit_copy`; checks one coming back |
| `src/comment_review/desk/proof.py` | **new** -- assembles a `master_proof` from `edit_copies` |
| `src/comment_review/desk/topology.py` | **new** -- reads and validates a topology file |
| `src/comment_review/flows/fan_out.py` | **new** -- splits a binder by dispatch |
| `src/comment_review/desk/collator.py` | source-verification (built) + reconciliation (Tasks 9-12) |
| `src/comment_review/desk/stages.py` | the closed `Role` set; the `STAGES` literal goes |
| `src/comment_review/docket/docket.py` | a schedule carries `role` |

! **RECONCILIATION LANDS IN `collator.py` AND IS NOT A CHOICE** -- `Vocabulary: #19` names the
collator's two steps, and this is the second.

---

## Task 1: The sheet, and the sha that rides on it

**Delivers:** T7.1, T7.2. **Works** `master-proof-and-edit-copy` T1 and T2.

**Files:**
- Modify: `src/comment_review/flows/marks.py` (`seed`)
- Test: `tests/test_marks_flow.py`

**Interfaces:**
- Produces: `seed(binder: dict, role: str) -> dict` returning
  `{"role": str, "read_from": dict, "sheets": [{"path": str, "sha": str, "marks": [...]}]}`.
  Each mark keeps today's keys -- `address`, `anchor`, `raw_text`, `mark`.

- [x] **Step 1: Write the failing test**

```python
def test_an_edit_copy_holds_a_sheet_per_page_with_its_sha():
    # INPUT FROM REALITY: a real package through the real binder.
    binder = binder_of(DESK, 0)
    copy = seed(binder, "block-context")

    by_path = {sheet["path"]: sheet for sheet in copy["sheets"]}
    # EXPECTATION FROM THE BINDER, not from `seed`: the pages it was given.
    assert set(by_path) == {page["path"] for page in binder["pages"]}
    for page in binder["pages"]:
        assert by_path[page["path"]]["sha"] == page["sha"]


def test_every_mark_reaches_the_sheet_for_its_own_page():
    binder = binder_of(DESK, 0)
    copy = seed(binder, "block-context")
    for sheet in copy["sheets"]:
        for mark in sheet["marks"]:
            assert mark["address"].startswith(sheet["path"])
```

- [x] **Step 2: Run and confirm both fail**

Run: `uv run pytest -q tests/test_marks_flow.py -k edit_copy_holds`
Expected: FAIL with `KeyError: 'sheets'`.

- [x] **Step 3: Build sheets from the binder's pages**

`seed` stops calling `rows_of`. It walks `binder["pages"]` and, for each, emits a sheet carrying that
page's `path` and `sha`. `rows_of` stamps the path onto each row today, which is what let the flat
form lose the page; keep the per-row `address` exactly as it is.

- [x] **Step 4: Run and confirm both pass**

Run: `uv run pytest -q tests/test_marks_flow.py`

- [x] **Step 5: Prove no module outside `binder/` reads the binder for a sha**

Run: `uv run python -c "import ast,sys;sys.path.insert(0,'src');print('write a scan')"` -- replace
with a real check: walk `src/comment_review/`, and for each module outside `binder/`, assert no
`ast.Attribute` reads `sha` off a value obtained from `binder.read`. If that scan cannot be written
precisely, assert the weaker and still-checkable claim: no module outside `binder/` imports
`binder.read` **and** references `sha` in the same file. State in the test which claim it makes.

- [x] **Step 6: Commit the WORK**

```
uv run python scripts/build_plugin.py && uv run pytest -q
```

Commit the code and its tests with `-F`. **No box moves in this commit.**

- [x] **Step 7: Tick the boxes -- ITS OWN COMMIT**

!! **THE TICKS ARE A SEPARATE COMMIT, NEVER FOLDED INTO THE WORK.** Roy, 2026-08-29:
*"the pair is its own commit - separate from the work"*. **Three places move together
or none do**, so a reader can never find one ahead of another:

```
uv run python scripts/todo_tool.py check master-proof-and-edit-copy 1
uv run python scripts/todo_tool.py check master-proof-and-edit-copy 2
```

`Edit` `T7.1` and `T7.2` to `- [x]` in `docs/plans/0.2.4-the-mark-and-the-collator.md`.
`Edit` **this task's own step boxes above** to `- [x]` -- the SP marks off its own work.
Commit with `-F`.


---

## Task 2: `problems_in` and `verify_report` walk sheets

**Delivers:** T7.4. **Works** `master-proof-and-edit-copy` T4.

**Files:**
- Modify: `src/comment_review/flows/marks.py` (`problems_in`, `unruled`)
- Modify: `src/comment_review/desk/collator.py` (`verify_report`)
- Test: `tests/test_marks_flow.py`, `tests/test_collator.py`

**Interfaces:**
- Consumes: Task 1's `edit_copy`.
- Produces: `problems_in(report: dict) -> tuple[list[str], int]` and
  `verify_report(report: dict, binder: dict, root: Path) -> list[str]`, both unchanged in signature
  and both walking `report["sheets"]`.

!! **THE PASS CRITERION IS THAT NO EXPECTATION MOVES.** These functions' rules do not change --
only the shape they walk. If a test needs its ASSERTION edited rather than its FIXTURE, stop: that
means behaviour changed and this task did not intend it.

- [x] **Step 1: Write the failing test**

```python
def test_problems_in_reads_every_sheet_not_just_the_first():
    copy = seed(binder_of(DESK, 0), "block-context")
    # A malformed mark on the LAST sheet -- a walker that stops at the first
    # sheet passes this file and misses it.
    copy["sheets"][-1]["marks"][0]["mark"] = {"instruction": "correct"}
    messages, ruled = problems_in(copy)
    assert ruled == 1
    assert messages, "a correct with no claim must be refused wherever it sits"
```

- [x] **Step 2: Run and confirm it fails**

Run: `uv run pytest -q tests/test_marks_flow.py -k every_sheet`
Expected: FAIL -- `problems_in` reads `report["marks"]`, which no longer exists.

- [x] **Step 3: Walk sheets in both functions**

Replace `report["marks"]` with a walk over `report["sheets"]` then each sheet's `marks`. `unruled`
takes the same walk. `verify_report` already takes the binder for `known_addresses`; that stays.

- [x] **Step 4: Run the whole suite**

Run: `uv run pytest -q`
Expected: PASS with **no assertion edited** -- only fixtures reshaped.

- [x] **Step 5: Commit the WORK**

```
uv run python scripts/build_plugin.py && uv run pytest -q
```

Commit the code and its tests with `-F`. **No box moves in this commit.**

- [x] **Step 6: Tick the boxes -- ITS OWN COMMIT**

!! **THE TICKS ARE A SEPARATE COMMIT, NEVER FOLDED INTO THE WORK.** Roy, 2026-08-29:
*"the pair is its own commit - separate from the work"*. **Three places move together
or none do**, so a reader can never find one ahead of another:

```
uv run python scripts/todo_tool.py check master-proof-and-edit-copy 4
```

`Edit` `T7.4` to `- [x]` in `docs/plans/0.2.4-the-mark-and-the-collator.md`.
`Edit` **this task's own step boxes above** to `- [x]` -- the SP marks off its own work.
Commit with `-F`.


---

## Task 3: `sheet` becomes `edit_copy` in the prose

**Delivers:** T7.5. **Works** `master-proof-and-edit-copy` T5.

**Files:**
- Modify: `src/comment_review/flows/marks.py` (docstrings)
- Modify: `plugins/comment-review/skills/comment-review/SKILL.md`
- Modify: `plugins/comment-review/skills/comment-review/references/reviewer-brief.md`
- Modify: `docs/vocabulary.md`
- Test: `tests/gates/test_vocabulary.py`

! **A ONE-FOR-ONE SUBSTITUTION IN ANOTHER LANE'S FILE IS ALLOWED** when the change forces it --
`docs/conventions.md`. What may NOT change is what the instruction MEANS. If a sentence would make an
agent do something different, stop and say so.

- [x] **Step 1: Write the failing test**

```python
def test_no_agent_facing_file_calls_the_per_role_container_a_sheet():
    # EXPECTATION FROM `docs/vocabulary.md`, which states the four containers.
    for path in AGENT_FACING:
        text = path.read_text(encoding="utf-8")
        for n, line in enumerate(text.splitlines(), 1):
            if "sheet" in line.lower():
                assert "edit_copy" in line or "page" in line.lower(), (
                    f"{path.name}:{n} names a sheet without saying it is a page-unit"
                )
```

- [x] **Step 2: Run and confirm it fails**

Run: `uv run pytest -q tests/gates/test_vocabulary.py -k per_role_container`
Expected: FAIL naming `SKILL.md` lines.

- [x] **Step 3: Rename, and add the containers to the vocabulary**

`docs/vocabulary.md` gains the four-container table and `master proof` stops being marked
*"unnamed."* Its existing `master proof` row is EDITED, not duplicated.

- [x] **Step 4: Run**

```
uv run pytest -q && uv run python scripts/check_vocabulary.py
```

- [x] **Step 5: Commit the WORK**

```
uv run python scripts/build_plugin.py && uv run pytest -q
```

Commit the code and its tests with `-F`. **No box moves in this commit.**

- [x] **Step 6: Tick the boxes -- ITS OWN COMMIT**

!! **THE TICKS ARE A SEPARATE COMMIT, NEVER FOLDED INTO THE WORK.** Roy, 2026-08-29:
*"the pair is its own commit - separate from the work"*. **Three places move together
or none do**, so a reader can never find one ahead of another:

```
uv run python scripts/todo_tool.py check master-proof-and-edit-copy 5
```

`Edit` `T7.5` to `- [x]` in `docs/plans/0.2.4-the-mark-and-the-collator.md`.
`Edit` **this task's own step boxes above** to `- [x]` -- the SP marks off its own work.
Commit with `-F`.


---

## Task 4: The `master_proof`

**Delivers:** T7.3. **Works** `master-proof-and-edit-copy` T3.

**Files:**
- Create: `src/comment_review/desk/proof.py`
- Test: `tests/test_master_proof.py`

**Interfaces:**
- Consumes: Task 1's `edit_copy`.
- Produces: `gather(stage: str, edit_copies: list[dict]) -> dict` returning
  `{"stage": str, "read_from": dict, "edit_copies": [...]}`, and
  `MismatchedRoot(Exception)`.

- [ ] **Step 1: Write the failing test**

```python
def test_a_master_proof_holds_every_edit_copy_of_one_stage():
    binder = binder_of(DESK, 0)
    copies = [seed(binder, role) for role in ("block-context", "module-context")]
    proof = gather("4c", copies)
    assert [c["role"] for c in proof["edit_copies"]] == [
        "block-context", "module-context"
    ]
    assert proof["read_from"] == binder["read_from"]


def test_one_role_and_seven_shards_both_assemble():
    binder = binder_of(DESK, 0)
    assert len(gather("4a", [seed(binder, "ownership-context")])["edit_copies"]) == 1
    shards = [seed(binder, "block-context") for _ in range(7)]
    assert len(gather("4c", shards)["edit_copies"]) == 7


def test_an_edit_copy_from_another_root_is_refused():
    # ! THE CHECK THAT CAN FAIL: two copies censused from different revises
    # cannot be reconciled -- their addresses answer to different trees.
    a = seed(binder_of(DESK, 0), "block-context")
    b = seed(binder_of(DESK, 0), "module-context")
    b["read_from"] = {**b["read_from"], "revise": 1}
    with pytest.raises(MismatchedRoot):
        gather("4c", [a, b])
```

- [ ] **Step 2: Run and confirm all three fail**

Run: `uv run pytest -q tests/test_master_proof.py`
Expected: FAIL with `ModuleNotFoundError: comment_review.desk.proof`.

- [ ] **Step 3: Write `gather`**

It takes the `read_from` from the first copy and raises `MismatchedRoot` naming both values when a
later copy disagrees. It sorts nothing and drops nothing -- the order it is given is the order it
holds.

- [ ] **Step 4: Run**

Run: `uv run pytest -q tests/test_master_proof.py`

- [ ] **Step 5: Commit the WORK**

```
uv run python scripts/build_plugin.py && uv run pytest -q
```

Commit the code and its tests with `-F`. **No box moves in this commit.**

- [ ] **Step 6: Tick the boxes -- ITS OWN COMMIT**

!! **THE TICKS ARE A SEPARATE COMMIT, NEVER FOLDED INTO THE WORK.** Roy, 2026-08-29:
*"the pair is its own commit - separate from the work"*. **Three places move together
or none do**, so a reader can never find one ahead of another:

```
uv run python scripts/todo_tool.py check master-proof-and-edit-copy 3
```

`Edit` `T7.3` to `- [x]` in `docs/plans/0.2.4-the-mark-and-the-collator.md`.
`Edit` **this task's own step boxes above** to `- [x]` -- the SP marks off its own work.
Commit with `-F`.


---

## Task 5: The topology file and its validator

**Delivers:** T7.6. **Works** `topology-is-a-source-edit` T1.

**Files:**
- Create: `src/comment_review/desk/topology.py`
- Create: `tests/test_topology.py`
- Create: `tests/fixtures/topologies/all-at-once.toml`, `sequential.toml`, `4a-then-4c.toml`

**Interfaces:**
- Produces: `read(text: str) -> tuple[list[Stage], str]` in this repo's refuse-rather-than-raise
  shape -- `(stages, "")` when it reads, `([], reason)` when it does not.
  `Stage` is a NamedTuple `(name: str, kind: Kind, reads: str, carries: tuple[str, ...],
  dispatches: tuple[Dispatch, ...])`; `Dispatch` is `(role: Role, paths: tuple[str, ...])`.

! **THE THREE FIXTURES ARE THE SPEC'S OWN TOPOLOGIES**, copied from its section 2. They are INPUTS,
and the expectation is the spec's prose.

- [ ] **Step 1: Write the failing test**

```python
def test_each_topology_in_the_spec_parses():
    for name in ("all-at-once", "sequential", "4a-then-4c"):
        stages, why = read((TOPOLOGIES / f"{name}.toml").read_text(encoding="utf-8"))
        assert why == "", f"{name}: {why}"
        assert stages


def test_paths_fan_one_role_and_leave_the_others_whole():
    # EXPECTATION FROM THE SPEC: block-context split two ways, the others not.
    stages, why = read((TOPOLOGIES / "4a-then-4c.toml").read_text(encoding="utf-8"))
    assert why == ""
    later = [s for s in stages if s.name == "4c"][0]
    fanned = [d for d in later.dispatches if d.role == Role.BLOCK_CONTEXT]
    assert len(fanned) == 2 and all(d.paths for d in fanned)
    others = [d for d in later.dispatches if d.role != Role.BLOCK_CONTEXT]
    assert others and all(d.paths == () for d in others)


def test_a_role_outside_the_closed_set_is_refused():
    stages, why = read(
        '[[stage]]\nname="x"\nkind="editorial"\nreads="original"\n'
        '[[stage.dispatch]]\nrole="not-a-role"\n'
    )
    assert stages == [] and "not-a-role" in why
```

- [ ] **Step 2: Run and confirm all three fail**

Run: `uv run pytest -q tests/test_topology.py`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write `read`**

`tomllib` parses; every refusal returns a reason naming the offending key and its stage. A dispatch
with no `paths` yields `paths == ()`, meaning every page.

- [ ] **Step 4: Commit the WORK**

```
uv run pytest -q tests/test_topology.py
uv run python scripts/build_plugin.py && uv run pytest -q
```

Commit the code and its tests with `-F`. **No box moves in this commit.**

- [ ] **Step 5: Tick the boxes -- ITS OWN COMMIT**

!! **THE TICKS ARE A SEPARATE COMMIT, NEVER FOLDED INTO THE WORK.** Roy, 2026-08-29:
*"the pair is its own commit - separate from the work"*. **Three places move together
or none do**, so a reader can never find one ahead of another:

```
uv run python scripts/todo_tool.py check topology-is-a-source-edit 1
```

`Edit` `T7.6` to `- [x]` in `docs/plans/0.2.4-the-mark-and-the-collator.md`.
`Edit` **this task's own step boxes above** to `- [x]` -- the SP marks off its own work.
Commit with `-F`.


---

## Task 6: Forward references, enriching reads, and `carries`

**Delivers:** T7.7, T7.10. **Works** `topology-is-a-source-edit` T2 and T5.

**Files:**
- Modify: `src/comment_review/desk/topology.py`
- Test: `tests/test_topology.py`

**Interfaces:**
- Consumes: Task 5's `read`.

- [ ] **Step 1: Write the failing test**

```python
def test_reading_a_later_stage_is_refused():
    stages, why = read(
        '[[stage]]\nname="1"\nkind="editorial"\nreads="revise:2"\n'
        '[[stage.dispatch]]\nrole="block-context"\n'
        '[[stage]]\nname="2"\nkind="editorial"\nreads="original"\n'
        '[[stage.dispatch]]\nrole="module-context"\n'
    )
    assert stages == [] and "revise:2" in why


def test_reading_an_enriching_stage_is_refused_BY_NAME():
    # ! An enriching stage pulls no revise, so naming it in `reads` cannot be
    # quietly resolved to the previous editorial one.
    stages, why = read(
        '[[stage]]\nname="a"\nkind="enriching"\nreads="original"\n'
        '[[stage.dispatch]]\nrole="block-context"\n'
        '[[stage]]\nname="b"\nkind="editorial"\nreads="revise:a"\n'
        '[[stage.dispatch]]\nrole="module-context"\n'
    )
    assert stages == []
    assert "enriching" in why and "a" in why


def test_a_non_empty_carries_is_refused_with_a_reason():
    stages, why = read(
        '[[stage]]\nname="1"\nkind="editorial"\nreads="original"\ncarries=["0"]\n'
        '[[stage.dispatch]]\nrole="block-context"\n'
    )
    assert stages == [] and "carries" in why
```

- [ ] **Step 2: Run and confirm all three fail**

Run: `uv run pytest -q tests/test_topology.py -k refused`

- [ ] **Step 3: Add the three refusals**

`carries = []` parses. A non-empty one is refused with a reason naming it unbuilt -- `Process: #50`.

- [ ] **Step 4: Commit the WORK**

```
uv run pytest -q && uv run python scripts/build_plugin.py
```

Commit the code and its tests with `-F`. **No box moves in this commit.**

- [ ] **Step 5: Tick the boxes -- ITS OWN COMMIT**

!! **THE TICKS ARE A SEPARATE COMMIT, NEVER FOLDED INTO THE WORK.** Roy, 2026-08-29:
*"the pair is its own commit - separate from the work"*. **Three places move together
or none do**, so a reader can never find one ahead of another:

```
uv run python scripts/todo_tool.py check topology-is-a-source-edit 2
uv run python scripts/todo_tool.py check topology-is-a-source-edit 5
```

`Edit` `T7.7` and `T7.10` to `- [x]` in `docs/plans/0.2.4-the-mark-and-the-collator.md`.
`Edit` **this task's own step boxes above** to `- [x]` -- the SP marks off its own work.
Commit with `-F`.


---

## Task 7: Split `STAGES` -- the roles stay, the schedule goes

**Delivers:** T7.8. **Works** `topology-is-a-source-edit` T3.

**Files:**
- Modify: `src/comment_review/desk/stages.py`
- Modify: `src/comment_review/commands/mark.py`
- Test: `tests/test_stages.py`

**Interfaces:**
- Produces: `Role(StrEnum)` with `OWNERSHIP_CONTEXT`, `BLOCK_CONTEXT`, `FUNCTION_CONTEXT`,
  `MODULE_CONTEXT`, values derived via `_generate_next_value_` as
  `name.lower().replace("_", "-")`, and `ROLES = tuple(Role)` as its companion.

!! **A RUN'S TOPOLOGY MUST NOT DECIDE WHICH ROLE NAMES ARE VALID.** `commands/mark.py` draws
`--role`'s `choices=` from `STAGES` today (T1.16, 2026-08-28). It moves to `Role`.

- [ ] **Step 1: Write the failing test**

```python
def test_the_four_roles_are_a_closed_set_independent_of_any_topology():
    # EXPECTATION FROM `SKILL.md`'s stage-4 table, transcribed by hand.
    assert [str(r) for r in ROLES] == [
        "ownership-context", "block-context", "function-context", "module-context"
    ]


def test_mark_draws_its_choices_from_the_enum_not_from_a_schedule():
    import comment_review.commands.mark as mark_cmd

    source = Path(mark_cmd.__file__).read_text(encoding="utf-8")
    assert "STAGES" not in source, "a run's topology must not decide valid role names"
    assert "ROLES" in source or "Role" in source
```

- [ ] **Step 2: Run and confirm both fail**

Run: `uv run pytest -q tests/test_stages.py -k closed_set`

- [ ] **Step 3: Add `Role`, delete the `STAGES` literal, repoint `mark.py`**

`Stage`, `Kind` and `pulls_revise` stay -- `pulls_revise` reads `stage.kind` and is unchanged. The
two-row `STAGES` literal goes; `tests/test_stages.py`'s cases that read it move to reading a topology
fixture.

- [ ] **Step 4: Prove the CLI still refuses a bad role**

Run: `uv run python src/comment-review.py mark --seed --role not-a-role`
Expected: exit 2, `invalid choice`, the four names printed.

- [ ] **Step 5: Commit the WORK**

```
uv run python scripts/build_plugin.py && uv run pytest -q
```

Commit the code and its tests with `-F`. **No box moves in this commit.**

- [ ] **Step 6: Tick the boxes -- ITS OWN COMMIT**

!! **THE TICKS ARE A SEPARATE COMMIT, NEVER FOLDED INTO THE WORK.** Roy, 2026-08-29:
*"the pair is its own commit - separate from the work"*. **Three places move together
or none do**, so a reader can never find one ahead of another:

```
uv run python scripts/todo_tool.py check topology-is-a-source-edit 3
```

`Edit` `T7.8` to `- [x]` in `docs/plans/0.2.4-the-mark-and-the-collator.md`.
`Edit` **this task's own step boxes above** to `- [x]` -- the SP marks off its own work.
Commit with `-F`.


---

## Task 8: Fan a binder out by dispatch

**Delivers:** T7.9. **Works** `topology-is-a-source-edit` T4.

**Files:**
- Create: `src/comment_review/flows/fan_out.py`
- Test: `tests/test_fan_out.py`

**Interfaces:**
- Consumes: Task 5's `Stage` and `Dispatch`; Task 1's `seed`.
- Produces: `fan(binder: dict, stage: Stage) -> list[dict]` -- one `edit_copy` per dispatch, in the
  stage's own dispatch order. `OverlappingShards(Exception)` and `UncoveredPage(Exception)`.

- [ ] **Step 1: Write the failing test**

```python
def test_every_page_reaches_exactly_one_shard_of_each_role():
    binder = binder_of(DESK, 0)
    names = sorted(page["path"] for page in binder["pages"])
    stage = Stage("4c", Kind.EDITORIAL, "original", (), (
        Dispatch(Role.BLOCK_CONTEXT, (names[0],)),
        Dispatch(Role.BLOCK_CONTEXT, tuple(names[1:])),
        Dispatch(Role.MODULE_CONTEXT, ()),
    ))
    copies = fan(binder, stage)

    block = [c for c in copies if c["role"] == "block-context"]
    seen = [s["path"] for c in block for s in c["sheets"]]
    assert sorted(seen) == names          # every page, once
    assert len(seen) == len(set(seen))    # no page twice

    whole = [c for c in copies if c["role"] == "module-context"][0]
    assert sorted(s["path"] for s in whole["sheets"]) == names


def test_a_page_in_two_shards_of_one_role_is_refused():
    binder = binder_of(DESK, 0)
    name = binder["pages"][0]["path"]
    stage = Stage("4c", Kind.EDITORIAL, "original", (), (
        Dispatch(Role.BLOCK_CONTEXT, (name,)),
        Dispatch(Role.BLOCK_CONTEXT, (name,)),
    ))
    with pytest.raises(OverlappingShards):
        fan(binder, stage)
```

- [ ] **Step 2: Run and confirm both fail**

Run: `uv run pytest -q tests/test_fan_out.py`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write `fan`**

A dispatch with no `paths` gets every page. Overlap and uncovered pages each raise, naming the paths.

- [ ] **Step 4: Commit the WORK**

```
uv run pytest -q && uv run python scripts/build_plugin.py
```

Commit the code and its tests with `-F`. **No box moves in this commit.**

- [ ] **Step 5: Tick the boxes -- ITS OWN COMMIT**

!! **THE TICKS ARE A SEPARATE COMMIT, NEVER FOLDED INTO THE WORK.** Roy, 2026-08-29:
*"the pair is its own commit - separate from the work"*. **Three places move together
or none do**, so a reader can never find one ahead of another:

```
uv run python scripts/todo_tool.py check topology-is-a-source-edit 4
```

`Edit` `T7.9` to `- [x]` in `docs/plans/0.2.4-the-mark-and-the-collator.md`.
`Edit` **this task's own step boxes above** to `- [x]` -- the SP marks off its own work.
Commit with `-F`.


---

## Task 9: Group by every place a mark touches

**Delivers:** T4.1, T4.6. **Works** `collate-buckets-a-move-at-one-end` T1 and T2.

**Files:**
- Modify: `src/comment_review/desk/collator.py`
- Test: `tests/test_reconcile.py`

**Interfaces:**
- Consumes: Task 4's `master_proof`.
- Produces: `places(proof: dict) -> dict[str, list[dict]]` -- address -> the marks touching it, each
  carrying the role that made it under the key `role`.

- [ ] **Step 1: Write the failing test**

```python
def test_a_move_lands_in_both_the_origin_and_the_destination():
    # T1's failing case: a move a0 -> a8 against another role's correct on a8.
    proof = a_master_proof({
        "block-context": {"m.py@a0": a_move("m.py@a0", "m.py@a8")},
        "module-context": {"m.py@a8": a_correct("m.py@a8")},
    })
    grouped = places(proof)
    assert "m.py@a0" in grouped and "m.py@a8" in grouped
    assert len(grouped["m.py@a8"]) == 2, "the move must reach its destination"


def test_every_mark_carries_the_role_that_made_it():
    proof = a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})
    assert places(proof)["m.py@b1"][0]["role"] == "block-context"
```

- [ ] **Step 2: Run and confirm both fail**

Run: `uv run pytest -q tests/test_reconcile.py`

- [ ] **Step 3: Write `places`**

A `move`'s destination comes from its `claim.to`. `clean` marks are grouped like any other -- what
they mean is Task 10's question, not this one's.

- [ ] **Step 4: Commit the WORK**

```
uv run pytest -q && uv run python scripts/build_plugin.py
```

Commit the code and its tests with `-F`. **No box moves in this commit.**

- [ ] **Step 5: Tick the boxes -- ITS OWN COMMIT**

!! **THE TICKS ARE A SEPARATE COMMIT, NEVER FOLDED INTO THE WORK.** Roy, 2026-08-29:
*"the pair is its own commit - separate from the work"*. **Three places move together
or none do**, so a reader can never find one ahead of another:

```
uv run python scripts/todo_tool.py check collate-buckets-a-move-at-one-end 1
uv run python scripts/todo_tool.py check collate-buckets-a-move-at-one-end 2
```

`Edit` `T4.1` and `T4.6` to `- [x]` in `docs/plans/0.2.4-the-mark-and-the-collator.md`.
`Edit` **this task's own step boxes above** to `- [x]` -- the SP marks off its own work.
Commit with `-F`.


---

## Task 10: Settle, escalate, or re-read

**Delivers:** T4.2. **Implements** `Process: #49`.

**Files:**
- Modify: `src/comment_review/desk/collator.py`
- Test: `tests/test_reconcile.py`

**Interfaces:**
- Consumes: Task 9's `places`.
- Produces: `reconcile(proof: dict) -> Reconciled`, a NamedTuple
  `(settled: list[dict], escalations: list[dict], rereads: list[dict])`.

!! **THE PASS LIST IS ALREADY A COLUMN.** `owes_change` is False for exactly `clean` and `query`.
Read it from `INSTRUCTIONS`; do not retype the two names.

- [ ] **Step 1: Write the failing test**

```python
def test_one_change_settles_because_nobody_composed_anything():
    proof = a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})
    out = reconcile(proof)
    assert [s["address"] for s in out.settled] == ["m.py@b1"]
    assert out.escalations == [] and out.rereads == []


def test_two_changes_on_different_sentences_are_RE_READ_not_merged():
    proof = a_master_proof({
        "block-context": {"m.py@b1": a_correct("m.py@b1", sentence=0)},
        "module-context": {"m.py@b1": a_correct("m.py@b1", sentence=2)},
    })
    out = reconcile(proof)
    assert out.settled == []
    assert [r["address"] for r in out.rereads] == ["m.py@b1"]
    assert sorted(out.rereads[0]["roles"]) == ["block-context", "module-context"]


def test_two_changes_on_the_SAME_sentence_escalate():
    proof = a_master_proof({
        "block-context": {"m.py@b1": a_correct("m.py@b1", sentence=0)},
        "module-context": {"m.py@b1": a_correct("m.py@b1", sentence=0)},
    })
    out = reconcile(proof)
    assert [e["address"] for e in out.escalations] == ["m.py@b1"]


def test_clean_and_query_owe_no_change_so_they_compose_nothing():
    proof = a_master_proof({
        "block-context": {"m.py@b1": a_clean("m.py@b1")},
        "module-context": {"m.py@b1": a_query("m.py@b1")},
    })
    out = reconcile(proof)
    assert out.rereads == [] and out.escalations == []
```

- [ ] **Step 2: Run and confirm all four fail**

Run: `uv run pytest -q tests/test_reconcile.py -k settle or reread or escalate`

- [ ] **Step 3: Write `reconcile`**

Count the marks at a place whose instruction `owes_change`. Zero: nothing. One: settle. Two or more
on the same sentence: escalate. Two or more on different sentences: a re-read naming the roles.
Nothing is rendered -- `Vocabulary: #11`.

- [ ] **Step 4: Commit the WORK**

```
uv run pytest -q && uv run python scripts/build_plugin.py
```

Commit the code and its tests with `-F`. **No box moves in this commit.**

- [ ] **Step 5: Tick the boxes -- ITS OWN COMMIT**

!! **THE TICKS ARE A SEPARATE COMMIT, NEVER FOLDED INTO THE WORK.** Roy, 2026-08-29:
*"the pair is its own commit - separate from the work"*. **Three places move together
or none do**, so a reader can never find one ahead of another:

```
# no TODO task for this one
```

`Edit` `T4.2` to `- [x]` in `docs/plans/0.2.4-the-mark-and-the-collator.md`.
`Edit` **this task's own step boxes above** to `- [x]` -- the SP marks off its own work.
Commit with `-F`.


---

## Task 11: An `add` goes back to every role of the stage

**Delivers:** T4.3, T4.4. **Implements** the second half of `Process: #49`.

**Files:**
- Modify: `src/comment_review/desk/collator.py`
- Test: `tests/test_reconcile.py`

**Interfaces:**
- Consumes: Task 10's `reconcile`.

- [ ] **Step 1: Write the failing test**

```python
def test_an_add_reaches_a_role_that_marked_nothing_there():
    # ! Two adds at two addresses never meet under per-place grouping, so a
    # duplicated comment passes every check unless the whole stage reads them.
    proof = a_master_proof({
        "block-context": {"m.py@b1": an_add("m.py@b1")},
        "module-context": {"m.py@b9": a_clean("m.py@b9")},
    })
    out = reconcile(proof)
    reread = [r for r in out.rereads if r["address"] == "m.py@b1"][0]
    assert "module-context" in reread["roles"]


def test_a_scope_declaring_query_does_not_block_the_other_roles():
    proof = a_master_proof({
        "block-context": {"m.py@b1": a_clean("m.py@b1")},
        "function-context": {"m.py@b1": a_clean("m.py@b1")},
        "module-context": {"m.py@b1": a_clean("m.py@b1")},
        "ownership-context": {"m.py@b1": a_query("m.py@b1", shape="outside-my-role")},
    })
    out = reconcile(proof)
    assert out.escalations == []


def test_undetermined_settles_where_another_role_ruled_substantively():
    proof = a_master_proof({
        "block-context": {"m.py@b1": a_query("m.py@b1", shape="unable-to-determine")},
        "module-context": {"m.py@b1": a_correct("m.py@b1")},
    })
    out = reconcile(proof)
    assert [s["address"] for s in out.settled] == ["m.py@b1"]
    assert out.escalations == []
```

- [ ] **Step 2: Run and confirm all three fail**

Run: `uv run pytest -q tests/test_reconcile.py -k add or scope or undetermined`

- [ ] **Step 3: Implement the three rules**

An `add` names every role of the stage in its re-read -- and under fan-out, only the shard holding
that page, which is the shard whose `edit_copy` carries that path.

- [ ] **Step 4: Commit the WORK**

```
uv run pytest -q && uv run python scripts/build_plugin.py
```

Commit the code and its tests with `-F`. **No box moves in this commit.**

- [ ] **Step 5: Tick the boxes -- ITS OWN COMMIT**

!! **THE TICKS ARE A SEPARATE COMMIT, NEVER FOLDED INTO THE WORK.** Roy, 2026-08-29:
*"the pair is its own commit - separate from the work"*. **Three places move together
or none do**, so a reader can never find one ahead of another:

```
uv run python scripts/todo_tool.py check the-fields-do-not-say-a-mark-may-cite-across 7
```

`Edit` `T4.3` and `T4.4` to `- [x]` in `docs/plans/0.2.4-the-mark-and-the-collator.md`.
`Edit` **this task's own step boxes above** to `- [x]` -- the SP marks off its own work.
Commit with `-F`.


---

## Task 12: The docket carries the role, and the measurement is re-derived

**Delivers:** T4.5. **Works** `collate-buckets-a-move-at-one-end` T3.

**Files:**
- Modify: `src/comment_review/docket/docket.py`
- Modify: `src/comment_review/desk/collator.py`
- Test: `tests/test_docket.py`, `tests/test_reconcile.py`

**Interfaces:**
- Produces: a docket whose every schedule carries `role`, which `revise.pull._set_by` already reads.

!! **T4.5's "settle 13 of 16" WAS MEASURED UNDER SILENT-MERGE SEMANTICS** and `Process: #49`
invalidates it. This task RE-DERIVES the number; whatever it comes to is the new baseline. Carrying
the old one forward beside a rule that contradicts it is the failure.

- [ ] **Step 1: Write the failing test**

```python
def test_the_docket_names_the_role_that_set_each_alteration():
    proof = a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})
    docket = docket_from(reconcile(proof), proof)
    assert docket["pages"][0]["role"] == "block-context"


def test_set_by_stops_mapping_everything_to_empty():
    # `revise.pull._set_by` reads an optional `role` per page and has mapped
    # every address to "" because nothing wrote it.
    proof = a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})
    docket = docket_from(reconcile(proof), proof)
    assert set(_set_by(docket).values()) == {"block-context"}
```

- [ ] **Step 2: Run and confirm both fail**

Run: `uv run pytest -q tests/test_docket.py -k role`

- [ ] **Step 3: Write `docket_from` and add `role` to the schema**

- [ ] **Step 4: Re-derive the measurement**

Count, over `evidence/the-loop-measured-2026-08-27/`'s round-2 marks: how many of the 16 places carry
2+ marks owing a change. Write the number, and the new settle/escalate/re-read split, into
`docs/plans/0.2.4-the-mark-and-the-collator.md` beside T4.5.

- [ ] **Step 5: Commit the WORK**

```
uv run pytest -q && uv run python scripts/build_plugin.py
```

Commit the code and its tests with `-F`. **No box moves in this commit.**

- [ ] **Step 6: Tick the boxes -- ITS OWN COMMIT**

!! **THE TICKS ARE A SEPARATE COMMIT, NEVER FOLDED INTO THE WORK.** Roy, 2026-08-29:
*"the pair is its own commit - separate from the work"*. **Three places move together
or none do**, so a reader can never find one ahead of another:

```
uv run python scripts/todo_tool.py check collate-buckets-a-move-at-one-end 3
```

`Edit` `T4.5` to `- [x]` in `docs/plans/0.2.4-the-mark-and-the-collator.md`.
`Edit` **this task's own step boxes above** to `- [x]` -- the SP marks off its own work.
Commit with `-F`.

