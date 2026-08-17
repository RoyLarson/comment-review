"""Refuse to ship a plugin file that will not parse on the oldest Python we claim.

`plugins/` is copied into other people's `.claude/` directories and is then
formatted by THEIR ruff config, not ours. A repo targeting a newer Python
rewrites shipped code into syntax its own interpreter accepts, and the failure
surfaces on a THIRD party's machine — never on the author's, never on the
formatter's.

This checks the one half we control: that what leaves this repository parses at
the floor. Run it in the gate, after `ruff format`.

    python scripts/check_shipped_syntax.py

Exits nonzero and names every file that fails.
"""

import ast
import sys
from pathlib import Path

# The oldest interpreter a shipped file must parse on. Not a packaging floor --
# there is no package here -- so it is stated once, in code, where the check
# that enforces it can read it.
FLOOR = (3, 11)
FLOOR_TEXT = ".".join(str(n) for n in FLOOR)

SHIPPED = "plugins"

# ⚠ A tuple literal in an `except` clause is the known regression: under
# `target-version = "py314"` a formatter rewrites `except (A, B):` into PEP
# 758's unparenthesised form, which `ast.parse` at the floor then rejects.
# Binding the tuple to a NAME leaves nothing to rewrite. Found in the shipped
# census script and two eval scripts on 2026-08-14, after a `noqa` had already
# failed to hold it.
ROOT = Path(__file__).resolve().parent.parent

# Bound to a name for the same reason the shipped file does it — a checker that
# uses the construct it refuses is one formatter run from being the defect.
READ_ERRORS = (OSError, UnicodeDecodeError)


def runtime_defects(src: str) -> list[str]:
    """Constructs that PARSE at the floor and fail there at RUNTIME.

    `ast.parse(feature_version=...)` validates syntax and nothing else, so a
    file can pass it and still raise on the interpreter it claims to support.
    Both shapes below are ordinary expressions to the parser at any version.
    """
    out: list[str] = []
    tree = ast.parse(src)
    # ⚠⚠ FORWARD REFERENCES IN ANNOTATIONS. Python 3.14 evaluates annotations
    # lazily (PEP 649), so a parameter annotated with a class defined LOWER in
    # the file imports cleanly on a modern interpreter and raises `NameError` at
    # IMPORT time on the floor. Found 2026-08-17 in this repo's own shipped
    # code, the day `from __future__ import annotations` came out: two helpers
    # annotated `Finding` above the class that defines it. The tests passed,
    # this check passed, and the file could not have been imported at 3.11.
    defined_at = {
        n.name: n.lineno
        for n in ast.walk(tree)
        if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }
    # ⚠ The future import restores lazy evaluation at the floor, so a file
    # carrying it is exempt. Nothing shipped here carries it any more.
    lazy = any(
        isinstance(n, ast.ImportFrom)
        and n.module == "__future__"
        and any(a.name == "annotations" for a in n.names)
        for n in tree.body
    )
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not lazy:
            annotations = [a.annotation for a in n.args.args if a.annotation]
            if n.returns is not None:
                annotations.append(n.returns)
            for ann in annotations:
                for name in (x.id for x in ast.walk(ann) if isinstance(x, ast.Name)):
                    if defined_at.get(name, 0) > n.lineno:
                        out.append(
                            f"line {n.lineno}: {n.name}() annotates {name}, defined "
                            f"at line {defined_at[name]} — NameError on import"
                        )
        if not isinstance(n, ast.Call):
            continue
        fn = getattr(n.func, "id", "")
        if fn not in ("isinstance", "issubclass") or len(n.args) < 2:
            continue
        # ⚠ Reported against the FLOOR, not against 3.9. This read "TypeError
        # before 3.10" while `FLOOR` is 3.11, where the idiom works — a gate
        # refusing a valid construct for a reason about an interpreter this
        # repo does not claim to support.
        if (
            FLOOR < (3, 10)
            and isinstance(n.args[1], ast.BinOp)
            and isinstance(n.args[1].op, ast.BitOr)
        ):
            out.append(
                f"line {n.lineno}: PEP 604 union inside {fn}() — "
                f"TypeError on Python {FLOOR_TEXT}, invisible to a syntax check"
            )
    return out


def main() -> int:
    """Parse every shipped .py at the floor; report each failure."""
    files = sorted((ROOT / SHIPPED).rglob("*.py"))
    if not files:
        print(f"error: no .py files under {SHIPPED}/ -- wrong root?", file=sys.stderr)
        return 2

    bad: list[tuple[Path, str]] = []
    for f in files:
        try:
            src = f.read_text(encoding="utf-8")
            ast.parse(src, feature_version=FLOOR)
        except SyntaxError as e:
            bad.append((f, f"line {e.lineno}: {e.msg}"))
            continue
        except READ_ERRORS as e:
            bad.append((f, f"unreadable: {e}"))
            continue
        bad.extend((f, why) for why in runtime_defects(src))

    for f, why in bad:
        print(f"{f.relative_to(ROOT)}: {why}", file=sys.stderr)

    if bad:
        # ⚠ FILES, not findings. `len(bad)` counted entries, so three defects in
        # one file reported "3 of 8 shipped files" — and "do not parse" names a
        # cause this check no longer only looks for.
        print(
            f"\n{len({f for f, _ in bad})} of {len(files)} shipped files will not "
            f"LOAD on Python {FLOOR_TEXT}.\nThese ship into other people's "
            "repositories; the break lands on a third party.",
            file=sys.stderr,
        )
        return 1

    print(f"{len(files)} shipped files parse on Python {FLOOR_TEXT}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
