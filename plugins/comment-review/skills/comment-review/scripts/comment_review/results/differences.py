"""Renders the difference between two texts. Rules on nothing.

One module, two renderings -- `unified` is the first, and T5.1's `diff3`
renderer (base plus both edits) lands here next. Neither decides settle or
escalate; `decision-log.md Vocabulary: #11` holds the collator to that same
rule, and this module is held to it too.

!! NO GIT PROCESS. A revise root is a temp copy `flows.revise.pull` made and
need not be a repo -- `difflib.unified_diff` reads two strings, not two
commits.
"""

import difflib


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
