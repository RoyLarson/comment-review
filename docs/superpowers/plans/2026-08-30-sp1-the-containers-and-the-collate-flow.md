# SP-1: The containers and the collate flow -- Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Carry one stage's filled `edit_copies` forward to the copy chief's `edit_copy` and a console report, with every container typed and every mechanical resolution taken -- a clean forward run that stops at the first place needing a person.

**Architecture:** The mark gains the base text it is diffed against, so nothing downstream has to be handed it separately. The four containers get a type with a validating boundary, following `docket.Schedule`: `read` refuses, the typed view derives. `compose` is added beside `diff3` -- the merge that acts on disjointness where `diff3` only renders it. Those three are what `flows/collate.py` then composes into one flow: `gather -> places -> reconcile -> resolve`, out to the chief's copy, with a report naming whatever did not resolve.

**Tech Stack:** Python 3.11 (floor), standard library only under `src/comment_review/`, `pytest`, `ruff`, `ty`.

**Plan:** [`docs/plans/0.2.4-the-commands-for-the-middle.md`](../../plans/0.2.4-the-commands-for-the-middle.md). This SP delivers **P34, P21, P13, P1, P2, P22, P3**, which name the `T` tasks they close. **The arrows go one way: `SP -> P -> T`.**

**Supersedes:** [`2026-08-30-the-commands-for-the-middle.md`](2026-08-30-the-commands-for-the-middle.md), the 13-task monolith. See *What is obsolete in the monolith*, below, before copying anything out of it.

---

## Global Constraints

- **Everything through `uv run`.** Python **3.11** is the floor.
- **Standard library only** under `src/comment_review/`. No third-party import in a shipped file.
- **No tuple literal in an `except`** -- bind it to a name (`READ_ERRORS`, `PARSE_ERRORS`).
- **ASCII prose, `--` for an em-dash.** No subjective claims -- nothing that cannot be falsified by reading the code or re-running a command.
- **`clean` is one of the seven instructions, never a loose adjective.**
- **The ruling field is `instruction`, never `verdict`.** `block`/`blocks` is retired for `paragraph`.
- **NO heredocs, NO `sed`** -- a `PreToolUse` hook refuses them outright. Use `Write`/`Edit`, or `Write` a `.py` script and `uv run python` it. Commit messages: `Write` a file, then `git commit -F <file>`.
- **`plugins/` is BUILT from `src/`** -- `uv run python scripts/build_plugin.py`, and commit what it writes.
- **No test takes its expectation from the code under test**, and no fixture is hand-authored in the shape the code expects. Build inputs from `page_for`, `bind` and `seed` over a real tree.
- **Correct code and green tests in ONE commit** (Roy, 2026-08-29).

### The vocabulary this plan uses

Four containers, `decision-log.md Vocabulary: #28`. Nesting, outermost first:

| term | what it is |
| --- | --- |
| `master_proof` | every role's `edit_copy` for ONE stage, as `desk.proof.gather` returns it |
| `edit_copy` | ONE role's work -- `{role, read_from, sheets}` |
| `sheet` | ONE page within an edit_copy -- `{path, sha, marks}` |
| `mark` | ONE role's ruling on ONE place |
| `binder` | the censused pages a stage reads FROM, carrying `read_from` |
| `docket` | the settled changes, packaged for the write chain |
| **the fold** | `Vocabulary: #30` -- N `edit_copies` become ONE, same shape, `role: copy-chief` |

! **A seeded SLOT is not a mark.** `desk.mark.untouched()` tells them apart, and conflating the two is what made the reviewer brief's own worked example pass as unruled on 2026-08-29.

### How every task ends: two commits, never one

!! **A `P` closes in a LATER commit than the work, because a commit cannot cite its own hash.**

1. **Commit the work.** Green. No box moves.
2. **Commit the closes, separately**, citing the work's sha:

```
job-board plan close 0.2.4-the-commands-for-the-middle P<n> \
  --statement "<how it closed>" --commit <sha> \
  --plans-dir docs/plans --todo-dir TODO
```

