"""Stage 5's gate: join four reviewers' reports against the census.

    python verdicts.py --census census.json --repo D <report>...

Checks the task agent was asked to perform by hand, every one mechanical:

  COVERAGE      every census index accounted for, by every reviewer that ran
  SOURCES       every citation resolves, and its verbatim half is really there
  ADDRESS       BLOCK's `path:start-end` and transcribed text match the census
  BLOCK         the sentence a finding rules on is really in the block it cites
  EDIT          BLOCK-against-CHANGE edits the sentence CLAIM names, and no
                other. ! ONE ROUND ONLY -- it says nothing about whether N
                rounds converge on correct prose
  PAYLOAD       the verdict carries what its row of the table requires
  CONTRADICTION `drop` against `correct`/`patch` ON THE SAME SENTENCE -- a
                re-review. `move` composes with both and is not flagged.
                Counted apart from the fatal checks, and named in the closing
                line so the summary says which blocks are still out
  STANDS        blocks every reviewer that ran returned clean on
  SCOPED OUT    blocks nobody found anything in and nobody certified
  WORK LIST     each block needing a ruling, with the verdicts held on it
  CODE CONCERNS carried through, attributed, gated by nothing
  REVIEWER      every report is named for a PUBLISHED role, and (only with
                `--reviewers`) every expected reviewer actually reported

! Exits nonzero on a coverage gap or an unverifiable citation.

! It reports which findings are ADMISSIBLE. The ruling is stage 5's, in
SKILL.md's synthesis order.

! Every block is accounted for by a RECORD, `clean` included. A `clean` record
carries a BLOCK and a VERDICT and nothing else, so covering N blocks costs N
records that each name a real index and assert nothing about it. A
`clean` record carries no SOURCES, so it stops short of proof the file was read:
grade a run from its DIFF, and not from this exit code.

! `--reviewers` is OPTIONAL, and its absence is ANNOUNCED: without it, a
reviewer that never reported at all passes this tool unseen.

!! WHEN THIS FILE CANNOT RECOGNISE A BOUNDARY, IT MUST NAME WHAT IT COULD NOT
RECOGNISE -- NEVER MERGE ACROSS IT. Merging blames the neighbour, and the
neighbour is always correct work. Three defects in one day, all this shape,
each reported against something that was right:

  D7  a malformed citation absorbed into the valid one above it, so the error
      was reported against that valid citation
  D8  a bare field label absorbed into the field above it, so the error was
      reported against a correct SOURCES entry
  D9  a dropped span absorbing the punctuation beside it -- a trailing `.`,
      then markdown emphasis -- so a correct edit was refused for naming
      prose its CLAIM does not mention. ! The second shape had NO legal
      wording, and the reviewer reshaped a sound finding twice to route
      around it

! **It is the most expensive kind of diagnostic there is**, because it sends
the reader to fix something that is not broken. D7 was fixed for citations
specifically and the class survived to produce D8 and D9. A fourth is a reason
to change the SHAPE of the boundary decision, not to add a fourth case.

! What separated D9 from reviewer error was CORROBORATION: `block-context` had
implemented its own single-edit checker and passed the record this gate
refused. Two implementations of "did the edit match the claim" disagreeing is
worth running down.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from pathlib import Path

# ! The shim its three sibling importers carry. Run as a program this file
# resolves without it -- Python puts the script's own directory on `sys.path`
# -- so the gap was invisible from the documented invocation and appeared only
# on IMPORT, where a test or another script reaches in. `census.py`,
# `referrers.py` and `prove_unchanged.py` all insert it; this was the one
# sibling importer that did not.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from desk import (  # noqa: E402  -- path shim must run first
    CITE,
    PATHISH,
    _words,
    address_problem,
    block_problem,
    declares_scope,
    edit_problem,
    payload_problem,
    removed_spans,
    ruled_text,
    source_problem,
)
from record import (  # noqa: E402  -- path shim must run first
    VERDICTS,
    Finding,
    _is,
    _n,
    _substantive,
    claim_keys,
)
from repo import READ_ERRORS  # noqa: E402  -- path shim must run first
from vocabulary import Reviewer  # noqa: E402  -- path shim must run first

RECORD = re.compile(r"^---\s*RECORD\s*$(.*?)^---\s*$", re.M | re.S)
# Counts "--- RECORD" OPENERS on their own, independent of whether a closing
# "---" was ever found. A first record missing its close makes RECORD's
# non-greedy search skip straight past the second record's opener (it is not a
# bare "---" line) and swallow both into one match -- the second record's
# fields silently overwrite the first's and a finding vanishes with no output.
# Comparing this count against RECORD's match count is how that is caught.
OPENER = re.compile(r"^---\s*RECORD\s*$", re.M)
# The section `reviewer-brief.md` sends code problems to. Matched to the next
# heading or the end, because it is the LAST section of a report by contract.
CODE_CONCERNS = re.compile(r"^#+\s*CODE CONCERNS\s*$(.*?)(?=^#|\Z)", re.M | re.S | re.I)
# !! ANCHORED AT COLUMN 0, which is what makes a continuation unambiguous. A
# field's value runs until the next label, and a label is only a label at the
# left margin -- so an indented line reading `CHANGE the budget` inside a
# transcribed block is prose, not a new field.
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


def claim_text(verdict: str, claim: dict) -> str:
    """A record's `claim` OBJECT as the marker string the checks still read.

    !! A BRIDGE, and a deliberate one. The object is what a reviewer now fills
    and what `record.py` validates; the checks below -- `ruled_text`,
    `payload_problem` -- read the marker form the text record carried. Rendering
    the object into that form makes every one of them work UNCHANGED on a JSON
    report, which is what lets the change be proven equivalent before anything
    is rewritten to read the object directly.

    !! THE STRING IS NOW GENERATED, NEVER PARSED FROM A REVIEWER. That is the
    whole difference. The marker form was a defect surface because a reviewer
    wrote it and this file guessed where each half ended; built here from typed
    fields it is well-formed by construction.

    ! Keys the table does not name -- `anchor`, `side`, `attempted`, `settles`
    -- are appended as prose, because that is where the old format carried them
    and where `ANCHOR_NAME`, `ANCHOR_SIDE` and the attempted check look.
    """
    spec = VERDICTS.get(verdict)
    if spec is None or not claim:
        return ""
    markers, extras = claim_keys(spec)
    parts = [f'{m}: "{claim[m]}"' for m in markers if m in claim]
    out = " / ".join(parts)
    if "shape" in extras and claim.get("shape"):
        out = f"{claim['shape']} {out}".strip()
    # ! The SHAPE is a prefix and everything else trails. Anything already in
    # `out` is not repeated -- a reviewer whose `settles` restates the claim
    # would otherwise have it twice in the string the checks read.
    trailing = [
        str(claim[key])
        for key in extras
        if key != "shape" and claim.get(key) and str(claim[key]) not in out
    ]
    if trailing:
        out = f"{out} {' '.join(trailing)}".strip()
    return out


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
        block = rec.get("block")
        if not isinstance(block, int):
            malformed.append(f"a record carries block {block!r}, which is not an index")
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
                block=block,
                verdict=str(rec.get("verdict")),
                claim=claim_text(str(rec.get("verdict")), claim),
                reason=str(rec.get("reason") or ""),
                sources=[
                    f"{s.get('cite', '')} | {s.get('verbatim', '')}"
                    for s in rec.get("sources") or []
                    if isinstance(s, dict)
                ],
                # ! `str()` per line. `change` is a LINE ARRAY and `SHAPES`
                # checks only that it is a list, so a number in it raised
                # `TypeError` from `join` -- a crash the documented pre-flight
                # does not catch, on a file it calls well formed.
                change="\n".join(str(line) for line in rec.get("change") or []),
                address=str(rec.get("address") or ""),
                # ! The record no longer carries the block's text -- the census
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
        a block a reviewer never recorded is a block it never accounted for.
        `malformed` holds one sentence per record that names no block, which
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
        # INCLUDED. `BLOCK` carries a transcribed block and `CHANGE` carries a
        # replacement one, and a docstring has blank lines between its summary
        # and its `Args:` -- so a blank line is content here, not a separator.
        #
        # !! A blank line USED to end the continuation, and that single line
        # was the worst defect 0.2.0 shipped. Measured 2026-08-17: it truncated
        # both fields to their first paragraph on every block containing a
        # blank line -- 33% of one census, ~450 blocks of another -- so
        # `ORIGINAL` could never match and `CHANGE` compared its unedited first
        # paragraph against itself and reported the block UNCHANGED. It fell
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
        # are that block's text as the file reads it NOW. Only the index is
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
                    reason=fields.get("REASON", ""),
                    change=fields.get("CHANGE", ""),
                    address=addr.strip(),
                    original=raw.partition("\n")[2],
                )
            )
        else:
            malformed.append("a record with no BLOCK index")
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


def coverage_gaps(
    all_blocks: set[int], reported: set[str], found: list[Finding]
) -> dict[str, list[int]]:
    """Indices each reviewer left unaccounted for. A gap is a gap, not a pass.

    `reported` is who handed in a file, and the findings say who produced a
    record. A report that parsed to nothing is a reviewer that accounted for
    nothing, so taking the population from the findings alone would drop it.
    """
    by_reviewer: dict[str, set[int]] = defaultdict(set)
    for f in found:
        by_reviewer[f.reviewer].add(f.block)
    gaps: dict[str, list[int]] = {}
    for reviewer in reported | set(by_reviewer):
        missing = sorted(all_blocks - by_reviewer[reviewer])
        if missing:
            gaps[reviewer] = missing
    return gaps


def by_block(found: list[Finding]) -> dict[int, list[Finding]]:
    """Every finding, grouped by the block it rules on.

    This is what stage 5 works from: several roles rule on one block and the
    task agent emits ONE replacement, so the grouping IS the work list. It was
    computed inside `contradictions`, used for one boolean and dropped, leaving
    the agent to rebuild it from the report files by hand.

    Every finding here names a block, because a record that named none never
    became a `Finding` -- `parse_report` returns those separately.
    """
    out: dict[int, list[Finding]] = defaultdict(list)
    for f in found:
        out[f.block].append(f)
    return out


# A phrase a reviewer QUOTED inside prose. ! DOUBLE QUOTES ONLY, because in
# this system BACKTICKS MEAN CITATION -- the brief instructs a reviewer to
# cite by symbol or path in them, so a backticked token in `REASON` is a
# reference, not a quotation of the block's words.
#
# !! Measured 2026-08-17 before the narrowing: over 903 real findings the
# check fired 46 times and most were symbol citations -- ``_walk``,
# ``BY_EXT``, ``raw_lines`` -- which is the noise level at which a report
# stops being read. Quoting is the signal: a `REASON` that MENTIONS a
# subject is discussing context, which it is entitled to do; one that
# QUOTES the block's own words is describing a defect in them.
QUOTED = re.compile(r'"([^"\n]{4,})"')


def unrecorded_findings(
    grouped: dict[int, list[Finding]], blocks: list[dict]
) -> list[tuple[int, str, str]]:
    """Phrases a `REASON` quotes from its own block that no `CLAIM` names.

    !! A FINDING CAN BE STATED IN `REASON` AND GO NOWHERE. `REASON` is
    deliberately unverified -- a derived count is not a line any file contains,
    which is why it is a separate field from `SOURCES` -- so nothing downstream
    reads it as a claim. A reviewer whose reasoning wanders one sentence over
    from what its `CLAIM` names has filed a second finding with no record.

    ! Measured 2026-08-17. `module-context` wrote in `REASON` on block 1: *"the
    module's own prose already contradicts the 'three places' framing -- the
    fourth copy is named inside the file and nowhere in its docstring."* That
    sentence IS the finding. The record carried `add` with a `CLAIM` naming a
    different sentence, so the gate checked the claim it named and passed.
    *"Three places"* reached no work list, was never in front of stage 5, and is
    still wrong on disk.

    !! REPORTED, NEVER FATAL. `REASON` legitimately discusses context, and a
    fatal check here would refuse honest records -- which is the failure this
    whole file has been paying for all week. The permission to file a second
    record already exists (*"several of your findings may carry the same
    BLOCK"*); nothing tells a reviewer to use it.

    Args:
        grouped: findings by census block index.
        blocks: the census.

    Returns:
        `(block, reviewer, phrase)` per phrase, in block order.
    """
    # Every phrase any CLAIM in this run names, normalised once.
    # ! One call per finding. `ruled_text` already returns `_words(...)`, so
    # the walrus keeps the text rather than computing it twice to test it.
    claimed = {text for fs in grouped.values() for f in fs if (text := ruled_text(f))}
    out: list[tuple[int, str, str]] = []
    for block, fs in sorted(grouped.items()):
        if not 1 <= block <= len(blocks):
            continue
        prose = _words(blocks[block - 1].get("text") or "")
        if not prose:
            continue
        for f in fs:
            for match in QUOTED.finditer(f.reason or ""):
                phrase = _words(match.group(1) or "")
                # ! It must be the BLOCK'S OWN words. A phrase quoted from a
                # source file is evidence, not an unrecorded finding.
                if len(phrase) < 4 or phrase not in prose:
                    continue
                if any(phrase in c or c in phrase for c in claimed):
                    continue
                out.append((block, f.reviewer, match.group(1)))
    return out


def contradictions(grouped: dict[int, list[Finding]], blocks: list[dict]) -> list[int]:
    """Blocks where one role REMOVES the sentence another rules on.

    `drop` against `correct`/`patch` is one role saying the sentence should not
    exist and another saying it should exist and be fixed. Nothing composes
    those.

    !! Keyed on the TEXT, not the block index. A block of six sentences can
    carry six verdicts, so sharing an index is not sharing a subject -- measured
    on a live run, one of eight flagged collisions was two roles ruling on two
    different clauses of one docstring, and a re-review round was spent
    establishing it.

    !! The text is the DIFF between `BLOCK`'s original and `CHANGE`, not
    `CLAIM`. Ruled 2026-08-17. Both are accounts of the same edit and `CLAIM` is
    the reviewer's own; the diff is what the proposed text actually does, so two
    roles are rivals when their EDITS collide, whatever they each said. A role
    whose claim and edit disagree is `edit_problem`'s to refuse, and it runs
    first.

    ! One span CONTAINING the other still collides: a role may drop a paragraph
    whose clause another corrects.

    !! `move` is absent by ruling. Relocation and a truth fix compose -- the
    synthesis order applies every `move` at step 2 and every `correct` at step
    3, which is the sequence, not a rivalry.
    """

    def touched(f: Finding) -> str:
        # ! "" means CANNOT COMPARE, and the caller flags it rather than
        # passing: silence would hide a real collision behind an unreadable
        # record. An out-of-range index reads the same way -- the range check
        # reports it, and this must not pass the block for lack of an entry.
        if not 1 <= f.block <= len(blocks):
            return ""
        spans = removed_spans(f, blocks[f.block - 1])
        return " ".join(spans) if spans else ""

    out: list[int] = []
    for block, fs in grouped.items():
        removals = [touched(f) for f in fs if _is(f, "removes")]
        rulings = [touched(f) for f in fs if _is(f, "rules_on_text")]
        if not removals or not rulings:
            continue
        if any(not a or not b or a in b or b in a for a in removals for b in rulings):
            out.append(block)
    return sorted(out)


def main() -> int:
    """Join the reports, report what is inadmissible, and gate on it."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "reports",
        nargs="+",
        # ! The SUFFIX chooses the reader and the STEM names the role, so both
        # halves of the filename are load-bearing. A record file named `.md`
        # goes to the deprecated text parser, which finds no records in it and
        # reports the reviewer as a total coverage gap with nothing pointing at
        # the extension.
        help="one report file per reviewer, named <role>.json",
    )
    ap.add_argument("--census", required=True, help="census.py --json output")
    ap.add_argument("--repo", default=".", help="repo root for evidence resolution")
    ap.add_argument(
        "--out", metavar="PATH", help="write the report to PATH, not stdout"
    )
    ap.add_argument(
        "--reviewers",
        default="",
        help=(
            "comma-separated expected reviewer names, matched against each report"
            " file's STEM (ownership-context.md -> ownership-context); one missing"
            " a report is fatal"
        ),
    )
    args = ap.parse_args()
    # !! `--out`, BECAUSE A REDIRECT IS NOT AVAILABLE EVERYWHERE. A
    # worktree-isolated session REFUSES a command carrying one -- "too complex
    # to verify that it stays inside the worktree" -- and this gate's output is
    # what stage 5 works from, so the only route to keeping it was unrunnable
    # in the session type the skill is written for. `census.py` carries the
    # same flag for the same reason; this is the one that was missed.
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="") as fh:
            with redirect_stdout(fh):
                return _report(args)
    return _report(args)


