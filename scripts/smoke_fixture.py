"""Writes the middle-chain smoke test's two fixture files, and what lands on them.

`docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`, "The
fixture", names `fib.py`'s text verbatim: a short recursive Fibonacci with a
logging decorator, three trailing comments, three standalone comment runs,
two stacked decorators, a nested `def`, and a dunder-main block. `rate.py`
is the second file, beside it: one function holding a three-line comment of
two sentences and a trailing comment, the places a `patch`, an
`unable-to-determine` query and a composition are planted on, since every
prose place in `fib.py` already carries another row. Both structures are
fixed -- `LANDINGS` and `DISPOSITIONS` below plant decisions against
specific addresses on them, so neither text may drift from what those
tables describe.

`LANDINGS` names, per planted address, a `Landing`: what lands there and
what decides it. `ADDRESSER_ROW` is the entry the smoke script finds through
`addresser` rather than by its address. `DISPOSITIONS` is the chief's own
ruling over every place `collate` carries forward. `write_texts` writes the
files the smoke script's `mark` calls read by `@path` -- a file for every
text landing a `mark` call carries, one per clause where `mark` derives the
landing from a claim -- plus `dispositions.json` and `addresser-row.json`.

`EXPECTED` and `RATE_EXPECTED` are the texts the proof's `fib.py` and
`rate.py` must read once the chain closes, and `write_expected` writes them
for the smoke script's `diff` stage.
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

    Written with an explicit LF newline: the proof is set from this file,
    and the smoke script's `diff` stage compares the proof byte for byte
    with `EXPECTED`, which `write_expected` writes with LF too.
    `write_text`'s default newline translation would write CRLF on Windows.

    Args:
        root: the directory to write into. Not created here -- the caller's
            own tree, such as a smoke run's working directory, already exists.

    Returns:
        The path written.
    """
    path = root / "fib.py"
    path.write_text(FIXTURE, encoding="utf-8", newline="\n")
    return path


#: The second fixture file, `rate.py`. Its two prose places are the ones the
#: plant needs and `fib.py` cannot spare: `b1`, a comment of two sentences
#: whose first and last lines two roles each correct, with a line between so
#: the two edits do not touch; and `c3`, the trailing comment a `patch`
#: rewords.
RATE_FIXTURE = (
    "def rate(hits, total):\n"
    "    # Zero calls give a zero rate: nothing\n"
    "    # was asked of the cache. The rate is\n"
    "    # hits over total, never above one.\n"
    "    if total == 0:\n"
    "        return 0.0\n"
    "    return hits / total  # share of calls the cache answered\n"
)


def write_rate_fixture(root: Path) -> Path:
    """Write `RATE_FIXTURE` to `root / "rate.py"` and return its path.

    Written with an explicit LF newline, for the reason `write_fixture`
    gives.

    Args:
        root: the directory to write into, which `write_fixture` also writes
            into. Not created here.

    Returns:
        The path written.
    """
    path = root / "rate.py"
    path.write_text(RATE_FIXTURE, encoding="utf-8", newline="\n")
    return path


class Landing(NamedTuple):
    """What one planted address lands as on disk, and what decides it.

    `outcome` is `"text"` where a paragraph lands, `"removed"` where the
    address holds nothing afterward (a drop, or the move's own vacated
    origin), or `"kept"` where the fixture's own wording stands (an
    escalation the original side won, or a query nothing else settles).
    `text` is set only where `outcome` is `"text"`, and holds the whole
    paragraph exactly as it will sit on disk -- a `c` place's separator and
    marker included. For an `add` or the move's destination, a role's `mark`
    call carries it as `--change`; for a correction or a patch, `mark`
    derives it from `claim`; where the chief recasts the place in
    `DISPOSITIONS`, the recast prose is the text.

    `route` says what decides the outcome, and has no default, so every
    entry states its own: `"mark"` where the fold settles the place from the
    roles' marks alone; `"disposition"` where `collate` carries the place
    forward and the chief's ruling in `DISPOSITIONS` decides it; `"query"`
    where a human query rides to the end, nothing rules, and the fixture's
    wording stands.

    `claim` holds the clauses of a mark whose landing is its own derived
    change, bare and keyed as `mark`'s flags name them -- `false` and `true`
    for `fib.py`'s corrections `c6` and `c1`, `from` and `to` for
    `rate.py`'s patch `c3`. `mark` needs both to derive the change itself
    (`desk.mark.derived_change` replaces the quoted clause with the other in
    the paragraph the row seeded), and the smoke script passes each by
    `@path` from the file `write_texts` writes for it.

    `line` is set only where the place was empty in its file's fixture, and
    names the 1-based fixture line the landing is set against: the declaring
    line an `a` goes directly below, the line of code a `c` sits beside, the
    line of code a `b`'s gap sits directly above -- or, for the closing gap
    `b17`, which has no code below it, the file's last line, which it
    follows.
    """

    outcome: str
    route: str
    text: str | None = None
    claim: dict[str, str] | None = None
    line: int | None = None


