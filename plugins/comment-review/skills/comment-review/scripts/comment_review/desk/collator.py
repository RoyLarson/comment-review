"""`collator.py`'s two named steps -- source-verification, and reconciliation.

    known_addresses(binder)     every place the binder still carries
    address_problems(...)       T3.1 -- does the address resolve
    claim_verbatim_problems(...) T3.3 -- is the quoted sentence really in the
                                 paragraph
    source_problems(...)        T3.2 -- does every `source` resolve, with its
                                 `verbatim` within reach of the cited line
    source_verification(...)    all three, over one mark
    places(proof)                T4.1 -- one stage's marks, grouped by every
                                 place each TOUCHES
    reconcile(proof)             T4.2 -- `Process: #49`: settle, escalate, or
                                 send a place back for a re-read
    docket_from(reconciled, proof) T4.5 -- reconciliation's SETTLED places,
                                 packaged as the docket the write chain reads

`decision-log.md Vocabulary: #19` names the module and its two steps, keyed on
scope: source-verification is per MARK, against the page it rules on;
reconciliation is per PLACE, across the marks of one stage. **THE COLLATOR
RULES ON NOTHING** (`Vocabulary: #11`) -- every function below reports; none
of them decides what a mark should have said. `reconcile` counts and compares
what each mark already claims (how many marks at a place owe a change, and
whether they name the same sentence); it never judges which mark is right,
never renders the composed text, and never reads a file.

!! TWO OF THE THREE CHECKS COST NO FILE READ, because of `flows/marks.py`'s
`seed()`: the address and the paragraph's own `raw_text` are already on the
row a role filled in, so `address_problems` and `claim_verbatim_problems` read
only the mark. Only `source_problems` opens a file -- one per CITED file, read
once and cached, since 706 recorded marks carried 382 citations over 9 roots.

!! NO SHA CHECK, AND NO RE-READING THE PAGE THIS MARK RULES ON. Roy,
2026-08-28: *"Too early for the strictness and the look up time each time."*
A stale mark surfaces later, through the proof-setter pass -- not here.
"""

from pathlib import Path
from typing import NamedTuple

from comment_review.binder.binder import rows_of
from comment_review.desk.mark import INSTRUCTIONS, Instruction
from comment_review.machine.exceptions import READ_ERRORS
from comment_review.reading.addresser import cue_of, flatten, unflatten

#: `reviewer-brief.md`: "your text must appear within three lines" of the
#: cited line -- lines either side of it that a `source`'s `verbatim` may sit
#: in.
WITHIN = 3

#: A per-file cache -- `path` (relative to the root a `source` cites into) ->
#: its lines, or `None` when the file could not be read. Built fresh per run
#: and threaded through, so a stale entry never survives past one caller.
Cache = dict[str, tuple[str, ...] | None]


def known_addresses(binder: dict) -> frozenset[str]:
    """Every address the binder still carries -- what T3.1 checks a mark against."""
    return frozenset(
        row["address"] for row in rows_of(binder) if row.get("address")
    )


def address_problems(where: str, mark: dict, known: frozenset[str]) -> list[str]:
    """T3.1 -- the address resolves to a place the binder carries.

    ! Only fires when `address` is present: `clean` is not substantive and
    owes none, and a `mark` seeded onto a sheet always carries one, so a
    missing address here is `desk.mark.problems`'s question, not this one's.
    """
    address = mark.get("address")
    if isinstance(address, str) and address and address not in known:
        return [f"{where}: `address` {address!r} names no place the binder carries"]
    return []


def claim_verbatim_problems(where: str, mark: dict) -> list[str]:
    """T3.3 -- the sentence the claim rules on is really in the paragraph.

    The VERBATIM classifier (`Row.quotes_original`) names the one
    `claim` key checked this way -- `false` for `correct`, `drop` for `drop`,
    `from` for `patch`; the other four quote nothing. Reads `mark["raw_text"]`,
    the paragraph `seed()` put on the row -- no file, no re-read.
    """
    instruction = mark.get("mark")
    spec = INSTRUCTIONS.get(instruction) if isinstance(instruction, str) else None
    key = spec.quotes_original if spec is not None else ""
    if not key:
        return []
    claim = mark.get("claim")
    value = claim.get(key) if isinstance(claim, dict) else None
    if not isinstance(value, str) or not value.strip():
        # ! A missing or empty claim key is `desk.mark.problems`'s question --
        # it already refuses this shape before source-verification would run.
        return []
    raw_text = mark.get("raw_text")
    if not isinstance(raw_text, str) or value not in raw_text:
        return [f"{where}: `claim.{key}` is not in the paragraph this row seeded"]
    return []


