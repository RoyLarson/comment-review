"""Stage 5's gate: join four reviewers' reports against the census.

    python verdicts.py --census census.json --repo D <report>...

Checks the task agent was asked to perform by hand, every one mechanical:

  COVERAGE      every prose ADDRESS accounted for, by every reviewer that ran
  SOURCES       every citation resolves, and its verbatim half is really there
  ADDRESS       PARAGRAPH's `path:start-end` and transcribed text match the census
  PARAGRAPH         the sentence a finding rules on is really in the paragraph it cites
  DESTINATION   a `move`'s `to:` names a place the census carries -- including
                an EMPTY one, since a paragraph may move where no prose sits yet
  EDIT          PARAGRAPH-against-CHANGE edits the sentence CLAIM names, and no
                other. ! ONE ROUND ONLY -- it says nothing about whether N
                rounds converge on correct prose
  PAYLOAD       the verdict carries what its row of the table requires
  CONTRADICTION `drop` against `correct`/`patch` ON THE SAME SENTENCE -- a
                re-review. `move` composes with both and is not flagged.
                Counted apart from the fatal checks, and named in the closing
                line so the summary says which paragraphs are still out
  STANDS        paragraphs every reviewer that ran returned clean on
  SCOPED OUT    paragraphs nobody found anything in and nobody certified
  WORK LIST     each paragraph needing a ruling, with the verdicts held on it
  CODE CONCERNS carried through, attributed, gated by nothing
  REVIEWER      every report is named for a PUBLISHED role, and (only with
                `--reviewers`) every expected reviewer actually reported

! Exits nonzero on a coverage gap or an unverifiable citation.

! It reports which findings are ADMISSIBLE. The ruling is stage 5's, in
SKILL.md's synthesis order.

! Every paragraph is accounted for by a RECORD, `clean` included. A `clean` record
carries a PARAGRAPH and a VERDICT and nothing else, so covering N paragraphs costs N
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
    _words,
    address_problem,
    block_problem,
    declares_scope,
    destination_problem,
    edit_problem,
    payload_problem,
    removed_spans,
    ruled_text,
    source_problem,
)
from held import address_of, load_report  # noqa: E402  -- path shim must run first
from page import (
    FRONT_MATTER,  # noqa: E402  -- path shim must run first
    HOLDS_NO_PROSE,  # noqa: E402  -- path shim must run first
)
from record import (  # noqa: E402  -- path shim must run first
    VERDICTS,
    Finding,
    _is,
    _n,
    _substantive,
    claim_text,
    entry_for,
)
from repo import READ_ERRORS  # noqa: E402  -- path shim must run first
from vocabulary import Reviewer  # noqa: E402  -- path shim must run first


def coverage_gaps(
    all_blocks: set[str], reported: set[str], found: list[Finding]
) -> dict[str, list[str]]:
    """Indices each reviewer left unaccounted for. A gap is a gap, not a pass.

    `reported` is who handed in a file, and the findings say who produced a
    record. A report that parsed to nothing is a reviewer that accounted for
    nothing, so taking the population from the findings alone would drop it.
    """
    by_reviewer: dict[str, set[str]] = defaultdict(set)
    for f in found:
        by_reviewer[f.reviewer].add(f.address)
    gaps: dict[str, list[str]] = {}
    for reviewer in reported | set(by_reviewer):
        missing = sorted(all_blocks - by_reviewer[reviewer])
        if missing:
            gaps[reviewer] = missing
    return gaps


def by_paragraph(found: list[Finding]) -> dict[str, list[Finding]]:
    """Every finding, grouped by the paragraph it rules on.

    This is what stage 5 works from: several roles rule on one paragraph and the
    task agent emits ONE replacement, so the grouping IS the work list. It was
    computed inside `contradictions`, used for one boolean and dropped, leaving
    the agent to rebuild it from the report files by hand.

    Every finding here names a paragraph, because a record that named none never
    became a `Finding` -- `parse_report` returns those separately.
    """
    out: dict[str, list[Finding]] = defaultdict(list)
    for f in found:
        out[f.address].append(f)
    return out


# A phrase a reviewer QUOTED inside prose. ! DOUBLE QUOTES ONLY, because in
# this system BACKTICKS MEAN CITATION -- the brief instructs a reviewer to
# cite by symbol or path in them, so a backticked token in `REASON` is a
# reference, not a quotation of the paragraph's words.
#
# !! Measured 2026-08-17 before the narrowing: over 903 real findings the
# check fired 46 times and most were symbol citations -- ``_walk``,
# ``BY_EXT``, ``raw_lines`` -- which is the noise level at which a report
# stops being read. Quoting is the signal: a `REASON` that MENTIONS a
# subject is discussing context, which it is entitled to do; one that
# QUOTES the paragraph's own words is describing a defect in them.
QUOTED = re.compile(r'"([^"\n]{4,})"')


def unrecorded_findings(
    grouped: dict[str, list[Finding]], paragraphs: list[dict]
) -> list[tuple[str, str, str]]:
    """Phrases a `REASON` quotes from its own paragraph that no `CLAIM` names.

    !! A FINDING CAN BE STATED IN `REASON` AND GO NOWHERE. `REASON` is
    deliberately unverified -- a derived count is not a line any file contains,
    which is why it is a separate field from `SOURCES` -- so nothing downstream
    reads it as a claim. A reviewer whose reasoning wanders one sentence over
    from what its `CLAIM` names has filed a second finding with no record.

    ! Measured 2026-08-17. `module-context` wrote in `REASON` on paragraph 1: *"the
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
    PARAGRAPH"*); nothing tells a reviewer to use it.

    Args:
        grouped: findings by census paragraph index.
        paragraphs: the census.

    Returns:
        `(paragraph, reviewer, phrase)` per phrase, in paragraph order.
    """
    # Every phrase any CLAIM in this run names, normalised once.
    # ! One call per finding. `ruled_text` already returns `_words(...)`, so
    # the walrus keeps the text rather than computing it twice to test it.
    claimed = {text for fs in grouped.values() for f in fs if (text := ruled_text(f))}
    out: list[tuple[str, str, str]] = []
    for paragraph, fs in sorted(grouped.items()):
        held = entry_for(paragraph, paragraphs)
        if held is None:
            continue
        prose = _words(held.get("text") or "")
        if not prose:
            continue
        for f in fs:
            for match in QUOTED.finditer(f.reason or ""):
                phrase = _words(match.group(1) or "")
                # ! It must be the PARAGRAPH'S OWN words. A phrase quoted from a
                # source file is evidence, not an unrecorded finding.
                if len(phrase) < 4 or phrase not in prose:
                    continue
                if any(phrase in c or c in phrase for c in claimed):
                    continue
                out.append((paragraph, f.reviewer, match.group(1)))
    return out


def contradictions(
    grouped: dict[str, list[Finding]], paragraphs: list[dict]
) -> list[str]:
    """Paragraphs where one role REMOVES the sentence another rules on.

    `drop` against `correct`/`patch` is one role saying the sentence should not
    exist and another saying it should exist and be fixed. Nothing composes
    those.

    !! Keyed on the TEXT, not the paragraph index. A paragraph of six sentences can
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
        # reports it, and this must not pass the paragraph for lack of an entry.
        entry = entry_for(f.address, paragraphs)
        if entry is None:
            return ""
        spans = removed_spans(f, entry)
        return " ".join(spans) if spans else ""

    out: list[str] = []
    for paragraph, fs in grouped.items():
        removals = [touched(f) for f in fs if _is(f, "removes")]
        rulings = [touched(f) for f in fs if _is(f, "rules_on_text")]
        if not removals or not rulings:
            continue
        if any(not a or not b or a in b or b in a for a in removals for b in rulings):
            out.append(paragraph)
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
        paragraphs = json.loads(census_text)
    except json.JSONDecodeError as e:
        print(
            f"CANNOT PARSE {args.census} as JSON ({e})"
            " -- is this census.py --json output?"
        )
        return 1
    # !! ADDRESSABLE is not ACCOUNTABLE. Every interval between two lines of
    # code is a paragraph, and so is every declaration, so an `add` -- a finding
    # about prose that is MISSING -- has a place to cite instead of borrowing a
    # neighbour's. Most of them hold
    # nothing, and a reviewer owes no record on an empty one: coverage is over
    # the paragraphs that HOLD PROSE. Re-measured 2026-08-19: `census.py` over
    # itself is 1,607 paragraphs, 118 of them prose. Owing a record on all 1,607
    # would make `CLEAN 1-N` -- the cheapest fabrication there is -- 92% true.
    # !! THE FIGURE HAS NOW ROTTED TWICE, IN BOTH PLACES THAT RECORD IT ROTS. It
    # was 546/48, then 642/76, and the comment saying "re-measure both or
    # neither" did not make anyone do so: the ratio moved from 8-in-9 to 92%
    # while both copies said 8-in-9. A number written in two files with nothing
    # comparing them is a number that will be wrong in both.
    # !! ADDRESSES, not indices. Coverage is over the paragraphs that HOLD PROSE --
    # an empty place is addressable and nobody owes it a record.
    # ! FRONT MATTER IS NOT COVERAGE. It is filtered out of what a reviewer
    # reads -- a licence header settles no claim about the code -- so counting
    # it here would report a gap on the one paragraph nobody was shown.
    all_blocks = {
        str(b.get("address", ""))
        for b in paragraphs
        if b.get("kind") not in HOLDS_NO_PROSE
        and b.get("address")
        and FRONT_MATTER not in (b.get("annotations") or ())
    }

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
            # !! THE DEPRECATED FORMAT'S INDEX IS TRANSLATED HERE. A 0.2.x report
            # keys by census POSITION, and a `clean` record in it writes that
            # index alone with no address at all -- so without this every old
            # report joins as "names no paragraph". Everything downstream is
            # address-keyed.
            #
            # ! `held.address_of` OWNS THE RULE. It was written out here and
            # NOT in `held.convert`, so a held report joined and did not
            # convert: `convert` grouped on `f.address`, every held finding
            # landed under "", and it returned a file of null verdicts and
            # exited 0. Measured 2026-08-19, 3 of 3 dropped on a six-line file.
            # One bridge across the format change, built twice and finished
            # once.
            f.address = address_of(f, paragraphs)
            held = entry_for(f.address, paragraphs) or {}
            # !! ANY EDIT PROPOSED ON FRONT MATTER BECOMES A `query`. Roy,
            # 2026-08-19: an agent looking to edit that area gets an automatic
            # query -- ask the human -- instead of any of the other verdicts.
            #
            # ! Because the cost is asymmetric and sits OUTSIDE this system. A
            # licence header is a legal instrument and a shebang is how the file
            # runs; a wrong edit to either is not an editorial mistake, and no
            # role here can settle whether it is right -- see
            # `census.mark_front_matter`. The reviewer was not shown the paragraph,
            # `--filtered` drops it, so a verdict here came from reading the
            # file directly: a reasonable thing to have done, and still not this
            # system's call.
            #
            # ! CONVERTED, not refused. The reviewer saw something; dropping it
            # silently would lose it. The human is asked instead.
            #
            # ! The trigger is `owes_change` -- the table's own word for "this
            # verdict proposes an EDIT" -- not a verdict NAME. `clean` and
            # `query` propose none and are left exactly as they were.
            proposes = VERDICTS.get(f.verdict)
            if FRONT_MATTER in (held.get("annotations") or ()) and (
                proposes is not None and proposes.owes_change
            ):
                print(
                    f"  {f.address} {f.reviewer}: {f.verdict!r} on FRONT MATTER"
                    " (a licence header, shebang or coding line) -- turned into"
                    " a `query`. That is the human's to rule on, not a role's."
                )
                # ! A COMPLETE query, not just the word. `query` owes a shape,
                # what was attempted and what would settle it -- so converting
                # the verdict alone leaves a record its own gate refuses. The
                # shape is `outside the code`: settling a licence needs someone
                # who knows how the project is owned and operated, which is
                # exactly what that shape is for. What the reviewer proposed is
                # kept as `attempted`, so nothing it saw is lost.
                f.claim_fields = {
                    "shape": "outside the code",
                    "attempted": (f.claim or "").strip()
                    or f"a {f.verdict} on this paragraph",
                    "settles": "the human -- front matter is theirs to rule on",
                }
                f.claim = claim_text("query", f.claim_fields)
                f.change = ""
                f.verdict = "query"
            if not f.original:
                f.original = "\n".join(held.get("raw_lines") or [])
        found.extend(records)
        malformed.extend((reviewer, why) for why in unattributable)
        for line in code_lines_flagged:
            concerns.append((reviewer, line))
        reported.add(reviewer)

    print(
        f"{_n(len(found), 'finding')} from {_n(len(args.reports), 'reviewer')}"
        f" over {_n(len(all_blocks), 'prose paragraph')}"
        f" ({_n(len(paragraphs), 'paragraph')} in the census, the rest empty intervals"
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
            count = _n(len(missing), "paragraph")
            print(f"  {reviewer}: {count} unaccounted -- {shown}{more}")
            fatal += 1
        print()

    for reviewer, why in malformed:
        print(f"  MALFORMED {reviewer}: {why}")
        fatal += 1

    for f in found:
        if entry_for(f.address, paragraphs) is None:
            print(
                f"  {f.address} {f.reviewer}: names no paragraph in a"
                f" {_n(len(paragraphs), 'paragraph')} census"
            )
            fatal += 1
            continue
        if f.verdict not in VERDICTS:
            print(
                f"  {f.address} {f.reviewer}: {f.verdict!r} is not a verdict"
                f" ({', '.join(VERDICTS)})"
            )
            fatal += 1
        problem = source_problem(f, repo)
        if problem:
            print(f"  {f.address} {f.reviewer}: {problem}")
            fatal += 1
        misaddressed = address_problem(f, paragraphs)
        if misaddressed:
            print(f"  {f.address} {f.reviewer}: {misaddressed}")
            fatal += 1
        # !! A `move` IS ONLY AS GOOD AS ITS DESTINATION, and that half was
        # checked for presence and never resolved.
        nowhere = destination_problem(f, paragraphs)
        if nowhere:
            print(f"  {f.address} {f.reviewer}: {nowhere}")
            fatal += 1
        wrong_block = block_problem(f, paragraphs)
        if wrong_block:
            print(f"  {f.address} {f.reviewer}: {wrong_block}")
            fatal += 1
        held = entry_for(f.address, paragraphs)
        if held is not None:
            disagrees = edit_problem(f, held)
            if disagrees:
                print(f"  {f.address} {f.reviewer}: {disagrees}")
                fatal += 1
        payload = payload_problem(f)
        if payload:
            print(f"  {f.address} {f.reviewer}: {payload}")
            fatal += 1

    grouped = by_paragraph(found)
    # !! REPORTED, NOT GATED, and printed BEFORE the counts so it is not read as
    # a summary line. A finding stated in `REASON` that no `CLAIM` names is a
    # second finding with no record -- the gate checked the claim it was given
    # and passed, and the defect reached no work list. It is not fatal because
    # `REASON` is entitled to discuss context.
    unrecorded = unrecorded_findings(grouped, paragraphs)
    if unrecorded:
        print(
            f"\nA FINDING WITH NO RECORD -- {_n(len(unrecorded), 'phrase')} quoted in"
            " REASON that no CLAIM names:"
        )
        for at, reviewer, phrase in unrecorded[:20]:
            print(f"  {at} {reviewer}: {phrase!r}")
        if len(unrecorded) > 20:
            print(f"  ... and {len(unrecorded) - 20} more")
        print(
            "  Each is the paragraph's OWN words. File a second record on it"
            " rather than leaving the finding in prose nothing reads."
        )

    clash = contradictions(grouped, paragraphs)
    if clash:
        # ! Names what the check DOES. It read "drop/move" after `move` left the
        # set by ruling, so the one line a user reads named a pairing the join
        # had stopped making.
        print(f"\nRE-REVIEW -- drop against correct/patch on: {clash}")
        print(
            "  Not a tie-break. Send the paragraph back; the synthesis order"
            " must not decide it."
        )

    # !! THREE STATES, NOT TWO. A paragraph covered only by `clean` and out-of-role
    # queries is neither: no role certified it -- module-context returns `query`
    # rather than `clean` so it does not certify what it never read -- and
    # nothing is asked of stage 5 either. Counting those as work buried 76 real
    # verdicts inside 1159 on a measured run.
    ran = sorted(reported | {f.reviewer for f in found})
    in_range = [f for f in found if entry_for(f.address, paragraphs) is not None]
    ruled = {f.address for f in in_range if _substantive(f) and not declares_scope(f)}
    scoped_out = {f.address for f in in_range if declares_scope(f)} - ruled
    # !! A PARAGRAPH NOBODY ACCOUNTED FOR IS NOT A PARAGRAPH EVERY ROLE PASSED. It fell
    # into `stands` and was printed as "clean from all N reviewers", which is a
    # claim no reviewer made -- on a report where every slot was still empty,
    # every prose paragraph in the file was summarised that way, one line under the
    # COVERAGE GAPS list naming the same paragraphs. Measured 2026-08-18.
    #
    # ! It is the same shape `_substantive` already guards at the other end: an
    # unknown verdict answered False to everything, dropped out of the work
    # list, and was reported as clean on a paragraph a role HAD ruled on. Both
    # directions end in the summary asserting a pass nobody gave.
    unaccounted = {index for missing in gaps.values() for index in missing}
    stands = sorted(all_blocks - ruled - scoped_out - unaccounted)
    print(
        f"\nSTANDS UNCHANGED: {_n(len(stands), 'paragraph')} -- clean from all"
        f" {_n(len(ran), 'reviewer')} that ran"
    )
    print(f"NEEDS A RULING:   {_n(len(ruled), 'paragraph')}")
    if unaccounted:
        # ! Counted here as well as listed above, because the three lines
        # around it are counts and a reader compares them.
        print(
            f"NOT ACCOUNTED FOR: {_n(len(unaccounted), 'paragraph')} -- at least one"
            " reviewer left them out. Neither ruled on nor certified."
        )
    if scoped_out:
        print(
            f"NO FINDING, NOT CERTIFIED: {_n(len(scoped_out), 'paragraph')} -- every"
            " role that read it was `clean`, and at least one said it was outside"
            " its role. Nothing to rule; nothing certified either."
        )
    if gaps:
        print("  ! counts above are provisional: coverage is incomplete.")

    # ! The WORK LIST. Stage 5 holds several rulings per paragraph and must emit ONE
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
                "\nPER PARAGRAPH -- PROVISIONAL, the gate refused this report."
                "\n  Read it to see what the roles found; do not rule from it"
                " until the problems above are resolved."
            )
        else:
            print("\nPER PARAGRAPH -- what you hold, in census order:")
        for b in sorted(ruled):
            marks = "  ".join(
                f"{f.verdict}({f.reviewer})"
                for f in sorted(grouped[b], key=lambda f: (f.verdict, f.reviewer))
                if _substantive(f) and not declares_scope(f)
            )
            flag = "   ! RE-REVIEW" if b in out_for_rereview else ""
            print(f"  {b}  {marks}{flag}")

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
        # The closing line still has to say so -- printing "send the paragraph back"
        # and then "Stage 5 may rule" four lines later made the summary
        # contradict its own body at exit 0.
        print(
            f"\nEvery finding is admissible. {_n(len(clash), 'paragraph')} still OUT"
            " for re-review -- stage 5 may rule on the rest."
        )
        return 0
    print("\nEvery finding is admissible. Stage 5 may rule.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
