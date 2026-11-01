# The Proof Reads What Runs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A comment edit that changes what the language runs never reports PROVEN.

**Architecture:** `reading/stripped.py` compares physical lines with comments removed, so it is blind wherever a physical line is not the language's line: a lone CR, a backslash continuation, an open string, JSX text. Each task adds the check for one such shape to `_without_comments` or `preserved`, on both sides of the comparison, and a new row field where the fact is the language's. An unknown shape refuses; a token comparison waits for the per-language readers (#222). The byte-order mark and the Rust doc marker are separate causes, fixed where they arise.

**Tech Stack:** Python 3.11, stdlib only in shipped code, pytest, ruff, ty.

**Spec:** none. The filed tasks below and rulings #220, #221, #235, #254, #255 and #256 in `docs/decision-log.md`.

## Global Constraints

- Run everything through `uv run`. Gates: `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format .`, `uv run ty check`, `uv run python scripts/check_shipped_syntax.py`, `uv run python scripts/check_vocabulary.py`.
- Every language row states its own grammar. A row's value is justified from that language alone, never from a neighbour.
- A refusal is the safe direction: an unprovable page costs a report, a false PROVEN costs the claim.
- Addresses are not the invariant (#254). No place stops being offered; the refusal is at the proof.
- Shipped comments state the current rule and its reason, with no dates, attributions or ruling numbers.
- Test the unit responsible. No `plugins/` rebuild; that happens at release.
- Never stage `docs/conventions.md` or `docs/lanes.md`. Commit with `git commit -F <file> --only <paths>`.
- Backend lane. `docs/gates.md` is systems' and is not touched.

## Review Focus

1. A shell line `foo \  # note` whose comment is only reworded must still prove: the continuation was already broken before the edit.
2. MySQL reads `'it\'s -- x'` as one string and standard SQL as two tokens: a `.sql` file holding `\'` must be unprovable, not read either way.
3. A UTF-8 mark on a file whose line 1 paragraph is dropped must stay at byte 0, and a U+FEFF inside a later string must stay where it is.
4. A multi-line opening tag in JSX (`<div` / `className="a"` / `>`) followed by `// text` must be refused, since per-line tag matching would miss it.
5. A CRLF file with an unchanged interpreter line must still prove: the comparison holds the ending, not a preference for LF.

---

### Task 1: Refuse a lone CR at every read (one-line-ending T2)

**Files:**
- Modify: `src/comment_review/constants.py`
- Modify: `src/comment_review/flows/source.py:35-59`
- Modify: `src/comment_review/reading/stripped.py:59-85`
- Test: `tests/test_gather.py`, `tests/reading/test_stripped.py`

**Interfaces:**
- Produces: `constants.holds_lone_cr(text: str) -> bool`; diagnostic code `lone-cr` at `ReadStage.DECODE`.

- [ ] **Step 1: Write the failing tests**

```python
def test_a_lone_cr_is_unreadable_at_the_gather(tmp_path):
    # gather over a file holding b"# x\rtouch PWNED\n"
    # exits nonzero and names the file with `lone-cr`

def test_a_draft_holding_a_lone_cr_is_unprovable():
    before = "# x\ntouch PWNED\n"
    after = "# y\rtouch PWNED\n"
    assert read(before).preserved(read(after)).unprovable

def test_a_crlf_file_is_no_lone_cr():
    assert not constants.holds_lone_cr("a\r\nb\r\n")
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/test_gather.py tests/reading/test_stripped.py -k "lone_cr"`
Expected: FAIL; the proof test reports unchanged.

- [ ] **Step 3: Implement**

`holds_lone_cr` matches `\r(?!\n)`. `source_of` and `revision_source_of` return a `ReadFailure` with `lone-cr` for such a text, so gather, `proof` and `prove_unchanged` all refuse, and `_sibling` skips such a file. `_without_comments` returns None on one, for a draft that came from the setter rather than a file.

- [ ] **Step 4: Run the tests and the suite**

Run: `uv run pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

Message: `Refuse a file holding a lone CR at every read`.

### Task 2: Compare the interpreter line with its ending (lexical-code-identity T11)

**Files:**
- Modify: `src/comment_review/reading/stripped.py:159-166`
- Test: `tests/reading/test_stripped.py`, `tests/reading/test_rust.py`

**Interfaces:**
- Consumes: `Language.interpreter_line` unchanged; the reader's use of it is unaffected.

- [ ] **Step 1: Write the failing tests**

```python
@pytest.mark.parametrize("name", ["a.sh", "a.rs", "a.py"])
def test_a_shebang_gaining_a_cr_is_protected_source(name):
    result = read("#!/bin/sh\necho a\n", name).preserved(read("#!/bin/sh\r\necho a\n", name))
    assert not result.unchanged

def test_a_crlf_shebang_that_stays_proves():
    assert read("#!/bin/sh\r\necho a\r\n").preserved(read("#!/bin/sh\r\necho b\r\n")).diagnostics[0].code == "code-changed"
    assert read("#!/bin/sh\r\necho a\r\n").preserved(read("#!/bin/sh\r\necho a\r\n")).unchanged
```

Each language's source body in the test is that language's own code; `a.rs` and `a.py` use `fn f() {}` and `x = 1`.

- [ ] **Step 2: Run them to verify which fail**

Run: `uv run pytest -q tests/reading -k "shebang"`
Expected: `a.sh` FAILS; `a.rs` and `a.py` are not yet measured. Fix whichever fails, in that reader's own comparison.

- [ ] **Step 3: Implement**

`_shebang` returns line 1 of `text` through its ending when `interpreter_line` finds one.

- [ ] **Step 4: Run the suite**

Run: `uv run pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

Message: `Compare the interpreter line with its ending`.

### Task 3: Hold a backslash continuation in the comparison (lexical-code-identity T13)

**Files:**
- Modify: `src/comment_review/reading/language.py` (field, docstring, rows)
- Modify: `src/comment_review/reading/stripped.py:86-109`
- Test: `tests/reading/test_stripped.py`, `tests/test_language_definitions.py`

**Interfaces:**
- Produces: `Language.line_continuations: tuple[str, ...] = ()`. Shell, Ruby, C and C++ state `("\\",)` from their own grammars; every other row leaves it empty.

- [ ] **Step 1: Write the failing tests**

```python
@pytest.mark.parametrize(
    "before, after",
    [
        ("echo a \\\n  b\n", "echo a \\  # n\n  b\n"),   # c add ends the continuation
        ("echo a \\  # n\n  b\n", "echo a \\\n  b\n"),   # c drop joins the next line
        ("echo a \\\n  b\n", "echo a \\\n# n\n  b\n"),   # b add takes the joined line
        ("echo a \\\n# n\n  b\n", "echo a \\\n  b\n"),   # drop of the joined line
        ("echo a \\\n\n  b\n", "echo a \\\n  b\n"),      # blank is the joined line
    ],
)
def test_an_edit_at_a_continuation_is_changed_code(before, after):
    assert read(before).preserved(read(after)).diagnostics[0].code == "code-changed"

def test_rewording_a_comment_past_a_broken_continuation_proves():
    assert read("echo a \\  # one\n  b\n").preserved(read("echo a \\  # two\n  b\n")).unchanged

def test_two_backslashes_do_not_continue():
    assert read("echo a\\\\\n# one\n").preserved(read("echo a\\\\\n# two\n")).unchanged

def test_a_row_with_no_continuation_reads_its_comment_as_prose():
    assert read("x = a \\\n-- one\n", "a.lua").preserved(read("x = a \\\n-- two\n", "a.lua")).unchanged
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/reading/test_stripped.py -k "continuation or backslashes"`
Expected: FAIL; the first four parameters report unchanged.

- [ ] **Step 3: Implement**

Two rules in `_without_comments`, for a row with `line_continuations`. A code prefix keeps its blanks when its right-stripped text ends in an odd run of a continuation, so `foo \ ` and `foo \` differ. Walking `kept` in line order, the line after a kept line ending in that odd run is kept as its source text, comment or blank alike, and it survives the blank filter.

- [ ] **Step 4: Check against bash**

Run the five `before`/`after` pairs through `bash -c` and confirm each pair's output or error differs. Record the result in the task's closing statement.

- [ ] **Step 5: Run the suite and commit**

Run: `uv run pytest -q`
Message: `Hold a backslash continuation in the stripped comparison`.

### Task 4: Read a backslash in a verbatim quote as text (shell T6, SQL T3)

Before Task 5, whose quote scan must not read `'a\'` as open.

**Files:**
- Modify: `src/comment_review/reading/language.py` (field, docstring, shell, SQL and Go rows)
- Modify: `src/comment_review/reading/lexer.py:551-596`, `:1039`, `:1583`
- Test: `tests/reading/test_lexical.py`, `tests/reading/test_stripped.py`

**Interfaces:**
- Produces: `Language.verbatim_quotes: tuple[str, ...] = ()`, the quotes in which a backslash is ordinary text. Shell `("'",)`, SQL `("'", '"')`, Go ``("`",)``.
- Produces: `scan_strings(line, lang, quote="") -> tuple[str, str]`, the blanked line and the quote still open at its end. `_strip_strings` is replaced by it; both call sites pass the row.

- [ ] **Step 1: Write the failing tests**

```python
def test_a_shell_single_quote_ends_at_its_backslash():
    assert not paragraphs("echo 'a\\' 'b # c'\n", "a.sh")

def test_a_go_raw_string_ends_at_its_backslash():
    assert not paragraphs("x := `a\\` + `b // c`\n", "a.go")

def test_a_shell_double_quote_keeps_its_escape():
    assert not paragraphs('echo "a\\" # c"\n', "a.sh")

def test_a_sql_file_holding_an_escaped_quote_is_unprovable():
    # standard SQL and MySQL end this literal in different places
    assert read("SELECT 'it\\'s -- x';\n", "a.sql").preserved(read("SELECT 'it\\'s -- y';\n", "a.sql")).unprovable
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/reading -k "backslash or escape or escaped"`
Expected: the shell and SQL tests FAIL.

- [ ] **Step 3: Implement**

`scan_strings` treats `\` as an escape only outside a verbatim quote. The SQL row adds `"\\'"` to `spanning_quotes`, whose presence already refuses a file, with a one-line row comment saying the dialects disagree; update the field's docstring to cover it.

- [ ] **Step 4: Run the suite and commit**

Run: `uv run pytest -q`
Message: `Read a backslash in a verbatim quote as text`.

### Task 5: Refuse a comment standing inside an open string (lexical-code-identity T10)

**Files:**
- Modify: `src/comment_review/reading/stripped.py:59-128`
- Test: `tests/reading/test_stripped.py`

**Interfaces:**
- Consumes: `scan_strings` from Task 4.

- [ ] **Step 1: Write the failing tests**

```python
@pytest.mark.parametrize(
    "name, text",
    [
        ("a.sh", 'echo "a\n# b\nc"\n'),
        ("a.rb", 'x = "a\n# b\nc"\n'),
        ("a.sql", "SELECT 'a\n-- b\nc';\n"),
        ("a.lua", 'x = "a\\\n-- b\nc"\n'),
        ("a.js", 'x = "a\\\n// b\nc";\n'),
    ],
)
def test_a_comment_inside_an_open_string_is_unprovable(name, text):
    assert read(text, name).preserved(read(text, name)).unprovable

def test_a_string_spanning_lines_with_no_comment_in_it_proves():
    text = 'echo "a\nb"  # note\n'
    assert read(text).preserved(read(text)).unchanged

def test_a_comment_after_the_string_closes_proves():
    assert read('echo "a\nb"\n# one\n').preserved(read('echo "a\nb"\n# two\n')).unchanged

def test_an_apostrophe_in_a_comment_opens_nothing():
    assert read("# it's\necho a\n# two\n").preserved(read("# it's\necho a\n# three\n")).unchanged
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/reading/test_stripped.py -k "string or apostrophe"`
Expected: the parametrized test FAILS.

- [ ] **Step 3: Implement `_comment_in_a_string(lines, paragraphs, lang) -> bool`**

Walk the lines in order carrying the open quote: a line a paragraph holds whole, reached with a quote open, answers True and is otherwise skipped; a trailing paragraph's line is scanned up to its prefix; a code line is scanned whole. `_without_comments` returns None on True.

- [ ] **Step 4: Measure, run the suite and commit**

Rerun the corpus count over every lexical file. Expected: C 0 of 501, Lua at most 5 of 131, JS 0 of 12, shell 0 of 5, SQL 0 of 2; a higher number is reported to Roy before the commit.
Run: `uv run pytest -q`
Message: `Refuse a comment standing inside an open string`.

### Task 6: Refuse a comment inside JSX text (replaces JS T4)

JS T4 is superseded and reissued as *Refuse a comment inside JSX text in the stripped proof*: the reader cannot tell JSX text from a comment without a parser, and a stuck tag count in the reader would hide real comments from review.

**Files:**
- Modify: `src/comment_review/reading/language.py` (field, docstring, JS and TS rows)
- Modify: `src/comment_review/reading/stripped.py`
- Test: `tests/reading/test_stripped.py`

**Interfaces:**
- Produces: `Language.element_text: bool = False`; True on the JavaScript and TypeScript rows.

- [ ] **Step 1: Write the failing tests**

```python
@pytest.mark.parametrize(
    "text",
    [
        "const a = <p>\n  // text\n</p>;\n",
        "const a = <div\n  id='a'\n>\n  // text\n</div>;\n",
        "const a = <>\n  // text\n</>;\n",
    ],
)
def test_a_comment_inside_an_element_is_unprovable(text):
    assert read(text, "a.jsx").preserved(read(text, "a.jsx")).unprovable

@pytest.mark.parametrize(
    "text",
    [
        "const a = <p>b</p>;\n// note\n",
        "const a = <br />;\n// note\n",
        "const a: Array<string> = [];\n// note\n",
        "if (a < b) {}\n// note\n",
        "const f = (a) => a;\n// note\n",
    ],
)
def test_a_comment_outside_any_element_proves(text):
    assert read(text, "a.tsx").preserved(read(text, "a.tsx")).unchanged
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/reading/test_stripped.py -k "element"`
Expected: the first test FAILS.

- [ ] **Step 3: Implement `_comment_in_an_element(lines, paragraphs) -> bool`**

Over each line's code with its literals blanked, count depth up on `<Name` not preceded by a word character, `)` or `]`, and on `<>`; down on `</` and `/>`. A line a paragraph holds, reached at depth above zero, answers True. `_without_comments` returns None on True for a row with `element_text`. A stuck count refuses, which is the safe direction.

- [ ] **Step 4: Run the suite and commit**

Run: `uv run pytest -q`
Message: `Refuse a comment inside JSX text`.

### Task 7: Keep the byte-order mark at byte 0 (bom T5)

**Files:**
- Modify: `src/comment_review/results/compositor.py:111-225` and its return
- Modify: `src/comment_review/reading/stripped.py` (`preserved`)
- Modify: `src/comment_review/reading/rust/preservation.py`, and the Python read's `preserved` in `reading/python/records.py`
- Test: `tests/test_compositor.py`, `tests/reading/test_stripped.py`, `tests/reading/test_rust.py`, `tests/reading/test_python.py`

**Interfaces:**
- Consumes: `constants.mark_of`, `constants.without_mark`.

- [ ] **Step 1: Write the failing tests**

```python
@pytest.mark.parametrize("cue", ["f0", "a0", "b0"])
def test_a_head_add_sets_the_mark_first(cue):
    # add at `cue` on "﻿class A {}\n" as `a.java`
    assert set_page(page).startswith("﻿")
    assert set_page(page).count("﻿") == 1

