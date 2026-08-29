"""`taken_in`: the original against the revise a role is holding.

`docs/plans/0.2.4-the-mark-and-the-collator.md` T2.6 and T5.2.
`TODO/the-flow-assumes-every-role-reads-at-once.md` T6.
"""

from helpers import a_docket_over, a_small_real_tree, binder_of

from comment_review.binder.binder import rows_of
from comment_review.commands.taken_in import main
from comment_review.flows.revise import pull


def test_taken_in_prints_nothing_when_no_stage_has_set_anything(tmp_path, capsys):
    repo = a_small_real_tree(tmp_path)
    assert main(["--original", str(repo), "--revise", str(repo)]) == 0
    assert capsys.readouterr().out.strip() == ""


def test_taken_in_shows_a_real_revise(tmp_path, capsys):
    """A real docket, pulled through `flows.revise.pull` -- never a
    hand-authored before/after pair, per `CLAUDE.md`'s ruling on this suite."""
    repo = a_small_real_tree(tmp_path)
    pulled = pull(a_docket_over(repo, ["mark.py"]), repo, tmp_path / "r1", revise=1)
    assert not pulled.refusals

    exit_code = main(["--original", str(repo), "--revise", str(pulled.root)])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "--- mark.py" in out
    assert "+++ mark.py" in out
    assert "revised by a_docket_over" in out
    # !! HONEST ABOUT THE GAP -- `flows/revise.py`'s `Pulled.set_by` maps no
    # role today (no docket field produces one); this command never receives
    # a `Pulled` at all, so it states the gap rather than printing a blank.
    assert "role not tracked" in out


def test_an_unreadable_root_is_nonzero(tmp_path, capsys):
    repo = a_small_real_tree(tmp_path)
    assert main(["--original", str(tmp_path / "nope"), "--revise", str(repo)]) == 2
    assert "CANNOT READ" in capsys.readouterr().out


def test_an_address_that_disappeared_is_listed(tmp_path, capsys):
    # !! THE COMPREHENSION WALKED `after_rows` ALONE UNTIL 2026-08-28, so an
    # address in the ORIGINAL and GONE from the revise was never listed. This
    # module's docstring promises "one line per address whose row-level text
    # differs between the two roots", and an address that stopped existing
    # differs. ! The unified diff showed the loss; the address list did not.
    repo = a_small_real_tree(tmp_path)
    revise = tmp_path / "r1"
    revise.mkdir()
    for page in repo.glob("*.py"):
        (revise / page.name).write_text(
            page.read_text(encoding="utf-8"), encoding="utf-8", newline=""
        )
    # ! A comment REMOVED from the revise -- the shape a `drop` sets.
    target = revise / "mark.py"
    kept = [ln for ln in target.read_text(encoding="utf-8").splitlines(True)
            if not ln.lstrip().startswith("# ")]
    target.write_text("".join(kept), encoding="utf-8", newline="")

    # ! THE EXPECTATION COMES FROM THE BINDER, NOT FROM `taken_in`. Asserting
    # merely that SOME address was printed passed under the old code too --
    # removing comment lines renumbers the places below them, so other
    # addresses change anyway. What only the union can answer is the set that
    # DISAPPEARED, so that set is what is named.
    before = {r["address"] for r in rows_of(binder_of(repo, 0))}
    after = {r["address"] for r in rows_of(binder_of(revise, 1))}
    gone = before - after
    assert gone, "the fixture removed no address -- the test would be vacuous"

    assert main(["--original", str(repo), "--revise", str(revise)]) == 0
    out = capsys.readouterr().out
    missing = [address for address in gone if address not in out]
    assert not missing, f"addresses that disappeared were never listed: {missing}"


def test_a_page_that_cannot_be_read_is_named_not_skipped(tmp_path, capsys):
    # !! THE DEFECT THIS PINS: `source_of`'s reason was discarded into `_` and
    # the loop did a bare `continue`, so a page that could not be read produced
    # NO OUTPUT AND EXIT 0 -- which is this command's own success condition
    # above. "nothing changed" and "I could not look" were the same result.
    repo = a_small_real_tree(tmp_path)
    pulled = pull(a_docket_over(repo, ["mark.py"]), repo, tmp_path / "r1", revise=1)
    # ! The page is removed from the REVISE, so the original still names it and
    # the pair cannot be compared -- the shape a half-copied tree would take.
    (pulled.root / "mark.py").unlink()

    exit_code = main(["--original", str(repo), "--revise", str(pulled.root)])
    seen = capsys.readouterr()

    # ! Exit stays 0 and STDOUT stays clean: the rule is nonzero when a ROOT is
    # unreadable, and T2.6 requires the DIFF to be empty when nothing was set.
    assert exit_code == 0
    assert "mark.py" not in seen.out
    # ! ...and the page is named on stderr, which is what makes it not a skip.
    assert "NOT COMPARED" in seen.err
    assert "mark.py" in seen.err


def test_a_page_with_no_language_record_is_named_after_its_diff(tmp_path, capsys):
    # ! THE SECOND SKIP, and it needs a different trigger from the one above:
    # `page_of` returns None only for a suffix no language record covers.
    # MEASURED -- a syntax error, an empty file and binary bytes all still make
    # a page. `_every_page` filters these out, so this path is reached only when
    # a caller NAMES the file, which is why the paths argument exists.
    repo = a_small_real_tree(tmp_path)
    revise = tmp_path / "r1"
    revise.mkdir()
    (repo / "notes.xyzzy").write_text("before\n", encoding="utf-8", newline="")
    (revise / "notes.xyzzy").write_text("after\n", encoding="utf-8", newline="")

    exit_code = main(
        ["--original", str(repo), "--revise", str(revise), "notes.xyzzy"]
    )
    seen = capsys.readouterr()

    # ! THE DIFF IS STILL PRINTED -- two texts differ and `differences.unified`
    # needs no language. What cannot be done is the ADDRESS comparison, and that
    # is the half that is named.
    assert "--- notes.xyzzy" in seen.out
    assert exit_code == 0
    assert "NOT COMPARED" in seen.err
    assert "addresses not compared" in seen.err


def test_taken_in_is_a_named_command():
    from comment_review.__main__ import COMMANDS

    assert "taken_in" in COMMANDS
