"""Finding the commits whose prose moved and whose code did not.

! THE INPUT IS A REAL GIT REPOSITORY, built per test and committed through git
itself. A hand-written table of "what git would say" could only confirm what
this file already believes, and the thing under test is precisely the reading
of real history.
"""

import subprocess

import prose_commits
import pytest

CODE = '''\
def add(a, b):
    """Add two numbers."""
    # the sum
    return a + b
'''

PROSE_MOVED = '''\
def add(a, b):
    """Return the sum of a and b."""
    # ! the sum, and it is not checked for overflow
    return a + b
'''

CODE_MOVED = '''\
def add(a, b):
    """Add two numbers."""
    # the sum
    return b + a
'''

REFLOWED = '''\
def add(a, b):
    """Add two numbers."""
    # the sum,
    # wrapped onto two lines now
    return a + b
'''


@pytest.fixture
def repo(tmp_path):
    """A git repository with one committed file."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "t@example.com"], cwd=tmp_path, check=True
    )
    subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, check=True)
    (tmp_path / "m.py").write_text(CODE, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "first"], cwd=tmp_path, check=True)
    return tmp_path


def _commit(repo, message, **files):
    for name, text in files.items():
        (repo / name.replace("_", ".")).write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", message], cwd=repo, check=True)


def test_a_commit_that_moves_only_prose_is_found(repo):
    _commit(repo, "docs: say what it returns", m_py=PROSE_MOVED)

    found = prose_commits.scan(repo)

    assert len(found) == 1
    assert found[0].subject == "docs: say what it returns"
    assert found[0].paths == ("m.py",)


def test_a_commit_that_moves_code_is_not(repo):
    """`return b + a` is a different program, however small the diff."""
    _commit(repo, "swap the operands", m_py=CODE_MOVED)

    assert prose_commits.scan(repo) == []


def test_a_commit_moving_both_is_not_a_key(repo):
    """The grade could not tell a prose finding from the code half's reason."""
    both = CODE_MOVED.replace('"""Add two numbers."""', '"""Return the sum."""')
    _commit(repo, "docs and a swap", m_py=both)

    assert prose_commits.scan(repo) == []


def test_a_new_file_is_not_a_prose_edit(repo):
    """There is no before to compare, and its whole body is unreviewed code."""
    _commit(repo, "add a module", other_py=CODE)

    assert prose_commits.scan(repo) == []


def test_a_commit_touching_a_non_python_file_is_skipped(repo):
    """Its key would span two kinds of file; the census reads one."""
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    _commit(repo, "docs and a readme", m_py=PROSE_MOVED)

    assert prose_commits.scan(repo) == []


def test_a_comment_reflowed_onto_more_lines_is_still_prose_only(repo):
    """The line COUNT moves and the code does not, which is the common shape.

    ! This is what most real prose commits in this repo look like -- a
    paragraph grows, every following line shifts down, and not one executable
    statement changes.
    """
    _commit(repo, "reflow the comment", m_py=REFLOWED)

    found = prose_commits.scan(repo)

    assert len(found) == 1
    assert found[0].subject == "reflow the comment"


def test_the_pair_is_START_then_END_and_START_is_the_parent(repo):
    """A case is graded from START; naming them backwards inverts every run."""
    _commit(repo, "docs: say what it returns", m_py=PROSE_MOVED)
    found = prose_commits.scan(repo)[0]

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
    ).stdout.strip()
    parent = subprocess.run(
        ["git", "rev-parse", "HEAD^"], cwd=repo, capture_output=True, text=True
    ).stdout.strip()

    assert found.end == head
    assert found.start == parent


def test_prose_only_answers_False_for_a_file_that_will_not_parse(repo):
    """History holds broken states; one must not stop the survey."""
    _commit(repo, "broken", m_py="def add(a, b:\n")

    # ! It returns rather than raising, so the scan completes.
    assert prose_commits.scan(repo) == []


def test_the_survey_reads_only_the_last_limit_commits(repo):
    _commit(repo, "docs: say what it returns", m_py=PROSE_MOVED)
    _commit(repo, "unrelated", other_txt="x")

    assert prose_commits.scan(repo, limit=1) == []
    assert len(prose_commits.scan(repo, limit=5)) == 1


def test_json_output_is_machine_readable(repo, capsys):
    """It is what a staging step would consume, so it must parse."""
    import json

    _commit(repo, "docs: say what it returns", m_py=PROSE_MOVED)

    assert prose_commits.main(["--repo", str(repo), "--json"]) == 0

    rows = json.loads(capsys.readouterr().out)
    assert rows[0]["subject"] == "docs: say what it returns"
    assert rows[0]["paths"] == ["m.py"]


def test_it_always_exits_zero_because_it_is_an_input_not_a_gate(repo, capsys):
    _commit(repo, "swap the operands", m_py=CODE_MOVED)

    assert prose_commits.main(["--repo", str(repo)]) == 0
    assert "0 prose-only commits" in capsys.readouterr().out
