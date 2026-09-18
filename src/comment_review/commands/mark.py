"""The `mark` command: one ruling, placed on a role's edit copy from the console.

    comment_review mark --edit-copy COPY --address ADDRESS --instruction correct \
        --false "the clause as it stands" --true "the clause as it should read" \
        --reason "..." --cite pkg/mod.py:12 [--ran "rg -n ..."] [--repo ROOT]
    comment_review mark --edit-copy COPY --address ADDRESS --withdraw

`--withdraw` takes back every ruling the copy holds at `--address`, handing a
seeded slot back as it was seeded, so a role places its ruling again rather
than editing the JSON (`mark-defects` T24, `flows.fill.withdraw`).

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`. The flow is
`flows.fill`; this parses the console and reads and writes the copy.

!! ONE INVOCATION PER RULING, ONE FLAG PER FIELD, AND ANY VALUE MAY BE
`@path`. Roy, 2026-09-07, extending the 2026-08-17 ruling that no multi-line
value passes through a shell: *"Can we just tell the cli which file to read
for the text? And leave everything else in the cli pieces?"* A value spelled
`@path` is read from that file, so a clause that wraps a comment line or a
`change` that is a whole paragraph never crosses the shell; a one-line clause
goes inline. And *"a false clause is one statement not multiple paragraphs"*,
so the ordinary case is inline.

! THE CLAIM'S KEYS ARE FLAGS BY NAME -- `--false --true` for a `correct`,
`--from --to` for a `patch` or a `move`, `--drop`, `--missing --anchor` for an
`add`, `--shape --attempted --settles` for a `query`. A flag the instruction's
row does not carry is refused by name, and a missing one is named by
`desk.marks.mark.Mark.deserialize`, so a role learns the contract from the refusal.

! A SOURCE IS `--cite`, AND `--verbatim` OR `--ran` BINDS TO THE `--cite`
BEFORE IT. Ruled 2026-09-07. A `--cite` with no `--verbatim` has the cited
line read out of the checkout by the flow.

! `--anchor-line` IS NOT `--anchor`. The first is the line of code a slot
CREATED here sits on -- an `add` at an empty place, which the binder does not
carry -- as the addresser printed it. The second is `add`'s claim key: the
anchor NAMED in backticks.

`--change` is the text that moves or arrives and `--raw-text` is the
paragraph it lands in -- `decision-log.md Process: #172`, `#175` and `#176`.
An `add` gives the snippet in `--change` and the paragraph as it will read in
`--raw-text`; a `move` gives the snippet subtracted from the origin and the
destination paragraph as it will read. `--raw-text` is owed on every `move`
and on an `add` at a place that already holds prose; at an empty place the
two are the same text and it may be left off. Every other instruction takes
its paragraph from the page and is refused a `--raw-text`.

! NO BULK PASS OF ANY KIND. Roy, 2026-09-07: a flag that marks every null
slot `clean` *"invites skipping reviewing each paragraph"*; each role
certifies each paragraph under its remit, one invocation at a time.
"""

import argparse
import sys
from pathlib import Path

from comment_review.desk.marks.table import INSTRUCTIONS
from comment_review.flows.fill import fill, withdraw
from comment_review.flows.proof_io import load_copy, save_wire
from comment_review.machine import constants, exceptions
from comment_review.machine.repo import read_raw

#: Exit codes -- `check`'s. `BROKEN` is a ruling the flow refused, with the
#: reasons on stdout; `UNREADABLE` is a copy that is not one, or a usage error.
OK = 0
BROKEN = 1
UNREADABLE = 2

#: Every claim key any row names, in the order `docs/the-mark.md` lists the
#: rows. Each is a flag; which ones an instruction accepts is its row's
#: `claim_all`.
CLAIM_FLAGS = tuple(
    dict.fromkeys(key for spec in INSTRUCTIONS.values() for key in spec.claim_all)
)

#: The prefix that says "read this value from a file".
FROM_FILE = "@"


