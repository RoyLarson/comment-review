"""Writes the middle-chain smoke test's two fixture files, and what lands on them.

`docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`, "The
fixture", names `fib.py`'s text verbatim: a short recursive Fibonacci with a
logging decorator, three trailing comments, three standalone comment runs,
two stacked decorators, a nested `def`, and a dunder-main block. `rate.py`
is the second file, beside it: `rate`, holding a three-line comment of two
sentences and a trailing comment, and `share`, holding a one-line comment
with a blank line below it -- the places a `patch`, an
`unable-to-determine` query, a composition and a `drop` of a place that
owns a leading are planted on, since every prose place in `fib.py` already
carries another row. Both structures are
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
for the smoke script's `diff` stage. `ROLE_DRAFT` and `ROLE_RATE_DRAFT` are
what `proof --copy` drafts from `DRAFTED_ROLE`'s own copy before the fold, and
`write_role_draft` writes them for the smoke script's `draft` stage.
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


#: The second fixture file, `rate.py`. Its three prose places are the ones
#: the plant needs and `fib.py` cannot spare: `b1`, a comment of two
#: sentences whose first and last lines two roles each correct, with a line
#: between so the two edits do not touch; `c3`, the trailing comment a
#: `patch` rewords; and `b5`, the comment in `share` a `drop` vacates, whose
#: blank line below it is the leading `d1` it owns.
RATE_FIXTURE = (
    "def rate(hits, total):\n"
    "    # Zero calls give a zero rate: nothing\n"
    "    # was asked of the cache. The rate is\n"
    "    # hits over total, never above one.\n"
    "    if total == 0:\n"
    "        return 0.0\n"
    "    return hits / total  # share of calls the cache answered\n"
    "\n"
    "\n"
    "def share(hits, total):\n"
    "    # Kept for callers that ask for a share rather than a rate.\n"
    "\n"
    "    return rate(hits, total)\n"
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
    chief rules for the original, a place every role cleans, or a query
    nothing else settles).
    `text` is set only where `outcome` is `"text"`, and holds the whole
    paragraph exactly as it will sit on disk -- a `c` place's separator and
    marker included. For an `add` or the move's destination, a role's `mark`
    call carries it as `--change`; for a correction or a patch the turn
    leaves alone, `mark` derives it from `claim`; where the chief recasts the
    place in `DISPOSITIONS`, the recast prose is the text; where the turn
    settles the place on a text of its own, or the chief takes in a role's
    answer there, it is the `change` the place's answers in `ANSWERS` carry.

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

    `marked` is set only where something other than the first-round mark's
    change lands, and holds that change: at `c1`, what `mark` derives from
    `claim`, which the turn's answers replace; at `c12`, what the `add`'s
    `mark` call carries as `--raw-text`, which `mark` refuses because it does
    not keep the words the place already holds; at `b15`, what the `add`'s
    `mark` call carries, which a human query in the turn keeps off the page;
    at `b8`, what the `add`'s `mark` call carries, which the chief replaces
    with a turn answer's text; at `c3`, the same, which the chief replaces
    with a recast of its own.

    `line` is set exactly where the place was empty in its file's fixture,
    and names the 1-based fixture line the place is set against: the declaring
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
#: filled `a0` and `c12`, where `mark` accepts `a0`'s add and refuses
#: `c12`'s. Its `patch`, `unable-to-determine` query and
#: composition rows are planted on `rate.py`, and so is a second `drop`, of
#: a place that owns a leading; its turn row is `ANSWERS`
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
    # wrapper's docstring, indented to its body's depth. In the turn
    # block-context answers with an outside-my-role query and the other two
    # roles clean it; a deferring query abstains (`Process: #121`), so the
    # add settles.
    "fib.py@a2": Landing(
        "text",
        route="turn",
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
    # to logged's own body depth. In the turn function-context answers the
    # composition with a correct and the other two roles clean it, so an add
    # and a correct both stand there, two texts at one place, and the place
    # is carried forward as an escalation; disposition takes in
    # function-context's text. `marked` is the add's own change, which its
    # `mark` call carries.
    "fib.py@b8": Landing(
        "text",
        route="disposition",
        text="    # Counting finished, wrapper is handed back unchanged.",
        marked="    # Counting done, wrapper is handed back unchanged.",
        line=18,
    ),
    # module-context's add, on the absent closing gap after the dunder-main
    # block. In the turn ownership-context answers with an
    # unable-to-determine query and the other two roles clean it; a
    # deferring query abstains (`Process: #121`), so the add settles.
    "fib.py@b17": Landing(
        "text",
        route="turn",
        text="# Nothing follows; running this module only prints one count.",
        line=34,
    ),
    # module-context's add, on the absent b above `if __name__ ==
    # "__main__":` -- `ADDRESSER_ROW`. In the turn block-context answers the
    # composition with a human-review query and the other two roles clean it,
    # so the place rides to the end unruled and stays empty. `marked` is the
    # add's own change, which its `mark` call carries.
    "fib.py@b15": Landing(
        "kept",
        route="query",
        marked="# Run directly, the module prints fib(10) and how many calls it took.",
        line=33,
    ),
    # function-context's add, on an absent c beside `@functools.wraps(fn)`.
    # In the turn module-context answers the composition with a patch and
    # the other two roles clean it, so an add and a patch both stand there,
    # two texts at one place, and the place is carried forward as an
    # escalation; disposition recasts it in the chief's own words. The add is
    # the place's first mark, so the recast carries `add`, the instruction
    # the roles filed there (`flows.turn._recast_as`). `marked` is the
    # add's own change, which its `mark` call carries; no mark call and no
    # turn answer carries `text`, so it reaches the proof only inline in
    # dispositions.json.
    "fib.py@c3": Landing(
        "text",
        route="disposition",
        text="  # copies fn's name and docstring onto wrapper",
        marked="  # keeps wrapper's name and doc matching fn's own",
        line=12,
    ),
    # ownership-context's add, on a filled c that already holds `# base case`
    # beside `if n < 2:`. The paragraph it says will read there drops `base`
    # and `case`, and an add at a place holding prose keeps every word of it
    # in order (`Process: #132` and `#176`), so `mark` refuses it;
    # ownership-context then cleans the place, as the other three roles do,
    # the fold settles it, and `# base case` stands. `marked` is that refused
    # paragraph, which its `mark` call carries as `--raw-text`.
    "fib.py@c12": Landing(
        "kept",
        route="mark",
        marked="  # 0 and 1 are already fibonacci numbers",
    ),
    # block-context's add, on a filled a -- the module docstring already
    # reads. The paragraph it says will read there keeps every word of that
    # docstring in order, with the full stop moved, so `mark` accepts the add
    # (`Process: #132` and `#176`), and its `mark` call carries this text as
    # `--raw-text`; in the turn all four roles clean the composition, and the
    # fold settles it as one text.
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
    # the drop of a place that owns a leading: block-context drops share's
    # comment, and the other three roles mark a scope-declaring query
    # instead of clean, so the fold settles it. The blank line below the
    # comment is the leading `b5` owns, and `set_page` sets no leading after
    # a place a drop vacated, so the blank goes with the comment.
    "rate.py@b5": Landing("removed", route="mark"),
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
#: A composition `query` is planted in each of its three shapes:
#: human-review-necessary at `b15`, where it keeps the add off the page, and
#: outside-my-role at `a2` and unable-to-determine at `b17`, where it
#: abstains and the add settles (`Process: #121`).
#: A composition `correct` and a composition `patch` are planted on
#: `rate.py@b1`, whose base is a real paragraph, and at the empty places of
#: two `add`s, `b8` and `c3`, where each quotes the add's text -- the text the
#: turn sent (`Process: #115`). What each answer makes land is in `LANDINGS`.
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
        "fib.py@a2": {
            "instruction": "query",
            "claim": {
                "shape": "outside-my-role",
                "attempted": "read the added docstring against wrapper's body",
                "settles": "function-context",
            },
            "reason": "what wrapper's own docstring says is function-context's remit",
            "sources": [{"cite": "fib.py:13", "verbatim": "def wrapper(n):"}],
        },
        "fib.py@b15": {
            "instruction": "query",
            "claim": {
                "shape": "human-review-necessary",
                "attempted": "read the added comment against the dunder-main block",
                "settles": "human",
            },
            "reason": "whether the entry point wants a note is the author's call",
            "sources": [
                {"cite": "fib.py:33", "verbatim": 'if __name__ == "__main__":'}
            ],
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
        "fib.py@b8": {
            "instruction": "correct",
            "claim": {"false": "Counting done", "true": "Counting finished"},
            "reason": "finished says the counting is over, which done leaves open",
            "sources": [{"cite": "fib.py:18", "verbatim": "return wrapper"}],
            "change": LANDINGS["fib.py@b8"].text,
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
        "fib.py@c3": {
            "instruction": "patch",
            "claim": {"from": "matching fn's own", "to": "in step with fn's own"},
            "reason": "in step with reads more plainly than matching",
            "change": "  # keeps wrapper's name and doc in step with fn's own",
        },
    },
    "ownership-context": {
        "fib.py@b17": {
            "instruction": "query",
            "claim": {
                "shape": "unable-to-determine",
                "attempted": "read the added comment against the dunder-main block",
                "settles": "another role",
            },
            "reason": "the code does not say whether the module's foot wants a note",
            "sources": [{"cite": "fib.py:34", "verbatim": "print(fib(10), CALLS)"}],
        },
    },
}

#: The chief's own rulings over the four places the turn leaves carried
#: forward -- `a3` and `b9`, each left a lone correction, and `b8` and `c3`,
#: each holding an `add` beside another role's answer to it -- `LANDINGS`
#: above names what each one makes land; this names how. A carried-forward
#: place with no entry here is refused by `disposition`, by name, and so is
#: an entry for a place that is not carried forward.
DISPOSITIONS = [
    {
        "address": "fib.py@a3",
        "answer": "taken_in",
        "side": "original",
        "reason": (
            "module-context alone still holds its rewording after the turn, "
            "and it reads no more correctly than the wording already there"
        ),
    },
    {
        "address": "fib.py@b9",
        "answer": "recast",
        "prose": LANDINGS["fib.py@b9"].text,
        "reason": (
            "block-context still holds watches and module-context withdrew "
            "tracks; neither verb says what the paragraph means, so it is "
            "restated"
        ),
    },
    {
        "address": "fib.py@b8",
        "answer": "taken_in",
        "side": "function-context",
        "reason": "the corrected add says the counting is finished, as the code shows",
    },
    {
        "address": "fib.py@c3",
        "answer": "recast",
        "prose": LANDINGS["fib.py@c3"].text,
        "reason": (
            "the add and the patch word one point two ways; the chief says "
            "what wraps copies instead"
        ),
    },
]


def write_texts(run: Path) -> dict[str, Path]:
    """Write the plant's landing texts, dispositions.json and addresser-row.json.

    Every text a `mark` call carries gets a file that call passes as
    `@path`: one holding the text for an `add` or the move's destination --
    `marked` where the turn or the chief keeps it off the page, else `text`
    -- or one per
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
#: directly on its own code: `b0` under the blank after `a0` and `b8` under
#: the one after `return fn(n)`. The
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
    "    @functools.wraps(fn)  # copies fn's name and docstring onto wrapper\n"
    "    def wrapper(n):\n"
    '        """Count each call, then pass it through."""\n'
    "        global CALLS\n"
    "        CALLS += 1  # the decorator's only job\n"
    "        return fn(n)\n"
    "\n"
    "    # Counting finished, wrapper is handed back unchanged.\n"
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
    'if __name__ == "__main__":\n'
    "    print(fib(10), CALLS)\n"
    "# Nothing follows; running this module only prints one count.\n"
    "\n"
)


