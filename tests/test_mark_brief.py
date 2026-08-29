"""The gate against the brief a role reads.

! THE EXPECTATION IS A LITERAL COPIED FROM `reviewer-brief.md`, never from
`INSTRUCTIONS` -- `decision-log.md Vocabulary: #23`. A suite that builds its
cases from the table it is checking can only confirm.
"""

from comment_review.desk.mark import allowed, problems

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
    mark = {
        "mark": "add",
        "address": "src/m.py@b3",
        "reason": "the guard's direction is undocumented",
        "claim": {"missing": "the guard rejects zero", "anchor": "`compute_rates`"},
        "change": ["# Rejects zero."],
        "sources": [{"cite": "src/m.py:12", "verbatim": "if n == 0: raise"}],
    }
    assert problems("src/m.py@b3", mark) == []


def test_a_query_written_from_the_brief_is_accepted():
    mark = {
        "mark": "query",
        "address": "src/m.py@b3",
        "reason": "the units are not stated anywhere I can read",
        "claim": {
            "shape": "unable-to-determine",
            "attempted": "grepped the module and its callers for a unit",
            "settles": "the caller that supplies the value",
        },
        "sources": [{"cite": "src/m.py:12", "verbatim": "rate = n / total"}],
    }
    assert problems("src/m.py@b3", mark) == []


def test_a_query_naming_a_shape_outside_the_three_is_refused():
    mark = {
        "mark": "query",
        "address": "src/m.py@b3",
        "reason": "unclear",
        "claim": {"shape": "i-give-up", "attempted": "read it", "settles": "a human"},
        "sources": [{"cite": "src/m.py:12", "verbatim": "rate = n / total"}],
    }
    assert problems("src/m.py@b3", mark) != []
