# The mark, and the revise -- Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the mark gate agree with the brief a role actually reads, then stage the flow so a
later role reads a REVISE carrying what earlier stages settled -- and can see what changed.

**Architecture:** `desk/mark.py` states every key a claim owes in ONE row and the gate reads that
row. A stage list says which roles run when and whether a stage is `editorial` (pulls a revise) or
`enriching` (feeds the next binder). Each editorial boundary runs the existing
`flows/proof_setter.run` into a tree copy, proves the executable code unchanged, and asserts the
address space did not move. `taken_in` shows a role the original against the revise in its hand.

**Tech Stack:** Python 3.11 floor, standard library only in shipped files, `pytest` + `ruff` + `ty`
as pinned dev dependencies, all through `uv run`.

**Spec:** [`docs/plans/0.2.4-the-mark-and-the-collator.md`](../../plans/0.2.4-the-mark-and-the-collator.md)
-- the `P` plan. This `SP` delivers **P1**, **P2**, and **P5.2**.

**Why P5.2 is here and the rest of P5 is not:** `taken_in` (P2.6) cannot print a diff without the
renderer P5.2 builds, so the dependency is hard. P3, P4, P5.1, P5.3 and P6 get their own SP once
P2 is green -- they read "against that stage's root", group "the marks of one stage", and route on
"the revise's per-place provenance", none of which exist until this SP lands. Writing them now
means shaping code against inputs that have not decided what they are, which `CLAUDE.md` refuses.

---

## Global Constraints

Every task's requirements implicitly include these.

- **`uv run` for everything.** Python is pinned to 3.11, the floor `plugins/` ships against. A bare
  `python` re-opens a measured gap: four shipped scripts once raised `NameError` at import on 3.11
  while every test passed on 3.14.
- **NO HEREDOCS AND NO `sed`. NOT FOR ANYTHING.** Enforced by `~/.claude/hooks/shell-eats-text.py`,
  which refuses the call. Change a file with `Edit`/`Write`; do a repeated edit with a `.py` script
  run through `uv run python`; **write every commit message to a file and use `git commit -F
  <file>`.** The hook also refuses `-m`/`--message`/`--body` when the command contains a backtick
  or `$(` -- escaping is not the fix, the file form is.
- **Shipped files import the standard library only**, and no `except` clause in a shipped file
  holds a tuple literal -- bind it to a name (`READ_ERRORS`, `PARSE_ERRORS`).
- **`plugins/` is BUILT, not written.** Edit `src/comment_review/`, then
  `uv run python scripts/build_plugin.py`, and commit both. What is written by hand under
  `plugins/` is only `agents/*.md`, `SKILL.md` and `references/*.md`.
- **ASCII only in prose.** Write `--` for an em-dash.
- **No subjective claims** in comments, docstrings or commit messages -- no "robust", "clean",
  "elegant". Write what is measured, enforced, or observed. `clean` is a reserved verdict name and
  is never a loose adjective.
- **NO TEST TAKES ITS EXPECTATION FROM THE CODE UNDER TEST** (`decision-log.md Vocabulary: #23`).
  An input may come from reality -- a real page through `page_for`, a real binder, the 706 recorded
  marks. An expectation may come from the shipped prose, a recorded run's output, or a literal a
  human checked. **Never from the module being tested.**
- **A `T` box is ticked with the tool, a `P` box by hand.** `scripts/todo_tool.py` owns `TODO/` and
  recomputes counts on every write; it does **not** manage `docs/plans/`, so a `P` box is an
  ordinary `Edit`.

---

## Where each `P` box is checked off

**Roy, 2026-08-28:** *"make certain to include in the plan where each of these plan tasks should be
able to be checked off and that they are checked."* Every `P` box this SP delivers is ticked by
exactly one SP task, in that task's own commit -- so a stranger reading `git log` can see the box
and the work that earned it in the same diff.

| `P` box | ticked in | also ticks `T` |
| --- | --- | --- |
| **P1.1**, **P1.2**, **P1.3** | Task 1 | `the-ported-mark-does-not-fit-the-brief` T1, T2, T3; `record-and-verdicts-disagree` T4 |
| **P1.4** | Task 2 | -- (`Vocabulary: #17`, a substitution) |
| **P1.5**, **P1.6** | Task 3 | `the-ported-mark-does-not-fit-the-brief` T4 |
| **P1.7** | Task 4 | `the-ported-mark-does-not-fit-the-brief` T5 |
| **P1.8**, **P1.9** | Task 5 | `the-fields-do-not-say-a-mark-may-cite-across` T1, T2, T3, T4, T5 |
| **P2.1** | Task 6 | `the-flow-assumes-every-role-reads-at-once` T1 |
| **P2.2** | Task 7 | `the-flow-assumes-every-role-reads-at-once` T2 |
| **P2.3** | Task 8 | `the-flow-assumes-every-role-reads-at-once` T3 |
| **P2.4** | Task 9 | `the-flow-assumes-every-role-reads-at-once` T4 |
| **P2.5** | Task 10 | `the-flow-assumes-every-role-reads-at-once` T5 |
| **P5.2**, **P2.6** | Task 11 | `the-flow-assumes-every-role-reads-at-once` T6 |
| **P2.7** | Task 12 | `the-flow-assumes-every-role-reads-at-once` T7 |
| **G1**, **G2**, **G4** (P1/P2 scope) | Task 13 | -- |

! **G3, G5 and G6 are NOT ticked by this SP.** They are release gates over the whole `P` plan, and
P3-P6 are still open. Task 13 verifies its own scope and stops.

**The tick is a step, not a courtesy.** A task that implements the work and does not tick the box
has left the backlog claiming the work remains -- which is what an unchecked box asserts.

