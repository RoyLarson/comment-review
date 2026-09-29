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

! `a_master_proof`, `returned_copies`, `a_correct`, `a_move`, `a_clean`,
`a_query` and `an_add` serve the reconciliation cases, and several files share
them. Every mark is built through `desk.marks.table.INSTRUCTIONS`, never as a
hand-typed literal, so a changed row breaks a helper loudly instead of
letting it drift.

! `a_binder_over`, `copies_over` and `a_correct_setting` were added in Task 10,
for the fold's own cases; `tests/test_bus.py` and `tests/test_verify.py` are
what drive them now.
"""

import json
from pathlib import Path
from typing import Any

from conftest import ROOT, cue, run_command

from comment_review.binder.binder import VERSION, Binder, bind
from comment_review.commands import collate as collate_command
from comment_review.commands import disposition as disposition_command
from comment_review.commands import turn as turn_command
from comment_review.desk.marks.table import INSTRUCTIONS
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.mark import (
    ANCHOR_EXAMPLE,
    AddMark,
    CleanMark,
    CorrectMark,
    DropMark,
    Instruction,
    Mark,
    MoveMark,
    PatchMark,
    QueryMark,
    Shape,
    mark_type,
)
from comment_review.desk.proof.master_proof import MasterProof
from comment_review.desk.proof.sheet import Sheet
from comment_review.docket.docket import Docket
from comment_review.flows.bus import CopiesReturned, handle
from comment_review.flows.distribute import seed
from comment_review.flows.fill import fill
from comment_review.flows.page_for import page_of, source_of
from comment_review.flows.proof_io import load_proof

#: `src/comment_review/desk/` -- the source `a_small_real_tree` copies from.
#: Any package with a handful of ordinary Python files would do; this one was
#: picked because it is small and holds real comments in more than one series.
_DESK = Path(__file__).resolve().parents[1] / "src" / "comment_review" / "desk"

#: A real citation `a_correct`, `a_move`, `a_query` and `an_add` reuse for
#: `sources` -- `desk/proof/mark.py`'s own first line, read once at import
#: time. The file is the mark's own module and holds filled `b` rows for
#: `a_docket_over` to find.
_MARK_PY_CITE = "src/comment_review/desk/proof/mark.py:1"
_MARK_PY_LINE_1 = (
    (_DESK / "proof" / "mark.py").read_text(encoding="utf-8").splitlines()[0]
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
    content is read from `desk/proof/mark.py`, where `Mark` lives. The
    other three are along so `test_revise.py`'s own case can show a page the
    docket does not name is missing from the revise, per `decision-log.md
    Process: #117`.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "mark.py").write_bytes((_DESK / "proof" / "mark.py").read_bytes())
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
    when nothing read it. `P25` gave it a reader: the fold
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

    ! WRITTEN IN TASK 10, for the fold's own cases; `tests/test_bus.py` and
    `tests/test_collate_command.py` are what drive it now. `_synthetic_binder`
    seeds every row with an empty `raw_text`, which is enough to group marks
    by address -- that reads no text -- and not enough for a compose, whose
    whole subject is the base.

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
    cited.write_bytes((_DESK / "proof" / "mark.py").read_bytes())
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

    ! WRITTEN IN TASK 10. `returned_copies` builds its own synthetic binder per
    role; this seeds every role from ONE binder, which is what `collate` is
    handed.

    Args:
        binder: the binder every copy is seeded from.
        by_role: role name -> {address: mark}.

    Returns:
        One `edit_copy` per role, in `by_role` order.
    """
    copies = []
    for role, marks_by_address in by_role.items():
        copy = seed(binder, role)
        _overlaid(copy, marks_by_address)
        copies.append(copy)
    return copies


def _overlaid(copy: dict, marks_by_address: dict) -> dict:
    """`copy` with each mark laid over the seeded slot at its own address.

    ! ONLY A SLOT THE SEED ALREADY WROTE. A mark at a place the binder does
    not carry has none to lay over and is silently dropped here; `deal`'s
    `placed` is the way to put one on a copy, since creating a slot from the
    page is `flows.fill`'s.
    """
    for sheet in copy["sheets"]:
        for entry in sheet["marks"]:
            mark = marks_by_address.get(entry["address"])
            if mark is not None:
                entry.update(_quoting_the_real_text(mark, entry))
    return copy


