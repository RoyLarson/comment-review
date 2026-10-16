# Word alignment against retained raw text

## Purpose

Keep the complete paragraph in `raw_text`. Locate and compare editorial changes
by aligning whole words, with symbols, newlines and spacing represented
separately. Each alignment token retains its contributing raw-text positions.
This permits matching across wrapping and comment markers while retaining the
original form, paragraph breaks, indentation and closing-line comments.

The middle resolves edits against that retained representation. Setting uses
the existing galley and compositor, with language-specific operations only for
the changed material that needs placement, escaping or reflow. A move still
subtracts its sentence before review resolution. Each language owns its
definition; Python's rules belong in
[its own specification](2026-10-11-python-lexical-reader-design.md).

## Superseded requirements

This word-alignment contract supersedes the earlier requirements in this spec
to make stripped `text` the authoritative editable paragraph, propagate
syntax-free strings through every review artifact, and reconstruct complete
comment forms from those strings at setting. The proposed conversion of
`Alteration.text` to syntax-free prose is superseded as well. Retained raw
forms supply the information that reconstruction would otherwise have to infer.

Paragraph ownership, consistent field names, snapshot consistency, whole-section
addresses, atomic moves, separate code proof and local validation remain in
force. Token-to-raw correspondence is permitted for locating edits; the earlier
blanket exclusion of such correspondence does not apply to this matching work.
It does not authorize a replacement file writer or language parsing in the
middle.

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

The present contract already retains source syntax through alterations. The
change is to matching and composition against that representation, replacing
host-dependent form recovery while preserving the existing setting route.

## Ownership

The Binder contains Pages. Each Page contains Paragraphs. Each Paragraph owns
its original raw text, derived text and serialized representation:

```text
Binder
  Pages
    Paragraphs
      raw_text
      text
```

Paragraph serialization and deserialization preserve the two representations.
Derived text uses `text` both in memory and in the serialized Paragraph.
Raw text remains derived from the Paragraph's source lines. Neither
representation is duplicated on Page.

Page delegates to each Paragraph when serializing or reading its content
collection. Move the paragraph field construction and restoration currently in
`binder.page._place` and `_paragraph` into the Paragraph contract. Page owns its
identity and collection, while Paragraph owns validation of its own fields.
The serialized records inside a Page are Paragraphs, not a second Page-owned
row structure. This does not require exposing every internal Paragraph field.

The Binder delegates Page serialization and carries its existing envelope
metadata. It gains no prose field, parallel paragraph store or formatting
responsibility. Future Glossary and Index contents would be peers of Pages in
the Binder; they are outside this change.

## Paragraph snapshot lifecycle

A Paragraph's `raw_text` is the retained representation. Its derived `text`
describes that same snapshot and is not independently edited. Reading creates
them together; serialization and deserialization preserve the pair under the
same field names. Matching derives positional tokens from `raw_text`, so it
does not depend on restoring source from the derived `text`.

Review keeps the original Paragraph unchanged. Marks and resolved places hold
proposed and decided raw paragraph replacements separately, including results
passed to later review stages. Setting places the approved result. Rereading
the draft creates new Paragraphs with matching derived text and raw source.

The galley's draft preparation must preserve this boundary: replacing source
lines alone does not produce a new, synchronized Paragraph. Keep the original
snapshot available for verification and treat the prepared output as draft
material until rereading supplies the new pair. A Paragraph must never present
revised `text` beside original `raw_text`, or revised raw lines beside stale
`text`, as corresponding representations.

## Retained source and alignment tokens

Retain the complete `raw_text`, including markers, literal spelling, newlines,
paragraph breaks, indentation and closing-line comments. A temporary alignment
view never replaces it. Paragraph breaks inside one addressed Paragraph remain
internal structure and do not create additional addresses.

Alignment operates on whole-word tokens, not individual letters. Symbols and
newlines are separate tokens; spacing remains represented between words. Each
token records the raw span or spans that contributed it. Preserve exact word
spelling and case. Splitting out punctuation must not lose it.

For `# Keep the cache\n# until shutdown.`, the significant sequence is
`# | Keep | the | cache | newline | # | until | shutdown | .`, with spacing
also retained. The two opening hashes are identified markers; a hash in
`# Explain the # marker.` is content except for the opening marker.

