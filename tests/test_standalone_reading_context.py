from conftest import run_command
from test_proof_command import draft_of, proof_repository, prove_args

from comment_review.commands import prove_unchanged as command
from comment_review.flows import page_for
from comment_review.reading.diagnostics import ReadFailure


def test_standalone_cli_proves_mixed_paths_each_under_its_own_context(
    tmp_path, monkeypatch, capsys
):
    suffix = ".rs"
    repo, rust = proof_repository(tmp_path, "const value = 1; // old\r\n", suffix)
    py = rust.with_suffix(".py")
    py.write_bytes(b"value = 1 # old\r\n")
    draft_of(repo, rust).write_bytes(b"const value = 1; // new\r\n")
    draft_of(repo, py).write_bytes(b"value = 1 # new\r\n")
    actual = page_for.page_for
    admitted = []

    def observe(path, text, *args, **kwargs):
        page = actual(path, text, *args, **kwargs)
        assert not isinstance(page, ReadFailure)
        admitted.append((path, text, page.reading))
        return page

    monkeypatch.setattr(page_for, "page_for", observe)
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(rust), str(py)
    )
    assert code == 0, out
    assert f"PROVEN    pkg/source{suffix}" in out
    assert "PROVEN    pkg/source.py" in out
    assert [item[1] for item in admitted] == [
        "const value = 1; // old\r\n",
        "const value = 1; // new\r\n",
        "value = 1 # old\r\n",
        "value = 1 # new\r\n",
    ]
    assert [item[2].language for item in admitted] == [
        "rust",
        "rust",
        "python",
        "python",
    ]
    assert admitted[0][2] == admitted[1][2]
    assert admitted[2][2] == admitted[3][2]
