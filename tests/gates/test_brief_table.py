"""The committed instruction table agrees with a fresh render.

! THE EXPECTATION IS THE COMMITTED BLOCK, never the generator's own idea of
itself -- a fresh render is checked AGAINST the file, not the other way
round, so a change to `scripts/render_brief.py` that moves the table must
also re-run `--write` and commit the result.

    uv run pytest -q tests/gates/test_brief_table.py
"""

import subprocess
import sys

from conftest import ROOT

BRIEF_PATH = (
    ROOT
    / "plugins"
    / "comment-review"
    / "skills"
    / "comment-review"
    / "references"
    / "reviewer-brief.md"
)
RENDER_SCRIPT = ROOT / "scripts" / "render_brief.py"


def _fresh_render() -> str:
    result = subprocess.run(
        [sys.executable, str(RENDER_SCRIPT), "--print"],
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    )
    return result.stdout


def _committed_block() -> str:
    brief = BRIEF_PATH.read_text(encoding="utf-8")
    return brief.split("<!-- BEGIN GENERATED")[1].split("<!-- END GENERATED")[0]


def test_the_committed_block_matches_a_fresh_render():
    assert _fresh_render().strip() in _committed_block()


def test_the_marker_names_the_real_generator():
    brief = BRIEF_PATH.read_text(encoding="utf-8")
    marker = "<!-- BEGIN GENERATED: instruction table -- scripts/render_brief.py -->"
    assert marker in brief
