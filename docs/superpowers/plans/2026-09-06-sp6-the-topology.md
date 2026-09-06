# The Topology -- Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** A task agent builds a topology for the tree in front of it, proves it fits before
a page is read, and hands one stage of it to `distribute`, which seeds one edit copy per
dispatch; `collate` then says which dispatch of that stage came back empty.

**Architecture:** `desk/topology.py::read` already parses the file and is the only thing
that does. `flows/fan_out.py::fan` already partitions a binder by a stage's dispatches and
has never had a caller. This plan gives both their consumers: a `flows/topology.py` holding
`fit` (does this topology fit this binder) and `compose` (write one that fits by
construction), a `commands/topology.py` exposing them, `distribute --topology --stage`
calling `fan`, and `collate --topology` counting a stage's dispatches against the copies
that returned. SKILL.md then names the order.

**Tech Stack:** Python 3.11 (the floor; annotations EAGER), standard library only under
`src/comment_review/**` -- `tomllib` reads TOML and nothing in the stdlib writes it, so
`compose` emits text. `pytest`, `ruff`, `ty`.

**Spec:** `docs/superpowers/specs/2026-08-29-the-master-proof-and-reconciliation-design.md`,
section 2, *Topology, and fan-out* -- the format, the two fan-out guards, the barrier.

**Plan steps this delivers:** `docs/plans/0.2.4-the-commands-for-the-middle.md` **P26, P29,
P30, P31, P32, P33**. Those work `TODO/no-command-for-the-middle.md` **T12** (distribute
takes a stage) and `TODO/staged-chain-untested.md` **T1** (the fixture). Neither T is named
on the plan today; Task 0 adds them.

**Rulings:** `decision-log.md Process: #12` (a module does one job and has no CLI; a flow
calls modules; a command exposes a flow), `#40` (backend owns the format, its validator and
the fan-out; agents own when a stage runs), `#47` (why fan-out exists), `#55` (the fit check
lives in `topology --verify`, a command with a repo), `#63` (coverage is reported in its own
list, never raised), `#73` (the task agent sequences the stages from SKILL.md; no command
does), `#74` (the topology keeps a reader, and the reader is the distribution: `distribute`
takes a stage), `#99` (a reviewer is handed the binder and its seeded copy).

## Global Constraints

- Nothing under `src/comment_review/**` imports outside the standard library.
- No `except` clause in a shipped file holds a tuple literal; bind the tuple to a name.
- No raw dict past a load or a save: `json.loads -> deserialize -> work on containers ->
  serialize -> json.dumps` (`Process: #65`, `#67`).
- An end or the middle reaches down to a leaf, never across; a flow may import anything.
- ASCII only, in files and in output. `--` for a dash.
- Every command guards stdout with `constants.utf8_console()`; the gate in
  `tests/gates/test_shipped_cli_encoding.py` reads for it textually.
- A command's own tests run it through `main()` and `sys.argv` via
  `tests/conftest.py::run_command`, never by calling the flow.
- **Per task: commit the work, then tick the P and T it closed on the plan and the TODO,
  then commit the tick.** The tick commit names the work commit. `CLAUDE.md` overrides this
  skill's ledger: the boxes on `docs/plans/` and `TODO/` are the state.

---

## The order, and why

`distribute --stage` (Task 1) goes first because it is the reader `#74` ruled the topology
keeps: until it exists, `fit` and `compose` verify and build a file nothing consumes. `fit`
(Task 2) comes before `compose` (Task 3) because a built topology is proved by passing
`fit`. The command (Task 4) exposes both once both exist. `collate --topology` (Task 5) is
independent of 2-4 and follows 1 because it counts against the same stage `distribute`
seeded. The fixture (Task 6) needs `fit` and `compose` to make its two branches mechanical.
SKILL.md (Task 7) is last so every command it names exists -- the skill-commands gate reads
SKILL.md against `COMMANDS`, and naming `topology` there is what makes the gate cover it.

**A glob that matches no page is not a fault -- `Process: #100`**, ruling `staged-chain-untested`
T2 on 2026-09-06. `fit` has two misfit kinds, the design's two guards, and no third for a
glob that matched nothing: an empty glob either leaves a page uncovered, which is refused
and named, or costs nothing. P29's verify text is narrowed to that; P33's *"naming the
globs"* is met by the `uncovered` misfit naming the stage's globs beside the pages they
missed.

**Out of this plan, stated so nobody looks for them here:** `staged-chain-untested` T3 (the
four-stage accumulation test) and T4 (a stage seeding from the revise its `reads` names)
both need the revise carried between stages, which is `#73`'s task-agent hand-off and not a
command's; `no-command-for-the-middle` T6 (each returned copy's `read_from` checked against
the stage) is the same seam. They are filed and stay filed.

---

### Task 0: Name the T tasks on the plan

**Files:**
- Modify: `docs/plans/0.2.4-the-commands-for-the-middle.md` (through the board, never by hand)

- [ ] **Step 1: Add the two TODO tasks this plan works**

```bash
job-board --plans-dir docs/plans plan add-t 0.2.4-the-commands-for-the-middle no-command-for-the-middle.md:T12
job-board --plans-dir docs/plans plan add-t 0.2.4-the-commands-for-the-middle staged-chain-untested.md:T1
job-board --plans-dir docs/plans plan refresh 0.2.4-the-commands-for-the-middle
```

- [ ] **Step 2: Commit**

Write the message to a file, then `git add docs/plans/0.2.4-the-commands-for-the-middle.md
TODO/README.md && git commit -F <file>`.

---

### Task 1: `distribute --topology --stage` seeds one copy per dispatch

**Files:**
- Modify: `src/comment_review/commands/distribute.py`
- Modify: `src/comment_review/flows/fan_out.py` (return type only, see Interfaces)
- Test: `tests/test_distribute_command.py` (create if absent; check `Glob tests/test_distribute*`)

