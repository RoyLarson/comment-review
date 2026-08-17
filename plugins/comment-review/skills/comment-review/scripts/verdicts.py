"""Stage 5's gate: join four reviewers' reports against the census.

    python verdicts.py --census census.json --repo D <report>...

Checks the task agent was asked to perform by hand, every one mechanical:

  COVERAGE      every census index accounted for, by every reviewer that ran
  SOURCE        every citation resolves, and its verbatim half is really there
  BLOCK         the sentence a finding rules on is really in the block it cites
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

⚠ Exits nonzero on a coverage gap or an unverifiable citation.

⚠ It reports which findings are ADMISSIBLE. The ruling is stage 5's, in
SKILL.md's synthesis order.

⚠ Every block is accounted for by a RECORD, `clean` included. A `clean` record
carries a BLOCK and a VERDICT and nothing else, so covering N blocks costs N
records that each name a real index and assert nothing about it. A
`clean` record carries no SOURCE, so it stops short of proof the file was read:
grade a run from its DIFF, and not from this exit code.

⚠ `--reviewers` is OPTIONAL, and its absence is ANNOUNCED: without it, a
reviewer that never reported at all passes this tool unseen.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from vocabulary import Reviewer

READ_ERRORS = (OSError, UnicodeDecodeError)

VERDICTS = (
    "clean",
    "query",
    "drop",
    "correct",
    "patch",
    "add",
    "move",
)

# What a contradiction IS: one role REMOVING the sentence another rules on.
# Named rather than inlined so the join's message and this check cannot drift
# apart.
# ⚠⚠ `move` is NOT here. A relocation and a truth fix COMPOSE -- move the prose,
# then correct it at the destination, which is the synthesis order at steps 2
# and 3. Ruled 2026-08-17. Measured: 5 of 8 blocks the old set flagged were this
# shape, and the re-review spent a round on each confirming they were not rivals.
REMOVES = frozenset({"drop"})
RULES_ON_TEXT = frozenset({"correct", "patch"})

# ⚠⚠ The THREE shapes `reviewer-brief.md` says reach `query`, and a query must
# NAME the one it is. A closed set beats guessing at free text: the shape decides
# whether the block is work (the author must answer) or a boundary report (the
# role is saying which scope owns it), and that is not something to infer from
# whether a sentence happens to contain the word "resolved".
OUT_OF_ROLE = "outside my role"
QUERY_SHAPES = (OUT_OF_ROLE, "outside the checkout", "outside the code")

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
FIELD = re.compile(r"^\s*(BLOCK|VERDICT|SOURCE|CLAIM|REASON|CHANGE)\s+(.*)$")
# `file:line` or `file:start-end`, as a SOURCE writes its citation half.
CITE = re.compile(r"^(.+?):(\d+)(?:-(\d+))?$")

# How far from the cited line the quoted text may sit. Prose wraps and code
# moves; a hard equality would reject honest citations, and a wide window would
# accept a fabricated one.
SOURCE_WINDOW = 3

# The floor on a SOURCE's verbatim half, and it is ONE: zero length is not text.
# It was 12, which refused `x = 1`, `pass` and `return` -- real short lines whose
# only route through was to quote MORE than was read.
MIN_NEEDLE = 1

# What an `add`'s PAYLOAD must carry: a SIDE, and the anchor NAMED.
#
# ⚠ Backticks are the repo's own citation form -- the brief says cite by symbol
# or path, never by line number, and every record in it writes a symbol that way.
# So "named" is checkable without guessing which token is an identifier.
ANCHOR_SIDE = re.compile(r"\b(above|below|before|after)\b", re.I)
ANCHOR_NAME = re.compile(r"`[^`\s][^`]*`")

# What a `query`'s PAYLOAD must name: a check that was attempted, and the thing
# that would settle the claim.
#
# ⚠ A SHAPE check: it removes the query that names no check at all, and the
# word "grepped" passes it. A query owes a SOURCE on top of this --
# `source_problem` exempts `clean` alone.
#
# Matched on WORD BOUNDARIES. As substrings, "ran" hit *b**ran**ch*,
# *****ran***ge* and *t**ran**sfer*, and "settle" hit *un**settle**d*, so
# ordinary English naming no check passed while an honest query worded with
# "requires" / "resolves" / "determined by" was refused. `grep` is the one
# deliberate exception, left unanchored on its left so "ripgrep" counts:
# English words carry "ran" and "read" by accident, and "grep" they do not.
#
# ⚠⚠ The vocabulary is DERIVED from the verbs a reviewer is instructed in, never
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

    Field order follows the record in `reviewer-brief.md`. `sources` holds one
    entry per place examined, each `file:line | verbatim` -- BOTH halves
    verbatim, which is why they are one field where `claim` and `reason` are
    two.

    ⚠⚠ `claim` is the SURGICAL SPEC -- what must change, and from what to what.
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

    ⚠ `clean` and `query` carry NEITHER. A `clean` rules on nothing; a `query`
    says the claim is unsettled, so there is no text for stage 5 to apply.

    ⚠⚠ `move` changes TWO blocks, so its `change` shows both, `to:` and `from:`
    -- the destination once the prose arrives, and the origin once it has left.
    `from:` may be omitted, and omitting it ASSERTS the whole block moved.
    ⚠ Those two labels are `claim`'s words reused: in `claim` they are PLACES,
    in `change` they are the resulting BLOCKS. The field decides which.

    ⚠⚠ EVERY check that reads the ORIGINAL sentence reads it out of `claim`.
    `change` is a whole block, so no sentence can be parsed back out of it --
    which is the point: a reviewer that hands over a block has said what the
    result IS, not only what to swap, and stage 5 applies it rather than
    re-deriving it.

    ⚠ `reason` is the why: the evidence that verifies the claim. It is DERIVED
    and no checker can settle it, which is why it stays out of `sources`.
    """

    reviewer: str
    block: int
    verdict: str
    sources: list[str]
    claim: str
    reason: str
    change: str


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

    ⚠ A malformed record used to be a `Finding` carrying `block=-1`, and its
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
        # ⚠ SOURCE ACCUMULATES where every other field overwrites: a finding may
        # cite several places, one line each, and repeating the line avoids a
        # separator that verbatim text could contain.
        sources: list[str] = []
        # ⚠⚠ A line that names no field CONTINUES the one above it. `CHANGE`
        # holds a whole block of replacement prose, which is several lines by
        # construction, and those lines were previously skipped -- a multi-line
        # CHANGE arrived holding only its first line, silently.
        #
        # ⚠ A blank line ends the continuation, so a record may still be spaced
        # out without the gap being read as part of a field.
        last: str | None = None
        for line in body.splitlines():
            m = FIELD.match(line)
            if not m:
                if not line.strip():
                    last = None
                elif last == "SOURCE" and sources:
                    sources[-1] += "\n" + line.strip()
                elif last:
                    fields[last] += "\n" + line.rstrip()
                continue
            key = m.group(1)
            last = key
            if key == "SOURCE":
                sources.append(m.group(2).strip())
            else:
                fields[key] = m.group(2).strip()
        raw_block = fields.get("BLOCK", "")
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
                )
            )
        else:
            malformed.append("a record with no BLOCK index")
    return found, malformed


