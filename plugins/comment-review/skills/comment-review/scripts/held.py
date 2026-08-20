"""Reading a report HELD from an earlier version -- the 0.2.x TEXT shape.

! A LIBRARY, not a command. `record.py --convert` is the entry point and this is
what it calls; there is no `held.py --help` to run.

!! `# noqa: vocabulary` -- THIS FILE IS ABOUT A FORMAT THAT NO LONGER SHIPS, so
it says `BLOCK` where the rest of the tree says PARAGRAPH, and it must. `BLOCK`
is the line MARKER a held report is written with and `Finding.block` is the
index such a record keys by; renaming either makes every report already on disk
unreadable. Measured 2026-08-19 during the rename: it did, on 173 of 173.

!! IT IS ITS OWN MODULE FOR THAT REASON. These 473 lines were 30% of
`record.py`, which announces ONE subject -- what a record IS -- and held two.
Every pass over the retired vocabulary had to thread guards through a single
file rather than skip a module, and six of them were found by breaking the
suite. Roy, 2026-08-19: *"let's give ourselves a `# noqa: vocabulary` out on the
files that are not about the prose or the current representation. Let's make
certain to move the code into separate files to make it easy."*

! IT READS; IT DOES NOT WRITE. Nothing here is emitted by a current run --
`record.seed` writes the shape that ships. This is the bridge to what is already
on disk, and `convert` refuses a report it cannot key: an index is a position in
ONE census, that census carries no addresses, and today's census of the same
source is a different list.

! THE DEPENDENCY RUNS ONE WAY. This imports `record`, never the reverse, so the
current representation does not know the retired one exists. `record.main`'s
`--convert` defers its import into the function body for that reason.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record import (  # noqa: E402  -- path shim must run first
    ANCHOR_NAME,
    CITE,
    CODE_CONCERNS,
    OPENER,
    PATHISH,
    VERDICTS,
    Finding,
    _half,
    _n,
    claim_text,
    entry_for,
    seed,
    slot,
)

# !! READING A REPORT IS THE THIRD VERB ON THE SAME NOUN. This module already
# WRITES a record file (`--seed`) and CHECKS one (`--check`); parsing one back
# belongs with them. It sat in `verdicts.py` because the join was its first
# caller, which is where a subject goes when nobody asks whose it is.
RECORD = re.compile(r"^---\s*RECORD\s*$(.*?)^---\s*$", re.M | re.S)


# !! ANCHORED AT COLUMN 0, which is what makes a continuation unambiguous. A
# field's value runs until the next label, and a label is only a label at the
# left margin -- so an indented line reading `CHANGE the budget` inside a
# transcribed paragraph is prose, not a new field.
#
# !! THE VALUE IS OPTIONAL, because a label with nothing after it is still a
# LABEL. `\s+` required at least one space, so a bare `CHANGE` line failed to
# match, fell into the continuation branch and was glued onto the field above
# it -- producing a SOURCES needle ending `... MAY LIVE.\nCHANGE`. The record
# was then refused for a citation whose verbatim half could not be found,
# rather than for the empty `CHANGE` that `payload_problem` was waiting to
# report. Measured 2026-08-17, on a live run.
#
# ! `CHANGES` still does not match: after the label the pattern needs
# whitespace or the end of the line, and `S` is neither.
FIELD = re.compile(r"^(BLOCK|VERDICT|SOURCES|CLAIM|REASON|CHANGE)(?:\s+(.*))?$")


def load_report(
    path: Path, text: str, reviewer: str
) -> tuple[list[Finding], list[str], list[str]]:
    """One reviewer's report, from either shape.

    !! JSON IS THE SHIPPED SHAPE. `record.py --seed` writes it and a reviewer
    fills it, so nothing here guesses where a field ends -- the three defects
    that cost this system a day each were boundary guesses, and there are no
    boundaries left to guess.

    ! The TEXT reader is kept and DEPRECATED, not deleted. A run already in
    flight, and every captured package on disk, is written in it -- and
    `record.py --convert` needs it to carry those forward. It is the only route
    by which a held run stays a regression test.

    ! IT TAKES THE TEXT rather than reading the file. The caller has already
    read it -- guarded, which this was not -- and the report was read twice and
    JSON-parsed twice, once here and once in `report_concerns`. The format
    decision was written out in both places too, and had to stay in agreement.

    Args:
        path: the report. Its SUFFIX chooses the reader: `.json` is a record
            file, anything else the 0.2.x text parser.
        text: the file's contents.
        reviewer: the editorial role, taken from the file's stem by the caller.

    Returns:
        `(findings, malformed, code_concerns)`, the same triple either way.
    """
    if path.suffix.lower() != ".json":
        findings, malformed = parse_report(text, reviewer)
        return (findings, malformed, code_concerns(text))
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
    findings: list[Finding] = []
    malformed: list[str] = []
    for rec in report.get("records") or []:
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
        # !! THE ADDRESS IS THE KEY. The census index was dropped 2026-08-19 --
        # it went stale the moment an `add` or a `drop` shifted the list, while
        # the address survives, and an address identifies exactly one paragraph
        # (measured: 0 shared over 6,180). A record with none cannot be joined.
        where = rec.get("address")
        if not isinstance(where, str) or not where.strip():
            malformed.append(f"a record carries address {where!r}, which names nothing")
            continue
        claim = rec.get("claim")
        # ! NORMALISED HERE, not at the constructor. `claim_text` does
        # `claim[m]`, and the type test sat 23 lines below the use -- so a
        # record carrying `"claim": "drop: the note"`, which is exactly what a
        # hand-converted 0.2.x record looks like and what `record.py --check`
        # reports, took the whole join down with a traceback.
        if not isinstance(claim, dict):
            claim = {}
        findings.append(
            Finding(
                reviewer=reviewer,
                verdict=str(rec.get("verdict")),
                claim=claim_text(str(rec.get("verdict")), claim),
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
                anchor=str(rec.get("anchor") or ""),
                # ! The record no longer carries the paragraph's text -- the census
                # does. `address_problem` reads this, so it is filled from the
                # census by the caller rather than by the reviewer.
                original="",
                claim_fields=claim,
            )
        )
    return (findings, malformed, [str(c) for c in (report.get("code_concerns") or [])])


def parse_report(text: str, reviewer: str) -> tuple[list[Finding], list[str]]:
    """Every record in one reviewer's report, `clean` included.

    Args:
        text: the report as the reviewer returned it. Prose around the records
            is ignored, so a reviewer may still explain itself.
        reviewer: the editorial role's name, attached to every finding it made.

    Returns:
        `(findings, malformed)`. Coverage is computed from the findings alone --
        a paragraph a reviewer never recorded is a paragraph it never accounted for.
        `malformed` holds one sentence per record that names no paragraph, which
        `main()` reports and counts fatal.

    ! A malformed record used to be a `Finding` carrying `block=-1`, and its
    reason was stuffed into `REASON`. That made one field mean two things,
    distinguished by a sentinel in another, and every consumer had to filter on
    the sentinel before reading anything. They are separate now, so `REASON`
    holds a reviewer's clause and only that.
    """
    found: list[Finding] = []
    malformed: list[str] = []
    bodies = RECORD.findall(text)
    openers = len(OPENER.findall(text))
    if openers != len(bodies):
        malformed.append(
            f"{_n(openers, 'RECORD opener')} but"
            f" {_n(len(bodies), 'closed record')}"
            " -- an unterminated record swallows the next one"
        )
    for body in bodies:
        fields: dict[str, str] = {}
        # ! SOURCES ACCUMULATES where every other field overwrites: a finding
        # may cite several places, one line each, and repeating the line avoids
        # a separator that verbatim text could contain. The name is plural for
        # that reason.
        sources: list[str] = []
        # !! A line that names no field CONTINUES the one above it, BLANK LINES
        # INCLUDED. `BLOCK` carries a transcribed paragraph and `CHANGE` carries a
        # replacement one, and a docstring has blank lines between its summary
        # and its `Args:` -- so a blank line is content here, not a separator.
        #
        # !! A blank line USED to end the continuation, and that single line
        # was the worst defect 0.2.0 shipped. Measured 2026-08-17: it truncated
        # both fields to their first paragraph on every paragraph containing a
        # blank line -- 33% of one census, ~450 paragraphs of another -- so
        # `ORIGINAL` could never match and `CHANGE` compared its unedited first
        # paragraph against itself and reported the paragraph UNCHANGED. It fell
        # hardest on the role doing the most work: 113 of one reviewer's 134
        # findings were refused, every one of them correct.
        #
        # ! Nothing is needed in its place. The record is bounded by its
        # `--- RECORD` and `---` lines, and a field ends at the next label.
        last: str | None = None
        for line in body.splitlines():
            m = FIELD.match(line)
            if not m:
                if last == "SOURCES" and sources:
                    # ! Under SOURCES a continuation is ambiguous: it is either
                    # the NEXT citation or the wrapped tail of the one above.
                    # A line that opens with `path:line` is the former; a
                    # verbatim half that happens to wrap is the latter.
                    # ! A blank line is neither -- a citation does not span one.
                    #
                    # !! A MALFORMED citation is the third case, and it used to
                    # be filed as the second. `CITE` fails on `b.py | text` just
                    # as it fails on a wrapped tail, so the bad entry was glued
                    # onto the entry ABOVE it -- which then could not find its
                    # own verbatim half, and the tool reported the error against
                    # that CORRECT citation while never naming the broken one.
                    # `PATHISH` splits them: a path-shaped left half is an entry
                    # of its own, admissible or not, so `source_problem` rules
                    # on it.
                    head = line.strip().partition("|")[0].strip()
                    if not line.strip():
                        pass
                    elif CITE.match(head) or ("|" in line and PATHISH.match(head)):
                        sources.append(line.strip())
                    else:
                        sources[-1] += "\n" + line.strip()
                elif last:
                    fields[last] += "\n" + line.rstrip()
                continue
            key = m.group(1)
            last = key
            # ! `or ""` because the value is OPTIONAL: a bare label matches with
            # group 2 unset, and an empty field is what `payload_problem` reads
            # to say the verdict carries no such payload.
            value = (m.group(2) or "").strip()
            if key == "SOURCES":
                sources.append(value)
            else:
                fields[key] = value
        # ! Blank lines INSIDE a field are content; blank lines trailing one are
        # the spacing between records. Only the trailing ones come off, so a
        # docstring keeps the gap above its `Args:` and `CHANGE` does not end
        # with the newline that preceded the next label.
        fields = {k: v.rstrip() for k, v in fields.items()}
        # !! BLOCK is `<index> | <path>:<start>-<end>`, and the lines under it
        # are that paragraph's text as the file reads it NOW. Only the index is
        # required to parse -- a `clean` writes it alone.
        raw = fields.get("BLOCK", "")
        head, _, addr = raw.partition("\n")[0].partition("|")
        raw_block = head.strip()
        if raw_block.isdecimal():
            found.append(
                Finding(
                    reviewer=reviewer,
                    block=int(raw_block),
                    verdict=fields.get("VERDICT", "").strip().lower(),
                    sources=sources,
                    claim=fields.get("CLAIM", ""),
                    # !! THE 0.2.x CLAIM IS TYPED HERE, at the one place the two
                    # formats meet. `claim_object` reads the markers back into
                    # the keys they always were, so a check downstream reads a
                    # FIELD whichever format the report arrived in. Before this,
                    # a text record left `claim_fields` empty and every check
                    # fell back to searching a rendered string for its own key.
                    claim_fields=claim_object(
                        fields.get("VERDICT", "").strip().lower(),
                        fields.get("CLAIM", ""),
                    ),
                    reason=fields.get("REASON", ""),
                    change=fields.get("CHANGE", ""),
                    address=addr.strip(),
                    original=raw.partition("\n")[2],
                )
            )
        else:
            malformed.append("a record with no PARAGRAPH index")
    return found, malformed


def code_concerns(text: str) -> list[str]:
    """The `CODE CONCERNS` lines a report carries, if it has the section.

    ! NOT a verdict and NOT gated. `reviewer-brief.md` sends a code problem here
    -- "one line each ... with no verdict" -- because a reviewer that opens the
    code to settle a comment will sometimes find the code wrong. Nothing here
    reads them for admissibility; they are carried so they reach the author with
    everything else, which is the half the brief could not do on its own.

    Everything after the heading is taken, one finding per non-blank line, until
    the next heading or the end.
    """
    m = CODE_CONCERNS.search(text)
    if not m:
        return []
    out: list[str] = []
    for line in m.group(1).splitlines():
        line = line.strip().lstrip("-*+ ").strip()
        if line.startswith("#"):
            break
        if line:
            out.append(line)
    return out


def claim_object(verdict: str, claim: str) -> dict:
    """A 0.2.x `CLAIM` string as the object this shape carries.

    The markers ARE the keys, minus their colons, which is why the two formats
    can be converted at all -- `false: "x" / true: "y"` was always an object
    written as prose.

    ! Best effort, and it says so. The old field was free text a checker read
    with `in`, so a claim that never matched its markers converts to a partial
    object and `--check` reports it -- which is the right outcome, because the
    record was already inadmissible.
    """
    spec = VERDICTS.get(verdict)
    if spec is None or not claim.strip():
        return {}
    markers = list(spec.claim_all)
    out: dict[str, str] = {}
    # Split on each marker in turn, keeping what follows it up to the next one.
    positions: list[tuple[int, str]] = []
    lowered = claim.lower()
    for marker in markers:
        at = lowered.find(marker.lower())
        if at >= 0:
            positions.append((at, marker))
    positions.sort()
    for i, (at, marker) in enumerate(positions):
        start = at + len(marker)
        end = positions[i + 1][0] if i + 1 < len(positions) else len(claim)
        value = claim[start:end].strip()
        # ! The old form separated the halves with ` / `, which is not part of
        # either value.
        out[marker.rstrip(":")] = value.rstrip("/ ").strip().strip('"')
    if spec.claim_any:
        for shape in spec.claim_any:
            if shape.lower() in lowered:
                out["shape"] = shape
                break
    # !! THE OLD FORMAT CARRIED THESE AS PROSE INSIDE `CLAIM`, not as markers.
    # `needs_anchor`, `needs_attempted` and `needs_settles` were checked with a
    # regex over the whole field, so a conversion that read only the markers
    # dropped them and turned admissible records into malformed ones. Measured
    # 2026-08-17: 179 of one held report's 228 records failed on exactly this,
    # having passed the gate they were written for.
    #
    # ! The SAME patterns the gate used, imported rather than restated -- the
    # conversion has to agree with what it is converting from.
    if spec.needs_anchor:
        named = ANCHOR_NAME.search(claim)
        out["anchor"] = named.group(0) if named else ""
        # ! The SIDE a 0.2.x claim stated is DROPPED, not carried across. The
        # address says which side, so keeping the old word would reintroduce
        # the field this conversion exists to leave behind.
    if spec.needs_attempted or spec.needs_settles:
        # ! The old field ran both together in one sentence, and nothing marked
        # where one ended. The whole remaining claim goes to each, which is
        # lossy and says so: it preserves ADMISSIBILITY, not authorship.
        rest = claim.strip()
        if spec.needs_attempted:
            out["attempted"] = rest
        if spec.needs_settles:
            out["settles"] = rest
    return out


def address_of(finding, census: list[dict]) -> str:
    """A finding's address, reading its INDEX when the record carries none.

    !! ONLY SOUND WHEN THE CENSUS IS THE ONE THE RECORD WAS WRITTEN AGAINST.
    An index is a position in one census, not a name for a place, so it survives
    exactly as long as that census does. `verdicts.py` is where that holds: the
    reviewers were handed that census in this run, and a `clean` record in the
    deprecated shape writes its index alone. **It does NOT hold for a report
    held from an earlier version, and `convert` must not use it** -- see there.

    ! An index outside the census is left alone rather than clamped. It resolves
    to nothing downstream and is reported there, where the message can say which
    report and which paragraph; guessing a neighbour here would put a reviewer's
    verdict on prose it never read.

    Args:
        finding: one parsed record.
        census: the census this record was written against.

    Returns:
        The finding's own address, or the address at its index, or "".
    """
    if finding.address:
        return str(finding.address)
    if isinstance(finding.block, int) and 1 <= finding.block <= len(census):
        return str(census[finding.block - 1].get("address", ""))
    return ""


def convert(findings: list, census: list[dict], reviewer: str) -> dict:
    """A 0.2.x report, already parsed, as a seeded-and-filled record file.

    !! A CAPTURED RUN STAYS A REGRESSION TEST INSTEAD OF BECOMING AN ARCHIVE.
    Replaying held stage-4 output is what made 0.2.1 and 0.2.2 cheap to
    validate -- five joins over one set of reports, about 1.6M tokens of review
    reused -- and that property dies the day the shape moves unless something
    carries the old reports across.

    ! It seeds first and FILLS, so every paragraph still gets a slot and coverage
    stays structural. A paragraph the old report never mentioned keeps its null
    verdict rather than vanishing.

    Args:
        findings: `parse_report`'s output for one reviewer.
        census: the census that report was written against.
        reviewer: the editorial role's name.

    Returns:
        The report in the current shape.
    """
    # !! A RECORD WITH NO ADDRESS CANNOT BE CONVERTED AT ALL, AND THAT IS NOT A
    # BUG TO BE FIXED HERE. Roy, 2026-08-19: *"is it possible to convert the old
    # form to the new form at all without the code there next to it? I don't
    # think it is. There is not enough definition in the old form to make the
    # address."* Measured the same day, and both routes are closed:
    #
    #   PARAGRAPH <index>   An index is a position in ONE census. The census it
    #                   names carries no addresses -- 0 of 3,333 on a real held
    #                   run, because the field postdates it -- and a census
    #                   built TODAY is a different list: the held one holds
    #                   `interval`, `docstring`, `comment`, `trailing-comment`
    #                   and no `margin` or `undocumented`, which today's emits
    #                   one of per code line and per undocumented declaration.
    #                   Every index shifts, so `BLOCK 7` names unrelated prose.
    #   LOCATION        `path:start-end` is line numbers, and turning a line
    #                   into an ordinal needs the SOURCE to say which lines are
    #                   code. `Finding` does not even retain it.
    #
    # ! So it REFUSES rather than guessing. Grouping the unaddressed under ""
    # matched every paragraph against every finding: 3,333 paragraphs and 173 findings
    # produced 29,583 records, each with a verdict and no error raised.
    #
    # ! What replay needs is a report whose records carry addresses. A run held
    # from 0.2.4 on does; one held before it cannot be recovered without the
    # source at the pinned state AND a `LOCATION` this parser throws away.
    unkeyed = sum(1 for f in findings if not str(f.address or ""))
    if unkeyed:
        raise ValueError(
            f"{unkeyed} of {len(findings)} records carry no address. A 0.2.x"
            " report keys by census POSITION, and an index is only meaningful"
            " against the census it was written against -- which carries no"
            " addresses, and which today's census.py does not reproduce."
            " Nothing here can recover the place; replay a run held from 0.2.4"
            " on, or re-review the source."
        )
    report = seed(census, reviewer)
    by_paragraph: dict[str, list] = {}
    for f in findings:
        by_paragraph.setdefault(str(f.address), []).append(f)

    # !! EVERY CITED PARAGRAPH GETS A SLOT, PROSE OR NOT. `seed` lays down the prose
    # paragraphs because those are the ones a reviewer is ACCOUNTABLE for -- but an
    # `add` cites an empty INTERVAL by design, since its finding is that a
    # constraint exists in code and NOWHERE in prose. Seeding alone therefore
    # cannot express the one verdict that needs an interval, and a conversion
    # that only filled seeded slots dropped both of them silently. Measured
    # 2026-08-17 on this repo's own smoke test: 228 findings became 226.
    seeded = {rec["address"] for rec in report["records"]}
    order = {str(b.get("address", "")): i for i, b in enumerate(census)}
    for at in sorted(
        set(by_paragraph) - seeded, key=lambda a: order.get(a, len(census))
    ):
        held = entry_for(at, census)
        if held is not None:
            report["records"].append(slot(held))
    report["records"].sort(key=lambda r: order.get(r["address"], len(census)))

    filled = []
    for rec in report["records"]:
        found = by_paragraph.get(rec["address"], [])
        if not found:
            filled.append(rec)
            continue
        # ! One record per FINDING, not per paragraph. A paragraph ruled on twice by one
        # role is two records that share an index, which the format allows and
        # the old one did too.
        for f in found:
            out = dict(rec)
            out["verdict"] = f.verdict
            out["claim"] = claim_object(f.verdict, f.claim)
            out["reason"] = f.reason
            out["sources"] = [
                {"cite": c.strip(), "verbatim": v.strip()}
                for c, _, v in (s.partition("|") for s in f.sources)
            ]
            out["change"] = f.change.splitlines()
            filled.append(out)
    report["records"] = filled
    return report
