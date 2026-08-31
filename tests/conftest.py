"""The shadow suite: invariants derived from the CODE, not from `tests/`.

WHY IT EXISTS. Roy, 2026-08-25, after a night in which the existing suite passed
829 green while `verdicts.py`'s central check reported *"the sentence ruled on is not
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

    uv run pytest            1032 passed, 1 skipped, 3 xfailed, 480 subtests, ~2s

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

!! NEITHER THE VERDICTS NOR THE RECORD IS TOUCHED -- neither exists in `src/`,
only in `prototype/`, which does not run. Roy: *"There is code there none of it
is correct so testing it is solidifying wrong."* ! `desk/mark.py` is the
EXCEPTION, since 2026-08-28: `tests/test_mark.py` and `tests/test_mark_brief.py`
test it directly, once the port's own defect
(`TODO/the-ported-mark-does-not-fit-the-brief.md`) made it worth testing.
`desk/external_address.py` remains untouched here.

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

from comment_review.binder.binder import Binder  # noqa: E402
from comment_review.binder.page import page_for  # noqa: E402
from comment_review.machine.repo import sha_of  # noqa: E402
from comment_review.reading.addresser import cue_of, unflatten  # noqa: E402
from comment_review.reading.lexer import Paragraph, language_for  # noqa: E402


def build(text: str, name: str = "m.py"):
    """The page for this text, addressed as the repo would address it.

    ! `rel` IS PASSED, because `page_for` stamps addresses from it -- a page
    built without one carries none, and every assertion about a place would
    then be vacuous.

    ! THE SHA IS COMPUTED HERE, not read, because a test's text never came off
    a disk. `read_source` is what supplies it in the running system.
    """
    path = Path(name)
    lang = language_for(path)
    assert lang is not None, f"no language record for suffix {path.suffix!r}"
    return page_for(path, text, lang, rel=name, sha=sha_of(text))


def cue(paragraph) -> str:
    """The cue half of a paragraph's address -- `b3` -- or "" for a fence."""
    return (paragraph.address or "").split("@")[-1]


def by_cue(page) -> dict[str, Paragraph]:
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


#: A replacement that is legal in each series. A `c` carries its own separator
#: -- the compositor joins it to the code -- and an `a` carries its indentation.
#: ! SHARED, because the galley cases and the compositor cases set the same
#: places and a second copy is a second thing to keep current.
REPLACEMENT = {
    "a": '    """REPLACED."""',
    "b": "# REPLACED",
    "c": "  # REPLACED",
    "f": "#!/usr/bin/env REPLACED",
}


#: `bind()` has required `read_from` since `the-flow-assumes-every-role-reads-at-once`
#: T2. A page built by `build()` above is text handed straight to `page_for`, never
#: read off a census root, so there is no real root to name for it -- this stands in
#: for the tests below that exercise `bind()` in isolation and assert nothing about
#: `read_from` itself.
READ_FROM = {"root": "<synthetic>", "revise": 0}


def docket_from(flat: dict, binder: Binder) -> dict:
    """A nested docket from `{address: text}` plus the binder those addresses cite.

    !! A TEST-ONLY ADAPTER, and it exists so the chain's cases keep testing the
    CHAIN. Before 2026-08-26 the docket was one flat map and `proof_setter.run`
    took a binder alongside it, doing exactly what this does: split each address,
    `unflatten` its path against the binder's page paths, and look the sha up.
    That work moved INTO the docket; sixty cases that assert things about
    drafting, refusing and proving should not each be rewritten to say so.

    ! IT IS NOT WHAT PROVES THE FORMAT. `tests/test_docket.py` hand-writes the
    nested JSON and reads it back, so the shape has a witness that does not go
    through this function -- which is the point, since a fixture built by the
    same code it feeds can only agree with it.
    """
    paths = [p.path for p in binder.pages]
    shas = {p.path: p.sha for p in binder.pages}
    pages: dict[str, list[dict]] = {}
    for address, text in flat.items():
        addr = cue_of(address)
        rel = unflatten(str(addr.path), paths) or str(addr.path)
        pages.setdefault(rel, []).append({"cue": str(addr.cue), "text": text})
    return {
        "pages": [
            {"path": rel, "sha": shas.get(rel, ""), "alterations": alterations}
            for rel, alterations in sorted(pages.items())
        ]
    }


@pytest.fixture
def sample():
    """A fresh page over `SAMPLE`. Fresh, because the galley MUTATES a page."""
    return build(SAMPLE)
