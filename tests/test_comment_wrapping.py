import pytest
from conftest import build
from helpers import a_typed_mark, returned

from comment_review.binder.binder import Binder, bind
from comment_review.desk.marks.rules import comment_at, derived_change
from comment_review.desk.marks.table import INSTRUCTIONS
from comment_review.desk.proof.mark import Instruction, Touch, read_mark
from comment_review.flows import proof_setter
from comment_review.flows.distribute import seed
from comment_review.flows.fill import fill, row_problems
from comment_review.flows.transcribe import docket_of
from comment_review.reading.lexer import LANGUAGES
from comment_review.results import compositor, galley


@pytest.mark.parametrize(
    "address, raw, prose",
    [
        (
            "m.py@b1",
            "    # Keep this sentence.\n    # Move this sentence.\n",
            "Keep this sentence. Move this sentence.",
        ),
        (
            "m.rs@a1",
            "    //! Keep this sentence.\n    //! Move this sentence.\n",
            "Keep this sentence. Move this sentence.",
        ),
        (
            "m.js@b1",
            "    /*\n     * Keep this sentence.\n     * Move this sentence.\n     */",
            "Keep this sentence. Move this sentence.",
        ),
        (
            "m.js@a1",
            "    /**\n     * Keep this sentence.\n     * Move this sentence.\n     */",
            "Keep this sentence. Move this sentence.",
        ),
        (
            "m.sql@b1",
            "-- Keep this sentence.\n-- Move this sentence.",
            "Keep this sentence. Move this sentence.",
        ),
        (
            "m.py@a1",
            '    """Keep this sentence.\n    Move this sentence."""',
            "Keep this sentence. Move this sentence.",
        ),
    ],
)
def test_addressed_comment_unwraps_and_restores_its_form(address, raw, prose):
    form = comment_at(address, raw)
    assert form.text == prose
    wrapped = form.wrap(prose)
    assert comment_at(address, wrapped).text == prose
    assert max(map(len, wrapped.splitlines())) <= max(map(len, raw.splitlines()))
    assert wrapped.startswith(raw.splitlines()[0].split("Keep")[0])
    if raw.rstrip().endswith("*/"):
        assert wrapped.rstrip().endswith("*/")
    if raw.rstrip().endswith('"""'):
        assert wrapped.rstrip().endswith('"""')


def test_markers_inside_prose_are_kept():
    form = comment_at("m.js@b1", "// Keep // and /* as examples.\n// Keep punctuation!")
    assert form.text == "Keep // and /* as examples. Keep punctuation!"


def test_an_empty_remainder_removes_the_comment_delimiters():
    assert comment_at("m.js@b1", "/* The sentence. */").wrap("") == ""


@pytest.mark.parametrize(
    "name,source",
    [
        (
            "m.rs",
            "fn first() {}\n//! Keep this sentence. Move this\n"
            "//! sentence. Keep this one too.\nfn next() {}\n",
        ),
        (
            "m.js",
            "let first = 1;\n/**\n * Keep this sentence. Move this\n"
            " * sentence. Keep this one too.\n */\nfunction next() {}\n",
        ),
        (
            "m.py",
            'def next():\n    """Keep this sentence. Move this\n'
            '    sentence. Keep this one too."""\n    return 1\n',
        ),
        (
            "m.py",
            "first = 1\n# Keep this sentence. Move this\n"
            "# sentence. Keep this one too.\nnext = 2\n",
        ),
    ],
)
def test_a_move_removes_an_unwrapped_sentence_and_preserves_its_form(name, source):
    page = build(source, name)
    paragraph = next(p for p in page if "Move this" in p.raw_text)
    row = INSTRUCTIONS[Instruction.MOVE]
    mark = a_typed_mark(
        Instruction.MOVE,
        address=paragraph.address,
        claim={
            "from": paragraph.address,
            "to": next(p.address for p in page if p.address and not p.raw_text),
        },
        change="Move this sentence.",
        raw_text="# destination",
    )
    assert row.reads(mark, Touch.ORIGIN, paragraph.raw_text) == []
    changed = row.sets(mark, Touch.ORIGIN, paragraph.raw_text)
    assert changed is not None
    assert (
        comment_at(paragraph.address, changed).text
        == "Keep this sentence. Keep this one too."
    )
    assert max(map(len, changed.splitlines())) <= max(
        map(len, paragraph.raw_text.splitlines())
    )
    assert changed.startswith(paragraph.raw_text.split("Keep")[0])
    if name == "m.js":
        assert changed.rstrip().endswith("*/")
    if name == "m.py" and "@a" in paragraph.address:
        assert changed.rstrip().endswith('"""')


