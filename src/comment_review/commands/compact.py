r"""The `compact` command: stage 6's condensed text, onto the proof's places.

    comment_review compact --proof final.json --compacted C.json \\
        --proof-out compacted.json

The work is `flows.bus`: this loads the closed proof and the condensed texts,
sends one `CompactionsReturned`, prints the events, and saves the proof that
comes back. `decision-log.md Process: #191`: the decided text lives on the
place, so a later edit to it is made there.

    C.json  [{"address", "change"}]
            change: the paragraph as stage 6 condensed it, raw text.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.

Which places may take one is `desk.evaluate.compaction`'s, and every refusal
rolls the round back: a run that wrote the places it could would leave the
proof holding some condensed paragraphs and some at full length, with
nothing saying which. The refusal is the whole answer, so the caller fixes
what it named and runs again.

! `--proof-out` IS NOT `--proof`. The proof the fold closed is the record of
what was decided at full length, and a run that wrote over it would leave
nothing holding the text the roles settled on.
"""

import argparse
import sys
from pathlib import Path

from comment_review.commands.collate import _code_for, _counted, _print, _refused
from comment_review.flows.bus import CompactionsReturned, handle
from comment_review.flows.proof_io import load_proof, load_value, save_proof


def main() -> int:
    """Write each condensed paragraph onto the place that decided it.

    Returns:
        `UNREADABLE` when a file is not what it says or the output would be
        written over the input; `BROKEN` when a compaction cannot be
        written, each named, nothing written; `OK` with the compacted proof
        written.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--proof", required=True, help="the proof the chief's rulings closed"
    )
    ap.add_argument(
        "--compacted",
        required=True,
        help="the condensed texts, one per place stage 6 brought under the cap",
    )
    ap.add_argument(
        "--proof-out",
        required=True,
        help="where to write the proof carrying the condensed text",
    )
    args = ap.parse_args()

    # ! ASKED BEFORE THE LOAD, so a run that could only end by destroying its
    # own input never reads one. `resolve` is what makes two spellings of one
    # path the same answer.
    if Path(args.proof_out).resolve() == Path(args.proof).resolve():
        return _refused(
            [
                f"{args.proof_out}: the compacted proof is written beside the"
                " one the fold closed, never over it"
            ]
        )

    proof, why = load_proof(Path(args.proof))
    if proof is None:
        return _refused(why)
    handed, why = load_value(Path(args.compacted))
    if why:
        return _refused(why)
    # The shape of the file is this command's and the shape of one compaction
    # is the desk's: a list of objects is what the flag promises, and what
    # each object owes is `desk.evaluate.compaction`'s, which the message
    # reports.
    rows: list = (
        [r for r in handed if isinstance(r, dict)] if isinstance(handed, list) else []
    )
    if not isinstance(handed, list) or len(rows) != len(handed):
        return _refused(
            [f"{args.compacted}: the compacted texts are a list of objects"]
        )

    out, result = handle(CompactionsReturned(proof, rows))
    _print(out)
    if result is None:
        return _code_for(out)

    # The serialize is the container's and the dump is the flow's
    # (`decision-log.md Process: #65`, `#67`), as `collate` and `disposition`
    # save.
    save_proof(Path(args.proof_out), result.proof)
    print(f"{args.proof_out}: the proof compacted -- {_counted(result.proof.places)}")
    return _code_for(out)


if __name__ == "__main__":
    sys.exit(main())
