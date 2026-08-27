"""The chain from alterations to a drafted file a human can read.

! THE ORDER IS DATA. A missing check is then a missing element rather than a
forgotten call -- which is the one failure a runner that hard-codes its
sequence cannot show you.
"""

from pathlib import Path

import pytest
from conftest import PKG, SAMPLE, build, by_cue, docket_from

from comment_review.binder.binder import bind, rows_of
from comment_review.flows import page_for as page_for_mod
from comment_review.flows import proof_setter
from comment_review.machine.repo import undraftable
from comment_review.reading.addresser import cue_of
from comment_review.results import compositor, galley
from comment_review.results.prove_unchanged import code_fingerprint

#: A replacement that is legal in each series -- a `c` carries its own
#: separator, an `a` its indentation. Same table as `tests/test_galley.py`,
#: which is where the shapes were derived from the compositor.
ADDED = {
    "a": '    """ADDED."""',
    "b": "# ADDED",
    "c": "  # ADDED",
    "f": "#!/usr/bin/env ADDED",
}


def _split(text: str) -> tuple[set[str], set[str]]:
    """`(filled, absent)` -- every cue on this page, by whether it holds prose.

    ! DISCOVERED, NOT LISTED, so a series that stops being reachable through
    the chain fails the cases below whichever series it turns out to be. A
    hand-written list would have to be remembered when the page model moves,
    which is the way every case above `TestEveryVerdict...` came to edit one
    filled `b` and nothing else.
    """
    filled, absent = set(), set()
    for where, paragraph in by_cue(build(text)).items():
        held = any(line.strip() for line in paragraph.raw_lines)
        (filled if held else absent).add(where)
    return filled, absent


FILLED, ABSENT = _split(SAMPLE)

#: The docstring series. It is held out of the two cases below because a
#: docstring `add` or `drop` is STILL REFUSED at `prove` and that is a ruling
#: Roy holds -- `TODO/the-code-check-refuses-add-and-drop-on-a-docstring.md`,
#: task T1. The two cases that pin what happens today are named for it.
DOCSTRING = {c for c in FILLED | ABSENT if c.startswith("a")}


