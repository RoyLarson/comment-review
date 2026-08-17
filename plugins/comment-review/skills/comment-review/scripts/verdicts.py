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
"""

import argparse
import difflib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

# ! The shim its three sibling importers carry. Run as a program this file
# resolves without it -- Python puts the script's own directory on `sys.path`
# -- so the gap was invisible from the documented invocation and appeared only
# on IMPORT, where a test or another script reaches in. `census.py`,
# `referrers.py` and `prove_unchanged.py` all insert it; this was the one
# sibling importer that did not.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from census import block_text, language_for  # noqa: E402  -- path shim must run first
from vocabulary import Reviewer  # noqa: E402  -- path shim must run first

READ_ERRORS = (OSError, UnicodeDecodeError)


# !! The THREE shapes `reviewer-brief.md` says reach `query`, and a query must
# NAME the one it is. A closed set beats guessing at free text: the shape decides
# whether the block is work (the author must answer) or a boundary report (the
# role is saying which scope owns it), and that is not something to infer from
# whether a sentence happens to contain the word "resolved".
OUT_OF_ROLE = "outside my role"
QUERY_SHAPES = (OUT_OF_ROLE, "outside the checkout", "outside the code")


@dataclass(frozen=True)
class Verdict:
    """Everything this file knows about one verdict, in one place.

    !! ADDING OR CHANGING A VERDICT IS A ROW, NOT NEW CODE -- the same promise
    `census.py` makes about a language. It is written this way because the
    alternative was measured: on 2026-08-17 the record's contract changed twice
    and this knowledge lived in eight functions, each with its own branch on
    `verdict`. Finding all eight is what nobody did, and five defects shipped in
    one morning. A contract change should touch one row.

    Attributes:
        claim_all: markers `CLAIM` must ALL carry.
        claim_any: markers `CLAIM` must carry at least ONE of.
        claim_help: what to say when either is unmet -- per row, because
            "correct needs a false/true pair" reads and a generated list does
            not.
        quotes_original: the `CLAIM` marker the EXISTING sentence follows, or ""
            when the verdict quotes none. ! `move`'s from/to are PLACES, and
            `add` is about prose that is missing, so both quote nothing.
        quotes_until: what ends that sentence; "" runs to the end of `CLAIM`.
        change_all: markers `CHANGE` must carry. Only `move`, which changes two
            blocks and shows both.
        owes_claim: every verdict but `clean` states what must happen.
        owes_reason: likewise -- why.
        owes_change: `clean` rules on nothing and `query` proposes no text.
        owes_address: `clean` is exempt because a role returns it on most of the
            census; transcribing each would be the bulk of a report.
        owes_sources: `clean` cites no claim, so it cites no place.
        diffable: `BLOCK`-against-`CHANGE` names the edited sentence. False
            where there is nothing to diff -- no text proposed, no original, or
            a `CHANGE` holding two blocks rather than one.
        needs_anchor: `CLAIM` names a site in backticks and a side.
        needs_attempted: `CLAIM` names a check that was tried.
        needs_settles: `CLAIM` names what would settle the claim.
        substantive: this verdict ASKS something of stage 5. Only `clean`
            does not, which is what makes it the null verdict rather than
            a pass.
        can_declare_scope: this verdict may be a BOUNDARY REPORT rather
            than work -- `query`, and only in its `outside my role` shape.
        removes: takes the sentence out of the block.
        rules_on_text: keeps the sentence and changes it. ! `removes` against
            `rules_on_text` on ONE sentence is the contradiction, and `move` is
            deliberately neither -- relocation and a truth fix COMPOSE, applied
            at synthesis steps 2 and 3. Ruled 2026-08-17; measured, 5 of 8
            blocks the old set flagged were this shape and each cost a
            re-review round to establish it was not a rivalry.
    """

    claim_all: tuple[str, ...] = ()
    claim_any: tuple[str, ...] = ()
    claim_help: str = ""
    quotes_original: str = ""
    quotes_until: str = ""
    change_all: tuple[str, ...] = ()
    change_help: str = ""
    owes_claim: bool = True
    owes_reason: bool = True
    owes_change: bool = True
    owes_address: bool = True
    owes_sources: bool = True
    diffable: bool = True
    needs_anchor: bool = False
    needs_attempted: bool = False
    needs_settles: bool = False
    substantive: bool = True
    can_declare_scope: bool = False
    removes: bool = False
    rules_on_text: bool = False


VERDICTS: dict[str, Verdict] = {
    "clean": Verdict(
        owes_claim=False,
        owes_reason=False,
        owes_change=False,
        owes_address=False,
        owes_sources=False,
        diffable=False,
        substantive=False,
    ),
    "query": Verdict(
        claim_any=QUERY_SHAPES,
        claim_help=(
            "query must NAME its shape -- one of "
            + ", ".join(f"'{s}'" for s in QUERY_SHAPES)
            + " -- so the reason is attached to the ruling"
        ),
        owes_change=False,
        diffable=False,
        needs_attempted=True,
        needs_settles=True,
        can_declare_scope=True,
    ),
    "drop": Verdict(
        claim_all=("drop:",),
        claim_help='drop needs the sentence in CLAIM, as `drop: "..."`',
        quotes_original="drop:",
        removes=True,
    ),
    "correct": Verdict(
        claim_all=("false:", "true:"),
        claim_help="correct needs a false/true pair in CLAIM",
        quotes_original="false:",
        quotes_until="/ true:",
        rules_on_text=True,
    ),
    "patch": Verdict(
        claim_all=("from:", "to:"),
        claim_help="patch needs a from/to pair in CLAIM",
        quotes_original="from:",
        quotes_until="/ to:",
        rules_on_text=True,
    ),
    "add": Verdict(
        claim_all=("missing:",),
        claim_help='add needs the text in CLAIM, as `missing: "..."`',
        diffable=False,
        needs_anchor=True,
    ),
    "move": Verdict(
        claim_all=("from:", "to:"),
        claim_help="move needs a from/to pair in CLAIM",
        change_all=("to:",),
        change_help=(
            "move needs the DESTINATION block in CHANGE, as `to: ...` -- plus"
            " `from: ...`, the origin as it reads after, unless the WHOLE block moves"
        ),
        diffable=False,
    ),
}

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
# `file:line` or `file:start-end`, as each SOURCES entry writes its citation half.
CITE = re.compile(r"^(.+?):(\d+)(?:-(\d+))?$")
# A citation half that is PATH-SHAPED, whether or not it resolves: no whitespace,
# and a `.` or `/` in it. It is what tells a MALFORMED citation from the wrapped
# tail of the entry above, and `CITE` alone cannot -- both fail it.
#
# !! The space is the discriminator, and it has to be. A verbatim half may hold
# a `|` of its own: `def _show(repo: Path, ref: str, rel: str) -> str | None:`
# is a real line in this tree, and its left half is not path-shaped because it
# holds spaces. A wrapped line whose left half has neither a space nor anything
# but `.`/`/` would still be misread, which is the residue accepted here.
PATHISH = re.compile(r"^[^\s]*[./][^\s]*$")

# How far from the cited line the quoted text may sit. Prose wraps and code
# moves; a hard equality would reject honest citations, and a wide window would
# accept a fabricated one.
SOURCE_WINDOW = 3

# The floor on a SOURCES entry's verbatim half, and it is ONE: zero length is not text.
# It was 12, which refused `x = 1`, `pass` and `return` -- real short lines whose
# only route through was to quote MORE than was read.
MIN_NEEDLE = 1

# What an `add`'s PAYLOAD must carry: a SIDE, and the anchor NAMED.
#
# ! Backticks are the repo's own citation form -- the brief says cite by symbol
# or path, never by line number, and every record in it writes a symbol that way.
# So "named" is checkable without guessing which token is an identifier.
ANCHOR_SIDE = re.compile(r"\b(above|below|before|after)\b", re.I)
ANCHOR_NAME = re.compile(r"`[^`\s][^`]*`")

# What a `query`'s PAYLOAD must name: a check that was attempted, and the thing
# that would settle the claim.
#
# ! A SHAPE check: it removes the query that names no check at all, and the
# word "grepped" passes it. A query owes SOURCES on top of this --
# `source_problem` exempts `clean` alone.
#
# Matched on WORD BOUNDARIES. As substrings, "ran" hit *b**ran**ch*,
# *****ran***ge* and *t**ran**sfer*, and "settle" hit *un**settle**d*, so
# ordinary English naming no check passed while an honest query worded with
# "requires" / "resolves" / "determined by" was refused. `grep` is the one
# deliberate exception, left unanchored on its left so "ripgrep" counts:
# English words carry "ran" and "read" by accident, and "grep" they do not.
#
# !! The vocabulary is DERIVED from the verbs a reviewer is instructed in, never
# invented. The brief and the four agent files say resolve, enumerate, verify,
# list, trace, follow, compare, read, grep, count and open, so every one is here.
# Measured: a run refused 65 of 65 module-context queries whose payload read
# "resolved the enclosing definition at ..." -- `resolve` was in QUERY_SETTLES
# and missing here, so reports that were substantively complete were lexically
# refused, and the only route through was to reword another agent's report.
QUERY_ATTEMPTED = re.compile(
    r"\bran\b|\bcheck\w*|grep\w*|\bread\w*|\bsearch\w*|\bopen\w*|\bcount\w*"
    r"|\blook\w*|\bresolv\w*|\benumerat\w*|\bverif\w*|\btrac(ed|ing|e)\b"
    r"|\bfollow\w*|\bcompar\w*|\blisted\b|\binspect\w*",
    re.I,
)
QUERY_SETTLES = re.compile(
    r"\bsettl\w*|\bwould\s+\w+|\brequires?\b|\bresolv\w*|\bdetermined\s+by\b",
    re.I,
)


@dataclass
class Finding:
    """One reviewer's ruling on one census block.

    !! Field order follows the record in `reviewer-brief.md`, and the order is
    a CHAIN OF CUSTODY. Roy, 2026-08-17: *"Verdict -> Claim -> REASON ->
    SOURCES -> CHANGE ... that is a clear chain of custody on the reasoning and
    the required actions."* The ruling, what must change, why, the evidence
    the why rests on, and the result. `SOURCES` sat between `VERDICT` and
    `CLAIM`, which put the evidence before the thing it was evidence FOR.

    `sources` holds one entry per place examined, each `file:line | verbatim` --
    BOTH halves verbatim, which is why they are one field where `claim` and
    `reason` are two.

    !! `claim` is the SURGICAL SPEC -- what must change, and from what to what.
    `change` is the RESULT: that edit already made, written out with the
    surrounding block. Roy, 2026-08-17: *"The change is what allows the apply
    section to apply the claim appropriately."*

    | verdict   | claim                    | change                       |
    | --------- | ------------------------ | ---------------------------- |
    | `correct` | `false: ... / true: ...` | the result, with its block   |
    | `patch`   | `from: ... / to: ...`    | the result, with its block   |
    | `move`    | `from: ... / to: ...`    | BOTH blocks -- see below     |
    | `add`     | `missing: ...`           | the text added in            |
    | `drop`    | `drop: ...`              | the block with it removed    |

    ! `clean` and `query` carry NEITHER. A `clean` rules on nothing; a `query`
    says the claim is unsettled, so there is no text for stage 5 to apply.

    !! `move` changes TWO blocks, so its `change` shows both, `to:` and `from:`
    -- the destination once the prose arrives, and the origin once it has left.
    `from:` may be omitted, and omitting it ASSERTS the whole block moved.
    ! Those two labels are `claim`'s words reused: in `claim` they are PLACES,
    in `change` they are the resulting BLOCKS. The field decides which.

    !! EVERY check that reads the ORIGINAL sentence reads it out of `claim`.
    `change` is a whole block, so no sentence can be parsed back out of it --
    which is the point: a reviewer that hands over a block has said what the
    result IS, not only what to swap, and stage 5 applies it rather than
    re-deriving it.

    ! `reason` is the why: the evidence that verifies the claim. It is DERIVED
    and no checker can settle it, which is why it stays out of `sources`.

    !! `block` is an INDEX, `address` is `path:start-end`, and `original` is
    that block's text as the file reads it now. The reviewer writes all three
    and all three are CHECKED against the census. Ruled 2026-08-17: *"BLOCK gets
    the address and the original text verbatim. This allows the reviewer to have
    most the context and most of the time all of the context it needs to
    understand."* The index alone made a record unreadable on its own -- a
    re-review, or stage 5, had to hold the census open beside it to know what
    prose a finding was even about.

    ! `clean` owes neither. A role returns `clean` on most of the census, so
    transcribing every one would be the bulk of a report -- 1159 blocks on one
    measured run.
    """

    reviewer: str
    block: int
    verdict: str
    claim: str
    reason: str
    sources: list[str]
    change: str
    address: str = ""
    original: str = ""


def _substantive(f: Finding) -> bool:
    """Does this finding ASK something of stage 5?

    ! An UNKNOWN verdict answers True. `_is` answers False to everything, so a
    mistyped verdict fell out of the work list and was summarised as STANDS
    UNCHANGED -- reported as clean from all reviewers on a block a role had
    explicitly ruled on. The name check reports it fatal either way; the
    summary must not also call it a pass.
    """
    return f.verdict not in VERDICTS or _is(f, "substantive")


def _is(f: Finding, trait: str) -> bool:
    """Does this finding's verdict carry `trait`? False for an unknown verdict.

    ! An unknown verdict answers False to everything rather than raising. The
    VERDICT check reports it by name, and a lookup that raised would take the
    whole join down over one typo in one record.
    """
    spec = VERDICTS.get(f.verdict)
    return bool(spec and getattr(spec, trait))


def _n(count: int, noun: str) -> str:
    """`"1 block"`, `"2 blocks"` -- this output decides whether an agent proceeds."""
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


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


def payload_problem(f: Finding) -> str | None:
    """What the verdict's required payload is missing, or None.

    !! Reads the verdict's ROW. Every per-verdict fact this used to branch on
    is a field of `Verdict`, so a verdict that changes shape changes one row --
    which is the whole reason the table exists.
    """
    spec = VERDICTS.get(f.verdict)
    if spec is None:
        # ! An unknown verdict is the VERDICT check's to report, and it does so
        # by name. Reporting it twice would print two defects for one mistake.
        return None
    # ! Every verdict but `clean` states WHY, and `REASON` is the field that
    # holds it. It went unchecked while it doubled as a diagnostic slot for
    # malformed records; those are separate now, so it can be required.
    if spec.owes_reason and not f.reason.strip():
        return f"{f.verdict} states no REASON -- why the verdict was made"
    # ! CLAIM is the specific thing that must happen to make the result correct.
    # A finding without one has named a defect and asked for nothing.
    if spec.owes_claim and not f.claim.strip():
        return f"{f.verdict} states no CLAIM -- what must happen to make it right"
    # ! A reviewer that echoes the claim back has filed a verdict with no
    # reason. Compared normalised, because quoting and case are what make an
    # echo look like a statement.
    #
    # !! EQUALITY, never containment. A REASON that quotes the claim and then
    # says what is wrong with it is doing its job, and a containment test would
    # refuse exactly the well-written ones.
    if f.claim.strip() and _words(f.reason) == _words(f.claim):
        return "REASON restates CLAIM -- say what you derived, not what it says"

    claim = f.claim.lower()
    if any(marker not in claim for marker in spec.claim_all):
        return spec.claim_help
    named = [s for s in spec.claim_any if s in claim]
    if spec.claim_any and not named:
        return spec.claim_help
    if spec.needs_attempted or spec.needs_settles:
        # ! The shape is REMOVED before the word search. `check\w*` matches
        # "checkout", so "outside the checkout" would satisfy the attempted-check
        # test by naming itself -- a query could pass by declaring its shape and
        # doing nothing.
        probe = claim
        for shape in named:
            probe = probe.replace(shape, " ")
        if spec.needs_attempted and not QUERY_ATTEMPTED.search(probe):
            return (
                "query needs the check you ATTEMPTED -- a query naming none"
                " hands the judgement back"
            )
        if spec.needs_settles and not QUERY_SETTLES.search(probe):
            return "query needs what WOULD settle the claim"
    if spec.needs_anchor:
        # ! The brief asks for "the text AND its anchor -- which code, above or
        # below": a NAMED site and a side. This used to accept the bare word
        # "anchor", so `add an anchor comment` passed while
        # `above `retry_budget`` failed for not saying "anchor".
        if not ANCHOR_SIDE.search(claim):
            return "add needs a side -- is the text above or below the anchor"
        if not ANCHOR_NAME.search(f.claim):
            return (
                "add needs the anchor NAMED in backticks -- which declaration,"
                " not the word 'anchor'"
            )
    if spec.owes_change and not f.change.strip():
        return (
            f"{f.verdict} carries no CHANGE -- the edit already made, written out"
            " with its surrounding block, which is what stage 5 applies"
        )
    if any(marker not in f.change.lower() for marker in spec.change_all):
        return spec.change_help
    return None


def _resolve_lines(cite: str, repo: Path) -> tuple[Path, int, int, list[str]] | str:
    """Resolve ONE `file:line` or `file:start-end` citation, or say why not.

    Shared by SOURCES and LOCATION: both are inadmissible on exactly the same
    grounds -- an unparseable citation, a missing file, or a line number past
    the end of it (or below 1, which is off every file).

    ! It resolves a SINGLE citation. `source_problem` calls it once per SOURCES entry
    line, because a claim often needs two sites to settle.

    ! An `allow_range` flag held the citation to `file:line` and refused
    `file:start-end`. It stated no reason, and Roy removed it 2026-08-17: a
    range is where the reviewer looked, same as a line.

    Args:
        cite: the `file:line` or `file:start-end` text, one citation.
        repo: the repo root the path is relative to.

    Returns:
        `(path, start, end, lines)` when it resolves, else the problem string.
    """
    m = CITE.match(cite.strip())
    if not m:
        return f"{cite!r} is not file:line or file:start-end"
    rel, start_s, end_s = m.group(1), m.group(2), m.group(3)
    start = int(start_s)
    end = int(end_s) if end_s else start
    if start < 1 or end < 1:
        return f"{cite} -- line numbers are 1-based, 0 is not one"
    target = repo / rel
    if not target.is_file():
        return f"{cite} does not resolve to a file"
    try:
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    except READ_ERRORS as e:
        return f"{cite} unreadable ({type(e).__name__})"
    if end > len(lines):
        return (
            f"{cite} -- line {end} is past the end of {rel} ({_n(len(lines), 'line')})"
        )
    return target, start, end, lines


def source_problem(f: Finding, repo: Path) -> str | None:
    """Why this finding's citation cannot be trusted, or None.

    Reads each cited line out of the file and looks for that entry's verbatim
    half within a few lines of it. A finding whose text is absent from the file
    it cites is a finding the file did not supply -- a report is evidence of
    nothing on its own.

    ! The only floor is `MIN_NEEDLE`, which is ONE. What binds is PRESENCE: a
    short needle absent from the file is refused like any other.

    ! SOURCES is checked and `REASON` is not. `REASON` is the DERIVED statement --
    *"31 callers, all under tests/"* -- which is the reviewer's own sentence, so
    checking it against the tree made every counted claim structurally
    inadmissible. The forcing function lands on the field that is verbatim.

    !! `query` is NOT exempt. `reviewer-brief.md` has always said a query
    "requires `SOURCES`, by construction -- this is where you looked", and
    this script waived it; Roy ruled the brief right on
    2026-08-16. Where you looked is a real line in the checkout on all three
    query shapes, so it resolves like any other citation. Only `clean` is
    exempt, because a `clean` reports no claim to cite.

    !! SEVERAL CITATIONS, comma-separated, and EVERY one must resolve. The
    brief has always asked for "`file(s):line(s)` you opened", and this took one
    `file:line` for the whole field -- so a reviewer that cited two sites was
    refused for following the brief. Measured 2026-08-17 on a live run: 15 of 22
    refusals were the contract, not the reviewer. Roy ruled the gate widens.
    ! This makes the check STRICTER. Three citations that all resolve is more
    evidence than one, and a reviewer forced to pick one was being made to drop
    the other -- which is the cut-the-provenance failure stage 5 already names.
    """
    spec = VERDICTS.get(f.verdict)
    if spec is None or not spec.owes_sources:
        return None
    if not f.sources:
        return "no SOURCES -- a finding cites where it looked"
    for source in f.sources:
        cite, sep, verbatim = source.partition("|")
        if not sep:
            return (
                f"SOURCES entry {source!r} has no `|` -- it is `file:line | verbatim`"
            )
        resolved = _resolve_lines(cite.strip(), repo)
        if isinstance(resolved, str):
            return f"SOURCES {resolved}"
        _target, lineno, end, lines = resolved
        needle = " ".join(verbatim.split()).strip().strip('"')
        if len(needle) < MIN_NEEDLE:
            return f"SOURCES entry {cite.strip()} carries no verbatim half"
        # !! The window spans the WHOLE citation, start to end. `_resolve_lines`
        # says a range "is where the reviewer looked", and this windowed on the
        # START alone -- so `a.py:10-55 | line 50` was refused and counted
        # fatal, while only ranges three lines deep happened to pass. A
        # reviewer citing a function-sized range is the honest case.
        lo = max(0, lineno - 1 - SOURCE_WINDOW)
        window = " ".join(
            " ".join(ln.split()) for ln in lines[lo : end + SOURCE_WINDOW]
        )
        # !! The WHOLE needle is compared; only the MESSAGE is truncated. The
        # slice was on both, so a citation was verified on its first 40
        # characters and anything after them was unchecked -- 44 real
        # characters followed by 43 fabricated ones passed as admissible
        # evidence. `40` is a display width, and it had quietly become the
        # verification depth.
        if needle.lower() not in window.lower():
            return f"SOURCES not found near {cite.strip()}: {needle[:40]!r}"
    return None


def as_block(text: str, entry: dict) -> str:
    """A reviewer's transcription, normalised the way the CENSUS normalises.

    !! This calls `census.block_text`, and that is the whole point. A second
    implementation of lines-to-block is a second DEFINITION of what a block's
    text is, and the two drift. Measured 2026-08-17: this file grew its own and
    disagreed with the census three ways at once -- a blank line, a raw-string
    prefix, and a closing delimiter -- refusing 83 of 171 blocks in one run and
    roughly 450 in another. Every one of those transcriptions was correct.

    ! The KIND selects the reading and the PATH selects the comment markers,
    both taken from the census entry rather than guessed: a docstring is read
    past its delimiters, a comment run past its openers, and `///` must come
    off before `//` leaves a stray slash in the prose.

    Args:
        text: the reviewer's `original`, as lines from the file.
        entry: that block's census record.
    """
    lang = language_for(Path(str(entry.get("path", ""))))
    markers = (
        tuple(sorted(lang.line_comment, key=len, reverse=True)) if lang else ("#",)
    )
    # ! `doc_is_structural` decides how a `docstring` is READ: Python's is a
    # string inside a declaration's body, where a `///` or `/**` run is a
    # comment like any other. Reading the second as the first leaves the marker
    # in the prose and refuses every doc comment in ten of the eleven languages.
    structural = lang.doc_is_structural if lang else True
    return block_text(str(entry.get("kind", "")), text.split("\n"), markers, structural)


def _words(text: str) -> str:
    """`text` reduced to its words, for comparing a CLAIM against a diff.

    ! This is NOT the block normaliser -- `as_block` is, and it defers to the
    census. This one takes prose that never came from a file: a `CLAIM`'s
    quoted half, and the spans a word-diff reports. Neither has comment markers
    to strip, so all it owes is whitespace, case, and the punctuation a quoted
    sentence picks up.

    ! Trailing sentence punctuation comes off each word. A block reads `the
    budget is 3.` where the `CLAIM` quoting it reads `the budget is 3`, and a
    diff keyed on raw tokens would call `3.` and `3` different words -- so an
    honest correction would read as an edit to a sentence nobody claimed.

    !! BRACKETS COME OFF TOO, and leaving them out was a defect. The set held
    sentence punctuation only, so a `CLAIM` naming `the CLI` could not cover a
    `CHANGE` editing `the CLI)` -- the closing paren stayed glued on and the two
    reduced to different words. The only way through was to quote the bracket
    inside the claim, which reads as arbitrary from a reviewer's side because
    the same phrase at the end of a sentence works. Measured 2026-08-17 on a
    live run, where it defeated the CLAIM-covers-CHANGE check.
    """
    return (
        # !! ONE strip over BOTH classes, so this is IDEMPOTENT. Stripping
        # quotes and THEN punctuation is not: `` `cap`, `` loses its backtick
        # only on a second pass. `ruled_text` already returns `_words(...)` and
        # `edit_problem` normalises it again, while a diff span gets one pass --
        # so a claim and the edit naming it reduced to different strings, and a
        # correct finding was refused.
        " ".join(w.strip("\"'`.,;:!?()[]{}") for w in text.split()).strip().lower()
    )


def address_problem(f: Finding, blocks: list[dict]) -> str | None:
    """Does `BLOCK`'s address and transcribed text match the census?

    !! The record carries the block's ADDRESS and its ORIGINAL TEXT so that it
    can be read on its own -- a re-review, or stage 5, otherwise has to hold the
    census open beside it to learn what prose a finding is about. Ruled
    2026-08-17.

    !! This is NOT `LOCATION` coming back. Roy, 2026-08-17: *"Location was
    dropped because it was ambiguous ... It could also have meant where this
    should go in the case of move or add. Or on a granular level which sentence
    are we talking about specifically."* One `file:start-end` field carried FOUR
    possible subjects, and each has its own home now:

    | LOCATION could have meant     | where it lives now                     |
    | ----------------------------- | -------------------------------------- |
    | where the prose SITS          | `BLOCK` -- index, address, original    |
    | where the reviewer LOOKED     | `SOURCES`                              |
    | where the prose SHOULD GO     | `CLAIM`'s `to:`, or an `add`'s anchor  |
    | WHICH SENTENCE, exactly       | `BLOCK`'s original against `CHANGE`    |

    !! The last one is DERIVED, not declared, and that is why it is reliable.
    Roy, 2026-08-17: *"which sentence exactly is determined by the difference
    between BLOCK and CHANGE, since CHANGE is the whole block with the
    substitution."* Both hold the WHOLE block, before and after, so what differs
    between them is the sentence and nothing else has to say so.

    ! Each is checked against a DIFFERENT thing -- `BLOCK` against the census,
    `SOURCES` against the files, the sentence against the block's text. That is
    the gain: a field with four possible subjects can only be checked for
    RESOLVABILITY, because nothing says which subject to check it against.

    ! Both parts of `BLOCK` are CHECKED, and that is what makes them worth
    writing. An address nobody verifies costs a line and settles nothing.

    ! `clean` is exempt. A role returns `clean` on most of the census -- 1159
    blocks on one measured run -- so requiring a transcription of each would
    make the bulk of every report text nobody reads.

    Args:
        f: the finding.
        blocks: the census, as `census.py --json` emits it.

    Returns:
        One sentence naming what disagrees, or None. Out-of-range indices are
        left to the range check, which reports them better.
    """
    spec = VERDICTS.get(f.verdict)
    if spec is None or not spec.owes_address:
        return None
    if not 1 <= f.block <= len(blocks):
        return None
    entry = blocks[f.block - 1]
    start, end = entry.get("start"), entry.get("end")
    path = str(entry.get("path", "")).replace("\\", "/")
    want = f"{path}:{start}-{end}"
    # !! BOTH forms are accepted on a one-line block. The brief says write
    # `path:start-end`, so a reviewer following it writes `a.py:225-225` while
    # the census prints `a.py:225`. Measured 2026-08-17: 268 refusals in one
    # run, every single one this collision and not one a wrong address.
    ok = {want} if start != end else {want, f"{path}:{start}"}
    got = f.address.replace("\\", "/").strip()
    if not got:
        return f"BLOCK {f.block} carries no ADDRESS -- write `{f.block} | {want}`"
    if got not in ok:
        return f"BLOCK {f.block} address is {got!r}, the census says {want!r}"
    text = str(entry.get("text", ""))
    if not text.strip():
        # ! An empty INTERVAL has no text to transcribe, and it is exactly what
        # an `add` cites: prose that is missing has no original.
        return None
    if not f.original.strip():
        return (
            f"BLOCK {f.block} carries no ORIGINAL -- the block's text as it reads now"
        )
    # ! CASE is forgiven, the words are not -- which is what the brief promises
    # a reviewer. Everything else the two forms differ by (markers, delimiters,
    # wrapping, indentation) `as_block` has already resolved.
    if as_block(f.original, entry).lower() != text.lower():
        return f"BLOCK {f.block} ORIGINAL does not match the census text"
    return None


def block_problem(f: Finding, blocks: list[dict]) -> str | None:
    """Is the sentence this finding rules on actually IN the block it cites?

    !! This is what `LOCATION` could never do -- it was AMBIGUOUS, and the four
    subjects it could have named are set out in `address_problem`. A field whose
    subject is unknown can only be checked for RESOLVABILITY, never against the
    thing it describes. The census carries each block's joined text and the gate
    already loads it, so this costs nothing and catches a finding attached to
    the wrong block.

    !! Keyed on the ORIGINAL SENTENCE, which `CLAIM` carries in its `drop:`,
    `false:` or `from:` half -- never on `CHANGE`, which is the finished block
    and holds the REPLACEMENT. Matching the replacement against the original
    block would refuse every correct finding and pass the ones that changed
    nothing. `ruled_text` reads it, the same text the contradiction check keys
    on.

    ! Exempt: `clean` rules on nothing, `add` is about prose that is MISSING,
    `query` proposes no edit, and a `move`'s from/to are PLACES rather than
    text. All four -- and any malformed spec -- reach here as `ruled_text` "".

    Args:
        f: the finding.
        blocks: the census, as `census.py --json` emits it.

    Returns:
        The problem, or None. ! An out-of-range block returns None: `main()`
        reports it already, and saying so twice reads as two defects.
    """
    # ! No verdict list here. `ruled_text` returns "" for every verdict whose
    # row quotes no original -- `clean`, `add`, `query`, `move` -- and for a
    # malformed spec, and the next line already treats "" as nothing to check.
    # A second list would be a second place to update.
    if not 1 <= f.block <= len(blocks):
        return None
    needle = ruled_text(f)
    if not needle:
        return None
    # !! THE SAME NORMALISER as the needle. `ruled_text` returns `_words(...)`,
    # which drops per-token quotes and trailing punctuation; a haystack that
    # was only whitespace-collapsed still holds them, so any comma, colon or
    # backtick inside a quoted sentence refused a correct finding.
    haystack = _words(str(blocks[f.block - 1].get("text", "")))
    # ! Same rule as SOURCES: compare all of it, truncate only the message. A
    # fabricated tail here made `edit_problem` MORE permissive, because it
    # widened the string every removed span is checked against.
    if needle not in haystack:
        return f"the sentence ruled on is not in block {f.block}: {needle[:40]!r}"
    return None


def declares_scope(f: Finding) -> bool:
    """A `query` saying the block is not this role's to read.

    Not a ruling: nothing is asked of the task agent, and the role is reporting
    the boundary it was told to report. Every other `query` IS work -- it names a
    claim nobody could settle, and the brief sends it to the author.
    """
    return _is(f, "can_declare_scope") and OUT_OF_ROLE in f.claim.lower()


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


def ruled_text(f: Finding) -> str:
    """The verbatim sentence this finding rules on, normalised for comparison.

    A verdict rules on a SENTENCE and the census numbers BLOCKS, so two findings
    on one block need not share a subject.

    !! Read out of CLAIM, the surgical spec. CHANGE is the whole resulting
    block, so the original cannot be recovered from it -- the `drop:`,
    `false:` and `from:` halves of CLAIM are the only verbatim originals a
    record carries.

    ! FOUR verdicts return "" and always will. `clean` rules on nothing; `add`
    is about prose that is MISSING; `query` proposes no edit; and `move`'s
    from/to are PLACES rather than text, so it names no sentence either.

    ! Also "" when the spec is malformed. A caller must treat that as "cannot
    compare", never as "no overlap" -- silence there would hide a real collision
    behind an unreadable payload.
    """
    spec = VERDICTS.get(f.verdict)
    if spec is None or not spec.quotes_original:
        return ""
    # !! Found CASE-INSENSITIVELY, because `payload_problem` matches these
    # markers against `claim.lower()`. A record written `FALSE:` / `TRUE:`
    # passed PAYLOAD and reduced to "" here, which silently switched off
    # `block_problem`, `edit_problem` and `contradictions` -- a reviewer that
    # shouted its markers had every finding admitted unchecked.
    lowered = f.claim.lower()
    at = lowered.find(spec.quotes_original)
    if at == -1:
        return ""
    rest = f.claim[at + len(spec.quotes_original) :]
    if spec.quotes_until:
        stop = rest.lower().find(spec.quotes_until)
        text = rest[:stop] if stop != -1 else rest
    else:
        text = rest
    # ! `_words` strips the quotes PER TOKEN, so a reviewer that pads inside
    # them -- `false: "  the budget is 3 "` -- does not keep those spaces and
    # leave a needle that matches nothing in a block plainly containing it.
    return _words(text)


def removed_spans(f: Finding, entry: dict) -> list[str] | None:
    """What this finding's edit takes OUT of the block, span by span.

    !! DERIVED, never declared. `BLOCK`'s original and `CHANGE` both hold the
    WHOLE block -- before and after -- so what differs between them IS the
    prose the finding acts on. Roy, 2026-08-17: *"which sentence exactly is
    determined by the difference between BLOCK and CHANGE, since CHANGE is the
    whole block with the substitution."*

    ! This is the reliable answer where `CLAIM` is the reviewer's own account of
    it. They should agree; `edit_problem` is where they are made to.

    !! Both halves are read through `as_block`, the CENSUS's normaliser, not
    through `_words`. They are file text: a comment run carries its openers and
    a docstring its delimiters, and a diff over raw tokens reports the marker as
    a removed word. Measured 2026-08-17: a `drop` that removed one sentence
    reported the span `# callers round separately`, which no `CLAIM` names.

    ! Returns None where no diff is meaningful: `clean` and `query` propose no
    text, `add` has no original, a `move`'s `CHANGE` is two blocks rather than
    one, and a record missing either half cannot be diffed at all. A caller must
    treat None as "cannot compare", never as "nothing removed".

    Args:
        f: the finding.
        entry: its census record, which selects how the block is read.
    """
    spec = VERDICTS.get(f.verdict)
    if spec is None or not spec.diffable:
        return None
    if not f.change.strip():
        return None
    before = as_block(f.original, entry).lower().split()
    after = as_block(f.change, entry).lower().split()
    if not before:
        return None
    return [
        " ".join(before[i1:i2])
        for tag, i1, i2, _j1, _j2 in difflib.SequenceMatcher(
            None, before, after
        ).get_opcodes()
        if tag in ("delete", "replace")
    ]


def edit_problem(f: Finding, entry: dict) -> str | None:
    """Does `CHANGE` edit the sentence `CLAIM` says it edits?

    !! A BACKSTOP, and it is the only check that reads the two accounts of one
    edit against each other. `block_problem` confirms the claimed sentence is in
    the block; `payload_problem` confirms `CHANGE` exists. Neither notices a
    reviewer that reasoned about one sentence and rewrote another, and stage 5
    is meant to catch that by reading both -- this is what holds when it does
    not.

    ! The test is that every span the edit REMOVED lies inside the sentence
    `CLAIM` names, never that the named sentence appears in the diff. A
    correction usually changes a few words of a sentence, so the removed span is
    SHORTER than the claim; requiring the reverse would refuse almost every
    honest finding.

    ! A purely additive edit removes nothing and passes. Words that only appear
    are not a claim about existing prose, so there is nothing to disagree with.

    !! THIS GOVERNS ONE REVIEWER FINDING, and it must never be turned on stage
    5's synthesis. Roy, 2026-08-17: *"at some point we are going to have to
    trust the agents to synthesize a full block and that could mean inserting
    and deleting multiple sentences with multiple rounds of review."* A
    synthesised block composes several findings, so no single `CLAIM` names
    everything it changes and this test would refuse exactly that work.
    `verdicts.py` reads REVIEWER reports, where one verdict rules on one
    sentence, and that is the only place the test is sound.

    ! It follows that each finding's `CHANGE` carries ONLY THAT FINDING'S EDIT.
    Two findings on one block each show the block with their own change and no
    other -- composing them is stage 5's job. A reviewer that folds both edits
    into both records trips this check, correctly: the record would be claiming
    one edit and showing two.

    !! IT CHECKS ONE ROUND, and a green gate is not a correct block. Roy,
    2026-08-17: *"This catches the 'first' round of edit reviews it will not
    catch the next N rounds required to make it correct."* Every round is
    measured against the text that round started from, and nothing here measures
    whether the rounds CONVERGE. Do not read this passing as the prose being
    right -- it says each reviewer edited the sentence it said it was editing.

    !! THIS GATE ASSUMES ROUND ONE, and a round-2 record does not fit it.
    Roy, 2026-08-17: a re-review sends *"the joined resolved block back to the
    reviewers that had comments ... each can say yes my edits made it and are
    correct and the other edits do not negate that or cause mine to be wrong."*
    So round 2's subject is stage 5's SYNTHESIS -- text that is on no disk and
    in no census -- while `address_problem` compares `original` against the
    census and this function compares one claim against one edit. Neither holds.

    ! Do not paper over it by exempting round 2: that would leave the
    synthesised block, the only text the author ever approves, as the one thing
    nothing checks. `TODO/re-review-is-ordered-everywhere-and-defined-
    nowhere.md` owns the shape.
    """
    spans = removed_spans(f, entry)
    if spans is None:
        return None
    if as_block(f.original, entry).lower() == as_block(f.change, entry).lower():
        return (
            f"{f.verdict}: CHANGE is the block UNCHANGED -- the verdict proposes"
            " an edit and the text does not make one"
        )
    # ! `CLAIM` is not file text -- it is a sentence the reviewer quoted -- so
    # it goes through `_words` while the spans go through `as_block`. The two
    # meet here, which is why both end lowercased and punctuation-stripped.
    named = _words(ruled_text(f))
    if not named:
        return None
    if VERDICTS[f.verdict].removes and not spans:
        return "drop: CHANGE still holds the sentence -- nothing was removed"
    for span in spans:
        # ! `_words` HERE, not inside `as_block`. The spans come off the census
        # normaliser and keep their punctuation, because that is what the census
        # stores; the claim is a quoted sentence and loses it. They are only
        # comparable at the point they meet, so the conversion belongs here and
        # `as_block` stays faithful to the census for every other caller.
        if span and _words(span) not in named:
            return (
                f"CHANGE edits {span[:40]!r}, which CLAIM does not name --"
                " the claim and the edit are about different prose"
            )
    return None


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
    ap.add_argument("reports", nargs="+", help="one report file per reviewer")
    ap.add_argument("--census", required=True, help="census.py --json output")
    ap.add_argument("--repo", default=".", help="repo root for evidence resolution")
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
        records, unattributable = parse_report(text, reviewer)
        found.extend(records)
        malformed.extend((reviewer, why) for why in unattributable)
        for line in code_concerns(text):
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
                f" named {reviewer}.md"
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
    stands = sorted(all_blocks - ruled - scoped_out)
    print(
        f"\nSTANDS UNCHANGED: {_n(len(stands), 'block')} -- clean from all"
        f" {_n(len(ran), 'reviewer')} that ran"
    )
    print(f"NEEDS A RULING:   {_n(len(ruled), 'block')}")
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
