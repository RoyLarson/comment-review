"""`flows/page_for.py`: the read-and-build step, and the refusals its own
docstring promises.

Moved from `tests/test_proof_setter.py` 2026-08-26, where sitting in the write
chain's own file credited `proof_setter` with a contract that is `page_for`'s.
"""

from pathlib import Path

from conftest import PKG, SAMPLE, build

from comment_review.binder.binder import bind, rows_of
from comment_review.flows import page_for as page_for_mod
from comment_review.flows import proof_setter
from comment_review.machine import exceptions


def address(binder, path: str, series: str = "b") -> str:
    """One address off the binder, in the FORM THE BINDER PUBLISHES.

    !! EVERY TEST HERE HAND-WROTE `f"{rel}@{cue}"` UNTIL 2026-08-25, and that
    is what hid the CRITICAL defect: an address carries the FLATTENED path --
    `pkg:a:util.py` -- and a hand-written one carries `/`. `by_page` splits
    whatever it is handed, so the tests fed the chain a form nothing produces
    and only repo-root files, whose flattened form is their path, agreed. The
    fixture could not disagree with the code because the fixture was written to
    match it.

    ! IT ASKS `rows_of`, which is what a caller of this chain has.
    """
    for row in rows_of(binder):
        if (
            row["path"] == path
            and row["cue"].startswith(series)
            and row["raw_text"].strip()
        ):
            return str(row["address"])
    raise AssertionError(f"no filled {series} row for {path}")


def _tree(tmp_path):
    """A one-file repo, and the binder taken over it."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page = build(SAMPLE)
    return repo, bind([page]), page


class TestPageOfReturnsEveryRefusalItPromises:
    """`page_of`'s docstring promises `(page, "")` or `(None, reason)`.

    IMPORTANT, measured 2026-08-25: it caught only `exceptions.READ_ERRORS`
    while `page_for` also raises `exceptions.Refused`, so such a file took
    `proof_setter.run` down with a raw traceback. All five inline sites this
    function consolidates handle it -- `results/compositor.py` catches
    `Refused`, `commands/census.py` catches a bare `Exception`."""

    def test_page_for_DOES_raise_Refused(self):
        """! The handler below is not written for a hypothetical. This reads
        the raise sites out of the module rather than asserting they exist."""
        text = (PKG / "binder" / "page.py").read_text(encoding="utf-8")
        assert text.count("raise exceptions.Refused") == 2

    def test_a_Refused_comes_back_as_a_REASON(self, tmp_path, monkeypatch):
        def refusing_page_for(*args, **kwargs):
            raise exceptions.Refused("b0: a `c` place whose anchor has no line")

        monkeypatch.setattr(page_for_mod, "page_for", refusing_page_for)
        path = tmp_path / "m.py"
        path.write_text(SAMPLE, encoding="utf-8", newline="")

        page, why = page_for_mod.page_of(path, rel="m.py")
        assert page is None
        assert "anchor has no line" in why

    def test_a_Refused_REFUSES_THE_RUN_instead_of_escaping(self, tmp_path, monkeypatch):
        """! THE PATCH REACHES `_one`'s READ ONLY, because the run stops there.
        `_reread`'s own read is the case below."""
        repo, binder, _ = _tree(tmp_path)

        def refusing_page_for(*args, **kwargs):
            raise exceptions.Refused("b0: a `c` place whose anchor has no line")

        monkeypatch.setattr(page_for_mod, "page_for", refusing_page_for)
        drafted, refused = proof_setter.run(
            {address(binder, "m.py"): "# REPLACED"}, binder, repo, tmp_path / "out"
        )
        assert drafted == []
        assert refused[0].step == "read"

    def test_a_Refused_ON_THE_DRAFT_refuses_at_reread(self, tmp_path, monkeypatch):
        """CRITICAL, measured 2026-08-26: `_reread` inlined `read_source`,
        `language_for` and `page_for` with NO handler for either
        `exceptions.Refused` or `READ_ERRORS`, so a draft tripping `page_for`'s
        raise escaped `run()` as a traceback -- past its documented
        `(drafted, []) or ([], refusals)`.

        ! THE CASE ABOVE COULD NOT SEE IT: it patches the name `page_of` reads,
        which the inlined copy never consulted, and `_one`'s read refuses first
        anyway. This one refuses the DRAFT alone, so the chain reaches the step
        under test."""
        repo, binder, _ = _tree(tmp_path)
        into = tmp_path / "out"
        real_page_for = page_for_mod.page_for

        def refusing_on_the_draft(path, *args, **kwargs):
            if Path(path).resolve().is_relative_to(into.resolve()):
                raise exceptions.Refused("b0: a `c` place whose anchor has no line")
            return real_page_for(path, *args, **kwargs)

        monkeypatch.setattr(page_for_mod, "page_for", refusing_on_the_draft)
        drafted, refused = proof_setter.run(
            {address(binder, "m.py"): "# REPLACED"}, binder, repo, into
        )
        assert drafted == []
        assert [r.step for r in refused] == ["reread"]
        assert "anchor has no line" in refused[0].why
        assert list(into.iterdir()) == []
