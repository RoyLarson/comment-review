"""The containers parse what the real chain builds, and refuse what it cannot.

! INPUTS ARE REAL -- a binder from `bind` over a real tree, seeded by the real
`seed`, gathered by the real `gather`. A literal appears only where MALFORMED
is the input, which is what the refusals are about.
"""

from dataclasses import fields

import pytest
from helpers import a_clean, a_small_real_tree, binder_of, returned

from comment_review.desk.containers import (
    EditCopy,
    MasterProof,
    Sheet,
)
from comment_review.desk.proof import gather
from comment_review.flows.distribute import seed


def a_real_copy(tmp_path, role="block-context"):
    return seed(binder_of(a_small_real_tree(tmp_path), 0), role)


class TestTheWriteHalfLivesWithTheRead:
    """`Process: #64`. The keys come from the dataclass, not from a literal.

    ! THESE READ THE FIELD NAMES OFF THE CLASS. Asserting the literal key names
    would pass a rename that broke `seed` and the dataclass together, which is
    the pair this exists to keep from drifting apart.
    """

    def test_a_sheet_is_written_with_every_WIRE_field_the_class_declares(self):
        """!! IT ASKED FOR EVERY DECLARED FIELD UNTIL `P51`, and two of
        `Sheet`'s are now off the wire. `unruled` and `refused` are what the
        parse MADE of entries that are not marks, so no producer writes them --
        the pair this guards is `seed` against the WIRE shape, and demanding
        them would make `Sheet.seed` impossible to write.

        ! THE METADATA IS READ HERE RATHER THAN A LIST OF NAMES, for the same
        reason the class's fields were: a literal would pass a rename that
        broke `seed` and the declaration together.
        """
        row = Sheet.seed(path="m.py", sha="abc", marks=[])
        wire = {f.name for f in fields(Sheet) if f.metadata.get("wire", True)}
        assert set(row) == wire
        assert wire < {f.name for f in fields(Sheet)}, "some field must be off the wire"

    def test_an_edit_copy_is_written_with_every_field_the_class_declares(self):
        row = EditCopy.seed(role="block-context", read_from={"root": "."}, sheets=[])
        assert set(row) == {f.name for f in fields(EditCopy)}

    def test_a_master_proof_is_written_with_every_WIRE_field_the_class_declares(self):
        """`turns` and `determined` are off the wire since `Process: #87`: a fold
        writes them later, so `seed` -- which writes what `gather` takes from a
        copy -- cannot. Same rule as the sheet's `unruled` and `refused`."""
        row = MasterProof.seed(stage="4c", read_from={}, edit_copies=[])
        wire = {f.name for f in fields(MasterProof) if f.metadata.get("wire", True)}
        assert set(row) == wire
        assert wire < {f.name for f in fields(MasterProof)}, (
            "some field must be off the wire"
        )

    def test_what_seed_writes_is_what_parse_reads_back_for_a_FILLED_copy(
        self, tmp_path
    ):
        """The round trip, over the real tree rather than over a literal.

        !! IT RAN OVER A SEEDED COPY UNTIL `P51` AND CANNOT NOW, which is the
        asymmetry the class docstring states. A seeded copy's entries are all
        UNTOUCHED, so the parse sorts every one into `unruled` and `marks` comes
        back empty -- re-seeding from that writes no entries at all. The inverse
        holds for a copy whose entries RULED, which is what this drives, and the
        case it stopped covering is the test below.
        """
        wire = a_real_copy(tmp_path)
        for sheet in wire["sheets"]:
            for entry in sheet["marks"]:
                entry.update(a_clean(entry["address"]))
        copy, why = EditCopy.deserialize("copy 1", wire)
        assert why == []
        assert copy is not None
        assert any(sheet.marks for sheet in copy.sheets), "nothing ruled to trip on"
        again, why = EditCopy.deserialize("copy 1", copy.serialize())
        assert why == []
        assert again == copy

    def test_a_SEEDED_copy_comes_back_as_unruled_addresses_and_no_marks(self, tmp_path):
        """The asymmetry, asserted rather than left for someone to trip on.

        ! A SEEDED COPY IS THE ONE A ROLE IS HANDED, so this is not an edge
        case -- it is every copy before anyone writes in it. `Process: #66`
        makes a seeded mark an empty FORM, and an empty form is not a `Mark`;
        the parse says so by putting its address in `unruled`.
        """
        copy, why = EditCopy.deserialize("copy 1", a_real_copy(tmp_path))
        assert why == []
        assert copy is not None
        assert not any(sheet.marks for sheet in copy.sheets)
        assert not any(sheet.refused for sheet in copy.sheets)
        seeded = {a for sheet in copy.sheets for a in sheet.unruled}
        assert seeded, "a seeded copy carries the places it was seeded with"
        # ! AND THE WIRE IT WRITES BACK IS EMPTY OF ENTRIES, which is what makes
        # this lossy: the addresses left through `unruled`, not through `marks`.
        assert all(not s["marks"] for s in copy.serialize()["sheets"])


