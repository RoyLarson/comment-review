"""What a RECORD is: the shape a reviewer fills, and the file that carries them.

    python record.py --seed  --census census.json --reviewer ROLE --out DIR/ROLE.json
    python record.py --check DIR/ROLE.json --census census.json

A record is one ruling on one sentence. It used to travel as prose that
`verdicts.py` reconstructed a table from by guessing where each field ended,
and every guess was a defect surface -- a malformed citation absorbed into the
valid one above it, a bare label absorbed into the field above it, a dropped
span absorbing the punctuation beside it. Each of those reported its error
against work that was CORRECT.

!! A REVIEWER FILLS A TEMPLATE; IT DOES NOT COMPOSE A DOCUMENT. `--seed` writes
one slot per prose block with `block` and `address` already in it, so the
reviewer sets only what it decides: `verdict`, `claim`, `reason`, `sources`,
`change`. **Validation then asks whether the answer is COMPLETE rather than
whether the syntax can be parsed** -- a missing field is visibly empty, not
absent.

!! THE REVIEWER NEVER TRANSCRIBES THE BLOCK, and that retires a whole class of
refusal rather than a bug in one. Measured 2026-08-17: **83 refusals in one run
were spent on transcription fidelity, and not one of them was about a finding.**

!! IT IS NOT GIVEN THE TEXT EITHER -- only where to find it. A record carrying
the prose lets a reviewer rule without opening the file, which every role's
remit forbids and no check can detect. `slot()` carries the argument.

! `change` is a LINE ARRAY, which is what the census stores and what a diff can
compare without aligning tokens. A token diff had to decide where a span BEGAN,
and got it wrong on a trailing full stop and on markdown emphasis; lines have
no such question.

! COVERAGE IS STRUCTURAL. Every prose block gets a slot, so a block nobody
ruled on is a slot with a null verdict rather than an index missing from a
list, and nothing has to reconcile what was expected against what arrived.

!! A SEEDED SLOT IS NOT THE ONLY LEGAL RECORD -- APPEND ONE FOR ANY CENSUS
INDEX. `--seed` lays down the PROSE blocks because those are what a reviewer is
ACCOUNTABLE for, and an empty `interval` gets none. But `add` exists to cite an
interval: its finding is that a constraint holds in code and appears in NO
prose, so its subject is the gap. **A reviewer filing an `add` writes a new
record carrying that interval's index and address**, and `--check` reads it
like any other. ! Measured 2026-08-17: converting a held report that filled only
seeded slots turned 228 findings into 226, losing both of its `add`s in
silence.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from repo import READ_ERRORS  # noqa: E402  -- path shim must run first

# !! THE VERDICT TABLE LIVES HERE because a record IS a verdict and its payload,
# and `allowed()` below is derived entirely from this table. It sat in
# `verdicts.py` and was imported back, which made the two modules a cycle and
# blocked `claim_object` from being read by the join that needs it.
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
        may_empty: this verdict may leave the block with NOTHING in it, so an
            empty `CHANGE` is the edit rather than a missing one. Only `drop`,
            and only where `CLAIM` names the whole block -- `edit_problem`
            checks that rather than taking the reviewer's word, so a blank
            `CHANGE` is not a way to skip writing one. ! Without this a
            whole-block `drop` could not be expressed at all: the reviewer
            wrote the blank deliberately and said so in `REASON`, which nothing
            downstream reads. Measured 2026-08-17.
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
    may_empty: bool = False
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
    # !! WHAT THE BRIEF SAYS THIS VERDICT'S `claim` CARRIES, and the row owns it
    # so there is one source and one way to copy it. `scripts/render_brief.py`
    # writes the table in `reviewer-brief.md` from these plus `claim_keys`, and
    # a test refuses a brief that has drifted from them.
    #
    # ! It does NOT restate the key names -- those are generated. Measured
    # 2026-08-18, which is why: the hand-written table taught the 0.2.x marker
    # form (`false: "..." / true: "..."`) forty lines under a JSON worked
    # example, and ten of the eleven keys a reviewer must type appeared nowhere
    # in the brief as keys.
    payload: str = ""


VERDICTS: dict[str, Verdict] = {
    "clean": Verdict(
        payload=(
            "nothing. Name your role and stop -- `clean` proposes no text, so there"
            " is nothing for the task agent to apply"
        ),
        owes_claim=False,
        owes_reason=False,
        owes_change=False,
        owes_address=False,
        owes_sources=False,
        diffable=False,
        substantive=False,
    ),
    "query": Verdict(
        payload=(
            "the SHAPE in the brief's own words, the check you ATTEMPTED, and what"
            " WOULD settle it. All three are checked as SHAPE and none as truth; the"
            " claim itself is checked by nothing, so the other three are all that"
            " stands behind the ruling"
        ),
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
        payload=(
            "the sentence, verbatim, as it stands in the block. ! It is CHECKED"
            " against the census text, so a paraphrase is refused"
        ),
        claim_all=("drop:",),
        claim_help='drop needs the sentence in CLAIM, as `drop: "..."`',
        quotes_original="drop:",
        removes=True,
        may_empty=True,
    ),
    "correct": Verdict(
        payload=(
            "the false clause and the true one, and a `sources` entry carrying the"
            " line that settles it. ! The FALSE half is checked against the block --"
            " if it is not there, the finding is on the wrong block"
        ),
        claim_all=("false:", "true:"),
        claim_help="correct needs a false/true pair in CLAIM",
        quotes_original="false:",
        quotes_until="/ true:",
        rules_on_text=True,
    ),
    "patch": Verdict(
        payload=(
            "the sentence as it stands and the rewrite. ! `from` is checked against"
            " the block. A `patch` needs no source: the claim is already true, and"
            " only its wording is at issue"
        ),
        claim_all=("from:", "to:"),
        claim_help="patch needs a from/to pair in CLAIM",
        quotes_original="from:",
        quotes_until="/ to:",
        rules_on_text=True,
    ),
    "add": Verdict(
        payload=(
            "the text that is missing, the anchor NAMED IN BACKTICKS, and which side"
            ' of it. ! The word "anchor" is not an anchor -- name the declaration'
        ),
        claim_all=("missing:",),
        claim_help='add needs the text in CLAIM, as `missing: "..."`',
        diffable=False,
        needs_anchor=True,
    ),
    "move": Verdict(
        payload=(
            "where the prose sits now and where it belongs -- another line, another"
            " file, or out of the code entirely. ! These are PLACES, not text: the"
            " same two key names in `change` mean the resulting BLOCKS"
        ),
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


# What an `add`'s PAYLOAD must carry: a SIDE, and the anchor NAMED.
#
# ! Backticks are the repo's own citation form -- the brief says cite by symbol
# or path, never by line number, and every record in it writes a symbol that way.
# So "named" is checkable without guessing which token is an identifier.
ANCHOR_SIDE = re.compile(r"\b(above|below|before|after)\b", re.I)
ANCHOR_NAME = re.compile(r"`[^`\s][^`]*`")


def claim_keys(spec: "Verdict") -> tuple[list[str], list[str]]:
    """The `claim` keys this verdict owes: `(markers, extras)`.

    !! ONE ROW, which is the promise the `Verdict` table makes and which four
    sites had taken back. `record.allowed` told a reviewer what to fill,
    `record.claim_object` read the deprecated form, `claim_text` rendered it
    and `payload_problem` checked it -- each deriving the same key list from
    the same traits, and two of them hardcoding the names. A new trait had to
    be added in four places and nothing failed if one was missed.

    ! `markers` are the keys that render as `key: "value"`; `extras` are the
    ones carried as prose beside them. The split is what `claim_text` needs and
    it is the only reason this returns a pair.

    Args:
        spec: the verdict's row.

    Returns:
        `(markers, extras)`, each in the order a record states them.
    """
    markers = [marker.rstrip(":") for marker in spec.claim_all]
    extras: list[str] = []
    # ! `query`'s `claim_any` is a set of PHRASES, not keys -- it names its
    # SHAPE, so the phrase is the value and the key is fixed.
    if spec.claim_any:
        extras.append("shape")
    if spec.needs_attempted:
        extras.append("attempted")
    if spec.needs_settles:
        extras.append("settles")
    if spec.needs_anchor:
        extras += ["anchor", "side"]
    return (markers, extras)


# !! A `Finding` IS A RECORD IN MEMORY, which is why it sits with the table that
# says what one owes. It was in `verdicts.py` with the reader that builds it and
# the checks that read it, so both of those had to be one module or import a
# type from each other.
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

    !! `block` is an INDEX and `address` is `path:start-end`. THE REVIEWER
    WRITES NEITHER: `record.py --seed` puts both in the slot and both are
    checked against the census, so a mismatch says the file was edited rather
    than that a reviewer misquoted.

    ! `original` is that block's text, and it is filled from the CENSUS by
    `main` after the report is read. It was the reviewer's to transcribe under
    the first ruling of 2026-08-17 -- *"BLOCK gets the address and the original
    text verbatim"* -- and a second ruling the same day replaced it: handed the
    prose, a reviewer can produce a complete admissible ruling without opening
    the file, and no check can tell that from real work. 83 refusals in one
    measured run were spent on transcription fidelity and none was about a
    finding.

    ! `claim_fields` is the claim as the record held it, and empty for a 0.2.x
    text record. A check that can read a FIELD must not search the string
    `claim_text` renders it into -- see `_said`.

    ! `clean` owes no claim and no change. A role returns `clean` on most of
    the census -- 1159 blocks on one measured run.
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
    # !! THE CLAIM AS THE RECORD CARRIED IT, empty for a 0.2.x text record. A
    # check that can read the FIELD must not word-search the string the field
    # rendered into: the reviewer answered, and searching its wording for five
    # accepted verbs refuses correct answers written in other words. Measured
    # 2026-08-17 on the first JSON run: nine well-formed `query` records
    # refused, every one carrying a filled `settles`.
    claim_fields: dict = dataclass_field(default_factory=dict)


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


def _said(f: Finding, key: str) -> str:
    """What the record put in this `claim` key, or "" if it carries no fields.

    !! THE FIELD IS THE ANSWER; the rendered string is a fallback. `claim_text`
    builds one string out of every key, so a check that searches it for one
    key's value can be satisfied by another key's prose. Measured 2026-08-17: a
    `query` whose `settles` mentioned the phrase "outside my role" was
    classified as a scope declaration and dropped out of the work list.

    ! Empty for a 0.2.x text record, and every caller falls back to searching
    the string for exactly that case. That is the only path the deprecated
    format has.

    Args:
        f: the finding.
        key: the `claim` key wanted.

    Returns:
        The value as a string, or "".
    """
    return str(f.claim_fields.get(key, "")) if f.claim_fields else ""


def _claim_values(f: Finding) -> str:
    """Everything the reviewer WROTE in `claim`, without the marker words.

    !! `claim_text` prepends each key as a marker -- `drop: "..."` -- so a check
    comparing prose against the rendered string is comparing against a string
    that can never equal it. Measured 2026-08-17: the REASON-restates-CLAIM
    gate could not fire on any JSON record, for any verdict. It was switched
    off by the bridge that generated the string, silently.

    Args:
        f: the finding.

    Returns:
        The claim's values joined, or the rendered claim for a text record.
    """
    if not f.claim_fields:
        return f.claim
    return " ".join(str(v) for v in f.claim_fields.values())


def _answered(f: Finding, key: str, pattern: re.Pattern, probe: str) -> bool:
    """Did the reviewer answer `key` -- by its field, or failing that its words?

    !! THE FIELD OUTRANKS THE WORD SEARCH, and that is the whole point of a
    typed record. `record.py` gives a `query` a `settles` slot and refuses a
    record that leaves it out, so a filled slot has already answered the
    question this check asks. Searching the rendered prose for `settl`, `would`,
    `requires`, `resolv` or `determined by` then refuses an answer written in
    any other words -- and the reviewer's remedy is to pad the sentence with an
    accepted verb, which is a finding reshaped to satisfy a parser.

    ! Measured 2026-08-17, the first run over JSON records: nine `query` records
    refused for want of a settles-word, every one carrying a filled `settles`.
    One reads *"reading this docstring against the body of `line_endings` and
    against `splice`"* -- a check, named, containing none of the five.

    ! The word search STAYS for a 0.2.x text record, where there is no field to
    read: `claim_fields` is empty and this falls through to `pattern`. That is
    the only route by which the deprecated format keeps its guarantee.

    Args:
        f: the finding.
        key: the `claim` key that answers this check.
        pattern: the word search, for a record with no fields.
        probe: the rendered claim with its shape removed.

    Returns:
        True if the question was answered.
    """
    if f.claim_fields:
        return bool(str(f.claim_fields.get(key, "")).strip())
    return bool(pattern.search(probe))


def _n(count: int, noun: str) -> str:
    """`"1 block"`, `"2 blocks"` -- this output decides whether an agent proceeds."""
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


# The fields the TOOL fills from the census. ! A mismatch here means the file
# was CORRUPTED, never that the reviewer misquoted -- it never typed them.
SEEDED = ("block", "address")
# !! THE SHAPE IS VERSIONED, so a held report stays a REGRESSION TEST rather than
# becoming an archive the day the format moves. Replaying stage-4 output is what
# made 0.2.1 and 0.2.2 cheap to validate -- five joins over one set of reports,
# ~1.6M tokens of review reused -- and that property dies silently when the
# shape changes and nothing says so.
#
# ! PINNING THE CENSUS IS NOT ENOUGH. `SOURCES` cites the WORKING TREE, so a
# replay needs the tree at the run's commit too. Measured 2026-08-17: the same
# four reports joined green against a worktree at their commit and produced 78
# "SOURCES not found" against HEAD, 197 lines later in one file. Neither the
# reader nor the reports were wrong.
RECORD_VERSION = "1"
# The fields the REVIEWER fills. Empty is a legitimate answer for every one of
# them except `verdict`, which is the ruling itself.
ANSWERED = ("verdict", "claim", "reason", "sources", "change")


def prose_blocks(census: list[dict]) -> list[tuple[int, dict]]:
    """Every census block that HOLDS PROSE, with its 1-based index.

    ! An `interval` holds nothing and no reviewer owes it a record. It stays
    ADDRESSABLE so an `add` can cite the gap it is about, which is why the
    census numbers every one -- but it is not accountable, and seeding a slot
    for each would bury 224 real questions under 1730 empty ones.
    """
    return [(i, b) for i, b in enumerate(census, 1) if b.get("kind") != "interval"]


def slot(index: int, block: dict) -> dict:
    """One record, seeded from the census and otherwise empty.

    Args:
        index: the block's 1-based census index, which is its identity.
        block: the census entry.

    Returns:
        The record as the reviewer receives it.
    """
    return {
        "block": index,
        # !! THE ADDRESS AND NOTHING ELSE. The record does not carry the block's
        # text, so a reviewer cannot rule on it without OPENING THE FILE -- and
        # every role's remit requires that: block-context checks a claim against
        # the code it sits with, ownership-context cannot resolve an anchor
        # without reading, function-context reads name, signature and body
        # together.
        #
        # !! THE TWO ERRORS ARE NOT SYMMETRIC, which is what decides this. Hand
        # a reviewer the prose and it can produce a complete, admissible record
        # without opening anything, and NOTHING in the gate can tell that from
        # real work. Hand it only the address and it may read the wrong lines --
        # but then its `CLAIM` quotes a sentence the census block does not
        # contain, and `block_problem` already catches exactly that, using a
        # census the gate has already loaded. **One error is checked; the other
        # is invisible.**
        #
        # ! Re-check that asymmetry before reversing this. It has flipped three
        # times, and it is the only argument here that does not rest on taste.
        "address": f"{block['path']}:{block['start']}-{block['end']}",
        # ! `null`, not `""`. An unruled block must be distinguishable from one
        # ruled with an empty verdict, and only one of those is a coverage gap.
        "verdict": None,
        "claim": {},
        "reason": "",
        "sources": [],
        "change": [],
    }


def allowed() -> dict:
    """What may go in each CONSTRAINED field, stated in the file itself.

    !! A TEMPLATE THAT CONSTRAINS A FIELD WITHOUT SAYING WHAT IS ALLOWED HAS
    ONLY MOVED THE GUESSING. Half of *"fill out THIS message"* is the message
    saying what may go in each slot -- otherwise the reviewer is back to
    remembering a contract, which is the thing the template replaces.

    !! DERIVED FROM THE VERDICT TABLE, never restated. A JSON claim key is the
    table's marker minus its colon, so adding a verdict stays a ROW and this
    block cannot drift from what the gate enforces. `tests/test_record.py` pins
    that correspondence.

    Returns:
        `verdict` -> the seven; `claim` -> the keys each verdict's claim must
        carry; `values` -> the fields whose value is itself a closed set.
    """
    claims: dict[str, list[str]] = {}
    for name, spec in VERDICTS.items():
        markers, extras = claim_keys(spec)
        claims[name] = markers + extras
    return {
        "verdict": sorted(VERDICTS),
        "claim": claims,
        "values": {
            "shape": list(QUERY_SHAPES),
            "side": ["above", "below"],
        },
        # ! The one shape that is a BOUNDARY REPORT rather than work, named so a
        # reader of this file can tell the three apart without the brief.
        "scope_shape": OUT_OF_ROLE,
        # ! A FORM, not a value set, and it is stated for the same reason the
        # sets are: a template that constrains a field without saying what is
        # allowed has only moved the guessing. The join refuses an `add` whose
        # anchor is not backticked, and this file passed one -- two tools, one
        # record, different answers, which is the defect the typed record was
        # adopted to end.
        "anchor_form": "the anchor NAMED in backticks, e.g. `compute_rates`",
    }


# !! BUILT ONCE. `allowed()` walks all seven verdicts and allocates four
# structures; it was called twice per record, from `claim_problems` and
# `value_problems`. Measured 2026-08-17 over a 1174-record report with every
# slot filled: 5.44 ms of `check()`'s 8.24 ms total.
#
# ! `seed()` still calls `allowed()` for a FRESH copy, because the result is
# embedded in the JSON it writes and a shared mutable would let one run's
# report edit the next one's.
ALLOWED = allowed()


def seed(census: list[dict], reviewer: str) -> dict:
    """The whole file a reviewer is handed, ready to fill."""
    return {
        "record_version": RECORD_VERSION,
        "reviewer": reviewer,
        # ! FIRST, so it is read before the records it governs.
        "allowed": allowed(),
        "records": [slot(i, b) for i, b in prose_blocks(census)],
        # ! Code problems get one line each and carry no verdict. A list rather
        # than a section to find with a regex, which is one more boundary that
        # cannot be guessed wrong.
        "code_concerns": [],
    }


# What each answered field must BE, once it is filled. ! Shape only -- whether a
# citation resolves and whether the claim is true are `verdicts.py`'s, and
# splitting them is what makes these two files one subject each.
SHAPES: dict[str, type] = {
    "claim": dict,
    "reason": str,
    "sources": list,
    "change": list,
}


def seeded_problems(where: str, rec: dict, block: dict | None) -> list[str]:
    """Did the fields the TOOL wrote survive being filled in?

    !! THE MESSAGE MUST NOT ACCUSE THE REVIEWER OF MISQUOTING. It never typed
    these: `--seed` did. A mismatch means the FILE WAS EDITED -- a value
    clipped while its neighbour was filled -- and saying otherwise sends the
    reader to fix work that was correct, which is the defect class this whole
    format change exists to end.
    """
    if block is None:
        return [f"{where}: block {rec.get('block')!r} is not in the census"]
    want = f"{block['path']}:{block['start']}-{block['end']}"
    if rec.get("address") != want:
        return [
            f"{where}: `address` reads {rec.get('address')!r} and the census says"
            f" {want!r}. This field was WRITTEN BY THE TOOL, so it was edited"
            " after seeding -- restore it rather than re-deriving it."
        ]
    return []


def claim_problems(where: str, rec: dict) -> list[str]:
    """Does `claim` carry the keys this verdict's row requires, and no others?"""
    verdict = rec.get("verdict")
    spec = ALLOWED["claim"].get(verdict)
    if spec is None:
        return []
    claim = rec.get("claim")
    if not isinstance(claim, dict):
        # ! SILENT, because `record_problems` has already reported the type
        # through `SHAPES`. Reported here too, one defect produced two messages
        # in two vocabularies -- "not a dict" and "not an object".
        return []
    missing = [k for k in spec if k not in claim]
    extra = [k for k in claim if k not in spec]
    # !! PRESENT AND EMPTY IS MISSING. A slot is seeded for every key the
    # verdict owes, so a reviewer that skips one leaves it there holding "" --
    # and downstream `verdicts.py` now reads the FIELD rather than searching the
    # prose it renders into, so an empty field would answer a check by existing.
    blank = [k for k in spec if k in claim and not str(claim[k]).strip()]
    out = []
    # ! The one FORM the join enforces. Checked here so a record that passes
    # `--check` is a record the join admits.
    anchor = str(claim.get("anchor", ""))
    if "anchor" in spec and anchor.strip() and not ANCHOR_NAME.search(anchor):
        out.append(
            f"{where}: `claim.anchor` reads {anchor!r} -- it must NAME the"
            " declaration in backticks, which is what the join checks"
        )
    if blank:
        out.append(f"{where}: {verdict} left `claim` keys {blank} empty")
    if missing:
        out.append(
            f"{where}: {verdict} needs `claim` keys {missing} -- it carries"
            f" {sorted(claim) or 'none'}"
        )
    if extra:
        # ! An unexpected key is a finding, not noise. It is how a reviewer that
        # reached for another verdict's shape shows up before the join.
        out.append(f"{where}: {verdict} has no `claim` key {extra}")
    return out


