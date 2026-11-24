r"""A SKETCH. An EXTERNAL address: a coordinate into a file this system does not set.

!! NOTHING IMPORTS THIS YET. It is a shape put down for review, not a module in
service -- Roy, 2026-08-24: *"sketch a module for external_address."* Every open
question below is marked, and none is answered by guessing.

=== WHY IT IS NOT THE ADDRESS WE ALREADY HAVE

An `address` -- `pkg:mod.py@b3` -- names a PLACE on a page: the fourth gap, the
docstring of a declaration. It survives a prose edit above it, which is the
whole reason it exists, and it is only meaningful for a file this system reads
into a page and sets back.

An EXTERNAL address names a COORDINATE in a file the system does NOT rebuild --
a reference doc a role cites, and recommends a change to. Roy, 2026-08-24: *"We
probably need an external address to allow modification of reference docs.
Path:line_num:chars"*, and on where it belongs: *"the agents area because they
are going to need it because they cite sources using it and make recommendations
to it."*

| | address | external address |
| --- | --- | --- |
| names | a place on a page | a coordinate in a file |
| spelled | `pkg:mod.py@b3` | `path:line:chars` |
| survives an edit above it | YES -- the point of it | NO |
| the system rebuilds the file | yes, galley then compositor | no |

!! AND THE LINE-NUMBERED FORM IS RETIRED, WHICH THIS MUST NOT QUIETLY UNDO.
`docs/vocabulary.md`, Retired: **`line address` (`mod.py:1-24`) -> `address`**,
because it was *"true of ONE file state, and this tool edits prose"*;
`addresser.line_address` was DELETED 2026-08-20. ! The retirement stands. What
makes this legitimate is that it answers a different question -- and what makes
it SAFE is the rule below, which the retired form never had.

!! A COORDINATE IS ONLY MEANINGFUL BESIDE THE SHA OF THE FILE IT WAS TAKEN FROM.
That is the same guard as `machine.repo.sha_of`, one artifact over: an external
address recorded against a file that has since moved names something else, and
nothing in the string can say so. **Pair or refuse.**

=== IT ALREADY EXISTS, HOMELESS

`record.CITE` is `file:line` or `file:start-end` today, and its own comment says
the quiet part: *"WHAT A CITATION LOOKS LIKE is part of a record's shape, so it
sits here and not with the checks. The reader parses SOURCES with these and the
desk resolves them with the same two, WHICH IS WHY NEITHER MODULE CAN OWN
THEM."* It is declared in `binder/record.py` and resolved in `desk/desk.py`.

! So this module is not a new format. It is the home that comment describes and
does not have, plus the character precision Roy asked for.

=== PLACEMENT IS PROVISIONAL, AND SAYS SO

It sits in `desk/` because a ROLE is what cites and recommends. Roy: *"Currently
doesn't live besides the other part, but it could become part of the binder for
the code audit references piece so not certain."* ! Recorded as provisional in
the code and in `docs/decision-log.md` rather than settled by where it landed
first -- `conventions.md` asks for exactly that.

=== OPEN, AND NOT GUESSED

1. `chars` -- A COLUMN OR A SPAN? `path:12:5` names a point; `path:12:5-9` names
   the text a recommendation would replace. The second is the one that can carry
   an edit; the first cannot say how much it covers. NOT RULED.
2. WHICH END IS `chars` COUNTED FROM, and in what -- bytes, characters, or
   grapheme clusters? A tab counts once as a character and eight as a column,
   and this repo already refuses to guess about text (see `constants.text_lines`).
3. DOES IT SUBSUME `record.CITE`, or sit beside it? Subsuming means every
   existing `SOURCES` citation is an external address with the `chars` half
   absent, which reads well and is a change to a shipped format.
4. ONE-BASED OR ZERO-BASED. The rest of this system is one-based on lines
   (`original_start`), and every editor is one-based on columns. Almost certainly
   one-based, and unstated is how it gets got wrong.

=== THE HAZARD THAT IS NOT OPEN, BECAUSE IT IS ALREADY MEASURED

`:` IS ALREADY LOAD-BEARING TWICE. It is `addresser.SEPARATOR`, which `flatten`
joins path segments on -- chosen 2026-08-19 precisely because Windows forbids it
in a filename -- and it opens a Windows drive letter, `C:\...`. A third field
makes the parse more fragile, not less: `C:\x.py:12:5` has FOUR colons and only
the last two are structure. ! Whatever shape is ruled, the parser is written
against that string as a test case before it is believed.
"""

from typing import NamedTuple


class ExternalAddress(NamedTuple):
    """A coordinate in a file this system does not set.

    ! A `NamedTuple` for the reason `addresser.Address` is one: the alternative
    is callers subscripting `[1]`, and this repo has the measurement -- fifteen
    such sites before `Address` was named.

    Attributes:
        path: the file, as the repo sees it.
        line: 1-based, matching `original_start` -- see OPEN 4.
        start: the first character of the span, or `None` for a whole line.
        end: the last, or `None` when `start` names a point -- see OPEN 1.
    """

    path: str
    line: int
    start: int | None = None
    end: int | None = None


def sketch() -> None:
    """There is no implementation, and that is deliberate.

    A parser written before OPEN 1-4 are ruled would answer them by accident,
    which is how the retired `line address` got its shape the first time.
    """
    raise NotImplementedError(
        "external_address is a sketch -- see the module docstring"
    )
