"""Assemble the plugin from its two sources, WHOLESALE.

    python scripts/release.py

!! `plugins/comment-review/` IS OUTPUT. Nothing under it is written by hand.
It is assembled from two places and only at release, so between releases it
is allowed to lag the source, and no gate holds the two equal:

    src/plugin/           the prose an agent reads, and the manifest, laid out
                          in the plugin's own shape
    src/comment_review/   the package, with `src/comment-review.py` beside it,
                          copied into the skill's `scripts/` directory

!! WHOLESALE MEANS WHOLESALE. Roy, 2026-08-24: *"It is definitely not flattening
them out again. I said wholesale I meant it. Whatever structure we end up with
ends up there."* Both sources arrive with their sub-directories intact, so a
path that works in the source works in the plugin.

! IT DELETES THE PLUGIN AND REBUILDS IT. A copy that only adds leaves a renamed
or removed file sitting in the shipped tree, where it is what a stranger
installs. `tests/gates/test_release_assembles.py` proves a dropped file is gone.

The version bump, `claude plugin validate`, the tag and the push stay manual;
`CLAUDE.md`, *Cutting a release*, holds the order.
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROSE = ROOT / "src/plugin"
SRC = ROOT / "src"
PLUGIN = ROOT / "plugins/comment-review"

# Where the package lands inside the plugin, relative to the plugin root.
SCRIPTS = Path("skills/comment-review/scripts")

# The package, and the launcher beside it. ! The launcher is NOT in the package
# -- see `src/comment-review.py`, which says why it is hyphenated.
PACKAGE = "comment_review"
LAUNCHER = "comment-review.py"

# ! Not `*.pyc` alone: `__pycache__` is a DIRECTORY, and copying it ships one
# machine's bytecode to another interpreter.
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")


def assemble(prose: Path, src: Path, plugin: Path) -> list[Path]:
    """Replace `plugin` with `prose` plus the package, and list what is there.

    Returns every file under the rebuilt plugin, relative to it and sorted.
    """
    if plugin.exists():
        shutil.rmtree(plugin)
    shutil.copytree(prose, plugin, ignore=IGNORE)
    scripts = plugin / SCRIPTS
    shutil.copytree(src / PACKAGE, scripts / PACKAGE, ignore=IGNORE)
    shutil.copy2(src / LAUNCHER, scripts / LAUNCHER)
    return sorted(p.relative_to(plugin) for p in plugin.rglob("*") if p.is_file())


def main() -> int:
    """Assemble the plugin."""
    # ! A Windows console is cp1252 and this prints paths. The shipped tree
    # takes its guard from `constants.utf8_console`; a dev script cannot import
    # the package it is copying, so it spells the same three lines itself --
    # which is what every other script under `scripts/` does.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    files = assemble(PROSE, SRC, PLUGIN)
    print(f"assembled {len(files)} files into {PLUGIN.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
