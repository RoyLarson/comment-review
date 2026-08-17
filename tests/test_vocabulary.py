"""A definition exists once, and every agent is given the terms it uses."""

import unittest  # noqa: I001  -- path shim below must import before vocabulary
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401
import vocabulary as vocab


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
    """The block the task agent pastes into an agent's prompt."""

    def setUp(self):
        self.definitions, self.roles = vocab.load()

    def _render(self, role):
        return vocab.render(role, self.definitions, self.roles)

    def test_every_role_renders(self):
        for role in vocab.Reviewer:
            self.assertIn("## VOCABULARY", self._render(role.value))

    def test_the_shared_terms_reach_every_role(self):
        for role in vocab.Reviewer:
            block = self._render(role.value)
            for term in self.roles[vocab.EVERY_AGENT]:
                self.assertIn(f"**{term}**", block, f"{role.value} lost {term!r}")

    def test_a_role_gets_its_own_terms_and_not_another_role_s(self):
        # `guard` is block-context's and function-context's; `banner` is
        # module-context's alone. A role that receives every term has no remit.
        self.assertIn("**banner**", self._render("module-context"))
        self.assertNotIn("**banner**", self._render("ownership-context"))
        self.assertIn("**guard**", self._render("function-context"))
        self.assertNotIn("**guard**", self._render("module-context"))

    def test_a_term_appears_once_per_block(self):
        for role in vocab.Reviewer:
            block = self._render(role.value)
            entries = [ln for ln in block.splitlines() if ln.startswith("- **")]
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


# !! LAST LINE, ALWAYS. A runner placed above a class runs before that
# class exists, so `python tests/<file>.py` reported a green bar over a
# SHORTER suite than `unittest discover` -- and the tests it skipped were
# the ones someone running a single file was iterating on. Measured
# 2026-08-17: 26 direct against 28 discovered here, 9 against 11 in
# test_vocabulary.py.
if __name__ == "__main__":
    unittest.main()
