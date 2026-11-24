"""The `lost` command: its argument parsing and its exit code.

    python -m comment_review lost --repo D <overlay...>

The work is `flows.lost.lost_sentences`; this is only the console face of it.
Each overlay is a directory of drafts at their repo paths: the `proof --out`
directory and the freeform drafts.

Prints one tab-separated `<path>`, `<sentence>` line per removed sentence no
file of the tree as written holds, then `<N> sentences in no file`. It is an
input to the author's ruling, so it exits 0 whatever it lists.
"""

import argparse
from pathlib import Path

from comment_review.flows.lost import lost_sentences


def main() -> int:
    """Print the removed sentences that end up in no file.

    Returns:
        0 when the list was printed; 2 when an overlay is not a directory or
        git cannot list the tracked files under `--repo`.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("overlays", nargs="+", help="directories of drafts")
    ap.add_argument("--repo", default=".", help="repo root")
    args = ap.parse_args()

    overlays = [Path(raw) for raw in args.overlays]
    for overlay in overlays:
        if not overlay.is_dir():
            print(f"CANNOT READ {overlay}: not a directory")
            return 2
    lost = lost_sentences(Path(args.repo), overlays)
    if lost is None:
        print(f"NO GIT INDEX under {args.repo} -- cannot list the tree as written")
        return 2
    for rel, sentence in lost:
        print(f"{rel}\t{sentence}")
    print(f"{len(lost)} sentences in no file")
    return 0
