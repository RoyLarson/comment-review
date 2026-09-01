r"""The containers a mark travels in -- the sheet, the edit_copy, the master_proof.

    Sheet              one PAGE's marks, with that page's path and sha
    EditCopy           one ROLE's sheets, with the binder it was seeded from
    MasterProof        one STAGE's edit_copies
    Sheet.deserialize()      the boundary parse for one sheet
    EditCopy.deserialize()  for one edit_copy, and every sheet under it
    MasterProof.deserialize()  for one master_proof, and every copy under it

!! THE TYPE IS THE DEFINITION AND THERE IS NO MARKDOWN SOURCE, ruled
`decision-log.md Vocabulary: #30`. `docs/the-mark.md` exists because an agent
AUTHORS a mark, so a mark's shape must be published to a role. No agent ever
authors a container, so the type is where the shape lives, the way
`desk/mark.py` defines `Mark`.

!! THE WIRE STAYS DICTS. Each parse has `desk.mark.parse`'s own contract --
`(T, [])` or `(None, [one message per broken rule])` -- so a caller holds a
checked object rather than re-deriving the same keys with `isinstance`
ladders.

!! BOTH HALVES OF THE ROUND TRIP LIVE HERE, as of 2026-08-31. `seed` writes a
container from the class's own field names -- `Process: #64` -- and `parse`
reads one back. Renaming a field breaks at construction rather than folding to
a default one module away, which is `desk.mark.Mark.seed`'s guard one level up.

!!! **`seed` RETURNS THE WIRE DICT AND THAT IS CORRECT** -- `Process: #66`. A
seed is an EMPTY FORM, not an instance: `desk.mark.Mark.seed` writes three of
`Mark`'s eight fields plus `instruction: None`, and typing that as a `Mark`
would need five optionals, at which point holding a `Mark` would stop meaning
the ruling is complete. **The split is `parse` versus `seed`, not container
versus dict** -- a parse answers *is this a filled, well-formed X* and returns
the type; a seed answers *what does an unfilled X look like on the wire*.

! **THIS PARAGRAPH SAID THE OPPOSITE FOR ABOUT AN HOUR ON 2026-08-31**, claiming
`Process: #65` overrode the return type and citing `Mark`'s `seed`/`serialize`
split as the precedent. **Both of those return dicts.** `#65` governs what a
flow CARRIES between its load and its save; a seed is emitted AT a save --
`flows.distribute.seed` builds one and the command writes it as the JSON a role
is handed -- so the dict is where that ruling puts it.

    write   flows.distribute.seed, flows.collate._chief_copy,
            flows.collate._nothing_settled, desk.proof.gather
    read    flows.collate.collate, at its inbound boundary and after `gather`

! THE PARSES HAD NO PRODUCTION CALLER UNTIL 2026-08-31, and this file said so
for as long as that was true. `P21` closed it: `collate` runs `EditCopy.deserialize`
over every returned copy and `MasterProof.deserialize` over what `gather` builds,
so **every refusal declared below can now fire.**

!! THIS FILE STATES WHAT THE TWO BOUNDARIES ARE, AND NOTHING ELSE RESTATES IT.
A container guards the **ENVELOPE** -- is this document the shape a copy must
be -- while `flows.mark_errors` rules on the **CONTENTS**, so each per-mark
problem routes back to the role that wrote it. They are not competing
contracts, and both run. ! `flows/collate.py` owns the ORDER and the RESPONSE
(envelope first; reported, not raised) and cites this paragraph rather than
repeating it -- a rule in two places is a rule that will disagree with itself.

! THE CHIEF'S COPY IS AN ORDINARY `EditCopy`. `Vocabulary: #30`: after the fold
every place has exactly one answer, and one mark per place is an ordinary copy.
There is no second shape and no second parse.

!! `Sheet.marks` HOLDS `Mark`s SINCE `P51`, and was `tuple[object, ...]` --
an entry that is not an object was CARRIED so `desk.mark.parse` could refuse it
by name rather than have it vanish. `_sorted_entries` refuses it at the parse
instead, into `Sheet.refused`, so nothing vanishes and nothing downstream has to
re-read a raw entry. ! `Mark.sources` IS STILL `object` for the original
reason; the two are no longer the same case.
"""

from dataclasses import dataclass, field, fields
from typing import NamedTuple

