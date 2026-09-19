"""Writes the middle-chain smoke test's three fixture files, and what lands on them.

`docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`, "The
fixture", names `fib.py`'s text verbatim: a short recursive Fibonacci with a
logging decorator, three trailing comments, three standalone comment runs,
two stacked decorators, a nested `def`, and a dunder-main block. `rate.py`
is the second file, beside it: `rate`, holding a three-line comment of two
sentences and a trailing comment, and `share`, holding a one-line comment
with a blank line below it -- the places a `patch`, an
`unable-to-determine` query, a composition and a `drop` of a place that
owns a leading are planted on, since every prose place in `fib.py` already
carries another row. `store.py` is the third, four one-line functions
carrying four standalone comments and a trailing one -- the places a
partial move, a move a role holds for the human, a lone proposal against
cleans and a `correct` whose change is wider than its claim are planted on,
for the same reason. All three structures are
fixed -- `LANDINGS`, `ANSWERS` and `DISPOSITIONS` below plant decisions
against specific addresses on them, so no text may drift from what
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

`EXPECTED`, `RATE_EXPECTED` and `STORE_EXPECTED` are the texts the proof's
`fib.py`, `rate.py` and `store.py` must read once the chain closes, and
`write_expected` writes them
for the smoke script's `diff` stage. `ROLE_DRAFT` and `ROLE_RATE_DRAFT` are
what `proof --copy` drafts from `DRAFTED_ROLE`'s own copy before the fold, and
`write_role_draft` writes them for the smoke script's `draft` stage.

`APPROVED` is the partial approval `proof --only` sets alone,
`PARTIAL_EXPECTED` is the one page that run must leave, and `write_approval`
writes the addresses for the script to read rather than have it spell them
itself.
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


#: The third fixture file, `store.py`. Six one-line functions, each with a
#: standalone comment above its body, and one trailing comment. Its six prose
#: places are the ones the plant needs and the other two files cannot spare:
#: `b1`, a comment of two sentences whose second a partial move takes to `b3`,
#: leaving the first behind; `b3`, the comment that move arrives above; `b5`,
#: the comment a move sends to `b12` and a role holds for the human, so neither
#: end lands; `b7`, the comment one role corrects and the other three clean,
#: which carries forward to those three as a composition; `c5`, the
#: trailing comment whose `correct` writes a change wider than its claim;
#: `b9`, the comment one role moves up to `b8` while another rewords it where
#: it stands, which contests both ends of the move and leaves the chief to
#: rule each of them; and `b11`, the comment whose second sentence one role
#: moves to `b10` while another rewords that sentence where it stands -- the
#: move its own filer withdraws in the second turn, so the sentence lands once,
#: in the other role's wording, at `b11`, and `b10` stays empty.
STORE_FIXTURE = (
    "def kept(log):\n"
    "    # Every lookup is recorded. Entries are never removed.\n"
    "    return len(log)\n"
    "\n"
    "\n"
    "def missed(log, found):\n"
    "    # A miss is a lookup the store had no answer for.\n"
    "    return kept(log) - found\n"
    "\n"
    "\n"
    "def part(log, found):\n"
    "    # Rounded before it is printed.\n"
    "    return round(found / kept(log), 2)  # two places, as the report wants\n"
    "\n"
    "\n"
    "def empty(log):\n"
    "    # True when the store has answered nothing at all.\n"
    "    return kept(log) == 0\n"
    "\n"
    "\n"
    "def total(log):\n"
    "    # The number of lookups the store has seen.\n"
    "    return kept(log)\n"
    "\n"
    "\n"
    "def seen(log, key):\n"
    "    # True when the key is in the log. Every lookup goes through this store.\n"
    "    return key in log\n"
    "\n"
    "\n"
    "def summary(log, found):\n"
    '    """Two numbers, one line.\n'
    "\n"
    "    The report prints the count and the share, in that order.\n"
    '    """\n'
    "    # The store keeps every lookup it has ever answered, and the count\n"
    "    # is what the report prints at the end of the day. Nothing is ever\n"
    "    # removed from it, so the number only goes up.\n"
    "    counted = kept(log)\n"
    "    # Rounded twice.\n"
    "    share = part(log, found)\n"
    "    # The share is printed beside the count, and the two are read\n"
    "    # together: a count with no share says nothing about the store,\n"
    "    # and a share with no count says nothing about the day.\n"
    "    return counted, share  # both, in order\n"
)


