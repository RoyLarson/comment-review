"""Materialise the corpora in `corpora.toml` at their pinned refs.

    python scripts/fetch_corpora.py [--only NAME ...] [--list] [--clean NAME ...]

Nothing is copied into this repository. A `local` corpus becomes a git worktree
of a repo already on the machine; a `public` one is a shallow clone at a tag,
optionally sparse. Both land under `corpora/<name>/`, which is gitignored --
this repo carries the MANIFEST, not the code.

⚠ Every corpus is pinned, and a fetch that lands on a different ref than the
manifest names is a hard failure rather than a warning. A moving corpus makes a
regression indistinguishable from the corpus having changed underneath the
measurement.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

# The script lives in scripts/; the manifest and the fetched trees live in
# corpora/. Anchored on the repo root rather than on the script so it can be
# invoked from anywhere -- a corpus tool that only works from one cwd is a
# corpus tool nobody runs from CI.
ROOT = Path(__file__).resolve().parents[1]
CORPORA = ROOT / "corpora"
MANIFEST = CORPORA / "corpora.toml"


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a command and capture it; the caller decides what a failure means."""
    return subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _why(r: subprocess.CompletedProcess) -> str:
    """The last line of a failure, which is the line that says what broke."""
    return r.stderr.strip().splitlines()[-1] if r.stderr else "?"


def head_of(path: Path) -> str:
    """The commit a checkout is actually sitting on."""
    return run("git", "-C", str(path), "rev-parse", "HEAD").stdout.strip()


def fetch_local(c: dict, dest: Path) -> str:
    """A worktree of a repo already on disk — pinned, and nothing duplicated."""
    src = Path(c["source"])
    if not (src / ".git").exists():
        return f"SKIP  {c['name']}: {src} is not a git repo"
    if dest.exists():
        return f"have  {c['name']} @ {head_of(dest)[:8]}"
    r = run("git", "-C", str(src), "worktree", "add", "--detach", str(dest), c["ref"])
    if r.returncode:
        return f"FAIL  {c['name']}: {_why(r)}"
    return f"ok    {c['name']} @ {head_of(dest)[:8]} (worktree)"


def fetch_public(c: dict, dest: Path) -> str:
    """A shallow clone at a tag. Sparse where the manifest names subtrees."""
    if dest.exists():
        return f"have  {c['name']} @ {head_of(dest)[:8]}"
    sparse = c.get("sparse")
    # ⚠ depth 1 gives a TREE and no history, which is enough to census but makes
    # `git blame` impossible -- so any corpus used for the trailer split must
    # declare a depth. 0 means full.
    depth = c.get("depth", 1)
    args = ["git", "clone", "--branch", c["ref"]]
    if depth:
        args += ["--depth", str(depth)]
    if sparse:
        args += ["--filter=blob:none", "--sparse"]
    r = run(*args, c["source"], str(dest))
    if r.returncode:
        return f"FAIL  {c['name']}: {_why(r)}"
    if sparse:
        s = run("git", "-C", str(dest), "sparse-checkout", "set", *sparse)
        if s.returncode:
            return f"FAIL  {c['name']}: sparse-checkout — {s.stderr.strip()}"
    return f"ok    {c['name']} @ {c['ref']} ({'sparse ' if sparse else ''}clone)"


def main() -> int:
    """Materialise every corpus in the manifest, and verify each pin landed."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", nargs="*", default=None, help="fetch just these")
    ap.add_argument("--list", action="store_true", help="show the manifest and stop")
    ap.add_argument("--clean", nargs="*", default=None, help="remove these first")
    args = ap.parse_args()

    corpora = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))["corpus"]
    if args.only:
        corpora = [c for c in corpora if c["name"] in args.only]

    if args.list:
        print(f"{'name':22s} {'kind':7s} {'expect':7s} {'style':10s} ref")
        for c in corpora:
            print(
                f"{c['name']:22s} {c['kind']:7s} {c['expect']:7s} "
                f"{c.get('style', '?'):10s} {c['ref']}"
            )
        print(
            "\n`expect` is the prediction the corpus set exists to test: a heavily\n"
            "reviewed project should yield fewer findings per block than a solo one.\n"
            "If that gradient does not appear, the detector is measuring noise."
        )
        return 0

    for name in args.clean or []:
        d = CORPORA / name
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
            print(f"rm    {name}")

    bad = 0
    for c in corpora:
        dest = CORPORA / c["name"]
        line = fetch_local(c, dest) if c["kind"] == "local" else fetch_public(c, dest)
        print(line)
        if line.startswith("FAIL"):
            bad += 1
            continue
        # The pin is the whole point, so verify it landed rather than trusting
        # the clone: a tag can move, and --branch silently accepts a branch.
        if dest.exists():
            got = head_of(dest)
            want = c["ref"]
            resolved = run(
                "git", "-C", str(dest), "rev-parse", want + "^{commit}"
            ).stdout.strip()
            if resolved and got and not got.startswith(want) and got != resolved:
                print(f"      ⚠ PIN MISMATCH: manifest {want}, checkout {got[:8]}")
                bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
