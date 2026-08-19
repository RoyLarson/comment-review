"""Stage 2, COLLATE: every interval between two lines of code, numbered in order.

    python census.py [--repo D] [--census-only] [--json] [--out PATH] <paths>

The reviewers are handed this list, so it bounds everything they may rule on.
! Most of it is `interval` blocks, which hold no prose: they are ADDRESSABLE, so
an `add` can cite the gap its missing sentence belongs in, and nobody owes them a
record. Coverage is over the blocks that HOLD prose.

**Every file handed in is censused, or this errors** -- a file it could not read
or parse, or whose suffix has no language record, is named and the run exits
nonzero, because a block missing from the census is a block nobody reviews.

Read-only. It calls `annotate.py` on each block for stage 3, and `repo.py` for
the facts about the checkout that both need.

A block is built at the TIER available for its file's language. Both tiers find
the same blocks, and the tier says what else the file can answer:

  tokenized  a lexer + AST (Python, from the stdlib)   + DOCSTRING anchors
  lexical    a comment-syntax record                   blocks

! Only a STRUCTURAL doc carries an anchor, and only Python has one: the doc is a
string inside a declaration's body, so the AST names the declaration. A MARKED
doc (`///`, `/**`) is a comment run like any other. Every other anchor comes from
a reviewer READING the file, so a placement finding is a CANDIDATE in every
language.

! Tier counts are AGGREGATED over the run. A polyglot run reports one total per
tier, so read the per-file tier stamp to see which file reached which.
`--languages` lists the languages known and the tier each reaches.
"""

import argparse
import ast
import io
import json
import re
import sys
import tokenize
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from itertools import pairwise
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from annotate import (  # noqa: E402  -- path shim must run first
    SYMBOLISH,
    annotate,
    prose_numbers,
)
from repo import (  # noqa: E402  -- path shim must run first
    EXCLUDED_DIRS,
    PARSE_ERRORS,
    READ_ERRORS,
    path_index,
    tracked_paths,
)

# Tuples, so `DOC_ANCHORS` is built by concatenation and both go straight to
# `isinstance`.
NAMED_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
DOC_ANCHORS = (ast.Module,) + NAMED_DEFS


# !! A sentinel that CANNOT be a line number. `0` is one less than line 1, so
# `block.start == trailing_end[0] + 1` was true for every comment opening a
# file -- stamping `continues-a-trailing-comment` with no trailing comment
# anywhere, on 3 files in this repo's own tree. SKILL.md tells reviewers a
# mid-clause ending on a stamped block "is not a `correct`", so the false stamp
# SUPPRESSED real findings on file headers.
_NO_TRAILING = -2

# The work markers `counted_lines` leaves free of the cap.
MARKERS = ("TODO", "FIXME", "HACK", "XXX", "BUG")
WORK_MARKER = re.compile(r"^(" + "|".join(MARKERS) + r")\b")
# ! Every punctuation a language opens a comment with, stripped before the
# marker is matched. Anchored on `#`, the exemption was Python-only: a
# `// TODO:` was charged to the cap in a script that censuses eleven languages.
LEAD_PUNCT = re.compile(r"^[\s#/*\-!=;%<>]+")


def counted_lines(raw: list[str]) -> int:
    """Lines a cap charges for: a marker LINE itself is free.

    A marker points at filed work; the explanation is the rest of the block, and
    the cap measures the explanation. Charge the marker and the quickest route to
    green is deleting the pointer -- which is quick to do and expensive to have
    done: the work is still needed, and nothing names it any more.

    The exemption is one line wide. A run stays one run across a marker, and a
    marker's continuation lines are charged: six lines plus a `TODO:` is six.
    """
    # ! A BLANK LINE IS FREE TOO. It sits inside the block by the interval
    # definition -- only code bounds a block -- and SKILL.md says so directly:
    # "The blank is inside the block and is charged nothing." It reaches here
    # now that a blank no longer ends a lexical run.
    return sum(
        1 for ln in raw if ln.strip() and not WORK_MARKER.match(LEAD_PUNCT.sub("", ln))
    )


# -- Annotations ---------------------------------------------------------------
# Each is located here and RESOLVED in `annotate.py`. Locating is most of the
# work; the resolution is what stops a reviewer treating a citation as a
# verified claim. ! These are ANNOTATIONS, never marks -- a MARK is editorial,
# and stage 4 emits those.


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
    kind: str  # "comment" | "docstring" | "trailing-comment" | "interval"
    lines: int
    text: str  # the run JOINED, so a wrapped claim matches as one string
    anchor: str = ""  # the declaration it annotates, when structurally known
    tier: str = "lexical"  # which question set this file's census can answer
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
    # !! DOES THIS BLOCK OCCUPY ITS LINES, or does code share the first one?
    # False for a trailing comment, for a PEP 727 `Doc()` literal, and for a
    # block comment opened after a statement. Every one of those is prose
    # beginning partway through a line of code.
    #
    # !! IT IS STATED BY THE PRODUCER BECAUSE NO READER CAN INFER IT. Two tried
    # -- `code_lines` and `galley.shares_a_line_with_code` -- both by testing
    # whether the stored text is a proper SUFFIX of the physical line, and the
    # test cannot work: `blocks_stdlib` stores the WHOLE line for a trailing
    # comment, so the suffix test answers False and the galley spliced over the
    # code. Measured 2026-08-18: censusing `z = 3  # trailing` and editing that
    # block produced a galley reading `# reworded trailing` where the statement
    # had been -- a deleted statement, in the one artefact a human is asked to
    # approve. A `Doc()` fails the same test for the opposite reason: its
    # stored text is the AST value and is not a suffix of anything.
    whole_lines: bool = True

    def __post_init__(self) -> None:
        """Default the edit range to the addressing range."""
        if not self.edit_start and not self.edit_end:
            self.edit_start, self.edit_end = self.start, self.end


def _join(lines: list[str], markers: tuple[str, ...] = ("#",)) -> str:
    """A comment run as ONE normalised string, its comment markers stripped.

    Prose wraps, so every claim-bearing phrase in a real file straddles a line
    break. Matching line-by-line reports the fragment instead of the claim: a
    count reads as absent and `used to say` degrades to a bare `used to`.

    Args:
        lines: the run's raw source lines.
        markers: the language's comment openers, longest first at the call site
            so `///` is stripped before `//` leaves a stray slash in the prose.
    """
    out = []
    for ln in lines:
        s = ln.strip()
        for m in markers:
            if s.startswith(m):
                s = s[len(m) :].strip()
                break
        out.append(s)
    return re.sub(r"\s+", " ", " ".join(out)).strip()


