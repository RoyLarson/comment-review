from dataclasses import replace
from importlib.resources import files

import pytest

from comment_review.reading.definitions import LanguageDefinition, decode_definition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.python import read_python
from comment_review.reading.python.preservation import compare_preservation
from comment_review.reading.python.records import PythonRead


@pytest.fixture(scope="module")
def definition():
    text = (
        files("comment_review")
        .joinpath("references/languages/python.toml")
        .read_text(encoding="utf-8")
    )
    result = decode_definition(text)
    assert isinstance(result, LanguageDefinition)
    return result


def acquired(text, definition):
    result = read_python(text, definition)
    assert isinstance(result, PythonRead), result
    return result


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("", "# note\n\n"),
        ("x=1", "x=1\n# note\n"),
        ("x=1 # old\ny=2\n", "# heading\nx=1\n\n# detail\ny=2 # new"),
        ("x=1  \n", "x=1\t# note\n"),
        ("x=1\r\ny=2\r\n", "x=1\ry=2\n"),
        ('"old prose"\nx=1\n', 'r"""New\nprose."""\nx=1\n'),
        ('"a" "b"\nx=1\n', '"completely rewritten"\nx=1\n'),
        ('("old"); x=1\n', '("new"); x=1 # note\n'),
        (
            'def run(value):\n    "old"\n    return value\n',
            '# heading\ndef run(value):\n    """New\n    prose."""\n'
            "    # detail\n    return value # note\n",
        ),
        (
            "x = (\n # ordinary\n 1\n) # type: int\n",
            "x = (\n # rewritten ordinary\n 1\n) # type: int\n",
        ),
        ("x=1 # type: int\ny=2\n", "# head\nx=1 # type: int\n\ny=2\n"),
        ('x = f"{(\n value # old\n)}"\n', 'x = f"{(\n value # new\n)}"\n'),
        (
            'type Pair[T] = tuple[T, T]\n# old\nx = t"{value}"\n',
            'type Pair[T] = tuple[T, T]\n# new\nx = t"{value}"\n',
        ),
        (
            'value="""literal\n\n  exact  \n"""\n# old\n',
            'value="""literal\n\n  exact  \n"""\n# new\n',
        ),
    ],
)
def test_editorial_changes_preserve_code(definition, before, after):
    result = compare_preservation(
        acquired(before, definition), acquired(after, definition)
    )
    assert result.unchanged, result.diagnostics
    assert result.diagnostics == ()


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("x=1\n", "y=1\n"),
        ("x=1\n", "x=2\n"),
        ("x=0x10\n", "x=16\n"),
        ("x=1+2\n", "x=1-2\n"),
        ("return value\n", "yield value\n"),
        ("x=1; y=2\n", "x=1\ny=2\n"),
        ("x=1\ny=2\n", "y=2\nx=1\n"),
        ("x = 1\n", "x=1\n"),
        ("if ready:\n    act()\n", "if ready:\n\tact()\n"),
        ("x=1 # boundary\ny=2\n", "x=1y=2\n"),
        ('x="old"\n', 'x="new"\n'),
        ('x="# old"\n', 'x="# new"\n'),
        ('x=r"raw"\n', 'x="raw"\n'),
        ('x="same"\n', "x='same'\n"),
        ('x="""a\n\nb"""\n', 'x="""a\nb"""\n'),
        ('x="""a  \nb"""\n', 'x="""a\nb"""\n'),
        ('x="""a\r\nb"""\n', 'x="""a\nb"""\n'),
        ('x=f"literal {value}"\n', 'x=f"changed {value}"\n'),
        ('x=f"{value}"\n', 'x=f"{other}"\n'),
        ('x=f"{value + 1}"\n', 'x=f"{value+1}"\n'),
        ('x=f"{ value =}"\n', 'x=f"{value =}"\n'),
        ('x=f"{value=  }"\n', 'x=f"{value= }"\n'),
        ('x=f"{(\n value # old\n)=}"\n', 'x=f"{(\n value # new\n)=}"\n'),
        ('x=t"{ value }"\n', 'x=t"{value}"\n'),
        ('x=t"{(\n value # old\n)}"\n', 'x=t"{(\n value # new\n)}"\n'),
        ('x=t"{(\r\n value\r\n)}"\n', 'x=t"{(\n value\n)}"\n'),
        ('"doc"\nx=1\n', "x=1\n"),
        ("x=1\n", '"doc"\nx=1\n'),
        ('"first"\n"later"\nx=1\n', '"rewritten later"\nx=1\n'),
        (
            'def a():\n    "doc"\n    pass\ndef b():\n    pass\n',
            'def a():\n    pass\ndef b():\n    "doc"\n    pass\n',
        ),
        ('"doc"; x=1\n', '"new"\nx=1\n'),
        ('("doc")\nx=1\n', '"new"\nx=1\n'),
        ("#!/usr/bin/python\nx=1\n", "#!/usr/bin/python3\nx=1\n"),
        ("#!/usr/bin/python\nx=1\n", "# head\n#!/usr/bin/python\nx=1\n"),
        ("# coding: utf-8\nx=1\n", "# coding: utf_8\nx=1\n"),
        ("x=1 # type: int\n", "x=1 # type: str\n"),
        ("x=1 # type: int\ny=2\n", "x=1\ny=2 # type: int\n"),
        ("x=1 # type: ignore\nx=1\n", "x=1\nx=1 # type: ignore\n"),
        ("x=(1 # type: ignore\n + 2)\n", "x=(1\n + 2) # type: ignore\n"),
    ],
)
def test_executable_and_protected_changes_fail(definition, before, after):
    result = compare_preservation(
        acquired(before, definition), acquired(after, definition)
    )
    assert not result.unchanged
    assert result.diagnostics


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("x=1 # type: int\n", "x=1# type: int\n"),
        ("x=1 # type: ignore\n", "x=1\t# type: ignore\n"),
        ("# type: int\nx=1\n", "  # type: int\nx=1\n"),
        (" # type: ignore\nx=1\n", "\t# type: ignore\nx=1\n"),
        ("# coding: utf-8\nx=1\n", " # coding: utf-8\nx=1\n"),
        (
            "def run():\n    # type: () -> int\n    pass\n",
            "def run():\n  # type: () -> int\n    pass\n",
        ),
    ],
)
def test_spacing_before_protected_comments_remains_exact(definition, before, after):
    was, now = acquired(before, definition), acquired(after, definition)
    assert was.protected and now.protected
    for original, changed in ((was, now), (now, was)):
        result = compare_preservation(original, changed)
        assert not result.unchanged
        assert result.diagnostics


