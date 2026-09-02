# The Docket Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the one gap in the middle-to-write chain -- `collate` writes an `edit_copy`
and `proof` reads a docket, and nothing turns one into the other -- by making the proof flow
take ANY edit_copy and transcribe it as its first step.

**Architecture:** `flows/revise.py` gains `docket_of(copy) -> Docket`. `commands/proof.py`
takes `--copy` instead of `--docket`, plus `--from-docket` and `--to-docket` as the two
boundaries where the run may start or stop. `desk/collator.py` loses `docket_from` and
`_real_pages`, which deletes the last MIDDLE-to-WRITE-END import in the tree.

**Tech Stack:** Python 3.11 (floor, annotations EAGER), standard library only under
`src/comment_review/**`, `pytest`, `ruff`, `ty`.

**Plan steps this delivers:** `docs/plans/0.2.4-the-commands-for-the-middle.md` **P53-P61**.
Those close `TODO/no-command-for-the-middle.md` **T1**.

**Rulings:** `decision-log.md Process: #12` (a command exposes a flow), `#65`/`#67` (raw JSON
only at the load and the save), and Roy 2026-09-02, recorded as `#76` by Task 0.

---

## !! WHAT MAKES THIS BIGGER THAN THE GAP IT CLOSES

Roy, 2026-09-02: *"By the time the information is done on the 'middle' we should have a
resolved single edit-copy, the copy-chiefs edit-copy. But it could also be ownership contexts
edit-copy or any intermediate edit-copy which allows the stage outputs to run."*

**Any stage's output becomes a revise.** That is the mechanism behind two things already filed
and neither of them is in this plan's scope:

| | |
| --- | --- |
| `reads = "revise:N"` in a topology | a stage reads the revise an earlier stage pulled |
| `4b` -- `TODO/stage-4b-is-undefined.md` T6 | 4a's ownership-context copy becomes a revise, `census --revise 1` reads it back, and 4c reads the resolved placement |

! **THIS PLAN BUILDS THE PIECE, NOT THOSE USES.** Both are `agents` work in SKILL.md and are
tracked where they are filed. What this plan owes them is that `docket_of` accepts an
ordinary role's copy and not only the copy chief's -- which is Task 2's own verify.

## !! THE MOVE IS NOT A PROBLEM, AND AN EARLIER READING SAID IT WAS

A `move` Mark carries `claim_all=("from", "to")` -- `desk/mark.py:235,250` -- so **ONE Mark
holds both ends** and the transcribe derives two alterations from it: `None` at
`mark.address`, `mark.change` at `claim["to"]`.

! **`_chief_copy` WRITES A MOVE ONCE, AND THAT IS SUFFICIENT.** Its `id(mark)` dedup was read
on 2026-09-02 as losing the destination end. It does not: the copy holds one entry because one
entry carries both ends. `desk.collator._join_moves` keys the mark at both ends for a different
reason -- so one end cannot settle while the other escalates -- which is a RECONCILIATION
concern and not a transcription one.

! **SO THIS PLAN DOES NOT WAIT ON `move-is-a-composite-mark`** (0 of 21). When the composite
lands, `docket_of`'s two-alteration branch becomes a one-alteration-per-Mark loop and gets
simpler; nothing here has to be undone.

## Global Constraints

- Run everything through `uv run`. Python **3.11** floor; annotations are EAGER, so a name in
  an annotation must be imported at runtime. `Path.read_text(newline=...)` is 3.13 -- use
  `open()`.
- `src/comment_review/**` imports the **standard library and nothing else**. `tests/` may use
  `pytest`.
- **No `except` clause in a shipped file holds a tuple literal** -- bind every exception tuple
  to a name.
- **ASCII only.** `--` for an em dash.
- **No subjective claims.** If a sentence cannot be falsified by reading the code or running a
  command, it does not belong.
- **`clean` is a RESERVED WORD** -- one of the seven instructions -- never a loose adjective.
- **No sentence may name a symbol, file or test that does not exist at that commit.**
- **NO HEREDOCS AND NO `sed`.** A `PreToolUse` hook refuses them. Use `Edit`/`Write`, `Grep`,
  and write a commit message to a file then `git commit -F <file>`.
