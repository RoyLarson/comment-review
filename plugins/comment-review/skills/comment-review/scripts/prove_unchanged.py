"""Prove a comment-review sweep changed no executable code. Stage 7b's gate.

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
leaves the working tree inconsistent with every file the sweep did not touch --
and `git diff` hides it. Measured four times.
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from census import (  # noqa: E402  -- path shim must run first
    GIT_ERRORS,
    blocks_lexical,
    git_ls_files,
    language_for,
)

READ_ERRORS = (OSError, UnicodeDecodeError)
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


def _residue(text: str, path: Path) -> str | None:
    """The file with every comment block removed, or None if unreadable here."""
    lang = language_for(path)
    if lang is None:
        return None
    try:
        blocks = blocks_lexical(path, text, lang)
    except Exception:  # noqa: BLE001  -- an unprovable file is reported, not passed
        return None
    drop: set[int] = set()
    for block in blocks:
        for n in range(block.start, block.end + 1):
            drop.add(n)
    kept = [line for i, line in enumerate(text.splitlines(), 1) if i not in drop]
    return "\n".join(line.rstrip() for line in kept if line.strip())


def code_signature(text: str, path: Path) -> tuple[str, str]:
    """A value equal for two texts exactly when their executable code matches.

    Args:
        text: the file's contents.
        path: used only for its suffix, to pick the proof.

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
    return "residue", residue


def dominant_ending(text: str) -> str:
    """Which line ending this text mostly uses: "crlf", "lf" or "none"."""
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    if crlf == 0 and lf == 0:
        return "none"
    return "crlf" if crlf >= lf else "lf"


def _show(repo: Path, ref: str, rel: str) -> str | None:
    """`git show <ref>:<rel>`, or None when git cannot produce it."""
    try:
        got = subprocess.run(
            ["git", "-C", str(repo), "show", f"{ref}:{rel}"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except GIT_ERRORS:
        return None
    return got.stdout if got.returncode == 0 else None


def _sibling(repo: Path, target: Path, edited: set[Path]) -> Path | None:
    """A tracked file beside `target` that this sweep did not edit."""
    rels = git_ls_files(repo) or []
    for rel in rels:
        cand = (repo / rel).resolve()
        if cand.parent == target.parent and cand not in edited and cand != target:
            return cand
    return None


def main() -> int:
    """Prove every named path, and report what could not be proven."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--base", required=True, help="ref holding the pre-edit text")
    ap.add_argument("--repo", default=".", help="repo root")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    edited = {Path(p).resolve() for p in args.paths}
    failures = 0

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
            print(f"UNPROVABLE {rel}: no language record — code identity NOT shown")
            failures += 1
        elif sig_a != sig_b:
            print(f"FAIL      {rel}: executable code DIFFERS ({kind_a} proof)")
            failures += 1
        else:
            print(f"PROVEN    {rel}: code identical ({kind_a} proof)")

        sib = _sibling(repo, target, edited)
        if sib is None:
            print(f"          {rel}: no untouched sibling — line endings UNCHECKED")
        else:
            try:
                want = dominant_ending(sib.read_text(encoding="utf-8", newline=""))
            except READ_ERRORS:
                want = "none"
            got = dominant_ending(after)
            if want != "none" and got != want:
                print(f"FAIL      {rel}: line endings {got}, sibling {sib.name} {want}")
                failures += 1

    print()
    if failures:
        print(f"{failures} unproven. The sweep's identity claim does NOT hold.")
        return 1
    print(f"{len(args.paths)} paths proven: prose changed, executable code did not.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