# A docstring's delimiters, and the prefixes that may sit in front of them.
# ! Longest first: `"""` must be tried before `"`, or one quote comes off a
# triple and two are left in the prose.
_QUOTES = ('"""', "'''", '"', "'")
_PREFIXES = ("rb", "br", "r", "b", "f", "u")


def docstring_text(lines: list[str]) -> str:
    """A docstring as ONE normalised string, read from the FILE's lines.

    !! The census never takes this path: it reads a docstring's VALUE from the
    AST, which arrives with no delimiters. Anyone comparing against that value
    starts from the file instead -- delimiters, prefix and all -- and this is
    what makes the two comparable. Measured 2026-08-17: without it a perfect
    transcription kept its CLOSING delimiter, so a block ending `did it` ran
    together with the quotes into one token and was refused against a census
    holding the same sentence.

    Args:
        lines: the block's source lines, as the file reads them.
    """
    text = "\n".join(lines).strip()
    for prefix in _PREFIXES:
        if text[: len(prefix)].lower() == prefix and text[len(prefix) :].startswith(
            _QUOTES
        ):
            text = text[len(prefix) :]
            break
    for quote in _QUOTES:
        if text.startswith(quote):
            text = text[len(quote) :]
            if text.endswith(quote):
                text = text[: -len(quote)]
            break
    return re.sub(r"\s+", " ", text).strip()


def _from_marker(line: str, markers: tuple[str, ...]) -> str:
    """A trailing comment's line, cut back to where its comment starts.

    ! The census stores a trailing comment's PROSE from the comment token and
    its WIDTH from the physical line, so the text a reviewer transcribes -- the
    line as the file reads it -- carries code the census never had. Cutting at
    the marker is what makes the two comparable.

    ! This finds the marker by SEARCH where the census used a lexer, so a
    marker inside a string literal cuts in the wrong place. That is a wrong
    answer on a line the census read correctly; it replaces a guaranteed
    mismatch on every trailing comment.
    """
    at = [i for m in markers if (i := line.find(m)) != -1]
    return line[min(at) :] if at else line


def block_text(
    kind: str,
    lines: list[str],
    markers: tuple[str, ...] = ("#",),
    structural: bool = True,
) -> str:
    """A block's prose as the census stores it, from the file's LINES.

    !! The lines-to-block half of the block protocol, and the ONLY one. It is
    here rather than in a caller because the census defines what a block's text
    IS; a second implementation elsewhere is a second definition, and the two
    drift. Measured 2026-08-17: `verdicts.py` grew its own and disagreed with
    this file three ways at once -- a blank line, a raw-string prefix and a
    closing delimiter -- refusing 83 of 171 blocks in one run, ~450 in another.

    ! The inverse, block-to-lines, is stage 7b's and does not exist yet: WRITE
    is prose instructing an agent. When it is built it belongs beside this.

    Args:
        kind: the block's `kind`, as the census records it.
        lines: the block's source lines, as the file reads them.
        markers: the language's comment openers, longest first. ! The
            language's LINE comments only, because that is what the census
            passed -- a set that also stripped `/**` would produce prose the
            census never stored.
        structural: whether this language's doc is a STRING IN A DECLARATION'S
            BODY (Python) rather than a marked comment run (`///`, `/**`).
            `Language.doc_is_structural` records it, and it is the whole
            dispatch: `kind` alone says `docstring` for both.
    """
    # !! Routed on STRUCTURAL, never on `kind` alone. The lexical tier stamps
    # `docstring` on any run opening with a language's doc marker -- `///`,
    # `//!`, `/**` -- and those are comments, not string literals. Reading them
    # as literals leaves the marker in the prose and refuses every doc comment
    # in ten of the eleven languages. Only Python's docstring is a string in a
    # declaration's body, which is what `doc_is_structural` records.
    if kind == "docstring" and structural:
        return docstring_text(lines)
    if kind == "trailing-comment":
        lines = [_from_marker(ln, markers) for ln in lines]
    return _join(lines, markers)


@dataclass(frozen=True)
class Language:
    """What the LEXICAL tier needs to find prose in a language it only lexes.

    Adding a language is this record -- data, no code.

    Attributes:
        doc_line: line-comment openers that mean DOC rather than ordinary
            comment (Rust `///`, `//!`). Empty when the language marks docs
            some other way.
        doc_block: block openers that mean DOC (`/**`). Same idea.
        doc_is_structural: the doc is a string in a declaration's body (Python)
            or the run above a declaration (Go). Both need structure to decide,
            so this tier reports `comment` and annotates the block.
        quotes: string delimiters, so a marker inside a literal is skipped.
        spanning_quotes: delimiters whose literal may cross LINES -- a JS
            template literal, a Java text block. ! `_strip_strings` is per-line
            and carries no open-quote state, so a comment marker INSIDE one of
            these reads as a comment; `prove_unchanged` refuses such a file
            rather than proving it. Empty where a language has none.
    """

    name: str
    extensions: tuple[str, ...]
    line_comment: tuple[str, ...]
    block_comment: tuple[tuple[str, str], ...] = ()
    doc_line: tuple[str, ...] = ()
    doc_block: tuple[str, ...] = ()
    doc_is_structural: bool = False
    quotes: tuple[str, ...] = ('"', "'")
    spanning_quotes: tuple[str, ...] = ()


# ! Ordering inside a field is significant: openers are matched longest-first,
# so `///` must precede `//` or every Rust doc line loses one slash into the
# prose and the annotations then run over corrupted text.
LANGUAGES: tuple[Language, ...] = (
    Language(
        "python",
        (".py", ".pyi"),
        ("#",),
        doc_is_structural=True,
        # !! A triple quote spans lines, and Python reaches the LEXICAL
        # path whenever `ast.parse` fails -- syntax newer than the floor,
        # a file mid-edit. Declaring nothing here left the same fail-open
        # that was closed for JS the same day: two files differing only
        # in a `#` line INSIDE a triple-quoted literal fingerprinted
        # identically and the proof reported PROVEN.
        spanning_quotes=('"""', "'''"),
    ),
    Language(
        "rust",
        (".rs",),
        ("///", "//!", "//"),
        (("/*", "*/"),),
        doc_line=("///", "//!"),
    ),
    Language("go", (".go",), ("//",), (("/*", "*/"),), doc_is_structural=True),
    Language(
        "c-family",
        (".c", ".h", ".cpp", ".hpp", ".cc", ".java", ".cs", ".swift", ".kt"),
        ("//",),
        (("/*", "*/"),),
        doc_block=("/**",),
        # ! A Java TEXT BLOCK spans lines the same way, and a `//` inside one is
        # not a comment.
        spanning_quotes=('"""',),
    ),
    Language(
        "js-family",
        (".js", ".jsx", ".ts", ".tsx", ".mjs"),
        ("//",),
        (("/*", "*/"),),
        doc_block=("/**",),
        quotes=('"', "'", "`"),
        spanning_quotes=("`",),
    ),
    Language("ruby", (".rb",), ("#",), (("=begin", "=end"),), doc_is_structural=True),
    Language("shell", (".sh", ".bash", ".zsh"), ("#",)),
    Language("sql", (".sql",), ("--",), (("/*", "*/"),)),
    Language("lua", (".lua",), ("--",), (("--[[", "]]"),)),
    Language("toml-ini", (".toml", ".ini", ".cfg"), ("#",)),
    Language("yaml", (".yaml", ".yml"), ("#",)),
)

