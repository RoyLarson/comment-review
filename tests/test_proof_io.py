"""`flows.proof_io`: the master proof's load and save, raw JSON at the ends only.

`Process: #65`, `#67`. What `save_proof` writes, `load_proof` reads back equal,
and every way a file fails to be a proof is named rather than raised.
"""

from helpers import a_correct, a_master_proof

from comment_review.flows.proof_io import load_proof, save_proof


def a_proof():
    return a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})


class TestTheRoundTrip:
    def test_what_save_writes_load_reads_back_equal(self, tmp_path):
        proof = a_proof()
        save_proof(tmp_path / "p.json", proof)
        got, why = load_proof(tmp_path / "p.json")
        assert why == []
        assert got == proof

    def test_the_file_is_the_containers_own_wire(self, tmp_path):
        """No second shape: what is on disk is `MasterProof.serialize`."""
        import json

        proof = a_proof()
        save_proof(tmp_path / "p.json", proof)
        on_disk = json.loads((tmp_path / "p.json").read_text(encoding="utf-8"))
        assert on_disk == proof.serialize()


class TestEveryFailureIsNamed:
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
