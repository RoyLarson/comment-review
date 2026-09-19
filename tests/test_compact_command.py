"""The `compact` command: stage 6's condensed text, written onto the proof.

! DRIVEN THROUGH `main()` AND `sys.argv` over the real chain -- `collate`
deals and closes the fold, `compact` rewrites the text at a place it settled.
`decision-log.md Process: #191`.

! THE EXIT CODES ARE `collate`'s, for the reason `tests/test_turn_command.py`
gives: every command that folds through the desk exits the same five, so a
caller branching on a code branches once.
"""

import json

from conftest import run_command
from helpers import BASE, TWO, a_clean, a_correct_setting, deal, place_on, proof_at

from comment_review.commands import collate as collate_command
from comment_review.commands import compact as compact_command
from comment_review.flows.proof_io import load_proof

#: What stage 6 hands back at `m.py@b1` -- the decided text, condensed.
CONDENSED = "# 2"


def a_closed_proof(tmp_path, monkeypatch, capsys):
    """One place corrected and one left standing, settled at the first fold.

    The second place is what the refusal cases name: it decided no text, so
    there is nothing there to condense.
    """
    code = deal(
        tmp_path,
        monkeypatch,
        capsys,
        {
            "block-context": {
                "m.py@b1": a_correct_setting("m.py@b1", "two", TWO),
                "m.py@b2": a_clean("m.py@b2"),
            }
        },
        {"m.py@b1": BASE, "m.py@b2": "# four\n"},
    )
    assert code == collate_command.OK
    return tmp_path / "proof0.json"


def compact(tmp_path, monkeypatch, capsys, rows: object, out: str = "compacted.json"):
    """`compact` over `proof0.json`, writing the condensed proof at `out`."""
    (tmp_path / "compactions.json").write_text(json.dumps(rows), encoding="utf-8")
    return run_command(
        monkeypatch,
        capsys,
        compact_command,
        "--proof",
        str(tmp_path / "proof0.json"),
        "--compacted",
        str(tmp_path / "compactions.json"),
        "--proof-out",
        str(tmp_path / out),
    )


def _written(tmp_path, name: str = "compacted.json"):
    proof, why = load_proof(tmp_path / name)
    assert proof is not None, why
    return proof


class TestTheCompactedTextLandsOnThePlace:
    def test_the_place_carries_the_condensed_text_and_the_others_do_not_move(
        self, tmp_path, monkeypatch, capsys
    ):
        a_closed_proof(tmp_path, monkeypatch, capsys)
        code, out = compact(
            tmp_path, monkeypatch, capsys, [{"address": "m.py@b1", "change": CONDENSED}]
        )
        assert code == collate_command.OK, out
        assert place_on(_written(tmp_path), "m.py@b1")["text"] == CONDENSED
        assert place_on(_written(tmp_path), "m.py@b2")["text"] is None

    def test_the_place_is_named_on_stdout(self, tmp_path, monkeypatch, capsys):
        """Every place is named, never counted: a capped run that said only
        how many paragraphs it condensed could not be read against what the
        author is about to approve."""
        a_closed_proof(tmp_path, monkeypatch, capsys)
        _code, out = compact(
            tmp_path, monkeypatch, capsys, [{"address": "m.py@b1", "change": CONDENSED}]
        )
        assert "m.py@b1" in out

    def test_the_proof_it_read_is_left_as_it_was(self, tmp_path, monkeypatch, capsys):
        """! THE INPUT IS NOT REWRITTEN. The proof `disposition` closed is the
        record of what was decided at full length, and stage 7a's residue
        check reads the original prose against the text it is shown."""
        a_closed_proof(tmp_path, monkeypatch, capsys)
        compact(
            tmp_path, monkeypatch, capsys, [{"address": "m.py@b1", "change": CONDENSED}]
        )
        assert place_on(proof_at(tmp_path, 0), "m.py@b1")["text"] == TWO

    def test_the_written_proof_is_what_the_write_end_reads(
        self, tmp_path, monkeypatch, capsys
    ):
        """The output is a master proof, read back through the loader the
        write end reads one with -- not a document only this command can
        make sense of."""
        a_closed_proof(tmp_path, monkeypatch, capsys)
        compact(
            tmp_path, monkeypatch, capsys, [{"address": "m.py@b1", "change": CONDENSED}]
        )
        written = _written(tmp_path)
        assert {entry["address"] for entry in written.places} == {
            "m.py@b1",
            "m.py@b2",
        }


class TestWhatItRefuses:
    def test_a_place_that_settled_on_no_text_is_BROKEN_by_name(
        self, tmp_path, monkeypatch, capsys
    ):
        a_closed_proof(tmp_path, monkeypatch, capsys)
        code, out = compact(
            tmp_path, monkeypatch, capsys, [{"address": "m.py@b2", "change": CONDENSED}]
        )
        assert code == collate_command.BROKEN, out
        assert "m.py@b2" in out
        assert not (tmp_path / "compacted.json").exists()

    def test_an_address_the_proof_does_not_carry_is_BROKEN_by_name(
        self, tmp_path, monkeypatch, capsys
    ):
        a_closed_proof(tmp_path, monkeypatch, capsys)
        code, out = compact(
            tmp_path, monkeypatch, capsys, [{"address": "m.py@b9", "change": CONDENSED}]
        )
        assert code == collate_command.BROKEN, out
        assert "m.py@b9" in out

    def test_an_empty_compacted_text_is_BROKEN(self, tmp_path, monkeypatch, capsys):
        a_closed_proof(tmp_path, monkeypatch, capsys)
        code, out = compact(
            tmp_path, monkeypatch, capsys, [{"address": "m.py@b1", "change": ""}]
        )
        assert code == collate_command.BROKEN, out
        assert "m.py@b1" in out

    def test_one_refusal_writes_no_proof_at_all(self, tmp_path, monkeypatch, capsys):
        """All or nothing: the good compaction beside the refused one is not
        written either."""
        a_closed_proof(tmp_path, monkeypatch, capsys)
        code, _out = compact(
            tmp_path,
            monkeypatch,
            capsys,
            [
                {"address": "m.py@b1", "change": CONDENSED},
                {"address": "m.py@b2", "change": CONDENSED},
            ],
        )
        assert code == collate_command.BROKEN
        assert not (tmp_path / "compacted.json").exists()

    def test_a_file_that_is_not_a_list_of_objects_is_UNREADABLE(
        self, tmp_path, monkeypatch, capsys
    ):
        a_closed_proof(tmp_path, monkeypatch, capsys)
        code, _out = compact(tmp_path, monkeypatch, capsys, {"address": "m.py@b1"})
        assert code == collate_command.UNREADABLE

    def test_writing_over_its_own_input_is_UNREADABLE(
        self, tmp_path, monkeypatch, capsys
    ):
        """! THE INPUT IS THE RECORD OF WHAT WAS DECIDED. A run that wrote
        the condensed proof over it would leave nothing holding the text the
        fold settled on."""
        a_closed_proof(tmp_path, monkeypatch, capsys)
        code, out = compact(
            tmp_path,
            monkeypatch,
            capsys,
            [{"address": "m.py@b1", "change": CONDENSED}],
            out="proof0.json",
        )
        assert code == collate_command.UNREADABLE, out
        assert place_on(proof_at(tmp_path, 0), "m.py@b1")["text"] == TWO


def test_compact_is_a_named_command():
    from comment_review.__main__ import COMMANDS

    assert "compact" in COMMANDS
