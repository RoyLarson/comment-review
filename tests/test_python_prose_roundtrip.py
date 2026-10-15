import pytest
from conftest import build, cue

from comment_review.reading.series import Kind
from comment_review.results.compositor import set_page
from comment_review.results.galley import reset


def assert_documentation(page, raw, prose, owner, decoded):
    docs = [p for p in page if p.kind == Kind.DOCSTRING]
    assert len(docs) == 1
    doc = docs[0]
    assert cue(doc) == f"a{0 if owner is None else owner + 1}"
    assert doc.raw_text == raw
    assert doc.text == prose
    assert [p for p in page if p.raw_text == raw] == [doc]
    assert page.python_read is not None
    assert [p.text for p in page.python_read.payloads] == [decoded]
    assert [p.declaration for p in page.python_read.source.documentation] == [owner]
    return doc


def code_anchors(page):
    return [
        anchor for place, anchor in page.cues.places.items() if place.startswith("c")
    ]


@pytest.mark.parametrize("ending", ["\n", "\r\n"], ids=["lf", "crlf"])
@pytest.mark.parametrize("function", [False, True], ids=["module", "function"])
@pytest.mark.parametrize("multiline", [False, True], ids=["one-line", "multiline"])
def test_closing_comment_roundtrip_and_combined_replacement(
    ending, function, multiline
):
    indent = "    " if function else ""
    header = "def f():\n" if function else ""
    owner = 0 if function else None
    raw = (
        indent + '"""first\n' + indent + 'second""" # closing note'
        if multiline
        else indent + '"""first""" # closing note'
    )
    decoded = "first\n" + indent + "second" if multiline else "first"
    prose = "first second" if multiline else "first"
    following = indent + '"ordinary literal"\n' + indent
    following += "return 7  # detail\n" if function else "value = 7  # detail\n"
    text = (header + raw + "\n" + following).replace("\n", ending)
    compile(text, "m.py", "exec")
    expected_anchors = (["def f():"] if function else []) + [
        indent + '"ordinary literal"',
        indent + ("return 7" if function else "value = 7"),
    ]
    page = build(text)
    assert set_page(page) == text
    for current in (page, build(set_page(page))):
        doc = assert_documentation(current, raw, prose, owner, decoded)
        assert [p for p in current if "# closing note" in p.raw_text] == [doc]
        assert sum(p.raw_text.count("# closing note") for p in current) == 1
        assert code_anchors(current) == expected_anchors

    replacement = (
        indent + '"""changed""" # edited note'
        if multiline
        else indent + '"""changed\n' + indent + 'prose""" # edited note'
    )
    edited_decoded = "changed" if multiline else "changed\n" + indent + "prose"
    edited_prose = "changed" if multiline else "changed prose"
    assert reset(page, {cue(doc): replacement}) == []
    composed = set_page(page)
    expected = (header + replacement + "\n" + following).replace("\n", ending)
    assert composed == expected
    assert "# closing note" not in composed
    assert composed.count("# edited note") == 1
    compile(composed, "m.py", "exec")
    reread = build(composed)
    edited_doc = assert_documentation(
        reread, replacement, edited_prose, owner, edited_decoded
    )
    assert [p for p in reread if "# edited note" in p.raw_text] == [edited_doc]
    assert code_anchors(reread) == expected_anchors
    assert set_page(reread) == expected


@pytest.mark.parametrize("ending", ["\n", "\r\n"], ids=["lf", "crlf"])
@pytest.mark.parametrize(
    "header, raw, prose, decoded, following, owner",
    [
        (
            "",
            '"complete " r"module"',
            "complete module",
            "complete module",
            '"ordinary"\nvalue = 1\n',
            None,
        ),
        (
            "def f():\n",
            '    ("complete\\n"\n     "function")',
            "complete function",
            "complete\nfunction",
            '    "ordinary"\n    return 1\n',
            0,
        ),
        (
            "class C:\n",
            '    (("complete " "class"))',
            "complete class",
            "complete class",
            '    "ordinary"\n    value = 1\n',
            0,
        ),
        (
            "async def f():\n",
            '    (r"""complete\n    async """ "function")',
            "complete async function",
            "complete\n    async function",
            '    "ordinary"\n    return 1\n',
            0,
        ),
    ],
    ids=[
        "module-concatenated",
        "function-parenthesized",
        "class-nested",
        "async-multiline",
    ],
)
def test_complete_literal_expression_survives_writer_and_reread(
    ending, header, raw, prose, decoded, following, owner
):
    text = (header + raw + "\n" + following).replace("\n", ending)
    compile(text, "m.py", "exec")
    page = build(text)
    composed = set_page(page)
    assert composed == text
    expected_anchors = header.splitlines() + following.splitlines()
    for current in (page, build(composed)):
        assert_documentation(current, raw, prose, owner, decoded)
        assert code_anchors(current) == expected_anchors
        assert set_page(current) == text


def test_nested_lexical_owners_survive_replacement_and_reread():
    text = (
        '"module docs"\n'
        "class C:\n"
        '    ("class " "docs")\n'
        "    def method(self):\n"
        '        "method docs"\n'
        "        async def nested():\n"
        '            """nested\n'
        '            docs"""\n'
        "            return 1\n"
        "        return nested\n"
        "async def sibling():\n"
        '    "sibling docs"\n'
        "    return 2\n"
    )
    compile(text, "m.py", "exec")
    expected_docs = {
        "a0": "module docs",
        "a1": "class docs",
        "a2": "method docs",
        "a3": "nested docs",
        "a4": "sibling docs",
    }
    page = build(text)
    assert set_page(page) == text
    for current in (page, build(set_page(page))):
        assert {
            cue(p): p.text for p in current if p.kind == Kind.DOCSTRING
        } == expected_docs
        assert current.python_read is not None
        assert [p.text for p in current.python_read.payloads] == [
            "module docs",
            "class docs",
            "method docs",
            "nested\n            docs",
            "sibling docs",
        ]
        assert [p.declaration for p in current.python_read.source.documentation] == [
            None,
            0,
            1,
            2,
            3,
        ]
    anchors = code_anchors(page)
    replacement = '        ("changed " "method")'
    assert reset(page, {"a2": replacement}) == []
    composed = set_page(page)
    assert composed == text.replace('        "method docs"', replacement)
    compile(composed, "m.py", "exec")
    reread = build(composed)
    expected_docs["a2"] = "changed method"
    assert {cue(p): p.text for p in reread if p.kind == Kind.DOCSTRING} == expected_docs
    assert reread.python_read is not None
    assert [p.text for p in reread.python_read.payloads] == [
        "module docs",
        "class docs",
        "changed method",
        "nested\n            docs",
        "sibling docs",
    ]
    assert code_anchors(reread) == anchors
    assert set_page(reread) == composed
