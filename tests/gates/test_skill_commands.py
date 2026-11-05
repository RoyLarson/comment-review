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

SKILL_DIR = ROOT / "src" / "plugin" / "skills" / "comment-review"

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

#: The bare lowercase word after the name, continuation lines joined in: the
#: subcommand of a command that has subcommands.
WORD = re.compile(r"\s*([a-z][\w-]*)\b")

#: A long flag anywhere after the name -- `--repo`, `--out`, and so on.
FLAG = re.compile(r"--[\w-]+")


def _invocations(
    paths=AGENT_FACING,
) -> list[tuple[str, str | None, list[str], str, int]]:
    """`(command name, the word after it, flags found beside it, filename,
    1-based line)` for every invocation in `paths`, the agent-facing files by
    default.

    ! A CONTINUATION LINE (ending `\\`) IS JOINED IN, so a flag on the second
    line of a two-line invocation -- `proof --repo . --from-docket D.json \\` then
    `  --out DIR` -- is not missed.
    """
    found: list[tuple[str, str | None, list[str], str, int]] = []
    for path in paths:
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
            word = WORD.match(text.replace("\\", " "))
            found.append(
                (
                    name,
                    word.group(1) if word else None,
                    FLAG.findall(text),
                    path.name,
                    start + 1,
                )
            )
            i += 1
    return found


def _flags_of(command: str, word: str | None = None) -> set[str] | None:
    """The long option strings `commands.<command>.main`'s own parser
    accepts, read from the parser itself rather than re-typed here.

    ! A COMMAND WITH SUBCOMMANDS is answered from the subcommand `word` names,
    so a flag is checked against the parser that takes it -- `addresses find
    --file` passes, and `addresses resolve --file` does not. `None` when the
    command has subcommands and `word` names none of them.

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
    subcommands = [
        a for a in parser._actions if isinstance(a, argparse._SubParsersAction)
    ]
    if subcommands:
        if word not in subcommands[0].choices:
            return None
        chosen = subcommands[0].choices[word]
        assert isinstance(chosen, argparse.ArgumentParser)
        parser = chosen
    return {opt for opt in parser._option_string_actions if opt.startswith("--")}


def _unaccepted(invocations) -> list[tuple[str, str, str, int]]:
    """`(flag, command, filename, line)` for each flag its command refuses.

    A subcommand the command does not have is reported as its own row, with the
    word in place of a flag.
    """
    from comment_review.__main__ import COMMANDS

    bad = []
    for name, word, flags, path, line in invocations:
        if name not in COMMANDS:
            continue  # the other test already reports this invocation
        accepted = _flags_of(name, word)
        if accepted is None:
            bad.append((f"subcommand {word!r}", name, path, line))
            continue
        for flag in flags:
            if flag not in accepted:
                bad.append((flag, name, path, line))
    return bad


def test_every_command_named_in_agent_facing_prose_exists():
    from comment_review.__main__ import COMMANDS

    bad = [
        (name, path, line)
        for name, _word, _flags, path, line in _invocations()
        if name not in COMMANDS
    ]
    assert not bad, f"named a command not in COMMANDS: {bad}"


def test_every_flag_named_beside_it_is_accepted_by_that_command():
    bad = _unaccepted(_invocations())
    assert not bad, f"flag not accepted by its command's own parser: {bad}"


def test_a_flag_on_the_wrong_subcommand_is_refused():
    """The subcommand reading can fail: `--file` belongs to `addresses find`,
    so naming it beside `addresses resolve` is a row, and so is a subcommand
    the command does not have."""
    bad = _unaccepted(
        [
            ("addresses", "resolve", ["--file"], "probe", 1),
            ("addresses", "find", ["--file", "--line", "--series"], "probe", 2),
            ("addresses", "lookup", [], "probe", 3),
        ]
    )
    assert bad == [
        ("--file", "addresses", "probe", 1),
        ("subcommand 'lookup'", "addresses", "probe", 3),
    ]


def test_a_subcommand_on_a_continuation_line_is_read(tmp_path):
    """A command name ending its line still has its subcommand read from the
    next, as its flags are."""
    prose = tmp_path / "prose.md"
    prose.write_text(
        "python <skill>/scripts/comment-review.py addresses \\\n"
        "  find --repo <R> --file <p> --line 1 --series f\n",
        encoding="utf-8",
    )
    found = _invocations([prose])
    assert [word for _, word, *_ in found] == ["find"]
    assert _unaccepted(found) == []


#: The files the task agent reads. Stages 7a and 7b set pages from the closed
#: master proof, so every `proof` they run takes `--proof`; `--copy` sets one
#: role's own draft, which the brief hands the reviewers.
TASK_AGENT_FILES = (
    SKILL_DIR / "SKILL.md",
    SKILL_DIR / "references" / "write.md",
)


def proof_from_a_copy(paths=TASK_AGENT_FILES) -> list[tuple[list[str], str, int]]:
    """Every `proof` invocation in `paths` that sets pages from something
    other than the master proof: `(its flags, filename, 1-based line)`."""
    return [
        (flags, path, line)
        for name, _word, flags, path, line in _invocations(paths)
        if name == "proof" and ("--proof" not in flags or "--copy" in flags)
    ]


def test_the_task_agent_sets_pages_from_the_master_proof():
    bad = proof_from_a_copy()
    assert not bad, f"a task-agent `proof` that does not read --proof: {bad}"