@pytest.mark.parametrize(
    "snippet",
    ["not present.", "move this sentence.", "Move this sentence", "this sent"],
)
def test_move_matching_keeps_case_and_punctuation_and_word_boundaries(snippet):
    form = comment_at("m.py@b1", "# Move this sentence.\n# Move this sentence.\n")
    assert form.without_once(snippet) is None


def test_a_drop_rewraps_rust_inner_documentation():
    raw = "//! Kept. Remove this one.\n//! The ending also stays.\n"
    changed, problems = derived_change(
        Instruction.DROP, {"drop": " Remove this one."}, raw, address="m.rs@a1"
    )
    assert problems == []
    assert changed == "//! Kept. The ending also\n//! stays.\n"


def test_removing_a_sentence_retains_a_blank_between_paragraphs():
    form = comment_at("m.py@b1", "# Keep. Move.\n#\n# Second paragraph.\n")
    assert form.without_once("Move.") == "# Keep.\n#\n# Second paragraph.\n"


FORMS = [
    ("m" + lang.extensions[0], f"{marker} Keep. Move.\n{marker} Ending stays.")
    for lang in LANGUAGES
    for marker in lang.line_comment
] + [
    ("m" + lang.extensions[0], f"{op}\nKeep. Move.\nEnding stays.\n{close}")
    for lang in LANGUAGES
    for op, close in lang.block_comment
]


@pytest.mark.parametrize("name,raw", FORMS)
def test_each_supported_form_can_be_edited_from_a_serialized_binder(name, raw):
    source = f"x = 1;\n{raw}\nx = 2;\n"
    page = build(source, name)
    binder = bind([page], read_from={"root": ".", "revise": 0})
    loaded, problems = Binder.deserialize("test binder", binder.serialize())
    assert problems == []
    assert loaded is not None
    paragraph = next(p for p in loaded.paragraphs if "Keep." in p.raw_text)
    form = comment_at(paragraph.address, paragraph.raw_text)
    assert form.text == "Keep. Move. Ending stays."
    changed = form.without_once("Move.")
    assert changed is not None
    assert comment_at(paragraph.address, changed).text == "Keep. Ending stays."
    assert galley.reset(page, {paragraph.address.split("@")[1]: changed}) == []
    output = compositor.set_page(page)
    assert output.startswith("x = 1;\n")
    assert output.endswith("x = 2;\n")
    reread = build(output, name)
    edited = next(p for p in reread if "Keep." in p.raw_text)
    assert edited.address == paragraph.address
    assert edited.anchor == paragraph.anchor


@pytest.mark.parametrize("quote", ['"""', "'''", 'r"""', "r'''"])
def test_docstring_quotes_and_prefixes_survive_removal(quote):
    close = quote[-3:]
    page = build(
        f"def f():\n    {quote}Keep. Move.\n    Ending stays.{close}\n    return 1\n"
    )
    paragraph = next(p for p in page if "Keep." in p.raw_text)
    changed = comment_at(paragraph.address, paragraph.raw_text).without_once("Move.")
    assert changed is not None
    assert changed.startswith("    " + quote)
    assert changed.endswith(close)
    assert comment_at(paragraph.address, changed).text == "Keep. Ending stays."


