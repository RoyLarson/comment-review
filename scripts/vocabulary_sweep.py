"""Terms of art in the shipped tree that the vocabulary inventory does not list.

    python scripts/vocabulary_sweep.py [--min-files 2] [--limit 40]

The 2026-08-15 survey read the tree with twelve agents and still missed `budget`
(18 sites, four senses) and `own` (four senses) -- both found later by Roy reading
a justification. A word is easiest to miss when it reads as ordinary English, so
this looks for the two shapes a reader does not have to notice:

  MARKED    a word the prose itself singles out -- `backticked` in markdown, or
            ALLCAPS -- recurring often enough and across enough files to be a
            term rather than one-off emphasis.
  DOUBLE    a plain word used BOTH in the prose and as a Python identifier. This
            is the shape every miss so far has had: `budget`, `own`, `label`,
            `signature`, `residue` and `statement` were each a rule's word and a
            script's name at once, and the two senses drifted apart unnoticed.
            Raw frequency was tried and discarded -- it ranks `here` and
            `because` above every real term, so it discriminates nothing.

Known terms come from the SHIPPED `vocabulary.toml` and from `docs/vocabulary.md`,
so settling a term removes it from this output on the next run.
"""

import argparse
import re
import tomllib
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHIPPED = REPO / "plugins"
SETTLED = REPO / "docs" / "vocabulary.md"
EMITTED = SHIPPED / "comment-review/skills/comment-review/references/vocabulary.toml"

BACKTICKED = re.compile(r"`([A-Za-z][\w-]{2,})`")
ALLCAPS = re.compile(r"\b([A-Z][A-Z-]{2,})\b")
WORD = re.compile(r"\b([a-z][a-z-]{3,})\b")
# A name this repo DELIBERATELY binds, at module level: a function, a class, a
# dataclass field, or a CONSTANT. Locals are excluded on purpose -- `text`, `path`
# and `first` are incidental, and including them buried every real hit.
IDENT = re.compile(
    r"^(?:def|class)\s+_?([A-Za-z]\w+)"
    r"|^_?([A-Z][A-Z0-9_]+)\s*=[^=]"
    r"|^    ([a-z]\w+):\s*\w",
    re.MULTILINE,
)

# Markdown/code scaffolding, and English that ALLCAPS emphasis reaches constantly.
# Not a suppression list: every entry is a word this repo uses as emphasis or as a
# language keyword, never as a term of its own.
SCAFFOLD = frozenset(
    """
and are but for from has have its into not now one only that the them then they this
was were what when where which with you your all any can each else its more most must
never new nor off out over same some such than there these those too very via
""".split()
)

READ_ERRORS = (OSError, UnicodeDecodeError)


def known_terms() -> set[str]:
    """Every term already settled: emitted to agents, or recorded in `docs/`."""
    out: set[str] = set(
        tomllib.loads(EMITTED.read_text(encoding="utf-8"))["definitions"]
    )
    # `docs/vocabulary.md` names its terms in the first cell of a table row and
    # in bold or backticks inline; both forms count as settled.
    text = SETTLED.read_text(encoding="utf-8")
    for raw in text.splitlines():
        if raw.startswith("|"):
            cell = raw.split("|")[1]
            for name in re.findall(r"[`*]{1,2}([\w][\w -]*?)[`*]{1,2}", cell):
                out.add(name.strip().lower())
    for name in re.findall(r"\*\*([\w][\w -]*?)\*\*", text):
        out.add(name.strip().lower())
    for token in re.findall(r"`([\w-]{3,})`", text):
        out.add(token.lower())
    return {t for t in out if t}


def shipped_files() -> list[Path]:
    """Every markdown and Python file under `plugins/`, sorted."""
    return [
        p
        for p in sorted(SHIPPED.rglob("*"))
        if p.suffix in (".md", ".py") and "__pycache__" not in p.parts
    ]


def collect(
    files: list[Path],
) -> tuple[dict[str, set[Path]], dict[str, set[Path]], dict[str, set[Path]]]:
    """(marked, plain, bound): each word mapped to the files it appears in."""
    marked: dict[str, set[Path]] = defaultdict(set)
    plain: dict[str, set[Path]] = defaultdict(set)
    bound: dict[str, set[Path]] = defaultdict(set)
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except READ_ERRORS:
            continue
        for hit in BACKTICKED.findall(text):
            marked[hit.lower()].add(path)
        for hit in ALLCAPS.findall(text):
            marked[hit.lower()].add(path)
        for hit in WORD.findall(text):
            plain[hit].add(path)
        if path.suffix == ".py":
            for groups in IDENT.findall(text):
                name = next(g for g in groups if g)
                bound[name.lower().lstrip("_")].add(path)
    return marked, plain, bound


def report(
    title: str,
    found: dict[str, set[Path]],
    known: set[str],
    min_files: int,
    limit: int,
) -> None:
    """Print one ranked candidate list: word, how many files, which."""
    rows = [
        (word, files)
        for word, files in found.items()
        if word not in known and word not in SCAFFOLD and len(files) >= min_files
    ]
    rows.sort(key=lambda r: (-len(r[1]), r[0]))
    print(f"\n{title} -- {len(rows)} candidates\n")
    for word, files in rows[:limit]:
        names = ", ".join(sorted(f.name for f in files)[:4])
        extra = "" if len(files) <= 4 else f" +{len(files) - 4}"
        print(f"  {len(files):3d} files  {word:<24} {names}{extra}")


def main() -> int:
    """Print both candidate lists. Always exits 0: this is an input, not a gate."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-files", type=int, default=2)
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    known = known_terms()
    files = shipped_files()
    marked, plain, bound = collect(files)
    print(f"{len(files)} shipped files, {len(known)} names already settled")
    report("MARKED and unlisted", marked, known, args.min_files, args.limit)
    double = {
        w: plain[w] | bound[w] for w in bound if w in plain and len(plain[w]) >= 3
    }
    report("DOUBLE -- a rule's word AND a script's name", double, known, 3, args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
