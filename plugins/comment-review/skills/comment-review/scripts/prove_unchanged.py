"""THE CODE CHECK: does the parser read the file the same before and after?

Stage 7b's gate.

    python prove_unchanged.py --base <ref> [--repo D] <paths...>

Exits nonzero unless EVERY path is proven. The claim this skill makes to the
people who run it is that prose changed and the rest reads the same; that claim
is a pure function of two strings, so this computes it.

Two proofs, because two tiers:

  ast       Python, using the LANGUAGE'S OWN parser. Blank every docstring,
            compare `ast.dump`. Comments never reach the AST, so anything else
            that differs fails.
  stripped  Any other `LANGUAGES` record, using THIS REPO'S comment lexer.
            Delete every comment it finds, compare the lines that remain --
            right-stripped, blanks dropped. A PROJECTION of the file; line
            endings are compared separately below, since this drops them.

! For Python the proof is CPython parsing its own language. Elsewhere it rests
on a lexer built from a data row, so where that lexer is unsure this refuses: a
delimiter sharing a line with code, an unterminated paragraph comment, or a census
that disagrees with the file all return `unprovable`.

! A file this cannot prove is REPORTED as unprovable and counted a failure. A
proof that degrades to "looks fine" still prints PROVEN.

! Line endings are compared against an UNTOUCHED SIBLING rather than the stored
blob: under `core.autocrlf` the blob is always LF, so normalising to it leaves
the working tree inconsistent with every file WRITE left alone -- and `git diff`
hides that.
"""

import argparse
import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# ! `READ_ERRORS` is IMPORTED. It is bound to a NAME so no `except` clause here
# holds a tuple literal; `repo.py` carries that reason once.
from lexer import (  # noqa: E402  -- path shim must run first
    Language,
    language_for,
    paragraphs_lexical,
)
from repo import (  # noqa: E402  -- path shim must run first
    GIT_ERRORS,
    READ_ERRORS,
    git,
    git_ls_files,
    read_raw,
)

DOC_ANCHORS = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _blank_docstrings(tree: ast.AST) -> ast.AST:
    """Replace every docstring's value with an empty string, in place.

    A docstring is prose this skill is allowed to rewrite, so its CONTENT must
    not enter the fingerprint. Its presence still does: deleting a docstring
    entirely changes the body's shape and stays visible.
    """
    for node in ast.walk(tree):
        if not isinstance(node, DOC_ANCHORS):
            continue
        if not node.body:
            continue
        first = node.body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
            if isinstance(first.value.value, str):
                first.value.value = ""
    return tree


def _delimiter_shares_the_line(line: str, lang: Language) -> bool:
    """A paragraph-comment delimiter with real code beside it, on this ONE line.

    `paragraphs_lexical` stores the WHOLE line for a paragraph comment's opening,
    closing or single-line form -- including any code that sits before the
    opener or after the closer -- so that line is stored identically to a line
    that is comment start to end. Re-scanning the line for the delimiters
    themselves is what separates them.

    ! A raw substring search, where census's own lexer is string-literal-aware.
    A delimiter spelled inside a string literal on the same line trips this and
    routes a safe line to `unprovable` -- the SAFE direction for a proof to
    fail, so it stands in place of a second copy of census's quoting logic.
    """
    for opener, closer in lang.block_comment:
        if opener in line and line[: line.index(opener)].strip():
            return True
        if closer in line and line[line.index(closer) + len(closer) :].strip():
            return True
    return False


def _without_comments(text: str, path: Path) -> str | None:
    """The file with every comment paragraph removed, or None if unprovable here.

    Exact where the data allows it: a paragraph's `raw_lines` is a literal slice of
    the source, so a line whose stored text matches it exactly is dropped whole,
    and a line whose stored text is only a SUFFIX (the trailing-comment case)
    keeps its code prefix. A line this cannot place -- code sharing a line with
    a paragraph-comment delimiter, see `_delimiter_shares_the_line` -- makes the
    whole file unprovable.

    An UNTERMINATED paragraph comment is refused the same way, on the census's own
    `unterminated-paragraph-comment` annotation. The lexer swallows every line below
    the opener into that run, so code below it never reaches the comparison and
    the stripped text is merely SHORT -- short, plausible, and equal on two
    files whose executable code differs.
    """
    lang = language_for(path)
    if lang is None:
        return None
    try:
        paragraphs = paragraphs_lexical(path, text, lang)
    except Exception:  # noqa: BLE001  -- an unprovable file is reported, not passed
        return None
    if any("unterminated-paragraph-comment" in b.annotations for b in paragraphs):
        return None
    # !! A LITERAL THAT SPANS LINES MAKES THIS FILE UNPROVABLE. `_strip_strings`
    # is per-line and carries no open-quote state, so a line INSIDE a JS
    # template literal or a Java text paragraph that begins with the language's
    # comment marker is censused as a comment and deleted from BOTH
    # fingerprints. Measured 2026-08-17: a template literal whose body changed
    # from `// alpha` to `// omega` produced identical fingerprints and the file
    # was reported PROVEN -- a fail-OPEN in the one gate whose whole claim is
    # that executable code is byte-identical.
    #
    # ! This refuses on the delimiter's PRESENCE, not on parity: parity is what
    # the per-line lexer already cannot compute, so trusting it here would be
    # the same mistake one layer up. A proof that refuses costs a report; a
    # proof that lies costs the claim.
    if any(q in text for q in lang.spanning_quotes):
        return None

    lines = text.splitlines()
    # Pre-seed every line as itself; a paragraph below either drops its entry
    # (None) or replaces it with the code prefix it proved survives.
    kept: dict[int, str | None] = {i + 1: ln.rstrip() for i, ln in enumerate(lines)}
    for paragraph in paragraphs:
        for offset, n in enumerate(range(paragraph.start, paragraph.end + 1)):
            if n not in kept or offset >= len(paragraph.raw_lines):
                return None  # a paragraph naming a line this text does not have
            actual = lines[n - 1].rstrip()
            stored = paragraph.raw_lines[offset]
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