def _cite_at(cite: str) -> tuple[str, int] | None:
    """`path:line` split apart, or `None` -- `reviewer-brief.md`'s own form."""
    path, sep, line = cite.rpartition(":")
    if not sep or not path or not line.strip().isdigit():
        return None
    lineno = int(line)
    return (path, lineno) if lineno >= 1 else None


def _lines(root: Path, path: str, cache: Cache) -> tuple[str, ...] | None:
    """A cited file's lines, read once per `path` and kept in `cache`."""
    if path not in cache:
        try:
            text = (root / path).read_text(encoding="utf-8")
        except READ_ERRORS:
            cache[path] = None
        else:
            cache[path] = tuple(text.splitlines())
    return cache[path]


def source_problems(where: str, mark: dict, root: Path, cache: Cache) -> list[str]:
    """T3.2 -- every `source` resolves, its `verbatim` within reach of the cite.

    !! A BARE-STRING SOURCE IS REFUSED, NOT DROPPED, per a finding tracked in
    `TODO/`: a retired reader filtered `sources` to dicts before its own check
    ever ran, so a bare string vanished rather than being flagged. This loop
    walks `sources` as handed and reports on every entry, dict or not.
    """
    sources = mark.get("sources")
    if not isinstance(sources, list):
        return []
    out = []
    for i, source in enumerate(sources, 1):
        at = f"{where}: source {i}"
        if not isinstance(source, dict):
            out.append(f"{at} is not an object -- a bare string cannot be resolved")
            continue
        cite = source.get("cite")
        verbatim = source.get("verbatim")
        if not isinstance(cite, str) or not cite.strip():
            continue  # `desk.mark.problems`'s question, not this one's.
        parsed = _cite_at(cite)
        if parsed is None:
            out.append(f"{at}: `cite` {cite!r} is not `path:line`")
            continue
        path, lineno = parsed
        lines = _lines(root, path, cache)
        if lines is None:
            out.append(f"{at}: `cite` {cite!r} does not resolve -- the file "
                        "cannot be read")
            continue
        if lineno > len(lines):
            out.append(f"{at}: `cite` {cite!r} names a line past the end of "
                        "the file")
            continue
        if not isinstance(verbatim, str) or not verbatim.strip():
            continue  # `desk.mark.problems`'s question, not this one's.
        lo = max(0, lineno - 1 - WITHIN)
        hi = min(len(lines), lineno + WITHIN)
        window = "\n".join(lines[lo:hi])
        if verbatim not in window:
            out.append(
                f"{at}: `verbatim` is not within {WITHIN} lines of {cite}"
            )
    return out


def source_verification(
    where: str, mark: dict, *, known: frozenset[str], root: Path, cache: Cache
) -> list[str]:
    """T3.1 + T3.2 + T3.3, over one mark -- every check this step owns.

    Args:
        where: how to name this mark in a message -- its address, or a
            position.
        mark: one role's ruling on one place, as a filled sheet entry --
            carrying `address`, `raw_text` and `mark` from `seed()`, plus
            `claim` and `sources` from the role.
        known: every address the binder carries -- `known_addresses(binder)`.
        root: the checkout `sources` cite into.
        cache: a per-file line cache, built once per run and passed to every
            call so a repeated citation costs one read.

    Returns:
        One message per broken rule. Empty means source-verification found
        nothing to refuse -- it says nothing about whether the mark is right.
    """
    return (
        address_problems(where, mark, known)
        + claim_verbatim_problems(where, mark)
        + source_problems(where, mark, root, cache)
    )


def verify_report(report: dict, binder: dict, root: Path) -> list[str]:
    """Source-verification over a whole filled `edit_copy`.

    The shape `flows.marks.seed()` hands out, after a role filled it in --
    one sheet per page, walked in turn, then each sheet's `marks`.

    ! Skips an unruled entry (`mark` is `None`) the same way
    `flows.marks.problems_in` does -- a coverage gap is not a problem this
    step reports.
    """
    sheets = report.get("sheets")
    if not isinstance(sheets, list):
        return []
    known = known_addresses(binder)
    cache: Cache = {}
    out: list[str] = []
    i = 0
    for sheet in sheets:
        marks = sheet.get("marks") if isinstance(sheet, dict) else None
        if not isinstance(marks, list):
            continue
        for mark in marks:
            i += 1
            if not isinstance(mark, dict) or mark.get("mark") is None:
                continue
            where = str(mark.get("address") or f"mark {i}")
            out += source_verification(
                where, mark, known=known, root=root, cache=cache
            )
    return out