from comment_review.binder.binder import _read_from_problem
from comment_review.desk.mark import Mark, filled, untouched, without_location


def _wire_fields(cls) -> list[str]:
    """The field names that are on the WIRE, in the class's own order.

    !! NOT EVERY FIELD IS A WIRE FIELD, since `P51`. `Sheet.unruled` and
    `Sheet.refused` are DERIVED by the parse -- they are what the entries that
    are not a `Mark` came to -- so a producer must not be asked to write them
    and `_written` must not demand them. A field is off the wire when its
    metadata says `wire: False`; everything else is on it, which keeps the
    default the safe one.
    """
    return [f.name for f in fields(cls) if f.metadata.get("wire", True)]


def _written(cls, values: dict) -> dict:
    """One container as the wire dict, keyed by `cls`'s OWN field names.

    !! THE WRITE HALF OF THE ROUND TRIP LIVES WITH THE READ HALF, ruled
    `decision-log.md Process: #64`. It is `desk.mark.Mark.seed`'s guard one
    level up: every producer spelled these keys as literals, so renaming a
    field left another module writing the old key and NOTHING could notice --
    `Sheet.deserialize` folds an absent `sha` to `""` and reports no problem, where
    `Mark.seed` raises at the point the row is built.

    Args:
        cls: the container dataclass being written.
        values: one entry per declared field, by name.

    Returns:
        `values`, in the class's own field order.

    Raises:
        AttributeError: `values` names a field the class does not declare, or
            omits one it does. ! THIS IS THE WHOLE GUARD, and it fires at the
            point the row is built rather than silently one module away.
    """
    declared = _wire_fields(cls)
    if set(values) != set(declared):
        raise AttributeError(
            f"{cls.__name__}.seed writes {sorted(values)}, "
            f"which is not {cls.__name__}'s wire fields {sorted(declared)}"
        )
    return {name: values[name] for name in declared}


class Refused(NamedTuple):
    """One entry the parse could not read as a mark, and why.

    ! ADDRESS AND REASONS, NEVER THE ENTRY -- `decision-log.md Process: #72`.
    Roy, 2026-09-01: *"The agents can find the marks in their remit and fix in
    their stuff directly. No reason to try to duplicate or fill in the problems
    for them and have disjointed what needs fixed."* The role still holds the
    copy this came out of; what it needs is where and what, not the place back.

    Attributes:
        address: the entry's own `address`, or "" where it carried none -- an
            entry that is not an object, or one whose `address` is not a string.
            ! IT IS WHAT ROUTES, and "" means there is nothing to route on.
            Nothing may print it; `where` is for that.
        where: how to POINT AT the entry, never empty -- the address where there
            is one, else the page and the entry's position on it, as
            `m.py mark 3`.

            !! IT EXISTS BECAUSE `P51` REMOVED THE ONLY HANDLE ON AN
            ADDRESS-LESS ENTRY. `problems_in` fell back to `mark {n}` and that
            was dropped on the reasoning that *a position is not something a
            role can act on* -- which is true everywhere EXCEPT here, where the
            position is the one locator left. MEASURED 2026-09-01: a bare string
            in `marks` reported `block-context (the copy): this mark: a mark
            must be an object`, naming neither the page nor the entry, so a role
            could not find what to fix.
        reasons: every rule the entry broke, as `Mark.deserialize` worded them.
            ! ALL OF THEM, not the first -- one malformed `correct` breaks four,
            and a role fixing one at a time is three more round trips.
    """

    address: str
    where: str
    reasons: tuple[str, ...]


#: What a refusal says about an untouched entry naming no place. It is the one
#: sentence for that case, and it is a REFUSAL rather than a coverage gap for
#: the reason `_sorted_entries` gives.
NO_PLACE = "an untouched slot must carry the `address` it was seeded with"


