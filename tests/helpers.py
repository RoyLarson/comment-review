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
"""

from pathlib import Path

from comment_review.binder.binder import bind
from comment_review.flows.page_for import page_of, source_of

#: `src/comment_review/desk/` -- the source `a_small_real_tree` copies from.
#: Any package with a handful of ordinary Python files would do; this one was
#: picked because it is small and holds real comments in more than one series.
_DESK = Path(__file__).resolve().parents[1] / "src" / "comment_review" / "desk"


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


def binder_of(root: Path, revise: int) -> dict:
    return bind(pages_of(root), read_from={"root": str(root), "revise": revise})


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


def a_docket_over(repo: Path, names: list[str]) -> dict:
    """A docket that replaces one real, filled `b`-series comment in each
    named file.

    ! THE CUE AND ITS ORIGINAL TEXT COME OFF THE REAL PAGE, through
    `binder_of`, never hand-written -- a `b` row is picked because its
    replacement needs no more than `#`, which every file here (`.py`) shares.

    Args:
        repo: a checkout `binder_of` can read, e.g. from `a_small_real_tree`.
        names: file BASENAMES to alter one comment in each of.

    Returns:
        A docket in `docket.read`'s shape.

    Raises:
        AssertionError: a name has no filled `b` row to alter.
    """
    binder = binder_of(repo, 0)
    remaining = set(names)
    pages = []
    for page in binder.get("pages", []):
        if Path(page["path"]).name not in remaining:
            continue
        cue = next(
            (
                row["cue"]
                for row in page.get("rows", [])
                if row["cue"].startswith("b") and row["raw_text"].strip()
            ),
            None,
        )
        if cue is None:
            continue
        pages.append(
            {
                "path": page["path"],
                "sha": page["sha"],
                "alterations": [{"cue": cue, "text": "# revised by a_docket_over"}],
            }
        )
        remaining.discard(Path(page["path"]).name)
    if remaining:
        raise AssertionError(f"no filled 'b' row found for {sorted(remaining)}")
    return {"pages": pages}


def a_docket_whose_claim_is_not_in_the_page(repo: Path, name: str) -> dict:
    """A docket naming a cue no paragraph on the page holds -- a chain
    refusal, without asserting which step raises it.

    Args:
        repo: a checkout `binder_of` can read.
        name: the file basename to build the (unreachable) alteration over.

    Returns:
        A docket in `docket.read`'s shape.

    Raises:
        AssertionError: no page in `repo` has this basename.
    """
    binder = binder_of(repo, 0)
    for page in binder.get("pages", []):
        if Path(page["path"]).name == name:
            return {
                "pages": [
                    {
                        "path": page["path"],
                        "sha": page["sha"],
                        "alterations": [
                            {"cue": "zzz9999", "text": "# never reaches the page"}
                        ],
                    }
                ]
            }
    raise AssertionError(f"no page named {name!r} in {repo}")


def a_docket_that_rewrites(repo: Path, name: str) -> dict:
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
        A docket in `docket.read`'s shape.

    Raises:
        AssertionError: `name` has no filled `b` row to alter.
    """
    return a_docket_over(repo, [name])


def the_row_for(binder: dict, name: str) -> dict:
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
        The row dict, as `binder.page_row` shapes one.

    Raises:
        AssertionError: no page named `name`, or no filled `b` row on it.
    """
    for page in binder.get("pages", []):
        if Path(page["path"]).name != name:
            continue
        for row in page.get("rows", []):
            if row["cue"].startswith("b") and row["raw_text"].strip():
                return row
        raise AssertionError(f"no filled 'b' row on {name!r}")
    raise AssertionError(f"no page named {name!r} in binder")
