"""The one entry point. `python -m comment_review <command> [args...]`.

!! A FILE INSIDE A PACKAGE CANNOT BE RUN BY PATH, which is what forces this.
The modules import each other by the package name, so `python .../census.py`
fails at the first import: run by path, the file's own directory goes on
`sys.path` and `comment_review` is not on it. Roy,
2026-08-24: *"The entry points get an actual entry point .py file and the
commands run through it not through the scripts that are doing double or triple
duty."*

! IT DISPATCHES BY REPLACING `argv` AND CALLS THE COMMAND'S OWN `main()`. Each
command still parses its own arguments exactly as it did as a loose script, so
no command's interface changed when it stopped being one -- which is what makes
the `SKILL.md` rewrite a one-for-one substitution rather than a new instruction.
"""

import importlib
import sys
from enum import StrEnum, auto

from comment_review.machine import constants


class Command(StrEnum):
    """A command name typed on the console, closed.

    `T1.15` of `docs/plans/0.2.4-the-mark-and-the-collator.md`: value DERIVED
    from the member name via `_generate_next_value_`, never hand-typed.
    `reading.series.Kind` set the StrEnum precedent but hand-types its own
    member values (`TRAILING = "trailing-comment"` is not `name.lower()`), so
    it is not itself an example of this derivation. A value carries an
    underscore where the module it names does (`prove_unchanged`, `taken_in`),
    so `.lower()` alone is what derives it.
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.lower()

    ADDRESSER = auto()
    CARRY = auto()
    CENSUS = auto()
    COLLATE = auto()
    COMPOSITOR = auto()
    DISTRIBUTE = auto()
    PROOF = auto()
    PROVE_UNCHANGED = auto()
    REFERRERS = auto()
    TAKEN_IN = auto()


#: The command modules, by the name typed on the console -- `Command`'s
#: companion tuple, in definition order. Membership is asked of this, never
#: of the `Command` class itself.
COMMANDS = tuple(Command)


def main(argv: list[str] | None = None) -> int:
    """Run one command.

    Args:
        argv: the console arguments WITHOUT the program name. `None` reads
            `sys.argv[1:]`, which is what `python -m` supplies.

    Returns:
        The command's exit code, or 2 when no command was named or the name is
        not one -- the same code every command uses for a usage error.
    """
    # ! ONCE, HERE. A Windows console is cp1252 and one non-ASCII glyph in a
    # report kills the run; every command emits prose, so the guard belongs at
    # the entry rather than in each of them.
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
