"""What the checkout says, and the identity of what was read.

! THE SHA IS TAKEN AT THE READ because this tree has two readers and they
disagree. A sha taken downstream of whichever reader a consumer happened to use
answers WHICH READER RAN, not whether the file changed.
"""

import shutil
import stat

import pytest
from conftest import SRC  # noqa: F401  -- conftest puts src on the path

from comment_review.machine.repo import (
    Source,
    can_escape,
    read_raw,
    read_source,
    remove_tree,
    sha_of,
)

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


# --------------------------------------------------------------------------
# `can_escape` -- a question about the string, asked of a page path and of the
# `path` half of a citation.


def test_a_relative_page_path_does_not_escape():
    assert not can_escape("pkg/d.py")


def test_an_absolute_path_escapes():
    # `Path(root) / "/etc/passwd"` is `/etc/passwd` -- pathlib discards the
    # left operand -- and the same holds for a drive-qualified Windows path.
    assert can_escape("/etc/passwd")
    assert can_escape("C:/Windows/system.ini")


def test_a_drive_relative_path_escapes():
    # `Path("C:util.py").is_absolute()` is False, and it still carries a drive.
    assert can_escape("C:util.py")


def test_a_path_that_walks_up_escapes():
    assert can_escape("../outside/secrets.txt")


# --------------------------------------------------------------------------
# `remove_tree`


def _a_tree_holding_a_read_only_file(root):
    """A directory whose one file carries no write bit -- the mode git writes
    loose objects and packs under `.git/objects` with, which is what a
    `shutil.copytree` of a checkout reproduces."""
    root.mkdir()
    kept = root / "object"
    kept.write_bytes(b"contents\n")
    kept.chmod(stat.S_IREAD)
    return root


def test_remove_tree_deletes_a_tree_the_platform_refuses_to_unlink(tmp_path):
    """! THE PRECONDITION IS ASSERTED, NOT ASSUMED. `shutil.rmtree` is run over
    an identical tree first: where it succeeds, this platform does not enforce
    the read-only bit against unlink and the defect cannot arise there, so the
    case skips rather than passing on a machine it says nothing about."""
    probe = _a_tree_holding_a_read_only_file(tmp_path / "probe")
    try:
        shutil.rmtree(probe)
    except PermissionError:
        pass
    else:
        pytest.skip("this platform unlinks a read-only file; the defect cannot arise")

    tree = _a_tree_holding_a_read_only_file(tmp_path / "tree")
    remove_tree(tree)
    assert not tree.exists()