#: What the proof's `rate.py` must read once the chain closes, written out by
#: hand the same way from `RATE_FIXTURE`, `LANDINGS` and `ANSWERS`. `b1` and
#: `c3` each land as many lines as they held, so in `rate` four lines change:
#: the paragraph's first and last, which the two corrections touched, its
#: middle, which the turn's answers reword, and the line the patched
#: trailing comment sits on. In `share` the dropped comment is gone and so is
#: the blank line below it, the leading `b5` owned: `set_page` sets no
#: leading after a place a drop vacated. The two blank lines above `share`
#: are the leading `c3` owns, which a `c` keeps whatever sits beside it.
RATE_EXPECTED = (
    "def rate(hits, total):\n"
    "    # No calls give a zero rate: nothing\n"
    "    # was put to the cache. The rate is\n"
    "    # hits over total, never more than one.\n"
    "    if total == 0:\n"
    "        return 0.0\n"
    "    return hits / total  # fraction of calls the cache answered\n"
    "\n"
    "\n"
    "def share(hits, total):\n"
    "    return rate(hits, total)\n"
)


#: The role whose own copy the smoke drafts with `proof --copy` before the fold.
DRAFTED_ROLE = "function-context"

#: What `proof --copy` drafts of `fib.py` from `DRAFTED_ROLE`'s copy alone,
#: written out by hand from `FIXTURE` and that role's rows in the smoke
#: script's mark stage: its corrections at `c1` and `a3` and its adds at `c3`
#: and `a2` land, and every place it marked `clean` or `query` keeps the
#: fixture's prose -- a mark that proposes no text alters nothing
#: (`docket-defects` T10).
ROLE_DRAFT = (
    '"""Fibonacci, counted so the recursion can be seen."""\n'
    "\n"
    "import functools\n"
    "\n"
    "# Module state, written by the wrapper and read by the caller.\n"
    "CALLS = 0  # every entry, computed or not\n"
    "\n"
    "\n"
    "def logged(fn):\n"
    '    """Count each call and pass it through."""\n'
    "\n"
    "    @functools.wraps(fn)  # keeps wrapper's name and doc matching fn's own\n"
    "    def wrapper(n):\n"
    '        """Count each call, then pass it through."""\n'
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
    '    """The nth Fibonacci number, starting at fib(0) = 0."""\n'
    "    if n < 2:  # base case\n"
    "        return n\n"
    "    # Two calls per level, which is what the counter measures.\n"
    "    return fib(n - 1) + fib(n - 2)\n"
    "\n"
    "\n"
    'if __name__ == "__main__":\n'
    "    print(fib(10), CALLS)\n"
)

