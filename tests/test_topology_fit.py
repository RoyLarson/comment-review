"""`flows/topology.py::fit`: a topology fits a binder, or says which way it does not.

`decision-log.md Process: #55` puts the check in a command with a repo, and `#100`
narrows it to the design's two fan-out guards: a page two shards of one role claim,
and a page no shard of a role reaches. A glob that matches no page is not a fault.
"""

from helpers import a_binder_over

from comment_review.desk.topology import read
from comment_review.flows.topology import fit

TWO_PAGES = {"a.py@a0": "Doc for a.", "b.py@a0": "Doc for b."}


def _stages(toml: str):
    stages, why = read(toml)
    assert not why, why
    return stages


def test_a_topology_that_covers_every_page_once_fits():
    stages = _stages("""
[[stage]]
name = "4c"
kind = "editorial"
  [[stage.dispatch]]
  role = "block-context"
  paths = ["a.py"]
  [[stage.dispatch]]
  role = "block-context"
  paths = ["b.py"]
  [[stage.dispatch]]
  role = "module-context"
""")
    assert fit(stages, a_binder_over(TWO_PAGES)) == []


def test_a_glob_matching_no_page_is_not_a_misfit_when_every_page_is_covered():
    # ! `Process: #100`: an empty glob is not a fault. The agent that wrote it
    # reads the result and modifies; only a page nobody covers is refused.
    stages = _stages("""
[[stage]]
name = "4c"
kind = "editorial"
  [[stage.dispatch]]
  role = "block-context"
  paths = ["a.py", "zzz/*.py"]
  [[stage.dispatch]]
  role = "block-context"
  paths = ["b.py"]
""")
    assert fit(stages, a_binder_over(TWO_PAGES)) == []


def test_a_page_no_dispatch_covers_is_UNCOVERED_and_names_the_page_and_the_globs():
    stages = _stages("""
[[stage]]
name = "4c"
kind = "editorial"
  [[stage.dispatch]]
  role = "block-context"
  paths = ["a.py", "zzz/*.py"]
""")
    misfits = fit(stages, a_binder_over(TWO_PAGES))
    assert [m.kind for m in misfits] == ["uncovered"]
    assert misfits[0].stage == "4c"
    assert "b.py" in misfits[0].detail
    # ! P33: the message names the globs, so the writer of `zzz/*.py` sees it.
    assert "zzz/*.py" in misfits[0].detail


def test_a_page_two_dispatches_of_one_role_claim_is_an_OVERLAP_misfit():
    stages = _stages("""
[[stage]]
name = "4c"
kind = "editorial"
  [[stage.dispatch]]
  role = "block-context"
  paths = ["a.py", "b.py"]
  [[stage.dispatch]]
  role = "block-context"
  paths = ["b.py"]
""")
    misfits = fit(stages, a_binder_over(TWO_PAGES))
    assert [m.kind for m in misfits] == ["overlap"]
    assert "b.py" in misfits[0].detail


def test_every_stage_is_checked_and_each_misfit_names_its_stage():
    stages = _stages("""
[[stage]]
name = "4a"
kind = "editorial"
  [[stage.dispatch]]
  role = "ownership-context"
  paths = ["a.py"]

[[stage]]
name = "4c"
kind = "editorial"
reads = "revise:4a"
  [[stage.dispatch]]
  role = "block-context"
  paths = ["nowhere.py"]
""")
    kinds = sorted((m.stage, m.kind) for m in fit(stages, a_binder_over(TWO_PAGES)))
    assert kinds == [("4a", "uncovered"), ("4c", "uncovered")]
