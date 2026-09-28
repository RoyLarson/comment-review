"""Renders the difference between two texts, and composes them where disjoint.

One module, three operations over a base and its sides:

    unified(before, after, path)   the unified diff, one side against another
    diff3(base, sides)             the base with every edited span wrapped
    compose(base, sides)           the base with every side's edit applied,
                                    refused where two sides' edits meet

!! `diff3` RENDERS AND `compose` ACTS, and the pair is the reason both live
here. `diff3` wraps every span at least one side edited, even where only one
side touched it, so a person can read what each side did. `compose` applies
the edits, and refuses where two sides' edits meet.

Both read `SequenceMatcher` opcodes, base against each side, because `difflib`
ships no diff3 of its own.
"""

import difflib
from typing import Literal


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


#: `difflib.SequenceMatcher.get_opcodes()`'s own element shape --
#: `(tag, i1, i2, j1, j2)`, `i` into the base sequence and `j` into the other.
_Opcode = tuple[Literal["replace", "delete", "insert", "equal"], int, int, int, int]


# TODO: `diff3` and its helpers `_conflict_spans`, `_touching_roles` and
# `_side_slice` have no caller outside tests/; remove them or give `diff3` one.
def diff3(base: str, sides: dict[str, str]) -> list[str]:
    """The base paragraph plus every role's edit, in `diff3` form.

    !! N-WAY, NOT THREE-WAY. `sides` may carry any number of roles, and each
    is diffed against `base`.

    Args:
        base: the paragraph's `raw_text` before any of these edits.
        sides: role name -> that role's proposed `change`, both whole
            paragraphs as raw text (`decision-log.md Vocabulary: #27`).
            Rendered sorted by role name, so the same inputs render
            byte-identically every call.

    Returns:
        `base`, with every span at least one side edited wrapped in a
        conflict span naming each differing side; a span no side touched
        renders as plain text, unmarked. A conflict span reads:

            <<<<<<< conflict
            ||||||| base
            <base's lines for this span>
            ======= <role>
            <that role's lines for this span>
            ======= <another role, sorted after the first>
            <that role's lines for this span>
            >>>>>>> end

        Only roles that differ from `base` at that span appear -- a role
        left unchanged there is implied by its absence. Each content line
        still carries its own trailing newline where the source line had
        one; the marker lines this function adds always end in one.
    """
    base_lines = base.splitlines(True)
    roles = sorted(sides)
    sides_lines = {role: sides[role].splitlines(True) for role in roles}
    opcodes: dict[str, list[_Opcode]] = {
        role: difflib.SequenceMatcher(None, base_lines, sides_lines[role]).get_opcodes()
        for role in roles
    }

    out: list[str] = []
    at = 0
    for start, end in _conflict_spans(opcodes, roles):
        out.extend(base_lines[at:start])
        out.append("<<<<<<< conflict\n")
        out.append("||||||| base\n")
        out.extend(base_lines[start:end])
        for role in _touching_roles(opcodes, roles, start, end):
            out.append(f"======= {role}\n")
            out.extend(
                _side_slice(base_lines, sides_lines[role], opcodes[role], start, end)
            )
        out.append(">>>>>>> end\n")
        at = end
    out.extend(base_lines[at:])
    return out


# TODO: hand the message to the place the refusal is recorded on, or stop
# building it -- both catches in `desk/evaluate/passes.py` discard it.
class CannotCompose(Exception):
    """Two sides' edits met under the rule `compose` states, so no composition exists.

    !! RAISED, NOT RETURNED AS A SENTINEL, so a caller cannot mistake a refusal
    for text. A composed paragraph and "no composition" are different kinds of
    answer, and an empty string is a legal paragraph -- `drop`'s.

    The message names the base lines the meeting edits span and the two sides.
    `desk/evaluate/passes.py` catches the refusal without reading the message;
    only the tests read it.
    """


def compose(base: str, sides: dict[str, str]) -> str:
    """The base with every side's edit applied, where no two sides met.

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

    ! TWO SIDES MEET where their edits share a base line, where two rewrites
    sit on adjacent lines, where two inserts sit at one position, or where one
    side inserts inside lines the other rewrites. Adjacent rewrites meet
    because they can be two halves of one wrapped sentence; two inserts at one
    position have no order. An insert at the edge of another side's rewrite
    has one order, the base's, and composes (`mark-defects` T28).

    ! AN UNTERMINATED PARAGRAPH IS DIFFED AS IF TERMINATED. A `raw_text` ends
    without a newline, so a line added after it would otherwise read as a
    rewrite of the last line, and meet an edit on the line above it. The
    newline is added to the base and to every side for the diff, and taken off
    the composed paragraph again.

    Raises:
        CannotCompose: two sides' edits met, naming the base lines the first
            meeting pair spans and those two sides.
    """
    terminated = not base or base.endswith("\n")
    if not terminated:
        base += "\n"
        sides = {role: side + "\n" for role, side in sides.items()}
    composed = _compose_lines(base, sides)
    return composed if terminated else composed.removesuffix("\n")


