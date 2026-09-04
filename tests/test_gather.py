"""`flows.gather`, the chain of producers, and `flows.annotations_for`, stage 3.

`TODO/completed/census-should-be-a-chain-of-producers.md` T1 and T2, and their verify
texts word for word: *it takes a page and returns annotations, and nothing else
calls annotate.py directly*; *the chain is DATA, so adding references_for later
is a list element*.

! INPUTS ARE REAL -- pages over files on disk, through `page_of`. The one literal
is a two-line docstring written twice, because the repeated-literal pass needs
the same number in prose at two places, and no file in `desk/` was written to
supply that.
"""

import re

from conftest import PKG
from helpers import a_small_real_tree

from comment_review.binder.binder import Binder
from comment_review.concordance.annotate import annotate
from comment_review.flows import gather as flow
from comment_review.flows.annotations_for import annotations_for
from comment_review.flows.page_for import page_of

#: The same sentence in two files -- a backticked name `annotate` resolves and a
#: number the repeated-literal pass pairs.
A_PAGE = '"""See `budget`. The cap is 3."""\n'


def _pages(root):
    """Two real pages over the literal, through the real reader."""
    pages = []
    for name in ("a.py", "b.py"):
        (root / name).write_text(A_PAGE, encoding="utf-8", newline="")
        page, why = page_of(root / name, rel=name)
        assert page is not None, why
        pages.append(page)
    return pages


class TestAnnotationsFor:
    def test_it_sets_what_annotate_sets_plus_the_repeated_literal_pair(self, tmp_path):
        """`annotate` alone sees one paragraph; the step sees the pair."""
        alone = [b for p in _pages(tmp_path) for b in flow.carried(p)]
        for b in alone:
            annotate(b, known=set(), paths=set(), repo=tmp_path)
        stepped = [b for p in _pages(tmp_path) for b in flow.carried(p)]
        annotations_for(stepped, known=set(), paths=set(), repo=tmp_path)

        prose = [b for b in stepped if b.text]
        assert prose, "the literal carried no prose"
        for one, two in zip(alone, stepped, strict=True):
            assert two.annotations == one.annotations | (
                {"repeated-literal"} if one.text else set()
            )
        assert all(
            any(n.startswith("3 also in prose at") for n in b.notes) for b in prose
        )

    def test_nothing_else_calls_annotate_directly(self):
        """The step is the one caller. Read off the tree, not asserted."""
        # ! A CALL, not a definition and not a backticked mention in prose.
        call = re.compile(r"(?<!def )(?<!`)\bannotate\(")
        assert call.search("    annotate(b, known, paths, repo)")
        assert not call.search("def annotate(")
        assert not call.search("calls `annotate()` on each")
        callers = sorted(
            p.relative_to(PKG).as_posix()
            for p in PKG.rglob("*.py")
            if call.search(p.read_text(encoding="utf-8"))
        )
        assert callers == ["flows/annotations_for.py"]


class TestGather:
    def test_it_returns_the_binder_the_pages_and_the_gaps(self, tmp_path):
        repo = a_small_real_tree(tmp_path)
        (repo / "notes.lock").write_text("not a language\n", encoding="utf-8")
        got = flow.gather(repo, [repo], 0)

        assert isinstance(got.binder, Binder)
        assert [p.path for p in got.binder.pages] == [p.path for p in got.pages]
        assert got.paragraphs == [b for p in got.pages for b in flow.carried(p)]
        assert got.binder.read_from["revise"] == 0
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
        got = flow.gather(tmp_path, [bad], 0)
        assert got.pages == []
        assert not got.binder.pages
        assert len(got.unreadable) == 1 and "m.py" in got.unreadable[0]

    def test_a_target_that_matched_no_file_is_a_gap(self, tmp_path):
        got = flow.gather(tmp_path, [tmp_path / "nope.py"], 0)
        assert got.unreadable == [
            f"{(tmp_path / 'nope.py').as_posix()} (matched no files)"
        ]

    def test_the_chain_is_data_so_a_step_is_a_list_element(self, tmp_path, monkeypatch):
        """T2's verify. A step appended to `STEPS` runs, on the same `Gathering`,
        after the ones before it -- which is what `references_for` will be."""
        seen = []

        def references_for(g):
            seen.append((g, len(g.paragraphs), hasattr(g, "binder")))

        monkeypatch.setattr(flow, "STEPS", (*flow.STEPS, references_for))
        got = flow.gather(a_small_real_tree(tmp_path), [tmp_path / "repo"], 0)
        assert seen == [(got, len(got.paragraphs), True)]
        assert got.paragraphs, "the step ran over nothing"
