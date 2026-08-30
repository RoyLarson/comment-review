"""`differences.unified`, `differences.diff3` and `differences.compose`: a
per-page diff, the base-plus-every-side merge, and the applied composition.
Nothing else.

! `apply_unified` BELOW IS TEST-ONLY, not a shipped applier -- `differences.py`
renders and nothing reverses it. It exists so this suite's own pass criterion
(`docs/plans/0.2.4-the-mark-and-the-collator.md` T5.2: "the rendered diff
applies to the original") is a CHECKED literal round trip rather than a read
of the diff's text. It is local to this file because nothing else needs it --
`tests/helpers.py`'s own header reserves that file for inputs, not assertions.

! `parse_diff3` BELOW IS THE SAME KIND OF TEST-ONLY REVERSER, for T5.1's
`diff3`. It exists so T1's round trip
(`TODO/a-conflict-has-no-rendering.md`: "the output parses back into its
sides") is a checked literal comparison rather than a read of the marker text.
"""

import re
from pathlib import Path

import pytest
from helpers import a_small_real_tree, binder_of

from comment_review.results.differences import CannotCompose, compose, diff3, unified

_REPO_ROOT = Path(__file__).resolve().parents[1]

_HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@")


def apply_unified(before: str, diff_lines: list[str]) -> str:
    """`before`, with every hunk in `diff_lines` applied -- a minimal patcher
    for the exact format `difflib.unified_diff` emits.

    Args:
        before: the text the diff was rendered FROM.
        diff_lines: as `unified()` returns them.

    Returns:
        `before` with each hunk's `-`/`+` lines taken in.
    """
    before_lines = before.splitlines(True)
    result: list[str] = []
    at = 0  # index into before_lines already copied into result
    i = 0
    while i < len(diff_lines):
        line = diff_lines[i]
        if line.startswith("--- ") or line.startswith("+++ "):
            i += 1
            continue
        header = _HUNK_HEADER.match(line)
        if header is None:
            i += 1
            continue
        start = int(header.group(1)) - 1
        result.extend(before_lines[at:start])
        at = start
        i += 1
        while i < len(diff_lines) and not diff_lines[i].startswith("@@"):
            hunk_line = diff_lines[i]
            if hunk_line.startswith(" "):
                result.append(before_lines[at])
                at += 1
            elif hunk_line.startswith("-"):
                at += 1
            elif hunk_line.startswith("+"):
                result.append(hunk_line[1:])
            i += 1
    result.extend(before_lines[at:])
    return "".join(result)


def test_the_rendered_diff_reproduces_the_revise():
    # !! THE SUBSTITUTED TEXT IS REAL, GREPPED OFF THE FILE ITSELF -- `CLAUDE.md`'s
    # ruling against a hand-authored fixture. `mark.py:227`'s own docstring reads
    # "carries the keys this instruction's row demands".
    rel = "src/comment_review/desk/mark.py"
    before = (_REPO_ROOT / rel).read_text(encoding="utf-8")
    needle = "the keys this instruction's row demands"
    assert needle in before
    after = before.replace(needle, "the keys THIS instruction's row demands", 1)
    lines = unified(before, after, rel)
    assert apply_unified(before, lines) == after  # a checked literal round trip


def test_no_difference_renders_no_lines():
    text = (_REPO_ROOT / "src/comment_review/desk/mark.py").read_text(encoding="utf-8")
    assert unified(text, text, "mark.py") == []


def test_the_path_names_both_sides():
    lines = unified("a\n", "b\n", "m.py")
    assert lines[0].startswith("--- m.py")
    assert lines[1].startswith("+++ m.py")


def test_three_lines_of_context_on_each_side():
    # !! PINS `n=3` DIRECTLY. `apply_unified`'s round trip above does not --
    # it reconstructs from the `-`/`+` lines and ignores how much context
    # surrounds them, so a change to `n` would pass that test unnoticed.
    before = "".join(f"{i}\n" for i in range(1, 11))
    after = before.replace("5\n", "five\n")
    lines = unified(before, after, "m.py")
    context = [line for line in lines if line.startswith(" ")]
    assert len(context) == 6  # three lines before the change, three after


# --------------------------------------------------------------------------
# `diff3`


def _three_line_row(repo: Path) -> str:
    """A real paragraph's `raw_text`, three non-blank lines exactly -- found
    by scanning `repo` (built by `a_small_real_tree`), not hand-picked, so
    the fixture is real source and not a literal `CLAUDE.md` forbids.
    """
    binder = binder_of(repo, 0)
    for page in binder.get("pages", []):
        for row in page.get("rows", []):
            lines = row["raw_text"].splitlines()
            if len(lines) == 3 and all(line.strip() for line in lines):
                return row["raw_text"]
    raise AssertionError("no three-line row found in a_small_real_tree")


