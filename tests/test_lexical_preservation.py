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


@pytest.mark.parametrize(
    ("bare", "documented", "owner"),
    [
        ("x=1\n", '("module"); x=1\n', None),
        ("", '"module"\n', None),
        ("def f():\n    return 1\n", 'def f():\n    ("doc");\n    return 1\n', 0),
        ("class C:\n    value=1\n", 'class C:\n    "doc"\n    value=1\n', 0),
        (
            "async def f():\n    return 1\n",
            'async def f():\n    "doc"\n    return 1\n',
            0,
        ),
        ("def f():\n", 'def f(): "doc"\n', 0),
        (
            "def same():\n    def same():\n        return 1\n    return same\n",
            'def same():\n    def same():\n        "doc"\n'
            "        return 1\n    return same\n",
            1,
        ),
        (
            "def same():\n    pass\ndef same():\n    pass\n",
            'def same():\n    pass\ndef same():\n    "doc"\n    pass\n',
            1,
        ),
    ],
)
def test_selected_documentation_additions_and_removals(
    definition, bare, documented, owner
):
    was, now = acquired(bare, definition), acquired(documented, definition)
    for before, after in ((was, now), (now, was)):
        assert not compare_preservation(before, after).unchanged
        result = compare_preservation(
            before, after, allowed_documentation_owners={owner}
        )
        assert result.unchanged, result.diagnostics


@pytest.mark.parametrize(
    "header, indent, owner", [("", "", None), ("def f():\n", "    ", 0)]
)
def test_promoted_ordinary_literal_keeps_its_exact_source(
    definition, header, indent, owner
):
    before = acquired(
        header
        + indent
        + '"docs"\n'
        + indent
        + '(r"ordinary");\n'
        + indent
        + '"last"\n',
        definition,
    )
    after = acquired(
        header + indent + '(r"ordinary");\n' + indent + '"last"\n', definition
    )
    assert compare_preservation(
        before, after, allowed_documentation_owners={owner}
    ).unchanged
    for replacement in [
        '("ordinary");\n"last"\n',
        '"last"\n',
        '"last"\n(r"ordinary");\n',
    ]:
        changed = acquired(
            header
            + "".join(indent + line for line in replacement.splitlines(keepends=True)),
            definition,
        )
        assert not compare_preservation(
            before, changed, allowed_documentation_owners={owner}
        ).unchanged


@pytest.mark.parametrize(
    ("before", "after", "owners"),
    [
        ('x="ordinary"\n', '"docs"\n', {None}),
        ('"docs"\n"ordinary"\n', '"changed"\n', {None}),
        ('"docs"\nx=1; y=2\n', '"new"\nx=1\ny=2\n', {None}),
        ('def f(): "docs"; return 1\n', 'def f():\n    "new"\n    return 1\n', {0}),
        ('def f():\n    "docs"\n', "def f():\n    pass\n", {0}),
        (
            "def a():\n    pass\ndef b():\n    pass\n",
            'def a():\n    "docs"\n    pass\ndef b():\n    pass\n',
            {1},
        ),
        ('"docs"\nx=1 # type: int\n', "x=1  # type: int\n", {None}),
        ('"docs" # type: ignore\nx=1\n', "x=1\n", {None}),
    ],
)
def test_selected_owners_do_not_permit_code_or_protection_changes(
    definition, before, after, owners
):
    was, now = acquired(before, definition), acquired(after, definition)
    for original, changed in ((was, now), (now, was)):
        assert not compare_preservation(
            original, changed, allowed_documentation_owners=owners
        ).unchanged


def test_selected_doc_only_inline_shape_can_relocate(definition):
    before = acquired('def f(): "docs"\n', definition)
    after = acquired('def f():\n    "new docs"\n', definition)
    for original, changed in ((before, after), (after, before)):
        assert compare_preservation(
            original, changed, allowed_documentation_owners={0}
        ).unchanged


@pytest.mark.parametrize("owner", [-1, 1, True, "f"])
def test_documentation_owner_must_exist_as_a_source_position(definition, owner):
    source = acquired("def f():\n    pass\n", definition)
    result = compare_preservation(source, source, allowed_documentation_owners={owner})
    assert not result.unchanged


def test_selected_comparison_does_not_reacquire(definition, monkeypatch):
    from comment_review.reading import python
    from comment_review.reading.python import scanner

    before, after = (
        acquired('"docs"\n"ordinary"\n', definition),
        acquired('"ordinary"\n', definition),
    )

    def forbidden(*args, **kwargs):
        pytest.fail("comparison reacquired Python source")

    monkeypatch.setattr(python, "read_python", forbidden)
    monkeypatch.setattr(scanner, "scan_python", forbidden)
    assert compare_preservation(
        before, after, allowed_documentation_owners={None}
    ).unchanged