def _touches(mark: dict) -> list[str]:
    """Every place one mark reaches -- its own `address`, plus a `move`'s `claim.to`.

    ! `move` is the one instruction naming two places: `claim.from` is the
    same as the mark's own `address`, so only `claim.to` adds a second.
    """
    touched = []
    address = mark.get("address")
    if isinstance(address, str) and address:
        touched.append(address)
    if mark.get("mark") == Instruction.MOVE:
        claim = mark.get("claim")
        destination = claim.get("to") if isinstance(claim, dict) else None
        if isinstance(destination, str) and destination and destination not in touched:
            touched.append(destination)
    return touched


def places(proof: dict) -> dict[str, list[dict]]:
    """T4.1 -- one stage's marks, grouped by every place each TOUCHES.

    `decision-log.md Vocabulary: #19`'s reconciliation step, per PLACE across
    the marks of one stage. `collate-buckets-a-move-at-one-end`: a `move` from
    `a0` to `a8` grouped only under `a0` never meets another role's mark on
    `a8`, so the two are decided as if they never touched the same text. This
    groups a `move` into BOTH buckets instead.

    Args:
        proof: a `master_proof`, as `desk.proof.gather` returns it.

    Returns:
        address -> the marks touching it, each a copy of the role's mark with
        the role that made it added under `role`. An unruled entry (`mark` is
        `None`) is skipped, the same coverage-gap rule `verify_report` and
        `flows.marks.problems_in` use. `clean` marks group like any other
        instruction -- what a group of marks at one place MEANS is
        reconciliation's settle/escalate step, not this one's.
    """
    out: dict[str, list[dict]] = {}
    for copy in proof.get("edit_copies", []):
        role = copy.get("role")
        for sheet in copy.get("sheets", []):
            marks = sheet.get("marks") if isinstance(sheet, dict) else None
            if not isinstance(marks, list):
                continue
            for mark in marks:
                if not isinstance(mark, dict) or mark.get("mark") is None:
                    continue
                entry = {**mark, "role": role}
                for address in _touches(mark):
                    out.setdefault(address, []).append(entry)
    return out


class Reconciled(NamedTuple):
    """T4.2's outcome -- every place `places()` grouped, sorted into three.

    Attributes:
        settled: one mark owed a change here -- nobody composed anything.
        escalations: two or more marks owed a change here and named the same
            sentence -- the conflict case.
        rereads: two or more marks owed a change here and named different
            sentences -- their composition is text no role has read. An
            `add` lands here too, however many marks own the place: an `add`
            creates prose nobody has read, so its own place is always a
            re-read (`decision-log.md Process: #49`, second bullet).

    !! A `move` APPEARS IN ONE OF THE THREE AT BOTH OF ITS ENDS, never in two
    of them (`_join_moves`) -- so a caller reading `settled` alone never sees
    half of one.

    Each entry is `{"address": ..., "roles": [...], "marks": [...]}` -- the
    role names and the owing marks themselves, so a later phase can send a
    `reread` back to exactly the roles that touched it. For an `add`'s
    re-read, `roles` is not only the roles that marked THIS place -- see
    `reconcile`.
    """

    settled: list[dict]
    escalations: list[dict]
    rereads: list[dict]


def _owes_change(mark: dict) -> bool:
    """Whether `mark`'s instruction is one of the five that owe a change.

    Read off `INSTRUCTIONS[...].owes_change` -- False for exactly `clean`
    and `query` -- rather than the two names retyped here.
    """
    instruction = mark.get("mark")
    spec = INSTRUCTIONS.get(instruction) if isinstance(instruction, str) else None
    return spec.owes_change if spec is not None else False


