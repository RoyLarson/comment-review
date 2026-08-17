"""Ground truth for the SKILL.md search: which PROSE blocks changed, and where.

A candidate skill is scored on how much of this it rediscovers in one pass, so
the target set must contain only prose. A hunk that changed code is not
something a comment reviewer should have proposed.

    uv run python ground_truth.py <base-ref> <head-ref> [--out gt.json]

Emits {"path": [[start, end], ...]} in BASE-ref line numbers, because a
reviewer runs against the base tree and reports positions there.
"""

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def prose_lines(text: str) -> set[int]:
    """Line numbers that are a `#` comment or inside a docstring."""
    out: set[int] = set()
    for i, raw in enumerate(text.splitlines(), 1):
        if raw.strip().startswith("#"):
            out.add(i)
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return out
    for node in ast.walk(tree):
        if not isinstance(
            node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
        ):
            continue
        body = getattr(node, "body", None)
        if not body:
            continue
        first = body[0]
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            out.update(range(first.lineno, (first.end_lineno or first.lineno) + 1))
    return out


def git(*args: str, must_work: bool = False) -> str:
    """Run a git command and return its stdout.

    ⚠⚠ A FAILURE WAS INDISTINGUISHABLE FROM NO OUTPUT. The return code was
    discarded, so a mistyped or unfetched ref made `diff --name-only` return ""
    -- no files, an empty truth set, `{}` written to gt.json, and exit 0.
    `score.py` then had `total == 0`, which hardcodes recall to 0.0 for EVERY
    candidate, so a whole GA generation ranked on nothing with no sign of it in
    stdout or the exit status. Measured 2026-08-17.

    Args:
        *args: the git subcommand and its arguments.
        must_work: raise `RuntimeError` on a nonzero exit rather than returning
            "". Set where an empty result would be read as an answer.
    """
    r = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if must_work and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip() or 'failed'}")
    return r.stdout


def main() -> int:
    """Emit the changed-prose block map for the given ref range."""
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("head")
    ap.add_argument("--out", default="gt.json")
    ap.add_argument("--only", default="", help="substring a path must contain")
    args = ap.parse_args()

    try:
        # ⚠ `splitlines`, not `split`: a path holding a space became two
        # fragments whose `git show` then failed and was silently skipped.
        changed = git(
            "diff", "--name-only", args.base, args.head, "--", "*.py", must_work=True
        ).splitlines()
    except RuntimeError as e:
        # ⚠⚠ REFUSE rather than write an empty oracle. `{}` in gt.json makes
        # `score.py` report recall 0.0 for every candidate in the generation,
        # which reads as "they all found nothing" rather than "the refs were
        # wrong".
        print(f"ground_truth: {e}", file=sys.stderr)
        return 2
    files = [f for f in changed if args.only in f]
    truth: dict[str, list[list[int]]] = {}

    for path in files:
        before = git("show", f"{args.base}:{path}")
        if not before.strip():
            continue  # added by the branch: nothing in the base to review
        base_prose = prose_lines(before)
        diff = git("diff", "-U0", args.base, args.head, "--", path)
        hit: set[int] = set()
        for line in diff.splitlines():
            m = HUNK.match(line)
            if not m:
                continue
            start, count = int(m.group(1)), int(m.group(2) or 1)
            # A pure insertion reports count 0 at the line it FOLLOWS.
            #
            # ⚠⚠ The anchor survived only when that preceding line happened to
            # be prose ALREADY, so an added comment after `def f():` produced an
            # empty truth set -- the skill's whole `add` verdict was invisible
            # to the oracle, and a candidate correctly proposing one was
            # PENALISED on precision. An insertion is now kept whether or not
            # its anchor is prose; every other hunk still requires it, because
            # a modified line that was not prose is not a prose defect.
            if count == 0:
                hit.add(start)
                continue
            span = range(start, start + count)
            hit.update(n for n in span if n in base_prose)
        if not hit:
            continue
        blocks, run = [], []
        for n in sorted(hit):
            if run and n - run[-1] > 2:  # a 2-line gap still reads as one block
                blocks.append([run[0], run[-1]])
                run = []
            run.append(n)
        if run:
            blocks.append([run[0], run[-1]])
        truth[path] = blocks

    Path(args.out).write_text(json.dumps(truth, indent=1), encoding="utf-8")
    n_blocks = sum(len(v) for v in truth.values())
    print(f"{len(truth)} files, {n_blocks} changed prose blocks -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
