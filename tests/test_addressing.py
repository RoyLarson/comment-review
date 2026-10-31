"""An address, its two halves, and the series that define them.

`reading/series.py` and `reading/addresser.py`. Nothing here reads a file: an
address is a naming scheme, and it either composes and decomposes or it does
not.
"""

import pytest
from conftest import build, by_cue

from comment_review.reading.addresser import (
    SEPARATOR,
    address_for,
    cue,
    cue_of,
    flatten,
    unflatten,
)
from comment_review.reading.series import (
    ABSENT,
    ADDRESSED,
    BY_LETTER,
    Kind,
    Series,
)
from comment_review.reading.source import CodeLine, DocPlace

PATHS = [
    "m.py",
    "pkg/m.py",
    "a/b/c/deep.py",
    "with space.py",
    "dash-and_underscore.py",
    "UPPER.PY",
    "dotted.name.py",
]
CUES = ["a0", "b0", "c0", "f0", "a12", "b345", "c7", "f1"]


class TestTheSeriesDefinition:
    """The letter and the pair are ONE declaration -- `decision-log.md
    Addressing: #14`."""

    def test_every_series_has_a_distinct_letter(self):
        letters = [s.value.letter for s in Series]
        assert len(letters) == len(set(letters))

    def test_every_letter_is_one_character(self):
        assert all(len(s.value.letter) == 1 for s in Series)

    def test_a_letter_resolves_back_to_its_series(self):
        for s in Series:
            assert BY_LETTER[s.value.letter] is s

    def test_only_the_fence_has_no_absence(self):
        """`d` is the one series whose empty form cannot be cited -- there is
        nothing for `absent` to mean."""
        without = {s.name for s in Series if s.value.absent is None}
        assert without == {"LEAD"}

    def test_the_citable_letters_exclude_the_fence(self):
        assert set(ADDRESSED) == {
            s.value.letter for s in Series if s.value.absent is not None
        }
        assert "d" not in ADDRESSED

    def test_the_absences_are_derived_from_the_pairs(self):
        assert ABSENT == {s.value.absent for s in Series if s.value.absent is not None}

    def test_no_kind_is_both_a_presence_and_an_absence(self):
        present = {s.value.present for s in Series}
        assert present & ABSENT == set()

    def test_every_kind_belongs_to_exactly_one_series(self):
        owners: dict[Kind, int] = {}
        for s in Series:
            for kind in (s.value.present, s.value.absent):
                if kind is not None:
                    owners[kind] = owners.get(kind, 0) + 1
        assert set(owners) == set(Kind)
        assert set(owners.values()) == {1}

    @pytest.mark.parametrize("cue", CUES)
    def test_a_cue_finds_its_series(self, cue):
        assert Series.of(cue) is BY_LETTER[cue[0]]

    def test_a_cue_naming_no_series_answers_nothing(self):
        assert Series.of("") is None
        assert Series.of("z9") is None


class TestTheTwoPredicates:
    """They differ by exactly one member, and merging them renumbers a page."""

    def test_a_fence_holds_no_prose(self):
        assert Kind.holds_no_prose(Kind.LEADING)

    def test_a_fence_DOES_occupy_lines(self):
        """It stands on real blank lines. Answering otherwise takes them out of
        `occupied`, so they read as CODE and every `b` and `c` below
        renumbers."""
        assert not Kind.occupies_no_lines(Kind.LEADING)

    @pytest.mark.parametrize("kind", sorted(ABSENT))
    def test_an_absence_answers_yes_to_both(self, kind):
        assert Kind.holds_no_prose(kind)
        assert Kind.occupies_no_lines(kind)

    @pytest.mark.parametrize(
        "kind", sorted({s.value.present for s in Series} - {Kind.LEADING})
    )
    def test_prose_answers_no_to_both(self, kind):
        assert not Kind.holds_no_prose(kind)
        assert not Kind.occupies_no_lines(kind)

    def test_the_two_part_on_exactly_the_fence(self):
        differ = {
            k for k in Kind if Kind.holds_no_prose(k) != Kind.occupies_no_lines(k)
        }
        assert differ == {Kind.LEADING}