#: What the plant makes land at each planted address once the chain closes.
#: `docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`'s
#: "The scenario matrix" lists paths through the middle, not addresses; each
#: of its rows is planted at one or more of these. It asks for an `add` at an
#: empty place and one fed by the addresser lookup -- `a2` and `b15` -- and the
#: plant adds at five places more: the empty `b8`, `b17` and `c3`, and the
#: filled `a0` and `c12`. The matrix names no `patch`, no `unable-to-determine`
#: query and no composition; the plant puts all three on `rate.py`. `EXPECTED`
#: and `RATE_EXPECTED` below are written from the two fixtures and this table.
LANDINGS: dict[str, Landing] = {
    # block-context's correction is the only one that lands at c6; the
    # other three roles mark a scope-declaring query instead of clean, so
    # the fold settles it.
    "fib.py@c6": Landing(
        "text",
        route="mark",
        text="  # the decorator's only job",
        claim={
            "false": "the decorator's whole job",
            "true": "the decorator's only job",
        },
    ),
    # collate escalates c1; disposition takes block-context's correction
    # over function-context's losing one, which replaces the same `false`.
    "fib.py@c1": Landing(
        "text",
        route="disposition",
        text="  # every entry, cached or not",
        claim={"false": "memoised or not", "true": "cached or not"},
    ),
    # the move's --change: b1's paragraph relocates to b0, unchanged, and
    # the fold settles the move. b0's gap sits above `import functools`.
    "fib.py@b0": Landing(
        "text",
        route="mark",
        text="# Module state, written by the wrapper and read by the caller.",
        line=3,
    ),
    # function-context's add, on the absent a below `def wrapper(n):` --
    # wrapper's docstring, indented to its body's depth.
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
    # module-context's add, on the absent closing gap after the dunder-main
    # block.
    "fib.py@b17": Landing(
        "text",
        route="disposition",
        text="# Nothing follows; running this module only prints one count.",
        line=34,
    ),
    # module-context's add, on the absent b above `if __name__ ==
    # "__main__":` -- `ADDRESSER_ROW`.
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
    # module-context's patch is the only mark that owes a change at c3.
    # function-context marks an unable-to-determine query and the other two
    # a scope-declaring one; a query of either shape abstains, so the fold
    # settles the patch alone.
    "rate.py@c3": Landing(
        "text",
        route="mark",
        text="  # fraction of calls the cache answered",
        claim={"from": "share of calls", "to": "fraction of calls"},
    ),
    # the composition: block-context corrects the first sentence on the
    # paragraph's first line, function-context the second on its last, and
    # collate composes the two and carries the place forward as a re-read.
    # disposition recasts it with the composed paragraph as the chief's own
    # prose, since a `taken_in` names one role and would land one sentence.
    "rate.py@b1": Landing(
        "text",
        route="disposition",
        text=(
            "    # No calls give a zero rate: nothing\n"
            "    # was asked of the cache. The rate is\n"
            "    # hits over total, never more than one."
        ),
    ),
}

#: The `LANDINGS` entry smoke_middle.ps1 marks without spelling its address:
#: it asks `addresser` for the `b` place at this entry's `line`, and stops
#: unless the address that comes back is this one.
ADDRESSER_ROW = "fib.py@b15"

#: The chief's own rulings over the eleven places `collate` carries forward
#: (three escalations and eight re-reads, one per `add` and one for the
#: composition) -- `LANDINGS` above names what each one makes land; this
#: names how. A carried-forward place with no entry here is refused by
#: `disposition`, by name.
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
    {
        "address": "rate.py@b1",
        "answer": "recast",
        "prose": LANDINGS["rate.py@b1"].text,
        "reason": (
            "block-context and function-context each corrected a different "
            "sentence; the chief takes both, as the composition reads"
        ),
    },
]


