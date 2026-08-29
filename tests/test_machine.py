"""What the checkout says, and the identity of what was read.

! THE SHA IS TAKEN AT THE READ because this tree has two readers and they
disagree. A sha taken downstream of whichever reader a consumer happened to use
answers WHICH READER RAN, not whether the file changed.
"""

from conftest import SRC  # noqa: F401  -- conftest puts src on the path

from comment_review.machine.repo import Source, read_raw, read_source, sha_of

CRLF = b"# one\r\ndef f():\r\n    return 1\r\n"


def test_the_two_readers_disagree_on_a_crlf_file(tmp_path):
    p = tmp_path / "crlf.py"
    p.write_bytes(CRLF)
    assert read_raw(p) != p.read_text(encoding="utf-8")


def test_the_sha_is_of_the_untranslated_text(tmp_path):
    p = tmp_path / "crlf.py"
    p.write_bytes(CRLF)
    got = read_source(p)
    assert got.sha == sha_of(got.text)
    assert got.sha != sha_of(p.read_text(encoding="utf-8"))


def test_the_text_and_the_sha_arrive_together(tmp_path):
    p = tmp_path / "crlf.py"
    p.write_bytes(CRLF)
    assert isinstance(read_source(p), Source)


def test_the_same_bytes_answer_the_same_sha(tmp_path):
    one, two = tmp_path / "a.py", tmp_path / "b.py"
    one.write_bytes(CRLF)
    two.write_bytes(CRLF)
    assert read_source(one).sha == read_source(two).sha


def test_one_changed_byte_changes_the_sha(tmp_path):
    p = tmp_path / "a.py"
    p.write_bytes(CRLF)
    before = read_source(p).sha
    p.write_bytes(CRLF.replace(b"return 1", b"return 2"))
    assert read_source(p).sha != before
