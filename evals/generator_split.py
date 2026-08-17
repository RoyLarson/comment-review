"""Split a corpus's prose defects by WHO WROTE THE COMMIT that introduced them.

    python evals/generator_split.py <corpus-dir> [paths...]

The corpus set was built around curation level -- a heavily reviewed project
should carry fewer defects per block than a solo one. That is probably the wrong
variable. The reference corpus's profile (87 of 303 blocks over a six-line cap,
an 85-line comment run) does not appear in an older project by the same author,
which points at the GENERATOR rather than at the author or the review culture.

This measures that directly, and inside one repository, so author, domain,
reviewer and house style are all held constant. The only thing that varies is
whether the commit introducing a line carries a `Co-Authored-By: <assistant>`
trailer.

⚠ It is a correlation over commits, not an experiment. A trailer says an
assistant was involved, not that it wrote the prose; a human may have edited it
afterwards, and a block's lines can come from several commits. `mixed` blocks
are reported separately rather than forced into a bucket, and the line counts
are printed so a lopsided split is visible rather than averaged away.
"""

import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

SKILL = (
    Path(__file__).resolve().parents[1]
    / "plugins/comment-review/skills/comment-review/scripts"
)
sys.path.insert(0, str(SKILL))

import census  # noqa: E402  - the census is the skill's, not a second copy

# `Co-Authored-By: Claude`, `Assisted-by: ...`, `Generated with ...`. Broad on
# purpose: a false positive dilutes the contrast and understates the effect,
# which is the safe direction for a claim like this one.
#
# ⚠⚠ TWO SHAPES, because they are punctuated differently. A TRAILER is
# `Key: value` at the start of a line. The FOOTER is a sentence with no colon
# and no line start to anchor to — `🤖 Generated with [Claude Code](...)`, where
# an emoji is not `\s`. One pattern demanding both `^\s*` and `\s*:` matched
# only the trailer, so a commit carrying just the footer was filed under
# `human` — biasing the split against the very effect this module measures.
# Measured 2026-08-17: both real footer forms returned False.
# ⚠⚠ A LEADING BOUNDARY TOO. With `\b` only on the right, `ai` matched the tail
# of ordinary words: `Co-authored-by: Priya Desai` and `Nikolai Petrov` both
# read as assisted, filing a HUMAN co-author's whole commit under `assisted` and
# moving its blocks out of `human`. The split then reports an authorship effect
# the data does not contain — which is the one failure this module cannot
# tolerate, since the effect is the whole measurement.
#
# ⚠ The comment below argues that false positives are the SAFE direction. That
# holds for over-matching a TOOL name, which only dilutes the contrast. It does
# not hold for matching a person, which moves real human prose into the other
# bucket and manufactures the result.
TOOLS = r"(?<![A-Za-z])(claude|copilot|gpt|codex|cursor|gemini|llm|ai)\b"
ASSISTED = re.compile(
    r"(?im)^\s*(co-authored-by|assisted-by)\s*:.*"
    + TOOLS
    + r"|generated[- ]with\b.*"
    + TOOLS
)


def git(repo: Path, *args: str) -> str:
    """Run git in `repo` and return stdout, or "" if it failed."""
    r = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return r.stdout if r.returncode == 0 else ""


def line_authors(repo: Path, path: str) -> dict[int, str]:
    """Line number -> commit sha, from one blame pass over the whole file."""
    out: dict[int, str] = {}
    blame = git(repo, "blame", "--porcelain", "--", path)
    for chunk in blame.splitlines():
        m = re.match(r"^([0-9a-f]{40}) \d+ (\d+) ?(\d+)?$", chunk)
        if m:
            sha, start, n = m.group(1), int(m.group(2)), int(m.group(3) or 1)
            for i in range(start, start + n):
                out[i] = sha
    return out


def assisted_shas(repo: Path, shas: set[str]) -> set[str]:
    """Which of these commits carry an assistant trailer. One log call."""
    if not shas:
        return set()
    hits: set[str] = set()
    for sha in shas:
        if ASSISTED.search(git(repo, "log", "-1", "--format=%B", sha)):
            hits.add(sha)
    return hits


