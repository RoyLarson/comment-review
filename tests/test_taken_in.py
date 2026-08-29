"""`taken_in`: the original against the revise a role is holding.

`docs/plans/0.2.4-the-mark-and-the-collator.md` T2.6 and T5.2.
`TODO/the-flow-assumes-every-role-reads-at-once.md` T6.
"""

from helpers import a_docket_over, a_small_real_tree

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


def test_taken_in_is_a_named_command():
    from comment_review.__main__ import COMMANDS

    assert "taken_in" in COMMANDS
