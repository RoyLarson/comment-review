"""Comment-stripped comparisons for non-Python source and line-ending measures.

The comment lexer removes admitted prose and compares the remaining lines,
right-stripped with blank lines dropped. Ambiguous comment boundaries and
spanning literals make this comparison unprovable. Python proofs compare the
lexical records held by admitted pages in their proof flows.

Line endings are measured separately against an untouched sibling, since Git
may normalize the stored baseline's endings.
"""

from pathlib import Path

from comment_review import constants
from comment_review.reading.lexer import (
    Language,
    language_for,
    paragraphs_lexical,
)


def _delimiter_shares_the_line(line: str, lang: Language) -> bool:
    """A paragraph-comment delimiter with real code beside it, on this ONE line.

    `paragraphs_lexical` stores the WHOLE line for a paragraph comment's opening,
    closing or single-line form -- including any code that sits before the
    opener or after the closer -- so that line is stored identically to a line
    that is comment start to end. Re-scanning the line for the delimiters
    themselves is what separates them.

    ! A raw substring search, where gather's own lexer is string-literal-aware.
    A delimiter spelled inside a string literal on the same line trips this and
    routes a safe line to `unprovable` -- the SAFE direction for a proof to
    fail, so it stands in place of a second copy of gather's quoting logic.
    """
    for opener, closer in lang.block_comment:
        if opener in line and line[: line.index(opener)].strip():
            return True
        if closer in line and line[line.index(closer) + len(closer) :].strip():
            return True
    return False


def _without_comments(text: str, path: Path) -> str | None:
    """The file with every comment paragraph removed, or None if unprovable here.

    Exact where the data allows it: a paragraph's `raw_lines` is a literal slice of
    the source, so a line whose stored text matches it exactly is dropped whole,
    and a line whose stored text is only a SUFFIX (the trailing-comment case)
    keeps its code prefix. A line this cannot place -- code sharing a line with
    a paragraph-comment delimiter, see `_delimiter_shares_the_line` -- makes the
    whole file unprovable.

    An UNTERMINATED paragraph comment is refused the same way, on the gather's own
    `unterminated-paragraph-comment` annotation. The lexer swallows every line below
    the opener into that run, so code below it never reaches the comparison and
    the stripped text is merely SHORT -- short, plausible, and equal on two
    files whose executable code differs.
    """
    lang = language_for(path)
    if lang is None:
        return None
    try:
        paragraphs = paragraphs_lexical(path, text, lang)
    except Exception:  # noqa: BLE001  -- an unprovable file is reported, not passed
        return None
    if any("unterminated-paragraph-comment" in b.annotations for b in paragraphs):
        return None
    # !! A LITERAL THAT SPANS LINES MAKES THIS FILE UNPROVABLE. `_strip_strings`
    # is per-line and carries no open-quote state, so a line INSIDE a JS
    # template literal or a Java text block that begins with the language's
    # comment marker is read as a comment and deleted from BOTH
    # fingerprints. Measured 2026-08-17: a template literal whose body changed
    # from `// alpha` to `// omega` produced identical fingerprints and the file
    # was reported PROVEN -- a fail-OPEN in the one gate whose whole claim is
    # that executable code is byte-identical.
    #
    # ! This refuses on the delimiter's PRESENCE, not on parity: parity is what
    # the per-line lexer already cannot compute, so trusting it here would be
    # the same mistake one layer up. A proof that refuses costs a report; a
    # proof that lies costs the claim.
    if any(q in text for q in lang.spanning_quotes):
        return None

    lines = constants.text_lines(text)
    # Pre-seed every line as itself; a paragraph below either drops its entry
    # (None) or replaces it with the code prefix it proved survives.
    kept: dict[int, str | None] = {i + 1: ln.rstrip() for i, ln in enumerate(lines)}
    for paragraph in paragraphs:
        for offset, n in enumerate(range(paragraph.start, paragraph.end + 1)):
            if n not in kept or offset >= len(paragraph.raw_lines):
                return None  # a paragraph naming a line this text does not have
            actual = lines[n - 1].rstrip()
            stored = paragraph.raw_lines[offset]
            if actual == stored:
                if _delimiter_shares_the_line(actual, lang):
                    return None
                kept[n] = None
            elif stored and actual.endswith(stored):
                kept[n] = actual[: len(actual) - len(stored)].rstrip()
            else:
                return None  # binder and the file disagree; do not reconcile
    survivors = [v for v in kept.values() if v is not None]
    return "\n".join(v for v in survivors if v.strip())


def code_fingerprint(text: str, path: Path) -> tuple[str, str]:
    """Compare non-Python code using the language's comment-stripped source.

    Args:
        text: the file's contents.
        path: used only for its suffix, to pick which comparison runs.

    Returns:
        `(kind, fingerprint)`. `kind` is "stripped" or "unprovable". Python
        requires admitted lexical records and returns "unprovable" here. An
        unprovable file carries an empty fingerprint and cannot be proven.
    """
    if path.suffix.lower() in (".py", ".pyi"):
        return "unprovable", ""
    stripped = _without_comments(text, path)
    if stripped is None:
        return "unprovable", ""
    if not stripped.strip() and text.strip():
        # An all-comment file reaches here STRIPPED to nothing while the source
        # held text. `"" == ""` would "prove" any two such files identical
        # whatever code either one carried.
        return "unprovable", ""
    return "stripped", stripped


def dominant_ending(text: str) -> str:
    """Which line ending this text mostly uses: "crlf", "lf" or "none"."""
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    if crlf == 0 and lf == 0:
        return "none"
    return "crlf" if crlf >= lf else "lf"