def _quoting_the_real_text(mark: dict, entry: dict) -> dict:
    """`mark`, with a PLACEHOLDER quoted sentence replaced by the seeded text.

    !! MEASURED 2026-08-31, WHEN `P25` GAVE THE CLAIM A READER. `a_correct`'s
    default sentence -- `"the paragraph's own claim"` -- is in no paragraph any
    helper builds, so **every mark built from that default carried a claim that
    was never true of its own base**. Nothing could see it: a mark's own read
    imports no binder and no page, so the sentence was unfalsifiable until
    `desk.collator.claim_verbatim_problems` ran in the flow.

    ! THE WHOLE PARAGRAPH IS A LEGITIMATE `claim.false`, not a dodge --
    the composing pass sets exactly that when it synthesizes a
    `correct` over a base two roles both edited.

    ! ONLY THE PLACEHOLDER IS TOUCHED. A test that passes its own sentence --
    `a_correct_setting`, or `a_correct(addr, "a sentence that is not there")` --
    means that sentence and keeps it, which is what lets a verbatim failure
    still be written.

    !! THE KEY COMES FROM `quotes_original`, NOT FROM THE WORD `false`, and was
    keyed to `false` for one commit. `desk.collator.claim_verbatim_problems`
    reads the type's `quotes_original` -- `claim.drop` for a
    `drop`, `claim.false` for a `correct`, `claim.from` for a `patch` -- and
    `a_drop` defaults to the SAME placeholder. Keyed to one row's field name,
    the fix covered `correct` and left the next `drop` driven through `collate`
    to reproduce the defect it was written to close.
    """
    claim = mark.get("claim")
    instruction = mark.get("instruction")
    named = instruction in INSTRUCTIONS
    key = mark_type(Instruction(instruction)).quotes_original if named else None
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


def changes_of(marks: list[Mark]) -> list[str | None]:
    """Each mark's `change` as its wire entry carries it -- None for a type
    that carries none."""
    return [mark.serialize().get("change") for mark in marks]


def entries_of(copy: EditCopy) -> list[Mark]:
    """Every mark on a copy, flattened, in sheet then mark order.

    ! IT REPLACES `[m for s in copy.sheets for m in s.marks]`, which stood at
    thirteen sites in the old fold's test file alone.
    """
    return [mark for sheet in copy.sheets for mark in marks_of(sheet)]


def returned(wire: dict, where: str = "copy") -> EditCopy:
    """One returned edit_copy, PARSED -- what the middle takes since `P42`.

    A test builds the wire dict a role hands back -- `flows.distribute.seed`,
    then whatever the case writes into a slot -- and this is the boundary
    the fold runs it through before the per-mark checks,
    `verify_report`, `unruled` or `tally` sees it.

    ! IT ASSERTS THE PARSE SUCCEEDED, so a fixture that has quietly stopped
    being a well-formed copy fails HERE, naming the field, rather than as a
    surprising result from the function under test.
    """
    copy, why = EditCopy.deserialize(where, wire)
    assert copy is not None, why
    return copy


def a_master_proof(root: Path, by_role: dict) -> MasterProof:
    """A `master_proof`, as the bus builds one from a stage's returned copies.

    Every place `by_role` names is written under `root` holding `BASE`
    (`a_real_binder_over`); each role's copy is seeded from that one binder and
    overlaid with its marks (`copies_over`), parsed (`returned`), and handed to
    `flows.bus.handle` as one `CopiesReturned` -- the message
    `commands/collate.py` sends. What comes back is the proof the committed
    fold built.

    Args:
        root: the directory the pages are written into.
        by_role: role name -> {`path@b<n>`: mark}, one mark per place that role
            rules on. An empty map is a stage with no copies.

    Returns:
        `Result.proof` from the committed fold.

    Raises:
        AssertionError: the bus rolled the stage back, naming its events.
    """
    paragraphs = {address: BASE for marks in by_role.values() for address in marks}
    binder = a_real_binder_over(root, paragraphs or {"m.py@b1": BASE})
    copies = [returned(wire, wire["role"]) for wire in copies_over(binder, by_role)]
    out, result = handle(CopiesReturned("4c", copies, binder, root))
    assert result is not None, out
    return result.proof