! **NEVER hand-edit the plan file.** The tool sets the mark, recomputes `Plan-tasks:` and re-derives `Requires-Roy`. Hand-editing was measured on 2026-08-30 to produce the right bytes while missing three dead `T` references the tool reports on every write.

! **`job-board plan close` prints `unresolved: BT4 / BT5 / BT7` on every invocation.** That is section B's known state -- `a-revise-answer-has-no-artifact` writes its ids as `T4 --` where the tool reads `T4 |`. It is not caused by your change. **Do not "fix" it by hand-editing that TODO**; the board migration is paused deliberately (`TODO/board-predates-task-ids.md`).

!! **AND THE `A-T` TASKS CANNOT BE CLOSED BY THE TOOL YET.** MEASURED 2026-08-30: `TODO/no-command-for-the-middle.md` carries its five tasks as bare `- [ ]` lines with **no id column** -- the plan transcribes them as `A-T1`..`A-T5`, but on disk there is no `T1` for `close-task` to address. Closing them waits on the same paused migration. **Close the `P` steps; say in the close statement which `A-T` the work satisfies, and leave the TODO alone.**

---

## What is obsolete in the monolith

The superseded plan's Tasks 1-4 cover this same ground, and were reconciled against the `P` plan in `41b0ba0`. **Four things in it are now wrong.** They are listed so the correct parts can be reused without the rest coming with them.

| in the monolith | why it is obsolete |
| --- | --- |
| Task 3's `assert states <= {"settled","escalated","reread"}`, reading `m["state"]` off a chief's mark | **It contradicts its own Task 1**, which struck a `state` field on the grounds that the intermediate already has a type (`Reconciled`). MEASURED: `"state"` appears nowhere in `src/`. Resolved in Task 5 below -- the chief's copy holds the FOLD, and what did not fold rides beside it. |
| Task 1's `Sheet`/`EditCopy` as `NamedTuple` | **P21 says frozen dataclasses**, *"the way `desk/mark.py` defines `Mark`"*. The monolith drifted to `NamedTuple` from the `Schedule` comparison. |
| Task 1's `rounds` in the type, verified against *"what `seed` builds"* | **`rounds` appears nowhere in `src/`, and `seed` does not build it** -- so that verify contradicts itself. Task 3 below declares it optional on the envelope and leaves SP-5 to fill it. |
| Task 4's `job-board todo close-task no-command-for-the-middle T1` | **Unrunnable** -- that TODO has no id column. See above. |

! **What IS reusable:** the `Schedule` comparison table, the 54-raw-reads measurement and its gate, the `compose`/`diff3` distinction, and `Process: #12` -- a command exposes a flow and holds no orchestration. Those are carried into the tasks below rather than cited across.

---

## File structure

| file | responsibility |
| --- | --- |
| `docs/the-mark.md` | **the source.** The field table grows to eight; `raw_text` moves into it |
| `src/comment_review/desk/mark.py` | `Mark` gains `raw_text`; `parse` carries it through |
| `src/comment_review/desk/containers.py` | **new.** `Sheet`, `EditCopy`, `MasterProof`, a validating `read`, deriving views |
| `src/comment_review/results/differences.py` | gains `compose(base, sides)` and `OverlappingEdits` |
| `src/comment_review/flows/collate.py` | **new.** gather -> reconcile -> resolve, out to the chief's `edit_copy` |
| `src/comment_review/results/report.py` | **new.** the continuation report every middle command ends with |
| `src/comment_review/commands/collate.py` | **new.** the `collate` command |
| `tests/gates/test_mark_shape.py` | **new.** the field table and the dataclass move together |
| `tests/gates/test_containers_are_not_read_raw.py` | **new.** the type is gone through, not around |

**Order is a dependency chain, not a preference.** Task 1 changes what a mark carries, which Task 2's type describes and Task 5's resolutions read. Task 3 is independent of 1 and 2 and could run first; it is placed third because Task 5 consumes it.

---

## Task 1: The mark carries the text it is diffed against

**Delivers P34.**

