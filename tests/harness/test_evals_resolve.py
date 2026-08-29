"""Every module in `evals/` resolves what it imports.

!! THIS IS THE CHECK THAT WAS MISSING, and its absence cost five days.
`generator_split.py` imported a module the 2026-08-24 package move had deleted,
and stayed broken because:

    ruff check .                    passes -- an import resolving to nothing is
                                    still valid syntax
    ty check src/comment_review/    never looked at `evals/` at all
    pytest                          imported none of it

The command in `CLAUDE.md` named `src/comment_review/`, so the one tool that
could answer was pointed somewhere else. Closes T4 of
`TODO/generator-split-is-dead-at-import.md`.

!! IT CAN FAIL, WHICH IS THE ONLY PROPERTY WORTH HAVING, and it was MEASURED
rather than asserted. 2026-08-29: a module holding one unresolvable import was
written into `evals/`, both tests went red -- naming the module and the import --
and both went green again when it was removed. `docs/gates.md`: "does the check
pass" is not the question; "could the check fail" is.
"""

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
EVALS = REPO / "evals"


def test_ty_resolves_every_import_in_evals():
    """The gate `ty check src/comment_review/` could never have reached."""
    done = subprocess.run(
        ["uv", "run", "ty", "check", "evals/"],
        cwd=REPO, capture_output=True, text=True,
    )

    assert done.returncode == 0, done.stdout + done.stderr


def test_every_evals_module_actually_imports():
    """Cheaper than `ty`, and it catches the same class at a different moment.

    ! A TYPE CHECKER READS; THIS RUNS. An import that resolves statically can
    still raise at module level -- a `sys.path` insert pointing at a directory
    that no longer exists resolves fine to a reader and dies on execution.
    """
    for module in sorted(EVALS.glob("*.py")):
        done = subprocess.run(
            [sys.executable, "-c", f"import {module.stem}"],
            cwd=EVALS, capture_output=True, text=True,
        )
        assert done.returncode == 0, f"{module.name}: {done.stderr}"
