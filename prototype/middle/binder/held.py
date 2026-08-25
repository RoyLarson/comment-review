"""Reading a record file back -- the third verb on the noun `record.py` owns.

That module WRITES one (`--seed`) and CHECKS one (`--check`); parsing one back
belongs with them. It sat in `verdicts.py` because the join was its first
caller, which is where a subject goes when nobody asks whose it is.

! A LIBRARY, not a command. `verdicts.py` is the entry point and this is what it
calls; there is no `held.py --help` to run.

!! IT READS ONE SHAPE. A reader kept for an older one is a shim, and a shim under
`plugins/` is copied into someone else's `.claude/` where an agent reads it as
current. Roy, 2026-08-21: *"leave no memory while it is easy, rather than leave
residues of stuff that will not make it."* ! What this used to read is in
`docs/history.md`, which does not ship.

! WHAT A CURRENT REPORT IS: one PAGE entry per file, naming the file once, and
one record per prose paragraph under it citing its PLACE. `record.every_record`
walks it; this puts the two halves of the address back together and turns each
filled slot into a `Finding`.
"""

import json
from pathlib import Path

from comment_review.binder.record import (
    Finding,
    _half,
    address_for,
    claim_text,
    every_record,
)


def held_records(report: dict):
    """Every record in a report, as `(address, record)`.

    !! THE FILE CARRIES THE TWO HALVES SEPARATELY: the PAGE names the file once
    and each record names only its PLACE. This is the seam that puts them back
    together, so everything below works on a full address.

    ! IT YIELDS WHAT IS THERE, INCLUDING AN ENTRY THAT IS NOT AN OBJECT and one
    that names no place -- the caller reports both, and a walk that filtered
    them reported a clean join over a report that was not.

    ! A REPORT IN ANY OTHER SHAPE YIELDS NOTHING, which is why `load_report`
    refuses one before reaching here: the caller counts the paragraphs nobody
    ruled on, so a report this cannot read would read as a total coverage gap.

    Args:
        report: the parsed record file.

    Yields:
        `(address, record)`. The address is "" where the record names no place.
    """
    for page, rec in every_record(report):
        if not isinstance(rec, dict):
            yield "", rec
            continue
        place = rec.get("place")
        yield (address_for(page, place.strip()) if isinstance(place, str) else ""), rec