class TestComposingAndTakingApart:
    @pytest.mark.parametrize("path", PATHS)
    @pytest.mark.parametrize("cue", CUES)
    def test_an_address_splits_into_the_halves_it_was_made_from(self, path, cue):
        got = cue_of(address_for(path, cue))
        assert got.cue == cue
        assert got.path == flatten(path)

    @pytest.mark.parametrize("cue", CUES)
    def test_the_series_is_read_off_the_cue(self, cue):
        assert cue_of(address_for("m.py", cue)).series == cue[0]

    @pytest.mark.parametrize("path", PATHS)
    def test_a_flattened_path_recovers_the_real_one(self, path):
        assert unflatten(flatten(path), [path]) == path

    def test_a_path_that_no_page_carries_recovers_nothing(self):
        assert unflatten(flatten("nope.py"), ["m.py"]) == ""

    def test_an_ambiguous_flattening_answers_nothing(self):
        """Two real paths flattening alike cannot be told apart, so picking one
        would answer a question nobody asked."""
        assert unflatten(flatten("a/b.py"), ["a/b.py", f"a{SEPARATOR}b.py"]) == ""

    @pytest.mark.parametrize("text", ["m.py", "b3", "", "no-at-sign", "m.py@", "@b3"])
    def test_a_string_that_is_not_an_address_splits_into_nothing(self, text):
        """An address is `path@cue`. A BARE CUE is not one -- the compositor was
        measured disagreeing with itself for assuming otherwise."""
        got = cue_of(text)
        assert got == ("", "") or "" in got

    def test_asking_a_non_address_for_its_series_RAISES(self):
        """It has no series to give. Answering "" let a fence travel as though
        it were a cue."""
        with pytest.raises(IndexError):
            _ = cue_of("m.py").series

    def test_either_half_missing_composes_no_address(self):
        assert address_for("", "b0") == ""
        assert address_for("m.py", "") == ""


class TestTheWalkOverCodeLines:
    """`cue` over hand-built `CodeLine`s: an `a` is set where `DocPlace` says."""

    @staticmethod
    def walk(documented: dict[int, DocPlace], lines=(1, 2, 3, 5)):
        return cue([CodeLine(n, f"line {n}", documented.get(n)) for n in lines])

    def test_a_doc_inside_its_declaration_is_set_after_the_line_it_names(self):
        cues = self.walk({1: DocPlace(3, False)})
        assert cues.reading == [
            *("f0", "a0", "b0", "c0", "b1", "c1", "b2", "c2"),
            *("a1", "b3", "c3", "b4", "a2", "f1"),
        ]
        assert cues.anchor_line("a1") == 1
        assert cues.anchor_of("a1") == "line 1"

    def test_a_doc_above_its_declaration_is_set_between_the_gap_and_the_line(self):
        cues = self.walk({3: DocPlace(3, True)})
        assert cues.reading == [
            *("f0", "a0", "b0", "c0", "b1", "c1", "b2", "a1", "c2"),
            *("b3", "c3", "b4", "a2", "f1"),
        ]
        assert cues.anchor_line("a1") == 3

    def test_a_doc_after_the_last_line_comes_before_the_closing_gap(self):
        cues = self.walk({2: DocPlace(2, False)}, lines=(1, 2))
        assert cues.reading == [
            "f0",
            "a0",
            "b0",
            "c0",
            "b1",
            "c1",
            "a1",
            "b2",
            "a2",
            "f1",
        ]

    def test_a_one_line_def_sets_its_doc_after_the_line_not_before_its_gap(self):
        """The one reading-order change `CodeLine`s made: the `a` of a
        declaration whose body shares its line follows that line's `c`."""
        cues = cue([CodeLine(1, "def f(): return 1", DocPlace(1, False))])
        assert cues.reading == ["f0", "a0", "b0", "c0", "a1", "b1", "a2", "f1"]

    def test_the_a_series_meets_eof_between_the_closing_gap_and_the_foot(self):
        cues = cue([CodeLine(1, "x", DocPlace(1, True)), CodeLine(2, "y", None)])
        assert cues.reading[-3:] == ["b2", "a2", "f1"]
        assert cues.anchor_of("a2") == "<eof>"
        assert cues.anchor_line("a2") is None
        assert cues.anchor_num("a2") == 3

    @pytest.mark.parametrize(
        ("sentinel", "expected"),
        [
            ("<module>", [["a0"], [], [], ["f0"]]),
            ("<eof>", [["a2"], ["b2"], [], ["f1"]]),
        ],
    )
    def test_a_sentinel_names_the_places_each_series_emitted_there(
        self, sentinel, expected
    ):
        cues = cue([CodeLine(1, "x", DocPlace(1, True)), CodeLine(2, "y", None)])
        assert [cues.at_line(sentinel, s) for s in "abcf"] == expected

    def test_without_an_a_series_nothing_meets_eof_but_the_gap_and_the_foot(self):
        cues = cue([CodeLine(1, "x", None)], a_series=False)
        assert cues.reading == ["f0", "b0", "c0", "b1", "f1"]

    def test_a_language_with_no_closing_docstring_has_no_a_at_eof(self):
        cues = cue([CodeLine(1, "x", None)], closing_docstring=False)
        assert cues.reading == ["f0", "a0", "b0", "c0", "b1", "f1"]

    def test_a_doc_set_before_its_own_declaration_is_refused(self):
        with pytest.raises(ValueError, match="a1"):
            self.walk({3: DocPlace(2, False)})


