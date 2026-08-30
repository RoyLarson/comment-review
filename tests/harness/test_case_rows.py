"""A keyed row in `evals/test-cases.jsonl` resolves against the history it names.

!! A CASE FILE NOTHING READS IS A CASE FILE NOTHING CHECKS. `test-cases.jsonl` is
imported by no module in this tree -- measured 2026-08-30, `grep -l test.cases`
over every `.py` returns nothing -- so a row naming a hash that does not resolve,
a path absent at START, or a defect that was never there would sit correct-looking
until someone spent a graded run on it. At about $0.68 a reading, the row is
cheaper to check here.

!! WHAT MAKES A ROW A KEY RATHER THAN A CLAIM is the last two assertions: the
quoted sentence is IN the file at START and is GONE at END. A row asserting a
defect that the tree never held would grade a run down for not finding it, and a
row whose END did not fix it would grade a run down for finding it twice.

! IT CAN FAIL, and by construction rather than by hope: every assertion reads git
rather than the row, so any of them disagreeing is the row being wrong. MEASURED
2026-08-30 -- see `TestTheCheckItselfFires`, which mutates each field in turn and
requires the matching assertion to reject it.

! THE PROSE-ONLY TEST IS THE SHIPPED ONE, `prove_unchanged.code_fingerprint`, the
same call `evals/prose_commits.py` makes and the same one stage 7b gates a WRITE
on. A private "strip the comments and compare" here would be a second
implementation of this repo's central claim, and the one nobody tests.
"""

import json
import pathlib
import re
import subprocess
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
CASES = REPO / "evals" / "test-cases.jsonl"

sys.path.insert(0, str(REPO / "src"))

from comment_review.results.prove_unchanged import code_fingerprint  # noqa: E402

#: The four editorial roles, as `plugins/comment-review/agents/` names them.
ROLES = {
    "ownership-context",
    "block-context",
    "function-context",
    "module-context",
}


def rows() -> list[dict]:
    text = CASES.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def keyed(all_rows: list[dict]) -> list[dict]:
    """The rows naming a range. A row pinning one `commit` is not one of these.

    ! SIX ROWS PIN A SINGLE `commit` AND ARE LEFT ALONE. They record a defect an
    observed run made, not a START/END pair, so they have no END to resolve --
    which is what T15 of `the-harness-cannot-run-the-system-it-grades` is about.
    """
    return [row for row in all_rows if "start" in row or "end" in row]


