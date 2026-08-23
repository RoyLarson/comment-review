# The bridge landed and the rewrite did not

```
Status:   in-progress
Progress: 5 of 10 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-17, by /simplify over the 0.2.3 branch
Updated:  2026-08-18 — the cycle is gone and the claim is typed at the seam
Corrected: 2026-08-19 — the census-shape split is FIVE readers and four idioms, not
           three -- and verdicts.py has no dict handling at all, so a {blocks: [...]}
           census gives a traceback
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

- [x] **DONE `113e2f8`**, in `parse_report` where the two formats meet. Both formats now arrive typed; a text record used to leave `claim_fields` empty and every check fell back to searching a rendered string.

- [x] **DONE `113e2f8`.** Verified on the case the task named: `false: "the cap is 5 / true: not really"` returns the whole value from the field and truncates to `the cap is 5` under the scan. ! `ruled_text` is what `block_problem`, `edit_problem` and `contradictions` compare on, so a truncated original is a finding checked against the wrong sentence.

- [x] * **RULED 2026-08-18: `record.py`**, which already derived `allowed()` from the table and imported six names back. Moving it inverted the cycle that blocked the task above.

- [ ] **`verdicts.load_report` knows the record's field names, and `record.py` declares them.**
      `records`, `block`, `verdict`, `claim`, `sources` as `{cite, verbatim}`, `change` as a
      line array, `code_concerns` -- all of it restated in a module that does not own it. A
      `record.load(path, text)` is the seam, and it is where the task above belongs.

- [x] **DONE `d01c367`.** All five `claim_help` rows name `claim.<key>` instead of the retired marker form, and four tests that asserted the old phrasing now assert the KEY, which is what the record carries.

- [ ] **`sources` is a typed pair round-tripped through a string.** `load_report` flattens
      `{cite, verbatim}` into `"cite | verbatim"` and `citation_problem` partitions it back.
      Not a live defect -- the first-pipe partition holds -- but it is the same shape and it
      goes away with the task above.

- [x] **DONE `0599091`.** `ANCHOR_EXAMPLE` is one string -- published in the form and run against the pattern -- and two tests hold them equal. ! Verified by MUTATION: loosening the pattern to `.*` fails three tests.

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
- [ ] !! **IT IS FIVE READERS, NOT THREE, AND ONE CRASHES.** Measured 2026-08-19:
      `cues` uses `.get("blocks", [])`, `galley` `census["blocks"]`,
      `locator` an `entries()` helper, `record` `loaded["blocks"]`, and
      **`verdicts.py` has no dict handling at all** -- a `{"blocks": [...]}`
      census gives an `AttributeError` traceback. `census.py` emits a bare list
      unconditionally, so nothing exercises the other branch.

## Related

- [`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
  -- D7, D8 and D9, the three defects that made the record a value.
- [`the-record-is-a-parsed-template-and-should-be-a-value`](completed/the-record-is-a-parsed-template-and-should-be-a-value.md)
  -- the change that built the bridge, and the ruling that it was temporary.
