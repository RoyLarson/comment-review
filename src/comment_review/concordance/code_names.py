"""Every name the tree defines, harvested from the AST.

! It answers the obituary question. `block-context`'s remit includes a symbol, file,
test or flag that exists nowhere; `flows.gather._name_corpus` builds that corpus from
these harvests, and its docstring says why the names come from the AST.

It also words the corpus's gap rows: `no_harvester` for a file no harvester reads, and
`WALKED_TREE_ROW` for a corpus built without git's list of tracked files.
"""

import ast
from pathlib import Path

from comment_review.concordance.names import NAMED_DEFS, SYMBOLISH
from comment_review.reading.language import INSTALLED_REGISTRY

# The two gaps in the name corpus that are not read failures, named so a caller
# could tell them apart from one, though none does. A `NO_HARVESTER` row reads
# like a read failure's -- `<path> (<reason>)` -- and a reporting caller that
# treated all of them as unreadable files would tell a polyglot repo its files
# "could not be read" and have the reader wait for a list that can never empty.
NO_HARVESTER = "no name harvester for"
WALKED_TREE = "name corpus built by WALKING the tree"

#: The gap row for a corpus built without git's list of tracked files.
WALKED_TREE_ROW = (
    f"{WALKED_TREE} (not a git checkout, or git unavailable) -- "
    "untracked or vendored code may mask an obituary"
)


def no_harvester(path: Path) -> str | None:
    """The gap row for a file no harvester reads, or None for a Python file.

    ! A non-Python file is a known hole, reported as one. Parsed as Python it
    came back `a.go (SyntaxError)`, which reads as "your file is malformed" and
    sends a reviewer after an invented defect. Liveness in these languages
    needs its own harvester; this names the gap until there is one.
    """
    definition = INSTALLED_REGISTRY.for_path(path)
    if definition is not None and definition.language == "python":
        return None
    if definition is not None:
        name = definition.language
    elif INSTALLED_REGISTRY.is_freeform(path):
        name = "a freeform file"
    else:
        name = "unknown"
    return f"{path.as_posix()} ({NO_HARVESTER} {name})"


def names_in(path: Path, text: str) -> set[str]:
    """Every name one Python file defines or references, harvested from its AST.

    Args:
        path: the file, for its stem and for whether it is a test.
        text: its contents.

    Returns:
        The stem, every defined, bound or referenced, attribute, argument and
        imported name, and outside the tests every string constant shaped
        like a symbol.

    Raises:
        SyntaxError, ValueError: `text` does not parse.
    """
    tree = ast.parse(text)
    names = {path.stem}
    harvest_constants = not (path.name.startswith("test_") or "tests" in path.parts)
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
    return names
