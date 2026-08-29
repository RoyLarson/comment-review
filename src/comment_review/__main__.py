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

from comment_review.machine import constants

# The command modules, by the name typed on the console.
COMMANDS = (
    "addresser",
    "carry",
    "census",
    "compositor",
    "mark",
    "proof",
    "prove_unchanged",
    "referrers",
    "taken_in",
)

# An older name that still resolves to a real command's module. `galley` ->
# `proof`: `SKILL.md` still invokes `galley` at stage 7a, and that file is
# `agents` lane -- rewiring the stage name is
# `TODO/the-skill-names-commands-that-moved-to-prototype.md`. Roy, 2026-08-26:
# "Create the galley entry_point function that points to proof_setter and
# delete the unused command," and on the shape: "there is no reason to go to
# the galley for something that proof-setter is supposed to do." See
# `docs/history.md`.
#
# ! THE NAME CARRIES OVER; THE FLAGS DO NOT. `galley` used to take `--census`
# and `--edits`; `proof` takes `--binder` and `--docket`, so a skill run
# typed under the old flags reaches `proof`'s parser and is refused as an
# unrecognised argument -- an alias resolves the NAME, nothing more.
#
# ! NOT IN THE HELP LISTING OR THE UNKNOWN-NAME ERROR: both exist to tell a
# reader what to type, and this name is deprecated -- nobody should be
# choosing it fresh. It still has to RESOLVE for the one caller (`SKILL.md`)
# that already types it.
ALIASES = {
    "galley": "proof",
}


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
    # A name is valid when it is a command OR resolves through ALIASES to
    # one; `target` is what gets imported either way.
    target = ALIASES.get(name, name)
    if target not in COMMANDS:
        print(f"error: no command named {name!r}", file=sys.stderr)
        print(f"commands: {', '.join(COMMANDS)}", file=sys.stderr)
        return 2
    module = importlib.import_module(f".commands.{target}", __package__)
    # !! `argv` IS REBUILT SO EACH COMMAND PARSES WHAT IT ALWAYS PARSED. Its
    # own `argparse` reads `sys.argv[1:]`, and its usage line names `prog`,
    # which is why the command's name is put back at position 0 -- the name
    # TYPED, not `target`, so an alias still names itself in its own usage
    # line even though another module's parser is what answers it.
    sys.argv = [f"comment_review {name}", *rest]
    return module.main()


if __name__ == "__main__":
    sys.exit(main())
