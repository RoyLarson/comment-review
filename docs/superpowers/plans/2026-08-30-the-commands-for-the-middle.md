# The commands for the middle -- Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the middle of the pipeline a console face, so the chain runs from a binder to a revise with no Python written by hand.

**Architecture:** `gather -> places -> reconcile -> resolve` becomes one flow, `flows/collate.py`, whose output is the copy chief's `edit_copy` -- the final container. The docket is a TRANSCRIPTION of that copy rather than a computation over reconciliation's buckets, which is what lets `docket_from` take one argument. The revise round reuses the same flow over a different input: diff-marks rather than marks.

**Tech Stack:** Python 3.11 (floor), standard library only under `src/comment_review/`, `pytest`, `ruff`, `ty`.

**Plan:** [`docs/plans/0.2.4-the-commands-for-the-middle.md`](../../plans/0.2.4-the-commands-for-the-middle.md) -- this SP delivers its `P` steps, which name the `T` tasks they close. **The arrows go one way: `SP -> P -> T`.**

## Global Constraints

- **Everything through `uv run`.** Python **3.11** is the floor.
- **Standard library only** under `src/comment_review/`. No third-party import in a shipped file.
- **No tuple literal in an `except`** -- bind it to a name (`READ_ERRORS`, `PARSE_ERRORS`).
- **ASCII prose, `--` for an em-dash.** No subjective claims ("robust", "clean" as an adjective).
- **The field is `instruction`, never `verdict`.** `block`/`blocks` is retired for `paragraph`.
- **NO heredocs, NO `sed`** -- a `PreToolUse` hook refuses them. Use `Write`/`Edit`, or `Write` a `.py` script and `uv run python` it. Commit messages: `Write` a file, then `git commit -F <file>`.
- **`plugins/` is BUILT from `src/`** -- `uv run python scripts/build_plugin.py`, and commit what it writes.
- **No test takes its expectation from the code under test.**
- **Correct code and green tests in ONE commit** (Roy, 2026-08-29).

### How every task ends: two commits, never one

!! **A `P` closes in a LATER commit than the work, because a commit cannot cite its own hash.**

1. **Commit the work.** Green. No box moves.
2. **Commit the closes, separately**, citing the work's sha:

```
job-board plan close 0.2.4-the-commands-for-the-middle P<n> \
  --statement "<how it closed>" --commit <sha> \
  --plans-dir docs/plans --todo-dir TODO
```

! **NEVER hand-edit the plan file.** The tool sets the mark, recomputes `Plan-tasks:`, and re-derives `Requires-Roy`. Hand-editing was measured on 2026-08-30 to produce the right bytes while missing three dead `T` references the tool reports on every write.

! **`job-board plan close` prints `unresolved: BT4 / BT5 / BT7` on every invocation.** That is section B's known state -- `a-revise-answer-has-no-artifact` writes ids as `T4 --` where the tool reads `T4 |`. It is not caused by your change. **Do not "fix" it by hand-editing that TODO**; the board migration is paused deliberately (`TODO/board-predates-task-ids.md`).

## File structure

| file | responsibility |
| --- | --- |
| `docs/the-mark.md` | **the source.** Gains the `edit_copy` and the copy chief's `edit_copy` |
| `src/comment_review/results/differences.py` | gains `compose(base, sides)` -- MERGES, where `diff3` only renders |
| `src/comment_review/flows/collate.py` | **new.** gather -> reconcile -> resolve, out to the chief's `edit_copy` |
| `src/comment_review/desk/collator.py` | `docket_from` changes shape; the resolution helpers live here |
| `src/comment_review/desk/chief.py` | **new.** the chief's three acts -- `taken_in`, `stet`, `recast` |
| `src/comment_review/desk/diff_mark.py` | **new.** the diff-mark artifact and its closed set of four |
| `src/comment_review/commands/collate.py` | **new.** the `collate` command |
| `src/comment_review/commands/docket.py` | **new.** the `docket` command |
| `tests/gates/test_edit_copy_shape.py` | **new.** reads the shape out of `docs/the-mark.md` |

