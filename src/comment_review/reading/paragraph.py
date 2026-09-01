"""What a PARAGRAPH is: one unit of prose, or the empty place where prose could go.

!! IT LIVED INSIDE THE LEXER UNTIL 2026-08-31, AND THAT WAS A KNOT RATHER THAN A
CHOICE. Roy: *"it kind of is in the wrong place for the set of containers but it
also had a valid reason for being stuck there ... circular imports a long time
ago having to do with addresses and Series and cues and all of that. The
addresser in particular I think was a sticky point."*

!! THE REASON IS GONE, AND IT WENT WITH TWO FIELDS AND A TYPE. MEASURED
2026-08-31: the class body references `dataclass`, `field` and builtins --
**nothing from this package at all**. `original_column` and `declares` were
deleted the same day (`decision-log.md Process: #69`), and `kind` is a plain
`str`, so the type no longer reaches for `Series`, for a cue, or for the
addresser.

! **AND IT IS THE SECOND TIME THIS CORRECTION HAS BEEN MADE.** `binder/page.py`
records the first: *"`Paragraph` first lived in `census.py`, at the top of the
graph, so the modules that READ paragraphs could not import the definition of
one -- 21 untyped `paragraph.get(...)` reads."* It moved down into the lexer and
stopped being at the top; what it did not stop being is a definition living
inside a BUILDER.

!! WHY NOT WITH `Page`, WHICH IS THE OBVIOUS HOME. `binder` imports `reading` in
four modules, so `reading.lexer` -- which BUILDS paragraphs -- would have to
import `binder` back. That edge is the cycle, and it is not about a paragraph:
it is where the page's own dependencies already point. Roy: a page *"is also all
of the leadings ... it only tacks on a couple of attributes but those are
load-bearing"*, so `Page` stays where it is and this sits beneath both.

! A LEAF, LIKE `series` AND `machine`. It imports nothing from this package, so
the lexer that makes one and every module that reads one take it from the same
declaration instead of from each other.
"""

from dataclasses import dataclass, field


