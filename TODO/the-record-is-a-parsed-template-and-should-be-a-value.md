# The record is a template someone parses, and it should be a value

```
Status:   open
Progress: 1 of 7 tasks done
Owner:    session * Roy (* 2 rulings, 1 made -- the format; the interface is open)
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

!! **D9 IS KILLED TOO, IF THE RECORD CARRIES SENTENCES RATHER THAN BLOBS.** Roy: *"D9 is only a
diff problem if the comparison is outside of code."*

That has two readings and only one of them works:

- **Carry the removed span as a FIELD**, computed where the edit was made. ! This reintroduces
  trust. `removed_spans` exists because it is *"the reliable answer where `CLAIM` is the
  reviewer's own account of it"*, and a field the reviewer fills is that account again.
- **Compare SENTENCES, not tokens.** If `BLOCK` and `CHANGE` carry lists of sentences, what was
  removed is a SET DIFFERENCE over whole sentences rather than an alignment over tokens. **A
  span then cannot begin mid-sentence**, which is the mechanism of both D9 shapes -- the
  swallowed word before a parenthetical, and the emphasis delimiters bracketing a claim.

!! **The second is not new vocabulary.** This system already declares the sentence as its unit
-- *"a verdict rules on a SENTENCE, not on a block"* -- and
[`the-unit-of-review-is-the-statement-not-the-block`](completed/the-unit-of-review-is-the-statement-not-the-block.md)
is closed. **The DATA never caught up with the rule.** Every remaining token-level comparison is
the block-shaped structure outliving the block-shaped decision.

! `EDGE` survives either way, for normalising a sentence to compare it. What it stops doing is
deciding where a span BEGINS.

! **Who splits the sentences is the open question**, and it is the one that decides whether this
is cheap. The census already holds the block; splitting prose into sentences is not free and
gets it wrong on abbreviations, code samples and lists.

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
- **Whether the reviewer can be kept out of the SYNTAX entirely.** Roy: *"we give them a cli to
  emit one. No ambiguity on if they write it correctly."* ! The hazard moves rather than
  vanishing if the values reach that CLI through a SHELL: multi-line text in an argument is the
  same escaping problem one layer out, and heredocs mangled `\n` and `\w` five-plus times in the
  session that raised this. The safe shape is the agent writing the file with its FILE-WRITE
  tool -- no shell in the path -- and a CLI validating it, which is `run_context.py --template`
  and `--check` already.

## * RULED 2026-08-17: JSON

Not on taste, and not on "no stdlib writer" alone. Roy: *"python chose to make it read only
since it is a config format more than a storage format."*

| | verdict |
| --- | --- |
| **TOML** | **wrong KIND of format.** `tomllib` is read-only BY DESIGN -- it is a config language, and a record is storage. ! That forecloses adding `tomli_w`: the objection is not that the stdlib cannot write it, it is that writing it was never the point of the format |
| **YAML** | **not in the stdlib at all** -- `yaml` and `ruamel.yaml` are both third party, so it fails the shipped-code rule before preference enters. ! It is also rejected on preference (Roy: *"I really don't like yaml"*) and on having dropped an agent's entire metadata in this tree on 2026-08-17, silently, through every release to date |
| **JSON** | `json.dumps` is stdlib, and it round-tripped a block carrying emphasis, quotes, a tab, a backslash, a trailing brace and a blank line BYTE-IDENTICALLY. Measured 2026-08-17 |

!! **JSON is not merely preferred: it is the only stdlib format that is both WRITABLE and SAFE
to load from a file an agent produced.** The whole stdlib set, checked 2026-08-17 on the pinned
3.11:

| module | writes? | usable |
| --- | --- | --- |
| `json` | `dumps`/`dump` | **yes** |
| `tomllib` | none | read-only by design |
| `configparser`, `csv` | no nesting or flat only | no |
| `plistlib` | `dumps`/`dump` | technically -- an Apple XML format no reader here would recognise |
| `xml.etree` | `tostring`/`write` | **no -- it EXPANDS ENTITIES**; see below |
| `pickle`, `shelve`, `dill` | `dumps`/`dump` | **NO -- they execute arbitrary code on load** |
| `marshal` | `dumps`/`dump` | no -- executes what it loads, and version-unstable |

!! **TWO stdlib formats are disqualified on SECURITY, for different reasons, and both would have
been reached for by someone optimising away an escaping problem.**

- **`pickle`** round-trips anything, including the multi-line source blocks a record carries.
  Loading it from a file an AGENT wrote is arbitrary code execution inside a review tool.
- **`xml.etree`** is the one this list originally MISSED. Roy: *"technically that does leave us
  the worst of the worst options -- xml itself -- that is stdlib."* It does not execute code; it
  expands entities. Measured 2026-08-17 on the pinned 3.11: **three levels of nested internal
  entity became 1000 characters**, and the unbounded form of that shape is a denial of service.
  `defusedxml` is the answer where XML is unavoidable, and it is third party -- so here the
  answer is that XML is avoidable.

! **Recorded here and nowhere else, deliberately.** A gate refusing these imports was written
and removed the same day: nothing in this repo reaches for them, and no one relitigates a format
already ruled. Roy: *"thorough - also very unnecessary."* The decision is the artifact worth
keeping; the enforcement was defence against a scenario with no path to it.

! The cost accepted with JSON: it escapes newlines, so a record is unreadable in a diff, and it
carries no comments. **That is what the CLI is for** -- nobody reads or writes the encoding by
hand.

## !! Timing

**Two sessions are mid-run against the current record contract.** Changing it now strands them,
and the contract changed once already today. This is a 0.3.0-scale breaking change, and it wants
the runs that are in flight to finish first.

## Tasks

- [x] * **RULED 2026-08-17: the record becomes a value, and the format is JSON.** See above.

- [ ] * **Decide the INTERFACE the reviewer uses**, now that the format is settled. A CLI it
      calls per record, a template it fills, or a schema it writes to with its FILE-WRITE tool.
      !! The deciding constraint is that **no multi-line value passes through a SHELL** -- that
      is the same escaping problem one layer out, and it is the layer that actually failed in
      the session that raised this file.

- [ ] **Take the malformed-report rate on the reports already on disk.** Four from this repo's
      smoke test, plus whatever the live runs leave. ! The format is chosen, so this is no
      longer a format comparison: it measures how often a reviewer gets the CURRENT template
      wrong, which is the number the change has to beat.

- [ ] **Round-trip a real record through JSON.** Already done for one synthetic block -- markers,
      emphasis, quotes, tab, backslash, trailing brace, blank line, byte-identical. ! Repeat it
      on a record from an actual report, because a synthetic block is one someone chose.

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