def test_a_dropped_first_paragraph_keeps_the_mark():
    # drop the line-1 comment of "﻿// c\nint x;\n" as `a.c`
    assert set_page(page) == "﻿int x;\n"

def test_a_mark_inside_a_later_string_stays():
    # "﻿int x;\nchar *s = \"﻿\";\n" with an add at the head keeps both

@pytest.mark.parametrize("name", ["a.sh", "a.rs", "a.py"])
def test_a_lost_or_moved_mark_is_protected_source(name):
    # lost: marked text against the same text unmarked; moved: mark on line 2
    assert not lost.unchanged and not moved.unchanged
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/test_compositor.py tests/reading -k "mark"`
Expected: FAIL; `a.sh` reports both as unchanged.

- [ ] **Step 3: Implement**

When `page.text` opens with the mark, `_set` removes it from the first line of `out` that opens with it and sets it ahead of the first line, and returns the mark alone if `out` is empty. Each reader's `preserved` compares `mark_of` on both sides first; a difference is `protected-source-changed`.

- [ ] **Step 4: Check with rustc, run the suite and commit**

Run a head add over a marked `.rs` page through `rustc --crate-type lib --emit=metadata` and confirm exit 0.
Run: `uv run pytest -q`
Message: `Keep the byte-order mark at byte 0`.

### Task 8: Refuse a Rust doc marker with nothing to attach to (lexer T68, #256)

**Files:**
- Modify: `src/comment_review/reading/rust/documentation.py:205-260`
- Modify: `src/comment_review/reading/rust/records.py:196-210`, `:267-280`
- Modify: `src/comment_review/reading/rust/projection.py:52`
- Modify: `src/comment_review/reading/rust/preservation.py:15-28`
- Test: `tests/reading/test_rust.py`

**Interfaces:**
- Produces: `RustDocumentation.unattached` and `RustRead.unattached: tuple[SourceSpan, ...] = ()`; diagnostic code `doc-without-item`.

- [ ] **Step 1: Write the failing tests**

Each row was run through rustc on this tree.

```python
@pytest.mark.parametrize(
    "draft",
    [
        "fn f() {}\n/// A note.\n",                       # expected item after doc comment
        "fn f() {\n    /// A note.\n}\n",                 # E0585
        "struct S {\n    a: u8,\n    /// A note.\n}\n",   # E0585
        "fn f() {}\n//! A note.\nfn g() {}\n",            # E0753
        "fn f() {\n    let _a = 1;\n    //! A note.\n}\n",  # E0753
    ],
)
def test_a_draft_adding_an_unattached_doc_is_refused(draft):
    # before_of: the draft with the line holding "A note." removed
    assert read(before_of(draft)).preserved(read(draft)).diagnostics[0].code == "doc-without-item"

