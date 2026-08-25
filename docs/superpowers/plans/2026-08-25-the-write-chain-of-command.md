# The Write Chain of Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the chain that runs after the reviewers mark and before a human is asked -- notations plus the saved binder become one drafted temporary file per page, proven to hold only comment changes.

**Architecture:** A flow module owns the ORDER as data; the galley edits a page, the compositor sets it, and neither knows the sequence. A page RECEIVES its sha from the read rather than hashing anything itself, and the chain compares that against the sha the binder recorded. Any refusal aborts the run whole and names its step.

**Tech Stack:** Python 3.11 floor, stdlib only in shipped code, pytest + ruff + ty as pinned dev dependencies. Everything runs through `uv run`.

**Spec:** [`docs/plans/0.2.4-the-write-chain-of-command.md`](../../plans/0.2.4-the-write-chain-of-command.md) -- the `P` plan, 19 boxes over seven steps. Each task below cites the `P` boxes it delivers. Read the spec's *"The rulings it is built on"* table before starting; it is ten dated quotations and it is where every decision here comes from.

## Global Constraints

- **Python 3.11 is the floor.** `.python-version` and `[project] requires-python` pin it. Run EVERYTHING through `uv run`; a bare `python` is whatever the machine has.
- **Shipped code imports the standard library only.** Anything under `src/comment_review/` is copied into a stranger's `.claude/`. `tests/gates/test_shipped_imports.py` enforces it.
- **No `except` clause in shipped code holds a tuple literal.** Bind the tuple to a name (`READ_ERRORS`, `PARSE_ERRORS`) -- a downstream formatter can rewrite a literal into a `SyntaxError` on an older interpreter.
- **ASCII only in prose.** Write `--` for an em-dash. This tree has no smart quotes and no unicode dashes.
- **No subjective claims in comments or commit messages.** Not "robust", "clean", "elegant". Write what is measured, what is enforced, or what was observed. If a sentence cannot be falsified by reading the code or re-running a command, it does not belong.
- **No heredocs and no `sed`, ever.** A `PreToolUse` hook refuses both. Use `Edit`/`Write`, or write a `.py` script and run it. For a commit message: `Write` it to a file, then `git commit -F <file>`.
- **`plugins/` is BUILT, not edited.** Run `uv run python scripts/build_plugin.py` and commit what it writes.
- **Lane:** this is all `backend`. Do not edit `plugins/comment-review/agents/**`, `SKILL.md`, or `scripts/**`.

## The gate for every task

```bash
uv run pytest -q                          # 782 passed, 3 xfailed at HEAD
uv run ruff check .
uv run ty check src/comment_review/
uv run python scripts/check_shipped_syntax.py
```

---

## Marking off `P` and `T` -- every task, not at the end

!! **THE ARROWS RUN `SP -> P -> T`, AND SOMETHING HAS TO WALK BACK UP THEM.** A task that
delivers a `P` box and leaves it unticked makes the plan advertise work that is done. Roy,
2026-08-18: *"a check box not-marked is left as something todo, even if it was superseded and no
longer necessary."* MEASURED the same day: five settled proposals with no boxes made `resync`
generate a README row reading `0/9` on a file a third finished.

! **AND AN INTERRUPTED BRANCH IS THE CASE THIS EXISTS FOR.** Ticking everything in a final task
means a session that stops at task 7 leaves `0 of 19` on a plan that is two-thirds delivered --
and the next reader cannot tell which third.

**So the LAST step of every task below is: tick what it delivered, in the same commit as the
work.** Not a separate pass, not a final reconciliation.

| | how | why |
| --- | --- | --- |
| a **`P`** box, in `docs/plans/0.2.4-the-write-chain-of-command.md` | `Edit` -- `- [ ]` to `- [x]` | `todo_tool` manages `TODO/`, not `docs/plans/`. **The boxes are the state**; there is no `Progress:` line to keep |
| a **`T`** task, in `TODO/*.md` | `uv run python scripts/todo_tool.py check <file> <n>` | the tool recomputes every count and README row from the boxes it just wrote. **Never hand-edit a `Progress:` line** |
| a `T` only PARTLY answered | `uv run python scripts/todo_tool.py note <file> --text "..."` | **Deferred is not done.** A partial answer leaves the box unchecked and says what landed |

!! **TICK A `T` ONLY WHEN ITS OWN STATED VERIFICATION IS MET** -- the words after *"Verify:"* in
that task, not your impression that the area is handled. A box ticked on a judgement is the
thing `CLAUDE.md` calls *a judgement wearing a checkbox*.

### What each task marks off

| task | `P` boxes | `T` tasks |
| --- | --- | --- |
| 1 | **none** -- see below | **note** `two-areas-have-no-tests` -- `machine/` now has tests, `commands/` still has none |
| 2 | P5.4 only -- see below | `check a-page-carries-no-identity.md 1`; `check galley-and-compositor-write-path.md 3`; `... 4` |
| 3 | **P2.1, P2.2**, P2.3 | -- |
| 4 | P1.1, P1.2 | -- |
| 5 | P1.3 | -- |
| 6 | P3.1 | -- |
| 7 | P3.2 | -- |
| 8 | P2.4, P4.1, P6.1 | -- |
| 9 | P2.5, P2.6 | `check a-page-carries-no-identity.md 2`; `... 3`; `... 4` |
| 10 | P5.1, P5.2 | -- |
| 11 | P5.3 | -- |
| 12 | P4.2 | **note** `the-flow-lives-in-the-command` -- task 5 is answered for the galley half only, and names verdicts and record too |
| 13 | P7.1 | -- |

! **P2 HAS SIX BOXES AND P5 HAS FOUR.** Count them in the file before ticking; the numbering
above is positional, not a label written in the plan.

!! **TASK 1 TICKS NO `P` BOX, AND THAT IS THE RULE WORKING RATHER THAN AN OVERSIGHT.** P2 box 1
reads *"Verify: `hashlib` is imported in `machine/` and nowhere else in the package."* Task 1
ADDS the hash to `machine/`; `binder/binder.py` keeps its own until Task 3 deletes it. **The
move is not complete until the second half lands**, so the box belongs to Task 3.

! **IT WAS TICKED AT TASK 1 AND UNTICKED, 2026-08-25.** The dispatch instructed it and the
implementer flagged the gap in its own report. Recorded rather than quietly corrected, because
the mistake is the one this whole section exists to prevent: **a box ticked on the shape of the
work instead of on its stated verification.**

!! **AND P2 BOX 2 MOVED THE SAME WAY, AT TASK 2, WITHOUT ANYONE HAVING TO CATCH IT.** Its verify
clause is *"`Page` carries it beside `path`, and neither `page.py` nor `binder.py` computes
one"* -- and `binder.py` computes `sha_of(page.text)` until Task 3. **The Task 2 implementer
read the clause, found it false, declined the tick and said so in its report.** ! That is the
rule working as designed rather than a second mistake: the instruction to verify before ticking
was added to the dispatch BECAUSE of Task 1, and it caught the next one on its own. **Two of
P2's boxes therefore land at Task 3, where the binder finally gives up its hash.**

! **TWO `T`s ARE DELIBERATELY NOT TICKED BY ANY TASK.** `two-areas-have-no-tests` and
`the-flow-lives-in-the-command` are each answered in PART, and a partial answer takes a note. Over-ticking
is the failure that makes a backlog lie towards LESS work, which no gate can see.

- [ ] **Final check, Task 13:** `grep -c '^- \[ \]' docs/plans/0.2.4-the-write-chain-of-command.md`
      returns **0**, and `uv run python scripts/todo_tool.py resync` reports no drift. Any box
      still open names work that was not done -- **file it in `TODO/` before this plan closes,
      or it is lost.**

---

## File Structure

| file | responsibility | task |
| --- | --- | --- |
| `src/comment_review/machine/repo.py` | MODIFY -- gains `Source`, `sha_of`, `read_source`. The only place `hashlib` is imported | 1 |
| `src/comment_review/binder/page.py` | MODIFY -- `Page` gains `sha`; `page_for` receives it | 2 |
| `src/comment_review/binder/binder.py` | MODIFY -- reports `page.sha`; loses `sha_of` and `hashlib` | 3 |
| `src/comment_review/desk/notations.py` | CREATE -- the stand-in shape the middle will emit, and its refusal | 4, 5 |
| `src/comment_review/results/galley.py` | MODIFY -- `reset` takes cues and `None`; `drifted` is retired | 6, 7 |
| `src/comment_review/flows/write.py` | CREATE -- owns the ORDER, as data | 8, 9, 10, 11 |
| `src/comment_review/commands/write.py` | CREATE -- parses arguments, calls the flow, holds no orchestration | 12 |
| `tests/test_machine.py` | CREATE -- `machine/` has no tests today | 1 |
| `tests/test_notations.py` | CREATE | 4, 5 |
| `tests/test_write_chain.py` | CREATE | 8-11 |