def test_multiple_selected_owners_keep_independent_source_positions(definition):
    before = acquired(
        '"module"\ndef f():\n    "function"\n    "ordinary"\n', definition
    )
    after = acquired('def f():\n    "ordinary"\n', definition)
    assert compare_preservation(
        before, after, allowed_documentation_owners={None, 0}
    ).unchanged
    assert not compare_preservation(
        before, after, allowed_documentation_owners={0}
    ).unchanged
    assert not compare_preservation(
        before, after, allowed_documentation_owners={None}
    ).unchanged


def test_selected_owner_still_compares_retained_declaration_metadata(definition):
    before = acquired('def f():\n    "docs"\n    pass\n', definition)
    declaration = replace(
        before.source.declarations[0], anchor=before.source.declarations[0].anchor + 1
    )
    changed = replace(
        before, source=replace(before.source, declarations=(declaration,))
    )
    result = compare_preservation(before, changed, allowed_documentation_owners={0})
    assert not result.unchanged
    assert result.diagnostics[0].code == "declaration-changed"


def test_dropping_a_sole_doc_leaves_compilation_to_the_caller(definition):
    documented = 'def f():\n    "docs"\n'
    bare = "def f():\n"
    compile(documented, "<fixture>", "exec")
    with pytest.raises(IndentationError):
        compile(bare, "<fixture>", "exec")
    assert compare_preservation(
        acquired(documented, definition),
        acquired(bare, definition),
        allowed_documentation_owners={0},
    ).unchanged


def test_demoting_documentation_into_ordinary_code_is_refused(definition):
    before = acquired('"old docs"\nx=1\n', definition)
    after = acquired('"new docs"\n"old docs"\nx=1\n', definition)
    assert not compare_preservation(
        before, after, allowed_documentation_owners={None}
    ).unchanged


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ('"docs"  # type: ignore\nx=1\n', '"new" # type: ignore\nx=1\n'),
        ('"docs"\t# type: int\nx=1\n', '"new" # type: int\nx=1\n'),
        ('("docs")  # type: ignore\nx=1\n', '("new") # type: ignore\nx=1\n'),
        (
            '(\n "docs"\n) # type: ignore\nx=1\n',
            '(\n "new" # type: ignore\n)\nx=1\n',
        ),
        ('# type: ignore\n"docs"\nx=1\n', "# type: ignore\nx=1\n"),
    ],
)
def test_selected_documentation_keeps_directive_spacing_and_attachment(
    definition, before, after
):
    was, now = acquired(before, definition), acquired(after, definition)
    for original, changed in ((was, now), (now, was)):
        assert not compare_preservation(original, changed).unchanged
        assert not compare_preservation(
            original, changed, allowed_documentation_owners={None}
        ).unchanged


@pytest.mark.parametrize(
    ("before", "after", "owners"),
    [
        ('"docs"  # type: ignore\nx=1\n', '"new prose"  # type: ignore\nx=1\n', {None}),
        ('# type: ignore\n"docs"\nx=1\n', '# type: ignore\n"new prose"\nx=1\n', {None}),
        (
            '(\n "docs" # old\n) # type: ignore\nx=1\n',
            '# heading\n(\n "new prose" # updated\n) # type: ignore\nx=1\n',
            {None},
        ),
        (
            'def f():\n    "docs" # type: ignore\n    pass\n',
            '"module"\ndef f():\n    "new prose" # type: ignore\n    pass\n',
            {None, 0},
        ),
        (
            '"docs"\n"ordinary" # type: ignore\n',
            '"ordinary" # type: ignore\n',
            {None},
        ),
    ],
)
def test_selected_documentation_allows_safe_prose_near_directives(
    definition, before, after, owners
):
    result = compare_preservation(
        acquired(before, definition),
        acquired(after, definition),
        allowed_documentation_owners=owners,
    )
    assert result.unchanged, result.diagnostics


@pytest.mark.parametrize(
    "expression",
    ['"""docs\n    """;', '(\n        "docs"\n    );'],
)
def test_selected_multiline_doc_keeps_executable_suffix_indentation(
    definition, expression
):
    documented = acquired(f"def f():\n    {expression} x=1\n", definition)
    bare = acquired("def f():\n    x=1\n", definition)
    for before, after in ((documented, bare), (bare, documented)):
        result = compare_preservation(before, after, allowed_documentation_owners={0})
        assert result.unchanged, result.diagnostics
    changed = acquired("def f():\n  x=1\n", definition)
    for before, after in ((documented, changed), (changed, documented)):
        assert not compare_preservation(
            before, after, allowed_documentation_owners={0}
        ).unchanged
