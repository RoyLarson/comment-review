"""The chain from notations to a drafted file a human can read.

! THE ORDER IS DATA. A missing check is then a missing element rather than a
forgotten call -- which is the one failure a runner that hard-codes its
sequence cannot show you.
"""

from pathlib import Path

import pytest
from conftest import PKG, SAMPLE, SRC, build, by_cue

from comment_review.binder.binder import bind, rows_of
from comment_review.flows import page_for as page_for_mod
from comment_review.flows import proof_setter
from comment_review.machine import exceptions
from comment_review.reading.addresser import cue_of
from comment_review.results import compositor, galley
from comment_review.results.prove_unchanged import code_fingerprint


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


def test_the_chain_IS_this_list():
    assert proof_setter.STEPS == (
        "read",
        "verify",
        "edit",
        "set",
        "draft",
        "reread",
        "prove",
    )


def _tree(tmp_path):
    """A one-file repo, and the binder taken over it."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page = build(SAMPLE)
    return repo, bind([page]), page


def test_a_notation_reaches_a_drafted_file(tmp_path):
    repo, binder, _ = _tree(tmp_path)
    into = tmp_path / "out"
    drafted, refused = proof_setter.run(
        {address(binder, "m.py"): "# REPLACED"}, binder, repo, into
    )
    assert refused == []
    assert len(drafted) == 1
    assert "# REPLACED" in drafted[0].draft.read_text(encoding="utf-8")


def test_a_file_BELOW_THE_REPO_ROOT_drafts(tmp_path):
    """CRITICAL, measured 2026-08-25: `by_page` keys by the FLATTENED path an
    address carries, and `run` used that string both as a binder key and as a
    filesystem path -- so `pkg/a/util.py` was looked up as `pkg:a:util.py`,
    missed the binder, and was handed to `page_of` as `repo/pkg:a:util.py`,
    which is invalid on Windows and missing on POSIX. EVERY notation on a file
    below the repo root refused at step `read`; only repo-root files, whose
    flattened form equals their path, worked."""
    repo = tmp_path / "repo"
    (repo / "pkg" / "a").mkdir(parents=True)
    (repo / "pkg" / "a" / "util.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = bind([build(SAMPLE, "pkg/a/util.py")])

    where = address(binder, "pkg/a/util.py")
    assert where.startswith("pkg:a:util.py@")

    into = tmp_path / "out"
    drafted, refused = proof_setter.run({where: "# REPLACED"}, binder, repo, into)
    assert refused == []
    assert [d.path for d in drafted] == ["pkg/a/util.py"]
    assert "# REPLACED" in drafted[0].draft.read_text(encoding="utf-8")
    assert drafted[0].draft == into / "pkg" / "a" / "util.py"


def test_an_address_NAMING_NO_PAGE_IN_THE_BINDER_refuses_at_read(tmp_path):
    """`unflatten` answers "" for a name no page carries and for one several
    carry. "" is not a path -- handing it on asks the filesystem for the repo
    root itself."""
    repo, binder, _ = _tree(tmp_path)
    drafted, refused = proof_setter.run(
        {"pkg:nowhere.py@b0": "# x"}, binder, repo, tmp_path / "out"
    )
    assert drafted == []
    assert len(refused) == 1
    assert refused[0].step == "read"
    assert "pkg:nowhere.py@b0" in refused[0].why


def test_nothing_under_the_repo_is_touched(tmp_path):
    repo, binder, _ = _tree(tmp_path)
    before = (repo / "m.py").read_bytes()
    proof_setter.run(
        {address(binder, "m.py"): "# REPLACED"}, binder, repo, tmp_path / "out"
    )
    assert (repo / "m.py").read_bytes() == before


def test_a_RELATIVE_into_does_not_refuse_every_page(tmp_path, monkeypatch):
    """CRITICAL, measured 2026-08-25: `_one` compared `(into / rel).resolve()`
    -- absolute -- against an UNRESOLVED `into`, so with `into =
    Path("out_rel")` every page refused at step `draft` with "would be written
    outside the draft directory". `commands/proof.py` resolves before calling,
    which hid it; `run` is a flow anyone may call and its docstring said only
    "Created if absent"."""
    repo, binder, _ = _tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    drafted, refused = proof_setter.run(
        {address(binder, "m.py"): "# REPLACED"}, binder, repo, Path("out_rel")
    )
    assert refused == []
    assert len(drafted) == 1
    assert (tmp_path / "out_rel" / "m.py").exists()


def test_a_refusal_NAMES_ITS_STEP(tmp_path):
    repo, binder, _ = _tree(tmp_path)
    _, refused = proof_setter.run({"m.py@b99": "# x"}, binder, repo, tmp_path / "out")
    assert refused and refused[0].step in proof_setter.STEPS


def test_ONE_FILES_REFUSAL_DRAFTS_NOTHING_FOR_ANY_FILE(tmp_path):
    """Abort-whole: a good page in the same run gets no draft either."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    (repo / "n.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page_m = build(SAMPLE, "m.py")
    page_n = build(SAMPLE, "n.py")
    binder = bind([page_m, page_n])
    into = tmp_path / "out"
    notations = {address(binder, "m.py"): "# REPLACED", "n.py@b99": "# bad"}
    drafted, refused = proof_setter.run(notations, binder, repo, into)
    assert drafted == []
    assert len(refused) == 1
    assert refused[0].path == "n.py"
    assert list(into.iterdir()) == []