def _sorted_entries(
    path: str,
    marks: list,
) -> "tuple[list[Mark], list[str], list[Refused]]":
    """One sheet's entries, split into the three kinds a returned sheet holds.

    !! THE ONLY PLACE A MARK IS PARSED, since `P51`. It was parsed at FOUR --
    `problems_in`, `verify_report`, `places` and `flows.collate._keeps` -- so
    every ruled entry went through `Mark.deserialize` four times per run,
    measured 2026-09-01. Each of those four also spelled its own `where`
    fallback and its own untouched test, which is four chances to disagree
    about what an unruled place is.

    Args:
        path: the page this sheet holds, for the locator below. ! IT IS TAKEN
            RATHER THAN DERIVED because an address-less entry has no other way
            to say which page it sits on.
        marks: the sheet's `marks` list, as it came back. Entries are whatever
            JSON held -- an object, a string, a number.

    Returns:
        `(ruled, unruled, refused)`.

        ruled: one `Mark` per entry that parsed.
        unruled: the ADDRESS of every untouched entry -- `desk.mark.untouched`,
            a place nobody wrote in. ! IT IS ASKED FIRST, because an untouched
            entry does not parse either: `Mark.deserialize` refuses its
            `instruction: None` with *"must be one of add, clean, ..."*, which
            would report a coverage gap as a malformed mark.
        refused: one `Refused` per entry that is neither.

    !! AN UNTOUCHED ENTRY NAMING NO PLACE IS REFUSED, NOT UNRULED, and that is
    a ruling rather than a convenience. *"Handed to this role and not ruled on"*
    is a claim about a PLACE, so an entry that names none cannot be it -- and
    `_coverage_problems` reads `unruled` as addresses, so an "" among them would
    count a place the binder never held. `seed` writes the address on every slot
    it hands out, so an entry reaching here without one was edited after it was
    seeded, which is a role's mistake and routes back as one.

    ! AN ENTRY THAT IS NOT AN OBJECT IS REFUSED, NOT DROPPED. `Sheet.marks` was
    typed `object` precisely so a bare string could be named rather than vanish;
    that reason survives the retyping, here, where the entry is read.

    ! AND THE POSITION IS KEPT FOR EXACTLY THE ENTRY THAT NEEDS IT. `P51` cut
    the old `mark {n}` fallback as *not something a role can act on*, which is
    true wherever an address exists and false where none does -- there it is the
    only handle there is. `Refused.where` carries it.
    """
    ruled: list[Mark] = []
    unruled: list[str] = []
    refused: list[Refused] = []
    for n, entry in enumerate(marks, 1):
        address = entry.get("address") if isinstance(entry, dict) else None
        named = str(address) if filled(address) else ""
        # ! NEVER EMPTY, which is what lets `commands/collate.py` keep
        # `(the copy)` for findings that really are about the whole document.
        where = named or f"{path} mark {n}"
        if isinstance(entry, dict) and untouched(entry):
            if named:
                unruled.append(named)
            else:
                refused.append(Refused("", where, (NO_PLACE,)))
            continue
        mark, why = Mark.deserialize(where, entry)
        if mark is None:
            # ! THE LOCATOR IS A FIELD, SO IT IS NOT ALSO A PREFIX -- T3 of
            # `collate-command-defects`. `where` went IN to name the mark in
            # each message; `Refused.where` carries it now, so the sentence
            # does not repeat it.
            refused.append(
                Refused(named, where, tuple(without_location(where, m) for m in why))
            )
        else:
            ruled.append(mark)
    return ruled, unruled, refused


