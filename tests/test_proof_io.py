"""`flows.proof_io`: the middle's artifacts on disk, raw JSON at the ends only.

`Process: #65`, `#67`. What a save writes its load reads back equal, and every
way a file fails to be the artifact it claims is named rather than raised --
in one wording, since every command reads through here (T17 of
`TODO/no-command-for-the-middle.md`).
"""

import json

import pytest
from helpers import (
    REPO,
    a_binder_over,
    a_correct,
    a_master_proof,
    copies_over,
)

from comment_review.binder.binder import Binder
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.flows.proof_io import (
    load_batch,
    load_binder,
    load_copy,
    load_proof,
    load_value,
    save_batch,
    save_copy,
    save_proof,
)


def a_proof(tmp_path):
    return a_master_proof(
        tmp_path / "repo", {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
    )


class TestTheRoundTrip:
    def test_what_save_writes_load_reads_back_equal(self, tmp_path):
        proof = a_proof(tmp_path)
        save_proof(tmp_path / "p.json", proof)
        got, why = load_proof(tmp_path / "p.json")
        assert why == []
        assert got == proof

    def test_a_read_proof_saves_to_the_same_file(self, tmp_path):
        """Each mark is stored once and each place points at it, so reading a
        proof and saving it again writes the file it was read from, byte for
        byte."""
        save_proof(tmp_path / "p.json", a_proof(tmp_path))
        got, why = load_proof(tmp_path / "p.json")
        assert why == [] and got is not None
        save_proof(tmp_path / "again.json", got)
        assert (tmp_path / "again.json").read_bytes() == (
            tmp_path / "p.json"
        ).read_bytes()

    def test_the_file_is_the_containers_own_wire(self, tmp_path):
        """No second shape: what is on disk is `MasterProof.serialize`."""
        import json

        proof = a_proof(tmp_path)
        save_proof(tmp_path / "p.json", proof)
        on_disk = json.loads((tmp_path / "p.json").read_text(encoding="utf-8"))
        assert on_disk == proof.serialize()


class TestEveryFailureIsNamed:
    @pytest.mark.parametrize("kind", ["place", "move"])
    def test_a_human_held_proof_is_rejected_by_name_state_and_address(
        self, tmp_path, kind
    ):
        wire = a_proof(tmp_path).serialize()
        if kind == "place":
            wire["places"][0]["state"] = "unsettlable"
            old_state = "unsettlable"
        else:
            wire["moves"] = [
                {"origin": "m.py@b1", "destination": "m.py@b2", "placement": "held"}
            ]
            old_state = "held"
        source = tmp_path / "old-proof.json"
        source.write_text(json.dumps(wire), encoding="utf-8")
        got, why = load_proof(source)
        assert got is None
        assert any(
            "old-proof.json" in one and "m.py@b1" in one and old_state in one
            for one in why
        )

    @pytest.mark.parametrize("kind", ["place", "move"])
    def test_a_retired_asking_lifecycle_is_not_silently_reinterpreted(
        self, tmp_path, kind
    ):
        wire = a_proof(tmp_path).serialize()
        if kind == "place":
            wire["places"][0]["asking"] = ["block-context: Who owns this?"]
        else:
            wire["moves"] = [
                {
                    "origin": "m.py@b1",
                    "destination": "m.py@b2",
                    "placement": "agreed",
                    "asking": ["block-context: Who owns this?"],
                }
            ]
        source = tmp_path / "old-proof.json"
        source.write_text(json.dumps(wire), encoding="utf-8")
        got, why = load_proof(source)
        assert got is None
        assert any(
            "old-proof.json" in one and "m.py@b1" in one and "asking" in one
            for one in why
        )

    def test_a_missing_file(self, tmp_path):
        got, why = load_proof(tmp_path / "nope.json")
        assert got is None
        assert len(why) == 1 and "nope.json" in why[0]

    def test_text_that_is_not_an_object(self, tmp_path):
        (tmp_path / "p.json").write_text("[1, 2]", encoding="utf-8")
        got, why = load_proof(tmp_path / "p.json")
        assert got is None
        assert len(why) == 1 and "p.json" in why[0]

    def test_an_object_that_is_not_a_proof_is_the_containers_refusal(self, tmp_path):
        (tmp_path / "p.json").write_text('{"stage": "4c"}', encoding="utf-8")
        got, why = load_proof(tmp_path / "p.json")
        assert got is None
        assert any("edit_copies" in one for one in why)


class TestTheOtherArtifacts:
    """The binder, a copy, a batch and any value -- the same three steps each."""

    def test_a_binder_round_trips_through_the_container(self, tmp_path):
        binder = a_binder_over({"m.py@b1": "# one\n"})
        (tmp_path / "b.json").write_text(
            json.dumps(binder.serialize()), encoding="utf-8"
        )
        got, why = load_binder(tmp_path / "b.json")
        assert why == []
        assert isinstance(got, Binder)
        assert got.serialize() == binder.serialize()

    def test_a_binder_that_is_not_one_is_refused_by_the_container(self, tmp_path):
        (tmp_path / "b.json").write_text('{"pages": "oops"}', encoding="utf-8")
        got, why = load_binder(tmp_path / "b.json")
        assert got is None
        assert why

    def test_a_copy_loads_as_its_wire_dict_and_save_copy_writes_the_same(
        self, tmp_path
    ):
        binder = a_binder_over({"m.py@b1": "# one\n"})
        (wire,) = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        copy, why = EditCopy.deserialize("c", wire)
        assert copy is not None, why
        save_copy(tmp_path / "c.json", copy)
        loaded, why = load_copy(tmp_path / "c.json")
        assert why == []
        assert loaded == copy.serialize()

    def test_a_copy_that_is_not_an_object_is_named(self, tmp_path):
        (tmp_path / "c.json").write_text("[]", encoding="utf-8")
        loaded, why = load_copy(tmp_path / "c.json")
        assert loaded == {}
        assert len(why) == 1 and "c.json" in why[0]

    def test_a_batch_round_trips_and_a_non_list_role_is_left_out(self, tmp_path):
        save_batch(tmp_path / "b.json", {"block-context": [{"address": "m.py@b1"}]})
        batch, why = load_batch(tmp_path / "b.json")
        assert why == []
        assert batch == {"block-context": [{"address": "m.py@b1"}]}
        (tmp_path / "b.json").write_text('{"block-context": "nope"}', encoding="utf-8")
        batch, why = load_batch(tmp_path / "b.json")
        assert batch == {}
        assert any("names no role" in one for one in why)

    def test_any_value_loads_and_a_non_json_file_is_named(self, tmp_path):
        (tmp_path / "v.json").write_text("[1, {}]", encoding="utf-8")
        assert load_value(tmp_path / "v.json") == ([1, {}], [])
        (tmp_path / "v.json").write_text("{nope", encoding="utf-8")
        value, why = load_value(tmp_path / "v.json")
        assert value is None
        assert any("not JSON" in one for one in why)

    def test_the_root_a_binder_carries_is_what_the_commands_resolve_against(self):
        binder = a_binder_over({"m.py@b1": "# one\n"})
        assert str(binder.root) == binder.read_from["root"]
        assert REPO.exists()
