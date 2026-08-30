"""The containers parse what the real chain builds, and refuse what it cannot.

! INPUTS ARE REAL -- a binder from `bind` over a real tree, seeded by the real
`seed`, gathered by the real `gather`. A literal appears only where MALFORMED
is the input, which is what the refusals are about.
"""

from helpers import a_small_real_tree, binder_of

from comment_review.desk.containers import (
    EditCopy,
    MasterProof,
    Sheet,
    parse_edit_copy,
    parse_master_proof,
    parse_sheet,
)
from comment_review.desk.proof import gather
from comment_review.flows.distribute import seed


def a_real_copy(tmp_path, role="block-context"):
    return seed(binder_of(a_small_real_tree(tmp_path), 0), role)


class TestWhatTheChainBuilds:
    def test_an_edit_copy_seed_built_parses(self, tmp_path):
        copy, why = parse_edit_copy("copy 1", a_real_copy(tmp_path))
        assert why == []
        assert isinstance(copy, EditCopy)
        assert copy.role == "block-context"
        assert copy.sheets
        assert all(isinstance(s, Sheet) for s in copy.sheets)

    def test_every_sheet_names_a_page_the_binder_carried(self, tmp_path):
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        copy, why = parse_edit_copy("copy 1", seed(binder, "block-context"))
        assert why == []
        assert copy is not None
        carried = {p["path"] for p in binder["pages"]}
        assert {s.path for s in copy.sheets} == carried

    def test_a_master_proof_gather_built_parses(self, tmp_path):
        binder = binder_of(a_small_real_tree(tmp_path), 0)
        copies = [seed(binder, "block-context"), seed(binder, "function-context")]
        proof, why = parse_master_proof("4c", gather("4c", copies))
        assert why == []
        assert isinstance(proof, MasterProof)
        assert proof.stage == "4c"
        assert [c.role for c in proof.edit_copies] == [
            "block-context",
            "function-context",
        ]

    def test_the_chiefs_copy_parses_as_an_ORDINARY_edit_copy(self, tmp_path):
        """`decision-log.md Vocabulary: #30`: the chief's copy is the same
        shape. There is no second type and no second parse."""
        copy = a_real_copy(tmp_path)
        copy["role"] = "copy-chief"
        got, why = parse_edit_copy("the chief's", copy)
        assert why == []
        assert got is not None
        assert got.role == "copy-chief"


class TestWhatItRefuses:
    def test_a_sheet_that_is_not_an_object(self):
        sheet, why = parse_sheet("sheet 1", "m.py")
        assert sheet is None
        assert "must be an object" in why[0]

    def test_a_sheet_with_no_path(self):
        sheet, why = parse_sheet("sheet 1", {"sha": "abc", "marks": []})
        assert sheet is None
        assert "`path`" in why[0]

    def test_a_sheet_whose_marks_are_not_a_list(self):
        sheet, why = parse_sheet("sheet 1", {"path": "m.py", "marks": {}})
        assert sheet is None
        assert "`marks` list" in why[0]

    def test_an_edit_copy_with_no_role(self, tmp_path):
        copy = a_real_copy(tmp_path)
        del copy["role"]
        got, why = parse_edit_copy("copy 1", copy)
        assert got is None
        assert "`role`" in why[0]

    def test_an_edit_copy_with_an_emptied_read_from(self, tmp_path):
        """`decision-log.md Process: #34`: the field exists so a later role can
        know it holds a REVISE. An empty one is the ambiguity it was added to
        remove."""
        copy = a_real_copy(tmp_path)
        copy["read_from"] = {}
        got, why = parse_edit_copy("copy 1", copy)
        assert got is None
        assert "read_from" in why[0]

    def test_an_edit_copy_reports_EVERY_bad_sheet_not_just_the_first(self, tmp_path):
        copy = a_real_copy(tmp_path)
        copy["sheets"] = [{"sha": "a"}, {"sha": "b"}]
        got, why = parse_edit_copy("copy 1", copy)
        assert got is None
        assert len(why) == 2

    def test_a_master_proof_whose_edit_copies_are_not_a_list(self):
        proof, why = parse_master_proof("4c", {"stage": "4c", "edit_copies": {}})
        assert proof is None
        assert "`edit_copies` list" in why[0]

    def test_a_master_proof_whose_read_from_disagrees_with_the_first_copy(
        self, tmp_path
    ):
        """`desk.proof.gather` refuses this same disagreement with
        `MismatchedRoot` before a master_proof is ever built -- a proof
        reaching `parse_master_proof` with one is malformed, not merely
        unusual."""
        binder = binder_of(a_small_real_tree(tmp_path), 0)
        proof = gather("4c", [seed(binder, "block-context")])
        proof["read_from"] = {"root": "somewhere else", "revise": 99}
        got, why = parse_master_proof("4c", proof)
        assert got is None
        assert "disagrees with the first edit_copy's" in why[0]

    def test_a_master_proof_whose_read_from_is_malformed(self, tmp_path):
        """The same shape check `_read_from_problem` runs for an edit_copy,
        reused here for the master_proof's own `read_from` field."""
        binder = binder_of(a_small_real_tree(tmp_path), 0)
        proof = gather("4c", [seed(binder, "block-context")])
        proof["read_from"] = {"root": proof["read_from"]["root"]}
        got, why = parse_master_proof("4c", proof)
        assert got is None
        assert "`revise`" in why[0]

    def test_a_master_proof_WITH_NO_EDIT_COPIES_still_parses(self):
        """`desk.proof.gather`'s own contract: an empty `edit_copies` gathers
        to `read_from={}`, since there is no first copy to take it from --
        that is not the disagreement or malformed shape the two cases above
        refuse."""
        got, why = parse_master_proof("4c", {"stage": "4c", "edit_copies": []})
        assert why == []
        assert got is not None
        assert got.read_from == {}


class TestANullFieldIsAbsentNotTheWordNone:
    """`.get(key, "")` DEFAULTS ONLY WHEN THE KEY IS ABSENT -- a key present
    and holding `None` returns `None` from `.get`, and `str(None)` is the
    four-character word "None". The same class of defect as a null
    `verbatim` rendering as the word "None" in `results/verdicts.py`."""

    def test_a_null_sha(self):
        sheet, why = parse_sheet("sheet 1", {"path": "m.py", "sha": None, "marks": []})
        assert why == []
        assert sheet is not None
        assert sheet.sha == ""

    def test_a_null_stage(self):
        proof, why = parse_master_proof("4c", {"stage": None, "edit_copies": []})
        assert why == []
        assert proof is not None
        assert proof.stage == ""


class TestTheShape:
    def test_no_container_declares_a_field_nothing_reads(self):
        """!! `P21`'s own verify. `decision-log.md Vocabulary: #30` proposed a
        `rounds` field; `P7` is SUPERSEDED by `Process: #51`, which struck
        carried round state as guarding an accident that cannot happen. A field
        nothing reads is what let `Instruction` be an enum the wire never
        carried."""
        import dataclasses

        for kind in (Sheet, EditCopy, MasterProof):
            names = {f.name for f in dataclasses.fields(kind)}
            assert "rounds" not in names, kind.__name__
