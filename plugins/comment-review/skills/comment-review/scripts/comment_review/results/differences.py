"""Renders the difference between two texts.

One module, two renderings -- `unified` is the first; `diff3` is the second,
rendering the base paragraph plus every role's edit.

!! NO GIT PROCESS. A revise root is a temp copy `flows.revise.pull` made and
need not be a repo -- `difflib.unified_diff` reads two strings, not two
commits.

!! `diff3` IS N-WAY, NOT THREE-WAY. One mark per role per place, and the
all-concurrent topology dispatches four roles at once against one paragraph
-- base plus four sides is the normal case, not an edge one. `difflib` ships
no diff3 of its own; this builds the merge from `SequenceMatcher` opcodes,
base against each side.
"""

import difflib
from typing import Literal


def unified(before: str, after: str, path: str) -> list[str]:
    """The unified diff from `before` to `after`, naming `path` on both sides.

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


def diff3(base: str, sides: dict[str, str]) -> list[str]:
    """The base paragraph plus every role's edit, in `diff3` form.

    !! N-WAY, NOT THREE-WAY. One mark per role per place, and the
    all-concurrent topology dispatches four roles at once -- base plus four
    sides is the ordinary case, not an edge one. `sides` may carry any
    number of entries.

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
    """Roles with a non-`equal` opcode inside `[start, end)`, in `roles` order.

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
    needs. A half-open overlap test (`i2 <= start or i1 >= end`) is FALSE for
    every empty base range, so one shared test dropped every pure insert.
    MEASURED 2026-08-29: `diff3("# a\n# b\n", {"block-context":
    "# a\n# INSERTED\n# b\n"})` rendered the conflict span with the added
    line nowhere, under a `======= block-context` header `_touching_roles`
    still printed -- so a role that used `add`, one of the seven instructions,
    read in the artifact a human rules on as having proposed nothing. With a
    second role at the same span the inserting role's section renders
    byte-identical to base, which reads as agreement rather than as a loss.

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
