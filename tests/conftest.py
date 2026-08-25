"""The shadow suite: invariants derived from the CODE, not from `tests/`.

WHY IT EXISTS. Roy, 2026-08-25, after a night in which the existing suite passed
829 green while the join's central check reported *"the sentence ruled on is not
in <place>"* for EVERY finding: *"866 tests are likely garbage piling up with
maybe 50 good ones in the mix."* Three changes that night -- fences leaving the
census, eleven fields leaving the row, and a rename that broke every finding --
were noticed by ZERO tests each, because the fixtures were hand-authored in the
shape the code expected and moved only when someone remembered to move them.

! SO NOTHING HERE WAS COPIED FROM `tests/`, OR READ FROM IT. Every invariant
below was derived by reading the modules and by running them over real input to
see what they actually do. Where an assertion states a value, that value was
OBSERVED first.

!! IT IS THE SUITE NOW. It was built beside the old one as `shadow/`, run for a
night, and then swapped in -- Roy, 2026-08-25: *"Delete the old test suit put in
the new one."* The old suite is gone; `gates/` beside this is the part that
survived, because it asks a different question -- whether a GATE still bites,
over `scripts/` and the release rather than over the code under redesign.

    uv run pytest            779 passed, 3 xfailed, ~1.5s

! IT RUNS IN A TENTH OF THE TIME the old suite took, which is a consequence
rather than a goal: nothing here starts a subprocess to ask a question that can
be asked in-process.

=== WHAT IS IN SCOPE, AND WHAT IS DELIBERATELY NOT

Two chains, and they are INDEPENDENT. Roy, 2026-08-25: *"Reading -> binder.
Page -> galley -> compositor. The binder is not going through the galley."* The
workflow re-reads each page from disk on the results side, because it needs the
FULL page -- fences included -- and none of what a binder carries.

    reading -> binder     what an agent is handed
    page -> galley -> compositor    the write path, from a freshly read page

!! NOTHING TOUCHES THE DESK, THE VERDICTS OR THE JOIN. Roy: *"There is code
there none of it is correct so testing it is solidifying wrong."*

! AND THE FRONT-MATTER/`b` COLLISION IS OFF LIMITS -- a file whose front matter
is not on line 1. It is a known normalisation, ruled a sacrifice rather than a
defect, and a test over it would pin the sacrifice.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
#: The package itself. `gates/` sweeps it -- the files that ship are the files
#: in `src/`, and `plugins/` is a built copy checked separately by the build
#: gate.
PKG = SRC / "comment_review"

sys.path.insert(0, str(SRC))

from comment_review.binder.page import page_for  # noqa: E402
from comment_review.reading.lexer import language_for  # noqa: E402


def build(text: str, name: str = "m.py"):
    """The page for this text, addressed as the repo would address it.

    ! `rel` IS PASSED, because `page_for` stamps addresses from it -- a page
    built without one carries none, and every assertion about a place would
    then be vacuous.
    """
    path = Path(name)
    return page_for(path, text, language_for(path), rel=name)


def cue(paragraph) -> str:
    """The cue half of a paragraph's address -- `b3` -- or "" for a fence."""
    return (paragraph.address or "").split("@")[-1]


def by_cue(page) -> dict[str, object]:
    """Every addressed place on the page, keyed by its cue."""
    return {cue(b): b for b in page.paragraphs if b.address}


def occupied(page) -> list[tuple[int, int]]:
    """The line spans every paragraph stands on, in file order.

    ! An EMPTY PLACE stands on nothing and carries `None` for both ends, so it
    contributes no span -- which is what makes the partition below checkable.
    """
    spans = [
        (b.original_start, b.original_end)
        for b in page.paragraphs
        if b.original_start is not None and b.original_end is not None
    ]
    return sorted(spans)


#: One ordinary Python page carrying a FILLED place in every series and an
#: ABSENT one in every series. Front matter is on line 1, which keeps the `f`/`b`
#: collision out of scope.
SAMPLE = (
    "#!/usr/bin/env python\n"
    '"""Doc."""\n'
    "\n"
    "\n"
    "# note\n"
    "def f(x):\n"
    '    """Has one."""\n'
    "    return x + 1  # beside\n"
    "\n"
    "\n"
    "def g(y):\n"
    "    return y\n"
)


@pytest.fixture
def sample():
    """A fresh page over `SAMPLE`. Fresh, because the galley MUTATES a page."""
    return build(SAMPLE)
