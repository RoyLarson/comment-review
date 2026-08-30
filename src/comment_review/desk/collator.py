
from pathlib import Path
from typing import NamedTuple

from comment_review.binder.binder import rows_of
from comment_review.desk.mark import INSTRUCTIONS, Instruction, Mark, parse, untouched
from comment_review.machine import constants
from comment_review.machine.exceptions import READ_ERRORS
from comment_review.machine.repo import can_escape, read_raw
from comment_review.reading.addresser import cue_of, flatten, unflatten

WITHIN = 3

Cache = dict[str, tuple[str, ...] | None]

def known_addresses(binder: dict) -> frozenset[str]:
    return frozenset(
        row["address"] for row in rows_of(binder) if row.get("address")
    )

def address_problems(where: str, mark: Mark, known: frozenset[str]) -> list[str]:
    if mark.address and mark.address not in known:
        return [
            f"{where}: `address` {mark.address!r} names no place the binder carries"
        ]
    return []

def claim_verbatim_problems(where: str, mark: Mark, raw_text: str) -> list[str]:
    key = INSTRUCTIONS[mark.instruction].quotes_original
    if not key:
        return []
    value = mark.claim.get(key)
    if not isinstance(value, str) or not value.strip():
        return []
    if value not in raw_text:
        return [f"{where}: `claim.{key}` is not in the paragraph this row seeded"]
    return []

def _cite_at(cite: str) -> tuple[str, int] | None:
    path, sep, line = cite.rpartition(":")
    if not sep or not path or not line.strip().isdigit():
        return None
    lineno = int(line)
    return (path, lineno) if lineno >= 1 else None

def _lines(root: Path, path: str, cache: Cache) -> tuple[str, ...] | None:
    if path not in cache:
        try:
            text = read_raw(root / path)
        except READ_ERRORS:
            cache[path] = None
        else:
            cache[path] = tuple(constants.text_lines(text))
    return cache[path]

def source_problems(where: str, mark: Mark, root: Path, cache: Cache) -> list[str]:
    out = []
    for i, source in enumerate(mark.sources, 1):
        at = f"{where}: source {i}"
        if not isinstance(source, dict):
            out.append(f"{at} is not an object -- a bare string cannot be resolved")
            continue
        cite = source.get("cite")
        verbatim = source.get("verbatim")
        if not isinstance(cite, str) or not cite.strip():
            continue
        parsed = _cite_at(cite)
        if parsed is None:
            out.append(f"{at}: `cite` {cite!r} is not `path:line`")
            continue
        path, lineno = parsed
        if can_escape(path):
            out.append(f"{at}: `cite` {cite!r} names a path outside the "
                        "checkout")
            continue
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
            continue
        lo = max(0, lineno - 1 - WITHIN)
        hi = min(len(lines), lineno + WITHIN)
        window = "\n".join(lines[lo:hi])
        if verbatim not in window:
            out.append(
                f"{at}: `verbatim` is not within {WITHIN} lines of {cite}"
            )
    return out

def source_verification(
    where: str,
    mark: Mark,
    *,
    raw_text: str,
    known: frozenset[str],
    root: Path,
    cache: Cache,
) -> list[str]:
    return (
        address_problems(where, mark, known)
        + claim_verbatim_problems(where, mark, raw_text)
        + source_problems(where, mark, root, cache)
    )

def verify_report(report: dict, binder: dict, root: Path) -> list[str]:
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
        for entry in marks:
            i += 1
            if untouched(entry):
                continue
            where = str(
                (entry.get("address") if isinstance(entry, dict) else None)
                or f"mark {i}"
            )
            mark, why = parse(where, entry)
            if mark is None:
                out += why
                continue
            raw_text = entry.get("raw_text")
            out += source_verification(
                where,
                mark,
                raw_text=raw_text if isinstance(raw_text, str) else "",
                known=known,
                root=root,
                cache=cache,
            )
    return out