! **`tests/` IS FLAT** -- `test_reading.py`, `test_addressing.py`, `test_binder.py`, `test_galley.py`, `test_compositor.py`, plus `gates/`. New files follow that, not a mirrored tree.

! **The command name `write` is provisional.** The flow is named for Roy's own phrase, *"the write chain of command"*. The workflow does not write over a real file -- it drafts -- so `proof` may be the better trade word. Not a blocker; raise it when the middle is rewritten.

---

### Task 1: The read supplies the sha

**Delivers:** spec P2 box 1 (`hashlib` in `machine/` and nowhere else). Also gives `machine/` its first test -- see `TODO/two-areas-have-no-tests.md`.

**Files:**
- Modify: `src/comment_review/machine/repo.py`
- Test: `tests/test_machine.py` (create)

**Interfaces:**
- Consumes: `repo.read_raw(path) -> str`, which already exists.
- Produces: `repo.Source(text: str, sha: str)`, `repo.sha_of(text: str) -> str`, `repo.read_source(path: Path) -> Source`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_machine.py`:

```python
"""What the checkout says, and the identity of what was read.

! THE SHA IS TAKEN AT THE READ because this tree has two readers and they
disagree. A sha taken downstream of whichever reader a consumer happened to use
answers WHICH READER RAN, not whether the file changed.
"""

from conftest import SRC  # noqa: F401  -- conftest puts src on the path

from comment_review.machine.repo import Source, read_raw, read_source, sha_of

CRLF = b"# one\r\ndef f():\r\n    return 1\r\n"


def test_the_two_readers_disagree_on_a_crlf_file(tmp_path):
    p = tmp_path / "crlf.py"
    p.write_bytes(CRLF)
    assert read_raw(p) != p.read_text(encoding="utf-8")


def test_the_sha_is_of_the_untranslated_text(tmp_path):
    p = tmp_path / "crlf.py"
    p.write_bytes(CRLF)
    got = read_source(p)
    assert got.sha == sha_of(got.text)
    assert got.sha != sha_of(p.read_text(encoding="utf-8"))


def test_the_text_and_the_sha_arrive_together(tmp_path):
    p = tmp_path / "crlf.py"
    p.write_bytes(CRLF)
    assert isinstance(read_source(p), Source)


def test_the_same_bytes_answer_the_same_sha(tmp_path):
    one, two = tmp_path / "a.py", tmp_path / "b.py"
    one.write_bytes(CRLF)
    two.write_bytes(CRLF)
    assert read_source(one).sha == read_source(two).sha


def test_one_changed_byte_changes_the_sha(tmp_path):
    p = tmp_path / "a.py"
    p.write_bytes(CRLF)
    before = read_source(p).sha
    p.write_bytes(CRLF.replace(b"return 1", b"return 2"))
    assert read_source(p).sha != before
```

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/test_machine.py -q`
Expected: FAIL -- `ImportError: cannot import name 'Source'`.

- [ ] **Step 3: Implement**

In `src/comment_review/machine/repo.py`, change the imports at the top:

```python
import hashlib
import subprocess
from pathlib import Path
from typing import NamedTuple
```

Then add this immediately after `read_raw`'s closing line (`return f.read()`):

```python
class Source(NamedTuple):
    """A file's text and the sha of that exact text, read together.

    !! THEY TRAVEL AS ONE BECAUSE A SHA OF THE WRONG READING IS WORSE THAN NO
    SHA. Roy, 2026-08-25: *"that is the only place to properly ensure it gets
    read exactly the same and the middle things shouldn't depend on the
    external things."*

    Attributes:
        text: as `read_raw` returns it -- the file's own line endings.
        sha: of that text, so a caller cannot pair the two wrongly.
    """

    text: str
    sha: str


def sha_of(text: str) -> str:
    """The identity of a text, short enough to sit in a row and be read.

    ! WHAT IT ANSWERS is one question -- *are these the bytes that were
    reviewed?* Roy, 2026-08-21: *"if the file shifted at all it is dead and so
    are the edits."*

    Args:
        text: the text to identify.

    Returns:
        The first 16 hex characters of its UTF-8 SHA-256.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def read_source(path: Path) -> Source:
    r"""Read a file and identify what was read, in one act.

    !! THE READING AND THE HASHING CANNOT BE SEPARATED WITHOUT LOSING THE
    GUARANTEE. MEASURED 2026-08-25 over `b"# one\r\ndef f():\r\n    return
    1\r\n"`, with this tree's two readers:

        read_raw    newline=""            f13497990c3d92d0
        read_text   universal newlines    83ec58343641fd11

    ! ONE FILE, ONE SET OF BYTES, TWO SHAS. A sha taken downstream of whichever
    reader a consumer happened to use answers *which reader ran*, not *did the
    file change* -- so a byte-identical CRLF checkout refuses.

    ! AND THE DEFECT WAS LIVE WHEN THIS LANDED: `census.py` read through
    `Path.read_text` and the binder hashed that, so the recorded sha described
    the TRANSLATED text and not the file.

    Args:
        path: the file to read.

    Returns:
        Its text with line endings untouched, and the sha of that text.
    """
    text = read_raw(path)
    return Source(text, sha_of(text))
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_machine.py -q`
Expected: 5 passed.

- [ ] **Step 5: Full gate**

Run: `uv run pytest -q && uv run ruff check . && uv run ty check src/comment_review/`
Expected: 787 passed, 3 xfailed. Both checkers clean.

- [ ] **Step 6: Commit**

Write the message to a file first -- the shell eats backticks in `-m`.

```bash
git add src/comment_review/machine/repo.py tests/test_machine.py
git commit -F <message-file>
```

Message body: *"machine: the read supplies the sha, because two readers disagree"*, stating the measured pair of shas.

---

### Task 2: A page receives its sha; it never asks for one

**Delivers:** spec P2 box 2, and P5 box 4 (`compositor` reads through `read_raw`) -- one change, because the compositor's two `read_text` sites are exactly the call sites this task must update. Works `a-page-carries-no-identity` T1 and `galley-and-compositor-write-path` T3 and T4.

**Files:**
- Modify: `src/comment_review/binder/page.py` -- `Page` fields at `:148-151`, `page_for` signature at `:678`, `Page(...)` construction at `:855`
- Modify: `src/comment_review/commands/census.py:148` (the read) and `:196` (the call)
- Modify: `src/comment_review/commands/galley.py:125` (the read) and `:136` (the call)
- Modify: `src/comment_review/results/compositor.py:302`, `:309`, `:333`, `:339`
- Modify: `scripts/render_page.py:191`
- Modify: `tests/conftest.py:64-72`
- Test: `tests/test_reading.py`

**Interfaces:**
- Consumes: `repo.read_source`, `repo.sha_of` from Task 1.
- Produces: `Page.sha: str`; `page_for(path, text, lang, rel=None, *, sha: str) -> Page`. **`sha` is keyword-only and REQUIRED** -- a default would let a caller build a page whose identity is a lie, and the chain's comparison would pass vacuously.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_reading.py`:

```python
class TestAPageCarriesTheShaItWasGiven:
    """The page RECEIVES a sha. Roy, 2026-08-25: *"It is information received by
    page and binder, not something requested by page/binder."*"""

    def test_the_page_carries_it(self):
        page = build(SAMPLE)
        assert page.sha == sha_of(SAMPLE)

    def test_page_for_computes_no_sha_of_its_own(self):
        # A page built with a sha that does not describe its text keeps the sha
        # it was HANDED. If page.py hashed anything, this would disagree.
        path = Path("m.py")
        page = page_for(path, SAMPLE, language_for(path), rel="m.py", sha="deadbeef")
        assert page.sha == "deadbeef"

    def test_the_sha_is_required(self):
        path = Path("m.py")
        with pytest.raises(TypeError):
            page_for(path, SAMPLE, language_for(path), rel="m.py")
