"""`flows/distribute.py`: the seeded row carries `raw_text`, and the sheet's shape."""

import ast
import re
from pathlib import Path

from helpers import a_binder_over, binder_of

from comment_review.binder.binder import VERSION, Binder
from comment_review.desk.stages import Kind, Stage
from comment_review.flows.distribute import seed
from comment_review.reading.addresser import flatten

#: A stage dealt the `b` and `c` places over a cap of two lines, and admitting
#: the edit instructions -- `decision-log.md Process: #193`.
COMPACTING = Stage(
    name="6",
    kind=Kind.EDITORIAL,
    reads="revise:4",
    cap=2,
    series=("b", "c"),
    admits=("patch", "drop", "add", "clean"),
)

#: One page whose `b1` runs over that cap and whose `b2` does not.
OVER_AND_UNDER = {"m.py@b1": "# one\n# two\n# three", "m.py@b2": "# short"}


def _addresses(copy: dict) -> list[str]:
    return [mark["address"] for sheet in copy["sheets"] for mark in sheet["marks"]]


def test_a_stage_that_deals_by_a_cap_seeds_the_over_cap_places_alone():
    binder = a_binder_over(OVER_AND_UNDER)
    assert _addresses(seed(binder, "block-context", COMPACTING)) == ["m.py@b1"]


def test_without_a_stage_every_place_a_role_is_handed_is_seeded():
    """An ordinary stage behaves exactly as it did before the three keys: the
    seed is what a role was always handed."""
    binder = a_binder_over(OVER_AND_UNDER)
    assert _addresses(seed(binder, "block-context")) == ["m.py@b1", "m.py@b2"]


def test_a_stage_that_deals_nothing_seeds_a_copy_with_no_slots():
    """Every place is under the cap, so the stage has nothing to condense.
    The copy still carries its page, so the run goes on and says so rather
    than leaving the caller a missing file to interpret."""
    binder = a_binder_over({"m.py@b1": "# short", "m.py@b2": "# also short"})
    copy = seed(binder, "block-context", COMPACTING)
    assert _addresses(copy) == []
    assert [sheet["path"] for sheet in copy["sheets"]] == ["m.py"]


def test_the_copy_carries_the_stage_and_what_it_admits():
    """`mark` and `check` refuse an instruction the stage does not admit, and
    what they read is the copy in hand -- as `read_from` is what tells a role
    it holds a revise (`decision-log.md Process: #34`)."""
    copy = seed(a_binder_over(OVER_AND_UNDER), "block-context", COMPACTING)
    assert copy["stage"] == "6"
    assert copy["admits"] == ["patch", "drop", "add", "clean"]


def test_an_ordinary_stages_copy_names_no_stage_and_admits_everything():
    copy = seed(a_binder_over(OVER_AND_UNDER), "block-context")
    assert (copy["stage"], copy["admits"]) == ("", [])


# !! ABSOLUTE, matching `tests/test_binder_records_its_root.py`'s own `DESK` --
# a relative `Path("src/comment_review/desk")` only rglobs correctly when the
# suite runs from the repo root; see that file's header for the measured bug.
DESK = Path(__file__).resolve().parents[1] / "src" / "comment_review" / "desk"

#: `src/comment_review/`, for Step 5's sweep -- the tree `seed`'s own module
#: lives in, and the scope its claim is made over.
SRC = Path(__file__).resolve().parents[1] / "src" / "comment_review"


def test_a_seeded_row_carries_the_paragraph_bytes():
    # INPUT FROM REALITY: a real page of this repo through the real binder.
    binder = binder_of(DESK, 0)
    sheet = seed(binder, "block-context")
    # !! EXACT, NOT `endswith`. `desk/` holds several files whose own `@a0` is
    # its module docstring, and more than one name ends in another's --
    # `endswith("mark.py")` once matched `mark.py` and `diff_mark.py` both, and
    # `next()` returned whichever the walk visited first. The page is named in
    # full, and the seeded address is flattened because it sits in a
    # sub-package.
    real = str(Path("marks") / "rules.py")
    marks_page = next(s for s in sheet["sheets"] if s["path"] == real)
    row = next(r for r in marks_page["marks"] if r["address"] == f"{flatten(real)}@a0")
    source = (DESK / "marks" / "rules.py").read_text(encoding="utf-8")
    assert row["raw_text"] in source


