# Python and Rust Only Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Only Python and Rust are read, addressed, written and proved; every other source file is listed as freeform and answers `UNCHECKED`.

**Architecture:** A file no reader claims travels on `Binder.freeform`, a list of paths, not as a page. Topology and distribution deal those paths to reviewers beside the pages, so nothing in `desk/` changes. `reading/lexer.py`, `reading/stripped.py` and the language rows are deleted once the behaviour lands and the tests no longer lean on them.

**Tech Stack:** Python 3.11, stdlib only in shipped code, pytest, ruff, ty.

**Spec:** rulings #259 and #260 in `docs/decision-log.md`; `docs/superpowers/specs/2026-11-01-lexical-removal-map.md` holds every call site this plan cites.

## Global Constraints

- Run everything through `uv run`. Gates on each task: `uv run pytest -q`, `uv run ruff check .`, `uv run ty check`, `uv run python scripts/check_shipped_syntax.py`, `uv run python scripts/check_vocabulary.py`.
- The suite is green at every commit.
- Python and Rust behaviour does not change, except the orphans Task 8 removes.
- Keep the `reading/readers.py` door: `read_python`, `read_rust`, `reader_for`, `read_source`, `ReaderBinding`.
- Reader ids `python-lexical`, `rust-lexical` and `PythonRead.proof == "lexical"` stay; they are hashed into the compatibility digest.
- Shipped comments state the current rule and its reason, with no dates, attributions or ruling numbers.
- A TODO or plan file changes only through `job-board`. `CLAUDE.md` wording goes to Roy first.
- Never stage `docs/conventions.md` or `docs/lanes.md`. No `git stash`. No `plugins/` rebuild.
- `src/plugin/` is not touched here. Plan `2026-11-01-freeform-agent-prose` follows this one.

## Review Focus

1. A run handed only `.js` files: gather exits 0, topology builds, distribute deals them, and `check` and `collate` accept a copy with no sheets.
2. `prove_unchanged` on `a.py` and `b.js` together prints `1 proven, 1 UNCHECKED`; on `b.js` alone it never prints the word proven.
3. A binder written at version 3 is refused with the existing `regather` message.
4. A `.png` or `uv.lock` in a walked directory stays `PASSED OVER`, and no reviewer gets it.
5. A `.py` that fails to read still exits nonzero: freeform must not swallow a reader failure.

---

### Task 1: Port the tests that lean on a lexical language

Section 7 of the map names the files; about 83 functions, about 100 new parameters.

**Files:** Modify the `port` rows of the section 7 table, largest first: `tests/test_proof_setter.py`, `tests/test_comment_wrapping.py`, `tests/test_compositor.py`, `tests/test_page_for.py`, `tests/test_proof_command.py`, `tests/test_standalone_reading_context.py`, then the rest.

- [ ] **Step 1: Give each function a Python or Rust case**

Keep each function's assertion unchanged; change only its fixture language. Rust holds the `/* */` and `///` shapes, Python the `#` and docstring shapes.

- [ ] **Step 2: Add a Rust row for any FORMS shape only C or Java held**

Check `C block`, `trailing block wrapped` and `C both` in the `test_compositor.py` FORMS table row by row.

- [ ] **Step 3: Report a shape with no Python or Rust spelling**

List each such test in the report as a candidate to die, naming the behaviour it pinned, and leave it as it is for Task 6.

- [ ] **Step 4: Run the suite with the lexical languages installed**

Run: `uv run pytest -q`
Expected: all pass, which is the proof a port kept its assertion.

- [ ] **Step 5: Commit per test file**

Message: `Port <file> off the lexical fixtures`.

### Task 2: Move the helpers that survive

**Files:**
- Modify: `src/comment_review/concordance/names.py`, `concordance/code_names.py:17`, `concordance/referrers.py:23-34`
- Modify: `src/comment_review/binder/page.py`, `reading/lexer.py`
- Modify: `scripts/measure_binder.py:41`
- Test: `tests/reading/test_lexical.py:679-694` moves to `tests/test_page_for.py`

**Interfaces:**
- Produces: `concordance.names.NAMED_DEFS`; `binder.page.leading_between(paragraphs, text, code)`.

- [ ] **Step 1: Move the two names and the two `leading_between` tests**

No behaviour changes. `measure_binder.py` takes `Kind` from `reading.series`.

- [ ] **Step 2: Run the suite and commit**

Run: `uv run pytest -q`
Message: `Move NAMED_DEFS and leading_between to their users`.

### Task 3: `prove_unchanged` answers UNCHECKED

