"""`differences.unified` and `differences.compose`: a per-page diff and the
applied composition. Nothing else.

! `apply_unified` BELOW IS TEST-ONLY, not a shipped applier -- `differences.py`
renders and nothing reverses it. It exists so this suite's own pass criterion
(`docs/plans/0.2.4-the-mark-and-the-collator.md` T5.2: "the rendered diff
applies to the original") is a CHECKED literal round trip rather than a read
of the diff's text. It is local to this file because nothing else needs it --
`tests/helpers.py`'s own header reserves that file for inputs, not assertions.
"""

import re
from pathlib import Path

import pytest

from comment_review.differences import CannotCompose, compose, unified

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
    # ruling against a hand-authored fixture. `marks/rules.py`'s `derived_change`
    # docstring reads "The quoted clause is one statement".
    rel = "src/comment_review/desk/marks/rules.py"
    before = (_REPO_ROOT / rel).read_text(encoding="utf-8")
    needle = "The quoted clause is one statement"
    assert needle in before
    after = before.replace(needle, "The quoted clause is ONE statement", 1)
    lines = unified(before, after, rel)
    assert apply_unified(before, lines) == after  # a checked literal round trip


def test_no_difference_renders_no_lines():
    text = (_REPO_ROOT / "src/comment_review/desk/marks/rules.py").read_text(
        encoding="utf-8"
    )
    assert unified(text, text, "rules.py") == []


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
# `compose`


class TestCompose:
    @pytest.mark.parametrize("ending", ("\n", ""))
    def test_identical_replacements_apply_once(self, ending):
        base = "# one\n# two" + ending
        side = "# ONE\n# two" + ending
        assert compose(base, {"a": side, "b": side}) == side

    def test_identical_deletions_apply_once(self):
        assert compose("# one\n# two\n", {"a": "# two\n", "b": "# two\n"}) == "# two\n"

    @pytest.mark.parametrize("base", ("", "# one\n"))
    def test_identical_insertions_apply_once(self, base):
        side = "# inserted\n" + base
        assert compose(base, {"a": side, "b": side}) == side

    def test_shared_edit_and_independent_edit_apply_once(self):
        base = "# one\n# two\n# three\n# four\n"
        assert (
            compose(
                base,
                {
                    "a": "# ONE\n# two\n# three\n# four\n",
                    "b": "# ONE\n# two\n# three\n# FOUR\n",
                },
            )
            == "# ONE\n# two\n# three\n# FOUR\n"
        )

    def test_three_equal_proposers_are_input_order_independent(self):
        sides = {role: "# inserted\n" for role in ("a", "b", "c")}
        assert compose("", sides) == "# inserted\n"
        assert compose("", dict(reversed(list(sides.items())))) == "# inserted\n"

    def test_equal_operations_keep_all_proposers_in_a_real_conflict(self):
        with pytest.raises(CannotCompose) as caught:
            compose(
                "# base\n",
                {"alpha": "# equal\n", "bravo": "# equal\n", "charlie": "# rival\n"},
            )
        named = str(caught.value).split("edited by ")[1].split(" -- ")[0]
        assert set(named.split(", ")) == {"alpha", "bravo", "charlie"}

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
        """An `insert` opcode has `i1 == i2`, and a half-open overlap test is
        False for every empty base range, so a pure insert is the shape to pin."""
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

    def test_a_line_added_after_an_unterminated_paragraph_composes_with_an_edit_above(
        self,
    ):
        """A `raw_text` ends without a newline, so a line added after it must
        read as an insert, not as a rewrite of the last line: the edit on the
        first line and the added line are on different sentences."""
        base = "# one\n# two"
        sides = {
            "correct": "# ONE\n# two",
            "add": "# one\n# two\n# TODO: three",
        }
        assert compose(base, sides) == "# ONE\n# two\n# TODO: three"

    def test_a_line_added_right_after_an_edited_last_line_composes(self):
        """`mark-defects` T28: a correct on the paragraph's last sentence and
        a TODO added right after it. An insert at the edge of another side's
        rewrite has one order, the base's, so the two do not meet."""
        base = "# one\n# two"
        sides = {
            "correct": "# one\n# TWO",
            "add": "# one\n# two\n# TODO: three",
        }
        assert compose(base, sides) == "# one\n# TWO\n# TODO: three"

    def test_a_line_added_right_before_an_edited_line_lands_before_it(self):
        base = "# one\n# two\n"
        sides = {
            "correct": "# one\n# TWO\n",
            "add": "# one\n# INSERTED\n# two\n",
        }
        assert compose(base, sides) == "# one\n# INSERTED\n# TWO\n"

    def test_two_edits_on_adjacent_lines_compose(self):
        """Edits meet only where their changed words overlap, so rewrites of
        two adjacent lines compose."""
        base = "# one\n# two\n"
        sides = {"a": "# ONE\n# two\n", "b": "# one\n# TWO\n"}
        assert compose(base, sides) == "# ONE\n# TWO\n"

    def test_two_edits_on_different_words_of_one_sentence_compose(self):
        base = "# Alpha: one and two.\n"
        sides = {"a": "# Alpha: 1 and two.\n", "b": "# Alpha: one and 2.\n"}
        assert compose(base, sides) == "# Alpha: 1 and 2.\n"

    def test_two_edits_on_two_sentences_of_one_line_compose(self):
        base = "# Alpha: one. Beta: two."
        sides = {"a": "# Alpha: 1. Beta: two.", "b": "# Alpha: one. Beta: 2."}
        assert compose(base, sides) == "# Alpha: 1. Beta: 2."

    def test_two_edits_of_one_word_refuse(self):
        base = "# Alpha: one and two.\n"
        sides = {"a": "# Alpha: 1 and two.\n", "b": "# Alpha: uno and two.\n"}
        with pytest.raises(CannotCompose):
            compose(base, sides)

    def test_an_edit_overlapping_part_of_another_refuses(self):
        base = "# Alpha: one and two.\n"
        sides = {"a": "# Alpha: 1 and two.\n", "b": "# Alpha: two.\n"}
        with pytest.raises(CannotCompose):
            compose(base, sides)

    def test_two_lines_added_at_one_position_refuse(self):
        """Two inserts at one position have no order of their own."""
        base = "# one\n# two\n"
        sides = {"a": "# one\n# A\n# two\n", "b": "# one\n# B\n# two\n"}
        with pytest.raises(CannotCompose):
            compose(base, sides)

    def test_a_line_added_between_two_rewritten_lines_composes(self):
        """An insert meets only the edit it falls inside. Between two edited
        lines it falls inside neither, and the base gives its order."""
        base = "# one\n# two\n# three\n"
        sides = {
            "rewrite": "# ONE\n# TWO\n# three\n",
            "add": "# one\n# INSERTED\n# two\n# three\n",
        }
        assert compose(base, sides) == "# ONE\n# INSERTED\n# TWO\n# three\n"

    def test_words_added_inside_another_sides_rewritten_words_refuse(self):
        base = "# alpha beta gamma\n"
        sides = {"rewrite": "# x\n", "add": "# alpha new beta gamma\n"}
        with pytest.raises(CannotCompose):
            compose(base, sides)

    def test_an_unterminated_paragraph_stays_unterminated(self):
        base = "# one\n# two"
        assert compose(base, {"correct": "# ONE\n# two"}) == "# ONE\n# two"
