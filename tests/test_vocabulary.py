"""A definition exists once, and every agent is given the terms it uses."""

import unittest  # noqa: I001  -- path shim below must import before vocabulary
from pathlib import Path

import sys

from _paths import SCRIPTS  # noqa: F401
import vocabulary as vocab

REPO = Path(__file__).resolve().parent.parent
REFERENCES = REPO / "plugins/comment-review/skills/comment-review/references"

# ! `check_vocabulary.py` is a development script, not a shipped one, so it is
# not on the path `_paths` sets up for the plugin's own modules.
sys.path.insert(0, str(REPO / "scripts"))
import check_vocabulary as cv  # noqa: E402


class TestTheFile(unittest.TestCase):
    """`references/vocabulary.toml` is the single source, so it has to hold."""

    def setUp(self):
        self.definitions, self.roles = vocab.load()

    def test_every_key_a_role_is_given_has_a_definition(self):
        for role, keys in self.roles.items():
            for key in keys:
                self.assertIn(key, self.definitions, f"{role} lists undefined {key!r}")

    def test_no_definition_is_written_for_nobody(self):
        given = set().union(*(set(keys) for keys in self.roles.values()))
        self.assertEqual(
            sorted(set(self.definitions) - given),
            [],
            "a definition nobody receives belongs in docs/, not here",
        )

    def test_a_role_never_repeats_what_every_agent_already_gets(self):
        shared = set(self.roles[vocab.EVERY_AGENT])
        for role, keys in self.roles.items():
            if role == vocab.EVERY_AGENT:
                continue
            self.assertEqual(
                sorted(shared & set(keys)), [], f"{role} repeats a shared term"
            )

    def test_every_dispatchable_role_has_a_list(self):
        for role in vocab.Reviewer:
            self.assertIn(role.value, self.roles)


class TestWhatIsEmitted(unittest.TestCase):
    """The paragraph the task agent pastes into an agent's prompt."""

    def setUp(self):
        self.definitions, self.roles = vocab.load()

    def _render(self, role):
        return vocab.render(role, self.definitions, self.roles)

    def test_every_role_renders(self):
        for role in vocab.Reviewer:
            self.assertIn("## VOCABULARY", self._render(role.value))

    def test_the_shared_terms_reach_every_role(self):
        for role in vocab.Reviewer:
            paragraph = self._render(role.value)
            for term in self.roles[vocab.EVERY_AGENT]:
                self.assertIn(f"**{term}**", paragraph, f"{role.value} lost {term!r}")

    def test_a_role_gets_its_own_terms_and_not_another_role_s(self):
        # `guard` is block-context's and function-context's; `banner` is
        # module-context's alone. A role that receives every term has no remit.
        self.assertIn("**banner**", self._render("module-context"))
        self.assertNotIn("**banner**", self._render("ownership-context"))
        self.assertIn("**guard**", self._render("function-context"))
        self.assertNotIn("**guard**", self._render("module-context"))

    def test_a_term_appears_once_per_block(self):
        for role in vocab.Reviewer:
            paragraph = self._render(role.value)
            entries = [ln for ln in paragraph.splitlines() if ln.startswith("- **")]
            self.assertEqual(len(entries), len(set(entries)), role.value)

    def test_a_key_with_no_definition_is_refused_not_skipped(self):
        roles = dict(self.roles, review=["a-term-that-is-not-defined"])
        with self.assertRaises(KeyError):
            vocab.render("review", self.definitions, roles)


