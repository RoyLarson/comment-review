"""The `lost` command: its argument parsing and its exit code.

    python -m comment_review lost --repo D [--proof P ...] <overlay...>

The work is `flows.lost.lost_sentences`; this is only the console face of it.
Each overlay is a directory of drafts at their repo paths: the `proof --out`
directory and the freeform drafts. Each `--proof` is a stage's closed proof,
read for the moves it agreed.

Prints one tab-separated `<path>`, `<sentence>` line per removed sentence found
neither in its own file nor where a move sent it, then `<N> sentences in no
file`. It is an input to the author's ruling, so it exits 0 whatever it lists.
"""

import argparse
from pathlib import Path

from comment_review.flows.lost import lost_sentences
from comment_review.flows.proof_io import load_proof


def main() -> int:
    """Print the removed sentences that end up at no place they were sent.

    Returns:
        0 when the list was printed; 2 when an overlay is not a directory, a
        proof will not load, or git cannot list the tracked files under
        `--repo`.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("overlays", nargs="+", help="directories of drafts")
    ap.add_argument("--repo", default=".", help="repo root")
    ap.add_argument(
        "--proof", action="append", default=[], help="a closed proof; repeatable"
    )
    args = ap.parse_args()

    overlays = [Path(raw) for raw in args.overlays]
    for overlay in overlays:
        if not overlay.is_dir():
            print(f"CANNOT READ {overlay}: not a directory")
            return 2
    proofs = []
    for raw in args.proof:
        proof, why = load_proof(Path(raw))
        if proof is None:
            for line in why:
                print(f"CANNOT READ {raw}: {line}")
            return 2
        proofs.append(proof)
    lost = lost_sentences(Path(args.repo), overlays, proofs)
    if lost is None:
        print(f"NO GIT INDEX under {args.repo} -- cannot list the tree as written")
        return 2
    for rel, sentence in lost:
        print(f"{rel}\t{sentence}")
    print(f"{len(lost)} sentences in no file")
    return 0
