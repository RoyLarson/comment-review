"""A stage's reads resolve against ITS OWN root, not the original's.

`TODO/the-flow-assumes-every-role-reads-at-once.md` T5, delivered by task 10 of
`.superpowers/sdd/2026-08-28-the-mark-and-the-revise/task-10-brief.md`.
"""

import argparse
import json

from helpers import a_docket_that_rewrites, a_small_real_tree, binder_of, the_row_for

from comment_review.commands import census as census_command
from comment_review.flows.revise import pull


def test_a_source_citing_an_edited_page_reads_the_revise(tmp_path):
    # `marks.py` imports from `mark.py`, so a source cite crosses between them
    # for real rather than by arrangement.
    repo = a_small_real_tree(tmp_path)
    pulled = pull(
        a_docket_that_rewrites(repo, "mark.py"), repo, tmp_path / "r1", revise=1
    )
    row = the_row_for(binder_of(pulled.root, 1), "mark.py")
    assert row["raw_text"] in (pulled.root / "mark.py").read_text(encoding="utf-8")
    assert row["raw_text"] not in (repo / "mark.py").read_text(encoding="utf-8")


def _census_args(repo, revise: int, paths: list[str]) -> argparse.Namespace:
    """The `argparse.Namespace` `commands.census._report` reads -- built
    directly rather than through `sys.argv`, since `_report` is the call
    site itself and the point is to force ITS `revise` handling, not
    argparse's.
    """
    return argparse.Namespace(
        languages=False,
        paths=paths,
        repo=str(repo),
        json=True,
        filtered=False,
        include_matter=False,
        include_absent=False,
        revise=revise,
    )


def test_the_census_command_states_the_revise_it_read(tmp_path, capsys, monkeypatch):
    """`commands/census.py --json` wrote `"revise": 0` into `read_from`
    unconditionally -- MEASURED, no `--revise` argument existed at all, so a
    stage censusing a revise still reported the ORIGINAL's number, which is
    indistinguishable from having read the original.
    """
    repo = a_small_real_tree(tmp_path)
    pulled = pull(
        a_docket_that_rewrites(repo, "mark.py"), repo, tmp_path / "r1", revise=1
    )
    # !! THE CWD IS NOT THE ROOT, AND IT WAS `chdir(pulled.root)` UNTIL
    # 2026-08-28. MEASURED by mutation: with the two equal, replacing
    # `Path(args.repo)` with `Path.cwd()` in the command left this test GREEN --
    # so the test could not tell whether the census honoured the root it was
    # GIVEN or merely read where it happened to be standing, which is the one
    # question T2.5 exists to answer. ! Standing one directory up is what makes
    # the two distinguishable; `--repo` is then a real choice.
    monkeypatch.chdir(tmp_path)
    exit_code = census_command._report(
        _census_args(pulled.root, revise=1, paths=[str(pulled.root / "mark.py")])
    )
    assert exit_code == 0
    binder = json.loads(capsys.readouterr().out)
    assert binder["read_from"]["revise"] == 1
    # ! THE RECORDED ROOT IS ASSERTED, and nothing asserted it until the same
    # day: a fixed string in place of the computed root passed every check here.
    # Resolved on both sides, because the field is now written RELATIVE to the
    # cwd (`Process`, Roy 2026-08-28) and a string compare would be asserting
    # the spelling rather than the place.
    recorded = (tmp_path / binder["read_from"]["root"]).resolve()
    assert recorded == pulled.root.resolve()
    row = the_row_for(binder, "mark.py")
    assert row["raw_text"] in (pulled.root / "mark.py").read_text(encoding="utf-8")
    assert row["raw_text"] not in (repo / "mark.py").read_text(encoding="utf-8")