BY_EXT = {ext: lang for lang in LANGUAGES for ext in lang.extensions}

# The ladder is named by the QUESTION each rung answers, not by the library
# that happens to answer it. Only the top rung knows which declaration a block
# belongs to.
TIER_ANSWERS = {
    "tokenized": "blocks, annotations, and DOCSTRING anchors",
    "lexical": "blocks and annotations only",
}


def language_for(path: Path) -> Language | None:
    """The language record for a path, or None when the suffix is unknown."""
    return BY_EXT.get(path.suffix.lower())


def _strip_strings(line: str, quotes: tuple[str, ...]) -> str:
    """Blank out string literals so a marker inside one stays out of the census.

    `url = "http://x"` holds `//` in most C-family languages. It handles
    single-line literals with backslash escapes; raw strings, heredocs and
    template nesting are where this tier stops and the lexer starts.
    """
    out, quote, esc = [], "", False
    for ch in line:
        if esc:
            out.append(" " if quote else ch)
            esc = False
            continue
        if ch == "\\":
            esc = True
            out.append(" " if quote else ch)
            continue
        if quote:
            out.append(" ")
            if ch == quote:
                quote = ""
            continue
        if ch in quotes:
            quote = ch
            out.append(" ")
            continue
        out.append(ch)
    return "".join(out)


def blocks_lexical(path: Path, text: str, lang: Language) -> list[Block]:
    """Comment runs for a language with no parser here -- the FLOOR tier.

    Answers where every block is, its line range, its text and its annotations.
    Every block comes back stamped `tier="lexical"` with an empty anchor.

    ! A block opener with no closer swallows every remaining line into one run,
    so code below it is censused as prose. That block is STAMPED
    `unterminated-block-comment`, which is how a consumer tells it from a long
    comment; `prove_unchanged.py` refuses the whole file on that annotation.
    """
    openers = tuple(sorted(lang.line_comment, key=len, reverse=True))
    lines = text.splitlines()
    out: list[Block] = []
    run: list[tuple[int, str]] = []
    # ! Blank lines seen since the last comment line. They join the run only if
    # another comment follows; otherwise they are dropped, so a run ends on its
    # last comment line.
    pending: list[tuple[int, str]] = []
    in_block: tuple[str, str] | None = None
    # ! The line the last trailing comment ended on. Measured: this tier splits a
    # wrapped trailing comment exactly as `blocks_stdlib` does, so it needs the
    # same stamp. A list because `flush` is a closure and rebinds nothing.
    trailing_end = [_NO_TRAILING]

    # !! DOES CODE SHARE THE RUN'S FIRST LINE -- on EITHER side? `/* note */ x
    # = 1` has it after the closer and `x = 1; /* note` has it before the
    # opener, and both mean the same thing: a splice over that line deletes a
    # statement. Deriving it from the CUT alone answered only the second, and
    # the first was censused as prose holding `int b = 2;` with the galley
    # willing to write over it. Measured 2026-08-18.
    #
    # ! `trailing` does not answer it either: a MULTI-LINE block comment opened
    # after a statement cuts the same way and flushes with `trailing=False`,
    # because by then the run spans several lines. A list because `flush` is a
    # closure and rebinds nothing.
    partial_first = [False]

    def flush(trailing: bool = False) -> None:
        pending.clear()
        if not run:
            partial_first[0] = False
            return
        raw = [t for _, t in run]
        stripped = raw[0].strip()
        is_doc = stripped.startswith(lang.doc_line) if lang.doc_line else False
        if lang.doc_block and stripped.startswith(lang.doc_block):
            is_doc = True
        if is_doc:
            kind = "docstring"
        else:
            kind = "trailing-comment" if trailing else "comment"
        block = Block(
            path=path.as_posix(),
            start=run[0][0],
            end=run[-1][0],
            kind=kind,
            lines=counted_lines(raw),
            text=_join(raw, openers),
            raw_lines=raw,
            tier="lexical",
            whole_lines=not partial_first[0],
        )
        partial_first[0] = False
        # !! Same split as the tokenized tier: a trailing comment closes its run,
        # so a sentence wrapped onto the next line becomes a SECOND block anchored
        # to the code below it. Stamped, not re-cut.
        if kind == "comment" and block.start == trailing_end[0] + 1:
            block.annotations.add("continues-a-trailing-comment")
            block.notes.append(
                "opens on the line after a trailing comment, so it may be the"
                " tail of that sentence rather than a note about the code"
                " below. A mid-clause ending here may be the split."
            )
        if kind == "trailing-comment":
            trailing_end[0] = block.end
        out.append(block)
        run.clear()

    for n, raw_line in enumerate(lines, 1):
        if in_block is not None:
            run.append((n, raw_line.rstrip()))
            if in_block[1] in raw_line:
                in_block = None
                flush()
            continue
        # !! ONLY CODE ENDS A BLOCK -- a blank line does not, and this reached
        # `flush()` because `"".startswith(openers)` is False. SKILL.md names
        # the consequence exactly: "Split on blanks and a 9-line block reads as
        # `6 + 3` and passes a cap of 6 -- the quickest way to fake compliance."
        # Measured 2026-08-17: a six-line run with one blank censused as 3L + 3L
        # in every LEXICAL language, while `blocks_stdlib` skips NL tokens and
        # kept it whole. Ten of the eleven languages could evade any cap.
        #
        # ! The blank JOINS the run rather than being skipped, so `raw_lines`
        # stays index-aligned with `start..end` -- `prove_unchanged` walks the
        # two together and a gap there makes the file unprovable.
        #
        # !! A blank line INSIDE a run joins it; a blank line AFTER one does
        # NOT extend it. They are held here and committed only when another
        # comment line arrives. A run's `end` must stay on its last comment
        # line, because `doc-kind-unresolved` asks whether the very next line
        # is a declaration -- extend the block over the gap and an ORPHAN run,
        # held off its declaration by exactly that gap, reads as documenting it.
        if not raw_line.strip():
            if run:
                pending.append((n, ""))
            continue
        code = _strip_strings(raw_line, lang.quotes)
        line_at = min((code.index(o) for o in openers if o in code), default=-1)
        opened = next((p for p in lang.block_comment if p[0] in code), None)
        # !! WHICHEVER OPENER COMES FIRST on the line owns it. The block test
        # ran first unconditionally, so `// see /* the note` opened a block run
        # that swallowed every line up to the next `*/` -- executable code
        # handed to four reviewers as prose, carrying no annotation to say so,
        # and dropped from `code_lines`, which put every interval in that file
        # at the wrong boundary. Measured on a five-line C file: one block
        # spanning lines 2-4 whose text held `int b = 2;`.
        if opened is not None and -1 < line_at < code.index(opened[0]):
            opened = None
        if opened is not None:
            flush()
            # !! CUT AT THE OPENER, like the line-comment path below does. The
            # whole raw line was appended, so `int b = 2; /* note */` was
            # censused as one `comment` block whose TEXT held the statement --
            # executable code handed to four reviewers as prose, run through the
            # annotation regexes, and dropped from `code_lines`, which moved
            # every interval boundary in the file. Measured 2026-08-17, the same
            # shape as the `//`-before-`/*` case fixed directly above.
            opens_at = code.index(opened[0])
            tail = code[opens_at + len(opened[0]) :]
            closes_here = opened[1] in tail
            # !! CUT AT THE OPENER ONLY WHEN THE COMMENT RUNS TO END OF LINE.
            # `int b = 2; /* note */` cuts, and the statement stays code. But
            # `int x = /* why */ 5;` has code AFTER the closer, and cutting
            # there loses the `5;` -- so `5` and `7` compare EQUAL and
            # `prove_unchanged` reports PROVEN on a changed literal. Storing the
            # whole line keeps `_delimiter_shares_the_line` able to refuse it,
            # which is the safe answer for a proof. Measured 2026-08-17: the cut
            # was written without this condition and the existing test caught it.
            after = (
                tail[tail.index(opened[1]) + len(opened[1]) :] if closes_here else ""
            )
            # ! The ONE shape that must not cut is code AFTER the closer on this
            # same line. When the run continues to the next line, everything
            # from the opener onward is comment, so a multi-line block opening
            # after a statement cuts too -- without it the block's text read
            # `int b = 2; /* opens ...`, the statement handed over as prose.
            cut = 0 if (closes_here and after.strip()) else opens_at
            # ! Only the run's FIRST line decides it. A continuation line of a
            # block comment is entirely prose whatever surrounds the run.
            #
            # !! BOTH SIDES. Code before the opener, and code after the closer
            # on a comment that closes on this line -- the second is exactly
            # the case `cut` is set to 0 for, so testing `cut` missed it.
            if not run:
                partial_first[0] = bool(code[:opens_at].strip()) or bool(
                    closes_here and after.strip()
                )
            run.append((n, raw_line[cut:].rstrip()))
            if closes_here:
                # ! Code BEFORE the opener makes it a trailing comment, which is
                # what it is: prose about the statement on its own line.
                flush(trailing=bool(cut and code[:opens_at].strip()))
            else:
                in_block = opened
            continue
        if code.strip().startswith(openers):
            run.extend(pending)
            pending.clear()
            run.append((n, raw_line.rstrip()))
            continue
        flush()  # ! CODE ends a block; a blank line does not
        at = line_at
        if at >= 0:
            # ! `flush()` above emptied the run, so this line is the first
            # one and the code before `at` is what makes it trailing. A line
            # comment runs to end of line, so there is no other side to test.
            partial_first[0] = bool(at and code[:at].strip())
            run.append((n, raw_line[at:].rstrip()))
            flush(trailing=True)  # its own block, anchored to the code on that line
    flush()
    if in_block is not None and out:
        # The loop ended with a block comment still open, so the final flush
        # emitted the run that ate the rest of the file. It is the ONE block
        # that may hold code.
        out[-1].annotations.add("unterminated-block-comment")
        out[-1].notes.append(
            f"UNTERMINATED {in_block[0]}: no closing {in_block[1]} before end of "
            "file, so every line below the opener was swallowed into this run. "
            "Code down there was NOT censused as code."
        )
    return out


