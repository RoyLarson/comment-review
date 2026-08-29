"""`commands/proof.py`: the CLI's console face over `flows/proof_setter.run`.

Moved from `tests/test_proof_setter.py` 2026-08-26 -- `tests/test_addresser_command.py`
is the standing precedent for a command's own file.
"""

from conftest import SAMPLE, SRC, build, by_cue

from comment_review.binder.binder import bind


def _tree(tmp_path):
    """A one-file repo, and the binder taken over it."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page = build(SAMPLE)
    return repo, bind([page], read_from={"root": str(repo), "revise": 0}), page


class TestTheCommand:
    """`commands/proof.py` exposes this flow and orchestrates nothing: it takes
    a binder and hands it straight to `proof_setter.run`.

    ! `galley` IS THE OLD NAME FOR IT since 2026-08-26. It used to resolve an
    address through `rows_of(census)` -- the binder-row coupling this chain was
    ruled out of -- and keep a staleness comparison, an overlap guard and a
    draft loop of its own; all of it went, and the name now runs this chain.
    See `docs/history.md`."""

    def test_galley_DELEGATES_to_proof(self, monkeypatch):
        """`SKILL.md` still invokes `galley` at stage 7a, so the name has to
        reach the chain -- `__main__.ALIASES` maps it to `proof` and imports
        that module, rather than a `commands/galley.py` of its own. ! It does
        NOT make a skill run work: the flags differ -- `--census`/`--edits`
        against `--binder`/`--docket` -- which is
        `TODO/the-skill-names-commands-that-moved-to-prototype.md`."""
        from comment_review.__main__ import ALIASES, COMMANDS, main
        from comment_review.commands import proof

        assert "galley" not in COMMANDS
        assert ALIASES["galley"] == "proof"
        called: list[bool] = []
        monkeypatch.setattr(proof, "main", lambda: called.append(True) or 7)
        assert main(["galley"]) == 7
        assert called == [True]

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

    def test_A_VALID_RUN_READS_THE_DOCKET_AND_DRAFTS(
        self, tmp_path, capsys, monkeypatch
    ):
        """!! THE HAPPY PATH HAD NO TEST UNTIL 2026-08-26, and the two argv
        cases below are why it looked covered: both stop at the `--out` guard,
        which returns 2 BEFORE the docket is read. So nothing exercised the
        line that turns an argparse flag into an attribute.

        !! MEASURED THE SAME DAY: renaming `--notations` to `--docket` left the
        body reading `args.alterations`, and `cmd.main()` raised
        `AttributeError: 'Namespace' object has no attribute 'alterations'` --
        past 946 green tests, ruff, ty, the build gate and the floor check. It
        was found by running the command, which is the only thing that could.

        ! THE DOCKET IS HAND-WRITTEN, like every one in `test_docket.py`: it
        arrives from outside the system, so a helper building it would only
        agree with the reader.
        """
        import json

        from comment_review.commands import proof as cmd

        repo, _, page = _tree(tmp_path)
        # ! DISCOVERED FROM THE PAGE, never hardcoded -- a literal cue is a
        # fixture asserting what the walk emitted last time someone looked.
        cue = next(
            c
            for c, b in by_cue(page).items()
            if c.startswith("b") and any(x.strip() for x in b.raw_lines)
        )
        (tmp_path / "d.json").write_text(
            json.dumps(
                {
                    "pages": [
                        {
                            "path": "m.py",
                            "sha": page.sha,
                            "alterations": [{"cue": cue, "text": "# REWRITTEN"}],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(
            "sys.argv",
            [
                "proof",
                "--repo",
                str(repo),
                "--docket",
                str(tmp_path / "d.json"),
                "--out",
                str(tmp_path / "out"),
            ],
        )
        assert cmd.main() == 0
        assert "drafted for review" in capsys.readouterr().out
        drafted = (tmp_path / "out" / "m.py").read_text(encoding="utf-8")
        assert "# REWRITTEN" in drafted
        # ! AND THE SOURCE IS UNTOUCHED, which is the whole promise of a draft.
        assert (repo / "m.py").read_text(encoding="utf-8") == SAMPLE

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
                "--docket",
                "n.json",
                "--out",
                str(repo / "inside"),
            ],
        )
        assert cmd.main() == 2
        assert "REFUSED" in capsys.readouterr().out

    def test_an_out_that_NAMES_A_FILE_prints_a_reason(
        self, tmp_path, capsys, monkeypatch
    ):
        """IMPORTANT, measured 2026-08-25: `run`'s
        `into.mkdir(parents=True, exist_ok=True)` raises `FileExistsError` when
        `--out` names a regular file -- `exist_ok` covers an existing DIRECTORY
        only -- and it reached the console as a traceback. Every other bad
        input in this command prints a reason and returns 2."""
        from comment_review.commands import proof as cmd

        repo, _, _ = _tree(tmp_path)
        not_a_dir = tmp_path / "notadir"
        not_a_dir.write_text("x", encoding="utf-8")
        monkeypatch.setattr(
            "sys.argv",
            [
                "proof",
                "--repo",
                str(repo),
                "--docket",
                "n.json",
                "--out",
                str(not_a_dir),
            ],
        )
        assert cmd.main() == 2
        assert "is not a directory" in capsys.readouterr().out

    def test_an_out_that_ALREADY_EXISTS_is_REFUSED(self, tmp_path, capsys, monkeypatch):
        """!! `--out` IS THE REVISE ROOT SINCE 2026-08-28, and `revise.pull`
        copies `--repo` into it with `shutil.copytree`, which raises
        `FileExistsError` on a directory that is already there -- even an
        empty one, which `undraftable` (a non-directory or an overlap) does
        not refuse. The same convention as every other bad `--out` above:
        a reason printed at exit 2, not a traceback."""
        from comment_review.commands import proof as cmd

        repo, _, _ = _tree(tmp_path)
        already_there = tmp_path / "out"
        already_there.mkdir()
        monkeypatch.setattr(
            "sys.argv",
            [
                "proof",
                "--repo",
                str(repo),
                "--docket",
                "n.json",
                "--out",
                str(already_there),
            ],
        )
        assert cmd.main() == 2
        assert "already exists" in capsys.readouterr().out
