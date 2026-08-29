"""`differences.unified`: a per-page diff, and nothing else.

! `apply_unified` BELOW IS TEST-ONLY, not a shipped applier -- `differences.py`
renders and nothing reverses it. It exists so this suite's own pass criterion
(`docs/plans/0.2.4-the-mark-and-the-collator.md` T5.2: "the rendered diff
applies to the original") is a CHECKED literal round trip rather than a read
of the diff's text. It is local to this file because nothing else needs it --
`tests/helpers.py`'s own header reserves that file for inputs, not assertions.
"""

import re
from pathlib import Path

from comment_review.results.differences import unified

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