def write_texts(run: Path) -> dict[str, Path]:
    """Write the plant's landing texts, dispositions.json and addresser-row.json.

    Every text landing a `mark` call carries gets a file that call passes
    as `@path`: one holding `text` for an `add` or the move's destination,
    or one per `claim` key -- `<cue>-false.txt` and `<cue>-true.txt` for the
    two corrections (`fib.py`'s `c6`, `c1`), `<cue>-from.txt` and
    `<cue>-to.txt` for the patch (`rate.py`'s `c3`) -- whose clauses `mark`
    needs separately, matching its own rule that a whole paragraph is passed
    by file while a one-line clause may go inline. A file is named by its
    address's cue alone, not its page, so two landings sharing a cue and a
    suffix would write one file; the plant's do not. A place the chief
    recasts in `DISPOSITIONS` -- `fib.py`'s `b9`, `rate.py`'s `b1` -- is
    skipped: its text is the chief's own prose and no `mark` call carries
    it. This reads each disposition's `answer` to find it rather than
    checking its address by name. `addresser-row.json` holds
    `ADDRESSER_ROW` and its `line`, which the smoke script reads to ask
    `addresser` and to check what it answers.

    Args:
        run: the run directory the smoke script writes into. Not created
            here -- the caller's own run directory already exists.

    Returns:
        one path per file written, keyed by the address (`"<address>:<key>"`
        for each `claim` key), plus `"dispositions"` for `dispositions.json`
        and `"addresser-row"` for `addresser-row.json`.
    """
    paths: dict[str, Path] = {}
    recast = {d["address"] for d in DISPOSITIONS if d["answer"] == "recast"}
    for address, landing in LANDINGS.items():
        if landing.text is None or address in recast:
            continue
        part = address.split("@")[1]
        if landing.claim is not None:
            for key, value in landing.claim.items():
                path = run / f"{part}-{key}.txt"
                path.write_text(value, encoding="utf-8", newline="\n")
                paths[f"{address}:{key}"] = path
        else:
            path = run / f"{part}.txt"
            path.write_text(landing.text, encoding="utf-8", newline="\n")
            paths[address] = path

    dispositions_path = run / "dispositions.json"
    dispositions_path.write_text(
        json.dumps(DISPOSITIONS, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    paths["dispositions"] = dispositions_path

    row_path = run / "addresser-row.json"
    row = {"address": ADDRESSER_ROW, "line": LANDINGS[ADDRESSER_ROW].line}
    row_path.write_text(json.dumps(row) + "\n", encoding="utf-8", newline="\n")
    paths["addresser-row"] = row_path
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


#: What the proof's `rate.py` must read once the chain closes, written out by
#: hand the same way from `RATE_FIXTURE` and `LANDINGS`. Both places were
#: filled and each lands as many lines as it held, so the file is
#: `RATE_FIXTURE` with three lines changed: the paragraph's first and last,
#: which the two corrections touched, and the line the patched trailing
#: comment sits on.
RATE_EXPECTED = (
    "def rate(hits, total):\n"
    "    # No calls give a zero rate: nothing\n"
    "    # was asked of the cache. The rate is\n"
    "    # hits over total, never more than one.\n"
    "    if total == 0:\n"
    "        return 0.0\n"
    "    return hits / total  # fraction of calls the cache answered\n"
)


def write_expected(root: Path) -> tuple[Path, Path]:
    """Write `EXPECTED` to `root / "fib.py"` and `RATE_EXPECTED` to `root / "rate.py"`.

    Written with an explicit LF newline, as `write_fixture` writes, so each
    carries the line endings the proof sets from its fixture. The smoke
    script's `diff` stage compares this directory with the proof's using
    `git diff --no-index` under `core.autocrlf=false`, so a line-ending
    difference fails it as a text one does.

    Args:
        root: the directory to write into. Not created here -- the smoke
            script creates its run's `expected` directory first.

    Returns:
        The two paths written, `fib.py`'s first.
    """
    fib = root / "fib.py"
    fib.write_text(EXPECTED, encoding="utf-8", newline="\n")
    rate = root / "rate.py"
    rate.write_text(RATE_EXPECTED, encoding="utf-8", newline="\n")
    return fib, rate
