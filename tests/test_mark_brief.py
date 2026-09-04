"""The gate against the brief a role reads.

! THE EXPECTATION IS A LITERAL COPIED FROM `reviewer-brief.md`, never from
`INSTRUCTIONS` -- `decision-log.md Vocabulary: #23`. A suite that builds its
cases from the table it is checking can only confirm.

! THE BRIEF'S OWN WORKED EXAMPLE IS RUN IN
`tests/test_brief_worked_example.py`, read out of the shipped file rather than
retyped. Every mark below is keyed `instruction`, which is what the brief
publishes and what the code read as `mark` until 2026-08-29.
"""

from comment_review.desk.mark import Instruction, Mark, allowed

# The brief's published table, reviewer-brief.md:280-288, copied by hand.
BRIEF = {
    "clean": [],
    "query": ["shape", "attempted", "settles"],
    "drop": ["drop"],
    "correct": ["false", "true"],
    "patch": ["from", "to"],
    "add": ["missing", "anchor"],
    "move": ["from", "to"],
}


def test_every_instruction_owes_the_keys_the_brief_publishes():
    assert allowed()["claim"] == BRIEF


def test_an_add_written_from_the_brief_is_accepted():
    entry = {
        "instruction": "add",
        "address": "src/m.py@b3",
        "reason": "the guard's direction is undocumented",
        "claim": {"missing": "the guard rejects zero", "anchor": "`compute_rates`"},
        "change": "# Rejects zero.",
        "sources": [{"cite": "src/m.py:12", "verbatim": "if n == 0: raise"}],
    }
    mark, why = Mark.deserialize("src/m.py@b3", entry)
    assert why == []
    assert mark is not None and mark.instruction is Instruction.ADD


def test_a_query_written_from_the_brief_is_accepted():
    entry = {
        "instruction": "query",
        "address": "src/m.py@b3",
        "reason": "the units are not stated anywhere I can read",
        "claim": {
            "shape": "unable-to-determine",
            "attempted": "grepped the module and its callers for a unit",
            "settles": "the caller that supplies the value",
        },
        "sources": [{"cite": "src/m.py:12", "verbatim": "rate = n / total"}],
    }
    mark, why = Mark.deserialize("src/m.py@b3", entry)
    assert why == []
    assert mark is not None and mark.instruction is Instruction.QUERY


def test_a_query_naming_a_shape_outside_the_three_is_refused():
    entry = {
        "instruction": "query",
        "address": "src/m.py@b3",
        "reason": "unclear",
        "claim": {"shape": "i-give-up", "attempted": "read it", "settles": "a human"},
        "sources": [{"cite": "src/m.py:12", "verbatim": "rate = n / total"}],
    }
    mark, why = Mark.deserialize("src/m.py@b3", entry)
    assert mark is None and why != []
