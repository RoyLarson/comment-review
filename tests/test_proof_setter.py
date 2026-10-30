"""The chain from alterations to a drafted file a human can read.

! THE ORDER IS DATA. A missing check is then a missing element rather than a
forgotten call -- which is the one failure a runner that hard-codes its
sequence cannot show you.
"""

import dataclasses
from pathlib import Path

import pytest
from conftest import PKG, SAMPLE, build, by_cue, cue, docket_from
from helpers import a_move, copies_over, entries_of, returned

from comment_review.binder.binder import bind
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.docket.docket import Alteration, Docket, Schedule
from comment_review.flows import page_for as page_for_mod
from comment_review.flows import proof_setter, revise
from comment_review.flows import source as source_flow
from comment_review.flows.distribute import seed
from comment_review.flows.transcribe import docket_of
from comment_review.machine.repo import undraftable
from comment_review.reading import stripped
from comment_review.reading.addresser import cue_of
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.stripped import code_fingerprint
from comment_review.results import compositor, galley


@pytest.mark.parametrize("fault", ["digest", "malformed", "duplicate-settings"])
def test_saved_context_refuses_before_setting(tmp_path, monkeypatch, fault):
    repo, binder, _ = _tree(tmp_path)
    docket = docket_from({address(binder, "m.py"): "# replacement"}, binder)
    saved = docket.schedules[0].reading
    if fault == "digest":
        saved = dataclasses.replace(saved, compatibility="0" * 64)
    elif fault == "malformed":
        saved = []
    else:
        object.__setattr__(saved, "settings", (("mode", "on"), ("mode", "off")))
    schedule = dataclasses.replace(docket.schedules[0], reading=saved)

    def forbidden_set(*args, **kwargs):
        pytest.fail("incompatible context reached the setter")

    monkeypatch.setattr(galley, "reset", forbidden_set)
    drafted, refused = proof_setter.run(Docket((schedule,)), repo, tmp_path / "out")
    assert drafted == []
    assert refused and "reading" in refused[0].why


@pytest.mark.parametrize("different", ["same", "sha", "reading"])
def test_direct_duplicate_paths_refuse_before_drafting(
    tmp_path, monkeypatch, different
):
    repo, binder, _ = _tree(tmp_path)
    docket = docket_from({address(binder, "m.py"): "# replacement"}, binder)
    first = docket.schedules[0]
    second = first
    if different == "sha":
        second = dataclasses.replace(first, sha="different")
    elif different == "reading":
        second = dataclasses.replace(
            first, reading=dataclasses.replace(first.reading, compatibility="0" * 64)
        )

    def forbidden_set(*args, **kwargs):
        pytest.fail("duplicate paths reached the setter")

    monkeypatch.setattr(galley, "reset", forbidden_set)
    drafted, refused = proof_setter.run(Docket((first, second)), repo, tmp_path / "out")
    assert drafted == []
    assert "two schedules" in refused[0].why


def test_later_saved_context_mismatch_discards_nested_draft(tmp_path, monkeypatch):
    repo, into = tmp_path / "repo", tmp_path / "out"
    originals = {
        "a/deep/first.py": b"x = 1\r\n\r\n# note\r\ny = 2\r\n",
        "z.py": b"x = 1\n\n# note\ny = 2\n",
    }
    pages = []
    for rel, raw in originals.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        page = proof_setter.page_of(path, rel=rel)
        assert not isinstance(page, ReadFailure)
        pages.append(page)
    binder = bind(pages, read_from={"root": str(repo), "revise": 0})
    docket = docket_from(
        {address(binder, rel): "# replacement" for rel in originals}, binder
    )
    first, second = docket.schedules
    second = dataclasses.replace(
        second, reading=dataclasses.replace(second.reading, compatibility="0" * 64)
    )
    real_page = proof_setter.page_of
    observed = []

    def observing_page(path, *args, **kwargs):
        if path == repo / "z.py":
            observed.append((into / "a/deep/first.py").is_file())
        return real_page(path, *args, **kwargs)

    monkeypatch.setattr(proof_setter, "page_of", observing_page)
    drafted, refused = proof_setter.run(Docket((first, second)), repo, into)
    assert drafted == [] and refused
    assert observed == [True]
    assert list(into.iterdir()) == []
    assert {rel: (repo / rel).read_bytes() for rel in originals} == originals


@pytest.mark.parametrize("text", ["x = 1\n\n# note\ny = 2\n", ""])
def test_saved_nondefault_settings_reach_original_and_draft(
    tmp_path, monkeypatch, text
):
    from comment_review.flows import reading_context as flow_context

    original_reader = flow_context.reader_for
    registry = flow_context.installed_registry()
    assert not isinstance(registry, ReadFailure)
    selected = original_reader(Path("m.py"), registry)
    assert selected is not None and not isinstance(selected, ReadFailure)
    definition, binding = selected
    configured = dataclasses.replace(
        definition, defaults={"mode": "default"}, choices={"mode": ("default", "saved")}
    )
    monkeypatch.setattr(
        flow_context, "reader_for", lambda path, registry: (configured, binding)
    )
    repo, into = tmp_path / "repo", tmp_path / "out"
    repo.mkdir()
    path = repo / "m.py"
    path.write_text(text, encoding="utf-8")
    page = proof_setter.page_of(path, rel="m.py", settings={"mode": "saved"})
    assert not isinstance(page, ReadFailure)
    if text:
        binder = bind([page], read_from={"root": str(repo), "revise": 0})
        docket = docket_from({address(binder, "m.py"): "# replacement"}, binder)
        docket = Docket(
            (dataclasses.replace(docket.schedules[0], reading=page.reading),)
        )
    else:
        docket = Docket((Schedule("m.py", page.sha, (), page.reading),))
    real_page = page_for_mod.page_for
    observed = []

    def require_saved(path, *args, **kwargs):
        reading = kwargs["reading"]
        observed.append((Path(path), reading.settings))
        return real_page(path, *args, **kwargs)

    monkeypatch.setattr(page_for_mod, "page_for", require_saved)
    drafted, refused = proof_setter.run(docket, repo, into)
    assert refused == [] and len(drafted) == 1
    assert observed == [
        (path, (("mode", "saved"),)),
        (into / "m.py", (("mode", "saved"),)),
    ]