```

Add `from comment_review.machine.repo import sha_of` and `page_for`, `language_for`, `Path`, `pytest` to that file's imports if absent.

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/test_reading.py -q -k Sha`
Expected: FAIL -- `AttributeError: 'Page' object has no attribute 'sha'`.

- [ ] **Step 3: Give `Page` the field**

In `src/comment_review/binder/page.py`, add to the `Attributes:` block of `Page`'s docstring, after the `text:` line:

```
        sha: of `text`, RECEIVED from the read and never derived here. Roy,
            2026-08-25: *"the querying of it should not have left the machine/
            modules. It is information received by page and binder, not
            something requested by page/binder."* ! The write chain compares it
            against the one the binder recorded, which is the only comparison
            that can fail -- a sha this module took for itself would be asking
            whether the text equals itself.
```

And add the field between `text` and `paragraphs`:

```python
    path: str
    text: str
    sha: str
    paragraphs: list[Paragraph]
    cues: Cues
```

- [ ] **Step 4: Give `page_for` the parameter**

Change the signature at `page.py:678`:

```python
def page_for(
    path: Path, text: str, lang: Language, rel: str | None = None, *, sha: str
) -> Page:
```

Add to its `Args:` block:

```
        sha: of `text`, from `repo.read_source`. KEYWORD-ONLY AND REQUIRED: a
            default would let a caller build a page whose identity does not
            describe its text, and the write chain's comparison would then pass
            on a file nobody verified.
```

And pass it through at the `Page(` construction (`:855`):

```python
    return Page(
        path=rel if rel is not None else path.as_posix(),
        text=text,
        sha=sha,
        paragraphs=sorted(got, key=lambda b: (b.start, b.end)),
        cues=cues,
        leading=edges,
    )
```

- [ ] **Step 5: Update `tests/conftest.py`**

```python
def build(text: str, name: str = "m.py"):
    """The page for this text, addressed as the repo would address it.

    ! `rel` IS PASSED, because `page_for` stamps addresses from it -- a page
    built without one carries none, and every assertion about a place would
    then be vacuous.

    ! THE SHA IS COMPUTED HERE, not read, because a test's text never came off
    a disk. `read_source` is what supplies it in the running system.
    """
    path = Path(name)
    return page_for(path, text, language_for(path), rel=name, sha=sha_of(text))
```

Add `from comment_review.machine.repo import sha_of` beside the existing imports.

- [ ] **Step 6: Update the four production call sites**

`commands/census.py` -- replace the `read_text` at `:148` and pass the sha at `:196`:

```python
            source = read_source(path)
            text = source.text
...
            got = page_for(path, text, lang, rel, sha=source.sha)
```

`commands/galley.py:125` already reads via `read_raw`; change it to `read_source` and pass it:

```python
            source = read_source(source_path)
            text = source.text
...
        page = page_for(source_path, text, lang, rel=rel, sha=source.sha)
```

`results/compositor.py` -- BOTH `lossless` (`:302`, `:309`) and `identity` (`:333`, `:339`):

```python
        source = read_source(path)
        text = source.text
...
        got = set_page(page_for(path, text, lang, sha=source.sha))
```

Add `from comment_review.machine.repo import read_source` to each module's imports.

`scripts/render_page.py:191`:

```python
    src = repo_mod.read_source(path)
    pg = page_mod.page_for(path, src.text, lang, rel=path.as_posix(), sha=src.sha)
```

- [ ] **Step 7: Run the suite**

Run: `uv run pytest -q`
Expected: green. If any test fails with `TypeError: page_for() missing 1 required keyword-only argument`, a call site was missed -- the error names the file.

- [ ] **Step 8: Prove the compositor no longer translates**

Run: `uv run pytest -q && grep -n "read_text" src/comment_review/results/compositor.py`
Expected: tests green, and the grep returns NOTHING. That is `galley-and-compositor-write-path` T4's stated verification.

- [ ] **Step 9: Full gate and commit**

```bash
uv run ruff check . && uv run ty check src/comment_review/ && uv run python scripts/check_shipped_syntax.py
git add -A
git commit -F <message-file>
```

Message: *"page: a page receives its sha, and the compositor stops translating"* -- recording that the two compositor reads were the last `read_text` sites on the write path.

---

### Task 3: The binder reports the page's sha

**Delivers:** spec P2 box 3.

**Files:**
- Modify: `src/comment_review/binder/binder.py` -- delete `sha_of` (`:95-111`), the `import hashlib` (`:38`), and change `bind` (`:147`)
- Test: `tests/test_binder.py`

**Interfaces:**
- Consumes: `Page.sha` from Task 2.
- Produces: no signature change. `bind(pages, absent=False) -> dict` still emits `{"version", "pages": [{"path", "sha", "rows"}]}`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_binder.py`:

```python
def test_the_binder_reports_the_page_s_sha_rather_than_taking_one():
    page = build(SAMPLE)
    page.sha = "notarealsha"
    assert bind([page])["pages"][0]["sha"] == "notarealsha"


def test_only_machine_imports_hashlib():
    """! `machine/` OWNS THE QUERY. Roy, 2026-08-25: the querying of io/git
    software *"should not have left the machine/ modules."*"""
    offenders = [
        p.relative_to(PKG).as_posix()
        for p in PKG.rglob("*.py")
        if "hashlib" in p.read_text(encoding="utf-8") and p.parent.name != "machine"
    ]
    assert offenders == []
```

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/test_binder.py -q -k "sha or hashlib"`
Expected: BOTH fail -- `bind` hashes `page.text`, and `binder.py` imports `hashlib`.

- [ ] **Step 3: Implement**

Delete `import hashlib` from `binder.py`. Delete the whole `sha_of` function. In `bind`, change the one line:

```python
                "sha": page.sha,
```

Add to `bind`'s docstring, above `Args:`:

```
    ! THE SHA IS REPORTED, NOT TAKEN. It arrives on the page from
    `repo.read_source`; this module hashes nothing. Roy, 2026-08-25: *"It is
    information received by page and binder, not something requested by
    page/binder."*
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_binder.py -q`
Expected: green.

- [ ] **Step 5: Full gate and commit**

Message: *"binder: the sha is reported, not taken"*.

---

### Task 4: The notations shape, and its refusal

**Delivers:** spec P1 boxes 1 and 2.

!! **THIS IS A STAND-IN. Roy, 2026-08-25:** *"It is a prototype or stand in for what might need to be built. It will probably not be what gets built so don't over engineer it. We need the shape not the concrete implementation."* **No versioning, no schema evolution, no second accepted form.** The refusal stays because a silent empty read is the defect the binder rewrite was measured on.

**Files:**
- Create: `src/comment_review/desk/notations.py`
- Test: `tests/test_notations.py` (create)

**Interfaces:**
- Produces: `notations.read(text: str) -> tuple[dict[str, str | None], str]` -- `(notations, "")` when it reads, `({}, reason)` when it does not. Mirrors `binder.read`'s contract exactly, deliberately.

- [ ] **Step 1: Write the failing test**

Create `tests/test_notations.py`:

```python
"""What the agents hand the write chain -- an address, and the text for it.

! A STAND-IN. The middle piece is not designed; this is the SHAPE so the write
chain has something to build to. See TODO/notations-collides-with-annotations.md
-- the NAME is deferred, not settled.
"""

import json

import pytest

from comment_review.desk.notations import read


def test_a_well_formed_notations_file_reads():
    got, why = read(json.dumps({"m.py@b1": "# new", "m.py@c0": None}))
    assert why == ""
    assert got == {"m.py@b1": "# new", "m.py@c0": None}


def test_None_is_the_delete():
    got, why = read(json.dumps({"m.py@b1": None}))
    assert why == "" and got["m.py@b1"] is None


@pytest.mark.parametrize(
    "text,fragment",
    [
        ("{not json", "not JSON"),
        ("[]", "not a notations"),
        ('"a string"', "not a notations"),
        (json.dumps({"m.py@b1": 123}), "must be text"),
        (json.dumps({"m.py@b1": ["a", "b"]}), "must be text"),
        (json.dumps({"m.py@b1": ""}), "empty string"),
    ],
)
def test_what_is_refused(text, fragment):
    got, why = read(text)
    assert got == {}
    assert fragment in why


def test_a_refusal_is_never_an_empty_result():
    """!! THE DEFECT THIS EXISTS FOR. A guess that is wrong reads as an EMPTY
    input, which downstream is indistinguishable from a run with nothing to do."""
    got, why = read("[]")
    assert got == {} and why != ""
```

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/test_notations.py -q`
Expected: FAIL -- `ModuleNotFoundError: comment_review.desk.notations`.

- [ ] **Step 3: Implement**

Create `src/comment_review/desk/notations.py`:

```python
"""What the reviewers' marks become, on the way to the galley.

    {"<address>": "<the replacement paragraph>"}   set this place to this text
    {"<address>": null}                            delete what is here

!! A STAND-IN, AND DELIBERATELY SO. Roy, 2026-08-25: *"It is a prototype or
stand in for what might need to be built. It will probably not be what gets
built so don't over engineer it. We need the shape not the concrete
implementation."* The write side is known to work and the middle is not
designed, so this exists to give the chain something to build TO.

! THE NAME IS NOT SETTLED. `notations` sits one letter from the `annotations`
that `binder/annotate.py` already owns for candidate flags on a paragraph.
Deferred, by ruling, until the middle is rewritten --
`TODO/notations-collides-with-annotations.md`.

!! `None` IS THE DELETE AND AN EMPTY STRING IS REFUSED. Roy, 2026-08-25: *"None
is explicit enough."* ! The galley took `""` as its vacation signal until this
landed, and a key whose value failed to serialise arrives looking exactly like
a deliberate deletion. Two spellings for one act is how a bug upstream becomes
a deletion downstream at exit 0.
"""