class _Source(argparse.Action):
    """`--cite` opens a source; `--verbatim` and `--ran` land on the last one."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values,
        option_string: str | None = None,
    ) -> None:
        sources = getattr(namespace, self.dest, None) or []
        if option_string == "--cite":
            sources.append({"cite": values})
        elif not sources:
            parser.error(f"{option_string} needs a --cite before it")
        else:
            sources[-1][str(option_string).lstrip("-")] = values
        setattr(namespace, self.dest, sources)


def _names_a_file(value: str) -> bool:
    """Whether `value` is an `@path` -- the prefix and something after it."""
    return value.startswith(FROM_FILE) and len(value) > 1


def _from_file(value: str) -> tuple[str | None, str]:
    """The text of the file an `@path` value names, or None and why not.

    The file's line endings become LF, whatever it was written with: a slot's
    `raw_text` is the page's lines joined on LF, so that is the form a
    `change` or a clause is compared against, and a CRLF scratch file on
    Windows would otherwise never match.
    """
    path = Path(value[1:])
    try:
        return constants.LINE_BREAK.sub("\n", read_raw(path)), ""
    except exceptions.READ_ERRORS as err:
        return None, f"cannot read {path}: {err}"


def _expanded(argv: list[str]) -> tuple[list[str], list[str]]:
    """`argv` with every `@path` value replaced by that file's text.

    A value is read from its file whether it stands as its own token or
    follows a flag's `=` -- `--true=@path`, which argparse reads as it reads
    `--true @path`. Only the first form was read until `mark-defects` T23,
    so the second saved the literal path as the clause and inside the derived
    change. A flag is never a path, and neither is a lone `@`.
    """
    out: list[str] = []
    problems: list[str] = []
    for token in argv:
        flag, eq, value = token.partition("=")
        if token.startswith("--") and eq and _names_a_file(value):
            text, why = _from_file(value)
        elif _names_a_file(token) and not token.startswith("-"):
            flag, eq = "", ""
            text, why = _from_file(token)
        else:
            out.append(token)
            continue
        if text is None:
            problems.append(why)
        else:
            out.append(f"{flag}{eq}{text}")
    return out, problems


def _entry(args: argparse.Namespace) -> tuple[dict, list[str]]:
    """The ruling as `flows.fill` takes it, or the claim flags the row refuses."""
    spec = INSTRUCTIONS[args.instruction]
    given = {key: getattr(args, key) for key in CLAIM_FLAGS if getattr(args, key)}
    stray = sorted(set(given) - set(spec.claim_all))
    if stray:
        return {}, [
            f"{args.instruction} carries no {', '.join('--' + k for k in stray)}"
            + (
                f" -- its claim is {', '.join('--' + k for k in spec.claim_all)}"
                if spec.claim_all
                else " -- it carries no claim"
            )
        ]
    entry: dict = {"address": args.address, "instruction": args.instruction}
    if given:
        entry["claim"] = given
    for key in ("reason", "change", "raw_text"):
        if getattr(args, key) is not None:
            entry[key] = getattr(args, key)
    if args.sources:
        entry["sources"] = args.sources
    if args.anchor_line:
        entry["anchor"] = args.anchor_line
    return entry, []


def main() -> int:
    """Place one ruling on the copy and say so, or say why it was refused.

    Returns:
        `OK` with the placed mark named on stdout; `BROKEN` with every reason
        on stdout and the copy untouched; `UNREADABLE` when the copy or a
        `@path` cannot be read.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--edit-copy", required=True, metavar="PATH", help="the role's copy"
    )
    ap.add_argument(
        "--address", required=True, help="the place, as the slot carries it"
    )
    ap.add_argument(
        "--instruction",
        choices=sorted(INSTRUCTIONS),
        help="one of the seven; required unless --withdraw",
    )
    ap.add_argument(
        "--withdraw",
        action="store_true",
        help="take back every ruling placed at --address, and place nothing",
    )
    for key in CLAIM_FLAGS:
        ap.add_argument(f"--{key}", help=f"claim.{key}")
    ap.add_argument("--reason", help="what you derived, and why the claim is wrong")
    ap.add_argument(
        "--change",
        help="the updated paragraph as raw text; derived where the row quotes",
    )
    ap.add_argument(
        "--raw-text",
        dest="raw_text",
        help="for an add or a move: the paragraph as it will read, with the"
        " added or moved text in",
    )
    ap.add_argument(
        "--cite", dest="sources", action=_Source, metavar="PATH:LINE", help="one source"
    )
    ap.add_argument(
        "--verbatim", dest="sources", action=_Source, help="the text at the last --cite"
    )
    ap.add_argument(
        "--ran", dest="sources", action=_Source, help="the command that settled it"
    )
    ap.add_argument(
        "--anchor-line",
        help="the line of code a slot created here sits on, as addresser printed it",
    )
    ap.add_argument("--repo", help="the checkout a bare --cite is read from")
    argv, why = _expanded(sys.argv[1:])
    if why:
        for line in why:
            print(line, file=sys.stderr)
        return UNREADABLE
    args = ap.parse_args(argv)
    if args.withdraw and args.instruction:
        ap.error("--withdraw takes back what is placed; it takes no --instruction")
    if not args.withdraw and not args.instruction:
        ap.error("--instruction is required, unless --withdraw")

    copy_path = Path(args.edit_copy)
    copy, why = load_copy(copy_path)
    if why:
        for line in why:
            print(line, file=sys.stderr)
        return UNREADABLE
    if args.withdraw:
        _, why = withdraw(copy, args.address, Path(args.repo) if args.repo else None)
        if why:
            for line in why:
                print(line)
            return BROKEN
        save_wire(copy_path, copy)
        print(f"{args.address}: withdrawn from {copy_path}")
        return OK
    entry, why = _entry(args)
    if not why:
        _, why = fill(copy, entry, Path(args.repo) if args.repo else None)
    if why:
        for line in why:
            print(line)
        return BROKEN
    save_wire(copy_path, copy)
    print(f"{args.address}: {args.instruction} placed on {copy_path}")
    return OK


if __name__ == "__main__":
    sys.exit(main())