def _sentence_key(mark: dict) -> object:
    """Which sentence a mark rules on, from its `claim` -- never `change`.

    (`TODO/change-is-raw-text-not-lines.md` is a known, filed contradiction
    this function does not depend on.)

    `INSTRUCTIONS[...].quotes_original` names the one `claim` key checked
    word-for-word against the paragraph -- `false` for `correct`, `drop` for
    `drop`, `from` for `patch`. `add` and `move` quote no existing sentence
    (`docs/the-mark.md`, "The classifiers"), so each such mark is given an
    identity of its own and can never be found to share a sentence with
    another mark.
    """
    instruction = mark.get("mark")
    spec = INSTRUCTIONS.get(instruction) if isinstance(instruction, str) else None
    key = spec.quotes_original if spec is not None else ""
    if key:
        claim = mark.get("claim")
        if isinstance(claim, dict):
            return claim.get(key)
    return id(mark)


def _roles_of_stage(proof: dict, path: str) -> set[str]:
    """Every role reachable at this page -- the `add` re-read's blast radius.

    `path` is the FLATTENED half of an address (`cue_of(address).path`,
    `addresser.flatten`'s own form). An `edit_copy`'s sheets carry the real,
    unflattened path (`flows.marks.seed` copies it straight off the binder's
    page), so each is flattened here before the comparison.

    ! ONE `edit_copy` PER ROLE, OR PER SHARD UNDER FAN-OUT (`desk/proof.py`).
    Walking every `edit_copy`'s sheets and keeping the ones whose `path`
    matches is what narrows to the SHARD holding this page, per
    `decision-log.md Process: #49`: *"all roles of the stage, and for a
    partitioned role only the shard holding that file."* A role's OTHER
    shards, covering other files, contribute nothing.

    Args:
        proof: a `master_proof`, as `desk.proof.gather` returns it.
        path: the flattened path half of the address in question.

    Returns:
        The role names whose `edit_copy` holds a sheet for this page --
        whether or not that role left a mark at the specific place asked
        about.
    """
    out: set[str] = set()
    for copy in proof.get("edit_copies", []):
        role = copy.get("role")
        if not isinstance(role, str):
            continue
        for sheet in copy.get("sheets", []):
            sheet_path = sheet.get("path") if isinstance(sheet, dict) else None
            if isinstance(sheet_path, str) and flatten(sheet_path) == path:
                out.add(role)
                break
    return out


#: The three outcomes a place can be given, WEAKEST FIRST -- the order
#: `_join_moves` compares when a `move`'s two ends were sorted differently.
#: `docs/the-mark.md`: *"a `move` escalated at EITHER place escalates WHOLE"*
#: -- so an escalation outranks a re-read. A settlement is the weakest of the
#: three because it is the only outcome that puts a place on the docket, and a
#: `move` may not be written at one end while the other is still being asked
#: about.
OUTCOMES = ("settled", "rereads", "escalations")


def _outcome(proof: dict, address: str, owing: list[dict]) -> tuple[str, dict]:
    """Which of `OUTCOMES` one place's change-owing marks fall into.

    The per-place half of `Process: #49` -- `reconcile`'s own docstring holds
    the rule and Roy's ruling behind it. This decides ONE place and can see
    nothing of any other, which is why `_join_moves` runs after it.

    Args:
        proof: a `master_proof` -- read only for an `add`'s blast radius.
        address: the place being ruled on.
        owing: the marks there whose instruction owes a change.

    Returns:
        `(one of OUTCOMES, the entry)` -- the entry in the shape
        `Reconciled` documents.
    """
    roles = {mark["role"] for mark in owing}
    if any(mark.get("mark") == Instruction.ADD for mark in owing):
        roles |= _roles_of_stage(proof, cue_of(address).path)
        kind = "rereads"
    elif len(owing) == 1:
        kind = "settled"
    elif len({_sentence_key(mark) for mark in owing}) == 1:
        kind = "escalations"
    else:
        kind = "rereads"
    return kind, {"address": address, "roles": sorted(roles), "marks": owing}


