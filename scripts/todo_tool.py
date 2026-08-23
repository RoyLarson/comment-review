"""Write-side companion to scripts/tests/test_todo_counts_agree.py.

Creates, edits, and closes TODO/*.md files and keeps TODO/README.md's
tables in sync with them. The boxes stay the source of truth — every
mutating command here recomputes Progress:/README N/M from the boxes it
just wrote rather than incrementing a counter, so a tool-driven edit
cannot itself introduce the drift test_todo_counts_agree.py checks for.

Every write goes through `_write`, a crash-safe primitive (same-directory
temp file, byte-exact round-trip verification, atomic replace) — a disk
fault or a pre-existing Progress/boxes disagreement raises a clean
`_WriteCheckFailure` instead of ever leaving a partial or corrupted file
on disk.

Run: uv run python scripts/todo_tool.py <command> --help
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import textwrap
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parent.parent
TODO = ROOT / "TODO"

_BOX = re.compile(r"^\s*- \[([ xX])\]", re.MULTILINE)
_PROGRESS = re.compile(r"^Progress:\s*(\d+)\s+of\s+(\d+)\s+tasks?\s+done", re.MULTILINE)
# Named, not numbered: the `roy` column sits BETWEEN owner and the counts, so
# every positional index past it shifts when a column is added. Six call sites
# and test_todo_counts_agree.py read these, and a silently renumbered group is
# the paired-value drift conventions.md warns about.
_ROW_PREFIX = (
    r"^\|\s*\[(?P<slug>[^\]]+)\]\((?P<file>[^)]+\.md)\)\s*"
    r"\|(?P<owner>[^|]*)"
    r"\|(?P<roy>[^|]*)"
    r"\|\s*(?P<done>\d+)\s*/\s*(?P<total>\d+)\s*\|"
)
_ROW = re.compile(_ROW_PREFIX, re.MULTILINE)
# Hyphen as well as space, so `Requires-Roy:` starts a field rather than reading
# as a continuation of `Owner:` above it. Side effect, measured over all 288
# files: 5 `Raised:` values shrink, because `Also-found:`/`Cross-ref:`/
# `Follow-up:` now end that field instead of being absorbed into it.
_FIELD_START = re.compile(r"^[A-Za-z][A-Za-z -]*:")

REQUIRES_ROY_FIELD = "Requires-Roy"
ROY_YES, ROY_NO = "yes", "—"

# ONE definition of an Open table's shape — `_insert_section` builds new
# sections from these and `resync` checks existing ones against them, so a
# column cannot be added to one and missed by the other.
TABLE_HEADER = "| file | owner | roy? | done | what |"
TABLE_SEPARATOR = "| --- | --- | :-: | ---: | --- |"


LANES = (
    # ! LOCAL PATCH, not upstream. This repo's four lanes -- see `docs/lanes.md`.
    # `_owner_cell` keeps only names it finds HERE, so a lane missing from this
    # tuple is silently dropped from the README's owner cell and the file
    # disappears from `list --owner`. MEASURED 2026-08-23: nine TODOs owned
    # `agents · Roy` or `backend · Roy` rendered as `Roy` alone, and
    # `list --owner agents` returned 21 of 26.
    #
    # !! THE LANES THIS TOOL ARRIVED WITH ARE DELETED, not kept alongside. They
    # named the lanes of a PRIVATE repo, and this one is going public: a
    # vendored file is a way for one repo's internals to leave in another's
    # history. A re-grab must drop them again.
    "agents",
    "backend",
    "testing",
    "systems",
    "Roy",
    "unassigned",
    "mixed",
)
# `,`, `/` and "with" are here because five real fields used them for a genuine
# co-owner and lost that lane from the queue. Adding them changes NOTHING about
# the 193 fields today (measured) — those five were rewritten to `·` — so this
# only stops the next one being written that way from going silently missing.
#
# `;` is deliberately NOT here: all four fields that contain one use it as prose
# punctuation, never as a list separator, and splitting on it lifts a lane out
# of a sentence that merely mentions it ("...; the shared vocabulary and the
# census and the addresser are testing + agents" under an `unassigned` owner).
_OWNER_SPLIT = re.compile(r"\s*[·+→,/]\s*|\s+with\s+")
_PARENTHETICAL = re.compile(r"\([^)]*\)")
# Answers "nobody" and "read the tasks" — neither composes with a lane list.
_EXCLUSIVE_OWNERS = ("unassigned", "mixed")
# A line that STARTS like a data row, whether or not `_ROW` can parse the rest.
_DATA_ROW_START = re.compile(r"^\|\s*\[[^\]]+\]\([^)]+\.md\)")


def _owner_cell(owner: str) -> str:
    """The README owner cell for an `Owner:` field — its LANES, nothing else.

    The field carries role annotations ("backend (the lexer/the page)") and
    the table carries the lanes alone, so `list --owner` can match every lane the
    field names without the table growing to 160 characters.

    Reads the LEADING name of each `·`-separated segment rather than every lane
    word it can find: a segment's own prose routinely names other lanes as
    history ("the record half was driven by systems at Roy's direction"),
    and those are not owners. Parentheticals come off first because they contain
    separators of their own ("(the fetcher + the analysis)").

    Falls back to the field unchanged when no leading lane is found, so a field
    written in a shape this does not model degrades to today's behaviour instead
    of silently emptying the cell.
    """
    stripped = _PARENTHETICAL.sub("", owner).strip()
    for exclusive in _EXCLUSIVE_OWNERS:
        if stripped.lower().startswith(exclusive):
            return exclusive
    seen: list[str] = []
    for segment in _OWNER_SPLIT.split(stripped):
        head = segment.strip()
        for lane in LANES:
            if head.lower().startswith(lane.lower()) and lane not in seen:
                seen.append(lane)
                break
    return " · ".join(seen) if seen else owner.strip()


_COUNTS_CELL = re.compile(r"^\d+\s*/\s*\d+$")
_LINK_TEXT = re.compile(r"^\|\s*\[([^\]]+)\]")


def _salvage_row(line: str) -> tuple[str | None, str | None]:
    """(link text, `what`) recovered from a row `_ROW` cannot parse.

    Neither is derivable from the file. The `what` column is NOT the title —
    `create --summary` writes an independent summary and rows carry long
    hand-curated ones — and one row's LINK TEXT deliberately differs from its
    slug. Regenerating either turns a repair into data loss.

    `what` is everything after the `N/M` cell, found by SHAPE rather than by
    position: taking the last cell blindly promotes `3/5` into the summary on a
    row that has no `what` at all, and keeps only the final fragment when a
    `what` itself contains a `|`. Both come back None when the row cannot
    supply them, and a `what` that spans a `|` is returned whole so the caller
    can refuse the rebuild rather than truncate it.
    """
    m = _LINK_TEXT.match(line)
    link_text = m.group(1) if m else None
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    for i, cell in enumerate(cells):
        if _COUNTS_CELL.match(cell):
            rest = [c for c in cells[i + 1 :] if c]
            return link_text, " | ".join(rest) if rest else None
    return link_text, None


def _require_no_pipe(value: str, field: str) -> str:
    """Refuse a cell value containing the column separator.

    A `|` splits the row into more cells than the table has, so `_ROW` stops
    matching it: the TODO then vanishes from `list` (including
    `--requires-roy`) and `resync` aborts the whole run rather than repairing
    it. Guards the two places a cell is composed, so no command can route
    around it.
    """
    if "|" in value:
        raise ValueError(
            f"{field} may not contain '|' — it is the README column separator"
        )
    return value


def _roy_cell(requires_roy: bool) -> str:
    """The README `roy?` cell for a flag value."""
    return ROY_YES if requires_roy else ROY_NO


def _roy_from_cell(cell: str) -> bool:
    """Read a README `roy?` cell back to its flag value."""
    return cell.strip().lower() == ROY_YES


def _parse_roy_field(value: str) -> bool:
    """`true`/`false` as written in a TODO header, case-insensitively."""
    v = value.strip().lower()
    if v not in ("true", "false"):
        raise ValueError(
            f"{REQUIRES_ROY_FIELD} must be 'true' or 'false', got {value!r}"
        )
    return v == "true"


def _unfenced_line_indices(lines: list[str]) -> list[int]:
    """Indices of lines NOT inside a fenced (```/~~~) block — the one
    definition of fence-membership every fence-aware scan builds on."""
    idxs, inside = [], False
    for i, line in enumerate(lines):
        if line.lstrip().startswith(("```", "~~~")):
            inside = not inside
            continue
        if not inside:
            idxs.append(i)
    return idxs


def _outside_fences(text: str) -> str:
    """The document with fenced blocks removed — same rule as the header
    block being a fence and CLAUDE.md's template examples being fences."""
    lines = text.splitlines()
    return "\n".join(lines[i] for i in _unfenced_line_indices(lines))


def _boxes(text: str) -> tuple[int, int]:
    hits = _BOX.findall(_outside_fences(text))
    return sum(1 for h in hits if h in "xX"), len(hits)


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def _slug_for(title: str, slug: str | None) -> str:
    """The filename stem: an explicit `slug` when given, else the title.

    A title long enough to say what the problem IS makes a filename long enough
    to be painful to type and to read in a README link, so the two are allowed
    to differ — the title stays descriptive, the stem gets abbreviated. An
    explicit stem is still slugified (and a typed `.md` dropped) so no caller
    can put a space, a capital, or a double extension into a filename.
    """
    if slug is None:
        return slugify(title)
    cleaned = slugify(slug.removesuffix(".md"))
    if not cleaned:
        raise ValueError(f"slug {slug!r} has no filename-safe characters")
    return cleaned


def _split_header(text: str) -> tuple[list[str], list[str], list[str]]:
    """Split around the first fenced block (the Status/Progress/Owner/
    Raised header). `header` excludes the fence lines; `before` ends with
    the opening fence, `after` starts with the closing fence."""
    lines = text.splitlines()
    fence_idxs = [i for i, ln in enumerate(lines) if ln.lstrip().startswith("```")]
    if len(fence_idxs) < 2:
        raise ValueError("no fenced header block found")
    start, end = fence_idxs[0], fence_idxs[1]
    return lines[: start + 1], lines[start + 1 : end], lines[end:]


def _field_bounds(header: list[str], label: str) -> tuple[int, int]:
    """(start, end) line indices of `label`'s field, including any wrapped
    continuation lines — everything up to the next line that itself looks
    like the start of a new `Label:` field, or the end of the header."""
    prefix = f"{label}:"
    start = next((i for i, ln in enumerate(header) if ln.startswith(prefix)), None)
    if start is None:
        raise ValueError(f"no {label!r} field in header")
    end = start + 1
    while end < len(header) and not _FIELD_START.match(header[end]):
        end += 1
    return start, end


def _get_field(header: list[str], label: str) -> str:
    start, end = _field_bounds(header, label)
    first = header[start][len(f"{label}:") :].strip()
    rest = [ln.strip() for ln in header[start + 1 : end]]
    return " ".join([first, *rest]).strip()


def _render_field(label: str, value: str, width: int = 88) -> list[str]:
    prefix = f"{label}:"
    # 10 aligns the value column for every label up to 9 characters, which is
    # all of them except `Requires-Roy:` (13) — its value sits at 14 and reads
    # one step right of the rest. 20 keeps wrapped text usably wide even when a
    # long label eats more of `width`.
    indent_width = max(10, len(prefix) + 1)
    pad = " " * (indent_width - len(prefix))
    wrapped = textwrap.wrap(
        value, width=max(width - indent_width, 20), break_long_words=False
    ) or [""]
    lines = [f"{prefix}{pad}{wrapped[0]}"]
    lines += [" " * indent_width + w for w in wrapped[1:]]
    return lines


def _set_field(header: list[str], label: str, value: str) -> list[str]:
    start, end = _field_bounds(header, label)
    return header[:start] + _render_field(label, value) + header[end:]


def _append_field(header: list[str], label: str, value: str) -> list[str]:
    return header + _render_field(label, value)


def _get_requires_roy(header: list[str]) -> bool:
    """The Requires-Roy flag, False when the field is absent.

    Absent is the shape of a TODO written before the field existed, and of a
    `completed/` file closed before `complete_todo` began clearing the flag. A
    field that is PRESENT but not true/false still raises — that is drift, not
    an old file.
    """
    try:
        raw = _get_field(header, REQUIRES_ROY_FIELD)
    except ValueError:
        return False
    return _parse_roy_field(raw)


def _set_requires_roy_field(header: list[str], requires_roy: bool) -> list[str]:
    """Set Requires-Roy, inserting it under `Owner:` when it is not there yet."""
    value = "true" if requires_roy else "false"
    try:
        _field_bounds(header, REQUIRES_ROY_FIELD)
    except ValueError:
        _, owner_end = _field_bounds(header, "Owner")
        rendered = _render_field(REQUIRES_ROY_FIELD, value)
        return header[:owner_end] + rendered + header[owner_end:]
    return _set_field(header, REQUIRES_ROY_FIELD, value)


def _render_progress(done: int, total: int) -> str:
    return f"Progress: {done} of {total} tasks done"


def _set_progress(header: list[str], done: int, total: int) -> list[str]:
    return _set_field(header, "Progress", f"{done} of {total} tasks done")


def _task_lines(text: str) -> list[int]:
    lines = text.splitlines()
    return [i for i in _unfenced_line_indices(lines) if _BOX.match(lines[i])]


def _rewrite_progress(text: str) -> str:
    before, header, after = _split_header(text)
    done, total = _boxes(text)
    header = _set_progress(header, done, total)
    return "\n".join(before + header + after)


def _toggle_task(text: str, index: int, checked: bool) -> str:
    lines = text.splitlines()
    idxs = _task_lines(text)
    if not (1 <= index <= len(idxs)):
        raise ValueError(f"task index {index} out of range (1-{len(idxs)})")
    line_no = idxs[index - 1]
    mark = "x" if checked else " "
    line = lines[line_no]
    mark_match = _BOX.match(line)
    assert mark_match is not None, (
        "idxs came from _task_lines, which only returns _BOX matches"
    )
    lines[line_no] = line[: mark_match.start(1)] + mark + line[mark_match.end(1) :]
    return _rewrite_progress("\n".join(lines))


def _render_task_line(text: str) -> list[str]:
    return textwrap.wrap(
        text, width=82, initial_indent="- [ ] ", subsequent_indent="      "
    )


def _section_bounds(
    lines: list[str], heading: str, filename: str = ""
) -> tuple[int, int]:
    """(heading_idx, section_end) for a top-level "## <heading>" section —
    section_end is the index of the next "## " heading, or len(lines)."""
    start = next((i for i, ln in enumerate(lines) if ln.strip() == heading), None)
    if start is None:
        where = f"{filename}: " if filename else ""
        raise ValueError(f"{where}no {heading!r} heading found")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    return start, end


def _insert_task_line(text: str, task_text: str, filename: str = "") -> str:
    lines = text.splitlines()
    tasks_start, section_end = _section_bounds(lines, "## Tasks", filename)
    box_idxs = [i for i in _task_lines(text) if tasks_start <= i < section_end]
    insert_at = (box_idxs[-1] + 1) if box_idxs else tasks_start + 1
    # The last task's wrapped continuation lines are indented but aren't box
    # lines themselves -- skip past them so the new task lands after the
    # whole last task, not spliced into the middle of it.
    while (
        insert_at < section_end
        and lines[insert_at].startswith(" ")
        and not _BOX.match(lines[insert_at])
    ):
        insert_at += 1
    new_lines = lines[:insert_at] + _render_task_line(task_text) + lines[insert_at:]
    return _rewrite_progress("\n".join(new_lines))


# The `what` column is `[^|\n]*` -- it cannot contain a literal `|`
# (e.g. backtick-quoted code with a pipe in it), which would get misread as
# a column boundary and truncate the capture. Pre-existing limitation of
# the pipe-delimited table format, not new to this regex.
_ROW_FULL = re.compile(_ROW_PREFIX + r"(?P<what>[^|\n]*)\|?", re.MULTILINE)

_COMPLETED_ROW = re.compile(
    r"^\|\s*\[([^\]]+)\]\(completed/([^)]+\.md)\)\s*\|", re.MULTILINE
)

_SECTION_RE = re.compile(r"^### (.+?)\s+\((\d+)\)\s*$")

CANONICAL_SECTIONS = ["decision-needed", "in flight", "blocked", "in-progress", "open"]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _progress_disagreement(text: str) -> tuple[str, str] | None:
    """If `text` has its own `Progress:` line disagreeing with its own
    boxes, return (header, actual) as 'D/T' strings. Returns None if
    there's no Progress: line (pre-template files) or it already agrees."""
    m = _PROGRESS.search(text)
    if m is None:
        return None
    done, total = _boxes(text)
    header, actual = f"{m.group(1)}/{m.group(2)}", f"{done}/{total}"
    if header == actual:
        return None
    return header, actual


class _WriteCheckFailure(ValueError):
    """Raised by _write when a write's own crash-safety check fails
    (round-trip mismatch, or a Progress: line disagreeing with its own
    boxes) -- a ValueError subclass so every existing `except ValueError`
    still catches it, but a caller that needs to tell "this file's write
    failed" apart from "this file's header couldn't be parsed" can catch
    it specifically."""


def _write(path: Path, text: str) -> None:
    """Write `text` to `path` crash-safely against a process-level crash or
    a disk/handle fault -- not against power loss, which would need an
    fsync before the replace that this does not do: normalizes `text` to
    end with exactly one newline, writes a same-directory temp file,
    verifies the write round-tripped byte-for-byte (catches a disk or
    handle fault), and -- if `text` has its own `Progress:` line -- that
    it agrees with `text`'s own boxes (catches a logic bug, the same
    consistency test_todo_counts_agree.py already asserts). Only then
    atomically replaces `path`. A README write has no `Progress:` line, so
    that half of the check is a no-op for it; README N/M correctness
    already depends on the caller re-reading each file fresh before
    assembling the README text.

    Same directory, not the OS temp dir, because os.replace() is only
    atomic within one filesystem -- TODO/ could be on a different volume
    than the system temp directory.
    """
    if not text.endswith("\n"):
        text += "\n"
    tmp = path.parent / f".{path.name}.tmp{os.getpid()}"
    data = text.encode("utf-8")
    try:
        tmp.write_bytes(data)
        if tmp.read_bytes() != data:
            raise _WriteCheckFailure(
                f"{path}: write did not round-trip (disk or handle fault)"
            )
        disagreement = _progress_disagreement(text)
        if disagreement is not None:
            header, actual = disagreement
            raise _WriteCheckFailure(
                f"{path}: Progress: {header} disagrees with {actual} actual boxes "
                "-- run 'resync' to fix it"
            )
    except Exception:
        # Covers the two explicit ValueErrors above AND an OSError from
        # write_bytes/read_bytes itself (e.g. a full disk) -- either way,
        # the temp file must not be left behind. `raise` (not `raise exc`)
        # preserves the original traceback.
        tmp.unlink(missing_ok=True)
        raise
    os.replace(tmp, path)


def _read_readme(todo_dir: Path) -> str:
    return _read(todo_dir / "README.md")


def _write_readme(todo_dir: Path, text: str) -> None:
    _write(todo_dir / "README.md", text)


def _section_for_status(status: str) -> str:
    s = status.strip().lower()
    if s.startswith("decision-needed"):
        return "decision-needed"
    if s.startswith(("in-flight", "in flight")):
        return "in flight"
    if s.startswith("blocked"):
        return "blocked"
    if s.startswith(("in-progress", "in progress")):
        return "in-progress"
    return "open"


def _table_rows_end(lines: list[str], rows_start: int) -> int:
    """First index at or after `rows_start` that is no longer a table row."""
    rows_end = rows_start
    while rows_end < len(lines) and lines[rows_end].startswith("|"):
        rows_end += 1
    return rows_end


def _section_rows_at(lines: list[str], header_idx: int) -> tuple[int, int]:
    """Given the line index of a '### name  (N)' heading, return
    (rows_start, rows_end) for its row table."""
    j = header_idx + 1
    while j < len(lines) and lines[j].strip() == "":
        j += 1
    j += 2  # skip the "| file | ... |" header row and its "| --- |" separator
    rows_start = j
    return rows_start, _table_rows_end(lines, rows_start)


def _find_section(lines: list[str], name: str) -> tuple[int, int, int, int] | None:
    for i, ln in enumerate(lines):
        m = _SECTION_RE.match(ln)
        if m and m.group(1).strip() == name:
            count = int(m.group(2))
            rows_start, rows_end = _section_rows_at(lines, i)
            return i, count, rows_start, rows_end
    return None


def _count_sections_named(lines: list[str], name: str) -> int:
    return sum(
        1 for ln in lines if (m := _SECTION_RE.match(ln)) and m.group(1).strip() == name
    )


def _set_section_count(lines: list[str], header_idx: int, count: int) -> None:
    m = re.match(r"^(### .+?\s+\()\d+(\)\s*)$", lines[header_idx])
    assert m is not None
    lines[header_idx] = f"{m.group(1)}{count}{m.group(2)}"


def _resync_section_counts(lines: list[str]) -> list[str]:
    """Rewrite every '### name  (N)' heading to match its actual row count.
    Mutates `lines` in place; returns one description per heading changed.

    Recomputes each heading from ITS OWN index, not by re-searching for a
    heading with the same name -- re-searching would silently skip a
    second heading sharing a name with an earlier one (a plausible merge
    artifact: two branches each independently add e.g. '### blocked')."""
    changes: list[str] = []
    for i, ln in enumerate(lines):
        m = _SECTION_RE.match(ln)
        if m is None:
            continue
        name = m.group(1)
        declared = int(m.group(2))
        rows_start, rows_end = _section_rows_at(lines, i)
        actual = rows_end - rows_start
        if actual != declared:
            _set_section_count(lines, i, actual)
            changes.append(f"### {name}: ({declared}) -> ({actual})")
    return changes


def _find_row_line(lines: list[str], filename: str) -> int | None:
    marker = f"]({filename})"
    for i, ln in enumerate(lines):
        if ln.startswith("|") and marker in ln:
            return i
    return None


def _section_containing(lines: list[str], row_idx: int) -> tuple[str, int, int]:
    for i in range(row_idx, -1, -1):
        # A top-level '## ' heading (Open/Completed) reached before any
        # '### ' subsection means the row sits directly under '## Open'
        # with no subsection of its own -- the shape a botched README
        # merge conflict resolution can leave behind.
        if lines[i].startswith("## ") and not lines[i].startswith("### "):
            break
        m = _SECTION_RE.match(lines[i])
        if m:
            return m.group(1), int(m.group(2)), i
    raise ValueError("row is not inside a ### section")


def _row_line(
    slug: str,
    owner: str,
    requires_roy: bool,
    done: int,
    total: int,
    what: str,
    link_text: str | None = None,
) -> str:
    """One README row. `link_text` defaults to the slug.

    Args:
        link_text: The link's display text, when a rebuild must preserve one
            that deliberately differs from the slug.
    """
    _require_no_pipe(owner, "owner")
    _require_no_pipe(what, "the README row's 'what' text")
    return (
        f"| [{link_text or slug}]({slug}.md) | {owner} | {_roy_cell(requires_roy)} "
        f"| {done}/{total} | {what} |"
    )


def _insert_section(lines: list[str], name: str) -> list[str]:
    idx_in_order = CANONICAL_SECTIONS.index(name)
    skeleton = [
        "",
        f"### {name}  (0)",
        "",
        TABLE_HEADER,
        TABLE_SEPARATOR,
    ]
    # Anchor against whichever neighbor already exists: prefer inserting
    # right before the nearest LATER section in canonical order, falling
    # back to right after the nearest EARLIER one, so the new section
    # lands in the correct canonical position regardless of which
    # neighbors happen to exist yet.
    for later_name in CANONICAL_SECTIONS[idx_in_order + 1 :]:
        found = _find_section(lines, later_name)
        if found is None:
            continue
        insert_at = found[0]
        while insert_at > 0 and lines[insert_at - 1].strip() == "":
            insert_at -= 1
        return lines[:insert_at] + skeleton + lines[insert_at:]
    for earlier_name in reversed(CANONICAL_SECTIONS[:idx_in_order]):
        found = _find_section(lines, earlier_name)
        if found is None:
            continue
        insert_at = found[3]
        return lines[:insert_at] + skeleton + lines[insert_at:]
    raise ValueError("no existing Open subsection to anchor a new section against")


def _insert_row_into_section(lines: list[str], name: str, row: str) -> list[str]:
    found = _find_section(lines, name)
    if found is None:
        lines = _insert_section(lines, name)
        found = _find_section(lines, name)
    assert found is not None
    if _count_sections_named(lines, name) > 1:
        raise ValueError(
            f"two '### {name}' sections exist -- a row cannot be inserted "
            f"unambiguously until the duplicate heading (likely a merge "
            f"artifact) is resolved by hand"
        )
    header_idx, count, _, rows_end = found
    new_lines = lines[:rows_end] + [row] + lines[rows_end:]
    _set_section_count(new_lines, header_idx, count + 1)
    return new_lines


def _remove_row_from_section(lines: list[str], filename: str) -> tuple[list[str], str]:
    idx = _find_row_line(lines, filename)
    if idx is None:
        raise ValueError(f"{filename} has no row in README.md")
    name, count, header_idx = _section_containing(lines, idx)
    new_lines = lines[:idx] + lines[idx + 1 :]
    _set_section_count(new_lines, header_idx, count - 1)
    return new_lines, name


def _completed_row_line(dest_stem: str, dest_name: str, outcome: str) -> str:
    return f"| [{dest_stem}](completed/{dest_name}) | {outcome} |"


def _insert_completed_row(lines: list[str], row: str) -> list[str]:
    heading_idx = next(
        (i for i, ln in enumerate(lines) if ln.strip() == "## Completed"), None
    )
    if heading_idx is None:
        raise ValueError("TODO/README.md has no '## Completed' heading")
    i = heading_idx + 1
    while i < len(lines) and not lines[i].startswith("| file"):
        i += 1
    if i >= len(lines):
        raise ValueError("no Completed table found under ## Completed")
    rows_start = i + 2
    rows_end = _table_rows_end(lines, rows_start)
    return lines[:rows_end] + [row] + lines[rows_end:]


def _resync_file_progress(path: Path) -> tuple[str, str] | None:
    """Fixes `path`'s Progress: header if `_progress_disagreement` finds a
    disagreement, and returns what it returned. Returns None if it did."""
    text = _read(path)
    disagreement = _progress_disagreement(text)
    if disagreement is None:
        return None
    _write(path, _rewrite_progress(text))
    return disagreement


def _resync_progress_pass(
    paths: list[Path], prefix: str, changes: list[str], unreadable: list[str]
) -> set[str]:
    """Run _resync_file_progress over `paths`, collecting each file's
    header fix into `changes` and each failure into `unreadable` -- one
    file's failure never stops the rest from being fixed. `prefix` is ""
    for open files, "completed/" for completed/. Returns the subset of
    `paths`' names whose failure was a genuine header-parse problem (not
    a write-check failure) -- the only kind a caller's own separate
    header-parsing pass would redundantly re-fail on; a write-check
    failure means the file's structure was fine, so a caller doing
    unrelated work with that file should still proceed."""
    header_unreadable: set[str] = set()
    for path in paths:
        try:
            result = _resync_file_progress(path)
        except _WriteCheckFailure as exc:
            unreadable.append(f"{prefix}{path.name}: {exc}")
            continue
        except ValueError as exc:
            unreadable.append(f"{prefix}{path.name}: {exc}")
            header_unreadable.add(path.name)
            continue
        if result:
            changes.append(f"{prefix}{path.name}: header {result[0]} -> {result[1]}")
    return header_unreadable


def readme_add_row(
    todo_dir: Path,
    slug: str,
    owner: str,
    requires_roy: bool,
    done: int,
    total: int,
    what: str,
    status: str,
) -> None:
    lines = _read_readme(todo_dir).splitlines()
    row = _row_line(slug, owner, requires_roy, done, total, what)
    lines = _insert_row_into_section(lines, _section_for_status(status), row)
    _write_readme(todo_dir, "\n".join(lines))


def _rewrite_row_counts(line: str, m: re.Match[str], done: int, total: int) -> str:
    """Splice new `done`/`total` values into a README row already matched by
    `_ROW`, replacing its N/M cell in place. Shared by every write path that
    rewrites a row's counts without moving or removing it."""
    return (
        line[: m.start("done")]
        + str(done)
        + line[m.end("done") : m.start("total")]
        + str(total)
        + line[m.end("total") :]
    )


def _rewrite_row_cell(line: str, m: re.Match[str], group: str, value: str) -> str:
    """Splice `value` into one named cell of a README row already matched by
    `_ROW`, leaving every other cell byte-identical."""
    _require_no_pipe(value, group)
    return line[: m.start(group)] + f" {value} " + line[m.end(group) :]


def _require_row_match(line: str, name: str) -> re.Match[str]:
    m = _ROW.match(line)
    if m is None:
        raise ValueError(f"{name}: README row does not match the expected format")
    return m


def readme_update_counts(todo_dir: Path, slug: str, done: int, total: int) -> None:
    lines = _read_readme(todo_dir).splitlines()
    filename = f"{slug}.md"
    idx = _find_row_line(lines, filename)
    if idx is None:
        raise ValueError(f"{filename} has no row in README.md")
    line = lines[idx]
    m = _require_row_match(line, filename)
    lines[idx] = _rewrite_row_counts(line, m, done, total)
    _write_readme(todo_dir, "\n".join(lines))


def _readme_update_cell(todo_dir: Path, slug: str, group: str, value: str) -> None:
    lines = _read_readme(todo_dir).splitlines()
    filename = f"{slug}.md"
    idx = _find_row_line(lines, filename)
    if idx is None:
        raise ValueError(f"{filename} has no row in README.md")
    m = _require_row_match(lines[idx], filename)
    lines[idx] = _rewrite_row_cell(lines[idx], m, group, value)
    _write_readme(todo_dir, "\n".join(lines))


def readme_update_owner(todo_dir: Path, slug: str, owner: str) -> None:
    _readme_update_cell(todo_dir, slug, "owner", owner)


def set_requires_roy(todo_dir: Path, filename: str, requires_roy: bool) -> None:
    _require_readme_row(todo_dir, filename)
    _update_header(
        todo_dir, filename, lambda h: _set_requires_roy_field(h, requires_roy)
    )
    readme_update_requires_roy(todo_dir, Path(filename).stem, requires_roy)


def readme_update_requires_roy(todo_dir: Path, slug: str, requires_roy: bool) -> None:
    _readme_update_cell(todo_dir, slug, "roy", _roy_cell(requires_roy))


def readme_move_section(todo_dir: Path, slug: str, new_status: str) -> None:
    lines = _read_readme(todo_dir).splitlines()
    filename = f"{slug}.md"
    idx = _find_row_line(lines, filename)
    if idx is None:
        raise ValueError(f"{filename} has no row in README.md")
    old_section, _, _ = _section_containing(lines, idx)
    new_section = _section_for_status(new_status)
    if new_section == old_section:
        return
    row = lines[idx]
    lines, _ = _remove_row_from_section(lines, filename)
    lines = _insert_row_into_section(lines, new_section, row)
    _write_readme(todo_dir, "\n".join(lines))


def create_todo(
    todo_dir: Path,
    title: str,
    owner: str,
    raised_from: str,
    status: str = "open",
    summary: str | None = None,
    tasks: tuple[str, ...] = (),
    today: date | None = None,
    slug: str | None = None,
    requires_roy: bool = False,
) -> Path:
    if not tasks:
        raise ValueError("create needs at least one task")
    # Up front, with the other precondition: `_row_line` would catch these too,
    # but only AFTER `_write` has already put the file on disk — leaving the
    # half-created TODO this function's FileExistsError check exists to avoid.
    _require_no_pipe(owner, "owner")
    _require_no_pipe(summary or title, "the README row's 'what' text")
    slug = _slug_for(title, slug)
    path = todo_dir / f"{slug}.md"
    if path.exists():
        raise FileExistsError(str(path))
    today = today or date.today()
    task_lines: list[str] = []
    for t in tasks:
        task_lines += _render_task_line(t)
    tasks_block = "## Tasks\n\n" + "\n".join(task_lines) + "\n"
    header: list[str] = []
    header += _render_field("Status", status)
    header += [
        _render_progress(0, 0)
    ]  # placeholder -- _rewrite_progress fixes it below
    header += _render_field("Owner", owner)
    header += _render_field(REQUIRES_ROY_FIELD, "true" if requires_roy else "false")
    header += _render_field("Raised", f"{today.isoformat()} ({raised_from})")
    text = (
        f"# {title}\n\n"
        "```\n" + "\n".join(header) + "\n```\n\n"
        "## Objective\n\n" + title + ".\n\n" + tasks_block
    )
    done, total = _boxes(text)
    text = _rewrite_progress(text)
    _write(path, text)
    readme_add_row(
        todo_dir,
        slug,
        _owner_cell(owner),
        requires_roy,
        done,
        total,
        summary or title,
        status,
    )
    return path


def _require_readme_row(todo_dir: Path, filename: str) -> None:
    """Raise before anything is written if `filename` has no README row —
    the check `readme_update_counts`/`readme_move_section` would otherwise
    perform only after the file mutation already landed on disk."""
    normalized = f"{Path(filename).stem}.md"
    lines = _read_readme(todo_dir).splitlines()
    idx = _find_row_line(lines, normalized)
    if idx is None:
        raise ValueError(f"{normalized} has no row in README.md")
    # Existence is not enough: the cell writers go on to call
    # `_require_row_match`, which raises on a row `_ROW` cannot parse — by which
    # point the FILE has been written and the README has not, which is the
    # half-updated state this precheck exists to make impossible.
    _require_row_match(lines[idx], normalized)


def _apply_and_sync(
    todo_dir: Path, filename: str, transform: Callable[[str], str]
) -> None:
    path = todo_dir / filename
    _require_readme_row(todo_dir, filename)
    new_text = transform(_read(path))
    _write(path, new_text)
    done, total = _boxes(new_text)
    readme_update_counts(todo_dir, Path(filename).stem, done, total)


def check_task(todo_dir: Path, filename: str, index: int, checked: bool = True) -> None:
    _apply_and_sync(todo_dir, filename, lambda text: _toggle_task(text, index, checked))


def add_task(todo_dir: Path, filename: str, task_text: str) -> None:
    _apply_and_sync(
        todo_dir, filename, lambda text: _insert_task_line(text, task_text, filename)
    )


def _update_header(
    todo_dir: Path, filename: str, transform: Callable[[list[str]], list[str]]
) -> None:
    """Apply `transform` to `filename`'s header fields and write it back.
    Every `_update_header`-based command (set_owner, set_status, add_note)
    edits only the fields `transform` touches -- it never recomputes
    Progress: from the boxes, so if the file's Progress: line already
    disagrees with its own boxes (drift a merge left behind), `_write`'s
    crash-safety check correctly refuses the write; run `resync` first."""
    path = todo_dir / filename
    before, header, after = _split_header(_read(path))
    header = transform(header)
    _write(path, "\n".join(before + header + after))


def _update_header_field(todo_dir: Path, filename: str, label: str, value: str) -> None:
    _update_header(todo_dir, filename, lambda header: _set_field(header, label, value))


def set_owner(todo_dir: Path, filename: str, owner: str) -> None:
    # BOTH sides, one command, same shape as `set_status`. `list --owner`
    # matches the README cell, so a file whose Owner: field alone was changed
    # stays invisible to the query a session runs to find its work.
    _require_no_pipe(owner, "owner")
    _require_readme_row(todo_dir, filename)
    _update_header_field(todo_dir, filename, "Owner", owner)
    readme_update_owner(todo_dir, Path(filename).stem, _owner_cell(owner))


def set_status(
    todo_dir: Path, filename: str, status: str, note: str | None = None
) -> None:
    _require_readme_row(todo_dir, filename)
    _update_header_field(todo_dir, filename, "Status", status)
    readme_move_section(todo_dir, Path(filename).stem, status)
    if note:
        add_note(todo_dir, filename, note)


def complete_todo(
    todo_dir: Path, filename: str, outcome: str, superseded: bool = False
) -> Path:
    src = todo_dir / filename
    if not src.exists():
        raise FileNotFoundError(str(src))
    dest_stem, suffix = Path(filename).stem, Path(filename).suffix
    dest_name = filename
    if superseded:
        dest_stem = f"{dest_stem}-SUPERSEDED"
        dest_name = f"{dest_stem}{suffix}"
    dest_dir = todo_dir / "completed"
    dest_dir.mkdir(exist_ok=True)
    dest = dest_dir / dest_name
    if dest.exists():
        raise FileExistsError(str(dest))
    lines = _read_readme(todo_dir).splitlines()
    lines, _ = _remove_row_from_section(lines, filename)
    lines = _insert_completed_row(
        lines, _completed_row_line(dest_stem, dest_name, outcome)
    )
    # A closed TODO owes no decision, so a flag that is SET comes off on the way
    # out. Left set, it survives into `completed/` and `reopen_todo` reads it
    # back — restoring a demand on Roy he may have already answered.
    #
    # ⚠ Clears only; never INSERTS. A file with no flag needs none once closed,
    # and writing one would drag every legacy file through `_write` — which
    # refuses a file whose `Progress:` already disagrees with its boxes, so
    # `complete` would start failing on exactly the old files it has always
    # closed fine. Same reason the missing-`Owner:` shape stays untouched
    # instead of being repaired here.
    text = _read(src)
    cleared: str | None = None
    try:
        before, header, after = _split_header(text)
    except ValueError:
        pass  # predates the header template; there is no flag to clear
    else:
        # `_get_requires_roy` sits OUTSIDE that except on purpose: it documents
        # a PRESENT-but-not-true/false value as drift that must RAISE, and a
        # blanket catch here swallowed exactly that — renaming the file into
        # `completed/` with the bad value intact, where nothing reads it again.
        if _get_requires_roy(header):
            cleared = "\n".join(before + _set_requires_roy_field(header, False) + after)
    if cleared is not None:
        # OUTSIDE the except above: `_WriteCheckFailure` subclasses ValueError,
        # so a file whose `Progress:` already disagrees with its boxes would
        # have had its clearing write swallowed and then been renamed into
        # `completed/` still demanding a decision — the opposite of what the
        # comment above promises. It must surface.
        _write(src, cleared)
    src.rename(dest)
    _write_readme(todo_dir, "\n".join(lines))
    return dest


def _find_completed_row_line(lines: list[str], filename: str) -> int | None:
    marker = f"](completed/{filename})"
    for i, ln in enumerate(lines):
        if ln.startswith("|") and marker in ln:
            return i
    return None


def _remove_completed_row(lines: list[str], filename: str) -> list[str]:
    idx = _find_completed_row_line(lines, filename)
    if idx is None:
        raise ValueError(f"{filename} has no row in the Completed table")
    return lines[:idx] + lines[idx + 1 :]


def _title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError("no top-level '# Title' heading found")


def reopen_todo(
    todo_dir: Path, filename: str, status: str = "open", note: str | None = None
) -> Path:
    """Undo a wrongful `complete` — move `filename` back out of `completed/`,
    give it an Open-table row again (Owner and boxes read from the file
    itself; What is the file's own title), and set its Status.

    The inverse of `complete_todo`, needed because every mutation command
    requires an existing README row and a file moved to `completed/` no
    longer has one — recovering used to mean hand-editing README.md's row
    and section-count arithmetic directly (TODO/completed/
    todo-tool-reopen-and-completed-consistency.md).
    """
    src = todo_dir / "completed" / filename
    if not src.exists():
        raise FileNotFoundError(str(src))
    dest = todo_dir / filename
    if dest.exists():
        raise FileExistsError(str(dest))
    lines = _read_readme(todo_dir).splitlines()
    lines = _remove_completed_row(lines, filename)

    text = _read(src)
    before, header, after = _split_header(text)
    header = _set_field(header, "Status", status)
    # `complete_todo` clears the flag on the way in, and a file closed before it
    # did that carries none at all. Either way reopening makes this open work
    # again, so the field is written explicitly rather than left absent for the
    # counts checker to trip over. It reopens as FALSE by design — whether Roy
    # still owes a decision is a fresh judgment, not the one that was true when
    # the file was closed.
    requires_roy = False
    header = _set_requires_roy_field(header, requires_roy)
    new_text = "\n".join(before + header + after)
    owner = _get_field(header, "Owner")
    done, total = _boxes(new_text)
    what = _title(new_text)
    row = _row_line(
        Path(filename).stem, _owner_cell(owner), requires_roy, done, total, what
    )
    lines = _insert_row_into_section(lines, _section_for_status(status), row)

    _write(src, new_text)
    src.rename(dest)
    _write_readme(todo_dir, "\n".join(lines))
    if note:
        add_note(todo_dir, filename, note)
    return dest


def _stale_row_scan(
    pattern: re.Pattern[str], text: str, file_names: set[str], no_such_file_label: str
) -> tuple[list[str], set[str]]:
    """Rows matched by `pattern` in `text` whose captured filename (group 2)
    isn't in `file_names` -- in the document order rows appear. Also
    returns every matched filename, so a caller needing the full name set
    for a reverse (file-has-no-row) scan doesn't have to re-run the same
    regex over the same text a second time."""
    stale = []
    row_names: set[str] = set()
    for m in pattern.finditer(text):
        row_names.add(m.group(2))
        if m.group(2) not in file_names:
            stale.append(f"{m.group(2)}: {no_such_file_label}")
    return stale, row_names


def _stale_file_scan(
    paths: list[Path], row_names: set[str], no_such_row_label: str
) -> list[str]:
    """Paths (already sorted by the caller) whose filename isn't in `row_names`."""
    return [f"{p.name}: {no_such_row_label}" for p in paths if p.name not in row_names]


def resync(todo_dir: Path) -> list[str]:
    """Recompute every derived number and section placement in
    TODO/README.md, and every file's own Progress: header, from what's
    actually on disk. Fixes drift a merge can introduce even when each
    branch's own commit was internally consistent -- the union of two
    correct edits is not guaranteed correct.

    Writes every fix it can make unambiguously. Four kinds of problem are
    left untouched and collected instead of fixed -- all raised together
    as a single ValueError AFTER every other fix in this call has already
    been written to disk: a README row (Open or Completed) pointing at a
    file that does not exist where the table says; a completed/ file with
    no matching row in the README's Completed table (the mirror case --
    invisible, not wrong, until this scan checks); a file (open or
    completed) whose own header resync cannot read (no fenced header
    block -- a plausible state for a file that came out of a botched
    merge conflict resolution), or, for an open file, one missing its
    `Status:` field, or -- when adding a missing README row -- missing
    its `Owner:` field or `# Title` heading; and a write that failed its
    own crash-safety check (see _write) -- covers both a file's own
    Progress: header write and resync's own final README write. That
    is a deliberate exception to every other command's all-or-nothing rule:
    withholding real, unrelated fixes until a human resolves one bad file
    or stale row would leave live drift sitting around for no reason.
    """
    changes: list[str] = []
    unreadable: list[str] = []

    open_paths = sorted(p for p in todo_dir.glob("*.md") if p.name != "README.md")
    completed_dir = todo_dir / "completed"
    completed_paths = (
        sorted(completed_dir.glob("*.md")) if completed_dir.exists() else []
    )

    header_unreadable = _resync_progress_pass(open_paths, "", changes, unreadable)
    _resync_progress_pass(completed_paths, "completed/", changes, unreadable)

    original_readme = _read_readme(todo_dir)
    lines = original_readme.splitlines()
    for path in open_paths:
        if path.name in header_unreadable:
            # A header-parse failure here would just re-find the same
            # problem loop 1 already reported (see _resync_progress_pass's
            # docstring for why a _WriteCheckFailure does NOT land in
            # `header_unreadable`, and so does not skip this loop).
            continue
        # EVERYTHING derived from this file is computed here, under one guard,
        # and nothing below may raise on the file's contents. Three review
        # rounds each found a new abort inside this loop -- an unguarded
        # `Owner:` read, an unparseable row, a `|` reaching `_require_no_pipe`
        # -- because each new repair added its own raising call among the
        # README edits. Computing first and applying second is what stops the
        # next one: a bad file lands in `unreadable` and the other 192 are
        # still repaired.
        #
        # A ValueError from the README-structure work below (e.g. a row sitting
        # outside any ### section) is a different problem and must still
        # propagate uncaught.
        try:
            text = _read(path)
            done, total = _boxes(text)
            _before, header, _after = _split_header(text)
            status = _get_field(header, "Status")
            requires_roy = _get_requires_roy(header)
            # BOTH optional, for the same reason: each is consumed only by the
            # row-missing and row-rebuild branches, so a file whose row exists
            # and parses must still get its counts, roy cell, owner cell and
            # section repaired when one of them is unusable. Making `Owner:`
            # optional and leaving the title a hard requirement just moved the
            # whole-file skip from one field to the other.
            what: str | None
            try:
                what = _require_no_pipe(_title(text), "the README row's 'what' text")
            except ValueError as exc:
                what = None
                unreadable.append(f"{path.name}: row text not rebuilt ({exc})")
            want_owner: str | None
            try:
                want_owner = _require_no_pipe(
                    _owner_cell(_get_field(header, "Owner")), "owner"
                )
            except ValueError as exc:
                want_owner = None
                unreadable.append(f"{path.name}: owner cell not repaired ({exc})")
        except ValueError as exc:
            unreadable.append(f"{path.name}: {exc}")
            continue

        row_idx = _find_row_line(lines, path.name)

        if row_idx is None:
            if want_owner is None or what is None:
                continue  # already reported; no row can be built without them
            row = _row_line(path.stem, want_owner, requires_roy, done, total, what)
            lines = _insert_row_into_section(lines, _section_for_status(status), row)
            changes.append(f"{path.name}: added README row ({done}/{total})")
            continue

        # REBUILT, not just reported. A legacy 4-column row can never match
        # `_ROW`, so leaving it alone left it permanently unrepairable: `list`
        # told the reader to run resync, resync could not fix it, and
        # `_require_readme_row` refused every other command for that file. The
        # file's own fields are the source of truth, so rebuild the row from
        # them the same way the row-missing branch builds one.
        if _ROW.match(lines[row_idx]) is None:
            if want_owner is None:
                continue  # already reported
            # ⚠ KEEP what the ROW holds and the file does not: the curated
            # `what` (one real row is 1453 characters against an 89-character
            # title) and a link text that deliberately differs from the slug.
            # Regenerating either turns this repair into data loss on exactly
            # the merge damage it exists to fix.
            link_text, salvaged = _salvage_row(lines[row_idx])
            if salvaged is None and what is None:
                unreadable.append(
                    f"{path.name}: README row has no summary and the title is "
                    "unusable; fix it by hand"
                )
                continue
            if salvaged is not None and "|" in salvaged:
                # Cannot be written back without splitting the row again, and
                # dropping a fragment to make it fit is the silent loss above.
                unreadable.append(
                    f"{path.name}: README row's summary spans a '|'; fix it by hand"
                )
                continue
            lines[row_idx] = _row_line(
                path.stem,
                want_owner,
                requires_roy,
                done,
                total,
                cast(str, salvaged or what),
                link_text=link_text,
            )
            changes.append(f"{path.name}: rebuilt an unparseable README row")

        # ONE match serves all three cell rewrites because they run RIGHT TO
        # LEFT: `done`/`total` sit after `roy`, which sits after `owner`, so
        # editing a cell cannot move the offsets of any cell left of it. The
        # reverse order would (a 9/10 -> 10/10 rewrite changes the line's
        # length).
        m = _require_row_match(lines[row_idx], path.name)
        if (int(m.group("done")), int(m.group("total"))) != (done, total):
            old_done, old_total = m.group("done"), m.group("total")
            lines[row_idx] = _rewrite_row_counts(lines[row_idx], m, done, total)
            changes.append(
                f"{path.name}: README {old_done}/{old_total} -> {done}/{total}"
            )

        if _roy_from_cell(m.group("roy")) != requires_roy:
            lines[row_idx] = _rewrite_row_cell(
                lines[row_idx], m, "roy", _roy_cell(requires_roy)
            )
            changes.append(f"{path.name}: README roy? -> {_roy_cell(requires_roy)}")

        # The owner cell became reconcilable the day it stopped being free text.
        # It is the file's LANES, derived, so resync can compute the right value
        # the same way it computes the counts -- which is what closed
        # TODO/set-owner-readme-drift.md.
        if want_owner is not None and m.group("owner").strip() != want_owner:
            old_owner = m.group("owner").strip()
            lines[row_idx] = _rewrite_row_cell(lines[row_idx], m, "owner", want_owner)
            changes.append(f"{path.name}: README owner {old_owner!r} -> {want_owner!r}")

        want_section = _section_for_status(status)
        cur_section, _count, _hdr = _section_containing(lines, row_idx)
        if cur_section != want_section:
            row = lines[row_idx]
            lines, _ = _remove_row_from_section(lines, path.name)
            lines = _insert_row_into_section(lines, want_section, row)
            changes.append(f"{path.name}: moved {cur_section} -> {want_section}")

    # A section forked before the `roy?` column keeps a 4-column header and
    # 4-column rows. Those rows do not match `_ROW`, so `list` cannot see them
    # and every repair above skips them -- and any row inserted afterwards lands
    # under a header with the wrong arity. Repairing the header is what makes
    # the comment on TABLE_HEADER true.
    # Bounded to `## Open`: the Completed table is a DIFFERENT shape
    # (`| file | outcome |`), and rewriting its header to this one would be the
    # corruption this repair exists to prevent.
    #
    # Guarded like `list_todos`'s sibling call: the tool that exists to repair a
    # mangled README must not be the one that refuses to run on it. Unguarded,
    # a renamed `## Open` aborted here AFTER loop 1 had already rewritten
    # per-file `Progress:` lines — leaving the files touched and the README not.
    try:
        open_start, open_end = _section_bounds(lines, "## Open")
    except ValueError as exc:
        open_start = open_end = 0
        unreadable.append(f"README.md: table headers not checked ({exc})")
    for i in range(open_start, open_end):
        if lines[i].startswith("| file |") and lines[i] != TABLE_HEADER:
            lines[i] = TABLE_HEADER
            changes.append("README: Open table header -> current columns")
        elif lines[i].startswith("| --- |") and lines[i] != TABLE_SEPARATOR:
            lines[i] = TABLE_SEPARATOR
            changes.append("README: Open table separator -> current columns")

    changes.extend(_resync_section_counts(lines))

    new_readme = "\n".join(lines)
    if new_readme.strip("\n") != original_readme.strip("\n"):
        try:
            _write_readme(todo_dir, new_readme)
        except _WriteCheckFailure as exc:
            unreadable.append(f"README.md: {exc}")

    open_names = {p.name for p in open_paths}
    open_stale, _ = _stale_row_scan(
        _ROW, new_readme, open_names, f"README Open row, but no such file in {todo_dir}"
    )
    completed_names = {p.name for p in completed_paths}
    completed_stale, completed_rows = _stale_row_scan(
        _COMPLETED_ROW,
        new_readme,
        completed_names,
        "README Completed row, but no such file in completed/",
    )
    stale = open_stale + completed_stale
    stale += _stale_file_scan(
        completed_paths,
        completed_rows,
        "completed/ file has no row in README Completed table",
    )

    if stale or unreadable:
        applied = "; ".join(changes) if changes else "none needed"
        parts = []
        if stale:
            detail = "\n".join(f"  {s}" for s in stale)
            parts.append(f"{len(stale)} README/completed-file mismatch(es):\n{detail}")
        if unreadable:
            detail = "\n".join(f"  {s}" for s in unreadable)
            parts.append(
                f"{len(unreadable)} file(s) resync could not finish for:\n{detail}"
            )
        raise ValueError(
            f"resync found problems it could not fix on its own "
            f"(fixes already applied: {applied}):\n" + "\n".join(parts)
        )
    return changes


def add_note(
    todo_dir: Path,
    filename: str,
    text: str,
    label: str = "Updated",
    note_date: date | None = None,
) -> None:
    note_date = note_date or date.today()
    _update_header(
        todo_dir,
        filename,
        lambda header: _append_field(
            header, label, f"{note_date.isoformat()} — {text}"
        ),
    )


def _replace_objective_text(text: str, new_body: str, filename: str = "") -> str:
    lines = text.splitlines()
    start, end = _section_bounds(lines, "## Objective", filename)
    body = new_body.strip("\n").splitlines()
    new_lines = lines[: start + 1] + ["", *body, ""] + lines[end:]
    return _rewrite_progress("\n".join(new_lines))


def replace_objective(todo_dir: Path, filename: str, text: str) -> None:
    _apply_and_sync(
        todo_dir, filename, lambda t: _replace_objective_text(t, text, filename)
    )


def list_todos(
    todo_dir: Path,
    owner: str | None = None,
    status: str | None = None,
    notes: bool = False,
    requires_roy: bool = False,
) -> str:
    text = _read_readme(todo_dir)
    lines = text.splitlines()
    section_filter = _section_for_status(status) if status else None
    out = []
    # A row `_ROW_FULL` cannot parse used to be skipped in silence, which
    # answered "what is waiting on me" with "nothing" for a legacy 4-column row
    # or one whose cell holds a `|`. That is the data gap conventions.md refuses
    # to swallow -- name the row, then still list everything that DID parse.
    # Bounded to `## Open`: a Completed row is a different, valid shape
    # (`| file | outcome |`) and is not an unparsed Open row.
    parsed = {m.group("file") for m in _ROW_FULL.finditer(text)}
    try:
        open_start, open_end = _section_bounds(lines, "## Open")
    except ValueError:
        # A diagnostic must not be able to take down the listing it decorates.
        # `list` was a pure regex scan that degraded gracefully; requiring the
        # heading made it exit 1 on the botched-merge README that
        # `_section_containing` already documents as reachable.
        open_start = open_end = 0
    unparsed = [
        ln
        for ln in lines[open_start:open_end]
        if _DATA_ROW_START.match(ln) and not any(f"]({f})" in ln for f in parsed)
    ]
    for m in _ROW_FULL.finditer(text):
        filename = m.group("file")
        owner_cell = m.group("owner").strip()
        what = m.group("what").strip()
        done, total = m.group("done"), m.group("total")
        if owner and owner.lower() not in owner_cell.lower():
            continue
        if requires_roy and not _roy_from_cell(m.group("roy")):
            continue
        row_idx = _find_row_line(lines, filename)
        assert row_idx is not None, "the row just matched by _ROW_FULL must be a line"
        try:
            section, _, _ = _section_containing(lines, row_idx)
        except ValueError:
            continue
        if section_filter and section != section_filter:
            continue
        roy = "  [ROY]" if _roy_from_cell(m.group("roy")) else ""
        out.append(
            f"{filename}  [{section}]  {owner_cell}{roy}  {done}/{total}  {what}"
        )
        if notes:
            path = todo_dir / filename
            if path.exists():
                _, header, _ = _split_header(_read(path))
                out.extend(f"    {ln}" for ln in header)
                out.append("")
    if unparsed:
        out.append("")
        out.append(
            f"⚠ {len(unparsed)} README row(s) could not be parsed and are NOT "
            "listed above — run resync, or fix the row by hand:"
        )
        out.extend(f"    {ln.strip()[:100]}" for ln in unparsed)
    return "\n".join(out)


def _normalize_filename(name: str) -> str:
    return name if name.endswith(".md") else f"{name}.md"


def _todo_dir_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--todo-dir",
        type=Path,
        default=TODO,
        help="override the TODO directory (mainly for tests)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo_tool")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("title")
    create.add_argument("--owner", required=True)
    create.add_argument("--raised-from", required=True)
    create.add_argument("--status", default="open")
    create.add_argument("--summary")
    create.add_argument(
        "--slug",
        help="filename stem to use instead of the slugified title — pick a short "
        "one when the title is long (a trailing .md is dropped)",
    )
    create.add_argument("--task", action="append", required=True, dest="tasks")
    create.add_argument(
        "--requires-roy",
        action="store_true",
        help="Roy has to do something in this TODO (a ruling, a decision, work "
        "only he can do) — independent of who owns it",
    )
    _todo_dir_arg(create)

    check = sub.add_parser("check")
    check.add_argument("file", type=_normalize_filename)
    check.add_argument("n", type=int)
    _todo_dir_arg(check)

    uncheck = sub.add_parser("uncheck")
    uncheck.add_argument("file", type=_normalize_filename)
    uncheck.add_argument("n", type=int)
    _todo_dir_arg(uncheck)

    add_task_p = sub.add_parser("add-task")
    add_task_p.add_argument("file", type=_normalize_filename)
    add_task_p.add_argument("text")
    _todo_dir_arg(add_task_p)

    set_owner_p = sub.add_parser("set-owner")
    set_owner_p.add_argument("file", type=_normalize_filename)
    set_owner_p.add_argument("owner")
    _todo_dir_arg(set_owner_p)

    set_roy_p = sub.add_parser("set-requires-roy")
    set_roy_p.add_argument("file", type=_normalize_filename)
    set_roy_p.add_argument("value", choices=("true", "false"))
    _todo_dir_arg(set_roy_p)

    set_status_p = sub.add_parser("set-status")
    set_status_p.add_argument("file", type=_normalize_filename)
    set_status_p.add_argument("status")
    set_status_p.add_argument("--note")
    _todo_dir_arg(set_status_p)

    complete_p = sub.add_parser("complete")
    complete_p.add_argument("file", type=_normalize_filename)
    complete_p.add_argument("--outcome", required=True)
    complete_p.add_argument("--superseded", action="store_true")
    _todo_dir_arg(complete_p)

    reopen_p = sub.add_parser("reopen")
    reopen_p.add_argument("file", type=_normalize_filename)
    reopen_p.add_argument("--status", default="open")
    reopen_p.add_argument("--note")
    _todo_dir_arg(reopen_p)

    note_p = sub.add_parser("note")
    note_p.add_argument("file", type=_normalize_filename)
    note_p.add_argument("--text", required=True)
    note_p.add_argument("--label", default="Updated")
    note_p.add_argument("--date", type=date.fromisoformat)
    _todo_dir_arg(note_p)

    ro_p = sub.add_parser("replace-objective")
    ro_p.add_argument("file", type=_normalize_filename)
    ro_text = ro_p.add_mutually_exclusive_group(required=True)
    ro_text.add_argument(
        "--text", help="the new Objective body, literal (embedded newlines allowed)"
    )
    ro_text.add_argument(
        "--text-file",
        type=Path,
        help="read the new Objective body from this file instead of --text "
        "— easier than quoting multi-paragraph markdown on a command line",
    )
    _todo_dir_arg(ro_p)

    resync_p = sub.add_parser("resync")
    _todo_dir_arg(resync_p)

    list_p = sub.add_parser("list")
    list_p.add_argument("--owner")
    list_p.add_argument("--status")
    list_p.add_argument("--notes", action="store_true")
    list_p.add_argument(
        "--requires-roy",
        action="store_true",
        help="only TODOs needing something from Roy, whoever owns them",
    )
    _todo_dir_arg(list_p)

    return parser