**Interfaces:**
- Consumes: `desk.topology.read(text) -> tuple[list[Stage], str]`;
  `flows.fan_out.fan(binder, stage) -> list[dict]`; `flows.proof_io.load_binder(path)`.
- Produces: the console contract
  `distribute --topology T.toml --stage 4c --binder B.json --out-dir DIR`, writing
  `DIR/<stage>_<role>_<n>.json` for each dispatch in dispatch order, `n` counting from 1
  within the role. Exit 0 and one line per file:
  `DIR/4c_block-context_1.json: 3 places for block-context to rule on`. Exit 2 with a
  reason on stderr when the topology does not parse, the stage is not in it, or `fan`
  raises `OverlappingShards` or `UncoveredPage` -- the reason is the exception's own text.

- [ ] **Step 1: Write the failing test**

```python
"""`commands/distribute.py --topology --stage`: one seeded copy per dispatch, in order."""

import json
from pathlib import Path

from conftest import SAMPLE, run_command

from comment_review.commands import distribute as distribute_command
from comment_review.commands import gather as gather_command

FOUR_C = """
[[stage]]
name = "4a"
kind = "editorial"
reads = "original"
  [[stage.dispatch]]
  role = "ownership-context"

[[stage]]
name = "4c"
kind = "editorial"
reads = "revise:4a"
  [[stage.dispatch]]
  role = "block-context"
  paths = ["a.py"]
  [[stage.dispatch]]
  role = "block-context"
  paths = ["b.py"]
  [[stage.dispatch]]
  role = "function-context"
"""


def _tree(tmp_path, monkeypatch, capsys) -> Path:
    """Two pages, a binder over them, and the topology above, all on disk."""
    for name in ("a.py", "b.py"):
        (tmp_path / name).write_text(SAMPLE, encoding="utf-8", newline="")
    binder = tmp_path / "binder.json"
    code, _ = run_command(
        monkeypatch, capsys, gather_command,
        "--repo", str(tmp_path), "--out", str(binder), "a.py", "b.py",
    )
    assert code == 0
    (tmp_path / "t.toml").write_text(FOUR_C, encoding="utf-8")
    return tmp_path


def test_a_stage_seeds_one_copy_per_dispatch_in_dispatch_order(tmp_path, monkeypatch, capsys):
    root = _tree(tmp_path, monkeypatch, capsys)
    out = root / "copies"
    code, printed = run_command(
        monkeypatch, capsys, distribute_command,
        "--topology", str(root / "t.toml"), "--stage", "4c",
        "--binder", str(root / "binder.json"), "--out-dir", str(out),
    )
    assert code == 0, printed
    names = sorted(p.name for p in out.iterdir())
    assert names == ["4c_block-context_1.json", "4c_block-context_2.json", "4c_function-context_1.json"]
    first = json.loads((out / "4c_block-context_1.json").read_text(encoding="utf-8"))
    assert [s["path"] for s in first["sheets"]] == ["a.py"]
    third = json.loads((out / "4c_function-context_1.json").read_text(encoding="utf-8"))
    assert [s["path"] for s in third["sheets"]] == ["a.py", "b.py"]


def test_a_stage_the_topology_lacks_is_refused_by_name(tmp_path, monkeypatch, capsys):
    root = _tree(tmp_path, monkeypatch, capsys)
    code, printed = run_command(
        monkeypatch, capsys, distribute_command,
        "--topology", str(root / "t.toml"), "--stage", "4b",
        "--binder", str(root / "binder.json"), "--out-dir", str(root / "copies"),
        with_stderr=True,
    )
    assert code == 2
    assert "4b" in printed and "4a" in printed and "4c" in printed


def test_an_uncovered_page_is_refused_with_fan_outs_own_reason(tmp_path, monkeypatch, capsys):
    root = _tree(tmp_path, monkeypatch, capsys)
    (root / "t.toml").write_text(FOUR_C.replace('paths = ["b.py"]', 'paths = ["zzz.py"]'), encoding="utf-8")
    code, printed = run_command(
        monkeypatch, capsys, distribute_command,
        "--topology", str(root / "t.toml"), "--stage", "4c",
        "--binder", str(root / "binder.json"), "--out-dir", str(root / "copies"),
        with_stderr=True,
    )
    assert code == 2
    assert "no dispatch covers" in printed and "b.py" in printed
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest -q tests/test_distribute_command.py`
Expected: FAIL -- argparse exits 2 on `--topology` (unrecognized arguments), so the first
test fails on `code == 0`.

- [ ] **Step 3: Write the minimal implementation**

In `commands/distribute.py`, add the arguments and the branch. The header docstring gains
the third invocation line:

```python
    comment_review distribute --topology T.toml --stage 4c --binder B.json --out-dir DIR
```

Imports to add:

```python
from comment_review.desk.topology import read as read_topology
from comment_review.flows.fan_out import OverlappingShards, UncoveredPage, fan
```

Bind the two exceptions to a name -- no tuple literal in an `except`:

```python
# ! Bound to a name: a tuple literal in an `except` is what a newer formatter
# rewrites into a form the floor interpreter cannot parse.
FAN_REFUSALS = (OverlappingShards, UncoveredPage)
```

Arguments, after `--out`:

```python
    ap.add_argument("--topology", help="the run's topology file (--stage only)")
    ap.add_argument("--stage", help="the stage to seed, by its name in the topology")
    ap.add_argument("--out-dir", help="where one copy per dispatch is written (--stage only)")
```

The branch, before `ap.print_usage()`:

```python
    if args.stage:
        # !! ONE INVOCATION, ONE STAGE, ONE COPY PER DISPATCH -- `Process: #74`.
        # The task agent reads the ORDER from SKILL.md and runs this once per
        # stage; this reads that stage's DISPATCHES from the topology.
        missing = [n for n in ("topology", "binder", "out_dir") if not getattr(args, n)]
        if missing:
            wanted = ", ".join("--" + n.replace("_", "-") for n in missing)
            print(f"--stage needs {wanted}", file=sys.stderr)
            return 2
        stages, why = read_topology(Path(args.topology).read_text(encoding="utf-8"))
        if why:
            print(why, file=sys.stderr)
            return 2
        stage = next((s for s in stages if s.name == args.stage), None)
        if stage is None:
            known = ", ".join(s.name for s in stages)
            print(f"stage {args.stage!r} is not in the topology -- it holds: {known}", file=sys.stderr)
            return 2
        binder, problems = load_binder(Path(args.binder))
        if binder is None:
            for line in problems:
                print(line, file=sys.stderr)
            return 2
        try:
            copies = fan(binder, stage)
        except FAN_REFUSALS as exc:
            print(f"stage {stage.name!r}: {exc}", file=sys.stderr)
            return 2
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        seen: dict[str, int] = {}
        for dispatch, copy in zip(stage.dispatches, copies, strict=True):
            n = seen[dispatch.role] = seen.get(dispatch.role, 0) + 1
            where = out_dir / f"{stage.name}_{dispatch.role}_{n}.json"
            where.write_text(_as_json(copy), encoding="utf-8", newline="")
            places = sum(len(sheet["marks"]) for sheet in copy["sheets"])
            print(f"{where}: {places} places for {dispatch.role} to rule on")
        return 0
```

`fan` returns `list[dict]` in dispatch order today; leave its signature alone. If `ty`
reports `dispatch.role` as `Role` where an f-string wants `str`, `str(dispatch.role)` -- a
`StrEnum` formats as its value either way.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest -q tests/test_distribute_command.py tests/test_distribute_flow.py`
Expected: PASS. Then `uv run ruff check src tests && uv run ruff format --check src tests
&& uv run ty check`.

- [ ] **Step 5: Commit the work**

Message to a file, then `git add src/comment_review/commands/distribute.py
tests/test_distribute_command.py && git commit -F <file>`.

- [ ] **Step 6: Tick, then commit the tick**

```bash
job-board --plans-dir docs/plans todo close-task no-command-for-the-middle.md T12 --commit <sha> --statement "FINISHED"
job-board --plans-dir docs/plans plan refresh 0.2.4-the-commands-for-the-middle
```

Commit the board files with a message naming T12 and the work's sha.

---

### Task 2: `fit` -- does this topology fit this binder

**Files:**
- Create: `src/comment_review/flows/topology.py`
- Modify: `src/comment_review/flows/fan_out.py` -- `partition` is split out of `fan` so
  `fit` and `fan` compute one thing
- Test: `tests/test_topology_fit.py`

**Interfaces:**
- Consumes: `Binder` (`binder.binder`), `Stage`/`Dispatch` (`desk.stages`),
  `fan_out.OverlappingShards`, `fan_out.UncoveredPage`.
- Produces:
  - `fan_out.partition(binder, stage) -> list[tuple[Dispatch, list[Page]]]` -- the guard
    pass and the match, raising the two exceptions; `fan` becomes
    `[seed(replace(binder, pages=tuple(m)), d.role) for d, m in partition(binder, stage)]`.
  - `flows.topology.Misfit(kind: str, stage: str, detail: str)` NamedTuple, `kind` one of
    `"overlap"`, `"uncovered"`, `"reads"`. An `uncovered` detail names the pages missed AND
    the stage's globs, so the agent that wrote the glob sees it (`Process: #100`).
  - `flows.topology.fit(stages: list[Stage], binder: Binder) -> list[Misfit]` -- empty
    when the topology fits. `"reads"` is the one `desk.topology.read` already refuses;
    `fit` takes parsed stages, so the command reports `read`'s reason under that kind
    before `fit` is called (Task 4).

- [ ] **Step 1: Write the failing tests**

```python
"""`flows/topology.py::fit`: a topology either fits a binder or says which way it does not."""

from conftest import SAMPLE
from helpers import a_binder_over  # a binder over {path: source}; see helpers.py

from comment_review.desk.topology import read
from comment_review.flows.topology import fit

TWO_PAGES = {"a.py": SAMPLE, "b.py": SAMPLE}


def _stages(toml: str):
    stages, why = read(toml)
    assert not why, why
    return stages


def test_a_topology_that_covers_every_page_once_fits():
    stages = _stages("""
[[stage]]
name = "4c"
kind = "editorial"
  [[stage.dispatch]]
  role = "block-context"
  paths = ["a.py"]
  [[stage.dispatch]]
  role = "block-context"
  paths = ["b.py"]
  [[stage.dispatch]]
  role = "module-context"
""")
    assert fit(stages, a_binder_over(TWO_PAGES)) == []


def test_a_glob_matching_no_page_is_not_a_misfit_when_every_page_is_covered():
    # ! `Process: #100`: an empty glob is not a fault. The agent that wrote it
    # reads the result and modifies; only a page nobody covers is refused.
    stages = _stages("""
[[stage]]
name = "4c"
kind = "editorial"
  [[stage.dispatch]]
  role = "block-context"
  paths = ["a.py", "zzz/*.py"]
  [[stage.dispatch]]
  role = "block-context"
  paths = ["b.py"]
""")
    assert fit(stages, a_binder_over(TWO_PAGES)) == []