def value_problems(where: str, rec: dict) -> list[str]:
    """Are the CONSTRAINED values among the ones the template offered?"""
    out = []
    claim = rec.get("claim")
    if not isinstance(claim, dict):
        return out
    for field, permitted in ALLOWED["values"].items():
        if field in claim and claim[field] not in permitted:
            out.append(
                f"{where}: `claim.{field}` reads {claim[field]!r}, and the"
                f" template offers {permitted}"
            )
    return out


def version_problem(report: dict) -> str | None:
    """Was this file written by a reader that agrees with this one?

    !! THE VERSION WAS WRITTEN AND READ BY NOTHING, which made the property it
    claims -- that a held report stays a regression test rather than becoming
    an archive the day the shape moves -- a sentence rather than a guarantee.
    A file from a future version was read as if it were this one, and the first
    sign of it would have been a field silently absent.

    ! A MISSING version is the 0.2.x text format converted by hand, or a file
    written before the field existed. Reported, not refused: `--convert` is the
    supported route and it writes the field.

    Args:
        report: the parsed record file.

    Returns:
        One sentence naming the disagreement, or None.
    """
    got = report.get("record_version")
    if got == RECORD_VERSION:
        return None
    if got is None:
        return (
            f"no `record_version` -- this reader writes {RECORD_VERSION!r}, and a"
            " file without one was not written by `record.py --seed`"
        )
    return (
        f"`record_version` is {got!r} and this reader is {RECORD_VERSION!r} --"
        " the shape moved, so what is missing here would not announce itself"
    )