class TestWhatTheChainBuilds:
    def test_an_edit_copy_seed_built_parses(self, tmp_path):
        copy, why = EditCopy.deserialize("copy 1", a_real_copy(tmp_path))
        assert why == []
        assert isinstance(copy, EditCopy)
        assert copy.role == "block-context"
        assert copy.sheets
        assert all(isinstance(s, Sheet) for s in copy.sheets)

    def test_every_sheet_names_a_page_the_binder_carried(self, tmp_path):
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        copy, why = EditCopy.deserialize("copy 1", seed(binder, "block-context"))
        assert why == []
        assert copy is not None
        carried = {p.path for p in binder.pages}
        assert {s.path for s in copy.sheets} == carried

    def test_a_master_proof_gather_built_parses(self, tmp_path):
        """! THE ROUND TRIP, NOT A PARSE OF A DICT, since `P42`. `gather`
        RETURNS a `MasterProof`, so what is read back here is that container's
        own `serialize` -- which is the stronger claim: the write half and the
        read half agree over the real producer."""
        binder = binder_of(a_small_real_tree(tmp_path), 0)
        copies = [
            returned(seed(binder, "block-context")),
            returned(seed(binder, "function-context")),
        ]
        proof, why = MasterProof.deserialize("4c", gather("4c", copies).serialize())
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
        got, why = EditCopy.deserialize("the chief's", copy)
        assert why == []
        assert got is not None
        assert got.role == "copy-chief"


class TestAnEmptyProofStillHoldsItsHeader:
    """`_read_from_problem` ran only `if copies:`, so a proof carrying no copies
    admitted any `read_from` at all.

    !! MEASURED 2026-08-30: all six values below returned `problems == []`, and
    the two dict-shaped ones were carried into `MasterProof.read_from`
    VERBATIM -- which are precisely the two `desk/collator.py:467-470` records
    as the reason this helper was reused instead of a hand-rolled
    `isinstance(..., dict) and truthy`. The validator had re-acquired the defect
    its own comment exists to explain.
    """

    @pytest.mark.parametrize("junk", ["oops", None, 7, [], {"root": 7}, {"junk": 1}])
    def test_an_empty_proof_still_holds_its_read_from_to_a_shape(self, junk):
        _, problems = MasterProof.deserialize(
            "p", {"stage": "4c", "edit_copies": [], "read_from": junk}
        )
        assert problems != []

    def test_an_empty_proof_with_an_empty_read_from_is_still_admitted(self):
        """`gather` itself produces this shape -- the docstring's reasoning for
        admitting `{}` was sound, and only the other five values were not."""
        parsed, problems = MasterProof.deserialize(
            "p", {"stage": "4c", "edit_copies": [], "read_from": {}}
        )
        assert problems == []
        assert parsed is not None
        assert parsed.read_from == {}

    def test_what_gather_writes_for_no_copies_still_parses(self):
        """The round trip, so the admission above is measured against the real
        producer rather than against a literal that agrees with it."""
        parsed, problems = MasterProof.deserialize("4c", gather("4c", []).serialize())
        assert problems == []
        assert parsed is not None


