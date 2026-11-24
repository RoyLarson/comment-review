"""The package's entry point. `python -m comment_review <command> [args...]`.

A file inside a package cannot be run by path, which is what forces this.
The modules import each other by the package name, so `python .../gather.py`
fails at the first import: run by path, the file's own directory goes on
`sys.path` and `comment_review` is not on it.

It dispatches by replacing `argv` and calling the command's own `main()`.
"""

import importlib
import sys
from enum import StrEnum, auto

from comment_review import constants


class Command(StrEnum):
    """A command name typed on the console, closed.

    Each value is derived from the member name via `_generate_next_value_`, never
    hand-typed. A value carries an underscore where the module it names does
    (`prove_unchanged`), so `.lower()` alone is what derives it.
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.lower()

    ADDRESSES = auto()
    CHECK = auto()
    COLLATE = auto()
    COMPARE = auto()
    COMPOSITOR = auto()
    DISPOSITION = auto()
    DISTRIBUTE = auto()
    GATHER = auto()
    LOST = auto()
    MARK = auto()
    PROOF = auto()
    PROVE_UNCHANGED = auto()
    REFERRERS = auto()
    STAGE = auto()
    TOPOLOGY = auto()
    TURN = auto()


#: The command names typed on the console -- `Command`'s companion tuple, in
#: definition order. Membership is asked of this, never of the `Command` class
#: itself: on Python 3.11, `in` over an enum class raises `TypeError` for a
#: string that is not a member.
COMMANDS = tuple(Command)


def main(argv: list[str] | None = None) -> int:
    """Run one command.

    Args:
        argv: the console arguments WITHOUT the program name. `None` reads
            `sys.argv[1:]`, which is what `python -m` supplies.

    Returns:
        The command's exit code, 0 for `-h` or `--help`, or 2 when no command
        was named or the name is not one -- the same code every command uses
        for a usage error.
    """
    # A Windows console is cp1252 and one non-ASCII glyph in a report kills the
    # run; every command emits prose, so the guard runs here, at the entry.
    constants.utf8_console()
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] in ("-h", "--help"):
        print("usage: python -m comment_review <command> [args...]\n")
        print("commands:")
        for name in COMMANDS:
            print(f"    {name}")
        # ! A bare invocation is a USAGE ERROR, not a success. A run that names
        # no command has done nothing, and a zero would tell a caller it worked.
        return 0 if args else 2
    name, rest = args[0], args[1:]
    if name not in COMMANDS:
        print(f"error: no command named {name!r}", file=sys.stderr)
        print(f"commands: {', '.join(COMMANDS)}", file=sys.stderr)
        return 2
    module = importlib.import_module(f".commands.{name}", __package__)
    # !! `argv` IS REBUILT SO EACH COMMAND PARSES WHAT IT ALWAYS PARSED. Its
    # own `argparse` reads `sys.argv[1:]`, and its usage line names `prog`,
    # which is why the command's name is put back at position 0.
    sys.argv = [f"comment_review {name}", *rest]
    return module.main()


if __name__ == "__main__":
    sys.exit(main())