- `uv run ruff check .`, `uv run ruff format .`, then `uv run ruff check .` AGAIN, then
  `uv run ty check` (bare, both trees). All green.
- `tests/gates/test_build.py` is EXPECTED to fail throughout -- `plugins/` is built at RELEASE.
  **Exactly one failure is correct.**

## !! EVERY TASK ENDS WITH ITS OWN TICK STEP, AS ITS OWN COMMIT

`CLAUDE.md`: *"THE TICK STEP COMES AFTER THE WORK'S COMMIT, AND IS ITS OWN COMMIT."* A box
asserts the work is done, and the work is not done until it is committed -- so the tick names
the commit that did the work. **Not a closing section. One step per unit, in the unit.**

!! **AND IT TICKS TWO PLACES: THIS FILE'S OWN BOXES, AND THE PARENT `P`.** Ticking only the
`P` is the failure `CLAUDE.md` names against this very skill -- *"Superpowers authors plans
full of checkboxes and then tracks execution in a gitignored ledger; nothing in it ever says
to tick the plan, so the boxes it wrote stay open while every task lands."* **This file has
58 step boxes.** They are the state a stranger reads; a ledger under `.superpowers/` is
gitignored scratch and is not a substitute.

! **THE FIRST DRAFT OF THIS PLAN GOT IT WRONG**, on 2026-09-02, in the nine tick steps below
-- every one closed its `P` and none mentioned these boxes. Roy caught it by asking. It is
recorded here rather than quietly corrected, because the rule's own point is that an
obligation with no place in the sequence is what gets dropped.

---

## Tasks

### Task 0: Record the rulings

**Files:** Modify: `docs/decision-log.md`

**Landed:** `e8a773e` -- `Process: #76` (the proof flow transcribes any edit_copy) and
`#77` (`--from-docket` / `--to-docket`). Later tasks cite these two numbers.

- [x] **Step 1:** Append `Process: #76` -- the proof flow takes any edit_copy and transcribes
      it on its first step. Quote Roy, 2026-09-02, verbatim: *"flows/proof takes any edit-copy
      and does the transform of edit-copy -> docket on its first step"*, and *"it could also be
      ownership contexts edit-copy or any intermediate edit-copy which allows the stage outputs
      to run."*

- [x] **Step 2:** In the same entry, record that `Docket.from(edit_copy)` was considered and
      NOT taken. Roy called it *"provisionally okay"* while noting it *"does break the import
      rules meant to isolate the two pieces."* **It is not needed:** `flows/revise.py` already
      imports `binder.binder` (35), `desk.collator` (36) and `docket.docket` (37), so a
      transcribe in the flow adds one import from an area the file already reaches. **The
      provisional form was the harder one** -- it would have needed a marker in the code, an
      entry here, and a later migration.

- [x] **Step 3:** Append `Process: #77` -- `--from-docket` and `--to-docket`. Roy, 2026-09-02:
      *"we add a --from-docket, --to-docket flags that allow the flow to start/stop in the
      middle of the flow."* Record that this is what keeps `Docket.serialize` and
      `Docket.deserialize` alive with **production readers** rather than on a stated intent:
      Roy's first answer was to keep them *"for some logging or troubleshooting ... since it is
      there it is worth not reinventing"*, and a method kept on intent alone is what
      `scripts/dead_sweep.py` reports and a later session deletes. **The flags are the
      readers.**

- [x] **Step 4:** Commit. `git add docs/decision-log.md && git commit -F <msgfile>`

- [x] **Step 5: TICK.** Tick Task 0's boxes in THIS file. There is no `P` to close --
      this task delivers none. Note the two entry numbers in the commit message so later
      tasks can cite them. Commit the tick separately.

---

### Task 1: `text_at` moves to `desk/mark.py`

**Landed:** `586c13a` -- `P53`. The move's two ends are asserted by `TestTextAtOneEndOfAMark`.

**Delivers:** P53

