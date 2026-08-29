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
    """Source-verification over a whole filled sheet.

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
            sentences -- their composition is text no role has read.

    Each entry is `{"address": ..., "roles": [...], "marks": [...]}` -- the
    role names and the owing marks themselves, so a later phase can send a
    `reread` back to exactly the roles that touched it.
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
        1                          settle -- nobody composed anything
        2+, different sentences    a re-read -- the composition is text no
                                   role has read
        2+, same sentence          escalate -- the conflict case

    Args:
        proof: a `master_proof`, as `desk.proof.gather` returns it.

    Returns:
        A `Reconciled` -- see its own docstring for each list's shape. A
        place with no change-owing mark (every mark there is `clean` or
        `query`) appears in none of the three.
    """
    settled: list[dict] = []
    escalations: list[dict] = []
    rereads: list[dict] = []
    for address, marks in places(proof).items():
        owing = [mark for mark in marks if _owes_change(mark)]
        if not owing:
            continue
        entry = {
            "address": address,
            "roles": sorted({mark["role"] for mark in owing}),
            "marks": owing,
        }
        if len(owing) == 1:
            settled.append(entry)
            continue
        if len({_sentence_key(mark) for mark in owing}) == 1:
            escalations.append(entry)
        else:
            rereads.append(entry)
    return Reconciled(settled, escalations, rereads)