def flag_structural_docs(blocks: list[Block], text: str, lang: Language) -> None:
    """Mark each run whose KIND is still an open question at this tier.

    Go and Ruby attach documentation by POSITION -- an ordinary line comment
    directly above a declaration IS that declaration's documentation -- so a
    doc reads like any other run, and telling them apart needs the structure
    this tier lacks.

    The block is annotated as an OPEN QUESTION instead. That matters because
    `compact.md` routes on KIND: a `comment` is governed by LENGTH and may be
    cut to the cap, a `docstring` by FORMAT and stands. Unmarked, a three-line
    Go export doc reads as over a cap of two and is cut by a rule that governs
    comments.

    Args:
        blocks: this file's blocks, mutated in place.
        text: the file's source, for looking at what follows each run.
        lang: the language record, which decides whether this pass applies.
    """
    if not lang.doc_is_structural:
        return
    lines = text.splitlines()
    for block in blocks:
        # Only a leading `comment` run can be a positional doc: a trailing
        # comment annotates the code on its own line.
        if block.kind != "comment":
            continue
        # ! The IMMEDIATELY next line. Both languages require a doc comment to
        # touch its declaration, so a run held off by a blank line is an ORPHAN
        # -- left unmarked here, and charged to the cap.
        nxt = lines[block.end].strip() if block.end < len(lines) else ""
        if not nxt:
            continue
        block.annotations.add("doc-kind-unresolved")
        block.notes.append(
            "KIND UNRESOLVED: this run sits above code and "
            f"{lang.name} attaches docs by position, so it may be documentation "
            "governed by FORMAT rather than a comment governed by LENGTH. "
            "NOT counted against the cap. Confirm the kind before compacting."
        )


