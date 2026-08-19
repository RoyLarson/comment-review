"""Stage 3: the questions a symbol table and a filesystem can already settle.

A reviewer reads prose against code. Everything a machine can resolve first --
does this path exist, is this name defined anywhere, what number does this claim
-- is resolved here and handed over as an ANNOTATION on the paragraph, so the
reviewer spends its reading on the claim instead of on the lookup.

! Every annotation is a CANDIDATE. `names-a-symbol` most of all: a backticked
token can name a config key, a record field or an API payload, and the resolver
holds the namespaces it was handed.

`census.py` builds the paragraphs and calls `annotate()` on each one.
"""

import re
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

# !! `Paragraph` exists for TYPING ONLY -- `census.py` imports this module, so a
# real import would be circular -- and it is therefore NOT BOUND AT RUNTIME.
# Every annotation naming it is QUOTED for that reason. Measured 2026-08-17:
# unquoted and without `from __future__ import annotations`, this module and
# the three that import it raised `NameError: name 'Paragraph' is not defined`
# at import on Python 3.13 and on the 3.11 floor, while passing on the 3.14
# dev machine where PEP 649 makes annotations lazy.
if TYPE_CHECKING:
    from census import Paragraph

PATH_CITE = re.compile(r"`?([\w./-]+\.(?:py|md|toml|txt|json|ya?ml))(?:::(\w+))?`?")
TICKED = re.compile(r"`([^`\s]+)`")
# A token that could name a symbol. Single words count: every one-word module in
# a package is otherwise invisible.
# A trailing call form is stripped, so `foo()` resolves against `foo`.
# The alternative is U+2026, the ellipsis CHARACTER, written as an escape so
# this file stays ASCII -- `re` resolves it inside a raw pattern. It is not
# spelled out here because a literal one would be the very character this line
# exists to avoid, and `...` beside it means three dots, which the pattern
# already matches on its own.
CALLFORM = re.compile(r"\(\s*(?:\.\.\.|\u2026)?\s*\)$")
SYMBOLISH = re.compile(r"^[A-Za-z_][\w.]*$")
NOT_A_SYMBOL = frozenset(
    {"true", "false", "none", "null", "and", "or", "not", "if", "in", "is"}
)

COUNTED = re.compile(
    r"(?i)\b(one|two|three|four|five|six|seven|eight|nine|ten|only|every|all|no|"
    r"single|exactly|\d+)\s+"
    r"(call sites?|callers?|files?|modules?|tests?|readers?|consumers?|copies|"
    r"producers?|renderers?|writers?|places?|definitions?|sources?|entry points?)\b"
)
COVERAGE = re.compile(
    r"(?i)\b(pinned|guarded|asserted|enforced|covered|checked|locked)\s+(by|in)\b"
    r"|\bthe only call site\b|\bread by nothing\b|\bno reader\b|\bwrite-only\b"
    r"|\bsingle source of truth\b|\bnothing (reads|calls|enforces)\b"
)
FORBIDS = re.compile(
    r"(?i)\b(never|must not|do not|don't|no)\b[^.]{0,80}?"
    r"(\b\d+(?:\.\d+)?\b|`[^`]+`|\bliteral\b|\bhardcod\w+\b)"
)
# A bare number in prose. The PAIR is the finding: a number stated twice is a
# hand-copied threshold, and the copies drift.
# ! Dates are stripped first, so a `2026-08-09` reads as one date rather than
# three numbers.
# !! A trailing `.` is allowed unless a DIGIT follows it. The lookahead was
# `(?![\w.%])`, which rejected any match followed by a period and had no shorter
# alternative to backtrack to -- so a SENTENCE-FINAL number was never found.
# Measured 2026-08-17: `the cap is 3` gave `{'3'}` and `the cap is 3.` gave
# nothing, while `budget 3, not 5.` lost the 5. Prose is written in sentences,
# so `repeated-literal` never fired for the commonest form of the case its own
# docstring cites. ! `(?!\.\d)` still refuses a version or a decimal.
NUMBER = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w%])(?!\.\d)")
DATEISH = re.compile(r"\b\d{4}-\d{2}-\d{2}\w*|\bv?\d+\.\d+\.\d+\b")
# An ORDINAL opening a line -- `1.`, `2)`, after any comment marker, all of which
# are non-word characters. Allowing the sentence-final `3.` above also admitted
# the `1.` of a numbered list, and a list ordinal is not a value: two files that
# each number their steps share `1`, `2`, `3` and were annotated
# `repeated-literal` for it. Measured 2026-08-17: two files whose only numbers
# were list markers cross-reported at every ordinal.
LISTMARK = re.compile(r"^\W*\d+[.)]\s")


