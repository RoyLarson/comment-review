# The doc-to-declaration join landed, and doc-kind-unresolved now fires on the wrong runs

```
Status:   closed
Progress: 12 of 12 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-20 (found while adding the per-language declares keyword list,
          2026-08-20)
Measured: 2026-08-20 — 2026-08-20 -- WHAT THE LEXER ALREADY SETTLES, per language. Roy
          asked whether the lexer states that the paragraph is a docstring and not a
          comment. It does where a doc MARKER exists (`///`, `/**`), so syntax alone
          decides the kind. go and ruby have no marker -- a doc comment there IS an
          ordinary comment in the right POSITION, which is exactly what
          `doc_is_structural` means. Python is already `a1` via the AST. !! AND
          `declares` WAS -1 IN EVERY NON-PYTHON CASE. ! SO THE COLLATOR IS THE PAGE'S --
          Roy: *"this is something the page needs to resolve probably."*
RE-CHECKED: 2026-08-23 — 2026-08-23. THE COLLATOR HAS LANDED, so tasks 2, 3 and 6 are
            FINISHED -- verified by calling `page.page_for` on the exact shape this file
            was filed about. ! But re-running the same probe over go turned task 5 from
            a forecast into a measured defect with the sign REVERSED: the runs the
            census now says ARE documentation still carry `doc-kind-unresolved`, and the
            runs it says are NOT are the ones exempted from the cap. See the Objective.
```

## Objective

Documentation classification and address ownership must agree for each language.
Each language establishes its rules independently from its own definition and
authoritative references.

Roy approved following Go's documentation rule: a documentation section must
immediately precede its declaration, with no intervening blank line, to occupy
the declaration's a place. For ordinary mid-file comments, an intervening blank
line leaves the whole section at its b place. The section remains whole in both
cases. Reference: https://go.dev/doc/comment

T7 combined this decision with implementation and code-comment changes. T9
records the approved decision; T10 carries implementation and its verification.
Closing the decision does not claim that the reader has been changed.

Ruby follows RDoc attachment: blank lines and whitespace may separate a
documentation section from its following eligible declaration. There is no
one-blank-line limit. Intervening executable code ends that attachment
candidate. The section occupies the declaration's a place; ordinary mid-file
prose before non-declaration code stays at b. Existing matter and margin rules
still apply. Same-type comments between code lines stay together as one section.

Ruby's comment grammar defines comment delimiters; RDoc defines documentation
attachment. RDoc's Ruby parser, prepare_comments, skips blank lines for both
line comments and embedded documentation blocks:
https://github.com/ruby/rdoc/blob/master/lib/rdoc/parser/ruby.rb#L275-L325 Ruby
syntax reference: https://docs.ruby-lang.org/en/master/syntax/comments_rdoc.html

T8 incorrectly made this language investigation a human decision and checked
agreement between comments instead of behavior. T11 records the evidence in the
lexical-reader design's Ruby documentation section. T12 carries the reader and
fixture work. Verify touching comments, one and several blank lines,
whitespace-only lines, both comment forms, whole blank-separated sections, and
intervening executable code. Check kind, owner, address and line-control
coverage.

T6 updates the compact reference to describe whatever unresolved cases actually
remain after the reader changes. The lexical-reader specification supplies the
current architecture; references to retired helpers in older task checks need
board reconciliation rather than restoring the old implementation.

## !! What is left: two functions ask the same question and answer it differently

`lexer.document_declarations` (`:1541-1563`) joins by NEARNESS: *"PROSE BELONGS TO WHICHEVER SIDE
IT IS NEARER TO, and a TIE goes to the side the language documents on"*, so a run one blank line
above a declaration and with nothing above it IS joined.

`lexer.flag_structural_docs` (`:1482-1487`) stamps `doc-kind-unresolved` by ADJACENCY: *"The
IMMEDIATELY next line. Both languages require a doc comment to touch its declaration, so a run
held off by a blank line is an ORPHAN -- left unmarked here, and charged to the cap."*

MEASURED 2026-08-23, three go files through `page_for`:

| the run | `declares` | series | `doc-kind-unresolved` |
| --- | ---: | --- | --- |
| `// doc` flush above `func one() {}` | 1 | `a1` | **yes** |
| `// doc` flush above `x := 1` (declares nothing) | -1 | `b2` | **yes** |
| `// doc`, one blank, then `func one() {}` | 1 | `a1` | **no** |