def write_store_fixture(root: Path) -> Path:
    """Write `STORE_FIXTURE` to `root / "store.py"` and return its path.

    Written with an explicit LF newline, for the reason `write_fixture`
    gives.

    Args:
        root: the directory to write into, which `write_fixture` also writes
            into. Not created here.

    Returns:
        The path written.
    """
    path = root / "store.py"
    path.write_text(STORE_FIXTURE, encoding="utf-8", newline="\n")
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
    (`desk.marks.mark.derived_change` replaces the quoted clause with the other in
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

    `filed` names every instruction any role files at the place, once each
    and in no particular order -- what the plant reaches at that address,
    which is what `tests/gates/test_smoke_fixture.py` walks the marks table
    against. A move is named at both of the places it touches, since the row
    writes at both. `tests/test_differential_collate.py` reads the copies one
    smoke run leaves and holds this to what the `mark` calls actually placed.

    `line` is set exactly where the place was empty in its file's fixture,
    and names the 1-based fixture line the place is set against: the declaring
    line an `a` goes directly below, the line of code a `c` sits beside, the
    line of code a `b`'s gap sits directly above -- or, for the closing gap
    `b17`, which has no code below it, the file's last line, which it
    follows.
    """

    outcome: str
    route: str
    filed: tuple[str, ...] = ()
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
        filed=("correct", "query"),
        text="  # the decorator's only job",
        claim={
            "false": "the decorator's whole job",
            "true": "the decorator's only job",
        },
    ),
    # collate escalates c1: block-context and function-context each replace
    # the same `false`. In the turn block-context corrects its change to
    # this text and function-context patches its own to the same, so the two
    # sides come to one text -- which the two roles that cleaned c1 have
    # still not seen, so the place is carried forward to them
    # (`Process: #180`) and the chief takes the text in. `marked` is
    # block-context's first-round change, which the turn replaced.
    "fib.py@c1": Landing(
        "text",
        route="disposition",
        filed=("correct", "clean"),
        text="  # every call, cached or not",
        claim={"false": "memoised or not", "true": "cached or not"},
        marked="  # every entry, cached or not",
    ),
    # the move's --change: b1's paragraph relocates to b0, unchanged, and
    # the fold settles the move. b0's gap sits above `import functools`.
    "fib.py@b0": Landing(
        "text",
        route="mark",
        filed=("move",),
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
        filed=("add",),
        text='        """Count each call, then pass it through."""',
        line=13,
    ),
    # collate escalates b9. In the turn block-context and module-context each
    # hold their correction, so two texts still stand at the place and it is
    # carried forward again; disposition recasts it in the chief's own words
    # -- no mark call's --true and no turn answer carries this text, so it
    # reaches the proof only inline in dispositions.json.
    "fib.py@b9": Landing(
        "text",
        route="disposition",
        filed=("correct", "clean"),
        text=(
            "# The cache and the counter measure different things, worth stating\n"
            "# separately. fib is cached; logged counts every call, cached or not."
        ),
    ),
    # the drop vacates b14, and the fold settles it; nothing replaces the
    # dropped paragraph.
    "fib.py@b14": Landing("removed", route="mark", filed=("drop", "query")),
    # the move vacates its own address, and the fold settles it; the text it
    # carried now lives at b0.
    "fib.py@b1": Landing("removed", route="mark", filed=("move", "query")),
    # collate escalates a3. In the turn block-context withdraws and the other
    # two each hold, so two texts still stand at the place and it is carried
    # forward; disposition keeps the original over both.
    "fib.py@a3": Landing("kept", route="disposition", filed=("correct", "clean")),
    # block-context's query settles nothing and rides to the end; a1 is left
    # as it was.
    "fib.py@a1": Landing("kept", route="query", filed=("query", "clean")),
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
        filed=("add",),
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
        filed=("add",),
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
        filed=("add",),
        marked="# Run directly, the module prints fib(10) and how many calls it took.",
        line=33,
    ),
    # function-context's add, on an absent c beside `@functools.wraps(fn)`.
    # In the turn module-context answers the composition with a patch and
    # the other two roles clean it, so an add and a patch both stand there,
    # two texts at one place, and the place is carried forward as an
    # escalation; disposition recasts it in the chief's own words. The add is
    # the place's first mark, so the recast carries `add`, the instruction
    # the roles filed there (`desk.dispositions`). `marked` is the
    # add's own change, which its `mark` call carries; no mark call and no
    # turn answer carries `text`, so it reaches the proof only inline in
    # dispositions.json.
    "fib.py@c3": Landing(
        "text",
        route="disposition",
        filed=("add",),
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
        filed=("clean",),
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
        filed=("add", "clean"),
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
        filed=("patch", "query"),
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
        filed=("correct", "clean"),
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
    "rate.py@b5": Landing("removed", route="mark", filed=("drop", "query")),
    # the partial move's origin: ownership-context takes the paragraph's
    # second sentence to `b3` and the first stays where it is, since a move's
    # `change` is the snippet and the origin keeps what the snippet left
    # behind (`Process: #172`). The other three roles mark a scope-declaring
    # query rather than clean, so the fold settles it. `marked` is that
    # snippet, which the move's `mark` call carries as `--change`.
    "store.py@b1": Landing(
        "text",
        route="mark",
        filed=("move", "query"),
        text="    # Every lookup is recorded.",
        marked=" Entries are never removed.",
    ),
    # and its destination: the paragraph `b3` already held with the snippet
    # on a line below it, which is the move's `--raw-text` -- the destination
    # text as it will read (`Process: #175`). ownership-context marks `b3`
    # clean beside its own move and the other three query, so the fold
    # settles it.
    "store.py@b3": Landing(
        "text",
        route="mark",
        filed=("move", "clean", "query"),
        text=(
            "    # A miss is a lookup the store had no answer for.\n"
            "    # Entries are never removed."
        ),
    ),
    # the held move's origin: module-context moves the whole paragraph to
    # `b12` and block-context marks a human-review query at the same place, so
    # both ends ride to the end unruled and the paragraph stays where it is
    # (`Process: #182`).
    "store.py@b5": Landing("kept", route="query", filed=("move", "query")),
    # and its destination, the empty gap between the last two functions,
    # which stays empty for the same reason. `marked` is the paragraph the
    # move carries, which its `mark` call passes as both `--change` and
    # `--raw-text`: the whole paragraph leaves, so the two are one text.
    # ! IT WAS THE CLOSING GAP UNTIL `summary` WAS APPENDED for the
    # compacting stage, and the case it plants is a move held for the human
    # at both ends (`Process: #182`) rather than anything about the file's
    # end -- `fib.py@b17` is the closing-gap plant.
    "store.py@b12": Landing(
        "kept",
        route="query",
        filed=("move",),
        marked="    # Rounded before it is printed.",
        line=31,
    ),
    # the contested move's origin: block-context moves the whole paragraph up
    # to `b8`, the gap above the declaration it describes, and
    # function-context rewords it where it stands. Two texts that do not
    # compose, so the place is an escalation and the pairing carries the
    # destination with it; both roles hold in the turn and the chief takes the
    # move in at each end, which empties the origin. `marked` is the paragraph
    # the move carries -- the whole of it leaves, so its `--change` and its
    # `--raw-text` differ only in the indentation the destination reads with.
    "store.py@b9": Landing(
        "removed",
        route="disposition",
        filed=("move", "correct", "query"),
        marked="    # The number of lookups the store has seen.",
    ),
    # and its destination, the gap above `def total`, where the chief's second
    # ruling lands the paragraph at the declaration's own indentation.
    "store.py@b8": Landing(
        "text",
        route="disposition",
        filed=("move",),
        text="# The number of lookups the store has seen.",
        line=21,
    ),
    # the lone proposal against cleans: module-context corrects, and the
    # other three roles clean rather than defer, so the text is one none of
    # them has seen and the place carries forward to exactly those three as a
    # composition (`Process: #180`). Each answers `clean` in the turn and the
    # fold settles it.
    "store.py@b7": Landing(
        "text",
        route="turn",
        filed=("correct", "clean"),
        text="    # True when the store has answered nothing yet.",
        claim={"false": "nothing at all", "true": "nothing yet"},
    ),
    # the `correct` whose change is wider than its claim: block-context
    # writes its own `--change` rather than letting the claim derive one, and
    # it drops a word the claim never named. The fold reports that as an
    # advisory and rolls nothing back for it (`Process: #177`), the other
    # three roles query, and the change lands. `text` is what the role wrote,
    # which is not what the claim derives -- `tests/gates/
    # test_smoke_fixture.py`'s `WIDER` names the word it drops.
    "store.py@c5": Landing(
        "text",
        route="mark",
        filed=("correct", "query"),
        text="  # two decimal places, as the report asks",
        claim={"false": "two places", "true": "two decimal places"},
    ),
    # the withdrawn move's origin: module-context takes the paragraph's second
    # sentence to `b10`, the gap above the declaration, and block-context
    # rewords that same sentence where it stands. The two texts do not
    # compose, so the origin is an escalation and the pairing carries the
    # destination with it. Both roles hold in the first turn; in the second
    # the mover withdraws, and a withdrawal reaches the move whole
    # (`Process: #129`), so the sentence lands once, in block-context's
    # wording, where it already was. `marked` is the snippet, which the move's
    # `mark` call carries as `--change`; block-context's clauses are short and
    # its `mark` call spells them inline, so no `claim` is written here.
    "store.py@b11": Landing(
        "text",
        route="turn",
        filed=("move", "correct", "query"),
        text=(
            "    # True when the key is in the log."
            " Each lookup goes through this store."
        ),
        marked=" Every lookup goes through this store.",
    ),
    # and its destination, which stays empty: the move it was the landing of
    # is off at both ends, and block-context's `clean` there was an acceptance
    # of the moved text rather than a proposal of its own, so nothing is left
    # proposing it. `marked` is the destination text the move's `mark` call
    # carries as `--raw-text` -- the snippet as it would have read at the
    # module's own indentation.
    "store.py@b10": Landing(
        "kept",
        route="turn",
        filed=("move",),
        marked="# Every lookup goes through this store.",
        line=26,
    ),
    # `summary`'s five places, which every role cleans: length is no concern
    # of the four editorial roles (`decision-log.md Process: #193`, Roy: they
    # need the comments to be correct, true and current, and however many
    # lines that takes is what it is). They stand as the fixture has them and
    # reach the revise unchanged, which is where the compacting stage reads
    # them: `b13` and `b15` run over its cap and are dealt, and the docstring
    # `a7`, the one-line `b14` and the trailing `c15` are not.
    "store.py@a7": Landing("kept", route="mark", filed=("clean",)),
    "store.py@b13": Landing("kept", route="mark", filed=("clean",)),
    "store.py@b14": Landing("kept", route="mark", filed=("clean",)),
    "store.py@b15": Landing("kept", route="mark", filed=("clean",)),
    "store.py@c15": Landing("kept", route="mark", filed=("clean",)),
}

#: The `LANDINGS` entry smoke_middle.ps1 marks without spelling its address:
#: it asks `addresser` for the `b` place at this entry's `line`, and stops
#: unless the address that comes back is this one.
ADDRESSER_ROW = "fib.py@b15"

#: The places `collate` carries forward at a lone proposal, and whose
#: proposal each is. The turn's batch sends each to every other role that read
#: the page: a text settles once every role that read the place has accepted
#: it, and the role that proposed it has (`decision-log.md Process: #180`), so
#: the proposing role is not asked about its own proposal. Six are `add`s, at
#: places no other role was handed a slot for; `store.py@b7` is a `correct`
#: the other three roles cleaned, which is the same rule reaching a place they
#: all read.
PROPOSED = {
    "fib.py@a0": "block-context",
    "fib.py@b8": "block-context",
    "fib.py@c3": "function-context",
    "fib.py@a2": "function-context",
    "fib.py@b17": "module-context",
    "fib.py@b15": "module-context",
    "store.py@b7": "module-context",
}

#: The places `collate` carries forward as an escalation -- two texts at one
#: place that will not compose -- which is the question the turn asks there.
#: Every other place the plant answers is carried forward as a composition.
#: `check --answers` refuses an answer the question does not admit, so the
#: smoke is what holds this to the fold rather than this table standing alone.
#: `store.py@b8` is NOT here, and it is the contested move's destination: an
#: end takes its partner's STATE but keeps its own question and its own roles
#: where it has them (`desk.evaluate.passes.pair_moves`). One role proposed
#: the moved text there and one other has not seen it, so `b8` is carried
#: forward contested, with its own composition put to that one role.
ESCALATED = (
    "fib.py@c1",
    "fib.py@b9",
    "fib.py@a3",
    "store.py@b9",
    "store.py@b11",
)


def question_at(address: str) -> str:
    """Which question the turn asks at one answered place.

    Args:
        address: a place the plant answers for some role.

    Returns:
        `"escalation"` for a place in `ESCALATED`, else `"composition"`.
    """
    return "escalation" if address in ESCALATED else "composition"


#: Each role's answers to the batch `collate` sends for the turn, keyed by
#: address and holding only the fields the role fills; `turn` lays them over
#: the place it is asking about. An escalation (`c1`, `b9`, `a3`) takes
#: `hold`, `withdraw`, `correct` or `patch`, and a composition `clean`,
#: `query`, `correct` or `patch`; each of the eight is planted at least once,
#: and a role answers `clean` at every place in `PROPOSED` this gives it
#: nothing for.
#: A composition `query` is planted in each of its three shapes:
#: human-review-necessary at `b15`, where it keeps the add off the page, and
#: outside-my-role at `a2` and unable-to-determine at `b17`, where it
#: abstains and the add settles (`Process: #121`).
#: A composition `correct` and a composition `patch` are planted on
#: `rate.py@b1`, whose base is a real paragraph, and at the empty places of
#: two `add`s, `b8` and `c3`, where each quotes the add's text -- the text the
#: turn sent (`Process: #115`). What each answer makes land is in `LANDINGS`.
#:
#: A composition goes to every role that read the page, so `rate.py@b1` is
#: asked of the two roles that proposed nothing there as well. Each abstains
#: with a deferring `query`: a `clean` there would take the composed text as
#: that role's own side, against the two sides the answers reword, and the
#: place would stay contested rather than settling on the text they agree on.
#:
#: An escalation the answers leave one side standing settles on that side, so
#: the two places the chief rules -- `b9` and `a3` -- keep two sides through
#: the turn, and the withdraw planted at `a3` is one of three answers there.
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
        # The contested move's origin, held: the mover keeps its move, so the
        # two texts there still stand and the chief rules each end. Its
        # destination is not asked of this role -- the text there is its own.
        "store.py@b9": {
            "instruction": "hold",
            "reason": "the paragraph describes the declaration, not the body",
        },
        # The withdrawn move's origin, where this role holds the rewording it
        # filed, and its destination, which it is the one role asked about --
        # the two that deferred at the origin defer on the move, so nobody
        # else is owed a say there. The `clean` takes the moved text as this
        # role's side, and the mover's withdrawal in the second turn takes
        # both off.
        "store.py@b11": {
            "instruction": "hold",
            "reason": "each reads more plainly than every for one lookup at a time",
        },
        "store.py@b10": {
            "instruction": "clean",
            "reason": "the sentence reads as the module's own note where it lands",
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
        "store.py@b9": {
            "instruction": "hold",
            "reason": "the wording is what wants fixing, not where it sits",
        },
        # The move's destination is a composition to this role, the one reader
        # of the page that has not seen the text there, and it accepts it --
        # which leaves the place carried forward all the same, since its
        # partner is still contested and the two take one state.
        "store.py@b8": {
            "instruction": "clean",
            "reason": "the paragraph reads correctly where the move puts it",
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
        "rate.py@b1": {
            "instruction": "query",
            "claim": {
                "shape": "outside-my-role",
                "attempted": "read the composed paragraph against the guard below it",
                "settles": "block-context",
            },
            "reason": "how one function's guard is worded is not my remit",
            "sources": [{"cite": "rate.py:5", "verbatim": "if total == 0:"}],
        },
        # The withdrawn move's origin, where this role is the mover: it holds
        # its move in the first turn and withdraws it in the second. Its own
        # destination is not asked of it, the text there being its own.
        "store.py@b11": {
            "instruction": "hold",
            "reason": "the sentence is about the store, not about this one lookup",
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
        "rate.py@b1": {
            "instruction": "query",
            "claim": {
                "shape": "outside-my-role",
                "attempted": "read the composed paragraph against the guard below it",
                "settles": "block-context",
            },
            "reason": "which words this paragraph uses is not my remit",
            "sources": [{"cite": "rate.py:5", "verbatim": "if total == 0:"}],
        },
    },
}

#: Each role's answers to the batch the first turn sends out, keyed the same
#: way. Every slot that batch carries is answered here by name: unlike the
#: first turn's, these are not filled in from `PROPOSED`, since what the
#: second turn asks is what the first one left open rather than a list of lone
#: proposals.
#:
#: The withdrawn move is the reason there is a second turn at all. Its mover
#: withdraws at the origin here, having held in the first; the move is off at
#: both of its ends (`decision-log.md Process: #129`), and the destination --
#: settled on its own after the first turn and carried forward only by its
#: partner -- loses the moved text although nothing was written there this
#: turn.
#:
#: Every other place the second turn asks about is one the chief rules in
#: `DISPOSITIONS`, and each answer here keeps it carried forward so that it
#: reaches the chief: the escalations are held, and at the three compositions
#: one role proposes a text of its own rather than cleaning, which would have
#: settled the place and left the chief a ruling `disposition` refuses. What
#: those proposals say never lands -- the chief's ruling decides each of the
#: three -- so `LANDINGS` is unchanged by them.
ANSWERS2: dict[str, dict[str, dict]] = {
    "block-context": {
        "fib.py@b8": {
            "instruction": "hold",
            "reason": "the add still says what the return does, however it is worded",
        },
        "fib.py@c3": {
            "instruction": "hold",
            "reason": "what wraps copies is the point, and mine says it",
        },
        "store.py@b9": {
            "instruction": "hold",
            "reason": "the paragraph still belongs above the declaration",
        },
        "store.py@b8": {
            "instruction": "hold",
            "reason": "and this is still where it belongs",
        },
        "store.py@b11": {
            "instruction": "hold",
            "reason": "each lookup is the one the reader is following here",
        },
        "store.py@b10": {
            "instruction": "hold",
            "reason": "the sentence reads as well above the declaration as in it",
        },
    },
    "function-context": {
        "fib.py@b9": {
            "instruction": "correct",
            "claim": {"false": "logged watches", "true": "logged records"},
            "reason": "records is what the counter does; watches says nothing is kept",
            "change": (
                "# The cache sits inside the decorator stack on purpose:"
                " logged records\n"
                "# every call, cache sees only the misses."
            ),
        },
        "fib.py@b8": {
            "instruction": "hold",
            "reason": "finished is still the word for counting that is over",
        },
        "fib.py@c3": {
            "instruction": "hold",
            "reason": "the add says what the decorator does to wrapper",
        },
        "store.py@b9": {
            "instruction": "hold",
            "reason": "the wording is what wants fixing, not where the note sits",
        },
        "store.py@b8": {
            "instruction": "hold",
            "reason": "the text is the same wherever the chief puts it",
        },
    },
    "module-context": {
        "fib.py@c1": {
            "instruction": "correct",
            "claim": {"false": "every call", "true": "each call"},
            "reason": "each call is one call at a time, which is what the counter adds",
            "change": "  # each call, cached or not",
        },
        "fib.py@b8": {
            "instruction": "hold",
            "reason": "the add reads as the module's own note about the return",
        },
        "fib.py@c3": {
            "instruction": "hold",
            "reason": "in step with still reads more plainly than matching",
        },
        "store.py@b11": {
            "instruction": "withdraw",
            "reason": "reworded where it stands it reads as the store's own note",
        },
        "store.py@b10": {
            "instruction": "hold",
            "reason": "nothing of mine is left at this place",
        },
    },
    "ownership-context": {
        "fib.py@c1": {
            "instruction": "clean",
            "reason": "the two roles' wording says what the counter counts",
        },
        "fib.py@b9": {
            "instruction": "clean",
            "reason": "the paragraph reads as one, whichever verb it takes",
        },
        "fib.py@a3": {
            "instruction": "patch",
            "claim": {"from": "beginning at", "to": "counted from"},
            "reason": "counted from is the phrase the module docstring uses",
            "change": '    """The nth Fibonacci number, counted from fib(0) = 0."""',
        },
        "fib.py@b8": {
            "instruction": "hold",
            "reason": "the add belongs to the block it closes",
        },
        "fib.py@c3": {
            "instruction": "hold",
            "reason": "the add belongs beside the decorator it describes",
        },
    },
}

#: The chief's own rulings over the seven places the two turns leave carried
#: forward -- `a3`, `b9` and `c1`, each left with texts no role has taken, and
#: `b8` and `c3`, each holding an `add` beside another role's answer to it,
#: and the contested move at both of its ends --
#: `LANDINGS` above names what each one makes land; this names how. A
#: carried-forward place with no entry here is refused by `disposition`, by
#: name, and so is an entry for a place that is not carried forward.
DISPOSITIONS = [
    {
        "address": "fib.py@c1",
        "answer": "taken_in",
        "side": "block-context",
        "reason": (
            "block-context and function-context came to one wording in the "
            "turn, and it says what the counter counts"
        ),
    },
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
    # The contested move, ruled at each of its ends. A move's two places take
    # one state, so the chief is owed a ruling at both and `disposition`
    # refuses the round for either one left alone; each end closes on the
    # text its own ruling decides.
    {
        "address": "store.py@b9",
        "answer": "taken_in",
        "side": "block-context",
        "reason": (
            "the paragraph says what the function is for, which is read above "
            "the declaration rather than inside it"
        ),
    },
    {
        "address": "store.py@b8",
        "answer": "taken_in",
        "side": "block-context",
        "reason": "and this is where the move lands it",
    },
]


def file_for(address: str, key: str = "") -> str:
    """What `write_texts` names the file holding one address's text.

    The page's stem as well as the cue, so `fib.py@b8` and `store.py@b8` are
    two files: the plant reaches the same cue on more than one page, and a
    name taken from the cue alone would have one landing's text overwrite
    another's.

    Args:
        address: `path@cue`, as a `LANDINGS` key spells it.
        key: a `claim` key where the file holds one clause, else `""`.

    Returns:
        The file's name, `"<stem>-<cue>.txt"` or `"<stem>-<cue>-<key>.txt"`.
    """
    page, _, cue = address.partition("@")
    stem = page.rsplit(".", 1)[0]
    return f"{stem}-{cue}-{key}.txt" if key else f"{stem}-{cue}.txt"


def write_texts(run: Path) -> dict[str, Path]:
    """Write the plant's landing texts, dispositions.json and addresser-row.json.

    Every text a `mark` call carries gets a file that call passes as
    `@path`: one holding the text for an `add`, a move's snippet or a move's
    destination -- `marked` where the mark carries something other than what
    lands, else `text` -- or one per
    `claim` key -- `<stem>-<cue>-false.txt` and `<stem>-<cue>-true.txt` for
    the three corrections, `<stem>-<cue>-from.txt` and
    `<stem>-<cue>-to.txt` for the patch (`rate.py`'s `c3`) -- whose clauses
    `mark` needs separately, matching its own rule that a whole paragraph is
    passed by file while a one-line clause may go inline. `file_for` names
    every one of them, by the page as well as the cue, so two landings
    sharing a cue never write one file. A place whose text no
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
        if landing.claim is not None:
            for key, value in landing.claim.items():
                path = run / file_for(address, key)
                path.write_text(value, encoding="utf-8", newline="\n")
                paths[f"{address}:{key}"] = path
            continue
        carried = landing.marked
        if carried is None and address not in recast | turned:
            carried = landing.text
        if carried is None:
            continue
        path = run / file_for(address)
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


#: What a role says when it adopts the text the turn sent it. Every answer
#: owes a reason, a `clean` included, so the auto-filled ones carry this.
CLEAN_REASON = "the paragraph the turn sent reads as one; I have nothing to add"


def answers_for(role: str) -> list[dict]:
    """One role's whole answer to the turn's batch, in the order it is written.

    Every place `ANSWERS` answers for that role, then a `clean` carrying
    `CLEAN_REASON` at each place in `PROPOSED` it does not -- except its own
    proposal, which it is not asked about -- one answer for each slot the
    plant expects the batch to send the role.

    Args:
        role: whose answers these are.

    Returns:
        The answers, each a `{"address", **fields}` object.
    """
    given = ANSWERS.get(role, {})
    answers = [{"address": address, **fields} for address, fields in given.items()]
    return answers + [
        {"address": address, "instruction": "clean", "reason": CLEAN_REASON}
        for address, proposer in PROPOSED.items()
        if address not in given and role != proposer
    ]


def write_answers(run: Path) -> dict[str, Path]:
    """Write each role's answers to the turn's batch, one file per role.

    A role's file is `answers-<role>.json` and holds `answers_for(role)`.
    `check --answers` refuses a file that leaves a sent slot unanswered or
    answers one that was never sent.

    Args:
        run: the run directory the smoke script writes into. Not created
            here -- the caller's own run directory already exists.

    Returns:
        role -> the path written.
    """
    paths: dict[str, Path] = {}
    for role in ANSWERS:
        path = run / f"answers-{role}.json"
        path.write_text(
            json.dumps(answers_for(role), indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        paths[role] = path
    return paths


def write_answers2(run: Path) -> dict[str, Path]:
    """Write each role's answers to the second turn's batch, one file per role.

    A role's file is `answers2-<role>.json` and holds `ANSWERS2[role]` as
    written, with no `clean` filled in: the second turn asks about what the
    first one left open, and every slot it sends is answered in that table by
    name.

    Args:
        run: the run directory the smoke script writes into. Not created
            here -- the caller's own run directory already exists.

    Returns:
        role -> the path written.
    """
    paths: dict[str, Path] = {}
    for role, given in ANSWERS2.items():
        answers = [{"address": address, **fields} for address, fields in given.items()]
        path = run / f"answers2-{role}.json"
        path.write_text(
            json.dumps(answers, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        paths[role] = path
    return paths


#: The refusal sub-plant for `decision-log.md Process: #181`: one of
#: `BAD_CITE_ROLE`'s answers has its sources replaced by this one, whose page
#: is real and whose line is past the end of it, so the cite does not resolve.
#: `check --answers` and `turn` each refuse the round for it, and the turn
#: writes nothing.
BAD_CITE = {"cite": "fib.py:999", "verbatim": "def wrapper(n):"}

#: Whose answers the sub-plant spoils, and which of them. The place is one the
#: role already answers with sources, so the only thing that changes is where
#: the evidence is cited from.
BAD_CITE_ROLE = "block-context"
BAD_CITE_ADDRESS = "fib.py@a2"


def write_bad_cite_answers(run: Path) -> Path:
    """Write `BAD_CITE_ROLE`'s answers with one source cited past a file's end.

    Every other answer in the file is the one `write_answers` writes, so a
    refusal of this file is a refusal of the cite and of nothing else.

    Args:
        run: the run directory the smoke script writes into.

    Returns:
        The path written, `answers-<role>-bad-cite.json`.
    """
    answers = [
        {**one, "sources": [dict(BAD_CITE)]}
        if one["address"] == BAD_CITE_ADDRESS
        else one
        for one in answers_for(BAD_CITE_ROLE)
    ]
    path = run / f"answers-{BAD_CITE_ROLE}-bad-cite.json"
    path.write_text(
        json.dumps(answers, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return path


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


#: What the proof's `store.py` must read once the chain closes, written out by
#: hand the same way from `STORE_FIXTURE` and `LANDINGS`. `b1` keeps the first
#: of its two sentences and `b3` reads with the second on a line of its own --
#: the partial move, whose origin keeps what the snippet left behind. `b5`
#: stands exactly as the fixture has it: the move sending it to `b12` is held
#: for the human, so neither end of it lands. `b7` reads with the correction
#: three roles cleaned their way to in the turn, and `c5` with the change its
#: own role wrote. `b9` is empty and `b8` holds its paragraph: the chief took
#: the contested move in at both ends, so the comment leaves the body and
#: stands above the declaration at the declaration's own indentation -- the
#: one place here that IS vacated, which is why `def total` follows its
#: comment with no blank line between them. `b11` keeps both its sentences,
#: the second in block-context's wording, and `b10` is empty: the move that
#: would have taken that sentence away was withdrawn by its own filer in the
#: second turn, so neither end of it lands either. `summary` is untouched by
#: this stage -- every role cleans its five places -- and it is what the
#: compacting stage reads out of this revise.
STORE_EXPECTED = (
    "def kept(log):\n"
    "    # Every lookup is recorded.\n"
    "    return len(log)\n"
    "\n"
    "\n"
    "def missed(log, found):\n"
    "    # A miss is a lookup the store had no answer for.\n"
    "    # Entries are never removed.\n"
    "    return kept(log) - found\n"
    "\n"
    "\n"
    "def part(log, found):\n"
    "    # Rounded before it is printed.\n"
    "    return round(found / kept(log), 2)"
    "  # two decimal places, as the report asks\n"
    "\n"
    "\n"
    "def empty(log):\n"
    "    # True when the store has answered nothing yet.\n"
    "    return kept(log) == 0\n"
    "\n"
    "\n"
    "# The number of lookups the store has seen.\n"
    "def total(log):\n"
    "    return kept(log)\n"
    "\n"
    "\n"
    "def seen(log, key):\n"
    "    # True when the key is in the log. Each lookup goes through this store.\n"
    "    return key in log\n"
    "\n"
    "\n"
    "def summary(log, found):\n"
    '    """Two numbers, one line.\n'
    "\n"
    "    The report prints the count and the share, in that order.\n"
    '    """\n'
    "    # The store keeps every lookup it has ever answered, and the count\n"
    "    # is what the report prints at the end of the day. Nothing is ever\n"
    "    # removed from it, so the number only goes up.\n"
    "    counted = kept(log)\n"
    "    # Rounded twice.\n"
    "    share = part(log, found)\n"
    "    # The share is printed beside the count, and the two are read\n"
    "    # together: a count with no share says nothing about the store,\n"
    "    # and a share with no count says nothing about the day.\n"
    "    return counted, share  # both, in order\n"
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


#: And of `store.py` from the same copy: the role's own correction at `b9`
#: lands and every other place it marked is a `clean` or a `query`, which
#: propose no text -- including `b9`'s move, which is another role's, and
#: `b11`'s, which is another role's too. The
#: comment stays inside `total`'s body here, since the draft is one role's
#: marks and the move is not among them.
ROLE_STORE_DRAFT = (
    "def kept(log):\n"
    "    # Every lookup is recorded. Entries are never removed.\n"
    "    return len(log)\n"
    "\n"
    "\n"
    "def missed(log, found):\n"
    "    # A miss is a lookup the store had no answer for.\n"
    "    return kept(log) - found\n"
    "\n"
    "\n"
    "def part(log, found):\n"
    "    # Rounded before it is printed.\n"
    "    return round(found / kept(log), 2)  # two places, as the report wants\n"
    "\n"
    "\n"
    "def empty(log):\n"
    "    # True when the store has answered nothing at all.\n"
    "    return kept(log) == 0\n"
    "\n"
    "\n"
    "def total(log):\n"
    "    # The count of lookups the store has seen.\n"
    "    return kept(log)\n"
    "\n"
    "\n"
    "def seen(log, key):\n"
    "    # True when the key is in the log. Every lookup goes through this store.\n"
    "    return key in log\n"
    "\n"
    "\n"
    "def summary(log, found):\n"
    '    """Two numbers, one line.\n'
    "\n"
    "    The report prints the count and the share, in that order.\n"
    '    """\n'
    "    # The store keeps every lookup it has ever answered, and the count\n"
    "    # is what the report prints at the end of the day. Nothing is ever\n"
    "    # removed from it, so the number only goes up.\n"
    "    counted = kept(log)\n"
    "    # Rounded twice.\n"
    "    share = part(log, found)\n"
    "    # The share is printed beside the count, and the two are read\n"
    "    # together: a count with no share says nothing about the store,\n"
    "    # and a share with no count says nothing about the day.\n"
    "    return counted, share  # both, in order\n"
)


def write_role_draft(root: Path) -> tuple[Path, Path, Path]:
    """Write the three role drafts to `root`, as `write_expected` writes.

    Args:
        root: the directory to write into. Not created here -- the smoke
            script creates its run's `role-expected` directory first.

    Returns:
        The three paths written, `fib.py`'s first.
    """
    fib = root / "fib.py"
    fib.write_text(ROLE_DRAFT, encoding="utf-8", newline="\n")
    rate = root / "rate.py"
    rate.write_text(ROLE_RATE_DRAFT, encoding="utf-8", newline="\n")
    store = root / "store.py"
    store.write_text(ROLE_STORE_DRAFT, encoding="utf-8", newline="\n")
    return fib, rate, store


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
#: the fixture's prose, which the role only queried. `fib.py` and `store.py`
#: are drafted from the same copy and are `ROLE_DRAFT` and `ROLE_STORE_DRAFT`
#: unchanged -- the collide move touches no place of either.
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


def write_collide_draft(root: Path) -> tuple[Path, Path, Path]:
    """Write what the collide copy drafts, as `write_expected` writes.

    Args:
        root: the directory to write into. Not created here -- the smoke
            script creates its run's `collide-expected` directory first.

    Returns:
        The three paths written, `fib.py`'s first.
    """
    fib = root / "fib.py"
    fib.write_text(ROLE_DRAFT, encoding="utf-8", newline="\n")
    rate = root / "rate.py"
    rate.write_text(COLLIDE_RATE_DRAFT, encoding="utf-8", newline="\n")
    store = root / "store.py"
    store.write_text(ROLE_STORE_DRAFT, encoding="utf-8", newline="\n")
    return fib, rate, store


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


#: The second stage's label in the topology and the one role it dispatches.
#: Its `reads` is `revise:4`, so `distribute` seeds it from the revise the
#: first stage's `proof` pulled rather than from the original -- the stage's
#: own `reads` deciding which tree it is cut from
#: (`desk.topology.seeded_from_problem`).
SECOND_STAGE = "5"
SECOND_ROLE = "ownership-context"

#: What that stage rules, on the revise's `fib.py`: one `correct` over the
#: module docstring, a paragraph the first stage already changed, so the
#: correction is measured against the revised text rather than the original's.
#: No other role reads the place, so the proposal stands at once
#: (`decision-log.md Process: #180`).
SECOND_CORRECT = "fib.py@a0"
SECOND_CLAIM = {"false": "why it is counted", "true": "why the count matters"}

#: And a `clean` at every other prose place the revise carries, written out by
#: hand from `EXPECTED` -- the addresses the revise has, which are not the
#: addresses the original had. `tests/gates/test_smoke_fixture.py` reads the
#: revise's own page and holds this list to it.
SECOND_CLEAN = (
    "fib.py@b0",
    "fib.py@c1",
    "fib.py@a1",
    "fib.py@c3",
    "fib.py@a2",
    "fib.py@c6",
    "fib.py@b8",
    "fib.py@b9",
    "fib.py@a3",
    "fib.py@c12",
    "fib.py@b17",
)


def write_second_plant(run: Path) -> dict[str, Path]:
    """Write the second stage's clause files and its clean list.

    One file per key of `SECOND_CLAIM`, which the stage's `mark` call passes
    by `@path` as every other clause in the plant is passed, and
    `second-clean.json`, which the smoke script loops over. Named with the
    stage's own prefix rather than through `file_for`, since the revise
    spells its addresses the way the original does and a file named for
    `fib.py@a0` would be the first stage's to name.

    Args:
        run: the run directory the smoke script writes into.

    Returns:
        one path per file written, keyed by the `SECOND_CLAIM` key, plus
        `"clean"` for `second-clean.json`.
    """
    paths = {}
    for key, value in SECOND_CLAIM.items():
        path = run / f"second-a0-{key}.txt"
        path.write_text(value, encoding="utf-8", newline="\n")
        paths[key] = path
    clean = run / "second-clean.json"
    clean.write_text(
        json.dumps(list(SECOND_CLEAN)) + "\n", encoding="utf-8", newline="\n"
    )
    paths["clean"] = clean
    return paths


#: What the second stage's proof must read, written out by hand from
#: `EXPECTED` and the correction above: the module docstring's last clause is
#: the one thing that moves, and every other line is the revise's. `# base
#: case` is the line the plant is watching -- the first stage left it exactly
#: as the fixture had it and the second stage cleans it, so a revise that
#: dropped the paragraphs nobody changed would be caught here.
SECOND_EXPECTED = (
    '"""Fibonacci, counted so the recursion can be seen -- and why the count '
    'matters."""\n'
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


def write_second_expected(root: Path) -> Path:
    """Write `SECOND_EXPECTED` to `root / "fib.py"`, as `write_expected` writes.

    Args:
        root: the directory to write into. Not created here -- the smoke
            script creates its run's `second-expected` directory first.

    Returns:
        The path written.
    """
    path = root / "fib.py"
    path.write_text(SECOND_EXPECTED, encoding="utf-8", newline="\n")
    return path


#: The places the author approves in the partial approval, and the one whose
#: approval is refused. `store.py@b7` and `store.py@c5` are settled places on
#: one page with no move between them, so the run that sets them leaves a
#: `store.py` differing from the fixture at those two places and nowhere
#: else. `store.py@b9` is one end of the move the chief took in at both, and
#: `store.py@b8` is the end it leaves out (`Process: #192`).
APPROVED = ("store.py@b7", "store.py@c5")
HALF_A_MOVE = "store.py@b9"
THE_OTHER_END = "store.py@b8"


#: What `proof --only APPROVED` must leave as `store.py` -- `STORE_FIXTURE`
#: with those two places set and every other line of it untouched, written
#: out by hand the same way the expected pages above are. The comment in
#: `empty` reads as the roles agreed it and the trailing comment on `part` as
#: its own role wrote it; the partial move at `b1` and `b3`, the move the
#: chief took in at `b9` and `b8`, and the sentence `b11` keeps are all
#: decided on this proof and none of them is approved here, so each stands as
#: the fixture has it.
PARTIAL_EXPECTED = (
    "def kept(log):\n"
    "    # Every lookup is recorded. Entries are never removed.\n"
    "    return len(log)\n"
    "\n"
    "\n"
    "def missed(log, found):\n"
    "    # A miss is a lookup the store had no answer for.\n"
    "    return kept(log) - found\n"
    "\n"
    "\n"
    "def part(log, found):\n"
    "    # Rounded before it is printed.\n"
    "    return round(found / kept(log), 2)"
    "  # two decimal places, as the report asks\n"
    "\n"
    "\n"
    "def empty(log):\n"
    "    # True when the store has answered nothing yet.\n"
    "    return kept(log) == 0\n"
    "\n"
    "\n"
    "def total(log):\n"
    "    # The number of lookups the store has seen.\n"
    "    return kept(log)\n"
    "\n"
    "\n"
    "def seen(log, key):\n"
    "    # True when the key is in the log. Every lookup goes through this store.\n"
    "    return key in log\n"
    "\n"
    "\n"
    "def summary(log, found):\n"
    '    """Two numbers, one line.\n'
    "\n"
    "    The report prints the count and the share, in that order.\n"
    '    """\n'
    "    # The store keeps every lookup it has ever answered, and the count\n"
    "    # is what the report prints at the end of the day. Nothing is ever\n"
    "    # removed from it, so the number only goes up.\n"
    "    counted = kept(log)\n"
    "    # Rounded twice.\n"
    "    share = part(log, found)\n"
    "    # The share is printed beside the count, and the two are read\n"
    "    # together: a count with no share says nothing about the store,\n"
    "    # and a share with no count says nothing about the day.\n"
    "    return counted, share  # both, in order\n"
)


#: The compacting stage: a third stage reading the revise the first stage's
#: proof pulled, dealt the `b` and `c` places whose text runs over a cap of
#: two lines, and admitting the edit instructions and `clean`
#: (`decision-log.md Process: #193`). Its row is appended to the topology the
#: `topology --build` call writes, which is where a run's author would type
#: it.
COMPACTING_STAGE = "6"
COMPACTING_ROLE = "block-context"
COMPACTING_CAP = 2
COMPACTING_ROW = (
    "\n"
    "[[stage]]\n"
    f'name = "{COMPACTING_STAGE}"\n'
    'kind = "editorial"\n'
    'reads = "revise:4"\n'
    f"cap = {COMPACTING_CAP}\n"
    'series = ["b", "c"]\n'
    'admits = ["patch", "drop", "add", "clean"]\n'
    "  [[stage.dispatch]]\n"
    f'  role = "{COMPACTING_ROLE}"\n'
)

#: `summary`'s five places, which the first stage's four roles clean and the
#: compacting stage reads out of the revise. They carry the same addresses in
#: both trees: `summary` is appended below everything the first stage edits.
UNTOUCHED = (
    "store.py@a7",
    "store.py@b13",
    "store.py@b14",
    "store.py@b15",
    "store.py@c15",
)

#: The two of them the stage deals: over the cap, and in a series it names.
#: The docstring `a7` runs to four lines and is not dealt because `a` is not
#: in the series; `b14` and `c15` stand on one line each.
DEALT = ("store.py@b13", "store.py@b15")

#: The paragraph at `b13`, as `STORE_FIXTURE` writes it and as the revise
#: still holds it -- the `claim.from` of the one `patch`, which quotes the
#: whole paragraph because the whole paragraph is what a condensation
#: replaces. `tests/gates/test_smoke_fixture.py` holds it to the fixture.
OVER_THE_CAP = (
    "    # The store keeps every lookup it has ever answered, and the count\n"
    "    # is what the report prints at the end of the day. Nothing is ever\n"
    "    # removed from it, so the number only goes up."
)

#: What the compacting role condenses `b13` to, written out by hand -- the
#: `claim.to` of that patch.
CONDENSED = (
    "    # Every lookup is kept, so the count the report prints\n"
    "    # at the end of the day only goes up."
)

#: And why it leaves `b15` at length: a paragraph that cannot come under the
#: cap is reported, never cut (`references/compact.md`), which for a dealt
#: place is a `clean` carrying the reason.
KEPT_AT_LENGTH = (
    "each sentence here is the reason for the next, and cutting one leaves"
    " the other two unexplained"
)

#: The instruction the stage does not admit, planted to be refused by `mark`.
REFUSED_INSTRUCTION = "correct"


def write_compacting(run: Path) -> dict[str, Path]:
    """Write the compacting stage's plant: its table, and the patch's clauses.

    Args:
        run: the run directory the smoke script writes into.

    Returns:
        `{"table": compacting.json, "from": the paragraph as it stands,
        "to": the condensed paragraph}`. The script reads the table for the
        stage's row, the places it deals, and the places every role cleans in
        the first stage; the two clause files are what its `mark` call passes
        by `@path`.
    """
    table = run / "compacting.json"
    table.write_text(
        json.dumps(
            {
                "stage": COMPACTING_STAGE,
                "role": COMPACTING_ROLE,
                "row": COMPACTING_ROW,
                "untouched": list(UNTOUCHED),
                "dealt": list(DEALT),
                "patched": DEALT[0],
                "kept": DEALT[1],
                "reason": KEPT_AT_LENGTH,
                "refused": REFUSED_INSTRUCTION,
            }
        ),
        encoding="utf-8",
        newline="\n",
    )
    clauses = {
        "from": (run / "compacting-from.txt", OVER_THE_CAP),
        "to": (run / "compacting-to.txt", CONDENSED),
    }
    for path, text in clauses.values():
        path.write_text(text, encoding="utf-8", newline="\n")
    return {"table": table, **{key: path for key, (path, _t) in clauses.items()}}


def write_approval(run: Path) -> Path:
    """Write the author's partial approval -- the addresses `--only` names.

    The script reads the addresses from here rather than spelling them
    itself, as it reads `second-clean.json` for the second stage's places,
    so the plant and the invocation cannot come to name different places.

    Args:
        run: the run directory the smoke script writes into.

    Returns:
        The path written, holding
        `{"approved": [...], "half-a-move": <address>}`.
    """
    path = run / "approval.json"
    path.write_text(
        json.dumps({"approved": list(APPROVED), "half-a-move": HALF_A_MOVE}),
        encoding="utf-8",
        newline="\n",
    )
    return path


#: What the compacting stage's proof must hold as `store.py`: the revise's
#: own page with `b13` condensed and nothing else touched. Its `b15` stands
#: at three lines, which is the place the role reported rather than cut, and
#: the docstring `a7` stands at four, which the stage was never dealt.
COMPACTED_EXPECTED = (
    "def kept(log):\n"
    "    # Every lookup is recorded.\n"
    "    return len(log)\n"
    "\n"
    "\n"
    "def missed(log, found):\n"
    "    # A miss is a lookup the store had no answer for.\n"
    "    # Entries are never removed.\n"
    "    return kept(log) - found\n"
    "\n"
    "\n"
    "def part(log, found):\n"
    "    # Rounded before it is printed.\n"
    "    return round(found / kept(log), 2)"
    "  # two decimal places, as the report asks\n"
    "\n"
    "\n"
    "def empty(log):\n"
    "    # True when the store has answered nothing yet.\n"
    "    return kept(log) == 0\n"
    "\n"
    "\n"
    "# The number of lookups the store has seen.\n"
    "def total(log):\n"
    "    return kept(log)\n"
    "\n"
    "\n"
    "def seen(log, key):\n"
    "    # True when the key is in the log. Each lookup goes through this store.\n"
    "    return key in log\n"
    "\n"
    "\n"
    "def summary(log, found):\n"
    '    """Two numbers, one line.\n'
    "\n"
    "    The report prints the count and the share, in that order.\n"
    '    """\n'
    "    # Every lookup is kept, so the count the report prints\n"
    "    # at the end of the day only goes up.\n"
    "    counted = kept(log)\n"
    "    # Rounded twice.\n"
    "    share = part(log, found)\n"
    "    # The share is printed beside the count, and the two are read\n"
    "    # together: a count with no share says nothing about the store,\n"
    "    # and a share with no count says nothing about the day.\n"
    "    return counted, share  # both, in order\n"
)


def write_compacted_expected(root: Path) -> Path:
    """Write `COMPACTED_EXPECTED` to `root / "store.py"`, as `write_expected` writes.

    One page and no other: the compacting stage's docket schedules the page
    its one condensed place sits on, and a revise holds only what its docket
    schedules.

    Args:
        root: the directory to write into. Not created here.

    Returns:
        The path written.
    """
    path = root / "store.py"
    path.write_text(COMPACTED_EXPECTED, encoding="utf-8", newline="\n")
    return path


def write_partial_expected(root: Path) -> Path:
    """Write `PARTIAL_EXPECTED` to `root / "store.py"`, as `write_expected` writes.

    One page and no other: a revise holds only the pages its docket
    schedules, and a partial approval over two places of `store.py`
    schedules that page alone.

    Args:
        root: the directory to write into. Not created here -- the smoke
            script creates its run's `partial-expected` directory first.

    Returns:
        The path written.
    """
    path = root / "store.py"
    path.write_text(PARTIAL_EXPECTED, encoding="utf-8", newline="\n")
    return path


def write_expected(root: Path) -> tuple[Path, Path, Path]:
    """Write `EXPECTED`, `RATE_EXPECTED` and `STORE_EXPECTED` to `root`.

    Written with an explicit LF newline, as `write_fixture` writes, so each
    carries the line endings the proof sets from its fixture. The smoke
    script's `diff` stage compares this directory with the proof's using
    `git diff --no-index` under `core.autocrlf=false`, so a line-ending
    difference fails it as a text one does.

    Args:
        root: the directory to write into. Not created here -- the smoke
            script creates its run's `expected` directory first.

    Returns:
        The three paths written, in the order the fixtures are written.
    """
    fib = root / "fib.py"
    fib.write_text(EXPECTED, encoding="utf-8", newline="\n")
    rate = root / "rate.py"
    rate.write_text(RATE_EXPECTED, encoding="utf-8", newline="\n")
    store = root / "store.py"
    store.write_text(STORE_EXPECTED, encoding="utf-8", newline="\n")
    return fib, rate, store