def returned_copies(by_role: dict) -> list[EditCopy]:
    """One parsed `edit_copy` per role, for a case that folds the copies itself.

    Each role's copy is seeded over a synthetic binder sized to that role's own
    addresses, each seeded entry updated with the caller's mark as written, and
    the result parsed through `EditCopy.deserialize`. No page is read and
    nothing is checked against one, so a case may hand in a mark the bus would
    refuse and ask what the parse or the fold makes of it.

    Args:
        by_role: role name -> {address: mark}, built by `a_correct`, `a_move`,
            `a_clean`, `a_query` or `an_add`.

    Returns:
        The copies, in `by_role` order.
    """
    copies = []
    for role, marks_by_address in by_role.items():
        wire = seed(_synthetic_binder(list(marks_by_address)), role)
        for sheet in wire["sheets"]:
            for entry in sheet["marks"]:
                mark = marks_by_address.get(entry["address"])
                if mark is not None:
                    entry.update(mark)
        copies.append(returned(wire, role))
    return copies


def a_typed_mark(
    instruction: Instruction,
    *,
    address: str = "m.py@b1",
    anchor: str = "x = 1",
    raw_text: str = "",
    claim: dict | None = None,
    reason: str = "r",
    sources: tuple[object, ...] = (),
    change: str = "",
) -> Mark:
    """A mark of `instruction`'s type, BUILT rather than read.

    For a case that hands a table verb or a fold a mark directly, the way the
    split and the chief build one. Nothing is checked: a claim key left out is
    "", and a `query` with no shape is `unable-to-determine`. A case asking
    what the read refuses goes through `read_mark` instead.
    """
    got = dict(claim or {})
    common: dict[str, Any] = {
        "address": address,
        "anchor": anchor,
        "raw_text": raw_text,
        "reason": reason,
        "sources": sources,
    }
    match instruction:
        case Instruction.CLEAN:
            return CleanMark(**common)
        case Instruction.QUERY:
            return QueryMark(
                **common,
                shape=Shape(got.get("shape", Shape.UNABLE_TO_DETERMINE)),
                attempted=got.get("attempted", ""),
                settles=got.get("settles", ""),
            )
        case Instruction.DROP:
            return DropMark(**common, change=change, drop=got.get("drop", ""))
        case Instruction.CORRECT:
            return CorrectMark(
                **common,
                change=change,
                false=got.get("false", ""),
                true=got.get("true", ""),
            )
        case Instruction.PATCH:
            return PatchMark(
                **common, change=change, from_=got.get("from", ""), to=got.get("to", "")
            )
        case Instruction.ADD:
            return AddMark(
                **common,
                change=change,
                missing=got.get("missing", ""),
                named_anchor=got.get("anchor", ""),
            )
        case Instruction.MOVE:
            return MoveMark(
                **common, change=change, from_=got.get("from", ""), to=got.get("to", "")
            )


def _mark(instruction: Instruction, address: str, claim: dict) -> dict:
    """One mark, its required fields read off the instruction's type --
    never hand-typed, so a type changed under this helper breaks it loudly.

    Args:
        instruction: which of the seven.
        address: this mark's own `address`.
        claim: exactly the keys the type's `claim_all` names.

    Returns:
        A mark carrying `address`, `instruction`, `reason`, `claim`, and
        `sources` and `change` where the row owes them. ! `change` is RAW
        TEXT, per `docs/the-mark.md`.

    Raises:
        AssertionError: `claim` does not carry exactly the keys the row's
            `claim_all` demands.
    """
    spec = mark_type(instruction)
    if set(claim) != set(spec.claim_all):
        raise AssertionError(
            f"{instruction}: claim needs {sorted(spec.claim_all)}, got {sorted(claim)}"
        )
    mark: dict = {
        "address": address,
        "instruction": instruction,
        "reason": f"written for the mark helpers ({instruction})",
        "claim": claim,
    }
    if spec.owes_sources:
        mark["sources"] = [{"cite": _MARK_PY_CITE, "verbatim": _MARK_PY_LINE_1}]
    if spec.owes_change:
        mark["change"] = f"# set by the mark helpers ({instruction})"
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
    """A `drop` mark -- the one type `may_empty` is True for,
    so an empty `change` on it is the edit rather than a missing one."""
    return _mark(Instruction.DROP, address, {"drop": sentence})