@dataclass(frozen=True)
class Sheet:
    """One page's RULINGS, inside the `edit_copy` that seeded them.

    !! IT HOLDS WHAT PARSED, AND WAS `tuple[object, ...]` UNTIL `P51`. Roy,
    2026-09-01: *"we clearly need sheet to take Marks not Objects."* A returned
    sheet's entries come back in three kinds and only one is a mark -- the other
    two leave as `unruled` and `refused`, which is `Process: #72`'s shape.

    !! SO `deserialize` IS NOT `serialize`'s INVERSE FOR A SHEET THAT HOLDS
    EITHER, and that is deliberate rather than a gap. What a role hands back has
    an entry per place; what this holds is the rulings. The two other kinds are
    not thrown away -- they are the whole subject of `flows/mark_errors.py`, and
    they are addresses and reasons rather than places, so nothing can put them
    back. ! The inverse DOES hold for a sheet whose every entry ruled, which is
    what `tests/test_containers.py` round-trips.

    Attributes:
        path: the page's real repo path, as the binder stated it.
        sha: that page's sha when it was censused. Read by `docket_from`, which
            writes it onto the docket page so the setter can refuse a page that
            moved underneath the run.
        marks: one `Mark` per place a role RULED on, in the order they came
            back.
        unruled: the address of every place handed to the role and left
            untouched -- `desk.mark.untouched`. A coverage gap, not an error.
        refused: one `Refused` per entry that is neither untouched nor
            parseable. ! IT IS NOT FATAL TO THE SHEET, and that is what keeps
            one role's bad mark from blocking the stage: `flows.collate.collate`
            returns early on an envelope failure, so refusing here would stop
            three roles over one. Roy, 2026-08-30: *"the errors should be
            stacked and capable of being read off correctly so that each can be
            fixed or sent back to the role."*
    """

    path: str
    sha: str
    marks: tuple[Mark, ...]
    #: ! OFF THE WIRE. Both are what the parse MADE of entries that are not
    #: marks, so no producer writes them and `_written` must not demand them.
    unruled: tuple[str, ...] = field(default=(), metadata={"wire": False})
    refused: tuple[Refused, ...] = field(default=(), metadata={"wire": False})

    @classmethod
    def seed(cls, path: str, sha: object, marks: list) -> dict:
        """One sheet as the wire dict every producer writes.

        !! `sha` IS NORMALIZED HERE, AND THIS IS THE ONE PLACE THAT DOES IT.
        `.get("sha", "")` defaults only when the key is ABSENT, so a `"sha":
        null` binder page arrives with the key PRESENT and holding None, and
        `str(None)` is the four-character word "None". `flows.distribute.seed`
        and `Sheet.deserialize` each carried this fold; a rule stated twice is a rule
        that will disagree with itself.

        Args:
            path: the page's real repo path, as the binder stated it.
            sha: that page's sha, or anything that is not a `str` -- an absent
                or null sha becomes "".
            marks: the entries for this page, carried as given.

        Returns:
            `{path, sha, marks}` -- what `Sheet.deserialize` reads back.
        """
        return _written(
            cls,
            {
                "path": path,
                "sha": sha if isinstance(sha, str) else "",
                "marks": list(marks),
            },
        )

    @classmethod
    def deserialize(cls, where: str, data: object) -> "tuple[Sheet | None, list[str]]":
        """One sheet, checked.

        Args:
            where: how to name this sheet in a message.
            data: one entry of an edit_copy's `sheets`, as it came back.

        Returns:
            `(Sheet, [])` or `(None, [messages])`. An absent OR a null `sha` is
            admitted as "".

            !! THE REASON GIVEN HERE WAS FALSE UNTIL 2026-08-31. It read *"a page
            can be censused from a tree that is not a repo"*. `machine.repo.sha_of`
            digests the TEXT with the standard library and asks nothing of git, so
            a census over a directory holding no `.git` reports a real sha for every
            page. Roy, 2026-08-31: *"this is not a valid reason to not sha hash the
            file ... we are not using the git sha for this we are using the python
            hashing library."*

            ! THE REAL PRODUCERS ARE TWO SITES INSIDE THE MIDDLE, and both write
            `""` for a path `unflatten` could not resolve back to a real page:
            `desk.collator._real_pages` and `flows.collate._chief_copy`. Neither is
            a census, and neither is about a repo.

            ! SO WHETHER AN ABSENT KEY SHOULD BE ADMITTED AT ALL IS OPEN -- no real
            producer writes a sheet without one, and `containers-and-verification-
            are-unwired` T9 holds that question. What is fixed here is the
            justification, which was not true of this code on any day.
        """
        if not isinstance(data, dict):
            return None, [f"{where}: a sheet must be an object"]
        path = data.get("path")
        if not filled(path):
            return None, [f"{where}: a sheet needs the `path` of the page it holds"]
        marks = data.get("marks")
        if not isinstance(marks, list):
            return None, [f"{where}: {path} needs a `marks` list"]
        # ! `.get("sha", "")` DEFAULTS ONLY WHEN THE KEY IS ABSENT. A `"sha":
        # null` reaching here is a PRESENT key holding None, so `.get` returns
        # None and `str(None)` is the four-character word "None" -- folded into
        # the same absent-sha case above instead.
        #
        # ! `Sheet.seed` FOLDS ON THE WAY OUT AND THIS ON THE WAY IN, so a sheet
        # written by hand -- an artifact read off disk, a role's own edit -- meets
        # the same rule as one this module wrote.
        #
        # !! AND THE FOLD IS SPELLED AT FIVE SITES. `desk.collator._real_pages`,
        # `flows.carry` and `flows.collate._chief_copy` each carry their own copy,
        # and none of the three imports this module; `carry`'s own comment already
        # says it is "matching `desk.containers.Sheet.deserialize`". This pair is the
        # round trip; those three are duplicates a change to the rule would not
        # reach.
        #
        # ! THE COUNT WAS FOUR UNTIL 2026-08-31 AND THE FIFTH WAS ADDED KNOWINGLY.
        # `_chief_copy` subscripted `sheet["sha"]` on the belief that the envelope
        # guaranteed it; it does not, and `823834f` restored the fold there rather
        # than carry the parsed `Sheet` that already holds the answer. That is a
        # stopgap standing until `Process: #65`, and counting it here is what keeps
        # it from reading as the settled shape.
        raw_sha = data.get("sha")
        sha = raw_sha if isinstance(raw_sha, str) else ""
        ruled, unruled, refused = _sorted_entries(path, marks)
        return (
            Sheet(
                path=path,
                sha=sha,
                marks=tuple(ruled),
                unruled=tuple(unruled),
                refused=tuple(refused),
            ),
            [],
        )

    def serialize(self) -> dict:
        """This sheet as the wire dict, the shape `seed` writes.

        !! IT WRITES THE RULINGS, AND IS NOT `deserialize`'s INVERSE FOR A SHEET
        HOLDING `unruled` OR `refused` -- see the class docstring. Those two are
        addresses and reasons rather than places, so there is nothing to write
        back; `flows/mark_errors.py` is where they go instead.

        ! THE THREE WIRE KEYS ARE THE THREE `seed` WRITES. `unruled` and
        `refused` are off the wire, which `_wire_fields` states once.
        """
        return {
            "path": self.path,
            "sha": self.sha,
            "marks": [mark.serialize() for mark in self.marks],
        }