def load_report(
    path: Path, text: str, reviewer: str
) -> tuple[list[Finding], list[str], list[str]]:
    """One reviewer's report.

    !! JSON IS THE ONLY SHAPE. `record.py --seed` writes it and a reviewer fills
    it, so nothing here guesses where a field ends -- the three defects that cost
    this system a day each were boundary guesses, and there are no boundaries
    left to guess.

    !! A REPORT THAT IS NOT `.json` IS REFUSED BY NAME. Nothing here parses any
    other shape: a reader kept for an older one is a shim, and a shim under
    `plugins/` is copied into someone else's `.claude/` where an agent reads it
    as current.

    ! IT TAKES THE TEXT rather than reading the file. The caller has already
    read it -- guarded, which this was not -- and the report was read twice and
    JSON-parsed twice, once here and once in `report_concerns`. The format
    decision was written out in both places too, and had to stay in agreement.

    Args:
        path: the report, whose SUFFIX must be `.json`.
        text: the file's contents.
        reviewer: the editorial role, taken from the file's stem by the caller.

    Returns:
        `(findings, malformed, code_concerns)`.
    """
    if path.suffix.lower() != ".json":
        why = (
            f"{path.name} is not a record file -- `record.py --seed` writes"
            " `<role>.json` and a reviewer fills it"
        )
        return ([], [why], [])
    try:
        report = json.loads(text)
    except json.JSONDecodeError as e:
        # ! Names its own position, which a merged field never could.
        return ([], [f"CANNOT PARSE as JSON ({e})"], [])
    # ! A top-level list parses as JSON and is not a report -- handing in the
    # CENSUS by mistake does exactly that. Every neighbouring read in this file
    # names the file and the reason in one line; this raised `AttributeError`
    # and took the whole join down.
    if not isinstance(report, dict):
        why = f"is a JSON {type(report).__name__}, not a report object"
        return ([], [why], [])
    # !! A REPORT WITH NO `pages` IS REFUSED, NOT READ AS EMPTY. The walk below
    # finds nothing in one and returns no findings AND no malformed, so the join
    # credits the reviewer with zero findings and reports every prose paragraph
    # as its coverage gap -- pointing the reader at the reviewer when the fault
    # is the file. ! Worse where the file carries `code_concerns`: those come
    # through, so the join PRINTS that reviewer's concerns beside the gap.
    if "pages" not in report:
        why = (
            f"{path.name} carries no `pages` list. A record file names one PAGE"
            " per file, with that page's records under it"
        )
        return ([], [why], [])
    findings: list[Finding] = []
    malformed: list[str] = []
    # !! THE ADDRESS IS THE KEY, AND `held_records` COMPOSED IT. The census index
    # was dropped 2026-08-19 -- it went stale the moment an `add` or a `drop`
    # shifted the list, while the address survives, and an address identifies
    # exactly one paragraph (measured: 0 shared over 6,180).
    for where, rec in held_records(report):
        # ! An ENTRY that is not an object. The guard above catches a report
        # that is not one; this catches a record inside a well-shaped report,
        # which `record.py --check` also reports and which raised
        # `AttributeError` here and took the whole join down.
        if not isinstance(rec, dict):
            malformed.append(f"a record is a {type(rec).__name__}, not an object")
            continue
        if rec.get("verdict") is None:
            # ! An unfilled slot is a COVERAGE gap, counted by the caller from
            # the findings it does not see. It is not a malformed record.
            continue
        if not where:
            place = rec.get("place")
            malformed.append(f"a record names the place {place!r}, which is no place")
            continue
        claim = rec.get("claim")
        # ! NORMALISED HERE, not at the constructor. `claim_text` does
        # `claim[m]`, and the type test sat 23 lines below the use -- so a
        # record carrying `"claim": "drop: the note"` -- what a hand-edited record
        # looks like, and what `record.py --check` reports -- took the whole join
        # down with a traceback.
        if not isinstance(claim, dict):
            claim = {}
        # ! ONE READ OF ONE FIELD. It was rendered twice, four characters apart,
        # for the same record.
        verdict = str(rec.get("verdict"))
        findings.append(
            Finding(
                reviewer=reviewer,
                verdict=verdict,
                claim=claim_text(verdict, claim),
                reason=str(rec.get("reason") or ""),
                # !! `filled` ON BOTH HALVES, because an f-string renders a
                # non-string into prose and the result is SEARCHED FOR. Measured
                # 2026-08-18: a source carrying `"verbatim": null` flattened to
                # `a.py:1 | None`, and `source_problem` then looked for the word
                # "None" near the cited line -- which a large share of Python
                # lines contain, so the citation PASSED. A verbatim that was
                # merely false was correctly refused; a null one was admitted.
                # Blanking it here makes the entry carry no verbatim half, which
                # `source_problem` already refuses by name.
                sources=[
                    f"{_half(s.get('cite'))} | {_half(s.get('verbatim'))}"
                    for s in rec.get("sources") or []
                    if isinstance(s, dict)
                ],
                # ! `str()` per line. `change` is a LINE ARRAY and `SHAPES`
                # checks only that it is a list, so a number in it raised
                # `TypeError` from `join` -- a crash the documented pre-flight
                # does not catch, on a file it calls well formed.
                change="\n".join(str(line) for line in rec.get("change") or []),
                address=where.strip(),
                # ! The record no longer carries the paragraph's text -- the census
                # does. `address_problem` reads this, so it is filled from the
                # census by the caller rather than by the reviewer.
                original="",
                claim_fields=claim,
            )
        )
    return (findings, malformed, [str(c) for c in (report.get("code_concerns") or [])])