class TestWhatItRefuses:
    def test_a_sheet_that_is_not_an_object(self):
        sheet, why = Sheet.deserialize("sheet 1", "m.py")
        assert sheet is None
        assert "must be an object" in why[0]

    def test_a_sheet_with_no_path(self):
        sheet, why = Sheet.deserialize("sheet 1", {"sha": "abc", "marks": []})
        assert sheet is None
        assert "`path`" in why[0]

    def test_a_sheet_whose_marks_are_not_a_list(self):
        sheet, why = Sheet.deserialize("sheet 1", {"path": "m.py", "marks": {}})
        assert sheet is None
        assert "`marks` list" in why[0]

    def test_an_edit_copy_with_no_role(self, tmp_path):
        copy = a_real_copy(tmp_path)
        del copy["role"]
        got, why = EditCopy.deserialize("copy 1", copy)
        assert got is None
        assert "`role`" in why[0]

    @pytest.mark.parametrize(
        "bad", [{"junk": 1}, {"root": 7, "revise": "x"}, {}, "oops", None, []]
    )
    def test_an_edit_copy_whose_read_from_is_the_wrong_SHAPE(self, tmp_path, bad):
        """`decision-log.md Process: #34`: the field exists so a later role can
        know it holds a REVISE. Each of these is a way of not saying so.

        !! MOVED FROM `tests/test_collator.py` BY `P42`, where it drove
        `problems_in`. That function takes an `EditCopy` now, so the header is
        no longer its question -- this parse is the only door, and the six
        values come across unchanged.

        ! WHAT THEY MEASURED, on `problems_in`'s own comment: a hand-rolled
        `isinstance(..., dict) and truthy` let `{"junk": 1}` and `{"root": 7,
        "revise": "x"}` through at exit 0 while `bind` REFUSED the identical
        value -- two spellings of one rule, disagreeing. `_read_from_problem`
        is the one spelling, and this is what holds it to it.
        """
        copy = a_real_copy(tmp_path)
        copy["read_from"] = bad
        got, why = EditCopy.deserialize("copy 1", copy)
        assert got is None, bad
        assert "read_from" in why[0], bad

    def test_an_edit_copy_reports_EVERY_bad_sheet_not_just_the_first(self, tmp_path):
        copy = a_real_copy(tmp_path)
        copy["sheets"] = [{"sha": "a"}, {"sha": "b"}]
        got, why = EditCopy.deserialize("copy 1", copy)
        assert got is None
        assert len(why) == 2

    def test_a_master_proof_whose_edit_copies_are_not_a_list(self):
        proof, why = MasterProof.deserialize("4c", {"stage": "4c", "edit_copies": {}})
        assert proof is None
        assert "`edit_copies` list" in why[0]

    def test_a_master_proof_whose_read_from_disagrees_with_the_first_copy(
        self, tmp_path
    ):
        """`desk.proof.gather` refuses this same disagreement with
        `MismatchedRoot` before a master_proof is ever built -- a proof
        reaching `MasterProof.deserialize` with one is malformed, not merely
        unusual."""
        binder = binder_of(a_small_real_tree(tmp_path), 0)
        proof = gather("4c", [returned(seed(binder, "block-context"))]).serialize()
        proof["read_from"] = {"root": "somewhere else", "revise": 99}
        got, why = MasterProof.deserialize("4c", proof)
        assert got is None
        assert "disagrees with the first edit_copy's" in why[0]

    def test_a_master_proof_whose_read_from_is_malformed(self, tmp_path):
        """The same shape check `_read_from_problem` runs for an edit_copy,
        reused here for the master_proof's own `read_from` field."""
        binder = binder_of(a_small_real_tree(tmp_path), 0)
        proof = gather("4c", [returned(seed(binder, "block-context"))]).serialize()
        proof["read_from"] = {"root": proof["read_from"]["root"]}
        got, why = MasterProof.deserialize("4c", proof)
        assert got is None
        assert "`revise`" in why[0]

    def test_a_master_proof_WITH_NO_EDIT_COPIES_still_parses(self):
        """`desk.proof.gather`'s own contract: an empty `edit_copies` gathers
        to `read_from={}`, since there is no first copy to take it from --
        that is not the disagreement or malformed shape the two cases above
        refuse."""
        got, why = MasterProof.deserialize("4c", {"stage": "4c", "edit_copies": []})
        assert why == []
        assert got is not None
        assert got.read_from == {}


