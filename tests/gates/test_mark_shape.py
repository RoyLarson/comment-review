"""The dataclass carries exactly what the spec allows, and no prose.

! EXPECTATION FROM `docs/the-mark.md`. `decision-log.md Process: #37` records
what it cost to have no file able to refuse a field: a 22-field classifier
scheme entered `desk/mark.py` during a port that was never proposed and never
approved, because nothing could name what the row was allowed to carry.

    uv run pytest -q tests/gates/test_mark_shape.py
"""

import dataclasses
import re

import pytest
from conftest import ROOT

from comment_review.desk.mark import INSTRUCTIONS, Row

SPEC = (ROOT / "docs" / "the-mark.md").read_text(encoding="utf-8")

#: The section stating the four columns and the seven flags, and nothing
#: else -- `## The classifiers ...` up to the next `##` heading,
#: `## The three \`query\` shapes`. Scoped so the parse below cannot pick up
#: an unrelated bold-first-column table or fixed-width block elsewhere in the
#: file (`## \`move\`'s destination`, further down, has both).
_SECTION = re.search(
    r"^## The classifiers.*?(?=^## )", SPEC, re.MULTILINE | re.DOTALL
).group()

#: The four classifier columns and the seven row flags, each stated once in
#: `docs/the-mark.md`, mapped to the field that carries it. English prose is
#: not a valid Python identifier, so this dict is the one place the spec's
#: wording and the dataclass's field names meet -- it supplies no NAMES of its
#: own; every key below must appear as a parsed phrase from the spec's own
#: tables, checked by `test_every_mapped_phrase_is_in_the_spec` below.
FIELD_FOR = {
    "claim keys": "claim_all",
    "verbatim": "quotes_original",
    "change": "owes_change",
    "sources": "owes_sources",
    "not substantive": "substantive",
    "may declare scope": "can_declare_scope",
    "empty change allowed": "may_empty",
    "rules on text": "rules_on_text",
    "not diffable": "diffable",
    "anchor named in backticks": "needs_anchor",
    "destination addressable": "owes_destination",
}


def _classifier_names() -> list[str]:
    """The four classifier-column names, read out of the spec's own table.

    `docs/the-mark.md`'s "The classifiers" table names each in its first,
    bolded column -- `| **claim keys** | ... |`.
    """
    return re.findall(r"^\| \*\*([^*]+)\*\* \|", _SECTION, re.MULTILINE)


def _flag_names() -> list[str]:
    """The seven row-flag phrases, read out of the spec's own fixed block.

    Each flag starts a line right after the block's 4-space indent, followed
    by a 2+ space gap and its one-line explanation; a WRAPPED continuation
    line (see "may declare scope") carries extra leading whitespace instead
    and does not match.
    """
    return re.findall(r"^ {4}(\S.*?) {2,}\S", _SECTION, re.MULTILINE)


def allowed_names() -> set[str]:
    """The classifier and flag names the spec states, as field names."""
    names = _classifier_names() + _flag_names()
    assert len(names) == 11, f"expected 11 names in the spec, found: {names}"
    return {FIELD_FOR[n] for n in names}


def test_every_mapped_phrase_is_in_the_spec():
    """`FIELD_FOR`'s keys are exactly what the spec's tables state -- proof
    the mapping cannot silently drift from the prose it translates."""
    assert set(FIELD_FOR) == set(_classifier_names()) | set(_flag_names())


def test_the_row_carries_only_what_the_spec_allows():
    have = {f.name for f in dataclasses.fields(Row)}
    assert have == allowed_names(), sorted(have ^ allowed_names())


def test_no_field_carries_prose():
    """A row states facts. A sentence for a human is not a fact about the row."""
    for f in dataclasses.fields(Row):
        assert f.type is not str or f.name in {"quotes_original"}, f.name


# === Per-instruction agreement: the spec's own table against `INSTRUCTIONS`.
#
# !! WHY THIS EXISTS. `tests/test_mark.py`'s
# `test_patch_owes_no_source_because_its_payload_says_so` was deleted
# 2026-08-28 along with the `payload` field it read, but it was not noise: it
# guarded a defect `desk/mark.py`'s own history records as having SHIPPED and
# been RE-CONFIRMED TWICE -- `patch`'s stored prose said "needs no source"
# while its flag said otherwise, fatally refusing every compliant `patch`.
# That prose now lives in `docs/the-mark.md`'s "What each instruction owes"
# table, so the agreement worth checking is SPEC TABLE against ROW -- stronger
# than the old row-against-itself check, because the expectation now sits
# where the code cannot move it.

#: The fenced block under "## What each instruction owes": the header line,
#: the `---` separator, then one wrapped record per instruction.
_OWES_LINES = re.search(
    r"^## What each instruction owes\n.*?```\n(.*?)\n```",
    SPEC,
    re.MULTILINE | re.DOTALL,
).group(1).splitlines()
_OWES_HEADER, _OWES_ROWS = _OWES_LINES[0], _OWES_LINES[2:]

#: Column start offsets, read from the header itself rather than hand-copied
#: -- a column that moves in the spec moves this too. A cell is sliced by
#: POSITION, not by indentation: `add`'s wrapped line carries a fragment of
#: BOTH the claim column ("anchor") and the flags column ("NAMED IN
#: BACKTICKS") on the same physical line, which an indent-only match cannot
#: tell apart.
_OWES_CELLS = ("name", "claim", "verbatim", "change", "sources", "flags")
_OWES_COLUMNS = (
    "claim carries",
    "verbatim",
    "change",
    "sources",
    "the row's own flags",
)
_OWES_STARTS = (0, *(_OWES_HEADER.index(c) for c in _OWES_COLUMNS))
#: (cell name, start offset, end offset) triples, the header's own column
#: starts sliding each cell's END to the next cell's START.
_OWES_BOUNDS = tuple(
    zip(_OWES_CELLS, _OWES_STARTS, (*_OWES_STARTS[1:], None), strict=True)
)


