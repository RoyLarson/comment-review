"""Writes the fixture the middle-chain smoke test drives.

`docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`, "The
fixture", names this text verbatim: a short recursive Fibonacci with a
logging decorator, three trailing comments, three standalone comment runs,
two stacked decorators, a nested `def`, and a dunder-main block. Its structure
is fixed -- a later task plants decisions against specific addresses on it,
so the text here must not drift from what that table describes.
"""

import json
from pathlib import Path

#: The fixture, exactly as the spec's "The fixture" section shows it. Joined
#: as lines rather than a triple-quoted block, since the text itself holds
#: `"""` docstrings -- this needs no escaping, matching `tests/conftest.py`'s
#: `SAMPLE`.
FIXTURE = (
    '"""Fibonacci, counted so the recursion can be seen."""\n'
    "\n"
    "import functools\n"
    "\n"
    "# Module state, written by the wrapper and read by the caller.\n"
    "CALLS = 0  # every entry, memoised or not\n"
    "\n"
    "\n"
    "def logged(fn):\n"
    '    """Count each call and pass it through."""\n'
    "\n"
    "    @functools.wraps(fn)\n"
    "    def wrapper(n):\n"
    "        global CALLS\n"
    "        CALLS += 1  # the decorator's whole job\n"
    "        return fn(n)\n"
    "\n"
    "    return wrapper\n"
    "\n"
    "\n"
    "# The cache sits inside the decorator stack on purpose: logged sees\n"
    "# every call, cache sees only the misses.\n"
    "@logged\n"
    "@functools.cache\n"
    "def fib(n):\n"
    '    """The nth Fibonacci number, counting from fib(0) = 0."""\n'
    "    if n < 2:  # base case\n"
    "        return n\n"
    "    # Two calls per level, which is what the counter measures.\n"
    "    return fib(n - 1) + fib(n - 2)\n"
    "\n"
    "\n"
    'if __name__ == "__main__":\n'
    "    print(fib(10), CALLS)\n"
)


def write_fixture(root: Path) -> Path:
    """Write the fixture to `root / "fib.py"` and return its path.

    Written with an explicit LF newline: a later task diffs the proof
    against this file byte for byte, and `write_text`'s default newline
    translation would make the fixture differ by machine on a repo that
    mixes line endings.

    Args:
        root: the directory to write into. Not created here -- the caller's
            own tree, such as a smoke run's working directory, already exists.

    Returns:
        The path written.
    """
    path = root / "fib.py"
    path.write_text(FIXTURE, encoding="utf-8", newline="\n")
    return path


#: The chief's own prose for the `b9` recast -- text neither role proposed,
#: kept as its own file rather than typed inline into a JSON literal, matching
#: the "text never crosses the shell" rule the `mark` calls follow: a
#: multi-line value gets a file of its own rather than a string built by hand
#: at the call site.
RECAST_PROSE = (
    "# The cache and the counter measure different things, worth stating\n"
    "# separately. fib is cached; logged counts every call, cached or not."
)

#: The chief's dispositions for Task 9's plant -- one entry per place
#: `collate` carries forward (the three escalations and the one re-read),
#: matching the matrix's own "the chief" column. A carried-forward place with
#: no entry here is refused by `disposition`, by name.
DISPOSITIONS = [
    {
        "address": "fib.py@a3",
        "answer": "taken_in",
        "side": "original",
        "reason": (
            "three roles rewrote the same clause three ways; none reads as "
            "more correct than the wording already there"
        ),
    },
    {
        "address": "fib.py@b9",
        "answer": "recast",
        "prose": RECAST_PROSE,
        "reason": (
            "block-context and module-context each rewrote one verb "
            "differently; neither wording is preferred, so the paragraph is "
            "restated"
        ),
    },
    {
        "address": "fib.py@c1",
        "answer": "taken_in",
        "side": "block-context",
        "reason": (
            "cached matches the vocabulary the module docstring and b9's "
            "paragraph already use"
        ),
    },
    {
        "address": "fib.py@a2",
        "answer": "taken_in",
        "side": "function-context",
        "reason": (
            "function-context is the only role that read this place; its "
            "docstring is what lands"
        ),
    },
]


def write_texts(run: Path) -> dict[str, Path]:
    """Write the plant's file-carried values under `run`, and return their paths.

    Two values in Task 9's plant do not fit as CLI flags or as bare literals
    typed into a JSON file by hand: the `b9` recast's own two-line prose,
    kept as its own file, and the dispositions themselves, which
    `disposition`'s `--dispositions` flag always takes as a file.

    Args:
        run: the run directory the smoke script writes into. Not created
            here -- the caller's own run directory already exists.

    Returns:
        `{"recast_prose": path, "dispositions": path}`.
    """
    recast_path = run / "recast_prose.txt"
    recast_path.write_text(RECAST_PROSE, encoding="utf-8", newline="\n")

    dispositions_path = run / "dispositions.json"
    dispositions_path.write_text(
        json.dumps(DISPOSITIONS, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return {"recast_prose": recast_path, "dispositions": dispositions_path}
