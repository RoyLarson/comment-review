"""Count the comment and docstring lines that say what the code does NOT do.

The measurement behind `TODO/the-shipped-python-does-not-pass-its-own-review.md`:
every comment or docstring LINE is the denominator, and those carrying one of
the nine words below are the numerator. Roy, 2026-08-16, on `census.py`: *"this
creates the pCST and that is it. Comments about 'cannot answer OWNERSHIP' are
not helpful."*

It reads a COMMIT rather than the working tree, so a historical claim can be
re-derived instead of remembered. That is what it was written for: on
2026-08-23 it identified the 2026-08-16 hand pass as the four commits
`5cb05ce..8c0cef6` by matching the recorded numbers against each candidate
tree, after a `--grep` search over the same window returned nothing.

!! **IT DOES NOT USE `page.py`, AND THAT IS THE POINT.** The census already
knows which lines are prose, so counting them again here is a second
implementation. It is deliberate for one reason: this script reads trees from
before the census existed in its current shape, and a `page.py` from HEAD is
not what those trees were written against. `tokenize` and `ast` are the floor
interpreter's own answer and are the same at every commit this can be pointed
at.

! **The counts do not reproduce the recorded table exactly, and the difference
is the DENOMINATOR.** Measured 2026-08-23: numerators land within 2 of every
row, and four of eight denominators match to the line, while the rest run
larger -- this counts a docstring's delimiter and blank lines as prose lines
and the hand count did not. So it identifies a tree reliably and does not
restate the table's percentages.

Usage:
    uv run python scripts/measure_negative_prose.py <commit> [<commit> ...]
"""

import argparse
import ast
import re
import subprocess
import sys
import tokenize
from io import BytesIO

# The nine words the TODO's tables are measured on. A negative is not
# automatically wrong -- one naming an OUTPUT ("REPORTED as unprovable") or
# aimed at whoever edits next earns its place -- so this reports a count and
# rules on nothing.
NEGATIVES = (
    "cannot",
    "never",
    "does not",
    "is not",
    "nothing",
    "neither",
    "without",
    "no longer",
    "not a",
)
NEGATIVE_RE = re.compile("|".join(re.escape(word) for word in NEGATIVES), re.IGNORECASE)

# A tree old enough to predate a syntax the floor interpreter accepts, or a
# file that is not valid Python at that commit, is REPORTED by path rather than
# skipped -- a silently dropped file moves the total.
PARSE_ERRORS = (SyntaxError, tokenize.TokenError, UnicodeDecodeError)


def git(*args: str) -> str:
    """Run git in the current repository and return stdout, raising on failure."""
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    ).stdout


def python_files(commit: str, prefix: str) -> list[str]:
    """Every `.py` path under `prefix` in `commit`'s tree, sorted."""
    listing = git("ls-tree", "-r", "--name-only", commit, "--", prefix)
    return sorted(path for path in listing.splitlines() if path.endswith(".py"))


def prose_lines(source: str) -> set[int]:
    """The 1-indexed line numbers holding a comment or a docstring.

    A docstring contributes every line it spans, delimiters included; a comment
    contributes the line its `#` opens on. A string that is not the first
    statement of a module, class or function is an expression, not a docstring,
    and is not counted.
    """
    lines: set[int] = set()

    for token in tokenize.tokenize(BytesIO(source.encode("utf-8")).readline):
        if token.type == tokenize.COMMENT:
            lines.add(token.start[0])

    owners = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, owners) or not node.body:
            continue
        first = node.body[0]
        if not (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            continue
        # `end_lineno` is Optional on the ast node but is always populated for a
        # tree built by `ast.parse`, which is the only source here.
        end = first.end_lineno if first.end_lineno is not None else first.lineno
        lines.update(range(first.lineno, end + 1))

    return lines


def measure(commit: str, path: str) -> tuple[int, int]:
    """Return (lines carrying a negative, total prose lines) for one file."""
    source = git("show", f"{commit}:{path}")
    numbered = source.splitlines()
    marked = prose_lines(source)
    hits = sum(1 for line in marked if NEGATIVE_RE.search(numbered[line - 1]))
    return hits, len(marked)


def row(name: str, hits: int, prose: int) -> str:
    """One printed line: the name, the two counts, and their percentage."""
    return f"  {name:<22} {hits:>4} / {prose:<4} ({round(100 * hits / prose)}%)"


def report(commit: str, prefix: str) -> None:
    """Print one commit's per-file counts and its total."""
    subject = git("log", "-1", "--pretty=%h %ad %s", "--date=short", commit).strip()
    print(f"\n=== {subject}")

    total_hits = total_prose = 0
    for path in python_files(commit, prefix):
        try:
            hits, prose = measure(commit, path)
        except PARSE_ERRORS as exc:
            print(f"  {path}: UNREADABLE at this commit -- {exc}")
            continue
        if prose == 0:
            continue
        total_hits += hits
        total_prose += prose
        print(row(path.split("/")[-1], hits, prose))

    if total_prose == 0:
        print("  no prose found under this prefix")
        return
    print(row("TOTAL", total_hits, total_prose))


def main() -> int:
    """Measure every commit named on the command line, in the order given."""
    # A Windows console is cp1252; one non-ASCII glyph kills the run, and a
    # commit subject is arbitrary text.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    # Not `__doc__`, which is None under `-OO` and would crash the parser.
    parser = argparse.ArgumentParser(
        description="Count prose lines saying what the code does NOT do."
    )
    parser.add_argument("commits", nargs="+", help="commits to measure, in order")
    parser.add_argument(
        "--prefix",
        default="plugins/",
        help="path prefix to measure under (default: the shipped tree)",
    )
    args = parser.parse_args()

    for commit in args.commits:
        report(commit, args.prefix)
    return 0


if __name__ == "__main__":
    sys.exit(main())