def _touches(mark: Mark) -> list[str]:
    touched = []
    if mark.address:
        touched.append(mark.address)
    if mark.instruction is Instruction.MOVE:
        destination = mark.claim.get("to")
        if isinstance(destination, str) and destination and destination not in touched:
            touched.append(destination)
    return touched

class UnnamedRole(Exception):
    pass

class MalformedMark(Exception):
    pass

class Placed(NamedTuple):

    mark: Mark
    role: str

def places(proof: dict) -> dict[str, list[Placed]]:
    out: dict[str, list[Placed]] = {}
    for i, copy in enumerate(proof.get("edit_copies", [])):
        role = copy.get("role")
        if not isinstance(role, str) or not role.strip():
            raise UnnamedRole(
                f"edit_copy {i} carries no `role` -- every mark it holds would "
                "be grouped under a name no reader can route on"
            )
        for sheet in copy.get("sheets", []):
            marks = sheet.get("marks") if isinstance(sheet, dict) else None
            if not isinstance(marks, list):
                continue
            for entry in marks:
                if untouched(entry):
                    continue
                where = str(
                    (entry.get("address") if isinstance(entry, dict) else None)
                    or f"a mark of {role}"
                )
                mark, why = parse(where, entry)
                if mark is None:
                    raise MalformedMark("; ".join(why))
                placed = Placed(mark, role)
                for address in _touches(mark):
                    out.setdefault(address, []).append(placed)
    return out

class Reconciled(NamedTuple):

    settled: list[dict]
    escalations: list[dict]
    rereads: list[dict]

def _owes_change(mark: Mark) -> bool:
    return INSTRUCTIONS[mark.instruction].owes_change

def _sentence_key(mark: Mark) -> object:
    key = INSTRUCTIONS[mark.instruction].quotes_original
    if key:
        return mark.claim.get(key)
    return id(mark)

def _roles_of_stage(proof: dict, path: str) -> set[str]:
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

OUTCOMES = ("settled", "rereads", "escalations")

def _outcome(proof: dict, address: str, owing: list[Placed]) -> tuple[str, dict]:
    roles = {placed.role for placed in owing}
    if any(placed.mark.instruction is Instruction.ADD for placed in owing):
        roles |= _roles_of_stage(proof, cue_of(address).path)
        kind = "rereads"
    elif len(owing) == 1:
        kind = "settled"
    elif len({_sentence_key(placed.mark) for placed in owing}) == 1:
        kind = "escalations"
    else:
        kind = "rereads"
    return kind, {"address": address, "roles": sorted(roles), "marks": owing}

def _join_moves(outcomes: dict[str, tuple[str, dict]]) -> None:
    ends_of = {
        tuple(_touches(placed.mark))
        for _, entry in outcomes.values()
        for placed in entry["marks"]
        if placed.mark.instruction is Instruction.MOVE
        and len(_touches(placed.mark)) > 1
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
    outcomes: dict[str, tuple[str, dict]] = {}
    for address, marks in places(proof).items():
        owing = [placed for placed in marks if _owes_change(placed.mark)]
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
    paths: list[str] = []
    shas: dict[str, str] = {}
    for copy in proof.get("edit_copies", []):
        for sheet in copy.get("sheets", []):
            path = sheet.get("path") if isinstance(sheet, dict) else None
            if isinstance(path, str) and path and path not in shas:
                paths.append(path)
                shas[path] = str(sheet.get("sha", ""))
    return paths, shas

def _alteration_text(address: str, mark: Mark) -> str | None:
    if mark.instruction is Instruction.MOVE and address == mark.address:
        return None
    return mark.change or None

def docket_from(reconciled: Reconciled, proof: dict) -> dict:
    paths, shas = _real_pages(proof)
    pages: dict[str, dict] = {}
    roles_of: dict[str, set[str]] = {}
    for entry in reconciled.settled:
        address = entry["address"]
        mark = entry["marks"][0].mark
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