!! **THE PLAN'S WORDING FOR THIS STEP IS HALF-SATISFIED ALREADY, AND THE OTHER HALF IS THE WORK.** P34 asks that `seed` write `raw_text` onto every slot *"as it does today"* -- and MEASURED 2026-08-30, `flows/marks.py:87` already does, and `docs/the-mark.md:53` already says the seeded row carries it. **What drops it is `parse`.** `Mark` has seven fields, `raw_text` is not among them, and `mark.py:520-522` says so deliberately: *"Keys the spec does not name (`raw_text`, seeded onto the row) are carried by the entry and are not part of the `Mark`."*

! **So this task promotes a field that already travels, and deletes the paragraph that argued it should not.** `mark.py:262-266` currently reads *"NOTHING IS ADDED HERE THAT THE SPEC DOES NOT NAME. `raw_text` is the SEEDED ROW's, not the mark's"*. After this task that sentence is false, and a false comment beside the field it describes is the exact defect this repo's reviewers exist to catch.

!! **WHY IT MOVES, IN ROY'S TERMS.** Roy, 2026-08-30: *"I think the base text needs to be carried by the Mark and seeded at this point."* Reconciliation currently decides what composes without ever holding the paragraph it composes into -- `raw_text` is threaded as a loose argument into `collator.claim_verbatim_problems` (`collator.py:320-328`) and dropped after. `compose` in Task 4 needs a base, and `Placed` is `(mark, role)`.

! **FLAT, NOT NESTED.** Roy raised nesting as a risk -- *"it is hard enough getting the line breaks and other pieces through the shell"*. These containers travel as JSON files (`commands/mark.py` dumps and loads them), not as shell arguments, so the serialiser handles line breaks. The exposure is an AGENT AUTHORING THE SHAPE, and there a third seeded scalar is flatter than either alternative: **no `Placed(mark, role, raw_text)`, and no `Mark` holding a `Placed`.**

**Files:**
- Modify: `docs/the-mark.md` -- the field table, and the pair of rows below it
- Modify: `src/comment_review/desk/mark.py` -- the `Mark` dataclass, its docstring, `parse`'s `Args` and its construction
- Create: `tests/gates/test_mark_shape.py`
- Modify: `tests/test_mark.py`

**Interfaces:**
- Consumes: `flows.marks.seed`, which already writes `raw_text` onto every slot.
- Produces: `Mark.raw_text: str`, seeded, empty where the row carried none.

```python
@dataclass(frozen=True)
class Mark:
    address: str
    anchor: str
    raw_text: str      # NEW -- seeded, beside address and anchor
    instruction: Instruction
    claim: dict
    reason: str
    sources: tuple[object, ...]
    change: str
```

! **IT GOES THIRD, WITH THE OTHER SEEDED FIELDS, NOT LAST.** The field order is the chain of custody -- *"the two seeded fields that say WHERE in front of them"*. `raw_text` is seeded, so it belongs in front with them; appending it after `change` would put a seeded field at the end of the role's own chain.

- [ ] **Step 1: Write the failing gate -- the table and the dataclass move together**

```python
def test_every_field_in_the_mark_table_is_a_field_of_Mark():
    """The source is docs/the-mark.md. The dataclass may not drift from it."""
    named = _fields_named_in(Path("docs/the-mark.md"))
    assert named == [f.name for f in dataclasses.fields(Mark)]
```

`_fields_named_in` reads the rows of the `## The fields` table and returns the backticked name in column one, in order. **Read the table, do not restate it** -- a gate holding its own copy of the list agrees with itself.

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/gates/test_mark_shape.py -q`
Expected: FAIL -- the table names seven, the dataclass has seven, and `raw_text` is in neither. **It must fail for the RIGHT reason**: confirm the failure message names the missing field, not a parse error in `_fields_named_in`.

- [ ] **Step 3: Update `docs/the-mark.md`**

Change the heading to `## The fields -- eight`, and insert after the `anchor` row:

```
| `raw_text` | the paragraph as it stands, verbatim -- what `change` is diffed against | seeded |
```

Then rewrite the two-row table below it (`the seeded row carries` / `the role returns`) so it reads as a contrast between two FIELDS of one mark rather than between a row and a return. **Keep the four paragraphs under it unchanged** -- the diff-directly reason, the measured hole, and the supersession of the line-array form all still hold, and are the evidence for this field existing at all.

