"""Stage 3, inbound: the names by which a tracked file would cite a file under review.

`flows.referrers.files_naming` searches the tree for them.

The gather resolves what a comment cites. These names serve the other direction --
who cites the code being edited -- which is the half that decides the
`REFERENCE ONLY` list. Without it that list is assembled from memory, and a `target`
run has no diff to widen from at all.
"""

import ast
from pathlib import Path

# ! The exception tuples are IMPORTED. Each is bound to a NAME so no `except`
# clause here holds a tuple literal; `exceptions.py` carries that reason once.
from comment_review import exceptions
from comment_review.concordance.names import NAMED_DEFS


def tokens_for(path: Path, text: str) -> set[str]:
    """Every name by which prose elsewhere would refer to this file.

    Args:
        path: the file's repo-relative path.
        text: its contents, parsed for top-level names when it is Python.

    Returns:
        The stem, the posix path and each of its trailing suffixes, and the
        public top-level definitions. Underscored names are excluded: prose
        cites the public surface, and a private helper's name collides with
        every unrelated private helper spelled the same way. A name of two
        characters or fewer is left out: searched with `git grep -l -F` it
        matches nearly every tracked file.
    """
    out = {path.stem}
    parts = path.as_posix().split("/")
    for i in range(len(parts)):
        out.add("/".join(parts[i:]))
    if path.suffix.lower() in (".py", ".pyi"):
        try:
            tree = ast.parse(text)
        except exceptions.PARSE_ERRORS:
            # !! A file that will not parse yields its path and stem only, and
            # must still reach the length filter below -- an earlier `return`
            # here skipped it, so a two-character stem went to `git grep -l -F`
            # and matched nearly every tracked file. ! `tree = None`, not a bare
            # `pass`: this is not a loop, and falling through left `tree`
            # unbound, so the handler written for a mid-edit file crashed on one.
            tree = None
        for node in tree.body if tree is not None else ():
            if isinstance(node, NAMED_DEFS) and not node.name.startswith("_"):
                out.add(node.name)
    return {t for t in out if len(t) > 2}