---

## File Structure

| file | responsibility |
| --- | --- |
| `src/comment_review/desk/mark.py` | **modify.** One row states every key a claim owes; the gate reads that row |
| `src/comment_review/flows/marks.py` | **modify.** The seeded row carries `raw_text` and the sheet a `code_concerns` list; the header names the revise |
| `src/comment_review/binder/binder.py` | **modify.** The binder records the root it was censused from |
| `src/comment_review/desk/stages.py` | **create.** The stage list as data, and the two kinds |
| `src/comment_review/flows/revise.py` | **create.** Pull one revise: tree copy, drafts overlaid, `prove_unchanged`, address-set assertion |
| `src/comment_review/results/differences.py` | **create.** Render a difference in git's spelling. Rules on nothing |
| `src/comment_review/commands/taken_in.py` | **create.** `main()` and argparse for `taken_in` |
| `src/comment_review/__main__.py` | **modify.** Register `taken_in` |
| `scripts/render_brief.py` | **create.** Write the brief's generated block from `INSTRUCTIONS` |
| `tests/test_mark.py` | **replace.** Cases from the brief's table and the 706 recorded marks |
| `tests/test_stages.py`, `tests/test_revise.py`, `tests/test_differences.py`, `tests/test_taken_in.py` | **create** |

---

## Test helpers -- write these once, in `tests/helpers.py`

Tasks 8, 9, 10 and 11 use these. **Every one takes its input from reality**, which is the
constraint above: a real tree, a real docket, a real page. None of them builds an expectation.

```python
"""Inputs the revise tests need. ! INPUTS ONLY -- no helper here decides what
a test should expect. `decision-log.md Vocabulary: #23`.
"""

from pathlib import Path

from comment_review.binder.binder import bind
from comment_review.flows.page_for import page_of, source_of

ORIGINAL = {"root": ".", "revise": 0}


def a_small_real_tree(tmp_path: Path) -> Path:
    """Three real files copied out of this repo, so the pages are real pages."""
    repo = tmp_path / "lib"
    repo.mkdir()
    for name in ("mark.py", "marks.py", "binder.py"):
        src = next(Path("src/comment_review").rglob(name))
        (repo / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return repo


def pages_of(root: Path) -> list:
    """Every `.py` page under `root`, through the real reader."""
    return [page_of(p, source_of(p), root) for p in sorted(root.rglob("*.py"))]


def binder_of(root: Path, revise: int) -> dict:
    return bind(pages_of(root), read_from={"root": str(root), "revise": revise})


def the_row_for(binder: dict, name: str) -> dict:
    from comment_review.binder.binder import rows_of

    return next(r for r in rows_of(binder) if r["path"].endswith(name))


def a_docket_over(root: Path, names: list[str], mangle: bool = False) -> dict:
    """A docket replacing each named page's first paragraph with itself plus a
    marker line -- so the replacement is real prose at a real cue.

    ! The shape is `docket.docket`'s own, documented at its module docstring:
    `{"pages": [{"path", "sha", "alterations": [{"cue", "text"}]}]}`.

    Args:
        mangle: state a sha the page does not have, which the chain refuses at
            `verify`. What `test_a_refusal_leaves_no_revise` needs.
    """
    pages = []
    for name in names:
        row = the_row_for(binder_of(root, 0), name)
        page = next(p for p in pages_of(root) if p.path.endswith(name))
        pages.append({
            "path": name,
            "sha": "0" * len(page.sha) if mangle else page.sha,
            "alterations": [{"cue": row["cue"], "text": row["raw_text"] + "\n# set here."}],
        })
    return {"pages": pages}


def a_docket_that_rewrites(root: Path, name: str) -> dict:
    """One page altered, so the revise differs from the original in one file."""
    return a_docket_over(root, [name])


def a_docket_whose_claim_is_not_in_the_page(root: Path, name: str) -> dict:
    """A docket the chain must refuse, so no revise survives it."""
    return a_docket_over(root, [name], mangle=True)


def apply_unified(before: str, diff_lines: list[str]) -> str:
    """Apply a unified diff. ! A CHECKED LITERAL ROUND TRIP: this is deliberately
    a second implementation, so `differences.unified` is not asked whether it
    agrees with itself."""
```

!! **RULING, pre-flight 2026-08-28: this file is written in Task 3, Step 0.** It was scheduled for
Task 8, but **Task 3's own test already calls `binder_of`** -- the first task that uses it is the
one that writes it. ! Writing it earlier changes nothing about what any test asserts, because the
file is inputs-only and carries no expectation. ! `a_docket_over` reads
the page's OWN first paragraph and appends to it, so `claim.from` is verbatim by construction and
the chain cannot refuse it for a reason the test did not intend.

---

## Task 1: The claim keys, and the gate that reads them

**Delivers:** P1.1, P1.2, P1.3. **Works** `the-ported-mark-does-not-fit-the-brief` T1, T2, T3 and
`record-and-verdicts-disagree` T4.

**Files:**
- Modify: `src/comment_review/desk/mark.py:242-244` (`claim_keys`), `:256-279` (`allowed`),
  `:282-306` (`_claim_problems`)
- Replace: `tests/test_mark.py`

**Interfaces:**
- Produces: `claim_keys(spec: Instruction) -> list[str]` -- **one flat list**, not a pair.
  `allowed()["claim"]` becomes `dict[str, list[str]]`.
- Consumes: nothing from earlier tasks.

**The expectation, and where it comes from:** `plugins/comment-review/skills/comment-review/references/reviewer-brief.md:280-288`,
the table a role actually reads. Copy it as a literal into the test. **Do not derive it from
`INSTRUCTIONS`** -- that is the defect this task exists to close.

```
clean    -> []
query    -> ["shape", "attempted", "settles"]
drop     -> ["drop"]
correct  -> ["false", "true"]
patch    -> ["from", "to"]
add      -> ["missing", "anchor"]
move     -> ["from", "to"]
```

- [ ] **Step 1: Write the failing test**

Create `tests/test_mark_brief.py`:

```python
"""The gate against the brief a role reads.