def prose_numbers(text: str, raw_lines: Sequence[str] = ()) -> set[str]:
    """Numbers a reader would call a VALUE -- dates, versions and ordinals gone.

    !! SINGLE DIGITS COUNT. A `len(n) > 1` filter discarded every one of them,
    and `repeated-literal` exists to catch a hand-copied threshold whose copies
    drift -- where the thresholds in this domain are overwhelmingly single
    digits. `the cap is 3` in two files never tripped it, which is precisely
    the case the annotation was built for. Measured 2026-08-17: `prose_numbers`
    returned nothing at all for `the cap is 3` and `retry 5 times`.

    Args:
        text: the paragraph's prose, already joined.
        raw_lines: the paragraph's lines as they sit in the file. Supplied, a list
            ordinal can be told from a sentence-final number -- the two are the
            same characters once the run is joined, and only the line start
            separates them. Re-joined here rather than reusing `text`, and the
            two agree on numbers because a comment marker holds no digit.
    """
    if raw_lines:
        text = " ".join(LISTMARK.sub(" ", ln) for ln in raw_lines)
    return set(NUMBER.findall(DATEISH.sub(" ", text)))


NARRATIVE = {
    "a date": re.compile(r"\b\d{4}-\d{2}-\d{2}\w*"),
    "a review label": re.compile(
        r"(?i)\bfix (wave|round)\b|\bfinding [A-Z]?\d|\breview finding\b"
        r"|\bround \d\b|\bCRITICAL [A-Z0-9]\b"
    ),
    # ! `used to` needs a VERB OF SAYING after it, not any verb. A bare
    # `\bused to\b` matches "often used to model a count process" -- ordinary
    # English about what a thing is FOR, rather than a claim about what the
    # code once was.
    "a retraction": re.compile(
        r"(?i)\bretract(ed|ion)?\b|\bpreviously\b|\bno longer\b"
        r"|\bused to (say|read|be|claim|mean|do|call|live|sit|carry|hold|return)\b"
        r"|\ban earlier (version|draft)\b|\bas before\b"
    ),
    "a rejected alternative": re.compile(
        r"(?i)considered and rejected|\brejected in favou?rs? of\b"
        r"|\bwas tried and\b|\balternatives? (were|was) (considered|rejected)\b"
    ),
}

# A runnable usage line is exempt from the narrative check: a date in
# `--start 2026-07-14` is a copy-pasteable EXAMPLE, not a claim about history.
# Without this WRITE pushes a working command out of a docstring in favour
# of a placeholder, degrading the docs.
COMMAND_LINE = re.compile(r"^\s*(\$ |uv run |python |pytest |npm |cargo |go )")


def annotate(
    paragraph: "Paragraph", known: set[str], paths: set[str], repo: Path
) -> None:
    """Attach every annotation this paragraph carries, and resolve it where possible."""
    t = paragraph.text
    if not t:
        return

    for tok in TICKED.findall(t):
        tok = CALLFORM.sub("", tok)
        if not SYMBOLISH.match(tok) or tok.lower() in NOT_A_SYMBOL:
            continue
        paragraph.annotations.add("names-a-symbol")
        # The HEAD segment must resolve, not ANY segment: matching any part lets
        # `Thing.meta` pass on `meta`, an obituary hiding behind a common
        # attribute name.
        if tok not in known and tok.split(".")[0] not in known:
            paragraph.notes.append(f"UNRESOLVED symbol `{tok}` (CANDIDATE)")

    for cited, member in PATH_CITE.findall(t):
        paragraph.annotations.add("cites-a-path")
        if cited not in paths and (repo / cited).exists():
            # Present on disk, absent from the index: derived or gitignored. A
            # fresh checkout holds no such file, so a claim resting on it is
            # UNVERIFIABLE -- a different note from one that resolves nowhere.
            paragraph.notes.append(f"UNVERIFIABLE path {cited} (untracked/derived)")
        elif cited not in paths:
            paragraph.notes.append(f"UNRESOLVED path {cited}")
        elif member and member.startswith("test_"):
            paragraph.notes.append(
                f"cites {cited}::{member} -- confirm the test exists"
            )

    if m := COUNTED.search(t):
        paragraph.annotations.add("counted")
        paragraph.notes.append(f"RE-COUNT, and name the population: {m.group(0)!r}")
    if m := COVERAGE.search(t):
        paragraph.annotations.add("coverage-claim")
        paragraph.notes.append(
            f"CHECK the guard exists AND can fail, exemptions OFF: {m.group(0)!r}"
        )
    if m := FORBIDS.search(t):
        paragraph.annotations.add("forbids-a-literal")
        paragraph.notes.append(
            f"GREP this file for what it forbids: {m.group(0)[:60]!r}"
        )

    if paragraph.kind == "docstring":
        for label, pat in NARRATIVE.items():
            for raw in paragraph.raw_lines:
                if COMMAND_LINE.match(raw):
                    continue
                if pat.search(raw):
                    paragraph.annotations.add("narrative-in-docstring")
                    paragraph.notes.append(f"{label}: {raw.strip()[:60]}")
                    break
