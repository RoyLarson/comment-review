"""`commands/referrers.py`: which tracked files name the files under review.

Inputs are a real git checkout in `tmp_path`, built through `git_in`, because
the search is `git grep` over the index.
"""

import pytest
from conftest import run_command
from helpers import git_in

from comment_review.commands import referrers as referrers_command
from comment_review.constants import BYTE_ORDER_MARK
from comment_review.flows.referrers import files_naming


def a_checkout(root, files):
    """A git checkout at `root` tracking `files`, a name -> text map."""
    git_in(root, "init", "-q")
    for name, text in files.items():
        (root / name).write_text(text, encoding="utf-8", newline="")
    git_in(root, "add", "-A")
    return root


def test_a_bom_file_still_yields_its_public_names(tmp_path, monkeypatch, capsys):
    repo = a_checkout(
        tmp_path,
        {
            "target.py": BYTE_ORDER_MARK + "def harvested():\n    pass\n",
            "cites.md": "See `harvested` for the rule.\n",
        },
    )
    status, out = run_command(
        monkeypatch,
        capsys,
        referrers_command,
        "--repo",
        str(repo),
        str(repo / "target.py"),
    )
    assert status == 0
    assert "cites.md\n      names: harvested" in out


def test_a_run_that_fails_leaves_no_out_file(tmp_path, monkeypatch, capsys):
    repo = a_checkout(tmp_path, {"target.py": "def harvested():\n    pass\n"})

    def fails(*args):
        raise RuntimeError("the search broke")

    monkeypatch.setattr(referrers_command, "files_naming", fails)
    out = tmp_path / "referrers.txt"
    with pytest.raises(RuntimeError):
        run_command(
            monkeypatch,
            capsys,
            referrers_command,
            "--repo",
            str(repo),
            "--out",
            str(out),
            str(repo / "target.py"),
        )
    assert not out.exists()


def test_files_naming_lists_an_awkward_name_verbatim(tmp_path):
    name = 'a\t"b".md'
    try:
        repo = a_checkout(tmp_path, {name: "harvested\n"})
    except OSError:
        pytest.skip("this filesystem refuses a tab or a quote in a file name")
    assert files_naming(repo, "harvested") == ([name], "")