def test_a_page_no_dispatch_covers_is_an_UNCOVERED_misfit_naming_the_page_and_the_globs():
    stages = _stages("""
[[stage]]
name = "4c"
kind = "editorial"
  [[stage.dispatch]]
  role = "block-context"
  paths = ["a.py", "zzz/*.py"]
""")
    misfits = fit(stages, a_binder_over(TWO_PAGES))
    assert [m.kind for m in misfits] == ["uncovered"]
    assert "b.py" in misfits[0].detail
    # ! P33: the message names the globs, so the writer of `zzz/*.py` sees it.
    assert "zzz/*.py" in misfits[0].detail


def test_a_page_two_dispatches_of_one_role_claim_is_an_OVERLAP_misfit():
    stages = _stages("""
[[stage]]
name = "4c"
kind = "editorial"
  [[stage.dispatch]]
  role = "block-context"
  paths = ["a.py", "b.py"]
  [[stage.dispatch]]
  role = "block-context"
  paths = ["b.py"]
""")
    misfits = fit(stages, a_binder_over(TWO_PAGES))
    assert [m.kind for m in misfits] == ["overlap"]
    assert "b.py" in misfits[0].detail


def test_every_stage_is_checked_and_each_misfit_names_its_stage():
    stages = _stages("""
[[stage]]
name = "4a"
kind = "editorial"
  [[stage.dispatch]]
  role = "ownership-context"
  paths = ["a.py"]

[[stage]]
name = "4c"
kind = "editorial"
reads = "revise:4a"
  [[stage.dispatch]]
  role = "block-context"
  paths = ["nowhere.py"]
""")
    kinds = sorted((m.stage, m.kind) for m in fit(stages, a_binder_over(TWO_PAGES)))
    assert kinds == [("4a", "uncovered"), ("4c", "uncovered")]
```

Check `helpers.a_binder_over`'s real signature before using it (`tests/helpers.py:329`);
if it takes something other than `{path: source}`, use `binder_of` over a `tmp_path`
tree instead, as `tests/test_distribute_flow.py` does.

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/test_topology_fit.py`
Expected: FAIL with `ModuleNotFoundError: comment_review.flows.topology`.

- [ ] **Step 3: Split `partition` out of `fan`**

In `flows/fan_out.py`, the body of `fan` from `all_paths = ...` through the two raises
becomes:

```python
def partition(binder: Binder, stage: Stage) -> list[tuple[Dispatch, list[Page]]]:
    """Each dispatch with the pages its globs select, after the two guards.

    Raises:
        OverlappingShards: a page matches two dispatches of the SAME role.
        UncoveredPage: a page matches NO dispatch of a role this stage dispatches.
    """
    all_paths = [page.path for page in binder.pages]
    shards = [
        (dispatch, [p for p in binder.pages if _matches(p.path, dispatch.paths)])
        for dispatch in stage.dispatches
    ]
    by_role: dict = {}
    for dispatch, matched in shards:
        by_role.setdefault(dispatch.role, []).append(matched)
    for role, groups in by_role.items():
        counts: dict[str, int] = {}
        for group in groups:
            for page in group:
                counts[page.path] = counts.get(page.path, 0) + 1
        overlapping = sorted(path for path, n in counts.items() if n > 1)
        if overlapping:
            raise OverlappingShards(f"{role}: reached by two dispatches -- {overlapping}")
        missing = sorted(set(all_paths) - set(counts))
        if missing:
            raise UncoveredPage(f"{role}: no dispatch covers -- {missing}")
    return shards


def fan(binder: Binder, stage: Stage) -> list[dict]:
    """(docstring unchanged)"""
    return [
        seed(replace(binder, pages=tuple(matched)), dispatch.role)
        for dispatch, matched in partition(binder, stage)
    ]
```

`Page` and `Dispatch` are imported from `binder.page` and `desk.stages` -- check the
class name of a binder page in `src/comment_review/binder/binder.py` before writing the
annotation. Run `uv run pytest -q tests/test_fan_out.py` (or whichever file covers `fan`;
`Grep "fan(" tests`) to prove the split changed nothing.

- [ ] **Step 4: Write `flows/topology.py`**

```python
"""TOPOLOGY -- does a topology fit a binder, and write one that does.

    fit(stages, binder)          every way the topology does not fit, or []
    compose(directives, binder)  a topology's TEXT that fits by construction

! WHY A FLOW AND NOT `desk/topology.py`: `read` takes text and has no binder,
so it cannot ask whether a glob matches a page -- `Process: #55` puts that
question in a command with a repo, and a command exposes a flow (`#12`).