@pytest.mark.parametrize("stage", ["lex", "place"])
def test_direct_proof_refuses_failed_reading(monkeypatch, stage):
    from comment_review.reading.diagnostics import ReadDiagnostic, ReadStage
    from comment_review.reading.source import SourceSpan

    def failed_page(*args, **kwargs):
        return ReadFailure(
            (
                ReadDiagnostic(
                    ReadStage(stage),
                    "refused-input",
                    "source refused",
                    SourceSpan(0, 1),
                ),
            )
        )

    monkeypatch.setattr(page_for_mod, "page_for", failed_page)
    refusal = proof_setter._prove(
        "m.js", "const value = 1;\n", "const value = 1;\n", Path("m.js")
    )
    assert refusal is not None
    assert refusal.step == "prove"
    assert f"{stage}/refused-input" in refusal.why


def test_failed_draft_read_rejects_and_rolls_back(tmp_path, monkeypatch):
    from comment_review.reading.diagnostics import ReadDiagnostic, ReadStage

    repo, binder, _ = _tree(tmp_path)
    into = tmp_path / "out"
    real_page = page_for_mod.page_for

    def failed_draft(path, *args, **kwargs):
        if Path(path).is_relative_to(into):
            return ReadFailure(
                (ReadDiagnostic(ReadStage.PLACE, "draft-placement", "draft refused"),)
            )
        return real_page(path, *args, **kwargs)

    monkeypatch.setattr(page_for_mod, "page_for", failed_draft)
    drafted, refused = proof_setter.run(
        docket_from({address(binder, "m.py"): "# replacement"}, binder), repo, into
    )
    assert drafted == []
    assert refused[0].step == "reread"
    assert "place/draft-placement" in refused[0].why
    assert not (into / "m.py").exists()


@pytest.mark.parametrize("side", ["source", "draft"])
@pytest.mark.parametrize("stage", ["acquire", "decode", "lex", "place", "programming"])
def test_second_file_read_failure_discards_all_nested_drafts(
    tmp_path, monkeypatch, side, stage
):
    originals = {
        "a/first.py": b"value = 1\r\n\r\n# first note\r\nother = 2\r\n",
        "z/deep/second.py": b"value = 3\n\n# second note\nother = 4\n",
    }
    repo = tmp_path / "repo"
    into = tmp_path / "out"
    into.mkdir()
    pages = []
    for rel, raw in originals.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        page = proof_setter.page_of(path, rel=rel)
        assert not isinstance(page, ReadFailure), page
        pages.append(page)
    binder = bind(pages, read_from={"root": str(repo), "revise": 0})
    docket = docket_from(
        {address(binder, rel): "# replacement" for rel in originals}, binder
    )
    target = (repo if side == "source" else into) / "z/deep/second.py"
    observed = []
    bug = RuntimeError("reader implementation failed")

    def check_staged():
        assert (into / "a/first.py").is_file()
        assert (into / "a/first.py").read_bytes() != originals["a/first.py"]
        if side == "draft":
            assert target.is_file()
        observed.append(target)

    if stage in ("acquire", "decode"):
        real_read = source_flow.read_source

        def failing_source(path):
            if path == target:
                check_staged()
                if stage == "acquire":
                    raise PermissionError("source acquisition refused")
                raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte")
            return real_read(path)

        monkeypatch.setattr(source_flow, "read_source", failing_source)
    else:
        real_page = page_for_mod.page_for

        def failing_page(path, *args, **kwargs):
            if Path(path) == target:
                check_staged()
                if stage == "programming":
                    raise bug
                return ReadFailure(
                    (
                        ReadDiagnostic(
                            ReadStage(stage), "refused-input", "source refused"
                        ),
                    )
                )
            return real_page(path, *args, **kwargs)

        monkeypatch.setattr(page_for_mod, "page_for", failing_page)

    if stage == "programming":
        with pytest.raises(
            RuntimeError, match="^reader implementation failed$"
        ) as raised:
            proof_setter.run(docket, repo, into)
        assert raised.value is bug
    else:
        drafted, refused = proof_setter.run(docket, repo, into)
        assert drafted == []
        assert len(refused) == 1
        assert (refused[0].step, refused[0].path) == (
            "read" if side == "source" else "reread",
            "z/deep/second.py",
        )
        code = {"acquire": "io-error", "decode": "invalid-utf8"}.get(
            stage, "refused-input"
        )
        assert f"{stage}/{code}" in refused[0].why
    assert observed == [target]
    assert list(into.iterdir()) == []
    assert {rel: (repo / rel).read_bytes() for rel in originals} == originals


def test_proof_reuses_admitted_pages(tmp_path, monkeypatch):
    repo, binder, _ = _tree(tmp_path)
    real_page = proof_setter.page_of
    reads = []

    def watching_page(path, *args, **kwargs):
        reads.append(path)
        return real_page(path, *args, **kwargs)

    monkeypatch.setattr(proof_setter, "page_of", watching_page)
    into = tmp_path / "out"
    drafted, refused = proof_setter.run(
        docket_from({address(binder, "m.py"): "# replacement"}, binder), repo, into
    )
    assert refused == [] and len(drafted) == 1
    assert reads == [repo / "m.py", into / "m.py"]


@pytest.mark.parametrize("kind", ["unprovable", "unknown", "ast"])
def test_direct_proof_failed_fingerprint_kind_cannot_pass(monkeypatch, kind):
    monkeypatch.setattr(stripped, "code_fingerprint", lambda *args: (kind, ""))
    refusal = proof_setter._prove(
        "m.js", "const value = 1;\n", "const value = 1;\n", Path("m.js")
    )
    assert refusal is not None and refusal.step == "prove"


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

#: The docstring series. It is held out of the two matrices below because a
#: docstring `add` or `drop` changes a docstring's presence, which the proof
#: sets aside only at the declaration an approved alteration documents
#: (`decision-log.md Process: #113`); the cases named for it sit beside the
#: cases the proof still refuses.
DOCSTRING = {c for c in FILLED | ABSENT if c.startswith("a")}

