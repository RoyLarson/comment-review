"""No shipped file calls the mark's field a `verdict`, or the per-role
container a `sheet`.

`decision-log.md Vocabulary: #17`, `#28`.

    uv run pytest -q tests/gates/test_vocabulary.py

`verdict` was struck 2026-08-27 in favour of `instruction` -- see
`docs/decision-log.md Vocabulary: #17`. A line citing that ruling is exempt;
everything else under `plugins/` must not use the retired word.

! A FENCED BLOCK IS LITERAL SYNTAX, NOT PROSE, so a line inside one is skipped
-- a shell invocation, a JSON worked example and an ASCII table each spell an
exact string a reader is meant to type or match verbatim, the same reason a
real filename (`verdicts.py`, kept by `prototype/`) or a real identifier
(`TestEveryVerdictThePlacesCanEXPRESSGetsThroughTheChain`, in `tests/`) is not
reworded. `SKILL.md`'s stage 5 command names a subcommand that no longer
exists in `src/comment_review/__main__.py`'s `COMMANDS` -- tracked separately
in `TODO/the-skill-names-commands-that-moved-to-prototype.md` -- and inventing
a replacement token here would be worse than leaving the broken one legible.
"""

import re

from conftest import ROOT

REPO = ROOT

_SKILL_DIR = ROOT / "plugins" / "comment-review" / "skills" / "comment-review"

#: Every file an agent reads that may name a container -- matches
#: `test_skill_commands.py`'s own `AGENT_FACING`.
AGENT_FACING = (
    _SKILL_DIR / "SKILL.md",
    _SKILL_DIR / "references" / "write.md",
    _SKILL_DIR / "references" / "review.md",
    _SKILL_DIR / "references" / "reviewer-brief.md",
)


def test_no_shipped_file_calls_the_field_a_verdict():
    offenders = []
    for path in (REPO / "plugins").rglob("*"):
        if path.suffix not in {".md", ".py", ".toml"} or not path.is_file():
            continue
        fenced = False
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip().startswith("```"):
                fenced = not fenced
                continue
            if fenced:
                continue
            if "verdict" in line.lower() and "decision-log" not in line:
                offenders.append(f"{path.relative_to(REPO)}:{n}")
    assert offenders == [], offenders


#: The retired PER-ROLE-CONTAINER phrasing (`decision-log.md Vocabulary:
#: #28`) always paired `sheet` with `role` -- "Hand a role a sheet to fill",
#: "role: the editorial role this sheet is for". The PAGE-UNIT sense pairs
#: `sheet` with `page` ("one sheet per page"), and `style sheet` (declared in
#: `vocabulary.toml`, the stage-1.5 doc-convention artifact) pairs it with
#: `style`. `role` within 40 characters of `sheet`, on a line naming neither
#: `page` nor `style sheet`, is the retired sense.
_ROLE_NEAR_SHEET = re.compile(
    r"\bsheet\b.{0,40}\brole\b|\brole\b.{0,40}\bsheet\b", re.IGNORECASE
)


def test_no_agent_facing_file_calls_the_per_role_container_a_sheet():
    """EXPECTATION FROM `docs/vocabulary.md`'s four-container table
    (`decision-log.md Vocabulary: #28`): `sheet` names the PAGE-UNIT inside
    an `edit_copy`, never the per-role container.

    ! MEASURED 2026-08-29: every `sheet` mention in `AGENT_FACING` today is
    `style sheet` (the declared stage-1.5 term) or one of its anaphoric
    continuations ("the sheet"); none is the per-role container, so no
    rename was owed to any of these four files.
    """
    offenders = []
    for path in AGENT_FACING:
        text = path.read_text(encoding="utf-8")
        for n, line in enumerate(text.splitlines(), 1):
            if "style sheet" in line.lower() or "page" in line.lower():
                continue
            if _ROLE_NEAR_SHEET.search(line):
                offenders.append(f"{path.name}:{n}")
    assert offenders == [], offenders
