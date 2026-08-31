r"""The containers a mark travels in -- the sheet, the edit_copy, the master_proof.

    Sheet              one PAGE's marks, with that page's path and sha
    EditCopy           one ROLE's sheets, with the binder it was seeded from
    MasterProof        one STAGE's edit_copies
    parse_sheet()      the boundary parse for one sheet
    parse_edit_copy()  for one edit_copy, and every sheet under it
    parse_master_proof()  for one master_proof, and every copy under it

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

    write   flows.distribute.seed, flows.collate._chief_copy,
            flows.collate._nothing_settled, desk.proof.gather
    read    flows.collate.collate, at its inbound boundary and after `gather`

! THE PARSES HAD NO PRODUCTION CALLER UNTIL 2026-08-31, and this file said so
for as long as that was true. `P21` closed it: `collate` runs `parse_edit_copy`
over every returned copy and `parse_master_proof` over what `gather` builds,
so **every refusal declared below can now fire.**

!! THIS FILE STATES WHAT THE TWO BOUNDARIES ARE, AND NOTHING ELSE RESTATES IT.
A container guards the **ENVELOPE** -- is this document the shape a copy must
be -- while `desk.collator.problems_in` rules on the **CONTENTS**, so each
per-mark problem routes back to the role that wrote it. They are not competing
contracts, and both run. ! `flows/collate.py` owns the ORDER and the RESPONSE
(envelope first; reported, not raised) and cites this paragraph rather than
repeating it -- a rule in two places is a rule that will disagree with itself.

! THE CHIEF'S COPY IS AN ORDINARY `EditCopy`. `Vocabulary: #30`: after the fold
every place has exactly one answer, and one mark per place is an ordinary copy.
There is no second shape and no second parse.

! `marks` IS TYPED `tuple[object, ...]`, matching `Mark.sources` and for the
same reason: an entry that is not an object is CARRIED so `desk.mark.parse` can
refuse it by name. Filtering to dicts here would make a bare string vanish
instead of being flagged.
"""

from dataclasses import dataclass, fields

from comment_review.binder.binder import _read_from_problem
from comment_review.desk.mark import filled


def _written(cls, values: dict) -> dict:
    """One container as the wire dict, keyed by `cls`'s OWN field names.

    !! THE WRITE HALF OF THE ROUND TRIP LIVES WITH THE READ HALF, ruled
    `decision-log.md Process: #64`. It is `desk.mark.Mark.seed`'s guard one
    level up: every producer spelled these keys as literals, so renaming a
    field left another module writing the old key and NOTHING could notice --
    `parse_sheet` folds an absent `sha` to `""` and reports no problem, where
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
    declared = [f.name for f in fields(cls)]
    if set(values) != set(declared):
        raise AttributeError(
            f"{cls.__name__}.seed writes {sorted(values)}, "
            f"which is not {cls.__name__}'s {sorted(declared)}"
        )
    return {name: values[name] for name in declared}


@dataclass(frozen=True)
class Sheet:
    """One page's marks, inside the `edit_copy` that seeded them.

    Attributes:
        path: the page's real repo path, as the binder stated it.
        sha: that page's sha when it was censused. Read by `docket_from`, which
            writes it onto the docket page so the setter can refuse a page that
            moved underneath the run.
        marks: one entry per place on the page, as they came back.
    """

    path: str
    sha: str
    marks: tuple[object, ...]

    @classmethod
    def seed(cls, path: str, sha: object, marks: list) -> dict:
        """One sheet as the wire dict every producer writes.

        !! `sha` IS NORMALIZED HERE, AND THIS IS THE ONE PLACE THAT DOES IT.
        `.get("sha", "")` defaults only when the key is ABSENT, so a `"sha":
        null` binder page arrives with the key PRESENT and holding None, and
        `str(None)` is the four-character word "None". `flows.distribute.seed`
        and `parse_sheet` each carried this fold; a rule stated twice is a rule
        that will disagree with itself.

        Args:
            path: the page's real repo path, as the binder stated it.
            sha: that page's sha, or anything that is not a `str` -- an absent
                or null sha becomes "".
            marks: the entries for this page, carried as given.

        Returns:
            `{path, sha, marks}` -- what `parse_sheet` reads back.
        """
        return _written(
            cls,
            {
                "path": path,
                "sha": sha if isinstance(sha, str) else "",
                "marks": list(marks),
            },
        )


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


def parse_sheet(where: str, data: object) -> tuple[Sheet | None, list[str]]:
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
    # says it is "matching `desk.containers.parse_sheet`". This pair is the
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
    return Sheet(path=path, sha=sha, marks=tuple(marks)), []


def parse_edit_copy(where: str, data: object) -> tuple[EditCopy | None, list[str]]:
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
        sheet, why = parse_sheet(f"{where}: {role} sheet {i}", raw)
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


def parse_master_proof(
    where: str, data: object
) -> tuple[MasterProof | None, list[str]]:
    """One master_proof and every copy under it, checked.

    Args:
        where: how to name this proof in a message -- its stage label.
        data: a master_proof, as `desk.proof.gather` returns one.

    Returns:
        `(MasterProof, [])` or `(None, [messages])`. Every bad copy is
        reported, and so is a `read_from` that fails `_read_from_problem` --
        the same check `parse_edit_copy` runs on an edit_copy's own field --
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
        copy, why = parse_edit_copy(f"{where}: edit_copy {i}", raw)
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
    # carried into `MasterProof.read_from` VERBATIM. Those are exactly the two
    # `desk.collator.problems_in`'s own comment records as the reason it reused
    # instead of a hand-rolled `isinstance(..., dict) and truthy` -- so the
    # validator had re-acquired the defect its own comment exists to explain.
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
    # `parse_sheet` and `parse_master_proof` each already guard.
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
