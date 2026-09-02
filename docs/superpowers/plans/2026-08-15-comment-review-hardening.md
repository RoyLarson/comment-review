# comment-review Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

!! **AUDITED 2026-09-02 -- ALL 68 TASK STEPS HAD LANDED AND NONE WERE TICKED.**
The work shipped on 2026-08-15 across nine commits, `681bcfb` through
`5798a12`, and merged to main at `3e09207` (*"add 167 tests"*). Every one is
reachable from HEAD. This file read **0 of 71** for eighteen days while its
work sat in the tree -- the failure `CLAUDE.md` names: superpowers authors the
boxes and then tracks execution in a gitignored ledger, so nothing ever says to
tick the plan.

! **The ticks were derived, not assumed.** The branch tip `4a3e06f` was
extracted and its suite run: **167 tests, OK** -- which is what closes every
*"run the tests to verify they pass"* step. Two CLI expectations were
reproduced verbatim, at Task 3 Step 8 and Task 7 Step 5; both are recorded on
their tasks.

! **The three boxes under *After the plan: re-measure* are the only open work
in this file**, and they are DEFERRED rather than unstarted -- see the note
there.

! **TWO SHIPPED ARTIFACTS HAVE SINCE MOVED, WHICH DOES NOT REOPEN A BOX.**
`verdicts.py` and `run_context.py` sit in `prototype/original/` since
2026-08-25 and do not run; `prove_unchanged` and `referrers` are
`src/comment_review/` commands. A step is closed by what LANDED, not by what
survives -- and the 2026-08-25 suite replacement deleted the `unittest` files
these tasks wrote.

---

**Goal:** Close two confirmed silent-failure bugs in `census.py`, ship the three
checks the skill currently asks an agent to perform freehand, and convert the
task agent's most error-prone prose obligations into gates that exit nonzero.

**Architecture:** Two phases that ship independently. **Phase A** (Tasks 1-5)
fixes shipped code behind a new stdlib test harness -- no change to the skill's
contract, so it can land and be measured against the existing corpora
immediately. **Phase B** (Tasks 6-9) changes the pipeline contract: reviewers
emit a parseable finding record, a new `verdicts.py` performs the census join
and the evidence check mechanically, a run-context packet gates stage-4
dispatch, and COMPACT and REVIEW become mandatory separate subagents. Every new
script replaces prose in `SKILL.md`/`references/` rather than adding to it --
`docs/limitations.md` caps the prose budget per file, so a rule that becomes a
gate must be **deleted** from the document that used to carry it.

**Tech Stack:** Python 3.9-compatible stdlib only (`ast`, `tokenize`, `re`,
`subprocess`, `argparse`, `unittest`). No third-party dependencies anywhere
under `plugins/`. Ruff for lint/format.

**Spec:** This plan is its own spec. It implements the findings from the
2026-08-15 fresh-eyes review of this repository; each task's **Why** section
states the finding it closes and the evidence for it.

## Global Constraints

Every task's requirements implicitly include this section.

- **Anything under `plugins/` must parse on Python 3.9.** Enforced by
  `python scripts/check_shipped_syntax.py`, run AFTER `ruff format`. No `match`,
  no PEP 604 unions inside `isinstance`, no unparenthesised `except A, B`.
- **Bind every exception tuple to a NAME** in shipped files (`READ_ERRORS`,
  `PARSE_ERRORS`, `GIT_ERRORS`). A shipped file must contain nothing worth
  rewriting, because it is formatted by the *user's* ruff config, not ours.
- **Stdlib only under `plugins/`.** A tier selected by whether some package
  happens to be importable makes coverage depend on the ambient environment.
- **Ruff:** `line-length = 88`, `select = ["E","F","W","I","UP","B","D"]`,
  `convention = "google"`. New shipped functions need Google-style docstrings.
- **No hardcoded paths, directory names, or caps in shipped scripts**
  (`docs/limitations.md`). The skill has no cap of its own.
- **A rule belongs in exactly one file.** Shared reviewer contract ->
  `reviewer-brief.md`; one angle's -> that angle's agent file; apply-side ->
  `apply.md`; orchestration -> `SKILL.md`. Moving a rule into a script means
  deleting its prose from wherever it lived.
- **The census must miss ZERO blocks.** A block missing from the census is a
  block nobody reviews. A weaker verdict beats an absent one.
- **Absence is declared, never inferred.** A check that cannot see a defect must
  report that it could not see it -- never report it clean.
- **Never improvise a parse.** On an unknown structure the answer is to declare
  the gap or propose a `LANGUAGES` row, never to have an agent work it out by
  reading the file.

---

# PHASE A -- correctness of shipped code

## Task 1: Test harness and per-language fixtures

**Landed:** `681bcfb` -- `tests/_paths.py`, the four per-language fixtures and
`tests/test_census_blocks.py`, plus the `"tests/**" = ["D"]` ruff ignore in
`pyproject.toml`. Verified 2026-09-02: the era's three census test files run
**20/20 green** against `census.py` at `22a434d`.

**Why:** `census.py` is 858 lines, ships to strangers, and has no tests. Every
regression in it has so far been caught by a manual evidence sweep after the
fact. `docs/parsing.md` already commits to this: *"a per-language fixture test
is part of the work, not polish."* Tasks 2 and 3 modify census internals and
must not land without a net.

**Files:**
- Create: `tests/_paths.py`
- Create: `tests/test_census_blocks.py`
- Create: `tests/fixtures/sample.go`
- Create: `tests/fixtures/sample.rb`
- Create: `tests/fixtures/sample.rs`
- Create: `tests/fixtures/sample.py`
- Modify: `pyproject.toml:24-27` (add a `tests/**` per-file-ignore)

**Interfaces:**
- Produces: `tests/_paths.py` exposing `SCRIPTS` (Path to the shipped scripts
  directory) and `FIXTURES` (Path to `tests/fixtures`). Every later test file
  imports these two names.

- [x] **Step 1: Create the path helper**

`tests/_paths.py`:

```python
"""Where the tests find the shipped scripts and their fixtures.

`unittest discover -s tests` puts this directory on `sys.path`, so test
modules import this by bare name. The scripts live under `plugins/` and are
not a package -- there is no install step -- so the path is prepended here
once rather than in every test module.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "comment-review" / "skills" / "comment-review" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
```

- [x] **Step 2: Create the four fixtures**

`tests/fixtures/sample.go`:

```go
// Package fx does one thing.
// This is the package doc comment.
package fx

// Add returns the sum of a and b.
// It is exported, so this run is its documentation.
// A third line, to exceed a cap of two.
func Add(a, b int) int {
	return a + b // a trailing comment
}

// An orphan run that documents nothing, because a blank line
// and then more blank lines follow it.

var url = "http://example.com/not-a-comment"
```

`tests/fixtures/sample.rb`:

```ruby
# A leading run that documents the method below it.
# Ruby attaches docs by position, exactly like Go.
def add(a, b)
  a + b
end

=begin
A block comment spanning
two lines of prose.
=end
```

`tests/fixtures/sample.rs`:

```rust
//! A module-level doc comment.

/// Adds two numbers.
/// This is a doc comment, not an ordinary one.
pub fn add(a: i32, b: i32) -> i32 {
    // An ordinary comment inside the body.
    a + b
}
```

`tests/fixtures/sample.py`:

```python
"""A module docstring."""

CONST = 1
# A run bounded by code above it.

# A blank line does NOT end this run.
# TODO: a free marker line
result = CONST + 1  # a trailing comment


def add(a, b):
    """Add two numbers."""
    return a + b
```

- [x] **Step 3: Write the failing tests**

`tests/test_census_blocks.py`:

```python
"""The census finds every block, at the tier its language reaches."""

import unittest

from _paths import FIXTURES  # noqa: I001  -- path shim must import first

import census


def blocks_for(name):
    """Census one fixture file by name."""
    path = FIXTURES / name
    text = path.read_text(encoding="utf-8")
    lang = census.language_for(path)
    return census.census_for(path, text, lang)


class TestPythonTier(unittest.TestCase):
    def test_reaches_the_tokenized_tier(self):
        self.assertEqual(census.tier_for(census.language_for(FIXTURES / "sample.py")), "tokenized")

    def test_a_blank_line_does_not_end_a_run(self):
        runs = [b for b in blocks_for("sample.py") if b.kind == "comment"]
        self.assertEqual(len(runs), 1, [b.text for b in runs])

    def test_a_marker_line_is_free(self):
        # Three COMMENT tokens (the blank line yields NL, which is skipped and
        # never joins the run), of which the TODO line is not charged.
        run = [b for b in blocks_for("sample.py") if b.kind == "comment"][0]
        self.assertEqual(len(run.raw_lines), 3)
        self.assertEqual(run.lines, 2)

    def test_a_trailing_comment_is_its_own_block(self):
        trailing = [b for b in blocks_for("sample.py") if b.kind == "trailing-comment"]
        self.assertEqual(len(trailing), 1)
        self.assertNotIn("result", trailing[0].text)

    def test_docstrings_carry_an_owner(self):
        docs = {b.owner for b in blocks_for("sample.py") if b.kind == "docstring"}
        self.assertEqual(docs, {"<module>", "add"})


class TestLexicalTier(unittest.TestCase):
    def test_go_reaches_the_lexical_tier(self):
        self.assertEqual(census.tier_for(census.language_for(FIXTURES / "sample.go")), "lexical")

    def test_a_string_holding_a_marker_is_not_prose(self):
        texts = " ".join(b.text for b in blocks_for("sample.go"))
        self.assertNotIn("example.com", texts)

    def test_rust_doc_comments_are_docstrings(self):
        kinds = {b.kind for b in blocks_for("sample.rs")}
        self.assertIn("docstring", kinds)

    def test_rust_strips_the_longest_opener_first(self):
        docs = [b for b in blocks_for("sample.rs") if b.kind == "docstring"]
        self.assertFalse(any(b.text.startswith("/") for b in docs), [b.text for b in docs])

    def test_ruby_block_comment_is_one_block(self):
        blocks = blocks_for("sample.rb")
        begins = [b for b in blocks if "=begin" in "".join(b.raw_lines)]
        self.assertEqual(len(begins), 1)


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 4: Run the tests and record which fail**

Run: `python -m unittest discover -s tests -v`

Expected: **every test PASSES.** These assertions describe behaviour `census.py`
already documents, so a green run is the point -- this task is the net, not a
bug hunt.

! **If a test fails, do NOT relax the assertion to make it green.** A failure
means the script and its own documentation disagree, which is a finding. Report
it in your report file with the actual output and stop; the controller rules on
whether the code or the fixture is wrong.

- [x] **Step 5: Allow test files to skip docstring lint**

In `pyproject.toml`, add to `[tool.ruff.lint.per-file-ignores]` below the
existing `corpora` entry:

```toml
# Test names are the documentation here; a docstring per case restates the
# name and rots separately from it.
"tests/**" = ["D"]
```

- [x] **Step 6: Verify lint and syntax floor are clean**

Run:
```bash
ruff check . && ruff format --check . && python scripts/check_shipped_syntax.py
```
Expected: no errors.

- [x] **Step 7: Commit**

```bash
git add tests pyproject.toml
git commit -m "test(census): a stdlib fixture harness, one per language tier

No net existed under an 858-line script that ships to other people's
repositories. Every regression so far was caught by a manual sweep after
the fact. docs/parsing.md already committed to per-language fixtures.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 2: Build the name corpus from TRACKED files only

**Landed:** `7b32004` -- `git_ls_files` and `tracked_paths` in `census.py`,
`code_names(roots, tracked)` filtering to the tracked set, `path_index` on the
same helper, `main` passing it, and `tests/test_census_names.py`.
`test_an_untracked_name_does_not_mask_an_obituary` is the defect's own check.

**Why -- confirmed by measurement, 2026-08-15.** `code_names()` walks the
filesystem while `path_index()` uses `git ls-files`. In this very repository the
gitignored `corpora/` trees are therefore harvested into the live-name set:

```
# probe.py, censused with --repo .
# Uses `asanyarray` and `zzz_definitely_not_real` here.
  -> UNRESOLVED symbol `zzz_definitely_not_real` (CANDIDATE)
```

`asanyarray` exists nowhere in this repo's own source -- only in
`corpora/numpy/` -- and resolved as **alive**. This is the poisoned-name-corpus
failure the `EXCLUDED_DIRS` comment already warns about, arriving through a
route that list does not cover: any vendored, generated or gitignored tree.
It **suppresses obituaries**, which is the currency angle's highest-value
detector, and it fails silently. `path_index`'s own docstring already argues
that tracked-files-only is the more correct rule; this makes the two agree.

