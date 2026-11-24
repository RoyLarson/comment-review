"""`flows.gather`, the chain of producers.

`TODO/completed/census-should-be-a-chain-of-producers.md` T2, and its verify
text word for word: *the chain is DATA, so adding references_for later is a
list element*.

! INPUTS ARE REAL -- pages over files on disk, through `page_of`.
"""

import pytest
from helpers import a_small_real_tree

from comment_review.binder.binder import Binder
from comment_review.flows import gather as flow


def test_a_reader_failure_is_reported_without_a_successful_page(tmp_path):
    from comment_review.flows.gather import Gathering, _pages

    name = "m.rs"
    text = "const V: i32 = 1;\n/* open"
    expected = (
        "m.rs [rust] lex/unterminated-comment: unterminated comment "
        "(line 2, one-based; column 0, zero-based)"
    )

    path = tmp_path / name
    path.write_text(text, encoding="utf-8", newline="")
    gathered = Gathering(tmp_path, [path], files=[path])
    _pages(gathered)
    assert gathered.pages == []
    assert gathered.unreadable == [expected]


@pytest.mark.parametrize(
    ("name", "raw"),
    [
        ("m.rs", b"// x\rtouch PWNED\n"),
        ("m.py", b"# x\rtouch PWNED\n"),
    ],
    ids=["rs", "py"],
)
def test_a_lone_cr_is_unreadable_at_the_gather(tmp_path, name, raw):
    from comment_review.flows.gather import Gathering, _pages

    path = tmp_path / name
    path.write_bytes(raw)
    gathered = Gathering(tmp_path, [path], files=[path])
    _pages(gathered)
    assert gathered.pages == []
    assert len(gathered.unreadable) == 1
    assert name in gathered.unreadable[0]
    assert "decode/lone-cr" in gathered.unreadable[0]


def test_unexpected_page_errors_propagate_from_gather(tmp_path, monkeypatch):
    from comment_review.flows import gather as gather_mod

    path = tmp_path / "m.py"
    path.write_text("v = 1\n", encoding="utf-8")
    gathered = gather_mod.Gathering(tmp_path, [path], files=[path])

    def broken_page(*args, **kwargs):
        raise RuntimeError("page bug")

    monkeypatch.setattr(gather_mod, "page_of", broken_page)
    with pytest.raises(RuntimeError, match="page bug"):
        gather_mod._pages(gathered)


class TestGather:
    def test_it_returns_the_binder_the_pages_and_the_gaps(self, tmp_path):
        repo = a_small_real_tree(tmp_path)
        (repo / "notes.lock").write_text("not a language\n", encoding="utf-8")
        got = flow.gather(repo, [repo])

        assert isinstance(got.binder, Binder)
        assert [p.path for p in got.binder.pages] == [p.path for p in got.pages]
        assert "stage" not in got.binder.read_from
        assert got.unreadable == []
        assert got.no_record == [(repo / "notes.lock").as_posix()]
        assert sorted(f.name for f in got.files) == [
            "__init__.py",
            "collator.py",
            "mark.py",
            "stages.py",
        ]

    def test_a_named_file_it_cannot_read_is_a_gap_and_not_a_raise(self, tmp_path):
        bad = tmp_path / "m.py"
        bad.write_bytes(b"\xff\xfe" + "x = 1\n".encode("utf-16-le"))
        got = flow.gather(tmp_path, [bad])
        assert got.pages == []
        assert len(got.unreadable) == 1 and "m.py" in got.unreadable[0]

    def test_a_target_that_matched_no_file_is_a_gap(self, tmp_path):
        got = flow.gather(tmp_path, [tmp_path / "nope.py"])
        assert got.unreadable == [
            f"{(tmp_path / 'nope.py').as_posix()} (matched no files)"
        ]

    def test_the_chain_is_data_so_a_step_is_a_list_element(self, tmp_path, monkeypatch):
        """T2's verify. A step appended to `STEPS` runs, on the same `Gathering`,
        after the ones before it -- which is what `references_for` will be."""
        seen = []

        def references_for(g):
            seen.append((g, hasattr(g, "binder")))

        monkeypatch.setattr(flow, "STEPS", (*flow.STEPS, references_for))
        got = flow.gather(a_small_real_tree(tmp_path), [tmp_path / "repo"])
        assert seen == [(got, True)]
        assert got.binder.paragraphs, "the step ran over nothing"

    @pytest.mark.parametrize("gap", ["unreadable", "matched-nothing"])
    def test_a_step_that_found_a_gap_is_the_last_that_runs(
        self, tmp_path, monkeypatch, gap
    ):
        """Neither stage 3 nor the bind runs over a gather that will be refused."""

        def not_reached(*args, **kwargs):
            raise AssertionError("stage 3 ran past a gap")

        monkeypatch.setattr(flow, "_name_corpus", not_reached)
        target = tmp_path / "m.py"
        if gap == "unreadable":
            target.write_bytes(b"\xff\xfe" + "x = 1\n".encode("utf-16-le"))
        got = flow.gather(tmp_path, [target])
        assert len(got.unreadable) == 1
        assert not hasattr(got, "binder")


def test_a_bom_file_still_yields_its_names(tmp_path):
    (tmp_path / "m.py").write_bytes(b"\xef\xbb\xbfdef harvested():\n    pass\n")
    names, unread = flow._name_corpus(tmp_path, None)
    assert "harvested" in names
    assert not any("m.py" in row for row in unread)