**Files:**
- Modify: `src/comment_review/flows/prove_unchanged.py:18-25,85-89`
- Modify: `src/comment_review/commands/prove_unchanged.py:38-49`
- Test: `tests/test_proof_command.py`

**Interfaces:**
- Produces: `ProofReport.freeform: int`.

- [ ] **Step 1: Write the failing tests**

```python
def test_a_file_no_reader_claims_is_unchecked(tmp_path):
    # r.md committed and edited
    # prints "UNCHECKED  r.md: no reader -- formatter and compiler are the check"
    # exit 0, freeform == 1, failures == 0

def test_the_summary_never_counts_a_freeform_path_as_proven(tmp_path):
    # a.py unchanged, r.md edited: output holds "1 proven, 1 UNCHECKED"
    # r.md alone: "proven" not in output

def test_a_python_file_that_fails_to_read_still_fails(tmp_path):
    # invalid UTF-8 a.py: exit 1
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/test_proof_command.py -k "unchecked or freeform or fails_to_read"`
Expected: the first two FAIL, `unsupported-language`.

- [ ] **Step 3: Implement**

After the `outside --repo` check, `reader_for(target) is None` prints the line, counts `freeform`, and continues; line endings are not compared. A `ReadFailure` from `reader_for` still fails. The summary uses `len(paths) - freeform` for proven.

- [ ] **Step 4: Run the suite and commit**

Run: `uv run pytest -q`
Message: `Answer UNCHECKED for a file no reader claims`.

### Task 4: Carry freeform paths on the binder

**Files:**
- Modify: `src/comment_review/binder/binder.py:73,76,269-303,316`
- Test: `tests/test_binder.py`

**Interfaces:**
- Produces: `Binder.freeform: tuple[str, ...]`, repo-relative posix paths; `bind(pages, read_from, absent, freeform=())`; `VERSION == "4"`.

- [ ] **Step 1: Write the failing tests**

```python
def test_freeform_paths_round_trip():
    assert deserialize(serialize(bind(pages, r, a, freeform=("b.js",)))).freeform == ("b.js",)

def test_a_version_3_binder_is_refused():
    # the existing "unsupported binder version ...; regather" message

def test_a_freeform_field_that_is_not_a_list_is_refused():
    ...
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/test_binder.py -k "freeform or version_3"`
Expected: FAIL.

- [ ] **Step 3: Implement, run the suite, commit**

Run: `uv run pytest -q`
Message: `Carry freeform paths on the binder`.

### Task 5: Gather lists freeform; topology deals it

**Files:**
- Modify: `src/comment_review/flows/gather.py:93,115-125,140`, `commands/gather.py:56,108-113,130-132,183-205`
- Modify: `src/comment_review/reading/registry.py` (the decision below)
- Modify: `src/comment_review/flows/fan_out.py:110-146`, `flows/topology.py:89-102`, `commands/distribute.py:189`
- Test: `tests/test_gather_command.py`, `tests/test_topology_compose.py`, `tests/test_distribute_command.py`

**Interfaces:**
- Consumes: `Binder.freeform`.
- Produces: `registry.FREEFORM_SUFFIXES: frozenset[str]`; `Gathering.freeform: list[str]`; `Shard` gains its matched freeform paths as a third element.

Ruled in #260: a source file is one whose suffix is in `registry.FREEFORM_SUFFIXES`, a plain set of the suffixes the lexical rows name today, so `.md`, lockfiles and images stay `PASSED OVER`. Adding a language is one word in that set.

- [ ] **Step 1: Write the failing tests**

```python
def test_a_named_js_file_is_freeform_and_gather_exits_0(tmp_path):
    # gather a.py b.js: binder has page a.py, freeform ("b.js",), exit 0

def test_a_binary_in_a_walked_directory_stays_passed_over(tmp_path):
    # logo.png, uv.lock not in freeform

def test_a_python_file_that_fails_to_read_still_stops_the_gather(tmp_path):
    # invalid UTF-8 a.py with b.js: exit 1

def test_topology_builds_over_a_freeform_only_binder(tmp_path):
    # `topology --build` exits 0 where it exits 2 today

def test_partition_deals_a_freeform_path_to_one_shard_of_each_role():
    ...

def test_check_and_collate_accept_a_copy_with_no_sheets(tmp_path):
    ...
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/test_gather_command.py tests/test_topology_compose.py -k "freeform or passed_over or fails_to_read"`
Expected: FAIL.

- [ ] **Step 3: Implement**

`_walk` routes a path whose suffix is in `FREEFORM_SUFFIXES` to `Gathering.freeform` whether named or walked; any other path with no definition stays `PASSED OVER`. Freeform files are not opened. `partition` matches `binder.freeform` beside page paths under the same guards. `dealt` keeps a shard's paths on its received binder. `compose` sorts page and freeform paths together. A copy with no sheets is seeded empty; if `check` or `collate` refuses one, fix it there.

