"""Refuse to ship a plugin file that will not parse on the oldest Python we claim.

`plugins/` is copied into other people's `.claude/` directories and is then
formatted by THEIR ruff config, not ours. A repo targeting a newer Python
rewrites shipped code into syntax its own interpreter accepts, and the failure
surfaces on a THIRD party's machine -- never on the author's, never on the
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

# ! A tuple literal in an `except` clause is the known regression: under
# `target-version = "py314"` a formatter rewrites `except (A, B):` into PEP
# 758's unparenthesised form, which `ast.parse` at the floor then rejects.
# Binding the tuple to a NAME leaves nothing to rewrite. Found in the shipped
# census script and two eval scripts on 2026-08-14, after a `noqa` had already
# failed to hold it.
ROOT = Path(__file__).resolve().parent.parent

# Bound to a name for the same reason the shipped file does it -- a checker that
# uses the construct it refuses is one formatter run from being the defect.
READ_ERRORS = (OSError, UnicodeDecodeError)


def _annotations(tree: ast.AST) -> list[tuple[int, str, ast.expr]]:
    """Every annotation the floor EVALUATES, as `(line, where, expression)`.

    !! ALL SIX POSITIONS, and the first version of this checked two. It read
    `args.args` and `returns` only, so a keyword-only parameter, `*args`,
    `**kwargs`, a positional-only parameter, and a dataclass field annotation
    were all unexamined -- and a dataclass field is exactly how this repo
    declares its records.

    ! A STRING annotation is skipped: quoting is the sanctioned way to name a
    type that is not bound at runtime, and it is what the fix looks like.
    """
    out: list[tuple[int, str, ast.expr]] = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a = n.args
            slots = [*a.posonlyargs, *a.args, *a.kwonlyargs, a.vararg, a.kwarg]
            for arg in slots:
                if arg is not None and arg.annotation is not None:
                    out.append((n.lineno, f"{n.name}()", arg.annotation))
            if n.returns is not None:
                out.append((n.lineno, f"{n.name}()", n.returns))
        elif isinstance(n, ast.AnnAssign) and n.annotation is not None:
            label = getattr(n.target, "id", "a field")
            out.append((n.lineno, str(label), n.annotation))
    return [(ln, w, a) for ln, w, a in out if not isinstance(a, ast.Constant)]


def runtime_defects(src: str) -> list[str]:
    """Constructs that PARSE at the floor and fail there at RUNTIME.

    `ast.parse(feature_version=...)` validates syntax and nothing else, so a
    file can pass it and still raise on the interpreter it claims to support.
    """
    out: list[str] = []
    tree = ast.parse(src)
    # ! The future import restores lazy evaluation at the floor, so a file
    # carrying it is exempt from everything below.
    if any(
        isinstance(n, ast.ImportFrom)
        and n.module == "__future__"
        and any(a.name == "annotations" for a in n.names)
        for n in tree.body
    ):
        return out

    # !! AN ANNOTATION MAY NAME ONLY WHAT IS BOUND AT RUNTIME. Python 3.14
    # evaluates annotations lazily (PEP 649), so a name that does not exist yet
    # -- or never exists -- is fine on a modern interpreter and raises
    # `NameError` AT IMPORT on the floor.
    #
    # Two ways to get it wrong, and this repo has now shipped both:
    #   2026-08-17  two helpers annotated `Finding` twelve lines ABOVE the class
    #   2026-08-17  `annotate.py` annotated `Block`, imported under
    #               TYPE_CHECKING only -- which took census, prove_unchanged and
    #               verdicts down with it, four of eight shipped scripts, while
    #               this gate reported success
    defined_at = {
        n.name: n.lineno
        for n in ast.walk(tree)
        if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }
    type_only: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.If) and "TYPE_CHECKING" in ast.dump(n.test):
            for sub in ast.walk(n):
                if isinstance(sub, (ast.Import, ast.ImportFrom)):
                    type_only.update(
                        a.asname or a.name.split(".")[0] for a in sub.names
                    )

    for line, where, ann in _annotations(tree):
        for name in {x.id for x in ast.walk(ann) if isinstance(x, ast.Name)}:
            if name in type_only:
                out.append(
                    f"line {line}: {where} annotates {name}, which is imported"
                    " under TYPE_CHECKING and is NOT bound at runtime -- quote it"
                )
            elif defined_at.get(name, 0) > line:
                out.append(
                    f"line {line}: {where} annotates {name}, defined at line "
                    f"{defined_at[name]} -- NameError on import"
                )

    # ! PEP 604 inside isinstance()/issubclass() is a TypeError before 3.10.
    # `FLOOR` is 3.11, so this cannot fire today and is kept as a guard for a
    # floor that drops -- the summary and the docstring must not claim otherwise.
    if FLOOR >= (3, 10):
        return out
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        fn = getattr(n.func, "id", "")
        if fn not in ("isinstance", "issubclass") or len(n.args) < 2:
            continue
        if isinstance(n.args[1], ast.BinOp) and isinstance(n.args[1].op, ast.BitOr):
            out.append(
                f"line {n.lineno}: PEP 604 union inside {fn}() -- "
                f"TypeError on Python {FLOOR_TEXT}, invisible to a syntax check"
            )
    return out


def main() -> int:
    """Parse every shipped .py at the floor; report each failure."""
    # ! A Windows console is cp1252; one non-ASCII glyph in this program's own
    # output kills the run. Every CLI in this repo carries this, and
    # `tests/test_shipped_cli_encoding.py` is the gate -- it globbed only the
    # shipped `plugins/` scripts until 2026-08-17, which is how four of these
    # went without it.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
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
        # ! FILES, not findings. `len(bad)` counted entries, so three defects in
        # one file reported "3 of 8 shipped files" -- and "do not parse" names a
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
    sys.exit(main())
