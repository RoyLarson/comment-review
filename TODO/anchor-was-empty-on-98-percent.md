# Every address carries an anchor, and 98 percent of the census did not

```
Status:   open
Progress: 3 of 4 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (Roy's anchor ruling, 2026-08-19)
Updated:  2026-08-19 — task 3 owes a ruling: does an 'a' anchor become the declaration
          LINE, or stay the NAME
Ruled:    2026-08-19 — Roy, 2026-08-19: 'anchor -- the line of code that an address is
          attached to' and 'drop it -- the line is the anchor.' An a is attached to its
          declaration's LINE; the name is not carried. A module is the one address with
          no line of code and keeps <module>, the language's own name for module-level
          code; every other language gets its declared module name wherever that line
          sits.
```

## Objective

!! **THE ANCHOR WAS WIRED INTO THE RECORD AND NEVER POPULATED.** Roy asked for it earlier in the
same conversation -- *"add the anchor text to the record. That will be useful for the agents to
grep"* -- and `record.SEEDED` became `("address", "anchor")`. The field arrived; the value did
not.

**Measured 2026-08-19 against the commit before the fix: 6,376 of 6,531 blocks in this repo's own
shipped scripts carried an EMPTY anchor -- 98% of the census.**

| kind | blocks with no anchor |
| --- | ---: |
| `margin` | 3,144 |
| `interval` | 2,923 |
| `comment` | 272 |
| `trailing-comment` | 37 |

!! **IT WAS INVISIBLE FROM BOTH ENDS AT ONCE, WHICH IS WHY NO GATE SAW IT.**

- `census.py` printed *"NO COMMENT carries an anchor at either tier"* in its own run summary -- a
  statement of INTENT, so an empty field read as correct.
- `test_record.py::test_only_the_address_and_the_anchor_are_seeded` asserted which KEYS are
  seeded, never that either held a value.
- `record.seeded_problems` checked `address` against the census and did not check `anchor`,
  though both are `SEEDED`.

**The two halves agreed with each other and agreed on nothing.** Roy: *"an anchor missing in a
Record is a broken Record."*

! **AND THE FIX NEEDED NO TOOLING.** A whole exchange went into which build tools a user's project
can be assumed to have -- cargo, go, tsc, gradle -- before Roy cut it off: *"how do we parse to
the end of the line to find the comment and then not keep the string that is the anchor by
definition ... the lexer either knows what is before the trailing comment and can snag the whole
string or it is broken."* Every tier already computes where the comment opens in order to cut
there. The characters before it were known one step earlier and thrown away.

**FIXED in the same session.** This TODO exists because the finding is the reusable part: a field
threaded end to end, a test that checks the key rather than the value, and a producer that
DOCUMENTS the hole as intended behaviour. Everything below is what remains.

## Tasks

- [x] DONE 2026-08-19. `census._anchor_of` states a `c`'s anchor at both
      tiers, `anchor_the_gaps` states a `b`'s by COPYING that line's `c`, and the
      gap at EOF takes the line above. 0 empty anchors over 6,531 blocks.
- [x] DONE 2026-08-19. `record.seeded_problems` refuses a record with no
      anchor, and one whose anchor is not the census's -- with the same 'the tool
      wrote this, so the FILE was edited' message `address` uses.
- [x] ! An `a`'s anchor is still a NAME (`f`, `<module>`) where a `b`'s and a
      `c`'s are the LINE OF CODE. Both are declared in `pcst.Block`. RULING
      WANTED: does an `a` become its declaration LINE too? It would make the field
      one meaning, and it would change what `--anchor NAME --series a|b|c` is
      asked with -- the brief teaches asking by name.
- [ ] The lesson, not the fix: a field threaded end to end, a test asserting the
      KEY rather than the value, and a producer DOCUMENTING the hole as intended
      behaviour. Look for the same shape in the other SEEDED fields and in every
      '! NO x carries a y' line in the shipped scripts.