---

## Task 1: Give the containers a type

**Delivers P21.** Nothing else may start: `P4`, `P7` and `P14` are built on a shape that exists only in code.

!! **THE CONTAINERS ARE ONE SHAPE, AND THE CHIEF'S IS NOT SPECIAL** -- `decision-log.md
Vocabulary: #30`. The chief step is a FOLD: `master_proof` holding N `edit_copies` becomes ONE
`edit_copy` whose `role` is `copy-chief`. It is the RESULT, so every place carries exactly one
mark, which is what an ordinary `edit_copy` already is.

! **A `state` FIELD WAS PROPOSED AND IS STRUCK.** `settled`, `escalated` and `reread` are the
INTERMEDIATE, and the intermediate already has a type -- `desk.collator.Reconciled`.

! **AND THE TYPE LIVES IN `desk/`, NOT A MARKDOWN SOURCE.** An agent authors a mark, so
`docs/the-mark.md` publishes its shape to a role. **No agent authors a container** -- `seed`,
`fan` and `gather` build them -- so the type IS the definition, as `desk/mark.py` defines `Mark`.

**Files:**
- Create: `src/comment_review/desk/containers.py`
- Create: `tests/test_containers.py`
- Modify: `src/comment_review/flows/marks.py` (`seed` returns the type)
- Modify: `src/comment_review/desk/proof.py` (`gather` takes and returns it)

**Interfaces:**
- Consumes: the shape as built today -- `flows/marks.py:36` (`seed`) and `desk/mark.py:318` (`allowed`).
- Produces:

```python
@dataclass(frozen=True)
class Sheet:
    path: str
    sha: str
    marks: list[Mark]

@dataclass(frozen=True)
class EditCopy:
    role: str
    read_from: dict
    sheets: list[Sheet]
    rounds: dict[str, dict[str, int]] = field(default_factory=dict)

@dataclass(frozen=True)
class MasterProof:
    stage: str
    read_from: dict
    edit_copies: list[EditCopy]
```

! **`rounds` IS ON THE ENVELOPE, NOT ON A MARK.** The chief's copy from round N is the input to
round N+1, so the tally rides the container -- `{"m.py@b1": {"composition": 1, "conflict": 0}}` --
and the mark's SEVEN FIELDS STAY SEVEN.

- [ ] **Step 1: Write the failing test -- the type matches what `seed` already builds**

```python
def test_the_edit_copy_type_matches_what_seed_BUILDS(tmp_path):
    built = seed(binder_of(a_small_real_tree(tmp_path), 0), "block-context")
    parsed, problems = EditCopy.read("probe", built)
    assert problems == []
    assert parsed.role == "block-context"
    assert parsed.sheets and parsed.sheets[0].path
```

! **THE EXPECTATION COMES FROM `seed` OVER A REAL TREE, NOT FROM A LITERAL.** A hand-written
`edit_copy` would confirm the type against itself.

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/test_containers.py -q`
Expected: FAIL -- `desk.containers` does not exist.

- [ ] **Step 3: Write `desk/containers.py` with the three types and a boundary parse**

Follow `desk/mark.py`: `read(where, entry) -> (Type | None, problems)`. **One object or named
problems, and no third outcome.**

- [ ] **Step 4: Write the failing test for the chief's copy -- same type, no new shape**

```python
def test_the_chiefs_copy_is_an_ordinary_edit_copy(tmp_path):
    chief = EditCopy(role="copy-chief", read_from={...}, sheets=[...],
                     rounds={"m.py@b1": {"composition": 1, "conflict": 0}})
    parsed, problems = EditCopy.read("probe", asdict(chief))
    assert problems == []
