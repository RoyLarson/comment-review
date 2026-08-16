"""THE CODE CHECK: prove the WRITE stage changed no executable code. Stage 7b's gate.

    python prove_unchanged.py --base <ref> [--repo D] <paths...>

Exits nonzero unless EVERY path is proven. The claim this skill makes to the
people who run it is that prose changed and code did not; that claim is a pure
function of two strings and must not rest on an agent performing it carefully.

Two proofs, because two tiers:

  ast       Python. Parse both, blank every docstring, compare `ast.dump`.
            Comments never reach the AST, so anything else that differs fails.
  residue   Any language with a `LANGUAGES` record. Delete every comment block
            the census finds, compare what remains, byte for byte.

⚠ A file this cannot prove is REPORTED as unprovable, never passed. A proof
that quietly degrades to "looks fine" is worse than no proof, because the
report still says PROVEN.

⚠ Line endings are checked against an UNTOUCHED SIBLING, never against the
stored blob: under `core.autocrlf` the blob is always LF, so normalising to it
leaves the working tree inconsistent with every file WRITE did not touch --
and `git diff` hides it. Measured four times.

⚠ An UNTERMINATED block comment makes the whole file UNPROVABLE. The lexer
swallows every line below the opener into that one run, so a code change after
that point never reaches the comparison and the residue is merely SHORT -- not
obviously wrong, and equal across two files whose code differs. The census
stamps that run `unterminated-block-comment` and this refuses the file on the
mark, rather than on a residue that only LOOKS like a proof.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# ⚠ `READ_ERRORS` is IMPORTED, not re-declared. It is bound to a NAME so no
# `except` clause holds a tuple literal, and `census.py` carries the reason
# once -- a second copy of that reasoning drifts before the code does.
from census import (  # noqa: E402  -- path shim must run first
    GIT_ERRORS,
    READ_ERRORS,
    Language,
    blocks_lexical,
    git,
    git_ls_files,
    language_for,
)

DOC_OWNERS = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _blank_docstrings(tree: ast.AST) -> ast.AST:
    """Replace every docstring's value with an empty string, in place.

    A docstring is prose this skill is allowed to rewrite, so its CONTENT must
    not enter the signature. Its presence still does: deleting a docstring
    entirely changes the body's shape and stays visible.
    """
    for node in ast.walk(tree):
        if not isinstance(node, DOC_OWNERS):
            continue
        if not node.body:
            continue
        first = node.body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
            if isinstance(first.value.value, str):
                first.value.value = ""
    return tree


def _delimiter_shares_the_line(line: str, lang: Language) -> bool:
    """A block-comment delimiter with real code beside it, on this ONE line.

    `blocks_lexical` stores the WHOLE line for a block comment's opening,
    closing or single-line form -- including any code that sits before the
    opener or after the closer -- so that line is stored identically to a
    line that is comment start to end. String equality cannot tell those
    apart; this can, cheaply, by re-scanning the line for the delimiters
    themselves.

    ⚠ This is a raw substring search, not a string-literal-aware scan like
    census's own lexer uses. A delimiter spelled out inside a string literal
    on the same line can trip this and route an actually-safe line to
    `unprovable` -- that is the SAFE direction for a proof to fail in, so it
    is accepted rather than duplicating census's quoting logic here.
    """
    for opener, closer in lang.block_comment:
        if opener in line and line[: line.index(opener)].strip():
            return True
        if closer in line and line[line.index(closer) + len(closer) :].strip():
            return True
    return False


def _residue(text: str, path: Path) -> str | None:
    """The file with every comment block removed, or None if unprovable here.

    Exact where the data allows it: a block's `raw_lines` is a literal slice
    of the source, so a line whose stored text matches it exactly is dropped
    whole, and a line whose stored text is only a SUFFIX (the trailing-comment
    case) keeps its code prefix. A line this cannot place with certainty --
    code sharing a line with a block-comment delimiter, which is stored as the
    whole line and so cannot be told apart from a line that is comment start
    to end -- is refused, not guessed at: the whole file becomes unprovable.

    An UNTERMINATED block comment is refused the same way, on the census's own
    `unterminated-block-comment` mark. The lexer swallows every line below the
    opener into that run, so the code below it never reaches the comparison and
    the residue is merely SHORT -- short, plausible and equal on two files whose
    executable code differs.
    """
    lang = language_for(path)
    if lang is None:
        return None
    try:
        blocks = blocks_lexical(path, text, lang)
    except Exception:  # noqa: BLE001  -- an unprovable file is reported, not passed
        return None
    if any("unterminated-block-comment" in b.marks for b in blocks):
        return None

    lines = text.splitlines()
    # Pre-seed every line as itself; a block below either drops its entry
    # (None) or replaces it with the code prefix it proved survives.
    kept: dict[int, str | None] = {i + 1: ln.rstrip() for i, ln in enumerate(lines)}
    for block in blocks:
        for offset, n in enumerate(range(block.start, block.end + 1)):
            if n not in kept or offset >= len(block.raw_lines):
                return None  # a block naming a line this text does not have
            actual = lines[n - 1].rstrip()
            stored = block.raw_lines[offset]
            if actual == stored:
                if _delimiter_shares_the_line(actual, lang):
                    return None
                kept[n] = None
            elif stored and actual.endswith(stored):
                kept[n] = actual[: len(actual) - len(stored)].rstrip()
            else:
                return None  # census and the file disagree; do not reconcile
    survivors = [v for v in kept.values() if v is not None]
    return "\n".join(v for v in survivors if v.strip())


def code_signature(text: str, path: Path) -> tuple[str, str]:
    """A value equal for two texts exactly when their executable code matches.

    Args:
        text: the file's contents.
        path: used only for its suffix, to pick which comparison runs.

    Returns:
        `(kind, signature)`. `kind` is "ast", "residue" or "unprovable"; an
        unprovable file carries an empty signature and must never be reported
        as proven.
    """
    if path.suffix.lower() in (".py", ".pyi"):
        try:
            return "ast", ast.dump(_blank_docstrings(ast.parse(text)))
        except SyntaxError:
            pass  # fall through to residue; a broken parse proves nothing
    residue = _residue(text, path)
    if residue is None:
        return "unprovable", ""
    if not residue.strip() and text.strip():
        # An all-comment file reaches here with an EMPTY residue while the
        # source was not empty. `"" == ""` would "prove" any two such files
        # identical no matter what code either held -- comparing nothing is
        # not a proof.
        return "unprovable", ""
    return "residue", residue


def dominant_ending(text: str) -> str:
    """Which line ending this text mostly uses: "crlf", "lf" or "none"."""
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    if crlf == 0 and lf == 0:
        return "none"
    return "crlf" if crlf >= lf else "lf"


def _read_raw(path: Path) -> str:
    r"""The file's own line endings, untranslated.

    `Path.read_text` (and a plain `open` with no `newline=`) applies
    universal-newline translation, collapsing every `\r\n` to `\n` before
    this code ever sees it -- so a CRLF file and an LF file become
    indistinguishable by the time `dominant_ending` looks at them. `newline=""`
    disables that translation.

    ⚠ `Path.read_text`'s own `newline=` parameter was added in Python 3.13;
    calling it on the 3.9 floor this script promises is a `TypeError` that
    `check_shipped_syntax.py` cannot see (it checks syntax, not which
    keyword arguments exist at runtime). `open(...).read()` works at the
    floor and does the same thing.
    """
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def _show(repo: Path, ref: str, rel: str) -> str | None:
    """`git show <ref>:<rel>`, or None when git cannot produce it."""
    try:
        got = git(repo, "show", f"{ref}:{rel}")
    except GIT_ERRORS:
        return None
    return got.stdout if got.returncode == 0 else None


def _sibling(
    repo: Path, target: Path, edited: set[Path], tracked: list[str]
) -> Path | None:
    """A READABLE tracked file beside `target` that WRITE did not edit.

    Skips a candidate this process cannot itself read as UTF-8 text -- a
    binary or non-UTF-8 sibling is not a usable line-ending reference, and
    committing to the first NAME found in the same directory silently
    disabled the check instead of trying the next tracked file.

    Args:
        repo: the repository root.
        target: the file being proven; never returned as its own sibling.
        edited: every path this run was asked to prove, resolved -- none of
            them qualifies as "untouched".
        tracked: `git_ls_files(repo)` (or `[]`), passed in rather than
            queried here so a multi-path run spawns git once, not per path.
    """
    for rel in tracked:
        cand = (repo / rel).resolve()
        if cand.parent != target.parent or cand in edited or cand == target:
            continue
        try:
            _read_raw(cand)
        except READ_ERRORS:
            continue
        return cand
    return None


def main() -> int:
    """Prove every named path, and report what could not be proven."""
    # A report that dies on an em-dash in someone's docstring is not a tool.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--base", required=True, help="ref holding the pre-edit text")
    ap.add_argument("--repo", default=".", help="repo root")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    edited = {Path(p).resolve() for p in args.paths}
    tracked = git_ls_files(repo) or []  # one subprocess for the whole run
    failures = 0
    unchecked = 0

    for raw in args.paths:
        target = Path(raw).resolve()
        try:
            rel = target.relative_to(repo).as_posix()
        except ValueError:
            print(f"FAIL      {raw}: outside --repo")
            failures += 1
            continue

        before = _show(repo, args.base, rel)
        if before is None:
            print(f"UNPROVABLE {rel}: no {args.base}:{rel} — new file, or bad ref")
            failures += 1
            continue
        try:
            after = target.read_text(encoding="utf-8")
        except READ_ERRORS as e:
            print(f"FAIL      {rel}: {type(e).__name__}")
            failures += 1
            continue

        kind_b, sig_b = code_signature(before, target)
        kind_a, sig_a = code_signature(after, target)
        if kind_a == "unprovable" or kind_b == "unprovable":
            print(
                f"UNPROVABLE {rel}: prose could not be separated from code"
                " — code identity NOT shown"
            )
            failures += 1
        elif kind_a != kind_b:
            print(
                f"FAIL      {rel}: proof kind changed ({kind_b} -> {kind_a}) "
                "— likely broke Python syntax"
            )
            failures += 1
        elif sig_a != sig_b:
            print(f"FAIL      {rel}: executable code DIFFERS ({kind_a} proof)")
            failures += 1
        else:
            print(f"PROVEN    {rel}: code identical ({kind_a} proof)")

        sib = _sibling(repo, target, edited, tracked)
        if sib is None:
            print(f"UNCHECKED  {rel}: no readable untouched sibling — line endings")
            unchecked += 1
        else:
            want = dominant_ending(_read_raw(sib))
            got = dominant_ending(_read_raw(target))
            # ⚠ BOTH sides are guarded against "none". A single-line file with
            # no trailing newline has no ending to measure, so it reads "none"
            # and would FAIL against any CRLF sibling -- a file whose endings
            # are not wrong, only absent.
            if want != "none" and got != "none" and got != want:
                print(f"FAIL      {rel}: line endings {got}, sibling {sib.name} {want}")
                failures += 1

    print()
    if failures:
        print(f"{failures} unproven. WRITE's identity claim does NOT hold.")
        return 1
    if unchecked:
        print(
            f"{len(args.paths)} paths proven code-identical; {unchecked} with line "
            "endings UNCHECKED (no readable untouched sibling to compare against)."
        )
    else:
        print(
            f"{len(args.paths)} paths proven: prose changed, executable code did not."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
