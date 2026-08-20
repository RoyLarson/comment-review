"""The copy desk: can this mark be acted on, before anyone acts on it.

Imported by `verdicts.py`; it has no command line of its own.

A reviewer hands in a finding. Before the join can weigh it against the other
reviewers' findings, five questions have to be answered about that ONE finding,
and each is mechanical:

  PAYLOAD   does the verdict carry what its row of the table requires
  SOURCE    does every citation resolve, and is its verbatim half really there
  ADDRESS   does `path:start-end` and the transcribed text match the census
  PARAGRAPH     is the sentence the finding rules on really in the paragraph it cites
  EDIT      does PARAGRAPH-against-CHANGE edit the sentence CLAIM names, and no
            other. ! ONE ROUND ONLY -- it says nothing about whether N rounds
            converge on correct prose

!! NONE OF THESE COMPARES ONE REVIEWER AGAINST ANOTHER. A question that needs
two findings -- who contradicts whom, which paragraphs nobody accounted for -- is
the join's, and lives in `verdicts.py`. The split is that line: one finding, or
several.

! A desk check REPORTS what is wrong and never repairs it. Returning `None`
means it found nothing to say, which is not a claim the finding is correct.
"""

import difflib
import re
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lexer import block_text, language_for  # noqa: E402  -- path shim must run first
from record import (  # noqa: E402  -- path shim must run first
    ANCHOR_NAME,
    CITE,
    OUT_OF_ROLE,
    VERDICTS,
    Finding,
    _answered,
    _claim_values,
    _is,
    _n,
    _said,
    claim_keys,
    entry_for,
    filled,
)
from repo import READ_ERRORS  # noqa: E402  -- path shim must run first

# !! WHAT COMES OFF A WORD'S EDGES: ALL PUNCTUATION, not a list of it. `_words`
# strips it from a quoted CLAIM and `removed_spans` from the tokens it diffs,
# and **the two must agree or a correct record is refused**.
#
# ! An ENUMERATED list was the defect, three times in one day. Each fix added
# the characters that had just been measured and left the next set out:
#
#   * brackets absent -- a `CLAIM` naming `the CLI` could not cover a `CHANGE`
#     editing `the CLI)`
#   * the diff kept punctuation the claim had lost, so `policy` and `policy.`
#     would not align and a dropped trailing parenthetical was reported as
#     starting at `policy`, a word no `CLAIM` names
#   * markdown emphasis absent -- a span reading `*"a wrap ... defect"*` could
#     be matched by NO wording of the claim, cleanly quoted or not, because the
#     span comes from the FILE and carries the file's markup
#
# !! The third had no legal expression at all, and the reviewer reshaped a
# sound finding twice to route around it. **A reviewer contorting its judgement
# to satisfy a mechanical defect is CONSERVATIVE ON MEANING, FREE ON FORM
# failing from the tooling side** -- the gate was deciding what could be found,
# not whether it was true.
#
# ! The cost is PRECISION, and it is the cheap direction. `-3` reduces to `3`
# and `_private` to `private`, so two texts that differ only in edge
# punctuation now compare EQUAL and a gate that should refuse might pass. A
# false pass costs a finding the next round catches; a false refusal costs a
# session, and has three times.
EDGE = string.punctuation

# How far from the cited line the quoted text may sit. Prose wraps and code
# moves; a hard equality would reject honest citations, and a wide window would
# accept a fabricated one.
SOURCE_WINDOW = 3

