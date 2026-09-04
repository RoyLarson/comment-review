"""The dataclasses carry exactly what the spec allows, and no prose.

! EXPECTATION FROM `docs/the-mark.md`. `decision-log.md Process: #37` records
what it cost to have no file able to refuse a field: a 22-field classifier
scheme entered `desk/mark.py` during a port that was never proposed and never
approved, because nothing could name what the row was allowed to carry.

!! TWO TABLES, TWO TYPES. `Row` answers "The classifiers"; `Mark` answers "The
fields -- eight". Both are READ out of the spec here, never restated -- adding
a row to either table fails this file until the type follows, which is the only
form of the check that cannot be satisfied by editing the code alone.

    uv run pytest -q tests/gates/test_mark_shape.py
"""

import dataclasses
import re

import pytest
from conftest import ROOT

from comment_review.desk.mark import INSTRUCTIONS, Instruction, Mark, Row

SPEC = (ROOT / "docs" / "the-mark.md").read_text(encoding="utf-8")


def _found(match: re.Match[str] | None, name: str) -> re.Match[str]:
    """A required regex match against `docs/the-mark.md`, or a failure that
    NAMES the scan that came back empty.

    !! ASSERTS RATHER THAN SUPPRESSES: `'NoneType' object has no attribute
    'group'` names nothing; `name` says which scan of the spec failed.
    """
    assert match is not None, f"{name} did not match docs/the-mark.md"
    return match


#: The number words `docs/the-mark.md` states its own counts in. ! IT IS NOT A
#: COUNT -- it is the dictionary that turns the spec's word into an integer, so
#: no number below is a restatement of what the spec says. English has no
#: stdlib word-to-int, which is the whole reason this exists.
NUMBER = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}

#: The heading's own stated count -- `## The fields -- eight`.
_FIELDS_HEADING = _found(
    re.search(r"^## The fields -- (\w+)$", SPEC, re.MULTILINE),
    "the fields heading (## The fields -- N)",
)

#: The section stating the mark's own fields, up to the next `##` heading.
#: Scoped the same way `_SECTION` below is, so no other backtick-first-column
#: table in the file can be picked up.
_FIELDS_SECTION = _found(
    re.search(r"^## The fields -- \w+.*?(?=^## )", SPEC, re.MULTILINE | re.DOTALL),
    "the fields section (## The fields -- ... up to the next ##)",
).group()


def _field_names() -> list[str]:
    """The mark's field names, read out of the spec's own table.

    The table's first column names each in backticks -- `| \\`address\\` | ...`
    -- and the header and separator rows carry no backticks, so neither
    matches.
    """
    return re.findall(r"^\| `([a-z_]+)` \|", _FIELDS_SECTION, re.MULTILINE)


def test_the_fields_table_holds_WHAT_ITS_OWN_HEADING_SAYS():
    """The heading states a number and the table under it must hold that
    many -- so a row added or lost is caught here rather than by the
    comparison below quietly agreeing with a shorter list.

    ! THE EXPECTATION IS THE SPEC'S OWN HEADING. Nothing in this file says
    how many fields a mark has."""
    stated = NUMBER[_FIELDS_HEADING.group(1)]
    names = _field_names()
    assert len(names) == stated, (stated, names)


def test_the_mark_carries_exactly_the_fields_the_spec_NAMES():
    """!! THE EXPECTATION IS THE SPEC'S TABLE, NOT A LIST TYPED HERE. Roy,
    2026-08-29: *"mark.py should define a Mark that follows 'the_mark.md' that
    is not negotiable."* A test restating the eight could only confirm, and a
    restated field name is exactly how `mark` and `instruction` came to name
    one thing in two files."""
    have = [f.name for f in dataclasses.fields(Mark)]
    assert have == _field_names()


def test_no_field_is_spelled_two_ways():
    """T6's verify: the file and the code name the same eight, so a reader
    grepping either spelling finds the whole set. The retired spelling of the
    ruling field was `mark`, which is also the name of the OBJECT -- the
    self-nesting that made this ambiguous."""
    assert "mark" not in _field_names()
    assert "instruction" in _field_names()


