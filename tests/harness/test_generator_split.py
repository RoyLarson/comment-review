"""`generator_split` runs against the package, not against a `sys.path` insert.

The 2026-08-24 move put the Python in `src/comment_review/` and split the flat
`census` module across four areas. This file left a `sys.path` insert pointing
into `plugins/` and imported `census` from it, so it raised
`ModuleNotFoundError` before reading an argument -- for five days, while
`CLAUDE.md` documented it as a working command.

! NOTHING COULD SEE IT. `ruff` passes on an import that resolves to nothing, and
`ty check` is pointed at `src/comment_review/` alone, so `evals/` was never
type-checked. The failure needed someone to RUN it.
"""

import pathlib
import re
import subprocess
import sys

import generator_split

REPO = pathlib.Path(__file__).resolve().parents[2]

SCRIPT = REPO / "evals" / "generator_split.py"


def test_every_name_it_needs_resolves():
    """The defect itself: the module could not be imported at all.

    ! ASSERTED NAME BY NAME, not by `import generator_split` alone. The nine
    `census.*` uses did not move together -- they are spread across `machine`,
    `binder`, `concordance` and `reading` -- so an import that merely succeeds
    says nothing about whether the calls inside `main` resolve.
    """
    for name in (
        "walk_files", "tracked_paths", "path_index", "code_names",
        "NO_HARVESTER", "WALKED_TREE", "language_for", "page_for",
        "annotate", "read_source", "PARSE_ERRORS", "READ_ERRORS",
    ):
        assert hasattr(generator_split, name), name

    assert callable(generator_split.main)


def test_it_splits_a_real_target_in_this_repo():
    """End to end over a real checkout, because `git blame` is the whole method.

    ! ONE SMALL TARGET. The walk and the name corpus cover the repo either way;
    naming a single file keeps the blame to one file, and the split still has to
    do every step to report anything at all.
    """
    # ! `sys.executable`, NEVER a bare `python`. The package is installed in this
    # project's venv, and the ambient interpreter is whatever the machine has --
    # which is the substitution `CLAUDE.md` forbids for exactly this reason.
    done = subprocess.run(
        [sys.executable, str(SCRIPT), str(REPO), "evals/workspace.py"],
        capture_output=True, text=True, cwd=REPO,
    )

    assert done.returncode == 0, done.stderr
    assert "commits touching them" in done.stdout
    assert "bucket" in done.stdout and "blocks" in done.stdout

    # !! A BUCKET WITH BLOCKS IN IT IS WHAT PROVES THE PORT. An empty table
    # would print just as happily: `page_for` is the deepest call, and a run
    # that read no paragraphs still reaches this banner.
    rows = re.findall(r"^(human|assisted|mixed)\s+(\d+)", done.stdout, re.M)
    assert rows, done.stdout
    assert any(int(blocks) > 0 for _, blocks in rows), done.stdout

    # ! AND AN ANNOTATION PROVES THE REST OF IT -- `annotate` was the last name
    # ported, and it can only fire on a corpus `code_names` and `path_index`
    # actually built.
    assert "names-a-symbol" in done.stdout
