"""Every shipped frontmatter parses as YAML, so no metadata is silently dropped.

!! Measured 2026-08-17, by `claude plugin validate`: `SKILL.md` and
`comment-review-block-context.md` both failed to parse, and had failed since at
least v0.2.0. The runtime does not report it -- a skill loads with EMPTY
metadata and an agent loads with its name taken from the filename and every
other field dropped. The visible symptom was that block-context's description
read "Agent from comment-review plugin" in the agent registry while the other
five read their own, so the one text that tells a model when to reach for that
reviewer was missing from every session.

The cause is a `: ` INSIDE an unquoted value. YAML ends a plain scalar at
colon-space, so `description: three kinds of claim: state and ...` is not a
string -- it is a parse error. Confirmed against the real validator with eight
one-construct probes: `?`, `"`, `--` and `()` mid-value all parse; colon-space
does not, in any position.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHIPPED = ROOT / "plugins" / "comment-review"
# A frontmatter paragraph is the first `---` fenced region of the file.
FENCE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)


def frontmatter_files():
    """Every shipped Markdown file that opens with a frontmatter fence."""
    return sorted(p for p in SHIPPED.rglob("*.md") if FENCE.match(p.read_text("utf-8")))


class TestShippedFrontmatterParses(unittest.TestCase):
    def test_there_are_files_to_check(self):
        # A glob that matched nothing would make every test below vacuous.
        self.assertGreaterEqual(len(frontmatter_files()), 7)

    def test_no_value_carries_an_unquoted_colon_space(self):
        for path in frontmatter_files():
            body = FENCE.match(path.read_text("utf-8")).group(1)
            for line in body.splitlines():
                key, sep, value = line.partition(": ")
                if not sep:
                    continue
                # A quoted or paragraph scalar may hold anything; a plain one may not.
                if value[:1] in {'"', "'", ">", "|"}:
                    continue
                with self.subTest(file=path.name, key=key.strip()):
                    self.assertNotIn(
                        ": ",
                        value,
                        f"{path.relative_to(ROOT).as_posix()}: the value of "
                        f"`{key.strip()}` holds a colon-space, which ends a "
                        "plain YAML scalar -- the whole frontmatter then fails "
                        "to parse and every field is dropped at runtime. Use "
                        "` -- ` instead, or quote the value.",
                    )
