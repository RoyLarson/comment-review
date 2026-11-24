"""Every edit_copy of one stage, held in one master_proof.

`referenced_reading_problems` is the proof's reference check: every page
a place, move, sheet or mark names carries a reading context and an
original sha. `deserialize` asks it before decoding a proof.
"""

from dataclasses import dataclass, field
from typing import cast

from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.mark import filled, read_text
from comment_review.desk.proof.move import Move
from comment_review.desk.proof.place import Place
from comment_review.read_from import read_from_problem
from comment_review.reading.addresser import cue_of, flatten, unflatten
from comment_review.reading.context import ReadingContext
from comment_review.reading.context_io import context_from_wire, context_to_wire


@dataclass(frozen=True)
class MasterProof:
    """Every `edit_copy` of one stage, held in one place.

    Attributes:
        stage: the label the copies were dispatched under -- `SKILL.md`'s "4a",
            "4c".
        read_from: taken from the first copy by the bus's `_on_copies`, and `{}`
            where there is none.
        edit_copies: one per role, or one per SHARD under fan-out.
        page_readings: real path -> the `ReadingContext` the page was read
            under, for every page a sheet, a place or a move names.
        places: every place one fold of this stage decided. `flows.bus`
            writes it; empty until such a fold has run. Each is read by
            `Place.deserialize` where the proof is read, so a reader of the
            proof holds places, not their wire.
        moves: every move one fold of this stage decided, as the proof records
            it (`Move.recorded`).
        page_shas: real path -> sha for pages touched outside the copies.
        dispatched: the copies the stage dispatched, as the run's jacket
            names them; empty for a proof folded without a jacket.
        returned: the copies folded into this proof, named the same way.

    Each place carries its answers, state and owed readers. Each move carries
    its placement answers. These records determine the proof's turn and rulings.
    """

    stage: str
    read_from: dict
    edit_copies: tuple[EditCopy, ...]
    page_readings: dict[str, ReadingContext]
    places: tuple[Place, ...] = ()
    moves: tuple[Move, ...] = ()
    page_shas: dict[str, str] = field(default_factory=dict)
    dispatched: tuple[str, ...] = ()
    returned: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Detach caller-owned metadata mappings."""
        object.__setattr__(self, "page_readings", dict(self.page_readings))
        object.__setattr__(self, "page_shas", dict(self.page_shas))

    def reading_problems(self, where: str) -> list[str]:
        """Hold the sheets and the two page tables to each other.

        `deserialize` asks this after `referenced_reading_problems` has held
        the wire to its references and each reading has decoded.
        """
        problems: list[str] = []
        if any(
            not isinstance(path, str)
            or not path.strip()
            or not isinstance(sha, str)
            or not sha.strip()
            for path, sha in self.page_shas.items()
        ):
            problems.append(
                f"{where}: master_proof's `page_shas` must map nonempty paths"
                " to nonempty shas; regather"
            )
        shas: dict[str, object] = {}
        for copy in self.edit_copies:
            for sheet in copy.sheets:
                if self.page_readings.get(sheet.path) != sheet.reading:
                    problems.append(
                        f"{where}: {sheet.path}: sheet reading context disagrees"
                        " with page_readings; regather"
                    )
                if sheet.path in shas and shas[sheet.path] != sheet.sha:
                    problems.append(
                        f"{where}: {sheet.path}: conflicting sheet shas; regather"
                    )
                shas[sheet.path] = sheet.sha
        for path, sha in self.page_shas.items():
            if path not in self.page_readings:
                problems.append(
                    f"{where}: {path}: destination page_readings is missing; regather"
                )
            if path in shas and shas[path] != sha:
                problems.append(
                    f"{where}: {path}: destination sha disagrees with sheet; regather"
                )
        for path in self.page_readings.keys() - shas.keys() - self.page_shas.keys():
            problems.append(
                f"{where}: {path}: page_readings lacks matching page_shas; regather"
            )
        return problems

    @classmethod
    def deserialize(
        cls, where: str, data: object
    ) -> "tuple[MasterProof | None, list[str]]":
        """One master_proof and every copy under it, checked.

        Args:
            where: how to name this proof in a message -- its stage label.
            data: a master_proof, as `serialize` writes one.

        Returns:
            `(MasterProof, [])` or `(None, [messages])`. Every bad copy is
            reported, and so is a `read_from` that fails `read_from_problem` --
            the same check `EditCopy.deserialize` runs on an edit_copy's own field --
            and every edit_copy whose `read_from` disagrees with the proof's is
            named, as `edit_copy {i}`: the bus's `_on_copies` takes a proof's
            `read_from` from its first copy and refuses copies that disagree,
            so a proof holding one was not built by it, and a copy from another
            tree would give the docket a sha from that tree.

            Every place and every move is read here, and one that will not read
            is named by its position -- `place 2`, `move 1` -- and, for a
            place, its address, so every command that reads the proof names a
            bad entry the same way. A place's filed marks point into the
            copies, which are read first, and a copy entry that will not read
            refuses the proof. A `places` or `moves` that is not a list is
            refused; an absent one is empty, as a proof written before the
            first fold carries neither.
        """
        if not isinstance(data, dict):
            return None, [f"{where}: a master_proof must be an object"]
        raw_copies = data.get("edit_copies")
        if not isinstance(raw_copies, list):
            return None, [f"{where}: a master_proof needs an `edit_copies` list"]
        missing = referenced_reading_problems(data, where)
        if missing:
            return None, missing
        copies: list[EditCopy] = []
        problems: list[str] = []
        for i, raw in enumerate(raw_copies, 1):
            copy, why = EditCopy.deserialize(f"{where}: edit_copy {i}", raw)
            if copy is None:
                problems += why
            else:
                copies.append(copy)
        # A proof's copies hold only marks that read -- `Sheet.serialize`
        # writes a sheet's marks and nothing else -- so a place's pointer lands
        # on the mark it was written for. An entry that will not read would
        # shift every mark after it, and is refused here by name.
        problems += [
            f"{where}: edit_copy {i}: {one.where}: {reason}"
            for i, copy in enumerate(copies, 1)
            for sheet in copy.sheets
            for one in sheet.refused
            for reason in one.reasons
        ]
        if problems:
            return None, problems
        raw_readings = data.get("page_readings")
        if not isinstance(raw_readings, dict):
            return None, [
                f"{where}: page_readings must map paths to reading contexts; regather"
            ]
        page_readings: dict[str, ReadingContext] = {}
        for path, raw in raw_readings.items():
            if not isinstance(path, str) or not path.strip():
                problems.append(
                    f"{where}: page_readings needs nonempty path keys; regather"
                )
                continue
            context, why = context_from_wire(f"{where}: page_readings {path}", raw)
            problems.extend(why)
            if context is not None:
                page_readings[path] = context
        raw_shas = data.get("page_shas", {})
        if not isinstance(raw_shas, dict):
            problems.append(
                f"{where}: master_proof's `page_shas` must map paths to shas; regather"
            )
        if problems:
            return None, problems
        metadata = cls(
            "",
            {},
            tuple(copies),
            page_readings,
            page_shas=cast(dict[str, str], raw_shas),
        )
        problems.extend(metadata.reading_problems(where))
        if problems:
            return None, problems
        read_from = data.get("read_from")
        # !! The header is held to a shape whether or not there are copies.
        #
        # ! `read_from_problem` is reused rather than hand-rolled, so this header
        # and `bind` refuse the same values.
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
            why_header = read_from_problem(data)
            if why_header:
                return None, [f"{where}: master_proof's {why_header}"]
        # Every copy is held to the proof's `read_from`, not the first alone. An
        # empty proof has no copy to disagree with.
        disagree = [
            f"{where}: edit_copy {i}'s `read_from` {copy.read_from!r} disagrees"
            f" with the master_proof's {read_from!r}"
            for i, copy in enumerate(copies, 1)
            if copy.read_from != read_from
        ]
        if disagree:
            return None, disagree
        # Read as an edit_copy's is: absent or null is "", any other type is
        # refused rather than turned into a string.
        stage, why = read_text(f"{where}: master_proof", "stage", data.get("stage"))
        problems += why
        places, why = _places_in(where, data.get("places", []), tuple(copies))
        problems += why
        moves, why = _moves_in(where, data.get("moves", []))
        problems += why
        # Absent is empty, as `places` and `moves` are: a proof folded without
        # a jacket names no dispatch.
        named = {key: data.get(key, []) for key in ("dispatched", "returned")}
        for key, value in named.items():
            if not isinstance(value, list) or not all(
                isinstance(one, str) for one in value
            ):
                problems.append(f"{where}: master_proof's `{key}` must list copies")
        raw_shas = data.get("page_shas", {})
        page_shas: dict = raw_shas if isinstance(raw_shas, dict) else {}
        if problems:
            return None, problems
        return (
            MasterProof(
                stage=stage,
                read_from={**read_from} if isinstance(read_from, dict) else {},
                edit_copies=tuple(copies),
                page_readings=page_readings,
                places=places,
                moves=moves,
                page_shas=dict(page_shas),
                dispatched=tuple(cast(list[str], named["dispatched"])),
                returned=tuple(cast(list[str], named["returned"])),
            ),
            [],
        )

    def serialize(self) -> dict:
        """This master_proof as the wire dict `deserialize` reads back."""
        return {
            "stage": self.stage,
            "read_from": {**self.read_from},
            "edit_copies": [copy.serialize() for copy in self.edit_copies],
            "places": [place.serialize() for place in self.places],
            "moves": [move.serialize() for move in self.moves],
            "page_shas": dict(self.page_shas),
            "dispatched": list(self.dispatched),
            "returned": list(self.returned),
            "page_readings": {
                path: context_to_wire(context)
                for path, context in self.page_readings.items()
            },
        }


def referenced_reading_problems(data: dict, where: str) -> list[str]:
    """Require reference metadata before proof decoding or downstream resolution."""
    contexts = data.get("page_readings")
    shas = data.get("page_shas", {})
    if not isinstance(contexts, dict) or not isinstance(shas, dict):
        return [f"{where}: page_readings/page_shas are missing or malformed; regather"]
    sources = dict(shas)
    references: set[str] = set()

    def collect(record: object, keys: tuple[str, ...]) -> None:
        if not isinstance(record, dict):
            return
        for key in keys:
            address = record.get(key)
            if isinstance(address, str):
                path = cue_of(address).path
                if path:
                    references.add(flatten(path))

    for key, fields in (("places", ("address",)), ("moves", ("origin", "destination"))):
        records = data.get(key, [])
        if isinstance(records, list):
            for record in records:
                collect(record, fields)
    copies = data.get("edit_copies", [])
    if isinstance(copies, list):
        for copy in copies:
            sheets = copy.get("sheets", []) if isinstance(copy, dict) else []
            if not isinstance(sheets, list):
                continue
            for sheet in sheets:
                if not isinstance(sheet, dict):
                    continue
                path, sha = sheet.get("path"), sheet.get("sha")
                if isinstance(path, str):
                    references.add(flatten(path))
                    sources.setdefault(path, sha)
                marks = sheet.get("marks", [])
                if isinstance(marks, list):
                    for mark in marks:
                        collect(mark, ("address",))
                        if isinstance(mark, dict) and mark.get("instruction") == "move":
                            collect(mark.get("claim"), ("to",))
    problems: list[str] = []
    known = [path for path in contexts.keys() | sources.keys() if isinstance(path, str)]
    for reference in sorted(references):
        path = unflatten(reference, known) or reference
        if path not in contexts:
            problems.append(
                f"{where}: {path}: referenced page_readings is missing; regather"
            )
        if path not in sources:
            problems.append(
                f"{where}: {path}: referenced original sha in page_shas or sheets"
                " is missing; regather"
            )
    return problems


def _places_in(
    where: str, raw: object, copies: tuple[EditCopy, ...]
) -> "tuple[tuple[Place, ...], list[str]]":
    """A proof's `places`, each read against its copies.

    One message is named per entry that will not read.
    """
    if not isinstance(raw, list):
        return (), [f"{where}: master_proof's `places` must be a list"]
    places: list[Place] = []
    problems: list[str] = []
    for i, entry in enumerate(raw, 1):
        address = entry.get("address") if isinstance(entry, dict) else None
        at = f"{where}: place {i}" + (f" at {address}" if filled(address) else "")
        place, why = Place.deserialize(at, entry, copies)
        if place is None:
            problems += why
        else:
            places.append(place)
    return tuple(places), problems


def _moves_in(where: str, raw: object) -> "tuple[tuple[Move, ...], list[str]]":
    """A proof's `moves`, each read, and one message per entry that will not."""
    if not isinstance(raw, list):
        return (), [f"{where}: master_proof's `moves` must be a list"]
    moves: list[Move] = []
    problems: list[str] = []
    for i, entry in enumerate(raw, 1):
        move, why = Move.deserialize(f"{where}: move {i}", entry)
        if move is None:
            problems += why
        else:
            moves.append(move)
    return tuple(moves), problems