The language's existing form recognition supplies marker roles. The alignment
engine consumes supplied roles and raw positions; it does not recognize Python
or another language. Symbol spelling alone never grants zero cost. Literal
delimiters can be recognized decoration, while a quoted hash or backslash can
be content. Where literal escapes or adjacent literals alter visible spelling,
language-owned handling must preserve the correspondence to all contributing
raw spans. It must not guess by stripping quotes or escape characters.

| Token difference | Alignment treatment |
| --- | --- |
| Equal word or content symbol | Match with no content-change cost. |
| Inserted, deleted or replaced word | Positive content-change cost for the whole word. |
| Inserted, deleted or replaced content symbol | Positive content-change cost. |
| Ordinary spacing, wrapping or recognized comment decoration | Zero alignment cost; retain the raw characters. |
| Paragraph breaks or meaningful indentation | Retained structure, never silently collapsed. |
| Protected directive or executable material | Preserve text and attachment independently of alignment score. |

For snippet lookup, align the entire snippet within the addressed raw paragraph;
unrelated leading and trailing paragraph content is outside the match. Require
zero content-change cost and a unique content occurrence. A close spelling is
not a successful match. Equivalent paths through the same formatting are not
distinct occurrences, but repeated content at different raw positions is
ambiguous. Whole-word boundaries keep `now here` distinct from `nowhere`.

For complete revisions, align the full base and proposal to identify changed
word and symbol spans. Ambiguous mappings that imply different edits require
resolution. The result identifies content spans and intervening retained
decoration; it is not permission to delete one contiguous raw interval that
also contains markers. Unrelated raw text stays exact. Applying a change must
retain paragraph breaks and meaningful indentation outside that change.

The implementation uses pure Python and the standard library. It needs no
alignment dependency. The engine aligns text tokens; it builds no programming
language token model, statement tree or identifier relationships.

### Small lookup prototypes

These examples exercise lookup with supplied marker positions. They do not test
language recognition, full revision alignment or applying changes. Raw portions
listed below exclude surrounding decoration but retain their original spelling.

```python
# Keep the cache
# until shutdown.
# Keep the cache until shutdown.
# Explain the # marker.
```

Only each line's first hash is an opening marker.

| Sentence to find | Matching raw portions |
| --- | --- |
| `Keep the cache until shutdown.` | Two occurrences: `Keep the cache` on the first line plus `until shutdown.` on the second; the complete sentence on the third. Lookup refuses the ambiguity. |
| `Keep cache until shutdown.` | None: the source includes `the`. |
| `Explain the # marker.` | `Explain the # marker.` on the last line, including the internal hash. |
| `Explain the marker.` | None: the internal hash is content. |

```python
"""Call run(x).
Keep the # marker."""  # noqa: D400
```

The triple quotes and the hash after the closing quotes are supplied as
decoration. The hash inside the literal remains content.

| Sentence to find | Matching raw portions |
| --- | --- |
| `Call run ( x ) .` | `Call run(x).` on the first line; each symbol matches despite spacing. |
| `Call run(y).` | None: `y` differs from `x`. |
| `Keep the # marker.` | `Keep the # marker.` on the second line, ending before the closing quotes. |
| `noqa: D400` | `noqa: D400` in the closing-line comment. Locating it grants no permission to change the protected directive. |

A throwaway lookup probe reproduced these expected portions using explicit
fixture marker positions and whole-word/symbol comparison. This establishes
the examples' lookup behavior only; production integration remains required.

### Small editing prototypes

Use the same supplied marker positions to locate edits, then compare the entire
result with a literal expected raw string. These probes cover single-line
replacement and wrapped deletion; they do not choose wrapping for a longer
replacement or exercise the production setter.

```python
# Keep the cache
# until shutdown.
#
# Example:
#     run()
```

Replacing `cache` with `buffer` changes only that word. Removing
`Keep the cache until shutdown.` removes its content from the first two lines.
The exact result, with newlines written as `\n`, is:

```text
"# \n# \n#\n# Example:\n#     run()"
```

