"""The packet four reviewers are dispatched with, and its gate.

    python run_context.py --template > run-<id>/context.md
    python run_context.py --check run-<id>/context.md

Stage 4 hands each reviewer seven things. Nothing checked the prompt before
four agents fired in parallel, and a section quietly absent degrades an angle
with no error anywhere: measured, a run with no style sheet introduced 14
en-GB spellings into a codebase whose identifiers are en-US, and every angle
was satisfied because nothing owned consistency.

⚠ A section that is present and EMPTY is a failure, not a default. "No cap
published" is an answer and must be written; a blank is a question nobody
asked.

⚠ ANGLE FILES carries ABSOLUTE paths on purpose. The plugin agents are
namespaced and resolve only if the plugin was installed before the session
started -- measured failing on 3 of 3 verification runs. With the paths in the
packet, the sanctioned fallback (four general-purpose agents given the paths of
their angle file and the brief) is a substitution, not an improvisation.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED = (
    "LEVEL",
    "CAP",
    "WIDTH",
    "DOC CONVENTION",
    "STYLE SHEET",
    "LSP LANGUAGES",
    "MOVE DESTINATION",
    "CENSUS",
    "ANGLE FILES",
    "FILES UNDER REVIEW",
    "REFERENCE ONLY",
)

HINTS = {
    "LEVEL": "fact-check | line | full | proof",
    "CAP": "the number, or `none published` — never invent one",
    "WIDTH": "the number, or `none published`",
    "DOC CONVENTION": "google | numpy | sphinx | none found, plus a template",
    "STYLE SHEET": "path to it, or `new — started this run`",
    "LSP LANGUAGES": (
        "which answered, which had no server, or `no LSP tool — no probe possible`"
    ),
    "MOVE DESTINATION": "the tree, or `UNAVAILABLE` — say which here, not at stage 6",
    "CENSUS": "absolute path, unique to THIS run",
    "ANGLE FILES": "absolute path per angle, plus the brief",
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


def missing_sections(text: str) -> list[str]:
    """Required sections that are absent, or present with no answer.

    Args:
        text: the filled packet.

    Returns:
        The names of sections a reviewer would be dispatched without. A hint
        comment is not an answer, whole-span and however it is wrapped — the
        template's own hints must be replaced, not merely reflowed.
    """
    heads = list(SECTION.finditer(text))
    # Every occurrence is kept, not just the first -- a section given twice
    # must not let one answered copy mask an empty other. All occurrences of
    # a name must carry an answer, or the name is bad.
    bodies: dict[str, list[str]] = {}
    for i, m in enumerate(heads):
        name = m.group(1).strip().upper()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        bodies.setdefault(name, []).append(text[m.end() : end])
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

    Comments are stripped as SPANS, not lines: a hint reflowed across two
    lines by an editor must not survive because its continuation line does
    not itself start with `<!--`. An unterminated `<!--` with no closing
    `-->` is treated as commenting out everything from the opener to the end
    of the body -- deliberately, not an oversight: over-rejecting a stray
    `<!--` costs one edit, while under-rejecting dispatches four agents
    against context nobody actually supplied.
    """
    text = COMMENT.sub("", body)
    opener = text.find("<!--")
    if opener != -1:
        text = text[:opener]
    return bool(text.strip())


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
    print(
        f"Complete: all {len(REQUIRED)} sections answered."
        " Dispatch all four in ONE message."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