import json


def read(text: str) -> tuple[dict[str, str | None], str]:
    """The notations, or the reason they could not be read.

    !! IT REFUSES RATHER THAN COPING, which is the shape `binder.read` already
    uses and for the same measured reason: a guess that is wrong reads as an
    EMPTY input, and downstream that is indistinguishable from a run with
    nothing to do.

    Args:
        text: the notations file's contents.

    Returns:
        `(notations, "")` when it reads, or `({}, reason)` when it does not.
    """
    try:
        loaded = json.loads(text)
    # ! ONE CLASS, NOT A TUPLE, so the shipped-code rule against a tuple literal
    # in an `except` does not bite. This is the spelling `binder.read` uses.
    except json.JSONDecodeError as e:
        return {}, f"not JSON ({e})"
    if not isinstance(loaded, dict):
        return {}, f"a JSON {type(loaded).__name__}, not a notations file"
    for address, replacement in loaded.items():
        if replacement is None:
            continue
        if not isinstance(replacement, str):
            return {}, (
                f"{address}: a replacement must be text or null, not"
                f" {type(replacement).__name__}"
            )
        if not replacement:
            return {}, (
                f"{address}: an empty string is not a delete -- null is."
                " Two spellings for one act is how a serialisation bug becomes"
                " a deletion"
            )
    return loaded, ""
```

! **MEASURED before this plan was written:** `machine/exceptions.py` defines `READ_ERRORS`, `TOML_ERRORS`, `TOKENIZE_ERRORS`, `PARSE_ERRORS` and `GIT_ERRORS` -- there is no `JSON_ERRORS`, and `binder.read` catches `json.JSONDecodeError` directly. **Do not add one.** The rule in Global Constraints forbids a tuple LITERAL in an `except`; a single exception class is not a tuple.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_notations.py -q`
Expected: 9 passed.

- [ ] **Step 5: Full gate and commit**

Message: *"desk: the notations shape, refusing rather than coping"* -- saying in the body that it is a stand-in, quoting the ruling.

---

### Task 5: An address resolves against the saved binder

**Delivers:** spec P1 box 3.

**Files:**
- Modify: `src/comment_review/desk/notations.py`
- Test: `tests/test_notations.py`

**Interfaces:**
- Consumes: `binder.rows_of(binder) -> list[dict]`, which stamps each row with `path` and `address`.
- Produces: `notations.by_page(notations, binder) -> tuple[dict[str, dict[str, str | None]], list[str]]` -- `({path: {cue: text_or_None}}, refusals)`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_notations.py`:

```python
from comment_review.binder.binder import bind
from comment_review.desk.notations import by_page
from conftest import SAMPLE, build, by_cue


def _binder():
    return bind([build(SAMPLE)])


def test_an_address_the_binder_carries_resolves_to_its_page_and_cue():
    page = build(SAMPLE)
    cue = next(c for c in by_cue(page) if c.startswith("b"))
    grouped, refused = by_page({f"m.py@{cue}": "# new"}, bind([page]))
    assert refused == []
    assert grouped == {"m.py": {cue: "# new"}}


def test_an_address_no_binder_row_names_is_REFUSED_and_named():
    grouped, refused = by_page({"m.py@b99": "# new"}, _binder())
    assert grouped == {}
    assert any("m.py@b99" in r for r in refused)


def test_a_file_the_binder_never_saw_is_REFUSED():
    grouped, refused = by_page({"other.py@b1": "# new"}, _binder())
    assert grouped == {}
    assert any("other.py@b1" in r for r in refused)


def test_ONE_bad_address_refuses_the_WHOLE_set():
    """!! ABORT-WHOLE. Roy, 2026-08-25: *"fails loud amd stops is the right
    answer for now."* A partial group is a state no page describes."""
    page = build(SAMPLE)
    cue = next(c for c in by_cue(page) if c.startswith("b"))
    grouped, refused = by_page(
        {f"m.py@{cue}": "# good", "m.py@b99": "# bad"}, bind([page])
    )
    assert grouped == {}
    assert len(refused) == 1
```

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/test_notations.py -q -k by_page`
Expected: FAIL -- `ImportError: cannot import name 'by_page'`.

- [ ] **Step 3: Implement**

Add to `notations.py`:

```python
from comment_review.binder.binder import rows_of


def by_page(
    notations: dict[str, str | None], binder: dict
) -> tuple[dict[str, dict[str, str | None]], list[str]]:
    """Group notations by the file they land on, refusing any the binder lacks.

    !! THE SAVED BINDER IS WHAT SAYS WHICH FILE TO RELOAD. Roy, 2026-08-25:
    *"We also have to grab the binder address from the saved material."* An
    address is a key rather than data, and the binder is where the key was
    minted -- so an address it never carried names a place nobody reviewed.

    !! ONE REFUSAL REFUSES THE WHOLE SET, by ruling. Roy, 2026-08-25: *"fails
    loud amd stops is the right answer for now."* PROVISIONAL -- the
    per-page resumable form belongs to the workflow that writes for real.

    Args:
        notations: address -> replacement text, or None to delete.
        binder: as `binder.read` returned it.

    Returns:
        `({path: {cue: replacement}}, [])`, or `({}, refusals)`.
    """
    known = {row["address"]: row for row in rows_of(binder)}
    refused = [a for a in notations if a not in known]
    if refused:
        return {}, [f"{a}: no binder row carries this address" for a in sorted(refused)]
    grouped: dict[str, dict[str, str | None]] = {}
    for address, replacement in notations.items():
        row = known[address]
        grouped.setdefault(str(row["path"]), {})[str(row["cue"])] = replacement
    return grouped, []
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_notations.py -q`
Expected: 13 passed.

- [ ] **Step 5: Full gate and commit**

Message: *"desk: an address resolves against the saved binder, or the set refuses"*.

---

### Task 6: The galley takes a page and cues, and `None` deletes

**Delivers:** spec P3 box 1.

!! **27 EXISTING SITES PASS `m.py@<cue>` AND THEY ARE UPDATED, NOT DUPLICATED.** Roy, 2026-08-25: *"lets make certain we are not duplicating tests only adding new to truly new functionality."* 25 in `tests/test_galley.py`, 2 in `tests/test_compositor.py`. **Add no galley cases in this task.**

**Files:**
- Modify: `src/comment_review/results/galley.py` -- `reset` at `:83-192`
- Modify: `tests/test_galley.py` (25 sites), `tests/test_compositor.py` (2 sites)

**Interfaces:**
- Produces: `galley.reset(page, edits: dict[str, str | None]) -> list[str]`. Keys are CUES (`"b1"`), not addresses. `None` vacates; `""` is refused.

- [ ] **Step 1: Change the existing tests to the new spelling**

In `tests/test_galley.py` and `tests/test_compositor.py`, replace every `f"m.py@{cue}"` key with `cue`, and every drop's `""` value with `None`. Do this with a `.py` script, not `sed`:

```python
from pathlib import Path

for name in ("tests/test_galley.py", "tests/test_compositor.py"):
    p = Path(name)
    t = p.read_text(encoding="utf-8")
    before = t
    t = t.replace('f"m.py@{cue}"', "cue")
    t = t.replace('f"m.py@{next(iter(by_cue(sample)))}"', "next(iter(by_cue(sample)))")
    assert t != before, f"{name}: nothing replaced -- check the spellings first"
    p.write_text(t, encoding="utf-8", newline="")
```

! **The `assert` is the point.** A replacement that matched nothing must stop the script, not write the file back unchanged.

Then update the two refusal tests by hand: `TestWhatTheGalleyRefuses::test_a_replacement_that_is_not_TEXT` must now treat `None` as VALID and `""` as refused.

- [ ] **Step 2: Run and watch them fail**

Run: `uv run pytest tests/test_galley.py -q`
Expected: FAIL -- `reset` still splits its keys with `cue_of`, so a bare cue finds no place.

- [ ] **Step 3: Implement**

In `galley.py`, change `reset`'s signature and its `Args:`:

```python
def reset(page, edits: dict[str, str | None]) -> list[str]:
```

```
    Args:
        page: the page to change, built from the file as it reads NOW.
        edits: cue -> the replacement paragraph as text, or None to vacate.
```

Add to the docstring, above `Args:`:

```
    !! IT IS HANDED A PAGE AND CUES, AND RESOLVES NEITHER. Roy, 2026-08-25:
    *"the galley shouldn't be resolving the page ... it should get handed the
    page, the cues-new text or a delete."* A page names its own file, so the
    path half of an address is a fact the caller already had.

    !! `None` IS THE DELETE AND `""` IS REFUSED. Roy, 2026-08-25: *"None is
    explicit enough."* ! An empty string was the vacation signal until then,
    which made a failed serialisation upstream indistinguishable from a
    deliberate deletion.
```

Replace the body's key handling. `cue_of` is no longer needed for the edits, only for reading a paragraph's own address:

```python
    by_place: dict[str, list] = {}
    by_symbol = {b.symbol: b for b in page if b.symbol}
    for b in page:
        if b.address:
            by_place.setdefault(cue_of(b.address).cue, []).append(b)
    refused = []
    for where, replacement in edits.items():
        found = by_place.get(where)
        if not found:
            refused.append(f"{where}: this page carries no such place")
            continue
        if len(found) > 1:
            refused.append(
                f"{where}: {len(found)} paragraphs share this place, so no"
                " replacement can be placed against it"
            )
            continue
        if replacement is None:
            owns_leading = not where.startswith(ON)
            _vacate(
                found[0],
                by_symbol.get(page.leading.get(where, "")) if owns_leading else None,
            )
            continue
        if not isinstance(replacement, str) or not replacement:
            refused.append(
                f"{where}: a replacement must be non-empty text, or None to"
                f" delete -- not {type(replacement).__name__}"
            )
            continue
        found[0].raw_lines = constants.text_lines(replacement)
    return refused
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_galley.py tests/test_compositor.py -q`
Expected: green, with the SAME number of galley tests as before -- none added.

- [ ] **Step 5: Prove no address reaches the galley**

Run: `grep -n "@" src/comment_review/results/galley.py | grep -v "^.*#"`
Expected: no `cue_of(address)` on an edit key remains.

- [ ] **Step 6: Full gate and commit**

Message: *"galley: handed a page and cues, and None is the delete"*.

---

### Task 7: Retire `drifted`

**Delivers:** spec P3 box 2.

**Files:**
- Modify: `src/comment_review/results/galley.py` -- delete `drifted` (`:213` to the end of the function)
- Modify: `src/comment_review/commands/galley.py` -- its call site
- Modify: `docs/history.md` -- record the mechanism that was removed

**Interfaces:**
- Removes: `galley.drifted(page, census)`. Nothing replaces it inside `results/`; the sha gate in Task 9 answers the same question in one comparison.

! **NOTHING IS ADDED TO PROVE IT IS GONE.** Roy: *"You just can't put more tests back to prove something cut is gone ... There are an infinite number of 'not' things."*

- [ ] **Step 1: Find every caller**

Run: `grep -rn "drifted" src/ tests/ scripts/`
Record what you find before deleting anything.

- [ ] **Step 2: Delete the function and its callers**

Remove `drifted` from `galley.py`. Remove its invocation from `commands/galley.py`, and any now-unused imports YOUR change orphaned (ruff will name them).

- [ ] **Step 3: Prove no binder or census row is read on the write side**

Run: `grep -rn "census\|rows_of\|binder" src/comment_review/results/`
Expected: NOTHING. That is the spec's stated verification for this box.

- [ ] **Step 4: Record the removal**

Add an entry to `docs/history.md` naming `drifted`, what it compared (`raw_lines` per paragraph, after a full re-parse), why it went (the sha answers it in one comparison, before anything is parsed), and this commit.

- [ ] **Step 5: Full gate and commit**

Run the full gate. Expected: green, with FEWER tests than before -- the `drifted` tests leave with it.

Message: *"galley: drifted retired -- the sha answers it in one comparison"*.

---

### Task 8: A flow owns the order, and it is data

**Delivers:** spec P4 box 1, P6 box 1, and **P2 box 4** -- the `recorded` dict below is where the sha is read OUT of the saved binder rather than recomputed from a file.

**Files:**
- Create: `src/comment_review/flows/write.py`
- Test: `tests/test_write_chain.py` (create)

**Interfaces:**
- Consumes: `notations.read`, `notations.by_page`, `binder.read`, `repo.read_source`, `page_for`, `language_for`, `galley.reset`, `compositor.set_page`, `compositor.draft`.
- Produces:
  - `write.STEPS: tuple[str, ...]` -- `("read", "verify", "edit", "set", "draft", "reread", "prove")`
  - `write.Refusal(step: str, path: str, why: str)`
  - `write.Drafted(path: str, draft: Path, sha: str)`
  - `write.run(notations, binder, repo, into) -> tuple[list[Drafted], list[Refusal]]`

- [ ] **Step 1: Write the failing test**

Create `tests/test_write_chain.py`:

```python
"""The chain from notations to a drafted file a human can read.

! THE ORDER IS DATA. A missing check is then a missing element rather than a
forgotten call -- which is the one failure a runner that hard-codes its
sequence cannot show you.
"""

import json
from pathlib import Path

from conftest import SAMPLE, SRC, build, by_cue

from comment_review.binder.binder import bind
from comment_review.flows import write


def test_the_chain_IS_this_list():
    assert write.STEPS == ("read", "verify", "edit", "set", "draft", "reread", "prove")


def _tree(tmp_path):
    """A one-file repo, and the binder taken over it."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page = build(SAMPLE)
    return repo, bind([page]), page


def test_a_notation_reaches_a_drafted_file(tmp_path):
    repo, binder, page = _tree(tmp_path)
    cue = next(c for c in by_cue(page) if c.startswith("b"))
    into = tmp_path / "out"
    drafted, refused = write.run({f"m.py@{cue}": "# REPLACED"}, binder, repo, into)
    assert refused == []
    assert len(drafted) == 1
    assert "# REPLACED" in drafted[0].draft.read_text(encoding="utf-8")


def test_nothing_under_the_repo_is_touched(tmp_path):
    repo, binder, page = _tree(tmp_path)
    cue = next(c for c in by_cue(page) if c.startswith("b"))
    before = (repo / "m.py").read_bytes()
    write.run({f"m.py@{cue}": "# REPLACED"}, binder, repo, tmp_path / "out")
    assert (repo / "m.py").read_bytes() == before


def test_a_refusal_NAMES_ITS_STEP(tmp_path):
    repo, binder, _ = _tree(tmp_path)
    _, refused = write.run({"m.py@b99": "# x"}, binder, repo, tmp_path / "out")
    assert refused and refused[0].step in write.STEPS
```

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/test_write_chain.py -q`
Expected: FAIL -- `ModuleNotFoundError: comment_review.flows.write`.

- [ ] **Step 3: Implement**

Create `src/comment_review/flows/write.py`:

```python
"""From the reviewers' notations to a file a human can read.

    notations + the saved binder
        -> reload the page FROM DISK
        -> the sha is the one the binder recorded
        -> galley           the marks are put on the page
        -> compositor       the page is set as text
        -> draft            a temporary file, never the original
        -> read it back     each notation is at the cue it was given
        -> prove            only comments changed
        -> the human

!! IT STOPS AT THE TEMPORARY FILE. Roy, 2026-08-25: *"The workflow stops at
making a temporary file for the human to review. The final human-review
human-edit machine-review machine copy is its own workflow."* So `approve` is
not called here, and neither is anything transactional -- the per-page state,
the manifest and the resumable retry all belong to that second workflow.

!! NOTHING TRANSFERS FROM THE BINDER TO THE END EXCEPT TWO VALUES. Roy,
2026-08-24: *"Nothing will transfer from the binder to the end."* The ADDRESS
crosses as a key, and the SHA crosses as the thing the verification compares.
No paragraph text, kind or anchor does -- the page is read again from disk.

! THE ORDER LIVES HERE AND NOWHERE ELSE. The galley edits, the compositor sets,
and neither knows what runs next. `STEPS` is the sequence as DATA so a missing
check is a missing element rather than a forgotten call.
"""