- [ ] **Step 4: Add the field to `Mark`, and run the gate to green**

Add `raw_text: str` third, and an `Attributes:` entry for it. **Delete the `! NOTHING IS ADDED HERE...` paragraph's first two sentences** -- the `role` sentence stays, because `role` really does still belong to the `edit_copy` and `Placed` really is what carries the pair.

- [ ] **Step 5: Carry it through `parse`, with a test that fails first**

```python
def test_parse_carries_the_seeded_raw_text_onto_the_Mark():
    row = _one_seeded_slot_over_a_real_tree(tmp_path)   # from seed(), not a literal
    ruled = {**row, "instruction": "correct", "reason": "...", "claim": {...}, "change": "..."}
    mark, why = parse("m.py@b1", ruled)
    assert why == []
    assert mark.raw_text == row["raw_text"]
```

Then in `parse`'s construction add `raw_text=str(entry.get("raw_text") or "")`, and update its `Args:` -- the sentence naming `raw_text` as a key the spec does not name is now wrong.

- [ ] **Step 6: Prove the empty case, and that it is not owed**

`raw_text` is **seeded, not owed** -- `parse` must not grow a rule requiring it. A `clean` carries no address and no raw_text and must still parse. Assert both: a slot whose row had no `raw_text` gives `mark.raw_text == ""`, and `parse` reports no problem for it.

- [ ] **Step 7: Run every gate**

`uv run pytest -q`, `uv run ruff check .`, `uv run ty check src/comment_review/`, `uv run python scripts/build_plugin.py --check`, `uv run python scripts/check_shipped_syntax.py`, `uv run python scripts/check_vocabulary.py`

- [ ] **Step 8: Commit the work** -- `build_plugin.py` first, and commit what it writes

- [ ] **Step 9: Close P34, separately, citing Step 8's sha**

---

## Task 2: Give the containers a type

**Delivers P21.**

!! **THE CONTAINERS ARE ONE SHAPE, AND THE CHIEF'S IS NOT SPECIAL** -- `Vocabulary: #30`. The chief step is a FOLD: a `master_proof` holding N `edit_copies` becomes ONE `edit_copy` whose `role` is `copy-chief`. It is the RESULT, so every place it holds carries exactly one mark -- which is what an ordinary `edit_copy` already is. **No second type.**

!! **FOLLOW `docket.Schedule`, NOT A DATACLASS-ON-THE-WIRE.** Both structures at either end of the middle settled this, and they agree:

| | on the wire | validator | typed view |
| --- | --- | --- | --- |
| `binder` | `dict` | `read(text) -> (dict, str)` | `rows_of` -- **dicts again, no type** |
| `docket` | `dict` | `read(text) -> (dict, str)` | `schedules_of -> list[Schedule]` |

! **AN `edit_copy` IS JSON ON DISK** -- `commands/mark.py` dumps it and loads it -- so a frozen dataclass on the wire would break `mark --seed` or force `asdict()` at every boundary. **`read` validates; the view derives, and refuses nothing.** `docket.py:190` states that division: *"There is nothing here that can fail: `read` has already ruled on the shape."*

!! **THE DELIVERABLE IS THE BOUNDARY BEING PARSED, NOT THE TYPE EXISTING.** MEASURED 2026-08-30: **54 sites across 9 modules** index these containers by raw string key. **A type nothing reads is decoration, and that is exactly the Mark failure** -- `Instruction` existed as an enum, the wire held a bare string, the two never met, and `flows/marks.py` dropped filled entries as coverage gaps. **This task is done when the readers go through the type and a gate keeps them there.**

**Files:**
- Create: `src/comment_review/desk/containers.py`
- Create: `tests/test_containers.py`
- Create: `tests/gates/test_containers_are_not_read_raw.py`
- Modify: `src/comment_review/desk/proof.py`, `src/comment_review/desk/collator.py`, `src/comment_review/flows/fan_out.py`, `src/comment_review/flows/marks.py` -- the READING sites

