"""T7 -- the brief's OWN worked example, run through `collate`.

!! THE DEFECT THIS EXISTS FOR, MEASURED 2026-08-29. `reviewer-brief.md` keys a
mark's ruling `instruction` and `desk/mark.py` read `mark`, so the example the
brief publishes for a role to copy passed `mark --check` AT EXIT 0 -- as
UNRULED. `problems_in` skipped any entry whose `mark` key was absent and
counted it as a place nobody looked at. **A reviewer following the brief
produced findings that vanished in silence, and every gate was green.**

! SO EXIT 0 IS NOT THE CHECK. This asserts the mark was COUNTED -- one place
ruled on, none left unruled -- which is the half that was false while the exit
code was right.

! THE INPUT IS READ OUT OF THE SHIPPED BRIEF, never retyped. A copy typed into
this file would agree with whatever the code expects on the day it was typed,
which is exactly how the two drifted apart.

!! THE END-TO-END CASE MOVED FROM `mark --check` TO `collate`, 2026-08-30.
`--check` left `mark` entirely and became `collate`'s first act -- see
`src/comment_review/commands/distribute.py`'s own docstring -- so the command a
role's output actually meets is now `collate`, not `mark --check`.

    uv run pytest -q tests/test_brief_worked_example.py
"""

import json
import re
import sys

import pytest
from conftest import ROOT
from helpers import a_binder_over, returned

from comment_review.commands.collate import main as collate_main
from comment_review.desk.collator import tally
from comment_review.desk.mark import Mark, untouched
from comment_review.flows.mark_errors import mark_errors

BRIEF_PATH = (
    ROOT
    / "plugins"
    / "comment-review"
    / "skills"
    / "comment-review"
    / "references"
    / "reviewer-brief.md"
)


def the_briefs_worked_example() -> dict:
    """The first ```json block in `reviewer-brief.md`, parsed.

    ! That block is the filled `edit_copy` under *"You FILL a record; you do
    not write one"* -- the shape a role is handed and hands back.
    """
    brief = BRIEF_PATH.read_text(encoding="utf-8")
    block = re.search(r"```json\n(.*?)\n```", brief, re.DOTALL)
    assert block is not None, "the brief no longer publishes a JSON example"
    return json.loads(block.group(1))


EXAMPLE = the_briefs_worked_example()
#: The one mark that example carries.
ENTRY = EXAMPLE["sheets"][0]["marks"][0]
#: The same example through the boundary the flow runs it through -- what
#: `problems_in`, `unruled` and `tally` take since `P42`. ! IT IS ALSO A CLAIM
#: ABOUT THE BRIEF: the block a role is shown must parse as an `EditCopy`, and
#: `returned` asserts that here rather than letting a malformed example reach
#: the functions below as a surprising result.
PARSED = returned(EXAMPLE, "the brief's example")


def test_the_example_is_one_filled_mark():
    """The input's own shape, stated so a brief that changed underneath this
    file fails here rather than making the assertions below vacuous."""
    assert len(EXAMPLE["sheets"]) == 1
    assert len(EXAMPLE["sheets"][0]["marks"]) == 1


def test_the_example_is_not_read_as_an_untouched_slot():
    """The exact confusion: a filled mark read as a place nobody looked at."""
    assert not untouched(ENTRY)


def test_the_examples_mark_parses():
    mark, why = Mark.deserialize("the brief's example", ENTRY)
    assert why == []
    assert mark is not None
    assert mark.instruction == ENTRY["instruction"]
    assert mark.change == ENTRY["change"]


def test_the_example_is_ONE_RULED_MARK_and_owes_nothing():
    """!! THE ASSERTION THAT WOULD HAVE CAUGHT IT. The per-copy check returned
    `([], 0)` on this input -- no problems AND nothing ruled on.

    ! ASKED OF `flows.mark_errors` SINCE `P52`, which is the one assembler now.
    Its EMPTY return is both halves of the old claim at once: nothing refused,
    and nothing left unruled."""
    assert mark_errors([PARSED]) == []
    assert [mark.address for sheet in PARSED.sheets for mark in sheet.marks] == [
        ENTRY["address"]
    ]


def test_tally_names_the_instruction_the_brief_wrote():
    assert tally(PARSED) == {ENTRY["instruction"]: 1}


def test_collate_reads_it_as_a_ruled_mark_and_reports_only_what_it_cannot_resolve(
    tmp_path, capsys, monkeypatch
):
    """The command a role's output actually meets, end to end.

    ! `--binder` carries no page for `b47`, so `drift_in`'s `address not in
    base` skip fires and nothing is compared -- the drift check is not what
    this test is about.

    !! IT ASSERTED `code == 0` UNTIL 2026-08-31, AND THAT ONLY HELD WHILE
    SOURCE VERIFICATION WAS UNWIRED. `P25` put `desk.collator.verify_report`
    into the flow, and it reports three true things about this input:

        `address` 'b47' names no place the binder carries   -- the binder is EMPTY
        `claim.false` is not in the paragraph this row seeded -- there is no paragraph
        two `cite`s do not resolve                          -- see below

    !! THE CITATIONS CAN NEVER RESOLVE IN THIS TREE, BY DESIGN. The brief's
    worked example cites `redacted_pkg/...`, a package this repo does not ship
    and will not -- so the example is not verifiable HERE, and that is a fact
    about the example rather than a defect in the flow.

    ! SO WHAT THIS TEST NOW ASSERTS IS THE PART THAT IS ABOUT THE BRIEF: the
    example is a WELL-FORMED ruled mark -- `problems_in` returns `([], 1)`, in
    the test above -- and every finding the command reports is a
    source-verification one, not a shape one. A `code == 0` here would now mean
    verification had stopped running.
    """
    copy_path = tmp_path / "edit_copy.json"
    copy_path.write_text(json.dumps(EXAMPLE), encoding="utf-8")
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(a_binder_over({}).serialize()), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "collate",
            "--stage",
            "4c",
            "--binder",
            str(binder_path),
            "--out",
            str(tmp_path / "chief.json"),
            "--edit-copy",
            str(copy_path),
        ],
    )
    code = collate_main()
    printed = capsys.readouterr().out
    assert code == 1, printed
    # ! EVERY LINE IS A SOURCE-VERIFICATION FINDING. If a SHAPE problem ever
    # appears here, the brief's worked example has stopped being a well-formed
    # mark, which is the thing this file exists to notice.
    lines = [line for line in printed.splitlines() if line.strip()]
    assert lines
    for line in lines:
        assert any(
            claim in line
            for claim in (
                "names no place",
                "is not in the paragraph",
                "does not resolve",
            )
        ), line


@pytest.mark.parametrize("key", ["claim", "reason", "sources", "change"])
def test_dropping_a_field_the_example_fills_is_refused(key):
    """T7 CAN FAIL: the example is accepted because it is well formed, not
    because the parse waves it through. Each field the brief fills is removed
    in turn and the mark must be refused."""
    broken = dict(ENTRY)
    del broken[key]
    mark, why = Mark.deserialize("the brief's example", broken)
    assert mark is None and why != []


def test_the_retired_key_name_is_refused_by_name():
    """A role written against the OLD code -- keying the ruling `mark` --
    is now told so, where it was silently counted as unruled."""
    old = {k: v for k, v in ENTRY.items() if k != "instruction"}
    old["mark"] = ENTRY["instruction"]
    assert not untouched(old)
    mark, why = Mark.deserialize("the brief's example", old)
    assert mark is None
    assert any("instruction" in message for message in why)
