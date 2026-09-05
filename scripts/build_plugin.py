"""Copy the source tree into the plugin, WHOLESALE.

    python scripts/build_plugin.py

!! `plugins/` IS BUILT, NOT EDITED, since 2026-08-24. Before that the shipped
scripts WERE the source, so there was nothing to build and nothing to disagree
with; the move to `src/comment_review/` made them a copy, and a copy needs a
step that makes it. It runs at release, not per change, and nothing holds the
two equal between releases.

!! WHOLESALE MEANS WHOLESALE. Roy, 2026-08-24: *"It is definitely not flattening
them out again. I said wholesale I meant it. Whatever structure we end up with
ends up there."* The package arrives with its sub-packages intact, so the
shipped tree and the source tree are the same shape and a path that works in one
works in the other.

! IT DELETES WHAT THE SOURCE NO LONGER HAS. A build that only copies leaves a
renamed or removed module sitting in the shipped tree, where it is what a
stranger installs -- and every gate reading `plugins/` would keep passing on it.
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
DEST = ROOT / "plugins/comment-review/skills/comment-review/scripts"

# The package, and the launcher beside it. ! The launcher is NOT in the package
# -- see `src/comment-review.py`, which says why it is hyphenated.
PACKAGE = "comment_review"
LAUNCHER = "comment-review.py"

# ! Not `*.pyc` alone: `__pycache__` is a DIRECTORY, and copying it ships one
# machine's bytecode to another interpreter.
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")


def sources() -> list[Path]:
    """Every file the build copies, relative to `src/`."""
    out = [Path(LAUNCHER)]
    for p in sorted((SRC / PACKAGE).rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            out.append(p.relative_to(SRC))
    return out


def build() -> None:
    """Replace the shipped tree with the source tree."""
    if (DEST / PACKAGE).exists():
        shutil.rmtree(DEST / PACKAGE)
    shutil.copytree(SRC / PACKAGE, DEST / PACKAGE, ignore=IGNORE)
    shutil.copy2(SRC / LAUNCHER, DEST / LAUNCHER)


def main() -> int:
    """Build the plugin."""
    # ! A Windows console is cp1252 and this prints paths. The shipped tree
    # takes its guard from `constants.utf8_console`; a dev script cannot import
    # the package it is building, so it spells the same three lines itself --
    # which is what every other script under `scripts/` does.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    DEST.mkdir(parents=True, exist_ok=True)
    build()
    print(f"built {len(sources())} files into {DEST.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
