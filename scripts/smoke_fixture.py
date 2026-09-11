"""Writes the fixture the middle-chain smoke test drives, and what lands on it.

`docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`, "The
fixture", names this text verbatim: a short recursive Fibonacci with a
logging decorator, three trailing comments, three standalone comment runs,
two stacked decorators, a nested `def`, and a dunder-main block. Its structure
is fixed -- `LANDINGS` and `DISPOSITIONS` below plant decisions against
specific addresses on it, so the text here must not drift from what those
tables describe.

`LANDINGS` names, per planted address, a `Landing`: the outcome (`"text"`,
`"removed"` or `"kept"`), what decides it, the paragraph as it will sit on
disk where the outcome is text, the `--false` and `--true` clauses beside it
for the two corrections whose landing IS the corrected side, since `mark`
needs both, and -- where the place was empty in `FIXTURE` -- the fixture line
the landing is set against. `DISPOSITIONS` is the chief's own ruling over
every place `collate` carries forward -- three escalations and seven
re-reads, one per `add` -- reading its `b9` recast prose out of `LANDINGS`
rather than holding a second copy. `write_texts` writes a file for every
text landing a `mark` call carries (two files for a correction's clauses,
one otherwise), plus `dispositions.json`; `b9` is recast in `DISPOSITIONS`,
so it gets no file and reaches the proof only inline.

`EXPECTED` is the text the proof's `fib.py` must read once the chain
closes, and `write_expected` writes it for the smoke script's `diff` stage.
"""

import json
from pathlib import Path
from typing import NamedTuple

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


class Landing(NamedTuple):
    """What one planted address lands as on disk, and what decides it.

    `outcome` is `"text"` where a paragraph lands, `"removed"` where the
    address holds nothing afterward (a drop, or the move's own vacated
    origin), or `"kept"` where the fixture's own wording stands (an
    escalation the original side won, or a query nothing else settles).
    `text` is set only where `outcome` is `"text"`, and holds the whole
    paragraph exactly as it will sit on disk -- a `c` place's separator and
    marker included. A role's `mark` call carries it as `--change` or
    `--true`, except where the chief recasts the place in `DISPOSITIONS`,
    whose own prose is the text.

    `route` says what decides the outcome, and has no default, so every
    entry states its own: `"mark"` where the fold settles the place from the
    roles' marks alone; `"disposition"` where `collate` carries the place
    forward and the chief's ruling in `DISPOSITIONS` decides it; `"query"`
    where a human query rides to the end, nothing rules, and the fixture's
    wording stands.

    `false` and `true` hold a correction's own clauses, bare, beside its
    landing -- set only for `c6` and `c1`, the two corrections whose
    landing IS the corrected side. `mark` needs both to derive the change
    itself (`desk.mark.claim_change` replaces `false` with `true` in the
    paragraph it seeded), so `write_texts` writes each to its own file.

    `line` is set only where the place was empty in `FIXTURE`, and names the
    1-based `FIXTURE` line the landing is set against: the declaring line an
    `a` goes directly below, the line of code a `c` sits beside, the line of
    code a `b`'s gap sits directly above -- or, for the closing gap `b17`,
    which has no code below it, the file's last line, which it follows.
    """

    outcome: str
    route: str
    text: str | None = None
    false: str | None = None
    true: str | None = None
    line: int | None = None