def _join_moves(outcomes: dict[str, tuple[str, dict]]) -> None:
    """Lift every `move` to the strongest outcome either of its ends was given.

    !! A `move` IS INDIVISIBLE (`docs/the-mark.md`): *"a `move` escalated at
    EITHER place escalates WHOLE. It may not be settled at one end and
    escalated at the other."* `_outcome` rules on one place at a time and
    cannot see the other end, so a `move` whose origin no other role marked
    settles there while its destination -- carrying a second role's mark --
    goes back for a re-read.

    !! MEASURED before this landed, on a `move` from `m.py@a0` to `m.py@a8`
    against another role's `correct` on `a8`: `settled` held `a0` alone, so the
    docket
    DELETED the origin and never wrote the destination and the moved paragraph
    was lost. With the second role's mark on `a0` instead, the destination
    settled alone and the paragraph was written twice. Both dockets are well
    formed, `prove_unchanged` passes on either -- only prose moved -- so
    nothing downstream can disagree.

    ! IT RUNS HERE, NOT IN `docket_from`, so the rule holds for EVERY reader of
    a `Reconciled`. The revise step asks a role about a re-read; half a `move`
    in that list is the same defect one stage later, and a rule applied where
    the docket is packaged would leave it there.

    ! TO A FIXED POINT, because a lift can meet a second `move`: `a0 -> a8` and
    `a16 -> a8` share a place, so lifting `a8` carries `a0` and `a16` with it,
    and either of those may be an end of a further `move`.

    Args:
        outcomes: address -> `(one of OUTCOMES, the entry)`, as `_outcome`
            built each. MUTATED in place -- only an outcome ever changes, never
            an entry.
    """
    ends_of = {
        tuple(_touches(mark))
        for _, entry in outcomes.values()
        for mark in entry["marks"]
        if mark.get("mark") == Instruction.MOVE and len(_touches(mark)) > 1
    }
    changed = True
    while changed:
        changed = False
        for ends in ends_of:
            strongest = max((outcomes[end][0] for end in ends), key=OUTCOMES.index)
            for end in ends:
                kind, entry = outcomes[end]
                if kind != strongest:
                    outcomes[end] = (strongest, entry)
                    changed = True


def reconcile(proof: dict) -> Reconciled:
    """T4.2 -- `Process: #49`: settle, escalate, or send a place for a re-read.

    Roy, 2026-08-29: *"If two roles have a mark that edits a paragraph - I
    think we need to send the revision back to them because they could have
    fixed the same defect in different ways that then causes a new defect. To
    ensure that the reading still sticks together any composition of edits
    has to be re-read. The only two that get a pass is query and clean."*

    Counts, at every place `places()` groups, the marks whose instruction
    OWES A CHANGE:

        0                          nothing
        1, none of them `add`      settle -- nobody composed anything
        2+, different sentences    a re-read -- the composition is text no
                                   role has read
        2+, same sentence          escalate -- the conflict case
        any of them `add`          a re-read, however many -- see below

    !! AN `add` IS ALWAYS A RE-READ, EVEN ALONE. `decision-log.md Process:
    #49`, second bullet, Roy: *"Or they could have duplicated the comment. An
    add on a new place is sent back to all of them."* Two `add`s at two
    addresses never meet under this per-place grouping, so a duplicated
    comment would pass every check unless the place itself always re-reads
    and the re-read reaches every role that could hold the duplicate --
    `_roles_of_stage` -- not only the role that wrote this `add`.

    !! AND A `move` IS DECIDED ONCE, ACROSS BOTH OF ITS PLACES. The table above
    rules on one place at a time, so it can settle a `move`'s origin while
    sending its destination back; `_join_moves` then lifts both ends to the
    stronger of the two outcomes, because a `move` is indivisible
    (`docs/the-mark.md`) and no docket may carry one end of one.

    ! `clean` and `query` NEVER OWE A CHANGE (`_owes_change`), which is what
    already keeps a scope-declaring `query` (`Shape.OUTSIDE_MY_ROLE`) and an
    `unable-to-determine` one from blocking another role's owing mark at the
    same place: neither is ever counted into `owing`, so a place carrying one
    of those plus a single substantive mark elsewhere still settles on that
    one mark (`decision-log.md Process: #33`).

    Args:
        proof: a `master_proof`, as `desk.proof.gather` returns it.

    Returns:
        A `Reconciled` -- see its own docstring for each list's shape. A
        place with no change-owing mark (every mark there is `clean` or
        `query`) appears in none of the three.
    """
    outcomes: dict[str, tuple[str, dict]] = {}
    for address, marks in places(proof).items():
        owing = [mark for mark in marks if _owes_change(mark)]
        if owing:
            outcomes[address] = _outcome(proof, address, owing)
    _join_moves(outcomes)
    settled: list[dict] = []
    escalations: list[dict] = []
    rereads: list[dict] = []
    into = {"settled": settled, "escalations": escalations, "rereads": rereads}
    for kind, entry in outcomes.values():
        into[kind].append(entry)
    return Reconciled(settled, escalations, rereads)


