"""The packet four reviewers are dispatched with, and its gate.

    python run_context.py --template > run-<id>/context.md
    python run_context.py --check run-<id>/context.md

`REQUIRED` names 9 sections below, and stage 4 hands each reviewer all of them
EXCEPT the ones in `TASK_AGENT_ONLY`. This gate runs before four agents fire in
parallel: a section quietly absent degrades a reviewer with no error anywhere,
and a run with no style sheet introduced en-GB spellings into a codebase whose
identifiers are en-US, with every reviewer satisfied because nothing owned
consistency.

! REPO ROOT is what every other path is relative to. FILES UNDER REVIEW, the
census entries and every citation a reviewer writes are repo-relative, and
without the root a reviewer resolving `a.py` is guessing at a working directory.

! CAP and WIDTH are absent from REQUIRED. Stage 6 is handed the cap through
`compact.md`'s own input contract instead.

! A section present and EMPTY is a failure. A published non-answer --
`UNAVAILABLE` for MOVE DESTINATION, `no LSP tool` for LSP LANGUAGES -- is an
answer and gets written; a blank is refused.

!! REVIEWER FILES is the TASK AGENT's section and is NOT pasted to a reviewer.
It carries absolute paths into the installed plugin under `.claude/`, and the
plugin's tree is not the tree under review -- handing them over is a reason to go
reading it. They are here for the stage-1.6 fallback: the plugin agents are
namespaced and resolve only where the plugin was installed before the session
started, which has been measured failing, and with the paths already in the
packet the fallback -- four general-purpose agents handed their reviewer file and
the brief -- is a substitution rather than an improvisation.

Three sections carry an answer a machine can settle, and they ARE checked:
`REPO ROOT`, `CENSUS` and each `REVIEWER FILES` entry, against the filesystem.
Presence alone let a packet whose every hint was replaced with `x` report itself
complete. The rest carry prose no oracle settles, and this reports nothing about
them.
"""

import argparse
import re
import sys
from pathlib import Path

REQUIRED = (
    "REPO ROOT",
    "DOC CONVENTION",
    "STYLE SHEET",
    "LSP LANGUAGES",
    "MOVE DESTINATION",
    "CENSUS",
    "REVIEWER FILES",
    "FILES UNDER REVIEW",
    "REFERENCE ONLY",
)

# ! Filled by the task agent, checked here, and NOT handed to a reviewer: it
# names paths inside the installed plugin, which is not the tree under review.
TASK_AGENT_ONLY = frozenset({"REVIEWER FILES"})

HINTS = {
    "REPO ROOT": (
        "absolute path to the repo under review -- what every relative path in"
        " this packet, in the census and in every citation resolves against"
    ),
    "DOC CONVENTION": (
        "MEASURED templates: module docstring, function docstring, and comment"
        " format if the repo is consistent about one -- never a standard's name alone"
    ),
    "STYLE SHEET": "path to it, or `new -- started this run`",
    "LSP LANGUAGES": (
        "which answered, which had no server, or `no LSP tool -- no probe possible`"
    ),
    "MOVE DESTINATION": (
        "the tree, or `UNAVAILABLE` -- say which here, not at stage 6."
        " ! May be PER PATH: one line per scope where a repo built the tree"
        " for some packages and not others"
    ),
    "CENSUS": "absolute path, unique to THIS run",
    "REVIEWER FILES": (
        "absolute path per reviewer, the brief, and the compact + review agents"
    ),
    "FILES UNDER REVIEW": "one per line -- the ONLY files a verdict may target",
    "REFERENCE ONLY": "one per line -- read to settle a claim, never propose a change",
}

SECTION = re.compile(r"^##\s+(.+?)\s*$", re.M)
# ! Any line starting with "##" is a boundary, even inside another section's
# answer prose -- a REFERENCE ONLY entry quoting `"see the ## CENSUS heading"`
# splits the packet there. The failure direction is over-rejection: a spurious
# split makes a real answer read as empty.

# A terminated `<!-- ... -->` span, non-greedy and crossing newlines: a hint
# word-wrapped across two lines must be stripped as ONE span, not survive
# because neither line alone starts with "<!--".
COMMENT = re.compile(r"<!--.*?-->", re.S)

READ_ERRORS = (OSError, UnicodeDecodeError)
# ! Bound to a NAME so no `except` clause here holds a tuple LITERAL -- the
# same rule `repo.py` carries in full. ValueError is in this one because
# `Path.exists()` raises it (not OSError) on a candidate holding a NUL byte,
# and a packet is arbitrary text a person typed.
PATH_ERRORS = (OSError, ValueError)