- [ ] **Step 4: Run the suite and commit**

Run: `uv run pytest -q`
Message: `List freeform files at gather and deal them to reviewers`.

### Task 6: Uninstall the lexical languages

**Files:**
- Modify: `src/comment_review/reading/language.py` (`READER_METADATA`), `commands/gather.py:108-113`
- Test: delete the `rows drop` rows and `die` tests of section 7, and any shape Task 1 listed that Roy agreed to drop

- [ ] **Step 1: Empty `READER_METADATA` and drop the tier column from `gather --languages`**

- [ ] **Step 2: Run the suite**

Run: `uv run pytest -q`
Expected: every failure is a test in section 7's `rows drop` or `die` columns, or a port Task 1 missed. Port a miss; delete the rest.

- [ ] **Step 3: Commit**

Message: `Uninstall the lexical languages`.

### Task 7: Delete the lexical code

**Files:**
- Delete: `src/comment_review/reading/lexer.py`, `reading/stripped.py`, `tests/reading/test_lexical.py`, `tests/reading/test_stripped.py`
- Modify: `reading/comment.py`, `reading/paragraph.py:178`, `desk/marks/rules.py:30`, `reading/language.py`, `reading/readers.py`, `binder/page.py:61-70,731-738,816`, `flows/language_definitions.py:10,15-16`, `flows/page_for.py:71-83`
- Test: the fakes that use `LexicalRead`: `tests/test_page_for.py`, `tests/test_sheet_reading.py`, `tests/test_reading_context.py`, `tests/test_page_reading_context.py`

**Interfaces:**
- Produces: `reading.comment.comment_form(path, series, raw_text, anchor)`, reduced to the scanner path; `language.py` holds `_shipped_definitions`, `SHIPPED_DEFINITIONS`, `INSTALLED_REGISTRY`, `documents_in_literals`, `line_comment_markers`.

- [ ] **Step 1: Move `comment_form` with `_Grammar`, `_grammar_for`, `_scanned_form`, `_comment_fragment`, `_join`**

Drop the row branches listed in section 1. Import `comment_scanner` inside `_grammar_for` to break the cycle with `rust/scanner.py`.

- [ ] **Step 2: Delete the modules and reduce `language.py`, `readers.py` and `page.py` per sections 2 and 3**

`tier_for`, `read_paragraphs`, `_read_paragraphs`, `_paragraph_source_span` and `page_for.py:71-83` go.

- [ ] **Step 3: Run every gate**

Expected: all pass, and `git grep -n -E "read_lexical|StrippedRead|LexicalRead|code_fingerprint" -- src tests` returns nothing.

- [ ] **Step 4: Commit**

Message: `Delete the lexical reader`.

### Task 8: Remove what only the lexical reader fed

**Files:**
- Modify: `src/comment_review/reading/addresser.py:751`, `binder/page.py:770-771`, `reading/python/records.py:301-314`, `reading/rust/records.py:383-397`
- Test: `tests/test_addresser_command.py` (`a_closing_binder`)

- [ ] **Step 1: Remove `closing_docstring`, `a_series`, `Cues.closing_documentation`, the `a` at `<eof>` and the `b.anchor == EOF` branch**

Both readers answer `a_series` True and `closing_docstring` False, so each goes as a parameter.

- [ ] **Step 2: Run the suite and commit**

Run: `uv run pytest -q`
Message: `Remove the closing docstring branch`.

### Task 9: Bring the prose and the board up to date

**Files:**
- Modify: the code comments in section 8; `docs/addressing.md`, `docs/parsing.md`, `docs/vocabulary.md`, `references/vocabulary.toml`, `README.md:350-356`, `scripts/retired_words.toml`
- Modify: `CLAUDE.md:71,219-302`, on Roy's approved wording

- [ ] **Step 1: Rewrite the comments and docs**

`git grep -n -E "\blexical\b|tier" -- src docs/addressing.md docs/parsing.md README.md` returns only reader ids and `proof` values.

- [ ] **Step 2: Propose the `CLAUDE.md` wording to Roy, then apply it**

- [ ] **Step 3: Supersede the dead board work**

Through `job-board`, with the Task 7 commit as evidence: the 13 `language-reader-*` TODOs and section 9's lists. Rework `2026-10-11-lexical-readers`: supersede P41, reword P43, P44, P46-P50.

- [ ] **Step 4: Run every gate and commit**

Message: `State the system as Python and Rust`.