def address(binder, path: str, series: str = "b") -> str:
    """One address off the binder, in the FORM THE BINDER PUBLISHES.

    !! EVERY TEST HERE HAND-WROTE `f"{rel}@{cue}"` UNTIL 2026-08-25, and that
    is what hid the CRITICAL defect: an address carries the FLATTENED path --
    `pkg:a:util.py` -- and a hand-written one carries `/`. `schedules_of` splits
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


def test_a_alteration_reaches_a_drafted_file(tmp_path):
    repo, binder, _ = _tree(tmp_path)
    into = tmp_path / "out"
    drafted, refused = proof_setter.run(
        docket_from({address(binder, "m.py"): "# REPLACED"}, binder), repo, into
    )
    assert refused == []
    assert len(drafted) == 1
    assert "# REPLACED" in drafted[0].draft.read_text(encoding="utf-8")


def test_a_file_BELOW_THE_REPO_ROOT_drafts(tmp_path):
    """CRITICAL, measured 2026-08-25: `schedules_of` keys by the FLATTENED path an
    address carries, and `run` used that string both as a binder key and as a
    filesystem path -- so `pkg/a/util.py` was looked up as `pkg:a:util.py`,
    missed the binder, and was handed to `page_of` as `repo/pkg:a:util.py`,
    which is invalid on Windows and missing on POSIX. EVERY alteration on a file
    below the repo root refused at step `read`; only repo-root files, whose
    flattened form equals their path, worked."""
    repo = tmp_path / "repo"
    (repo / "pkg" / "a").mkdir(parents=True)
    (repo / "pkg" / "a" / "util.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = bind([build(SAMPLE, "pkg/a/util.py")])

    where = address(binder, "pkg/a/util.py")
    assert where.startswith("pkg:a:util.py@")

    into = tmp_path / "out"
    drafted, refused = proof_setter.run(
        docket_from({where: "# REPLACED"}, binder), repo, into
    )
    assert refused == []
    assert [d.path for d in drafted] == ["pkg/a/util.py"]
    assert "# REPLACED" in drafted[0].draft.read_text(encoding="utf-8")
    assert drafted[0].draft == into / "pkg" / "a" / "util.py"


def test_a_page_the_REPO_DOES_NOT_HAVE_refuses_at_read_and_names_it(tmp_path):
    """!! THIS ASKED A DIFFERENT QUESTION UNTIL 2026-08-26, and the question
    stopped existing. It was `..._NAMING_NO_PAGE_IN_THE_BINDER`: an address
    carries a FLATTENED path, `run` called `unflatten` over the binder's page
    paths to recover a real one, and `""` came back for a name no page carried
    OR that several carried. `""` is not a path -- handing it on asks the
    filesystem for the repo root itself -- so `run` refused it by name.

    ! A SCHEDULE STATES ITS PATH, so there is nothing to resolve and no
    ambiguity to refuse. What remains is the ordinary case: the docket names a
    page the checkout does not have, and the read step says so with the path in
    the reason.
    """
    repo, _, _ = _tree(tmp_path)
    docket = {
        "pages": [
            {
                "path": "pkg/nowhere.py",
                "sha": "whatever",
                "alterations": [{"cue": "b0", "text": "# x"}],
            }
        ]
    }
    drafted, refused = proof_setter.run(docket, repo, tmp_path / "out")
    assert drafted == []
    assert len(refused) == 1
    assert refused[0].step == "read"
    assert refused[0].path == "pkg/nowhere.py"


def test_nothing_under_the_repo_is_touched(tmp_path):
    repo, binder, _ = _tree(tmp_path)
    before = (repo / "m.py").read_bytes()
    proof_setter.run(
        docket_from({address(binder, "m.py"): "# REPLACED"}, binder),
        repo,
        tmp_path / "out",
    )
    assert (repo / "m.py").read_bytes() == before


class TestTheFlowItselfRefusesADraftDirectoryOverTheRepo:
    """!! DESTRUCTIVE, MEASURED 2026-08-25: `run(alterations, binder, repo, repo)`
    answered `refused=[]` and the SOURCE FILE on disk held `# OVERWRITTEN`.
    `_one`'s containment check passes when `into == repo`, because the source
    file IS inside `into`. The disjointness guard existed only in the two
    COMMANDS, and `run` is a flow this module's own docstring says anyone may
    call -- the same reasoning already applied on this branch to
    `into.resolve()`."""

    def test_into_EQUAL_TO_the_repo_refuses(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        drafted, refused = proof_setter.run(
            docket_from({address(binder, "m.py"): "# OVERWRITTEN"}, binder), repo, repo
        )
        assert drafted == []
        assert len(refused) == 1
        assert refused[0].step == "draft"
        assert "overlaps" in refused[0].why

    def test_the_SOURCE_FILE_is_byte_identical_afterwards(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        before = (repo / "m.py").read_bytes()
        proof_setter.run(
            docket_from({address(binder, "m.py"): "# OVERWRITTEN"}, binder), repo, repo
        )
        assert (repo / "m.py").read_bytes() == before

    def test_into_INSIDE_the_repo_refuses(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        drafted, refused = proof_setter.run(
            docket_from({address(binder, "m.py"): "# x"}, binder), repo, repo / "drafts"
        )
        assert drafted == []
        assert refused and refused[0].step == "draft"
        assert not (repo / "drafts").exists()

    def test_the_repo_INSIDE_into_refuses(self, tmp_path):
        """The other direction. `is_relative_to` is asked both ways because a
        draft directory ABOVE the repo holds it just as destructively."""
        repo, binder, _ = _tree(tmp_path)
        drafted, refused = proof_setter.run(
            docket_from({address(binder, "m.py"): "# x"}, binder), repo, tmp_path
        )
        assert drafted == []
        assert refused and refused[0].step == "draft"

    def test_the_RULE_IS_ONE_FUNCTION_both_callers_ask(self):
        """! A rule lives in exactly one file -- `docs/conventions.md`. It used
        to be written out in `commands/proof.py` AND `commands/galley.py`, with
        the same `is_relative_to` note on each, and asked in the flow nowhere.

        ! `repo.is_relative_to(` is the half NO OTHER GUARD NEEDS: the per-file
        guard asks whether a path derived from a root is still under that root,
        and only DISJOINTNESS asks the repo about the draft directory. The
        command holds no other comparison against `repo` at all, so the
        stricter form still stands there.

        ! IT WAS THREE CALLERS UNTIL 2026-08-26, WHEN `commands/galley.py` WAS
        DELETED. `galley` is now an alias in `__main__.ALIASES` that dispatches
        straight to `proof`'s own module, so it holds no chain and asks nothing
        -- `test_galley_DELEGATES_to_proof` in `tests/test_proof_command.py` is
        what pins that."""
        for rel in ("commands/proof.py", "flows/proof_setter.py"):
            text = (PKG / rel).read_text(encoding="utf-8")
            assert "undraftable(" in text, rel
            assert "repo.is_relative_to(" not in text, rel
        text = (PKG / "commands" / "proof.py").read_text(encoding="utf-8")
        assert "is_relative_to(repo)" not in text


def test_a_DANGLING_SYMLINK_is_not_a_directory(tmp_path):
    """`exists()` FOLLOWS the link, so a link naming nothing answers `False` and
    passed the clause that exists to stop a non-directory -- then
    `into.mkdir(exist_ok=True)`, which does NOT follow a link, raises the same
    `FileExistsError` to the console the clause was added for.

    ! IT SKIPS WHERE SYMLINKS ARE NOT AVAILABLE rather than faking the
    filesystem the case is entirely about: creating one on the machine this was
    written on raises `WinError 1314`."""
    link = tmp_path / "link"
    try:
        link.symlink_to(tmp_path / "nowhere", target_is_directory=True)
    except OSError as e:
        pytest.skip(f"symlinks unavailable: {e}")
    assert not link.exists()
    assert undraftable(link, tmp_path / "repo")


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
        docket_from({address(binder, "m.py"): "# REPLACED"}, binder),
        repo,
        Path("out_rel"),
    )
    assert refused == []
    assert len(drafted) == 1
    assert (tmp_path / "out_rel" / "m.py").exists()


def test_a_refusal_NAMES_ITS_STEP(tmp_path):
    repo, binder, _ = _tree(tmp_path)
    _, refused = proof_setter.run(
        docket_from({"m.py@b99": "# x"}, binder), repo, tmp_path / "out"
    )
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
    alterations = {address(binder, "m.py"): "# REPLACED", "n.py@b99": "# bad"}
    drafted, refused = proof_setter.run(docket_from(alterations, binder), repo, into)
    assert drafted == []
    assert len(refused) == 1
    assert refused[0].path == "n.py"
    assert list(into.iterdir()) == []


def _two_pages(tmp_path):
    """A two-file repo whose FIRST page in sort order is already stale."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "a.py").write_text(SAMPLE, encoding="utf-8", newline="")
    (repo / "z.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = bind([build(SAMPLE, "a.py"), build(SAMPLE, "z.py")])
    # ! Stale AFTER the binder was taken, so `a.py` refuses at `verify`.
    (repo / "a.py").write_text(SAMPLE + "\n", encoding="utf-8", newline="")
    alterations = {
        address(binder, "a.py"): "# REPLACED",
        address(binder, "z.py"): "# REPLACED",
    }
    return repo, binder, alterations


def test_NO_LATER_PAGE_IS_READ_once_an_earlier_one_refuses(tmp_path, monkeypatch):
    """CRITICAL, measured 2026-08-26: `run` recorded the refusal and CARRIED ON
    -- reading, editing, drafting, rereading and proving every remaining page --
    against its own docstring's *"A REFUSAL ABORTS THE RUN WHOLE"* and Roy's
    ruling that it *"fails loud amd stops"*.

    ! IT WATCHES `source_of`, WHICH IS THE READ. It watched `page_of` until the
    sha comparison moved above the parse on 2026-08-26; from then on the stale
    first page refuses before anything is paged, so watching the parse would
    have measured `[]` for both pages and could no longer tell the two apart."""
    repo, binder, alterations = _two_pages(tmp_path)
    into = tmp_path / "out"

    read: list[str] = []
    real_source_of = proof_setter.source_of

    def watching_source_of(path, *args, **kwargs):
        read.append(Path(path).name)
        return real_source_of(path, *args, **kwargs)

    monkeypatch.setattr(proof_setter, "source_of", watching_source_of)
    drafted, refused = proof_setter.run(docket_from(alterations, binder), repo, into)

    assert drafted == []
    assert [r.step for r in refused] == ["verify"]
    assert read == ["a.py"]
    assert list(into.iterdir()) == []


def test_A_STALE_FILE_IS_REFUSED_WITHOUT_BEING_PARSED(tmp_path, monkeypatch):
    """The sha comparison sat BELOW `page_of` until 2026-08-26, so every stale
    page was read, lexed and paged before the one comparison that was going to
    refuse it. `source_of` supplies the sha, so nothing has to be parsed to ask
    the question.

    ! IT ALSO DECIDES WHICH REASON A STALE AND UNPAGEABLE FILE GETS. With the
    order reversed the refusal said `has no page`, which is a consequence of the
    change the run is refusing FOR."""
    repo, binder, alterations = _two_pages(tmp_path)

    def unpageable(*args, **kwargs):
        raise AssertionError("a stale page must not be parsed")

    monkeypatch.setattr(proof_setter, "page_of", unpageable)
    drafted, refused = proof_setter.run(
        docket_from(alterations, binder), repo, tmp_path / "out"
    )

    assert drafted == []
    assert [(r.step, r.path) for r in refused] == [("verify", "a.py")]
    assert "changed since it was reviewed" in refused[0].why


def test_A_REFUSAL_IS_NOT_LOST_to_a_later_page_that_raises(tmp_path, monkeypatch):
    """CRITICAL, measured 2026-08-26: `run` collected the refusal, went on to
    the next page, and that page's write raised -- so `run` re-raised and the
    caller got a traceback INSTEAD of the refusals, past the documented
    `(drafted, []) or ([], refusals)`."""
    repo, binder, alterations = _two_pages(tmp_path)
    into = tmp_path / "out"
    real_write_text = Path.write_text

    def failing_write_text(self, *args, **kwargs):
        if self.name == "z.py":
            raise PermissionError("simulated: a later page's write fails")
        return real_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", failing_write_text)

    drafted, refused = proof_setter.run(docket_from(alterations, binder), repo, into)

    assert drafted == []
    assert [(r.step, r.path) for r in refused] == [("verify", "a.py")]


def test_TWO_PAGES_SHARING_A_BASENAME_do_not_collide(tmp_path):
    """CRITICAL, measured 2026-08-25: `into / Path(rel).name` flattened
    `pkg/a/util.py` and `pkg/b/util.py` to the same `<into>/util.py`, so the
    second page's draft silently overwrote the first's -- a human reviewing
    `pkg/a/util.py`'s approved text would have read `pkg/b`'s instead, at
    exit 0. The galley command kept the repo-relative path under its output
    directory and this was mirrored from it; that command was emptied on
    2026-08-26 -- `docs/history.md` -- so this is the only place the shape is
    pinned."""
    repo = tmp_path / "repo"
    (repo / "pkg" / "a").mkdir(parents=True)
    (repo / "pkg" / "b").mkdir(parents=True)
    (repo / "pkg" / "a" / "util.py").write_text(SAMPLE, encoding="utf-8", newline="")
    (repo / "pkg" / "b" / "util.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = bind([build(SAMPLE, "pkg/a/util.py"), build(SAMPLE, "pkg/b/util.py")])
    into = tmp_path / "out"
    alterations = {
        address(binder, "pkg/a/util.py"): "# FROM A",
        address(binder, "pkg/b/util.py"): "# FROM B",
    }
    drafted, refused = proof_setter.run(docket_from(alterations, binder), repo, into)
    assert refused == []
    assert len(drafted) == 2
    by_path = {d.path: d for d in drafted}
    assert by_path["pkg/a/util.py"].draft != by_path["pkg/b/util.py"].draft
    assert "# FROM A" in by_path["pkg/a/util.py"].draft.read_text(encoding="utf-8")
    assert "# FROM B" in by_path["pkg/b/util.py"].draft.read_text(encoding="utf-8")


def test_a_rel_that_ESCAPES_the_repo_is_REFUSED_AT_READ(tmp_path, monkeypatch):
    """CRITICAL, measured 2026-08-26: only the WRITE target was contained. With
    `rel = "../escape_repo/sub/util.py"` the file OUTSIDE the checkout was read,
    lexed, paged and run through `galley.reset` before the draft guard refused
    -- so the refusal blamed the draft location while the fault is a binder
    naming a page outside `repo`, and a file nobody put under review had already
    been read.

    ! IT NAMES THE BINDER PAGE PATH NOW. `run` asks `_can_escape` of every page
    path as it reads the shas, before the loop, so the refusal states the fault
    rather than whichever of the two roots the join happened to leave first."""
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

    read: list[Path] = []
    real_page_of = proof_setter.page_of

    def watching_page_of(path, *args, **kwargs):
        read.append(Path(path))
        return real_page_of(path, *args, **kwargs)

    monkeypatch.setattr(proof_setter, "page_of", watching_page_of)

    drafted, refused = proof_setter.run(
        docket_from({address(binder, rel): "# REPLACED"}, binder), repo, into
    )

    assert drafted == []
    assert len(refused) == 1
    assert refused[0].step == "read"
    assert "not relative to the repository" in refused[0].why
    assert read == []
    assert escaped_file.read_bytes() == before


def test_a_rel_that_RESOLVES_INSIDE_the_repo_but_outside_into_is_REFUSED(tmp_path):
    """CRITICAL, measured 2026-08-25: `(into / rel).resolve()` joins and never
    checks, so with a matching sha the draft lands outside `into` entirely -- up
    to and including the source file under review.

    ! IT IS THE HALF NEITHER PER-FILE GUARD COULD SHARE, and that is why the
    rule moved up. `repo` and `into` are siblings here, so
    `sub/../../repo/util.py` resolves INSIDE `repo` -- a legitimate read -- and
    outside `into`; each guard therefore answered for its own root and neither
    could state the fault. `run` now asks `_can_escape` of the binder page path
    once, which is true of both roots at once, so this refuses at `read` before
    any file is opened."""
    repo = tmp_path / "repo"
    (repo / "sub").mkdir(parents=True)
    source = repo / "util.py"
    source.write_text(SAMPLE, encoding="utf-8", newline="")
    before = source.read_bytes()

    rel = "sub/../../repo/util.py"
    assert (repo / rel).resolve() == source.resolve()
    into = tmp_path / "out"
    assert not (into / rel).resolve().is_relative_to(into)

    binder = bind([build(SAMPLE, rel)])
    drafted, refused = proof_setter.run(
        docket_from({address(binder, rel): "# REPLACED"}, binder), repo, into
    )

    assert drafted == []
    assert len(refused) == 1
    assert refused[0].step == "read"
    assert "not relative to the repository" in refused[0].why
    assert source.read_bytes() == before


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
    alterations = {
        address(binder, "m.py"): "# REPLACED",
        address(binder, "n.py"): "# REPLACED",
    }
    with pytest.raises(PermissionError):
        proof_setter.run(docket_from(alterations, binder), repo, into)

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
        proof_setter.run(
            docket_from({address(binder, "m.py"): "# REPLACED"}, binder), repo, into
        )

    assert list(into.iterdir()) == []


def test_a_refusal_over_a_NESTED_rel_removes_its_directory_too(tmp_path, monkeypatch):
    """CRITICAL, measured 2026-08-25: `compositor.draft`'s
    `target.parent.mkdir(parents=True, ...)` can create directories nested
    under `into` -- `pkg/` for a `rel` of `pkg/d.py` -- that unlinking the
    FILE alone never removes. A refused run over `pkg/d.py` left `<into>/pkg/`
    on disk, against this module's own docstring: "a stopped run leaves no
    half-set of files that no page describes." `_tree`'s flat `m.py` cannot
    show this; only a nested `rel` can, which is why the test above -- pinned
    against `into.rglob("*.py")` -- passed before this defect was fixed."""
    repo = tmp_path / "repo"
    (repo / "pkg").mkdir(parents=True)
    (repo / "pkg" / "d.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = bind([build(SAMPLE, "pkg/d.py")])
    into = tmp_path / "out"

    def failing_reread(*args, **kwargs):
        raise RuntimeError("simulated: a step past the write raised")

    monkeypatch.setattr(proof_setter, "_reread", failing_reread)

    with pytest.raises(RuntimeError):
        proof_setter.run(
            docket_from({address(binder, "pkg/d.py"): "# REPLACED"}, binder), repo, into
        )

    assert list(into.iterdir()) == []


def test_a_REREAD_REFUSAL_over_a_NESTED_rel_removes_its_directory_too(
    tmp_path, monkeypatch
):
    """The same defect, on the `_reread`-REFUSES branch rather than the
    raises branch -- `_one` unlinked `target` there too without removing the
    directory `compositor.draft` made for it."""
    repo = tmp_path / "repo"
    (repo / "pkg").mkdir(parents=True)
    (repo / "pkg" / "d.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = bind([build(SAMPLE, "pkg/d.py")])
    into = tmp_path / "out"

    def refusing_reread(*args, **kwargs):
        return "", proof_setter.Refusal("reread", "pkg/d.py", "simulated mismatch")

    monkeypatch.setattr(proof_setter, "_reread", refusing_reread)

    drafted, refused = proof_setter.run(
        docket_from({address(binder, "pkg/d.py"): "# REPLACED"}, binder), repo, into
    )

    assert drafted == []
    assert refused and refused[0].step == "reread"
    assert list(into.iterdir()) == []


class TestTheFileMustBeTheONEThatWasReviewed:
    """!! THE CHECK THE READ-ONLY ROLES HAVE NEVER HAD. No agent file declares
    `tools:`, so all six inherit Edit and Write -- read-only is prose. This is
    what catches a reviewer that edited the file it was reading.
    See TODO/reviewers-are-not-read-only.md."""

    def test_a_ONE_BYTE_edit_since_the_binder_refuses(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        (repo / "m.py").write_text(SAMPLE + "\n", encoding="utf-8", newline="")
        drafted, refused = proof_setter.run(
            docket_from({address(binder, "m.py"): "# REPLACED"}, binder),
            repo,
            tmp_path / "out",
        )
        assert drafted == []
        assert refused[0].step == "verify"

    def test_NO_DRAFT_is_written_when_the_sha_disagrees(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        (repo / "m.py").write_text(SAMPLE + "\n", encoding="utf-8", newline="")
        into = tmp_path / "out"
        proof_setter.run(
            docket_from({address(binder, "m.py"): "# REPLACED"}, binder), repo, into
        )
        assert list(into.iterdir()) == []

    def test_an_UNCHANGED_file_passes(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        drafted, refused = proof_setter.run(
            docket_from({address(binder, "m.py"): "# REPLACED"}, binder),
            repo,
            tmp_path / "out",
        )
        assert refused == [] and len(drafted) == 1


def test_the_drafted_FILE_holds_each_alteration_at_its_cue(tmp_path):
    repo, binder, _ = _tree(tmp_path)
    where = address(binder, "m.py")
    drafted, refused = proof_setter.run(
        docket_from({where: "# REPLACED"}, binder), repo, tmp_path / "out"
    )
    assert refused == []
    again = build(drafted[0].draft.read_text(encoding="utf-8"))
    assert by_cue(again)[cue_of(where).cue].raw_lines == ["# REPLACED"]


class TestEveryVerdictThePlacesCanEXPRESSGetsThroughTheChain:
    """!! `drop` AND `add` ARE TWO OF SKILL.md's SEVEN VERDICTS, and the chain
    refused both over whole series. Nothing above could see it: every test here
    edited one FILLED `b`, which is the one shape that always worked.

    ! The two cases are discovered from the page rather than listed, so a
    series that stops being reachable fails here whichever series it is."""

    def _run(self, tmp_path, alterations):
        repo, binder, _ = _tree(tmp_path)
        return proof_setter.run(
            docket_from(alterations, binder), repo, tmp_path / "out"
        )

    def test_the_sample_offers_a_filled_and_an_absent_place_in_every_series(self):
        page = build(SAMPLE)
        for series in "abcf":
            of = {c: b for c, b in by_cue(page).items() if c.startswith(series)}
            assert any(any(line.strip() for line in b.raw_lines) for b in of.values())
            assert any(
                not any(line.strip() for line in b.raw_lines) for b in of.values()
            )

    @pytest.mark.parametrize("where", sorted(FILLED - DOCSTRING))
    def test_a_DROP_reaches_a_draft_at_every_filled_place(self, tmp_path, where):
        """CRITICAL, measured 2026-08-25: `page.empty_places` stores a margin's
        prose as `[lines[n - 1][len(code):]]`, which is `['']` when nothing
        sits beside the code, while `_reread` built `want = []` and compared
        exactly. `c0`, `c1` and `c2` each refused with `Refusal('reread', ...,
        "c1: holds [''], was given []")` -- the galley, the compositor and the
        draft on disk all correct, and the draft then discarded."""
        drafted, refused = self._run(tmp_path, {f"m.py@{where}": None})
        assert refused == []
        assert len(drafted) == 1
        again = build(drafted[0].draft.read_text(encoding="utf-8"))
        assert not any(line.strip() for line in by_cue(again)[where].raw_lines)

    # ! `b4` WAS EXCLUDED HERE UNTIL 2026-08-26, because the closing gap and the
    # back matter shared the foot of the file. The trailing leading separates
    # them, so the matrix is every absent place again.
    @pytest.mark.parametrize("where", sorted(ABSENT - DOCSTRING))
    def test_an_ADD_reaches_a_draft_at_every_absent_place(self, tmp_path, where):
        drafted, refused = self._run(tmp_path, {f"m.py@{where}": ADDED[where[0]]})
        assert refused == []
        assert len(drafted) == 1
        again = build(drafted[0].draft.read_text(encoding="utf-8"))
        assert by_cue(again)[where].raw_lines == [ADDED[where[0]]]

    def test_a_comment_at_the_FOOT_of_a_file_is_reachable_as_f1(self, tmp_path):
        """The capability finding 5 says is impossible IS reachable -- at `f1`,
        which is the back matter, not at `b4`, which is the closing gap. The
        two are emitted at the SAME `<eof>` trigger; `addresser.cue` says so
        in its own comment."""
        drafted, refused = self._run(tmp_path, {"m.py@f1": "# ADDED"})
        assert refused == []
        assert drafted[0].draft.read_text(encoding="utf-8").endswith("# ADDED\n")

    def test_b4_AND_f1_NO_LONGER_COMPOSE_THE_SAME_BYTES(self):
        """!! THEY DID UNTIL 2026-08-26, and that was the whole collision: the
        galley and the compositor were not what refused `b4` -- the draft it
        produced was byte-for-byte the draft `f1` produced, so only the READER
        decided which of the two co-located places gave the prose back, and it
        always said `f1`.

        ! WHAT SEPARATES THEM is a trailing leading below the closing gap, so
        its run no longer ends on the last line and is no longer back matter.
        The back matter keeps the foot; the gap sits above the blank.
        """
        at_gap, at_matter = build(SAMPLE), build(SAMPLE)
        assert galley.reset(at_gap, {"b4": "# ADDED"}) == []
        assert galley.reset(at_matter, {"f1": "# ADDED"}) == []
        gap, matter = compositor.set_page(at_gap), compositor.set_page(at_matter)
        assert gap != matter
        assert gap.endswith("# ADDED\n\n")
        assert matter.endswith("# ADDED\n")
        # ! AND EACH COMES BACK AT ITS OWN CUE, which is the claim that matters.
        assert by_cue(build(gap))["b4"].raw_lines == ["# ADDED"]
        assert by_cue(build(matter))["f1"].raw_lines == ["# ADDED"]

    def test_a_docstring_DROP_is_STILL_REFUSED_at_prove(self, tmp_path):
        """!! NOT FIXED IN THIS WAVE, AND DELIBERATELY. MEASURED 2026-08-25:
        `{'m.py@a0': None}` and `{'m.py@a1': None}` both answer
        `Refusal('prove', ..., 'the executable code is not what it was')`.
        `prove_unchanged._blank_docstrings` blanks a docstring's CONTENT and
        keeps its NODE, so the PRESENCE is in the fingerprint.

        ! REMOVING PRESENCE FROM THE FINGERPRINT WOULD CERTIFY A REAL CHANGE AS
        UNCHANGED: a docstring binds `__doc__`, and SIX modules in this package
        read `ArgumentParser(description=__doc__)`. Whether the proof stays a
        blanket one or becomes a diff against the APPROVED set is task T1 of
        `TODO/the-code-check-refuses-add-and-drop-on-a-docstring.md` -- a `*`
        box, which is a decision only Roy makes.

        ! THIS IS WHAT T5 OF THAT FILE ASKS FOR: a docstring ADDED and a
        docstring REMOVED, running, so the suite states the behaviour instead
        of leaving it to be rediscovered."""
        for n, where in enumerate(sorted(FILLED & DOCSTRING)):
            each = tmp_path / str(n)
            each.mkdir()
            drafted, refused = self._run(each, {f"m.py@{where}": None})
            assert drafted == []
            assert refused[0].step == "prove", where
            assert "not what it was" in refused[0].why

    def test_a_docstring_ADD_is_STILL_REFUSED_at_prove(self, tmp_path):
        """The other half, on the `undocumented` place that exists precisely so
        an `add` can cite it -- `binder.bind`'s own docstring says so."""
        for n, where in enumerate(sorted(ABSENT & DOCSTRING)):
            each = tmp_path / str(n)
            each.mkdir()
            drafted, refused = self._run(each, {f"m.py@{where}": ADDED["a"]})
            assert drafted == []
            assert refused[0].step == "prove", where
            assert "not what it was" in refused[0].why

    def test_an_ADD_at_b4_NOW_REACHES_A_DRAFT_AT_ITS_OWN_PLACE(self, tmp_path):
        """!! IT REFUSED UNTIL 2026-08-26, and the refusal was right about the
        page rather than about the alteration: `b4` and `f1` are emitted at the
        same `<eof>` trigger, so prose set at the closing gap came back at the
        back matter and `reread` reported `f1 holds it`.

        Roy: *"still the same rule as the frontmatter in reverse."* Matter is
        the run that STARTS on line 1 or ENDS on the last one, so the blank that
        pushes a gap clear of it goes BEFORE at the head and AFTER at the foot.
        The compositor sets a trailing leading below an added closing gap, and
        the two places separate.
        """
        drafted, refused = self._run(tmp_path, {"m.py@b4": "# ADDED"})
        assert refused == []
        assert len(drafted) == 1
        again = build(drafted[0].draft.read_text(encoding="utf-8"))
        assert by_cue(again)["b4"].raw_lines == ["# ADDED"]


class TestOnlyCommentsChange:
    """Roy, 2026-08-25: prove_unchanged runs *"just before the human review and
    just after the human review edit piece just to be certain we only changed
    only comments."* This is the first of those two.

    ! `_prove` IS TESTED DIRECTLY BELOW, NOT THROUGH `run()`. For Python's
    AST tier, `_reread` already requires exact `raw_lines` equality at every
    edited cue, so an alteration surviving it was -- by construction -- read back
    as prose at that cue, and a COMMENT never enters the AST.

    !! THIS PARAGRAPH CLAIMED *"No `b`, `a` or `c` cue alteration reaching
    `proof_setter.run()` on this module's own `SAMPLE` fixture can therefore
    make `_prove`'s comparison disagree -- measured, not assumed"*, AND IT WAS
    FALSE WHEN IT WAS WRITTEN. Two `a` cues do exactly that on exactly that
    fixture: `{'m.py@a0': None}` and `{'m.py@a1': None}` both refuse with
    `Refusal('prove', ..., 'the executable code is not what it was')`, because
    `_blank_docstrings` keeps a docstring's PRESENCE in the fingerprint -- and
    so does an `add` at `a2`.
    `TestEveryVerdictThePlacesCanEXPRESSGetsThroughTheChain` above is what
    would have disagreed; the measurement behind the claim only ever tried the
    `b` series it was written beside. ! The claim holds for a COMMENT and that
    is the whole of what it holds for.

    The real hazard `_prove` guards is `TODO/closing-line-deletes-code.md`: a
    comment whose run closes mid-line, or never closes at all, can swallow the
    code that follows it -- code beyond the cue `_reread` was asked about,
    which is exactly what `_reread` cannot see.
    """

    def test_an_ordinary_comment_change_PASSES(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        drafted, refused = proof_setter.run(
            docket_from({address(binder, "m.py"): "# still a comment"}, binder),
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


def test_a_CUE_COLLISION_in_the_draft_is_REFUSED_and_not_last_one_wins(
    tmp_path, monkeypatch
):
    """IMPORTANT, measured 2026-08-25: `_reread` built
    `placed = {cue_of(b.address).cue: b for b in page if b.address}`, so two
    paragraphs sharing a cue silently kept the LAST and checked the alteration
    against it -- a draft holding the approved text at one and prose nobody
    looked at at the other passed. `galley.reset` refuses that shape BY NAME
    (157 of them measured in one tree on 2026-08-21), so the verification step
    was weaker than the edit step it exists to check.

    ! THE COLLISION IS THE INPUT, which is why it is made rather than found: no
    file in this tree produces one today, and `_reread` reads the DRAFT, so the
    only way in is the reader it calls. The page is a real page over the real
    draft; one paragraph's address is copied onto another so the shape under
    test is the shape being asserted about.

    ! IT IS CONDITIONED ON THE PATH because `_reread` reads through `page_of`,
    the same step `_one` reads the SOURCE through. Colliding both would refuse
    at `edit` -- `galley.reset`'s own collision check -- and never reach the
    step under test."""
    repo, binder, _ = _tree(tmp_path)
    into = tmp_path / "out"
    where = address(binder, "m.py")
    cue = cue_of(where).cue
    real_page_for = page_for_mod.page_for

    def colliding_page_for(path, *args, **kwargs):
        page = real_page_for(path, *args, **kwargs)
        if not Path(path).resolve().is_relative_to(into.resolve()):
            return page
        addressed = [b for b in page if b.address]
        held = next(b for b in addressed if cue_of(b.address).cue == cue)
        other = next(b for b in addressed if b is not held)
        other.address = held.address
        return page

    monkeypatch.setattr(page_for_mod, "page_for", colliding_page_for)
    drafted, refused = proof_setter.run(
        docket_from({where: "# REPLACED"}, binder), repo, into
    )
    assert drafted == []
    assert len(refused) == 1
    assert refused[0].step == "reread"
    assert "2 paragraphs share this place" in refused[0].why


def test_a_directory_THAT_WAS_THERE_BEFORE_the_run_survives_it(tmp_path, monkeypatch):
    """IMPORTANT, measured 2026-08-25: `_discard` walked up `rmdir`-ing ANY
    empty directory under `into`, so a `<into>/pkg` that existed before the run
    was gone after a run that refused. Its own docstring promised only *"any
    directory under `into` IT leaves empty"* -- narrower than the code kept.

    ! A FLAT `rel` CANNOT SHOW THIS. `_tree`'s `m.py` drafts straight into
    `into`, which `_discard` has always stopped at, so the directory walk never
    runs at all."""
    repo = tmp_path / "repo"
    (repo / "pkg").mkdir(parents=True)
    (repo / "pkg" / "d.py").write_text(SAMPLE, encoding="utf-8", newline="")
    (repo / "n.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = bind([build(SAMPLE, "pkg/d.py"), build(SAMPLE, "n.py")])
    into = tmp_path / "out"
    (into / "pkg").mkdir(parents=True)

    drafted, refused = proof_setter.run(
        docket_from(
            {address(binder, "pkg/d.py"): "# REPLACED", "n.py@b99": "# bad"}, binder
        ),
        repo,
        into,
    )
    assert drafted == []
    assert refused and refused[0].path == "n.py"
    assert (into / "pkg").is_dir()
    assert list((into / "pkg").iterdir()) == []


def test_a_WRITE_THAT_RAISES_leaves_no_directory_behind(tmp_path, monkeypatch):
    """IMPORTANT, measured 2026-08-25: `compositor.draft` mkdirs with
    `parents=True` and THEN writes, and the call sat OUTSIDE `_one`'s `try` --
    so with `rel = 'pkg/d.py'` and the write raising, `into.iterdir()` answered
    `['pkg']`. The existing regression above monkeypatches `_reread`, which
    runs after a write that SUCCEEDED, so it could not reach this."""
    repo = tmp_path / "repo"
    (repo / "pkg").mkdir(parents=True)
    (repo / "pkg" / "d.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = bind([build(SAMPLE, "pkg/d.py")])
    into = tmp_path / "out"

    real_write_text = Path.write_text

    def failing_write_text(self, *args, **kwargs):
        if self.name == "d.py":
            raise PermissionError("simulated: the draft could not be written")
        return real_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", failing_write_text)

    with pytest.raises(PermissionError):
        proof_setter.run(
            docket_from({address(binder, "pkg/d.py"): "# REPLACED"}, binder), repo, into
        )

    assert list(into.iterdir()) == []