#: A decorated declaration nested inside another, with an undocumented `inner`
#: at `a2` -- the shape where the page's `a` numbering and `ast.walk`'s order
#: disagree.
NESTED = (
    "def outer(fn):\n"
    '    """Outer."""\n'
    "\n"
    "    @fn\n"
    "    def inner():\n"
    "        return 1\n"
    "\n"
    "    return inner\n"
    "\n"
    "\n"
    "def later():\n"
    '    """Later."""\n'
    "    return 2\n"
)


def address(binder, path: str, series: str = "b") -> str:
    """One address off the binder, in the FORM THE BINDER PUBLISHES.

    !! EVERY TEST HERE HAND-WROTE `f"{rel}@{cue}"` UNTIL 2026-08-25, and that
    is what hid the CRITICAL defect: an address carries the FLATTENED path --
    `pkg:a:util.py` -- and a hand-written one carries `/`. The flat form split
    whatever it is handed, so the tests fed the chain a form nothing produces
    and only repo-root files, whose flattened form is their path, agreed. The
    fixture could not disagree with the code because the fixture was written to
    match it.

    ! IT ASKS `Binder.paragraphs`, which is what a caller of this chain has.
    """
    for row in binder.paragraphs:
        if row.path == path and cue(row).startswith(series) and row.raw_text.strip():
            return row.address
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
    return repo, bind([page], read_from={"root": str(repo), "revise": 0}), page


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
    """CRITICAL, measured 2026-08-25: the flat form keyed by the FLATTENED path an
    address carries, and `run` used that string both as a binder key and as a
    filesystem path -- so `pkg/a/util.py` was looked up as `pkg:a:util.py`,
    missed the binder, and was handed to `page_of` as `repo/pkg:a:util.py`,
    which is invalid on Windows and missing on POSIX. EVERY alteration on a file
    below the repo root refused at step `read`; only repo-root files, whose
    flattened form equals their path, worked."""
    repo = tmp_path / "repo"
    (repo / "pkg" / "a").mkdir(parents=True)
    (repo / "pkg" / "a" / "util.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = bind(
        [build(SAMPLE, "pkg/a/util.py")], read_from={"root": str(repo), "revise": 0}
    )

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
    # ! HAND-WRITTEN WIRE, THROUGH THE BOUNDARY -- `conftest.docket_from` builds
    # its dockets from a real binder's pages, and this case needs a page the
    # checkout does NOT have, which no binder can supply.
    docket, problems = Docket.deserialize(
        "d.json",
        {
            "pages": [
                {
                    "path": "pkg/nowhere.py",
                    "sha": "whatever",
                    "reading": build("", "pkg/nowhere.py").serialize()["reading"],
                    "alterations": [{"cue": "b0", "text": "# x"}],
                }
            ]
        },
    )
    assert docket is not None, problems
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
        DELETED, leaving the two below. `galley` ran on as a CLI alias in
        `__main__.ALIASES` that dispatched straight to `proof`'s own module,
        asking nothing of its own, until that alias was removed 2026-08-28 --
        `docs/history.md` is what pins that."""
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
    binder = bind([page_m, page_n], read_from={"root": str(repo), "revise": 0})
    into = tmp_path / "out"
    alterations = {address(binder, "m.py"): "# REPLACED", "n.py@b99": "# bad"}
    drafted, refused = proof_setter.run(docket_from(alterations, binder), repo, into)
    assert drafted == []
    assert len(refused) == 1
    assert refused[0].path == "n.py"
    assert list(into.iterdir()) == []


def _fail_the_draft_of(monkeypatch, name: str, why: str) -> None:
    """Make ONE page's draft write raise, leaving every other page's alone.

    !! IT PATCHES `results.compositor.write_raw`, AND PATCHED `Path.write_text`
    UNTIL `P45`. The draft reaches disk through `machine.repo.write_raw` now, so
    the old patch stopped biting -- and when it did, TWO of the three tests
    below went green WITHOUT RAISING. `docs/gates.md`: not *"does the check
    pass"* but *"could the check fail"*.

    ! ONE SPELLING, THREE CALLERS. The three sites each carried the same
    seven-line closure over `Path.write_text`, differing only in the filename
    and the message -- which is why the move had to be made three times and why
    one of them could have been missed.

    Args:
        monkeypatch: the test's own fixture.
        name: the basename whose write raises. Every other write is real.
        why: the `PermissionError`'s message.
    """
    real = compositor.write_raw

    def failing(path, text):
        if path.name == name:
            raise PermissionError(why)
        return real(path, text)

    monkeypatch.setattr(compositor, "write_raw", failing)


def _the_draft_also(monkeypatch, old: str, new: str) -> None:
    """Make every draft carry one change beyond the approved alterations.

    It patches `results.compositor.write_raw`, the one writer, so the draft
    `_one` reads back and proves holds `new` where the set page held `old`.
    `_reread` checks only the places an alteration names, so the change
    reaches `_prove`.

    Args:
        monkeypatch: the test's own fixture.
        old: text the set page holds exactly once.
        new: what the draft holds in its place.
    """
    real = compositor.write_raw

    def changed(path, text):
        assert text.count(old) == 1, old
        return real(path, text.replace(old, new))

    monkeypatch.setattr(compositor, "write_raw", changed)


def _two_pages(tmp_path):
    """A two-file repo whose FIRST page in sort order is already stale."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "a.py").write_text(SAMPLE, encoding="utf-8", newline="")
    (repo / "z.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = bind(
        [build(SAMPLE, "a.py"), build(SAMPLE, "z.py")],
        read_from={"root": str(repo), "revise": 0},
    )
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