#: What `proof --copy` drafts of `rate.py` from the same copy: the role's
#: correction on `b1`'s last line lands, and its queries at `c3` and `b5` keep
#: the fixture's prose.
ROLE_RATE_DRAFT = (
    "def rate(hits, total):\n"
    "    # Zero calls give a zero rate: nothing\n"
    "    # was asked of the cache. The rate is\n"
    "    # hits over total, never more than one.\n"
    "    if total == 0:\n"
    "        return 0.0\n"
    "    return hits / total  # share of calls the cache answered\n"
    "\n"
    "\n"
    "def share(hits, total):\n"
    "    # Kept for callers that ask for a share rather than a rate.\n"
    "\n"
    "    return rate(hits, total)\n"
)


def write_role_draft(root: Path) -> tuple[Path, Path]:
    """Write `ROLE_DRAFT` and `ROLE_RATE_DRAFT` to `root`, as `write_expected` writes.

    Args:
        root: the directory to write into. Not created here -- the smoke
            script creates its run's `role-expected` directory first.

    Returns:
        The two paths written, `fib.py`'s first.
    """
    fib = root / "fib.py"
    fib.write_text(ROLE_DRAFT, encoding="utf-8", newline="\n")
    rate = root / "rate.py"
    rate.write_text(ROLE_RATE_DRAFT, encoding="utf-8", newline="\n")
    return fib, rate