def code_concerns(text: str) -> list[str]:
    """The `CODE CONCERNS` lines a report carries, if it has the section.

    ⚠ NOT a verdict and NOT gated. `reviewer-brief.md` sends a code problem here
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

    `query` is checked in the most detail, because it is the one verdict whose
    payload has a fixed shape the brief spells out.
    """
    # ⚠ Every verdict but `clean` states WHY, and `REASON` is the field that
    # holds it. It went unchecked while it doubled as a diagnostic slot for
    # malformed records; those are separate now, so it can be required.
    if f.verdict != "clean" and not f.reason.strip():
        return f"{f.verdict} states no REASON — why the verdict was made"
    # ⚠ CLAIM is the specific thing that must happen to make the result correct.
    # A finding without one has named a defect and asked for nothing.
    if f.verdict != "clean" and not f.claim.strip():
        return f"{f.verdict} states no CLAIM — what must happen to make it right"
    # ⚠ A reviewer that echoes the claim back has filed a verdict with no
    # reason. Compared normalised, because quoting and case are what make an
    # echo look like a statement.
    #
    # ⚠⚠ EQUALITY, never containment. A REASON that quotes the claim and then
    # says what is wrong with it is doing its job, and a containment test would
    # refuse exactly the well-written ones.
    claim = " ".join(f.claim.split()).strip().strip('"').lower()
    reason = " ".join(f.reason.split()).strip().strip('"').lower()
    if claim and reason == claim:
        return "REASON restates CLAIM — say what you derived, not what it says"
    # ⚠⚠ Every per-verdict shape below is CLAIM's, because CLAIM is the SPEC.
    # CHANGE is only required to EXIST: it is a block of finished prose, and no
    # checker can judge whether prose is good -- only whether it was supplied.
    spec = f.claim.lower()
    if f.verdict == "query":
        named = [s for s in QUERY_SHAPES if s in spec]
        if not named:
            return (
                "query must NAME its shape — one of "
                + ", ".join(f"'{s}'" for s in QUERY_SHAPES)
                + " — so the reason is attached to the ruling"
            )
        # ⚠ The shape is REMOVED before the word search. `check\w*` matches
        # "checkout", so "outside the checkout" would satisfy the attempted-check
        # test by naming itself -- a query could pass by declaring its shape and
        # doing nothing.
        probe = spec
        for shape in named:
            probe = probe.replace(shape, " ")
        if not QUERY_ATTEMPTED.search(probe):
            return (
                "query needs the check you ATTEMPTED — a query naming none"
                " hands the judgement back"
            )
        if not QUERY_SETTLES.search(probe):
            return "query needs what WOULD settle the claim"
        # ⚠ A query proposes no text, so it owes no CHANGE and returns here.
        return None
    if f.verdict == "correct" and not ("false:" in spec and "true:" in spec):
        return "correct needs a false/true pair in CLAIM"
    # ⚠⚠ `patch` and `move` take `from:`/`to:` where `correct` takes
    # `false:`/`true:`. The pair differs on purpose: `correct` asserts the
    # sentence is FALSE, and that assertion is what separates it from a `patch`,
    # where the sentence is true and merely reads badly. A neutral from/to would
    # erase the distinction the synthesis order depends on.
    #
    # ⚠ `move`'s halves are PLACES, not text -- from here, to there -- so it is
    # the one edit whose CLAIM names no sentence, and `ruled_text` reports ""
    # for it. The BLOCK it cites is what identifies the prose.
    if f.verdict in ("patch", "move") and not ("from:" in spec and "to:" in spec):
        return f"{f.verdict} needs a from/to pair in CLAIM"
    if f.verdict == "drop" and "drop:" not in spec:
        return 'drop needs the sentence in CLAIM, as `drop: "..."`'
    if f.verdict == "add":
        # ⚠ The brief asks for "the text AND its anchor — which code, above or
        # below": a NAMED site and a side. This used to accept the bare word
        # "anchor", so `add an anchor comment` passed while
        # `above `retry_budget`` failed for not saying "anchor".
        if "missing:" not in spec:
            return 'add needs the text in CLAIM, as `missing: "..."`'
        if not ANCHOR_SIDE.search(spec):
            return "add needs a side — is the text above or below the anchor"
        if not ANCHOR_NAME.search(f.claim):
            return (
                "add needs the anchor NAMED in backticks — which declaration,"
                " not the word 'anchor'"
            )
    if f.verdict != "clean" and not f.change.strip():
        return (
            f"{f.verdict} carries no CHANGE — the edit already made, written out"
            " with its surrounding block, which is what stage 5 applies"
        )
    # ⚠⚠ A `move` is the one edit that changes TWO blocks, so its CHANGE shows
    # both: `to:` is the destination as it reads once the prose arrives, and
    # `from:` is the origin as it reads once the prose has left. Ruled
    # 2026-08-17.
    #
    # ⚠ `from:` is OPTIONAL, and leaving it out ASSERTS the WHOLE block moved --
    # there is no remainder to show. Nothing can tell a whole-block move from a
    # partial one by inspection, so the reviewer says which by what it supplies.
    if f.verdict == "move" and "to:" not in f.change.lower():
        return (
            "move needs the DESTINATION block in CHANGE, as `to: ...` — plus"
            " `from: ...`, the origin as it reads after, unless the WHOLE block moves"
        )
    return None


