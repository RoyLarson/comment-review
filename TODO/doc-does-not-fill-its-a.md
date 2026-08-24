# The doc-to-declaration join landed, and doc-kind-unresolved now fires on the wrong runs

```
Status:   open
Progress: 4 of 6 tasks done
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
          `declares` WAS -1 IN EVERY NON-PYTHON CASE. ! SO THE JOIN IS THE PAGE'S --
          Roy: *"this is something the page needs to resolve probably."*
RE-CHECKED: 2026-08-23 — 2026-08-23. THE JOIN HAS LANDED, so tasks 2, 3 and 6 are
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

!! **THE ANNOTATION IS INVERTED AGAINST THE JOIN.** A run the census has already ruled IS a
declaration's documentation is handed to the reviewer as an open question, and a run the census
has ruled documents NOTHING is handed over as one too -- while the one case that is genuinely
arguable, the blank-separated join, is the one left unmarked and charged to the cap.

! It costs a reviewer real work. `compact.md:99` routes `comment` + `doc-kind-unresolved` to
**UNKNOWN -- ask, or carry it at length**, and `:113` explains the stamp. So the pass asks a
human to confirm a fact the census emitted two fields earlier, and does not ask about the one it
guessed.

! Python is unaffected: `paragraphs_stdlib` has always carried `declares` from the AST. This is
the lexical tier only.

## Tasks

- [x] T1 -- MEASURED 2026-08-20, moved to the Objective: on `/// The one doc.` above
      `fn one() {}` the doc was a `b1` with `declares=-1` while `a1` reported `undocumented`.
      Re-run 2026-08-23, it is `a1` with `declares=1`.

- [x] T2 -- FINISHED. The keyword list made the join computable and it is built: `declarations()`
      reports the declaring lines and `document_declarations()` sets `declares` on the run that
      documents each one.

- [x] T3 -- FINISHED. The doc LEAVES the `b` series when it joins. Verified 2026-08-23: the Rust
      `///` is `a1` and the gap above `fn one() {}` is `b0` -- different addresses, no place
      shared.

- [x] T4 -- Python is unaffected -- its docstrings already carry `declares` from the AST. A
      statement of scope, moved to the Objective.

- [ ] T5 -- MAKE `flag_structural_docs` READ `declares` INSTEAD OF RE-DERIVING IT. The two
      functions use different rules (nearness vs adjacency) and produce the inverted table above.
      Verify, all three through `page_for` on go: a run with `declares >= 0` carries NO
      `doc-kind-unresolved`; a run with `declares == -1` above a non-declaring line carries none
      either; and whatever remains genuinely unresolved is named in `compact.md:113`. ! Both
      functions run inside `page_for` (`page.py:698` then `:726`), so ordering is the only
      obstacle and it is `page_for`'s to change.

- [ ] * T6 -- RULE which adjacency rule is right for go and ruby, since fixing T5 by reading
      `declares` adopts NEARNESS wholesale. `document_declarations` joins across one blank line
      on a corpus measurement (`:1559-1563`, 23 ties); `flag_structural_docs` states that both
      languages require the doc to TOUCH. Both cannot be the language's rule. It finishes when
      one of the two comments is corrected to cite the other.
