"""A definition exists once, and every agent is given the terms it uses."""

import unittest  # noqa: I001  -- path shim below must import before vocabulary

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


if __name__ == "__main__":
    unittest.main()