def code_fingerprint(text: str, path: Path) -> tuple[str, str]:
    """A value equal for two texts exactly when their executable code matches.

    Args:
        text: the file's contents.
        path: used only for its suffix, to pick which comparison runs.

    Returns:
        `(kind, fingerprint)`. `kind` is "ast", "stripped" or "unprovable"; an
        unprovable file carries an empty fingerprint and must never be reported
        as proven.
    """
    if path.suffix.lower() in (".py", ".pyi"):
        try:
            return "ast", ast.dump(_blank_docstrings(ast.parse(text)))
        except SyntaxError:
            pass  # fall through to the stripped compare; a broken parse proves nothing
    stripped = _without_comments(text, path)
    if stripped is None:
        return "unprovable", ""
    if not stripped.strip() and text.strip():
        # An all-comment file reaches here STRIPPED to nothing while the source
        # held text. `"" == ""` would "prove" any two such files identical
        # whatever code either one carried.
        return "unprovable", ""
    return "stripped", stripped


def dominant_ending(text: str) -> str:
    """Which line ending this text mostly uses: "crlf", "lf" or "none"."""
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    if crlf == 0 and lf == 0:
        return "none"
    return "crlf" if crlf >= lf else "lf"


def _spec(ref: str, rel: str) -> str:
    """The `git show` argument, built in ONE place so a failure can quote it.

    !! `./` MATTERS. `git show <rev>:<path>` resolves the path against the
    TOP OF THE WORKTREE, not against `-C`'s directory, so running the stage-7b
    gate with `--repo` on a package subdirectory made every path print
    "UNPROVABLE ... new file, or bad ref" and exit 1 -- blaming a bad ref for a
    path-prefix bug. A leading `./` makes it cwd-relative, which is what every
    sibling script already assumes.

    !! The failure message then read `no <base>:<rel>` -- a spec git was never
    asked for, and one that resolves DIFFERENTLY from the one that failed. It
    put the same misdirection back for exactly the case the `./` fixed, so both
    callers now read the spec from here.
    """
    return f"{ref}:./{rel}"


def _show(repo: Path, ref: str, rel: str) -> str | None:
    """`git show <ref>:./<rel>`, or None when git cannot produce it."""
    try:
        got = git(repo, "show", _spec(ref, rel))
    except GIT_ERRORS:
        return None
    return got.stdout if got.returncode == 0 else None


def _sibling(
    repo: Path, target: Path, edited: set[Path], tracked: list[str]
) -> Path | None:
    """A READABLE tracked file beside `target` that WRITE did not edit.

    Skips a candidate this process cannot itself read as UTF-8 text: a binary
    or non-UTF-8 sibling is unusable as a line-ending reference, and committing
    to the first NAME in the directory disabled the check where trying the next
    tracked file would have answered.

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
            read_raw(cand)
        except READ_ERRORS:
            continue
        return cand
    return None


def main() -> int:
    """Prove every named path, and report what could not be proven."""
    # UTF-8 with replacement, so an em-dash in someone's docstring still prints
    # on a console whose encoding lacks it.
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
            spec = _spec(args.base, rel)
            print(f"UNPROVABLE {rel}: no {spec} -- new file, or bad ref")
            failures += 1
            continue
        try:
            after = target.read_text(encoding="utf-8")
        except READ_ERRORS as e:
            print(f"FAIL      {rel}: {type(e).__name__}")
            failures += 1
            continue

        kind_b, fp_b = code_fingerprint(before, target)
        kind_a, fp_a = code_fingerprint(after, target)
        if kind_a == "unprovable" or kind_b == "unprovable":
            print(
                f"UNPROVABLE {rel}: prose could not be separated from code"
                " -- sameness NOT shown"
            )
            failures += 1
        elif kind_a != kind_b:
            print(
                f"FAIL      {rel}: proof kind changed ({kind_b} -> {kind_a}) "
                "-- likely broke Python syntax"
            )
            failures += 1
        elif fp_a != fp_b:
            print(f"FAIL      {rel}: executable code DIFFERS ({kind_a} proof)")
            failures += 1
        else:
            print(f"PROVEN    {rel}: reads the same ({kind_a})")

        sib = _sibling(repo, target, edited, tracked)
        if sib is None:
            print(f"UNCHECKED  {rel}: no readable untouched sibling -- line endings")
            unchecked += 1
        else:
            want = dominant_ending(read_raw(sib))
            got = dominant_ending(read_raw(target))
            # ! BOTH sides are guarded against "none". A single-line file with
            # no trailing newline has no ending to measure, so it reads "none"
            # and would FAIL against any CRLF sibling on ABSENT endings rather
            # than wrong ones.
            if want != "none" and got != "none" and got != want:
                print(f"FAIL      {rel}: line endings {got}, sibling {sib.name} {want}")
                failures += 1

    print()
    if failures:
        print(f"{failures} unproven. WRITE's claim does NOT hold.")
        return 1
    if unchecked:
        print(
            f"{len(args.paths)} paths proven; {unchecked} with line "
            "endings UNCHECKED (no readable untouched sibling to compare against)."
        )
    else:
        print(
            f"{len(args.paths)} paths proven: prose changed, the rest reads the same."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
