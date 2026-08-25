"""Where the tests find the package, its module sources, and its commands.

`unittest discover -s tests` puts this directory on `sys.path`, and pytest does
the same because `tests/` itself holds no `__init__.py` -- so test modules in
any subdirectory import this by bare name. Both runners work and neither is
going away.

!! THE PACKAGE IS IMPORTED, NOT PATH-INSERTED PER MODULE. `src/` goes on the
path once, here, and every test then writes `from comment_review.binder import
page` -- the same import the shipped code uses. Before 2026-08-24 this inserted
a directory of loose scripts, so a test imported `page` by a bare name that
existed nowhere else.

! THREE THINGS ARE NEEDED AND THEY ARE NOT THE SAME. Importing a module is one;
READING its source, which the boundary tests do, is another and needs a PATH;
RUNNING a command is a third and needs an argv, because a module inside a
package cannot be run by path.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PKG = SRC / "comment_review"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

# !! THE SKILL DID NOT MOVE, AND MOST OF `references/` DID NOT EITHER. `SKILL.md`
# and the `.md` references are read by AGENTS; only `vocabulary.toml` is read by
# code, so only it travels with the package. A test that reached the skill by
# walking up from a module's `__file__` was reading the two as one directory.
SKILL = ROOT / "plugins/comment-review/skills/comment-review"
REFERENCES = SKILL / "references"
VOCABULARY = PKG / "references" / "vocabulary.toml"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# !! AND ON `PYTHONPATH`, FOR THE CHILDREN. A subprocess does not inherit this
# process's `sys.path` -- it inherits the ENVIRONMENT -- so a test that runs a
# command would import nothing without this. Set once here rather than as an
# `env=` argument at each of the 27 call sites, which is 27 places to forget.
_pp = os.environ.get("PYTHONPATH", "")
if str(SRC) not in _pp.split(os.pathsep):
    os.environ["PYTHONPATH"] = os.pathsep.join(p for p in (str(SRC), _pp) if p)

# !! LIBRARY MODULES ONLY, KEYED BY STEM -- `commands/` is excluded because it
# shares stems with what it exposes. `commands/census.py` and `flows/census.py`
# are two files named `census`, and a map holding both would answer whichever
# was walked last.
MODULES = {
    p.stem: p
    for p in sorted(PKG.rglob("*.py"))
    if p.parent.name != "commands" and not p.stem.startswith("__")
}


COMMANDS = {
    p.stem: p
    for p in sorted((PKG / "commands").glob("*.py"))
    if not p.stem.startswith("__")
}


def source_of(name: str) -> str:
    """The text of one library module, for a test that READS rather than runs."""
    return MODULES[name].read_text(encoding="utf-8")


def command_source(name: str) -> str:
    """The text of one COMMAND module.

    ! A separate function rather than a wider `source_of`, because the two
    share stems: `commands/census.py` and `flows/census.py` are both `census`,
    and a test asking for one must not silently get the other.
    """
    return COMMANDS[name].read_text(encoding="utf-8")


def cli(name: str) -> list[str]:
    """The argv prefix that runs one command as a subprocess.

    ! `-m` IS NOT A STYLE CHOICE. Every module imports its siblings relatively,
    so `python .../census.py` fails at the first import with no package to
    resolve against. The entry point is the only way in.

    Args:
        name: the command. A trailing `.py` is accepted and dropped -- callers
            named a FILE for as long as one existed, and the two spellings mean
            the same command.
    """
    return [sys.executable, "-m", "comment_review", name.removesuffix(".py")]