```

- [ ] **Step 5: Run to green, then make `seed` and `gather` return the types**

- [ ] **Step 6: Run every gate**

`uv run pytest -q`, `ruff check .`, `ty check src/comment_review/`, `build_plugin.py --check`,
`check_shipped_syntax.py`, `check_vocabulary.py`

- [ ] **Step 7: Commit the work**

- [ ] **Step 8: Close P21, in a separate commit, citing Step 7's sha**

---

## Task 2: `compose` -- the merge that `diff3` is not

**Delivers P13.** This is what answers *"how do both get taken in"* without a fifth answer.

**Files:**
- Modify: `src/comment_review/results/differences.py`
- Modify: `tests/test_differences.py`

**Interfaces:**
- Consumes: `SequenceMatcher` opcodes, as `diff3` and `_side_slice` already use.
- Produces: `compose(base: str, sides: dict[str, str]) -> str` and `OverlappingEdits`.

- [ ] **Step 1: Write the failing tests -- both directions**

```python
def test_two_edits_on_different_sentences_merge_to_a_paragraph_carrying_both():
    base = "# one.\n# two.\n# three.\n"
    out = compose(base, {"block-context": "# ONE.\n# two.\n# three.\n",
                         "function-context": "# one.\n# two.\n# THREE.\n"})
    assert out == "# ONE.\n# two.\n# THREE.\n"

def test_two_edits_on_the_SAME_span_refuse_by_name():
    base = "# one.\n"
    with pytest.raises(OverlappingEdits):
        compose(base, {"block-context": "# A.\n", "function-context": "# B.\n"})
```

! **The second test is the one that matters.** A compose that picks a side is worse than one that refuses, because it decides an editorial question with arithmetic.

- [ ] **Step 2: Run and watch both fail**

Expected: FAIL -- `compose` is not defined.

- [ ] **Step 3: Implement `compose`**

For each side, take the opcodes against the base and record which base spans it touches. If two sides touch the same span, raise `OverlappingEdits` naming the place and both roles. Otherwise apply every side's replacement to its own span and return the result.

! **`diff3` DOES NOT DO THIS and must not be changed to.** It wraps *"every span at least one side edited"* as a conflict, even where one side touched it -- a render for a reader. `compose` is the half that acts.

- [ ] **Step 4: Run to green, then the whole suite**

- [ ] **Step 5: Commit the work**

- [ ] **Step 6: Close P13, separately, citing Step 5's sha**

---

## Task 3: `flows/collate.py` -- one flow, gather to the chief's copy

**Delivers P1 and P2.**

**Files:**
- Create: `src/comment_review/flows/collate.py`
- Create: `tests/test_collate.py`

**Interfaces:**
- Consumes: `desk.proof.gather(stage, edit_copies) -> dict`; `desk.collator.places(proof)`; `desk.collator.reconcile(proof) -> Reconciled(settled, escalations, rereads)`; `results.differences.compose` from Task 2.
- Produces: `collate(stage: str, edit_copies: list[dict]) -> dict` -- the copy chief's `edit_copy`, in the shape Task 1 defined.

- [ ] **Step 1: Write the failing test**

```python
def test_collate_returns_the_chiefs_edit_copy_with_every_place_in_a_state():
    chief = collate("stage-2", [copy_a, copy_b])
    states = {m["state"] for s in chief["sheets"] for m in s["marks"]}
    assert states <= {"settled", "escalated", "reread"}
    assert chief["role"] == "copy-chief"
```

- [ ] **Step 2: Run and watch it fail**

- [ ] **Step 3: Implement the flow**

`gather` -> `reconcile` -> for each bucket, write an entry in the chief's copy carrying the state Task 1 defined.

- [ ] **Step 4: Write the failing test for the automatic resolutions (P2)**

Three cases, and only three: **one** mark owes a change (settles); **every** owing mark proposes byte-identical text (settles, one alteration); a `reread` whose sides `compose` cleanly (settles, carrying the composed text and BOTH roles in `set_by`). Anything else carries forward NAMED and unresolved.

- [ ] **Step 5: Implement the resolutions, and run to green**

! **RESOLVE NOTHING EDITORIAL.** `Process: #42` says reconciliation *"emits escalations and resolves nothing"*; these three are MECHANICAL -- no judgement is exercised, and a case needing one is carried forward.