@pytest.mark.parametrize(
    "draft",
    [
        "fn f() {\n    /// A note.\n    let _a = 1;\n}\n",  # rustc warns only
        "fn f() {\n    //! A note.\n}\n",
        "/// A\n// b\nfn f() {}\n",                         # #235
        "#![allow(unused)]\n//! A note.\nfn f() {}\n",
    ],
)
def test_a_doc_rustc_accepts_is_not_refused(draft):
    assert read(before_of(draft)).preserved(read(draft)).unchanged

def test_a_page_already_holding_one_is_not_refused():
    text = "fn f() {}\n/// A note.\n"
    assert read(text).preserved(read(text.replace("A note", "B note"))).unchanged
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/reading/test_rust.py -k "unattached or rustc_accepts or already_holding"`
Expected: the first test FAILS.

- [ ] **Step 3: Implement**

`_Assigner` records a run's span in `unattached` in two cases. `_outer`: no significant token follows, or the next one is `}`. `_inner`: a significant token precedes it, other than `{` or the end of an inner attribute (`ATTRIBUTE_KINDS`). `compare_preservation` refuses when `before` has none and `after` has some; a read does not refuse.

- [ ] **Step 4: Check with rustc, run the suite and commit**

Run each draft through `rustc` and confirm it agrees with its test.
Run: `uv run pytest -q`
Message: `Refuse a Rust doc marker with nothing to attach to`.

### Task 9: State what the comparison now holds

**Files:**
- Modify: `src/comment_review/reading/stripped.py` (module and `code_fingerprint` docstrings)
- Modify: `TODO` notes through job-board only

- [ ] **Step 1: Rewrite the docstrings**

The module docstring lists what makes a file unprovable or changed: a lone CR, a comment inside a string or element, a line after a continuation. `code_fingerprint`'s closing sentences lose any shape this plan closed; T8 and T9 stay named.

- [ ] **Step 2: Run every gate**

Run the six commands under Global Constraints.
Expected: all pass.

- [ ] **Step 3: Commit**

Message: `State what the stripped comparison holds`.
