"""Writes the fixture the middle-chain smoke test drives, and what lands on it.

`docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`, "The
fixture", names this text verbatim: a short recursive Fibonacci with a
logging decorator, three trailing comments, three standalone comment runs,
two stacked decorators, a nested `def`, and a dunder-main block. Its structure
is fixed -- a later task plants decisions against specific addresses on it,
so the text here must not drift from what that table describes.

`LANDINGS` names, per planted address, the text the plant makes reach the
proof, or `None` where the outcome leaves no text at all -- a drop, a
vacated origin, or an address left as the fixture already reads. `DISPOSITIONS`
is the chief's own ruling over each place `collate` escalates, reading its
`b9` recast prose out of `LANDINGS` rather than holding a second copy.
`write_texts` writes the nine addresses `LANDINGS` gives text that a `mark`
call plants, one file each, plus `dispositions.json`.
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


#: What the plant makes land at each planted address once the chain closes --
#: the same outcomes `docs/superpowers/specs/2026-09-08-the-middle-chain-
#: smoke-design.md`'s "The scenario matrix" describes in prose, held here by
#: address instead. Nine entries carry text: a role's own clause, the move's
#: destination, or one of six `add`s -- one on the empty `a2`, and five more
#: testing an `add` at other absent and already-filled places across the `a`,
#: `b` and `c` series. One entry carries the chief's own `recast` prose; four
#: carry no text at all, because the outcome drops the paragraph, vacates its
#: origin, or leaves the fixture as it already reads. Task 10 diffs `FIXTURE`
#: against this table to know what the closed proof should read at each
#: address.
LANDINGS = {
    # block-context's --true clause is the only mark at c6; it lands as is.
    "fib.py@c6": "the decorator's only job",
    # collate escalates c1; disposition takes block-context's --true clause
    # over function-context's losing one.
    "fib.py@c1": "cached or not",
    # the move's --change: b1's paragraph relocates to b0, reworded there.
    "fib.py@b0": "# Module state, written by the wrapper and read by the caller.",
    # the add's --change: wrapper's docstring, indented to its body's depth.
    "fib.py@a2": '        """Count each call, then pass it through."""',
    # collate escalates b9; disposition recasts it in the chief's own words,
    # over both roles' losing corrections.
    "fib.py@b9": (
        "# The cache and the counter measure different things, worth stating\n"
        "# separately. fib is cached; logged counts every call, cached or not."
    ),
    # the drop vacates b14; nothing replaces the dropped paragraph.
    "fib.py@b14": None,
    # the move vacates its own address; the text it carried now lives at b0.
    "fib.py@b1": None,
    # collate escalates a3; disposition keeps the original over all three
    # roles' losing corrections.
    "fib.py@a3": None,
    # block-context's query settles nothing; a1 is left as it was.
    "fib.py@a1": None,
    # block-context's add, on an absent b above `return wrapper`.
    "fib.py@b8": "# Counting done, wrapper is handed back unchanged.",
    # module-context's add, on an absent b at the foot, after the dunder-main
    # block -- Addressing #19's foot rule.
    "fib.py@b17": "# Nothing follows; running this module only prints one count.",
    # function-context's add, on an absent c beside `@functools.wraps(fn)`.
    "fib.py@c3": "  # keeps wrapper's name and doc matching fn's own",
    # ownership-context's add, on a filled c that already holds `# base case`
    # beside `if n < 2:` -- the add's own change is what lands, not a merge
    # with what was there.
    "fib.py@c12": "  # 0 and 1 are already fibonacci numbers",
    # block-context's add, on a filled a -- the module docstring already
    # reads. Same rule: the add's own change replaces it outright.
    "fib.py@a0": (
        '"""Fibonacci, counted so the recursion can be seen -- and why it is '
        'counted."""'
    ),
}

#: The chief's own rulings over the nine places `collate` carries forward
#: (three escalations and six re-reads, one per `add`) -- `LANDINGS` above
#: names what each one makes land; this names how. A carried-forward place
#: with no entry here is refused by `disposition`, by name.
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
        "prose": LANDINGS["fib.py@b9"],
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
    {
        "address": "fib.py@b8",
        "answer": "taken_in",
        "side": "block-context",
        "reason": "block-context is the only role that read this place",
    },
    {
        "address": "fib.py@b17",
        "answer": "taken_in",
        "side": "module-context",
        "reason": "module-context is the only role that read this place",
    },
    {
        "address": "fib.py@c3",
        "answer": "taken_in",
        "side": "function-context",
        "reason": "function-context is the only role that read this place",
    },
    {
        "address": "fib.py@c12",
        "answer": "taken_in",
        "side": "ownership-context",
        "reason": "ownership-context is the only role that read this place",
    },
    {
        "address": "fib.py@a0",
        "answer": "taken_in",
        "side": "block-context",
        "reason": "block-context is the only role that read this place",
    },
]


def write_texts(run: Path) -> dict[str, Path]:
    """Write the plant's landing texts to their own files, and dispositions.json.

    `LANDINGS` names nine addresses whose text a single `mark` call plants
    on a role's copy -- `c6`, `c1`, the move's destination `b0`, and six
    `add`s (`a0`, `a2`, `b8`, `b17`, `c3`, `c12`) -- and one, `b9`, that only
    `disposition` reads, inline out of `dispositions.json`; `b9` gets no file
    of its own here. Each of the nine files holds exactly the text `LANDINGS`
    names, with no trailing newline, so the `mark` call that plants it can
    pass `@<path>` rather than the text itself, matching the "text never
    crosses the shell" rule every `mark` call follows.

    Args:
        run: the run directory the smoke script writes into. Not created
            here -- the caller's own run directory already exists.

    Returns:
        one path per file written, keyed by the address whose text it holds,
        plus `"dispositions"` for `dispositions.json`.
    """
    paths: dict[str, Path] = {}
    for address, text in LANDINGS.items():
        if text is None or address == "fib.py@b9":
            continue
        path = run / f"{address.split('@')[1]}.txt"
        path.write_text(text, encoding="utf-8", newline="\n")
        paths[address] = path

    dispositions_path = run / "dispositions.json"
    dispositions_path.write_text(
        json.dumps(DISPOSITIONS, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    paths["dispositions"] = dispositions_path
    return paths