- [ ] **Step 6: Commit the work**

- [ ] **Step 7: Close P1 and P2, separately, citing Step 6's sha**

---

## Task 4: the `collate` command

**Delivers P3, and closes A-T1, A-T2, A-T3.**

**Files:**
- Create: `src/comment_review/commands/collate.py`
- Modify: `src/comment_review/__main__.py` (add `COLLATE` to `Command`)
- Create: `tests/test_collate_command.py`

**Interfaces:**
- Consumes: `flows.collate.collate`.
- Produces: `collate --stage <name> --copies <dir> --repo <root> --out <file>`.

- [ ] **Step 1: Write the failing tests -- the report AND the exit codes**

The command must name the escalated and re-read places on stdout (A-T2), and its exit code must separate the three outcomes (A-T3): all settled, something escalated, something owes a re-read.

- [ ] **Step 2: Run and watch them fail**

- [ ] **Step 3: Implement the command**

! **A COMMAND EXPOSES A FLOW AND HOLDS NO ORCHESTRATION** -- `Process: #12`. Parse arguments, call `flows.collate.collate`, print, return an exit code. See `tests/test_proof_command.py::test_the_command_holds_no_orchestration`.

- [ ] **Step 4: Run to green; run `build_plugin.py` and commit what it writes**

- [ ] **Step 5: Commit the work**

- [ ] **Step 6: Close P3, and close A-T1, A-T2, A-T3 on the TODO**

```
job-board todo close-task no-command-for-the-middle T1 \
  --statement "the collate command writes the docket the chain reads" --commit <sha>
```

---

## Task 5: `docket_from` transcribes, and the `docket` command

**Delivers P4 and P5.**

**Files:**
- Modify: `src/comment_review/desk/collator.py`
- Create: `src/comment_review/commands/docket.py`
- Modify: `tests/test_docket.py` (8 call sites)

**Interfaces:**
- Consumes: the chief's `edit_copy` from Task 3.
- Produces: `docket_from(chief_copy: dict) -> dict` -- ONE argument.

- [ ] **Step 1: Write the failing test**

```python
def test_docket_from_takes_the_chiefs_copy_alone():
    docket = docket_from(collate("stage-2", [copy_a, copy_b]))
    assert [p["path"] for p in docket["pages"]]
```

- [ ] **Step 2: Run and watch it fail**

- [ ] **Step 3: Change the signature and update all 8 call sites in `tests/test_docket.py`**

! **A TRAP MEASURED 2026-08-30:** `tests/conftest.py:148` defines an UNRELATED helper of the same name, used ~35 times across other test files. **Do not touch it.** Only the 8 sites calling `desk.collator.docket_from` change.

- [ ] **Step 4: Implement the `docket` command, and run to green**

! **IT TRANSCRIBES; IT DECIDES NOTHING.** Only `settled` entries become alterations.

- [ ] **Step 5: Commit the work**

- [ ] **Step 6: Close P4 and P5, separately, citing Step 5's sha**

---

## Task 6: the round tally, and the cap that terminates the only cycle

**Delivers P7, and closes `a-revise-answer-has-no-artifact` T8** -- unticked 2026-08-30 because it claimed a cap that no code implemented.

**Files:**
- Modify: `src/comment_review/flows/collate.py`
- Modify: `tests/test_collate.py`

- [ ] **Step 1: Write the failing tests**

A place that took one composition round and one conflict round is AT THE CAP; a third round cannot start; the run reports each place's rounds BY KIND rather than as one number.

- [ ] **Step 2: Run and watch them fail**

- [ ] **Step 3: Implement the tally on the chief's `edit_copy`, and the refusal at the cap**

!! **THIS TERMINATES THE SYSTEM'S ONLY CYCLE.** Drawn as a graph, the re-read loop is the one cycle in the design -- `reconcile -> rereads -> compose -> roles -> diff-marks -> collate -> reconcile`. Everything else is monotonic. `Process: #9` caps it at two rounds, and until this lands the loop is unbounded.