This exposes the residue of preserving raw form: the first two lines still
contain their marker and following space. The existing paragraph break and
example indentation are unchanged. This is the intermediate raw edit, not a
claim that final setting should retain every newly empty comment line. Matching
and content removal alone do not decide that cleanup.

For the docstring example above:

| Edit | Exact expected raw result (`\n` denotes a newline) |
| --- | --- |
| Replace `Keep the # marker.` with `Keep the / marker.` | `"""Call run(x).\nKeep the / marker."""  # noqa: D400` |
| Remove `Call run ( x ) .` | `"""\nKeep the # marker."""  # noqa: D400` |
| Attempt to remove `noqa: D400` | Refuse using the supplied protected range; the original text remains unchanged. |

The throwaway probe reproduces these results. The closing quotes, spaces and
directive survive both permitted edits exactly. Protection is an explicit
fixture input, not something the alignment algorithm infers from the words.

## Field roles

The field roles are:

| Carrier | Proposed meaning |
| --- | --- |
| Paragraph `raw_text` | Original source representation for the place. |
| Paragraph `text`, in memory and serialized | Derived view of the same raw snapshot, with the same field name on both sides. |
| Seeded edit-copy `raw_text` | Complete original paragraph supplied to the role. |
| Ordinary mark `raw_text` | Retained source context, not the authoritative base for verification. |
| Correct, patch and drop `change` | Complete resulting raw paragraph; the existing empty-result rule remains. |
| Add or move `change` | Content snippet being added or moved, located by whole-word alignment. |
| Add or move destination proposal | Complete proposed raw destination paragraph under its declared artifact field; no conversion to a syntax-free string. |
| Quoted editorial claims | Content located against authoritative raw text by alignment. |
| Answer `change`, chief recast `text` | Complete proposed raw paragraph for the corresponding side or place. |
| `Place.base`, `Place.sides`, `Place.text` | Original, proposed and decided raw paragraph strings respectively. |
| Turn batches and chief copies | Retained raw results from those same fields. |
| `Alteration.text` | Approved complete raw paragraph replacement, or `None` to vacate the place. |

Source citations and their verbatim evidence continue to quote source exactly.
They are separate from editorial claims located by alignment. The copy, mark
and answer contracts distinguish original raw text, complete raw replacements
and content snippets explicitly; no field is reinterpreted by guessing from its
opening characters.

## Admission and middle operations

Flows obtain the authoritative raw base from a Paragraph in the received Binder
or the existing address-resolution flow. Extra addresses receive the same reading and
identity checks as gathered places. Returned marks cannot supply their own base
for verification. Anchors remain opaque values used by existing address checks.

Mark creation, check, collation, direct-copy transcription, answers and chief
rulings consume the same retained-text and word-alignment contract. Flows
supply the acquired form's token roles and raw correspondence through a narrow
text interface. The middle receives no language definition or scanner state.
Admission validates representation and required fields; intermediate edits need
not already satisfy final wrapping or placement rules. Source validity and
directive attachment are checked when setting and rereading.

The middle performs language-independent matching, addition, subtraction and
composition. A move subtracts the content spans of a uniquely matching snippet
from its retained raw origin and
uses the supplied complete destination proposal. It checks that the destination
keeps its existing prose and the moved prose in their required order. It does
not append the snippet a second time. Absent and ambiguous matches retain their
existing refusals. Changes to one end do not bypass atomic move approval.

Parallel proposals are still measured against their authoritative common base;
sequential review consumes the previous stage's resolved raw result. Each
candidate retains the original form around its edited content. Alignment
ignores eligible formatting for matching without removing it from candidates.
Language-specific repair of changed material and width-driven reflow occur
at setting.

Composition compares proposed edits against spans of the authoritative base
text. Edits to separate spans combine even when they occur on the same displayed
line. Identical edits apply once. Incompatible edits to overlapping spans remain
unresolved. Ordinary source wrapping alone does not create a conflict; paragraph
breaks and meaningful indentation remain part of the retained text contract.
The existing line-based algorithm must meet these requirements before it can
serve this representation. Composition preserves the surrounding retained text
and uses no language syntax. This changes neither approval rules nor the review
history model.

For the raw base `# A small red box.`, the required results are:

| Proposals | Composition result |
| --- | --- |
| `# A large red box.` and `# A small blue box.` | `# A large blue box.`: separate spans combine and the marker remains. |
| Two proposals of `# A small blue box.` | `# A small blue box.`: the equal edit applies once. |
| `# A small blue box.` and `# A small green box.` | Unresolved: incompatible replacements of the same word. |
| `# A small\n# red box.` and `# A small blue box.` | The wrap alone creates no conflict with the color change; markers remain accounted for. |

Empty strings and missing results keep distinct meanings: `Place.text is None`
means no decided text, while an approved empty result becomes the docket's
explicit deletion. An unchanged raw result creates no alteration. A zero-cost
alignment score alone is not evidence that two raw strings are identical;
required structure, protected text and explicit formatting changes remain
accounted for. Unchanged places are not reformatted as a side effect.

## Language-specific setting by Series

The proof-setting flow checks the schedule's recorded source identity and
reading context, then acquires the language implementation. It supplies the
setter with a callable selected by Series and bound to that page's language.
The setter declares the narrow interface it needs. Language definitions and
scanner state stay within the language implementation; the middle receives
neither a formatting callable nor those details.

For each alteration, the operation receives the approved raw replacement,
verified original raw paragraph and its identified form, plus existing placement
and line controls. It preserves untouched form directly. It does not rebuild
the paragraph from stripped prose or infer where a removed closing comment
used to begin. The retained raw replacement remains the editing record.

Only changed material needing escaping, destination-specific markers or width
handling requires language-specific adjustment. Empty places use the language's
defined insertion form. A moved snippet transfers its content into the
destination's form rather than copying origin markers as content. Such changes
must retain the approved words, content symbols, paragraph structure and Series.
Unrepresentable output produces a setting refusal.

A documentation section that owns a closing-line comment retains that comment
outside the documentation literal, on its closing line. Sharing one address
does not make the literal and comment interchangeable output forms. Tool
directives in that comment retain their exact text and effective attachment;
prose edits must not absorb them into the literal, reflow them or silently
discard them. A rewrite, move or deletion that cannot preserve this requirement
must produce a setting refusal. Language-specific details belong to the
language's specification.

For `"""Explain the cache."""  # noqa: D400`, changing `cache` to `buffer` retains
the surrounding quotes, spaces and full closing comment. The raw boundary
already distinguishes the two forms. An ordinary editable closing comment
also retains that boundary when its words change; a match must identify which
content occurrence is edited rather than concatenate both portions and infer
a new split afterward.

A, B, C and F retain their placement and whole-section rules; D remains leading
space. Each language has its own definition and assembly, even where mechanics
can be shared.

The formatted replacements are passed to the existing galley and compositor.
The docket holds approved raw replacements. Deletions use the existing
vacating path. A setting refusal discards the draft run under the current
all-or-nothing contract, including both ends of a move across different files.
This is a preparation step in the existing setting flow, not another writer.

## Rereading and proof

Reread the draft under the admitted context and check the intended place and
Series. Compare actual raw output with the prepared replacement and independently
check that it retains the approved content and protected boundaries. Where
setting legitimately changes wrapping or escaping, check content using the
same word/symbol and language-owned literal rules used at admission. Added,
missing, reordered or differently decoded content must fail. A raw-layout
check uses the prepared result; alignment cost alone cannot prove exact form.
Check a deletion by absence of editable content at its retained place, with
directive and code preservation checked independently.

Independently prove that executable pieces and their order are unchanged.
Comment delimiters that escape into code, changed literal data, changed code
boundaries, indentation and protected material remain covered by that proof.
No operation may insert executable statements to make a deletion compile.
Local compilation remains a separate check.

Comment formation is part of producing the draft that gets proved. A later
whole-source formatter still runs only after prose-only proof and presents its
own diff; that later output does not inherit proof of unchanged code spelling.

## Compatibility and affected interfaces

Keep raw replacement semantics through marks, proofs and `Alteration.text`.
Supersede the proposed wholesale migration to syntax-free fields. Any actual
field or interpretation change must have an explicit identity through existing
admission mechanisms. The Binder envelope may identify a changed nested
Paragraph contract; Paragraph still owns its fields. Keep `text` consistently
named in memory and on the wire wherever that field is used, including the
proposed chief-recast rename. Refuse incompatible artifacts with a regeneration
instruction; never guess whether a string is raw source or a content snippet.

