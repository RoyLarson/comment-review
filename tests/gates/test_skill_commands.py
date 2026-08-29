"""Every command an agent is told to run exists, and every flag it is given parses.

! EXPECTATION FROM `__main__.py`'s COMMANDS and each command's own argparse --
neither of which is the prose under test. `SKILL.md` and the three
`references/*.md` files it dispatches from are read as PROSE, never imported,
so a rename in the code cannot make this gate pass by accident.

    uv run pytest -q tests/gates/test_skill_commands.py

! THE NAME HALF IS NOT ENOUGH ON ITS OWN. `galley` was the case that proved
it: the name used to resolve through an alias to `proof`, and the invocation
still could not run because it spelled flags `proof`'s parser refused. The
alias is gone (`docs/history.md`, 2026-08-28) -- every name in agent-facing
prose must now be a real entry in `COMMANDS`, with nothing standing in for it.
"""

import argparse
import importlib
import re

from conftest import ROOT

SKILL_DIR = ROOT / "plugins" / "comment-review" / "skills" / "comment-review"

#: Every file an agent reads that may name a command. Matches
#: `docs/plans/0.2.4-the-mark-and-the-collator.md` T1.11's own list.
AGENT_FACING = (
    SKILL_DIR / "SKILL.md",
    SKILL_DIR / "references" / "write.md",
    SKILL_DIR / "references" / "review.md",
    SKILL_DIR / "references" / "reviewer-brief.md",
)

#: `comment-review.py <name>` -- the name is the first token after the
#: script, never a flag (a flag starts with `-`).
INVOCATION = re.compile(r"comment-review\.py\s+(\S+)")

#: A long flag anywhere after the name -- `--repo`, `--out`, and so on.
FLAG = re.compile(r"--[\w-]+")


def _invocations() -> list[tuple[str, list[str], str, int]]:
    """`(command name, flags found beside it, filename, 1-based line)` for
    every invocation in the agent-facing files.

    ! A CONTINUATION LINE (ending `\\`) IS JOINED IN, so a flag on the second
    line of a two-line invocation -- `proof --repo . --docket D.json \\` then
    `  --out DIR` -- is not missed.
    """
    found: list[tuple[str, list[str], str, int]] = []
    for path in AGENT_FACING:
        lines = path.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(lines):
            match = INVOCATION.search(lines[i])
            if not match:
                i += 1
                continue
            name = match.group(1)
            start = i
            text = lines[i][match.end() :]
            while lines[i].rstrip().endswith("\\") and i + 1 < len(lines):
                i += 1
                text += " " + lines[i]
            found.append((name, FLAG.findall(text), path.name, start + 1))
            i += 1
    return found


def _flags_of(command: str) -> set[str]:
    """The long option strings `commands.<command>.main`'s own parser
    accepts, read from the parser itself rather than re-typed here.

    !! CAPTURED BY MONKEYPATCHING `parse_args`, NOT BY RUNNING THE COMMAND.
    Every one of these `main()` functions builds its `ArgumentParser`, calls
    `add_argument` on it, and then calls `parse_args()` before doing anything
    else -- so patching `parse_args` to record `self` and raise stops the
    function at exactly that point, before any file is read or written.
    """
    module = importlib.import_module(f"comment_review.commands.{command}")
    captured: list[argparse.ArgumentParser] = []
    real_parse_args = argparse.ArgumentParser.parse_args

    def _capture(self, *args, **kwargs):
        captured.append(self)
        raise SystemExit(0)

    argparse.ArgumentParser.parse_args = _capture
    try:
        try:
            module.main()
        except SystemExit:
            pass
    finally:
        argparse.ArgumentParser.parse_args = real_parse_args
    assert len(captured) == 1, f"{command}.main() built {len(captured)} parsers"
    (parser,) = captured
    return {opt for opt in parser._option_string_actions if opt.startswith("--")}


def test_every_command_named_in_agent_facing_prose_exists():
    from comment_review.__main__ import COMMANDS

    bad = [
        (name, path, line)
        for name, _flags, path, line in _invocations()
        if name not in COMMANDS
    ]
    assert not bad, f"named a command not in COMMANDS: {bad}"


def test_every_flag_named_beside_it_is_accepted_by_that_command():
    from comment_review.__main__ import COMMANDS

    bad = []
    for name, flags, path, line in _invocations():
        if name not in COMMANDS:
            continue  # the other test already reports this invocation
        accepted = _flags_of(name)
        for flag in flags:
            if flag not in accepted:
                bad.append((flag, name, path, line))
    assert not bad, f"flag not accepted by its command's own parser: {bad}"
