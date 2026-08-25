"""Copy the source tree into the plugin, WHOLESALE.

    python scripts/build_plugin.py [--check]

!! `plugins/` IS BUILT, NOT EDITED, since 2026-08-24. Before that the shipped
scripts WERE the source, so there was nothing to build and nothing to disagree
with; the move to `src/comment_review/` made them a copy, and a copy needs a
step that makes it and a gate that proves it.

!! WHOLESALE MEANS WHOLESALE. Roy, 2026-08-24: *"It is definitely not flattening
them out again. I said wholesale I meant it. Whatever structure we end up with
ends up there."* The package arrives with its sub-packages intact, so the
shipped tree and the source tree are the same shape and a path that works in one
works in the other.

! IT DELETES WHAT THE SOURCE NO LONGER HAS. A build that only copies leaves a
renamed or removed module sitting in the shipped tree, where it is what a
stranger installs -- and every gate reading `plugins/` would keep passing on it.

! `--check` WRITES NOTHING and reports whether the two agree. That is the gate;
`tests/gates/test_build.py` is what proves the gate can fail.
"""

import argparse
import filecmp
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


def built() -> list[Path]:
    """Every file currently in the shipped tree, relative to it."""
    out = []
    for p in sorted(DEST.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            out.append(p.relative_to(DEST))
    return out


def differences() -> tuple[list[Path], list[Path], list[Path]]:
    """`(missing, extra, differing)` between the source and the shipped tree.

    Returns:
        missing: in `src/`, absent from the plugin.
        extra: in the plugin, absent from `src/` -- a file the source dropped.
        differing: present in both, with different bytes.
    """
    want, have = set(sources()), set(built())
    differing = [
        rel
        for rel in sorted(want & have)
        if not filecmp.cmp(SRC / rel, DEST / rel, shallow=False)
    ]
    return sorted(want - have), sorted(have - want), differing


def build() -> None:
    """Replace the shipped tree with the source tree."""
    if (DEST / PACKAGE).exists():
        shutil.rmtree(DEST / PACKAGE)
    shutil.copytree(SRC / PACKAGE, DEST / PACKAGE, ignore=IGNORE)
    shutil.copy2(SRC / LAUNCHER, DEST / LAUNCHER)


def main() -> int:
    """Build the plugin, or check that it is already built."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="write nothing; exit 1 if the plugin does not match the source",
    )
    args = ap.parse_args()

    # ! A Windows console is cp1252 and this prints paths. The shipped tree
    # takes its guard from `constants.utf8_console`; a dev script cannot import
    # the package it is building, so it spells the same three lines itself --
    # which is what every other script under `scripts/` does.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    if not args.check:
        DEST.mkdir(parents=True, exist_ok=True)
        build()
        print(f"built {len(sources())} files into {DEST.relative_to(ROOT).as_posix()}")
        return 0

    missing, extra, differing = differences()
    if not (missing or extra or differing):
        print(f"the plugin matches the source: {len(sources())} files")
        return 0
    print("THE SHIPPED TREE DOES NOT MATCH THE SOURCE.")
    for rel in missing:
        print(f"  missing from the plugin   {rel.as_posix()}")
    for rel in extra:
        print(f"  not in the source         {rel.as_posix()}")
    for rel in differing:
        print(f"  differs                   {rel.as_posix()}")
    print("\nRun `python scripts/build_plugin.py`.")
    print("Edit `src/`, never `plugins/`.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