class TestANullFieldIsAbsentNotTheWordNone:
    """`.get(key, "")` DEFAULTS ONLY WHEN THE KEY IS ABSENT -- a key present
    and holding `None` returns `None` from `.get`, and `str(None)` is the
    four-character word "None". The same class of defect as a null
    `verbatim` rendering as the word "None" in `results/verdicts.py`."""

    def test_a_null_sha(self):
        sheet, why = Sheet.deserialize(
            "sheet 1", {"path": "m.py", "sha": None, "marks": []}
        )
        assert why == []
        assert sheet is not None
        assert sheet.sha == ""

    def test_a_null_stage(self):
        proof, why = MasterProof.deserialize("4c", {"stage": None, "edit_copies": []})
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


class TestAnAddressLessEntryIsStillFindable:
    """A place a role must fix that the system cannot ROUTE, it must still NAME.

    !! MEASURED 2026-09-01, AFTER `P51` REMOVED THE ONLY HANDLE. A bare string
    in `marks` reported `block-context (the copy): this mark: a mark must be an
    object` -- naming neither the page nor the entry, and borrowing the
    rendering that means *this finding is about the whole copy*. `problems_in`
    had fallen back to `mark {n}` and `P51` cut it as *not something a role can
    act on*, which is true wherever an address exists and false where none does.
    """

    def test_a_bare_string_is_located_by_page_and_position(self):
        sheet, why = Sheet.deserialize(
            "s", {"path": "m.py", "sha": "a", "marks": [{}, {}, "not an object"]}
        )
        assert why == []
        assert sheet is not None
        last = sheet.refused[-1]
        assert last.address == "", "there is nothing to route on"
        assert last.where == "m.py mark 3", "and still somewhere to look"

    def test_an_untouched_entry_naming_no_place_is_REFUSED_not_unruled(self):
        """*"Handed to this role and not ruled on"* is a claim about a PLACE.

        ! AND `_coverage_problems` READS `unruled` AS ADDRESSES, so an "" among
        them would count a place the binder never held toward what the role
        carried back.
        """
        sheet, why = Sheet.deserialize(
            "s", {"path": "m.py", "sha": "a", "marks": [{"instruction": None}]}
        )
        assert why == []
        assert sheet is not None
        assert sheet.unruled == (), "it names no place, so it is not a gap"
        assert sheet.refused[0].where == "m.py mark 1"
        assert "`address`" in sheet.refused[0].reasons[0]

    def test_an_untouched_entry_WITH_a_place_is_still_unruled(self):
        """The other half, so the case above is a distinction and not a change
        of behaviour for every seeded slot."""
        sheet, why = Sheet.deserialize(
            "s",
            {
                "path": "m.py",
                "sha": "a",
                "marks": [{"address": "m.py@b1", "instruction": None}],
            },
        )
        assert why == []
        assert sheet is not None
        assert sheet.unruled == ("m.py@b1",)
        assert sheet.refused == ()
