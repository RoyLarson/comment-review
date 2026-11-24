"""Renders the difference between two texts, and composes them where disjoint.

    unified(before, after, path)   the unified diff, one side against another
    compose(base, sides)           the base with every side's edit applied,
                                    refused where two sides' edits meet

`compose` reads `SequenceMatcher` opcodes, base against each side, because
`difflib` ships no three-way merge of its own.

The top-level `comment_review.differences` leaf renders and composes texts
without file I/O. It is shared by the middle and the command line.
"""

import bisect
import difflib
import re


def unified(before: str, after: str, path: str) -> list[str]:
    """The unified diff from `before` to `after`, naming `path` on both sides.

    !! NO GIT PROCESS. A revise root is a temp copy `flows.revise.pull` made and
    need not be a repo -- `difflib.unified_diff` reads two strings, not two
    commits.

    Args:
        before: the page's text before the revise.
        after: the page's text after the revise.
        path: printed on the `---`/`+++` lines. The original and the revise
            root name the same page at the same relative path, so one string
            serves both sides.

    Returns:
        Every line `difflib.unified_diff` yields, each still carrying its own
        trailing newline where the source line had one -- a caller prints
        them joined, or writes them to a patch file, without re-adding
        separators.
    """
    return list(
        difflib.unified_diff(
            before.splitlines(True),
            after.splitlines(True),
            fromfile=path,
            tofile=path,
            n=3,
        )
    )


# TODO: hand the message to the place the refusal is recorded on, or stop
# building it -- both catches in `desk/evaluate/passes.py` discard it.
class CannotCompose(Exception):
    """Two sides' edits met under the rule `compose` states, so no composition exists.

    !! RAISED, NOT RETURNED AS A SENTINEL, so a caller cannot mistake a refusal
    for text. A composed paragraph and "no composition" are different kinds of
    answer, and an empty string is a legal paragraph -- `drop`'s.

    The message names the base lines the meeting edits span and their proposers.
    `desk/evaluate/passes.py` catches the refusal without reading the message;
    only the tests read it.
    """


def compose(base: str, sides: dict[str, str]) -> str:
    """The base with each distinct edit applied once, unless edits compete.

    ! A SIDE THAT CHANGED NOTHING AT A SPAN IS NOT A PARTY TO IT. Only a side's
    non-`equal` opcodes are its edits, so three roles of which one edited
    compose to that one's text.

    Args:
        base: the paragraph before any of these edits. !! IT MUST BE THE TEXT
            THE RUN SEEDED, never a `raw_text` that came back on a mark -- a
            check that reads its base off the thing it is checking cannot
            disagree with it.
        sides: a name for each side -> that side's proposed text, a whole
            paragraph as raw text: a role's `change`, or one mark's text when
            a role's own marks compose.

    Returns:
        The composed paragraph. An empty `sides` returns `base` unchanged --
        nothing was proposed, so nothing is applied.

    ! AN EDIT IS A SPAN OF WORDS. Each side is diffed against the base by
    line, and each run of rewritten lines again by token -- a line end, a
    run of other whitespace, a word, or one other character -- so an edit is
    the base tokens it replaces and the tokens it puts there. A line added or
    removed whole stays one edit at a line's edge. Only the texts are read, so
    edits compose alike whoever filed them.

    Equal edits share a base span and replacement tokens. They apply once;
    their proposer names remain available if a different edit conflicts.

    ! TWO DIFFERENT EDITS MEET where the base tokens they change overlap,
    where two inserts sit at one position, or where one inserts strictly
    inside the tokens the other changes. Two inserts at one position have no
    order; anywhere else the base gives the order, so edits on neighbouring
    words or lines compose.

    ! AN UNTERMINATED PARAGRAPH IS DIFFED AS IF TERMINATED. A `raw_text` ends
    without a newline, so a line added after it would otherwise read as a
    rewrite of the last line, and meet an edit on the line above it. The
    newline is added to the base and to every side for the diff, and taken off
    the composed paragraph again.

    Raises:
        CannotCompose: different edits met, naming the base lines the first
            meeting pair spans and every proposer of those edits.
    """
    terminated = not base or base.endswith("\n")
    if not terminated:
        base += "\n"
        sides = {role: side + "\n" for role, side in sides.items()}
    composed = _compose_tokens(base, sides)
    return composed if terminated else composed.removesuffix("\n")


#: A token, as `compose` diffs rewritten lines: a line end, a run of other
#: whitespace, a word, or one other character. Every character of a text
#: falls in exactly one, so joining a text's tokens gives the text back.
_TOKEN = re.compile(r"\n|[^\S\n]+|\w+|[^\w\s]")

#: One distinct edit: its proposers, base token span, and replacement tokens.
_Edit = tuple[frozenset[str], int, int, tuple[str, ...]]


def _meet(a: _Edit, b: _Edit) -> bool:
    """Whether two sides' edits meet, under the rule `compose` states."""
    _, a1, a2, _ = a
    _, b1, b2, _ = b
    if a1 == a2 and b1 == b2:
        return a1 == b1
    if a1 == a2:
        return b1 < a1 < b2
    if b1 == b2:
        return a1 < b1 < a2
    return a1 < b2 and b1 < a2


def _compose_tokens(base: str, sides: dict[str, str]) -> str:
    """`compose` over a base whose every line ends in a newline, the last included."""
    base_lines = base.splitlines(True)
    base_tokens = _TOKEN.findall(base)
    # The token index each base line starts at, and one past the last line.
    starts = [0]
    for line in base_lines:
        starts.append(starts[-1] + len(_TOKEN.findall(line)))
    by_operation: dict[tuple[int, int, tuple[str, ...]], set[str]] = {}
    for role in sorted(sides):
        side_lines = sides[role].splitlines(True)
        lines = difflib.SequenceMatcher(None, base_lines, side_lines, autojunk=False)
        for tag, i1, i2, j1, j2 in lines.get_opcodes():
            if tag == "equal":
                continue
            tokens = _TOKEN.findall("".join(side_lines[j1:j2]))
            at = starts[i1]
            if tag != "replace":
                operation = (at, starts[i2], tuple(tokens))
                by_operation.setdefault(operation, set()).add(role)
                continue
            words = difflib.SequenceMatcher(
                None, base_tokens[at : starts[i2]], tokens, autojunk=False
            )
            for word_tag, a1, a2, b1, b2 in words.get_opcodes():
                if word_tag != "equal":
                    operation = (at + a1, at + a2, tuple(tokens[b1:b2]))
                    by_operation.setdefault(operation, set()).add(role)
    edits: list[_Edit] = [
        (frozenset(roles), i1, i2, tokens)
        for (i1, i2, tokens), roles in by_operation.items()
    ]
    for i, a in enumerate(edits):
        for b in edits[i + 1 :]:
            if len(a[0] | b[0]) > 1 and _meet(a, b):
                first = bisect.bisect_right(starts, min(a[1], b[1])) - 1
                last = bisect.bisect_right(starts, max(a[2], b[2]) - 1) - 1
                raise CannotCompose(
                    f"base lines {first + 1}-{max(first, last) + 1} were edited by "
                    f"{', '.join(sorted(a[0] | b[0]))} -- no composition"
                )
    # An insert at a position goes before a rewrite that starts there.
    edits.sort(key=lambda edit: (edit[1], edit[1] != edit[2]))
    out: list[str] = []
    at = 0
    for _role, i1, i2, tokens in edits:
        out.extend(base_tokens[at:i1])
        out.extend(tokens)
        at = i2
    out.extend(base_tokens[at:])
    return "".join(out)