! THE GUARDS ARE `fan_out.partition`'s, NOT A SECOND COPY. `fit` runs the same
partition `fan` will run and turns its two refusals into misfits, so a topology
`fit` passes is one `fan` will not refuse. A glob that matches no page is NOT
a third kind -- `Process: #100`: it either leaves a page uncovered, which the
guard names, or costs nothing, and the agent that wrote it reads the result.
What `fit` adds is the stage's globs on an `uncovered` detail, so that agent
sees which glob missed.
"""

from typing import NamedTuple

from comment_review.binder.binder import Binder
from comment_review.desk.stages import Stage
from comment_review.flows.fan_out import OverlappingShards, UncoveredPage, partition

FAN_REFUSALS = (OverlappingShards, UncoveredPage)


class Misfit(NamedTuple):
    """One way a topology does not fit a binder.

    Attributes:
        kind: `overlap` (a page in two shards of one role), `uncovered` (a
            page no shard of a role reaches), `reads` (the file's own order
            refuses it -- reported by the command from `read`'s reason, never
            produced here).
        stage: the stage's name.
        detail: what to look at -- the role, the pages, and the stage's globs.
    """

    kind: str
    stage: str
    detail: str


def fit(stages: list[Stage], binder: Binder) -> list[Misfit]:
    """Every misfit between these stages and this binder; `[]` when it fits."""
    out: list[Misfit] = []
    for stage in stages:
        globs = ", ".join(repr(p) for d in stage.dispatches for p in d.paths) or "none"
        try:
            partition(binder, stage)
        except OverlappingShards as exc:
            out.append(Misfit("overlap", stage.name, str(exc)))
        except UncoveredPage as exc:
            out.append(Misfit("uncovered", stage.name, f"{exc} -- the stage's globs: {globs}"))
    return out
```

`partition` raises on the FIRST role that fails, so one stage yields at most one misfit;
the tests above expect exactly that. Wrap long lines for `ruff`.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run pytest -q tests/test_topology_fit.py tests/test_fan_out.py` then the gates
(`ruff check`, `ruff format --check`, `ty check`).

- [ ] **Step 6: Commit the work**

`git add src/comment_review/flows/topology.py src/comment_review/flows/fan_out.py
tests/test_topology_fit.py && git commit -F <file>`.

- [ ] **Step 7: Tick, then commit the tick**

```bash
job-board --plans-dir docs/plans plan close 0.2.4-the-commands-for-the-middle P29 --commit <sha> --statement "FINISHED; fit reports overlap and uncovered per Process 100; reads is read's"
job-board --plans-dir docs/plans plan refresh 0.2.4-the-commands-for-the-middle
```

---

### Task 3: `compose` -- write a topology that fits by construction

**Files:**
- Modify: `src/comment_review/flows/topology.py`
- Test: `tests/test_topology_compose.py`

**Interfaces:**
- Consumes: `fit`, `desk.topology.read`, `Binder`.
- Produces: `Directive = tuple[str, list[tuple[str, int]]]` -- a stage name and, in
  order, `(role, ways)` pairs; `compose(directives: list[Directive], binder: Binder) ->
  str`, TOML text that `read` accepts and `fit` passes against `binder`. A role split
  `ways` > 1 gets `ways` dispatches, each carrying an explicit list of page paths, the
  binder's pages sorted and dealt round-robin. A role with `ways == 1` gets one dispatch
  with no `paths`. Every stage is `editorial`; the first `reads = "original"`, each later
  one reads the revise of the stage before it. `ValueError` on an unknown role, on
  `ways < 1`, and on `ways` greater than the page count.

- [ ] **Step 1: Write the failing tests**

```python
"""`flows/topology.py::compose`: a topology written from directives fits the binder it was written for."""

import pytest
from conftest import SAMPLE
from helpers import a_binder_over

from comment_review.desk.topology import read
from comment_review.flows.topology import compose, fit

FOUR = {f"{n}.py": SAMPLE for n in "abcd"}


def test_a_composed_topology_reads_and_fits():
    binder = a_binder_over(FOUR)
    text = compose(
        [("4a", [("ownership-context", 1)]),
         ("4c", [("block-context", 2), ("function-context", 1), ("module-context", 1)])],
        binder,
    )
    stages, why = read(text)
    assert not why, why
    assert [s.name for s in stages] == ["4a", "4c"]
    assert stages[1].reads == "revise:4a"
    assert fit(stages, binder) == []


def test_a_split_role_gets_that_many_dispatches_dealing_the_pages_round_robin():
    text = compose([("4c", [("block-context", 2)])], a_binder_over(FOUR))
    stages, _ = read(text)
    paths = [d.paths for d in stages[0].dispatches]
    assert paths == [("a.py", "c.py"), ("b.py", "d.py")]


def test_an_unsplit_role_gets_one_dispatch_with_no_paths():
    text = compose([("4c", [("module-context", 1)])], a_binder_over(FOUR))
    stages, _ = read(text)
    assert [d.paths for d in stages[0].dispatches] == [()]


@pytest.mark.parametrize("bad", [("4c", [("no-such-role", 1)]), ("4c", [("block-context", 0)]), ("4c", [("block-context", 5)])])
def test_a_directive_the_binder_cannot_honour_is_refused(bad):
    with pytest.raises(ValueError):
        compose([bad], a_binder_over(FOUR))


def test_a_path_with_a_quote_in_it_is_still_valid_toml():
    binder = a_binder_over({'we"ird.py': SAMPLE, "plain.py": SAMPLE})
    text = compose([("4c", [("block-context", 2)])], binder)
    _, why = read(text)
    assert not why, why
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/test_topology_compose.py`
Expected: FAIL with `ImportError: cannot import name 'compose'`.

- [ ] **Step 3: Write `compose`**

Add to `flows/topology.py`:

```python
import json

from comment_review.desk.stages import ROLES

Directive = tuple[str, list[tuple[str, int]]]


def _toml_string(s: str) -> str:
    # ! JSON's string escaping is a subset of TOML's basic-string escaping for
    # every character a path may carry, and the stdlib has a JSON encoder and
    # no TOML one. Checked by a test that round-trips a quote through `read`.
    return json.dumps(s)


def compose(directives: list[Directive], binder: Binder) -> str:
    """A topology, as text, that `read` accepts and `fit` passes for `binder`."""
    pages = sorted(page.path for page in binder.pages)
    lines: list[str] = []
    previous: str | None = None
    for name, roles in directives:
        lines += ["[[stage]]", f"name = {_toml_string(name)}", 'kind = "editorial"']
        lines.append(f'reads = "revise:{previous}"' if previous else 'reads = "original"')
        for role, ways in roles:
            if role not in ROLES:
                raise ValueError(f"stage {name!r}: {role!r} is not a known role")
            if ways < 1 or ways > len(pages):
                raise ValueError(f"stage {name!r}: {role!r} split {ways} ways over {len(pages)} pages")
            for i in range(ways):
                lines += ["  [[stage.dispatch]]", f"  role = {_toml_string(role)}"]
                if ways > 1:
                    shard = ", ".join(_toml_string(p) for p in pages[i::ways])
                    lines.append(f"  paths = [{shard}]")
        lines.append("")
        previous = name
    return "\n".join(lines)
```

`ROLES` is what `desk.topology.read` validates against; `Grep "^ROLES" src/comment_review/desk/stages.py`
to confirm it is a collection of the string values.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest -q tests/test_topology_compose.py tests/test_topology_fit.py`, then
the three gates.

- [ ] **Step 5: Commit the work**, then **Step 6: tick P30 and commit the tick**, the same
shape as Task 2's steps 6 and 7 with `P30` and a statement.

---

### Task 4: `commands/topology.py` exposes `--verify` and `--build`

**Files:**
- Create: `src/comment_review/commands/topology.py`
- Modify: `src/comment_review/__main__.py` -- `TOPOLOGY = auto()` in `Command`, in
  alphabetical position after `TAKEN_IN`
- Test: `tests/test_topology_command.py`

**Interfaces:**
- Consumes: `desk.topology.read`, `flows.topology.fit`, `flows.topology.compose`,
  `flows.proof_io.load_binder`, `machine.constants.utf8_console`.
- Produces the console contract:
  - `topology --verify T.toml --binder B.json`: exit 0 and `T.toml fits B.json: N stages`
    when it fits; exit 1 and one line per misfit, `<stage>  <kind>  <detail>`, sorted by
    stage then kind; exit 2 with `read`'s reason prefixed `reads` when the file itself
    is refused (the `reads` kind, `Process: #55`).
  - `topology --build --binder B.json --stage 4a=ownership-context --stage 4c=block-context/2,function-context,module-context --out T.toml`:
    writes the composed text, runs `fit` over it, exit 0 and the same `fits` line; exit 2
    with the `ValueError`'s text on a directive the binder cannot honour. `--stage` is
    repeatable and ordered; `NAME=role[/ways],role[/ways]...`.

- [ ] **Step 1: Write the failing tests**

```python
"""`commands/topology.py`: the console face of fit and compose."""

from conftest import SAMPLE, run_command
from helpers import ...  # whatever writes a real tree; or write files and run gather as Task 1's test does

from comment_review.commands import gather as gather_command
from comment_review.commands import topology as topology_command


def _binder(tmp_path, monkeypatch, capsys):
    for n in "abcd":
        (tmp_path / f"{n}.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = tmp_path / "binder.json"
    code, _ = run_command(monkeypatch, capsys, gather_command, "--repo", str(tmp_path), "--out", str(binder), *[f"{n}.py" for n in "abcd"])
    assert code == 0
    return binder


def test_build_then_verify_round_trips(tmp_path, monkeypatch, capsys):
    binder = _binder(tmp_path, monkeypatch, capsys)
    out = tmp_path / "t.toml"
    code, printed = run_command(
        monkeypatch, capsys, topology_command,
        "--build", "--binder", str(binder), "--out", str(out),
        "--stage", "4a=ownership-context",
        "--stage", "4c=block-context/2,function-context,module-context",
    )
    assert code == 0, printed
    assert "fits" in printed and out.exists()
    code, printed = run_command(monkeypatch, capsys, topology_command, "--verify", str(out), "--binder", str(binder))
    assert code == 0 and "2 stages" in printed


def test_verify_names_every_misfit_with_its_stage_and_kind(tmp_path, monkeypatch, capsys):
    binder = _binder(tmp_path, monkeypatch, capsys)
    t = tmp_path / "t.toml"
    t.write_text('[[stage]]\nname = "4c"\nkind = "editorial"\n  [[stage.dispatch]]\n  role = "block-context"\n  paths = ["a.py", "zzz.py"]\n', encoding="utf-8")
    code, printed = run_command(monkeypatch, capsys, topology_command, "--verify", str(t), "--binder", str(binder))
    assert code == 1
    assert "4c  uncovered" in printed and "b.py" in printed
    # ! The stage's globs ride on the uncovered line, so `zzz.py` is named too.
    assert "zzz.py" in printed


def test_a_file_read_refuses_is_the_reads_kind_at_exit_2(tmp_path, monkeypatch, capsys):
    binder = _binder(tmp_path, monkeypatch, capsys)
    t = tmp_path / "t.toml"
    t.write_text('[[stage]]\nname = "4c"\nkind = "editorial"\nreads = "revise:4a"\n  [[stage.dispatch]]\n  role = "block-context"\n', encoding="utf-8")
    code, printed = run_command(monkeypatch, capsys, topology_command, "--verify", str(t), "--binder", str(binder), with_stderr=True)
    assert code == 2 and "reads" in printed and "4a" in printed


def test_build_refuses_a_directive_the_binder_cannot_honour(tmp_path, monkeypatch, capsys):
    binder = _binder(tmp_path, monkeypatch, capsys)
    code, printed = run_command(
        monkeypatch, capsys, topology_command,
        "--build", "--binder", str(binder), "--out", str(tmp_path / "t.toml"), "--stage", "4c=block-context/9",
        with_stderr=True,
    )
    assert code == 2 and "9 ways" in printed


def test_it_is_a_command():
    from comment_review.__main__ import COMMANDS
    assert "topology" in COMMANDS
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/test_topology_command.py`
Expected: FAIL with `ModuleNotFoundError: comment_review.commands.topology`.

- [ ] **Step 3: Write the command**

```python
"""The `topology` command: does a topology fit this binder, and write one that does.

    comment_review topology --verify T.toml --binder B.json
    comment_review topology --build --binder B.json --out T.toml --stage 4a=ownership-context --stage 4c=block-context/2,function-context,module-context

