"""Inputs the revise tests need. ! INPUTS ONLY -- no helper here decides what
a test should expect. `decision-log.md Vocabulary: #23`.

! WRITTEN IN TASK 3, STEP 0 -- moved here from Task 8 because Task 3's own test
is the first to call `binder_of`. Only what Task 3 needs is written; later
tasks extend this file as they need more.

! `a_small_real_tree`, `a_docket_over` and `a_docket_whose_claim_is_not_in_the_page`
were added in Task 8, for `tests/test_revise.py`. Task 9's own test
(`tests/test_revise_addresses.py`) reuses `a_docket_over` rather than a second
copy -- `decision-log.md Vocabulary: #23` is the rule for why it lives here
and not beside either test module.

! `a_docket_that_rewrites` and `the_row_for` were added in Task 10, for
`tests/test_stage_root.py`.

! `a_master_proof`, `a_correct`, `a_move`, `a_clean`, `a_query` and `an_add`
were added in Task 9, for `tests/test_reconcile.py` -- Tasks 9 through 12 all
share them. Every mark is built through `desk.mark.INSTRUCTIONS`, never as a
hand-typed literal, so a changed row breaks a helper loudly instead of
letting it drift.

! `a_binder_over`, `copies_over` and `a_correct_setting` were added in Task 10,
for `tests/test_collate.py`.
"""

import json
from pathlib import Path

from conftest import ROOT, cue, run_command

from comment_review.binder.binder import VERSION, Binder, bind
from comment_review.commands import collate as collate_command
from comment_review.commands import disposition as disposition_command
from comment_review.commands import turn as turn_command
from comment_review.desk.containers import EditCopy, MasterProof, Sheet
from comment_review.desk.mark import (
    ANCHOR_EXAMPLE,
    INSTRUCTIONS,
    Instruction,
    Mark,
    Shape,
)
from comment_review.desk.proof import master_proof_of
from comment_review.docket.docket import Docket
from comment_review.flows._collate import Collated, collate
from comment_review.flows.distribute import seed
from comment_review.flows.fill import fill
from comment_review.flows.page_for import page_of, source_of
from comment_review.flows.proof_io import load_proof, save_batch, save_proof
from comment_review.flows.turn import batch_for, proof_after

#: `src/comment_review/desk/` -- the source `a_small_real_tree` copies from.
#: Any package with a handful of ordinary Python files would do; this one was
#: picked because it is small and holds real comments in more than one series.
_DESK = Path(__file__).resolve().parents[1] / "src" / "comment_review" / "desk"

#: A real citation `a_correct`, `a_move`, `a_query` and `an_add` reuse for
#: `sources` -- `desk/marks/mark.py`'s own first line, read once at import
#: time. `desk/mark.py` moved to `desk/marks/mark.py` in T1 of
#: `docs/superpowers/plans/2026-09-14-the-middle-rebuilt.md`, taking its
#: comment paragraphs with it; the shim left behind is thirteen lines of
#: imports, with no filled `b` row for `a_docket_over` to find.
_MARK_PY_CITE = "src/comment_review/desk/marks/mark.py:1"
_MARK_PY_LINE_1 = (
    (_DESK / "marks" / "mark.py").read_text(encoding="utf-8").splitlines()[0]
)

#: The sentence `a_drop` and `a_correct` quote when a caller names none. It is
#: a PLACEHOLDER and belongs to no paragraph, which `_quoting_the_real_text`
#: substitutes away wherever a real base is in hand -- see its docstring for
#: what that measured.
_PLACEHOLDER_SENTENCE = "the paragraph's own claim"

#: !! THE ROOT `_MARK_PY_CITE` RESOLVES AGAINST, and the one a `collate` test
#: must pass. Source verification opens what a `cite` names, so a test handed
#: `tmp_path` reports EVERY built mark's citation as unresolvable -- and a test
#: asserting some OTHER finding would then pass on the wrong one. Measured
#: 2026-08-31 while wiring `P25`.
#:
#: ! IT IS `conftest.ROOT`, NOT A SECOND COMPUTATION OF IT. Both files sit
#: directly under `tests/`, so a fresh `parents[1]` here would agree by
#: coincidence and diverge silently if the anchor ever moved.
#: `tests/gates/test_vocabulary.py` already imports it this way.
REPO = ROOT


def pages_of(root: Path) -> list:
    """Every `.py` page under `root`, through the real reader."""
    pages = []
    for path in sorted(root.rglob("*.py")):
        source, why = source_of(path)
        if why:
            continue
        rel = str(path.relative_to(root))
        page, why = page_of(path, rel=rel, source=source)
        if page is not None:
            pages.append(page)
    return pages