**Files:**
- Modify: `plugins/comment-review/skills/comment-review/scripts/census.py:523-565` (`code_names`)
- Modify: `plugins/comment-review/skills/comment-review/scripts/census.py:586-629` (`path_index`)
- Modify: `plugins/comment-review/skills/comment-review/scripts/census.py:738-742` (`main`)
- Create: `tests/test_census_names.py`

**Interfaces:**
- Consumes: `tests/_paths.py` from Task 1.
- Produces: `census.git_ls_files(repo: Path) -> list[str] | None` -- tracked
  repo-relative posix paths, or `None` when git could not answer.
  `census.code_names(roots: list[Path], tracked: set[Path] | None = None)` keeps
  its `(names, unread)` return shape.

- [x] **Step 1: Write the failing test**

`tests/test_census_names.py`:

```python
"""The name corpus is built from tracked files, so vendored code cannot mask a death."""

import subprocess
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES  # noqa: I001,F401  -- path shim must import first

import census


class TestNameCorpusScope(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # The repo is a SUBDIRECTORY of the temp dir, so the no-git case below
        # can be a sibling. A directory inside the repo is still inside a git
        # checkout, and `git -C <repo>/sub ls-files` would answer for it.
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / "tracked.py").write_text("def tracked_name():\n    pass\n")
        (self.repo / "vendored.py").write_text("def vendored_name():\n    pass\n")
        (self.repo / ".gitignore").write_text("vendored.py\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "tracked.py", ".gitignore"], check=True)
        subprocess.run(
            ["git", "-C", str(self.repo), "-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "-qm", "init"],
            check=True,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_tracked_name_is_alive(self):
        tracked = census.tracked_paths(self.repo)
        names, _ = census.code_names([self.repo], tracked)
        self.assertIn("tracked_name", names)

    def test_an_untracked_name_does_not_mask_an_obituary(self):
        tracked = census.tracked_paths(self.repo)
        names, _ = census.code_names([self.repo], tracked)
        self.assertNotIn("vendored_name", names)

    def test_no_git_falls_back_and_says_so(self):
        plain = Path(self.tmp.name) / "nogit"  # sibling of the repo, not inside it
        plain.mkdir()
        (plain / "a.py").write_text("def only_name():\n    pass\n")
        self.assertIsNone(census.git_ls_files(plain))
        names, unread = census.code_names([plain], census.tracked_paths(plain))
        self.assertIn("only_name", names)
        self.assertTrue(any("not a git" in u.lower() or "untracked" in u.lower() for u in unread))


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run it to verify it fails**

Run: `python -m unittest tests.test_census_names -v` (or
`python -m unittest discover -s tests -k names -v`)

Expected: FAIL with `AttributeError: module 'census' has no attribute 'tracked_paths'`.

- [x] **Step 3: Add the shared git helper and use it in `path_index`**

In `census.py`, insert immediately above `path_index` (around line 586):

```python
def git_ls_files(repo: Path) -> "list[str] | None":
    """Tracked, repo-relative posix paths -- or None when git cannot answer.

    None is a THIRD state, not an empty list: "this is not a git checkout" and
    "this checkout tracks nothing" lead to different fallbacks, and collapsing
    them lets a working tree with no index silently produce an empty corpus.

    Args:
        repo: the repository root.

    Returns:
        The tracked paths, or None if this is not a git repo or git is absent.
    """
    if not repo.is_dir():
        return None
    try:
        listed = subprocess.run(
            ["git", "-C", str(repo), "ls-files"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except GIT_ERRORS:
        return None
    if listed.returncode != 0:
        return None
    return listed.stdout.splitlines()


def tracked_paths(repo: Path) -> "set[Path] | None":
    """`git_ls_files` as resolved absolute paths, for membership tests."""
    rels = git_ls_files(repo)
    if rels is None:
        return None
    return {(repo / rel).resolve() for rel in rels}
```

Then replace the body of `path_index` between its docstring and the final loop
(currently lines 605-624) with:

```python
    out: set[str] = set()
    if not repo.is_dir():
        return out
    rels = git_ls_files(repo)
    if not rels:  # not a git repo, or git unavailable
        rels = [
            p.relative_to(repo).as_posix()
            for p in repo.rglob("*")
            if p.is_file() and not EXCLUDED_DIRS.intersection(p.parts)
        ]
```

Leave the trailing suffix-indexing loop unchanged.

- [x] **Step 4: Scope `code_names` to the tracked set**

Change the signature and add the filter. Replace line 523's `def` line and the
loop head (lines 531-536) with:

```python
def code_names(
    roots: list[Path], tracked: "set[Path] | None" = None
) -> tuple[set[str], list[str]]:
    """Every name the tree DEFINES, from the AST -- never from raw text.

    A corpus built from text contains the comments being checked, so every
    obituary resolves against itself and the check always passes. Unreadable
    files are RETURNED, not dropped: a hole in the corpus turns every symbol
    defined only there into a false obituary, which fails loud-and-wrong.

    ! TRACKED files only, when git can say which. A vendored, generated or
    gitignored tree under the repo root otherwise donates its whole namespace:
    measured 2026-08-15, `asanyarray` resolved ALIVE in a repo that does not
    define it, because a fetched corpus sat in the working tree. That failure
    is SILENT and one-sided -- it can only ever suppress an obituary, never
    manufacture one.

    Args:
        roots: directories or files to harvest.
        tracked: absolute paths git reports as tracked, or None when git could
            not answer -- in which case the whole tree is walked and the caller
            is told, because coverage that changes silently cannot be reported.

    Returns:
        The set of defined names, and the list of files that could not be read.
    """
    names: set[str] = set()
    unread: list[str] = []
    if tracked is None:
        unread.append(
            "name corpus built by WALKING the tree (not a git checkout, or git "
            "unavailable) -- untracked or vendored code may mask an obituary"
        )
    for root in roots:
        for p in _walk(root):
            if tracked is not None and p.resolve() not in tracked:
                continue
            lang = language_for(p)
```

The remainder of the loop body is unchanged.

- [x] **Step 5: Pass the tracked set from `main`**

In `main`, replace line 741 (`known, unread = code_names([repo])`) with:

```python
    known, unread = code_names([repo], tracked_paths(repo))
```

- [x] **Step 6: Run the tests to verify they pass**

Run: `python -m unittest discover -s tests -v`
Expected: PASS, all tests including Task 1's.

- [x] **Step 7: Confirm the original defect is gone**

Run:
```bash
printf '# Uses `asanyarray` and `zzz_not_real` here.\nx = 1\n' > /tmp/probe.py
python plugins/comment-review/skills/comment-review/scripts/census.py --repo . /tmp/probe.py 2>&1 | grep UNRESOLVED
```
Expected: **both** `asanyarray` and `zzz_not_real` now report UNRESOLVED.
Before this change only `zzz_not_real` did.

- [x] **Step 8: Commit**

```bash
ruff check . && ruff format . && python scripts/check_shipped_syntax.py
git add plugins tests
git commit -m "fix(census): harvest names from TRACKED files, as path_index already does

Measured: \`asanyarray\` resolved ALIVE in a repo that does not define it,
because a fetched corpus sat gitignored in the working tree. code_names
walked the filesystem while path_index used git ls-files; the two now
agree. The failure was silent and one-sided -- it can only suppress an
obituary, which is the currency angle's highest-value detector.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 3: Make `doc_is_structural` load-bearing -- declare the kind gap

**Landed:** `22a434d` -- `flag_structural_docs`, `flush(trailing=True)` at the
lexical tier, the `doc-kind-unresolved` mark excluded from the cap tally and
reported separately, and `compact.md`'s third kind row. Step 8 reproduced
verbatim 2026-09-02: `over cap (2): 0` and `kind unresolved, NOT counted
against the cap: 2`.

**Why -- confirmed by measurement, 2026-08-15.** `doc_is_structural` is set on
`python`, `go` and `ruby` and is **read nowhere in the file**. Go and Ruby also
declare no `doc_line`/`doc_block`, because their documentation is attached by
POSITION, so at the lexical tier every Go doc comment is classified
`kind="comment"`. Measured on a three-line `// Add returns...` doc run above
`func Add`, with `--cap 2`: `over cap (2): 1`. `compact.md` makes kind the field
that decides whether a block is LENGTH-governed (cuttable) or FORMAT-governed
(*"A cap never applies to a docstring"*), so today the cap will cut a Go export
doc -- precisely the harm the kind field exists to prevent.

The fix is **not** to detect declarations: `docs/parsing.md` forbids improvising
a parse, and that rule is right. `compact.md` already states the correct
behaviour for this case -- *"If a block arrives without its kind, stop and ask
for it -- do not infer it."* So the tier declares the gap instead of guessing.

**Files:**
- Modify: `plugins/comment-review/skills/comment-review/scripts/census.py` -- `blocks_lexical` (stamp `trailing-comment`), a new `flag_structural_docs` beside it, `census_for`, and `main`'s over-cap tally and report
- Modify: `plugins/comment-review/skills/comment-review/references/compact.md`
- Create: `tests/test_census_doc_kind.py`

! **Locate every edit by the quoted CONTENT, not by line number.** Task 2 adds
roughly forty lines to `census.py` above these sites, so every line number in
the original plan text has already shifted by the time this task runs.

**Interfaces:**
- Consumes: `tests/_paths.py`, and `census.census_for` from Task 1's tests.
- Produces: a new mark string `doc-kind-unresolved` on `Block.marks`, and
  `census.flag_structural_docs(blocks: list[Block], text: str, lang: Language) -> None`
  which mutates blocks in place.

- [x] **Step 1: Write the failing test**

`tests/test_census_doc_kind.py`:

```python
"""A language that attaches docs by POSITION declares the gap, never guesses."""

import unittest

from _paths import FIXTURES  # noqa: I001  -- path shim must import first

import census


def blocks_for(name):
    path = FIXTURES / name
    text = path.read_text(encoding="utf-8")
    return census.census_for(path, text, census.language_for(path))


class TestStructuralDocGap(unittest.TestCase):
    def test_a_run_above_code_in_go_is_marked_unresolved(self):
        above_func = [b for b in blocks_for("sample.go") if "Add returns" in b.text]
        self.assertEqual(len(above_func), 1)
        self.assertIn("doc-kind-unresolved", above_func[0].marks)

    def test_the_mark_carries_a_note_naming_the_consequence(self):
        block = [b for b in blocks_for("sample.go") if "Add returns" in b.text][0]
        self.assertTrue(any("cap" in n.lower() for n in block.notes), block.notes)

    def test_an_orphan_run_followed_by_blank_lines_is_not_marked(self):
        orphan = [b for b in blocks_for("sample.go") if "orphan run" in b.text]
        self.assertEqual(len(orphan), 1)
        self.assertNotIn("doc-kind-unresolved", orphan[0].marks)

    def test_a_lexical_trailing_comment_is_stamped(self):
        trailing = [b for b in blocks_for("sample.go") if "trailing comment" in b.text]
        self.assertEqual(len(trailing), 1)
        self.assertEqual(trailing[0].kind, "trailing-comment")

    def test_a_trailing_comment_is_never_a_structural_doc(self):
        trailing = [b for b in blocks_for("sample.go") if "trailing comment" in b.text]
        self.assertEqual(len(trailing), 1)
        self.assertNotIn("doc-kind-unresolved", trailing[0].marks)

    def test_rust_is_untouched_because_it_marks_docs_lexically(self):
        for block in blocks_for("sample.rs"):
            self.assertNotIn("doc-kind-unresolved", block.marks)

    def test_python_never_reaches_this_pass(self):
        for block in blocks_for("sample.py"):
            self.assertNotIn("doc-kind-unresolved", block.marks)


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run it to verify it fails**

Run: `python -m unittest discover -s tests -k doc_kind -v`
Expected: FAIL -- `'doc-kind-unresolved' not found in set()`.

- [x] **Step 3: Stamp `trailing-comment` at the lexical tier**

`compact.md` says *"The census stamps every block `comment`, `trailing-comment`
or `docstring`"*, but only `blocks_stdlib` ever stamps the middle one --
`blocks_lexical` calls the same `flush()` for a leading run and for a trailing
comment, so every Go/Rust/Ruby trailing comment arrives as `comment`. Step 4
needs the distinction (a trailing comment can never be a positional doc), and
the claim in `compact.md` should be true.

In `blocks_lexical`, change `flush` to take the flag, and pass it at the one
call site that handles a trailing comment:

```python
    def flush(trailing: bool = False) -> None:
        if not run:
            return
        raw = [t for _, t in run]
        stripped = raw[0].strip()
        is_doc = stripped.startswith(lang.doc_line) if lang.doc_line else False
        if lang.doc_block and stripped.startswith(lang.doc_block):
            is_doc = True
        if is_doc:
            kind = "docstring"
        else:
            kind = "trailing-comment" if trailing else "comment"
        out.append(
            Block(
                path=path.as_posix(),
                start=run[0][0],
                end=run[-1][0],
                kind=kind,
                lines=counted_lines(raw),
                text=_join(raw, openers),
                raw_lines=raw,
                tier="lexical",
            )
        )
        run.clear()
```

and at the bottom of the scan loop, where the comment already reads *"a trailing
comment is its own block, owned by this line"*:

```python
        at = min((code.index(o) for o in openers if o in code), default=-1)
        if at >= 0:
            run.append((n, raw_line[at:].rstrip()))
            flush(trailing=True)  # its own block, owned by the line it sits on
```

- [x] **Step 4: Add the post-pass**

In `census.py`, insert immediately after `blocks_lexical`:

```python
def flag_structural_docs(blocks: list[Block], text: str, lang: Language) -> None:
    """Declare, per block, that this tier cannot tell a doc from a comment.

    Go and Ruby attach documentation by POSITION -- an ordinary line comment
    directly above a declaration IS that declaration's documentation -- so
    nothing in the text distinguishes it from any other run, and no rule this
    tier can apply will separate them. Working it out by reading the file is
    the improvised parse `docs/parsing.md` refuses.

    So the block is marked as an OPEN QUESTION instead. That matters because
    `compact.md` routes on KIND: a `comment` is governed by LENGTH and may be
    cut to the cap, a `docstring` by FORMAT and may not. Left unmarked, a
    three-line Go export doc counts as over a cap of two and gets cut --
    destroying documentation that was never in violation.

    Args:
        blocks: this file's blocks, mutated in place.
        text: the file's source, for looking at what follows each run.
        lang: the language record, which decides whether this pass applies.
    """
    if not lang.doc_is_structural:
        return
    lines = text.splitlines()
    for block in blocks:
        # A trailing comment annotates the line it sits ON, so it is never the
        # documentation of what follows.
        if block.kind != "comment":
            continue
        # ! The IMMEDIATELY next line, not the next non-blank one. Both
        # languages require a doc comment to touch its declaration; a blank
        # line between them means the run documents nothing, which is an
        # ORPHAN -- a locality finding, and emphatically not a doc comment to
        # be exempted from the cap.
        nxt = lines[block.end].strip() if block.end < len(lines) else ""
        if not nxt:
            continue
        block.marks.add("doc-kind-unresolved")
        block.notes.append(
            "KIND UNRESOLVED: this run sits above code and "
            f"{lang.name} attaches docs by position, so it may be documentation "
            "governed by FORMAT rather than a comment governed by LENGTH. "
            "NOT counted against the cap. Confirm the kind before compacting."
        )
```

- [x] **Step 5: Call it from `census_for`**

Replace `census_for`'s body with:

```python
    if lang.name == "python":
        got = blocks_stdlib(path, text)
    else:
        got = blocks_lexical(path, text, lang)
        flag_structural_docs(got, text, lang)
    for b in got:
        b.tier = tier_for(lang)
    return got
```

- [x] **Step 6: Exclude the unresolved blocks from the cap tally and report them**

In `main`, replace the `over` comprehension with:

```python
    deferred = [b for b in census if "doc-kind-unresolved" in b.marks]
    over = [
        b
        for b in census
        if args.cap
        and b.kind == "comment"
        and "doc-kind-unresolved" not in b.marks
        and b.lines > args.cap
    ]
```

And immediately after the existing `if args.cap:` report line, add:

```python
        if deferred:
            print(
                f"  kind unresolved, NOT counted against the cap: {len(deferred)}"
                " -- a positional doc comment this tier cannot distinguish"
            )
```

- [x] **Step 7: Run the tests to verify they pass**

Run: `python -m unittest discover -s tests -v`
Expected: PASS.

- [x] **Step 8: Confirm the original defect is gone**

Run:
```bash
python plugins/comment-review/skills/comment-review/scripts/census.py \
  --repo . --cap 2 tests/fixtures/sample.go 2>&1 | grep -E "over cap|kind unresolved"
```
Expected: `over cap (2): 0` and `kind unresolved, NOT counted against the cap: 2`.
Before this change it read `over cap (2): 1`.

- [x] **Step 9: Teach `compact.md` the new mark, and delete nothing else**

In `references/compact.md`, in the kind table, add a third row:

```markdown
| `comment` with `doc-kind-unresolved` | **UNKNOWN** -- the census could not tell | **nothing.** Ask, or carry it at length |
```

And directly below that table, replace the sentence *"If a block arrives without
its kind, stop and ask for it -- do not infer it."* with:

```markdown
! **A block whose kind is UNRESOLVED is not a block whose kind is `comment`.**
The census stamps `doc-kind-unresolved` where a language attaches documentation
by position (Go, Ruby) and this tier cannot separate a doc run from an ordinary
one. Do not infer it from the text, and do not cut it: carry it at length and
say why. Measured: a three-line Go export doc counted as over a cap of two.
```

- [x] **Step 10: Commit**

```bash
ruff check . && ruff format . && python scripts/check_shipped_syntax.py
git add plugins tests
git commit -m "fix(census): doc_is_structural was set on three languages and read by none

Go and Ruby attach docs by position and declare no doc_line, so every Go
export doc censused as kind=comment -- and compact.md routes on kind, so a
cap cut it. Measured: a 3-line \`// Add returns...\` run above func Add
reported 'over cap (2): 1'.

The tier declares the gap rather than detecting declarations, which is the
improvised parse docs/parsing.md refuses. Marked blocks are excluded from
the cap tally and reported separately.

Also stamps trailing-comment at the lexical tier, which compact.md already
claimed the census did and only blocks_stdlib actually did.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 4: Ship the code-identity proof as a script

**Landed:** `767fd22` -- `prove_unchanged.py` (`code_signature`,
`dominant_ending`, the untouched-sibling line-ending check) and `apply.md`
losing the hand procedure. Hardened the same day by `c3609c5` (UTF-8 decode)
and `ae33321` (exact residue on shared lines, no empty proof).

**Why:** `apply.md` asks the task agent to *"Parse both versions, blank every
docstring `Constant`, compare `ast.dump`"*, to re-run it after the formatter,
and to *"Check LINE ENDINGS against an UNTOUCHED SIBLING FILE"* -- a check whose
own prose records being **measured wrong four times**. This is the single most
consequential claim the pipeline makes (*"the executable code is byte-identical"*)
and it is the one thing left to a model to perform freehand every run. It is a
pure function of two strings. The project already refuses to trust unscripted
claims of exactly this kind -- that is why `scripts/check_shipped_syntax.py`
exists.

**Files:**
- Create: `plugins/comment-review/skills/comment-review/scripts/prove_unchanged.py`
- Modify: `plugins/comment-review/skills/comment-review/references/apply.md:44-57`
- Create: `tests/test_prove_unchanged.py`

**Interfaces:**
- Consumes: `census.BY_EXT`, `census.language_for`, `census.blocks_lexical`,
  `census.git_ls_files` (Task 2).
- Produces:
  - `prove_unchanged.code_signature(text: str, path: Path) -> tuple[str, str]`
    returning `(kind, signature)` where kind is `"ast"`, `"residue"` or
    `"unprovable"`.
  - `prove_unchanged.dominant_ending(text: str) -> str` returning `"crlf"`,
    `"lf"` or `"none"`.
  - CLI: `python prove_unchanged.py --base <ref> --repo <dir> <path>...`,
    exit 0 only when every path is PROVEN.

- [x] **Step 1: Write the failing test**

`tests/test_prove_unchanged.py`:

```python
"""Code identity is proven by a script, not asserted by an agent."""

import unittest
from pathlib import Path

from _paths import FIXTURES  # noqa: I001,F401  -- path shim must import first

import prove_unchanged as pu


PY_BEFORE = '''"""Old summary."""


def add(a, b):
    """Old docstring."""
    # an old comment
    return a + b
'''

PY_COMMENT_ONLY = '''"""New summary."""


def add(a, b):
    """New docstring."""
    # a new comment
    return a + b
'''

PY_CODE_CHANGED = '''"""Old summary."""


def add(a, b):
    """Old docstring."""
    # an old comment
    return a - b
'''

GO_BEFORE = "// old doc\nfunc Add(a, b int) int {\n\treturn a + b\n}\n"
GO_COMMENT_ONLY = "// new doc\n// second line\nfunc Add(a, b int) int {\n\treturn a + b\n}\n"
GO_CODE_CHANGED = "// old doc\nfunc Add(a, b int) int {\n\treturn a - b\n}\n"


class TestPythonProof(unittest.TestCase):
    def test_prose_only_change_is_proven(self):
        path = Path("x.py")
        self.assertEqual(
            pu.code_signature(PY_BEFORE, path), pu.code_signature(PY_COMMENT_ONLY, path)
        )

    def test_a_code_change_is_caught(self):
        path = Path("x.py")
        self.assertNotEqual(
            pu.code_signature(PY_BEFORE, path), pu.code_signature(PY_CODE_CHANGED, path)
        )

    def test_the_proof_kind_is_named(self):
        kind, _ = pu.code_signature(PY_BEFORE, Path("x.py"))
        self.assertEqual(kind, "ast")


class TestLexicalProof(unittest.TestCase):
    def test_prose_only_change_is_proven(self):
        path = Path("x.go")
        self.assertEqual(
            pu.code_signature(GO_BEFORE, path), pu.code_signature(GO_COMMENT_ONLY, path)
        )

    def test_a_code_change_is_caught(self):
        path = Path("x.go")
        self.assertNotEqual(
            pu.code_signature(GO_BEFORE, path), pu.code_signature(GO_CODE_CHANGED, path)
        )

    def test_the_proof_kind_is_named(self):
        kind, _ = pu.code_signature(GO_BEFORE, Path("x.go"))
        self.assertEqual(kind, "residue")


class TestUnprovable(unittest.TestCase):
    def test_an_unknown_suffix_is_reported_not_passed(self):
        kind, _ = pu.code_signature("whatever\n", Path("x.zzz"))
        self.assertEqual(kind, "unprovable")

    def test_a_syntax_error_falls_back_to_residue_not_to_success(self):
        kind, _ = pu.code_signature("def (:\n", Path("x.py"))
        self.assertIn(kind, ("residue", "unprovable"))


class TestLineEndings(unittest.TestCase):
    def test_crlf_detected(self):
        self.assertEqual(pu.dominant_ending("a\r\nb\r\n"), "crlf")

    def test_lf_detected(self):
        self.assertEqual(pu.dominant_ending("a\nb\n"), "lf")

    def test_a_flip_is_visible(self):
        self.assertNotEqual(pu.dominant_ending("a\r\n"), pu.dominant_ending("a\n"))


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run it to verify it fails**

Run: `python -m unittest discover -s tests -k prove -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'prove_unchanged'`.

- [x] **Step 3: Write the script**

`plugins/comment-review/skills/comment-review/scripts/prove_unchanged.py`:

```python
"""Prove a comment-review sweep changed no executable code. Stage 7b's gate.

    python prove_unchanged.py --base <ref> [--repo D] <paths...>

Exits nonzero unless EVERY path is proven. The claim this skill makes to the
people who run it is that prose changed and code did not; that claim is a pure
function of two strings and must not rest on an agent performing it carefully.

Two proofs, because two tiers:

  ast       Python. Parse both, blank every docstring, compare `ast.dump`.
            Comments never reach the AST, so anything else that differs fails.
  residue   Any language with a `LANGUAGES` record. Delete every comment block
            the census finds, compare what remains, byte for byte.

! A file this cannot prove is REPORTED as unprovable, never passed. A proof
that quietly degrades to "looks fine" is worse than no proof, because the
report still says PROVEN.

! Line endings are checked against an UNTOUCHED SIBLING, never against the
stored blob: under `core.autocrlf` the blob is always LF, so normalising to it
leaves the working tree inconsistent with every file the sweep did not touch --
and `git diff` hides it. Measured four times.
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from census import (  # noqa: E402  -- path shim must run first
    GIT_ERRORS,
    blocks_lexical,
    git_ls_files,
    language_for,
)

READ_ERRORS = (OSError, UnicodeDecodeError)
DOC_OWNERS = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _blank_docstrings(tree: ast.AST) -> ast.AST:
    """Replace every docstring's value with an empty string, in place.

    A docstring is prose this skill is allowed to rewrite, so its CONTENT must
    not enter the signature. Its presence still does: deleting a docstring
    entirely changes the body's shape and stays visible.
    """
    for node in ast.walk(tree):
        if not isinstance(node, DOC_OWNERS):
            continue
        if not node.body:
            continue
        first = node.body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
            if isinstance(first.value.value, str):
                first.value.value = ""
    return tree


def _residue(text: str, path: Path) -> str | None:
    """The file with every comment block removed, or None if unreadable here."""
    lang = language_for(path)
    if lang is None:
        return None
    try:
        blocks = blocks_lexical(path, text, lang)
    except Exception:  # noqa: BLE001  -- an unprovable file is reported, not passed
        return None
    drop: set[int] = set()
    for block in blocks:
        for n in range(block.start, block.end + 1):
            drop.add(n)
    kept = [
        line for i, line in enumerate(text.splitlines(), 1) if i not in drop
    ]
    return "\n".join(line.rstrip() for line in kept if line.strip())


def code_signature(text: str, path: Path) -> tuple[str, str]:
    """A value equal for two texts exactly when their executable code matches.

    Args:
        text: the file's contents.
        path: used only for its suffix, to pick the proof.

    Returns:
        `(kind, signature)`. `kind` is "ast", "residue" or "unprovable"; an
        unprovable file carries an empty signature and must never be reported
        as proven.
    """
    if path.suffix.lower() in (".py", ".pyi"):
        try:
            return "ast", ast.dump(_blank_docstrings(ast.parse(text)))
        except SyntaxError:
            pass  # fall through to residue; a broken parse proves nothing
    residue = _residue(text, path)
    if residue is None:
        return "unprovable", ""
    return "residue", residue


def dominant_ending(text: str) -> str:
    """Which line ending this text mostly uses: "crlf", "lf" or "none"."""
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    if crlf == 0 and lf == 0:
        return "none"
    return "crlf" if crlf >= lf else "lf"


def _show(repo: Path, ref: str, rel: str) -> str | None:
    """`git show <ref>:<rel>`, or None when git cannot produce it."""
    try:
        got = subprocess.run(
            ["git", "-C", str(repo), "show", f"{ref}:{rel}"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except GIT_ERRORS:
        return None
    return got.stdout if got.returncode == 0 else None


def _sibling(repo: Path, target: Path, edited: set[Path]) -> Path | None:
    """A tracked file beside `target` that this sweep did not edit."""
    rels = git_ls_files(repo) or []
    for rel in rels:
        cand = (repo / rel).resolve()
        if cand.parent == target.parent and cand not in edited and cand != target:
            return cand
    return None


def main() -> int:
    """Prove every named path, and report what could not be proven."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--base", required=True, help="ref holding the pre-edit text")
    ap.add_argument("--repo", default=".", help="repo root")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    edited = {Path(p).resolve() for p in args.paths}
    failures = 0

    for raw in args.paths:
        target = Path(raw).resolve()
        try:
            rel = target.relative_to(repo).as_posix()
        except ValueError:
            print(f"FAIL      {raw}: outside --repo")
            failures += 1
            continue

        before = _show(repo, args.base, rel)
        if before is None:
            print(f"UNPROVABLE {rel}: no {args.base}:{rel} -- new file, or bad ref")
            failures += 1
            continue
        try:
            after = target.read_text(encoding="utf-8")
        except READ_ERRORS as e:
            print(f"FAIL      {rel}: {type(e).__name__}")
            failures += 1
            continue

        kind_b, sig_b = code_signature(before, target)
        kind_a, sig_a = code_signature(after, target)
        if kind_a == "unprovable" or kind_b == "unprovable":
            print(f"UNPROVABLE {rel}: no language record -- code identity NOT shown")
            failures += 1
        elif sig_a != sig_b:
            print(f"FAIL      {rel}: executable code DIFFERS ({kind_a} proof)")
            failures += 1
        else:
            print(f"PROVEN    {rel}: code identical ({kind_a} proof)")

        sib = _sibling(repo, target, edited)
        if sib is None:
            print(f"          {rel}: no untouched sibling -- line endings UNCHECKED")
        else:
            try:
                want = dominant_ending(sib.read_text(encoding="utf-8", newline=""))
            except READ_ERRORS:
                want = "none"
            got = dominant_ending(after)
            if want != "none" and got != want:
                print(f"FAIL      {rel}: line endings {got}, sibling {sib.name} {want}")
                failures += 1

    print()
    if failures:
        print(f"{failures} unproven. The sweep's identity claim does NOT hold.")
        return 1
    print(f"{len(args.paths)} paths proven: prose changed, executable code did not.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest discover -s tests -v`
Expected: PASS.

- [x] **Step 5: Replace the hand-execution prose in `apply.md`**

In `references/apply.md`, replace the block from *"**Prove code identity; do not
assert it.**"* through the end of the `! **The stored blob is the wrong baseline...**`
paragraph (lines 44-57) with:

```markdown
**Prove code identity; do not assert it.** Run the proof -- do not perform it:

```bash
python <skill>/scripts/prove_unchanged.py --base <merge-base> --repo . <paths...>
```

It exits nonzero unless every path is proven, and it reports an **unprovable**
file rather than passing it. It carries the AST proof for Python, a
comment-stripped byte comparison for every other language with a `LANGUAGES`
record, and the line-ending check against an untouched sibling. ! **Re-run it
after the formatter** -- the formatter can reshape what you wrote.

! **A `FAIL` or `UNPROVABLE` line is a stop, not a note.** The identity claim is
what this skill promises the people who run it; report the line verbatim and
restore the file.
```

- [x] **Step 6: Verify the script runs against a real edit**

Run:
```bash
git stash list >/dev/null 2>&1
python plugins/comment-review/skills/comment-review/scripts/prove_unchanged.py \
  --base HEAD --repo . plugins/comment-review/skills/comment-review/scripts/census.py
```
Expected: with a clean tree, `PROVEN` and exit 0. (If census.py has uncommitted
prose edits from Tasks 2-3, it should still read PROVEN -- that is the point.)

- [x] **Step 7: Commit**

```bash
ruff check . && ruff format . && python scripts/check_shipped_syntax.py
git add plugins tests
git commit -m "feat(apply): ship the code-identity proof instead of describing it

The sweep's central claim -- prose changed, code did not -- was performed
freehand by the task agent every run, including a line-ending check whose
own prose records being measured wrong four times. It is a pure function of
two strings.

Python gets the AST proof; every other language with a LANGUAGES record
gets a comment-stripped byte comparison. A file that cannot be proven is
REPORTED, never passed. apply.md loses the procedure it used to carry.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 5: `referrers.py` -- the missing inbound half of stage 3

**Landed:** `fb9b2d1` -- `referrers.py` (`tokens_for`, the `NOISE_FLOOR`
suppression) and `SKILL.md` stage 3's inbound half, which now runs in `target`
mode too. Hardened by `efd9724`, `4c79558`, `576a656` and `404029c`.

**Why:** Stage 3 is called FIND REFERENCES and finds only *outbound* ones --
what a comment cites. The inbound direction (who cites the code under review) is
a single prose instruction at `SKILL.md:429`, and it **explicitly does not apply
in `target` mode**: *"Under `target` there is no diff; the named path is the
whole scope and this widening does not apply."* So `/comment-review full path/to/file.py`
-- the invocation a person reaches for first -- gets **zero** backlink discovery,
and the REFERENCE ONLY list is assembled from the task agent's memory of the
repo. Measured consequence already recorded in `SKILL.md`: one unreviewed config
file held 12 confirmed defects, six of them the same rewrite already applied in
a `.py` file.

**Files:**
- Create: `plugins/comment-review/skills/comment-review/scripts/referrers.py`
- Modify: `plugins/comment-review/skills/comment-review/SKILL.md:426-432`
- Create: `tests/test_referrers.py`

**Interfaces:**
- Consumes: `census.git_ls_files` (Task 2), `census.language_for`.
- Produces:
  - `referrers.tokens_for(path: Path, text: str) -> set[str]` -- the names by
    which prose elsewhere would refer to this file.
  - CLI: `python referrers.py --repo <dir> <target>...` printing a
    REFERENCE-ONLY candidate list. Always exits 0 -- it is an input to a review.

- [x] **Step 1: Write the failing test**

`tests/test_referrers.py`:

```python
"""Who names this file? The inbound half of FIND REFERENCES."""

import unittest
from pathlib import Path

from _paths import FIXTURES  # noqa: I001,F401  -- path shim must import first

import referrers


PY = '''"""A module."""


def visible_helper():
    pass


class VisibleThing:
    def _private(self):
        pass


def _hidden():
    pass
'''


class TestTokens(unittest.TestCase):
    def test_the_stem_is_a_token(self):
        self.assertIn("rates", referrers.tokens_for(Path("billing/rates.py"), PY))

    def test_the_posix_path_is_a_token(self):
        self.assertIn("billing/rates.py", referrers.tokens_for(Path("billing/rates.py"), PY))

    def test_top_level_names_are_tokens(self):
        got = referrers.tokens_for(Path("billing/rates.py"), PY)
        self.assertIn("visible_helper", got)
        self.assertIn("VisibleThing", got)

    def test_underscored_names_are_not_tokens(self):
        got = referrers.tokens_for(Path("billing/rates.py"), PY)
        self.assertNotIn("_hidden", got)
        self.assertNotIn("_private", got)

    def test_a_non_python_file_still_yields_its_path_tokens(self):
        got = referrers.tokens_for(Path("config/app.toml"), "key = 1\n")
        self.assertIn("app", got)
        self.assertIn("config/app.toml", got)


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run it to verify it fails**

Run: `python -m unittest discover -s tests -k referrers -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'referrers'`.

- [x] **Step 3: Write the script**

`plugins/comment-review/skills/comment-review/scripts/referrers.py`:

```python
"""Stage 3, inbound: which tracked files NAME the files under review.

    python referrers.py --repo D <targets...>

The census resolves what a comment CITES. This resolves the other direction --
who cites the code being edited -- and it is the half that decides the
REFERENCE ONLY list. Without it that list is assembled from memory, and a
`target` run has no diff to widen from at all.

Read-only, and always exits 0: this is an input to a review, not a gate. Every
line it prints is a CANDIDATE. A file that names a token is a file to READ, not
a file with a defect, and not a file a verdict may target.

! A token too common to discriminate is reported as SUPPRESSED with its hit
count, never dumped. A detector below roughly 10% precision buries its own
hits, so the list a human is asked to read must stay readable.
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from census import GIT_ERRORS, git_ls_files  # noqa: E402  -- path shim first

PARSE_ERRORS = (OSError, UnicodeDecodeError, SyntaxError)
NAMED_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

# Above this many hits a token is describing the codebase, not this file.
NOISE_FLOOR = 40


def tokens_for(path: Path, text: str) -> set[str]:
    """Every name by which prose elsewhere would refer to this file.

    Args:
        path: the file's repo-relative path.
        text: its contents, parsed for top-level names when it is Python.

    Returns:
        The stem, the posix path and each of its trailing suffixes, and the
        PUBLIC top-level definitions. Underscored names are excluded: prose
        does not cite them, and they collide with unrelated private helpers.
    """
    out = {path.stem}
    parts = path.as_posix().split("/")
    for i in range(len(parts)):
        out.add("/".join(parts[i:]))
    if path.suffix.lower() in (".py", ".pyi"):
        try:
            tree = ast.parse(text)
        except PARSE_ERRORS:
            return out
        for node in tree.body:
            if isinstance(node, NAMED_DEFS) and not node.name.startswith("_"):
                out.add(node.name)
    return {t for t in out if len(t) > 2}


def _grep(repo: Path, token: str) -> list[str]:
    """Tracked files containing `token` as a fixed string.

    ! The encoding is PINNED. git emits UTF-8; `text=True` alone decodes with
    whatever locale the user's machine has, and a non-ASCII path then arrives
    corrupted -- so a real referrer is reported under a name that resolves to
    nothing. Measured on this repo's own `cp1252` machine against the same
    construct in `prove_unchanged.py`.
    """
    try:
        got = subprocess.run(
            ["git", "-C", str(repo), "grep", "-l", "-F", "--", token],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
    except GIT_ERRORS:
        return []
    return got.stdout.splitlines() if got.returncode == 0 else []


def main() -> int:
    """Print the REFERENCE ONLY candidates for the named targets."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--repo", default=".", help="repo root")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if git_ls_files(repo) is None:
        print("NO GIT INDEX -- cannot resolve referrers. Say so in the stage 3 report.")
        return 0

    under_review = set()
    for raw in args.targets:
        try:
            under_review.add(Path(raw).resolve().relative_to(repo).as_posix())
        except ValueError:
            print(f"  skipped {raw}: outside --repo")

    hits: dict[str, set[str]] = defaultdict(set)
    suppressed: list[str] = []
    for rel in sorted(under_review):
        target = repo / rel
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            text = ""
        for token in sorted(tokens_for(Path(rel), text)):
            found = [f for f in _grep(repo, token) if f not in under_review]
            if len(found) > NOISE_FLOOR:
                suppressed.append(f"{token} ({len(found)} files)")
                continue
            for f in found:
                hits[f].add(token)

    print(f"REFERENCE ONLY candidates for {len(under_review)} file(s) under review")
    print("Every line is a file to READ. None of them may be the target of a verdict.\n")
    if not hits:
        print("  none -- nothing tracked names these files.")
    for f in sorted(hits):
        print(f"  {f}\n      names: {', '.join(sorted(hits[f]))}")
    if suppressed:
        print("\nSUPPRESSED -- too common to discriminate, triage by hand if needed:")
        for s in suppressed:
            print(f"  {s}")
    print(
        "\n! CANDIDATES, not findings. A file here is REFERENCE ONLY unless it is "
        "also under review."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest discover -s tests -v`
Expected: PASS.

- [x] **Step 5: Verify against this repository**

Run:
```bash
python plugins/comment-review/skills/comment-review/scripts/referrers.py \
  --repo . plugins/comment-review/skills/comment-review/scripts/census.py
```
Expected: names `SKILL.md`, `docs/parsing.md`, `README.md` and the reference
files among the candidates -- the documents that actually discuss census.py.

- [x] **Step 6: Wire it into `SKILL.md` stage 3, replacing the prose rule**

In `SKILL.md`, replace the paragraph at lines 426-432 (*"! **Scope by SUBJECT,
not by file extension.**..."* through *"...this widening does not apply."*) with:

```markdown
! **Scope by SUBJECT, not by file extension**, and resolve it with the tool
rather than from memory -- this is the INBOUND half of stage 3:

```bash
python <skill>/scripts/referrers.py --repo . <paths under review...>
```

It prints every tracked file that NAMES one of them -- by path, by stem, or by a
public top-level definition -- and suppresses a token too common to discriminate
rather than dumping it. Those files are the **REFERENCE ONLY** list you hand the
reviewers at stage 4; a config, data or documentation file carrying prose that
justifies a value is a node like any other. Measured: one unreviewed config file
held 12 confirmed defects, six of them the same rewrite the pass had already
applied in a `.py` file.

!! **This runs in `target` mode too.** A `target` run has no diff to widen from,
which is exactly why the memory-based rule it replaces could not fire there --
the invocation most likely to be typed by hand was the one with no backlink
discovery at all.
```

- [x] **Step 7: Commit**

```bash
ruff check . && ruff format . && python scripts/check_shipped_syntax.py
git add plugins tests
git commit -m "feat(census): resolve INBOUND references, the missing half of stage 3

Stage 3 resolved what a comment cites and nothing about who cites the code
under review. That direction was one prose instruction that explicitly did
not apply in target mode -- so the invocation people type by hand had zero
backlink discovery and REFERENCE ONLY was assembled from memory.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

# PHASE B -- the pipeline contract

Phase B changes what reviewers emit and how stages are dispatched. Land Phase A
first and re-measure the corpora, so a change in finding rate is attributable.

## Task 6: A parseable finding record, and `verdicts.py` to join it

**Landed:** `5f14da7` -- `verdicts.py` carrying all six checks (coverage,
evidence, payload, level, contradiction, the clean-arithmetic), the RECORD
format in `reviewer-brief.md`, and the gate in `SKILL.md`. Hardened by
`aa5adfe` and `ffcf695`, which closed four ways past the gate.

**Why -- this is the highest-value item in the plan.** `SKILL.md:485-490`
instructs the task agent to *"Open each finding's `SUMMARY` right half and
confirm the quoted line is within a few lines of its citation"*, because
**one graded run had fabricated 5 of its 7 reviewer reports**. It also asks the
agent to compute, by hand, across four reviewers x N blocks: coverage gaps
(*"a block nobody mentioned is a gap"*), contradictions (`drop` vs `correct`),
payload completeness, level legality, and the clean-arithmetic (*"every angle
that RAN"*). All six of those are mechanical. None is checked today.

The blocker is that findings are free prose. The brief already mandates a rigid
five-part shape -- this makes it *parseable* and adds the two fields the checks
need: the census **BLOCK** index (enables the join) and an **EVIDENCE**
`file:line` (enables the fabrication check).

It also adds a `CLEAN` range line. Without one, the module-coherence reviewer --
whose own agent file says it will return clean on ~500 blocks -- must emit 500
full records, and *that* is why coverage walking degrades in practice.

**Files:**
- Create: `plugins/comment-review/skills/comment-review/scripts/verdicts.py`
- Modify: `plugins/comment-review/skills/comment-review/references/reviewer-brief.md:39-52`
- Modify: `plugins/comment-review/skills/comment-review/SKILL.md:483-499`
- Create: `tests/test_verdicts.py`

**Interfaces:**
- Consumes: the census JSON from `census.py --json`.
- Produces:
  - `verdicts.parse_report(text: str, angle: str) -> tuple[list[Finding], set[int]]`
    returning findings and the set of block indices declared clean.
  - `verdicts.Finding` -- a dataclass with `angle, block, verdict, location,
    evidence, summary, finding, change`.
  - CLI: `python verdicts.py --census <census.json> --level <level> <report>...`
    exiting nonzero on any coverage gap, unverifiable evidence, missing payload
    or illegal-at-level verdict.

- [x] **Step 1: Define the record format in the brief**

In `references/reviewer-brief.md`, replace the "Every finding has five parts"
fenced block and the paragraph under it (lines 39-52) with:

```markdown
## Every finding is a RECORD, and it is parsed

Emit findings in exactly this shape. A tool joins your report against the
census and against the other angles', so a malformed record is a finding that
does not count.

```
--- FINDING
BLOCK       17
VERDICT     correct
LOCATION    redacted_pkg/billing/rates.py:342-347
EVIDENCE    redacted_pkg/billing/rates.py:355
SUMMARY     "kept because twenty call sites want this" || 31 callers, all under tests/
FINDING     the count is stale and every caller is a test
CHANGE      false: "twenty call sites want this" / true: "31 callers, all in tests/"
---
```

| field | what it carries |
| --- | --- |
| `BLOCK` | the census INDEX. This is how coverage is checked; a finding without it is unattributable |
| `VERDICT` | one of the nine, and one your LEVEL carries |
| `LOCATION` | `file:start-end` of the prose |
| `EVIDENCE` | `file:line` of the code that SETTLES the claim -- **verified to exist, and to say what you quoted** |
| `SUMMARY` | the claim as written, quoted `\|\|` the code line that settles it |
| `FINDING` | what is wrong, one clause |
| `CHANGE` | the payload the verdict table requires |

**Then account for every remaining block on one line:**

```
CLEAN 1-16,18,20-45,47
```

!! **`EVIDENCE` is the forcing function, and it is now CHECKED.** The line is
read out of the file and compared against your `SUMMARY`'s right half. Measured:
one graded run had **fabricated 5 of its 7 reviewer reports**, and a
self-certified confidence label ran at **97% across 298 findings**. A citation
that does not resolve is not a weaker finding -- it is not a finding.

! **`CLEAN` is a range list, not an invitation to skip.** Every census index
must appear exactly once across your findings and your clean ranges. The join
reports any index you did not account for as a COVERAGE GAP against your angle
by name.
```

- [x] **Step 2: Write the failing test**

`tests/test_verdicts.py`:

```python
"""The census join, the evidence check, and the clean arithmetic -- mechanically."""

import json
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES  # noqa: I001,F401  -- path shim must import first

import verdicts


REPORT = """
Some preamble the tool ignores.

--- FINDING
BLOCK       1
VERDICT     correct
LOCATION    a.py:1-2
EVIDENCE    a.py:5
SUMMARY     "only one caller" || three callers here
FINDING     the count is wrong
CHANGE      false: "only one caller" / true: "three callers"
---

CLEAN 2-3
"""


class TestParsing(unittest.TestCase):
    def test_a_record_is_parsed(self):
        found, clean = verdicts.parse_report(REPORT, "currency")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].block, 1)
        self.assertEqual(found[0].verdict, "correct")
        self.assertEqual(found[0].evidence, "a.py:5")

    def test_clean_ranges_expand(self):
        _, clean = verdicts.parse_report(REPORT, "currency")
        self.assertEqual(clean, {2, 3})

    def test_the_angle_is_attached(self):
        found, _ = verdicts.parse_report(REPORT, "currency")
        self.assertEqual(found[0].angle, "currency")


class TestCoverage(unittest.TestCase):
    def test_an_unaccounted_block_is_a_gap(self):
        gaps = verdicts.coverage_gaps({1, 2, 3, 4}, {"currency": {2, 3}}, [
            verdicts.Finding("currency", 1, "correct", "a.py:1-2", "a.py:5", "x", "y", "z")
        ])
        self.assertEqual(gaps, {"currency": [4]})

    def test_full_coverage_reports_no_gap(self):
        gaps = verdicts.coverage_gaps({1, 2}, {"currency": {2}}, [
            verdicts.Finding("currency", 1, "clean", "", "", "", "", "")
        ])
        self.assertEqual(gaps, {})


class TestPayload(unittest.TestCase):
    def test_correct_without_a_pair_is_rejected(self):
        f = verdicts.Finding("currency", 1, "correct", "a.py:1", "a.py:5", "s", "f", "fix it")
        self.assertIn("true/false pair", verdicts.payload_problem(f))

    def test_correct_with_a_pair_passes(self):
        f = verdicts.Finding(
            "currency", 1, "correct", "a.py:1", "a.py:5", "s", "f",
            'false: "a" / true: "b"',
        )
        self.assertIsNone(verdicts.payload_problem(f))

    def test_add_without_an_anchor_is_rejected(self):
        f = verdicts.Finding("locality", 1, "add", "a.py:1", "a.py:5", "s", "f", "some text")
        self.assertIn("anchor", verdicts.payload_problem(f))


class TestLevel(unittest.TestCase):
    def test_patch_is_illegal_at_fact_check(self):
        self.assertFalse(verdicts.allowed("patch", "fact-check"))

    def test_correct_is_legal_at_every_level(self):
        for level in ("fact-check", "line", "full"):
            self.assertTrue(verdicts.allowed("correct", level))

    def test_reanchor_needs_line(self):
        self.assertFalse(verdicts.allowed("reanchor", "fact-check"))
        self.assertTrue(verdicts.allowed("reanchor", "line"))


class TestContradiction(unittest.TestCase):
    def test_drop_against_correct_is_flagged(self):
        found = [
            verdicts.Finding("locality", 7, "drop", "a.py:1", "a.py:5", "s", "f", "c"),
            verdicts.Finding("currency", 7, "correct", "a.py:1", "a.py:5", "s", "f", "c"),
        ]
        self.assertEqual(verdicts.contradictions(found), [7])

    def test_drop_alone_is_not_a_contradiction(self):
        found = [verdicts.Finding("locality", 7, "drop", "a.py:1", "a.py:5", "s", "f", "c")]
        self.assertEqual(verdicts.contradictions(found), [])


class TestEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "a.py").write_text("one\ntwo\nthree\nfour\nthe settling line\nsix\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_resolvable_citation_passes(self):
        f = verdicts.Finding(
            "currency", 1, "correct", "a.py:1", "a.py:5",
            'x || the settling line', "f", "c",
        )
        self.assertIsNone(verdicts.evidence_problem(f, self.repo))

    def test_a_missing_file_is_caught(self):
        f = verdicts.Finding("currency", 1, "correct", "a.py:1", "gone.py:5", "x || y", "f", "c")
        self.assertIn("does not resolve", verdicts.evidence_problem(f, self.repo))

    def test_a_line_past_the_end_is_caught(self):
        f = verdicts.Finding("currency", 1, "correct", "a.py:1", "a.py:900", "x || y", "f", "c")
        self.assertIn("900", verdicts.evidence_problem(f, self.repo))

    def test_a_quote_that_is_not_there_is_caught(self):
        f = verdicts.Finding(
            "currency", 1, "correct", "a.py:1", "a.py:5",
            "x || a line that appears nowhere at all", "f", "c",
        )
        self.assertIn("not found near", verdicts.evidence_problem(f, self.repo))


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 3: Run it to verify it fails**

Run: `python -m unittest discover -s tests -k verdicts -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'verdicts'`.

- [x] **Step 4: Write the script**

`plugins/comment-review/skills/comment-review/scripts/verdicts.py`:

```python
"""Stage 5's gate: join four reviewers' reports against the census.

    python verdicts.py --census census.json --level full --repo D <report>...

Six checks the task agent was asked to perform by hand, every one mechanical:

  COVERAGE      every census index accounted for, by every angle that ran
  EVIDENCE      each finding's citation resolves, and says what was quoted
  PAYLOAD       the verdict carries what its row of the table requires
  LEVEL         the verdict is one this run's level carries
  CONTRADICTION `drop` against `correct`/`patch` on one block -- a re-review
  STANDS        blocks every angle that ran returned clean on

! Exits nonzero on a coverage gap or an unverifiable citation. Measured: one
graded run had FABRICATED 5 of its 7 reviewer reports and did not notice until
asked to grade itself. A report is not evidence that a file was read.

! It cannot tell a correct verdict from an incorrect one. It tells you which
findings are ADMISSIBLE. Ruling remains stage 5's, and the synthesis order in
SKILL.md is unchanged.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

READ_ERRORS = (OSError, UnicodeDecodeError)

VERDICTS = (
    "clean",
    "query",
    "drop",
    "correct",
    "patch",
    "add",
    "move",
    "reanchor",
    "split",
)

# What each level ADDS to the one above it, per SKILL.md's level table.
LEVELS = {
    "fact-check": {"correct", "query", "clean"},
    "line": {"correct", "query", "clean", "drop", "move", "reanchor", "split", "add"},
    "full": set(VERDICTS),
    "proof": set(),
}

RECORD = re.compile(r"^---\s*FINDING\s*$(.*?)^---\s*$", re.M | re.S)
FIELD = re.compile(r"^\s*(BLOCK|VERDICT|LOCATION|EVIDENCE|SUMMARY|FINDING|CHANGE)\s+(.*)$")
CLEAN_LINE = re.compile(r"^\s*CLEAN\s+([\d,\s-]+)$", re.M)
CITE = re.compile(r"^(.+?):(\d+)$")

# How far from the cited line the quoted text may sit. Prose wraps and code
# moves; a hard equality would reject honest citations, and a wide window would
# accept a fabricated one.
EVIDENCE_WINDOW = 3


@dataclass
class Finding:
    """One reviewer's ruling on one census block."""

    angle: str
    block: int
    verdict: str
    location: str
    evidence: str
    summary: str
    finding: str
    change: str


def _expand(ranges: str) -> set[int]:
    """`"1-3,7"` to `{1, 2, 3, 7}`."""
    out: set[int] = set()
    for part in ranges.replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            lo, _, hi = part.partition("-")
            if lo.isdigit() and hi.isdigit():
                out.update(range(int(lo), int(hi) + 1))
        elif part.isdigit():
            out.add(int(part))
    return out


def parse_report(text: str, angle: str) -> tuple[list[Finding], set[int]]:
    """Findings and clean-block indices from one reviewer's report.

    Args:
        text: the report as the reviewer returned it. Prose around the records
            is ignored, so a reviewer may still explain itself.
        angle: the reviewer's name, attached to every finding it produced.

    Returns:
        The parsed findings, and the set of indices declared clean by range.
    """
    found: list[Finding] = []
    for body in RECORD.findall(text):
        fields: dict[str, str] = {}
        for line in body.splitlines():
            m = FIELD.match(line)
            if m:
                fields[m.group(1)] = m.group(2).strip()
        raw_block = fields.get("BLOCK", "")
        found.append(
            Finding(
                angle=angle,
                block=int(raw_block) if raw_block.isdigit() else -1,
                verdict=fields.get("VERDICT", "").strip().lower(),
                location=fields.get("LOCATION", ""),
                evidence=fields.get("EVIDENCE", ""),
                summary=fields.get("SUMMARY", ""),
                finding=fields.get("FINDING", ""),
                change=fields.get("CHANGE", ""),
            )
        )
    clean: set[int] = set()
    for ranges in CLEAN_LINE.findall(text):
        clean |= _expand(ranges)
    return found, clean


def coverage_gaps(
    all_blocks: set[int], clean: dict[str, set[int]], found: list[Finding]
) -> dict[str, list[int]]:
    """Indices each angle never accounted for. A gap is not a pass."""
    by_angle: dict[str, set[int]] = defaultdict(set)
    for f in found:
        by_angle[f.angle].add(f.block)
    gaps: dict[str, list[int]] = {}
    for angle in set(list(clean) + list(by_angle)):
        missing = sorted(all_blocks - by_angle[angle] - clean.get(angle, set()))
        if missing:
            gaps[angle] = missing
    return gaps


def allowed(verdict: str, level: str) -> bool:
    """Does this run's level carry this verdict?"""
    return verdict in LEVELS.get(level, set())


def payload_problem(f: Finding) -> str | None:
    """What the verdict's required payload is missing, or None."""
    change = f.change.lower()
    if f.verdict == "correct" and not ("false:" in change and "true:" in change):
        return "correct needs a true/false pair in CHANGE"
    if f.verdict == "add" and "anchor" not in change and "above" not in change and "below" not in change:
        return "add needs an anchor (which declaration, above or below)"
    if f.verdict == "move" and "->" not in change and " to " not in change:
        return "move needs a destination and the verbatim extract"
    if f.verdict == "reanchor" and not change.strip():
        return "reanchor needs the declaration it constrains"
    if f.verdict == "split" and change.count("/") < 1:
        return "split needs each fragment and its own anchor"
    if f.verdict not in ("clean",) and not f.change.strip():
        return f"{f.verdict} carries no payload -- the judgement was handed back"
    return None


def evidence_problem(f: Finding, repo: Path) -> str | None:
    """Why this finding's citation cannot be trusted, or None.

    Reads the cited line out of the file and looks for the SUMMARY's right half
    within a few lines of it. A finding whose evidence is not there is not a
    finding -- the report is not evidence that the file was read.
    """
    if f.verdict == "clean":
        return None
    m = CITE.match(f.evidence.strip())
    if not m:
        return f"EVIDENCE {f.evidence!r} is not file:line"
    target, lineno = repo / m.group(1), int(m.group(2))
    if not target.is_file():
        return f"EVIDENCE {f.evidence} does not resolve to a file"
    try:
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    except READ_ERRORS as e:
        return f"EVIDENCE unreadable ({type(e).__name__})"
    if lineno > len(lines):
        return f"EVIDENCE line {lineno} is past the end of {m.group(1)} ({len(lines)} lines)"
    _, _, right = f.summary.partition("||")
    needle = " ".join(right.split()).strip().strip('"')
    if not needle:
        return "SUMMARY has no right half -- nothing was checked against the code"
    lo = max(0, lineno - 1 - EVIDENCE_WINDOW)
    window = " ".join(" ".join(ln.split()) for ln in lines[lo : lineno + EVIDENCE_WINDOW])
    head = needle[:40]
    if head.lower() not in window.lower():
        return f"quoted evidence not found near {f.evidence}: {head!r}"
    return None


def contradictions(found: list[Finding]) -> list[int]:
    """Blocks where one angle says delete and another says fix. Re-review."""
    by_block: dict[int, set[str]] = defaultdict(set)
    for f in found:
        by_block[f.block].add(f.verdict)
    return sorted(
        b for b, vs in by_block.items() if "drop" in vs and ({"correct", "patch"} & vs)
    )


def main() -> int:
    """Join the reports, report what is inadmissible, and gate on it."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("reports", nargs="+", help="one report file per angle")
    ap.add_argument("--census", required=True, help="census.py --json output")
    ap.add_argument("--level", default="full", choices=sorted(LEVELS))
    ap.add_argument("--repo", default=".", help="repo root for evidence resolution")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    blocks = json.loads(Path(args.census).read_text(encoding="utf-8"))
    all_blocks = set(range(1, len(blocks) + 1))

    found: list[Finding] = []
    clean: dict[str, set[int]] = {}
    for raw in args.reports:
        path = Path(raw)
        angle = path.stem
        got, cl = parse_report(path.read_text(encoding="utf-8"), angle)
        found.extend(got)
        clean[angle] = cl

    print(f"{len(found)} findings from {len(args.reports)} angles over {len(blocks)} blocks\n")

    fatal = 0
    gaps = coverage_gaps(all_blocks, clean, found)
    if gaps:
        print("COVERAGE GAPS -- a block nobody mentioned is a gap, not a pass:")
        for angle, missing in sorted(gaps.items()):
            shown = ", ".join(str(n) for n in missing[:20])
            more = f" (+{len(missing) - 20} more)" if len(missing) > 20 else ""
            print(f"  {angle}: {len(missing)} unaccounted -- {shown}{more}")
            fatal += 1
        print()

    for f in found:
        if f.block < 0:
            print(f"  MALFORMED {f.angle}: a record with no BLOCK index")
            fatal += 1
            continue
        if f.verdict not in VERDICTS:
            print(f"  BLOCK {f.block} {f.angle}: {f.verdict!r} is not one of the nine")
            fatal += 1
        elif not allowed(f.verdict, args.level):
            print(f"  BLOCK {f.block} {f.angle}: {f.verdict} not carried at {args.level}")
            fatal += 1
        problem = evidence_problem(f, repo)
        if problem:
            print(f"  BLOCK {f.block} {f.angle}: {problem}")
            fatal += 1
        payload = payload_problem(f)
        if payload:
            print(f"  BLOCK {f.block} {f.angle}: {payload}")

    clash = contradictions(found)
    if clash:
        print(f"\nRE-REVIEW -- drop against correct/patch on: {clash}")
        print("  Not a tie-break. Send the block back; the synthesis order must not decide it.")

    # A block stands only when EVERY angle that ran returned clean on it. With
    # coverage gaps already reported as fatal above, "no angle ruled on it" and
    # "every angle cleaned it" are the same set -- so this subtraction is the
    # clean-arithmetic, not an approximation of it.
    ran = sorted(set(clean) | {f.angle for f in found})
    ruled = {f.block for f in found if f.verdict != "clean"}
    stands = sorted(all_blocks - ruled)
    print(f"\nSTANDS UNCHANGED: {len(stands)} blocks -- clean from all {len(ran)} angles that ran")
    print(f"NEEDS A RULING:   {len(ruled)} blocks")
    if gaps:
        print("  ! counts above are provisional: coverage is incomplete.")

    if fatal:
        print(f"\n{fatal} inadmissible. Resolve or send back before stage 5 rules.")
        return 1
    print("\nEvery finding is admissible. Stage 5 may rule.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 5: Run the tests to verify they pass**

Run: `python -m unittest discover -s tests -v`
Expected: PASS.

- [x] **Step 6: Replace the hand-check prose in `SKILL.md`**

In `SKILL.md`, replace the two paragraphs at lines 485-499 (from *"!! **Resolve
the reviewers' evidence yourself.**"* through *"...never a tie-break."*) with:

```markdown
!! **Run the join before you rule on anything.** It is the gate between MARK and
EDIT:

```bash
python <skill>/scripts/verdicts.py --census <census>.json --level <level> \
  --repo . <one report file per angle>
```

It exits nonzero on a coverage gap, a citation that does not resolve, a quote
not found near its cited line, a verdict the level does not carry, or a payload
the verdict table requires and the record lacks. It also names the blocks where
`drop` meets `correct`/`patch` -- **a re-review, never a tie-break** -- and prints
which blocks STAND UNCHANGED under the clean-arithmetic.

!! **A finding whose evidence does not resolve is not a finding.** Measured: one
graded run had **fabricated 5 of its 7 reviewer reports** and did not notice
until asked to grade itself; self-certified `CONFIRMED` ran at **97% across 298
findings**. **Never grade a review by reading its report.**

! **The tool rules on ADMISSIBILITY, not on truth.** It cannot tell a correct
verdict from an incorrect one. Synthesis, and the order below, remain yours.
```

- [x] **Step 7: Commit**

```bash
ruff check . && ruff format . && python scripts/check_shipped_syntax.py
git add plugins tests
git commit -m "feat(mark): parse the findings and gate stage 5 on their admissibility

Six checks SKILL.md asked the task agent to do by hand across four reviewers
x N blocks -- coverage, evidence, payload, level, contradiction, the
clean-arithmetic -- were all mechanical and none were checked. The blocker
was free-prose findings.

Findings become records carrying a census BLOCK index and a verified
EVIDENCE file:line, plus a CLEAN range line so an angle scoped to a small
slice can account for 500 blocks without emitting 500 records.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 7: A validated run-context packet for stage-4 dispatch

**Landed:** `b99181b` -- `run_context.py` (`REQUIRED`, `template`,
`missing_sections`), `SKILL.md` stage 4's packet and 1.6's fallback pointed at
`ANGLE FILES`. Hardened by `96c12f9`, `47a73f1` and `dd09671`. Step 5
reproduced verbatim 2026-09-02: `INCOMPLETE -- 11 section(s)`, `exit=1`.

**Why:** Stage 4 requires the task agent to hand each reviewer seven things --
census path, stage-1 resolutions, docstring template, style sheet, level, which
languages an LSP answered for, and the two file lists. Nothing checks the
dispatch prompt before four agents fire in parallel; a missing style sheet
silently degrades every angle with no error surfaced (the measured consequence
is 14 en-GB spellings introduced into an en-US codebase). Separately, stage
1.6's plugin-agent resolution **failed on 3 of 3 measured verification runs**
and each improvised the same fallback. One packet fixes both: it is validated
before dispatch, and it carries the absolute angle-file paths that make the
general-purpose fallback a one-line substitution.

**Files:**
- Create: `plugins/comment-review/skills/comment-review/scripts/run_context.py`
- Modify: `plugins/comment-review/skills/comment-review/SKILL.md:438-462`
- Modify: `plugins/comment-review/skills/comment-review/SKILL.md:275-283` (stage 1.6)
- Create: `tests/test_run_context.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `run_context.REQUIRED` -- the tuple of section names.
  - `run_context.missing_sections(text: str) -> list[str]`.
  - CLI: `--template` prints the skeleton; `--check <file>` exits nonzero naming
    every empty or absent section.

- [x] **Step 1: Write the failing test**

`tests/test_run_context.py`:

```python
"""The dispatch packet is validated before four agents fire in parallel."""

import unittest

from _paths import FIXTURES  # noqa: I001,F401  -- path shim must import first

import run_context


FULL = """
## LEVEL
full

## CAP
none published

## WIDTH
88

## DOC CONVENTION
google

## STYLE SHEET
docs/style-sheet.md

## LSP LANGUAGES
python answered; go had no server

## MOVE DESTINATION
UNAVAILABLE -- no destination tree

## CENSUS
/tmp/run-abc/census.txt

## ANGLE FILES
/abs/agents/comment-review-locality.md

## FILES UNDER REVIEW
a.py

## REFERENCE ONLY
docs/decisions.md
"""


class TestValidation(unittest.TestCase):
    def test_a_complete_packet_passes(self):
        self.assertEqual(run_context.missing_sections(FULL), [])

    def test_an_absent_section_is_named(self):
        without = FULL.replace("## STYLE SHEET\ndocs/style-sheet.md", "")
        self.assertIn("STYLE SHEET", run_context.missing_sections(without))

    def test_an_empty_section_is_named(self):
        empty = FULL.replace("docs/decisions.md", "")
        self.assertIn("REFERENCE ONLY", run_context.missing_sections(empty))

    def test_the_template_validates_as_incomplete(self):
        self.assertTrue(run_context.missing_sections(run_context.template()))

    def test_every_required_section_is_in_the_template(self):
        tmpl = run_context.template()
        for name in run_context.REQUIRED:
            self.assertIn(f"## {name}", tmpl)


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run it to verify it fails**

Run: `python -m unittest discover -s tests -k run_context -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'run_context'`.

- [x] **Step 3: Write the script**

`plugins/comment-review/skills/comment-review/scripts/run_context.py`:

```python
"""The packet four reviewers are dispatched with, and its gate.

    python run_context.py --template > run-<id>/context.md
    python run_context.py --check run-<id>/context.md

Stage 4 hands each reviewer seven things. Nothing checked the prompt before
four agents fired in parallel, and a section quietly absent degrades an angle
with no error anywhere: measured, a run with no style sheet introduced 14
en-GB spellings into a codebase whose identifiers are en-US, and every angle
was satisfied because nothing owned consistency.

! A section that is present and EMPTY is a failure, not a default. "No cap
published" is an answer and must be written; a blank is a question nobody
asked.

! ANGLE FILES carries ABSOLUTE paths on purpose. The plugin agents are
namespaced and resolve only if the plugin was installed before the session
started -- measured failing on 3 of 3 verification runs. With the paths in the
packet, the sanctioned fallback (four general-purpose agents given the paths of
their angle file and the brief) is a substitution, not an improvisation.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED = (
    "LEVEL",
    "CAP",
    "WIDTH",
    "DOC CONVENTION",
    "STYLE SHEET",
    "LSP LANGUAGES",
    "MOVE DESTINATION",
    "CENSUS",
    "ANGLE FILES",
    "FILES UNDER REVIEW",
    "REFERENCE ONLY",
)

HINTS = {
    "LEVEL": "fact-check | line | full | proof",
    "CAP": "the number, or `none published` -- never invent one",
    "WIDTH": "the number, or `none published`",
    "DOC CONVENTION": "google | numpy | sphinx | none found, plus a template",
    "STYLE SHEET": "path to it, or `new -- started this run`",
    "LSP LANGUAGES": "which answered, which had no server, or `no LSP tool -- no probe possible`",
    "MOVE DESTINATION": "the tree, or `UNAVAILABLE` -- say which here, not at stage 6",
    "CENSUS": "absolute path, unique to THIS run",
    "ANGLE FILES": "absolute path per angle, plus the brief",
    "FILES UNDER REVIEW": "one per line -- the ONLY files a verdict may target",
    "REFERENCE ONLY": "one per line -- read to settle a claim, never propose a change",
}

SECTION = re.compile(r"^##\s+(.+?)\s*$", re.M)


def template() -> str:
    """The skeleton, with a hint under each heading and no answers."""
    out = [
        "# comment-review run context",
        "",
        "Handed to every reviewer. Fill every section; `--check` refuses a blank.",
        "",
    ]
    for name in REQUIRED:
        out.append(f"## {name}")
        out.append(f"<!-- {HINTS[name]} -->")
        out.append("")
    return "\n".join(out)


def missing_sections(text: str) -> list[str]:
    """Required sections that are absent, or present with no answer.

    Args:
        text: the filled packet.

    Returns:
        The names of sections a reviewer would be dispatched without. A comment
        line is not an answer -- the template's own hints must be replaced.
    """
    heads = list(SECTION.finditer(text))
    bodies: dict[str, str] = {}
    for i, m in enumerate(heads):
        name = m.group(1).strip().upper()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        bodies.setdefault(name, text[m.end() : end])
    bad: list[str] = []
    for name in REQUIRED:
        body = bodies.get(name)
        if body is None:
            bad.append(name)
            continue
        answered = [
            ln
            for ln in body.splitlines()
            if ln.strip() and not ln.strip().startswith("<!--")
        ]
        if not answered:
            bad.append(name)
    return bad


def main() -> int:
    """Print the template, or check a filled packet."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--template", action="store_true")
    ap.add_argument("--check", metavar="FILE")
    args = ap.parse_args()

    if args.template:
        print(template())
        return 0
    if not args.check:
        ap.error("one of --template or --check is required")

    text = Path(args.check).read_text(encoding="utf-8")
    bad = missing_sections(text)
    if bad:
        print(f"INCOMPLETE -- {len(bad)} section(s) would dispatch unanswered:")
        for name in bad:
            print(f"  {name}: {HINTS[name]}")
        print("\nDo not dispatch. A reviewer cannot report a context it never received.")
        return 1
    print(f"Complete: all {len(REQUIRED)} sections answered. Dispatch all four in ONE message.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest discover -s tests -v`
Expected: PASS.

- [x] **Step 5: Verify the CLI both ways**

Run:
```bash
python plugins/comment-review/skills/comment-review/scripts/run_context.py --template > /tmp/ctx.md
python plugins/comment-review/skills/comment-review/scripts/run_context.py --check /tmp/ctx.md; echo "exit=$?"
```
Expected: `INCOMPLETE -- 11 section(s)...` and `exit=1`.

- [x] **Step 6: Wire it into `SKILL.md` stage 4**

In `SKILL.md`, replace the paragraph beginning *"Each already carries its own
angle and reads the shared brief itself. **You supply the run context, and only
that:**"* through *"...which disables every cross-file check."* (lines 449-456)
with:

```markdown
Each already carries its own angle and reads the shared brief itself. **You
supply the run context as a PACKET, and the packet is checked before anyone is
dispatched:**

```bash
python <skill>/scripts/run_context.py --template > <run-dir>/context.md
# fill every section, then:
python <skill>/scripts/run_context.py --check <run-dir>/context.md
```

It refuses a section that is absent **or present and blank** -- *"no cap
published"* is an answer and must be written; a blank is a question nobody
asked. Hand every reviewer the one path. Measured: a run dispatched without a
style sheet introduced **14 en-GB spellings** into a codebase whose identifiers
are en-US, and every angle was satisfied because nothing owned consistency.
```

- [x] **Step 7: Point stage 1.6's fallback at the packet**

In `SKILL.md`, replace the final sentence of 1.6 (lines 280-283, *"The sanctioned
fallback is...which is what this file forbids for a different reason (a copy goes
stale)."*) with:

```markdown
The sanctioned fallback is **four general-purpose agents given the ANGLE FILES
paths from the packet** -- never the angle text pasted into a prompt, which goes
stale the moment an angle is edited. Because the packet already carries those
absolute paths, the fallback is a substitution rather than an improvisation.
```

- [x] **Step 8: Commit**

```bash
ruff check . && ruff format . && python scripts/check_shipped_syntax.py
git add plugins tests
git commit -m "feat(mark): validate the dispatch packet before four agents fire

Stage 4 required seven pieces of context per reviewer and nothing checked the
prompt. A silently absent style sheet degrades every angle with no error:
measured, 14 en-GB spellings into an en-US codebase.

The packet also carries the absolute angle-file paths, so 1.6's fallback --
which fired on 3 of 3 measured runs -- becomes a substitution instead of an
improvisation.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 8: COMPACT and REVIEW become mandatory separate subagents

**Landed:** `dc27abb` -- `comment-review-compact.md` and
`comment-review-review.md`, stages 6 and 8 dispatching them, `compact.md`'s
note, and the packet's `ANGLE FILES` hint. Both agents' frontmatter parses and
both still ship today. `516eae5` cut the rules they restated.

**Why:** Stage 4 gets independence because four agents are dispatched
separately. Stages 6 and 8 do not: by default they run in the same task-agent
context that just wrote the text they are checking -- the exact self-grading
shape this project's own evidence indicts. Both documents already argue for the
separation and then leave it optional: `compact.md` says its narrow input
contract *"is what makes this pass safe to hand to a **separate subagent**"*,
and `review.md` says it is *"the only one that reads the ARTIFACT rather than
the plan"* -- a claim that is weaker when the reader is the author.

**Files:**
- Create: `plugins/comment-review/agents/comment-review-compact.md`
- Create: `plugins/comment-review/agents/comment-review-review.md`
- Modify: `plugins/comment-review/skills/comment-review/SKILL.md:594-609` (stage 6)
- Modify: `plugins/comment-review/skills/comment-review/SKILL.md:638-645` (stage 8)
- Modify: `plugins/comment-review/skills/comment-review/references/compact.md:89-92`

**Interfaces:**
- Consumes: `run_context.py` from Task 7 (the packet lists the angle files;
  extend it to list these two agent files too).
- Produces: two dispatchable agent names,
  `comment-review:comment-review-compact` and
  `comment-review:comment-review-review`.

- [x] **Step 1: Write the COMPACT agent**

`plugins/comment-review/agents/comment-review-compact.md`:

```markdown
---
name: comment-review-compact
description: Stage 6 of the /comment-review skill. Condenses ALREADY-CORRECT proposed comment text to a published cap, working from a deliberately narrow input -- the block's KIND, the original block, the edited text, the cap and the style sheet -- and never from the reasoning that produced the edit. Refuses to shorten a docstring, refuses a block whose kind is unresolved, and reports a block it cannot condense rather than cutting evidence. Not for direct invocation; the skill supplies the inputs and loads references/compact.md.
model: inherit
---

You are the CONDENSER for a comment review. You write no files.

**Read `references/compact.md` at the absolute path the task agent gives you.**
It carries the per-block procedure, the kind table and the rails. Everything
below assumes it.

**Your input is deliberately narrow, and that is the safety property.** You get
the block's KIND, the ORIGINAL block, the EDITED text, the CAP and the STYLE
SHEET. You do **not** get the reasoning that produced the edit, and you must not
ask for it.

!! **An agent that never saw the argument cannot keep a sentence because it
remembers writing it.** That is the whole reason this pass is yours and not the
editor's. If you find yourself reconstructing why a clause is there, you are
doing the editor's job with less information than they had.

## What you may not do

- **You may not change a claim.** Truth was settled at stage 5. If shortening
  requires deciding whether something is true, the EDIT was not finished -- say
  so and return the block at length.
- **You may not touch a `docstring`.** A cap never applies to one; it is
  governed by FORMAT.
- **You may not touch a block marked `doc-kind-unresolved`.** The census could
  not tell a positional doc comment from an ordinary run. Unknown is not
  `comment`.
- **You may not reach the cap by deleting evidence.** Between an over-cap
  comment and an in-cap unfalsifiable one, the over-cap one is correct.

## Return

Per block: the condensed text, or the block at length with what holds it there.
Then the final longest block. **A block you could not condense is a finding, not
a silence.**
```

- [x] **Step 2: Write the REVIEW agent**

`plugins/comment-review/agents/comment-review-review.md`:

```markdown
---
name: comment-review-review
description: Stage 8 of the /comment-review skill. Reads each file a sweep changed end to end, as a reader would rather than as a list of blocks, looking for damage the editing itself caused -- a block that is no longer a proposition, two runs that merged across a blank line, the same sentence now in two places, drift from the style sheet. Reports defects that predate the run separately and may not re-open a verdict. Not for direct invocation; the skill supplies the file list and loads references/review.md.
model: inherit
---

You are the PROOFREADER for a comment review. You read the finished files.

**Read `references/review.md` at the absolute path the task agent gives you.**
It carries what to look for and the two prohibitions. Everything below assumes
it.

**You did not write this text, and that is the point.** Every earlier stage
compared prose to code; you compare the artifact to itself. Damage the editing
caused is visible only to someone reading the page rather than the plan -- and
only barely to someone who remembers intending each edit.

!! **You may not re-open a verdict.** Truth was settled at stage 5, length at
6, and the author ruled at 7a. A better wording you notice here is next run's
`patch`; writing it now puts text on disk the author never saw.

! **Fix only what THIS pass created.** A defect that predates the run goes in a
separate list, which is the next run's input. Do not fold the two together.

## Return

Files read end to end; damage found and repaired; and -- separately -- every
defect that predates this run.
```

- [x] **Step 3: Make stage 6 dispatch it**

In `SKILL.md`, replace the paragraph at lines 599-601 (*"If there is a cap, and
only once **every** block from stage 5 is CORRECT, load
[`references/compact.md`](references/compact.md) and cut the edited text to
fit."*) with:

```markdown
If there is a cap, and only once **every** block from stage 5 is CORRECT,
dispatch `comment-review:comment-review-compact` with the narrow input contract
below and the absolute path of [`references/compact.md`](references/compact.md).

!! **This pass is not yours to run.** You wrote the text; an agent that never
saw the argument cannot preserve a sentence because it remembers writing it.
The narrow contract is only a safety property if the reader is different from
the writer. If the agent does not resolve, use the same fallback as 1.6 -- a
general-purpose agent given the path -- and **say in the report that you ran it
yourself** if you had to.
```

- [x] **Step 4: Make stage 8 dispatch it**

In `SKILL.md`, replace lines 640-641 (*"On completion of 7b, load
[`references/review.md`](references/review.md) and follow it."*) with:

```markdown
On completion of 7b, dispatch `comment-review:comment-review-review` with the
list of changed files, the style sheet, and the absolute path of
[`references/review.md`](references/review.md).

!! **This pass is not yours to run either**, and for the same reason: a reader
who remembers intending each edit reads the page they meant to write. If the
agent does not resolve, fall back as at 1.6 and say so.
```

- [x] **Step 5: Update `compact.md`'s input-contract note**

In `references/compact.md`, replace the sentence *"...which is what makes this
pass safe to hand to a separate subagent."* (line 92) with:

```markdown
...which is what makes this pass safe. ! **It IS a separate subagent --
`comment-review:comment-review-compact` -- not an optional handoff.** The
contract only buys anything if the reader is not the writer.
```

- [x] **Step 6: Add the two agents to the packet's ANGLE FILES hint**

In `run_context.py`, change the `ANGLE FILES` hint to:

```python
    "ANGLE FILES": "absolute path per angle, the brief, and the compact + review agents",
```

- [x] **Step 7: Verify the agents are well-formed and the tests still pass**

Run:
```bash
python -m unittest discover -s tests -v
head -4 plugins/comment-review/agents/comment-review-compact.md
head -4 plugins/comment-review/agents/comment-review-review.md
```
Expected: tests PASS; both files start with `---` and a `name:` matching the
filename stem.

- [x] **Step 8: Commit**

```bash
git add plugins
git commit -m "feat(skill): COMPACT and REVIEW become separate agents, not optional handoffs

Stage 4 gets independence from being dispatched; 6 and 8 ran in the context
that wrote the text they check -- the self-grading shape this project's own
evidence indicts. Both documents already argued for the separation and left
it optional.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 9: Sync the documentation to what now exists

**Landed:** `5798a12` -- README's known-gaps note and the two layout rows,
CLAUDE.md's command block for the four new scripts, and `docs/parsing.md`'s
second instance of the never-improvise-a-parse refusal.

**Why:** `README.md`'s "Known gaps" and `CLAUDE.md`'s architecture section
describe the pre-Phase-A/B system. A stale README in a repository whose entire
subject is stale prose is the obituary this project exists to find.

**Files:**
- Modify: `README.md:196-236` (Known gaps)
- Modify: `README.md:149-158` (Layout table)
- Modify: `CLAUDE.md`
- Modify: `docs/parsing.md:133-141`

- [x] **Step 1: Correct the README's known-gaps section**

In `README.md`, in the *"What is still compiled in rather than detected per
project"* table (lines 213-218), delete the `Doc()` row if present and add a
line beneath the table:

```markdown
! **Two of these moved.** A `LANGUAGES` row that sets `doc_is_structural` now
declares a per-block KIND GAP instead of silently classifying a positional doc
comment as an ordinary run -- measured, a three-line Go export doc counted as
over a cap of two. And the name corpus is built from `git ls-files`, so a
vendored or gitignored tree can no longer donate its namespace and mask an
obituary.
```

- [x] **Step 2: Add the new scripts to the README layout table**

In the `Layout` table, change the `plugins/comment-review/` row's description to:

```markdown
| `plugins/comment-review/` | the plugin -- `skills/` (with `scripts/`: `census.py`, `referrers.py`, `verdicts.py`, `run_context.py`, `prove_unchanged.py`), `agents/`, manifests |
```

And add a row:

```markdown
| `tests/`                  | a stdlib fixture harness for the census, one file per language tier -- `python -m unittest discover -s tests`                                            |
```

- [x] **Step 3: Update CLAUDE.md**

In `CLAUDE.md`, under Commands, add:

```bash
# Run the test suite (stdlib unittest; there are no third-party test deps)
python -m unittest discover -s tests -v

# Stage 3 inbound: which tracked files NAME the files under review
python plugins/comment-review/skills/comment-review/scripts/referrers.py --repo . <paths...>

# Stage 5 gate: join reviewer reports against the census, check every citation
python plugins/comment-review/skills/comment-review/scripts/verdicts.py \
  --census <census>.json --level full --repo . <report>...

# Stage 4 gate: the dispatch packet
python plugins/comment-review/skills/comment-review/scripts/run_context.py --template
python plugins/comment-review/skills/comment-review/scripts/run_context.py --check <file>

# Stage 7b gate: prove the sweep changed no executable code
python plugins/comment-review/skills/comment-review/scripts/prove_unchanged.py \
  --base <merge-base> --repo . <paths...>
```

And replace the sentence *"There is no test suite (`pytest` etc.) in this
repo."* with:

```markdown
Tests are stdlib `unittest` with per-language fixtures under `tests/fixtures/`;
there are no third-party test dependencies, matching the plugin's own
stdlib-only rule. `evals/grade_hazards.py` remains the end-to-end grade, and
`scripts/check_shipped_syntax.py` the shipped-syntax floor.
```

- [x] **Step 4: Record in `docs/parsing.md` that the kind gap is now declared**

In `docs/parsing.md`, at the end of the *"The refusal: never improvise a parse"*
section (after line 79), add:

```markdown
* **The refusal has a second instance now, and it is the same shape.** Go and
Ruby attach docs by POSITION, so the lexical tier cannot separate a doc comment
from an ordinary run -- and detecting declarations to find out would be the
improvised parse this section refuses. The census marks `doc-kind-unresolved`
and excludes the block from the cap tally instead. Measured 2026-08-15: without
it, a three-line `// Add returns...` run above `func Add` reported `over cap (2): 1`,
and `compact.md` routes on KIND, so the cap would have cut an export doc.
```

- [x] **Step 5: Verify everything still passes together**

Run:
```bash
python -m unittest discover -s tests -v \
  && ruff check . && ruff format --check . \
  && python scripts/check_shipped_syntax.py \
  && python plugins/comment-review/skills/comment-review/scripts/census.py --languages
```
Expected: all green.

- [x] **Step 6: Commit**

```bash
git add README.md CLAUDE.md docs
git commit -m "docs: sync the README, CLAUDE.md and parsing.md to what now exists

A stale README in a repository whose subject is stale prose is the obituary
this project exists to find.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

# After the plan: re-measure

Phase A changes what the census reports; Phase B changes what reviewers emit.
Both invalidate the README's headline numbers (339 blocks, 97 findings, 27
worth acting on, 0.40 per 100 lines), which were taken with the old detectors.

!! **THESE THREE ARE DEFERRED, NOT DONE. Audited 2026-09-02.** Each says what
it waits on:

| box | waits on |
| --- | --- |
| re-run the corpora | a runnable end-to-end pass. `scripts/fetch_corpora.py` still works; nothing grades what it fetches |
| re-run `grade_hazards.py` | **the file it names is not in this tree and never was tracked** -- `git log --all --oneline -- evals/grade_hazards.py` returns nothing. Rebuilding it is `TODO/the-harness-cannot-run-the-system-it-grades.md` |
| publish the new numbers | **superseded in part.** The *note that the instrument changed* DID land, in `5798a12` -- `README.md` carries it. The NUMBERS did not, and that same README still reads *"no corpus has been re-run since"* |

- [ ] Re-run the corpora: `python scripts/fetch_corpora.py`, then a full pass
      over the same one-file-per-project slice.
- [ ] Re-run `python evals/grade_hazards.py <worktree>` against the twelve
      planted hazards. **Expect the obituary hazards (D9, D11) to change
      behaviour** -- Task 2 stops vendored trees masking dead names, so a run
      that previously passed them by luck should now pass them by detection.
- [ ] Publish the new numbers with a note that the instrument changed. ! A
      measurement taken with a different detector is not comparable to one
      taken before it -- the same discipline the corpus manifest applies to refs.

---

# Self-review

**Spec coverage.** Every finding from the 2026-08-15 review maps to a task:
census has no tests -> 1; name corpus poisoned by untracked trees -> 2;
`doc_is_structural` dead and Go/Ruby docs cap-cuttable -> 3; AST/CRLF proof
performed freehand -> 4; inbound links absent, and absent entirely under
`target` -> 5; no mechanical evidence/coverage/contradiction check -> 6; no
pre-flight on the dispatch prompt, and 1.6 failing 3/3 -> 7; self-grading at
stages 6 and 8 -> 8; docs drift -> 9.

**Deliberately out of scope, and why.** Markdown and reStructuredText get no
`LANGUAGES` row. The census model is *find the prose among the code*; in a
prose file every line is prose, so a row would report one enormous block per
file and satisfy no angle. Reviewing prose files needs a different node model
(heading-scoped sections), which is a separate plan and should follow the
corpus-in-another-language work the README already names as the higher-value
step. Saying so here is the point -- a gap declared is not a gap skipped.

**Type consistency.** `git_ls_files` returns `list[str] | None` and
`tracked_paths` returns `set[Path] | None`; Task 2 defines both, Task 4 uses
`git_ls_files`, Task 5 uses `git_ls_files`. `code_signature` returns
`(kind, signature)` in Task 4 and is consumed only there. `Finding`'s eight
fields are defined in Task 6 and used only within it. `REQUIRED` and
`missing_sections` are defined in Task 7 and referenced by Task 8's Step 6.

**Ordering.** Task 1 must precede 2 and 3 (it is their net). Task 2 must
precede 4 and 5 (both import `git_ls_files`). Task 7 must precede 8's Step 6.
Everything else is independent.
