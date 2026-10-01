"""The `topology` command: does a topology fit this binder, and write one that does.

    comment_review topology --verify T.toml --binder B.json
    comment_review topology --build --binder B.json --out T.toml
        --stage 4a=ownership-context
        --stage 4c=block-context/2,function-context,module-context

The work is `flows.topology`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.

! VERIFY BEFORE A PAGE IS READ. A bad configuration costs nothing only when
it is caught here -- `fan` refuses the same shapes, but from inside a run,
blaming the tree for the topology's assumption (`Process: #55`). `--build`
verifies what it wrote, so a built topology is a verified one.

! EXIT CODES. 0 fits; 1 does not fit, one misfit per line as
`<stage>  <kind>  <detail>`; 2 the file itself is refused -- `read`'s
reason under the `reads` kind -- or an input could not be read.
"""

import argparse
import sys
from pathlib import Path

from comment_review.desk.topology import read
from comment_review.flows.proof_io import load_binder
from comment_review.flows.topology import Directive, compose, fit
from comment_review import constants


def _directive(spec: str) -> Directive:
    """One `--stage` value, `NAME=role[/ways],...`, as a directive.

    `4c=block-context/2,function-context` is
    `("4c", [("block-context", 2), ("function-context", 1)])`.
    """
    name, _, roles = spec.partition("=")
    if not name or not roles:
        raise ValueError(f"--stage {spec!r}: want NAME=role[/ways],role[/ways]")
    out: list[tuple[str, int]] = []
    for item in roles.split(","):
        role, _, ways = item.partition("/")
        out.append((role.strip(), int(ways) if ways else 1))
    return name, out


def main() -> int:
    """Verify a topology against a binder, or build one for it."""
    constants.utf8_console()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verify", metavar="T.toml", help="the topology to check")
    ap.add_argument(
        "--build", action="store_true", help="compose a topology for the binder"
    )
    ap.add_argument("--binder", required=True, help="the binder the topology must fit")
    ap.add_argument(
        "--stage",
        action="append",
        default=[],
        help="NAME=role[/ways],... in run order (--build)",
    )
    ap.add_argument("--out", help="where the built topology is written (--build)")
    args = ap.parse_args()

    binder, problems = load_binder(Path(args.binder))
    if binder is None:
        for line in problems:
            print(line, file=sys.stderr)
        return 2

    if args.build:
        if not args.out or not args.stage:
            print("--build needs --out and at least one --stage", file=sys.stderr)
            return 2
        try:
            text = compose([_directive(s) for s in args.stage], binder)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        target = Path(args.out)
        target.write_text(text, encoding="utf-8", newline="")
    elif args.verify:
        target = Path(args.verify)
        text = target.read_text(encoding="utf-8")
    else:
        ap.print_usage()
        return 2

    stages, why = read(text)
    if why:
        print(f"reads  {why}", file=sys.stderr)
        return 2
    misfits = sorted(fit(stages, binder))
    for m in misfits:
        print(f"{m.stage}  {m.kind}  {m.detail}")
    if misfits:
        return 1
    print(f"{target} fits {args.binder}: {len(stages)} stages")
    return 0