def _edit_line(raw_text: str, index: int, marker: str) -> str:
    """`raw_text` with `marker` appended to line `index`, before its newline.

    A mechanical edit of real text -- nothing about the other lines moves,
    so two calls on the SAME `raw_text` at DIFFERENT indices differ from
    each other only where they were each told to.
    """
    lines = raw_text.splitlines(True)
    line = lines[index]
    if line.endswith("\n"):
        lines[index] = line[:-1] + marker + "\n"
    else:
        lines[index] = line + marker
    return "".join(lines)


def _insert_line(raw_text: str, index: int, added: str) -> str:
    """`raw_text` with `added` as a whole NEW line before line `index`.

    ! THE SHAPE `_edit_line` CANNOT PRODUCE. A replace leaves the base line
    count alone, so `SequenceMatcher` never emits an `insert` opcode for one --
    which is why every diff3 case above was blind to how an insert renders.
    `add` is one of the seven instructions, and it is prose that was not there.
    """
    lines = raw_text.splitlines(True)
    lines.insert(index, added + "\n")
    return "".join(lines)


def parse_diff3(lines: list[str], roles: list[str]) -> tuple[str, dict[str, str]]:
    """`diff3`'s own inverse, for `roles` it is known to carry.

    Args:
        lines: as `diff3()` returns them.
        roles: every role name the render may carry a `======= <role>`
            section for.

    Returns:
        `(base, sides)` -- `base` the whole base text `diff3` was given,
        `sides` every named role's whole reconstructed text. A role absent
        from a conflict block contributed nothing there, so that span comes
        from `base` in its reconstruction.
    """
    base_out: list[str] = []
    sides_out: dict[str, list[str]] = {role: [] for role in roles}
    i = 0
    while i < len(lines):
        line = lines[i]
        if line != "<<<<<<< conflict\n":
            base_out.append(line)
            for role in roles:
                sides_out[role].append(line)
            i += 1
            continue
        i += 1
        assert lines[i] == "||||||| base\n"
        i += 1
        base_block: list[str] = []
        while not (lines[i].startswith("=======") or lines[i] == ">>>>>>> end\n"):
            base_block.append(lines[i])
            i += 1
        base_out.extend(base_block)
        side_blocks: dict[str, list[str]] = {}
        while lines[i].startswith("======= "):
            role = lines[i][len("======= ") :].rstrip("\n")
            i += 1
            block: list[str] = []
            while not (lines[i].startswith("=======") or lines[i] == ">>>>>>> end\n"):
                block.append(lines[i])
                i += 1
            side_blocks[role] = block
        assert lines[i] == ">>>>>>> end\n"
        i += 1
        for role in roles:
            sides_out[role].extend(side_blocks.get(role, base_block))
    sides = {role: "".join(block) for role, block in sides_out.items()}
    return "".join(base_out), sides


def test_diff3_round_trip_recovers_base_and_every_side(tmp_path):
    repo = a_small_real_tree(tmp_path)
    base = _three_line_row(repo)
    side_a = _edit_line(base, 0, " -- EDITED BY block-context")
    side_b = _edit_line(base, 2, " -- EDITED BY function-context")

    roles = ["block-context", "function-context"]
    rendered = diff3(base, {"block-context": side_a, "function-context": side_b})
    parsed_base, parsed_sides = parse_diff3(rendered, roles)

    assert parsed_base == base  # T1: the base side is byte-identical to the paragraph
    assert parsed_sides == {"block-context": side_a, "function-context": side_b}


def test_diff3_shows_disjoint_edits_the_two_sided_form_does_not(tmp_path):
    # T2: two edits on DIFFERENT lines of one paragraph must render disjoint,
    # and the same pair rendered two-sided (no base) must not.
    repo = a_small_real_tree(tmp_path)
    base = _three_line_row(repo)
    side_a = _edit_line(base, 0, " -- EDITED BY block-context")
    side_b = _edit_line(base, 2, " -- EDITED BY function-context")

    rendered = diff3(base, {"block-context": side_a, "function-context": side_b})
    # !! THE ASSERTION THAT FAILS UNDER THE TWO-SIDED FORM: two separate
    # conflict blocks, one per edited line, with base's untouched middle
    # line sitting as plain text between them.
    assert rendered.count("<<<<<<< conflict\n") == 2
    first_close = rendered.index(">>>>>>> end\n")
    second_open = rendered.index("<<<<<<< conflict\n", first_close)
    between = rendered[first_close + 1 : second_open]
    assert between == [base.splitlines(True)[1]]  # the unedited middle line

    # The two-sided form: `side_a` diffed straight against `side_b`, no base.
    # With one unchanged line between two one-line edits, `unified`'s default
    # context (n=3) folds both into ONE hunk -- the two edits are no longer
    # distinguishable as separate, disjoint changes.
    two_sided = unified(side_a, side_b, "paragraph")
    hunks = [line for line in two_sided if line.startswith("@@")]
    assert len(hunks) == 1


