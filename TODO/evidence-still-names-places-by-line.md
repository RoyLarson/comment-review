# Evidence and every downstream artifact still name places by line

```
Status:   decision-needed
Progress: 0 of 9 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
```

## Objective

Evidence and every downstream artifact still name places by line.

## Tasks

- [ ] !! **The SOURCES verification hole is the WHOLE FILE, not the ±3 window.**
      `_resolve_lines` accepts an unbounded range on purpose and `source_problem`
      windows the whole range -- so `file:1-868` reduces the verbatim check to
      *"this string occurs somewhere in this file"*. **A fabricated citation to a
      real file passes today.** Fix this ahead of the fuzz.
- [ ] * **RULED but UNIMPLEMENTED: `address:lines`.** Roy, 2026-08-18: *"if it is
      in the code it should be the address:lines in the adress"*, the lines
      counted WITHIN the block, 1-based, blanks included. It removes the fuzz
      entirely -- the block bounds the range -- but needs two decisions first: **a
      code RANGE has no address expression** (every code line is its own one-line
      `c`, so the function-sized range ruled admissible 2026-08-17 becomes 20
      addresses), and **sources cite callers in files nobody censused** (the
      brief's own example cites `redacted_pkg/export/invoice.py:88`). Census on demand, or
      keep the line form there and accept the fuzz?
- [ ] * **RULE NEEDED: what bounds a FREEFORM source.** Once "outside the censused
      documents" waives verification, a reviewer can label any fabricated evidence
      that way. Candidate: a freeform source is admissible only ALONGSIDE at least
      one resolvable one; a finding resting on freeform alone is a `query`.
- [ ] **CODE CONCERNS carry no place whatsoever** -- bare strings, attributed to a
      role, gated by nothing. The one channel for a non-prose finding hands the
      human a sentence with no way to find the code.
- [ ] **Stage 8 REVIEW has no citation form at all.** It is asked to report
      "naming what and where" in free prose, and it has `--resolve` for READING
      but nothing for REPORTING. Its predates-this-run list is the next round's
      input and cannot be joined to any census.
- [ ] **Stage 6 COMPACT names blocks by nothing.** Its input contract is KIND /
      original / edited / cap / style sheet, and its return is "blocks condensed,
      blocks left at length". 6b must then galley what it shortened. An address
      leaks none of the reasoning the narrow contract protects.
- [ ] **Two agent files instruct a `move` destination in the form the gate now
      refuses** -- `function-context` (*"belongs to a different line in this
      function"*) and `ownership-context` (*"the destination is the line above"*).
      Neither mentions the address or the tools. ! Role prose is budget-fixed:
      route through [`role-rule-register`](role-rule-register.md).
- [ ] **`census.py` still WRITES the line form into the census a reviewer reads**
      -- the `repeated-literal` note emits `{n} also in prose at a.py:12`, while
      the row above it leads with `@b12`. `b.address` is on the same object.
- [ ] **`residue-check.md` keys the scratch copy by `file:start-end`**, inside
      stage 7b -- the one stage actively moving lines.