from pathlib import Path
from typing import NamedTuple

from comment_review.binder.page import page_for
from comment_review.desk import notations as notations_mod
from comment_review.machine.repo import read_source
from comment_review.reading.lexer import language_for
from comment_review.results import compositor, galley

#: The chain, as data. ! A test asserts this tuple, so removing a check is a
#: visible deletion rather than a call somebody forgot to make.
STEPS = ("read", "verify", "edit", "set", "draft", "reread", "prove")


class Refusal(NamedTuple):
    """One reason the run stopped, and where.

    ! A REFUSAL NAMES ITS STEP. `census.py` was measured catching bare
    `Exception` and printing a type name, which tells a reader that something
    went wrong and nothing about where to look.
    """

    step: str
    path: str
    why: str


class Drafted(NamedTuple):
    """One page set into a temporary file, and the bytes it was reviewed at."""

    path: str
    draft: Path
    sha: str


def run(
    notations: dict[str, str | None], binder: dict, repo: Path, into: Path
) -> tuple[list[Drafted], list[Refusal]]:
    """The whole chain, or nothing at all.

    !! A REFUSAL ABORTS THE RUN WHOLE, by ruling. Roy, 2026-08-25: *"fails loud
    amd stops is the right answer for now."* Every draft this run wrote is
    removed, so a stopped run leaves no half-set of files that no page
    describes. ! PROVISIONAL: the resumable per-page form belongs to the
    workflow that writes over the real files.

    Args:
        notations: address -> replacement text, or None to delete.
        binder: as `binder.read` returned it.
        repo: the checkout the pages are read from.
        into: the directory drafts are written to. Created if absent.

    Returns:
        `(drafted, [])` when every page passed, or `([], refusals)`.
    """
    grouped, unresolved = notations_mod.by_page(notations, binder)
    if unresolved:
        return [], [Refusal("read", "", why) for why in unresolved]

    # ! THE `verify` STEP IS ADDED IN TASK 9, test-first. `recorded` and the
    # comparison that reads it arrive there together; leaving them out here is
    # what lets Task 9's test fail before it passes.
    recorded: dict[str, str] = {}
    into.mkdir(parents=True, exist_ok=True)
    drafted: list[Drafted] = []
    refusals: list[Refusal] = []

    for rel, edits in sorted(grouped.items()):
        made, why = _one(rel, edits, recorded.get(rel, ""), repo, into)
        if why is not None:
            refusals.append(why)
        elif made is not None:
            drafted.append(made)

    if refusals:
        for made in drafted:
            made.draft.unlink(missing_ok=True)
        return [], refusals
    return drafted, []


def _one(
    rel: str, edits: dict[str, str | None], recorded: str, repo: Path, into: Path
) -> tuple[Drafted | None, Refusal | None]:
    """One page through every step, or the first step that refused."""
    source_path = repo / rel
    try:
        source = read_source(source_path)
    except OSError as e:
        return None, Refusal("read", rel, f"could not be read ({e})")

    # ! THE `verify` STEP LANDS HERE IN TASK 9, test-first.

    lang = language_for(source_path)
    if lang is None:
        return None, Refusal("edit", rel, "no language record, so it has no places")
    page = page_for(source_path, source.text, lang, rel=rel, sha=source.sha)

    placed = galley.reset(page, edits)
    if placed:
        return None, Refusal("edit", rel, "; ".join(placed))

    text = compositor.set_page(page)
    target = into / Path(rel).name
    target.write_text(text, encoding="utf-8", newline="")
    return Drafted(rel, target, source.sha), None
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_write_chain.py -q`
Expected: 4 passed.

- [ ] **Step 5: Full gate and commit**

Message: *"flows: the write chain owns the order, and the order is data"*.

---

### Task 9: The sha gate refuses a shifted file

**Delivers:** spec P2 boxes 4, 5 and 6. Works `a-page-carries-no-identity` T2, T3 (as restated) and T4.

**Files:**
- Modify: `src/comment_review/flows/write.py` -- add the `verify` step
- Modify: `src/comment_review/results/galley.py` -- the per-paragraph comparison's comment
- Test: `tests/test_write_chain.py`

**Interfaces:** no new symbols. Task 8 left `recorded` empty and the `verify` step unwritten so that this task's test can fail first.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_write_chain.py`:

```python
class TestTheFileMustBeTheONEThatWasReviewed:
    """!! THE CHECK THE READ-ONLY ROLES HAVE NEVER HAD. No agent file declares
    `tools:`, so all six inherit Edit and Write -- read-only is prose. This is
    what catches a reviewer that edited the file it was reading.
    See TODO/reviewers-are-not-read-only.md."""

    def test_a_ONE_BYTE_edit_since_the_binder_refuses(self, tmp_path):
        repo, binder, page = _tree(tmp_path)
        cue = next(c for c in by_cue(page) if c.startswith("b"))
        (repo / "m.py").write_text(SAMPLE + "\n", encoding="utf-8", newline="")
        drafted, refused = write.run(
            {f"m.py@{cue}": "# REPLACED"}, binder, repo, tmp_path / "out"
        )
        assert drafted == []
        assert refused[0].step == "verify"

    def test_NO_DRAFT_is_written_when_the_sha_disagrees(self, tmp_path):
        repo, binder, page = _tree(tmp_path)
        cue = next(c for c in by_cue(page) if c.startswith("b"))
        (repo / "m.py").write_text(SAMPLE + "\n", encoding="utf-8", newline="")
        into = tmp_path / "out"
        write.run({f"m.py@{cue}": "# REPLACED"}, binder, repo, into)
        assert list(into.iterdir()) == []

    def test_an_UNCHANGED_file_passes(self, tmp_path):
        repo, binder, page = _tree(tmp_path)
        cue = next(c for c in by_cue(page) if c.startswith("b"))
        drafted, refused = write.run(
            {f"m.py@{cue}": "# REPLACED"}, binder, repo, tmp_path / "out"
        )
        assert refused == [] and len(drafted) == 1
```

! **The third test is what makes the first two mean something.** A gate that refuses everything passes both refusal cases.

- [ ] **Step 2: Run them and watch two fail**

Run: `uv run pytest tests/test_write_chain.py -q -k Reviewed`
Expected: the first two FAIL -- Task 8 left `recorded` empty and wrote no `verify` step, so a shifted file drafts happily. The third PASSES already, which is what makes it a control rather than a second assertion of the same thing.

- [ ] **Step 3: Add the `verify` step**

In `flows/write.py`, fill `recorded` in `run` -- **this is where the sha is read OUT of the saved binder** rather than recomputed from a file:

```python
    recorded = {
        str(page.get("path", "")): str(page.get("sha", ""))
        for page in binder.get("pages", [])
    }
```

Pass it into `_one` (add a `recorded: str` parameter, supplied at the call site as `recorded.get(rel, "")`), and add the comparison immediately after the read:

```python
    if not recorded or source.sha != recorded:
        return None, Refusal(
            "verify",
            rel,
            "the file has changed since it was reviewed -- reviewed at"
            f" {recorded or '<nothing recorded>'}, reads now as {source.sha}",
        )
```

!! **AN ABSENT RECORDED SHA REFUSES; IT DOES NOT PASS.** `not recorded` is the first clause on purpose -- a binder page carrying no sha would otherwise compare `""` against a real hash, and a future shape that dropped the field would turn this gate off silently rather than loudly.

- [ ] **Step 4: Run them again**

Run: `uv run pytest tests/test_write_chain.py -q`
Expected: all green, including the control.

- [ ] **Step 5: Make the comment honest**

In `galley.py`, the surviving per-paragraph comparison comment must name the sha as what answers *did the file shift*. Find any prose still claiming the per-paragraph compare is the staleness check and correct it to say the sha answers it in one comparison, before anything is parsed.