def test_diff3_renders_a_pure_INSERT_a_role_proposed(tmp_path):
    """A role that ADDS a line rendered as having proposed nothing: the added
    line appeared nowhere under its own `======= <role>` header, in the
    artifact a human rules on."""
    repo = a_small_real_tree(tmp_path)
    base = _three_line_row(repo)
    side = _insert_line(base, 1, "# ADDED BY block-context")

    rendered = diff3(base, {"block-context": side})
    assert "# ADDED BY block-context\n" in rendered
    parsed_base, parsed_sides = parse_diff3(rendered, ["block-context"])
    assert parsed_base == base
    assert parsed_sides == {"block-context": side}


def test_diff3_keeps_an_INSERT_beside_another_role_s_edit(tmp_path):
    """The worse shape: with a second role editing the same span, the inserting
    role's section rendered byte-identical to base -- which reads as agreement
    rather than as a lost proposal."""
    repo = a_small_real_tree(tmp_path)
    base = _three_line_row(repo)
    inserted = _insert_line(base, 1, "# ADDED BY block-context")
    replaced = _edit_line(base, 1, " -- EDITED BY module-context")

    roles = ["block-context", "module-context"]
    rendered = diff3(base, {"block-context": inserted, "module-context": replaced})
    parsed_base, parsed_sides = parse_diff3(rendered, roles)
    assert parsed_base == base
    assert parsed_sides == {"block-context": inserted, "module-context": replaced}
    assert parsed_sides["block-context"] != base


def test_diff3_keeps_every_side_when_several_roles_conflict_at_one_place(tmp_path):
    # T4: three, then four, conflicting marks at one place render without
    # losing any of them.
    repo = a_small_real_tree(tmp_path)
    base = _three_line_row(repo)
    role_names = [
        "block-context",
        "function-context",
        "module-context",
        "ownership-context",
    ]

    for count in (3, 4):
        roles = role_names[:count]
        sides = {role: _edit_line(base, 0, f" -- EDITED BY {role}") for role in roles}

        rendered = diff3(base, sides)
        assert rendered.count("<<<<<<< conflict\n") == 1  # one place, one block
        seen = [
            line[len("======= ") :].rstrip("\n")
            for line in rendered
            if line.startswith("======= ")
        ]
        assert seen == sorted(roles)  # every side present, in the stable order

        parsed_base, parsed_sides = parse_diff3(rendered, roles)
        assert parsed_base == base
        assert parsed_sides == sides


# --------------------------------------------------------------------------
# `compose`


class TestCompose:
    def test_two_edits_on_different_lines_merge(self):
        base = "# one\n# two\n# three\n"
        sides = {
            "block-context": "# ONE\n# two\n# three\n",
            "function-context": "# one\n# two\n# THREE\n",
        }
        assert compose(base, sides) == "# ONE\n# two\n# THREE\n"

    def test_two_edits_on_one_line_refuse_by_name(self):
        base = "# one\n# two\n"
        sides = {
            "block-context": "# ONE\n# two\n",
            "function-context": "# uno\n# two\n",
        }
        with pytest.raises(CannotCompose) as caught:
            compose(base, sides)
        message = str(caught.value)
        assert "block-context" in message
        assert "function-context" in message

    def test_one_side_composes_to_that_side(self):
        base = "# one\n# two\n"
        sides = {"block-context": "# ONE\n# two\n"}
        assert compose(base, sides) == "# ONE\n# two\n"

    def test_no_side_composes_to_the_base(self):
        base = "# one\n# two\n"
        assert compose(base, {}) == base

    def test_a_side_that_changed_nothing_does_not_claim_a_span(self):
        """A role that edited nothing is not a party to any span, so another
        role's lone edit still composes."""
        base = "# one\n# two\n"
        sides = {
            "block-context": "# ONE\n# two\n",
            "function-context": "# one\n# two\n",
        }
        assert compose(base, sides) == "# ONE\n# two\n"

    def test_a_pure_insert_is_carried(self):
        """!! THE SHAPE THAT WAS MEASURED LOST ONCE. An `insert` opcode has
        `i1 == i2`, and a half-open overlap test is False for every empty base
        range -- which dropped every pure insert from `diff3`'s render on
        2026-08-29. `_side_slice` uses the closed test; this proves `compose`
        inherits it."""
        base = "# a\n# b\n"
        sides = {"block-context": "# a\n# INSERTED\n# b\n"}
        assert compose(base, sides) == "# a\n# INSERTED\n# b\n"

    def test_an_insert_and_a_distant_edit_compose(self):
        base = "# a\n# b\n# c\n# d\n"
        sides = {
            "block-context": "# a\n# INSERTED\n# b\n# c\n# d\n",
            "function-context": "# a\n# b\n# c\n# D\n",
        }
        assert compose(base, sides) == "# a\n# INSERTED\n# b\n# c\n# D\n"