def _report(args: argparse.Namespace) -> int:
    """Everything the join prints, so `--out` can wrap it in one place."""
    repo = Path(args.repo).resolve()
    # ! Guarded like a report file, so a missing census prints which file and
    # why in one line.
    try:
        census_text = Path(args.census).read_text(encoding="utf-8")
    except READ_ERRORS as e:
        print(
            f"CANNOT READ {args.census} ({type(e).__name__})"
            " -- no census to join against"
        )
        return 1
    try:
        blocks = json.loads(census_text)
    except json.JSONDecodeError as e:
        print(
            f"CANNOT PARSE {args.census} as JSON ({e})"
            " -- is this census.py --json output?"
        )
        return 1
    # !! ADDRESSABLE is not ACCOUNTABLE. Every interval between two lines of
    # code is a block, so an `add` -- a finding about prose that is MISSING --
    # has an index to cite instead of borrowing a neighbour's. Most of them hold
    # nothing, and a reviewer owes no record on an empty one: coverage is over
    # the blocks that HOLD PROSE. Measured 2026-08-17: `census.py` over itself
    # is 642 blocks, 76 of them prose. Owing a record on all 642 would make
    # `CLEAN 1-N` -- the cheapest fabrication there is -- eight parts out of
    # nine true.
    # ! The figure was 546/48 and had rotted; it was written in TWO places,
    # here and in `SKILL.md`, with nothing comparing them. Re-measure both or
    # neither.
    all_blocks = {i for i, b in enumerate(blocks, 1) if b.get("kind") != "interval"}

    fatal = 0

    # ! Refused on every run, `--reviewers` or not: a reviewer is keyed by its
    # report's stem, so two files with the same stem put one reviewer's
    # coverage in place of the other's.
    stems = [Path(r).stem for r in args.reports]
    expected = {a.strip() for a in args.reviewers.split(",") if a.strip()}
    for stem in sorted({s for s, n in Counter(stems).items() if n > 1}):
        print(f"  DUPLICATE report stem {stem!r} -- two files claim the same reviewer")
        fatal += 1

    # ! A stem was taken as a role name on sight, so `ownershp-context.md` was
    # accepted as a reviewer called `ownershp-context` and every line below
    # named a role that does not exist. `Reviewer` is the published list.
    published = {r.value for r in Reviewer}
    for name in sorted(set(stems) | expected):
        if name not in published:
            print(
                f"  UNKNOWN reviewer {name!r} -- not one of"
                f" {', '.join(sorted(published))}"
            )
            fatal += 1

    found: list[Finding] = []
    reported: set[str] = set()
    concerns: list[tuple[str, str]] = []
    malformed: list[tuple[str, str]] = []
    for raw in args.reports:
        path = Path(raw)
        reviewer = path.stem
        try:
            text = path.read_text(encoding="utf-8")
        except READ_ERRORS as e:
            print(
                f"  CANNOT READ {raw} ({type(e).__name__}) -- {reviewer} did not report"
            )
            fatal += 1
            continue
        records, unattributable, code_lines_flagged = load_report(path, text, reviewer)
        # !! THE TOOL SUPPLIES THE ORIGINAL, NOT THE REVIEWER. A record carries
        # an INDEX and an address; the census holds the text. Filling it here
        # means `removed_spans` and `edit_problem` work unchanged, and the
        # transcription-mismatch class -- 83 refusals in one measured run, none
        # of them about a finding -- cannot arise, because nobody transcribed
        # anything.
        for f in records:
            if not f.original and 1 <= f.block <= len(blocks):
                f.original = "\n".join(blocks[f.block - 1].get("raw_lines") or [])
        found.extend(records)
        malformed.extend((reviewer, why) for why in unattributable)
        for line in code_lines_flagged:
            concerns.append((reviewer, line))
        reported.add(reviewer)

    print(
        f"{_n(len(found), 'finding')} from {_n(len(args.reports), 'reviewer')}"
        f" over {_n(len(all_blocks), 'prose block')}"
        f" ({_n(len(blocks), 'block')} in the census, the rest empty intervals"
        " an `add` may cite)\n"
    )

    # ! DECLARED, the way this repo names a population everywhere else. Without
    # --reviewers, "every reviewer" means "every file I was handed", so a
    # reviewer that reported nothing at all passes unseen.
    if args.reviewers:
        for reviewer in sorted(expected - reported):
            print(
                f"  NO REPORT from reviewer {reviewer!r} -- a missing report is the"
                " easier version of a fabricated one. --reviewers is matched against"
                f" each report file's STEM, so a report for {reviewer!r} must be"
                f" named {reviewer}.json"
            )
            fatal += 1
    else:
        print(
            "! --reviewers not given: whether every expected reviewer reported was"
            " NOT checked.\n"
        )

    gaps = coverage_gaps(all_blocks, reported, found)
    if gaps:
        print("COVERAGE GAPS - indices no reviewer accounted for:")
        for reviewer, missing in sorted(gaps.items()):
            shown = ", ".join(str(n) for n in missing[:20])
            more = f" (+{len(missing) - 20} more)" if len(missing) > 20 else ""
            count = _n(len(missing), "block")
            print(f"  {reviewer}: {count} unaccounted -- {shown}{more}")
            fatal += 1
        print()

    for reviewer, why in malformed:
        print(f"  MALFORMED {reviewer}: {why}")
        fatal += 1

    for f in found:
        if not 1 <= f.block <= len(blocks):
            print(
                f"  BLOCK {f.block} {f.reviewer}: out of range for a"
                f" {_n(len(blocks), 'block')} census"
            )
            fatal += 1
            continue
        if f.verdict not in VERDICTS:
            print(
                f"  BLOCK {f.block} {f.reviewer}: {f.verdict!r} is not a verdict"
                f" ({', '.join(VERDICTS)})"
            )
            fatal += 1
        problem = source_problem(f, repo)
        if problem:
            print(f"  BLOCK {f.block} {f.reviewer}: {problem}")
            fatal += 1
        misaddressed = address_problem(f, blocks)
        if misaddressed:
            print(f"  BLOCK {f.block} {f.reviewer}: {misaddressed}")
            fatal += 1
        wrong_block = block_problem(f, blocks)
        if wrong_block:
            print(f"  BLOCK {f.block} {f.reviewer}: {wrong_block}")
            fatal += 1
        if 1 <= f.block <= len(blocks):
            disagrees = edit_problem(f, blocks[f.block - 1])
            if disagrees:
                print(f"  BLOCK {f.block} {f.reviewer}: {disagrees}")
                fatal += 1
        payload = payload_problem(f)
        if payload:
            print(f"  BLOCK {f.block} {f.reviewer}: {payload}")
            fatal += 1

    grouped = by_block(found)
    # !! REPORTED, NOT GATED, and printed BEFORE the counts so it is not read as
    # a summary line. A finding stated in `REASON` that no `CLAIM` names is a
    # second finding with no record -- the gate checked the claim it was given
    # and passed, and the defect reached no work list. It is not fatal because
    # `REASON` is entitled to discuss context.
    unrecorded = unrecorded_findings(grouped, blocks)
    if unrecorded:
        print(
            f"\nA FINDING WITH NO RECORD -- {_n(len(unrecorded), 'phrase')} quoted in"
            " REASON that no CLAIM names:"
        )
        for block, reviewer, phrase in unrecorded[:20]:
            print(f"  BLOCK {block} {reviewer}: {phrase!r}")
        if len(unrecorded) > 20:
            print(f"  ... and {len(unrecorded) - 20} more")
        print(
            "  Each is the block's OWN words. File a second record on that block"
            " rather than leaving the finding in prose nothing reads."
        )

    clash = contradictions(grouped, blocks)
    if clash:
        # ! Names what the check DOES. It read "drop/move" after `move` left the
        # set by ruling, so the one line a user reads named a pairing the join
        # had stopped making.
        print(f"\nRE-REVIEW -- drop against correct/patch on: {clash}")
        print(
            "  Not a tie-break. Send the block back; the synthesis order"
            " must not decide it."
        )

    # !! THREE STATES, NOT TWO. A block covered only by `clean` and out-of-role
    # queries is neither: no role certified it -- module-context returns `query`
    # rather than `clean` so it does not certify what it never read -- and
    # nothing is asked of stage 5 either. Counting those as work buried 76 real
    # verdicts inside 1159 on a measured run.
    ran = sorted(reported | {f.reviewer for f in found})
    in_range = [f for f in found if 1 <= f.block <= len(blocks)]
    ruled = {f.block for f in in_range if _substantive(f) and not declares_scope(f)}
    scoped_out = {f.block for f in in_range if declares_scope(f)} - ruled
    # !! A BLOCK NOBODY ACCOUNTED FOR IS NOT A BLOCK EVERY ROLE PASSED. It fell
    # into `stands` and was printed as "clean from all N reviewers", which is a
    # claim no reviewer made -- on a report where every slot was still empty,
    # every prose block in the file was summarised that way, one line under the
    # COVERAGE GAPS list naming the same blocks. Measured 2026-08-18.
    #
    # ! It is the same shape `_substantive` already guards at the other end: an
    # unknown verdict answered False to everything, dropped out of the work
    # list, and was reported as clean on a block a role HAD ruled on. Both
    # directions end in the summary asserting a pass nobody gave.
    unaccounted = {index for missing in gaps.values() for index in missing}
    stands = sorted(all_blocks - ruled - scoped_out - unaccounted)
    print(
        f"\nSTANDS UNCHANGED: {_n(len(stands), 'block')} -- clean from all"
        f" {_n(len(ran), 'reviewer')} that ran"
    )
    print(f"NEEDS A RULING:   {_n(len(ruled), 'block')}")
    if unaccounted:
        # ! Counted here as well as listed above, because the three lines
        # around it are counts and a reader compares them.
        print(
            f"NOT ACCOUNTED FOR: {_n(len(unaccounted), 'block')} -- at least one"
            " reviewer left them out. Neither ruled on nor certified."
        )
    if scoped_out:
        print(
            f"NO FINDING, NOT CERTIFIED: {_n(len(scoped_out), 'block')} -- every"
            " role that read it was `clean`, and at least one said it was outside"
            " its role. Nothing to rule; nothing certified either."
        )
    if gaps:
        print("  ! counts above are provisional: coverage is incomplete.")

    # ! The WORK LIST. Stage 5 holds several rulings per block and must emit ONE
    # replacement, so this grouping is what it works from -- and rebuilding it
    # from the report files by hand is the step this tool can do exactly and a
    # reader cannot.
    #
    # !! PRINTED EVEN WHEN FATAL, and LABELLED instead of withheld. It used to
    # be withheld on any fatal problem, on the reasoning that a work list after
    # a refusal reads as permission to start. That reasoning holds and the
    # heading below carries it -- but withholding paid for it with the run's
    # only readable summary of what the roles found, exactly while someone is
    # iterating on refusals. Measured 2026-08-17: five joins over one report
    # set, and the only one that printed the list was the fifth, which needed
    # it least.
    out_for_rereview = set(clash)
    if ruled:
        if fatal:
            print(
                "\nPER BLOCK -- PROVISIONAL, the gate refused this report."
                "\n  Read it to see what the roles found; do not rule from it"
                " until the problems above are resolved."
            )
        else:
            print("\nPER BLOCK -- what you hold, in census order:")
        for b in sorted(ruled):
            marks = "  ".join(
                f"{f.verdict}({f.reviewer})"
                for f in sorted(grouped[b], key=lambda f: (f.verdict, f.reviewer))
                if _substantive(f) and not declares_scope(f)
            )
            flag = "   ! RE-REVIEW" if b in out_for_rereview else ""
            print(f"  {b:4d}  {marks}{flag}")

    # ! Printed whether or not the gate refuses, and counted toward nothing. A
    # code problem is not a verdict, so it is neither admissible nor
    # inadmissible -- but a run that stops at stage 5 must still carry it, or the
    # defect dies with the refusal.
    if concerns:
        print(f"\nCODE CONCERNS -- {_n(len(concerns), 'line')}, no verdict, not gated:")
        for reviewer, line in concerns:
            print(f"  {reviewer}: {line}")

    if fatal:
        print(f"\n{_n(fatal, 'problem')}. Resolve or send back before stage 5 rules.")
        return 1
    if clash:
        # ! A contradiction is counted apart from the fatal checks: it is a
        # re-review, and both records are well formed.
        # The closing line still has to say so -- printing "send the block back"
        # and then "Stage 5 may rule" four lines later made the summary
        # contradict its own body at exit 0.
        print(
            f"\nEvery finding is admissible. {_n(len(clash), 'block')} still OUT"
            " for re-review -- stage 5 may rule on the rest."
        )
        return 0
    print("\nEvery finding is admissible. Stage 5 may rule.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
