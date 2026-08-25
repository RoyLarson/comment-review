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

import re
from collections import defaultdict

from comment_review.binder.record import Finding, _is, entry_for

# ! The shim its three sibling importers carry. Run as a program this file
# resolves without it -- Python puts the script's own directory on `sys.path`
# -- so the gap was invisible from the documented invocation and appeared only
# on IMPORT, where a test or another script reaches in. `census.py`,
# `referrers.py` and `prove_unchanged.py` all insert it; this was the one
# sibling importer that did not.
from comment_review.desk.desk import _words, removed_spans, ruled_text


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
    became a `Finding` -- `load_report` reports those as malformed instead.
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
        # ! `raw_text`, NOT `text` -- the same rename `desk.py` carries the
        # reason for. A working guard is swapped, never dropped, when the field
        # it reads is only renamed.
        prose = _words(held.get("raw_text") or "")
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