def _slice_row(line: str) -> dict[str, str]:
    """One physical line, sliced into its cells by column POSITION."""
    return {key: line[start:end].strip() for key, start, end in _OWES_BOUNDS}


def _owes_table() -> dict[str, dict[str, str]]:
    """One entry per instruction: the table's five cells, as raw strings.

    A cell that wraps (`query`'s claim keys, `move`'s `change`, several
    rows' flags column) continues on a line sliced at the same column
    positions as the first; this joins each fragment back onto the cell it
    belongs to before any value is interpreted.
    """
    table: dict[str, dict[str, str]] = {}
    order: list[str] = []
    for line in _OWES_ROWS:
        if not line.strip():
            continue
        cells = _slice_row(line)
        if cells["name"]:
            order.append(cells["name"])
            table[cells["name"]] = {k: cells[k] for k in _OWES_CELLS[1:]}
            continue
        row = table[order[-1]]
        for key in _OWES_CELLS[1:]:
            if cells[key]:
                row[key] = (row[key] + " " + cells[key]).strip()
    return table


def _claim_all_from(cell: str) -> tuple[str, ...]:
    """"--" is no keys; otherwise a comma-joined list, `,`-split and stripped."""
    cell = cell.strip()
    if cell == "--":
        return ()
    return tuple(p.strip() for p in cell.split(",") if p.strip())


def _quotes_original_from(cell: str) -> str:
    """"--" quotes nothing; otherwise the cell names the claim key verbatim."""
    cell = cell.strip()
    return "" if cell == "--" else cell


def _owed_from(cell: str) -> bool:
    """"no"/"NO" is not owed; "yes"/"YES"/"the COMPOSITE" is owed."""
    return cell.strip().lower() != "no"


OWES_TABLE = _owes_table()


def test_the_owes_table_names_the_same_seven_rows():
    assert set(OWES_TABLE) == set(INSTRUCTIONS)


@pytest.mark.parametrize("name", sorted(INSTRUCTIONS))
def test_the_owes_table_claim_keys_agree_with_the_row(name):
    assert _claim_all_from(OWES_TABLE[name]["claim"]) == INSTRUCTIONS[name].claim_all


@pytest.mark.parametrize("name", sorted(INSTRUCTIONS))
def test_the_owes_table_verbatim_agrees_with_the_row(name):
    got = _quotes_original_from(OWES_TABLE[name]["verbatim"])
    assert got == INSTRUCTIONS[name].quotes_original


@pytest.mark.parametrize("name", sorted(INSTRUCTIONS))
def test_the_owes_table_change_agrees_with_the_row(name):
    assert _owed_from(OWES_TABLE[name]["change"]) == INSTRUCTIONS[name].owes_change


@pytest.mark.parametrize("name", sorted(INSTRUCTIONS))
def test_the_owes_table_sources_agree_with_the_row(name):
    """The `patch` case specifically -- see the module-level note above this
    section: this exact cell/flag pair shipped out of agreement once and
    fatally refused every compliant `patch`, re-confirmed twice."""
    assert _owed_from(OWES_TABLE[name]["sources"]) == INSTRUCTIONS[name].owes_sources


#: The block's own wrapped description text, phrase -> full explanation
#: (continuation lines, e.g. "may declare scope"'s, joined back on).
_FLAGS_BLOCK = re.search(
    r"\*\*The flags, and there are seven:\*\*\n\n(.*?)\n\n!!", SPEC, re.DOTALL
).group(1)


def _flag_descriptions() -> dict[str, str]:
    out: dict[str, str] = {}
    current = ""
    for line in _FLAGS_BLOCK.splitlines():
        m = re.match(r"^ {4}(\S.*?) {2,}(\S.*)$", line)
        if m:
            current = m.group(1)
            out[current] = m.group(2)
        elif line.strip():
            out[current] += " " + line.strip()
    return out


_WORD = re.compile(r"[A-Za-z]+")

#: The two flags stated in the NEGATIVE ("not substantive", "not diffable"):
#: the description names who the flag applies to, which is the opposite of
#: what the field's own boolean reads for that row.
_INVERTED = {"substantive", "diffable"}


def _flag_owners(description: str, names: set[str]) -> set[str]:
    """The instruction name(s) a flag's description names it for -- "clean
    alone", "correct and patch" -- by walking its leading words and
    stopping at the first word that names neither an instruction nor the
    connector "and"."""
    owners: set[str] = set()
    for word in _WORD.findall(description):
        lw = word.lower()
        if lw in names:
            owners.add(lw)
        elif lw == "and":
            continue
        else:
            break
    return owners


@pytest.mark.parametrize("phrase", sorted(set(_flag_names())))
def test_the_flags_block_names_agree_with_the_row(phrase):
    field = FIELD_FOR[phrase]
    names = set(INSTRUCTIONS)
    owners = _flag_owners(_flag_descriptions()[phrase], names)
    assert owners, f"{phrase!r} names no instruction in its own description"
    for name in names:
        got = getattr(INSTRUCTIONS[name], field)
        want = (name not in owners) if field in _INVERTED else (name in owners)
        assert got == want, f"{name}.{field} is {got}, {phrase!r} says {want}"
