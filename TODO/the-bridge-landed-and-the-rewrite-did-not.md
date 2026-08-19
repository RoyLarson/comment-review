# The bridge landed and the rewrite did not

```
Status:   open
Progress: 0 of 9 tasks done
Owner:    session * Roy (* 1 ruling -- where the verdict table lives)
Requires-Roy: true
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

!! **THE IMPORT ARROW IS WHY THE FALLBACK STAYED AT THE READERS.** `record.py` imports
`VERDICTS`, the three claim regexes and the deprecated parser FROM `verdicts.py`, and
`verdicts.py` imports nothing back -- so `record.claim_object`, the one function that turns a
0.2.x claim into fields, cannot be called from `load_report` without a cycle. That is not a
tidiness problem: it is the reason each new check written in `verdicts.py` gets its own policy,
and there are seven sites with five policies today. Ruling where the table lives is the
PREREQUISITE for normalising once.

! Measured 2026-08-18, the five policies: `_said` returns "" and lets the caller decide;
`_claim_values` falls back to the whole rendered claim; `_answered` falls back to a regex;
`payload_problem`'s anchor branch tests `claim_fields` explicitly because `or` would read a
present-but-empty field as absent; `declares_scope` uses exactly the `or`-shaped test that
comment warns against. `ruled_text` has no branch at all and still marker-searches the string
this module generated, feeding `block_problem`, `edit_problem`, `contradictions` and
`unrecorded_findings`.

## Tasks

- [ ] **Normalise a 0.2.x record into `claim_fields` at `load_report`.** `record.claim_object`
      already converts a text `CLAIM` into the typed object, using the same `ANCHOR_NAME` and
      `ANCHOR_SIDE` it imports from `verdicts.py` for exactly that agreement. Doing it at the
      one place both formats meet leaves ONE dual path in the codebase and lets every check
      read fields only. Verify: `_said` and `_claim_values` lose their fallback arms, and the
      deprecated parser keeps working unchanged.

- [ ] **Then `ruled_text` reads `claim_fields[...]` rather than re-parsing.** Verify: a `false`
      value containing the literal `/ true:` survives, which today truncates.

- [ ] * **Rule where `Verdict` and `VERDICTS` live. ! THIS GATES THE TASK ABOVE, and is not
      a parallel cleanup.** `record.py` announces itself as *"what a
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

- [ ] **`record.anchor_form` is published as English and enforced from a regex nothing holds
      it equal to.** Every other entry in `allowed()` is derived from the `VERDICTS` table and
      checked against the very thing it published; this one is a hand-written sentence in the
      template and an `ANCHOR_NAME.search` in the checker. Loosen the pattern and the sentence
      silently becomes a lie to the reviewer. ! A `forms` table beside `values` --
      `{"anchor": (ANCHOR_NAME, "the anchor NAMED in backticks")}` -- publishes and enforces one
      object, and `value_problems` loops it exactly as it loops `values`. Where that table
      LIVES is the same ruling as the one above.

- [ ] **Three readers of a census file, and the two new ones unwrap a shape `census.py` cannot
      emit.** `galley.py` and `record.py` both carry
      `census["blocks"] if isinstance(census, dict) else census`; `verdicts.py` does not. The
      only `--json` emitter writes a bare list unconditionally, so the branch defends against
      nothing this tree produces -- and if the dict shape ever did arrive, two readers would
      succeed and the third would take `len(dict)` as the block count. A `census.load_blocks`
      in the module that owns the format is the seam, and `galley.unanswerable` is already
      half of it.
- [ ] **Make `Finding.sources` a typed pair instead of a flattened string.**
      `load_report` renders `{cite, verbatim}` into `"cite | verbatim"` and
      `source_problem` partitions it back. ! The TODO called this "not a live
      defect" and it WAS one: a source carrying `"verbatim": null` rendered the
      word "None" and PASSED, because the cited line contained it. Fixed
      2026-08-18 by putting both halves through `filled`, so what remains is the
      round-trip itself -- a cite containing `|` still splits wrong. ! Blast
      radius is ~20 test call sites that use the string form as a literal.

## Related

- [`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
  -- D7, D8 and D9, the three defects that made the record a value.
- [`the-record-is-a-parsed-template-and-should-be-a-value`](completed/the-record-is-a-parsed-template-and-should-be-a-value.md)
  -- the change that built the bridge, and the ruling that it was temporary.
