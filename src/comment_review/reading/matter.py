"""The file's own matter: the prose that opens a file and the prose that closes it.

Every reader asks this one rule which of its runs are `Kind.MATTER`, and assigns
the kind itself. What a reader hands in is its own: the line the matter may
open on, the lines that are prose, the lines of its module and closing
docstrings, and whether the file holds code. The rule learns no language.

A PROSE line holds a comment that is not documentation and stands on its line
alone, and holds no code. Every line such a comment stands on is prose, a blank
line inside a delimited comment included, so a comment is never cut. A fully
empty line between two comments is not prose, and neither is a line of a
doc-marked run, so documentation ends a walk over prose lines. The module and
closing docstrings are never matter. Other documentation is matter only where
it lies inside a back matter below a closing docstring or in a file with no
code, the two cases that take every line and not only prose lines.

Front matter with a module docstring is every line from the opening line down
to that docstring, whatever blank lines lie between. With none, it is the prose
lines from the opening line down to the first line that is not prose.

Back matter with a closing docstring is every line below it. With none, it is
the prose lines from the file's last line upward to the first line that is not
prose.

In a file with no code, everything below the module docstring -- or below the
front matter, with no docstring -- is one back matter, documentation inside it
included.

Back matter reaches the last line: a last line that is not prose, blank or
documentation, leaves none, whatever stands above it.

A lone doc over a declaration is the declaration's, so a reader does not name
it as the module docstring.
"""

from collections.abc import Collection
from dataclasses import dataclass
from itertools import pairwise


@dataclass(frozen=True)
class Matter:
    """Where a file's front and back matter lie, as line ranges."""

    front: range
    back: range

    def parts(
        self, start: int, end: int, held: Collection[int]
    ) -> list[tuple[int, int, bool]]:
        """The run on lines `start..end`, cut at the matter's edges.

        Each part is `(start, end, is_matter)`, trimmed to its first and last
        `held` line -- a line the run has a comment on; a part holding none is
        dropped. A run inside one range, or in neither, is one part.
        """
        edges = sorted(
            {start, end + 1}
            | {at for at in (self.front.stop, self.back.start) if start < at <= end}
        )
        parts = []
        for first, stop in pairwise(edges):
            lines = [n for n in range(first, stop) if n in held]
            if not lines:
                continue
            matter = first in self.front or first in self.back
            parts.append((lines[0], lines[-1], matter))
        return parts


def file_matter(
    total: int,
    opens: int,
    prose: Collection[int],
    *,
    module_doc: range | None = None,
    closing_doc: range | None = None,
    codeless: bool = False,
) -> Matter:
    """The front and back matter of a file of `total` lines.

    Args:
        total: the file's line count.
        opens: the first line matter may open on -- line 1, or the line below
            a line the reader keeps as the file's own and not as prose, such as
            a shebang that is not a comment.
        prose: the prose lines, as the module docstring defines them.
        module_doc: the lines of the docstring that opens the file's code.
        closing_doc: the lines of the docstring that ends the file's code.
        codeless: the file holds no line of code; `module_doc` does not count
            as one.
    """
    if module_doc is not None:
        front = range(opens, module_doc.start)
    else:
        line = opens
        while line in prose:
            line += 1
        front = range(opens, line)
    if closing_doc is not None:
        below = closing_doc.stop
    elif codeless:
        below = front.stop if module_doc is None else module_doc.stop
    else:
        below = total
        while below >= front.stop and below in prose:
            below -= 1
        below += 1
    if total not in prose:
        below = total + 1
    return Matter(front, range(below, total + 1))
