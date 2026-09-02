# The tier is dispatched on the language NAME, so a second tokenized language is not a data row

```
Status:   open
Progress: 5 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (/simplify rounds 1 and 2, 2026-08-22, both rounds independently;
          round 2 measured it)
```

## Objective

The tier is dispatched on the language NAME, so a second tokenized language is not a data row.

## Tasks

- [x] T1 | FINISHED | unknown | MEASURED 2026-08-22: language.py:394 is
      literally return tokenized if lang.name == python else lexical, and
      page.py:694 dispatches the READER on the same test while page.py:815/825
      stamps the tier via tier_for. A file can therefore be READ at one tier and
      LABELLED at the other, and half a fix does exactly that
- [x] T2 | FINISHED | unknown | CLAUDE.md CLAIMS THE OPPOSITE AND THE CLAIM IS
      LOAD-BEARING: *adding a language is a data row, not new code*. True for a
      LEXICAL language. For a TOKENIZED one it is three edits in two modules,
      and nothing tells you the third is missing
- [x] T3 | FINISHED | unknown | THE SAME SHAPE IN THREE MORE PLACES:
      census.py:160 gates its name harvester on lang.name != python;
      prove_unchanged.py:176 and referrers.py:53 both re- spell the suffix tuple
      that language.py:99 already owns. Four sites deciding *is this Python*
      four ways
- [x] T4 | FINISHED | unknown | * THE FIX ROUND 2 PROPOSED: tier becomes a FIELD
      on the Language row, so the dispatch reads the row like every other
      per-language rule. ! This is the enabling change for
      python-cannot-read-python -- moving Python off the AST means the tier
      stops being a name test at all
- [x] T5 | FINISHED | unknown | RE-MEASURE AFTER: no module outside language.py
      may test lang.name, and no module may re-spell a suffix tuple. Both are
      greppable, which is what makes this closeable by a stranger