def record_problems(where: str, rec: dict, block: dict | None) -> list[str]:
    """Everything wrong with the SHAPE of one record."""
    out = seeded_problems(where, rec, block)
    verdict = rec.get("verdict")
    if verdict is not None and verdict not in VERDICTS:
        out.append(f"{where}: verdict {verdict!r} is not one of {sorted(VERDICTS)}")
    for field, want in SHAPES.items():
        if field not in rec:
            out.append(f"{where}: no `{field}` -- the seeded template carries one")
        elif not isinstance(rec[field], want):
            out.append(
                f"{where}: `{field}` is {type(rec[field]).__name__}, not"
                f" {want.__name__}"
            )
    for i, source in enumerate(rec.get("sources") or [], 1):
        if not isinstance(source, dict) or {"cite", "verbatim"} - set(source):
            out.append(
                f"{where}: source {i} is not `{{cite, verbatim}}` -- it reads"
                f" {source!r}"
            )
    out += claim_problems(where, rec)
    out += value_problems(where, rec)
    return out


def check(report: dict, census: list[dict]) -> tuple[list[str], int]:
    """Every shape problem in a filled report, and how many slots are UNRULED.

    Returns:
        `(problems, unruled)`. ! Unruled is counted, not refused: a reviewer
        checking its own work part-way through needs to know how many slots
        are left, and that is the whole point of a template you FILL. The
        coverage GATE is `verdicts.py`'s, at the join.
    """
    problems: list[str] = []
    if not isinstance(report.get("records"), list):
        return (["no `records` list -- this is not a seeded report"], 0)
    unruled = 0
    for rec in report["records"]:
        index = rec.get("block")
        where = f"block {index}"
        known = isinstance(index, int) and 1 <= index <= len(census)
        block = census[index - 1] if known else None
        if rec.get("verdict") is None:
            unruled += 1
            # ! A slot nobody filled is not MALFORMED, so it is counted rather
            # than reported field by field.
            continue
        problems += record_problems(where, rec, block)
    return (problems, unruled)


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
        side = ANCHOR_SIDE.search(claim)
        out["anchor"] = named.group(0) if named else ""
        # ! `before`/`after` were accepted as sides and mean the same two
        # places; the new shape offers only two, so they map onto them.
        word = side.group(1).lower() if side else ""
        out["side"] = {"before": "above", "after": "below"}.get(word, word)
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


