"""What a pCST NODE is -- the unit every other module reads.

A pCST is a *pseudo* Concrete Syntax Tree: this line is code, this PART of a line
is code, this line is comment, this line is docstring. Pseudo because a real CST
would carry the names and the symbols precisely, and this carries only which
lines are which -- which is what a reviewer of COMMENTS needs and no more.
`census.py` builds one; this says what the thing it builds is made of.

!! IT IS A FLAT LIST, AND THE ADDRESS IS WHY. Roy, 2026-08-18: *"it probably is
just a flat list because of the way we defined the address ... a CST has it but
it is not actually one, which is why it is a pseudoCST."* An address is an
ORDINAL over a linear sequence -- `b3` is "after the 3rd code line", `a5` is
"the 5th declaration" -- and an ordinal cannot express containment. So the
flatness is not an omission this module should fix; it is what the addressing
forces, and it is the second reason the name says *pseudo*.

! Nothing here asks a tree question either. Measured 2026-08-18 across the
shipped scripts: ZERO containment tests, and every consumer is a flat scan by
path, a lookup by line, an ordered walk or a range splice. A tree would be
flattened again at each of them.

! Where hierarchy IS wanted it arrives as a stamped FACT, not a structure: a
block's enclosing declaration, which the Python AST already knows and which 191
of this repo's 266 anchorless prose blocks sit inside. Depth is 1 for 182 of
those 191, so a parent link is the shape that fits and a tree is not.

!! IT IS A LEAF, and that is the whole reason it exists. `Block` lived in
`census.py`, which sits at the top of the import graph -- `census` imports
`addresser` imports `galley` -- so the three modules that READ blocks could not
import the definition of one. Measured 2026-08-18: 21 untyped `block.get(...)`
reads across `galley`, `addresser` and `record`, and two kind sets that ended up
in `galley` because it was the deepest module all three could reach. Letting the
import graph choose a module's subject is how `galley` came to announce the
proposed text AND the vocabulary of a syntax tree.
"""

from dataclasses import dataclass, field

# !! EVERY LINE HAS AN ADDRESS, AND SO DOES EVERY POTENTIAL LINE. Roy,
# 2026-08-19: without an empty `c` "you can't specify that the comment belongs
# at the end of the code line", and without an empty `b` "you can't specify that
# the code should have multiple lines of comment above it". So each series has
# an EMPTY kind, and they are what an `add` cites:
#
#   a   `undocumented`  a declaration with no docstring
#   b   `interval`      a gap with no prose
#   c   `margin`        a code line with no trailing comment
#
# !! KINDS THAT OCCUPY NO LINES OF THEIR OWN. A `trailing-comment` sits on a
# code line, and an `interval` and an `undocumented` declaration are both
# EMPTY -- a place where prose could go and does not. Counting any of them as
# occupied would drop a real code line from the count and renumber every `b`
# below it.
OCCUPIES_NOTHING = ("trailing-comment", "margin", "interval", "undocumented")
# !! HOLDS NO PROSE -- a DIFFERENT set, and the two are not interchangeable. A
# `trailing-comment` occupies no lines of its own but is prose; an `interval`
# and an `undocumented` declaration are places where prose could go and does
# not. This set is what "addressable, not accountable" means: they are cited by
# an `add` and they get no seeded record.
HOLDS_NO_PROSE = ("interval", "undocumented", "margin")