def blocks_stdlib(path: Path, text: str) -> list[Block]:
    """Comment blocks (bounded by CODE) and docstrings, via tokenize + ast."""
    out: list[Block] = []
    source_lines = text.splitlines()
    # (line, physical source line, the comment token alone, is it trailing)
    run: list[tuple[int, str, str, bool]] = []
    # ! The line the last trailing comment ended on. A comment opening on the
    # VERY NEXT line continues that sentence, and the flush below has already
    # split them. A list because `flush` is a closure and rebinds nothing.
    trailing_end = [_NO_TRAILING]

    def flush() -> None:
        if run:
            # ! PROSE comes from the comment token; WIDTH from the physical
            # line, which is the whole line a width rule measures. Using the
            # physical line for both fed a trailing comment's own code to the
            # annotation regexes -- reviewers saw
            # `models.Index(fields=(...)),  # note` as the note's text.
            prose = [c for _, _, c, _ in run]
            out.append(
                block := Block(
                    path=path.as_posix(),
                    start=run[0][0],
                    end=run[-1][0],
                    kind="trailing-comment" if run[0][3] else "comment",
                    # ! A TRAILING comment is by definition preceded by code on
                    # its line, whatever `raw_lines` happens to hold.
                    whole_lines=not run[0][3],
                    lines=counted_lines(prose),
                    text=_join(prose),
                    # !! THE LINES THE BLOCK SPANS, not the lines that carry a
                    # comment token. A blank line inside a run has no token, so
                    # taking them from `run` skipped it while `start..end`
                    # still spanned it -- `raw_lines` was then SHORTER than the
                    # block, and anything comparing the two disagreed on an
                    # untouched file. Measured 2026-08-18: 4 blocks in this
                    # repo, each refused by `galley.block_matches` as stale,
                    # and each one a splice that would have deleted the blank
                    # line it did not know about.
                    raw_lines=source_lines[run[0][0] - 1 : run[-1][0]],
                )
            )
            # !! A trailing comment CLOSES its run, so a sentence wrapped onto
            # the next line becomes a SECOND block and re-anchors to the
            # declaration below it. That is correct by the block definition --
            # the continuation sits between two lines of code -- and wrong about
            # the prose, which is one sentence. STAMPED rather than re-cut:
            # merging would change block boundaries and renumber every census,
            # and the harm is a reviewer filing `correct` against a mid-clause
            # ending the census manufactured.
            if block.kind == "comment" and block.start == trailing_end[0] + 1:
                block.annotations.add("continues-a-trailing-comment")
                block.notes.append(
                    "opens on the line after a trailing comment, so it may be"
                    " the tail of that sentence rather than a note about the"
                    " code below. A mid-clause ending here may be the split."
                )
            if block.kind == "trailing-comment":
                trailing_end[0] = block.end
            run.clear()

    for raw in tokenize.generate_tokens(io.StringIO(text).readline):
        if raw.type == tokenize.COMMENT:
            trailing = bool(raw.line[: raw.start[1]].strip())
            run.append((raw.start[0], raw.line.rstrip("\n"), raw.string, trailing))
            # ! A trailing comment CLOSES its run. Its code sits before it, so
            # the next token to arrive is the following leading comment, and the
            # two merged across two blank lines -- gluing `raise original
            # DoesNotExist` to an unrelated `TODO` four lines down and handing a
            # reviewer one block built from two comments.
            if trailing:
                flush()
        elif raw.type in (
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.INDENT,
        ) or raw.type in (tokenize.ENDMARKER, tokenize.DEDENT):
            continue
        else:
            flush()
    flush()

    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        out.append(
            Block(
                path=path.as_posix(),
                start=getattr(e, "lineno", 1) or 1,
                end=getattr(e, "lineno", 1) or 1,
                kind="unparsed",
                lines=0,
                text=f"UNPARSED ({e.msg}) -- no docstrings, no names harvested",
            )
        )
        return out

    for node in ast.walk(tree):
        if not isinstance(node, DOC_ANCHORS):
            continue
        doc = ast.get_docstring(node, clean=False)
        if not doc:
            continue
        stmt = node.body[0]
        start = stmt.lineno
        end = getattr(stmt, "end_lineno", stmt.lineno) or stmt.lineno
        # !! `raw_lines` IS THE FILE'S LINES, sliced, and never the AST value.
        # `ast.get_docstring` returns the string CONTENT: no quote delimiters,
        # and no indent on the first line. Stored, it made every consumer that
        # compares a block to the file compare unlike things -- measured
        # 2026-08-17 on `galley.py`'s own census, `block_matches` returned False
        # for all six docstring blocks of an UNMODIFIED file and True for all
        # five comment blocks, so a docstring edit was refused as stale and the
        # galley could not be set for it at all. `text` is the whole source and
        # the node carries 1-based inclusive lines, so the slice is exact.
        raw = source_lines[start - 1 : end]
        out.append(
            Block(
                path=path.as_posix(),
                start=start,
                end=end,
                kind="docstring",
                # ! The PHYSICAL count, which is what `end - start` spans. The
                # AST value is one line short of a multi-line docstring, having
                # no closing-delimiter line, so `lines` and `len(raw_lines)`
                # disagreed by one on every one of them.
                lines=len(raw),
                text=re.sub(r"\s+", " ", doc).strip(),
                anchor=getattr(node, "name", "<module>"),
                raw_lines=raw,
            )
        )
    out.extend(_annotated_docs(path, tree))
    return sorted(out, key=lambda b: b.start)


def _annotated_docs(path: Path, tree: ast.AST) -> list[Block]:
    """Prose carried by a PEP 727 `Doc()` inside an `Annotated[...]`.

    ! These are STRING LITERALS, so `ast.get_docstring` passes over them and so
    does the tokenizer. On a file that documents its parameters this way they
    are most of its prose.
    """
    out: list[Block] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if getattr(fn, "id", getattr(fn, "attr", "")) != "Doc":
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant):
            continue
        val = node.args[0].value
        if not isinstance(val, str):
            continue
        start = node.args[0].lineno
        end = getattr(node.args[0], "end_lineno", start) or start
        out.append(
            Block(
                path=path.as_posix(),
                start=start,
                end=end,
                kind="docstring",
                lines=len(val.splitlines()) or 1,
                text=re.sub(r"\s+", " ", val).strip(),
                raw_lines=val.splitlines() or [val],
                # !! A `Doc()` IS A STRING INSIDE A LINE OF CODE. `raw_lines`
                # stays the AST value here, deliberately: the file's slice
                # would carry the `Annotated[...]` wrapper, which is code, and
                # no consumer wants that as prose. Saying so is what lets a
                # consumer refuse the block for what it is rather than call it
                # stale.
                whole_lines=False,
            )
        )
    return out


def _walk(root: Path):
    """Every file under `root` this script has a language record for.

    ! Filters on `BY_EXT`, so every language `--languages` advertises is walked.
    Hardcoded to `*.py`, the scan went Python-only, and a file the walk skips is
    absent from the NOT CHECKED list too -- the run then reports a full census of
    a fraction of the tree.
    """
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in BY_EXT:
            # !! RELATIVE to the root being walked. Matched against `p.parts`
            # this tested every ANCESTOR too, so a checkout living anywhere
            # under a directory called `venv`, `.venv`, `node_modules`,
            # `site-packages`, `__pycache__` or `.git` excluded ITSELF.
            # Measured 2026-08-17: `code_names` harvested 0 names from a repo
            # under `.../venv/myproject`, and nothing joined `unread`, so the
            # NOT CHECKED list stayed empty and the run read as complete --
            # every `names-a-symbol` a false obituary, handed to four reviewers
            # as settled fact.
            if not EXCLUDED_DIRS.intersection(p.relative_to(root).parts):
                yield p


