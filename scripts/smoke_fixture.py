"""Writes the middle-chain smoke test's two fixture files, and what lands on them.

`docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`, "The
fixture", names `fib.py`'s text verbatim: a short recursive Fibonacci with a
logging decorator, three trailing comments, three standalone comment runs,
two stacked decorators, a nested `def`, and a dunder-main block. `rate.py`
is the second file, beside it: one function holding a three-line comment of
two sentences and a trailing comment, the places a `patch`, an
`unable-to-determine` query and a composition are planted on, since every
prose place in `fib.py` already carries another row. Both structures are
fixed -- `LANDINGS`, `ANSWERS` and `DISPOSITIONS` below plant decisions
against specific addresses on them, so neither text may drift from what
those tables describe.

`LANDINGS` names, per planted address, a `Landing`: what lands there and
what decides it. `ADDRESSER_ROW` is the entry the smoke script finds through
`addresser` rather than by its address. `ANSWERS` is each role's answers to
the batch `collate` sends out for the one turn the smoke script runs, and
`write_answers` writes one file of them per role. `DISPOSITIONS` is the
chief's own ruling over every place the turn leaves carried forward.
`write_texts` writes the files the smoke script's `mark` calls read by
`@path` -- a file for every text a `mark` call carries, one per clause where
`mark` derives the change from a claim -- plus `dispositions.json` and
`addresser-row.json`.

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
    origin), or `"kept"` where the fixture's own wording stands (a place the
    chief rules for the original, or a query nothing else settles).
    `text` is set only where `outcome` is `"text"`, and holds the whole
    paragraph exactly as it will sit on disk -- a `c` place's separator and
    marker included. For an `add` or the move's destination, a role's `mark`
    call carries it as `--change`; for a correction or a patch the turn
    leaves alone, `mark` derives it from `claim`; where the chief recasts the
    place in `DISPOSITIONS`, the recast prose is the text; where the turn
    settles the place on a text of its own, it is the `change` the place's
    answers in `ANSWERS` carry.

    `route` says what decides the outcome, and has no default, so every
    entry states its own: `"mark"` where the fold settles the place from the
    roles' marks alone; `"turn"` where the fold settles it once the turn's
    answers are applied; `"disposition"` where the place is still carried
    forward after the turn and the chief's ruling in `DISPOSITIONS` decides
    it; `"query"` where a human query rides to the end, nothing rules, and
    the fixture's wording stands.

    `claim` holds the clauses of a mark whose change `mark` derives, bare
    and keyed as `mark`'s flags name them -- `false` and `true` for
    `fib.py`'s corrections `c6` and `c1`, `from` and `to` for `rate.py`'s
    patch `c3`. `mark` needs both to derive the change itself
    (`desk.mark.derived_change` replaces the quoted clause with the other in
    the paragraph the row seeded), and the smoke script passes each by
    `@path` from the file `write_texts` writes for it.

    `marked` is set only where the turn leaves something other than the
    first-round mark's change to land, and holds that change: at `c1`, what
    `mark` derives from `claim`, which the turn's answers replace; at `c12`,
    what the `add`'s `mark` call carries as `--change`, which a human query
    in the turn keeps off the page.

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
    marked: str | None = None
    line: int | None = None


#: What the plant makes land at each planted address once the chain closes.
#: `docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`'s
#: "The scenario matrix" lists paths through the middle, not addresses; each
#: of its rows is planted at one or more of these. It asks for an `add` at an
#: empty place and one fed by the addresser lookup -- `a2` and `b15` -- and the
#: plant adds at five places more: the empty `b8`, `b17` and `c3`, and the
#: filled `a0` and `c12`. Its `patch`, `unable-to-determine` query and
#: composition rows are planted on `rate.py`, and its turn row is `ANSWERS`
#: below. `EXPECTED` and `RATE_EXPECTED` below are written from the two
#: fixtures, this table and `ANSWERS`.
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
    # collate escalates c1: block-context and function-context each replace
    # the same `false`. In the turn block-context corrects its change to
    # this text and function-context patches its own to the same, so the
    # fold settles the two as one text. `marked` is block-context's
    # first-round change, which the turn replaced.
    "fib.py@c1": Landing(
        "text",
        route="turn",
        text="  # every call, cached or not",
        claim={"false": "memoised or not", "true": "cached or not"},
        marked="  # every entry, cached or not",
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
    # collate escalates b9. In the turn block-context holds its correction
    # and module-context withdraws its own, which leaves block-context's a
    # lone mark and the place still carried forward; disposition recasts it
    # in the chief's own words -- no mark call's --true and no turn answer
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
    # collate escalates a3. In the turn block-context and function-context
    # withdraw and module-context holds, which leaves module-context's a
    # lone correction and the place still carried forward; disposition
    # keeps the original over it.
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
    # beside `if n < 2:`. In the turn module-context answers the composition
    # with a human-review query, so the place rides to the end unruled and
    # `# base case` stands. `marked` is the add's own change, which its
    # `mark` call carries.
    "fib.py@c12": Landing(
        "kept",
        route="query",
        marked="  # 0 and 1 are already fibonacci numbers",
    ),
    # block-context's add, on a filled a -- the module docstring already
    # reads. The add's own change replaces it outright rather than merging
    # with what was there: in the turn all four roles clean the composition,
    # and the fold settles it as one text.
    "fib.py@a0": Landing(
        "text",
        route="turn",
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
    # In the turn block-context answers the composed text with a correct and
    # function-context with a patch, each rewording the middle line the same
    # way, so the fold settles the two as one text.
    "rate.py@b1": Landing(
        "text",
        route="turn",
        text=(
            "    # No calls give a zero rate: nothing\n"
            "    # was put to the cache. The rate is\n"
            "    # hits over total, never more than one."
        ),
    ),
}

#: The `LANDINGS` entry smoke_middle.ps1 marks without spelling its address:
#: it asks `addresser` for the `b` place at this entry's `line`, and stops
#: unless the address that comes back is this one.
ADDRESSER_ROW = "fib.py@b15"

#: The places `collate` carries forward at an `add`. The turn's batch sends
#: each to all four roles, since an `add`'s place is re-read by every role
#: that read its page.
ADDED = (
    "fib.py@a0",
    "fib.py@c12",
    "fib.py@b8",
    "fib.py@c3",
    "fib.py@a2",
    "fib.py@b17",
    "fib.py@b15",
)

#: Each role's answers to the batch `collate` sends for the turn, keyed by
#: address and holding only the fields the role fills; `turn` lays them over
#: the slot it sent. An escalation (`c1`, `b9`, `a3`) takes `hold`,
#: `withdraw`, `correct` or `patch`, and a composition `clean`, `query`,
#: `correct` or `patch`; each of the eight is planted at least once, and a
#: role answers `clean` at every place in `ADDED` this gives it nothing for.
#: A composition `correct` or `patch` is planted only on `rate.py@b1`, whose
#: base is a real paragraph: at an `add`'s empty place there is no base
#: clause for one to quote. What each answer makes land is in `LANDINGS`.
ANSWERS: dict[str, dict[str, dict]] = {
    "block-context": {
        "fib.py@c1": {
            "instruction": "correct",
            "reason": "the counter counts calls, and entry says less than that",
            "change": LANDINGS["fib.py@c1"].text,
        },
        "fib.py@b9": {
            "instruction": "hold",
            "reason": "watches is still the verb for what logged does",
        },
        "fib.py@a3": {
            "instruction": "withdraw",
            "reason": "the docstring already says where the count starts",
        },
        "rate.py@b1": {
            "instruction": "correct",
            "claim": {
                "false": "was asked of the cache",
                "true": "was put to the cache",
            },
            "reason": "a call is put to the cache rather than asked of it",
            "sources": [
                {
                    "cite": "rate.py:3",
                    "verbatim": "# was asked of the cache. The rate is",
                }
            ],
            "change": LANDINGS["rate.py@b1"].text,
        },
    },
    "function-context": {
        "fib.py@c1": {
            "instruction": "patch",
            "reason": "every call reads closer to what wrapper increments on",
            "change": LANDINGS["fib.py@c1"].text,
        },
        "fib.py@a3": {
            "instruction": "withdraw",
            "reason": "the signature is described well enough as it stands",
        },
        "rate.py@b1": {
            "instruction": "patch",
            "claim": {
                "from": "was asked of the cache",
                "to": "was put to the cache",
            },
            "reason": "put to reads more plainly than asked of",
            "change": LANDINGS["rate.py@b1"].text,
        },
    },
    "module-context": {
        "fib.py@b9": {
            "instruction": "withdraw",
            "reason": "tracks and watches say the same, so mine adds nothing",
        },
        "fib.py@a3": {
            "instruction": "hold",
            "reason": "beginning at still matches the module docstring",
        },
        "fib.py@c12": {
            "instruction": "query",
            "claim": {
                "shape": "human-review-necessary",
                "attempted": "read the add against the base case it replaces",
                "settles": "human",
            },
            "reason": (
                "whether the base case needs more than its name is the author's call"
            ),
            "sources": [{"cite": "fib.py:27", "verbatim": "if n < 2:  # base case"}],
        },
    },
    "ownership-context": {},
}

#: The chief's own rulings over the seven places the turn leaves carried
#: forward -- `a3` and `b9`, each left a lone correction, and the five
#: `add`s at empty places, which every role cleans and the fold re-reads
#: again -- `LANDINGS` above names what each one makes land; this names
#: how. A carried-forward place with no entry here is refused by
#: `disposition`, by name, and so is an entry for a place that is not
#: carried forward.
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
]


def write_texts(run: Path) -> dict[str, Path]:
    """Write the plant's landing texts, dispositions.json and addresser-row.json.

    Every text a `mark` call carries gets a file that call passes as
    `@path`: one holding the text for an `add` or the move's destination --
    `marked` where the turn keeps it off the page, else `text` -- or one per
    `claim` key -- `<cue>-false.txt` and `<cue>-true.txt` for the two
    corrections (`fib.py`'s `c6`, `c1`), `<cue>-from.txt` and
    `<cue>-to.txt` for the patch (`rate.py`'s `c3`) -- whose clauses `mark`
    needs separately, matching its own rule that a whole paragraph is passed
    by file while a one-line clause may go inline. A file is named by its
    address's cue alone, not its page, so two landings sharing a cue and a
    suffix would write one file; the plant's do not. A place whose text no
    `mark` call carries is skipped: `fib.py`'s `b9`, which the chief
    recasts in `DISPOSITIONS` in its own prose, and `rate.py`'s `b1`, which
    the turn settles on the `change` its answers in `ANSWERS` carry. This
    reads each disposition's `answer` and each answer's `change` to find
    them rather than checking addresses by name. `addresser-row.json` holds
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
    turned = {
        address
        for given in ANSWERS.values()
        for address, fields in given.items()
        if "change" in fields
    }
    for address, landing in LANDINGS.items():
        part = address.split("@")[1]
        if landing.claim is not None:
            for key, value in landing.claim.items():
                path = run / f"{part}-{key}.txt"
                path.write_text(value, encoding="utf-8", newline="\n")
                paths[f"{address}:{key}"] = path
            continue
        carried = landing.marked
        if carried is None and address not in recast | turned:
            carried = landing.text
        if carried is None:
            continue
        path = run / f"{part}.txt"
        path.write_text(carried, encoding="utf-8", newline="\n")
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


def write_answers(run: Path) -> dict[str, Path]:
    """Write each role's answers to the turn's batch, one file per role.

    A role's file, `answers-<role>.json`, lists `{"address", **fields}` for
    each place `ANSWERS` answers for it, then `{"address", "instruction":
    "clean"}` for every place in `ADDED` it does not -- one answer for each
    slot the plant expects the batch to send the role. `check --answers`
    refuses a file that leaves a sent slot unanswered or answers one that
    was never sent.

    Args:
        run: the run directory the smoke script writes into. Not created
            here -- the caller's own run directory already exists.

    Returns:
        role -> the path written.
    """
    paths: dict[str, Path] = {}
    for role, given in ANSWERS.items():
        answers = [{"address": address, **fields} for address, fields in given.items()]
        answers += [
            {"address": address, "instruction": "clean"}
            for address in ADDED
            if address not in given
        ]
        path = run / f"answers-{role}.json"
        path.write_text(
            json.dumps(answers, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        paths[role] = path
    return paths


#: What the proof's `fib.py` must read once the chain closes, written out by
#: hand from `FIXTURE` and the decisions in `LANDINGS`, `ANSWERS` and
#: `DISPOSITIONS` -- never taken from a proof the chain produced, since an
#: expectation copied from the output agrees with it by construction
#: (`docs/gates.md`). Each text landing sits at its place, the paragraphs
#: `b14` drops and `b1` moves are gone from where they stood, and every other
#: line is `FIXTURE`'s.
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
    "CALLS = 0  # every call, cached or not\n"
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
    "    if n < 2:  # base case\n"
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
#: hand the same way from `RATE_FIXTURE`, `LANDINGS` and `ANSWERS`. Both
#: places were filled and each lands as many lines as it held, so the file is
#: `RATE_FIXTURE` with four lines changed: the paragraph's first and last,
#: which the two corrections touched, its middle, which the turn's answers
#: reword, and the line the patched trailing comment sits on.
RATE_EXPECTED = (
    "def rate(hits, total):\n"
    "    # No calls give a zero rate: nothing\n"
    "    # was put to the cache. The rate is\n"
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
