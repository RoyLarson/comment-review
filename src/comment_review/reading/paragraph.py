"""What a PARAGRAPH is: one unit of prose, or the empty place where prose could go.

!! IT DEFINES WHAT A READER PRODUCES. A reader builds a `Paragraph` the moment
it finds prose, and it knows only what the TEXT says -- where the prose starts
and ends, what kind it is, the code beside it. Where that paragraph SITS is the
page's: the path it is on, the place it occupies, and the empty places where
prose could go and does not.

!! WHY NOT WITH `Page`, WHICH IS THE OBVIOUS HOME. `binder` imports `reading` in
three modules, so `reading.lexer` -- which BUILDS paragraphs -- would have to
import `binder` back. That edge is the cycle, and it is not about a paragraph:
it is where the page's own dependencies already point. A page adds its leadings
and a few load-bearing attributes to its paragraphs, so `Page` stays where it is
and this sits beneath both.

! BENEATH EVERY MODULE THAT MAKES OR READS ONE. At import it takes only
`series`, so every module that makes one and every module that reads one take
it from the same declaration instead of from each other; `text` calls
`lexer.comment_form` when it is first read.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from comment_review.reading.series import Series

MARKERS = ("TODO", "FIXME", "HACK", "XXX", "BUG")
WORK_MARKER = re.compile(r"^(" + "|".join(MARKERS) + r")\b")
# ! Every punctuation a language opens a comment with, stripped before the
# marker is matched.
LEAD_PUNCT = re.compile(r"^[\s#/*\-!=;%<>]+")


def counted_lines(raw: list[str]) -> int:
    """Lines a cap charges for: a marker LINE itself is free.

    A marker points at filed work; the explanation is the rest of the paragraph, and
    the cap measures the explanation. Charge the marker and the quickest route to
    green is deleting the pointer -- which is quick to do and expensive to have
    done: the work is still needed, and nothing names it any more.

    The exemption is one line wide. A run stays one run across a marker, and a
    marker's continuation lines are charged: six lines plus a `TODO:` is six.
    """
    # ! A BLANK LINE IS FREE TOO. It sits inside the paragraph by the interval
    # definition -- only code bounds a paragraph -- and is leading, not prose.
    return sum(
        1 for ln in raw if ln.strip() and not WORK_MARKER.match(LEAD_PUNCT.sub("", ln))
    )


@dataclass
class Paragraph:
    """One unit of prose on a page, or the empty place where prose could go.

    ! An interval holding no prose is a paragraph too, `kind="interval"`. It is
    one of the empty places an `add` can cite, with `undocumented`, `margin` and
    `dark-matter`: the finding is that a constraint exists in code and NOWHERE
    in prose, so it is about an empty place.
    """

    path: str
    start: int
    end: int
    kind: str  # a `series.Kind` value
    # !! WHAT THIS PARAGRAPH IS ATTACHED TO, and it is ONE-TO-MANY THE OTHER WAY:
    # an anchor has MANY addresses -- its own `a`, the `b` above it, the `c`
    # beside it, every `b` and `c` in its body -- and an address has ONE anchor.
    #
    # !! IT IS ALWAYS CODE, VERBATIM -- a line of code, or every line of a unit,
    # never a name and never a symbol. An `a` carries what DECLARES it,
    # `def f():` and not `f`; see `_anchor_of`.
    anchor: str = ""
    # !! THE LINE THIS PLACE'S ANCHOR OPENS ON, so an anchor's OTHER places can
    # be found: the `c` beside its `def`, the `b` above it, its own `a`. Without
    # it a consumer has to infer the line from the prose's position, which is
    # exactly the inference that breaks on the next language -- Rust's doc sits
    # BEFORE its `fn` and Python's after.
    #
    # !! IT WAS `declared_at` AND FILLED FOR `a` ALONE, which is why
    # `for_anchor` could only fall back to it with a declaration in hand. The
    # fact was never about declaring: it is the anchor's line, and every series
    # has one. Renamed and filled for all of them 2026-08-20.
    #
    # !! `None` WHERE THE ANCHOR IS A SENTINEL -- `<module>` at the head of the
    # walk, `<eof>` at its foot. Neither sits on a line, and this says so rather
    # than answering 0.
    #
    # ! IT WAS 0 FOR BOTH until 2026-08-22, and the two were not the same fact.
    # Line 0 is genuinely above line 1, so the head sorted first and rendered at
    # the top and both were correct; the foot inherited those behaviours and
    # both were wrong. Roy: *"the end of file getting a 0 is non-functional
    # filling in for a missing value."*
    anchor_line: int | None = None
    # !! THE ORDINAL OF THAT ANCHOR AMONG THE LINES OF CODE, and
    # `flows.proof_setter` checks it, with `anchor` and `anchor_line`, against the
    # page's cues. This tool edits prose and every prose edit moves the lines
    # below it; the Nth line of code stays the Nth line of code.
    #
    # ! CARRIED ALONGSIDE `anchor`, never instead of it. An ordinal cannot see a
    # rename in place and the text cannot cheaply see an insertion; the pair
    # sees both, which is the whole drift question in two fields.
    anchor_num: int = 0
    # !! WHICH PLACE THIS IS, as against where it sits -- see `addresser.address_for`.
    # Stamped in the path-normalising loop, the only place holding the file
    # text, the finished paragraph list and the repo-relative path at once.
    address: str = ""
    # !! A LABEL, NOT AN ADDRESS, and only LEADING carries one. `d0` marks a run
    # of blank lines in `scripts/render_page.py`'s margin, so a reader can see
    # that every line on the page belongs to something.
    #
    # !! IT IS NOT AN `address` BECAUSE LEADING IS NOT A PLACE, and putting it in
    # that field is what made `d` fail the substitution the other four series
    # satisfy. MEASURED: `a0` and every `f` answer `<module>` and every `b` and
    # `c` answer a line of code; a `d` answered `""`, which is the absence of an
    # answer rather than a different one.
    #
    # ! WHICH FOLLOWS FROM WHERE IT COMES FROM. Every other place exists because
    # the WALK reached a trigger -- and the trigger IS the anchor. A `d` exists
    # because the LEXER found blank lines, so there was never a trigger for it to
    # be anchored to. `addresser.SERIES` holds four series; `LEAD` is a symbol.
    symbol: str = ""
    annotations: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)

    # !! THE PARAGRAPH'S OWN CHARACTERS, EXACTLY AS THE FILE HOLDS THEM -- its
    # lines whole where it owns them, and from the end of the code onward on
    # the first line where code comes first. A `c`'s `anchor` holds that code,
    # so the two RECONSTRUCT the line: `anchor + raw_lines[0]` is what is on disk.
    #
    # !! SO THE CUT IS RECORDED IN THE LINES THEMSELVES, NOT IN A FIELD.
    # Whether a paragraph sits beside code is what its series answers.
    raw_lines: list[str] = field(default_factory=list)

    @property
    def raw_text(self) -> str:
        """This paragraph's own characters, as ONE string.

        !! THE PROSE LEAVES AS ONE STRING. The four reviewers ARE token parsers
        and prose is what they judge, so fragments make each role reassemble the
        sentence before it can ask whether it is true.

        ! IT IS DERIVED, NOT STORED, and that is what keeps it honest: it is
        `raw_lines` joined, so it cannot drift from the characters the file
        holds. `binder.page._place` writes exactly this as the wire's
        `raw_text`, and `_paragraph` reads it back into `raw_lines`.

        ! NOT `text`. That is the run joined for MATCHING -- what a claim is
        checked against -- and the two differ by every marker and line break
        `comment_form` takes out. A consumer that means the characters means
        this one.
        """
        return "\n".join(self.raw_lines)

    @property
    def text(self) -> str:
        """The prose JOINED, so a wrapped claim matches as one string.

        Derived by `lexer.comment_form` -- the one derivation of a paragraph's
        prose -- from `raw_lines`, the cue's series, `anchor` and the path's
        language, the first time it is asked for, and again only when one of
        those has changed. "" where the paragraph holds no prose.
        """
        cue = self.address.rsplit("@", 1)[-1]
        key = (self.path, cue, self.anchor, tuple(self.raw_lines))
        if self._text is not None and self._text[0] == key:
            return self._text[1]
        text = ""
        if self.raw_text.strip():
            # Imported here: `lexer` builds paragraphs, so it imports this module.
            from comment_review.reading.lexer import comment_form

            text = comment_form(
                Path(self.path), Series.of(cue), self.raw_text, self.anchor
            ).text
        self._text = (key, text)
        return text

    @property
    def lines(self) -> int:
        """The lines a stage's cap charges this paragraph for -- `counted_lines`.

        Derived from `raw_lines`, so every reader and a binder read back count
        one way. An empty place holds no prose line and counts 0.
        """
        return counted_lines(self.raw_lines)

    # !! THE LINES THIS PARAGRAPH COVERS IN THE FILE AS IT READS NOW. That is
    # the whole definition, and it is NOT always the range that ADDRESSES the
    # paragraph. A prose paragraph is replaced, so the two coincide. An empty
    # INTERVAL covers NOTHING: it holds no line, so `start` and `end` are 0 and
    # these two are None.
    #
    # !! IT IS NOT WHERE AN EDIT GOES, AND READING IT THAT WAY IS THE DEFECT
    # THIS SYSTEM EXISTS TO REMOVE.
    #
    # ! WHERE PROSE LANDS IS SETTLED BY THE ADDRESS and the reading order
    # `compositor.set_page` walks. These numbers say what is there now; the
    # address says which place is being written, and the galley places a
    # replacement by cue alone.
    #
    # !! A CLOSED LIST OF LINES, OR None. `[1..7]` -- not `(1..7)` or `[1..7)`
    # -- or None, meaning no line currently holds that place. Both ends are
    # INCLUSIVE and both are real lines of the file.
    #
    # ! SO THERE IS NO EMPTY-SLICE SENTINEL. `(n, n - 1)` reads as a range and
    # invites arithmetic; `None` cannot be mistaken for a position.
    #
    # ! Left None by a producer, they mirror `start`/`end` where those name
    # real lines -- see `__post_init__`. That is what makes this safe to add
    # without visiting every construction site.
    original_start: int | None = None
    original_end: int | None = None
    # `text` as last derived, with the inputs it was derived from.
    _text: tuple[tuple[str, str, str, tuple[str, ...]], str] | None = field(
        default=None, init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        """Default the covered lines to the addressing range, or to None.

        ! A producer that states neither gets the addressing range when that
        names real lines, and None when it does not -- `start`/`end` of 0 mean
        this paragraph occupies nothing, and None is how that is spelled here.
        """
        if self.original_start is None and self.original_end is None:
            if self.start >= 1 and self.end >= self.start:
                self.original_start, self.original_end = self.start, self.end
