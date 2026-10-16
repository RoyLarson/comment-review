# Comment operations by Series

## Purpose

Supply the middle with operations that apply a paragraph's language and Series
rules while it composes approved marks. A move removes its prose from the origin
and adds it at the destination. The language implementation handles comment
markers, delimiters and wrapping; the middle handles marks and their resolution.

This specification defines the shared operation boundary. Each language owns
its definition and implementation choices. Python's implementation is specified
in [Python lexical reader](2026-10-11-python-lexical-reader-design.md).

## Construction and ownership

The flow acquires the installed language definition and checks it against the
saved reading context before constructing the operations for that page. It
supplies a callable that selects the appropriate operations by Series. A review
containing several languages receives the operations appropriate to each page.
Selection by Series occurs within the selected language, rather than in a
process-wide table keyed only by Series.

The middle declares the narrow operation interface it consumes. Language
implementations satisfy that interface. Definitions, scanner state and parser
configuration stay inside those implementations. The middle uses the supplied
operations with its binder and edit-copy text; it does not acquire definitions
or read source files to perform an edit.

The address flow remains responsible for obtaining additional places. Once a
place has been resolved, the enclosing flow supplies its matching operations.
The operation callable neither assigns an address nor reclassifies its Series.

Callables exist only during execution. Binders, edit copies and proofs retain
their data representation. On opening or resuming a saved review, the flow
checks its recorded context and reconstructs the matching operations. A missing
or incompatible implementation produces the existing admission refusal before
marks are applied.

## Operation contract

Operations are pure transformations of supplied paragraph data. They return
updated raw paragraph text or an explicit refusal, leaving their inputs intact.
The supplied data includes the current raw text and the existing placement and
line-control information needed by the operation. Code anchors remain opaque;
an operation may use their occupied width when laying out trailing prose.

| Operation | Responsibility |
| --- | --- |
| Subtract | Find the requested prose uniquely across wrapping and comment markers, remove it, and restore the remaining paragraph's form. Preserve existing absent and ambiguous match refusals. |
| Add | Apply the destination's form to added prose at the placement supplied by the existing mark contract. Preserve the destination's existing prose and the proposed ordering. |
| Flow | Lay out the resulting prose using the paragraph's form, indentation and applicable line controls. Preserve its words and order. |

These are capabilities, not new mark instructions. Existing mark fields retain
their meaning. In particular, a move already supplies the proposed destination
raw text. The integration must use that proposal rather than inventing an
insertion point or appending the snippet again. Add and flow share the same
language implementation used to interpret and retain that proposed form.

The strategy uses the current paragraph for every operation. After one edit,
the next operation receives the resulting raw text; offsets derived from an
earlier version cannot be reused against changed text. The implementation may
derive transient prose-to-raw correspondence internally where removal needs it.

## Series and actual comment form

Series determines the placement rules. Current raw text identifies the actual
comment form within that Series. A language may offer several forms, so Series
alone does not select a unique marker. Existing filled places retain their
form; an empty place uses that language's defined insertion form and the
supplied placement information.

A, B, C and F use their established addressing and section rules. Same-form
sections between code boundaries remain whole, including intervening blanks.
D retains its meaning as leading space and exposes no prose-editing operation.
Protected material remains subject to its existing editing restrictions.

Line comments need their opening and continuation markers. Block comments also
need their closing delimiters. Python documentation needs its own handling of
quotes, raw prefixes, escapes, adjacent literals and closing-line comments.
Those details belong to each language's implementation. Shared mechanics may
be reused, while configuration and assembly remain specific to each language.

## Moves and refusal

The origin operation removes the snippet from the current origin paragraph.
The destination operation handles the supplied destination proposal using its
own language and Series. Moving between languages transfers prose, so origin
markers and literal escaping do not become destination prose.

The move retains its existing atomic approval and composition rules. Both ends
must succeed before their results are accepted. A missing or ambiguous snippet,
unsupported form or unrepresentable result refuses the move without applying
either end. The strategy does not decide approval or resolve competing marks.

## Setting and proof

Operation results use the existing raw-text contract consumed by alterations
and the writer. This interface does not introduce another writer or a source
replacement mechanism. The unresolved shared-line writer representation remains
a separate problem; supplying these operations does not establish its repair.

The proof step independently reads original and drafted source and compares
the executable pieces and their order. Successful prose transformation is not
proof that code is unchanged. The separate local compilation check and the
approved ordering of later formatting remain in force.

## Acceptance evidence

The middle can compose a move using supplied test operations while language
acquisition and source reading are unavailable to it. Its interface exposes
operations and paragraph data without exposing a language definition.

Real language cases demonstrate removal across wrapped lines, retention of
markers and delimiters, empty-origin behavior, explicit empty-destination form,
and refusal of absent or repeated snippets. Consecutive edits exercise the
current text rather than stale positions. Additions retain the proposed order
and are not applied twice.

A move between different languages and Series demonstrates independent origin
and destination behavior. Failure at either end leaves both unchanged. Saved
review resumption reconstructs compatible operations, and changed compatibility
refuses before composition.

Python cases include plain and raw docstrings, escaped characters, adjacent
literals, parenthesized literals and the combined docstring closing comment.
Their real move and drop routes work with host AST, tokenizer and evaluation
entry points forbidden. Existing reader, address, writer and proof checks remain
required; this specification does not relax their assertions.
