"""No shipped file calls the mark's field a `verdict`.

`decision-log.md Vocabulary: #17`.

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

from conftest import ROOT

REPO = ROOT


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