# The floor on a SOURCES entry's verbatim half, and it is ONE: zero length is not text.
# It was 12, which refused `x = 1`, `pass` and `return` -- real short lines whose
# only route through was to quote MORE than was read.
MIN_NEEDLE = 1


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
    # ! Against the claim's VALUES, not its rendered form -- the markers
    # `claim_text` prepends are not the reviewer's words, and comparing prose
    # against them made this unable to fire on any JSON record.
    echoed = _claim_values(f)
    if echoed.strip() and _words(f.reason) == _words(echoed):
        return "REASON restates CLAIM -- say what you derived, not what it says"

    claim = f.claim.lower()
    # !! PRESENT AND EMPTY IS MISSING, and only the FIELD can tell. `claim_text`
    # renders an empty value as `false: ""`, so the marker IS in the rendered
    # string and the search below admits it -- and `ruled_text` then reads ""
    # and returns "", which its own contract calls "cannot compare", so
    # `block_problem`, `edit_problem` and `contradictions` all skip in silence.
    # The finding is admitted AND unchecked. Measured 2026-08-18: the join
    # returned None where `record.claim_problems` reported the empty key.
    markers, _extras = claim_keys(spec)
    if f.claim_fields and markers:
        empty = [k for k in markers if not filled(f.claim_fields.get(k))]
        if empty:
            return spec.claim_help
    if any(marker not in claim for marker in spec.claim_all):
        return spec.claim_help
    # ! The SHAPE comes from its own key where there is one. Searching the
    # whole rendered claim for it lets a reviewer's `attempted` prose name a
    # shape the record never declared.
    shape = _said(f, "shape")
    named = (
        [shape]
        if shape in spec.claim_any
        else [s for s in spec.claim_any if s in claim]
    )
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
        if spec.needs_attempted and not _answered(
            f, "attempted", QUERY_ATTEMPTED, probe
        ):
            return (
                "query needs the check you ATTEMPTED -- a query naming none"
                " hands the judgement back"
            )
        if spec.needs_settles and not _answered(f, "settles", QUERY_SETTLES, probe):
            return "query needs what WOULD settle the claim"
    if spec.needs_anchor:
        # ! The brief asks for "the text AND its anchor -- which code, above or
        # below": a NAMED site and a side. This used to accept the bare word
        # "anchor", so `add an anchor comment` passed while
        # `above `retry_budget`` failed for not saying "anchor".
        # ! Each half from its own key where the record has one. Read off the
        # rendered string instead, a backtick anywhere in `missing` satisfied
        # the anchor test -- so an `add` with an EMPTY anchor passed the join
        # while `record.py --check` refused it. Two tools, one record,
        # different answers.
        # !! `or` will not do: an EMPTY field would fall back to the rendered
        # string, which is exactly the case being fixed. A record that carries
        # fields is answered from them, filled or not.
        anchor = _said(f, "anchor") if f.claim_fields else f.claim
        # !! NO SIDE IS ASKED FOR. The ADDRESS says which side -- `@bN` above
        # code line N, `@cN` beside it, `@aN` a declaration's documentation --
        # so a payload stating it again could disagree, and did: measured
        # 2026-08-19, an `add` on a `c` address passed carrying `side: above`.
        if not ANCHOR_NAME.search(anchor):
            return (
                "add needs the anchor NAMED in backticks -- which declaration,"
                " not the word 'anchor'"
            )
    # ! A verdict that MAY EMPTY its paragraph is exempt here and checked in
    # `edit_problem` instead, which holds the census entry an empty `CHANGE`
    # has to be measured against. Refusing here made a whole-paragraph `drop`
    # inexpressible: there is no text to show, and the record was rejected for
    # not showing it.
    if spec.owes_change and not f.change.strip() and not spec.may_empty:
        return (
            f"{f.verdict} carries no CHANGE -- the edit already made, written out"
            " with its surrounding paragraph, which is what stage 5 applies"
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

    !! This calls `lexer.block_text`, and that is the whole point. A second
    implementation of lines-to-paragraph is a second DEFINITION of what a paragraph's
    text is, and the two drift. Measured 2026-08-17: this file grew its own and
    disagreed with the census three ways at once -- a blank line, a raw-string
    prefix, and a closing delimiter -- refusing 83 of 171 paragraphs in one run and
    roughly 450 in another. Every one of those transcriptions was correct.

    ! The KIND selects the reading and the PATH selects the comment markers,
    both taken from the census entry rather than guessed: a docstring is read
    past its delimiters, a comment run past its openers, and `///` must come
    off before `//` leaves a stray slash in the prose.

    Args:
        text: the reviewer's `original`, as lines from the file.
        entry: that paragraph's census record.
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

    ! This is NOT the paragraph normaliser -- `as_block` is, and it defers to the
    census. This one takes prose that never came from a file: a `CLAIM`'s
    quoted half, and the spans a word-diff reports. Neither has comment markers
    to strip, so all it owes is whitespace, case, and the punctuation a quoted
    sentence picks up.

    ! Trailing sentence punctuation comes off each word. A paragraph reads `the
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
    # !! ONE strip over BOTH classes, and a token that strips to NOTHING is
    # dropped. Both are needed for the idempotence callers rely on, and each
    # was a separate refusal of a correct finding:
    #
    #   - stripping quotes and THEN punctuation is not idempotent -- `` `cap`, ``
    #     loses its backtick only on a second pass;
    #   - a token that is punctuation ALONE -- `...`, `--`, `*` -- reduces to
    #     the empty string, and joining on it leaves a double space that only a
    #     second pass collapses. Measured 2026-08-17: a whole-paragraph `drop` of
    #     any paragraph containing such a token was refused, telling the reviewer to
    #     write a remainder that was already there.
    #
    # ! The property is what lets `ruled_text` return `_words(...)` and a caller
    # normalise the other side once. Without it the two sides are reduced a
    # different number of times and cannot agree.
    return " ".join(s for w in text.split() if (s := w.strip(EDGE))).lower()


# An ADDRESS as it appears inside prose: a dotted path, `@`, a series letter and
# an ordinal. ! MATCHED, not split: a `move`'s `to:` is a sentence a reviewer
# wrote and the address sits somewhere inside it.
ADDRESS_IN = re.compile(r"[\w.:/\\-]+@[abc]\d+")
# The RETIRED line form, as it appears inside prose. ! A destination naming one
# is refused rather than taken for an out-of-code place: it is inside the code,
# and this tool moves the line it names.
LINE_FORM = re.compile(r"[\w./\-]+\.\w+:\d+(?:-\d+)?")


def destination_problem(f: Finding, paragraphs: list[dict]) -> str | None:
    """Does a `move`'s destination name a place that exists?

    !! A DESTINATION WAS CHECKED FOR PRESENCE AND NEVER RESOLVED, so a `move`
    could send a paragraph anywhere -- a line number, a prose description, a
    declaration that is not in this run -- and the gate passed it. `to:` is the
    one half stage 5 has to act on.

    !! AND THE PLACE IT NAMES MAY HOLD NO PROSE. Roy, 2026-08-19: something
    could move a line to a new place that does not have a comment. Every such
    place now has an address -- an empty `interval`, a bare `margin`, an
    `undocumented` declaration -- so the destination is nameable where before
    there was no paragraph to point at.

    ! A destination OUTSIDE the code carries no address and is left alone: the
    tree that receives it is not in the census, and whether it exists at all is
    stage 1's ruling, recorded in the run context. An address is recognised by
    its `@`; anything else is taken as outside and passes here.
    """
    spec = VERDICTS.get(f.verdict)
    if spec is None or not spec.owes_destination:
        return None
    where = (_said(f, "to") if f.claim_fields else f.claim).strip()
    if not where:
        return None  # ! Absence is the PAYLOAD check's to report, and it does.
    # !! A LINE IS HOW YOU ASK; AN ADDRESS IS HOW YOU ANSWER. The retired form
    # is refused by name rather than passed as an out-of-code destination --
    # `m.py:3` is inside the code, and it is stale the moment this run edits
    # anything above it.
    stale = LINE_FORM.search(where)
    if stale:
        return (
            f"move's destination names a LINE, {stale.group(0)!r} -- that form was"
            " retired: ask `foliator.py --anchor LINE --series a|b|c` for the"
            " address"
        )
    if "@" not in where:
        return None
    named = ADDRESS_IN.search(where)
    if named is None:
        return f"move's destination {where!r} is not an address"
    if entry_for(named.group(0), paragraphs) is None:
        return f"move's destination {named.group(0)} is not a place in the census"
    return None


def address_problem(f: Finding, paragraphs: list[dict]) -> str | None:
    """Does the record's address name the paragraph the census has at that index?

    !! THE RECORD CARRIES THE ADDRESS AND NOT THE TEXT. Ruled 2026-08-17, after
    a first ruling the same day that it should carry both. Handed the prose, a
    reviewer can produce a complete admissible ruling without opening the file,
    and no check can tell that from real work; reading the WRONG lines is
    caught, because the sentence the claim quotes will not be in the paragraph. The
    caller fills `original` from the census before this runs, so what is
    compared here is unchanged and where it comes from is not.

    !! This is NOT `LOCATION` coming back. Roy, 2026-08-17: *"Location was
    dropped because it was ambiguous ... It could also have meant where this
    should go in the case of move or add. Or on a granular level which sentence
    are we talking about specifically."* One `file:start-end` field carried FOUR
    possible subjects, and each has its own home now:

    | LOCATION could have meant     | where it lives now                     |
    | ----------------------------- | -------------------------------------- |
    | where the prose SITS          | `paragraph` and `address`                  |
    | where the reviewer LOOKED     | `sources`                              |
    | where the prose SHOULD GO     | `claim`'s `to`, or an `add`'s anchor   |
    | WHICH SENTENCE, exactly       | the census text against `change`       |

    !! The last one is DERIVED, not declared, and that is why it is reliable.
    Roy, 2026-08-17: *"which sentence exactly is determined by the difference
    between PARAGRAPH and CHANGE, since CHANGE is the whole paragraph with the
    substitution."* Both hold the WHOLE paragraph, before and after, so what differs
    between them is the sentence and nothing else has to say so.

    ! Each is checked against a DIFFERENT thing -- `BLOCK` against the census,
    `SOURCES` against the files, the sentence against the paragraph's text. That is
    the gain: a field with four possible subjects can only be checked for
    RESOLVABILITY, because nothing says which subject to check it against.

    ! The ADDRESS is checked and the TEXT is not, because only one of them is
    a reviewer's answer. An address nobody verifies costs a line and settles
    nothing; a text nobody wrote, compared against another copy the same tool
    made, only reports that the tool disagrees with itself.

    ! `clean` is exempt, and stays exempt for a different reason than it had. It
    was exempt because a role returns `clean` on most of the census -- 1159
    paragraphs on one measured run -- and transcribing each would have made the bulk
    of every report text nobody reads. Nothing is transcribed now; a `clean`
    record's address is the tool's own, so there is nothing a reviewer could
    have got wrong.

    Args:
        f: the finding.
        paragraphs: the census, as `census.py --json` emits it.

    Returns:
        One sentence naming what disagrees, or None. Out-of-range indices are
        left to the range check, which reports them better.
    """
    spec = VERDICTS.get(f.verdict)
    if spec is None or not spec.owes_address:
        return None
    entry = entry_for(f.address, paragraphs)
    if entry is None:
        return f"ADDRESS {f.address!r} is not in the census"
    # !! ONE FORM NOW. The line range this compared was deprecated 2026-08-18 --
    # it is true of one file state, and this tool edits prose. The stable
    # address has no short form, so the one-line tolerance that cost 268
    # refusals in a single run has nothing left to forgive.
    want = str(entry.get("address", ""))
    ok = {want}
    got = f.address.replace("\\", "/").strip()
    if not got:
        return f"a record carries no ADDRESS -- write `{want}`"
    if got not in ok:
        return f"address is {got!r}, the census says {want!r}"
    # !! THE TEXT IS NO LONGER COMPARED, and it must not be. `original` is
    # filled from the census's `raw_lines` by `_report`, and `text` is the
    # census's own normalised copy of the same paragraph -- so the comparison put
    # two TOOL-SUPPLIED strings against each other and refused the finding when
    # they disagreed, with a message that accused nobody.
    #
    # !! They do disagree. `raw_lines` is the file's literal slice and `text` is
    # the AST value for a Python docstring, so any escape sequence renders in
    # one and not the other. Measured 2026-08-18 over this repo: 3 of 663 prose
    # paragraphs -- a `\r\n` in a source string, a `\\s+`, a unicode escape. Every
    # finding on those paragraphs was fatally refused, and no reviewer could have
    # fixed it.
    #
    # ! What the check was FOR is gone with the transcription it guarded. The
    # ADDRESS is still compared above, and `block_problem` still measures the
    # claim's sentence against the census text -- which is the check that
    # catches a reviewer reading the wrong lines.
    return None


def block_problem(f: Finding, paragraphs: list[dict]) -> str | None:
    """Is the sentence this finding rules on actually IN the paragraph it cites?

    !! This is what `LOCATION` could never do -- it was AMBIGUOUS, and the four
    subjects it could have named are set out in `address_problem`. A field whose
    subject is unknown can only be checked for RESOLVABILITY, never against the
    thing it describes. The census carries each paragraph's joined text and the gate
    already loads it, so this costs nothing and catches a finding attached to
    the wrong paragraph.

    !! Keyed on the ORIGINAL SENTENCE, which `CLAIM` carries in its `drop:`,
    `false:` or `from:` half -- never on `CHANGE`, which is the finished paragraph
    and holds the REPLACEMENT. Matching the replacement against the original
    paragraph would refuse every correct finding and pass the ones that changed
    nothing. `ruled_text` reads it, the same text the contradiction check keys
    on.

    ! Exempt: `clean` rules on nothing, `add` is about prose that is MISSING,
    `query` proposes no edit, and a `move`'s from/to are PLACES rather than
    text. All four -- and any malformed spec -- reach here as `ruled_text` "".

    Args:
        f: the finding.
        paragraphs: the census, as `census.py --json` emits it.

    Returns:
        The problem, or None. ! An out-of-range paragraph returns None: `main()`
        reports it already, and saying so twice reads as two defects.
    """
    # ! No verdict list here. `ruled_text` returns "" for every verdict whose
    # row quotes no original -- `clean`, `add`, `query`, `move` -- and for a
    # malformed spec, and the next line already treats "" as nothing to check.
    # A second list would be a second place to update.
    if entry_for(f.address, paragraphs) is None:
        return None
    needle = ruled_text(f)
    if not needle:
        return None
    # !! THE SAME NORMALISER as the needle. `ruled_text` returns `_words(...)`,
    # which drops per-token quotes and trailing punctuation; a haystack that
    # was only whitespace-collapsed still holds them, so any comma, colon or
    # backtick inside a quoted sentence refused a correct finding.
    entry = entry_for(f.address, paragraphs) or {}
    haystack = _words(str(entry.get("text", "")))
    # ! Same rule as SOURCES: compare all of it, truncate only the message. A
    # fabricated tail here made `edit_problem` MORE permissive, because it
    # widened the string every removed span is checked against.
    if needle not in haystack:
        return f"the sentence ruled on is not in {f.address}: {needle[:40]!r}"
    return None


def declares_scope(f: Finding) -> bool:
    """A `query` saying the paragraph is not this role's to read.

    Not a ruling: nothing is asked of the task agent, and the role is reporting
    the boundary it was told to report. Every other `query` IS work -- it names a
    claim nobody could settle, and the brief sends it to the author.
    """
    if not _is(f, "can_declare_scope"):
        return False
    # !! FROM THE SHAPE KEY, which `record.value_problems` has already checked
    # against a closed set. The rendered claim also carries the reviewer's
    # `attempted` and `settles` prose, and a query whose prose merely MENTIONED
    # the phrase was reclassified as a boundary report -- real work, silently
    # moved out of the work list.
    shape = _said(f, "shape")
    if shape:
        return shape == OUT_OF_ROLE
    return OUT_OF_ROLE in f.claim.lower()


def ruled_text(f: Finding) -> str:
    """The verbatim sentence this finding rules on, normalised for comparison.

    A verdict rules on a SENTENCE and the census numbers PARAGRAPHS, so two findings
    on one paragraph need not share a subject.

    !! Read out of CLAIM, the surgical spec. CHANGE is the whole resulting
    paragraph, so the original cannot be recovered from it -- the `drop:`,
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
    # !! THE FIELD FIRST, and the scan below is now the FALLBACK. A JSON record
    # carries the keys already and `parse_report` types a 0.2.x claim at load,
    # so a record reaches here typed unless its claim did not parse at all.
    #
    # !! It is also the only way a value CONTAINING another key's marker
    # survives. `false: "the cap is 5 / true: not really" / true: "..."` is one
    # `false` value with `/ true:` inside it; the scan stops at the FIRST
    # `quotes_until` and truncates it, where the field is exact.
    said = _said(f, spec.quotes_original.rstrip(":"))
    if said:
        return _words(said)
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
    # leave a needle that matches nothing in a paragraph plainly containing it.
    return _words(text)


def removed_spans(f: Finding, entry: dict) -> list[str] | None:
    """What this finding's edit takes OUT of the paragraph, span by span.

    !! DERIVED, never declared. `BLOCK`'s original and `CHANGE` both hold the
    WHOLE paragraph -- before and after -- so what differs between them IS the
    prose the finding acts on. Roy, 2026-08-17: *"which sentence exactly is
    determined by the difference between PARAGRAPH and CHANGE, since CHANGE is the
    whole paragraph with the substitution."*

    ! This is the reliable answer where `CLAIM` is the reviewer's own account of
    it. They should agree; `edit_problem` is where they are made to.

    !! Both halves are read through `as_block`, the CENSUS's normaliser, not
    through `_words`. They are file text: a comment run carries its openers and
    a docstring its delimiters, and a diff over raw tokens reports the marker as
    a removed word. Measured 2026-08-17: a `drop` that removed one sentence
    reported the span `# callers round separately`, which no `CLAIM` names.

    ! Returns None where no diff is meaningful: `clean` and `query` propose no
    text, `add` has no original, a `move`'s `CHANGE` is two paragraphs rather than
    one, and a record missing either half cannot be diffed at all. A caller must
    treat None as "cannot compare", never as "nothing removed".

    Args:
        f: the finding.
        entry: its census record, which selects how the paragraph is read.
    """
    spec = VERDICTS.get(f.verdict)
    if spec is None or not spec.diffable:
        return None
    # !! AN EMPTY `CHANGE` IS A DIFF, not a missing half, when the verdict may
    # empty its paragraph. A `drop` whose `CLAIM` names the paragraph's only sentence
    # leaves nothing behind, so the whole paragraph IS the removed span -- and
    # returning None there made the one unambiguous removal in the system read
    # as "cannot compare". Every other verdict still owes text.
    if not f.change.strip() and not spec.may_empty:
        return None
    # !! STRIPPED WITH `EDGE`, the same characters `_words` takes off a `CLAIM`.
    # A token still carrying its punctuation cannot align with the same word
    # without it, so `policy` and `policy.` were different tokens and the
    # matcher reported a dropped trailing parenthetical as beginning at
    # `policy` -- a word no `CLAIM` names, refusing a correct record. Measured
    # 2026-08-17. ! The spans this returns are punctuation-free for the same
    # reason, which costs nothing: every caller reads them through `_words`.
    before = [
        w
        for w in (t.strip(EDGE) for t in as_block(f.original, entry).lower().split())
        if w
    ]
    after = [
        w
        for w in (t.strip(EDGE) for t in as_block(f.change, entry).lower().split())
        if w
    ]
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
    the paragraph; `payload_problem` confirms `CHANGE` exists. Neither notices a
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
    trust the agents to synthesize a full paragraph and that could mean inserting
    and deleting multiple sentences with multiple rounds of review."* A
    synthesised paragraph composes several findings, so no single `CLAIM` names
    everything it changes and this test would refuse exactly that work.
    `verdicts.py` reads REVIEWER reports, where one verdict rules on one
    sentence, and that is the only place the test is sound.

    ! It follows that each finding's `CHANGE` carries ONLY THAT FINDING'S EDIT.
    Two findings on one paragraph each show the paragraph with their own change and no
    other -- composing them is stage 5's job. A reviewer that folds both edits
    into both records trips this check, correctly: the record would be claiming
    one edit and showing two.

    !! IT CHECKS ONE ROUND, and a green gate is not a correct paragraph. Roy,
    2026-08-17: *"This catches the 'first' round of edit reviews it will not
    catch the next N rounds required to make it correct."* Every round is
    measured against the text that round started from, and nothing here measures
    whether the rounds CONVERGE. Do not read this passing as the prose being
    right -- it says each reviewer edited the sentence it said it was editing.

    !! THIS GATE ASSUMES ROUND ONE, and a round-2 record does not fit it.
    Roy, 2026-08-17: a re-review sends *"the joined resolved paragraph back to the
    reviewers that had comments ... each can say yes my edits made it and are
    correct and the other edits do not negate that or cause mine to be wrong."*
    So round 2's subject is stage 5's SYNTHESIS -- text that is on no disk and
    in no census -- while `address_problem` compares `original` against the
    census and this function compares one claim against one edit. Neither holds.

    ! Do not paper over it by exempting round 2: that would leave the
    synthesised paragraph, the only text the author ever approves, as the one thing
    nothing checks. `TODO/re-review-is-ordered-everywhere-and-defined-
    nowhere.md` owns the shape.
    """
    spans = removed_spans(f, entry)
    if spans is None:
        return None
    # !! AN EMPTY `CHANGE` IS CHECKED, NOT TRUSTED. A `drop` whose `CLAIM` names
    # the paragraph's only sentence empties it, and there is no text to show; the
    # record was refused for not showing it, so a whole-paragraph drop could not be
    # expressed at all. The reviewer wrote the blank deliberately and said so in
    # `REASON`, which nothing downstream reads -- so this reads the two things
    # that ARE checkable instead. Measured 2026-08-17.
    #
    # ! It admits the blank only where CLAIM accounts for the WHOLE paragraph. A
    # blank `CHANGE` on a partial drop is still refused, which is what stops
    # this becoming a way to skip writing one.
    if not f.change.strip():
        # ! No empty-original branch here. It was reachable while a REVIEWER
        # wrote `original`; the tool fills it from the census now, and a paragraph
        # with nothing to fill it from returns from `removed_spans` above
        # before this runs. A message for a refusal the tool cannot issue reads
        # like a rule.
        whole = _words(as_block(f.original, entry))
        if ruled_text(f) != whole:
            return (
                f"{f.verdict}: CHANGE is empty, which says the paragraph empties --"
                " but CLAIM names only part of it. Write the remainder."
            )
        return None
    if as_block(f.original, entry).lower() == as_block(f.change, entry).lower():
        return (
            f"{f.verdict}: CHANGE is the paragraph UNCHANGED -- the verdict proposes"
            " an edit and the text does not make one"
        )
    # ! `CLAIM` is not file text -- it is a sentence the reviewer quoted -- so
    # it goes through `_words` while the spans go through `as_block`. The two
    # meet here, which is why both end lowercased and punctuation-stripped.
    named = ruled_text(f)
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
