"""Exact source snapshots from filesystem and revision bytes."""

import hashlib
import subprocess
from pathlib import Path

import pytest
from conftest import SRC  # noqa: F401

from comment_review.machine import repo

CASES = [
    (b"", ""),
    (b"\xef\xbb\xbf", "\ufeff"),
    (b"\xef\xbb\xbf# text\r\n", "\ufeff# text\r\n"),
    (b"a\nb\n", "a\nb\n"),
    (b"a\r\nb\r\n", "a\r\nb\r\n"),
    (b"a\rb\r", "a\rb\r"),
    (b"a\r\nb\rc\n\tend  \t", "a\r\nb\rc\n\tend  \t"),
    (b"caf\xc3\xa9 e\xcc\x81 \xf0\x9f\x8c\xb1", "caf\u00e9 e\u0301 \U0001f331"),
    (b"a\x00b", "a\x00b"),
]


@pytest.mark.parametrize(("raw", "text"), CASES)
def test_sources_preserve_literal_bytes_and_identity(tmp_path, raw, text):
    path = tmp_path / "source.py"
    path.write_bytes(raw)
    identity = hashlib.sha256(raw).hexdigest()[:16]
    for source in (repo.source_from_bytes(raw), repo.read_source(path)):
        assert source.text == text
        assert source.text.encode("utf-8") == raw
        assert source.sha == identity
    assert repo.read_raw(path) == text


@pytest.mark.parametrize("raw", [b"\xff", b"\xc3", b"\xff\xfea\x00", b"\xfe\xff\x00a"])
def test_sources_reject_invalid_utf8(tmp_path, raw):
    path = tmp_path / "source.py"
    path.write_bytes(raw)
    for read in (
        lambda: repo.source_from_bytes(raw),
        lambda: repo.read_source(path),
        lambda: repo.read_raw(path),
    ):
        with pytest.raises(UnicodeDecodeError):
            read()


@pytest.mark.parametrize("reader", [repo.read_source, repo.read_raw])
def test_each_snapshot_reads_filesystem_bytes_once(tmp_path, monkeypatch, reader):
    path = tmp_path / "source.py"
    path.write_bytes(b"first\r\n")
    original = Path.read_bytes
    calls = []

    def read_bytes(self):
        calls.append(self)
        return original(self)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    first = reader(path)
    path.write_bytes(b"second\r")
    second = reader(path)
    assert calls == [path, path]
    assert (first.text if isinstance(first, repo.Source) else first) == "first\r\n"
    assert (second.text if isinstance(second, repo.Source) else second) == "second\r"


@pytest.fixture
def revision_repo(tmp_path):
    def run(*args):
        return subprocess.run(
            ["git", "-C", str(tmp_path), *args],
            capture_output=True,
            check=True,
            timeout=30,
        )

    run("init")
    run("config", "core.autocrlf", "false")
    folder = tmp_path / "nested"
    folder.mkdir()
    for index, (raw, _) in enumerate(CASES):
        (folder / f"source-{index}.py").write_bytes(raw)
    (folder / "invalid.py").write_bytes(b"\xff\xfea\x00")
    run("add", ".")
    run(
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        "Source fixtures",
    )
    return tmp_path


@pytest.mark.parametrize(("index", "case"), enumerate(CASES))
def test_revision_sources_preserve_literal_blob_bytes(revision_repo, index, case):
    raw, text = case
    for root, rel in [
        (revision_repo, f"nested/source-{index}.py"),
        (revision_repo / "nested", f"source-{index}.py"),
    ]:
        source = repo.read_revision_source(root, "HEAD", rel)
        assert source.text == text
        assert source.text.encode("utf-8") == raw
        assert source.sha == hashlib.sha256(raw).hexdigest()[:16]


@pytest.mark.parametrize(
    ("ref", "rel"), [("missing-ref", "nested/source-0.py"), ("HEAD", "missing.py")]
)
def test_missing_revision_or_path_raises(revision_repo, ref, rel):
    with pytest.raises(subprocess.CalledProcessError):
        repo.read_revision_source(revision_repo, ref, rel)


def test_revision_rejects_invalid_utf8(revision_repo):
    with pytest.raises(UnicodeDecodeError):
        repo.read_revision_source(revision_repo, "HEAD", "nested/invalid.py")


def test_metadata_git_helper_stays_text_and_reports_nonzero(revision_repo):
    result = repo.git(revision_repo, "ls-files")
    assert isinstance(result.stdout, str)
    assert "nested/source-0.py" in result.stdout.splitlines()
    assert repo.git(revision_repo, "show", "missing-ref:./missing.py").returncode != 0
