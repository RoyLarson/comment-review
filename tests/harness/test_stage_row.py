"""Staging a case BY ID: the row lookup, the scoped key, and the CLI's refusals.

`test_stage_case.py` covers `stage()` itself -- that the bytes written are the
stored blob rather than a checkout. This covers what 2026-08-30 added above it,
once the four keyed rows made a row-shaped input possible.

!! THE SCOPING TEST IS THE ONE WORTH HAVING. Two of the four cases were committed
with a `plugins/` copy of the same edit beside the `src/` one, and their rows name
only `src/`. An unscoped `git diff` would hand the grader a key containing changes
the role was never shown -- and the run would be marked down for missing every one
of them, which reads as a bad reviewer rather than a bad harness.
"""

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

import stage_case

REPO = pathlib.Path(__file__).resolve().parents[2]
EVALS = REPO / "evals"
CASES = EVALS / "test-cases.jsonl"

KEYED = "a-caller-list-that-names-four-of-seven"
UNKEYED = "an-add-cites-an-empty-interval"


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(EVALS / "stage_case.py"), *args],
        capture_output=True,
        text=True,
    )


class TestRowLookup(unittest.TestCase):
    def test_a_keyed_row_comes_back_whole(self):
        row = stage_case.row_for(CASES, KEYED)
        self.assertEqual(row["id"], KEYED)
        self.assertIn("start", row)
        self.assertIn("end", row)

    def test_an_unknown_id_is_refused_and_the_refusal_lists_what_exists(self):
        """A bare 'not found' sends the caller to the file to learn what they meant."""
        with self.assertRaises(stage_case.NoSuchCase) as refused:
            stage_case.row_for(CASES, "not-a-case-id")
        said = str(refused.exception)
        self.assertIn("not-a-case-id", said)
        self.assertIn(KEYED, said)

    def test_a_row_pinning_one_commit_is_refused_as_unkeyed_not_as_missing(self):
        """It IS a case; it has no START. 'No such case' would be the wrong answer."""
        with self.assertRaises(stage_case.NotKeyed):
            stage_case.row_for(CASES, UNKEYED)


class TestTheKeyIsScopedToTheRow(unittest.TestCase):
    def test_the_diff_holds_only_paths_the_row_names(self):
        """The commit touched a `plugins/` copy the row does not name."""
        row = stage_case.row_for(CASES, KEYED)
        self.assertTrue(
            all(path.startswith("src/") for path in row["files"]),
            "this test is about a src-only row; the fixture changed",
        )
        key = stage_case.end_diff(REPO, row)
        self.assertIn("src/comment_review/machine/repo.py", key)
        self.assertNotIn("plugins/", key)

    def test_the_unscoped_diff_would_have_leaked_that_copy(self):
        """The check can fail: without `-- paths`, the plugins/ half is right there.

        ! WITHOUT THIS the assertion above passes for any commit that never
        touched `plugins/` at all, and would go on passing if the scoping were
        removed.
        """
        row = stage_case.row_for(CASES, KEYED)
        unscoped = subprocess.run(
            ["git", "-C", str(REPO), "diff", row["start"], row["end"]],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        self.assertIn("plugins/", unscoped)


class TestTheCli(unittest.TestCase):
    def setUp(self):
        held = tempfile.TemporaryDirectory()
        self.addCleanup(held.cleanup)
        # ! `--out` MUST NOT EXIST, so the case goes one level BELOW the temp
        # directory rather than being it.
        self.dest = pathlib.Path(held.name) / "case"

    def test_it_stages_the_stored_blob_and_writes_the_key(self):
        done = run_cli("--case", KEYED, "--out", str(self.dest))
        self.assertEqual(done.returncode, 0, done.stderr)

        row = stage_case.row_for(CASES, KEYED)
        for path in row["files"]:
            written = (self.dest / "start" / path).read_bytes()
            stored = subprocess.run(
                ["git", "-C", str(REPO), "show", f"{row['start']}:{path}"],
                capture_output=True,
                check=True,
            ).stdout
            self.assertEqual(written, stored, f"{path} is not the stored blob")

        self.assertTrue((self.dest / "end.diff").read_text(encoding="utf-8").strip())
        recorded = json.loads((self.dest / "case.json").read_text(encoding="utf-8"))
        self.assertEqual(recorded["id"], KEYED)

    def test_an_unknown_case_exits_nonzero_and_writes_nothing(self):
        done = run_cli("--case", "not-a-case-id", "--out", str(self.dest))
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("REFUSED", done.stderr)
        self.assertFalse(self.dest.exists(), "a refusal left a directory behind")

    def test_an_unkeyed_case_exits_nonzero_and_writes_nothing(self):
        done = run_cli("--case", UNKEYED, "--out", str(self.dest))
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("pins a single commit", done.stderr)
        self.assertFalse(self.dest.exists())

    def test_an_existing_out_is_refused_before_anything_is_read(self):
        self.dest.mkdir(parents=True)
        done = run_cli("--case", KEYED, "--out", str(self.dest))
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("exists", done.stderr)
        self.assertEqual(list(self.dest.iterdir()), [], "it wrote into an existing dir")


if __name__ == "__main__":
    unittest.main()