! **A place at the cap goes to the CHIEF**, which is where `recast` becomes reachable.

- [ ] **Step 4: Run to green**

- [ ] **Step 5: Commit the work**

- [ ] **Step 6: Close P7, and close `a-revise-answer-has-no-artifact` T8**

! If the tool refuses T8 with `no task T8 under '## Tasks'`, that is the paused board migration. **Leave it, and say so in your report** -- do not hand-edit the TODO.

---

## Task 7: the chief's three acts, including `recast`

**Delivers P14.** `decision-log.md Vocabulary: #29`.

**Files:**
- Create: `src/comment_review/desk/chief.py`
- Create: `tests/test_chief.py`

**Interfaces:**
- Produces: `taken_in`, `stet`, `recast` over one place of the chief's `edit_copy`.

- [ ] **Step 1: Write the failing tests -- one per act**

`recast` sets a place's text to prose NEITHER role proposed; the docket records the CHIEF in `set_by`; and it is reachable exactly when a compose refused or a place reached the cap.

- [ ] **Step 2: Run and watch them fail**

- [ ] **Step 3: Implement the three acts**

! **`recast` IS THE LAST RESORT, NOT THE MECHANISM.** Two `hold`s on disjoint spans compose arithmetically (Task 2). `recast` exists for the case Roy named: *"no clean composition, or genuine disagreement where neither side is right."*

- [ ] **Step 4: Run to green**

- [ ] **Step 5: Commit the work**

- [ ] **Step 6: Close P14, separately, citing Step 5's sha**

---

## Task 8: the diff-mark as its own artifact

**Delivers P6.** `decision-log.md Process: #22`.

**Files:**
- Create: `src/comment_review/desk/diff_mark.py`
- Create: `tests/test_diff_mark.py`

**Interfaces:**
- Produces: `Answer` (a `StrEnum`: `HOLD`, `WITHDRAW`, `CORRECT`, `PATCH`) and `parse(where, entry) -> (DiffMark | None, problems)`.

- [ ] **Step 1: Write the failing tests**

All four parse; a fifth is refused by name; **an entry with no answer is REFUSED, never read as an inferred `withdraw`**.

- [ ] **Step 2: Run and watch them fail**

- [ ] **Step 3: Implement it, following `desk/mark.py`'s parse -- one object or named problems, no third outcome**

!! **IT IS NOT A `Mark` AND NOT AN EIGHTH INSTRUCTION.** `#22`: *"a diff-mark is a DIFFERENT ARTIFACT answering a different question ... The seven stay seven."*

! **THE ANTI-DECISION DECISION IS THE POINT.** Roy: *"Inferring the decision from lack of decision means that the agents get to do the human failure of the anti-decision decision."* An unanswered place must be written by a hand.

- [ ] **Step 4: Run to green**

- [ ] **Step 5: Commit the work**

- [ ] **Step 6: Close P6, separately, citing Step 5's sha**

---

## Task 9: the `diff3` on the payload, its render tool, and the gate

**Delivers P12, P18 and P19.**

**Files:**
- Modify: `src/comment_review/desk/diff_mark.py`
- Create: `tests/gates/test_diff3_is_never_parsed.py`

- [ ] **Step 1: Write the failing tests**

A revise row for a place two roles edited carries the render; a role that edited nothing there still receives it; and the render is the one `results.differences.diff3` already produces rather than a second one.

- [ ] **Step 2: Write the gate (P19)**

No module under `src/comment_review/` defines or imports a parser for the render. The gate fails if one appears.

!! **THIS IS WHAT KEEPS THE PROTOTYPE'S FIRST FAILURE AWAY.** Roy, 2026-08-30, on why the old system needed a rewrite: *"The shape passing was structured text that was not parsable and often times had parsing errors because code contains those symbols that were being used to divide the fields."* A conflict marker is a string a comment may legitimately contain. **The payload is READ. It is never PARSED.** Production holds that today only by habit; this makes it a gate.