@dataclass
class Paragraph:
    """The interval between two lines of code -- the unit a reviewer rules on.

    ! An interval holding no prose is a paragraph too, `kind="interval"`. It is the
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
    # !! WHAT THIS PARAGRAPH IS ATTACHED TO, and it is ONE-TO-MANY THE OTHER WAY:
    # an anchor has MANY addresses -- its own `a`, the `b` above it, the `c`
    # beside it, every `b` and `c` in its body -- and an address has ONE anchor.
    #
    # !! IT IS ALWAYS THE LINE OF CODE, VERBATIM -- never a name, and never a
    # symbol. Roy: *"the anchor isn't the technical symbols and their precise
    # semantic meaning and code use. It is 'the line of code' -- the exact
    # characters in that line of code."* An `a` carries the line that DECLARES
    # it, `def f():` and not `f`; see `_anchor_of`.
    anchor: str = ""
    # !! WHICH DECLARATION THIS DOCUMENTS, as an ordinal: 0 is the module and
    # 1..N its declarations in SOURCE order. -1 says this paragraph documents no
    # declaration -- every comment and every interval.
    #
    # !! STATED HERE BECAUSE ONLY A PARSER KNOWS IT. Python's docstring sits
    # AFTER its `def` and Rust's `///` sits BEFORE its `fn`, so position cannot
    # answer which declaration a doc belongs to and the addresser must not
    # guess. It reads this and names it `@aN`.
    # !! THE LINE THIS PLACE'S ANCHOR SITS ON, so an anchor's OTHER places can
    # be found: the `c` beside its `def`, the `b` above it, its own `a`.
    # Without it a consumer has to infer the line from the prose's position,
    # which is exactly the inference that breaks on the next language --
    # Rust's doc sits BEFORE its `fn` and Python's after.
    #
    # !! IT WAS `declared_at` AND FILLED FOR `a` ALONE, which is why
    # `for_anchor` could only fall back to it with a declaration in hand. The
    # fact was never about declaring: it is the anchor's line, and every
    # series has one. Renamed and filled for all of them 2026-08-20.
    #
    # !! `None` WHERE THE ANCHOR IS A SENTINEL -- `<module>` at the head of the
    # walk, `<eof>` at its foot. Neither sits on a line, and this says so
    # rather than answering 0.
    #
    # ! IT WAS 0 FOR BOTH until 2026-08-22, and the two were not the same fact.
    # Line 0 is genuinely above line 1, so the head sorted first and rendered at
    # the top and both were correct; the foot inherited those behaviours and
    # both were wrong. Roy: *"the end of file getting a 0 is non-functional
    # filling in for a missing value."*
    anchor_line: int | None = None
    # !! THE ORDINAL OF THAT ANCHOR AMONG THE LINES OF CODE, and it is what
    # ORDERS a record now. Roy, 2026-08-21: *"where it is in the original and
    # where it ends up on the resulting page can be two very different things --
    # but a single shift on anchor_num and you know it is all trash after
    # rereading."* This tool edits prose and every prose edit moves the lines
    # below it; the Nth line of code stays the Nth line of code.
    #
    # ! CARRIED ALONGSIDE `anchor`, never instead of it. An ordinal cannot see a
    # rename in place and the text cannot cheaply see an insertion; the pair
    # sees both, which is the whole drift question in two fields.
    anchor_num: int = 0
    # !! WHICH PLACE THIS IS, as against where it sits -- see `cues.address`.
    # Stamped in the path-normalising loop, the only place holding the file
    # text, the finished paragraph list and the repo-relative path at once.
    address: str = ""
    # !! A LABEL, NOT AN ADDRESS, and only LEADING carries one. Roy, 2026-08-22:
    # *"we need to keep the symbol for the leading, because the page/symbol map
    # has really helped in understanding what each line is, so that we maintain
    # the cover."* `d0` marks a run of blank lines in `scripts/render_page.py`'s
    # margin, so a reader can see that every line on the page belongs to
    # something.
    #
    # !! IT IS NOT AN `address` BECAUSE LEADING IS NOT A PLACE, and putting it
    # in that field is what made `d` fail the substitution the other four series
    # satisfy. Roy: *"it has no anchor, and so by the LSR -- any child class has
    # to be able to answer its parent class's answers as well, correctly -- it
    # breaks that rule."* MEASURED: `a0` and every `f` answer `<module>` and
    # every `b` and `c` answer a line of code; a `d` answered `""`, which is the
    # absence of an answer rather than a different one.
    #
    # ! WHICH FOLLOWS FROM WHERE IT COMES FROM. Every other place exists because
    # the WALK reached a trigger -- and the trigger IS the anchor. A `d` exists
    # because the LEXER found blank lines, so there was never a trigger for it
    # to be anchored to. `addresser.SERIES` holds four series; `LEAD` is a symbol.
    symbol: str = ""
    annotations: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)

    # !! THE PARAGRAPH'S OWN CHARACTERS, EXACTLY AS THE FILE HOLDS THEM -- its
    # lines whole where it owns them, and from the end of the code onward on
    # the first line where code comes first. With `anchor` holding that code,
    # the two RECONSTRUCT the line: `anchor + raw_lines[0]` is what is on disk.
    #
    # !! SO THE CUT IS RECORDED IN THE LINES THEMSELVES, NOT IN A FIELD. A
    # `Paragraph.original_column` held it until 2026-08-31 and every reader
    # tested it for TRUTHINESS -- *is this beside code* -- which the series
    # answers. `decision-log.md Process: #69`.
    #
    # !! THE TWO TIERS DISAGREED, AND FOUR OF SIX SHAPES COULD NOT BE WRITTEN.
    # `paragraphs_lexical` cut at the comment opener and `paragraphs_stdlib` kept the
    # whole physical line, so the retired `paragraph_matches` refused a FRESH census on
    # every lexical trailing comment (`'// note'` against `int b = 2; // note`)
    # and on every paragraph comment not at column 0 (`'/* why */'` against
    # `'    /* why */'` -- the indentation was the cut). Measured 2026-08-19.
    #
    # ! It also fed CODE to the annotators. `prose_numbers` reads this, so a
    # Python `TIMEOUT = 30  # the note says nothing` reported the number 30 as a
    # claim the prose makes. The lexical tier's own comment says that defect was
    # fixed; it was fixed on one tier.
    raw_lines: list[str] = field(default_factory=list)

    @property
    def raw_text(self) -> str:
        """This paragraph's own characters, as ONE string.

        !! THE PROSE LEAVES AS ONE STRING. Roy: *"LLMs and the token parsers
        read this as a complete and coherent statement. They do not read this as
        the same thing: ['LLMs and the token', 'parsers read this as a', ...]."*
        The four reviewers ARE token parsers and prose is what they judge, so
        fragments make each role reassemble the sentence before it can ask
        whether it is true.

        ! IT IS DERIVED, NOT STORED, and that is what keeps it honest: it is
        `raw_lines` joined, so it cannot drift from the characters the file
        holds. `binder.page._place` writes exactly this as the wire's
        `raw_text`, and `_paragraph` reads it back into `raw_lines`.

        ! NOT `text`. That is the run joined for MATCHING -- what a claim is
        checked against -- and the two differ wherever the lexer trimmed. A
        consumer that means the characters means this one.
        """
        return "\n".join(self.raw_lines)

    # !! THE LINES THIS PARAGRAPH COVERS IN THE FILE AS IT READS NOW. That is
    # the whole definition, and it is NOT always the range that ADDRESSES the
    # paragraph. A prose paragraph is replaced, so the two coincide. An empty
    # INTERVAL covers NOTHING: `start` and `end` are the two lines of CODE that
    # bound it, and it holds none of them, so it reports `(n+1, n)` -- a range
    # whose end precedes its start, which is how "covers nothing" is spelled.
    #
    # !! IT IS NOT WHERE AN EDIT GOES, AND READING IT THAT WAY IS THE DEFECT
    # THIS SYSTEM EXISTS TO REMOVE. Roy, 2026-08-20: *"that is the defect of
    # reading line numbers as the address. They are not. You see edit-lines
    # somewhere and you are assuming that means that is where the edit goes."*
    # The fields were called `edit_start`/`edit_end` until that day, and the
    # name taught the wrong reading -- a session read `(1, 0)` on a `b1` as
    # "inserts at line 1", concluded a shebang would be displaced, and filed a
    # bug against behaviour that was correct.
    #
    # ! WHERE PROSE LANDS IS SETTLED BY THE ADDRESS and the order the galley
    # applies a page's edits in -- `a` before `b` before `c`, so a `b` lands
    # outside the `a` it followed. These numbers say what is there now; the
    # address says which place is being written. ! The galley still derives its
    # splice position from this range, which is what `docs/plans/` A4 changes.
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
    # !! A CLOSED LIST OF LINES, OR None. `[1..7]` -- not `(1..7)` or `[1..7)`
    # -- or None, meaning no line currently holds that place. Both ends are
    # INCLUSIVE and both are real lines of the file.
    #
    # ! SO THERE IS NO EMPTY-SLICE SENTINEL. `(n, n - 1)` used to say "holds
    # nothing", which reads as a range, invites arithmetic, and was read once
    # this day as an insertion point. `None` cannot be mistaken for a position.
    #
    # ! Left None by a producer, they mirror `start`/`end` -- see
    # `__post_init__`. That is what makes this safe to add without visiting
    # every construction site.
    original_start: int | None = None
    original_end: int | None = None
    # !! WHERE THE `c` PLACE BEGINS ON `original_start`, 1-based like every other
    # position this census states -- `start`, `end`, `original_start`, `original_end`.
    # Two values:
    #
    #    0      the paragraph owns its lines WHOLE. Not a column: 0 is not one, and
    #           that is what makes it a sentinel rather than an accident. Every
    #           `comment`, `docstring` and `interval`.
    #    1..N   ONE PAST THE LAST CHARACTER OF CODE on that line, which is where
    #           the room beside the code starts. A `trailing-comment`, a
    #           `margin`, a paragraph comment opened after a statement. It is what
    #           lets the galley write one without deleting the code: the splice
    #           keeps `line[: column - 1]`.
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
    # line, and the test cannot work: `paragraphs_stdlib` stores the WHOLE line for
    # a trailing comment, so the suffix test answers False. Measured 2026-08-18:
    # censusing `z = 3  # trailing` and editing that paragraph produced a galley
    # reading `# reworded trailing` where the statement had been -- a deleted
    # statement, in the one artefact a human is asked to approve.
    #
    # ! IT REPLACED A BOOLEAN, `whole_lines`, which answered only WHETHER code
    # came first. That was enough to REFUSE the write and not enough to make it,
    # and the `c` series exists to be written. Roy, 2026-08-19: *"c needs to be
    # writeable. It is the reason c is not an extension of b."*

    def __post_init__(self) -> None:
        """Default the covered lines to the addressing range, or to None.

        ! A producer that states neither gets the addressing range when that
        names real lines, and None when it does not -- `start`/`end` of 0 mean
        this paragraph occupies nothing, and None is how that is spelled here.
        """
        if self.original_start is None and self.original_end is None:
            if self.start >= 1 and self.end >= self.start:
                self.original_start, self.original_end = self.start, self.end
