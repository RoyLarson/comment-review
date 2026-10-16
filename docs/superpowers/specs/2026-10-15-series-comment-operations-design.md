# Prose through the middle, comment forms at proof setting

## Purpose

The middle resolves changes to prose. Docket alterations carry the approved
prose or an explicit deletion. When setting the proof, language-specific
operations selected by Series supply comment markers, delimiters, escaping,
indentation and wrapping. A move still subtracts its sentence before review
resolution, so reviewers consider both the remaining and arriving prose.

This replaces the earlier proposal to restore comment syntax during every
middle operation. Each language owns its definition and construction of the
setting operations. This document defines their shared boundary; Python's
rules belong in [its own specification](2026-10-11-python-lexical-reader-design.md).

## Current raw-text contract traced

The following describes the implementation before this change, rather than
the proposed field meanings.

| Boundary | Current behavior | Source |
| --- | --- | --- |
| Reader to Page serialization | `Paragraph.raw_text` joins `raw_lines`; the Page's `_place` serializes that string in a row. Extracted `Paragraph.text` is not carried on the wire. `_paragraph` reconstructs `text` from `raw_text`, losing the distinction. | [paragraph.py](../../../src/comment_review/reading/paragraph.py), [page.py](../../../src/comment_review/binder/page.py), `raw_text`, `_place`, `_paragraph` |
| Bound Pages to edit copy | `distribute.seed` visits the Binder's Pages and copies each paragraph's raw string into `BlankMark.raw_text`. | [distribute.py](../../../src/comment_review/flows/distribute.py), `seed` |
| Mark construction | `_composed_text` keeps the seed's raw text for most marks. For add and move it instead takes the role's proposed complete destination paragraph. `change` carries the replacement paragraph, or the added/moved snippet. | [fill.py](../../../src/comment_review/flows/fill.py), `_composed_text`, `fill`; [mark.py](../../../src/comment_review/desk/proof/mark.py), `Amendment`, `AddMark`, `MoveMark` |
| Base acquisition | `held_at` returns `Paragraph.raw_text`; `bases_and_anchors` installs it as `Place.base`. The callback is supplied by the flow. | [on_the_page.py](../../../src/comment_review/flows/on_the_page.py), `held_at`; [places.py](../../../src/comment_review/flows/places.py), `bases_and_anchors` |
| Prose removal | Move rows call `_without_once`, which calls `comment_at` on raw paragraph and snippet. Drop derivation also calls comment-form recovery. These helpers decode or strip forms and return source-formatted text. | [table.py](../../../src/comment_review/desk/marks/table.py), `_without_once`; [rules.py](../../../src/comment_review/desk/marks/rules.py), `comment_at`, `derived_change` |
| Composition and resolution | `composed_side` composes row results against the raw base. `Place.base`, `sides` and `text` therefore carry source-formatted strings. Answer rewrites and chief recasts feed this same text path. | [passes.py](../../../src/comment_review/desk/evaluate/passes.py), `composed_side`, `answers_pass`, `dispositions_pass`; [place.py](../../../src/comment_review/desk/proof/place.py) |
| Later turns | `_batch_of` labels the resolved or base text `raw_text`; move questions expose the proposed destination under that same key. Chief copies are also built from decided places. | [bus.py](../../../src/comment_review/flows/bus.py), `_batch_of`; [places.py](../../../src/comment_review/flows/places.py), `chief_copy_of` |
| Transcription | `_schedules_of` copies `Place.text` to `Alteration.text`, converting an emptied paragraph to `None`. Both direct-copy and closed-proof paths use it. | [transcribe.py](../../../src/comment_review/flows/transcribe.py), `_schedules_of`, `docket_of`, `docket_of_proof` |
| Docket admission | An alteration checks cue, text type, deletion sentinel and anchor type. It does not require valid comment syntax. | [docket.py](../../../src/comment_review/docket/docket.py), `Alteration.deserialize` |
| Setting | `_one` hands `Schedule.edits` to `galley.reset`, which assigns replacement lines directly. The compositor emits the page. | [proof_setter.py](../../../src/comment_review/flows/proof_setter.py), `_one`; [galley.py](../../../src/comment_review/results/galley.py), `reset` |
| Rereading | `_reread` compares the draft paragraph's raw lines with the alteration's text exactly, followed by executable-code proof. | [proof_setter.py](../../../src/comment_review/flows/proof_setter.py), `_reread`, `_prove` |

The present contract depends on alterations already containing source syntax,
although their loader does not enforce it. Moving formatting to setting requires
changing both the input to `galley.reset` and the reread comparison.

## Ownership

The Binder contains Pages. Each Page owns its paragraphs and their serialized
place rows. Original raw text and extracted prose belong to those paragraphs:

```text
Binder
  Pages
    paragraphs / serialized place rows
      raw_text
      prose
```

