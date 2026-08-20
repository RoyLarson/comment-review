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


class TestTheThingIsAPage(unittest.TestCase):
    """It was a `prose tree`, then a `pCST`, and it is a PAGE.

    !! THE SECOND NAME WAS BORROWED AND NEVER FIT. Roy, 2026-08-20: *"using
    libcst in python made it easy to move and edit comments and so I thought
    that was what this was. It isn't."* Naming it for a syntax tree invited an
    apology for not being one -- every file that mentioned it explained at
    length why it was only *pseudo*, and everything those apologies defended is
    simply correct for a page.

    ! `check_vocabulary.RETIRED` is what holds this; these tests are the record
    of why, and that the retired table still says so.
    """

    ROOT = Path(__file__).resolve().parent.parent

    def test_no_shipped_file_says_either_older_name(self):
        """! A retired word NAMED is not a retired word USED.

        This grepped raw and so contradicted the gate it defers to: a docstring
        saying *"the name was wrong the way `pCST` was"* is a mention, which
        `MENTION` exempts and this refused. The exemption is stripped here the
        same way `check_retired` strips it, so the two cannot disagree.
        """
        shipped = sorted((self.ROOT / "plugins").rglob("*.md"))
        shipped += sorted((self.ROOT / "plugins").rglob("*.py"))
        self.assertTrue(shipped, "no shipped files found -- the glob is wrong")
        for path in shipped:
            body = path.read_text(encoding="utf-8")
            if cv.NOQA in body:
                continue
            for allowed in (*cv.MENTION, *cv.NOT_THE_TERM):
                body = body.replace(allowed, "")
            body = body.lower()
            for word in ("prose tree", "pcst"):
                with self.subTest(path=path.name, word=word):
                    # ! `assertFalse` with a short message, not `assertNotIn`:
                    # these files are tens of kilobytes and `assertNotIn` prints
                    # the whole haystack, burying the name of the file that
                    # failed.
                    self.assertFalse(word in body, f"{path.name} still says {word!r}")

    def test_the_retired_table_records_both_with_a_reason(self):
        text = (self.ROOT / "docs" / "vocabulary.md").read_text(encoding="utf-8")
        self.assertIn("`prose tree`", text)
        self.assertIn("`pCST`", text)

    def test_the_gate_holds_it_rather_than_this_test(self):
        # ! Naming a word here and not there is how `block` survived in 298
        # places: a test that greps is one file's opinion, and the gate runs on
        # every shipped file at once.
        self.assertIn("pcst", cv.RETIRED)


class TestADefinitionIsNotWrittenTwice(unittest.TestCase):
    """A live term is defined where it is EMITTED from, and nowhere else.

    !! TWO COPIES OF ONE DEFINITION DRIFT SILENTLY. Six terms carried one in
    both `vocabulary.toml` and `docs/vocabulary.md`, and the two copies of
    `anchor` had already disagreed -- the shipped one said an `a` is attached to
    "its declaration", the doc said "the LINE that declares it ... and the name
    is not carried at all". Every role was handed the first and every human read
    the second.
    """

    def setUp(self):
        self.definitions, _ = vocab.load()

    def test_the_doc_defines_nothing_the_shipped_file_defines(self):
        self.assertEqual(cv.check_duplicate(self.definitions), 0)

    def test_a_definition_row_IS_found(self):
        # ! Guards the guard: a pattern that matches nothing is a green bar over
        # every duplicate there is.
        self.assertEqual(cv.doc_defines("| **anchor** | a line of code |"), ["anchor"])

    def test_the_RETIRED_table_is_a_record_and_not_a_definition(self):
        # !! The record NAMES a shipped term on purpose -- `block` -> `paragraph`
        # only means something if it may say `paragraph`. Counting those rows
        # would make the gate refuse the file for doing its job.
        doc = "| **live** | x |\n## Retired\n| **paragraph** | the newer word |\n"
        self.assertEqual(cv.doc_defines(doc), ["live"])

    def test_the_real_doc_carries_the_retired_heading(self):
        # ! Without it the split is a no-op and the record would be scanned as
        # definitions -- the failure would look like a broken document.
        text = (REPO / "docs" / "vocabulary.md").read_text(encoding="utf-8")
        self.assertIn(cv.RETIRED_HEADING, text)


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