def convert(findings: list, census: list[dict], reviewer: str) -> dict:
    """A 0.2.x report, already parsed, as a seeded-and-filled record file.

    !! A CAPTURED RUN STAYS A REGRESSION TEST INSTEAD OF BECOMING AN ARCHIVE.
    Replaying held stage-4 output is what made 0.2.1 and 0.2.2 cheap to
    validate -- five joins over one set of reports, about 1.6M tokens of review
    reused -- and that property dies the day the shape moves unless something
    carries the old reports across.

    ! It seeds first and FILLS, so every block still gets a slot and coverage
    stays structural. A block the old report never mentioned keeps its null
    verdict rather than vanishing.

    Args:
        findings: `verdicts.parse_report`'s output for one reviewer.
        census: the census that report was written against.
        reviewer: the editorial role's name.

    Returns:
        The report in the current shape.
    """
    report = seed(census, reviewer)
    by_block: dict[int, list] = {}
    for f in findings:
        by_block.setdefault(f.block, []).append(f)

    # !! EVERY CITED BLOCK GETS A SLOT, PROSE OR NOT. `seed` lays down the prose
    # blocks because those are the ones a reviewer is ACCOUNTABLE for -- but an
    # `add` cites an empty INTERVAL by design, since its finding is that a
    # constraint exists in code and NOWHERE in prose. Seeding alone therefore
    # cannot express the one verdict that needs an interval, and a conversion
    # that only filled seeded slots dropped both of them silently. Measured
    # 2026-08-17 on this repo's own smoke test: 228 findings became 226.
    seeded = {rec["block"] for rec in report["records"]}
    for index in sorted(set(by_block) - seeded):
        if 1 <= index <= len(census):
            report["records"].append(slot(index, census[index - 1]))
    report["records"].sort(key=lambda r: r["block"])

    filled = []
    for rec in report["records"]:
        found = by_block.get(rec["block"], [])
        if not found:
            filled.append(rec)
            continue
        # ! One record per FINDING, not per block. A block ruled on twice by one
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


