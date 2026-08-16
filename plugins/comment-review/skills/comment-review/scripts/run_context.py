"""The packet four reviewers are dispatched with, and its gate.

    python run_context.py --template > run-<id>/context.md
    python run_context.py --check run-<id>/context.md

Stage 4 hands each reviewer the 9 sections `REQUIRED` names below.
⚠ CAP and WIDTH are deliberately NOT among them. Length is not an editorial
role, and an agent that knows the cap writes to the cap -- what survives a
length-driven cut is the confident assertion, not the evidence for it. The cap
reaches stage 6 through `compact.md`'s own input contract instead.
Nothing checked the prompt before four agents fired in parallel, and a
section quietly absent degrades a reviewer with no error anywhere: measured, a
run with no style sheet introduced 14 en-GB spellings into a codebase whose
identifiers are en-US, and every reviewer was satisfied because nothing owned
consistency.

⚠ A section that is present and EMPTY is a failure, not a default. "No cap
published" is an answer and must be written; a blank is a question nobody
asked.

⚠ REVIEWER FILES carries ABSOLUTE paths on purpose. The plugin agents are
namespaced and resolve only if the plugin was installed before the session
started -- measured failing on 3 of 3 verification runs. With the paths in the
packet, the sanctioned fallback (four general-purpose agents given the paths of
their reviewer file and the brief) is a substitution, not an improvisation.

Three sections carry an answer a machine can check, and they ARE checked --
`LEVEL` against the four level names, `CENSUS` and each `REVIEWER FILES` entry
against the filesystem. Presence alone was not enough: replacing every hint
with `x` reported "Complete: all 11 sections answered", which is the shape of
a check that reads like a pass. The other eight are prose no oracle settles,
and this says nothing about them.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED = (
    "LEVEL",
    "DOC CONVENTION",
    "STYLE SHEET",
    "LSP LANGUAGES",
    "MOVE DESTINATION",
    "CENSUS",
    "REVIEWER FILES",
    "FILES UNDER REVIEW",
    "REFERENCE ONLY",
)

HINTS = {
    "LEVEL": "fact-check | line | full | proof",
    "DOC CONVENTION": "google | numpy | sphinx | none found, plus a template",
    "STYLE SHEET": "path to it, or `new — started this run`",
    "LSP LANGUAGES": (
        "which answered, which had no server, or `no LSP tool — no probe possible`"
    ),
    "MOVE DESTINATION": "the tree, or `UNAVAILABLE` — say which here, not at stage 6",
    "CENSUS": "absolute path, unique to THIS run",
    "REVIEWER FILES": (
        "absolute path per reviewer, the brief, and the compact + review agents"
    ),
    "FILES UNDER REVIEW": "one per line — the ONLY files a verdict may target",
    "REFERENCE ONLY": "one per line — read to settle a claim, never propose a change",
}

SECTION = re.compile(r"^##\s+(.+?)\s*$", re.M)
# ⚠ Any line starting with "##" is a boundary, even inside another section's
# answer prose -- a REFERENCE ONLY entry that quotes `"see the ## CENSUS
# heading"` would split the packet there. The failure direction is
# over-rejection (a spurious split makes a real answer look empty), so it is
# not a bypass, but it is a trap worth knowing about when filling a section.

# A terminated `<!-- ... -->` span, non-greedy and crossing newlines: a hint
# word-wrapped across two lines must be stripped as ONE span, not survive
# because neither line alone starts with "<!--".
COMMENT = re.compile(r"<!--.*?-->", re.S)

READ_ERRORS = (OSError, UnicodeDecodeError)
# ⚠ Bound to a NAME so no `except` clause here holds a tuple LITERAL -- the
# same rule as `census.py`'s `READ_ERRORS`. ValueError is in this one because
# `Path.exists()` raises it (not OSError) on a candidate holding a NUL byte,
# and a packet is arbitrary text a person typed.
PATH_ERRORS = (OSError, ValueError)

# The four names `SKILL.md`'s level table defines. A level outside this set
# dispatches four reviewers against a verdict vocabulary nobody published.
LEVELS = ("fact-check", "line", "full", "proof")

# A leading list marker, so `- /abs/path` and `1. /abs/path` name the path
# rather than the bullet.
LIST_MARK = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def template() -> str:
    """The skeleton, with a hint under each heading and no answers."""
    out = [
        "# comment-review run context",
        "",
        "Handed to every reviewer. Fill every section; `--check` refuses a blank.",
        "",
    ]
    for name in REQUIRED:
        out.append(f"## {name}")
        out.append(f"<!-- {HINTS[name]} -->")
        out.append("")
    return "\n".join(out)


def section_bodies(text: str) -> dict[str, list[str]]:
    """Every section's raw body, keyed by its heading, in order.

    Every occurrence is kept, not just the first -- a section given twice must
    not let one answered copy mask an empty other.
    """
    heads = list(SECTION.finditer(text))
    bodies: dict[str, list[str]] = {}
    for i, m in enumerate(heads):
        name = m.group(1).strip().upper()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        bodies.setdefault(name, []).append(text[m.end() : end])
    return bodies


def missing_sections(text: str) -> list[str]:
    """Required sections that are absent, or present with no answer.

    Args:
        text: the filled packet.

    Returns:
        The names of sections a reviewer would be dispatched without. A
        section counts as answered only if a letter or digit survives
        outside its comment spans (see `_answered`) — the template's own
        hints must be replaced with a real answer, not merely reflowed,
        half-closed, or left as a bare delimiter.
    """
    bodies = section_bodies(text)
    bad: list[str] = []
    for name in REQUIRED:
        occurrences = bodies.get(name)
        if not occurrences:
            bad.append(name)
            continue
        if any(not _answered(body) for body in occurrences):
            bad.append(name)
    return bad


def _answered(body: str) -> bool:
    """Does this section's body carry real content, not just a hint comment?

    A positive test, not a blacklist of delimiter shapes: complete
    `<!-- ... -->` spans are removed wherever they wrap (non-greedy, across
    newlines), an unterminated `<!--` with no closing `-->` is treated as
    running from the opener to the end of the body, and what remains counts
    as answered only if a letter or digit survives in it. No answer to any
    of the eleven questions this packet asks is punctuation-only, so this
    costs a real answer nothing, and a bare delimiter artifact -- `-->`,
    `--->`, or any other dash count -- can never satisfy it on its own.

    HTML comments do not nest: `<!--` opens and the FIRST `-->` closes it.
    `"<!--- a <!-- b --> c --->"` therefore reports answered, because the
    `c` genuinely sits outside that first span by the same rule -- not a
    hole in this check.
    """
    return any(ch.isalnum() for ch in _hintless(body))


def _hintless(body: str) -> str:
    """A section's body with its template hint spans removed.

    Complete `<!-- ... -->` spans go wherever they wrap (non-greedy, across
    newlines); an unterminated `<!--` is treated as running to the end of the
    body. What is left is what the person filling the packet actually wrote.
    """
    text = COMMENT.sub("", body)
    opener = text.find("<!--")
    if opener != -1:
        text = text[:opener]
    return text


def _answer_lines(body: str) -> list[str]:
    """The non-blank lines of a section's answer, hints removed."""
    return [ln.strip() for ln in _hintless(body).splitlines() if ln.strip()]