#: `mark-defects` T25's plant: a `drop` on `rate.py@b1` of the clause that
#: spans its first line break, so the text either side joins onto one line --
#: 46 columns, where the paragraph's widest line was 42.
WRAP_DROP = " nothing\n    # was asked of the cache."

#: What `proof --copy` drafts of `rate.py` from a fresh ownership-context copy
#: holding that one drop and nothing else, written out by hand from
#: `RATE_FIXTURE`: the joined line rewrapped to 42 columns, under its own
#: indent and marker, and every other line as the fixture has it.
WRAP_RATE_DRAFT = (
    "def rate(hits, total):\n"
    "    # Zero calls give a zero rate: The\n"
    "    # rate is\n"
    "    # hits over total, never above one.\n"
    "    if total == 0:\n"
    "        return 0.0\n"
    "    return hits / total  # share of calls the cache answered\n"
    "\n"
    "\n"
    "def share(hits, total):\n"
    "    # Kept for callers that ask for a share rather than a rate.\n"
    "\n"
    "    return rate(hits, total)\n"
)


#: The move the collide plant places: `share`'s comment, exactly as
#: `RATE_FIXTURE` holds it, which is the whole of `rate.py@b5`.
COLLIDE_SNIPPET = "    # Kept for callers that ask for a share rather than a rate."