def binder_of(root: Path, revise: int) -> Binder:
    return bind(pages_of(root), read_from={"root": str(root), "revise": revise})


def _deserialized(wire: dict) -> Binder:
    """A hand-written binder, through the boundary that reads a real one.

    !! THE WIRE STAYS HAND-WRITTEN AND THE CONTAINER IS DERIVED, since
    2026-08-31. This module's own rule is that a fixture built by the code
    it feeds can only agree with it -- so these helpers keep spelling the
    JSON, and `Binder.deserialize` is what turns it into what the middle
    carries. ! It also means a fixture omitting a required field FAILS
    HERE, where before `binder.read` admitted it: every row these helpers
    write gained `original_start` and `original_end` for exactly that
    reason.
    """
    got, problems = Binder.deserialize("a test binder", wire)
    assert got is not None, problems
    return got


def _a_docket(wire: dict) -> Docket:
    """A hand-written docket, through the boundary the write flow reads it at.

    ! SAME RULE AS `_deserialized` ABOVE, on the other format: the wire stays
    hand-written, and the container is derived. A helper that built a `Docket`
    directly would skip every rule `Docket.deserialize` enforces, so these
    fixtures could drift out of the shape a real docket must take without
    anything noticing.
    """
    got, problems = Docket.deserialize("a test docket", wire)
    assert got is not None, problems
    return got


def _row(cue: str, text: str) -> dict:
    """One hand-written binder row, complete.

    ! THE LINE NUMBERS ARE PRESENT AND ARBITRARY. Nothing these fixtures feed
    reads them -- the write path reloads the page from disk (`Process: #14`)
    -- but a page's own reader requires them, so a fixture that left them out
    would be asserting a binder shape no gather produces.
    """
    return {
        "cue": cue,
        "anchor": "",
        "original_start": 1,
        "original_end": 1,
        "raw_text": text,
    }