Update serialization and deserialization together with mark/check input,
derived changes, claims, retained-word checks, move composition, answer and
chief output, saved resumption, both transcription routes and setter rereading.
Published CLI contracts and operational documentation must distinguish raw
replacements from content snippets consistently. This specification does not change
those runtime contracts or agent instructions.

Callables are constructed only when needed for setting and are never serialized.
The host-dependent raw-to-comment recovery path is retired once owned
recognition and word alignment cover its real callers. Python reading and
setting use owned rules without AST, tokenizer or evaluation entry points.
Other languages retain their existing readers until their own adapters supply
the required token roles and setting behavior. Their detailed rules remain in
their own specifications.

The known shared-line code-anchor representation problem remains independently
open. Word alignment does not prove that a docstring between two
pieces of code can be emitted correctly by the current compositor.

## Acceptance evidence

| Check | Required result |
| --- | --- |
| Paragraph roundtrip | `raw_text` and `text` retain their names and distinct meanings through serialization and deserialization, including Paragraphs contained in Pages inside a Binder. |
| Snapshot lifecycle | Review and setting preserve the original Paragraph pair; proposals remain separate. Rereading a formatted draft creates a new matching pair, including after saved-review resumption. Draft preparation never exposes stale extracted text as matching revised raw lines. |
| Ownership | Binder contains Pages; Page contains Paragraphs and delegates their serialization and field validation. Raw text and prose belong to Paragraph, with no duplicate fields on Page or Binder. |
| Middle isolation | Mark, move, answer, chief and resume paths align supplied text tokens and raw positions; language recognition, formatting and source I/O stay outside the middle. |
| Wrapped sentence | Whole words match across newline and marker tokens with zero content-change cost. Removal edits content spans once and preserves intervening form; both move ends remain visible before setting. |
| Text structure | Raw text retains paragraph breaks and example indentation. Alignment never replaces it with a flattened string or creates additional addresses. |
| Symbols | Opening markers may be zero-cost; literal hashes, slashes, asterisks and punctuation remain content. A changed content symbol incurs a cost. |
| Match identity | `now here` does not match `nowhere`; changed words refuse snippet lookup. Repeated content at different positions is ambiguous; equivalent formatting paths at one occurrence are not. |
| Composition | Separate edited spans combine even on one displayed line; identical edits apply once; incompatible overlapping edits remain unresolved. Ordinary wrapping alone creates no conflict, while paragraph breaks and meaningful indentation remain represented. |
| Move | Cross-language and cross-Series moves transfer prose, keep both ends atomic, and never insert the destination snippet twice. |
| Edit contracts | CLI-authored and directly supplied copies distinguish raw replacements from content snippets; source citations still compare verbatim source. |
| Saved reviews | Answer and disposition resumes, chief copies and turn batches retain raw form; incompatible representations refuse at admission. |
| Docket | Both transcription routes retain raw replacements, omit unchanged places and preserve explicit deletion and recorded source identities. |
| Setting | Untouched raw form remains exact under the existing output newline policy. Only changed material needing destination formatting is adjusted; a failed destination produces no partial draft run. |
| Reread | Approved prose agrees at its intended place despite different raw formatting; missing or changed content and wrong placement refuse. |
| Python documentation | Plain/raw and adjacent/parenthesized literals expose their full prose; a closing-line comment remains in the same section, with both portions accounted for once. |
| Closing-line directives | Editing a documentation section preserves its closing-line comment outside the literal at the same address. Directive text and effective attachment survive rewriting; moves and deletions either preserve them or refuse. |
| Preservation | Code mutations and protected-text changes still refuse independently of successful prose comparison. |

Use invented examples and the real gather, mark, collate, resume, transcribe and
proof paths. Existing reader, address, writer and preservation assertions remain
required. Include long wrapped sections and repeated-word cases when checking
alignment cost and ambiguity. Raw equality remains required for untouched form;
any authorized setting normalization has its own explicit expected result.
