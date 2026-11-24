"""The `topology` command: does a topology fit this binder, and write one that does.

    comment_review topology --verify T.toml --binder B.json
    comment_review topology --build --binder B.json --out T.toml
        --stage 4a=ownership-context
        --stage 4c=block-context/2,function-context,module-context
    comment_review topology --build --binder B.json --run <run-dir>
        [--repo <checkout>] [--ref <pre-edit commit> <paths...>]
        --stage 4a=ownership-context --stage 4c=block-context,...
        --stage 6=block-context --cap 6=<cap> --series 6=b,c
        --admits 6=patch,drop,add,clean,query

The work is `flows.topology`; this is only the console face of it.

! Verify before a page is read. A bad configuration costs nothing only when
it is caught here -- `stage open` refuses the same shapes through
`flows.fan_out.partition`, but from inside a run, blaming the tree for the
topology's assumption. `--build`
verifies what it wrote, so a built topology is a verified one.

`--run` writes the built rows into `<run-dir>/jacket.json` once they fit. A
run with no jacket yet needs `--ref` and the scope's paths, which create it;
`--ref` is resolved in `--repo` (default `.`) and the jacket records the
commit's full sha. A jacket already there keeps the ref and scope it records.
`--cap`, `--series` and `--admits` each take `NAME=value` and add that key to
the named stage's row.

! Exit codes. 0 fits; 1 does not fit, one misfit per line as
`<stage>  <kind>  <detail>`; 2 the file itself is refused (`read`'s
reason under the `reads` kind) or cannot be read, the binder could not be
read, the jacket could not be written, or the arguments are not usable.
`--out` is written only on exit 0, so a refusal leaves no file behind.
"""

import argparse
import sys
from pathlib import Path

from comment_review import constants, exceptions
from comment_review.desk.topology import read
from comment_review.flows.jacket import JACKET_FILE, put_topology
from comment_review.flows.proof_io import load_binder
from comment_review.flows.topology import Directive, RowKeys, compose, fit


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


def _keys(args: argparse.Namespace) -> RowKeys:
    """The `--cap`, `--series` and `--admits` values, by stage name."""
    keys: RowKeys = {}
    for key in ("cap", "series", "admits"):
        for spec in getattr(args, key):
            name, _, value = spec.partition("=")
            if not name or not value:
                raise ValueError(f"--{key} {spec!r}: want NAME=value")
            keys.setdefault(name, {})[key] = (
                int(value) if key == "cap" else value.split(",")
            )
    return keys


def main() -> int:
    """Verify a topology against a binder, or build one for it."""
    # `__main__.main` already runs this guard for every command, so this call
    # repeats it.
    constants.utf8_console()
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--verify", metavar="T.toml", help="the topology to check")
    mode.add_argument(
        "--build", action="store_true", help="compose a topology for the binder"
    )
    ap.add_argument("--binder", required=True, help="the binder the topology must fit")
    ap.add_argument(
        "--stage",
        action="append",
        default=[],
        help="NAME=role[/ways],... in run order (--build)",
    )
    for key, what in (
        ("cap", "NAME=lines"),
        ("series", "NAME=b,c"),
        ("admits", "NAME=instruction,..."),
    ):
        ap.add_argument(
            f"--{key}",
            action="append",
            default=[],
            metavar=what,
            help=f"add `{key}` to that stage's row (--build)",
        )
    ap.add_argument("--out", help="where the built topology is written (--build)")
    ap.add_argument(
        "--run", help="the run directory whose jacket receives the rows (--build)"
    )
    ap.add_argument("--ref", default="", help="the pre-edit commit, for a new jacket")
    ap.add_argument(
        "--repo", default=".", help="the checkout `--ref` is resolved in (--run)"
    )
    ap.add_argument("paths", nargs="*", help="the scope, for a new jacket")
    args = ap.parse_args()

    binder, problems = load_binder(Path(args.binder))
    if binder is None:
        for line in problems:
            print(line, file=sys.stderr)
        return 2

    if args.build:
        if not (args.out or args.run) or not args.stage:
            print("--build needs --out or --run, and a --stage", file=sys.stderr)
            return 2
        try:
            text = compose([_directive(s) for s in args.stage], binder, _keys(args))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        target = Path(args.out) if args.out else Path(args.run) / JACKET_FILE
    elif args.verify:
        target = Path(args.verify)
        try:
            text = target.read_text(encoding="utf-8")
        except exceptions.READ_ERRORS as exc:
            print(f"{target}: cannot be read: {exc}", file=sys.stderr)
            return 2
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
    if args.build and args.run:
        refused = put_topology(
            Path(args.run), text, args.ref, tuple(args.paths), Path(args.repo)
        )
        if refused:
            for line in refused:
                print(line, file=sys.stderr)
            return 2
    if args.build and args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="")
    print(f"{target} fits {args.binder}: {len(stages)} stages")
    return 0
