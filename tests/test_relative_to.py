"""`machine.repo.relative_to`: a path expressed from another, `pathlib` alone.

Roy, 2026-08-28: *"No os.path. Only Pathlib. Fix this everywhere."*

!! WHAT `pathlib` DOES NOT SHIP is the `..` walk. `Path.relative_to` RAISES when
the target is not under the start, and a revise root is a temporary directory
OUTSIDE the checkout -- which is why `os.path.relpath` was reached for on
2026-08-28 and why this function replaces it.

! EXPECTATIONS HERE ARE WRITTEN OUT, never taken from `os.path.relpath`. Deriving
them from the thing being replaced would only prove the two agree, including
where the old one was wrong -- it raised across drives, and this returns a path.
"""

import ast
from pathlib import Path

from conftest import ROOT

from comment_review.machine.repo import relative_to


def test_a_child_is_named_without_a_walk(tmp_path):
    child = tmp_path / "src" / "comment_review"
    child.mkdir(parents=True)
    assert relative_to(child, tmp_path) == Path("src/comment_review")


def test_the_same_place_is_a_dot(tmp_path):
    # ! WHAT THE CENSUS OF ITS OWN CHECKOUT REPORTS: `census --repo .` records
    # `{"root": ".", "revise": 0}`, which is the value this case produces.
    assert relative_to(tmp_path, tmp_path) == Path(".")


def test_a_sibling_walks_up(tmp_path):
    # ! THE REVISE CASE. `pull` puts a revise root beside the checkout, so the
    # census of that root has to walk out of the checkout and back down.
    repo = tmp_path / "repo"
    revise = tmp_path / "r1"
    repo.mkdir()
    revise.mkdir()
    assert relative_to(revise, repo) == Path("../r1")


def test_a_parent_is_dotdot(tmp_path):
    inner = tmp_path / "a" / "b"
    inner.mkdir(parents=True)
    assert relative_to(tmp_path / "a", inner) == Path("..")


def test_two_anchors_yield_the_absolute_target():
    # !! THE CASE THAT CRASHED, and the reason this is not a thin wrapper.
    # MEASURED 2026-08-28: `os.path.relpath(r"D:\\corpora\\numpy",
    # r"C:\\Users\\Roy")` raises `ValueError: path is on mount 'D:'`. There is
    # no relative path between two anchors, so the absolute target is the only
    # honest answer -- `census --json --repo D:\\...` from a `C:` cwd was an
    # uncaught traceback before this.
    #
    # ! POSIX HAS ONE ANCHOR, so this asserts the RULE rather than a Windows
    # spelling: where the anchors differ, the result is the resolved target.
    # On a single-anchor platform the branch is unreachable and the assertion
    # below still states what it must do.
    here = Path.cwd()
    assert relative_to(here, here) == Path(".")
    a, b = Path("/x/y"), Path("/x/z")
    out = relative_to(a, b)
    if a.anchor == b.anchor:
        assert out == Path("../y")
    else:
        assert out == a.resolve()


def _reaches_for_os_path(source: str) -> bool:
    """Does this module USE `os.path`, as against naming it?

    !! IT ASKS THE SYNTAX TREE, and asked the TEXT for one run -- which flagged
    `machine/repo.py`, whose docstring CITES `os.path.relpath` while calling
    nothing. That is the same mention-not-use defect
    `tests/test_no_second_draft_path.py` records being fixed the same day, made
    twice in one afternoon.

    ! IT ALSO CATCHES WHAT A GREP FOR `os.path.` DOES NOT: `from os.path import
    join`, `from os import path`, and `import os.path as p` each reach for the
    module without ever spelling that substring. MEASURED 2026-08-28: none are
    present in this tree, which a substring search could not have established.
    """
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Attribute)
            and node.value.attr == "path"
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id == "os"
        ):
            return True
        if isinstance(node, ast.ImportFrom):
            if (node.module or "").startswith("os.path"):
                return True
            if node.module == "os" and any(a.name == "path" for a in node.names):
                return True
        if isinstance(node, ast.Import) and any(
            a.name.startswith("os.path") for a in node.names
        ):
            return True
    return False


# ! `prototype/` IS EXEMPT because it does not run -- nothing imports it and
# nothing ships it. `.venv` and `corpora/` hold other people's code.
_NOT_OURS = frozenset({".venv", "corpora", "__pycache__", "prototype"})


def test_it_is_pathlib_only():
    # !! EVERY PYTHON FILE THIS REPO OWNS, not only the shipped package. Roy,
    # 2026-08-28: *"No os.path. Only Pathlib. Fix this everywhere."* -- and the
    # first form of this test read `src/comment_review/` alone, which is
    # narrower than the rule it claimed to enforce.
    #
    # ! `ROOT` comes from `conftest`, which already answers where the checkout
    # is; re-deriving it here with `parents[1]` was a second answer to a
    # settled question.
    offenders = [
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*.py")
        if not _NOT_OURS.intersection(p.parts)
        and _reaches_for_os_path(p.read_text(encoding="utf-8", errors="replace"))
    ]
    assert offenders == []


def test_naming_os_path_in_prose_is_not_using_it():
    # ! WHAT PROVES THE CHECK ASKS THE RIGHT QUESTION -- and `machine/repo.py`
    # is a live example, citing `os.path.relpath` in the measurement that
    # explains why `relative_to` exists.
    assert not _reaches_for_os_path('"""A note about os.path.relpath."""\n')
    assert _reaches_for_os_path("import os\nx = os.path.relpath('a', 'b')\n")