Page serialization and deserialization preserve the two representations. In
memory, the extracted prose uses the paragraph's existing text representation;
the serialized `prose` field carries it across that boundary. It does not add
a second in-memory copy or replace the Page's existing `prose` collection.

The Binder delegates Page serialization and carries its existing envelope
metadata. It gains no prose field, parallel paragraph store or formatting
responsibility. Future Glossary and Index contents would be peers of Pages in
the Binder; they are outside this change.

## Source text and editable prose

Keep `raw_text` for the original paragraph's source representation, including
its comment markers and literal spelling. It remains available as context and
evidence. Give editable prose its own explicit field, `prose`, on each Page's
serialized place rows and seeded edit-copy entries. This is needed because
reconstructing prose from raw text inside the middle would repeat language
recognition.

The reader supplies the original prose once, and Page serialization preserves
it rather than rebuilding it from `raw_text`. The new field is the editable
content already extracted by the reader; it carries no grammar, scanner state,
form recipe or source-position map. Source wrapping is removed for matching;
paragraph boundaries and content required to preserve documentation meaning
remain available. A matching view must not discard punctuation or change words.

Prose is an explicit representation, never guessed from its opening characters.
Quotes, hashes, backslashes and apparent comment delimiters within prose are
ordinary content. For example, `Explain the # marker.` must retain the hash.
A proposal with an unmatched quote remains editable prose and may be escaped
when set. The middle never tries to parse that proposal as source.

Original raw text is not overwritten with proposed prose. The field roles are:

| Carrier | Proposed meaning |
| --- | --- |
| Page row `raw_text` | Original source representation for the place. |
| Page row `prose` | Reader-extracted original editable prose. |
| Seeded edit-copy `raw_text`, `prose` | Original source context and original prose supplied to the role. |
| Ordinary mark `raw_text` | Retained source context, not the authoritative base for verification. |
| Correct, patch and drop `change` | Complete resulting prose; empty prose retains the existing drop meaning. |
| Add or move `change` | Prose being added or moved. |
| Add or move `prose` | Complete proposed destination prose, replacing the overloaded use of `raw_text` for this purpose. |
| Quoted editorial claims | Quotes from the authoritative prose supplied for review. |
| Answer `change`, chief recast `prose` | Complete proposed prose for the corresponding side or place. |
| `Place.base`, `Place.sides`, `Place.text` | Original, proposed and decided prose respectively. |
| Turn batches and chief copies | Prose from those same fields, presented as prose. Original source context, where carried, remains explicitly raw. |
| `Alteration.text` | Approved complete prose, or `None` to vacate the place. |

Source citations and their verbatim evidence continue to quote source exactly.
They are separate from editorial claims about paragraph prose. The copy, mark
and answer contracts must state which text is quoted and which text is proposed.

## Admission and middle operations

Flows obtain the authoritative prose base from a Page in the received Binder
or the existing address-resolution flow. Extra addresses receive the same reading and
identity checks as gathered places. Returned marks cannot supply their own base
for verification. Anchors remain opaque values used by existing address checks.

Mark creation, check, collation, direct-copy transcription, answers and chief
rulings all consume the same prose contract. Admission validates representation
and required fields. It does not require intermediate prose to be a valid
comment or string literal.

The middle performs language-independent matching, addition, subtraction and
composition. A move subtracts a uniquely matching snippet from its origin and
uses the supplied complete destination proposal. It checks that the destination
keeps its existing prose and the moved prose in their required order. It does
not append the snippet a second time. Absent and ambiguous matches retain their
existing refusals. Changes to one end do not bypass atomic move approval.

Parallel proposals are still measured against their authoritative common base;
sequential review consumes the previous stage's resolved prose. Intermediate
prose does not acquire markers, quotes, escaping or width-driven line breaks.
The existing line-based composition algorithm must be evaluated against this
representation: source wrap differences must not manufacture conflicts, equal
edits apply once, and incompatible content edits remain visible. This change
does not introduce an event-log redesign or silently change approval rules.

Empty strings and missing results keep distinct meanings: `Place.text is None`
means no decided text, while an approved empty result becomes the docket's
explicit deletion. A prose result equal to its base creates no alteration, so
unchanged places are not reformatted as a side effect.

## Language-specific setting by Series

The proof-setting flow checks the schedule's recorded source identity and
reading context, then acquires the language implementation. It supplies the
setter with a callable selected by Series and bound to that page's language.
The setter declares the narrow interface it needs. Language definitions and
scanner state stay within the language implementation; the middle receives
neither a formatting callable nor those details.

For each alteration, the operation receives approved prose, the original
paragraph's identified form, and the existing placement and line controls. It
returns the source-formatted paragraph or a setting refusal. The original form
comes from reading the verified source page. It does not come from parsing the
edited prose or from another copy of original source stored in the docket.

Existing filled places retain their comment form where it can represent the
approved prose. Empty places use the language's defined insertion form. The
operation chooses only among that language's permitted forms when quoting or
escaping requires a different spelling; the decoded prose and Series must stay
the same. It refuses an unrepresentable result instead of dropping content.

