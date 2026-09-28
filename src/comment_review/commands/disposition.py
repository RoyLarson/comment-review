r"""The `disposition` command: the chief's rulings close a stage's fold.

    comment_review disposition --proof P.json --dispositions D.json \\
        --out chief.json --proof-out final.json

The work is `flows.bus`: this loads the proof and the rulings, sends one
`DispositionsWritten`, prints the events the fold produced, and saves the
chief's copy and the closed proof. `Process: #78`: the task agent's max turns
ends the roles' part; `#87`: every place still carried forward takes the
chief's own ruling, and the chief's `edit_copy` is derived from every place
the fold decided.

    dispositions.json  [{"address", "answer", "side", "reason", "prose"}]
                   answer: taken_in or recast. side: a role, or the original,
                   for a taken_in. prose: the chief's own paragraph, for a
                   recast.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.

Nothing survives the chief's ruling unruled. A carried-forward place with no
ruling is refused by name, with the roles it was put to, and nothing is
written -- the refusal is the whole answer, so the caller rules and runs
again.

The unsettlable places are printed and not ruled (`Process: #90`). A
human-review query rides with the set to the end and is asked of the human
after everything else has settled; this is the end, so each is named here for
that asking, and none is on the chief's copy. A ruling at one of them is
refused, as at any place the fold does not carry forward.
"""

import argparse
import sys
from pathlib import Path

from comment_review.commands.collate import _code_for, _counted, _print, _refused
from comment_review.flows.bus import DispositionsWritten, handle, turn_of
from comment_review.flows.proof_io import (
    load_proof,
    load_value,
    save_copy,
    save_proof,
)


def main() -> int:
    """Rule every carried-forward place, derive the chief's copy, close the proof.

    Returns:
        `UNREADABLE` when a file is not what it says; `BROKEN` when a ruling
        cannot be applied or a place is left unruled, each named, nothing
        written; `OK` with the chief's copy and the closed proof written.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--proof", required=True, help="the master proof as the last fold wrote it"
    )
    ap.add_argument(
        "--dispositions",
        required=True,
        help="the chief's rulings, one per carried-forward place",
    )
    ap.add_argument("--out", required=True, help="where to write the chief's edit_copy")
    ap.add_argument(
        "--proof-out",
        required=True,
        help="where to write the closed proof -- every place as the chief left it",
    )
    args = ap.parse_args()

    proof, why = load_proof(Path(args.proof))
    if proof is None:
        return _refused(why)
    rulings, why = load_value(Path(args.dispositions))
    if why:
        return _refused(why)
    # The shape of the file is this command's and the shape of a ruling is the
    # table's: a list of objects is what the flag promises, and what each
    # object owes is `Disposition.deserialize`'s, which the fold reports.
    rows: list = (
        [r for r in rulings if isinstance(r, dict)] if isinstance(rulings, list) else []
    )
    if not isinstance(rulings, list) or len(rows) != len(rulings):
        return _refused(
            [f"{args.dispositions}: the dispositions are a list of objects"]
        )

    out, result = handle(DispositionsWritten(proof, rows))
    _print(out)
    if result is None:
        return _code_for(out)

    # The serialize is the container's and the dump is the flow's
    # (`decision-log.md Process: #65`, `#67`), as `collate` saves. A committed
    # `DispositionsWritten` always carries a chief copy; the field is optional
    # because another handler on this bus may have no copy to write, and the
    # guard is what says so rather than an assertion.
    if result.chief is not None:
        save_copy(Path(args.out), result.chief)
        places = sum(len(sheet.marks) for sheet in result.chief.sheets)
        print(f"{args.out}: the chief's copy, {places} places")
    save_proof(Path(args.proof_out), result.proof)
    print(
        f"{args.proof_out}: the proof closed at turn {turn_of(result.proof)} --"
        f" {_counted(result.proof.places)}"
    )
    return _code_for(out)


if __name__ == "__main__":
    sys.exit(main())