def _resolves(candidate: str) -> bool:
    """Is this an ABSOLUTE path that exists on this machine?

    Both halves matter and neither implies the other. A relative path resolves
    against whatever directory a reviewer happens to be in, which is the
    failure `REVIEWER FILES` carries absolute paths to avoid; an absolute path
    that is not there dispatches a reviewer at a file it cannot open.
    """
    try:
        path = Path(candidate)
        return path.is_absolute() and path.exists()
    except PATH_ERRORS:
        return False


def _path_candidates(line: str) -> list[str]:
    """The strings on this line that could be the path it names.

    A line may be bare, bulleted, or labelled (`ownership-context: /abs/path`). A
    Windows path carries a colon of its own, so splitting on ":" is not safe;
    the whole line and its LAST whitespace token are tried instead, and the
    line passes if either resolves.
    """
    bare = LIST_MARK.sub("", line).strip().strip("`").strip()
    out = [bare]
    tail = bare.split()[-1].strip("`") if bare.split() else ""
    if tail and tail != bare:
        out.append(tail)
    return out


def invalid_answers(text: str) -> list[str]:
    """Answers that are present but unusable, one line each.

    Only the three sections a machine can settle: `LEVEL` against the four
    published level names, `CENSUS` and each `REVIEWER FILES` entry against the
    filesystem. The other eight carry prose no oracle checks, and their
    absence from this list is not a pass on them.

    Args:
        text: the filled packet, already known to have every section answered.

    Returns:
        One string per problem, naming the section and what it holds.
    """
    bodies = section_bodies(text)
    bad: list[str] = []
    for body in bodies.get("LEVEL", []):
        answer = " ".join(_hintless(body).split()).strip("`. ")
        if answer.lower() not in LEVELS:
            bad.append(f"LEVEL: {answer!r} is not one of {' | '.join(LEVELS)}")
    for body in bodies.get("CENSUS", []):
        for line in _answer_lines(body):
            if not any(_resolves(c) for c in _path_candidates(line)):
                bad.append(f"CENSUS: {line!r} is not an absolute path that exists")
    for body in bodies.get("REVIEWER FILES", []):
        for line in _answer_lines(body):
            if not any(_resolves(c) for c in _path_candidates(line)):
                bad.append(
                    f"REVIEWER FILES: {line!r} is not an absolute path that exists"
                )
    return bad


def main() -> int:
    """Print the template, or check a filled packet."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--template", action="store_true")
    ap.add_argument("--check", metavar="FILE")
    args = ap.parse_args()

    if args.template:
        print(template())
        return 0
    if not args.check:
        ap.error("one of --template or --check is required")

    try:
        text = Path(args.check).read_text(encoding="utf-8")
    except READ_ERRORS as e:
        print(f"CANNOT READ {args.check} ({type(e).__name__}) — no packet to check")
        return 1

    bad = missing_sections(text)
    if bad:
        print(f"INCOMPLETE — {len(bad)} section(s) would dispatch unanswered:")
        for name in bad:
            print(f"  {name}: {HINTS[name]}")
        print(
            "\nDo not dispatch. A reviewer cannot report a context it never received."
        )
        return 1

    invalid = invalid_answers(text)
    if invalid:
        print(f"UNUSABLE — {len(invalid)} answer(s) a reviewer cannot act on:")
        for problem in invalid:
            print(f"  {problem}")
        print(
            "\nDo not dispatch. An answer that does not resolve is the same"
            " dispatch failure as a blank one, arriving later."
        )
        return 1

    print(
        f"Complete: all {len(REQUIRED)} sections answered, and LEVEL, CENSUS and"
        " REVIEWER FILES check out.\n⚠ The other six are prose nothing here can"
        " settle. Dispatch all four in ONE message."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