def test_the_files_own_matter_gets_no_slot(tmp_path):
    """The brief promises a role it will not be shown front matter. The text
    report that used to keep the promise is gone, so the seed keeps it."""
    (tmp_path / "m.py").write_text(
        "#!/usr/bin/env python\n"
        "# Copyright 2026 Example. Licensed under the MIT licence.\n"
        '"""A module with a licence header above its docstring."""\n'
        "\n"
        "\n"
        "def f(x):\n"
        '    """Doc."""\n'
        "    return x + 1  # beside\n",
        encoding="utf-8",
    )
    binder = binder_of(tmp_path, 0)
    # ! The case has to be able to fail: the binder does carry the place.
    assert any("@f" in b.address for page in binder.pages for b in page.paragraphs)
    copy = seed(binder, "block-context")
    seeded = [m["address"] for sheet in copy["sheets"] for m in sheet["marks"]]
    assert seeded, "nothing seeded at all"
    assert not [a for a in seeded if "@f" in a], seeded


def test_an_edit_copy_holds_a_sheet_per_page_with_its_sha():
    # INPUT FROM REALITY: a real package through the real binder.
    binder = binder_of(DESK, 0)
    copy = seed(binder, "block-context")

    by_path = {sheet["path"]: sheet for sheet in copy["sheets"]}
    # EXPECTATION FROM THE BINDER, not from `seed`: the pages it was given.
    assert set(by_path) == {page.path for page in binder.pages}
    for page in binder.pages:
        assert by_path[page.path]["sha"] == page.sha


def test_every_mark_reaches_the_sheet_for_its_own_page():
    # `mark["address"]` is flattened (`reading.addresser.flatten`, `:` for a
    # path separator); `sheet["path"]` is the raw relative path `pages_of`
    # stamped, `os.sep` on this platform. `desk/` gained a subdirectory in
    # T1 of the-middle-rebuilt, so a nested page's raw path and its
    # flattened address stopped reading as the same string here.
    binder = binder_of(DESK, 0)
    copy = seed(binder, "block-context")
    for sheet in copy["sheets"]:
        for mark in sheet["marks"]:
            assert mark["address"].startswith(flatten(sheet["path"]))


def test_a_NULL_sha_is_seeded_as_absent_not_the_word_None():
    """`.get("sha", "")` DEFAULTS ONLY WHEN THE KEY IS ABSENT -- a `"sha"` key
    present and holding `None` returns `None` from `.get`, and `str(None)` is
    the four-character word "None".

    !! THE BINDER IS PUT ON THE WIRE AND DESERIALIZED, since 2026-08-31. It
    was a hand-built dict handed straight to `seed`, which the docstring
    described as *"a binder `binder.read()` did not validate the shape of"* --
    true then, and the shape a `Binder` cannot be. `Process: #67` puts the
    fold at the boundary, so this asserts BOTH halves: `deserialize` folds the
    null, and `seed` carries the "" through.
    """
    wire = {
        "version": VERSION,
        "read_from": {"root": "tests/test_distribute_flow.py", "revise": 0},
        "pages": [{"path": "m.py", "sha": None, "rows": []}],
    }
    binder, problems = Binder.deserialize("b.json", wire)
    assert binder is not None, problems
    assert binder.pages[0].sha == ""
    assert seed(binder, "block-context")["sheets"][0]["sha"] == ""


def test_no_module_outside_binder_imports_read_and_mentions_sha_in_one_file():
    """The weaker, checkable claim ruled for Step 5 of the SP task brief.

    !! WHAT THIS DOES NOT PROVE: an `ast.Attribute` scan tracing that a `sha`
    reference in some module actually flows from a value `binder.read`
    returned. That precise claim was not written -- the pre-flight ruling in
    `.superpowers/sdd/2026-08-29-the-master-proof-and-reconciliation/progress.md`
    resolved the brief's "or" to this weaker one instead. What IS checked: no
    module outside `src/comment_review/binder/` both imports the name `read`
    from `comment_review.binder.binder` (however it is imported) and mentions
    the WORD `sha` anywhere in its own source -- `\bsha\b`, so `shape` and
    `shared` do not count. A module could still defeat this claim by reading a
    sha through an alias that hides the import, or by reading `sha` off a
    value passed in from elsewhere -- which is why the claim is named as an
    import-and-mention coincidence, not a data-flow proof.
    """
    sha_word = re.compile(r"\bsha\b")

    def imports_binder_read(tree: ast.Module) -> bool:
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == (
                "comment_review.binder.binder"
            ):
                if any(alias.name == "read" for alias in node.names):
                    return True
            if isinstance(node, ast.Import):
                if any(
                    alias.name == "comment_review.binder.binder" for alias in node.names
                ):
                    return True
        return False

    offenders = []
    for path in sorted(SRC.rglob("*.py")):
        if path.relative_to(SRC).parts[0] == "binder":
            continue
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
        if imports_binder_read(tree) and sha_word.search(text):
            offenders.append(str(path.relative_to(SRC)))

    assert offenders == []