#: The section stating the four columns and the seven flags, and nothing
#: else -- `## The classifiers ...` up to the next `##` heading,
#: `## The three \`query\` shapes`. Scoped so the parse below cannot pick up
#: an unrelated bold-first-column table or fixed-width block elsewhere in the
#: file (`## \`move\`'s destination`, further down, has both).
_SECTION = _found(
    re.search(r"^## The classifiers.*?(?=^## )", SPEC, re.MULTILINE | re.DOTALL),
    "the classifiers section (## The classifiers ... up to the next ##)",
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


#: The classifiers heading's own stated column count, and the flags label's
#: own stated flag count -- `## The classifiers -- FOUR COLUMNS ...` and
#: `**The flags, and there are seven:**`.
_CLASSIFIER_HEADING = _found(
    re.search(r"^## The classifiers -- (\w+) COLUMNS", SPEC, re.MULTILINE),
    "the classifiers heading (## The classifiers -- N COLUMNS)",
)
_FLAGS_LABEL = _found(
    re.search(r"\*\*The flags, and there are (\w+):\*\*", SPEC),
    "the flags label (**The flags, and there are N:**)",
)


def allowed_names() -> set[str]:
    """The classifier and flag names the spec states, as field names.

    ! THE TOTAL IS READ OFF THE SPEC'S OWN TWO STATEMENTS -- the heading's
    column count plus the label's flag count -- so neither number is typed
    here."""
    names = _classifier_names() + _flag_names()
    stated = (
        NUMBER[_CLASSIFIER_HEADING.group(1).lower()] + NUMBER[_FLAGS_LABEL.group(1)]
    )
    assert len(names) == stated, (
        f"the spec states {stated} names, its tables hold: {names}"
    )
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
_OWES_LINES = (
    _found(
        re.search(
            r"^## What each instruction owes\n.*?```\n(.*?)\n```",
            SPEC,
            re.MULTILINE | re.DOTALL,
        ),
        "the 'What each instruction owes' fenced block",
    )
    .group(1)
    .splitlines()
)
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
    """ "--" is no keys; otherwise a comma-joined list, `,`-split and stripped."""
    cell = cell.strip()
    if cell == "--":
        return ()
    return tuple(p.strip() for p in cell.split(",") if p.strip())


def _quotes_original_from(cell: str) -> str:
    """ "--" quotes nothing; otherwise the cell names the claim key verbatim."""
    cell = cell.strip()
    return "" if cell == "--" else cell


def _owed_from(cell: str) -> bool:
    """ "no"/"NO" is not owed; "yes"/"YES"/"the COMPOSITE" is owed."""
    return cell.strip().lower() != "no"


OWES_TABLE = _owes_table()


def test_the_owes_table_names_the_same_rows():
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
_FLAGS_BLOCK = _found(
    re.search(r"\*\*The flags, and there are \w+:\*\*\n\n(.*?)\n\n!!", SPEC, re.DOTALL),
    "the flags block (**The flags, and there are N:** ... up to !!)",
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


def _flag_owners(description: str, names: set[Instruction]) -> set[str]:
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


def test_no_count_in_this_file_restates_the_spec():
    """!! THE GATE MAY NOT CARRY A NUMBER THE SPEC STATES. Roy, 2026-08-30:
    "Clear the exact hard coded numbers and put in the file that they must
    match." A count typed here is one a field addition edits, and a gate
    edited to pass is indistinguishable afterwards from one that always
    passed."""
    source = (ROOT / "tests" / "gates" / "test_mark_shape.py").read_text(
        encoding="utf-8"
    )
    body = source.split("NUMBER = {", 1)[1].split("}", 1)[1]
    assert not re.search(r"==\s*\d+", body), (
        "a literal count survives outside NUMBER: "
        + str(re.findall(r".*==\s*\d+.*", body))
    )