**Interfaces:**
- Consumes: the shape as built today -- `flows/marks.py:71-95` (`seed`) and `desk/mark.py:318` (`allowed`).
- Produces:

```python
@dataclass(frozen=True)
class Sheet:
    path: str
    sha: str
    marks: list[dict]          # a slot or a filled mark -- untouched() tells them apart

@dataclass(frozen=True)
class EditCopy:
    role: str
    read_from: dict
    sheets: list[Sheet]
    rounds: dict = field(default_factory=dict)     # PROVISIONAL -- see below

@dataclass(frozen=True)
class MasterProof:
    stage: str
    edit_copies: list[EditCopy]

def read(text: str) -> tuple[dict, str]: ...       # validates, as binder/docket do
def sheets_of(edit_copy: dict) -> list[Sheet]: ...  # derives; refuses nothing
def copies_of(master_proof: dict) -> list[EditCopy]: ...
```

! **FROZEN DATACLASSES, per P21 -- *"the way `desk/mark.py` defines `Mark`"***. The superseded monolith wrote `NamedTuple`; that was a drift out of the `Schedule` comparison above, and the plan step is what governs.

! **`marks` IS `list[dict]`, AND THAT IS NOT LAZINESS.** A seeded entry is a SLOT, not a `Mark` -- `desk/mark.py:471`'s `untouched()` exists because conflating the two is what made the brief's own worked example pass as unruled. Typing it `list[Mark]` erases the distinction that bug cost us.

!! **`rounds` IS PROVISIONAL AND NOTHING FILLS IT IN THIS SP.** P21 asks that the round tally ride the envelope *"so the mark's ... fields stay"* at their count -- and that is the part this task delivers: the tally has a declared home that is **not** a mark field. **MEASURED 2026-08-30: `rounds` appears nowhere in `src/`, and `seed` does not build it**, so a test verifying the type against what `seed` builds cannot verify this key. It is declared with a default, marked provisional in the code, and **SP-5 is what writes and reads it** -- that is where the revise round lives. Per `docs/conventions.md`: *"Where a design deliberately reaches into territory that will later belong somewhere else, mark it provisional in the code AND in the records."*

- [ ] **Step 1: Write the failing test -- the view over what `seed` actually BUILDS**

```python
def test_sheets_of_derives_a_view_over_what_seed_BUILDS(tmp_path):
    built = seed(binder_of(a_small_real_tree(tmp_path)), "block-context")
    sheets = sheets_of(built)
    assert sheets and sheets[0].path and sheets[0].sha
    assert isinstance(sheets[0].marks, list)
    assert built["sheets"][0]["marks"][0]["raw_text"] == sheets[0].marks[0]["raw_text"]
```

! **THE EXPECTATION COMES FROM `seed` OVER A REAL TREE, NOT A LITERAL.** A hand-written `edit_copy` would confirm the view against itself -- which is the mechanism that made the retired suite unable to notice three real breaks in one day.

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/test_containers.py -q`
Expected: FAIL -- `desk.containers` does not exist.

- [ ] **Step 3: Write `desk/containers.py` -- `read` validating, the views deriving**

`read` refuses: a non-object, a missing or blank `role`, a missing `read_from`, `sheets` that is not a list, a sheet that is not an object, a sheet with no `path`. It returns `(data, "")` or `({}, "one message")`, matching `binder.read` and `docket.read`. **The views refuse nothing.**

- [ ] **Step 4: Write the failing test for the chief's copy -- same shape, no second type**

```python
def test_the_chiefs_copy_is_an_ordinary_edit_copy(tmp_path):
    folded = {**seed(binder_of(a_small_real_tree(tmp_path)), "copy-chief")}
    loaded, err = read(json.dumps(folded))
    assert err == ""
    assert copies_of({"stage": "s1", "edit_copies": [loaded]})[0].role == "copy-chief"