def test_failures_never_compare_successfully(definition):
    failure = read_python('x="unterminated', definition)
    assert isinstance(failure, ReadFailure)
    good = acquired("x=1\n", definition)
    for before, after in ((failure, good), (good, failure), (failure, failure)):
        result = compare_preservation(before, after)
        assert not result.unchanged
        assert failure.diagnostics[0] in result.diagnostics


def test_retained_owner_links_are_compared(definition):
    before = acquired('def a():\n    "old"\n    pass\ndef b():\n    pass\n', definition)
    owner = replace(before.source.documentation[0], declaration=1)
    payload = replace(
        before.payloads[0],
        expression=replace(before.payloads[0].expression, declaration=1),
    )
    after = replace(
        before,
        source=replace(before.source, documentation=(owner,)),
        payloads=(payload,),
    )
    assert not compare_preservation(before, after).unchanged


def test_retained_declaration_context_is_compared(definition):
    before = acquired('def run():\n    "doc"\n    pass\n', definition)
    declaration = replace(before.source.declarations[0], kind="class")
    after = replace(before, source=replace(before.source, declarations=(declaration,)))
    result = compare_preservation(before, after)
    assert not result.unchanged
    assert result.diagnostics[0].code == "declaration-changed"


def test_comparison_uses_acquired_source_only(definition, monkeypatch):
    from comment_review.reading import python
    from comment_review.reading.python import scanner

    before = acquired('"old"\nx=1 # old\n', definition)
    after = acquired('"new"\nx=1 # new\n', definition)

    def forbidden(*args, **kwargs):
        pytest.fail("comparison reacquired Python source")

    monkeypatch.setattr(python, "read_python", forbidden)
    monkeypatch.setattr(scanner, "scan_python", forbidden)
    assert compare_preservation(before, after).unchanged