- [ ] **Step 3: Run and watch them fail**

- [ ] **Step 4: Implement the render onto the row, and run to green**

- [ ] **Step 5: Commit the work**

- [ ] **Step 6: Close P12, P18 and P19, separately, citing Step 5's sha**

---

## Task 10: the revise round

**Delivers P8.** ! **BLOCKED until P20 is ruled** -- what `reads: revise:N` means when stage N settled nothing. Ask, do not guess.

**Files:**
- Modify: `src/comment_review/flows/collate.py`
- Create: `tests/test_revise_round.py`

- [ ] **Step 1: Write the failing tests**

Party-to is the union of three routes -- disagreed on a sentence, co-edited the paragraph, or holds a page that took an `add`. A role receives a row only in the shard holding that file.

- [ ] **Step 2: Run and watch them fail**

- [ ] **Step 3: Implement the round: resend to the parties, collect diff-marks, collate again**

! **THE SAME FLOW, A DIFFERENT INPUT.** Round one carries marks; round two carries diff-marks. The flow must know which it holds.

- [ ] **Step 4: Run to green**

- [ ] **Step 5: Commit the work**

- [ ] **Step 6: Close P8**

! Section B's `T4`, `T5` and `T7` cannot be closed through the tool -- the id format blocks it. **Report that; do not hand-edit.**

---

## Task 11: the sequencing command

**Delivers P9, and closes A-T5.**

**Files:**
- Create: `src/comment_review/commands/run.py`
- Create: `tests/test_run_command.py`

- [ ] **Step 1: Write the failing test**

One invocation runs stage 1, pulls revise-1, runs stage 2 against that revise, and STOPS.

- [ ] **Step 2: Run and watch it fail**

- [ ] **Step 3: Implement it over `desk.topology.read`**

! The topology already expresses the order and `fan_out` already partitions. **This drives them; it decides nothing.**

- [ ] **Step 4: Run to green**

- [ ] **Step 5: Commit the work**

- [ ] **Step 6: Close P9 and A-T5**

---

## Task 12: the gates see the new commands

**Delivers P10, and closes A-T4.**

**Files:**
- Modify: `plugins/comment-review/skills/comment-review/SKILL.md`
- Modify: `tests/gates/test_skill_commands.py`

- [ ] **Step 1: Run the gate and watch it miss them**

- [ ] **Step 2: Name the new commands in `SKILL.md`, and widen the gate to cover them**

! **`SKILL.md` is the `agents` lane, and this is a MECHANICAL one-for-one addition** -- naming a command that exists. Do not reword what a stage DOES.

- [ ] **Step 3: Run every gate**

`uv run pytest -q`, `ruff check .`, `ty check src/comment_review/`, `build_plugin.py --check`, `check_shipped_syntax.py`, `check_vocabulary.py`

- [ ] **Step 4: Commit the work**

- [ ] **Step 5: Close P10 and A-T4**

---

## Task 13: the record

**Delivers P11.**

**Files:**
- Modify: `docs/decision-log.md`, `docs/vocabulary.md`, `plugins/comment-review/skills/comment-review/references/vocabulary.toml`

- [ ] **Step 1: Add every ruling this plan produced to `docs/decision-log.md`**

Including P20's answer, and the chief's three-act set (`Vocabulary: #29` records `recast`; nothing yet records that the chief's set is THREE against the role's four).

- [ ] **Step 2: Add `recast` and `stet` to `vocabulary.toml`, so the gate can see them**

Measured 2026-08-30: `recast` is enforceable nowhere -- absent from the toml, absent from `check_vocabulary.py`. `taken_in` is the only one of the three with any code.

- [ ] **Step 3: Run `check_vocabulary.py` and the suite**

- [ ] **Step 4: Commit the work**

- [ ] **Step 5: Close P11, and run `job-board --plans-dir docs/plans` to confirm the plan reports closed**