@dataclass(frozen=True)
class EditCopy:
    """One role's copy of the binder -- what goes out, and what comes back.

    Attributes:
        role: the editorial role that filled it, or `copy-chief` for the fold's
            result. It is what an outcome is decided from and what a place is
            sent back to.
        read_from: `{root, revise}` -- which tree this copy was censused from.
            `decision-log.md Process: #34`: the field exists so a later role can
            know it holds a REVISE and not the original.
        sheets: one per page.
    """

    role: str
    read_from: dict
    sheets: tuple[Sheet, ...]

    @classmethod
    def seed(cls, role: str, read_from: dict, sheets: list) -> dict:
        """One edit_copy as the wire dict `flows.distribute.seed` hands out.

        Args:
            role: the editorial role this copy is for.
            read_from: `{root, revise}` -- which tree it was censused from.
            sheets: one `Sheet.seed` dict per page.

        Returns:
            `{role, read_from, sheets}`. ! `read_from` IS COPIED, NOT ALIASED,
            as `bind`, `seed` and `gather` all do with this field: a caller
            mutating its own dict afterward cannot change what this copy holds.
        """
        return _written(
            cls,
            {"role": role, "read_from": {**read_from}, "sheets": list(sheets)},
        )

    @classmethod
    def deserialize(
        cls, where: str, data: object
    ) -> "tuple[EditCopy | None, list[str]]":
        """One edit_copy and every sheet under it, checked.

        ! EVERY BAD SHEET IS REPORTED, not the first. A copy handed back with two
        malformed sheets is two things to fix, and a parse that stopped at the
        first would make the second invisible until the next run.

        Args:
            where: how to name this copy in a message.
            data: one edit_copy, as `flows.distribute.seed` builds one.

        Returns:
            `(EditCopy, [])` or `(None, [messages])`.
        """
        if not isinstance(data, dict):
            return None, [f"{where}: an edit_copy must be an object"]
        # !! DECLARED, NOT NARROWED, because the read at `checked["read_from"]`
        # below sits past a loop. An `isinstance` narrow is invalidated at a loop
        # back-edge, so `ty` loses it before that read; an explicit annotation is
        # a declaration and survives.
        checked: dict = data
        role = checked.get("role")
        if not filled(role):
            return None, [f"{where}: an edit_copy needs the `role` that wrote it"]
        why_header = _read_from_problem(checked)
        if why_header:
            return None, [f"{where}: {role}'s {why_header}"]
        raw_sheets = checked.get("sheets")
        if not isinstance(raw_sheets, list):
            return None, [f"{where}: {role} needs a `sheets` list"]
        sheets: list[Sheet] = []
        problems: list[str] = []
        for i, raw in enumerate(raw_sheets, 1):
            sheet, why = Sheet.deserialize(f"{where}: {role} sheet {i}", raw)
            if sheet is None:
                problems += why
            else:
                sheets.append(sheet)
        if problems:
            return None, problems
        return (
            EditCopy(
                role=role,
                # ! COPIED, NOT ALIASED -- `bind`, `seed` and `gather` all do the
                # same with this field, so a caller mutating its own dict cannot
                # change what a parsed copy already holds.
                read_from={**checked["read_from"]},
                sheets=tuple(sheets),
            ),
            [],
        )

    def serialize(self) -> dict:
        """This edit_copy as the wire dict, the shape `seed` writes.

        ! `read_from` IS COPIED, NOT ALIASED, matching `seed` and every other
        producer of this field.
        """
        return {
            "role": self.role,
            "read_from": {**self.read_from},
            "sheets": [sheet.serialize() for sheet in self.sheets],
        }


