# Four values are computed on every page and read by nobody

```
Status:   open
Progress: 0 of 8 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-22 (simplify round 7, 2026-08-22 -- found by Pyright and by reading,
          not by dead_sweep.py, which is blind to unused parameters and tuple elements)
```

## Objective

**Five things are computed on every page and read by nobody, and `dead_sweep.py` is blind to
every one of them.** The sweep reports *"0 shipped names nothing reads"* while an unused
PARAMETER, an unused DATACLASS FIELD, an unread TUPLE ELEMENT and an unreachable BRANCH all sit
in the shipped tree -- because it looks for names no module imports, and none of these is a name.

!! **PYRIGHT FOUND THREE OF THEM, ON LINES THIS SESSION HAD JUST EDITED.** `_insert` in
`lexer.py`, `_insert_at` in `addresser.py`, `rel` in `compositor.py`. ! Two of the three were
already spelled with a leading underscore, which is the convention for *deliberately ignored* --
so the code was ANNOUNCING that a value it is handed is thrown away, at both consumers of the
same tuple, and nothing asked why the tuple has three elements.

! **The prose beside them was wrong in the way that keeps this invisible.** `page.documentable`'s
docstring said the insert line is what `page.documented_by` walks up from. There is no
`documented_by`; the walk is `lexer.document_declarations`, and it walks up from the DECLARING
line. **A citation to a function that does not exist is what a reader checks the claim against**,
so the three-fact tuple read as three facts for as long as the citation stood. Round 7 corrected
the citation, which is what exposed the tuple.

!! **NONE OF THIS IS A COMMENT FIX, WHICH IS WHY IT IS HERE RATHER THAN IN THAT ROUND.** Each one
changes a signature, a return type or a branch: the tuple loses an element at three sites, the
`Cues` would have to carry what `places_on` already computed so `page_for` stops recomputing
it, `attach`'s matter branch may have a test as its only caller, and `prose_paragraphs` loses the
index that only a test reads.

! **The two repeated full-file scans are the one with a measured cost and it is small** --
`census.py`'s comparable double pass is 21 ms over 6,429 paragraphs. **Do not work these for
speed.** The reason to work them is that a value nobody reads is a value nobody can be wrong
about, and it is where the next false docstring attaches.

## Tasks

- [ ] THE INSERT LINE IS COMPUTED FOR EVERY DECLARATION AND READ BY NOBODY.
      `page.documentable` returns `index -> (the LINE the doc occupies, the code
      index it is set before, WHICH SIDE)`. Both consumers throw the first away:
      `addresser.py` unpacks `_insert_at, at_step, side` and `lexer.py`'s
      `document_declarations` unpacks `(line, _insert, above)` and walks up from
      the DECLARING line instead. ! Pyright flags both, which is how it was found.
- [ ] ! AND ITS PROSE CITED A FUNCTION THAT DOES NOT EXIST --
      `page.documented_by`, at two sites, named as the thing that reads the insert
      line. Corrected in round 7 to `lexer.document_declarations`, which is what
      actually walks; the THREE-FACT tuple that the correction exposed as a two-
      fact tuple is this task.
- [ ] `attach`'s `Kind.MATTER` BRANCH IS UNREACHABLE FROM PRODUCTION. `page_for`
      short-circuits every matter paragraph and reaches `attach` only in the
      `else` beneath it; the retype above converts a DECLARING matter run only. !
      The comment beside the branch records that it WAS dead once and was
      repaired, so check the four `test_cues.py` fixtures before cutting -- a
      test may be the only caller, which is a different finding.
- [ ] `record.prose_paragraphs` RETURNS AN INDEX NOTHING PRODUCTION READS. Its
      type is `list[tuple[int, dict]]` and the sole production caller is `for _, b
      in ...`; only `tests/test_record.py` reads the int. ! It is the last
      survivor of index-keyed records, which two comments in that same file
      document as gone.
- [ ] TWO FULL-FILE SCANS ARE RUN TWICE PER PAGE. `places_on` computes
      `code_lines(text, prose)` and `declarations(text, lang, code)` and returns
      only the `Cues`; `page_for` then computes both again with identical
      arguments. ! NOT fixed in round 7 because the fix is a signature change and
      `places_on` has four test callers that read the cues alone. The
      duplicated `vars()` rebuild between them WAS hoisted.
- [ ] ! MEASURED AND DELIBERATELY NOT COUNTED: `census.py`'s double
      `prose_numbers` pass is 21 ms over 6,429 paragraphs. Real duplication, too
      cheap to sell as efficiency -- recorded so nobody re-measures it.
- [ ] `language_for` IS TAKEN FROM TWO DIFFERENT MODULES. `compositor.py` imports
      it from `language` and `galley.py` from `lexer`'s re-export, for the same
      function. ! Round 7 narrowed the compositor comment that claimed the two
      direct importers were *"the only two that may ask a language anything"* --
      false, seven other sites call it -- but which import a module SHOULD take is
      unruled.
- [ ] TWO TODOs DESCRIBE A FUNCTION THAT NO LONGER EXISTS. `front-matter-
      protection-is-python-only.md` is written throughout as though `mark_matter`
      were live; it was removed and its five comment citations were cut in round
      7. `dead-sweep-skips-private.md` cites `page.py:793-794` for
      `_SHEBANG`/`_CODING`, which round 7 deleted. ! Neither is deleted -- a TODO
      is superseded and checked -- but both need their premise restated before
      anyone works them.