class TestTheWriteEndChecksAMarksAnchor:
    """`decision-log.md Process: #134`, `galley-and-compositor-write-path`
    T46. A mark's anchor rides from its copy through `docket_of` to the write
    end, which refuses one that is not the page's anchor at the mark's
    address. The copy is seeded from a binder over the real page, so the
    anchor it carries is the page's until a hand alters it."""

    def _copy(self, binder, where: str, anchor: str | None = None) -> EditCopy:
        wire = seed(binder, "block-context")
        slot = next(
            m for s in wire["sheets"] for m in s["marks"] if m["address"] == where
        )
        slot.update(
            instruction="correct",
            claim={"false": "note", "true": "NOTE"},
            reason="the note is set in capitals",
            sources=[{"cite": "m.py:5", "verbatim": "# note"}],
            change="# NOTE",
        )
        if anchor is not None:
            slot["anchor"] = anchor
        copy, why = EditCopy.deserialize("copy", wire)
        assert copy is not None, why
        return copy

    def test_a_mark_whose_anchor_was_altered_by_hand_is_refused(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        where = address(binder, "m.py")
        copy = self._copy(binder, where, anchor="a line the role invented")
        drafted, refused = proof_setter.run(
            docket_of(copy, repo), repo, tmp_path / "out"
        )
        assert drafted == []
        assert [(r.step, r.path) for r in refused] == [("verify", "m.py")]
        assert where in refused[0].why, refused[0].why
        assert "a line the role invented" in refused[0].why

    def test_a_mark_carrying_the_pages_anchor_is_set(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        where = address(binder, "m.py")
        copy = self._copy(binder, where)
        drafted, refused = proof_setter.run(
            docket_of(copy, repo), repo, tmp_path / "out"
        )
        assert refused == []
        assert "# NOTE" in drafted[0].draft.read_text(encoding="utf-8")


class TestEveryAlterationCarriesAnAnchor:
    """`decision-log.md Process: #135`, as amended, and
    `galley-and-compositor-write-path` T49. The write end refuses an
    alteration that carries no anchor. The flow gives every alteration the
    page's anchor at its place, a move's destination included, so its own
    docket for a move is set."""

    def test_an_alteration_with_no_anchor_is_refused(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        where = address(binder, "m.py")
        (page,) = binder.pages
        docket, problems = Docket.deserialize(
            "d.json",
            {
                "pages": [
                    {
                        "path": "m.py",
                        "sha": page.sha,
                        "reading": page.serialize()["reading"],
                        "alterations": [{"cue": cue_of(where).cue, "text": "# x"}],
                    }
                ]
            },
        )
        assert docket is not None, problems
        drafted, refused = proof_setter.run(docket, repo, tmp_path / "out")
        assert drafted == []
        assert [(r.step, r.path) for r in refused] == [("verify", "m.py")]
        assert where in refused[0].why, refused[0].why
        assert "no anchor" in refused[0].why, refused[0].why

    def test_the_flows_own_docket_for_a_move_is_set(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        origin = address(binder, "m.py")
        destination = f"m.py@{min(c for c in ABSENT if c.startswith('b'))}"
        # The whole paragraph moves, so the snippet subtracted from the origin
        # and the text the empty destination reads with are the same
        # (`decision-log.md Process: #172` and `#175`).
        base = next(p.raw_text for p in binder.paragraphs if p.address == origin)
        move = a_move(origin, destination, change=base, reads=base)
        copy = returned(copies_over(binder, {"block-context": {origin: move}})[0])
        (mark,) = entries_of(copy)
        drafted, refused = proof_setter.run(
            docket_of(copy, repo), repo, tmp_path / "out"
        )
        assert refused == []
        again = build(drafted[0].draft.read_text(encoding="utf-8"))
        assert by_cue(again)[cue_of(destination).cue].raw_lines == mark.raw_text.split(
            "\n"
        )


class TestOnePlaceTakesOneAlteration:
    """`docket-defects` T11. `Schedule.deserialize` refuses a repeated place, but
    `flows.transcribe.docket_of` builds its schedules directly, and
    `Schedule.edits` keeps the last alteration at a place -- so a role's copy
    that moves a paragraph into a place it also edits drafted with one of the
    two lost, at exit 0. The write end refuses it by name however the docket
    was built."""

    def test_two_alterations_at_one_place_are_refused_naming_both(self, tmp_path):
        repo, binder, _ = _tree(tmp_path)
        where = address(binder, "m.py")
        at = cue_of(where).cue
        (page,) = binder.pages
        held = page_for_mod.page_of(repo / "m.py", rel="m.py")
        assert not isinstance(held, ReadFailure), held
        anchor = held.cues.places[at]
        docket = Docket(
            schedules=(
                Schedule(
                    path="m.py",
                    sha=page.sha,
                    reading=page.reading,
                    alterations=(
                        Alteration(cue=at, text="# one", anchor=anchor),
                        Alteration(cue=at, text=None, anchor=anchor),
                    ),
                ),
            )
        )
        drafted, refused = proof_setter.run(docket, repo, tmp_path / "out")
        assert drafted == []
        assert [(r.step, r.path) for r in refused] == [("verify", "m.py")]
        assert f"{where}: two alterations for one place" in refused[0].why
        assert "'# one'" in refused[0].why, refused[0].why
        assert "a delete" in refused[0].why, refused[0].why


def test_A_REFUSAL_IS_NOT_LOST_to_a_later_page_that_raises(tmp_path, monkeypatch):
    """CRITICAL, measured 2026-08-26: `run` collected the refusal, went on to
    the next page, and that page's write raised -- so `run` re-raised and the
    caller got a traceback INSTEAD of the refusals, past the documented
    `(drafted, []) or ([], refusals)`."""
    repo, binder, alterations = _two_pages(tmp_path)
    into = tmp_path / "out"
    _fail_the_draft_of(monkeypatch, "z.py", "simulated: a later page's write fails")

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
    binder = bind(
        [build(SAMPLE, "pkg/a/util.py"), build(SAMPLE, "pkg/b/util.py")],
        read_from={"root": str(repo), "revise": 0},
    )
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

    ! IT NAMES THE BINDER PAGE PATH NOW. `run` asks `can_escape` of every page
    path as it reads the shas, before the loop, so the refusal states the fault
    rather than whichever of the two roots the path happened to leave first."""
    repo = tmp_path / "repo"
    repo.mkdir()
    escaped = tmp_path / "escape_repo" / "sub"
    escaped.mkdir(parents=True)
    escaped_file = escaped / "util.py"
    escaped_file.write_text(SAMPLE, encoding="utf-8", newline="")
    before = escaped_file.read_bytes()

    rel = "../escape_repo/sub/util.py"
    binder = bind([build(SAMPLE, rel)], read_from={"root": str(repo), "revise": 0})
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
    could state the fault. `run` now asks `can_escape` of the binder page path
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

    binder = bind([build(SAMPLE, rel)], read_from={"root": str(repo), "revise": 0})
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
    `PermissionError` from the draft write escaped `run()` as a raw traceback
    and `out/alpha.py` was left behind -- the cleanup below only ran on the
    `refusals` branch, never on an exception. The docstring's claim ("Every
    draft this run wrote is removed") must hold for either kind of stop."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    (repo / "n.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = bind(
        [build(SAMPLE, "m.py"), build(SAMPLE, "n.py")],
        read_from={"root": str(repo), "revise": 0},
    )
    into = tmp_path / "out"

    _fail_the_draft_of(monkeypatch, "n.py", "simulated: target pre-occupied")

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
    wrote is removed. The existing regression test exercises only the WRITE
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
    binder = bind(
        [build(SAMPLE, "pkg/d.py")], read_from={"root": str(repo), "revise": 0}
    )
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
    binder = bind(
        [build(SAMPLE, "pkg/d.py")], read_from={"root": str(repo), "revise": 0}
    )
    into = tmp_path / "out"

    def refusing_reread(*args, **kwargs):
        return None, proof_setter.Refusal("reread", "pkg/d.py", "simulated mismatch")

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
        if where == "f0":
            assert drafted == []
            assert refused and refused[0].step == "prove"
            assert "code-changed" in refused[0].why
            return
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

    @pytest.mark.parametrize("where", sorted(ABSENT & DOCSTRING))
    def test_an_approved_docstring_ADD_reaches_a_draft(self, tmp_path, where):
        """The proof compares against the approved changes, not against nothing
        changed -- `decision-log.md Process: #113`. A docstring added at an
        undocumented declaration by an approved `add` is the edit landing."""
        drafted, refused = self._run(tmp_path, {f"m.py@{where}": ADDED["a"]})
        assert refused == []
        assert len(drafted) == 1
        again = build(drafted[0].draft.read_text(encoding="utf-8"))
        assert by_cue(again)[where].raw_lines == [ADDED["a"]]

    @pytest.mark.parametrize("where", sorted(FILLED & DOCSTRING))
    def test_an_approved_docstring_DROP_reaches_a_draft(self, tmp_path, where):
        """The other half: the module's docstring and a function's, each
        removed by an approved `drop`."""
        drafted, refused = self._run(tmp_path, {f"m.py@{where}": None})
        assert refused == []
        assert len(drafted) == 1
        again = build(drafted[0].draft.read_text(encoding="utf-8"))
        assert not any(line.strip() for line in by_cue(again)[where].raw_lines)

    def test_a_docstring_presence_NO_ALTERATION_NAMES_is_refused_at_prove(
        self, tmp_path, monkeypatch
    ):
        """An approved `add` at `a2` sets aside the presence of that one
        declaration's docstring. The draft also loses the docstring `a1` holds,
        which no alteration names, so the proof refuses it: a docstring binds
        `__doc__`, and a module reading `ArgumentParser(description=__doc__)`
        behaves differently without one."""
        was = by_cue(build(SAMPLE))
        held = was["a1"].raw_lines
        assert len(held) == 1
        page = build(SAMPLE)
        galley.reset(page, {"a2": ADDED["a"]})
        after = compositor.set_page(page).replace(held[0] + "\n", "")
        now = by_cue(build(after))
        refused = proof_setter._prove(
            "m.py", SAMPLE, after, Path("m.py"), [(was["a2"], now["a2"])]
        )
        assert refused is not None
        assert refused.step == "prove"
        assert "not what it was" in refused.why

        # The whole chain stops one step sooner: nobody edited `a1`.
        _the_draft_also(monkeypatch, held[0] + "\n", "")
        drafted, chain = self._run(tmp_path, {"m.py@a2": ADDED["a"]})
        assert drafted == []
        assert chain[0].step == "reread"

    @pytest.mark.parametrize(
        "alterations",
        [{"m.py@a2": ADDED["a"]}, {"m.py@b0": "# REPLACED"}],
        ids=["beside-a-docstring-add", "no-docstring-alteration"],
    )
    def test_a_CODE_CHANGE_is_refused_at_prove(
        self, tmp_path, monkeypatch, alterations
    ):
        """Setting a docstring's presence aside leaves every line of code in
        the comparison, whether or not an approved docstring alteration sits
        beside the change."""
        _the_draft_also(monkeypatch, "    return y\n", "    return y + 1\n")
        drafted, refused = self._run(tmp_path, alterations)
        assert drafted == []
        assert refused[0].step == "prove"
        assert "not what it was" in refused[0].why

    def test_an_approved_ADD_at_a_NESTED_declaration_reaches_a_draft(self, tmp_path):
        """The declaration is the one the page puts the place's anchor on.
        `ast.walk` is breadth first and meets `later` before `inner`, so taking
        the `a` ordinal in walk order would set aside the wrong declaration and
        refuse this draft."""
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "m.py").write_text(NESTED, encoding="utf-8", newline="")
        binder = bind([build(NESTED)], read_from={"root": str(repo), "revise": 0})
        assert by_cue(build(NESTED))["a2"].anchor == "    def inner():"
        added = '        """ADDED."""'
        drafted, refused = proof_setter.run(
            docket_from({"m.py@a2": added}, binder), repo, tmp_path / "out"
        )
        assert refused == []
        again = build(drafted[0].draft.read_text(encoding="utf-8"))
        assert by_cue(again)["a2"].raw_lines == [added]

    def test_a_declaration_the_code_does_not_hold_there_is_refused_at_prove(self):
        """A place whose line holds no declaration in the code names nothing
        to set aside, and the proof refuses rather than guess at one."""
        page = build(SAMPLE)
        assert galley.reset(page, {"a2": ADDED["a"]}) == []
        after = compositor.set_page(page)
        was, now = by_cue(page)["a2"], by_cue(build(after))["a2"]
        assert (
            proof_setter._prove("m.py", SAMPLE, after, Path("m.py"), [(was, now)])
            is None
        )
        assert now.anchor_line is not None
        astray = dataclasses.replace(now, anchor_line=now.anchor_line + 1)
        refused = proof_setter._prove(
            "m.py", SAMPLE, after, Path("m.py"), [(was, astray)]
        )
        assert refused is not None
        assert refused.step == "prove"
        assert "cannot be identified" in refused.why

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

    ! `_prove` IS TESTED DIRECTLY BELOW, NOT THROUGH `run()`. `_reread` already
    requires each alteration's exact text on the lines written for it and every
    other paragraph's text unchanged, so a draft surviving it changed only the
    prose it was asked to.

    A docstring is the other prose that reaches the comparison: its presence
    is in the fingerprint except at a declaration an approved alteration
    documents (`decision-log.md Process: #113`), so an approved `add` or
    `drop` passes and a presence change no alteration names is refused.
    `TestEveryVerdictThePlacesCanEXPRESSGetsThroughTheChain` above holds those
    cases.

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

    def test_code_a_comment_never_closes_over_is_not_proven_as_no_code(self):
        """An unprovable file's fingerprint is the empty string, the same as a
        file with no code line, so a `_prove` that compared `want != got`
        without reading `kind` first would report these two IDENTICAL."""
        before = "// just a comment\n"
        after = "int y = 999; /* oops\n"
        assert code_fingerprint(before, Path("m.c")) == ("stripped", "")
        assert code_fingerprint(after, Path("m.c")) == ("unprovable", "")

        refused = proof_setter._prove("m.c", before, after, Path("m.c"))
        assert refused is not None
        assert refused.step == "prove"

    def test_two_files_with_no_code_line_prove_equal_because_neither_holds_code(self):
        refused = proof_setter._prove(
            "m.js", "// one\n", "/** two */\n// three\n", Path("m.js")
        )
        assert refused is None

    def test_code_added_to_a_file_with_no_code_line_refuses(self):
        refused = proof_setter._prove(
            "m.js", "// one\n", "// one\nlet x;\n", Path("m.js")
        )
        assert refused is not None
        assert refused.step == "prove"
        assert "code-changed" in refused.why

    @pytest.mark.parametrize("suffix", [".md", ".rst", ".txt", ".html"])
    def test_a_path_with_no_row_stays_unprovable(self, suffix):
        assert code_fingerprint("# Title\n", Path("m" + suffix)) == ("unprovable", "")


def _chain(tmp_path, name: str, text: str, alterations: dict):
    """The chain over a one-file repo holding `text` as `name`."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / name).write_text(text, encoding="utf-8", newline="")
    binder = bind([build(text, name)], read_from={"root": str(repo), "revise": 0})
    flat = {f"{name}@{where}": prose for where, prose in alterations.items()}
    return proof_setter.run(docket_from(flat, binder), repo, tmp_path / "out")


@pytest.mark.parametrize(
    ("text", "alterations", "expected"),
    [
        (
            "function f() {}\n",
            {"a0": "/** Module. */"},
            "/** Module. */\nfunction f() {}\n",
        ),
        (
            "function f() {}\n",
            {"a0": "/** Module. */", "a1": "/** F. */"},
            "/** Module. */\n/** F. */\nfunction f() {}\n",
        ),
    ],
    ids=["a0-over-a-declaration", "a0-and-a1"],
)
def test_an_alteration_read_back_at_its_partner_place_is_accepted(
    tmp_path, text, alterations, expected
):
    # `a0` filled alone above a declaration reads back as that declaration's `a`.
    drafted, refused = _chain(tmp_path, "m.js", text, alterations)
    assert refused == []
    assert drafted[0].draft.read_text(encoding="utf-8") == expected


def test_the_closing_docstring_above_back_matter_can_be_altered(tmp_path):
    text = "let y;\n/** D */\n// c\n\n// m\n"
    drafted, refused = _chain(tmp_path, "m.js", text, {"a1": "/** X */"})
    assert refused == []
    assert drafted[0].draft.read_text(encoding="utf-8") == (
        "let y;\n/** X */\n// c\n\n// m\n"
    )


def _step(tmp_path, n: int, name: str, text: str, alterations: dict) -> str:
    """One step of a chain of runs: what the draft holds after these alterations."""
    drafted, refused = _chain(tmp_path / str(n), name, text, alterations)
    assert refused == []
    return drafted[0].draft.read_bytes().decode("utf-8")


def _at(text: str, name: str, words: str) -> str:
    """The cue that holds `words` on a read of `text`."""
    return next(
        c for c, b in by_cue(build(text, name)).items() if b.raw_lines == [words]
    )


def _pulled(tmp_path, n: int, name: str, text: str, alterations: dict) -> str:
    """`_step` through `revise.pull`, the flow the `proof` command calls."""
    repo = tmp_path / str(n) / "repo"
    repo.mkdir()
    (repo / name).write_text(text, encoding="utf-8", newline="")
    binder = bind([build(text, name)], read_from={"root": str(repo), "revise": 0})
    flat = {f"{name}@{where}": prose for where, prose in alterations.items()}
    pulled = revise.pull(docket_from(flat, binder), repo, tmp_path / str(n) / "out", 1)
    assert pulled.refusals == []
    return (pulled.root / name).read_bytes().decode("utf-8")


@pytest.mark.parametrize("through", [_step, _pulled], ids=["run", "pull"])
@pytest.mark.parametrize("written", ["a0", "a1"])
def test_roys_chain_ends_byte_identical_to_the_first_draft(tmp_path, written, through):
    # Decision #247, on a blank docstring: add, read it back at the declaration's
    # `a`, run it through unchanged, move it to the other place.
    for path in (tmp_path / "1", tmp_path / "2", tmp_path / "3"):
        path.mkdir()
    words = "/** Doc. */"
    first = through(tmp_path, 1, "m.js", "function f() {}\n", {written: words})
    assert first == "/** Doc. */\nfunction f() {}\n"
    assert _at(first, "m.js", words) == "a1"
    assert through(tmp_path, 2, "m.js", first, {"a1": words}) == first
    assert through(tmp_path, 3, "m.js", first, {"a1": None, "a0": words}) == first


@pytest.mark.parametrize(
    ("name", "text", "words", "alteration", "expected"),
    [
        ("m.js", "", "", {"a0": "// A note."}, "// A note."),
        ("m.js", "// licence\n", "", {"a1": "/** End. */"}, None),
        ("m.js", "// a tpyo\n", "// a tpyo", {"": "// a typo"}, "// a typo\n"),
        ("m.h", "/** Teh doc. */\n", "/** Teh doc. */", {"": "/** The doc. */"}, None),
    ],
    ids=["blank-gets-a-comment", "eof-a", "typo-fixed", "header-of-docs"],
)
def test_a_file_with_no_code_line_takes_a_comment_change(
    tmp_path, name, text, words, alteration, expected
):
    alterations = {
        (_at(text, name, words) if not where else where): prose
        for where, prose in alteration.items()
    }
    drafted, refused = _chain(tmp_path, name, text, alterations)
    assert refused == []
    if expected is not None:
        assert drafted[0].draft.read_text(encoding="utf-8") == expected


class TestAnEmptyPackageInit:
    """An empty `__init__.py`, the no-code file Python reads and proves itself."""

    NAME = "__init__.py"

    def test_an_add_at_a0_is_accepted_and_runs_through_unchanged(self, tmp_path):
        for path in (tmp_path / "1", tmp_path / "2"):
            path.mkdir()
        words = '"""The package."""'
        first = _step(tmp_path, 1, self.NAME, "", {"a0": words})
        assert first == words
        assert _step(tmp_path, 2, self.NAME, first, {"a0": words}) == first

    def test_adding_code_to_it_refuses(self):
        refused = proof_setter._prove(self.NAME, "", "value = 1\n", Path(self.NAME), [])
        assert refused is not None
        assert refused.step == "prove"
        assert "code-changed" in refused.why


@pytest.mark.parametrize(
    ("text", "alterations", "expected"),
    [
        (
            "/** M */\n/** F */\nfunction f() {}\n",
            {"a1": None},
            "/** M */\nfunction f() {}\n",
        ),
        (
            "/** M */\n/** F */\nfunction f() {}\n",
            {"a0": None},
            "/** F */\nfunction f() {}\n",
        ),
        ("/** F */\nfunction f() {}\n", {"a1": None}, "function f() {}\n"),
        (
            "function f() {}\nfunction g() {}\n/** Module. */\n",
            {"a0": "/** Module. */"},
            "/** Module. */\nfunction f() {}\nfunction g() {}\n/** Module. */\n",
        ),
        (
            "/** F */\nfunction f() {}\n",
            {"a0": "/** M */", "a1": None},
            "/** M */\nfunction f() {}\n",
        ),
    ],
    ids=[
        "drop-a1",
        "drop-a0",
        "lone-doc",
        "same-words-stand-below",
        "doc-replaced-by-a-new-a0",
    ],
)
def test_a_draft_is_accepted_on_where_its_text_landed(
    tmp_path, text, alterations, expected
):
    drafted, refused = _chain(tmp_path, "m.js", text, alterations)
    assert refused == []
    assert drafted[0].draft.read_text(encoding="utf-8") == expected


@pytest.mark.parametrize(
    ("text", "alterations", "why"),
    [
        (
            "/** M */\n",
            {"a1": "/** End. */"},
            "a1: on lines 2-2 the draft holds",
        ),
        (
            "let y;\n/** D */\n// c\n\n// m\n",
            {"a1": "// X"},
            "a1: on lines 2-2 the draft holds",
        ),
        (
            "function f() {}\n",
            {"a0": "/** M */\n/** N */"},
            "a0: on lines 1-2 the draft holds",
        ),
    ],
    ids=["merged-with-a-neighbour", "foot", "read-as-two"],
)
def test_text_with_no_paragraph_of_its_own_on_its_lines_is_refused(
    tmp_path, text, alterations, why
):
    drafted, refused = _chain(tmp_path, "m.js", text, alterations)
    assert drafted == []
    assert refused[0].step == "reread"
    assert refused[0].why.startswith(why)


def _draft_written_as(monkeypatch, wrong: str, spans: dict | None = None) -> None:
    """The compositor writes `wrong`, and reports `spans` if handed any."""

    def write(page, into):
        into.parent.mkdir(parents=True, exist_ok=True)
        into.write_bytes(wrong.encode("utf-8"))
        return into

    monkeypatch.setattr(compositor, "draft", write)
    if spans is not None:
        monkeypatch.setattr(compositor, "spans", lambda page: spans)


@pytest.mark.parametrize(
    ("alterations", "wrong", "why"),
    [
        (
            {"b1": "// new"},
            "// a\nlet x;\nlet y;\n// new\n// c\nlet z;\n",
            "b1: on lines",
        ),
        ({"b1": "// new"}, "// a\nlet x;\n// new\nlet y;\nlet z;\n", "the draft reads"),
        ({"b1": None}, "// a\nlet x;\n// b\nlet y;\n// c\nlet z;\n", "the draft reads"),
        ({"b1": None}, "// a\nlet x;\nlet y;\n// changed\nlet z;\n", "the draft reads"),
        ({"b1": None}, "// c\nlet x;\nlet y;\n// a\nlet z;\n", "the draft reads"),
    ],
    ids=[
        "landed-on-other-lines",
        "neighbour-gone",
        "dropped-text-still-there",
        "neighbour-changed",
        "neighbours-swapped",
    ],
)
def test_the_reread_asks_the_file_on_disk_not_the_compositor(
    tmp_path, monkeypatch, alterations, wrong, why
):
    text = "// a\nlet x;\n// b\nlet y;\n// c\nlet z;\n"
    assert _at(text, "m.js", "// b") == "b1"
    _draft_written_as(monkeypatch, wrong)
    drafted, refused = _chain(tmp_path, "m.js", text, alterations)
    assert drafted == []
    assert refused[0].step == "reread"
    assert why in refused[0].why


@pytest.mark.parametrize(
    ("name", "text", "wrong"),
    [
        (
            "m.js",
            "// a\nlet x;\n// b\nlet y;\n",
            "// A\nlet x;\nlet y;\n// b\n",
        ),
        (
            "m.py",
            "# a\nx = 1\n# b\ny = 2\n",
            "# A\nx = 1\ny = 2\n# b\n",
        ),
        (
            "m.rs",
            "// a\nconst X: i32 = 1;\n// b\nconst Y: i32 = 2;\n",
            "// A\nconst X: i32 = 1;\nconst Y: i32 = 2;\n// b\n",
        ),
    ],
    ids=["js", "py", "rs"],
)
def test_an_unedited_comment_moved_across_a_code_line_is_refused(
    tmp_path, monkeypatch, name, text, wrong
):
    upper = wrong.splitlines()[0]
    alteration = {_at(text, name, upper.lower()): upper}
    _draft_written_as(monkeypatch, wrong)
    drafted, refused = _chain(tmp_path, name, text, alteration)
    assert drafted == []
    assert refused[0].step == "reread"
    assert "the draft reads" in refused[0].why


@pytest.mark.parametrize(
    ("text", "alterations", "wrong", "spans"),
    [
        (
            "// a\nlet x;\n// b\nlet y;\n// c\nlet z; // d\nlet w;\n",
            {"b1": "// B", "b2": "// C"},
            "// a\nlet x;\n// C\nlet y;\n// B\nlet z; // d\nlet w;\n",
            {"b1": (5, 5), "b2": (3, 3)},
        ),
        (
            "function f() {}\nfunction g() {}\n",
            {"a2": "/** G */"},
            "/** G */\nfunction f() {}\nfunction g() {}\n",
            {"a2": (1, 1)},
        ),
    ],
    ids=["two-edits-swapped", "set-on-the-wrong-declaration"],
)
def test_text_where_the_spans_say_is_refused_if_that_is_not_its_place(
    tmp_path, monkeypatch, text, alterations, wrong, spans
):
    # Draft and spans agree, so only the count of code lines above can object.
    _draft_written_as(monkeypatch, wrong, spans)
    drafted, refused = _chain(tmp_path, "m.js", text, alterations)
    assert drafted == []
    assert refused[0].step == "reread"
    assert "code lines in the draft" in refused[0].why


@pytest.mark.parametrize(
    "wrong",
    [
        '# TOP\n"""Head.\n    Body.\n    """\nx = 1\n',
        '# TOP\n"""Head.\n\n\n    Body.\n    """\nx = 1\n',
    ],
    ids=["removed", "added"],
)
def test_a_blank_changed_inside_an_unedited_docstring_is_refused(
    tmp_path, monkeypatch, wrong
):
    text = '# top\n"""Head.\n\n    Body.\n    """\nx = 1\n'
    alteration = {_at(text, "m.py", "# top"): "# TOP"}
    _draft_written_as(monkeypatch, wrong)
    drafted, refused = _chain(tmp_path, "m.py", text, alteration)
    assert drafted == []
    assert refused[0].step == "reread"
    assert "the draft reads" in refused[0].why


def test_spans_missing_a_place_refuse_by_name(tmp_path, monkeypatch):
    text = "let x;\n// a\nlet y;\n"
    _draft_written_as(monkeypatch, text.replace("// a", "// A"), {})
    drafted, refused = _chain(tmp_path, "m.js", text, {"b1": "// A"})
    assert drafted == []
    assert (refused[0].step, refused[0].why) == (
        "reread",
        "b1: the compositor set no lines for this place",
    )


@pytest.mark.parametrize(
    ("name", "text", "alterations"),
    [
        (
            "m.js",
            "/** D */\nlet x;\n\n/** A */\n\n// b\n\n// c\nlet y;\n",
            {"a1": None},
        ),
        (
            "m.py",
            '#!/usr/bin/env python\n"""M."""\n\n# note\n\n# more\nx = 1\n',
            {"a0": None},
        ),
    ],
    ids=["js", "py"],
)
def test_a_drop_beside_blank_separated_comments_is_accepted(
    tmp_path, name, text, alterations
):
    drafted, refused = _chain(tmp_path, name, text, alterations)
    assert refused == []
    assert drafted


@pytest.mark.parametrize(
    ("name", "text", "alterations"),
    [
        ("m.js", "/** F */\nfunction f() {}\n", {"a1": "   "}),
        ("m.js", "let x;\n// a\nlet y;\n", {"b1": "\n\n"}),
        ("m.py", 'def f():\n    """D."""\n    return 1\n', {"a1": "    "}),
        ("m.js", "function f() {}\n", {"a0": "   "}),
        ("m.js", "let x; // m\n", {"c0": "   "}),
    ],
    ids=["doc", "comment", "docstring", "empty-place", "margin"],
)
def test_white_space_is_not_a_way_to_spell_a_drop(tmp_path, name, text, alterations):
    drafted, refused = _chain(tmp_path, name, text, alterations)
    assert drafted == []
    assert refused[0].step == "reread"


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
    binder = bind(
        [build(SAMPLE, "pkg/d.py"), build(SAMPLE, "n.py")],
        read_from={"root": str(repo), "revise": 0},
    )
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
    binder = bind(
        [build(SAMPLE, "pkg/d.py")], read_from={"root": str(repo), "revise": 0}
    )
    into = tmp_path / "out"

    _fail_the_draft_of(monkeypatch, "d.py", "simulated: the draft could not be written")

    with pytest.raises(PermissionError):
        proof_setter.run(
            docket_from({address(binder, "pkg/d.py"): "# REPLACED"}, binder), repo, into
        )

    assert list(into.iterdir()) == []