@dataclass(frozen=True)
class MasterProof:
    """Every `edit_copy` of one stage, gathered.

    Attributes:
        stage: the label the copies were dispatched under -- `SKILL.md`'s "4a",
            "4c".
        read_from: taken from the first copy; `desk.proof.gather` refuses a set
            that disagrees.
        edit_copies: one per role, or one per SHARD under fan-out.
    """

    stage: str
    read_from: dict
    edit_copies: tuple[EditCopy, ...]

    @classmethod
    def seed(cls, stage: str, read_from: dict, edit_copies: list) -> dict:
        """One master_proof as the wire dict `desk.proof.gather` returns.

        Args:
            stage: the label these copies were dispatched under.
            read_from: taken from the first copy by `gather`, which refuses a
                set that disagrees.
            edit_copies: one `EditCopy.seed` dict per role, or per SHARD under
                fan-out. Held in the order given: nothing is sorted, nothing is
                dropped.

        Returns:
            `{stage, read_from, edit_copies}`, `read_from` copied not aliased.
        """
        return _written(
            cls,
            {
                "stage": stage,
                "read_from": {**read_from},
                "edit_copies": list(edit_copies),
            },
        )

    @classmethod
    def deserialize(
        cls, where: str, data: object
    ) -> "tuple[MasterProof | None, list[str]]":
        """One master_proof and every copy under it, checked.

        Args:
            where: how to name this proof in a message -- its stage label.
            data: a master_proof, as `desk.proof.gather` returns one.

        Returns:
            `(MasterProof, [])` or `(None, [messages])`. Every bad copy is
            reported, and so is a `read_from` that fails `_read_from_problem` --
            the same check `EditCopy.deserialize` runs on an edit_copy's own field --
            or that disagrees with the first edit_copy's, which is the
            disagreement `desk.proof.gather` itself refuses with
            `MismatchedRoot` before a master_proof is ever built.

            ! THE SHAPE CHECK RUNS WHETHER OR NOT THERE ARE COPIES, since
            2026-08-31; the COMPARISON needs a first copy and still only runs
            where there is one. The single exemption is an empty proof whose
            `read_from` is `{}` or absent, which is what `gather` writes when it
            had no first copy to take one from.
        """
        if not isinstance(data, dict):
            return None, [f"{where}: a master_proof must be an object"]
        raw_copies = data.get("edit_copies")
        if not isinstance(raw_copies, list):
            return None, [f"{where}: a master_proof needs an `edit_copies` list"]
        copies: list[EditCopy] = []
        problems: list[str] = []
        for i, raw in enumerate(raw_copies, 1):
            copy, why = EditCopy.deserialize(f"{where}: edit_copy {i}", raw)
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
        # ! `{}` IS STILL ADMITTED, AND ONLY FOR AN EMPTY PROOF. `desk.proof.gather`
        # writes it when there is no first copy to take a `read_from` from, so
        # refusing it would refuse a shape the producer itself makes. That is the
        # one exemption; it is not a licence for every other value.
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
        return (
            MasterProof(
                stage=stage,
                read_from={**read_from} if isinstance(read_from, dict) else {},
                edit_copies=tuple(copies),
            ),
            [],
        )

    def serialize(self) -> dict:
        """This master_proof as the wire dict, the shape `gather` returns."""
        return {
            "stage": self.stage,
            "read_from": {**self.read_from},
            "edit_copies": [copy.serialize() for copy in self.edit_copies],
        }
