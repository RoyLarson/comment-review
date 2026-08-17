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

import argparse
import shutil
import stat
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


def _force_writable(func, path, _exc) -> None:
    """`rmtree` error hook: clear the read-only bit and retry once.

    ⚠ `onerror`, not `onexc`. `onexc` arrives in 3.12 and this repo's floor is
    3.11 -- a `TypeError` on the interpreter the plugin claims. Caught by
    running it; no test exercises `--clean`.

    ⚠ Git writes `.git/objects/pack/*.pack` read-only, which is what makes
    `shutil.rmtree` fail on Windows. `ignore_errors=True` turned that into a
    silent no-op, so `--clean` printed `rm <name>` over a tree that was still
    there.
    """
    try:
        path_ = Path(path)
        path_.chmod(stat.S_IWRITE | stat.S_IREAD)
        func(path)
    except OSError as e:
        print(f"      ⚠ could not remove {path}: {e}")


def head_of(path: Path) -> str:
    """The commit a checkout is actually sitting on, or "" if git could not say.

    ⚠⚠ A caller must not read "" as a hash. This ignored `returncode`, so a
    failed `rev-parse` -- a half-deleted corpus, `rmtree` having silently
    no-opped on read-only git objects -- returned "" and the pin-mismatch guard
    short-circuited to False. The next run printed `have <name> @ ` with an
    empty hash, skipped the pin check, and exited 0: a broken corpus reporting
    as correctly pinned.
    """
    r = run("git", "-C", str(path), "rev-parse", "HEAD")
    return r.stdout.strip() if r.returncode == 0 else ""


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
    # ⚠⚠ A Windows console is cp1252 and this module's own docstring carries
    # U+26A0, so `--help` died inside `argparse.print_help` before doing
    # anything -- and the same fault hit mid-run, after some corpora were
    # already cloned. `find_llm_repos.py` carries this guard; the gate that
    # would have caught the gap only globs the shipped `plugins/` scripts.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
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

    by_name = {c["name"]: c for c in corpora}
    for name in args.clean or []:
        d = CORPORA / name
        if not d.exists():
            continue
        # ⚠⚠ A `local` corpus is a git WORKTREE, and its registration lives in
        # the SOURCE repo's `.git/worktrees/`. Deleting the directory alone left
        # a stale entry, so the documented refetch -- `--clean X --only X` --
        # then failed in `fetch_local` with git's "missing but already
        # registered working tree". Deregister first, then remove.
        c = by_name.get(name)
        if c and c.get("kind") == "local":
            src = Path(c["source"])
            run("git", "-C", str(src), "worktree", "remove", "--force", str(d))
            run("git", "-C", str(src), "worktree", "prune")
        if d.exists():
            # ⚠⚠ `ignore_errors` HID A FAILED DELETE. Git marks pack files
            # read-only, so on Windows `rmtree` cannot remove
            # `.git/objects/pack/*.pack` and left the tree in place -- while
            # the line below printed `rm <name>` regardless. The documented
            # refetch then found `dest.exists()`, returned `have ...`, and
            # never refetched anything. `onexc` clears the read-only bit and
            # retries; what still fails is REPORTED.
            shutil.rmtree(d, onerror=_force_writable)
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
            # ⚠⚠ AN UNREADABLE CHECKOUT IS A FAILURE, not a skipped check.
            # `got` is "" when `rev-parse` failed, and `and got` then
            # short-circuited the whole guard -- so a directory that exists but
            # is no longer a usable git repo printed `have <name> @ ` with an
            # empty hash, had its pin unchecked, and exited 0 reporting a
            # correctly-pinned corpus. Fixing `head_of` to return "" honestly
            # moved where the "" came from; this is the caller that swallowed it.
            if not got:
                print(f"      ⚠ UNREADABLE: {dest} is not a usable git checkout")
                bad += 1
            elif resolved and not got.startswith(want) and got != resolved:
                print(f"      ⚠ PIN MISMATCH: manifest {want}, checkout {got[:8]}")
                bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
