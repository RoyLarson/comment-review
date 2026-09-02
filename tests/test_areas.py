"""The areas import in one direction, and nothing reaches across.

Roy, 2026-08-31, in two sentences: *"The flows can reach into the other
containers to either create them or have them create themselves. This keeps
things from having import circles and keeps a single definition for what a thing
is."* And the rule those serve: *"No direct coupling inside of ends and middle,
flows are neither they run the steps."*

    READ END    binder                  may import a LEAF
    MIDDLE      desk                    may import a LEAF
    WRITE END   docket, results         may import a LEAF
    NEITHER     flows, commands         anything -- they run the steps
    LEAF        machine, reading,       nothing above them
                concordance

!! THE QUIET HALF IS WHAT THIS CHECKS, NOT THE LOUD ONE. A cycle announces
itself at import, and this tree has none -- measured 2026-08-31 by walking every
`ImportFrom`. The failure with no symptom is the DEFINITION: a module reaching
across has to know the other area's rules, so the rules end up stated twice and
one copy goes stale.

!! IT ASSERTS AN EXACT SET, NOT AN EMPTY ONE, BECAUSE THREE CROSSINGS ARE STILL
OPEN. A test demanding zero would fail for reasons this branch is not fixing,
and would then be relaxed rather than read -- which `docs/conventions.md` names
as the one crossing this repo has no tolerance for. Naming them makes a NEW
crossing fail while an old one stays visible and countable.

! IT IS A `backend` TEST DESPITE READING LIKE A GATE. `docs/lanes.md` files a
test under the lane that owns what it ASKS, and this asks whether the Python's
own areas hold -- not whether a release still installs. `tests/gates/` is
`systems`'.
"""

import ast

import pytest
from conftest import ROOT

SRC = ROOT / "src" / "comment_review"

#: Each area, and the areas it may NOT name. A LEAF is absent because it may
#: import nothing above it and names no area at all; `flows` and `commands` are
#: absent because they may reach anywhere -- they run the steps.
FORBIDDEN = {
    "binder": ("desk", "docket", "results"),
    "desk": ("binder", "docket", "results"),
    "docket": ("binder", "desk", "results"),
    "results": ("binder", "desk", "docket"),
}

#: The crossings that EXIST and are not yet repaired, measured 2026-08-31 and
#: recorded in `docs/conventions.md`. Each is a real defect; this set is what
#: keeps them visible rather than asserted away.
#:
#: !! A ROW LEAVES THIS SET WHEN THE IMPORT GOES, NEVER TO MAKE A TEST PASS.
#: `desk/collator.py -> comment_review.docket.docket` was the fourth and left at
#: `P55`: the middle no longer builds the write end's artifact, because
#: `flows/revise.py::docket_of` does.
KNOWN = {
    # MIDDLE -> READ END. `desk/collator.py` takes a `Binder` as a PARAMETER and
    # never builds one, which is still the middle knowing the read end's
    # artifact. What it needs is a set of addresses and a map of base texts,
    # which the FLOW can derive and hand over.
    "desk/collator.py: comment_review.binder.binder",
    # MIDDLE -> READ END. `_read_from_problem` is PRIVATE to `binder` while
    # `read_from` sits on a binder, on every `edit_copy` and on a `master_proof`
    # -- one definition, reachable by only one of its three owners.
    "desk/containers.py: comment_review.binder.binder",
    # WRITE END -> READ END. `results/compositor.py` reads `Page` and `page_for`.
    "results/compositor.py: comment_review.binder.page",
}


def crossings(forbidden: dict | None = None) -> set[str]:
    """Every import a module makes into an area that module may not name."""
    found = set()
    for area, may_not in (forbidden or FORBIDDEN).items():
        for path in sorted((SRC / area).rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom) or not node.module:
                    continue
                parts = node.module.split(".")
                if len(parts) > 1 and parts[0] == "comment_review":
                    if parts[1] in may_not:
                        found.add(f"{area}/{path.name}: {node.module}")
    return found


@pytest.fixture(scope="module")
def found() -> set[str]:
    """`crossings()` over the real `FORBIDDEN`, computed once for this file.

    ! IT PARSES 19 FILES, and two tests ask the same question of them. The walk
    is pure -- same tree, same map, same answer -- so running it per test was an
    exact duplication of a pure function's input rather than two measurements.
    The witness below cannot share it: it passes a different map, which is the
    whole point of it.
    """
    return crossings()


def test_no_area_reaches_across_except_the_three_still_open(found):
    assert found == KNOWN


def test_the_middle_no_longer_builds_the_write_ends_artifact(found):
    """`P55`. The one crossing this branch removed, asserted by name so a
    re-introduction fails here rather than only widening the set above."""
    assert not any(
        one.startswith("desk/") and "comment_review.docket" in one for one in found
    )


def test_the_walker_can_see_a_crossing():
    """!! THE CHECK'S OWN WITNESS -- `docs/gates.md`: *"does the check pass" is
    not the question; "could the check fail" is.* Run over a map that forbids an
    import the tree really makes, the walker must report it. Without this, a
    walker that silently read no files would pass every assertion above.
    """
    # `desk` legitimately imports the `reading` LEAF; forbidding it here proves
    # the walk reaches real `ImportFrom` nodes.
    assert crossings({"desk": ("reading",)}), "the walker found nothing at all"


@pytest.mark.parametrize("area", sorted(FORBIDDEN))
def test_every_area_in_the_map_exists(area):
    """! A TYPO IN `FORBIDDEN` WOULD MAKE THIS CHECK ASK LESS AND STILL PASS,
    because `rglob` over a missing directory yields nothing."""
    assert (SRC / area).is_dir(), f"{area} is not an area of src/comment_review"