# A leading list marker, so `- /abs/path` and `1. /abs/path` name the path
# rather than the bullet.
LIST_MARK = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def template() -> str:
    """The skeleton, with a hint under each heading and no answers."""
    out = [
        "# comment-review run context",
        "",
        "Fill every section; `--check` refuses a blank. Every section is handed"
        " to every reviewer EXCEPT the ones marked TASK AGENT ONLY.",
        "",
    ]
    for name in REQUIRED:
        out.append(f"## {name}")
        if name in TASK_AGENT_ONLY:
            out.append("<!-- ! TASK AGENT ONLY -- do not paste this section -->")
        out.append(f"<!-- {HINTS[name]} -->")
        out.append("")
    return "\n".join(out)


def section_bodies(text: str) -> dict[str, list[str]]:
    """Every section's raw body, keyed by its heading, in order.

    Every occurrence is kept, so a section given twice is judged on both copies
    and an answered one stands clear of an empty one.
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
        section counts as answered when a letter or digit survives outside
        its comment spans (see `_answered`), so the template's own hints
        have to be REPLACED -- reflowing one, half-closing it, or leaving a
        bare delimiter all still read as unanswered.
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
    """Does this section's body carry real content, past its hint comment?

    A POSITIVE test on what remains: complete `<!-- ... -->` spans are removed
    wherever they wrap (non-greedy, across newlines), an unterminated `<!--`
    runs from the opener to the end of the body, and what is left counts as
    answered when a letter or digit survives in it. Every answer this packet
    asks for carries one; a bare delimiter artifact -- `-->`, `--->`, any dash
    count -- carries none.

    HTML comments do not nest: `<!--` opens and the FIRST `-->` closes it, so
    `"<!--- a <!-- b --> c --->"` reports answered -- `c` sits outside that
    first span by the same rule.
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

    Both halves matter, independently. A relative path resolves against
    whatever directory a reviewer happens to be in, which is what absolute
    paths in `REVIEWER FILES` avoid; an absolute path that is absent dispatches
    a reviewer at a file it cannot open.
    """
    try:
        path = Path(candidate)
        return path.is_absolute() and path.exists()
    except PATH_ERRORS:
        return False


def _path_candidates(line: str) -> list[str]:
    """The strings on this line that could be the path it names.

    A line may be bare, bulleted, or labelled (`ownership-context: /abs/path`).
    A Windows path carries a colon of its own, so splitting on ":" would cut
    the drive letter; the whole line and its LAST whitespace token are tried
    instead, and the line passes if either resolves.
    """
    bare = LIST_MARK.sub("", line).strip().strip("`").strip()
    out = [bare]
    tail = bare.split()[-1].strip("`") if bare.split() else ""
    if tail and tail != bare:
        out.append(tail)
    return out


def invalid_answers(text: str) -> list[str]:
    """Answers that are present but unusable, one line each.

    Only the three sections a machine can settle: `REPO ROOT`, `CENSUS` and each
    `REVIEWER FILES` entry, against the filesystem. The rest carry prose no
    oracle checks, so this list stays silent about them.

    Args:
        text: the filled packet, already known to have every section answered.

    Returns:
        One string per problem, naming the section and what it holds.
    """
    bodies = section_bodies(text)
    bad: list[str] = []
    for body in bodies.get("REPO ROOT", []):
        for line in _answer_lines(body):
            if not any(_resolves(c) for c in _path_candidates(line)):
                bad.append(f"REPO ROOT: {line!r} is not an absolute path that exists")
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
        print(f"CANNOT READ {args.check} ({type(e).__name__}) -- no packet to check")
        return 1

    bad = missing_sections(text)
    if bad:
        print(f"INCOMPLETE -- {len(bad)} section(s) would dispatch unanswered:")
        for name in bad:
            print(f"  {name}: {HINTS[name]}")
        print(
            "\nDo not dispatch. A reviewer cannot report a context it never received."
        )
        return 1

    invalid = invalid_answers(text)
    if invalid:
        print(f"UNUSABLE -- {len(invalid)} answer(s) a reviewer cannot act on:")
        for problem in invalid:
            print(f"  {problem}")
        print(
            "\nDo not dispatch. An answer that does not resolve is the same"
            " dispatch failure as a blank one, arriving later."
        )
        return 1

    print(
        f"Complete: all {len(REQUIRED)} sections answered, and REPO ROOT, CENSUS"
        f" and REVIEWER FILES check out.\n! The other {len(REQUIRED) - 3} are"
        " prose nothing here can settle. Dispatch all four in ONE message, so no"
        " role sees another's findings.\n! Withhold every TASK AGENT ONLY"
        f" section: {', '.join(sorted(TASK_AGENT_ONLY))}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