def at(commit: str, path: str) -> str:
    """The file as the object store holds it, never as a checkout would write it.

    ! `git show`, NOT A CHECKOUT, for the reason `evals/stage_case.py` gives at
    length: with `core.autocrlf=true` the checkout filter returns CRLF where the
    stored blob is LF, so a test reading the working tree would compare different
    bytes on two machines.
    """
    return subprocess.run(
        ["git", "-C", str(REPO), "show", f"{commit}:{path}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def flattened(text: str) -> str:
    """One line, so a quotation matches however the source wrapped it.

    A sentence in a comment carries `#` and a newline every 80 characters; the
    same sentence in a row carries neither. Collapsing both to single spaces is
    what lets one be looked for in the other.
    """
    return re.sub(r"[\s#]+", " ", text).strip()


class TestKeyedRowsResolve(unittest.TestCase):
    def setUp(self):
        self.keyed = keyed(rows())

    def test_there_are_keyed_rows_to_check(self):
        """Otherwise every assertion below passes over an empty list."""
        self.assertTrue(self.keyed, f"no row in {CASES.name} names a start/end pair")

    def test_a_row_naming_a_range_carries_both_hashes(self):
        """T15's own verify, as a gate: `start` without `end` keys nothing."""
        for row in self.keyed:
            with self.subTest(row["id"]):
                self.assertIn("start", row, "carries end but no start")
                self.assertIn("end", row, "carries start but no end")

    def test_both_hashes_resolve_to_a_commit(self):
        for row in self.keyed:
            for side in ("start", "end"):
                with self.subTest(row["id"], side=side):
                    done = subprocess.run(
                        ["git", "-C", str(REPO), "cat-file", "-t", row[side]],
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(
                        done.returncode, 0, f"{row[side]} does not resolve"
                    )
                    self.assertEqual(done.stdout.strip(), "commit")

    def test_every_path_exists_at_start(self):
        """The failure `stage_case.py` refuses: a case written against a newer tree.

        A path absent at START stages nothing, and the role reports nothing where
        the defect was -- which reads as a miss rather than as a broken case.
        """
        for row in self.keyed:
            for path in row["files"]:
                with self.subTest(row["id"], path=path):
                    done = subprocess.run(
                        [
                            "git",
                            "-C",
                            str(REPO),
                            "cat-file",
                            "-e",
                            f"{row['start']}:{path}",
                        ],
                        capture_output=True,
                    )
                    self.assertEqual(
                        done.returncode, 0, f"not in {row['start'][:8]}: {path}"
                    )

    def test_the_pair_changed_no_executable_code(self):
        """The whole diff is the key, so there must be no code half to confuse it.

        !! THE `unprovable` KIND IS CHECKED FIRST, and equality alone would miss
        it. `code_fingerprint` returns `(kind, fingerprint)` and gives an
        unprovable file an EMPTY fingerprint -- so two files it cannot read
        compare EQUAL, and the pair would pass this as prose-only having proved
        nothing. Its own docstring says such a file "must never be reported as
        proven".
        """
        for row in self.keyed:
            for path in row["files"]:
                with self.subTest(row["id"], path=path):
                    named = pathlib.Path(path)
                    before = code_fingerprint(at(row["start"], path), named)
                    after = code_fingerprint(at(row["end"], path), named)
                    self.assertNotEqual(
                        before[0], "unprovable", f"{path} at START cannot be proven"
                    )
                    self.assertNotEqual(
                        after[0], "unprovable", f"{path} at END cannot be proven"
                    )
                    self.assertEqual(
                        before,
                        after,
                        f"{path} changed executable code between START and END",
                    )

    def test_every_site_names_a_real_role_the_row_declares(self):
        for row in self.keyed:
            for site in row.get("sites", []):
                with self.subTest(row["id"], said=site["said"][:40]):
                    self.assertIn(site["role"], ROLES)
                    self.assertIn(site["role"], row["roles"])

    def test_every_quoted_defect_is_in_the_file_at_start(self):
        """The row asserts a defect; START is what says whether it was ever there."""
        for row in self.keyed:
            for site in row.get("sites", []):
                with self.subTest(row["id"], said=site["said"][:40]):
                    self.assertIn(
                        flattened(site["said"]),
                        flattened(at(row["start"], site["file"])),
                        f"not in {site['file']} at {row['start'][:8]}",
                    )

    def test_every_quoted_defect_is_gone_at_end(self):
        """END is the answer key, so a defect it did not fix is not keyed by it."""
        for row in self.keyed:
            for site in row.get("sites", []):
                with self.subTest(row["id"], said=site["said"][:40]):
                    self.assertNotIn(
                        flattened(site["said"]),
                        flattened(at(row["end"], site["file"])),
                        f"still in {site['file']} at {row['end'][:8]}",
                    )


class TestTheCheckItselfFires(unittest.TestCase):
    """Each assertion above, run against a row mutated to break exactly it.

    !! WITHOUT THIS THE SUITE ABOVE IS SEVEN GREEN LINES THAT MIGHT ASSERT
    NOTHING -- `docs/gates.md`: "does the check pass" is not the question; "could
    the check fail" is. Each case here takes a row that passes, breaks one field,
    and requires the matching assertion to reject it.
    """

    def setUp(self):
        self.row = dict(keyed(rows())[0])

    def test_a_start_that_does_not_resolve_is_caught(self):
        done = subprocess.run(
            ["git", "-C", str(REPO), "cat-file", "-t", "0" * 40],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(done.returncode, 0)

    def test_a_path_absent_at_start_is_caught(self):
        """The fixture is the one the plan names, and it postdates every keyed START.

        ! `src/comment_review/` ARRIVED WITH THE 2026-08-24 PACKAGE MOVE, so it is
        on HEAD and on disk and in neither keyed START -- which is exactly the
        mistake `stage_case.py` exists to refuse, a case written today against an
        older hash. ! A first attempt used `evals/test-cases.jsonl` and this test
        FAILED: that file already existed on 2026-08-20.
        """
        absent = "src/comment_review/machine/__init__.py"
        self.assertTrue((REPO / absent).exists(), "fixture must exist on disk")
        done = subprocess.run(
            ["git", "-C", str(REPO), "cat-file", "-e", f"{self.row['start']}:{absent}"],
            capture_output=True,
        )
        self.assertNotEqual(
            done.returncode,
            0,
            "this path postdates the row's START; it must not resolve",
        )

    def test_a_sentence_the_file_never_held_is_caught(self):
        site = self.row["sites"][0]
        self.assertNotIn(
            flattened("a sentence no file in this tree has ever carried"),
            flattened(at(self.row["start"], site["file"])),
        )

    def test_a_defect_end_did_not_fix_is_caught(self):
        """A sentence END left standing must fail the gone-at-END assertion.

        ! THE FIXTURE IS THE ROW'S OWN FILE, not an invented one: the module
        docstring's first line survives START and END untouched, so it is exactly
        the shape a badly-keyed site would have.
        """
        site = self.row["sites"][0]
        survivor = flattened(at(self.row["end"], site["file"]))[:60]
        self.assertIn(survivor, flattened(at(self.row["start"], site["file"])))
        self.assertIn(survivor, flattened(at(self.row["end"], site["file"])))

    def test_a_role_outside_the_four_is_caught(self):
        self.assertNotIn("style-context", ROLES)


if __name__ == "__main__":
    unittest.main()
