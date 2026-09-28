"""Every edit_copy of one stage, held in one master_proof."""

from dataclasses import dataclass

from comment_review.binder.binder import _read_from_problem
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.mark import Validator


@dataclass(frozen=True)
class MasterProof:
    """Every `edit_copy` of one stage, held in one place.

    Attributes:
        stage: the label the copies were dispatched under -- `SKILL.md`'s "4a",
            "4c".
        read_from: taken from the first copy by the bus's `_on_copies`, and `{}`
            where there is none; `flows.bus._root_problems` refuses a set of
            copies that disagree, and `deserialize` a proof whose own
            `read_from` disagrees with its first copy's.
        edit_copies: one per role, or one per SHARD under fan-out.
        places: every place one fold of this stage decided, as
            `desk.proof.place.Place.serialize` writes one, read back by
            `Place.deserialize`. `flows.bus` writes it; empty until such a
            fold has run. `serialize` carries it; `deserialize` reads it where
            present.
        moves: every move one fold of this stage decided, as
            `desk.proof.move.Move.serialize` writes one. Carried and read
            like `places`, and absent from a proof written before
            `decision-log.md Process: #195`.

    !! THREE FIELDS WENT WITH THE OLD MIDDLE -- `turns`, `determined` and
    `unsettlable`, and with them the `turn` property that counted `turns`. Each
    place now carries its own answers, its own state and who it is asked of, as
    each move carries its placement answers. So the proof's places and moves
    say what turn it stands at (`flows.bus.turn_of`), and its places say what
    was ruled and what rides to the human. A proof on disk carrying the three
    old keys is neither refused nor read: `deserialize` names the keys it
    wants, so those are dropped and the proof reads back without them.
    """

    stage: str
    read_from: dict
    edit_copies: tuple[EditCopy, ...]
    places: tuple[dict, ...] = ()
    moves: tuple[dict, ...] = ()

    @classmethod
    def deserialize(
        cls, where: str, data: object, validate: Validator
    ) -> "tuple[MasterProof | None, list[str]]":
        """One master_proof and every copy under it, checked.

        Args:
            where: how to name this proof in a message -- its stage label.
            data: a master_proof, as `serialize` writes one.
            validate: the rule check every copy's ruled entries are held to.

        Returns:
            `(MasterProof, [])` or `(None, [messages])`. Every bad copy is
            reported, and so is a `read_from` that fails `_read_from_problem` --
            the same check `EditCopy.deserialize` runs on an edit_copy's own field --
            or that disagrees with the first edit_copy's -- the bus's
            `_on_copies` takes a proof's `read_from` from its first copy, so a
            proof that disagrees was not built by it.

            ! THE SHAPE CHECK RUNS WHETHER OR NOT THERE ARE COPIES, since
            2026-08-31; the COMPARISON needs a first copy and still only runs
            where there is one. The single exemption is an empty proof whose
            `read_from` is `{}` or absent, which is what `_on_copies` writes
            when it has no first copy to take one from.
        """
        if not isinstance(data, dict):
            return None, [f"{where}: a master_proof must be an object"]
        raw_copies = data.get("edit_copies")
        if not isinstance(raw_copies, list):
            return None, [f"{where}: a master_proof needs an `edit_copies` list"]
        copies: list[EditCopy] = []
        problems: list[str] = []
        for i, raw in enumerate(raw_copies, 1):
            copy, why = EditCopy.deserialize(f"{where}: edit_copy {i}", raw, validate)
            if copy is None:
                problems += why
            else:
                copies.append(copy)
        if problems:
            return None, problems
        read_from = data.get("read_from")
        # !! THE HEADER IS HELD TO A SHAPE WHETHER OR NOT THERE ARE COPIES, and was
        # not until 2026-08-31. `_read_from_problem` ran inside the `if copies:`
        # below, so a proof carrying none admitted ANY value: MEASURED with
        # `edit_copies: []`, all of `'oops'`, None, 7, [], {'root': 7} and
        # {'junk': 1} returned `problems == []`, and the two dict-shaped ones were
        # carried into `MasterProof.read_from` VERBATIM.
        #
        # ! AND THOSE TWO VALUES ARE THE REASON `_read_from_problem` IS REUSED
        # RATHER THAN HAND-ROLLED. A weaker `isinstance(..., dict) and truthy`
        # let `{"junk": 1}` and `{"root": 7, "revise": "x"}` through at exit 0
        # while `bind` REFUSED the identical value -- two spellings of one rule,
        # disagreeing. So the validator here had re-acquired the very defect
        # reuse exists to prevent.
        # ! THIS CITED `desk.collator.problems_in`'s OWN COMMENT for that
        # measurement until 2026-09-01, and `P42` had deleted the comment with
        # the header checks it explained. The measurement is stated here now,
        # where the code it justifies is.
        #
        # ! `{}` IS STILL ADMITTED, AND ONLY FOR AN EMPTY PROOF. The bus's
        # `_on_copies` writes it when there is no first copy to take a
        # `read_from` from, so refusing it would refuse a shape the producer
        # itself makes. That is the one exemption; it is not a licence for
        # every other value.
        #
        # !! THE DEFAULT IS WHAT SEPARATES AN ABSENT KEY FROM A NULL ONE, and the
        # two must not be folded together here. `.get("read_from", {})` returns `{}`
        # for an absent key -- exempt, the shape two of this module's own tests hand
        # in -- and `None` for a key PRESENT and holding null, which is checked and
        # refused. Reading `data.get("read_from")` would give `None` for both and
        # admit the null, which is the four-characters-of-"None" class of defect
        # `Sheet.deserialize` and `MasterProof.deserialize` each already guard.
        if copies or data.get("read_from", {}) != {}:
            why_header = _read_from_problem(data)
            if why_header:
                return None, [f"{where}: master_proof's {why_header}"]
        # !! THE COMPARISON AGAINST THE FIRST COPY STILL NEEDS ONE. An empty proof
        # has no first copy to disagree with.
        if copies and read_from != copies[0].read_from:
            return None, [
                f"{where}: `read_from` {read_from!r} disagrees with the "
                f"first edit_copy's {copies[0].read_from!r}"
            ]
        # ! `.get("stage", "")` DEFAULTS ONLY WHEN THE KEY IS ABSENT. A `"stage":
        # null` reaching here is a PRESENT key holding None, so `.get` returns
        # None and `str(None)` is the four-character word "None" -- folded into
        # the same absent-stage case instead.
        raw_stage = data.get("stage")
        stage = raw_stage if isinstance(raw_stage, str) else ""
        # ! BOTH ABSENT AND EMPTY READ AS EMPTY. A proof written before the
        # first fold carries no `places` key, and one written after carries
        # it; either way an entry that is not an object is dropped, and
        # `Place.deserialize` rules on the rest where a reader wants them.
        raw_places = data.get("places")
        places = (
            tuple(p for p in raw_places if isinstance(p, dict))
            if isinstance(raw_places, list)
            else ()
        )
        raw_moves = data.get("moves")
        moves = (
            tuple(m for m in raw_moves if isinstance(m, dict))
            if isinstance(raw_moves, list)
            else ()
        )
        return (
            MasterProof(
                stage=stage,
                read_from={**read_from} if isinstance(read_from, dict) else {},
                edit_copies=tuple(copies),
                places=places,
                moves=moves,
            ),
            [],
        )

    def serialize(self) -> dict:
        """This master_proof as the wire dict `deserialize` reads back."""
        return {
            "stage": self.stage,
            "read_from": {**self.read_from},
            "edit_copies": [copy.serialize() for copy in self.edit_copies],
            "places": [dict(p) for p in self.places],
            "moves": [dict(m) for m in self.moves],
        }
