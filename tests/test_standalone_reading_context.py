import subprocess

from conftest import run_command
from test_proof_command import proof_repository

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
    subprocess.run(
        ["git", "-C", str(repo), "add", "."],
        check=True,
        capture_output=True,
        timeout=30,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-m",
            "Mixed fixture",
        ],
        check=True,
        capture_output=True,
        timeout=30,
    )
    rust.write_bytes(b"const value = 1; // new\r\n")
    py.write_bytes(b"value = 1 # new\r\n")
    actual = page_for.page_for
    admitted = []

    def observe(path, text, *args, **kwargs):
        page = actual(path, text, *args, **kwargs)
        assert not isinstance(page, ReadFailure)
        admitted.append((path, text, page.reading))
        return page

    monkeypatch.setattr(page_for, "page_for", observe)
    code, out = run_command(
        monkeypatch,
        capsys,
        command,
        "--repo",
        str(repo),
        "--base",
        "HEAD",
        str(rust),
        str(py),
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