**Files:**
- Modify: `src/comment_review/desk/mark.py` (add `text_at`)
- Modify: `src/comment_review/desk/collator.py` (delete `_alteration_text`, import `text_at`)
- Test: `tests/test_mark.py`

**Interfaces:**
- Produces: `text_at(address: str, mark: Mark) -> str | None`

- [x] **Step 1: Write the failing test** in `tests/test_mark.py`:

```python
def test_a_move_at_its_origin_is_a_delete():
    mark = a_mark(instruction="move", address="m.py@b1", claim={"from": "x", "to": "m.py@b7"},
                  change="the moved text")
    assert text_at("m.py@b1", mark) is None


def test_a_move_at_its_destination_carries_the_change():
    mark = a_mark(instruction="move", address="m.py@b1", claim={"from": "x", "to": "m.py@b7"},
                  change="the moved text")
    assert text_at("m.py@b7", mark) == "the moved text"


def test_an_empty_change_is_a_delete():
    mark = a_mark(instruction="drop", address="m.py@b1", change="")
    assert text_at("m.py@b1", mark) is None
```

- [x] **Step 2: Run it and watch it fail.** `uv run pytest -q tests/test_mark.py -k text_at`
      Expected: `NameError` / import error -- `text_at` does not exist.

- [x] **Step 3: Implement.** Move the body of `desk/collator.py::_alteration_text` into
      `desk/mark.py` as `text_at`, public. It is a fact about a `Mark` -- which end of a move
      an address is, and whether the change is empty -- so it belongs where `Mark` is defined
      and not in the collator. Keep its docstring, which already states both rules.

- [x] **Step 4: Point the old caller at it.** `desk/collator.py::docket_from` calls `text_at`;
      delete `_alteration_text`. **`docket_from` still exists at this task** -- Task 3 deletes
      it, and doing both here would leave a commit whose tests do not run.

- [x] **Step 5: Run the checks.** `uv run pytest -q`, then `uv run ruff check .`,
      `uv run ruff format .`, `uv run ruff check .` again, `uv run ty check`.

- [x] **Step 6: Commit.**

- [x] **Step 7: TICK.** Tick Task 1's boxes in THIS file, then `job-board --plans-dir
      docs/plans plan close 0.2.4-the-commands-for-the-middle P53 --commit <sha> --statement
      "..."` -- reading P53's own verify text before ticking. Both cite the Step 6 commit.
      Commit the tick separately.

---

### Task 2: `docket_of` -- the transcribe

**Landed:** `e8fe5d8` -- `P54`. Six cases in `TestDocketOf`; the move's two ends are the first.

**Delivers:** P54

**Files:**
- Modify: `src/comment_review/flows/revise.py`
- Test: `tests/test_revise.py`

**Interfaces:**
- Consumes: `text_at` from Task 1.
- Produces: `docket_of(copy: EditCopy) -> Docket`

- [x] **Step 1: Write the failing tests.** Build the `EditCopy` with `EditCopy.deserialize`
      over a wire dict, or the existing `tests/helpers.py` builder -- **not a hand-written
      object**, per `tests/README.md`.

```python
def test_one_move_mark_yields_two_alterations():
    copy = an_edit_copy(role="block-context", sheets=[
        a_sheet(path="m.py", sha="abc", marks=[
            a_mark(instruction="move", address="m.py@b1",
                   claim={"from": "x", "to": "m.py@b7"}, change="moved"),
        ]),
    ])
    docket = docket_of(copy)
    schedule = docket.schedules[0]
    assert [(one.cue, one.text) for one in schedule.alterations] == [
        ("b1", None), ("b7", "moved"),
    ]


def test_the_schedule_carries_the_copys_own_role():
    copy = an_edit_copy(role="ownership-context", sheets=[...])
    assert docket_of(copy).schedules[0].role == "ownership-context"


def test_a_sheet_becomes_a_schedule_with_its_path_and_sha():
    ...


def test_an_ordinary_mark_yields_one_alteration():
    ...
