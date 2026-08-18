# The bridge landed and the rewrite did not

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    session * Roy (* 1 ruling -- where the verdict table lives)
Raised:   2026-08-17, by /simplify over the 0.2.3 branch
```

## Objective

`claim_text` renders a record's typed `claim` OBJECT back into the marker STRING the 0.2.x
checks read, and its own docstring calls that a bridge, kept *"before anything is rewritten to
read the object directly."* The bridge shipped; the rewrite did not. Four checks were then
found reading the generated string where the field was sitting beside them, and each was wrong
in a different way -- two had stopped firing, one fired on the wrong records, one disagreed
with `record.py --check` about the same record. Those four are fixed. **The pattern is not**:
`ruled_text` still marker-searches `false:` / `drop:` / `from:` back out of a string this
module generated, and it feeds `block_problem`, `edit_problem`, `contradictions` and
`unrecorded_findings`.

! **Generate-then-reparse is the defect class the record change exists to end** -- D7, D8 and
D9, all three of them a boundary guessed wrong. It now happens inside one module instead of
between a reviewer and a parser, which is better and is not the same as fixed.

## Tasks

- [ ] **Normalise a 0.2.x record into `claim_fields` at `load_report`.** `record.claim_object`
      already converts a text `CLAIM` into the typed object, using the same `ANCHOR_NAME` and
      `ANCHOR_SIDE` it imports from `verdicts.py` for exactly that agreement. Doing it at the
      one place both formats meet leaves ONE dual path in the codebase and lets every check
      read fields only. Verify: `_said` and `_claim_values` lose their fallback arms, and the
      deprecated parser keeps working unchanged.

- [ ] **Then `ruled_text` reads `claim_fields[...]` rather than re-parsing.** Verify: a `false`
      value containing the literal `/ true:` survives, which today truncates.

- [ ] * **Rule where `Verdict` and `VERDICTS` live.** `record.py` announces itself as *"what a
      RECORD is"* and derives `allowed()` entirely from a table in `verdicts.py`; `verdicts.py`
      imports nothing back. Moving the table and the three claim regexes into `record.py` would
      leave `verdicts.py` as the join and the citation checks -- one subject each. ! It is a
      ruling because this repo's one-subject-per-module rule is what makes it right or wrong,
      and that rule is Roy's.

- [ ] **`verdicts.load_report` knows the record's field names, and `record.py` declares them.**
      `records`, `block`, `verdict`, `claim`, `sources` as `{cite, verbatim}`, `change` as a
      line array, `code_concerns` -- all of it restated in a module that does not own it. A
      `record.load(path, text)` is the seam, and it is where the task above belongs.

- [ ] **The diagnostic speaks the deprecated format.** A JSON record missing a claim key falls
      to `spec.claim_help`, which says *'drop needs the sentence in CLAIM, as `drop: "..."`'* --
      a format the reviewer never wrote in. `record.claim_problems` produces the right message
      and the join does not run it.

- [ ] **`sources` is a typed pair round-tripped through a string.** `load_report` flattens
      `{cite, verbatim}` into `"cite | verbatim"` and `citation_problem` partitions it back.
      Not a live defect -- the first-pipe partition holds -- but it is the same shape and it
      goes away with the task above.

## Related

- [`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
  -- D7, D8 and D9, the three defects that made the record a value.
- [`the-record-is-a-parsed-template-and-should-be-a-value`](completed/the-record-is-a-parsed-template-and-should-be-a-value.md)
  -- the change that built the bridge, and the ruling that it was temporary.
