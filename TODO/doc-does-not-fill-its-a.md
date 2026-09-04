# The doc-to-declaration join landed, and doc-kind-unresolved now fires on the wrong runs

```
Status:   open
Progress: 5 of 8 tasks closed
Owner:    backend
Requires-Roy: true
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

An above-declaration doc comment used to be addressed as a `b`, never as the declaration's `a`.
**That is fixed.** `lexer.declarations()` reports the declaring lines,
`lexer.document_declarations()` (`lexer.py:1526`) says which run documents which, and
`page.attach()` routes a paragraph with `declares >= 0` to `cues.documents(declares)`
(`page.py:316-318`).

VERIFIED 2026-08-23, `page_for(Path('m.rs'), '/// The one doc.\nfn one() {}\n', rust)`:

```
m.rs@a0  undocumented  declares=0   <module>
m.rs@b0  interval      declares=-1  fn one() {}     <- the gap above, a separate place
m.rs@a1  docstring     declares=1   fn one() {}     <- the doc, in the a series
m.rs@c0  margin        declares=-1  fn one() {}
```

The doc LEFT the `b` series, which is what `a` was introduced for, and no place is shared.

! **WHAT THE ORIGINAL MEASUREMENT READ, 2026-08-20**: on `/// The one doc.` above `fn one() {}`
the doc was a `b1` with `declares=-1` while `a1` reported `undocumented`. Re-run 2026-08-23, it
is `a1` with `declares=1`. The keyword list is what made the collator computable, and it is built.

! **Python is unaffected**: `paragraphs_stdlib` has always carried `declares` from the AST. This
is the lexical tier only, and that is a statement of SCOPE rather than remaining work.

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
- [ ] T6 | T6 -- Name in `compact.md:113` whatever remains genuinely unresolved
      after T5. Verify: the stamp's explanation at :113 names the case that
      still fires.
- [?] T7 | T7 -- * RULE go's adjacency: must a doc comment TOUCH its
      declaration, or is nearest-above enough? Verify: one of the two comments
      cites the other, for go.
- [?] T8 | T8 -- * RULE ruby's adjacency, from ruby's own grammar and not from
      go's. Verify: one of the two comments is corrected to cite the other, for
      ruby.