# The two gaps in the name corpus that are NOT read failures, named so a caller
# can tell them apart from one. Every row `code_names` returns reads alike --
# `<path> (<reason>)` -- and a reporting caller that treated all of them as
# unreadable files told a polyglot repo that six files "could not be read" and
# then instructed the reader to wait for a list that can never empty.
NO_HARVESTER = "no name harvester for"
WALKED_TREE = "name corpus built by WALKING the tree"


def code_names(
    roots: list[Path], tracked: set[Path] | None = None
) -> tuple[set[str], list[str]]:
    """Every name the tree DEFINES, harvested from the AST.

    A corpus built from raw text contains the comments being checked, so every
    obituary resolves against itself and the check always passes. Unreadable
    files are RETURNED alongside the names: a hole in the corpus turns every
    symbol defined only there into a false obituary, which fails loud and wrong.

    ! TRACKED files only, when git can say which. A vendored, generated or
    gitignored tree under the repo root otherwise donates its whole namespace,
    so a symbol the repo defines nowhere resolves ALIVE. That failure is SILENT
    and one-sided: it can hide an obituary, and manufactures none.

    Args:
        roots: directories or files to harvest.
        tracked: absolute paths git reports as tracked, or None when git could
            not answer -- in which case the whole tree is walked and the caller
            is told, so a change in coverage arrives with the result.

    Returns:
        The set of defined names, and the rows naming every gap in it. A row
        holding `NO_HARVESTER` is a KNOWN hole and a row holding `WALKED_TREE`
        is a caveat about the whole corpus; anything else is a file this
        process genuinely could not read or parse. A caller that tells the
        three apart says so with those two constants -- the three read alike as
        prose, and a caller matching on the prose reclassifies them silently
        the next time this wording changes.
    """
    names: set[str] = set()
    unread: list[str] = []
    if tracked is None:
        unread.append(
            f"{WALKED_TREE} (not a git checkout, or git unavailable) -- "
            "untracked or vendored code may mask an obituary"
        )
    for root in roots:
        for p in _walk(root):
            if tracked is not None and p.resolve() not in tracked:
                continue
            lang = language_for(p)
            # ! A non-Python file is a KNOWN hole, reported as one. Parsed as
            # Python it came back `a.go (SyntaxError)`, which reads as "your
            # file is malformed" and sends a reviewer after an invented defect.
            # Liveness in these languages needs its own harvester; this names
            # the gap until there is one.
            if lang is None or lang.name != "python":
                name = lang.name if lang else "unknown"
                unread.append(f"{p.as_posix()} ({NO_HARVESTER} {name})")
                continue
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"))
            except PARSE_ERRORS as e:
                unread.append(f"{p.as_posix()} ({type(e).__name__})")
                continue
            names.add(p.stem)
            harvest_constants = not (p.name.startswith("test_") or "tests" in p.parts)
            for node in ast.walk(tree):
                if isinstance(node, NAMED_DEFS):
                    names.add(node.name)
                elif isinstance(node, ast.Name):
                    names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    names.add(node.attr)
                elif isinstance(node, ast.arg):
                    names.add(node.arg)
                elif isinstance(node, ast.alias):
                    names.add((node.asname or node.name).split(".")[0])
                elif harvest_constants and isinstance(node, ast.Constant):
                    if isinstance(node.value, str) and SYMBOLISH.match(node.value):
                        names.add(node.value)
    return names, unread


def code_lines(text: str, prose: list[Block]) -> set[int]:
    """Which lines of this file are LINES OF CODE, at the tier the census ran.

    A line is code when it holds something that is not blank and not prose. The
    two tiers cannot answer that identically, and the difference is the
    docstring: `tokenized` knows a string literal is a declaration's
    documentation, `lexical` knows only what its comment-syntax record spells.
    So a block's BOUNDS are tier-dependent while its CONTENT is not.

    ! A `trailing-comment` sits ON a code line, so that line stays code. A
    `comment` or `docstring` block occupies its lines entirely, so those lines
    are not. An `interval` occupies nothing, which is what makes this safe to
    run over a census that already holds intervals.
    """
    passes_through = ("trailing-comment", "interval")
    lines = text.splitlines()
    occupied: set[int] = set()
    for b in prose:
        if b.kind in passes_through:
            continue
        occupied.update(range(b.start, b.end + 1))
        # !! A block's FIRST line is NOT occupied when code precedes its opener.
        # !! A BLOCK'S FIRST LINE IS STILL CODE WHEN CODE PRECEDES ITS TEXT.
        # `int b = 2; /* opens` spans from that line, and taking the whole span
        # dropped the statement from the code set, moving every interval
        # boundary below it.
        #
        # !! THE BLOCK SAYS SO. This tested whether the stored text was a
        # proper SUFFIX of the physical line, which is an inference and was
        # wrong in both directions: `blocks_stdlib` stores the WHOLE line for a
        # trailing comment, so the test never fired for one, and a PEP 727
        # `Doc()` stores the AST value, which is a suffix of nothing -- so its
        # declaration line was dropped from the code set and every interval
        # boundary in the file moved. Measured 2026-08-18.
        if not b.whole_lines:
            occupied.discard(b.start)
    return {n for n, ln in enumerate(lines, 1) if ln.strip() and n not in occupied}


def intervals(path: Path, text: str, prose: list[Block]) -> list[Block]:
    """Every gap between two lines of code that holds no prose.

    A gap holding a comment run IS that run's block, so only the empty ones are
    emitted here and the census stays one block per interval either way.

    ! **The file boundary counts as a bound.** There is no code line above a
    module docstring and none below a comment at EOF, so the first and last
    intervals are bounded by the file itself rather than special-cased away. A
    file with no code at all is therefore one interval.

    ! `start` and `end` are the BOUNDING CODE LINES, not the blank lines
    between them, because a zero-width gap has no lines of its own and every
    citation in this system has to resolve. Two adjacent code lines give an
    interval whose range is those two lines.

    !! `edit_start` and `edit_end` are the OTHER range -- the gap itself, which
    is what an edit to this interval occupies. They are set here and nowhere
    else, because the edges walked here carry the file-boundary sentinels that
    `start` and `end` clamp away. See `Block`.
    """
    lines = text.splitlines()
    last = len(lines)
    if last == 0:
        return []
    code = sorted(code_lines(text, prose))
    starts = {b.start for b in prose}
    edges = [0, *code, last + 1]
    out: list[Block] = []
    for prev, nxt in pairwise(edges):
        if any(prev < s < nxt for s in starts):
            continue  # a prose block already IS this interval
        out.append(
            Block(
                path=path.as_posix(),
                # The ADDRESS: clamped, because a citation has to resolve.
                start=max(prev, 1),
                end=min(nxt, last),
                kind="interval",
                lines=0,
                text="",
                # The EDIT: unclamped, so the file boundary keeps its side.
                # `prev + 1 .. nxt - 1` is THE GAP ITSELF -- its own blank
                # lines, not the code lines that bound it. Empty for adjacent
                # code lines, and `1..0` above the first line of a file, which
                # is an empty range and so a pure insertion.
                #
                # ! The gap below the last code line is `last+1..last` only
                # when that line ENDS the file. With trailing blanks it spans
                # them, which is right: they are the gap.
                edit_start=prev + 1,
                edit_end=nxt - 1,
            )
        )
    return out


