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


class TestAddressesOnARealPage:
    SRC = '"""Doc."""\n\n# note\ndef f():\n    return 1  # beside\n'

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
