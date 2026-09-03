"""`flows/distribute.py`: the seeded row carries `raw_text`, and the sheet's shape."""

import ast
import re
from pathlib import Path

from helpers import binder_of

from comment_review.binder.binder import VERSION, Binder
from comment_review.flows.distribute import seed

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
    # its module docstring -- `endswith("mark.py")` matched `mark.py` until a
    # sibling named `diff_mark.py` arrived, whose name also ends in that
    # substring, and `next()` returned whichever the walk visited first.
    marks_page = next(s for s in sheet["sheets"] if s["path"] == "mark.py")
    row = next(r for r in marks_page["marks"] if r["address"] == "mark.py@a0")
    source = (DESK / "mark.py").read_text(encoding="utf-8")
    assert row["raw_text"] in source


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
    binder = binder_of(DESK, 0)
    copy = seed(binder, "block-context")
    for sheet in copy["sheets"]:
        for mark in sheet["marks"]:
            assert mark["address"].startswith(sheet["path"])


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