def _real_pages(proof: dict) -> tuple[list[str], dict[str, str]]:
    """Every page an `edit_copy` was seeded over -- its real path, and its sha.

    An address carries only the FLATTENED path half; the real one, and the
    sha `docket_from` must record, live on the sheets `flows.marks.seed`
    already put the page's own `path` and `sha` onto.
    """
    paths: list[str] = []
    shas: dict[str, str] = {}
    for copy in proof.get("edit_copies", []):
        for sheet in copy.get("sheets", []):
            path = sheet.get("path") if isinstance(sheet, dict) else None
            if isinstance(path, str) and path and path not in shas:
                paths.append(path)
                shas[path] = str(sheet.get("sha", ""))
    return paths, shas


def _alteration_text(address: str, mark: dict) -> str | None:
    """The docket's `text` for one settled mark's `change` -- joined, or `None`.

    !! A `move`'s ORIGIN IS A DELETE, NEVER ITS `change`. `_touches` groups a
    `move` mark into both its own `address` (the origin, where the paragraph
    is REMOVED) and `claim.to` (the destination, where `change` is WRITTEN),
    so the same mark reaches here twice under two different `address`
    arguments. Comparing `address` to the mark's OWN `address` is what tells
    the two apart -- equal means this call is for the origin.

    Args:
        address: the place this docket entry is FOR -- a settled entry's own
            `address`, which for a `move` may be either end.
        mark: the one owing mark that settled this place.

    Returns:
        `None` (delete) at a `move`'s origin, or when `change` is empty --
        the shape `may_empty` allows for exactly `drop`. Otherwise `change`'s
        lines joined with a newline.
    """
    if mark.get("mark") == Instruction.MOVE and address == mark.get("address"):
        return None
    change = mark.get("change")
    lines = change if isinstance(change, list) else []
    return "\n".join(lines) if lines else None


def docket_from(reconciled: Reconciled, proof: dict) -> dict:
    """T4.5 -- `reconciled.settled`, packaged as the docket the write chain reads.

    !! ONLY `settled` BECOMES A DOCKET. An escalation or a re-read names a
    place two or more marks owe a change to and no single mark can answer
    for alone -- the copy chief that would decide between them is out of
    0.2.4 (`Process: #42`), so there is nothing yet to write for those
    places.

    Args:
        reconciled: `reconcile(proof)`'s outcome.
        proof: the same `master_proof` `reconciled` was derived from -- read
            here only for the real page paths and shas its `edit_copies`'
            sheets carry; nothing here reads a file or re-reads a page.

    Returns:
        `{"pages": [{"path", "sha", "role", "alterations": [...]}]}`, one
        page per REAL path a settled place touches. `docket.read` rules on
        this shape; nothing here does.

    !! `role` IS ONE PER PAGE, matching `docket.read`'s own schema and
    `flows.revise.pull._set_by`, which reads it the same way -- so a page whose
    settled places were set by MORE THAN ONE role carries no `role` at all, and
    `_set_by` maps its addresses to `""`. **A FALSE ATTRIBUTION IS WORSE THAN
    AN ABSENT ONE**: `set_by` is the provenance a later phase (P6) ROUTES on
    (`flows.revise.Pulled`), so naming a role that never touched the place
    sends its reversal to someone who cannot answer for it. MEASURED --
    `block-context` settling `m.py@b1` and `module-context` settling `m.py@b3`
    mapped BOTH to `module-context`. Carrying the role per ALTERATION is a
    change to the docket format, filed in `TODO/`.
    """
    paths, shas = _real_pages(proof)
    pages: dict[str, dict] = {}
    roles_of: dict[str, set[str]] = {}
    for entry in reconciled.settled:
        address = entry["address"]
        mark = entry["marks"][0]
        role = entry["roles"][0]
        addr = cue_of(address)
        real_path = unflatten(addr.path, paths) or addr.path
        page = pages.setdefault(
            real_path,
            {
                "path": real_path,
                "sha": shas.get(real_path, ""),
                "role": role,
                "alterations": [],
            },
        )
        roles_of.setdefault(real_path, set()).add(role)
        page["alterations"].append(
            {"cue": addr.cue, "text": _alteration_text(address, mark)}
        )
    for real_path, page in pages.items():
        if len(roles_of[real_path]) != 1:
            del page["role"]
    return {"pages": list(pages.values())}