! THE EXPECTATION IS A LITERAL COPIED FROM `reviewer-brief.md`, never from
`INSTRUCTIONS` -- `decision-log.md Vocabulary: #23`. A suite that builds its
cases from the table it is checking can only confirm.
"""

from comment_review.desk.mark import allowed, problems

# The brief's published table, reviewer-brief.md:280-288, copied by hand.
BRIEF = {
    "clean": [],
    "query": ["shape", "attempted", "settles"],
    "drop": ["drop"],
    "correct": ["false", "true"],
    "patch": ["from", "to"],
    "add": ["missing", "anchor"],
    "move": ["from", "to"],
}


def test_every_instruction_owes_the_keys_the_brief_publishes():
    assert allowed()["claim"] == BRIEF


def test_an_add_written_from_the_brief_is_accepted():
    mark = {
        "mark": "add",
        "address": "src/m.py@b3",
        "reason": "the guard's direction is undocumented",
        "claim": {"missing": "the guard rejects zero", "anchor": "`compute_rates`"},
        "change": {"to": "# Rejects zero."},
        "sources": [{"cite": "src/m.py:12", "verbatim": "if n == 0: raise"}],
    }
    assert problems("src/m.py@b3", mark) == []


def test_a_query_written_from_the_brief_is_accepted():
    mark = {
        "mark": "query",
        "address": "src/m.py@b3",
        "reason": "the units are not stated anywhere I can read",
        "claim": {
            "shape": "unable-to-determine",
            "attempted": "grepped the module and its callers for a unit",
            "settles": "the caller that supplies the value",
        },
        "sources": [{"cite": "src/m.py:12", "verbatim": "rate = n / total"}],
    }
    assert problems("src/m.py@b3", mark) == []


def test_a_query_naming_a_shape_outside_the_three_is_refused():
    mark = {
        "mark": "query",
        "address": "src/m.py@b3",
        "reason": "unclear",
        "claim": {"shape": "i-give-up", "attempted": "read it", "settles": "a human"},
        "sources": [{"cite": "src/m.py:12", "verbatim": "rate = n / total"}],
    }
    assert problems("src/m.py@b3", mark) != []
```

- [ ] **Step 2: Run it and confirm it fails**

```
uv run pytest -q tests/test_mark_brief.py
```

Expected: all four FAIL. `allowed()["claim"]` returns `{"all": [...], "any": [...]}` per
instruction, `query` demands a key literally named `outside-my-role`, and `add`'s anchor check
reads `claim.missing`.

- [ ] **Step 3: One row states every key**

Replace `claim_keys` at `desk/mark.py:242`:

```python
def claim_keys(spec: Instruction) -> list[str]:
    """Every key this instruction's `claim` must carry.

    !! THE TRAITS DERIVE KEYS, AND DROPPING THAT IS WHAT BROKE THE GATE.
    MEASURED 2026-08-28: without it, `allowed()` published `query`'s three
    SHAPE VALUES as though they were claim KEYS, so a mark written from the
    brief verbatim was refused. One row states the whole obligation; a trait
    added here reaches the gate, the brief and the sheet together.
    """
    keys = list(spec.claim_all)
    if spec.claim_any:
        keys.append("shape")
    if spec.needs_attempted:
        keys.append("attempted")
    if spec.needs_settles:
        keys.append("settles")
    if spec.needs_anchor:
        keys.append("anchor")
    return keys
```

- [ ] **Step 4: `allowed()` publishes that list**

In `allowed()`, replace the loop and the `claim` entry:

```python
    claims = {name: claim_keys(spec) for name, spec in INSTRUCTIONS.items()}
```

and leave `"claim": claims`. `values.shape` already carries the closed set for `claim.shape`, so
nothing else in the returned shape moves.

- [ ] **Step 5: The gate reads the same list**

Replace the body of `_claim_problems` after the `isinstance` guard:

```python
    out = []
    missing = [k for k in claim_keys(spec) if not filled(claim.get(k))]
    if missing:
        out.append(f"{where}: {spec.claim_help} (missing {', '.join(missing)})")
    # ! The shape is a VALUE in a closed set, not a key. Checking it
    # structurally is what lets `collator` route on it without reading prose.
    if spec.claim_any and claim.get("shape") not in spec.claim_any:
        out.append(f"{where}: {spec.claim_help}")
    if spec.needs_anchor and not ANCHOR_NAME.search(str(claim.get("anchor", ""))):
        out.append(
            f"{where}: add needs the anchor NAMED in backticks, e.g. {ANCHOR_EXAMPLE}"
        )
    return out
```

Delete the trailing `owed` loop -- `attempted` and `settles` are now in `claim_keys`, so checking
them again is a second statement of one rule.

- [ ] **Step 6: Run the new test**

```
uv run pytest -q tests/test_mark_brief.py
```

Expected: 4 passed.

- [ ] **Step 7: Replace the circular suite**

Delete `tests/test_mark.py` and rewrite it taking **inputs** from
`evidence/the-loop-measured-2026-08-27/marks.jsonl` (706 real marks) and **expectations** from
`BRIEF` in `tests/test_mark_brief.py`. No case may read `INSTRUCTIONS`.

```
uv run pytest -q
```

Expected: the full suite green.

- [ ] **Step 8: Prove the new suite could have caught it**

Revert `claim_keys` to `return list(spec.claim_all), list(spec.claim_any)` in a scratch copy, run
`tests/test_mark_brief.py`, confirm FAIL, restore. A suite that passes both ways is testing itself.

- [ ] **Step 9: Build, gate, and tick the boxes**

```
uv run python scripts/build_plugin.py
uv run ruff check . && uv run ty check src/comment_review/
uv run python scripts/check_shipped_syntax.py
uv run python scripts/todo_tool.py check the-ported-mark-does-not-fit-the-brief 1
uv run python scripts/todo_tool.py check the-ported-mark-does-not-fit-the-brief 2
uv run python scripts/todo_tool.py check the-ported-mark-does-not-fit-the-brief 3
uv run python scripts/todo_tool.py check record-and-verdicts-disagree 4
```

Then `Edit` `docs/plans/0.2.4-the-mark-and-the-collator.md`, changing `- [ ] **T1.1**`,
`- [ ] **T1.2**` and `- [ ] **T1.3**` to `- [x]`.

- [ ] **Step 10: Commit**

`Write` the message to a file, then:

```
git add -A && git commit -F <message-file>
```

---

## Task 2: `verdict` -> `instruction`

**Delivers:** P1.4. A one-for-one substitution under `conventions.md` -- the spelling changes and
no reader's behaviour does.

**Files:**
- Modify: `src/comment_review/desk/mark.py`, `src/comment_review/flows/marks.py`
- Modify: **every hand-written file under `plugins/`** -- `SKILL.md`, all of `references/*.md`
  including `vocabulary.toml`, and the four files under `agents/`

!! **RULING, pre-flight 2026-08-28: the scope is every hand-written file under `plugins/`, not a
short list.** This task's own gate scans all of `plugins/`, and `SKILL.md` says *"The seven
verdicts"* while the references use the word throughout -- **a Files list shorter than the gate is
a task that cannot pass itself.** ! It stays a one-for-one substitution under `conventions.md`: the
spelling changes and no reader's behaviour does, which is what that rule permits across a lane
boundary.

! **The gate allows the word inside a fenced block quoting a ruling** (`decision-log`,
`history.md`, `prototype/`), which is the exception `check_vocabulary.py` already makes.

- [ ] **Step 1: Write the failing check**

Add to `tests/gates/test_vocabulary.py`:

```python
def test_no_shipped_file_calls_the_field_a_verdict():
    offenders = []
    for path in (REPO / "plugins").rglob("*"):
        if path.suffix not in {".md", ".py", ".toml"} or not path.is_file():
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "verdict" in line.lower() and "decision-log" not in line:
                offenders.append(f"{path.relative_to(REPO)}:{n}")
    assert offenders == [], offenders
```

- [ ] **Step 2: Run it and confirm it fails**

```
uv run pytest -q tests/gates/test_vocabulary.py -k verdict
```

- [ ] **Step 3: Substitute, in `src/` and the hand-written prose**

Write a `.py` script under the scratchpad that asserts the old token is present before replacing
it in each named file (`assert old in text`), then run it with `uv run python`. Do not use `sed`.
`prototype/` keeps the old word -- `Vocabulary: #19` rules that a captured record is not renamed.

- [ ] **Step 4: Build and re-run**

```
uv run python scripts/build_plugin.py
uv run pytest -q && uv run python scripts/check_vocabulary.py
```

- [ ] **Step 5: Tick and commit**

`Edit` P1.4 to `- [x]`, write the message to a file, `git add -A && git commit -F <file>`.

---

## Task 3: `raw_text` on the row, `code_concerns` on the sheet

**Delivers:** P1.5, P1.6. **Works** `the-ported-mark-does-not-fit-the-brief` T4.

**Files:**
- Modify: `src/comment_review/flows/marks.py:40-50` (`seed`), `:53-80` (`problems_in`)
- Modify: `plugins/comment-review/skills/comment-review/references/reviewer-brief.md`
- Test: `tests/test_marks_flow.py`

**Found while planning:** `raw_text` is **already on every binder row** --
`binder.py:89`, `"raw_text": "\n".join(paragraph.raw_lines)`. So P1.5 is one line in `seed`, not a
change to the binder. The paragraph is the revise's bytes because the binder was censused from
that root; **Task 7 is what names which root that was**, and this task does not need it.

- [ ] **Step 0: Write `tests/helpers.py`**

The file is in the *Test helpers* section above. Tasks 8, 9, 10 and 11 use it; this is the first
task that does. It carries inputs only -- no helper there decides what a test should expect.

- [ ] **Step 1: Write the failing test**

```python
def test_a_seeded_row_carries_the_paragraph_bytes():
    # INPUT FROM REALITY: a real page of this repo through the real binder.
    # ! `binder_of` is the helper above; Task 7 makes `read_from` required and
    # this call already goes through it, so nothing here moves then.
    binder = binder_of(Path("src/comment_review/desk"), 0)
    sheet = seed(binder, "block-context")
    row = next(r for r in sheet["marks"] if r["address"].endswith("@a0"))
    source = Path("src/comment_review/desk/mark.py").read_text(encoding="utf-8")
    assert row["raw_text"] in source


def test_a_sheet_carrying_a_code_concern_validates():
    sheet = {"role": "block-context", "marks": [], "code_concerns": [
        {"where": "src/m.py:12", "concern": "the guard admits a negative"}
    ]}
    assert problems_in(sheet) == ([], 0)
```

- [ ] **Step 2: Run and confirm both fail**

```
uv run pytest -q tests/test_marks_flow.py
```

- [ ] **Step 3: Carry `raw_text`, accept `code_concerns`**

In `seed`, add `"raw_text": row.get("raw_text", "")` to each emitted entry, and
`"code_concerns": []` beside `"role"` and `"marks"`. In `problems_in`, refuse a `code_concerns`
that is present and not a list; a missing one is not a problem.

- [ ] **Step 4: Run**

```
uv run pytest -q tests/test_marks_flow.py
```

- [ ] **Step 5: Name the key in the brief**

Add `code_concerns` to `reviewer-brief.md` as a sheet-level key, saying it holds concerns about the
CODE that no instruction can carry. **State the key and its shape only** -- when a role should
raise one is `agents`'.

- [ ] **Step 6: Build, gate, tick, commit**

```
uv run python scripts/build_plugin.py && uv run pytest -q
uv run python scripts/check_vocabulary.py
uv run python scripts/todo_tool.py check the-ported-mark-does-not-fit-the-brief 4
```

`Edit` P1.5 and P1.6 to `- [x]`. Commit with `-F`.

---

## Task 4: Rebuild the generator the brief claims to have

**Delivers:** P1.7. **Works** `the-ported-mark-does-not-fit-the-brief` T5.

`reviewer-brief.md:278` carries `<!-- BEGIN GENERATED: verdict table --
prototype/render_brief.py -->` and **that script exists nowhere in the tree**, so the table
announces it is generated while being hand-maintained. That is what let `add` drift.

**Files:**
- Create: `scripts/render_brief.py`
- Modify: `plugins/comment-review/skills/comment-review/references/reviewer-brief.md:278`
- Test: `tests/gates/test_brief_table.py`

- [ ] **Step 1: Write the failing gate**

```python
def test_the_committed_block_matches_a_fresh_render():
    import subprocess, sys
    fresh = subprocess.run(
        [sys.executable, str(REPO / "scripts/render_brief.py"), "--print"],
        capture_output=True, text=True, check=True,
    ).stdout
    brief = (REPO / BRIEF_PATH).read_text(encoding="utf-8")
    block = brief.split("<!-- BEGIN GENERATED")[1].split("<!-- END GENERATED")[0]
    assert fresh.strip() in block
```

- [ ] **Step 2: Run and confirm it fails** -- the script does not exist.

- [ ] **Step 3: Write `scripts/render_brief.py`**

It reads `INSTRUCTIONS`, emits the table from `claim_keys(spec)` and `spec.payload`, takes
`--print` (stdout) or `--write` (rewrite the block in place between the markers), and exits
nonzero if either marker is missing.

- [ ] **Step 4: Render, and correct the marker**

```
uv run python scripts/render_brief.py --write
```

The marker must name `scripts/render_brief.py`, not `prototype/render_brief.py`, and say
`instruction table` after Task 2.

- [ ] **Step 5: Run, then prove the gate bites**

```
uv run pytest -q tests/gates/test_brief_table.py
```

Then hand-edit one cell of the committed block, re-run, confirm FAIL, restore.

- [ ] **Step 6: Build, tick, commit**

```
uv run python scripts/build_plugin.py && uv run pytest -q
uv run python scripts/todo_tool.py check the-ported-mark-does-not-fit-the-brief 5
```

`Edit` P1.7 to `- [x]`. Commit with `-F`.

---

## Task 5: What the brief says about `ran`, and about the library

**Delivers:** P1.8, P1.9. **Works** `the-fields-do-not-say-a-mark-may-cite-across` T1, T2, T3, T4,
T5.

**Files:**
- Modify: `plugins/comment-review/skills/comment-review/references/reviewer-brief.md`
- Test: `tests/gates/test_brief_states_the_rules.py`

- [ ] **Step 1: Write the failing gate**

```python
def test_the_brief_names_ran_and_says_what_it_is_for():
    brief = (REPO / BRIEF_PATH).read_text(encoding="utf-8")
    assert "`ran`" in brief
    assert "library" in brief


def test_the_library_rule_is_stated_once():
    hits = [p for p in (REPO / "plugins").rglob("*.md")
            if "may cite any place in the library" in p.read_text(encoding="utf-8").lower()]
    assert len(hits) == 1, [str(p) for p in hits]
```

- [ ] **Step 2: Run and confirm it fails.**

- [ ] **Step 3: Write the two passages**

`ran` -- the command that settled a claim; a claim settled by execution without it is incomplete.
The library rule -- a `source` may cite any place in the LIBRARY (`Vocabulary: #15`: every file in
the project under review, never this program's own tree), with the disagree-and-cite rule and its
corollary. **One file states it; no agent file restates it.**

- [ ] **Step 4: Run, build, tick, commit**

```
uv run pytest -q && uv run python scripts/build_plugin.py
uv run python scripts/check_vocabulary.py
uv run python scripts/todo_tool.py check the-fields-do-not-say-a-mark-may-cite-across 1
uv run python scripts/todo_tool.py check the-fields-do-not-say-a-mark-may-cite-across 2
uv run python scripts/todo_tool.py check the-fields-do-not-say-a-mark-may-cite-across 3
uv run python scripts/todo_tool.py check the-fields-do-not-say-a-mark-may-cite-across 4
uv run python scripts/todo_tool.py check the-fields-do-not-say-a-mark-may-cite-across 5
```

`Edit` P1.8 and P1.9 to `- [x]`. Commit with `-F`.

---

## Task 6: The stage list, as data

**Delivers:** P2.1. **Works** `the-flow-assumes-every-role-reads-at-once` T1.

**Files:**
- Create: `src/comment_review/desk/stages.py`
- Test: `tests/test_stages.py`

**Interfaces:**
- Produces: `EDITORIAL = "editorial"`, `ENRICHING = "enriching"`,
  `Stage(NamedTuple)` with `name: str`, `kind: str`, `roles: tuple[str, ...]`;
  `STAGES: tuple[Stage, ...]`; `pulls_revise(stage: Stage) -> bool`.

**The expectation, and where it comes from:** `SKILL.md:544-583`, which states 4a runs
`ownership-context` alone and 4c runs the other three in one message.

- [ ] **Step 1: Write the failing test**

```python
from comment_review.desk.stages import (
    EDITORIAL,
    ENRICHING,
    STAGES,
    Stage,
    pulls_revise,
)

# EXPECTATION FROM SKILL.md:550-551 -- the shipped prose, not the module.
def test_ownership_context_runs_alone_and_first():
    assert STAGES[0].roles == ("ownership-context",)
    assert STAGES[0].kind == EDITORIAL


def test_the_other_three_share_one_stage():
    later = [s for s in STAGES if "block-context" in s.roles][0]
    assert set(later.roles) == {"block-context", "function-context", "module-context"}


def test_only_an_editorial_stage_pulls_a_revise():
    assert all(pulls_revise(s) == (s.kind == EDITORIAL) for s in STAGES)
    assert not pulls_revise(Stage("annotate", ENRICHING, ()))
```

- [ ] **Step 2: Run and confirm it fails.**

- [ ] **Step 3: Write `stages.py`** -- the two kind constants, the `Stage` tuple, `STAGES` as a
literal tuple, and `pulls_revise` as `stage.kind == EDITORIAL`. **No branch on a role's name**:
adding a stage must be a row.

- [ ] **Step 4: Run.** `uv run pytest -q tests/test_stages.py`

- [ ] **Step 5: Build, tick, commit**

```
uv run python scripts/build_plugin.py && uv run pytest -q
uv run python scripts/todo_tool.py check the-flow-assumes-every-role-reads-at-once 1
```

`Edit` P2.1 to `- [x]`. Commit with `-F`.

---

## Task 7: The binder records the root it was censused from

**Delivers:** P2.2. **Works** `the-flow-assumes-every-role-reads-at-once` T2.

**Files:**
- Modify: `src/comment_review/binder/binder.py` (`bind`, and the shape version constant)
- Modify: `src/comment_review/flows/marks.py` (`seed` header)
- Test: `tests/test_binder_records_its_root.py`

**Interfaces:**
- Produces: a binder key `"read_from"` -- `{"root": "<path>", "revise": <int>}`, where `revise` is
  `0` for the original. `seed()` copies it onto the sheet as `"read_from"`.

- [ ] **Step 1: Write the failing test**

```python
def test_a_binder_built_from_the_original_says_so():
    # !! RULING, pre-flight: COMPARE `Path`s, NEVER PATH STRINGS. This repo is
    # developed on Windows, where `str(Path("a/b"))` is `a\b` -- a string literal
    # here is green on one machine and red on the other.
    root = Path("src/comment_review/desk")
    binder = binder_of(root, 0)
    assert Path(binder["read_from"]["root"]) == root
    assert binder["read_from"]["revise"] == 0


def test_a_binder_that_cannot_say_which_root_it_read_is_refused():
    with pytest.raises(TypeError):
        bind(pages_of(Path("src/comment_review/desk")))


def test_the_sheet_header_names_the_revise():
    sheet = seed(binder_of(Path("src/comment_review/desk"), 0), "block-context")
    assert sheet["read_from"]["revise"] == 0
```

- [ ] **Step 2: Run and confirm it fails.**

- [ ] **Step 3: Add the field.** `bind` takes `read_from` and writes it; **absent is refused, not
defaulted** -- a binder that cannot say which root it read is the ambiguity this task removes.
Bump the binder's shape version so an old artifact is refused by name rather than misread.

- [ ] **Step 4: `seed` copies it** onto the sheet beside `role`, `marks` and `code_concerns`.

- [ ] **Step 5: Run, build, tick, commit**

```
uv run pytest -q && uv run python scripts/build_plugin.py
uv run python scripts/todo_tool.py check the-flow-assumes-every-role-reads-at-once 2
```

`Edit` P2.2 to `- [x]`. Commit with `-F`.

---

## Task 8: Pull a revise

**Delivers:** P2.3. **Works** `the-flow-assumes-every-role-reads-at-once` T3.

**Files:**
- Create: `src/comment_review/flows/revise.py`
- Test: `tests/test_revise.py`

**Interfaces:**
- Consumes: `proof_setter.run(docket: dict, repo: Path, into: Path) -> (list[Drafted], list[Refusal])`,
  where `Drafted` is `(path: str, draft: Path, sha: str)`.
- Produces: `pull(docket: dict, repo: Path, into: Path, revise: int) -> Pulled`, with
  `Pulled(root: Path, revise: int, set_by: dict[str, str], refusals: list[Refusal])`.
  `set_by` maps address -> the role that set it, which is the **provenance P6 routes on**.

**The order, and why:** copy the tree FIRST, then run `proof_setter` into a scratch directory, then
move each draft over its copy. `proof_setter` refuses an `into` that overlaps its `repo`, so the
scratch directory must be disjoint from both.

- [ ] **Step 1: Write the failing test**

```python
def test_the_revise_holds_every_library_file_and_only_the_scheduled_ones_differ(tmp_path):
    repo = a_small_real_tree(tmp_path)          # INPUT FROM REALITY, not a fixture literal
    pulled = pull(a_docket_over(repo, ["mark.py"]), repo, tmp_path / "r1", revise=1)
    assert {p.name for p in pulled.root.rglob("*.py")} == {p.name for p in repo.rglob("*.py")}
    changed = [p for p in pulled.root.rglob("*.py")
               if p.read_bytes() != (repo / p.relative_to(pulled.root)).read_bytes()]
    assert [p.name for p in changed] == ["mark.py"]


def test_a_refusal_leaves_no_revise(tmp_path):
    repo = a_small_real_tree(tmp_path)
    docket = a_docket_whose_claim_is_not_in_the_page(repo, "mark.py")
    pulled = pull(docket, repo, tmp_path / "r1", revise=1)
    assert pulled.refusals and not pulled.root.exists()
```

- [ ] **Step 2: Run and confirm both fail.**

- [ ] **Step 3: Write `pull`.** Copy the tree, run the chain into a scratch dir, overlay each
`Drafted.draft` onto its copy, record `set_by`. On any `Refusal`, discard the whole revise --
`Process: #20`, a refusal aborts the run whole.

- [ ] **Step 4: Run.** `uv run pytest -q tests/test_revise.py`

- [ ] **Step 5: Prove the executable code is unchanged**

```
uv run python src/comment-review.py prove_unchanged --base <sha> --repo <revise-root> <paths...>
```

Expected: every path passes. `proof_setter` already proves it per draft; this proves it over the
assembled revise, which is what a later stage reads.

- [ ] **Step 6: Build, tick, commit**

```
uv run python scripts/build_plugin.py && uv run pytest -q
uv run python scripts/todo_tool.py check the-flow-assumes-every-role-reads-at-once 3
```

`Edit` P2.3 to `- [x]`. Commit with `-F`.

---

## Task 9: The address-invariance gate

**Delivers:** P2.4. **Works** `the-flow-assumes-every-role-reads-at-once` T4.

**This is the whole safety argument of the design**, recorded as a claim to gate rather than a fact
-- `decision-log.md Process: #35`. Everything downstream assumes a mark written at stage 3 against
`foo.py@b7` names the place stage 1 saw.

**Files:**
- Modify: `src/comment_review/flows/revise.py` -- `pull` asserts it before returning
- Test: `tests/test_revise_addresses.py`

**Interfaces:**
- Produces: `class AddressesMoved(Exception)` and
  `assert_addresses_held(original: Path, pulled: Pulled) -> None`, which raises `AddressesMoved`
  naming the addresses that appeared and the ones that disappeared.

- [ ] **Step 1: Write the failing test**

```python
def test_a_revise_yields_the_address_set_the_original_yielded(tmp_path):
    repo = a_small_real_tree(tmp_path)
    before = {r["address"] for r in rows_of(binder_of(repo, 0))}
    pulled = pull(a_docket_over(repo, ["mark.py"]), repo, tmp_path / "r1", revise=1)
    after = {r["address"] for r in rows_of(binder_of(pulled.root, 1))}
    assert after == before


def test_the_gate_fires_when_the_code_moved(tmp_path):
    # ! WHAT PROVES THE CHECK CAN FAIL. A revise whose CODE was changed by hand
    # renumbers the places below it, which is exactly what the gate exists to catch.
    repo = a_small_real_tree(tmp_path)
    pulled = pull(a_docket_over(repo, ["mark.py"]), repo, tmp_path / "r1", revise=1)
    page = pulled.root / "mark.py"
    page.write_text(page.read_text(encoding="utf-8") + "\n\ndef added():\n    return 1\n",
                    encoding="utf-8")
    with pytest.raises(AddressesMoved):
        assert_addresses_held(repo, pulled)
```

- [ ] **Step 2: Run and confirm the second fails** (the first may already pass -- that is the point
of the second).

- [ ] **Step 3: Write `assert_addresses_held`** and call it from `pull` before returning. It raises
`AddressesMoved` naming the addresses that appeared and disappeared, not merely that a set differed.

- [ ] **Step 4: Run over a real tree**

```
uv run pytest -q tests/test_revise_addresses.py
```

- [ ] **Step 5: Build, tick, commit**

```
uv run python scripts/build_plugin.py && uv run pytest -q
uv run python scripts/todo_tool.py check the-flow-assumes-every-role-reads-at-once 4
```

`Edit` P2.4 to `- [x]`. Commit with `-F`.

---

## Task 10: Every read for a stage resolves against that stage's root

**Delivers:** P2.5. **Works** `the-flow-assumes-every-role-reads-at-once` T5.

**Files:**
- Modify: the call sites the test below forces -- **the implementer names them in its report**
- Test: `tests/test_stage_root.py`

! **RULING, pre-flight 2026-08-28:** the behaviour is pinned by the test, which is the checkable
part. An exact file list written before the code is read would be a guess presented as a spec.

- [ ] **Step 1: Write the failing test**

```python
def test_a_source_citing_an_edited_page_reads_the_revise(tmp_path):
    # `marks.py` imports from `mark.py`, so a source cite crosses between them
    # for real rather than by arrangement.
    repo = a_small_real_tree(tmp_path)
    pulled = pull(a_docket_that_rewrites(repo, "mark.py"), repo, tmp_path / "r1", revise=1)
    row = the_row_for(binder_of(pulled.root, 1), "mark.py")
    assert row["raw_text"] in (pulled.root / "mark.py").read_text(encoding="utf-8")
    assert row["raw_text"] not in (repo / "mark.py").read_text(encoding="utf-8")
```

- [ ] **Step 2: Run and confirm it fails.**

- [ ] **Step 3: Thread the root.** A stage's census, its binder and its source-cite reads all take
the same root. There is no default; a caller states it.

- [ ] **Step 4: Run, build, tick, commit**

```
uv run pytest -q && uv run python scripts/build_plugin.py
uv run python scripts/todo_tool.py check the-flow-assumes-every-role-reads-at-once 5
```

`Edit` P2.5 to `- [x]`. Commit with `-F`.

---

## Task 11: `differences.py`, and the `taken_in` command

**Delivers:** P5.2 and P2.6. **Works** `the-flow-assumes-every-role-reads-at-once` T6.

**Files:**
- Create: `src/comment_review/results/differences.py`
- Create: `src/comment_review/commands/taken_in.py`
- Modify: `src/comment_review/__main__.py` (register `taken_in` in `COMMANDS`)
- Test: `tests/test_differences.py`, `tests/test_taken_in.py`

**Interfaces:**
- Produces: `unified(before: str, after: str, path: str) -> list[str]` from `difflib.unified_diff`.
  **No git process** -- a revise root is a temp copy and need not be a repo.
- Produces: `taken_in --original <root> --revise <root> [paths...]`, printing the diff per page and
  a table of address -> the stage and role that set it, read from `Pulled.set_by`.

! `differences.py` **rules on nothing** -- `Vocabulary: #11` holds the collator to the same, and
P5.3 will keep rendering out of reconciliation. This module is where P5.1's `diff3` renderer lands
in the next SP.

- [ ] **Step 1: Write the failing tests**

```python
def test_the_rendered_diff_reproduces_the_revise():
    before = Path("src/comment_review/desk/mark.py").read_text(encoding="utf-8")
    after = before.replace("The keys an instruction", "The keys THIS instruction", 1)
    lines = unified(before, after, "src/comment_review/desk/mark.py")
    assert apply_unified(before, lines) == after      # a checked literal round trip


def test_taken_in_prints_nothing_when_no_stage_has_set_anything(tmp_path, capsys):
    repo = a_small_real_tree(tmp_path)
    assert main(["--original", str(repo), "--revise", str(repo)]) == 0
    assert capsys.readouterr().out.strip() == ""
```

- [ ] **Step 2: Run and confirm both fail.**

- [ ] **Step 3: Write `differences.unified`** -- `difflib.unified_diff` over `splitlines(True)`,
`fromfile`/`tofile` naming the path, `n=3`.

- [ ] **Step 4: Write `commands/taken_in.py`** and register it. Exit `0` with no output when the
roots agree; exit nonzero only when a root is unreadable.

- [ ] **Step 5: Run**

```
uv run pytest -q tests/test_differences.py tests/test_taken_in.py
uv run python src/comment-review.py taken_in --original . --revise . src/comment_review/desk/mark.py
```

Expected: the second prints nothing.

- [ ] **Step 6: Build, tick, commit**

```
uv run python scripts/build_plugin.py && uv run pytest -q
uv run python scripts/todo_tool.py check the-flow-assumes-every-role-reads-at-once 6
```

`Edit` P5.2 and P2.6 to `- [x]`. Commit with `-F`.

---

## Task 12: The last revise is the 7a draft

**Delivers:** P2.7. **Works** `the-flow-assumes-every-role-reads-at-once` T7.

**Files:**
- Modify: `src/comment_review/commands/proof.py` -- `--out` becomes the revise root
- Test: `tests/test_no_second_draft_path.py`

- [ ] **Step 1: Write the failing test**

```python
def test_only_one_path_builds_a_draft_tree():
    # EXPECTATION FROM docs/plans/0.2.4-the-mark-and-the-collator.md, P2.7:
    # one mechanism builds a draft tree, and it is the revise pull.
    callers = [p for p in (REPO / "src").rglob("*.py")
               if "proof_setter.run(" in p.read_text(encoding="utf-8")]
    assert [p.name for p in callers] == ["revise.py"]
```

- [ ] **Step 2: Run and confirm it fails** -- `commands/proof.py:78` calls it too.

- [ ] **Step 3: Route `proof` through `revise.pull`** so the command produces a revise, and the
final one is what 7a reads. Delete the second assembly path.

- [ ] **Step 4: Run, build, tick, commit**

```
uv run pytest -q && uv run python scripts/build_plugin.py
uv run python scripts/todo_tool.py check the-flow-assumes-every-role-reads-at-once 7
```

`Edit` P2.7 to `- [x]`. Commit with `-F`.

---

## Task 13: Close out this SP's scope

**Delivers:** G1, G2 and G4 **for the P1/P2 scope only**. G3, G5 and G6 stay open -- they are
release gates over the whole `P` plan, and P3-P6 have not been written.

- [ ] **Step 1: Every gate**

```
uv run ruff check .
uv run ruff format .
uv run python scripts/check_shipped_syntax.py
uv run ty check src/comment_review/
uv run python scripts/check_vocabulary.py
uv run python scripts/build_plugin.py --check
uv run pytest -q
claude plugin validate plugins/comment-review
```

**Order matters:** `check_shipped_syntax.py` runs AFTER `ruff format`, because the formatter is
what rewrites source.

- [ ] **Step 2: Prove no box in scope is left unticked**

```
uv run python scripts/todo_tool.py resync
uv run python scripts/todo_tool.py list --owner backend
```

Then `Grep` `docs/plans/0.2.4-the-mark-and-the-collator.md` for `- [ ] **P1` and `- [ ] **P2` --
both must return nothing. An unticked box asserts the work remains.

- [ ] **Step 3: Prove the SP and the P plan agree**

Read the checkbox map at the top of this file. For each row, confirm the `P` box is `[x]` and the
named `T` tasks are `[x]`. A row whose `P` is ticked and whose `T` is not means a plan closed over
a backlog entry that still claims the work is open.

- [ ] **Step 4: Tick G1, G2 and G4**, and add a dated note to
`docs/plans/0.2.4-the-mark-and-the-collator.md` saying G3, G5 and G6 wait on the P3-P6 SP.

- [ ] **Step 5: Commit**

Write the message to a file; `git add -A && git commit -F <file>`.