```

- [x] **Step 2: Run them and watch them fail.**
      `uv run pytest -q tests/test_revise.py -k docket_of`

- [x] **Step 3: Implement `docket_of`** in `flows/revise.py`. One `Sheet` becomes one
      `Schedule` carrying that sheet's own `path` and `sha` and the COPY's `role`. Each `Mark`
      becomes one `Alteration` at `cue_of(mark.address).cue` with `text_at(mark.address, mark)`
      -- except a `move`, which additionally emits one at `cue_of(mark.claim["to"]).cue` with
      `text_at(mark.claim["to"], mark)`.

      Add `EditCopy` to the imports beside the existing `desk.collator` import, and extend the
      `docket.docket` import to `Alteration, Docket, Schedule`.

- [x] **Step 4: Prove it takes an ordinary role's copy, not only the chief's.** The test at
      Step 1 uses `role="ownership-context"`; that is the assertion, and it is what the two
      downstream uses named at the top of this plan depend on.

- [x] **Step 5: Run the checks.** Full suite plus lint/format/lint/ty.

- [x] **Step 6: Commit.**

- [x] **Step 7: TICK.** Tick Task 2's boxes in THIS file and close P54, both citing the
      Step 6 commit. Its own commit.

---

### Task 3: `desk/collator.py` loses the write end

**Landed:** `7ae43d4` -- `P55`, `P56`. `tests/test_areas.py` is the gate, red before the cut.

**Delivers:** P55, P56

**Files:**
- Modify: `src/comment_review/desk/collator.py`
- Modify: `src/comment_review/flows/collate.py` (the stale comment)
- Modify: `tests/test_docket.py`, `tests/conftest.py`, `tests/test_page_for.py`,
  `tests/test_proof_setter.py` -- 53 references to `docket_from`
- Test: `tests/gates/` -- a new one asserting the boundary holds

- [x] **Step 1: Write the failing gate test.** This is the point of the task, so it gets a
      test that can fail:

```python
def test_the_middle_does_not_import_the_write_end():
    """desk/ may reach a LEAF. `docket` and `results` are the WRITE END.

    Roy, 2026-08-31: "No direct coupling inside of ends and middle, flows are
    neither they run the steps."
    """
    offenders = []
    for path in (ROOT / "src" / "comment_review" / "desk").rglob("*.py"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if "from comment_review.docket" in line or "from comment_review.results" in line:
                offenders.append(f"{path.name}: {line.strip()}")
    assert offenders == []
```

- [x] **Step 2: Run it and watch it fail.** Expected: one offender,
      `collator.py: from comment_review.docket.docket import Alteration, Docket, Schedule`.

- [x] **Step 3: Delete `docket_from` and `_real_pages`** from `desk/collator.py`, and the
      `docket.docket` import line with them. `_real_pages` has exactly one caller
      (`docket_from`), and `unflatten` is used in that file only inside `docket_from` -- check
      whether the `reading.addresser` import still needs it.

- [x] **Step 4: Move the 53 test references.** They test the transcription, which now lives in
      `flows/revise.py` -- so they move to `tests/test_revise.py` and call `docket_of` over an
      `EditCopy` rather than `docket_from` over `(reconciled, proof)`. **A test that cannot be
      re-expressed against `docket_of` is testing reconciliation, not transcription** -- leave
      it where it is and say so in the commit.

- [x] **Step 5: Fix the stale comment (P56).** `flows/collate.py::_chief_copy` carries a
      comment justifying its own path/sha loop: *"`_real_pages` is a private name in a file
      this module must not edit."* `_real_pages` no longer exists, so the sentence names a
      symbol that is gone -- which this plan's own Global Constraints forbid. Delete or rewrite
      it to say what is true: the loop is the only one now.

- [x] **Step 6: Run the checks.** Full suite plus lint/format/lint/ty.

- [x] **Step 7: Commit.**

- [x] **Step 8: TICK.** Tick Task 3's boxes in THIS file and close P55 and P56, all
      citing the Step 7 commit. Its own commit.

---

### Task 4: `proof` takes `--copy`

**Delivers:** P57

**Files:**
- Modify: `src/comment_review/commands/proof.py`
- Test: `tests/test_proof_command.py` (or the existing home for that command's tests)

- [ ] **Step 1: Write the failing test.** A chief `edit_copy` on disk, `--copy` pointing at
      it, and a revise at `--out` holding the altered pages.

- [ ] **Step 2: Run it and watch it fail.** Expected: `unrecognized arguments: --copy`.

- [ ] **Step 3: Implement.** Replace `--docket` with `--copy`. The command reads the file with
      `object_of`, builds an `EditCopy` with `EditCopy.deserialize`, calls `docket_of`, then
      `revise.pull` exactly as it does now.

      !! **`pull` KEEPS ITS SIGNATURE.** It takes a `Docket` and this plan does not change
      that -- the command sequences `docket_of` then `pull`, which is `Process: #12`'s "a
      command exposes a flow" with two of that flow's functions. Changing `pull` to take an
      `EditCopy` would make `--from-docket` (Task 6) need a second entry point into the same
      work.

- [ ] **Step 4: Check the refusal path still reports.** A `--copy` that will not deserialize
      must print what was wrong and exit nonzero, the way a bad `--docket` did -- `CANNOT READ`
      is what SKILL.md tells the agent to look for.

- [ ] **Step 5: Run the checks.** Full suite plus lint/format/lint/ty.

- [ ] **Step 6: Commit.**

- [ ] **Step 7: TICK.** Tick Task 4's boxes in THIS file and close P57, both citing the
      Step 6 commit. Its own commit.

---

### Task 5: `--to-docket` stops the run at the docket

**Delivers:** P58

**Files:**
- Modify: `src/comment_review/commands/proof.py`
- Test: the same file as Task 4

- [ ] **Step 1: Write the failing test.** `--copy C.json --to-docket D.json` writes a docket
      that `Docket.deserialize` accepts, and **nothing is created at `--out`**.

- [ ] **Step 2: Run it and watch it fail.**

- [ ] **Step 3: Implement.** With `--to-docket`, transcribe, write
      `json.dumps(docket.serialize(), indent=2)`, and RETURN -- no `pull`, no copytree.
      `--out` is not required when `--to-docket` is given.

      ! **THE SERIALIZE IS THE CONTAINER'S AND THE DUMP IS THE COMMAND'S**, matching
      `commands/collate.py`'s existing write -- `decision-log.md Process: #65`, `#67`.

- [ ] **Step 4: Run the checks.** Full suite plus lint/format/lint/ty.

- [ ] **Step 5: Commit.**

- [ ] **Step 6: TICK.** Tick Task 5's boxes in THIS file and close P58, both citing the
      Step 5 commit. Its own commit.

---

### Task 6: `--from-docket` starts the run at the docket

**Delivers:** P59

**Files:**
- Modify: `src/comment_review/commands/proof.py`
- Test: the same file as Task 4

- [ ] **Step 1: Write the failing test.** Round-trip: `--copy C.json --to-docket D.json`, then
      `--from-docket D.json --out DIR`, gives **the same revise** as `--copy C.json --out DIR`
      in one run. That is the assertion that the two halves compose.

- [ ] **Step 2: Run it and watch it fail.**

- [ ] **Step 3: Implement.** `--copy` and `--from-docket` are a mutually exclusive group, and
      one of them is required. `--from-docket` reads with `object_of` and
      `Docket.deserialize`, skips `docket_of`, and calls `pull`.

- [ ] **Step 4: Refuse the nonsense combination.** `--from-docket` with `--to-docket` reads a
      docket in order to write it back out; refuse it by name rather than doing it.

- [ ] **Step 5: Run the checks.** Full suite plus lint/format/lint/ty.

- [ ] **Step 6: Commit.**

- [ ] **Step 7: TICK.** Tick Task 6's boxes in THIS file and close P59, both citing the
      Step 6 commit. Its own commit.

---

### Task 7: the chain runs end to end

**Delivers:** P61, and closes `TODO/no-command-for-the-middle.md` T1

**Files:**
- Test: `tests/test_the_chain.py` (new)

- [ ] **Step 1: Write the failing test.** Over a scratch tree of two or three small files:
      `census` -> `distribute --seed` once per role -> fill each copy -> `collate` ->
      `proof --copy` -> a revise on disk. **Every step invoked as the command**, through
      `subprocess` or the command's own `main()`, with **no Python written by hand between
      them.** That wording is T1's verify and the test exists to make it checkable.

- [ ] **Step 2: Run it and watch it fail** at the `collate` -> `proof` hand-off if any earlier
      task is incomplete.

- [ ] **Step 3: Make it pass.** No new source is expected here; if something is missing, it is
      a defect in Tasks 1-6 and belongs in the task that owns it.

- [ ] **Step 4: Run the checks.** Full suite plus lint/format/lint/ty.

- [ ] **Step 5: Commit.**

- [ ] **Step 6: TICK.** Tick Task 7's boxes in THIS file and close P61, both citing the
      Step 5 commit. Then close
      `no-command-for-the-middle` T1 with `job-board --plans-dir docs/plans todo close-task
      no-command-for-the-middle T1 --commit <sha> --statement "..."`, **reading T1's own verify
      text first** -- it is explicit that the box stays open *"until the chain runs through to
      `proof`."* Commit the ticks separately from the work.

---

### Task 8: SKILL.md (`agents` LANE -- NAME THE LANE AND ASK)

**Delivers:** P60

!! **THIS TASK IS NOT `backend`'s AND IS NOT A ONE-FOR-ONE SUBSTITUTION.**
`docs/conventions.md`: a lane may make a mechanical swap in another lane's file when its own
change forces it, but **not change what the instruction MEANS.** Stage 7b currently hands
`proof` a **docket**; after this plan it hands it an **edit_copy**. The agent would do
something different, so the test the conventions file states is failed and this is the owning
lane's call.

**Files:**
- Modify: `plugins/comment-review/skills/comment-review/SKILL.md` (~line 896-917)
- Modify: `tests/gates/test_skill_commands.py` (~line 47)

- [ ] **Step 1: Ask.** Name the lane and hand over what changed: `--docket` becomes `--copy`,
      and `--from-docket`/`--to-docket` are new. SKILL.md:902 documents the docket's shape --
      `{"pages": [...]}` -- and that is now an internal artifact reachable only through
      `--to-docket`.

- [ ] **Step 2: Update the gate with the command.** `tests/gates/test_skill_commands.py:47`
      asserts the two-line invocation `proof --repo . --docket D.json \\`. It must assert what
      the command now takes. ! **THIS IS UPDATING A GATE TO MATCH A REAL CHANGE, NOT RELAXING
      ONE** -- the gate still bites, on the new surface. If the change makes the gate weaker,
      that is a defect in the change.

- [ ] **Step 3: Run the checks.** Full suite plus lint/format/lint/ty.

- [ ] **Step 4: Commit.**

- [ ] **Step 5: TICK.** Tick Task 8's boxes in THIS file and close P60, both citing the
      Step 4 commit. Its own commit.

---

## Not in scope

- **`move-is-a-composite-mark`** (0 of 21). Not a dependency -- see the header. When it lands,
  `docket_of`'s move branch simplifies; nothing here is undone.
- **`reads = "revise:N"` and `4b`.** This plan builds the piece both need and neither use.
  `stage-4b-is-undefined` T6 is where 4b is written into SKILL.md.
- **The topology's dispatches.** `no-command-for-the-middle` T12 -- `distribute` taking a
  stage, which gives `flows/fan_out.py::fan` its first caller. Independent of this plan.
- **`Schedule.role` for a two-role page.** `docket_of` reads the COPY's role, so the question
  `docket_from` answered with `""` does not arise here. If a fold ever needs per-place
  provenance, that is `a-revise-answer-has-no-artifact` T7's.

## Filing what this does not finish

Per `CLAUDE.md`: anything in a plan that does not get done is filed in `TODO/` before the plan
closes. That includes any of the 53 relocated tests that turn out to be testing reconciliation
rather than transcription (Task 3 Step 4).