The work is `flows.topology`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.

! VERIFY BEFORE A PAGE IS READ. A bad configuration costs nothing only when it
is caught here -- `fan` refuses the same shapes, but from inside a run, blaming
the tree for the topology's assumption (`Process: #55`).
"""

import argparse
import sys
from pathlib import Path

from comment_review.desk.topology import read
from comment_review.flows.proof_io import load_binder
from comment_review.flows.topology import Directive, compose, fit
from comment_review.machine import constants


def _directive(spec: str) -> Directive:
    """`4c=block-context/2,function-context` -> ("4c", [("block-context", 2), ("function-context", 1)])."""
    name, _, roles = spec.partition("=")
    if not name or not roles:
        raise ValueError(f"--stage {spec!r}: want NAME=role[/ways],role[/ways]")
    out: list[tuple[str, int]] = []
    for item in roles.split(","):
        role, _, ways = item.partition("/")
        out.append((role.strip(), int(ways) if ways else 1))
    return name, out


def main() -> int:
    """Verify a topology against a binder, or build one for it."""
    constants.utf8_console()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verify", metavar="T.toml", help="the topology to check")
    ap.add_argument("--build", action="store_true", help="compose a topology for the binder")
    ap.add_argument("--binder", required=True, help="the binder the topology must fit")
    ap.add_argument("--stage", action="append", default=[], help="NAME=role[/ways],... in run order (--build)")
    ap.add_argument("--out", help="where the built topology is written (--build)")
    args = ap.parse_args()

    binder, problems = load_binder(Path(args.binder))
    if binder is None:
        for line in problems:
            print(line, file=sys.stderr)
        return 2

    if args.build:
        if not args.out or not args.stage:
            print("--build needs --out and at least one --stage", file=sys.stderr)
            return 2
        try:
            text = compose([_directive(s) for s in args.stage], binder)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        Path(args.out).write_text(text, encoding="utf-8", newline="")
        target = Path(args.out)
    elif args.verify:
        target = Path(args.verify)
        text = target.read_text(encoding="utf-8")
    else:
        ap.print_usage()
        return 2

    stages, why = read(text)
    if why:
        print(f"reads  {why}", file=sys.stderr)
        return 2
    misfits = sorted(fit(stages, binder))
    for m in misfits:
        print(f"{m.stage}  {m.kind}  {m.detail}")
    if misfits:
        return 1
    print(f"{target} fits {args.binder}: {len(stages)} stages")
    return 0
```

Check how the other commands call the console guard (`Grep "utf8_console" src/comment_review/commands`)
and match it exactly -- the encoding gate matches the call textually. Add `TOPOLOGY =
auto()` to `Command` in `__main__.py`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest -q tests/test_topology_command.py tests/gates/` then the three gates and
`uv run python scripts/check_shipped_syntax.py`.

- [ ] **Step 5: Commit the work**, then **Step 6: tick P31 and commit the tick**. P31's
verify also wants `tests/gates/test_skill_commands.py` to cover it, which happens the moment
SKILL.md names the command (Task 7): tick P31 after Task 7, and say so in this task's commit.

---

### Task 5: `collate --topology` reports a dispatch that came back empty

**Files:**
- Modify: `src/comment_review/flows/collate.py` -- a `_stage_problems` beside
  `_coverage_problems`, reported in the same list
- Modify: `src/comment_review/commands/collate.py` -- `--topology` optional
- Test: `tests/test_collate.py` (add a class) or `tests/test_collate_command.py`

**Interfaces:**
- Consumes: `desk.topology.read`, the `Stage` for `--stage`, `Problem(role, address, message)`
  as `_coverage_problems` builds it, `EditCopy.role`.
- Produces: `flows.collate._stage_problems(stage: Stage, edit_copies: list[EditCopy]) ->
  list[Problem]` -- one per role whose returned copies number fewer than the stage's
  dispatches for that role: `Problem(role, "", f"stage {stage.name}: {role} returned {got}
  of {want} dispatches")`. Read the current `collate(...)` signature and where
  `_coverage_problems`' list reaches the report before wiring; append to that same list.
  The command: `--topology T.toml` optional; when given, `read` it, find `--stage`'s
  `Stage` (exit 2 by name if absent, as Task 1 does), and pass it in.

- [ ] **Step 1: Write the failing test** -- through `run_command` over `commands/collate`,
  driving Task 1's `distribute --stage` for a stage with two `block-context` dispatches,
  handing collate only the first copy, and asserting the report carries
  `stage 4c: block-context returned 1 of 2 dispatches` in its coverage list and that the
  exit code is the one `_coverage_problems` already uses for a short copy (read
  `commands/collate.py` for it; `Process: #63`). A second case: both copies returned, no
  such line.
- [ ] **Step 2: Run to verify it fails** (`--topology` unrecognized).
- [ ] **Step 3: Implement** `_stage_problems` and the flag, threading the optional `Stage`
  through `collate`'s flow signature as `stage: Stage | None = None`.
- [ ] **Step 4: Run** `tests/test_collate.py tests/test_collate_command.py` (whichever
  exist) and the gates.
- [ ] **Step 5: Commit the work**, then **Step 6: tick P26 and commit the tick**.

---

### Task 6: The fan-out fixture runs on any tree, both branches mechanical

**Files:**
- Modify: `tests/fixtures/topologies/4a-then-4c.toml` (its header comment only -- the
  globs stay, they are the format's own example from the spec)
- Test: `tests/test_staged_chain.py` (create)

**Interfaces:** consumes Tasks 1-4's commands only.

- [ ] **Step 1: Write the test**

```python
"""`staged-chain-untested` T1 and P33: the committed fan-out fixture on a tree it was not written for.