def a_small_real_tree(tmp_path: Path) -> Path:
    """A repo of a few real `.py` files, copied from `src/comment_review/desk/`.

    ! REAL SOURCE, NEVER A HAND-AUTHORED LITERAL -- `CLAUDE.md`'s ruling for
    this suite. `mark.py` keeps its own flat name in the written repo so a
    docket over "mark.py" names a file that is actually there, though its
    content is read from `desk/marks/mark.py` now that the move landed --
    the shim left at `desk/mark.py` carries no filled `b` row to pick. The
    other three are along so `test_revise.py`'s own case can show a page the
    docket does not name is missing from the revise, per `decision-log.md
    Process: #117`.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "mark.py").write_bytes((_DESK / "marks" / "mark.py").read_bytes())
    for name in ("stages.py", "collator.py", "__init__.py"):
        (repo / name).write_bytes((_DESK / name).read_bytes())
    return repo


def a_docket_over(repo: Path, names: list[str]) -> Docket:
    """A docket that replaces one real, filled `b`-series comment in each
    named file.

    ! THE CUE AND ITS ORIGINAL TEXT COME OFF THE REAL PAGE, through
    `binder_of`, never hand-written -- a `b` row is picked because its
    replacement needs no more than `#`, which every file here (`.py`) shares.
    The anchor is that row's own, which `binder_of` also read off the page.

    Args:
        repo: a checkout `binder_of` can read, e.g. from `a_small_real_tree`.
        names: file BASENAMES to alter one comment in each of.

    Returns:
        A deserialized `Docket`.

    Raises:
        AssertionError: a name has no filled `b` row to alter.
    """
    binder = binder_of(repo, 0)
    remaining = set(names)
    pages = []
    for page in binder.pages:
        if Path(page.path).name not in remaining:
            continue
        found = next(
            (
                row
                for row in page.paragraphs
                if cue(row).startswith("b") and row.raw_text.strip()
            ),
            None,
        )
        if found is None:
            continue
        pages.append(
            {
                "path": page.path,
                "sha": page.sha,
                "alterations": [
                    {
                        "cue": cue(found),
                        "text": "# revised by a_docket_over",
                        "anchor": found.anchor,
                    }
                ],
            }
        )
        remaining.discard(Path(page.path).name)
    if remaining:
        raise AssertionError(f"no filled 'b' row found for {sorted(remaining)}")
    return _a_docket({"pages": pages})


def a_docket_whose_claim_is_not_in_the_page(repo: Path, name: str) -> Docket:
    """A docket naming a cue no paragraph on the page holds -- a chain
    refusal, without asserting which step raises it.

    The page holds no anchor at that cue, so the alteration carries the anchor
    of the page's first carried place, and the cue is the one thing wrong
    with the docket.

    Args:
        repo: a checkout `binder_of` can read.
        name: the file basename to build the (unreachable) alteration over.

    Returns:
        A deserialized `Docket`.

    Raises:
        AssertionError: no page in `repo` has this basename.
    """
    binder = binder_of(repo, 0)
    for page in binder.pages:
        if Path(page.path).name == name:
            return _a_docket(
                {
                    "pages": [
                        {
                            "path": page.path,
                            "sha": page.sha,
                            "alterations": [
                                {
                                    "cue": "zzz9999",
                                    "text": "# never reaches the page",
                                    "anchor": page.paragraphs[0].anchor,
                                }
                            ],
                        }
                    ]
                }
            )
    raise AssertionError(f"no page named {name!r} in {repo}")


def a_docket_that_rewrites(repo: Path, name: str) -> Docket:
    """A docket in `a_docket_over`'s shape, rewriting exactly one file.

    ! DELEGATES TO `a_docket_over`, rather than re-deriving the selection --
    `test_stage_root.py`'s case only ever rewrites one file, and a single
    name reads more directly at the call site than a one-element list. Both
    build the alteration the same way, which is what lets `the_row_for`
    find it back by replaying the same rule.

    Args:
        repo: a checkout `binder_of` can read.
        name: the file basename to alter one comment in.

    Returns:
        A deserialized `Docket`.

    Raises:
        AssertionError: `name` has no filled `b` row to alter.
    """
    return a_docket_over(repo, [name])


def the_row_for(binder: Binder, name: str):
    """The row `a_docket_over` (or `a_docket_that_rewrites`) altered on
    `name`'s page -- found by replaying its own selection.

    ! A DOCKET CARRIES NO REFERENCE BACK TO THE ROW IT ALTERED, so the only
    way to find the row a caller means is to pick it by the rule the docket
    used to choose it: the first `b` row holding text. That rule survives a
    revise -- `assert_addresses_held` guarantees the address set, and so the
    cue order, is unchanged -- so the row is still first at the same
    position, only its text differs.

    Args:
        binder: as `binder_of` returns it -- the original's, or a revise's.
        name: the file basename to find the row on.

    Returns:
        The paragraph, as the binder carries it.

    Raises:
        AssertionError: no page named `name`, or no filled `b` row on it.
    """
    for page in binder.pages:
        if Path(page.path).name != name:
            continue
        for row in page.paragraphs:
            if cue(row).startswith("b") and row.raw_text.strip():
                return row
        raise AssertionError(f"no filled 'b' row on {name!r}")
    raise AssertionError(f"no page named {name!r} in binder")


def _synthetic_binder(addresses: list[str]) -> Binder:
    """A binder shaped only well enough for the real `seed()` to produce real
    sheets from -- one page per address's file half, one row per its cue half.

    ! `places()`, what this feeds, groups by whatever `address` a mark
    already carries and never resolves one against a binder or reads a page,
    so this needs no real page on disk -- only the shape `seed()` requires.

    !! BUT `read_from.root` MUST NAME A REAL DIRECTORY, and held the string
    `"tests/helpers.py"` until 2026-08-31 -- a FILE, chosen as a placeholder
    when nothing read it. `P25` gave it a reader: `flows.collate.collate`
    resolves every `sources` cite against this root, and `commands/collate.py`
    defaults to it. Against a file, every citation these helpers build fails to
    resolve, and five exit-code tests came back BROKEN for a reason that had
    nothing to do with what they assert. Nothing asserts on the old value.
    """
    by_path: dict[str, list[str]] = {}
    for address in addresses:
        path, _, cue = address.partition("@")
        by_path.setdefault(path, []).append(cue)
    return _deserialized(
        {
            "version": VERSION,
            "read_from": {"root": str(REPO), "revise": 0},
            "pages": [
                {
                    "path": path,
                    "sha": "0" * 40,
                    "rows": [_row(cue, "") for cue in cues],
                }
                for path, cues in by_path.items()
            ],
        }
    )


def a_binder_over(paragraphs: dict[str, str]) -> Binder:
    """A binder whose rows carry REAL paragraph text, keyed by address.

    ! WRITTEN IN TASK 10, for `tests/test_collate.py`. `_synthetic_binder`
    seeds every row with an empty `raw_text`, which is enough for `places()`
    -- it groups by address and reads no text -- and not enough for a compose,
    whose whole subject is the base.

    Args:
        paragraphs: `path@cue` -> the paragraph at that place.

    Returns:
        A binder in `bind`'s shape, one page per distinct path.
    """
    by_path: dict[str, list[tuple[str, str]]] = {}
    for address, text in paragraphs.items():
        path, _, cue = address.partition("@")
        by_path.setdefault(path, []).append((cue, text))
    return _deserialized(
        {
            "version": VERSION,
            "read_from": {"root": str(REPO), "revise": 0},
            "pages": [
                {
                    "path": path,
                    "sha": "0" * 40,
                    "rows": [_row(cue, text) for cue, text in rows],
                }
                for path, rows in by_path.items()
            ],
        }
    )


def a_real_binder_over(root: Path, paragraphs: dict[str, str]) -> Binder:
    """A binder over real pages whose `b` places hold `paragraphs`, by address.

    Each page is written into `root` as one line of code per `b` place up to
    the highest named, each named text directly above its line, and read
    back through `page_of`. The file `_MARK_PY_CITE` names is copied in
    beside it, so the citations the mark builders here write resolve against
    `root`. Only the written pages are bound, and `read_from.root` names
    `root`, so a command handed the binder alone reads its pages there.

    Args:
        root: the directory to write into, created if absent.
        paragraphs: `path@b<n>` -> comment lines, `n` at least 1, so every
            named place sits below a line of code.

    Returns:
        The binder over the written pages.

    Raises:
        AssertionError: a named place did not come back holding its text.
    """
    root.mkdir(parents=True, exist_ok=True)
    cited = root / _MARK_PY_CITE.rpartition(":")[0]
    cited.parent.mkdir(parents=True, exist_ok=True)
    cited.write_bytes((_DESK / "marks" / "mark.py").read_bytes())
    by_path: dict[str, dict[int, str]] = {}
    for address, text in paragraphs.items():
        path, _, place = address.partition("@")
        n = int(place.removeprefix("b"))
        assert place == f"b{n}" and n >= 1, address
        by_path.setdefault(path, {})[n] = text.rstrip("\n")
    pages = []
    for path, texts in by_path.items():
        lines: list[str] = []
        for n in range(max(texts) + 1):
            if n in texts:
                lines.append(texts[n])
            lines.append(f"v{n} = {n}")
        (root / path).write_text(
            "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
        )
        page, why = page_of(root / path, rel=path)
        assert page is not None, why
        pages.append(page)
    binder = bind(pages, read_from={"root": str(root), "revise": 0})
    held = {p.address: p.raw_text for p in binder.paragraphs}
    assert held == {a: t.rstrip("\n") for a, t in paragraphs.items()}, held
    return binder


def copies_over(binder: Binder, by_role: dict) -> list[dict]:
    """One real seeded `edit_copy` per role, each overlaid with that role's marks.

    ! WRITTEN IN TASK 10. `a_master_proof` builds its own synthetic binder per
    role; this seeds every role from ONE binder, which is what `collate` is
    handed and what the drift check measures against.

    Args:
        binder: the binder every copy is seeded from.
        by_role: role name -> {address: mark}.

    Returns:
        One `edit_copy` per role, in `by_role` order.
    """
    copies = []
    for role, marks_by_address in by_role.items():
        copy = seed(binder, role)
        for sheet in copy["sheets"]:
            for entry in sheet["marks"]:
                mark = marks_by_address.get(entry["address"])
                if mark is not None:
                    entry.update(_quoting_the_real_text(mark, entry))
        copies.append(copy)
    return copies


def _quoting_the_real_text(mark: dict, entry: dict) -> dict:
    """`mark`, with a PLACEHOLDER quoted sentence replaced by the seeded text.

    !! MEASURED 2026-08-31, WHEN `P25` GAVE THE CLAIM A READER. `a_correct`'s
    default sentence -- `"the paragraph's own claim"` -- is in no paragraph any
    helper builds, so **every mark built from that default carried a claim that
    was never true of its own base**. Nothing could see it: `desk.mark.parse`
    imports no binder and no page, so the sentence was unfalsifiable until
    `desk.collator.claim_verbatim_problems` ran in the flow.

    ! THE WHOLE PARAGRAPH IS A LEGITIMATE `claim.false`, not a dodge --
    `flows.collate._composition` sets exactly that when it synthesizes a
    `correct` over a base two roles both edited.

    ! ONLY THE PLACEHOLDER IS TOUCHED. A test that passes its own sentence --
    `a_correct_setting`, or `a_correct(addr, "a sentence that is not there")` --
    means that sentence and keeps it, which is what lets a verbatim failure
    still be written.

    !! THE KEY COMES FROM `quotes_original`, NOT FROM THE WORD `false`, and was
    keyed to `false` for one commit. `desk.collator.claim_verbatim_problems`
    reads `INSTRUCTIONS[mark.instruction].quotes_original` -- `claim.drop` for a
    `drop`, `claim.false` for a `correct`, `claim.from` for a `patch` -- and
    `a_drop` defaults to the SAME placeholder. Keyed to one row's field name,
    the fix covered `correct` and left the next `drop` driven through `collate`
    to reproduce the defect it was written to close.
    """
    claim = mark.get("claim")
    instruction = mark.get("instruction")
    row = INSTRUCTIONS.get(instruction) if instruction is not None else None
    key = row.quotes_original if row is not None else None
    if not key or not isinstance(claim, dict):
        return mark
    if claim.get(key) != _PLACEHOLDER_SENTENCE:
        return mark
    base = entry.get("raw_text")
    if not isinstance(base, str) or not base:
        return mark
    return {**mark, "claim": {**claim, key: base}}


def _without_sheet(copy: dict, path: str) -> dict:
    """`copy` with the sheet for `path` removed -- a role that skipped a page.

    ! A REMOVAL OVER A REAL SEEDED COPY, not a copy written with one sheet. The
    two are the same document, and only the removal proves it came from a
    binder that held both pages.
    """
    kept = [sheet for sheet in copy["sheets"] if sheet.get("path") != path]
    assert len(kept) < len(copy["sheets"]), f"{path} was not a sheet on this copy"
    return {**copy, "sheets": kept}


def _keeping_only(copy: dict, addresses: list[str]) -> dict:
    """`copy` with every mark outside `addresses` removed -- a role that
    answered for some of the slots it was handed and dropped the rest."""
    wanted = set(addresses)
    return {
        **copy,
        "sheets": [
            {
                **sheet,
                "marks": [m for m in sheet["marks"] if m.get("address") in wanted],
            }
            for sheet in copy["sheets"]
        ],
    }


def a_copy_missing_its_sheets(binder: Binder, role: str = "block-context") -> dict:
    """A real seeded copy with its `sheets` key REMOVED.

    ! A REMOVAL OVER `seed`, NOT A LITERAL. A hand-written `{"role": ...,
    "read_from": ...}` would also be asserting the shape of a well-formed copy,
    which is `seed`'s to state -- so the fixture and the code could drift apart
    and the test would go on passing.
    """
    copy = seed(binder, role)
    del copy["sheets"]
    return copy


def marks_of(sheet: Sheet) -> list[Mark]:
    """One sheet's marks, as the `Mark`s it holds.

    !! IT ASSERTED EACH ENTRY WAS A DICT UNTIL `P51`, because `Sheet.marks` was
    `tuple[object, ...]` and an entry that would not parse was carried so it
    could be refused by name. The parse sorts those into `Sheet.refused` now, so
    what is here is marks and the assertion has nothing left to catch.
    """
    return list(sheet.marks)


def entries_of(copy: EditCopy) -> list[Mark]:
    """Every mark on a copy, flattened, in sheet then mark order.

    ! IT REPLACES `[m for s in got.chief.sheets for m in s.marks]`, which stood
    at thirteen sites in `tests/test_collate.py` alone.
    """
    return [mark for sheet in copy.sheets for mark in marks_of(sheet)]


def returned(wire: dict, where: str = "copy") -> EditCopy:
    """One returned edit_copy, PARSED -- what the middle takes since `P42`.

    A test builds the wire dict a role hands back -- `flows.distribute.seed`,
    then whatever the case writes into a slot -- and this is the boundary
    `flows.collate.collate` runs it through before `problems_in`,
    `verify_report`, `drift_in`, `unruled` or `tally` sees it.

    ! IT ASSERTS THE PARSE SUCCEEDED, so a fixture that has quietly stopped
    being a well-formed copy fails HERE, naming the field, rather than as a
    surprising result from the function under test.
    """
    copy, why = EditCopy.deserialize(where, wire)
    assert copy is not None, why
    return copy


def a_master_proof(by_role: dict) -> MasterProof:
    """A `master_proof`, composed through the real `seed()` and `master_proof_of()`.

    Args:
        by_role: role name -> {address: mark}, one mark per place that role
            rules on, built by `a_correct`, `a_move`, `a_clean`, `a_query` or
            `an_add`.

    Returns:
        The `MasterProof` `desk.proof.master_proof_of` returns. One `edit_copy` per
        role, seeded for real over a synthetic binder sized to that role's own
        addresses, then each seeded entry overlaid with the caller's mark --
        the same `entry.update(...)` pattern `tests/test_collator.py` uses over
        a real one.

    ! IT RUNS THE REAL PARSE BETWEEN THE TWO, exactly as `flows.collate.collate`
    does since `P42`: `seed` writes the wire dict a role is handed, and
    `master_proof_of` takes the parsed `EditCopy`. A fixture that skipped the parse
    would hand `master_proof_of` a shape production cannot produce.
    """
    copies = []
    for role, marks_by_address in by_role.items():
        wire = seed(_synthetic_binder(list(marks_by_address)), role)
        for sheet in wire["sheets"]:
            for entry in sheet["marks"]:
                mark = marks_by_address.get(entry["address"])
                if mark is not None:
                    entry.update(mark)
        copy, why = EditCopy.deserialize(role, wire)
        assert copy is not None, why
        copies.append(copy)
    return master_proof_of("4c", copies)


def _mark(instruction: Instruction, address: str, claim: dict) -> dict:
    """One mark, its required fields read off `INSTRUCTIONS[instruction]` --
    never hand-typed, so a row changed under this helper breaks it loudly.

    Args:
        instruction: which of the seven.
        address: this mark's own `address`.
        claim: exactly the keys `INSTRUCTIONS[instruction].claim_all` names.

    Returns:
        A mark carrying `address`, `instruction`, `reason`, `claim`, and
        `sources` and `change` where the row owes them. ! `change` is RAW
        TEXT, per `docs/the-mark.md`.

    Raises:
        AssertionError: `claim` does not carry exactly the keys the row's
            `claim_all` demands.
    """
    spec = INSTRUCTIONS[instruction]
    if set(claim) != set(spec.claim_all):
        raise AssertionError(
            f"{instruction}: claim needs {sorted(spec.claim_all)}, got {sorted(claim)}"
        )
    mark: dict = {
        "address": address,
        "instruction": instruction,
        "reason": f"written for the reconcile test suite ({instruction})",
        "claim": claim,
    }
    if spec.owes_sources:
        mark["sources"] = [{"cite": _MARK_PY_CITE, "verbatim": _MARK_PY_LINE_1}]
    if spec.owes_change:
        mark["change"] = f"# set by the reconcile test suite ({instruction})"
    return mark


def a_correct_citing(address: str, cite: str) -> dict:
    """A `correct` whose one source cites `cite`.

    ! BUILT ON `a_correct`, not as a second builder for the same instruction --
    what varies is the citation, and everything else must stay whatever the
    row's own spec says it owes.
    """
    mark = a_correct(address)
    mark["sources"] = [{"cite": cite, "verbatim": _MARK_PY_LINE_1}]
    return mark


def a_clean(address: str) -> dict:
    """A `clean` mark -- the null mark. `INSTRUCTIONS[Instruction.CLEAN]` owes
    no `claim`, no `sources`, no `change`."""
    return _mark(Instruction.CLEAN, address, {})


def a_drop(address: str, sentence: str = _PLACEHOLDER_SENTENCE) -> dict:
    """A `drop` mark -- the one row `INSTRUCTIONS[...].may_empty` is True for,
    so an empty `change` on it is the edit rather than a missing one."""
    return _mark(Instruction.DROP, address, {"drop": sentence})


def a_correct(address: str, sentence: object = _PLACEHOLDER_SENTENCE) -> dict:
    """A `correct` mark -- `claim.false` is `sentence`, `claim.true` the fix,
    the two keys `INSTRUCTIONS[Instruction.CORRECT]` demands.

    ! `sentence` IS COERCED TO A STRING, so a caller may pass a bare
    discriminator (`sentence=0`, `sentence=2`) to say only *a different
    sentence from the other mark's*. `desk.mark.parse` requires a filled
    STRING, and `0` is neither.
    """
    return _mark(
        Instruction.CORRECT,
        address,
        {"false": str(sentence), "true": f"corrected: {sentence}"},
    )


def a_correct_setting(address: str, sentence: object, change: str) -> dict:
    """A `correct` whose `change` is exactly `change`.

    ! WRITTEN IN TASK 10. `a_correct` writes a fixed `change` string, which
    two roles would then propose identically at every place -- so a compose
    case cannot be built from it.
    """
    mark = a_correct(address, sentence)
    mark["change"] = change
    return mark


def a_move(origin: str, destination: str) -> dict:
    """A `move` mark -- `origin` as its own `address`, `destination` as
    `claim.to`. `collator.places()` must group it into both."""
    return _mark(Instruction.MOVE, origin, {"from": origin, "to": destination})


def a_query(address: str, shape: Shape = Shape.UNABLE_TO_DETERMINE) -> dict:
    """A `query` mark in one of the three `Shape`s -- default
    `unable-to-determine`, the one a collate step can act on."""
    return _mark(
        Instruction.QUERY,
        address,
        {
            "shape": shape,
            "attempted": "checked the paragraph against the code it sits with",
            "settles": "another role's ruling on the same place",
        },
    )


def an_add(address: str) -> dict:
    """An `add` mark -- `claim.anchor` NAMED IN BACKTICKS, using
    `desk.mark.ANCHOR_EXAMPLE` rather than a hand-typed name."""
    return _mark(
        Instruction.ADD,
        address,
        {
            "missing": "a sentence stating what the code does here",
            "anchor": ANCHOR_EXAMPLE,
        },
    )


#: A real page whose `b3`, the gap above `w = 4`, holds no prose -- so the
#: binder does not carry it and no seeded copy has a slot there.
GAPPED_PAGE = "x = 1\n# one\n# two\n# three\ny = 2\nz = 3\nw = 4\n"
EMPTY_PLACE = "m.py@b3"
ADDED_TEXT = "# w is 4 because the fixture says so\n"


def an_add_at_an_empty_place(root: Path) -> tuple[Binder, Collated]:
    """A fold over one `add` at an empty place on a real page, as `mark` leaves it.

    `GAPPED_PAGE` is written to `root/m.py`. block-context adds at
    `EMPTY_PLACE`, which the binder does not carry, and both roles clean the
    one place it does. `fill` places the add, so only block-context's copy
    holds a slot there.

    Returns:
        `(binder, the fold)` -- the fold carrying `EMPTY_PLACE` as its one
        re-read, sent to both roles.
    """
    (root / "m.py").write_text(GAPPED_PAGE, encoding="utf-8")
    binder = binder_of(root, 0)
    assert EMPTY_PLACE not in {p.address for p in binder.paragraphs}
    copies = [seed(binder, role) for role in ("block-context", "function-context")]
    for copy in copies:
        for paragraph in binder.paragraphs:
            clean = {"address": paragraph.address, "instruction": "clean"}
            _, why = fill(copy, clean, root)
            assert why == []
    added = {
        "address": EMPTY_PLACE,
        "instruction": "add",
        "claim": {"missing": "why w is 4", "anchor": "`w`"},
        "reason": "the constant is explained nowhere",
        "sources": [{"cite": "m.py:7"}],
        "change": ADDED_TEXT,
    }
    _, why = fill(copies[0], added, root)
    assert why == []
    got = collate("4c", copies, binder, root=root)
    assert [e["address"] for e in got.rereads] == [EMPTY_PLACE]
    assert got.rereads[0]["roles"] == ["block-context", "function-context"]
    return binder, got


# -- the hand driver: a review from the console, over `tmp_path` ----------------
#
# !! THROUGH `conftest.run_command`, so every flag is parsed by the command's
# own argparse -- the one thing that catches a flag the body reads under a
# different name. `test_turn_command` and `test_disposition_command` share it (T26 of
# `TODO/no-command-for-the-middle.md`); before this each set `sys.argv` by hand
# and one imported the other's underscored helpers.
#
# The files land in `tmp_path` under fixed names: `binder.json`, `copy<i>.json`,
# `proof<n>.json` for the proof after turn n (0 is the first fold),
# `batch<n>.json` for the batch turn n reads, `answers<n>_<role>.json`.

BASE = "# one\n# two\n# three\n"
TWO = "# one\n# TWO\n# three\n"
DOS = "# one\n# dos\n# three\n"
HAND_ROLES = ("block-context", "function-context")


def contested(address: str, sentence="two", one=TWO, other=DOS) -> dict:
    """Two roles correcting the same sentence to different texts."""
    return {
        "block-context": {address: a_correct_setting(address, sentence, one)},
        "function-context": {address: a_correct_setting(address, sentence, other)},
    }


def agreed(address: str) -> dict:
    """Two roles correcting the same sentence to the same text -- a stet at once."""
    return {
        role: {address: a_correct_setting(address, "two", DOS)} for role in HAND_ROLES
    }


def merged(*by_roles: dict) -> dict:
    """Several role -> {address: mark} maps as one."""
    out: dict = {}
    for by_role in by_roles:
        for role, marks in by_role.items():
            out.setdefault(role, {}).update(marks)
    return out


def deal(
    tmp_path, monkeypatch, capsys, by_role: dict, texts: dict | None = None
) -> int:
    """`collate` over `by_role`: binder.json, proof0.json, batch1.json, chief0.json.

    The binder is over real pages written to `tmp_path / "repo"`, which the
    commands read as its root.

    !! THE COMMAND DEALS THE HAND AND THE OLD FOLD WRITES WHAT THE TURN READS,
    which is two folds over one set of copies and is deliberately temporary.
    `collate` folds through the Unit of Work since T3 of
    `docs/superpowers/plans/2026-09-14-the-middle-rebuilt.md`, so the proof it
    writes carries decided PLACES and its batch carries a place's sides --
    neither of which `flows.turn.run_turn` reads. `turn` and `disposition`
    still fold through `flows._collate`, so the hand they are dealt is that
    fold's, and this writes `proof0.json` and `batch1.json` from it. T4 of
    that plan moves both commands onto the bus; the second half of this
    function goes with them.

    ! THE EXIT CODE IS THE COMMAND'S, not the old fold's. It is what a caller
    of `collate` reads, and every case here contests a place, where the two
    folds agree on the code.
    """
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, texts or {"m.py@b1": BASE})
    copies = copies_over(binder, by_role)
    (tmp_path / "binder.json").write_text(
        json.dumps(binder.serialize()), encoding="utf-8"
    )
    argv = [
        "--stage",
        "4c",
        "--binder",
        str(tmp_path / "binder.json"),
        "--out",
        str(tmp_path / "chief0.json"),
    ]
    for i, copy in enumerate(copies):
        path = tmp_path / f"copy{i}.json"
        path.write_text(json.dumps(copy), encoding="utf-8")
        argv += ["--edit-copy", str(path)]
    code, _out = run_command(monkeypatch, capsys, collate_command, *argv)

    got = collate("4c", copies, binder, root)
    if got.proof is not None:
        save_proof(tmp_path / "proof0.json", proof_after(got, root=root))
    if got.escalations or got.rereads:
        save_batch(tmp_path / "batch1.json", batch_for(got))
    return code


def answer(tmp_path, n: int, role: str, address: str, **fields) -> str:
    """This role's sent slot at `address` on batch<n>, with `fields` laid over.

    Returns:
        The `ROLE=PATH` spec `turn --answers` takes.
    """
    batch = json.loads((tmp_path / f"batch{n}.json").read_text(encoding="utf-8"))
    slot = next(s for s in batch[role] if s["address"] == address)
    path = tmp_path / f"answers{n}_{role}.json"
    path.write_text(json.dumps([{**slot, **fields}]), encoding="utf-8")
    return f"{role}={path}"


def turn(
    tmp_path, monkeypatch, capsys, n: int, *answers: str, proof: str = ""
) -> tuple[int, str]:
    """`turn` n: proof<n-1> and batch<n> in, proof<n> and batch<n+1> out."""
    argv = [
        "--proof",
        proof or str(tmp_path / f"proof{n - 1}.json"),
        "--binder",
        str(tmp_path / "binder.json"),
        "--sent",
        str(tmp_path / f"batch{n}.json"),
        "--proof-out",
        str(tmp_path / f"proof{n}.json"),
        "--batch-out",
        str(tmp_path / f"batch{n + 1}.json"),
    ]
    for one in answers:
        argv += ["--answers", one]
    return run_command(monkeypatch, capsys, turn_command, *argv)


def held_open(
    tmp_path, monkeypatch, capsys, extra: dict | None = None, texts=None
) -> None:
    """Deal a contested place and hold it through one turn: proof1.json."""
    by_role = contested("m.py@b1")
    if extra:
        by_role = merged(by_role, extra)
    deal(tmp_path, monkeypatch, capsys, by_role, texts)
    code, out = turn(
        tmp_path,
        monkeypatch,
        capsys,
        1,
        answer(tmp_path, 1, "block-context", "m.py@b1", instruction="hold", reason="a"),
        answer(
            tmp_path, 1, "function-context", "m.py@b1", instruction="hold", reason="b"
        ),
    )
    assert code == collate_command.ESCALATIONS, out


def disposition(
    tmp_path, monkeypatch, capsys, rulings: object, proof: str = "proof1.json"
) -> tuple[int, str]:
    """`disposition` over `proof`: chief.json and final.json out."""
    (tmp_path / "dispositions.json").write_text(json.dumps(rulings), encoding="utf-8")
    return run_command(
        monkeypatch,
        capsys,
        disposition_command,
        "--proof",
        str(tmp_path / proof),
        "--binder",
        str(tmp_path / "binder.json"),
        "--dispositions",
        str(tmp_path / "dispositions.json"),
        "--out",
        str(tmp_path / "chief.json"),
        "--proof-out",
        str(tmp_path / "final.json"),
    )


def proof_at(tmp_path, n: int) -> MasterProof:
    """The proof after turn n, read back through the loader."""
    got, why = load_proof(tmp_path / f"proof{n}.json")
    assert got is not None, why
    return got


def the_chief(tmp_path) -> EditCopy:
    """`disposition`'s chief.json, as the ordinary edit_copy it must be."""
    loaded = json.loads((tmp_path / "chief.json").read_text(encoding="utf-8"))
    return returned(loaded, "chief")