#: `rate.py@b1` as `RATE_FIXTURE` holds it, which is the base both of the
#: collide plant's two marks is measured against.
COLLIDE_RATE_BASE = (
    "    # Zero calls give a zero rate: nothing\n"
    "    # was asked of the cache. The rate is\n"
    "    # hits over total, never above one."
)

#: What `rate.py@b1` reads once the snippet arrives above it. It keeps every
#: word of the paragraph and of the snippet, so `mark` places the move, and it
#: edits no line the role's own `correct` at `b1` edits -- so the two compose
#: into that role's one side (`decision-log.md Process: #179`).
COLLIDE_RATE_B1 = COLLIDE_SNIPPET + "\n" + COLLIDE_RATE_BASE

#: And what it reads with the snippet below it instead, which keeps the same
#: words and does not compose: the paragraph's last line carries no newline,
#: so a line after it rewrites that line -- the one the `correct` rewrites.
COLLIDE_SAME_SENTENCE = COLLIDE_RATE_BASE + "\n" + COLLIDE_SNIPPET


def write_collide_plant(run: Path) -> tuple[Path, Path]:
    """Write the collide move's two destination texts, and return their paths.

    Args:
        run: the run directory; the texts go to `collide-raw-text.txt` and
            `collide-same-sentence.txt` in it, which the smoke script passes
            to `mark` as `@path`.

    Returns:
        The composing text's path first, the refused one's second.
    """
    composes = run / "collide-raw-text.txt"
    composes.write_text(COLLIDE_RATE_B1, encoding="utf-8", newline="\n")
    refused = run / "collide-same-sentence.txt"
    refused.write_text(COLLIDE_SAME_SENTENCE, encoding="utf-8", newline="\n")
    return composes, refused


#: What `proof --copy` drafts of `rate.py` from the collide copy, written out
#: by hand from `RATE_FIXTURE` and that copy's marks: `b1` reads with the
#: snippet the move brought and the `correct`'s own last line, which is the
#: composition of the role's two marks there; `b5`, the move's origin, is
#: vacated and takes the blank line below it, the leading it owned; `c3` keeps
#: the fixture's prose, which the role only queried. `fib.py` is drafted from
#: the same copy and is `ROLE_DRAFT` unchanged -- the collide move touches
#: neither of its pages' places.
COLLIDE_RATE_DRAFT = (
    "def rate(hits, total):\n"
    "    # Kept for callers that ask for a share rather than a rate.\n"
    "    # Zero calls give a zero rate: nothing\n"
    "    # was asked of the cache. The rate is\n"
    "    # hits over total, never more than one.\n"
    "    if total == 0:\n"
    "        return 0.0\n"
    "    return hits / total  # share of calls the cache answered\n"
    "\n"
    "\n"
    "def share(hits, total):\n"
    "    return rate(hits, total)\n"
)


def write_collide_draft(root: Path) -> tuple[Path, Path]:
    """Write what the collide copy drafts, as `write_expected` writes.

    Args:
        root: the directory to write into. Not created here -- the smoke
            script creates its run's `collide-expected` directory first.

    Returns:
        The two paths written, `fib.py`'s first.
    """
    fib = root / "fib.py"
    fib.write_text(ROLE_DRAFT, encoding="utf-8", newline="\n")
    rate = root / "rate.py"
    rate.write_text(COLLIDE_RATE_DRAFT, encoding="utf-8", newline="\n")
    return fib, rate


def write_wrap_plant(run: Path, expected: Path) -> tuple[Path, Path]:
    """Write `WRAP_DROP` for the smoke's `mark` call, and `WRAP_RATE_DRAFT`.

    Args:
        run: the run directory; the clause goes to `wrap-drop.txt` in it,
            which the smoke script passes to `mark` as `@path`.
        expected: the directory the expected draft goes into. Not created
            here -- the smoke script creates it first.

    Returns:
        The clause file and the expected `rate.py`.
    """
    clause = run / "wrap-drop.txt"
    clause.write_text(WRAP_DROP, encoding="utf-8", newline="\n")
    rate = expected / "rate.py"
    rate.write_text(WRAP_RATE_DRAFT, encoding="utf-8", newline="\n")
    return clause, rate


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