def tier_for(lang: Language) -> str:
    """The highest rung reachable for this language, here and now.

    One definition, read by the dispatcher and by `--languages`, so the listing
    and the run report the same tier.
    """
    return "tokenized" if lang.name == "python" else "lexical"


def address(block: dict) -> str:
    """`path:start-end` -- how every part of this system NAMES a block.

    !! ONE FORMAT, ONE OWNER. It is the contract between what `record.py
    --seed` writes into a slot and what the stage-5 gate admits, and it was
    written out at four sites that had already drifted: only
    `verdicts.address_problem` normalised a backslash separator, and only it
    accepted the one-line short form. The one measured divergence in this
    format cost 268 refusals in a single run, every one of them a correct
    address.

    ! The READER may be more forgiving than the writer -- `address_problem`
    still accepts `path:start` on a one-line block, because the brief tells a
    reviewer to write `path:start-end` and the census prints the short form.
    That tolerance is a rule about reading, and it stays with the reader.

    Args:
        block: one census entry, as a dict.

    Returns:
        The block's address.
    """
    path = str(block.get("path", "")).replace("\\", "/")
    return f"{path}:{block.get('start')}-{block.get('end')}"


def _repo_relative(path: Path, repo: Path) -> str:
    """`path` as `repo` sees it: posix, relative, no `..`.

    Args:
        path: the file censused.
        repo: the root every citation resolves against.

    Returns:
        The posix path relative to `repo`. ! A file NOT under `repo` keeps the
        path AS IT WAS PASSED, which may itself be relative -- run from a
        subdirectory, `--repo /r ../other/x.py` records `../other/x.py`. There
        is no relative-to-`repo` form of such a file and inventing one with
        `..` would hand a consumer a path that escapes the root it was given,
        so it is passed through unresolved and the consumers refuse it:
        `galley.py` writes nothing that lands outside `--out`.
    """
    try:
        return path.resolve().relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def census_for(path: Path, text: str, lang: Language) -> list[Block]:
    """The census for one file, at the highest tier available for its language.

    The ladder is by QUESTION ANSWERED. Python reaches TOKENIZED through the
    stdlib, which buys docstring anchors; every other language has the LEXICAL
    floor.
    """
    if lang.name == "python":
        got = blocks_stdlib(path, text)
    else:
        got = blocks_lexical(path, text, lang)
        flag_structural_docs(got, text, lang)
    # ! A file the parser refused is NOT enumerated into intervals. Its one
    # `unparsed` block reports the refusal, and the code lines below it were
    # never established, so any interval drawn there would be invented.
    if not any(b.kind == "unparsed" for b in got):
        got = got + intervals(path, text, got)
    for b in got:
        b.tier = tier_for(lang)
    return sorted(got, key=lambda b: (b.start, b.end))


def _not_censused(files: list[Path], unreadable: list[str]) -> str:
    """The refusal, worded ONCE for both output modes.

    !! The reviewers are handed the census, so a file missing from it is blocks
    nobody reviews and nothing downstream notices. `--json` used to return 0
    with a SHORT array on exactly the input the text path refused -- and
    `--json --out` is the route `SKILL.md` mandates for the census stage 5
    parses, so the coverage check then certified every block accounted for over
    blocks that were never collected.
    """
    listed = "\n".join(f"    {u}" for u in unreadable)
    return (
        f"NOT CENSUSED -- these are gaps, not passes:\n{listed}\n"
        f"ERROR: {len(unreadable)} of {len(files)} files handed in were not"
        " censused. Every file is censused or this errors."
    )


def main() -> int:
    """Build the census, resolve its annotations, print both."""
    # UTF-8 with replacement, so an em-dash in someone's docstring still prints
    # on a console whose encoding lacks it.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--repo", default=".", help="repo root for citation resolution")
    ap.add_argument("--census-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--filtered",
        action="store_true",
        help="the reviewer's view: prose blocks, and one line per run of intervals",
    )
    ap.add_argument(
        "--out", metavar="PATH", help="write the report to PATH, not stdout"
    )
    ap.add_argument(
        "--languages",
        action="store_true",
        help="list known languages and the tier each reaches, then exit",
    )
    args = ap.parse_args()

    # ! WRITES ITS OWN FILE. A shell redirect is refused outright by a
    # worktree-isolated harness -- "too complex to verify that it stays inside
    # the worktree" -- and the JSON census is what the stage-5 join parses, so
    # the only documented route to it was unrunnable there.
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="") as fh:
            with redirect_stdout(fh):
                return _report(args)
    return _report(args)