- [ ] **Step 6: Mark off what this task delivered**

```bash
uv run python scripts/todo_tool.py check a-page-carries-no-identity.md 2
uv run python scripts/todo_tool.py check a-page-carries-no-identity.md 3
uv run python scripts/todo_tool.py check a-page-carries-no-identity.md 4
```

Then tick P2 boxes 4, 5 and 6 in `docs/plans/0.2.4-the-write-chain-of-command.md`. `a-page-carries-no-identity` should now read **4 of 4**.

- [ ] **Step 7: Full gate and commit**

Message: *"flows: a file that shifted since review refuses, and no draft is written"*.

---

### Task 10: The draft is read back, at the cue it was given

**Delivers:** spec P5 boxes 1 and 2.

!! **BOX 1 STRENGTHENS AN EXISTING TEST, IT DOES NOT ADD ONE.** `tests/test_compositor.py:164` already does reset -> set -> re-read, then asserts `any(b.raw_lines == ["# REPLACED"] for b in again.paragraphs if b.address)` -- **`any` over every addressed paragraph, so text landing at the WRONG cue passes.**

**Files:**
- Modify: `tests/test_compositor.py:164-175`
- Modify: `src/comment_review/flows/write.py` -- add the `reread` step
- Test: `tests/test_write_chain.py`

**Interfaces:**
- Produces: `write._reread(rel, target, edits) -> Refusal | None`, called by `_one` after the draft is written.

- [ ] **Step 1: Strengthen the weak test**

Replace `test_the_composed_file_re_reads_to_the_same_prose` in `tests/test_compositor.py`:

```python
    def test_the_composed_file_re_reads_with_the_text_AT_ITS_CUE(self, sample):
        """! `any` OVER THE PAGE WAS THE ASSERTION UNTIL 2026-08-25, so text
        landing at the WRONG cue passed. The cue is the whole claim."""
        from comment_review.results.galley import reset

        cue = next(
            c
            for c, b in by_cue(sample).items()
            if c.startswith("b") and any(x.strip() for x in b.raw_lines)
        )
        reset(sample, {cue: "# REPLACED"})
        again = build(set_page(sample))
        assert by_cue(again)[cue].raw_lines == ["# REPLACED"]
```

- [ ] **Step 2: Run it and watch it fail if you break it**

Run: `uv run pytest tests/test_compositor.py -q -k AT_ITS_CUE`
Expected: PASS. **Then prove it can fail:** temporarily change the assertion's `cue` to a different existing cue and confirm it goes RED. Revert.

- [ ] **Step 3: Write the failing chain test**

Append to `tests/test_write_chain.py`:

```python
def test_the_drafted_FILE_holds_each_notation_at_its_cue(tmp_path):
    repo, binder, page = _tree(tmp_path)
    cue = next(c for c in by_cue(page) if c.startswith("b"))
    drafted, refused = write.run(
        {f"m.py@{cue}": "# REPLACED"}, binder, repo, tmp_path / "out"
    )
    assert refused == []
    again = build(drafted[0].draft.read_text(encoding="utf-8"))
    assert by_cue(again)[cue].raw_lines == ["# REPLACED"]
```

- [ ] **Step 4: Add the `reread` step**

In `flows/write.py`, after the draft is written in `_one`:

```python
    off = _reread(rel, target, edits)
    if off is not None:
        target.unlink(missing_ok=True)
        return None, off
    return Drafted(rel, target, source.sha), None
```

And the function:

```python
def _reread(rel: str, target: Path, edits: dict[str, str | None]) -> Refusal | None:
    """Read the draft back as a page: is each notation at the cue it was given?

    !! IT IS READ FROM DISK, NOT FROM THE PAGE IN HAND. Roy, 2026-08-24: the
    workflow *"Sends that through the page system again to make certain that
    the agents put the right comments in the right places."* A page still in
    memory would be agreeing with itself -- the shape `docs/gates.md` records
    the round trip scoring 699 of 699 on.
    """
    source = read_source(target)
    lang = language_for(target)
    if lang is None:
        return Refusal("reread", rel, "the draft has no language record")
    page = page_for(target, source.text, lang, rel=rel, sha=source.sha)
    placed = {cue_of(b.address).cue: b for b in page if b.address}
    for where, replacement in edits.items():
        got = placed.get(where)
        if got is None:
            return Refusal("reread", rel, f"{where}: the draft carries no such place")
        want = [] if replacement is None else constants.text_lines(replacement)
        if got.raw_lines != want:
            return Refusal(
                "reread", rel, f"{where}: holds {got.raw_lines!r}, was given {want!r}"
            )
    return None
```

Add `from comment_review.machine import constants` and `from comment_review.reading.addresser import cue_of` to the module's imports.

- [ ] **Step 5: Run the tests**

Run: `uv run pytest tests/test_write_chain.py tests/test_compositor.py -q`
Expected: green.

- [ ] **Step 6: Full gate and commit**

Message: *"flows: the draft is read back from disk, at the cue it was given"* -- recording in the body that the existing re-read assertion could not fail on a wrong cue.

---

### Task 11: `prove_unchanged` runs on the draft

**Delivers:** spec P5 box 3.

**Files:**
- Modify: `src/comment_review/flows/write.py`
- Test: `tests/test_write_chain.py`

**Interfaces:**
- Consumes: `prove_unchanged.code_fingerprint(text, path) -> tuple[str, str]` -- `kind` is `"ast"`, `"stripped"` or `"unprovable"`; **an unprovable file carries an empty fingerprint and must never be reported as proven.**
- Produces: `write._prove(rel, source_text, drafted_text, path) -> Refusal | None`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_write_chain.py`:

```python
class TestOnlyCommentsChange:
    """Roy, 2026-08-25: prove_unchanged runs *"just before the human review and
    just after the human review edit piece just to be certain we only changed
    only comments."* This is the first of those two."""

    def test_a_notation_that_alters_CODE_refuses(self, tmp_path):
        repo, binder, page = _tree(tmp_path)
        cue = next(c for c in by_cue(page) if c.startswith("b"))
        drafted, refused = write.run(
            {f"m.py@{cue}": "raise SystemExit(1)"}, binder, repo, tmp_path / "out"
        )
        assert drafted == []
        assert refused[0].step == "prove"

    def test_NO_temporary_file_is_offered_when_the_proof_fails(self, tmp_path):
        repo, binder, page = _tree(tmp_path)
        cue = next(c for c in by_cue(page) if c.startswith("b"))
        into = tmp_path / "out"
        write.run({f"m.py@{cue}": "raise SystemExit(1)"}, binder, repo, into)
        assert list(into.iterdir()) == []

    def test_an_ordinary_comment_change_PASSES(self, tmp_path):
        repo, binder, page = _tree(tmp_path)
        cue = next(c for c in by_cue(page) if c.startswith("b"))
        drafted, refused = write.run(
            {f"m.py@{cue}": "# still a comment"}, binder, repo, tmp_path / "out"
        )
        assert refused == [] and len(drafted) == 1
```

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/test_write_chain.py -q -k OnlyComments`
Expected: the first two FAIL -- nothing proves anything yet, so a code-altering notation drafts happily.

- [ ] **Step 3: Implement**

In `flows/write.py`, call it after `_reread` succeeds:

```python
    # !! `read_source`, NOT `read_text`. The translating reader is what this
    # branch exists to remove from the write path -- reading the draft through
    # it here would compare text read one way against text read another.
    unproven = _prove(rel, source.text, read_source(target).text, source_path)
    if unproven is not None:
        target.unlink(missing_ok=True)
        return None, unproven
    return Drafted(rel, target, source.sha), None
```

```python
def _prove(rel: str, before: str, after: str, path: Path) -> Refusal | None:
    """Is the executable code in the draft the code that was there before?

    !! AN UNPROVABLE FILE IS REFUSED, NOT PASSED. `code_fingerprint` returns an
    EMPTY fingerprint for a file it cannot strip, and two empty strings compare
    equal -- so reading its verdict without reading its KIND proves every
    unprovable file identical to every other.
    """
    kind, want = code_fingerprint(before, path)
    got_kind, got = code_fingerprint(after, path)
    if kind == "unprovable" or got_kind == "unprovable":
        return Refusal("prove", rel, "the code in this file cannot be proven unchanged")
    if want != got:
        return Refusal("prove", rel, "the executable code is not what it was")
    return None
```