def a_correct(address: str, sentence: object = _PLACEHOLDER_SENTENCE) -> dict:
    """A `correct` mark -- `claim.false` is `sentence`, `claim.true` the fix,
    the two keys `INSTRUCTIONS[Instruction.CORRECT]` demands.

    ! `sentence` IS COERCED TO A STRING, so a caller may pass a bare
    discriminator (`sentence=0`, `sentence=2`) to say only *a different
    sentence from the other mark's*. A mark's read requires a filled STRING,
    and `0` is neither.
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


def a_patch(address: str, was: str, now: str, change: str) -> dict:
    """A `patch` mark: `claim.from` is `was`, `claim.to` is `now`.

    `change` is the whole paragraph as it will read, the way every row that
    owes one carries it.

    The row owes no sources, which is what makes it the input
    `decision-log.md Process: #184` was ruled on: a text decided over patches
    alone has none behind it, and a mark synthesized to carry that text is one
    the parse refuses.
    """
    mark = _mark(Instruction.PATCH, address, {"from": was, "to": now})
    mark["change"] = change
    return mark


def a_move(origin: str, destination: str, change: str = "", reads: str = "") -> dict:
    """A `move` mark -- `origin` as its own `address`, `destination` as
    `claim.to`. `desk.marks.table.Row.places` files it at both.

    Args:
        origin: the mark's own address.
        destination: `claim.to`.
        change: the snippet the move subtracts from the origin's paragraph
            (`decision-log.md Process: #172`). A caller whose fold reads the
            real page passes the text that is there; the default belongs to
            no paragraph, which is what `_quoting_the_real_text` does for a
            quoted clause.
        reads: the destination paragraph as it will read, with the snippet in
            (`Process: #175`). Defaults to the snippet alone, which is what a
            move onto an empty place reads with.

    Returns:
        The mark, its `raw_text` the destination's text rather than the
        origin's -- the one row besides `add` where the role writes it.
    """
    mark = _mark(Instruction.MOVE, origin, {"from": origin, "to": destination})
    if change:
        mark["change"] = change
    mark["raw_text"] = reads or mark["change"]
    return mark


#: The kinds `a_misspelled_address` builds.
MISSPELLINGS = ("case", "bare-cue", "padded")


def a_misspelled_address(kind: str) -> tuple[dict, dict, list, str]:
    """One copy whose only fault is an address spelled otherwise than printed.

    `case` is a move onto its own paragraph with the path's case changed,
    which a file system that ignores case opens as the same page. `bare-cue`
    is a `clean` added at a cue with no path. `padded` is a move whose
    destination carries a trailing space.

    Args:
        kind: one of `MISSPELLINGS`.

    Returns:
        `(the page's paragraphs by address, block-context's marks by seeded
        address, entries appended to its sheet, a phrase the refusal holds)`,
        for `a_real_binder_over` and `copies_over`.
    """
    places = {"m.py@b1": BASE, "m.py@b5": "# dest para.\n"}
    marks = {address: a_clean(address) for address in places}
    appended: list = []
    if kind == "case":
        marks["m.py@b1"] = a_move("m.py@b1", "M.py@b1", change="# two", reads=BASE)
        named = "`claim.to` is this mark's own `address`"
    elif kind == "bare-cue":
        appended.append(a_clean("b1"))
        named = "b1: resolves against no page -- it is not a `path@cue` address"
    else:
        assert kind == "padded", kind
        marks["m.py@b1"] = a_move(
            "m.py@b1", "m.py@b5 ", change="# two", reads="# dest para. two"
        )
        named = "it is spelled otherwise than the page prints it, 'm.py@b5'"
    return places, marks, appended, named


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


def an_add(address: str, reads: str | None = None) -> dict:
    """An `add` mark -- `claim.anchor` NAMED IN BACKTICKS, using
    `desk.marks.rules.ANCHOR_EXAMPLE` rather than a hand-typed name.

    Args:
        address: the mark's own address.
        reads: the paragraph as it will read, with the added text in
            (`decision-log.md Process: #176`), as `a_move` takes its
            destination's. None leaves `raw_text` to the slot the mark is
            laid over.
    """
    mark = _mark(
        Instruction.ADD,
        address,
        {
            "missing": "a sentence stating what the code does here",
            "anchor": ANCHOR_EXAMPLE,
        },
    )
    if reads is not None:
        mark["raw_text"] = reads
    return mark


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


#: A paragraph with a typo on its first line and another on its last, and a
#: line between them neither role touches. Two sides editing abutting lines
#: are one span and refuse together (`machine.differences.compose`), so the
#: middle line is what lets the two patches below compose.
TYPOS = "# teh count\n# of the items\n# adn the sum\n"
FIRST_FIXED = "# the count\n# of the items\n# adn the sum"
LAST_FIXED = "# teh count\n# of the items\n# and the sum"
BOTH_FIXED = "# the count\n# of the items\n# and the sum"


def patched(address: str) -> dict:
    """Two roles patching different lines of one paragraph.

    `patch` is the row that owes no sources, so the composition these two come
    to has none behind it -- the hand `decision-log.md Process: #184` was
    ruled on. Composed, accepted and read from the decided place, that text
    reaches the docket; restated as one mark, it carried no source.
    """
    return {
        "block-context": {address: a_patch(address, "teh", "the", FIRST_FIXED)},
        "function-context": {address: a_patch(address, "adn", "and", LAST_FIXED)},
    }


def merged(*by_roles: dict) -> dict:
    """Several role -> {address: mark} maps as one."""
    out: dict = {}
    for by_role in by_roles:
        for role, marks in by_role.items():
            out.setdefault(role, {}).update(marks)
    return out


def deal(
    tmp_path,
    monkeypatch,
    capsys,
    by_role: dict | None = None,
    texts: dict | None = None,
    placed: dict | None = None,
) -> int:
    """`collate` over the hand: binder.json, chief0.json, proof0.json, batch1.json.

    The binder is over real pages written to `tmp_path / "repo"`, which the
    commands read as its root.

    ! ONE FOLD, THE COMMAND'S OWN. `collate --proof-out --batch-out` writes
    the state between turns and the first turn's batch, and `turn` reads both
    from there -- so the hand a turn is dealt is the hand `collate` dealt,
    with nothing folded twice.

    Args:
        by_role: role -> {address: mark}, each laid over the seeded slot at
            that address.
        texts: the paragraphs the binder's pages hold, for
            `a_real_binder_over`.
        placed: role -> [rulings], each PLACED through `flows.fill` -- the
            call `commands/mark.py` makes. ! IT IS NOT THE SAME AS
            `by_role`, and that is why both are here: a ruling at a place the
            binder does not carry has no seeded slot to lay a mark over, and
            `fill` is what creates one from the page. An `add` or a move's
            destination at an empty place can only be dealt this way. A role
            may appear in both, and its overlaid marks go on first.

    Returns:
        `collate`'s exit code, which is what a caller of it reads.
    """
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, texts or {"m.py@b1": BASE})
    roles = list(by_role or {})
    roles += [role for role in (placed or {}) if role not in roles]
    copies = []
    for role in roles:
        copy = _overlaid(seed(binder, role), (by_role or {}).get(role, {}))
        for ruling in (placed or {}).get(role, []):
            _mark, why = fill(copy, ruling, root)
            assert why == [], (role, ruling["address"], why)
        copies.append(copy)
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
        "--proof-out",
        str(tmp_path / "proof0.json"),
        "--batch-out",
        str(tmp_path / "batch1.json"),
    ]
    for i, copy in enumerate(copies):
        path = tmp_path / f"copy{i}.json"
        path.write_text(json.dumps(copy), encoding="utf-8")
        argv += ["--edit-copy", str(path)]
    code, _out = run_command(monkeypatch, capsys, collate_command, *argv)
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
    """`turn` n: proof<n-1> in, proof<n> and batch<n+1> out.

    `batch<n>` is what the answers were written against, and `answer` reads
    it; the command itself reads the proof alone, which says what each place
    was put to.
    """
    argv = [
        "--proof",
        proof or str(tmp_path / f"proof{n - 1}.json"),
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


def place_on(proof: MasterProof, address: str) -> dict:
    """One place the proof carries, as `Place.serialize` wrote it.

    Args:
        proof: a master proof read back, as `proof_at` returns one.
        address: the place to find.

    Returns:
        The entry, which a test reads `state`, `text` or `answers` off.

    Raises:
        AssertionError: the proof carries no place at that address.
    """
    for entry in proof.places:
        if entry.address == address:
            return entry.serialize()
    raise AssertionError(f"{address} is not on this proof")


def the_chief(tmp_path) -> EditCopy:
    """`disposition`'s chief.json, as the ordinary edit_copy it must be."""
    loaded = json.loads((tmp_path / "chief.json").read_text(encoding="utf-8"))
    return returned(loaded, "chief")