class TestAUnitOfJoinedLines:
    """Lines joined to the code line above are one line for `a` and `b`."""

    UNIT = "@Ann\n@Other(x = 1)\nclass App {}"

    @staticmethod
    def walk():
        return cue(
            [
                CodeLine(1, "class A {}", None),
                CodeLine(3, "@Ann", None),
                CodeLine(4, "@Other(x = 1)", None, True),
                CodeLine(5, "class App {}", DocPlace(3, True), True),
                CodeLine(6, "int x;", None),
            ]
        )

    def test_a_unit_takes_one_gap_and_one_a_above_its_first_line(self):
        assert self.walk().reading == [
            *("f0", "a0", "b0", "c0", "b1", "a1", "c1", "c2", "c3"),
            *("b2", "c4", "b3", "a2", "f1"),
        ]

    def test_the_units_gap_and_a_are_anchored_to_every_line_of_it(self):
        cues = self.walk()
        assert cues.anchor_of("b1") == cues.anchor_of("a1") == self.UNIT
        assert cues.anchor_line("a1") == cues.anchor_line("b1") == 3

    def test_each_line_of_a_unit_keeps_its_own_c(self):
        cues = self.walk()
        assert [cues.anchor_of(c) for c in ("c1", "c2", "c3")] == [
            "@Ann",
            "@Other(x = 1)",
            "class App {}",
        ]
        assert [cues.at_line(n, "c") for n in (3, 4, 5)] == [["c1"], ["c2"], ["c3"]]

    @pytest.mark.parametrize("line", [3, 4, 5])
    def test_every_line_of_a_unit_answers_the_units_a_and_gap(self, line):
        cues = self.walk()
        assert cues.at_line(line, "a") == ["a1"]
        assert cues.at_line(line, "b") == ["b1"]

    def test_the_gaps_around_a_unit_answer_by_line(self):
        cues = self.walk()
        assert cues.above(2) == "b1"
        assert cues.above(6) == "b2"
        assert cues.above(7) == "b3"
        assert cues.gap_bounds("b1") == (1, 3)
        assert cues.gap_bounds("b2") == (5, 6)


class TestAddressesOnARealPage:
    SRC = '"""Doc."""\n\n# note\ndef f():\n    return 1  # beside\n'

    def test_series_ordinals_empty_places_and_leading_on_a_real_page(self):
        page = build(
            '# Front.\n\n"""Module docs."""\n\n# Above.\n'
            'def f():\n    """Function docs."""\n'
            "    return 1 # Beside\n\n# Back.\n",
            "pkg/m.py",
        )
        places = by_cue(page)
        assert set(places) == {"a0", "a1", "b0", "b1", "b2", "c0", "c1", "f0", "f1"}
        assert places["a0"].raw_text == '"""Module docs."""'
        assert places["a1"].raw_text == '    """Function docs."""'
        assert places["b0"].raw_text == "# Above."
        assert places["c1"].raw_text == " # Beside"
        assert places["f0"].raw_text == "# Front."
        assert places["f1"].raw_text == "# Back."
        empty = {cue for cue, p in places.items() if not p.raw_text}
        assert empty == {"b1", "b2", "c0"}
        leading = [p for p in page if p.kind is Kind.LEADING]
        assert len(leading) == 3
        assert all(not p.address for p in leading)

    def test_every_address_carries_the_page_s_own_path(self):
        page = build(self.SRC, "pkg/m.py")
        for b in page.paragraphs:
            if b.address:
                assert cue_of(b.address).path == flatten("pkg/m.py")

    def test_every_address_recomposes_from_its_halves(self):
        page = build(self.SRC, "pkg/m.py")
        for b in page.paragraphs:
            if b.address:
                half = cue_of(b.address)
                assert address_for("pkg/m.py", half.cue) == b.address

    def test_a_place_keeps_its_address_whether_or_not_prose_fills_it(self):
        """The property line numbers cannot give: a documented and an
        undocumented declaration are both `a1`."""
        documented = by_cue(build('def f():\n    """D."""\n    return 1\n'))
        bare = by_cue(build("def f():\n    return 1\n"))
        assert "a1" in documented and "a1" in bare
        assert documented["a1"].kind != bare["a1"].kind