def main(argv: list[str] | None = None) -> int:
    # ! LOCAL PATCH, not upstream. This tool prints U+2192, U+26A0 and em
    # dashes, and `tests/test_shipped_cli_encoding.py` refuses a program that
    # prints without saying what encoding it prints in. Reproduced 2026-08-18
    # on this machine: a cp1252 stdout raised UnicodeEncodeError on U+2192.
    # The same gap is upstream and is worth reporting there.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    todo_dir: Path = args.todo_dir
    try:
        if args.command == "create":
            path = create_todo(
                todo_dir,
                args.title,
                owner=args.owner,
                raised_from=args.raised_from,
                status=args.status,
                summary=args.summary,
                tasks=tuple(args.tasks),
                slug=args.slug,
                requires_roy=args.requires_roy,
            )
            print(f"created {path}")
        elif args.command == "check":
            check_task(todo_dir, args.file, args.n, True)
        elif args.command == "uncheck":
            check_task(todo_dir, args.file, args.n, False)
        elif args.command == "add-task":
            add_task(todo_dir, args.file, args.text)
        elif args.command == "set-owner":
            set_owner(todo_dir, args.file, args.owner)
        elif args.command == "set-requires-roy":
            set_requires_roy(todo_dir, args.file, args.value == "true")
        elif args.command == "set-status":
            set_status(todo_dir, args.file, args.status, args.note)
        elif args.command == "complete":
            dest = complete_todo(todo_dir, args.file, args.outcome, args.superseded)
            print(f"moved to {dest}")
        elif args.command == "reopen":
            dest = reopen_todo(todo_dir, args.file, args.status, args.note)
            print(f"reopened to {dest}")
        elif args.command == "note":
            add_note(todo_dir, args.file, args.text, args.label, args.date)
        elif args.command == "replace-objective":
            text = (
                args.text
                if args.text is not None
                else args.text_file.read_text(encoding="utf-8")
            )
            replace_objective(todo_dir, args.file, text)
        elif args.command == "resync":
            changes = resync(todo_dir)
            print("\n".join(changes) if changes else "all numbers already agree")
        elif args.command == "list":
            print(
                list_todos(
                    todo_dir, args.owner, args.status, args.notes, args.requires_roy
                )
            )
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):
        if _s.encoding and _s.encoding.lower() != "utf-8":
            (cast(Any, _s)).reconfigure(encoding="utf-8")
    raise SystemExit(main())