Add `from comment_review.results.prove_unchanged import code_fingerprint`.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_write_chain.py -q`
Expected: green.

- [ ] **Step 5: Full gate and commit**

Message: *"flows: the draft is proven to change only comments"*.

---

### Task 12: A command exposes the flow

**Delivers:** spec P4 box 2. Works `the-flow-lives-in-the-command` task 5, the galley half.

**Files:**
- Create: `src/comment_review/commands/write.py`
- Modify: `src/comment_review/__main__.py:22-29` -- add `"write"` to `COMMANDS`
- Test: `tests/test_write_chain.py`

**Interfaces:**
- Produces: `commands/write.py::main(argv) -> int`. **It parses arguments and calls `flows.write.run`. It holds no orchestration** -- that is the whole point of the task.

- [ ] **Step 1: Write the failing test**

```python
def test_the_command_holds_no_orchestration():
    """! A COMMAND EXPOSES A FLOW; IT IS NOT ONE. `commands/census.py` took 446
    lines calling page_for directly while flows/census.py kept 261 of helpers.
    See TODO/the-flow-lives-in-the-command.md."""
    text = (SRC / "comment_review" / "commands" / "write.py").read_text(
        encoding="utf-8"
    )
    for forbidden in ("page_for", "galley.reset", "set_page", "code_fingerprint"):
        assert forbidden not in text


def test_write_is_a_named_command():
    from comment_review.__main__ import COMMANDS

    assert "write" in COMMANDS


def test_an_out_that_overlaps_the_repo_is_REFUSED(tmp_path, capsys, monkeypatch):
    """!! THE DESTRUCTIVE CASE, MEASURED 2026-08-22 on the galley: on an
    overlap the per-file guard is satisfied by the SOURCE FILE ITSELF, so the
    draft was written over the file under review at exit 0."""
    from comment_review.commands import write as cmd

    repo, _, _ = _tree(tmp_path)
    monkeypatch.setattr(
        "sys.argv",
        ["write", "--repo", str(repo), "--binder", "b.json",
         "--notations", "n.json", "--out", str(repo / "inside")],
    )
    assert cmd.main() == 2
    assert "REFUSED" in capsys.readouterr().out
```

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/test_write_chain.py -q -k command`
Expected: FAIL -- the file does not exist.

- [ ] **Step 3: Implement**

Create `src/comment_review/commands/write.py`:

```python
"""Draft every page the notations touch, for a human to read.

    comment_review write --binder B.json --notations N.json --repo . --out DIR

! IT EXPOSES `flows.write`; IT ORCHESTRATES NOTHING. The order of the chain
lives in the flow, so this file parses arguments, reads two files and prints.
"""

import argparse
from pathlib import Path

from comment_review.binder import binder as binder_mod
from comment_review.desk import notations as notations_mod
from comment_review.flows import write
from comment_review.machine import constants, exceptions


def main() -> int:
    """Read the notations and the binder, run the chain, report what refused."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".", help="repo root the addresses resolve against")
    ap.add_argument("--binder", required=True, help="the binder the agents ruled on")
    ap.add_argument(
        "--notations",
        required=True,
        help='JSON: {"<address>": "<replacement paragraph>"}, or null to delete',
    )
    ap.add_argument("--out", required=True, help="directory the drafts are written to")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    out = Path(args.out).resolve()
    # !! `--out` MUST BE DISJOINT FROM `--repo`, and the per-file guard cannot
    # ask this. On an OVERLAP a target lands inside `--out` by way of being the
    # source file itself -- MEASURED 2026-08-22 on `commands/galley.py`, which
    # overwrote the file under review, printed `1 page(s) set` and exited 0.
    # ! `is_relative_to` IS TRUE OF A PATH AND ITSELF, which is why both
    # directions are tested and an equality test would be redundant.
    if out.is_relative_to(repo) or repo.is_relative_to(out):
        print(
            f"REFUSED: --out {out} overlaps --repo {repo}, so a draft would be"
            " written over the files under review -- nothing written"
        )
        return 2
    try:
        binder_text = Path(args.binder).read_text(encoding="utf-8")
        notations_text = Path(args.notations).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as e:
        print(f"CANNOT READ ({type(e).__name__}) -- nothing written")
        return 2

    held, why = binder_mod.read(binder_text)
    if why:
        print(f"CANNOT READ THE BINDER: {why} -- nothing written")
        return 2
    marks, why = notations_mod.read(notations_text)
    if why:
        print(f"CANNOT READ THE NOTATIONS: {why} -- nothing written")
        return 2

    drafted, refused = write.run(marks, held, repo, out)
    for stopped in refused:
        print(f"REFUSED at {stopped.step}: {stopped.path or '<the set>'} -- {stopped.why}")
    if refused:
        print(f"{len(refused)} refusal(s) -- nothing drafted")
        return 1
    for made in drafted:
        print(f"{made.path} -> {made.draft}")
    print(f"{len(drafted)} page(s) drafted for review")
    return 0
```

! **`constants` is imported for the console guard.** Call `constants.utf8_console()` as the first line of `main` if that is what `commands/galley.py` does; match it exactly rather than inventing a second spelling. If `galley.py` calls it elsewhere, follow that instead and drop the import.

**If you find yourself importing `page_for`, stop -- that belongs in the flow, and the test in Step 1 will fail.**

- [ ] **Step 4: Run the tests and the command**

```bash
uv run pytest tests/test_write_chain.py -q
uv run python src/comment-review.py write --help
```

- [ ] **Step 5: Full gate and commit**

Message: *"commands: write exposes the chain and orchestrates nothing"*.

---

### Task 13: The rulings are recorded, and the plan is closed out

**Delivers:** spec P7 box 1.

**Files:**
- Modify: `docs/decision-log.md`
- Modify: `docs/plans/0.2.4-the-write-chain-of-command.md` -- tick every box
- Modify: `plugins/` -- via the build

- [ ] **Step 1: Record the rulings**

Add the ten dated 2026-08-24 / 2026-08-25 rulings from the spec's table to `docs/decision-log.md`, each findable by date and subject. Cite as `decision-log.md TOPIC: #N`.

- [ ] **Step 2: Build the plugin**

```bash
uv run python scripts/build_plugin.py
uv run python scripts/build_plugin.py --check
```

- [ ] **Step 3: Prove every box was ticked as it was earned**

Each task ticked its own -- see *Marking off `P` and `T`*. This step VERIFIES that, it does not
do it in bulk:

```bash
grep -c '^- \[ \]' docs/plans/0.2.4-the-write-chain-of-command.md   # expect 0
uv run python scripts/todo_tool.py resync
uv run python scripts/todo_tool.py list --owner backend | grep -E "a-page-carries|galley-and-compositor|flow-lives|two-areas"
```

Expected: **0 open boxes** on the `P` plan; `a-page-carries-no-identity` at **4/4**;
`galley-and-compositor-write-path` advanced by two. `two-areas-have-no-tests` and
`the-flow-lives-in-the-command` are UNCHANGED in count and each carry a new note -- they were
answered in part.

!! **A BOX STILL OPEN IS WORK THAT WAS NOT DONE.** File it in `TODO/` before this plan closes.
*"Anything in a plan that does not get done is filed in `TODO/` before the plan closes."*

- [ ] **Step 4: Full gate, including the ones only a release runs**

```bash
uv run pytest -q
uv run ruff check . && uv run ruff format --check .
uv run ty check src/comment_review/
uv run python scripts/check_shipped_syntax.py
uv run python scripts/check_vocabulary.py
uv run python scripts/build_plugin.py --check
uv run python scripts/todo_tool.py resync
claude plugin validate plugins/comment-review
```

- [ ] **Step 5: Commit**

Message: *"docs: the write chain's rulings, recorded"*.

---

## What this plan does NOT do

| | why |
| --- | --- |
| build the desk that emits notations | it is in `prototype/`; this builds TO its output |
| workflow 2 -- human edit, machine review, the real write | Roy's split, 2026-08-25. `approve()` is not called here |
| per-page state, a manifest, resumability | all workflow 2, and already designed in the custody spec's last section |
| `io.py` and its gate | another spec's scope, and a `systems` gate does not belong on a `backend` branch |
| `galley-and-compositor-write-path` T5, T8, T9, T10 | write-path work this chain does not reach. Left filed |
| `nothing-runs-the-whole-chain` | its T1 names `seed, record, join`, all in `prototype/`. Not workable as written |