class TestProseTreeRetired(unittest.TestCase):
    """Ruled 2026-08-17: the census builds a pCST, and one name had to go.

    Roy: *"pCST not prose tree"*. While the pCST was an aspiration and the prose
    tree was what the census actually built, the two were distinguishable. The
    census enumerates intervals now, so they name one thing.
    """

    ROOT = Path(__file__).resolve().parent.parent

    def test_no_shipped_file_says_prose_tree(self):
        shipped = sorted((self.ROOT / "plugins").rglob("*.md"))
        shipped += sorted((self.ROOT / "plugins").rglob("*.py"))
        self.assertTrue(shipped, "no shipped files found -- the glob is wrong")
        for path in shipped:
            with self.subTest(path=path.name):
                # ! `assertFalse` with a short message, not `assertNotIn`: these
                # files are tens of kilobytes and `assertNotIn` prints the whole
                # haystack, burying the name of the file that failed.
                self.assertFalse(
                    "prose tree" in path.read_text(encoding="utf-8").lower(),
                    f"{path.name} still says 'prose tree'",
                )

    def test_the_retired_table_records_it_with_a_reason(self):
        text = (self.ROOT / "docs" / "vocabulary.md").read_text(encoding="utf-8")
        self.assertIn("`prose tree`", text)
        self.assertIn("pCST", text)


class TestTheRetiredWordsStayRetired(unittest.TestCase):
    """A shipped file may not USE a word the vocabulary retired.

    !! NOTHING ENFORCED THIS, so `block` survived in 298 shipped places after
    `paragraph` replaced it, and three shipped DEFINITIONS still used it in
    their own text -- `clean`, `record` and `load-bearing` -- while the entry
    for `block` itself had already been rewritten. B7 renamed the term and not
    the sentences that spend it.

    ! `record`'s was also FALSE by then: it said the tool seeds *"the block
    index and address"*, and a seeded slot carries an address and an anchor and
    no index at all.
    """

    def test_the_shipped_tree_uses_no_retired_word(self):
        self.assertEqual(cv.check_retired(), 0)

    def test_a_retired_word_IS_caught(self):
        # ! Guards the guard: a check that never fires is a green bar over
        # nothing, which is the whole reason this file exists.
        self.assertTrue(cv.RETIRED)
        for word in cv.RETIRED:
            with self.subTest(word=word):
                self.assertNotIn(word, ("paragraph", "paragraphs"))

    def test_a_MENTION_in_backticks_is_not_a_use(self):
        # !! `paragraph`'s own definition says "`block` is the older word for
        # it", and `page.py` explains what the word meant before. Both keep an
        # error legible rather than erasing it -- the same rule that keeps a
        # SUPERSEDED task checked instead of deleted.
        self.assertIn("`block`", cv.MENTION)
        toml = (REFERENCES / "vocabulary.toml").read_text(encoding="utf-8")
        self.assertIn("`block` is the older word", toml)

    def test_the_EXEMPTION_is_per_file_and_held_carries_it(self):
        """!! `held.py` reads a format that no longer ships and must say
        `BLOCK`, because that is the line MARKER in reports already on disk.

        Renaming it there made 173 of 173 held records unreadable, measured
        2026-08-19. It is exempt WHOLE, which is why the code that needs the
        exemption was moved out of `record.py` first -- 473 lines, 30% of a file
        that announces ONE subject. Roy, 2026-08-19: *"let's make certain to
        move the code into separate files to make it easy."*
        """
        held = SCRIPTS / "held.py"
        self.assertTrue(held.exists(), "held.py is where the retired format lives")
        self.assertIn(cv.NOQA, held.read_text(encoding="utf-8"))

    def test_NO_OTHER_shipped_file_claims_the_exemption(self):
        # !! A per-FILE out is only safe while it stays rare. Exempting a file
        # that IS about the current representation would let the retired word
        # creep back one suppression at a time.
        claimed = [
            f.name
            for f in sorted((REPO / "plugins").rglob("*"))
            if f.is_file()
            and f.suffix in (".md", ".py", ".toml")
            and cv.NOQA in f.read_text(encoding="utf-8")
        ]
        self.assertEqual(claimed, ["held.py"])


# !! LAST LINE, ALWAYS. A runner placed above a class runs before that
# class exists, so `python tests/<file>.py` reported a green bar over a
# SHORTER suite than `unittest discover` -- and the tests it skipped were
# the ones someone running a single file was iterating on. Measured
# 2026-08-17: 26 direct against 28 discovered here, 9 against 11 in
# test_vocabulary.py.
if __name__ == "__main__":
    unittest.main()