def _report(args: argparse.Namespace) -> int:
    """Everything the run prints, so `--out` can wrap it in one place."""
    if args.languages:
        print(f"{'language':<10} {'tier':<11} extensions")
        for lang in LANGUAGES:
            exts = " ".join(lang.extensions)
            print(f"{lang.name:<10} {tier_for(lang):<11} {exts}")
        print("\nA suffix not listed is named, and the census exits nonzero.")
        return 0

    repo = Path(args.repo).resolve()
    targets = [Path(p) for p in args.paths]
    files = sorted({f for t in targets for f in _walk(t)})
    known, unread = code_names([repo], tracked_paths(repo))
    paths = path_index(repo)

    census: list[Block] = []
    # A path argument that matched no file joins `unreadable`, so a typo errors
    # on the same rule every other gap does.
    unreadable: list[str] = [
        f"{t.as_posix()} (matched no files)" for t in targets if not any(_walk(t))
    ]
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except READ_ERRORS as e:
            unreadable.append(f"{path.as_posix()} ({type(e).__name__})")
            continue
        lang = language_for(path)
        if lang is None:
            unreadable.append(f"{path.as_posix()} (no language record for its suffix)")
            continue
        try:
            got = census_for(path, text, lang)
        except Exception as e:  # a parse failure is REPORTED, as a gap
            unreadable.append(f"{path.as_posix()} ({type(e).__name__}: {e})")
            continue
        # !! EVERY BLOCK'S PATH IS REPO-RELATIVE. It is what `--repo` is for:
        # the census, the file lists and every citation a reviewer writes all
        # resolve against that root, so a block carrying an absolute path is a
        # block no consumer can place. It happened whenever the run was handed
        # absolute file arguments, which is how a task agent that resolved its
        # own paths would call this.
        #
        # !! Measured 2026-08-17: `galley.py` joins `out / block["path"]`, and
        # in Python an absolute right-hand side WINS a join -- so the galley
        # wrote over the source file, put nothing under `--out`, and printed
        # that it had succeeded. The module whose one promise is "nothing under
        # `--repo` is touched" was editing the tree under review.
        #
        # ! A file outside the repo keeps the path AS IT WAS PASSED -- see
        # `_repo_relative`, which says what that means. `galley.py` refuses to
        # write such a block rather than guessing where it belongs.
        # ! HOISTED. `_repo_relative` calls `Path.resolve()`, a filesystem
        # call, and both arguments are the same for every block of a file.
        # Measured 2026-08-18: 120 us a call, so one 793-block file spent
        # 95 ms resolving one path 793 times.
        rel = _repo_relative(path, repo)
        for b in got:
            b.path = rel
        census.extend(got)

    for b in census:
        annotate(b, known, paths, repo)

    # repeated-literal needs the whole census, so it is a second pass. A number
    # written twice is a hand-copied value, and the copies drift; one written
    # once is just a number.
    seen: Counter[str] = Counter()
    where: dict[str, set[str]] = defaultdict(set)
    for b in census:
        for n in prose_numbers(b.text, b.raw_lines):
            seen[n] += 1
            where[n].add(f"{b.path}:{b.start}")
    for b in census:
        for n in prose_numbers(b.text, b.raw_lines):
            if seen[n] > 1 and len(where[n]) > 1:
                b.annotations.add("repeated-literal")
                others = sorted(where[n] - {f"{b.path}:{b.start}"})[:3]
                b.notes.append(f"{n} also in prose at {', '.join(others)}")

    if args.json:
        # !! THE GATE FIRST. `--json --out` is the route SKILL.md mandates for
        # the census stage 5 parses, and this returned 0 with a SHORT array for
        # a file that could not be read -- so a file with no language record,
        # or one that failed to parse, vanished, and the coverage check then
        # certified "every block accounted for" over blocks never collected.
        # The text path errored on exactly the same input.
        if unreadable:
            print(_not_censused(files, unreadable), file=sys.stderr)
            return 1
        print(
            json.dumps(
                [vars(b) | {"annotations": sorted(b.annotations)} for b in census],
                indent=1,
                default=str,
            )
        )
        return 0

    # ! A tier is per FILE: a polyglot repo mixes them in one census. Reported
    # as one global mode, a finding from the lexical floor read like one from
    # the tokenized tier.
    tiers = Counter(b.tier for b in census)
    langs = Counter(lang.name for f in files if (lang := language_for(f)) is not None)
    deferred = [b for b in census if "doc-kind-unresolved" in b.annotations]

    print(f"comment-review stages 2-3 - {len(files)} files, {len(census)} blocks")
    print(f"  languages: {', '.join(f'{k} {v}' for k, v in sorted(langs.items()))}")
    for name in ("tokenized", "lexical"):
        if tiers.get(name):
            print(f"  tier {name}: {tiers[name]} blocks - {TIER_ANSWERS[name]}")
    print(
        "  ! NO COMMENT carries an anchor at either tier. A comment's anchor\n"
        "    comes from READING the file, so a placement finding is a CANDIDATE."
    )
    if deferred:
        print(
            f"  kind unresolved: {len(deferred)} -- a positional doc comment."
            " Confirm the kind before compacting; a cap governs one and not"
            " the other"
        )
    print()

    if args.filtered:
        # !! A PROJECTION, NEVER A RENUMBERING. Each block keeps the index it
        # has in the full census, because that index is what the join resolves
        # and what a record cites -- renumber and every citation from a filtered
        # reviewer resolves to the wrong block, with nothing able to tell.
        print("CENSUS - the blocks holding prose, numbered as in the full census.")
    else:
        print("CENSUS - every block, numbered.")
    run: list[int] = []

    def flush_run() -> None:
        """One line for a stretch of code no prose sits in."""
        if not run:
            return
        first, last = census[run[0] - 1], census[run[-1] - 1]
        span = f"{first.path}:{first.start}-{last.end}"
        print(f"{run[0]:4d}-{run[-1]:<4d} {span}  no prose ({len(run)} intervals)")
        run.clear()

    for i, b in enumerate(census, 1):
        # !! FILTERED, and the intervals become ONE LINE PER RUN rather than
        # vanishing. Measured 2026-08-18 over 1,120 blocks: the full census is
        # 131,353 bytes and every reviewer gets an identical copy, 966 of those
        # blocks are intervals, and prose-only would be 38,446. Collapsing each
        # run instead costs 52,383 -- 85% of the available saving -- and keeps
        # what an `add` is actually about visible: a stretch of code carrying no
        # commentary. A reviewer needing a spot outside its set asks
        # `locator.py`, which answers from the FULL census.
        if args.filtered and b.kind == "interval":
            run.append(i)
            continue
        flush_run()
        notes = ",".join(sorted(b.annotations)) or "-"
        anchor = f"  ({b.anchor})" if b.anchor else ""
        loc = address(vars(b))
        print(f"{i:4d}  {loc}  {b.kind}  {b.lines}L  {notes}{anchor}")
        if not args.census_only:
            for note in b.notes:
                print(f"        -> {note}")
    flush_run()
    print()

    if unread or unreadable:
        print("NOT CHECKED -- these are gaps, not passes:")
        for u in unread + unreadable:
            print(f"    {u}")
        print(
            "    !! A file missing from the name corpus turns every symbol defined\n"
            "      only there into a false obituary. Treat symbol notes as weaker\n"
            "      until this list is empty."
        )
        print()

    print(
        f"{len(census)} blocks censused. `names-a-symbol` and `counted` are\n"
        "CANDIDATES a reviewer confirms; a resolved path is a fact about the\n"
        "filesystem, already settled. The whole list is printed every run."
    )
    # The reviewers are handed the CENSUS, so a file missing from it is blocks
    # nobody reviews and there is nothing downstream that notices. Exit on it.
    if unreadable:
        print("\n" + _not_censused(files, unreadable))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
