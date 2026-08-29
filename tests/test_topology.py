"""The topology file: a run's schedule of stages, as data.

! EXPECTATIONS HERE COME FROM `docs/superpowers/specs/2026-08-29-the-master-
proof-and-reconciliation-design.md` section 2, transcribed by hand -- never
from `topology.py` itself. The three fixtures under
`tests/fixtures/topologies/` are that section's own three topologies,
written out; `test_paths_fan_one_role_and_leave_the_others_whole` checks the
fan-out claim that section makes about `4a-then-4c`: block-context split two
ways, the others left whole.
"""

from pathlib import Path

from comment_review.desk.stages import Role
from comment_review.desk.topology import read

TOPOLOGIES = Path(__file__).parent / "fixtures" / "topologies"


def test_each_topology_in_the_spec_parses():
    for name in ("all-at-once", "sequential", "4a-then-4c"):
        stages, why = read((TOPOLOGIES / f"{name}.toml").read_text(encoding="utf-8"))
        assert why == "", f"{name}: {why}"
        assert stages


def test_paths_fan_one_role_and_leave_the_others_whole():
    # EXPECTATION FROM THE SPEC: block-context split two ways, the others not.
    stages, why = read((TOPOLOGIES / "4a-then-4c.toml").read_text(encoding="utf-8"))
    assert why == ""
    later = [s for s in stages if s.name == "4c"][0]
    fanned = [d for d in later.dispatches if d.role == Role.BLOCK_CONTEXT]
    assert len(fanned) == 2 and all(d.paths for d in fanned)
    others = [d for d in later.dispatches if d.role != Role.BLOCK_CONTEXT]
    assert others and all(d.paths == () for d in others)


def test_a_role_outside_the_closed_set_is_refused():
    stages, why = read(
        '[[stage]]\nname="x"\nkind="editorial"\nreads="original"\n'
        '[[stage.dispatch]]\nrole="not-a-role"\n'
    )
    assert stages == [] and "not-a-role" in why


def test_all_at_once_holds_one_stage_with_four_dispatches():
    # EXPECTATION FROM THE SPEC's table: "all four at once" -- 1 stage, 4
    # edit_copies (one dispatch per role, none fanned).
    stages, why = read((TOPOLOGIES / "all-at-once.toml").read_text(encoding="utf-8"))
    assert why == ""
    assert len(stages) == 1
    assert len(stages[0].dispatches) == 4
    assert {d.role for d in stages[0].dispatches} == set(Role)
    assert stages[0].reads == "original"


def test_sequential_holds_four_stages_each_reading_the_one_before():
    # EXPECTATION FROM THE SPEC's table: "pure sequential" -- 4 stages, 1
    # edit_copy each, each reading the revise the one before it pulled.
    stages, why = read((TOPOLOGIES / "sequential.toml").read_text(encoding="utf-8"))
    assert why == ""
    assert len(stages) == 4
    assert all(len(s.dispatches) == 1 for s in stages)
    assert [s.reads for s in stages] == ["original", "revise:1", "revise:2", "revise:3"]


def test_a_dispatch_with_no_paths_means_every_page():
    stages, why = read(
        '[[stage]]\nname="1"\nkind="editorial"\nreads="original"\n'
        '[[stage.dispatch]]\nrole="ownership-context"\n'
    )
    assert why == ""
    assert stages[0].dispatches[0].paths == ()


def test_reading_a_later_stage_is_refused():
    stages, why = read(
        '[[stage]]\nname="1"\nkind="editorial"\nreads="revise:2"\n'
        '[[stage.dispatch]]\nrole="block-context"\n'
        '[[stage]]\nname="2"\nkind="editorial"\nreads="original"\n'
        '[[stage.dispatch]]\nrole="module-context"\n'
    )
    assert stages == [] and "revise:2" in why


def test_reading_an_enriching_stage_is_refused_BY_NAME():
    # ! An enriching stage pulls no revise, so naming it in `reads` cannot be
    # quietly resolved to the previous editorial one.
    stages, why = read(
        '[[stage]]\nname="a"\nkind="enriching"\nreads="original"\n'
        '[[stage.dispatch]]\nrole="block-context"\n'
        '[[stage]]\nname="b"\nkind="editorial"\nreads="revise:a"\n'
        '[[stage.dispatch]]\nrole="module-context"\n'
    )
    assert stages == []
    assert "enriching" in why and "a" in why


def test_a_non_empty_carries_is_refused_with_a_reason():
    stages, why = read(
        '[[stage]]\nname="1"\nkind="editorial"\nreads="original"\ncarries=["0"]\n'
        '[[stage.dispatch]]\nrole="block-context"\n'
    )
    assert stages == [] and "carries" in why