```

- [ ] **Step 5: Write the gate, and prove it can fail**

`tests/gates/test_containers_are_not_read_raw.py` -- no module outside `desk/containers.py` indexes `sheets`, `edit_copies` or `rounds` off a dict by string key. **Run it now, before Step 6, and watch it FAIL against the 54 existing sites.** A gate first run after the cleanup cannot tell you it bites.

! **WITHOUT THIS THE TASK DECAYS.** The next session adds one raw read and nothing notices, which is how 54 of them accumulated.

- [ ] **Step 6: Convert the READING sites to the views, and run the gate to green**

`desk/proof.gather`, `desk/collator.places`, `flows/fan_out.fan`, `flows/marks.problems_in`. **Leave `binder.py` and `docket.py` alone** -- those keys are their own containers'.

- [ ] **Step 7: Run every gate** (the six from Task 1, Step 7)

- [ ] **Step 8: Commit the work**

- [ ] **Step 9: Close P21, separately, citing Step 8's sha**

---

## Task 3: `compose` -- the merge that `diff3` is not

**Delivers P13.** This is what answers *"how do both get taken in"* without a fifth answer.

!! **`hold` ALREADY SAYS IT.** Roy asked *"how do the agents get to say both are true and should be taken_in"*. A `hold` says *my mark stands*, so two holds on disjoint spans are both saying it -- and the composition is then **arithmetic**, not a new editorial answer.

! **`diff3` DOES NOT DO THIS, and must not be changed to.** It RENDERS -- every span at least one side edited, wrapped in a conflict span, **even where only one side touched it**. That is correct for a reader. `compose` is the half that ACTS on the disjointness the render only shows.

**Files:**
- Modify: `src/comment_review/results/differences.py`
- Modify: `tests/test_differences.py`

**Interfaces:**
- Consumes: `SequenceMatcher` opcodes, as `diff3` and `_side_slice` already use (`differences.py:55-190`).
- Produces: `compose(base: str, sides: dict[str, str]) -> str`, and `OverlappingEdits(Exception)`.

- [ ] **Step 1: Write the failing tests -- both directions**

```python
def test_two_edits_on_different_sentences_merge_to_a_paragraph_carrying_both():
    base = "# one.\n# two.\n# three.\n"
    out = compose(base, {"block-context": "# ONE.\n# two.\n# three.\n",
                         "function-context": "# one.\n# two.\n# THREE.\n"})
    assert out == "# ONE.\n# two.\n# THREE.\n"

def test_two_edits_on_the_SAME_span_refuse_by_name():
    base = "# one.\n"
    with pytest.raises(OverlappingEdits) as raised:
        compose(base, {"block-context": "# A.\n", "function-context": "# B.\n"})
    assert "block-context" in str(raised.value) and "function-context" in str(raised.value)
```

! **The second test is the one that matters.** A compose that picks a side is worse than one that refuses, because it settles an editorial question with arithmetic. **The message must name both roles**, since that is what the escalation downstream reports.

- [ ] **Step 2: Run and watch both fail** -- `compose` is not defined

- [ ] **Step 3: Implement `compose`**

For each side, take the opcodes against the base and record the base spans it touches. If two sides touch the same span, raise `OverlappingEdits` naming the place and both roles. Otherwise apply each side's replacement to its own span and return the result.

- [ ] **Step 4: Cover the three degenerate cases**

One side (returns that side); zero sides (returns the base unchanged); a side byte-identical to the base (touches no span, so it cannot conflict with anything). **These are what Task 5's resolutions call into**, so they are this task's to prove, not that one's.

- [ ] **Step 5: Run to green, then the whole suite**

- [ ] **Step 6: Commit the work**

- [ ] **Step 7: Close P13, separately, citing Step 6's sha**

---

## Task 4: `flows/collate.py` -- one flow, gather to the chief's copy

**Delivers P1 and P2.** Roy: *"I think collate resolve is one flow."*

!! **WHAT DID NOT FOLD RIDES BESIDE THE COPY, NOT INSIDE IT.** The superseded monolith struck a `state` field in one task and then read `m["state"]` in the next. It is struck, and here is the reason it stays struck: **`untouched()` already means "nobody wrote here"**, so writing an unresolved place back as a slot would give one shape two meanings -- the exact conflation `untouched` exists to prevent. A place that escalated has no single mark, so it cannot be a mark in a folded copy at all.

! **So the flow returns both halves**, and the chief's copy stays an ordinary `edit_copy`:

```python
@dataclass(frozen=True)
class Collated:
    chief: dict          # the fold -- an edit_copy, role "copy-chief"
    reconciled: Reconciled    # what settled, what escalated, what owes a re-read