def _resolve_lines(cite: str, repo: Path) -> tuple[Path, int, int, list[str]] | str:
    """Resolve ONE `file:line` or `file:start-end` citation, or say why not.

    Shared by SOURCE and LOCATION: both are inadmissible on exactly the same
    grounds -- an unparseable citation, a missing file, or a line number past
    the end of it (or below 1, which is off every file).

    ⚠ It resolves a SINGLE citation. `source_problem` calls it once per SOURCE
    line, because a claim often needs two sites to settle.

    ⚠ An `allow_range` flag held the citation to `file:line` and refused
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

    Reads each cited line out of the file and looks for that SOURCE's verbatim
    half within a few lines of it. A finding whose text is absent from the file
    it cites is a finding the file did not supply — a report is evidence of
    nothing on its own.

    ⚠ The only floor is `MIN_NEEDLE`, which is ONE. What binds is PRESENCE: a
    short needle absent from the file is refused like any other.

    ⚠ SOURCE is checked and `REASON` is not. `REASON` is the DERIVED statement —
    *"31 callers, all under tests/"* — which is the reviewer's own sentence, so
    checking it against the tree made every counted claim structurally
    inadmissible. The forcing function lands on the field that is verbatim.

    ⚠⚠ `query` is NOT exempt. `reviewer-brief.md` has always said a query
    "requires `SOURCE`(s), by construction -- this is where you looked", and
    this script waived it; Roy ruled the brief right on
    2026-08-16. Where you looked is a real line in the checkout on all three
    query shapes, so it resolves like any other citation. Only `clean` is
    exempt, because a `clean` reports no claim to cite.

    ⚠⚠ SEVERAL CITATIONS, comma-separated, and EVERY one must resolve. The
    brief has always asked for "`file(s):line(s)` you opened", and this took one
    `file:line` for the whole field -- so a reviewer that cited two sites was
    refused for following the brief. Measured 2026-08-17 on a live run: 15 of 22
    refusals were the contract, not the reviewer. Roy ruled the gate widens.
    ⚠ This makes the check STRICTER. Three citations that all resolve is more
    evidence than one, and a reviewer forced to pick one was being made to drop
    the other -- which is the cut-the-provenance failure stage 5 already names.
    """
    if f.verdict == "clean":
        return None
    if not f.sources:
        return "no SOURCE — a finding cites where it looked"
    for source in f.sources:
        cite, sep, verbatim = source.partition("|")
        if not sep:
            return f"SOURCE {source!r} has no `|` — it is `file:line | verbatim`"
        resolved = _resolve_lines(cite.strip(), repo)
        if isinstance(resolved, str):
            return f"SOURCE {resolved}"
        _target, lineno, _end, lines = resolved
        needle = " ".join(verbatim.split()).strip().strip('"')
        if len(needle) < MIN_NEEDLE:
            return f"SOURCE {cite.strip()} carries no verbatim half"
        lo = max(0, lineno - 1 - SOURCE_WINDOW)
        window = " ".join(
            " ".join(ln.split()) for ln in lines[lo : lineno + SOURCE_WINDOW]
        )
        if needle[:40].lower() not in window.lower():
            return f"SOURCE not found near {cite.strip()}: {needle[:40]!r}"
    return None


