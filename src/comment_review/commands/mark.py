"""The `mark` command: one ruling, placed on a role's edit copy from the console.

    comment_review mark --edit-copy COPY --address ADDRESS --instruction correct \
        --false "the clause as it stands" --true "the clause as it should read" \
        --reason "..." --cite pkg/mod.py:12 [--ran "rg -n ..."] [--repo ROOT]
    comment_review mark --edit-copy COPY --address ADDRESS --withdraw \
        --instruction drop [--quote "the clause it quotes"]

`--withdraw` takes back the one ruling of `--instruction` the copy holds at
`--address`, so a role places it again rather than editing the JSON; where two
of that instruction are placed there, `--quote` names the one. The other
rulings at the address stay. With the last one gone, `check` reads the place
from the binder as still owed (`flows.fill.withdraw`).

The flow is `flows.fill`; this parses the console and reads and writes the copy.
The ruling is admitted against `--repo`, or the checkout the copy's own
`read_from` names, as `collate` admits the copy.

One invocation per ruling, one flag per field, and any value may be `@path`. A
value spelled `@path` is read from that file, so a clause that wraps a comment
line or a `change` that is a whole paragraph never crosses the shell; a
one-line clause goes inline. A false clause is one statement, not several
paragraphs, so the ordinary case is inline.

! The claim's keys are flags by name -- `--false --true` for a `correct`,
`--from --to` for a `patch` or a `move`, `--drop`, `--missing --anchor` for an
`add`, `--shape --attempted --settles` for a `query`. A flag the instruction's
type does not carry is refused by name, and a missing one is named by the
type's own read, so a role learns the contract from the refusal.

A source is `--cite`, and `--verbatim` or `--ran` binds to the `--cite`
before it. A `--cite` with no `--verbatim` has the cited line read out of the
checkout by the flow.

`--change` is the text that moves or arrives and `--raw-text` is the
paragraph it lands in.
An `add` gives the snippet in `--change` and the paragraph as it will read in
`--raw-text`; a `move` gives the snippet subtracted from the origin and the
destination paragraph as it will read. `--raw-text` is owed on every `move`
and on an `add` at a place that already holds prose; at an empty place the
two are the same text and it may be left off. Every other instruction takes
its paragraph from the page, and a `--raw-text` given to it is ignored.

Exits `OK` with the placed mark named on stdout, `BROKEN` with the flow's
reasons on stdout and the copy untouched, and `UNREADABLE` on stderr when the
copy or an `@path` cannot be read or a page identity the copy claims will not
admit -- the same 0, 1 and 2 as `check`.

There is no bulk pass of any kind. A flag that marks every null slot `clean`
would invite skipping the review of each paragraph; each role certifies each
paragraph under its remit, one invocation at a time.
"""

import argparse
import sys
from pathlib import Path

from comment_review import constants, exceptions
from comment_review.commands.report import BROKEN, OK, UNREADABLE, refused
from comment_review.desk.marks.table import INSTRUCTIONS
from comment_review.desk.proof.mark import Instruction, mark_type
from comment_review.flows.fill import admitted, fill, withdraw
from comment_review.flows.proof_io import load_copy, save_wire
from comment_review.machine.repo import read_raw

#: Every claim key any type names, in the order `docs/the-mark.md` lists the
#: instructions. Each is a flag; which ones an instruction accepts is its
#: type's `claim_all`.
CLAIM_FLAGS = tuple(
    dict.fromkeys(key for name in INSTRUCTIONS for key in mark_type(name).claim_all)
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
    `--true @path`. A flag is never a path, and neither is a lone `@`.
    A value that opens with `@` and has more after it is always read as a
    path; a literal one is passed in a file.
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
    """The ruling as `flows.fill` takes it, or the claim flags the type refuses."""
    spec = mark_type(Instruction(args.instruction))
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
    return entry, []


def _root_of(copy: dict) -> Path | None:
    """The checkout a copy's own `read_from` names, or None where it names none."""
    read_from = copy.get("read_from")
    root = read_from.get("root") if isinstance(read_from, dict) else None
    return Path(root) if isinstance(root, str) and root else None


def main() -> int:
    """Place one ruling, or withdraw one at `--address`; say so, or say why not.

    Returns:
        `OK` with the placed mark named on stdout; `BROKEN` with every reason
        on stdout and the copy untouched; `UNREADABLE` when the copy or a
        `@path` cannot be read, or a page identity it claims will not admit.
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
        help="one of the seven; with --withdraw, the one taken back",
    )
    ap.add_argument(
        "--withdraw",
        action="store_true",
        help="take back the --instruction placed at --address, and place nothing",
    )
    ap.add_argument(
        "--quote",
        help="with --withdraw, where two of --instruction are placed: the clause"
        " the one taken back quotes, or its change where it quotes none",
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
        "--repo",
        help="the checkout a --cite is read from and the ruling admitted against"
        " (default: the copy's own read_from.root)",
    )
    argv, why = _expanded(sys.argv[1:])
    if why:
        for line in why:
            print(line, file=sys.stderr)
        return UNREADABLE
    args = ap.parse_args(argv)
    if not args.instruction:
        ap.error("--instruction is required, and with --withdraw names what goes")
    if args.quote is not None and not args.withdraw:
        ap.error("--quote names a ruling to withdraw; it takes --withdraw")
    # A withdraw places nothing, so a flag that only placing reads is refused
    # rather than ignored. An argparse group cannot say this: it would also make
    # the placing flags exclude each other.
    placing = (*CLAIM_FLAGS, "reason", "change", "raw_text")
    if args.withdraw and (
        args.sources or any(getattr(args, key) is not None for key in placing)
    ):
        ap.error("--withdraw places nothing; it takes no claim, source or text flag")

    copy_path = Path(args.edit_copy)
    copy, why = load_copy(copy_path)
    if why:
        for line in why:
            print(line, file=sys.stderr)
        return UNREADABLE
    # The copy's pages are admitted once, here: a page identity that will not
    # admit is an input that cannot be read, not a ruling to send back.
    imprints, why, unadmitted = admitted(copy)
    if unadmitted:
        return refused(unadmitted)
    if why:
        for line in why:
            print(line)
        return BROKEN
    if args.withdraw:
        _, why = withdraw(
            copy, args.address, args.instruction, args.quote, imprints=imprints
        )
        if why:
            for line in why:
                print(line)
            return BROKEN
        save_wire(copy_path, copy)
        print(f"{args.address}: withdrawn from {copy_path}")
        return OK
    entry, why = _entry(args)
    if not why:
        root = Path(args.repo) if args.repo else _root_of(copy)
        _, why = fill(copy, entry, root, imprints)
    if why:
        for line in why:
            print(line)
        return BROKEN
    save_wire(copy_path, copy)
    print(f"{args.address}: {args.instruction} placed on {copy_path}")
    return OK


if __name__ == "__main__":
    sys.exit(main())
