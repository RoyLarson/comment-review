"""`scripts/check_vocabulary.py` exits 0 on this tree, and each of its checks can fail.

! `docs/gates.md`: *"does the check pass" is not the question; "could the check
fail" is.* The gate was reported green three times on 2026-08-20 while it was
red, because nothing in the suite ran it -- `TODO/vocabulary-gate-is-red.md`
holds the record. This is what runs it.

    uv run pytest -q tests/gates/test_vocabulary_gate_bites.py
"""

import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

from conftest import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import check_vocabulary as cv  # noqa: E402


def _shipped() -> tuple[dict[str, str], dict[str, list[str]]]:
    data = tomllib.loads(cv.EMITTED.read_text(encoding="utf-8"))
    return data["definitions"], data["roles"]


class TestTheGateIsGreen(unittest.TestCase):
    def test_all_four_checks_pass_on_this_tree(self):
        # `main` is the gate: it runs all four and returns 1 if any found something.
        self.assertEqual(cv.main(), 0)


class TestEachCheckCanFail(unittest.TestCase):
    """Each case hands a check one planted defect and expects it counted."""

    def test_complete_reports_a_term_defined_for_nobody(self):
        self.assertEqual(cv.check_complete({"zzzq": "planted"}, {}), 1)

    def test_complete_reports_a_term_given_but_undefined(self):
        self.assertEqual(cv.check_complete({}, {"compact": ["zzzq"]}), 1)

    def test_duplicate_reports_a_term_the_doc_also_defines(self):
        # ! PLANTED, not taken from the real doc: on this tree the doc defines
        # nothing above its Retired heading, so a case reading it would be vacuous.
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "vocabulary.md"
            live, retired = "| **zzzq** | planted |\n", "| **other** | x |\n"
            text = f"{live}\n{cv.RETIRED_HEADING}\n\n{retired}"
            doc.write_text(text, encoding="utf-8")
            saved, cv.DOC = cv.DOC, doc
            try:
                self.assertEqual(cv.check_duplicate({"zzzq": "planted"}), 1)
            finally:
                cv.DOC = saved

    def test_drift_reports_a_term_a_role_is_given_and_never_uses(self):
        definitions, roles = _shipped()
        definitions = {**definitions, "zzzq": "planted"}
        roles = {**roles, "compact": [*roles["compact"], "zzzq"]}
        self.assertGreaterEqual(cv.check_drift(definitions, roles), 1)

    def _retired_hits(self, planted: str) -> int:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "src").mkdir()
            (Path(tmp) / "src" / "planted.py").write_text(planted, encoding="utf-8")
            saved, cv.REPO = cv.REPO, Path(tmp)
            try:
                return cv.check_retired()
            finally:
                cv.REPO = saved

    def test_retired_reports_a_retired_word_in_a_shipped_file(self):
        self.assertIn("block", cv.RETIRED)
        self.assertGreaterEqual(self._retired_hits("# one block and two blocks\n"), 1)

    def test_retired_reports_a_retired_word_inside_an_identifier(self):
        # ! `_` is a `\w`, so a scan for the word between non-word characters
        # read `block_problem` as one word and never saw the retired noun in it.
        self.assertGreaterEqual(self._retired_hits("block_problem = 1\n"), 1)

    def test_a_declared_identifier_is_not_reported(self):
        # The live symbol-to-series sense, declared in NOT_THE_TERM.
        self.assertEqual(self._retired_hits("x = lang.block_comment\n"), 0)
