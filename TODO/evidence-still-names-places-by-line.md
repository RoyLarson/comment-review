# Evidence and every downstream artifact still name places by line

```
Status:   decision-needed
Progress: 0 of 9 tasks done
Owner:    testing
Requires-Roy: true
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
RE-CHECKED: 2026-08-23 — 2026-08-23. Every one of the nine claims was checked against
            the code and all nine are STILL TRUE; nothing here has been overtaken. The
            file was already well formed -- each box names something a stranger can look
            at -- so only the T labels, the current file:line for each claim, and a
            verify line per task were added. Three of the nine are RULINGS OWED and now
            carry a leading `*`.
```

## Objective

!! **THE ADDRESS REACHED THE RECORD KEY AND A `move`'s DESTINATION, AND STOPPED.** `SOURCES` --
the field the whole evidentiary contract rests on -- is 100% line-form, and four further
artifacts name a place by nothing at all.

!! **THE VERIFICATION HOLE IS THE WHOLE FILE, NOT THE +/-3 WINDOW.** VERIFIED 2026-08-23:
`desk._resolve_lines` (`desk.py:243-285`) accepts an unbounded range on purpose (ruled
2026-08-17: *"a range is where the reviewer looked"*, stated at `:253-255`), and
`source_problem` at `desk.py:343-345` builds its window as
`lines[lineno - 1 - SOURCE_WINDOW : end + SOURCE_WINDOW]` -- the WHOLE range. So `file:1-868`
reduces the verbatim check to *"this string occurs somewhere in this file"* -- **a fabricated
citation to a real file passes today.** That is worth fixing ahead of the fuzz it was filed for.

**Roy ruled the fix on 2026-08-18 and it is unimplemented:** *"the evidence still needs to be
freeform because it could be outside of the censused documents but if it is in the code it should
be the address:lines in the adress"* -- the lines counted WITHIN the block, 1-based, blanks
included. It closes the hole by construction, because the block bounds the range.

! **Two decisions come first.** A code RANGE has no address expression -- every code line is its
own one-line `c`, so the function-sized range explicitly ruled admissible becomes 20 addresses.
And sources cite CALLERS in files nobody censused: the brief's own worked example cites
`redacted_pkg/export/invoice.py:88`.

! **A third is about the freeform half.** Once "outside the censused documents" waives
verification, a reviewer can label any fabricated evidence that way.

## Tasks

- [ ] T1 -- CLOSE THE SOURCES VERIFICATION HOLE, which is the WHOLE FILE and not the +/-3 window.
      `_resolve_lines` accepts an unbounded range and `source_problem` (`desk.py:343-345`) windows
      the whole of it, so `file:1-868` asks only whether the string occurs somewhere in the file.
      Verify: a SOURCES entry citing a wide range with a verbatim half that appears far outside
      the cited lines is REFUSED, and the function-sized range ruled admissible 2026-08-17 still
      passes. Fix this ahead of the fuzz.

- [ ] * T2 -- RULED but UNIMPLEMENTED: `address:lines`. Roy, 2026-08-18: *"if it is in the code it
      should be the address:lines in the adress"*, the lines counted WITHIN the block, 1-based,
      blanks included. Two decisions are owed before it can be built: **a code RANGE has no
      address expression** (every code line is its own one-line `c`, so the function-sized range
      ruled admissible 2026-08-17 becomes 20 addresses), and **sources cite callers in files
      nobody censused** (the brief's own example cites `redacted_pkg/export/invoice.py:88`) --
      census on demand, or keep the line form there and accept the fuzz?

- [ ] * T3 -- RULE what bounds a FREEFORM source. Once "outside the censused documents" waives
      verification, a reviewer can label any fabricated evidence that way. Candidate: a freeform
      source is admissible only ALONGSIDE at least one resolvable one; a finding resting on
      freeform alone is a `query`.

- [ ] T4 -- GIVE `CODE CONCERNS` A PLACE. VERIFIED 2026-08-23: `verdicts.py:694-696` prints
      `f"  {reviewer}: {line}"` -- a bare string attributed to a role and gated by nothing, and
      `reviewer-brief.md:471` asks for exactly that (*"one line, no verdict"*). The one channel
      for a non-prose finding hands the human a sentence with no way to find the code. Verify: a
      `CODE CONCERNS` line carries a resolvable citation and `verdicts.py` refuses one that does
      not resolve.

- [ ] T5 -- GIVE STAGE 8 REVIEW A CITATION FORM. VERIFIED 2026-08-23: `references/review.md:57`
      asks it to report *"naming what and where"* in free prose, and `:74` gives it
      `addresser.py --resolve <ADDRESS>` for READING but nothing for REPORTING. Its
      predates-this-run list is the next round's input and cannot be joined to any census.
      Verify: a stage 8 report entry names an address, and the next round can look it up.

- [ ] T6 -- DECIDE WHAT STAGE 6 COMPACT NAMES A BLOCK BY. VERIFIED 2026-08-23: `compact.md`'s
      input contract is KIND / original / edited / cap / style sheet, and its return is "blocks
      condensed, blocks left at length"; 6b must then galley what it shortened. ! An address
      leaks none of the reasoning the narrow contract protects, which is why this is a decision
      about the contract rather than a defect in it.

- [ ] T7 -- CORRECT THE TWO AGENT FILES THAT INSTRUCT A `move` DESTINATION IN THE LINE FORM THE
      GATE NOW REFUSES. VERIFIED 2026-08-23:
      `agents/comment-review-function-context.md:112` (*"to a different line in this function"*)
      and `agents/comment-review-ownership-context.md:100` (*"and the destination is the line
      above"*). Neither mentions the address or the tools. ! Role prose is budget-fixed: route
      through [`role-rule-register`](role-rule-register.md).

- [ ] T8 -- STOP `census.py` WRITING THE LINE FORM INTO THE CENSUS A REVIEWER READS. VERIFIED
      2026-08-23: `census.py:401` builds `f"{b.path}:{b.start}"` and `:407` emits
      `f"{n} also in prose at {', '.join(others)}"` for the `repeated-literal` note, while the
      row above it leads with `@b12`. `b.address` is on the same object. Verify: the note names
      addresses, and `grep -n "b.start" census.py` shows no citation built from a line number.

- [ ] T9 -- RE-KEY THE RESIDUE CHECK. VERIFIED 2026-08-23: `references/residue-check.md:19` keys
      the scratch copy by *"its `file:start-end`"*, inside stage 7b -- the one stage actively
      moving lines. Verify: the scratch copy is keyed by address, and 7b's own edits cannot
      invalidate the key.