def test_TWO_PAGES_SHARING_A_BASENAME_do_not_collide(tmp_path):
    """CRITICAL, measured 2026-08-25: `into / Path(rel).name` flattened
    `pkg/a/util.py` and `pkg/b/util.py` to the same `<into>/util.py`, so the
    second page's draft silently overwrote the first's -- a human reviewing
    `pkg/a/util.py`'s approved text would have read `pkg/b`'s instead, at
    exit 0. `commands/galley.py:124` keeps the repo-relative path under its
    output directory; this pins the same shape here."""
    repo = tmp_path / "repo"
    (repo / "pkg" / "a").mkdir(parents=True)
    (repo / "pkg" / "b").mkdir(parents=True)
    (repo / "pkg" / "a" / "util.py").write_text(SAMPLE, encoding="utf-8", newline="")
    (repo / "pkg" / "b" / "util.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = bind([build(SAMPLE, "pkg/a/util.py"), build(SAMPLE, "pkg/b/util.py")])
    into = tmp_path / "out"
    notations = {
        address(binder, "pkg/a/util.py"): "# FROM A",
        address(binder, "pkg/b/util.py"): "# FROM B",
    }
    drafted, refused = proof_setter.run(notations, binder, repo, into)
    assert refused == []
    assert len(drafted) == 2
    by_path = {d.path: d for d in drafted}
    assert by_path["pkg/a/util.py"].draft != by_path["pkg/b/util.py"].draft
    assert "# FROM A" in by_path["pkg/a/util.py"].draft.read_text(encoding="utf-8")
    assert "# FROM B" in by_path["pkg/b/util.py"].draft.read_text(encoding="utf-8")


def test_a_rel_that_ESCAPES_into_is_REFUSED(tmp_path):
    """CRITICAL, measured 2026-08-25: `(into / rel).resolve()` joins and never
    checks -- with `rel = "../escape_repo/sub/util.py"` and a matching sha,
    the join lands outside `into` entirely, up to and including the source
    file under review. `commands/galley.py:124` already refuses this shape
    for `--out`; this pins the same guard here."""
    repo = tmp_path / "repo"
    repo.mkdir()
    escaped = tmp_path / "escape_repo" / "sub"
    escaped.mkdir(parents=True)
    escaped_file = escaped / "util.py"
    escaped_file.write_text(SAMPLE, encoding="utf-8", newline="")
    before = escaped_file.read_bytes()

    rel = "../escape_repo/sub/util.py"
    binder = bind([build(SAMPLE, rel)])
    into = tmp_path / "out"

    drafted, refused = proof_setter.run(
        {address(binder, rel): "# REPLACED"}, binder, repo, into
    )

    assert drafted == []
    assert len(refused) == 1
    assert refused[0].step == "draft"
    assert escaped_file.read_bytes() == before


def test_an_EXCEPTION_removes_earlier_drafts_and_still_propagates(
    tmp_path, monkeypatch
):
    """CRITICAL, measured 2026-08-25: with `out/beta.py` pre-occupied, a
    `PermissionError` from `write_text` escaped `run()` as a raw traceback
    and `out/alpha.py` was left behind -- the cleanup below only ran on the
    `refusals` branch, never on an exception. The docstring's claim ("Every
    draft this run wrote is removed") must hold for either kind of stop."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    (repo / "n.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = bind([build(SAMPLE, "m.py"), build(SAMPLE, "n.py")])
    into = tmp_path / "out"

    real_write_text = Path.write_text

    def failing_write_text(self, *args, **kwargs):
        if self.name == "n.py":
            raise PermissionError("simulated: target pre-occupied")
        return real_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", failing_write_text)

    # "m.py" sorts before "n.py", so it drafts first and succeeds before the
    # second page's write raises.
    notations = {
        address(binder, "m.py"): "# REPLACED",
        address(binder, "n.py"): "# REPLACED",
    }
    with pytest.raises(PermissionError):
        proof_setter.run(notations, binder, repo, into)

    assert list(into.iterdir()) == []


def test_an_EXCEPTION_AFTER_THE_WRITE_removes_the_draft_that_raised(
    tmp_path, monkeypatch
):
    """IMPORTANT, measured 2026-08-25: `run`'s cleanup unlinks what is in
    `drafted`, and the page being written is not in it yet. `_one` writes the
    target and THEN calls `_reread` and `_prove`; a raise from either left
    `<into>/<rel>` on disk while `run`'s docstring said every draft this run
    wrote is removed. The existing regression test exercises only `write_text`
    itself failing -- the one case where nothing was written."""
    repo, binder, _ = _tree(tmp_path)
    into = tmp_path / "out"

    def failing_reread(*args, **kwargs):
        raise RuntimeError("simulated: a step past the write raised")

    monkeypatch.setattr(proof_setter, "_reread", failing_reread)

    with pytest.raises(RuntimeError):
        proof_setter.run({address(binder, "m.py"): "# REPLACED"}, binder, repo, into)

    assert list(into.rglob("*.py")) == []


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
        repo, binder, _ = _tree(tmp_path)

        def refusing_page_for(*args, **kwargs):
            raise exceptions.Refused("b0: a `c` place whose anchor has no line")

        monkeypatch.setattr(page_for_mod, "page_for", refusing_page_for)
        drafted, refused = proof_setter.run(
            {address(binder, "m.py"): "# REPLACED"}, binder, repo, tmp_path / "out"
        )
        assert drafted == []
        assert refused[0].step == "read"


class TestTheFileMustBeTheONEThatWasReviewed:
    """!! THE CHECK THE READ-ONLY ROLES HAVE NEVER HAD. No agent file declares
    `tools:`, so all six inherit Edit and Write -- read-only is prose. This is
    what catches a reviewer that edited the file it was reading.
    See TODO/reviewers-are-not-read-only.md."""

    def test_a_ONE_BYTE_edit_since_the_binder_refuses(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        (repo / "m.py").write_text(SAMPLE + "\n", encoding="utf-8", newline="")
        drafted, refused = proof_setter.run(
            {address(binder, "m.py"): "# REPLACED"}, binder, repo, tmp_path / "out"
        )
        assert drafted == []
        assert refused[0].step == "verify"

    def test_NO_DRAFT_is_written_when_the_sha_disagrees(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        (repo / "m.py").write_text(SAMPLE + "\n", encoding="utf-8", newline="")
        into = tmp_path / "out"
        proof_setter.run({address(binder, "m.py"): "# REPLACED"}, binder, repo, into)
        assert list(into.iterdir()) == []

    def test_an_UNCHANGED_file_passes(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        drafted, refused = proof_setter.run(
            {address(binder, "m.py"): "# REPLACED"}, binder, repo, tmp_path / "out"
        )
        assert refused == [] and len(drafted) == 1


def test_the_drafted_FILE_holds_each_notation_at_its_cue(tmp_path):
    repo, binder, _ = _tree(tmp_path)
    where = address(binder, "m.py")
    drafted, refused = proof_setter.run(
        {where: "# REPLACED"}, binder, repo, tmp_path / "out"
    )
    assert refused == []
    again = build(drafted[0].draft.read_text(encoding="utf-8"))
    assert by_cue(again)[cue_of(where).cue].raw_lines == ["# REPLACED"]


class TestOnlyCommentsChange:
    """Roy, 2026-08-25: prove_unchanged runs *"just before the human review and
    just after the human review edit piece just to be certain we only changed
    only comments."* This is the first of those two.

    ! `_prove` IS TESTED DIRECTLY BELOW, NOT THROUGH `run()`. For Python's
    AST tier, `_reread` already requires exact `raw_lines` equality at every
    edited cue, so any notation that survives it was -- by construction --
    read back as a comment, and a comment never enters the AST. No `b`, `a`
    or `c` cue notation reaching `proof_setter.run()` on this module's own
    `SAMPLE` fixture can therefore make `_prove`'s comparison disagree; every
    attempt (a raw code line dropped where a comment gap was, on several
    cues) was refused by `_reread` first -- measured, not assumed. The real
    hazard `_prove` guards is `TODO/closing-line-deletes-code.md`: a comment
    whose run closes mid-line, or never closes at all, can swallow the code
    that follows it -- code beyond the cue `_reread` was asked about, which
    is exactly what `_reread` cannot see.
    """

    def test_an_ordinary_comment_change_PASSES(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        drafted, refused = proof_setter.run(
            {address(binder, "m.py"): "# still a comment"},
            binder,
            repo,
            tmp_path / "out",
        )
        assert refused == [] and len(drafted) == 1

    def test_a_comment_run_that_swallows_code_is_caught_by_prove(self):
        """A one-line C block comment, replaced with an opener that never
        closes: the composed file's comment run swallows the code line
        after it -- `TODO/closing-line-deletes-code.md`, measured on this
        exact shape."""
        before = "int a = 1;\n/* note */\nint b = 2;\n"
        page = build(before, "m.c")
        cue = next(c for c, b in by_cue(page).items() if b.raw_lines == ["/* note */"])
        galley.reset(page, {cue: "/* note"})
        after = compositor.set_page(page)
        assert after == "int a = 1;\n/* note\nint b = 2;\n"

        refused = proof_setter._prove("m.c", before, after, Path("m.c"))
        assert refused is not None
        assert refused.step == "prove"

    def test_TWO_UNPROVABLE_files_are_not_reported_identical(self):
        """The hazard named at the top of `code_fingerprint`'s own docstring:
        an unprovable file's fingerprint is the empty string, and two empty
        strings compare equal. These two files hold different code and are
        each unprovable for a different reason -- an all-comment file with no
        code at all, and one whose comment never closes -- so a `_prove` that
        compared `want != got` without reading `kind` first would report them
        IDENTICAL."""
        before = "// just a comment\n"
        after = "int y = 999; /* oops\n"
        assert code_fingerprint(before, Path("m.c")) == ("unprovable", "")
        assert code_fingerprint(after, Path("m.c")) == ("unprovable", "")

        refused = proof_setter._prove("m.c", before, after, Path("m.c"))
        assert refused is not None
        assert refused.step == "prove"


class TestTheCommand:
    """`commands/proof.py` exposes this flow and orchestrates nothing --
    `commands/galley.py` resolves an address through `rows_of(census)`, the
    binder-row coupling this chain was ruled out of; `proof.py` takes a
    binder and hands it straight to `proof_setter.run`."""

    def test_the_command_holds_no_orchestration(self):
        """! A COMMAND EXPOSES A FLOW; IT IS NOT ONE. `commands/census.py` took
        446 lines calling page_for directly while flows/census.py kept 261 of
        helpers. See TODO/the-flow-lives-in-the-command.md."""
        text = (SRC / "comment_review" / "commands" / "proof.py").read_text(
            encoding="utf-8"
        )
        for forbidden in ("page_for", "galley.reset", "set_page", "code_fingerprint"):
            assert forbidden not in text

    def test_proof_is_a_named_command(self):
        from comment_review.__main__ import COMMANDS

        assert "proof" in COMMANDS

    def test_an_out_that_overlaps_the_repo_is_REFUSED(
        self, tmp_path, capsys, monkeypatch
    ):
        """!! THE DESTRUCTIVE CASE, MEASURED 2026-08-22 on the galley: on an
        overlap the per-file guard is satisfied by the SOURCE FILE ITSELF, so
        the draft was written over the file under review at exit 0."""
        from comment_review.commands import proof as cmd

        repo, _, _ = _tree(tmp_path)
        monkeypatch.setattr(
            "sys.argv",
            [
                "proof",
                "--repo",
                str(repo),
                "--binder",
                "b.json",
                "--notations",
                "n.json",
                "--out",
                str(repo / "inside"),
            ],
        )
        assert cmd.main() == 2
        assert "REFUSED" in capsys.readouterr().out
