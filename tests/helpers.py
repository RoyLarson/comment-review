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

from pathlib import Path

from conftest import ROOT, cue

from comment_review.binder.binder import VERSION, Binder, bind
from comment_review.desk.containers import EditCopy, MasterProof, Sheet
from comment_review.desk.mark import ANCHOR_EXAMPLE, INSTRUCTIONS, Instruction, Shape
from comment_review.desk.proof import gather
from comment_review.docket.docket import Docket
from comment_review.flows.distribute import seed
from comment_review.flows.page_for import page_of, source_of

#: `src/comment_review/desk/` -- the source `a_small_real_tree` copies from.
#: Any package with a handful of ordinary Python files would do; this one was
#: picked because it is small and holds real comments in more than one series.
_DESK = Path(__file__).resolve().parents[1] / "src" / "comment_review" / "desk"

#: A real citation `a_correct`, `a_move`, `a_query` and `an_add` reuse for
#: `sources` -- `mark.py`'s own first line, read once at import time.
_MARK_PY_CITE = "src/comment_review/desk/mark.py:1"
_MARK_PY_LINE_1 = (_DESK / "mark.py").read_text(encoding="utf-8").splitlines()[0]

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
    would be asserting a binder shape no census produces.
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
    this suite. `mark.py` keeps its own name so a docket over "mark.py" names
    a file that is actually there; the other three are along for the
    "every library file" half of `test_revise.py`'s first case.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    for name in ("mark.py", "stages.py", "collator.py", "__init__.py"):
        (repo / name).write_bytes((_DESK / name).read_bytes())
    return repo


def a_docket_over(repo: Path, names: list[str]) -> Docket:
    """A docket that replaces one real, filled `b`-series comment in each
    named file.

    ! THE CUE AND ITS ORIGINAL TEXT COME OFF THE REAL PAGE, through
    `binder_of`, never hand-written -- a `b` row is picked because its
    replacement needs no more than `#`, which every file here (`.py`) shares.

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
                cue(row)
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
                "alterations": [{"cue": found, "text": "# revised by a_docket_over"}],
            }
        )
        remaining.discard(Path(page.path).name)
    if remaining:
        raise AssertionError(f"no filled 'b' row found for {sorted(remaining)}")
    return _a_docket({"pages": pages})


def a_docket_whose_claim_is_not_in_the_page(repo: Path, name: str) -> Docket:
    """A docket naming a cue no paragraph on the page holds -- a chain
    refusal, without asserting which step raises it.

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
                                {"cue": "zzz9999", "text": "# never reaches the page"}
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


def marks_of(sheet: Sheet) -> list[dict]:
    """One sheet's entries, each asserted to be an object.

    ! `Sheet.marks` IS `tuple[object, ...]` DELIBERATELY -- an entry that is not
    an object is CARRIED so `desk.mark.parse` can refuse it by name. A test
    reading a FIELD off an entry is asserting about a well-formed one, so this
    asserts that first and fails HERE rather than at the subscript.
    """
    for entry in sheet.marks:
        assert isinstance(entry, dict), entry
    return [entry for entry in sheet.marks if isinstance(entry, dict)]


def entries_of(copy: EditCopy) -> list[dict]:
    """Every mark entry on a copy, flattened, in sheet then mark order.

    ! IT REPLACES `[m for s in got.chief.sheets for m in s.marks]`, which stood
    at thirteen sites in `tests/test_collate.py` alone.
    """
    return [entry for sheet in copy.sheets for entry in marks_of(sheet)]


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
    """A `master_proof`, composed through the real `seed()` and `gather()`.

    Args:
        by_role: role name -> {address: mark}, one mark per place that role
            rules on, built by `a_correct`, `a_move`, `a_clean`, `a_query` or
            `an_add`.

    Returns:
        The `MasterProof` `desk.proof.gather` returns. One `edit_copy` per
        role, seeded for real over a synthetic binder sized to that role's own
        addresses, then each seeded entry overlaid with the caller's mark --
        the same `entry.update(...)` pattern `tests/test_collator.py` uses over
        a real one.

    ! IT RUNS THE REAL PARSE BETWEEN THE TWO, exactly as `flows.collate.collate`
    does since `P42`: `seed` writes the wire dict a role is handed, and `gather`
    takes the parsed `EditCopy`. A fixture that skipped the parse would hand
    `gather` a shape production cannot produce.
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
    return gather("4c", copies)


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