def main() -> int:
    """Split the corpus's blocks by the authorship of the commits behind them."""
    # A Windows console is cp1252; one non-ASCII glyph in a report kills the run.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    repo = Path(sys.argv[1]).resolve()
    # Targets are relative to the CORPUS, not to the cwd you invoked from --
    # the corpus is the subject and the caller is somewhere else entirely.
    targets = [repo / p for p in sys.argv[2:]] or [repo]

    files = sorted({f for t in targets for f in census._walk(t)})
    known, _ = census.code_names([repo])
    paths = census.path_index(repo)

    buckets: dict[str, list] = defaultdict(list)
    notes: dict[str, Counter] = defaultdict(Counter)
    all_shas: set[str] = set()
    per_file: dict[str, dict[int, str]] = {}

    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        # ⚠⚠ Through `census_for`, which DISPATCHES ON THE LANGUAGE. This called
        # `blocks_stdlib` -- Python's `tokenize` plus `ast` -- on every file
        # `_walk` yields, and `_walk` filters on `BY_EXT`, i.e. all eleven
        # languages. A three-line `.yaml` raised `IndentationError` uncaught and
        # killed the whole run; the quieter cases are worse, because a `.rs` or
        # `.go` file was scanned for `#` comments only and contributed zero
        # prose blocks, deflating every bucket without a word. Any polyglot
        # corpus in `corpora.toml` hits this.
        lang = census.language_for(f)
        if lang is None:
            continue
        rel = f.relative_to(repo).as_posix() if f.is_absolute() else f.as_posix()
        per_file[rel] = line_authors(repo, rel)
        all_shas.update(per_file[rel].values())
        try:
            blocks = census.census_for(f, text, lang)
        except census.PARSE_ERRORS:
            # ⚠ A file this repo's own census would REFUSE is a gap in the
            # split, not a crash in it. Named, so the count is readable.
            notes["unparsed"][rel] += 1
            continue
        for b in blocks:
            if not b.text.strip():
                continue
            census.annotate(b, known, paths, repo)
            buckets["_pending"].append((rel, b))

    # ⚠ A SHALLOW CLONE SILENTLY CORRUPTS THIS. Blame attributes every line older
    # than the horizon to the graft commit, so one sha swallows most of the file
    # and the split measures clone depth instead of authorship. Measured: a
    # depth-2000 checkout put 1177 of one file's 1364 lines on the graft point,
    # which happened to carry a trailer, labelling the whole pre-existing
    # codebase "assisted". The numbers looked entirely reasonable.
    # ⚠⚠ ASK GIT, do not build the path. A `local` corpus is a WORKTREE, where
    # `.git` is a FILE pointing at the source repo's gitdir — so
    # `repo/.git/shallow` can never exist, and this guard was structurally dead
    # for exactly the corpora this script targets. The failure recorded above
    # would have gone unreported on every one of them.
    # ⚠⚠ `--git-common-dir`, not `--absolute-git-dir`. In a linked worktree the
    # absolute gitdir is `<main>/.git/worktrees/<name>`, and `shallow` lives in
    # the COMMON dir — so the first fix pointed at a path that never holds it,
    # for exactly the corpora it was rewritten to cover. It is repo-relative
    # when it answers `.git`, so it is resolved against the repo.
    common = git(repo, "rev-parse", "--git-common-dir").strip() or ".git"
    gitdir = Path(common) if Path(common).is_absolute() else repo / common
    shallow = gitdir / "shallow"
    grafts = (
        set(shallow.read_text(encoding="utf-8").split()) if shallow.exists() else set()
    )
    if grafts:
        swallowed = sum(1 for m in per_file.values() for s in m.values() if s in grafts)
        total_lines = sum(len(m) for m in per_file.values()) or 1
        pct = 100 * swallowed / total_lines
        print(
            f"⚠ SHALLOW CLONE: {pct:.0f}% of blamed lines land on a graft commit.\n"
            f"  Authorship is unknowable beyond the horizon; this split is invalid.\n"
            f"  Refetch with depth = 0 in corpora.toml.\n"
        )
        if pct > 10:
            return 2

    aid = assisted_shas(repo, all_shas)

    # ⚠ `dict.pop` does NOT consult a defaultdict's factory, so this raised
    # KeyError when nothing was censused -- a path argument matching no file, or
    # a corpus whose files were all unreadable. An empty split is a result.
    for rel, b in buckets.pop("_pending", []):
        blame = per_file.get(rel, {})
        got = [blame.get(i) for i in range(b.start, b.end + 1) if blame.get(i)]
        if not got:
            key = "unknown"
        else:
            a = sum(1 for s in got if s in aid)
            key = "assisted" if a == len(got) else "human" if a == 0 else "mixed"
        buckets[key].append(b)
        for a in b.annotations:
            notes[key][a] += 1

    total_commits = len(all_shas)
    print(f"{repo.name}: {len(files)} files, {total_commits} commits touching them")
    print(f"  {len(aid)} of {total_commits} carry an assistant trailer\n")

    print(
        f"{'bucket':10s} {'blocks':>7s} {'mean L':>7s} "
        f"{'>6L':>6s} {'>6L%':>6s} {'notes/block':>12s}"
    )
    for key in ("human", "assisted", "mixed", "unknown"):
        bs = buckets.get(key) or []
        if not bs:
            continue
        n = len(bs)
        over = sum(1 for b in bs if b.kind == "comment" and b.lines > 6)
        mean = sum(b.lines for b in bs) / n
        mk = sum(notes[key].values()) / n
        print(
            f"{key:10s} {n:7d} {mean:7.1f} {over:6d} {100 * over / n:5.1f}% {mk:12.2f}"
        )

    print("\nannotations by bucket:")
    for key in ("human", "assisted", "mixed"):
        if notes.get(key):
            top = ", ".join(f"{k} {v}" for k, v in notes[key].most_common(6))
            print(f"  {key:9s} {top}")

    print(
        "\n⚠ A trailer means an assistant was involved in the COMMIT, not that it\n"
        "  wrote the prose. `mixed` blocks straddle both and are not forced into a\n"
        "  bucket. Read this as a correlation worth following, not a result."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
