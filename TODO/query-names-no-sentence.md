# A `query` names no sentence, so two marks on one place cannot be told apart

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, the first end-to-end run with a real block-context
          agent: it returned two marks on each of two places and reported that nothing
          linked its query to the sentence it queried, so it put the sentence in
          `reason`)
```

## Objective

A `query` names no sentence, so two marks on one place cannot be told apart.

## Tasks

- [ ] Decide whether a `query` owes a key naming its sentence. Verify: `docs/the-
      mark.md` states the answer for `query` as plainly as it does for `correct`,
      and `desk/mark.parse` enforces whatever it says.
- [ ] A reviewer can say WHICH sentence it is querying without using `reason`.
      Verify: a mark written from the brief puts the queried sentence in a field a
      checker reads, not in prose.
- [ ] `_sentence_key` is correct for `query` either way. Verify: two queries at
      one place resolve the same way the ruling says they should -- today each
      gets `id(mark)` and can never be found to share a sentence.
