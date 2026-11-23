"""The `distribute` command: its argument parsing and its exit code.

    comment_review distribute --shape
    comment_review distribute --seed --binder B.json --role block-context --out F.json
    comment_review distribute --topology T.toml --stage 4c --binder B.json --out-dir DIR
        [--revise REVISE_ROOT]

The work is `flows.distribute`, `flows.fan_out` and `desk.marks`; this is only
the console face of it.

!! `--stage` is the topology's reader. One
invocation reads one stage's dispatches out of the topology and writes one
seeded edit copy per dispatch, in dispatch order, as `DIR/<stage>_<role>_<n>.json`.
Its received binder is saved as `DIR/binders/<stage>_<role>_<n>.json`.
The task agent reads the order of the stages from SKILL.md and runs this once
per stage; no command sequences them.

!! And the stage's `reads` decides which tree it is seeded from. A stage
reading `"revise:<name>"` is seeded from the revise that stage's `proof`
pulled: `--revise` names that root and the binder must be the one gathered
from it, which `desk.topology.seeded_from_problem` rules on. A stage reading
`"original"` takes no `--revise`. The rule is the topology's; this passes it
the stage, the root and what the binder says about itself.

!! A module does one job and has no CLI; a flow calls modules; a command
exposes a flow.

This command seeds and does not check. `collate` checks every copy before it
folds, so a malformed copy is never folded; the `check` command checks one
returned copy on its own, which is how a role validates its copy before handing
it back.
"""

import argparse
import json
import sys
from pathlib import Path

from comment_review.desk.marks.rules import allowed
from comment_review.desk.stages import ROLES
from comment_review.desk.topology import read as read_topology
from comment_review.desk.topology import seeded_from_problem
from comment_review.flows.distribute import IncompatibleBinder, seed
from comment_review.flows.fan_out import OverlappingShards, UncoveredPage, dealt
from comment_review.flows.proof_io import load_binder

# ! Bound to a name: a tuple literal in an `except` is what a newer formatter
# rewrites into a form the floor interpreter cannot parse.
FAN_REFUSALS = (OverlappingShards, UncoveredPage, IncompatibleBinder)


def _as_json(payload: dict) -> str:
    """This command's one `json.dumps`, for every JSON it prints or writes.

    !! Several outputs, one spelling. `--shape` prints, and `--seed` and
    `--stage` write files. All of them are at the save end, which is where the
    rule allows raw json -- what the rule does not allow is one command holding
    two answers to *how does this command write JSON*, because that is where an
    indent or an encoding drifts apart between outputs nobody compares.
    """
    return json.dumps(payload, indent=2)


