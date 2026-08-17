# The record is a template someone parses, and it should be a value

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    Roy (* 1 ruling) * session
Raised:   2026-08-17, by Roy, after three parser defects of one shape in one day
```

## Objective

**A reviewer fills in a text form and `verdicts.py` reconstructs a table from it by guessing
where each field ends.** Roy: *"this is clearly that we are passing around the 'wrong' data
structure if the error is coming from how the agent has to fill out the template. This says we
should be using a real class or something that it can paste into and knows that it is receiving
strings, not 'can I parse this into the table'."*

Every defect in
[`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
is a boundary guess. The guessing is the defect surface, and it exists only because the record
travels as prose.

## What the change would actually buy

| | today | as a value |
| --- | --- | --- |
| **D7** malformed citation absorbed into the entry above | `SOURCES` repeats a line, and a line that parses as neither citation nor continuation joins its neighbour | a list of `{cite, verbatim}`; a malformed element is reported AS that element |
| **D8** bare label absorbed into the field above | a label is a label only with a value after it, at column 0 | an empty field is an empty string |
| **blank line ambiguity** | content inside a field, separator between records -- the wrong choice was 0.2.0's worst defect, refusing 113 of one reviewer's 134 correct findings | a string carries newlines; there is nothing to disambiguate |
| **field order, indentation, duplicate stems** | rules the reviewer must hold and the parser must enforce | gone with the format |

! **D9 is REDUCED, not killed.** Structure removes the outer quotes and the `drop:` marker, so
a reviewer stops embedding a quoted sentence inside a prose field. But the SPAN still comes from
file text carrying the file's markup, and matching a claimed sentence against it stays fuzzy.
`EDGE` survives this change.

! **Untouched:** whether the claim is TRUE, and whether the address matches the census. Those
are the checks worth having, and they are not the ones that have been breaking.

## !! The counter-argument, which is measured and from today

**A structured format's failure is TOTAL where a template's is partial.** On 2026-08-17 a YAML
frontmatter error dropped an entire agent's metadata -- silently, through every release to date.
Hand-written JSON with embedded multi-line strings is exactly where escaping goes wrong, and a
reviewer writing a 200-record report by hand will produce a malformed one.

! **The failure modes are still not equally bad, and that is the argument for changing.** A
parse error NAMES ITS OWN POSITION. A merged field blames the innocent neighbour, and sends the
reader to fix correct work -- which is the complaint this whole class exists under. Trading a
loud total failure for a quiet local one is the right direction; it is not a free trade.

## ! What is NOT established

- **That an agent writes the structured form more reliably than the template.** Nobody has
  measured it. The comparison that matters is malformed-report rate, and both formats have one.
- **That it can be hand-written at all.** A record carries two whole blocks of source text.
  Whether that survives JSON escaping in practice is an empirical question with an easy answer:
  try it on the reports already on disk.
- **Which format.** JSON escapes newlines and is unreadable in a diff; TOML has multi-line
  literals and no list-of-objects ergonomics; YAML has block scalars that suit this exactly and
  a footgun this repo was bitten by today.

## !! Timing

**Two sessions are mid-run against the current record contract.** Changing it now strands them,
and the contract changed once already today. This is a 0.3.0-scale breaking change, and it wants
the runs that are in flight to finish first.

## Tasks

- [ ] * **Rule on whether the record becomes a value, and in what format.** The three candidates
      and their trade-offs are above; the deciding evidence is the escaping question below, not
      an argument.

- [ ] **Take the malformed-report rate for BOTH formats before choosing.** Convert the reports
      already on disk -- four from this repo's own smoke test, plus whatever the live runs
      leave -- and count what a reviewer would have had to get right. ! This is available now
      and settles the "not established" points by measurement rather than by preference.

- [ ] **Try the round trip on a real record.** Take one carrying two multi-line blocks with
      comment markers, emphasis and quotes; write it in each candidate format; read it back and
      compare byte for byte. A format that cannot carry `BLOCK` and `CHANGE` intact is
      disqualified whatever else it offers.

- [ ] **Say what happens to a report that does not parse.** Today a malformed record is named
      and counted fatal while the rest of the report still joins. A total parse failure has no
      such middle, so the run needs an answer: refuse the reviewer, or ask it again.

- [ ] **Keep `verdicts.py`'s SEMANTIC checks whatever the format.** Address against census,
      citation resolution, verbatim-half lookup, CLAIM-covers-CHANGE, contradictions. Only
      `parse_report` and the record's shape are in scope; deleting a check because the new
      format made it awkward is how the synthesised block ends up unchecked.

- [ ] **Update `reviewer-brief.md` and the four role files together**, and re-run
      `scripts/check_vocabulary.py`. The record contract is taught in the brief and the brief is
      pasted into four prompts.

## Related

- [`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
  -- the three defects that prompted this. ! If the record becomes a value, that file closes for
  `parse_report` and stays open for `removed_spans`.
- [`re-review-is-ordered-everywhere-and-defined-nowhere`](re-review-is-ordered-everywhere-and-defined-nowhere.md)
  -- a round-2 record is an ordinary record, so it inherits whatever shape is chosen here.