#: What the plant makes land at each planted address once the chain closes.
#: `docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`'s
#: "The scenario matrix" names the first nine of these addresses in prose,
#: and asks for one more found by `addresser` -- `b15`; the plant goes five
#: further, testing an `add` at other absent and already-filled places
#: across the `a`, `b` and `c` series. Ten entries carry text landed by a
#: `mark` call's `--change`, `--false` or `--true`: a role's own clause, the
#: move's destination, or one of seven `add`s -- one on the empty `a2`, one
#: on the empty `b15`, and five more on `a0`, `b8`, `b17`, `c3` and `c12`.
#: One entry, `b9`, carries the chief's own `recast` prose instead, reaching
#: the proof only through `dispositions.json`. Four carry no text: `outcome`
#: is `"removed"` where the drop or the move's own vacated origin leaves
#: nothing, and `"kept"` where the fixture's own wording stands. Each entry's
#: `route` names what decides it: the fold alone for `c6`, `b14`, `b1` and
#: `b0`; a human query left standing for `a1`; and `disposition` for the
#: other ten -- `c1`, `a3`, `b9` and the seven adds. `EXPECTED` below is
#: written from `FIXTURE` and this table.
LANDINGS: dict[str, Landing] = {
    # block-context's correction is the only one that lands at c6; the
    # other three roles mark a scope-declaring query instead of clean, so
    # the fold settles it.
    "fib.py@c6": Landing(
        "text",
        route="mark",
        text="  # the decorator's only job",
        false="the decorator's whole job",
        true="the decorator's only job",
    ),
    # collate escalates c1; disposition takes block-context's correction
    # over function-context's losing one, which replaces the same `false`.
    "fib.py@c1": Landing(
        "text",
        route="disposition",
        text="  # every entry, cached or not",
        false="memoised or not",
        true="cached or not",
    ),
    # the move's --change: b1's paragraph relocates to b0, unchanged, and
    # the fold settles the move. b0's gap sits above `import functools`.
    "fib.py@b0": Landing(
        "text",
        route="mark",
        text="# Module state, written by the wrapper and read by the caller.",
        line=3,
    ),
    # the add's --change: wrapper's docstring, indented to its body's depth,
    # below `def wrapper(n):`.
    "fib.py@a2": Landing(
        "text",
        route="disposition",
        text='        """Count each call, then pass it through."""',
        line=13,
    ),
    # collate escalates b9; disposition recasts it in the chief's own words,
    # over both roles' losing corrections -- no single mark call's --true
    # carries this text, so it reaches the proof only inline in
    # dispositions.json.
    "fib.py@b9": Landing(
        "text",
        route="disposition",
        text=(
            "# The cache and the counter measure different things, worth stating\n"
            "# separately. fib is cached; logged counts every call, cached or not."
        ),
    ),
    # the drop vacates b14, and the fold settles it; nothing replaces the
    # dropped paragraph.
    "fib.py@b14": Landing("removed", route="mark"),
    # the move vacates its own address, and the fold settles it; the text it
    # carried now lives at b0.
    "fib.py@b1": Landing("removed", route="mark"),
    # collate escalates a3; disposition keeps the original over all three
    # roles' losing corrections.
    "fib.py@a3": Landing("kept", route="disposition"),
    # block-context's query settles nothing and rides to the end; a1 is left
    # as it was.
    "fib.py@a1": Landing("kept", route="query"),
    # block-context's add, on an absent b above `return wrapper`, indented
    # to logged's own body depth.
    "fib.py@b8": Landing(
        "text",
        route="disposition",
        text="    # Counting done, wrapper is handed back unchanged.",
        line=18,
    ),
    # module-context's add, on an absent b at the foot, after the dunder-main
    # block -- Addressing #19's foot rule.
    "fib.py@b17": Landing(
        "text",
        route="disposition",
        text="# Nothing follows; running this module only prints one count.",
        line=34,
    ),
    # module-context's add, on the absent b above `if __name__ ==
    # "__main__":` -- the addresser row. smoke_middle.ps1 does not spell
    # this address: it asks `addresser` for the `b` place at line 33 and
    # marks the address that comes back.
    "fib.py@b15": Landing(
        "text",
        route="disposition",
        text="# Run directly, the module prints fib(10) and how many calls it took.",
        line=33,
    ),
    # function-context's add, on an absent c beside `@functools.wraps(fn)`.
    "fib.py@c3": Landing(
        "text",
        route="disposition",
        text="  # keeps wrapper's name and doc matching fn's own",
        line=12,
    ),
    # ownership-context's add, on a filled c that already holds `# base case`
    # beside `if n < 2:` -- the add's own change is what lands, not a merge
    # with what was there.
    "fib.py@c12": Landing(
        "text",
        route="disposition",
        text="  # 0 and 1 are already fibonacci numbers",
    ),
    # block-context's add, on a filled a -- the module docstring already
    # reads. Same rule: the add's own change replaces it outright.
    "fib.py@a0": Landing(
        "text",
        route="disposition",
        text=(
            '"""Fibonacci, counted so the recursion can be seen -- and why it is '
            'counted."""'
        ),
    ),
}

#: The chief's own rulings over the ten places `collate` carries forward
#: (three escalations and seven re-reads, one per `add`) -- `LANDINGS` above
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
        "prose": LANDINGS["fib.py@b9"].text,
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
        "address": "fib.py@b15",
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
        "reason": (
            "ownership-context's add is the only ruling that changes the "
            "paragraph; the other three roles read the place and clean it"
        ),
    },
    {
        "address": "fib.py@a0",
        "answer": "taken_in",
        "side": "block-context",
        "reason": (
            "block-context's add is the only ruling that changes the "
            "paragraph; the other three roles read the place and clean it"
        ),
    },
]