def test_a_trailing_block_keeps_its_separator_and_code():
    source = "let x = 1;  /* Keep. Move.\n             * Ending stays. */\nlet y = 2;\n"
    page = build(source, "m.js")
    paragraph = next(p for p in page if "Keep." in p.raw_text)
    assert "@c" in paragraph.address
    changed = comment_at(paragraph.address, paragraph.raw_text).without_once("Move.")
    assert changed is not None and changed.startswith("  /* ")
    assert galley.reset(page, {paragraph.address.split("@")[1]: changed}) == []
    output = compositor.set_page(page)
    assert output.startswith("let x = 1;  /* ")
    assert output.endswith("let y = 2;\n")
    assert comment_at(paragraph.address, changed).text == "Keep. Ending stays."


def test_crlf_and_final_newline_survive_rewrapping():
    form = comment_at("m.rs@a1", "//! Keep. Move.\r\n//! Ending stays.\r\n")
    changed = form.without_once("Move.")
    assert changed is not None
    assert changed.endswith("\r\n")
    assert "\n" not in changed.replace("\r\n", "")


def test_nested_block_delimiters_in_prose_remain():
    form = comment_at("m.rs@b1", "/* Keep /* this nested note */. Move. */")
    changed = form.without_once("Move.")
    assert changed is not None
    assert "/* this nested note */" in changed
    assert changed.rstrip().endswith("*/")


def test_trailing_rewrapping_counts_the_carried_code_anchor():
    source = (
        "let value = 100; /* Kept. Move.\n * Longer ending stays here. */\nlet y = 2;\n"
    )
    page = build(source, "m.js")
    paragraph = next(p for p in page if "Move." in p.raw_text)
    form = comment_at(paragraph.address, paragraph.raw_text, anchor=paragraph.anchor)
    changed = form.without_once("Move.")
    assert changed is not None
    assert galley.reset(page, {paragraph.address.split("@")[1]: changed}) == []
    output = compositor.set_page(page)
    assert max(map(len, output.splitlines())) <= max(map(len, source.splitlines()))


@pytest.mark.parametrize("instruction", ["move", "drop"])
def test_mark_check_and_proof_agree_for_wrapped_sentences(tmp_path, instruction):
    source = (
        "x = 0\n# Kept. Move this\n# sentence. Ending stays.\ny = 1\n"
        "# Destination stays.\nz = 2\n"
    )
    (tmp_path / "m.py").write_text(source, encoding="utf-8", newline="\n")
    page = build(source)
    binder = bind([page], read_from={"root": str(tmp_path), "revise": 0})
    loaded, problems = Binder.deserialize("binder", binder.serialize())
    assert problems == [] and loaded is not None
    origin = next(p for p in loaded.paragraphs if "Move this" in p.raw_text)
    destination = next(p for p in loaded.paragraphs if "Destination" in p.raw_text)
    copy = seed(loaded, "block-context")
    entry = {
        "address": origin.address,
        "instruction": instruction,
        "reason": "This sentence belongs at the destination.",
        "sources": [{"cite": "m.py:1"}],
    }
    if instruction == "move":
        entry.update(
            claim={"from": origin.address, "to": destination.address},
            change="Move this sentence.",
            raw_text="# Destination stays. Move this sentence.",
        )
    else:
        entry["claim"] = {"drop": " Move this\n# sentence."}
    placed, problems = fill(copy, entry, tmp_path)
    assert problems == [] and placed is not None
    mark, problems = read_mark(origin.address, placed)
    assert problems == [] and mark is not None
    bases = {p.address: p.raw_text for p in loaded.paragraphs}
    assert row_problems(mark, bases.__getitem__) == []
    docket = docket_of(returned(copy), tmp_path)
    drafted, refused = proof_setter.run(
        docket, tmp_path, tmp_path.parent / (tmp_path.name + "-draft")
    )
    assert refused == [] and len(drafted) == 1
    output = drafted[0].draft.read_text(encoding="utf-8")
    again = build(output)
    remainder = next(p for p in again if p.address == origin.address)
    assert (
        comment_at(remainder.address, remainder.raw_text).text == "Kept. Ending stays."
    )
    assert [line for line in output.splitlines() if not line.startswith("#")] == [
        "x = 0",
        "y = 1",
        "z = 2",
    ]
    assert (tmp_path / "m.py").read_text(encoding="utf-8") == source