```

! **`Reconciled` IS ALREADY THE TYPE FOR THE INTERMEDIATE** (`collator.py:440`), which is why no new one is invented for it.

**Files:**
- Create: `src/comment_review/flows/collate.py`
- Create: `tests/test_collate.py`

**Interfaces:**
- Consumes: `desk.proof.gather(stage, edit_copies) -> dict`; `desk.collator.reconcile(proof) -> Reconciled`; `results.differences.compose` from Task 3; `desk.containers` from Task 2.
- Produces: `collate(stage: str, edit_copies: list[dict]) -> Collated`.

- [ ] **Step 1: Write the failing test -- the fold**

```python
def test_collate_folds_N_edit_copies_into_ONE_carrying_the_settled_places(tmp_path):
    copies = _two_roles_ruling_on_one_tree(tmp_path)   # built from seed(), then filled
    out = collate("stage-1", copies)
    assert out.chief["role"] == "copy-chief"
    assert read(json.dumps(out.chief))[1] == ""        # an ordinary edit_copy
    settled = {e["address"] for e in out.reconciled.settled}
    folded = {m["address"] for s in out.chief["sheets"] for m in s["marks"]
              if not untouched(m)}
    assert folded == settled
```

- [ ] **Step 2: Run and watch it fail**

- [ ] **Step 3: Implement the flow** -- `gather` -> `reconcile` -> fold the settled into the chief's copy

- [ ] **Step 4: Write the failing tests for the automatic resolutions (P2)**

**Three cases, and only three.** Each settles; anything else is carried forward NAMED.

| case | what the chief's copy gets |
| --- | --- |
| ONE owing mark at the place | that mark |
| every owing mark proposes **byte-identical** `change` | that text, once |
| a re-read whose sides `compose` cleanly against `mark.raw_text` | the composed text, carrying BOTH roles |

! **THE THIRD IS WHY TASK 1 CAME FIRST.** `compose` needs the base, and the base is `mark.raw_text` -- read off the mark, not threaded in.

- [ ] **Step 5: Write the failing test for what must NOT resolve**

Two marks on the same sentence stay an escalation. Two marks whose spans overlap stay a re-read -- `compose` raises `OverlappingEdits` and the flow **catches it and carries the place forward**, rather than letting it escape.

! **RESOLVE NOTHING EDITORIAL.** `Process: #42`: reconciliation *"emits escalations and resolves nothing"*. These three are MECHANICAL -- no judgement is exercised -- and a case needing one is carried forward.

- [ ] **Step 6: Implement the resolutions, and run to green**

- [ ] **Step 7: Run every gate**

- [ ] **Step 8: Commit the work**

- [ ] **Step 9: Close P1 and P2, separately, citing Step 8's sha**

---

## Task 5: The `collate` command, and the report every middle command owes

**Delivers P22 and P3.** Satisfies `A-T1`, `A-T2` and `A-T3` -- **name them in the close statement; do not run `close-task`** (see *How every task ends*).

!! **P22 IS A RULE FOR EVERY COMMAND IN THE MIDDLE, AND THIS IS THE FIRST ONE.** `Process: #51` -- **a command that leaves work undone names the work AND the command that continues it.** Roy, 2026-08-30: *"Just because we can put it in the flow doesn't mean the agents get notified that they should do more work or that there is something for them to do."*

! **AN AGENT LEARNS THERE IS WORK FROM THE RUN**, not from `--help` and not from a rule it is expected to remember. **THE COUNTER-EXAMPLE IS ALREADY SHIPPING:** `commands/mark.py:106` prints `"12 ruled on, 0 left unruled"` -- a count naming neither the places left nor the next invocation.

! **THE REPORT IS A SHARED SHAPE, SO IT IS ITS OWN MODULE.** SP-4, SP-5 and SP-6 each add a middle command that owes the same thing. Building it inside `commands/collate.py` would make the second one copy it.

