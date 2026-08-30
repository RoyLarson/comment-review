r"""B2 -- STAGE: put a case's paths, at its START hash, into the tree to be graded.

A case pins a START and an END (`decision-log.md Vocabulary: #31`). What a role
reads is START, and it must read the case rather than the repository: everything
the case did not name stays behind, or a role can resolve a reference the case
never handed it and the grade stops being about the case.

!! IT WRITES THE STORED BLOB, AND `git archive` DOES NOT. MEASURED 2026-08-29 on
this repo: `git archive` applies the checkout filter, so with `core.autocrlf=true`
it returned CRLF where `git show` returned LF -- the first byte-identity test
failed at index 3, `b'\r' != b'\n'`. B2 is graded against `git show`, so the
staging has to read the object store itself.

! AND THE STAGED TREE IS THEN THE SAME BYTES ON EVERY MACHINE, which a checkout
filter cannot promise: two runs of one case on two platforms would otherwise
stage different files and be graded as though they had not.

! THE READ AND THE CHECK USE DIFFERENT COMMANDS ON PURPOSE -- `git cat-file blob`
here, `git show` in the test. A check that issued the same command as the code it
checks could only agree with itself, which is `docs/gates.md`'s whole subject.

!! IT TAKES A CASE ROW AS OF 2026-08-30, and took only a hash and a path list
before. The note that stood here said so and named the reason -- *"no row carries
`start`/`end` yet"* -- which stopped being true when the four keyed rows landed
in `evals/test-cases.jsonl`.

!! IT STAGES; IT DOES NOT RUN. What EXECUTES a row -- a script in this repo or
`skill-creator` -- is unruled, and is T18 of
`the-harness-cannot-run-the-system-it-grades`, which carries a `*` because the
answer is Roy's. **This module deliberately stops at the artifacts**: the START
tree a role reads, and the END diff a grader keys against. Producing a
`findings.md` from that tree is the step in between, and it is not here.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys


class PathNotAtCommit(Exception):
    """A case named a path that does not exist at the commit being staged."""


def _exists_at(repo: pathlib.Path, commit: str, path: str) -> bool:
    return (
        subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", f"{commit}:{path}"],
            capture_output=True,
        ).returncode
        == 0
    )


def stage(
    repo: pathlib.Path, commit: str, paths: list[str], dest: pathlib.Path
) -> list[str]:
    """Write `paths` as they stood at `commit` into `dest`, and nothing else.

    ! EVERY PATH IS CHECKED BEFORE ANY IS WRITTEN, so a case that names one bad
    path leaves no half-staged tree behind -- and the refusal names all of them
    at once rather than one per re-run.

    ! THE REFUSAL NAMES THE COMMIT. The likely mistake is a case written today
    against an older START, where the path exists on disk and on HEAD and simply
    was not there yet; "no such file" would send a reader to the wrong question.
    """
    absent = [path for path in paths if not _exists_at(repo, commit, path)]
    if absent:
        raise PathNotAtCommit(
            f"not in {commit[:7]}: {', '.join(sorted(absent))}"
        )

    for path in paths:
        blob = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "blob", f"{commit}:{path}"],
            capture_output=True,
            check=True,
        )
        written = dest / path
        written.parent.mkdir(parents=True, exist_ok=True)
        written.write_bytes(blob.stdout)

    return sorted(paths)


class NoSuchCase(Exception):
    """No row in the case file carries the id asked for."""


class NotKeyed(Exception):
    """The row exists and pins one commit, so it has no START to stage."""


def row_for(cases: pathlib.Path, case_id: str) -> dict:
    """The row with this id, or a refusal that lists what is on offer.

    ! THE REFUSAL NAMES EVERY ID, because the likely mistake is a typo or a
    half-remembered slug, and a bare "not found" makes the caller open the file
    to find out what they meant.

    ! A ROW PINNING ONE `commit` IS REFUSED SEPARATELY. Six rows do -- they
    record a defect an observed run made, not a START/END pair -- so "no such
    case" would be the wrong answer for them; they are cases, and they have no
    START.
    """
    rows = [
        json.loads(line)
        for line in cases.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    named = [row for row in rows if row["id"] == case_id]
    if not named:
        offered = "\n  ".join(sorted(row["id"] for row in rows))
        raise NoSuchCase(f"no case {case_id!r}. The file holds:\n  {offered}")

    row = named[0]
    if "start" not in row or "end" not in row:
        raise NotKeyed(
            f"{case_id} pins a single commit and has no START/END pair to stage."
        )
    return row


def end_diff(repo: pathlib.Path, row: dict) -> str:
    """END's diff over the case's own paths -- the answer key, and nothing else.

    ! SCOPED TO THE ROW'S PATHS. A commit may touch files the case does not name
    -- both `machine`-area cases have a `plugins/` copy of the same edit -- and a
    key carrying changes the role was never shown grades it for missing them.
    """
    return subprocess.run(
        ["git", "-C", str(repo), "diff", row["start"], row["end"], "--", *row["files"]],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def main(argv: list[str] | None = None) -> int:
    """Stage one case by id, and print what still has to happen to grade it."""
    here = pathlib.Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Stage one eval case's START tree and END diff.",
    )
    parser.add_argument("--case", required=True, help="a row id in the case file")
    parser.add_argument("--repo", type=pathlib.Path, default=here.parent)
    parser.add_argument(
        "--cases", type=pathlib.Path, default=here / "test-cases.jsonl"
    )
    parser.add_argument(
        "--out",
        type=pathlib.Path,
        required=True,
        help="destination directory; must not exist",
    )
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")

    # ! REFUSED BEFORE ANYTHING IS WRITTEN, the same order `stage` uses on paths
    # and `reread.inspect` uses on arguments: a fault found halfway leaves a
    # directory a caller then has to reason about.
    if args.out.exists():
        print(f"REFUSED  --out: {args.out} exists", file=sys.stderr)
        return 1
    try:
        row = row_for(args.cases, args.case)
    except (NoSuchCase, NotKeyed) as refused:
        print(f"REFUSED  {refused}", file=sys.stderr)
        return 1

    start_tree = args.out / "start"
    try:
        staged = stage(args.repo, row["start"], row["files"], start_tree)
    except PathNotAtCommit as refused:
        print(f"REFUSED  {refused}", file=sys.stderr)
        return 1

    key = args.out / "end.diff"
    key.write_text(end_diff(args.repo, row), encoding="utf-8")
    (args.out / "case.json").write_text(
        json.dumps(row, indent=2, sort_keys=True), encoding="utf-8"
    )

    sites = row.get("sites", [])
    print(f"STAGED   {row['id']}")
    print(f"  start  {row['start'][:8]}  {len(staged)} file(s) -> {start_tree}")
    print(f"  end    {row['end'][:8]}  key -> {key} ({len(key.read_text()) } bytes)")
    print(f"  roles  {', '.join(row['roles'])}")
    print(f"  sites  {len(sites)} keyed")
    for path in staged:
        print(f"         {path}")
    # !! WHAT IS MISSING IS NOT A FLAG, IT IS T18. A grade needs a `findings.md`
    # that a RUN filed, and what executes a row is unruled -- so the findings
    # path is left as a placeholder rather than implying one exists.
    print(f"\n  NEXT   a run over {start_tree.name}/ must file a findings.md.")
    print("         What executes a row is T18, and unruled.")
    print("\n  THEN, AND ONLY BY ROY:")
    print("    uv run python evals/reread.py \\")
    print("      --findings <the run's findings.md> \\")
    print(f"      --under-review {start_tree} \\")
    print(f"      --start {row['start']} --end {row['end']} \\")
    print(f"      --end-diff {key} \\")
    print(f"      --arm with_skill --eval-id {row['id']} \\")
    print(f"      --out {args.out / 'comparison.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