def main() -> int:
    """Publish the shape, or seed an `edit_copy`.

    Returns:
        0 when the shape printed or the edit_copy was written; 2 when an
        input could not be read.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument(
        "--shape", action="store_true", help="print what a mark may carry, as JSON"
    )
    mode.add_argument("--seed", action="store_true", help="write a fillable edit_copy")
    ap.add_argument("--binder", help="the binder to seed from (--seed only)")
    # `choices=` takes the string values, not the `Role` members themselves:
    # argparse's "invalid choice" message reprs each choice, and a `StrEnum`
    # member's repr is `<Role.OWNERSHIP_CONTEXT: 'ownership-context'>` rather
    # than the plain name a user typed.
    ap.add_argument(
        "--role",
        choices=[str(role) for role in ROLES],
        help="the editorial role (--seed only)",
    )
    ap.add_argument("--out", help="the file to write (--seed only)")
    ap.add_argument("--topology", help="the run's topology file (--stage only)")
    mode.add_argument("--stage", help="the stage to seed, by its name in the topology")
    ap.add_argument(
        "--out-dir", help="where one copy per dispatch is written (--stage only)"
    )
    ap.add_argument(
        "--revise",
        help="the revise root a stage whose `reads` names one is seeded from"
        " (--stage only); the binder must be the one gathered from it",
    )
    args = ap.parse_args()

    if args.shape:
        print(_as_json(allowed()))
        return 0

    if args.seed:
        # ! Every one is required together: an edit_copy with no role cannot be
        # collated, and one with no address cannot be filled -- which is the
        # whole reason it is seeded rather than described.
        missing = [n for n in ("binder", "role", "out") if not getattr(args, n)]
        if missing:
            wanted = ", ".join("--" + n for n in missing)
            print(f"--seed needs {wanted}", file=sys.stderr)
            return 2
        # !! The load is the flow's, the deserialize the container's;
        # `flows.proof_io.load_binder` is both.
        binder, problems = load_binder(Path(args.binder))
        if binder is None:
            for line in problems:
                print(line, file=sys.stderr)
            return 2
        try:
            edit_copy = seed(binder, args.role)
        except IncompatibleBinder as exc:
            print(str(exc), file=sys.stderr)
            return 2
        Path(args.out).write_text(_as_json(edit_copy), encoding="utf-8", newline="")
        places = sum(len(sheet["marks"]) for sheet in edit_copy["sheets"])
        print(
            f"{args.out}: {places} places for {args.role} to rule on; "
            f"{len(binder.freeform)} freeform"
        )
        return 0

    if args.stage:
        missing = [n for n in ("topology", "binder", "out_dir") if not getattr(args, n)]
        if missing:
            wanted = ", ".join("--" + n.replace("_", "-") for n in missing)
            print(f"--stage needs {wanted}", file=sys.stderr)
            return 2
        stages, why = read_topology(Path(args.topology).read_text(encoding="utf-8"))
        if why:
            print(why, file=sys.stderr)
            return 2
        stage = next((s for s in stages if s.name == args.stage), None)
        if stage is None:
            known = ", ".join(s.name for s in stages)
            print(
                f"stage {args.stage!r} is not in the topology -- it holds: {known}",
                file=sys.stderr,
            )
            return 2
        binder, problems = load_binder(Path(args.binder))
        if binder is None:
            for line in problems:
                print(line, file=sys.stderr)
            return 2
        # ! The two paths are resolved before the rule asks, and only here: a
        # binder writes its root relative to the directory the gather was run
        # from, so the same tree is spelled two ways and a comparison of what
        # was typed would refuse a stage that is correctly seeded.
        named = str(Path(args.revise).resolve()) if args.revise else ""
        read_from = {
            **binder.read_from,
            "root": str(Path(binder.read_from["root"]).resolve()),
        }
        why = seeded_from_problem(stage, named, read_from)
        if why:
            print(why, file=sys.stderr)
            return 2
        # ! Refused before anything is written. `dealt` raises on the two guards
        # over the whole stage, so a stage that does not fit leaves no copies
        # behind for a role to be handed.
        try:
            packets = dealt(binder, stage)
        except FAN_REFUSALS as exc:
            print(f"stage {stage.name!r}: {exc}", file=sys.stderr)
            return 2
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        binder_dir = out_dir / "binders"
        binder_dir.mkdir(parents=True, exist_ok=True)
        seen: dict[str, int] = {}
        for dispatch, (received, copy) in zip(stage.dispatches, packets, strict=True):
            n = seen[dispatch.role] = seen.get(dispatch.role, 0) + 1
            where = out_dir / f"{stage.name}_{dispatch.role}_{n}.json"
            where.write_text(_as_json(copy), encoding="utf-8", newline="")
            binder_path = binder_dir / where.name
            binder_path.write_text(
                _as_json(received.serialize()), encoding="utf-8", newline=""
            )
            places = sum(len(sheet["marks"]) for sheet in copy["sheets"])
            print(
                f"{where}: {places} places for {dispatch.role} to rule on; "
                f"{len(received.freeform)} freeform; binder {binder_path}"
            )
        return 0

    ap.print_usage()
    return 2