def block_problem(f: Finding, blocks: list[dict]) -> str | None:
    """Is the sentence this finding rules on actually IN the block it cites?

    ⚠⚠ This is what `LOCATION` never did, and why retiring it is a NET GAIN.
    `LOCATION` was checked for RESOLVABILITY -- does `a.py:342` exist -- and
    never against the block it claimed to describe, so a finding attached to the
    wrong block resolved cleanly. The census carries each block's joined text
    and the gate already loads it, so this costs nothing and catches that.

    ⚠⚠ Keyed on the ORIGINAL SENTENCE, which `CLAIM` carries in its `drop:`,
    `false:` or `from:` half -- never on `CHANGE`, which is the finished block
    and holds the REPLACEMENT. Matching the replacement against the original
    block would refuse every correct finding and pass the ones that changed
    nothing. `ruled_text` reads it, the same text the contradiction check keys
    on.

    ⚠ Exempt: `clean` rules on nothing, `add` is about prose that is MISSING,
    `query` proposes no edit, and a `move`'s from/to are PLACES rather than
    text. All four -- and any malformed spec -- reach here as `ruled_text` "".

    Args:
        f: the finding.
        blocks: the census, as `census.py --json` emits it.

    Returns:
        The problem, or None. ⚠ An out-of-range block returns None: `main()`
        reports it already, and saying so twice reads as two defects.
    """
    if f.verdict in ("clean", "add"):
        return None
    if not 1 <= f.block <= len(blocks):
        return None
    needle = ruled_text(f)
    if not needle:
        return None
    haystack = " ".join(str(blocks[f.block - 1].get("text", "")).split()).lower()
    if needle[:40] not in haystack:
        return f"the sentence ruled on is not in block {f.block}: {needle[:40]!r}"
    return None