def write_texts(run: Path) -> dict[str, Path]:
    """Write the plant's landing texts to their own files, and dispositions.json.

    Every text landing a `mark` call carries gets a file that call passes
    as `@path`: one holding `text` for an `add` or the move's destination,
    or two -- `<part>-false.txt` and `<part>-true.txt` -- for the two
    corrections (`c6`, `c1`) whose `false` and `true` clauses `mark` needs
    separately, matching its own rule that a whole paragraph is passed by
    file while a one-line clause may go inline. A place the chief recasts in
    `DISPOSITIONS` -- `b9` -- is skipped: its text is the chief's own prose
    and no `mark` call carries it. This reads each disposition's `answer`
    to find it rather than checking its address by name.

    Args:
        run: the run directory the smoke script writes into. Not created
            here -- the caller's own run directory already exists.

    Returns:
        one path per file written, keyed by the address (`"<address>:false"`
        and `"<address>:true"` for a correction's pair), plus
        `"dispositions"` for `dispositions.json`.
    """
    paths: dict[str, Path] = {}
    recast = {d["address"] for d in DISPOSITIONS if d["answer"] == "recast"}
    for address, landing in LANDINGS.items():
        if landing.outcome != "text" or address in recast:
            continue
        part = address.split("@")[1]
        if landing.false is not None:
            for suffix, value in (("false", landing.false), ("true", landing.true)):
                path = run / f"{part}-{suffix}.txt"
                path.write_text(value, encoding="utf-8", newline="\n")
                paths[f"{address}:{suffix}"] = path
        else:
            path = run / f"{part}.txt"
            path.write_text(landing.text, encoding="utf-8", newline="\n")
            paths[address] = path

    dispositions_path = run / "dispositions.json"
    dispositions_path.write_text(
        json.dumps(DISPOSITIONS, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    paths["dispositions"] = dispositions_path
    return paths


#: What the proof's `fib.py` must read once the chain closes, written out by
#: hand from `FIXTURE` and the decisions in `LANDINGS` and `DISPOSITIONS` --
#: never taken from a proof the chain produced, since an expectation copied
#: from the output agrees with it by construction (`docs/gates.md`). Each text
#: landing sits at its place, the paragraphs `b14` drops and `b1` moves are
#: gone from where they stood, and every other line is `FIXTURE`'s.
#:
#: Blank lines follow `set_page` in `src/comment_review/results/compositor.py`.
#: A run of blank lines belongs to the place before it and is set where it
#: stood, so every blank line here but the last is one `FIXTURE` has. A `b`
#: added where the place before it owns blank lines sits below them and
#: directly on its own code: `b0` under the blank after `a0`, `b8` under the
#: one after `return fn(n)`, `b15` under the two after `fib`'s last line. The
#: places the drop and the move vacate owned no blank lines, so their
#: neighbours sit as they did. A `b` added past the last line of code takes a
#: blank line below it, so the file ends with the `b17` comment and then a
#: blank line.
EXPECTED = (
    '"""Fibonacci, counted so the recursion can be seen -- and why it is '
    'counted."""\n'
    "\n"
    "# Module state, written by the wrapper and read by the caller.\n"
    "import functools\n"
    "\n"
    "CALLS = 0  # every entry, cached or not\n"
    "\n"
    "\n"
    "def logged(fn):\n"
    '    """Count each call and pass it through."""\n'
    "\n"
    "    @functools.wraps(fn)  # keeps wrapper's name and doc matching fn's own\n"
    "    def wrapper(n):\n"
    '        """Count each call, then pass it through."""\n'
    "        global CALLS\n"
    "        CALLS += 1  # the decorator's only job\n"
    "        return fn(n)\n"
    "\n"
    "    # Counting done, wrapper is handed back unchanged.\n"
    "    return wrapper\n"
    "\n"
    "\n"
    "# The cache and the counter measure different things, worth stating\n"
    "# separately. fib is cached; logged counts every call, cached or not.\n"
    "@logged\n"
    "@functools.cache\n"
    "def fib(n):\n"
    '    """The nth Fibonacci number, counting from fib(0) = 0."""\n'
    "    if n < 2:  # 0 and 1 are already fibonacci numbers\n"
    "        return n\n"
    "    return fib(n - 1) + fib(n - 2)\n"
    "\n"
    "\n"
    "# Run directly, the module prints fib(10) and how many calls it took.\n"
    'if __name__ == "__main__":\n'
    "    print(fib(10), CALLS)\n"
    "# Nothing follows; running this module only prints one count.\n"
    "\n"
)


def write_expected(root: Path) -> Path:
    """Write `EXPECTED` to `root / "fib.py"` and return its path.

    Written with an explicit LF newline, as `write_fixture` writes, so it
    carries the line endings the proof sets from the fixture. The smoke
    script's `diff` stage compares the two with `git diff --no-index`, which
    under `core.autocrlf=true` reads a CRLF line as LF -- so that comparison
    does not see a line-ending difference, only a text one.

    Args:
        root: the directory to write into. Not created here -- the smoke
            script creates its run's `expected` directory first.

    Returns:
        The path written.
    """
    path = root / "fib.py"
    path.write_text(EXPECTED, encoding="utf-8", newline="\n")
    return path