Line comments receive their markers and continuation lines. Block comments
receive their opening and closing delimiters. Documentation literals receive
the required quoting and escaping. A, B, C and F retain their placement and
whole-section rules; D remains leading space. Each language has its own
definition and assembly, even where mechanics can be shared.

The formatted replacements are passed to the existing galley and compositor.
The docket itself continues to hold approved prose. Deletions use the existing
vacating path. A setting refusal discards the draft run under the current
all-or-nothing contract, including both ends of a move across different files.
This is a preparation step in the existing setting flow, not another writer.

## Rereading and proof

Reread the draft under the admitted context and check the intended place and
Series. Compare its extracted prose with the approved alteration using the
same representation used at admission. Added, missing, reordered or differently
decoded content must fail; a changed line wrap alone must not fail. Check a
deletion by absence of prose at its retained place. Any raw-layout comparison
uses the setter's formatted result rather than comparing prose with raw lines.

Independently prove that executable pieces and their order are unchanged.
Comment delimiters that escape into code, changed literal data, changed code
boundaries, indentation and protected material remain covered by that proof.
No operation may insert executable statements to make a deletion compile.
Local compilation remains a separate check.

Comment formation is part of producing the draft that gets proved. A later
whole-source formatter still runs only after prose-only proof and presents its
own diff; that later output does not inherit proof of unchanged code spelling.

## Compatibility and affected interfaces

This changes the meaning of editable fields and `Alteration.text`; it is not a
drop-in callable substitution. Give the affected Page, edit-copy, master-proof,
turn-batch and docket formats an explicit shared contract identity or version
through their existing admission mechanisms. The Binder envelope's version may
identify a changed nested Page contract; it does not own the Page's prose fields.
Old artifacts must be refused with a regeneration instruction before composition
or setting. Never guess whether
a legacy string contains prose or source syntax, and never silently reinterpret
an old `raw_text` destination proposal as the new `prose` field.

Update serialization and deserialization together with mark/check input,
derived changes, claims, retained-word checks, move composition, answer and
chief output, saved resumption, both transcription routes and setter rereading.
Published CLI contracts and operational documentation must describe prose input
and source context consistently. This specification does not itself change
those runtime contracts or agent instructions.

Callables are constructed only when needed for setting and are never serialized.
The current raw-to-comment helpers in middle operations are retired once their
prose replacements cover the real paths. Python reading and setting use the
owned rules without AST, tokenizer or evaluation entry points. Other languages
must have compatible adapters before accepting the new prose docket format;
their detailed rules remain in their own specifications.

The known shared-line code-anchor representation problem remains independently
open. Moving formatting to setting does not prove that a docstring between two
pieces of code can be emitted correctly by the current compositor.

## Acceptance evidence

| Check | Required result |
| --- | --- |
| Page roundtrip | Raw source and extracted prose both survive Page serialization with distinct meanings, including Pages serialized inside a Binder. |
| Ownership | Gathered prose belongs to Page paragraphs and seeds the corresponding edit-copy entries; the Binder envelope has no new prose or paragraph fields. |
| Middle isolation | Mark, move, answer, chief and resume paths operate on supplied prose with language recognition, formatting and source I/O unavailable inside the middle. |
| Wrapped sentence | A sentence split across comment-marker lines is removed once from the prose; the origin remainder and destination proposal are visible before setting. |
| Prose punctuation | Quotes, hashes, backslashes and apparent closing delimiters remain prose throughout review and reread identically after setting or produce a setting refusal. |
| Composition | Different source wraps with identical prose do not create different proposals; equal edits apply once; conflicting changes remain unresolved. |
| Move | Cross-language and cross-Series moves transfer prose, keep both ends atomic, and never insert the destination snippet twice. |
| Edit contracts | CLI-authored and directly supplied copies use identical prose semantics; source citations still compare verbatim source. |
| Saved reviews | Answer and disposition resumes, chief copies and turn batches preserve prose; legacy or mixed representations refuse at admission. |
| Docket | Both transcription routes produce prose alterations, omit unchanged places and retain explicit deletion and recorded source identities. |
| Setting | Markers, escaping, wrapping and empty-place defaults are applied only while setting; a failed destination produces no partial draft run. |
| Reread | Approved prose agrees at its intended place despite different raw formatting; missing or changed content and wrong placement refuse. |
| Python documentation | Plain/raw and adjacent/parenthesized literals expose their full prose; a closing-line comment remains in the same section, with both portions accounted for once. |
| Preservation | Code mutations and protected-text changes still refuse independently of successful prose comparison. |

Use invented examples and the real gather, mark, collate, resume, transcribe and
proof paths. Existing reader, address, writer and preservation assertions remain
required. Update raw-equality expectations only where the explicit new prose
contract replaces them, retaining independent checks for source loss and wrong
placement.