#: One side's edit: `(role, i1, i2, the lines it puts in base[i1:i2]'s place)`.
_Edit = tuple[str, int, int, list[str]]


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
    return a1 <= b2 and b1 <= a2


def _compose_lines(base: str, sides: dict[str, str]) -> str:
    """`compose` over a base whose every line ends in a newline, the last included."""
    base_lines = base.splitlines(True)
    edits: list[_Edit] = []
    for role in sorted(sides):
        side_lines = sides[role].splitlines(True)
        matcher = difflib.SequenceMatcher(None, base_lines, side_lines)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != "equal":
                edits.append((role, i1, i2, side_lines[j1:j2]))
    for i, a in enumerate(edits):
        for b in edits[i + 1 :]:
            if a[0] != b[0] and _meet(a, b):
                start, end = min(a[1], b[1]), max(a[2], b[2])
                raise CannotCompose(
                    f"base lines {start + 1}-{max(end, start + 1)} were edited by "
                    f"{', '.join(sorted({a[0], b[0]}))} -- no composition"
                )
    # An insert at a position goes before a rewrite that starts there.
    edits.sort(key=lambda edit: (edit[1], edit[1] != edit[2]))
    out: list[str] = []
    at = 0
    for _role, i1, i2, lines in edits:
        out.extend(base_lines[at:i1])
        out.extend(lines)
        at = i2
    out.extend(base_lines[at:])
    return "".join(out)


def _conflict_spans(
    opcodes: dict[str, list[_Opcode]], roles: list[str]
) -> list[tuple[int, int]]:
    """Every base-line span at least one side edits, merged where they touch.

    One side's edited span can overlap another's without the two agreeing on
    where it starts or ends; merging keeps `_side_slice` from ever having to
    cut a non-`equal` opcode in half, since every span this returns is grown
    to the full extent of every opcode that falls inside it.
    """
    spans = [
        (i1, i2)
        for role in roles
        for tag, i1, i2, _j1, _j2 in opcodes[role]
        if tag != "equal"
    ]
    if not spans:
        return []
    spans.sort()
    merged = [list(spans[0])]
    for start, end in spans[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


def _touching_roles(
    opcodes: dict[str, list[_Opcode]], roles: list[str], start: int, end: int
) -> list[str]:
    """Roles that edit the base span from `start` to `end`, in `roles` order.

    A non-`equal` opcode counts when it overlaps the half-open range
    `[start, end)`; an insert counts at any position from `start` to `end`
    inclusive.

    A role missing from the result left this span identical to `base` -- its
    content there IS the base text, so the conflict span says nothing about
    it and a reader reconstructing that role's side uses `base`.
    """
    touching = []
    for role in roles:
        for tag, i1, i2, _j1, _j2 in opcodes[role]:
            if tag == "equal":
                continue
            if i1 == i2:
                if start <= i1 <= end:
                    touching.append(role)
                    break
            elif i1 < end and i2 > start:
                touching.append(role)
                break
    return touching


def _side_slice(
    base_lines: list[str],
    side_lines: list[str],
    opcodes: list[_Opcode],
    start: int,
    end: int,
) -> list[str]:
    r"""One role's content for base span `[start, end)`.

    Walks that role's own opcodes -- which partition the whole base range --
    keeping only the ones overlapping this span. An `equal` opcode is safe to
    clip to an arbitrary sub-range, since it is a line-for-line
    correspondence with `base`; a non-`equal` opcode is never partial here,
    because `_conflict_spans` already grew `[start, end)` to the full extent
    of every opcode inside it.

    !! AN `insert` OPCODE HAS `i1 == i2` AND IS TESTED THE WAY `_touching_roles`
    TESTS IT -- `start <= i1 <= end`, the closed test a zero-width position
    needs. The half-open test the other opcodes take (`i2 <= start or
    i1 >= end`) would skip an insert at either edge of the span, and a span
    that holds only an insert is all edge.

    ! THE TWO TESTS CANNOT MEET AT ONE SPAN'S EDGE. `_conflict_spans` merges
    whenever `start <= merged[-1][1]`, so no two spans it returns are adjacent,
    and an insert at a shared boundary cannot be claimed by both.
    """
    out = []
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            if i2 <= start or i1 >= end:
                continue
            out.extend(base_lines[max(i1, start) : min(i2, end)])
            continue
        if i1 == i2:
            if not start <= i1 <= end:
                continue
        elif i2 <= start or i1 >= end:
            continue
        out.extend(side_lines[j1:j2])
    return out