def declares_scope(f: Finding) -> bool:
    """A `query` saying the block is not this role's to read.

    Not a ruling: nothing is asked of the task agent, and the role is reporting
    the boundary it was told to report. Every other `query` IS work -- it names a
    claim nobody could settle, and the brief sends it to the author.
    """
    return f.verdict == "query" and OUT_OF_ROLE in f.claim.lower()


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

    ⚠⚠ Read out of CLAIM, the surgical spec. CHANGE is the whole resulting
    block, so the original cannot be recovered from it -- the `drop:`,
    `false:` and `from:` halves of CLAIM are the only verbatim originals a
    record carries.

    ⚠ FOUR verdicts return "" and always will. `clean` rules on nothing; `add`
    is about prose that is MISSING; `query` proposes no edit; and `move`'s
    from/to are PLACES rather than text, so it names no sentence either.

    ⚠ Also "" when the spec is malformed. A caller must treat that as "cannot
    compare", never as "no overlap" -- silence there would hide a real collision
    behind an unreadable payload.
    """
    if f.verdict in REMOVES:
        _, sep, rest = f.claim.partition("drop:")
        text = rest if sep else f.claim
    elif f.verdict == "correct":
        _, sep, rest = f.claim.partition("false:")
        if not sep:
            return ""
        text = rest.partition("/ true:")[0]
    elif f.verdict == "patch":
        _, sep, rest = f.claim.partition("from:")
        if not sep:
            return ""
        text = rest.partition("/ to:")[0]
    else:
        return ""
    # ⚠ Strip AGAIN after the quotes come off. A reviewer that pads inside the
    # quotes -- `false: "  the budget is 3 "` -- otherwise keeps those spaces,
    # and the needle then matches nothing in a block that plainly contains it.
    return " ".join(text.split()).strip().strip('"').strip().lower()


def contradictions(grouped: dict[int, list[Finding]]) -> list[int]:
    """Blocks where one role REMOVES the sentence another rules on.

    `drop` against `correct`/`patch` is one role saying the sentence should not
    exist and another saying it should exist and be fixed. Nothing composes
    those.

    ⚠⚠ Keyed on the TEXT, not the block index. A block of six sentences can
    carry six verdicts, so sharing an index is not sharing a subject -- measured
    on a live run, one of eight flagged collisions was two roles ruling on two
    different clauses of one docstring, and a re-review round was spent
    establishing it.

    ⚠ One sentence CONTAINING the other still collides: a role may drop a
    paragraph whose clause another corrects.

    ⚠⚠ `move` is absent by ruling. Relocation and a truth fix compose -- the
    synthesis order applies every `move` at step 2 and every `correct` at step
    3, which is the sequence, not a rivalry.
    """
    out: list[int] = []
    for block, fs in grouped.items():
        removals = [ruled_text(f) for f in fs if f.verdict in REMOVES]
        rulings = [ruled_text(f) for f in fs if f.verdict in RULES_ON_TEXT]
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
    # ⚠ Guarded like a report file, so a missing census prints which file and
    # why in one line.
    try:
        census_text = Path(args.census).read_text(encoding="utf-8")
    except READ_ERRORS as e:
        print(
            f"CANNOT READ {args.census} ({type(e).__name__})"
            " — no census to join against"
        )
        return 1
    try:
        blocks = json.loads(census_text)
    except json.JSONDecodeError as e:
        print(
            f"CANNOT PARSE {args.census} as JSON ({e})"
            " — is this census.py --json output?"
        )
        return 1
    # ⚠⚠ ADDRESSABLE is not ACCOUNTABLE. Every interval between two lines of
    # code is a block, so an `add` -- a finding about prose that is MISSING --
    # has an index to cite instead of borrowing a neighbour's. Most of them hold
    # nothing, and a reviewer owes no record on an empty one: coverage is over
    # the blocks that HOLD PROSE. Measured: `census.py` over itself is 546
    # blocks, 48 of them prose. Owing a record on all 546 would make `CLEAN 1-N`
    # -- the cheapest fabrication there is -- nine parts out of ten true.
    all_blocks = {i for i, b in enumerate(blocks, 1) if b.get("kind") != "interval"}

    fatal = 0

    # ⚠ Refused on every run, `--reviewers` or not: a reviewer is keyed by its
    # report's stem, so two files with the same stem put one reviewer's
    # coverage in place of the other's.
    stems = [Path(r).stem for r in args.reports]
    expected = {a.strip() for a in args.reviewers.split(",") if a.strip()}
    for stem in sorted({s for s, n in Counter(stems).items() if n > 1}):
        print(f"  DUPLICATE report stem {stem!r} — two files claim the same reviewer")
        fatal += 1

    # ⚠ A stem was taken as a role name on sight, so `ownershp-context.md` was
    # accepted as a reviewer called `ownershp-context` and every line below
    # named a role that does not exist. `Reviewer` is the published list.
    published = {r.value for r in Reviewer}
    for name in sorted(set(stems) | expected):
        if name not in published:
            print(
                f"  UNKNOWN reviewer {name!r} — not one of"
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
                f"  CANNOT READ {raw} ({type(e).__name__}) — {reviewer} did not report"
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

    # ⚠ DECLARED, the way this repo names a population everywhere else. Without
    # --reviewers, "every reviewer" means "every file I was handed", so a
    # reviewer that reported nothing at all passes unseen.
    if args.reviewers:
        for reviewer in sorted(expected - reported):
            print(
                f"  NO REPORT from reviewer {reviewer!r} — a missing report is the"
                " easier version of a fabricated one. --reviewers is matched against"
                f" each report file's STEM, so a report for {reviewer!r} must be"
                f" named {reviewer}.md"
            )
            fatal += 1
    else:
        print(
            "⚠ --reviewers not given: whether every expected reviewer reported was"
            " NOT checked.\n"
        )

    gaps = coverage_gaps(all_blocks, reported, found)
    if gaps:
        print("COVERAGE GAPS - indices no reviewer accounted for:")
        for reviewer, missing in sorted(gaps.items()):
            shown = ", ".join(str(n) for n in missing[:20])
            more = f" (+{len(missing) - 20} more)" if len(missing) > 20 else ""
            print(
                f"  {reviewer}: {_n(len(missing), 'block')} unaccounted — {shown}{more}"
            )
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
        wrong_block = block_problem(f, blocks)
        if wrong_block:
            print(f"  BLOCK {f.block} {f.reviewer}: {wrong_block}")
            fatal += 1
        payload = payload_problem(f)
        if payload:
            print(f"  BLOCK {f.block} {f.reviewer}: {payload}")
            fatal += 1

    grouped = by_block(found)
    clash = contradictions(grouped)
    if clash:
        print(f"\nRE-REVIEW — drop/move against correct/patch on: {clash}")
        print(
            "  Not a tie-break. Send the block back; the synthesis order"
            " must not decide it."
        )

    # ⚠⚠ THREE STATES, NOT TWO. A block covered only by `clean` and out-of-role
    # queries is neither: no role certified it -- module-context returns `query`
    # rather than `clean` so it does not certify what it never read -- and
    # nothing is asked of stage 5 either. Counting those as work buried 76 real
    # verdicts inside 1159 on a measured run.
    ran = sorted(reported | {f.reviewer for f in found})
    in_range = [f for f in found if 1 <= f.block <= len(blocks)]
    ruled = {
        f.block for f in in_range if f.verdict != "clean" and not declares_scope(f)
    }
    scoped_out = {f.block for f in in_range if declares_scope(f)} - ruled
    stands = sorted(all_blocks - ruled - scoped_out)
    print(
        f"\nSTANDS UNCHANGED: {_n(len(stands), 'block')} — clean from all"
        f" {_n(len(ran), 'reviewer')} that ran"
    )
    print(f"NEEDS A RULING:   {_n(len(ruled), 'block')}")
    if scoped_out:
        print(
            f"NO FINDING, NOT CERTIFIED: {_n(len(scoped_out), 'block')} — every"
            " role that read it was `clean`, and at least one said it was outside"
            " its role. Nothing to rule; nothing certified either."
        )
    if gaps:
        print("  ⚠ counts above are provisional: coverage is incomplete.")

    # ⚠ The WORK LIST. Stage 5 holds several rulings per block and must emit ONE
    # replacement, so this grouping is what it works from -- and rebuilding it
    # from the report files by hand is the step this tool can do exactly and a
    # reader cannot.
    # ⚠ Withheld when anything is FATAL. The gate has just refused the report,
    # so a work list here reads as permission to start on it.
    out_for_rereview = set(clash)
    if ruled and not fatal:
        print("\nPER BLOCK — what you hold, in census order:")
        for b in sorted(ruled):
            marks = "  ".join(
                f"{f.verdict}({f.reviewer})"
                for f in sorted(grouped[b], key=lambda f: (f.verdict, f.reviewer))
                if f.verdict != "clean" and not declares_scope(f)
            )
            flag = "   ⚠ RE-REVIEW" if b in out_for_rereview else ""
            print(f"  {b:4d}  {marks}{flag}")

    # ⚠ Printed whether or not the gate refuses, and counted toward nothing. A
    # code problem is not a verdict, so it is neither admissible nor
    # inadmissible -- but a run that stops at stage 5 must still carry it, or the
    # defect dies with the refusal.
    if concerns:
        print(f"\nCODE CONCERNS — {_n(len(concerns), 'line')}, no verdict, not gated:")
        for reviewer, line in concerns:
            print(f"  {reviewer}: {line}")

    if fatal:
        print(f"\n{_n(fatal, 'problem')}. Resolve or send back before stage 5 rules.")
        return 1
    if clash:
        # ⚠ A contradiction is counted apart from the fatal checks: it is a
        # re-review, and both records are well formed.
        # The closing line still has to say so -- printing "send the block back"
        # and then "Stage 5 may rule" four lines later made the summary
        # contradict its own body at exit 0.
        print(
            f"\nEvery finding is admissible. {_n(len(clash), 'block')} still OUT"
            " for re-review — stage 5 may rule on the rest."
        )
        return 0
    print("\nEvery finding is admissible. Stage 5 may rule.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