@dataclass
class Block:
    """The interval between two lines of code -- the unit a reviewer rules on.

    ! An interval holding no prose is a block too, `kind="interval"`. It is the
    only thing an `add` can cite: the finding is that a constraint exists in
    code and NOWHERE in prose, so it is about an empty interval, and the record
    requires a `BLOCK` index. Without one an `add` had to borrow a neighbour's.
    """

    path: str
    start: int
    end: int
    kind: str  # comment | docstring | trailing-comment | interval | undocumented
    lines: int
    text: str  # the run JOINED, so a wrapped claim matches as one string
    # !! WHAT THIS BLOCK IS ATTACHED TO, and it is ONE-TO-MANY THE OTHER WAY:
    # an anchor has MANY addresses -- its own `a`, the `b` above it, the `c`
    # beside it, every `b` and `c` in its body -- and an address has ONE anchor.
    #
    # ! It holds a DECLARATION'S NAME for a block that owns its lines, and THE
    # LINE OF CODE, verbatim, for a block that sits beside code -- see
    # `census._anchor_of`. Roy, 2026-08-19: *"the anchor isn't the technical
    # symbols and their precise semantic meaning and code use. It is 'the line
    # of code' -- the exact characters in that line of code."* The two are
    # stated here rather than left to a reader because a field with an
    # undeclared second meaning is the defect, not the second meaning.
    anchor: str = ""
    # !! WHICH DECLARATION THIS DOCUMENTS, as an ordinal: 0 is the module and
    # 1..N its declarations in SOURCE order. -1 says this block documents no
    # declaration -- every comment and every interval.
    #
    # !! STATED HERE BECAUSE ONLY A PARSER KNOWS IT. Python's docstring sits
    # AFTER its `def` and Rust's `///` sits BEFORE its `fn`, so position cannot
    # answer which declaration a doc belongs to and the addresser must not
    # guess. It reads this and names it `@aN`.
    declares: int = -1
    # !! THE LINE THE DECLARATION ITSELF OPENS ON, so an anchor's OTHER places
    # can be found: the `c` beside its `def` and the `b` above it. Without it a
    # consumer has to infer the line from the docstring's position, which is
    # exactly the kind of inference that breaks on the next language -- Rust's
    # doc sits BEFORE its `fn`, Python's after. 0 where none applies.
    declared_at: int = 0
    tier: str = "lexical"  # which question set this file's census can answer
    # !! WHICH PLACE THIS IS, as against where it sits -- see `addresser.address`.
    # Stamped in the path-normalising loop, the only place holding the file
    # text, the finished block list and the repo-relative path at once.
    address: str = ""
    annotations: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)

    @property
    def widest(self) -> int:
        """The longest raw line in this block, in characters."""
        return max((len(ln) for ln in self.raw_lines), default=0)

    raw_lines: list[str] = field(default_factory=list)
    # !! THE LINES AN EDIT TO THIS BLOCK OCCUPIES, which is NOT always the
    # range that ADDRESSES it. A prose block is replaced, so the two coincide.
    # An empty INTERVAL is inserted into: `start` and `end` are the two lines
    # of CODE that bound it, and writing over them would delete code, so its
    # edit range is the gap between them -- `(n+1, n)` for adjacent lines,
    # which is an empty slice and therefore a pure insertion.
    #
    # !! IT IS COMPUTED HERE BECAUSE ONLY HERE IS IT KNOWABLE. `intervals()`
    # walks edges that carry SENTINELS -- 0 above the first code line, one past
    # the last below it -- and then clamps them, because a citation has to
    # resolve to a real line. The clamp is what says "this gap is at the file
    # boundary", and it destroys which SIDE it is on. Measured 2026-08-17: an
    # `add` citing the gap above the first line of a file landed BELOW that
    # line, and on a one-line file the gap above and the gap below reduced to
    # the same address, so a reviewer could not tell them apart either.
    #
    # ! Left 0/0 by a producer, they mirror `start`/`end` -- see
    # `__post_init__`. That is what makes this safe to add without visiting
    # every construction site.
    edit_start: int = 0
    edit_end: int = 0
    # !! WHERE THE `c` PLACE BEGINS ON `edit_start`, 1-based like every other
    # position this census states -- `start`, `end`, `edit_start`, `edit_end`.
    # Two values:
    #
    #    0      the block owns its lines WHOLE. Not a column: 0 is not one, and
    #           that is what makes it a sentinel rather than an accident. Every
    #           `comment`, `docstring` and `interval`.
    #    1..N   ONE PAST THE LAST CHARACTER OF CODE on that line, which is where
    #           the room beside the code starts. A `trailing-comment`, a
    #           `margin`, a block comment opened after a statement. It is what
    #           lets the galley write one without deleting the code: the splice
    #           keeps `line[: edit_column - 1]`.
    #
    # !! IT IS THE END OF THE CODE, NOT THE START OF THE PROSE, and Roy ruled
    # it 2026-08-19: *"c addresses start at the end of the code on the line."*
    # So the whitespace separating a statement from its trailing comment belongs
    # to the `c` place, and one rule covers both kinds -- a `margin` and the
    # `trailing-comment` that would replace it carry the SAME column. Pointing
    # at the `#` instead made them differ, and made a `drop` a special case: the
    # kept head ended in the separator of a comment that was gone.
    #
    # !! IT IS STATED BY THE PRODUCER BECAUSE NO READER CAN INFER IT. Two tried,
    # both by testing whether the stored text is a proper SUFFIX of the physical
    # line, and the test cannot work: `blocks_stdlib` stores the WHOLE line for
    # a trailing comment, so the suffix test answers False. Measured 2026-08-18:
    # censusing `z = 3  # trailing` and editing that block produced a galley
    # reading `# reworded trailing` where the statement had been -- a deleted
    # statement, in the one artefact a human is asked to approve.
    #
    # ! IT REPLACED A BOOLEAN, `whole_lines`, which answered only WHETHER code
    # came first. That was enough to REFUSE the write and not enough to make it,
    # and the `c` series exists to be written. Roy, 2026-08-19: *"c needs to be
    # writeable. It is the reason c is not an extension of b."*
    edit_column: int = 0

    def __post_init__(self) -> None:
        """Default the edit range to the addressing range."""
        if not self.edit_start and not self.edit_end:
            self.edit_start, self.edit_end = self.start, self.end
