"""The file's own matter: the prose that opens a file and the prose that closes it.

Every reader asks this one rule which of its runs are `Kind.MATTER`, and assigns
the kind itself. What a reader hands in is its own: the line the matter may
open on, and the lines that are prose.

A PROSE line holds a comment that is not documentation and stands on its line
alone, and holds no code. Every line such a comment stands on is prose, a blank
line inside a delimited comment included, so a comment is never cut. A fully
empty line between two comments is not prose, and neither is a line of a
doc-marked run: documentation at either end of a file is the module's
docstring, never its matter.

Front matter is the prose lines from the opening line down to the first line
that is not prose. Back matter is the same rule read from the file's last line
upward. A file that is prose throughout is front matter alone.
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


def file_matter(total: int, opens: int, prose: Collection[int]) -> Matter:
    """The front and back matter of a file of `total` lines.

    Args:
        total: the file's line count.
        opens: the first line matter may open on -- line 1, or the line below
            a line the reader keeps as the file's own and not as prose, such as
            a shebang that is not a comment.
        prose: the prose lines, as the module docstring defines them.
    """
    line = opens
    while line in prose:
        line += 1
    front = range(opens, line)
    line = total
    while line >= front.stop and line in prose:
        line -= 1
    return Matter(front, range(line + 1, total + 1))