**Files:**
- Create: `src/comment_review/results/report.py`
- Create: `src/comment_review/commands/collate.py`
- Modify: `src/comment_review/__main__.py` -- add `COLLATE` to `Command`
- Create: `tests/test_report.py`, `tests/test_collate_command.py`

**Interfaces:**
- Consumes: `flows.collate.collate`.
- Produces: `continuation(done: int, of: int, outstanding: dict[str, list[str]], next_command: str | None) -> str`, and `collate --stage <name> --copies <dir> --repo <root> --out <file>`.

- [ ] **Step 1: Write the failing tests for the REPORT, alone**

```python
def test_a_run_that_leaves_work_names_the_places_AND_the_next_command():
    out = continuation(done=4, of=10, outstanding={"escalated": ["m.py@b1", "m.py@b7"]},
                       next_command="comment-review collate --stage stage-2 ...")
    assert "m.py@b1" in out and "m.py@b7" in out       # the PLACES, not just a count
    assert "comment-review collate" in out

def test_a_run_that_settles_EVERYTHING_names_nothing_to_continue():
    out = continuation(done=10, of=10, outstanding={}, next_command=None)
    assert "comment-review" not in out
```

! **The first assertion is P22's whole point** -- *"no command reports only a count the way `mark --check` does today"*.

- [ ] **Step 2: Run and watch both fail**

- [ ] **Step 3: Implement `results/report.py`**

- [ ] **Step 4: Write the failing tests for the command -- output AND exit codes**

The exit code must separate the three outcomes (`A-T3`), since the task agent branches on it: everything settled, something escalated, something owes a re-read. **Assert three distinct non-negative codes**, and assert the report reaches stdout.

- [ ] **Step 5: Implement the command**

! **A COMMAND EXPOSES A FLOW AND HOLDS NO ORCHESTRATION** -- `Process: #12`. Parse arguments, call `flows.collate.collate`, print, return an exit code. See `tests/test_proof_command.py::test_the_command_holds_no_orchestration`.

- [ ] **Step 6: Prove the chain runs with no Python written by hand (`A-T1`)**

Drive `census -> mark --seed -> mark --check -> collate -> proof` over a real scratch tree, as commands. **This is the SP's acceptance test**, and it is the one that would notice an argument name that only makes sense from inside the flow.

- [ ] **Step 7: Add the command to `COMMANDS` and `--help`; run `tests/gates/test_skill_commands.py`**

! `A-T4` asks that the gate cover it. That gate is `systems`-owned; **the command appearing in `COMMANDS` is this task's, and the gate should then pass without being edited.** If it does not, fix the command -- **a lane that trips a gate fixes its own code.**

- [ ] **Step 8: Run every gate; `build_plugin.py` and commit what it writes**

- [ ] **Step 9: Commit the work**

- [ ] **Step 10: Close P22 and P3, separately, citing Step 9's sha**

State in P3's close statement which of `A-T1`, `A-T2`, `A-T3` the work satisfies, since the TODO cannot be ticked until the id migration lands.

---

## Where SP-1 stops

**At the first place that needs a person.** The flow runs binder -> seeded copies -> filled marks -> gather -> reconcile -> the three mechanical resolutions -> the chief's copy, and reports what is left. What it does **not** do, by design:

| left open | lands in |
| --- | --- |
| the docket transcribed from the chief's copy, and `recast` | SP-4 (`P4`, `P5`, `P14`, `P23`) |
| the diff-mark, the revise round, and `rounds` being filled | SP-5 (`P6`, `P8`, `P12`, `P18`, `P19`) |
| the topology configuration system | SP-3 (`P29`-`P33`) |
| sequencing the stages, the gates, the record | SP-6 (`P9`, `P10`, `P11`) |

! **An escalation still needs a copy chief, and the copy chief is `0.2.5`.** Roy: *"the copy-chief role is not in 0.2.4 it will be in 0.2.5. In 0.2.4 it will be handled by the task agent."* SP-1 produces the artifact that role will act on, and the report that tells the task agent it must.