def main() -> int:
    """Seed a reviewer's record file from the census."""
    # A Windows console is cp1252; one non-ASCII glyph in a report kills the run.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", action="store_true", help="write an empty record file")
    ap.add_argument("--check", metavar="PATH", help="check a filled record file")
    ap.add_argument(
        "--convert", metavar="PATH", help="a 0.2.x text report, as record JSON"
    )
    ap.add_argument("--census", required=True, help="census.py --json output")
    ap.add_argument("--reviewer", help="the editorial role's name (--seed only)")
    ap.add_argument("--out", help="the file to write (--seed only)")
    args = ap.parse_args()

    if not args.seed and not args.check and not args.convert:
        print("nothing to do: pass --seed, --check or --convert")
        return 2
    try:
        loaded = json.loads(Path(args.census).read_text(encoding="utf-8"))
    except READ_ERRORS as e:
        print(f"CANNOT READ {args.census} ({type(e).__name__})")
        return 2
    except json.JSONDecodeError as e:
        print(f"CANNOT PARSE {args.census} as JSON ({e})")
        return 2
    census = loaded["blocks"] if isinstance(loaded, dict) else loaded

    if args.check:
        try:
            report = json.loads(Path(args.check).read_text(encoding="utf-8"))
        except READ_ERRORS as e:
            print(f"CANNOT READ {args.check} ({type(e).__name__})")
            return 2
        except json.JSONDecodeError as e:
            # !! THE ONE FAILURE THIS FORMAT ADDS, and it names its own
            # position where a merged field never could.
            print(f"CANNOT PARSE {args.check} as JSON ({e})")
            return 2
        problems, unruled = check(report, census)
        # ! The version first, because every message below it assumes this
        # reader and that file agree about what a record is.
        stale = version_problem(report)
        if stale:
            print(f"  {stale}")
        for problem in problems:
            print(f"  {problem}")
        total = len(report.get("records") or [])
        print(f"\n{total - unruled} of {total} records ruled; {unruled} still empty.")
        # ! The VERSION counts as one. It is reported above and it is not in
        # `problems`, so a file whose only fault was a missing version printed
        # "0 problem(s)" and exited 1 -- a count contradicting the line above it
        # and the exit code below it.
        counted = len(problems) + bool(stale)
        if counted:
            print(f"{counted} problem(s). The shape is wrong, not the finding.")
            return 1
        # ! An unfilled report is INCOMPLETE, not malformed, and the two exit
        # differently: a reviewer part-way through is not in error.
        print("Every filled record is well formed." if total else "No records.")
        return 0

    if args.convert:
        if not args.reviewer or not args.out:
            print("--convert needs --reviewer and --out")
            return 2
        try:
            text = Path(args.convert).read_text(encoding="utf-8")
        except READ_ERRORS as e:
            print(f"CANNOT READ {args.convert} ({type(e).__name__})")
            return 2
        # ! The DEPRECATED parser, kept for exactly this. It is how a report
        # written before the shape moved stays a regression test.
        # !! IMPORTED HERE, not at module scope. The reader depends on this
        # module for the verdict table, so a top-level import would restore the
        # cycle this move removed -- and `--convert` is the only path that needs
        # it, so nothing else pays for the deprecated format.
        from verdicts import code_concerns, parse_report

        findings, malformed = parse_report(text, args.reviewer)
        report = convert(findings, census, args.reviewer)
        # ! CODE CONCERNS travel too. They carry no verdict and are gated by
        # nothing, which is exactly why a conversion drops them without any
        # count moving -- measured here, 14 lines that vanished while the
        # finding totals matched to the block.
        report["code_concerns"] = code_concerns(text)
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1), encoding="utf-8")
        ruled = sum(1 for r in report["records"] if r["verdict"] is not None)
        # ! The two counts are printed together so a LOSS is visible. A
        # conversion that quietly dropped findings read as a clean run.
        print(f"{args.reviewer}: {len(findings)} findings -> {ruled} filled records")
        print(f"  -> {out}")
        for line in malformed:
            print(f"  MALFORMED IN THE SOURCE: {line}")
        return 0

    if not args.reviewer or not args.out:
        print("--seed needs --reviewer and --out")
        return 2
    report = seed(census, args.reviewer)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")

    prose = len(report["records"])
    print(f"{args.reviewer}: {prose} records seeded from {len(census)} blocks -> {out}")
    print(f"  the reviewer fills {', '.join(ANSWERED)}")
    print(f"  {', '.join(SEEDED)} are already there")
    return 0


if __name__ == "__main__":
    sys.exit(main())
