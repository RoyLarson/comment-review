"""What a page could LOOK like, and what each rendering costs.

    uv run python scripts/render_page.py <paths...>
    uv run python scripts/render_page.py --show margin <path>

An INPUT to a ruling, not a gate: it always exits 0 and nothing consumes its
output. `TODO/the-census-is-mostly-intervals-nobody-rules-on.md` holds the
proposal and is where the decision lies. This exists so the question is answered
against renderings of a real file rather than against descriptions of them.

! IT NAMES THE TODO AND NOT A PLAN BOX. It cited one for the first hour of its
life; the box was superseded the same day and the citation rotted immediately.
A plan is a scope that closes -- the backlog is what outlives it.

Three renderings, and the file itself as the floor:

  ROWS    what ships today -- one numbered row per place, each carrying its
          anchor as a parenthetical. No code context: a reviewer reads N
          disconnected fragments.
  MARGIN  the file, every line, with each place's folio in the left margin. A
          gap gets its own rule between the lines it separates, so the place an
          `add` cites is visible as a position rather than a name.
  PROSE   the same, annotating ONLY the places that hold prose. The empty ones
          are listed under the page, which is cheaper and drops the position --
          the whole of what an empty place is for.

!! MEASURED 2026-08-21 over 26 files -- every shipped script, this repo's own
`scripts/`, plus `corpora/cpython/Objects/listobject.c` and
`corpora/sentry/eslint.config.ts` so the spread is not all Python:

    rows    1,635,544 bytes
    margin  1,088,304          -33%, and smaller on 23 of the 26
    prose   1,029,443          -37%

!! THE TWO FORMATS COST DIFFERENT THINGS, which is what decides where each
wins: ROWS pays per PLACE and MARGIN pays per LINE. A file with much code and
little prose has an empty place between every pair of statements, each costing a
row with its anchor repeated -- `listobject.c` -50%, `eslint.config.ts` -51%,
`todo_tool.py` -45%. ! The three files the margin LOSES on are prose-dense with
few code lines: `foliator.py` +7%, `desk.py` +9%, `page.py` level.

! A ONE-FILE MEASUREMENT SAID 17% AND IS SUPERSEDED. `check_vocabulary.py`
alone is -20%, which happened to sit near neither end of the real range.

! WHAT IT DOES NOT RENDER IS THE MARKS. Roy, 2026-08-21: *"the records though
also need to be potentially explicitly shown or retrievable. Because they are
supposed to mark on the records what is supposed to happen."* A page showing
addresses and not the records against them is a proof with no editorial marks
on it, and that half is unbuilt.

! The gutter glyphs were invented here and match nothing else in the tree.
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "plugins/comment-review/skills/comment-review/scripts"))

import lexer  # noqa: E402
import page as page_mod  # noqa: E402

READ_ERRORS = (OSError, UnicodeDecodeError)
# ! The margin is wide enough for a folio and a series letter; a page with more
# than four digits of places is past the point this rendering answers anything.
MARGIN = 8


def _places(pg) -> tuple[dict[int, list[str]], dict[int, list[str]]]:
    """Where each place would be CITED from: on a line, or in a gap above one.

    A place holding prose is cited at the prose. An empty `b` is cited in the
    gap it holds, which sits above the line that closes it. An empty `a` or `c`
    is cited at its anchor, since both have one.

    Returns:
        `(at_line, gap_above)`, each `line -> folios`.
    """
    at_line: dict[int, list[str]] = {}
    gap_above: dict[int, list[str]] = {}
    for b in pg.paragraphs:
        # !! A `d` ANSWERS WITH ITS SYMBOL, because it has no address -- leading
        # names no place. Roy, 2026-08-22, ruling that the symbol survives the
        # cut: *"the page/symbol map has really helped in understanding what
        # each line is, so that we maintain the cover."* This margin IS that
        # map, so reading `address` alone left every run of blank lines blank.
        folio = (b.address or "").split("@")[-1] or b.symbol
        if not folio:
            continue
        if b.original_start:
            at_line.setdefault(b.original_start, []).append(folio)
            continue
        # ! An EMPTY place, marked so a reader can tell it from a filled one --
        # it is a place a verdict can still cite, and nothing occupies it.
        if folio[0] == "b":
            low, high = pg.foliation.gap_bounds(folio)
            gap_above.setdefault(high or low + 1, []).append(f"{folio}*")
            continue
        anchored = pg.foliation.anchor_line(folio)
        if anchored:
            at_line.setdefault(anchored, []).append(f"{folio}*")
        else:
            gap_above.setdefault(1, []).append(f"{folio}*")
    return at_line, gap_above


def margin(pg, text: str) -> str:
    """The file with every place in the margin, gaps included."""
    at_line, gap_above = _places(pg)
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        for folio in gap_above.get(n, []):
            out.append(f"{'':>{MARGIN}} .. {folio}")
        out.append(f"{' '.join(at_line.get(n, [])):>{MARGIN}} | {line}")
    return "\n".join(out)


def prose_only(pg, text: str) -> str:
    """The file with only the places that HOLD prose in the margin."""
    held = {
        b.original_start: (b.address or "").split("@")[-1]
        for b in pg.paragraphs
        if b.original_start and (b.text or "").strip()
    }
    empty = sorted(
        (
            (b.address or "").split("@")[-1]
            for b in pg.paragraphs
            if (b.address or "") and not (b.text or "").strip()
        ),
        key=lambda f: (f[0], int(f[1:] or 0)),
    )
    body = "\n".join(
        f"{held.get(n, ''):>{MARGIN}} | {line}"
        for n, line in enumerate(text.splitlines(), 1)
    )
    return f"{body}\n\nEMPTY PLACES ({len(empty)}): {' '.join(empty)}"


def rows(path: Path) -> str:
    """What ships today, by RUNNING the census rather than rebuilding it.

    !! IT SHELLS OUT ON PURPOSE. `census.py` exposes only `_report(args)`, which
    prints; reproducing its format here would be a second implementation of the
    artifact this is measuring, and the untested one would be mine. A comparison
    against a rebuild measures the rebuild.
    """
    tool = REPO / "plugins/comment-review/skills/comment-review/scripts/census.py"
    done = subprocess.run(
        [sys.executable, str(tool), "--repo", str(REPO), str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return done.stdout


def render(path: Path, show: str | None) -> None:
    """Print one file's three renderings, or just the one asked for."""
    try:
        text = path.read_text(encoding="utf-8")
    except READ_ERRORS as exc:
        print(f"  SKIP {path} -- {exc}")
        return
    lang = lexer.language_for(path)
    if lang is None:
        print(f"  SKIP {path} -- no language record for {path.suffix!r}")
        return
    pg = page_mod.page_for(path, text, lang, rel=path.as_posix())
    built = {
        "rows": rows(path),
        "margin": margin(pg, text),
        "prose": prose_only(pg, text),
    }
    lines = len(text.splitlines())
    print(f"\n== {path}  --  {lang.name}, {lines} lines, {len(pg.paragraphs)} places")
    floor = len(text)
    for name in ("rows", "margin", "prose"):
        size = len(built[name])
        share = size / max(floor, 1)
        print(f"   {name:<7} {size:>8,} bytes   {share:>6.0%} of the file")
    print(f"   {'file':<7} {floor:>8,} bytes")
    if show:
        print()
        print(built[show])


def main(argv: list[str] | None = None) -> int:
    """Size every rendering of each path given, and print one in full on request."""
    parser = argparse.ArgumentParser(
        description="What a page could LOOK like, and what each rendering costs."
    )
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument(
        "--show",
        choices=("rows", "margin", "prose"),
        help="also print this rendering in full; sizes alone are printed without it",
    )
    args = parser.parse_args(argv)
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    for path in args.paths:
        render(path, args.show)
    # ! An INPUT, ruled 2026-08-21 for `dead_sweep.py` and applied here: *"I
    # don't think it deserves a gating. I do think it is a genuinely good idea
    # to run every now and then."* Nothing here can fail.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
