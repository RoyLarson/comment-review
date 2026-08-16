"""Every `file:line` citation in the vocabulary documents resolves to a real line.

    python scripts/check_vocabulary_anchors.py

A settled term's whole value is that a reader can go to the line and read the
sentence. A citation pointing past the end of a file, or at a path that no longer
exists, is the dangling pointer this repo's own skill exists to find -- and until
now nothing looked for it.

Reads the PATH KEY out of `docs/vocabulary-inventory.md` rather than hard-coding
the four prefixes, so adding one is a row in that document.

Exits 1 on the first document with a broken citation. Reports every one before
exiting, because fixing them one run at a time is how the second gets missed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = [
    REPO / "docs" / "vocabulary-inventory.md",
    REPO / "docs" / "vocabulary-usage.md",
]
KEY_DOC = REPO / "docs" / "vocabulary-inventory.md"

# `- `ref/…` = `plugins/…/references/…`` in the inventory's PATH KEY section.
KEY_LINE = re.compile(r"^- `([^`]+?)(?:/…)?` = `([^`]+?)(?:/…)?`$")

# A citation: a backticked path, a colon, then line numbers -- `12`, `12-18`,
# `12,15-20`. The trailing group stops at the first character that cannot be
# part of a line list, so `census.py:114-116,805-855` is one citation.
CITE = re.compile(r"`([\w./-]+\.(?:md|py|toml|json)):(\d+(?:[-,]\d+)*)`")

READ_ERRORS = (OSError, UnicodeDecodeError)

RENAMED = {"apply.md": "write.md"}


def path_key() -> dict[str, str]:
    """The inventory's own prefix table, as {prefix: repo-relative directory}."""
    out: dict[str, str] = {}
    for raw in KEY_DOC.read_text(encoding="utf-8").splitlines():
        m = KEY_LINE.match(raw.strip())
        if m:
            out[m.group(1)] = m.group(2)
    return out


def basenames() -> dict[str, list[Path]]:
    """Every tracked source file in scope, indexed by bare filename.

    The usage document cites `census.py:114` as often as it cites the full path,
    so a bare name resolves when exactly one file in scope carries it.
    """
    out: dict[str, list[Path]] = {}
    for sub in ("plugins", "docs", "evals", "scripts", "tests", "corpora"):
        for p in (REPO / sub).rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts:
                out.setdefault(p.name, []).append(p)
    for name in ("README.md", "CLAUDE.md"):
        out.setdefault(name, []).append(REPO / name)
    return out


def resolve(
    cited: str, key: dict[str, str], index: dict[str, list[Path]]
) -> Path | None:
    """The file a citation names, or None when nothing in scope matches it."""
    if cited in key:
        return REPO / key[cited]
    head, _, tail = cited.partition("/")
    if head in key:
        return REPO / key[head] / tail
    direct = REPO / cited
    if direct.exists():
        return direct
    # `apply.md` was renamed to `write.md` on 2026-08-15. The usage document
    # quotes it under the old name because the quotations predate the rename,
    # and a historical quotation still has to resolve to a readable line.
    bare = RENAMED.get(cited.rsplit("/", 1)[-1], cited.rsplit("/", 1)[-1])
    for name in (bare, f"comment-review-{bare}"):
        hits = index.get(name, [])
        if len(hits) == 1:
            return hits[0]
    return None


def line_count(path: Path) -> int | None:
    """How many lines the file has, or None when it cannot be read."""
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except READ_ERRORS:
        return None


def main() -> int:
    """Report every unresolvable or past-EOF citation; exit 1 if any."""
    key = path_key()
    index = basenames()
    if not key:
        print("no PATH KEY found in the inventory", file=sys.stderr)
        return 1

    broken = 0
    historical = 0
    checked = 0
    for doc in DOCS:
        counts: dict[Path, int | None] = {}
        for n, raw in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
            for cited, lines in CITE.findall(raw):
                checked += 1
                target = resolve(cited, key, index)
                if target is None or not target.exists():
                    print(f"{doc.name}:{n}  UNRESOLVED  {cited}")
                    broken += 1
                    continue
                if target not in counts:
                    counts[target] = line_count(target)
                total = counts[target]
                if total is None:
                    print(f"{doc.name}:{n}  UNREADABLE  {cited}")
                    broken += 1
                    continue
                past = [
                    int(part)
                    for chunk in lines.split(",")
                    for part in chunk.split("-")
                    if int(part) > total
                ]
                if past:
                    was_renamed = cited.rsplit("/", 1)[-1] in RENAMED
                    kind = "HISTORICAL" if was_renamed else "PAST EOF"
                    print(
                        f"{doc.name}:{n}  {kind}  `{cited}:{lines}`"
                        f" -- file has {total} lines, cites {max(past)}"
                    )
                    if was_renamed:
                        historical += 1
                    else:
                        broken += 1

    print(f"\n{checked} citations checked, {broken} broken.")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