! BOTH BRANCHES OF P33 ARE MECHANICAL NOW. The fixture's globs name this repo's own
layout, so on a scratch tree `topology --verify` refuses it and NAMES THE GLOBS --
that is the "state why it is not" branch, said by the system rather than by a
sentence here. And `topology --build` writes the same shape for the scratch tree,
which `distribute --stage` then drives -- the "drives a scratch tree of four files"
branch, on a topology built for it.
"""

from pathlib import Path

from conftest import ROOT, SAMPLE, run_command

from comment_review.commands import distribute as distribute_command
from comment_review.commands import gather as gather_command
from comment_review.commands import topology as topology_command

FIXTURE = ROOT / "tests" / "fixtures" / "topologies" / "4a-then-4c.toml"


def _four(tmp_path, monkeypatch, capsys) -> Path:
    for n in "abcd":
        (tmp_path / f"{n}.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = tmp_path / "binder.json"
    code, _ = run_command(monkeypatch, capsys, gather_command, "--repo", str(tmp_path), "--out", str(binder), *[f"{n}.py" for n in "abcd"])
    assert code == 0
    return binder


def test_the_committed_fixture_is_refused_on_a_scratch_tree_by_its_globs(tmp_path, monkeypatch, capsys):
    binder = _four(tmp_path, monkeypatch, capsys)
    code, printed = run_command(monkeypatch, capsys, topology_command, "--verify", str(FIXTURE), "--binder", str(binder))
    assert code == 1
    assert "src/comment_review/reading/*.py" in printed and "src/comment_review/binder/*.py" in printed


def test_the_same_shape_built_for_the_scratch_tree_drives_it(tmp_path, monkeypatch, capsys):
    binder = _four(tmp_path, monkeypatch, capsys)
    t = tmp_path / "t.toml"
    code, printed = run_command(
        monkeypatch, capsys, topology_command,
        "--build", "--binder", str(binder), "--out", str(t),
        "--stage", "4a=ownership-context",
        "--stage", "4c=block-context/2,function-context,module-context",
    )
    assert code == 0, printed
    out = tmp_path / "copies"
    code, printed = run_command(
        monkeypatch, capsys, distribute_command,
        "--topology", str(t), "--stage", "4c", "--binder", str(binder), "--out-dir", str(out),
    )
    assert code == 0, printed
    assert sorted(p.name for p in out.iterdir()) == [
        "4c_block-context_1.json", "4c_block-context_2.json",
        "4c_function-context_1.json", "4c_module-context_1.json",
    ]
```

- [ ] **Step 2: Run it** -- both should PASS on the first run if Tasks 1-4 are correct;
  if the first does not, the `uncovered` detail does not carry the stage's globs verbatim
  and Task 2's `fit` is what to fix.
- [ ] **Step 3: Update the fixture's header comment** to say it is the spec's example over
  this repo's layout, that `tests/test_staged_chain.py` shows it refused elsewhere, and that
  `topology --build` is how a run gets one for its own tree. Prose only; no key changes.
- [ ] **Step 4: Commit the work**, then **Step 5: tick P33 and `staged-chain-untested` T1,
  commit the tick**.

---

### Task 7: SKILL.md verifies before it distributes

**Files:**
- Modify: `src/plugin/skills/comment-review/SKILL.md` -- stage 1 gains a numbered step
  after 1.7; stage 4's seeding command changes; the packet section is unchanged
- Test: `tests/gates/test_skill_commands.py` (existing; it reads SKILL.md against
  `COMMANDS` and each command's parser)

**Lane:** `agents`, and **Roy authorized this plan's executor to modify SKILL.md for this
task explicitly, 2026-09-06**: *"Add in the modifications to SKILL.md as explicit
authorization to modify this time."* The authorization is for the changes this task names
and no other file in the lane. The commands it names are one-for-one with what Tasks 1 and
4 built.

- [ ] **Step 1: Write the stage-1 step.** After 1.7, a `**1.8 Build the topology and prove
  it fits, before any page is read.**` paragraph with the two commands:

```bash
python <skill>/scripts/comment-review.py topology --build --binder <run-dir>/binder.json --out <run-dir>/topology.toml \
  --stage 4a=ownership-context --stage 4c=block-context/2,function-context,module-context
python <skill>/scripts/comment-review.py topology --verify <run-dir>/topology.toml --binder <run-dir>/binder.json
```

  and the rule in one sentence each: a run against an unverified topology is not a path
  these instructions offer; a bad configuration costs nothing only when it is caught here;
  `--verify` exits 1 and names the stage, the kind and the glob or page, and the fix is to
  the topology, never to the tree. Note that 1.8 needs the binder, so it runs after stage 2
  in time; say so and keep it under stage 1 because it is a determination.
- [ ] **Step 2: Change stage 4's seeding** from one `distribute --seed --role` per role to
  one `distribute --topology --stage` per stage, naming the files it writes
  (`<stage>_<role>_<n>.json`) as the EDIT COPY paths the packet carries, one packet per
  dispatch.
- [ ] **Step 3: Run the gate**: `uv run pytest -q tests/gates/test_skill_commands.py`.
  Expected: PASS for every command and flag this task named; the `--anchor` failure
  inherited from the agents branch is not this task's. Then the vocabulary gate:
  `uv run python scripts/check_vocabulary.py`.
- [ ] **Step 4: Commit the work**, then **Step 5: tick P32 and P31, commit the tick, and
  run `plan refresh`**.

---

## Self-review, done while writing

- **Spec coverage.** Section 2's format: read by `read` (exists). Its two guards: `partition`
  (Task 2). `reads` barrier: `read` (exists), reported by the command (Task 4). Fan-out has a
  caller (Task 1). `carries`: format only, untouched, as the spec says.
- **Placeholders.** Task 5's steps are described rather than shown because `collate`'s flow
  signature and report path have to be read first; the executor reads
  `flows/collate.py::collate` and `commands/collate.py::main` before writing, and the
  `Problem` shape is quoted from `_coverage_problems`. Task 4's test imports a helper it
  does not need; use Task 1's tree-writing pattern.
- **Types.** `Misfit`, `fit`, `compose`, `Directive`, `partition` are named identically in
  Tasks 2, 3, 4 and 6. `fan`'s signature is unchanged.
