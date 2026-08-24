# Four values are computed on every page and read by nobody

```
Status:   open
Progress: 3 of 8 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (simplify round 7, 2026-08-22 -- found by Pyright and by reading,
          not by dead_sweep.py, which is blind to unused parameters and tuple elements)
RE-CHECKED: 2026-08-23 — 2026-08-23. Task 6 is a measurement the file itself says is
            deliberately not counted -- a record, not a task. Task 8 is done: front-
            matter-protection-is-python-only is SUPERSEDED in completed/, and the stale
            citations in dead-sweep-skips-private are resolved (page._SHEBANG,
            page._CODING and Cues.first_code_line/last_code_line are all deleted).
RE-VERIFIED: 2026-08-23 — 2026-08-23, every live claim re-read in the tree. STILL LIVE:
             `page.documentable` (page.py:341-343) still returns
             `dict[int, tuple[int, int, str]]` and addresser.py:783 still unpacks
             `_insert_at, at_step, side`, with `lexer.document_declarations`
             (lexer.py:1526) the other consumer; the `Kind.MATTER` branch in `attach` is
             page.py:332-333; `record.prose_paragraphs` is record.py:645 and still
             returns `list[tuple[int, dict]]`; `code_lines` and `declarations` are still
             computed at page.py:419-420 and again at page.py:725-726; and `language_for`
             is imported from `language` by compositor.py:68 and from `lexer` by
             galley.py:89. ! T2 is a RECORD of a correction already made in round 7 and
             names the same work as T1 -- ticked.
```

## Objective

**Four values are computed on every page and read by nobody, and `dead_sweep.py` is blind to
every one of them.** The sweep reports *"0 shipped names nothing reads"* while an unused
PARAMETER, an unused DATACLASS FIELD, an unread TUPLE ELEMENT and an unreachable BRANCH all sit
in the shipped tree -- because it looks for names no module imports, and none of these is a name.

! **THE COUNT IN THIS FILE HAS NEVER AGREED WITH ITSELF**, and it is not load-bearing: the
heading said *four*, the Objective said *five*, and the boxes name six sites. The SITES are the
work. Nobody should re-derive the number; the list below is what to check.

!! **PYRIGHT FOUND THREE OF THEM, ON LINES THIS SESSION HAD JUST EDITED.** `_insert` in
`lexer.py`, `_insert_at` in `addresser.py`, `rel` in `compositor.py`. ! Two of the three were
already spelled with a leading underscore, which is the convention for *deliberately ignored* --
so the code was ANNOUNCING that a value it is handed is thrown away, at both consumers of the
same tuple, and nothing asked why the tuple has three elements.

! **The prose beside them was wrong in the way that keeps this invisible.** The docstring of
`page.documentable` said the insert line is what `page.documented_by` walks up from. There is no
`documented_by`; the walk is `lexer.document_declarations`, and it walks up from the DECLARING
line. **A citation to a function that does not exist is what a reader checks the claim against**,
so the three-fact tuple read as three facts for as long as the citation stood. Round 7 corrected
the citation, which is what exposed the tuple.

!! **NONE OF THIS IS A COMMENT FIX, WHICH IS WHY IT IS HERE RATHER THAN IN THAT ROUND.** Each one
changes a signature, a return type or a branch: the tuple loses an element at three sites, the
`Cues` would have to carry what `places_on` already computed so `page_for` stops recomputing
it, the matter branch of `attach` may have a test as its only caller, and `prose_paragraphs`
loses the index that only a test reads.

! **The two repeated full-file scans are the one with a measured cost and it is small** --
the comparable double pass in `census.py` is 21 ms over 6,429 paragraphs. **Do not work these for
speed.** The reason to work them is that a value nobody reads is a value nobody can be wrong
about, and it is where the next false docstring attaches.

## Tasks

- [ ] T1 -- THE INSERT LINE IS COMPUTED FOR EVERY DECLARATION AND READ BY NOBODY.
      `page.documentable` (page.py:341-343) returns `index -> (the LINE the doc
      occupies, the code index it is set before, WHICH SIDE)`. Both consumers throw
      the first away: addresser.py:783 unpacks `_insert_at, at_step, side` and
      `lexer.document_declarations` (lexer.py:1526) unpacks `(line, _insert,
      above)` and walks up from the DECLARING line instead. ! Pyright flags both,
      which is how it was found. Verify: the return type is a 2-tuple, both
      consumers unpack two, and `uv run ty check` over the shipped scripts passes.
- [x] T2 -- RECORD, not a task. ! ITS PROSE CITED A FUNCTION THAT DOES NOT EXIST --
      `page.documented_by`, at two sites, named as the thing that reads the insert
      line. CORRECTED in round 7 to `lexer.document_declarations`, which is what
      actually walks. The THREE-FACT tuple that the correction exposed as a
      two-fact tuple is T1, and this box named the same work.
- [ ] T3 -- The `Kind.MATTER` BRANCH IN `attach` IS UNREACHABLE FROM PRODUCTION.
      It is page.py:332-333; `page_for` short-circuits every matter paragraph and
      reaches `attach` only in the `else` beneath it, and the retype above converts
      a DECLARING matter run only. ! The comment beside the branch records that it
      WAS dead once and was repaired, so check the four `test_cues.py` fixtures
      before cutting -- a test may be the only caller, which is a different
      finding. Verify: either the branch is gone and the suite is green, or this
      file records that a test is its only caller.
- [ ] T4 -- `record.prose_paragraphs` RETURNS AN INDEX NOTHING PRODUCTION READS.
      It is record.py:645, typed `list[tuple[int, dict]]`, and the sole production
      caller is `for _, b in ...`; only `tests/test_record.py` reads the int. ! It
      is the last survivor of index-keyed records, which two comments in that same
      file document as gone. Verify: the return type carries no index and the suite
      is green.
- [ ] T5 -- TWO FULL-FILE SCANS ARE RUN TWICE PER PAGE. `places_on` computes
      `code_lines(text, prose)` and `declarations(text, lang, code)` at
      page.py:419-420 and returns only the `Cues`; `page_for` then computes both
      again with identical arguments at page.py:725-726. ! NOT fixed in round 7
      because the fix is a signature change and `places_on` has four test callers
      that read the cues alone. The duplicated `vars()` rebuild between them WAS
      hoisted. Verify: each is computed once per page, and the four test callers
      still pass.
- [x] T6 -- RECORD, not a task. ! MEASURED AND DELIBERATELY NOT COUNTED: the double
      `prose_numbers` pass in `census.py` is 21 ms over 6,429 paragraphs. Real
      duplication, too cheap to sell as efficiency -- recorded so nobody re-measures
      it.
- [ ] T7 -- `language_for` IS TAKEN FROM TWO DIFFERENT MODULES. compositor.py:68
      imports it from `language` and galley.py:89 from the re-export in `lexer`, for
      the same function. ! Round 7 narrowed the compositor comment that claimed the
      two direct importers were *"the only two that may ask a language anything"* --
      false, seven other sites call it -- but which import a module SHOULD take is
      unruled. Verify: one rule stated in one place, both imports obeying it, and
      the comment at compositor.py:66 saying what the rule is.
- [x] T8 -- FINISHED. TWO TODOs DESCRIBED A FUNCTION THAT NO LONGER EXISTS.
      `front-matter-protection-is-python-only.md` was written throughout as though
      `mark_matter` were live; it is SUPERSEDED in `completed/`.
      `dead-sweep-skips-private.md` cited page.py:793-794 for `_SHEBANG`/`_CODING`,
      which round 7 deleted; those citations are resolved. ! Neither was deleted --
      a TODO is superseded and checked.
