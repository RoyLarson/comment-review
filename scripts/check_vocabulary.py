"""The vocabulary documents hold their shape: every term ruled, every citation live.

    python scripts/check_vocabulary.py

Two checks, and each exists because the thing it looks for had already gone wrong
without anyone noticing:

  CITATIONS  Every `file:line` in either document resolves to a line that exists.
             Deleting 34 lines of `reviewer-brief.md` on 2026-08-16 stranded 29
             citations past the end of their files, and nothing reported it.
  RULINGS    Every row in the inventory carries a ruling -- it is struck through,
             says SETTLED / DELETED / RETIRED, or names a site where the term is
             stated. Six rows read UNDEFINED for terms that had been settled for a
             day, because each term appears twice and only the first copy was
             updated.

Exits nonzero if either fails. A citation to a RENAMED file is reported as
HISTORICAL and does not fail: the quotation predates the rename and is the record.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INVENTORY = REPO / "docs" / "vocabulary-inventory.md"
DOCS = [INVENTORY, REPO / "docs" / "vocabulary-usage.md"]

# `- `ref/…` = `plugins/…/references/…`` in the inventory's PATH KEY section.
KEY_LINE = re.compile(r"^- `([^`]+?)(?:/…)?` = `([^`]+?)(?:/…)?`$")

# A citation: a backticked path, a colon, then line numbers -- `12`, `12-18`,
# `12,15-20`. The trailing group stops at the first character that cannot be
# part of a line list, so `census.py:114-116,805-855` is one citation.
CITE = re.compile(r"`([\w./-]+\.(?:md|py|toml|json)):(\d+(?:[-,]\d+)*)`")

READ_ERRORS = (OSError, UnicodeDecodeError)

RENAMED = {"apply.md": "write.md"}

# A row is RULED when it is struck through, says one of these, or names a site.
RULED = ("SETTLED", "DELETED", "RETIRED")
# A row is OPEN when it says one of these, whatever else it carries.
OPEN = ("UNRESOLVED", "UNDEFINED", "RE-OPENED")
NO_SITE = ("—", "-", "", "none")


def path_key() -> dict[str, str]:
    """The inventory's own prefix table, as {prefix: repo-relative directory}."""
    out: dict[str, str] = {}
    for raw in INVENTORY.read_text(encoding="utf-8").splitlines():
        m = KEY_LINE.match(raw.strip())
        if m:
            out[m.group(1)] = m.group(2)
    return out


def basenames() -> dict[str, list[Path]]:
    """Every source file in scope, indexed by bare filename.

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
    bare = cited.rsplit("/", 1)[-1]
    for name in (RENAMED.get(bare, bare), f"comment-review-{bare}"):
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


def check_citations() -> int:
    """Report every unresolvable or past-EOF citation. Returns how many broke."""
    key = path_key()
    if not key:
        print("no PATH KEY found in the inventory", file=sys.stderr)
        return 1
    index = basenames()
    broken = historical = checked = 0
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
    print(
        f"\n{checked} citations checked, {broken} broken,"
        f" {historical} historical (a renamed file, kept as the record)."
    )
    return broken


def check_rulings() -> int:
    """Report every inventory row with no ruling. Returns how many.

    A term appears in the summary table AND in the per-bundle table a collecting
    agent filled in, so both copies have to say the same thing.
    """
    unruled = rows = 0
    for n, raw in enumerate(INVENTORY.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.startswith("|") or set(raw) <= set("|- :"):
            continue
        cells = [c.strip() for c in raw.strip("|").split("|")]
        if cells[0] in ("Term", "Word"):
            continue
        rows += 1
        term = cells[0]
        site = cells[1] if len(cells) > 1 else ""
        ruled = "~~" in term or any(word in raw for word in RULED)
        if any(word in raw for word in OPEN) or (not ruled and site in NO_SITE):
            print(f"vocabulary-inventory.md:{n}  NO RULING  {term[:70]}")
            unruled += 1
    print(f"\n{rows} inventory rows checked, {unruled} without a ruling.")
    return unruled


def main() -> int:
    """Run both checks; exit nonzero if either found something."""
    broken = check_citations()
    unruled = check_rulings()
    return 1 if (broken or unruled) else 0


if __name__ == "__main__":
    raise SystemExit(main())
