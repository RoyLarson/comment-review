"""Exact source snapshots from filesystem and revision bytes."""

import hashlib
import subprocess
from pathlib import Path

import pytest
from conftest import SRC  # noqa: F401

from comment_review.machine import repo
from comment_review.reading.diagnostics import ReadFailure, ReadStage

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


@pytest.mark.parametrize(("raw", "text"), CASES)
def test_write_round_trip_preserves_bytes_and_creates_parents(tmp_path, raw, text):
    path = tmp_path / "nested" / "source.py"
    assert repo.write_raw(path, text) == path
    assert path.read_bytes() == raw
    assert repo.read_raw(path) == text


def test_invalid_output_preserves_target_and_creates_no_parent(tmp_path):
    existing = tmp_path / "existing.py"
    existing.write_bytes(b"unchanged\r\n")
    absent = tmp_path / "absent" / "source.py"
    for path in (existing, absent):
        with pytest.raises(UnicodeEncodeError):
            repo.write_raw(path, "prefix\ud800")
    assert existing.read_bytes() == b"unchanged\r\n"
    assert not absent.parent.exists()


def test_source_outcomes_separate_acquisition_and_decode(tmp_path):
    from comment_review.flows.source import source_of

    path = tmp_path / "source.py"
    missing = source_of(path)
    assert isinstance(missing, ReadFailure)
    assert missing.diagnostics[0].stage == ReadStage.ACQUIRE
    assert missing.diagnostics[0].code == "io-error"
    path.write_bytes(b"caf\xc3\xa9\xff")
    invalid = source_of(path)
    assert isinstance(invalid, ReadFailure)
    diagnostic = invalid.diagnostics[0]
    assert (diagnostic.stage, diagnostic.code, diagnostic.byte_offset) == (
        ReadStage.DECODE,
        "invalid-utf8",
        5,
    )
    from comment_review.flows.read_diagnostics import format_failure

    rendered = format_failure(invalid, path="source.py")
    assert "source.py decode/invalid-utf8" in rendered
    assert "byte offset 5, zero-based" in rendered
    path.write_bytes(b"")
    assert source_of(path) == repo.source_from_bytes(b"")


@pytest.mark.parametrize(
    ("ref", "rel"), [("missing-ref", "nested/source-0.py"), ("HEAD", "missing.py")]
)
def test_revision_failure_outcomes(revision_repo, ref, rel):
    from comment_review.flows.source import revision_source_of

    result = revision_source_of(revision_repo, ref, rel)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.ACQUIRE
    assert result.diagnostics[0].code == "missing-revision-source"
    assert result.diagnostics[0].message


def test_revision_empty_and_invalid_outcomes(revision_repo):
    from comment_review.flows.source import revision_source_of

    assert revision_source_of(revision_repo, "HEAD", "nested/source-0.py") == (
        repo.source_from_bytes(b"")
    )
    result = revision_source_of(revision_repo, "HEAD", "nested/invalid.py")
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.DECODE


def test_missing_repository_is_an_io_failure(tmp_path):
    from comment_review.flows.source import revision_source_of

    result = revision_source_of(tmp_path / "missing-repository", "HEAD", "a.py")
    assert isinstance(result, ReadFailure)
    diagnostic = result.diagnostics[0]
    assert (diagnostic.stage, diagnostic.code) == (ReadStage.ACQUIRE, "io-error")
    assert "cannot change to" in diagnostic.message


@pytest.mark.parametrize(
    "error",
    [
        OSError("denied"),
        subprocess.TimeoutExpired("git", 30),
        subprocess.SubprocessError("failed"),
    ],
)
@pytest.mark.parametrize("revision", [False, True])
def test_expected_acquisition_errors(tmp_path, monkeypatch, error, revision):
    from comment_review.flows import source

    def fail(*args):
        raise error

    monkeypatch.setattr(
        source, "read_revision_source" if revision else "read_source", fail
    )
    result = (
        source.revision_source_of(tmp_path, "HEAD", "a.py")
        if revision
        else source.source_of(tmp_path)
    )
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.ACQUIRE
    assert result.diagnostics[0].code == "io-error"


@pytest.mark.parametrize("error", [ValueError("bad argument"), RuntimeError("bug")])
def test_unexpected_errors_propagate(tmp_path, monkeypatch, error):
    from comment_review.flows import source

    def fail(*args):
        raise error

    monkeypatch.setattr(source, "read_source", fail)
    monkeypatch.setattr(source, "read_revision_source", fail)
    with pytest.raises(type(error)):
        source.source_of(tmp_path)
    with pytest.raises(type(error)):
        source.revision_source_of(tmp_path, "HEAD", "a.py")


@pytest.mark.parametrize("offset", [-1, 3, 9])
def test_decode_offset_must_be_inside_error_bytes(tmp_path, monkeypatch, offset):
    from comment_review.flows import source

    def fail(*args):
        raise UnicodeDecodeError("utf-8", b"abc", offset, offset + 1, "invalid")

    monkeypatch.setattr(source, "read_source", fail)
    result = source.source_of(tmp_path)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].byte_offset is None