!! **THE ANNOTATION IS INVERTED AGAINST THE COLLATOR.** A run the census has already ruled IS a
declaration's documentation is handed to the reviewer as an open question, and a run the census
has ruled documents NOTHING is handed over as one too -- while the one case that is genuinely
arguable, the blank-separated join, is the one left unmarked and charged to the cap.

! It costs a reviewer real work. `compact.md:99` routes `comment` + `doc-kind-unresolved` to
**UNKNOWN -- ask, or carry it at length**, and `:113` explains the stamp. So the pass asks a
human to confirm a fact the census emitted two fields earlier, and does not ask about the one it
guessed.

! **Ordering is the only obstacle to reading `declares` instead of re-deriving it, and it is
`page_for`'s to change**: both functions already run inside `page_for` (`page.py:698` then
`:726`).

! **THE ADJACENCY RULING IS PER-LANGUAGE, SO GO AND RUBY GET A BOX EACH.** Fixing the annotation
by reading `declares` adopts NEARNESS wholesale: `document_declarations` joins across one blank
line on a corpus measurement (`:1559-1563`, 23 ties), while `flag_structural_docs` states that
both languages require the doc to TOUCH. Both cannot be the language's rule, and `CLAUDE.md`'s
rule is that a language takes its definition from its own grammar and never from a neighbour's.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- MEASURED 2026-08-20 and re-run 2026-08-23.
      In the Objective.
- [x] T2 | FINISHED | unknown | T2 -- FINISHED. The keyword list made the
      collator computable and it is built -- `declarations()` reports the
      declaring lines, `document_declarations()` joins them.
- [x] T3 | FINISHED | unknown | T3 -- FINISHED. The doc LEAVES the `b` series
      when it joins -- verified 2026-08-23, the Rust `///` is `a1` and the gap
      above is `b0`. In the Objective.
- [x] T4 | FINISHED | unknown | T4 -- SCOPE, not a task. Python is unaffected;
      its docstrings carry `declares` from the AST. In the Objective.
- [-] T5 | SUPERSEDED -- Paragraph.declares went at 22af63a, so flag_structural_docs has nothing to read instead of re-deriving | 22af63a | T5
      -- Make `flag_structural_docs` read `declares` instead of re-deriving it.
      Verify: on go, a `declares >= 0` run and a `declares == -1` run both stamp
      nothing.
- [-] T6 | SUPERSEDED: doc-kind-unresolved retired (#231); nothing is left unresolved to name | 79cf418f | T6
      -- Name in `compact.md:113` whatever remains genuinely unresolved after
      T5. Verify: the stamp's explanation at :113 names the case that still
      fires.
- [-] T7 | Split into T9 for the approved Go rule and T10 for implementation and matching reader prose | 3376dc0f | T7
      -- * RULE go's adjacency: must a doc comment TOUCH its declaration, or is
      nearest-above enough? Verify: one of the two comments cites the other, for
      go.
- [-] T8 | Replaced by T11 source-backed rule and T12 behavior checks; no human ruling needed | 65a35b1e | T8
      -- * RULE ruby's adjacency, from ruby's own grammar and not from go's.
      Verify: one of the two comments is corrected to cite the other, for ruby.
- [x] T9 | Roy approved immediate adjacency; the objective and lexer spec record the Go rule | 3376dc0f | Record
      Go documentation adjacency; verify the spec requires no blank line before
      the declaration
        > 2026-10-11 Roy approved Go adjacency: no blank before its declaration.
- [-] T10 | Moved to language-reader-go.md | 42f3d3e5 | Implement Go
      documentation adjacency; verify touching comments use a, separated
      comments use b, and reader prose agrees
- [x] T11 | Ruby spec cites RDoc blank-line attachment and retains whole sections | 65a35b1e | Record
      Ruby attachment from authoritative RDoc sources; verify the spec permits
      blank lines and preserves whole sections
- [-] T12 | Moved to language-reader-ruby.md | 42f3d3e5 | Implement Ruby
      attachment; verify blank-separated prose uses a, intervening code blocks
      attachment, and sections stay whole
