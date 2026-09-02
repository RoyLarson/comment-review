# Four defects in collator.py, found by reading only the code

```
Status:   open
Progress: 6 of 29 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-08-30 (2026-08-30, from the blind rewrite of collator.py -- the prose was
          deleted whole and written back by an agent with no access to the vocabulary,
          the docs, the prototype, git history or the built copy under plugins)
Pending:  2026-08-30 — the four single-defect files -- move-onto-itself-deletes, crlf-
          verbatim-never-matches, cache-keyed-without-root, cite-at-raises-on-a-nondigit
          -- STAND until the board migration lands, and are superseded into this file in
          one pass then. Roy, 2026-08-30. Do not close them by hand
```

## Objective

Four defects in collator.py, found by reading only the code.

## Tasks

- [x] T1 | Refuse a `move` whose `claim.to` equals its own `address`, by name.
      Verify: `desk.mark.parse` returns a named problem -- today it returns (mark,
      []), measured 2026-08-30.
- [x] T2 | Prove the docket cannot carry that shape. Verify: a test asserts no
      alteration is a delete with no matching write, and it FAILS against today's
      code, which produces a docket entry of path m.py, cue b1, text None.
- [ ] T3 | Check the neighbouring shapes. Verify: a `move` across files, and one
      whose `to` names a place the binder does not carry, each reach a named
      outcome rather than a silent delete.
- [ ] T4 | Reproduce the CRLF mismatch as a failing test over a real CRLF file.
      Verify: a two-line `verbatim` taken verbatim from that file is reported as
      not found. MEASURED: the window is rejoined with a newline while `_lines`
      preserved the carriage returns.
- [?] T5 | Decide which side normalises -- the window, the `verbatim`, or both
      at the boundary. Verify: a single-line `verbatim` still matches, and the
      choice is stated where `_lines` says it preserves the endings.
- [ ] T6 | Check the same rejoin elsewhere. Verify: no other comparison in `src/`
      splits on real line endings and rejoins with one spelling.
- [ ] T7 | Reproduce the cache collision: one cache, two roots holding the same
      path with different text. Verify: the second read returns the first root's
      lines, and the test fails today.
- [ ] T8 | Key the cache on the root as well, or refuse a cache handed a second
      root. Verify: the staged design cannot answer from the wrong tree -- a run
      reads an original at one stage and a revise at the next.
- [ ] T9 | Reproduce the cite guard. Verify: `_cite_at` raises `ValueError` on a
      superscript line number today, and a test asserts a named problem instead.
- [ ] T10 | Return a problem rather than raising. Verify: `verify_report` over an
      edit_copy holding one malformed cite reports it and still checks every other
      mark -- today one bad cite aborts the whole report.
- [ ] T11 | Audit the other guards for the same shape. Verify: no `isdigit()` in
      `src/` is followed by an `int()` that can still fail.
- [x] T12 | Implement the topological order over the resolved moves, where an edge
      B to A means B's origin is A's destination, so B vacates the address before
      A fills it. Verify: two independent moves emit in an order that does not
      depend on which role's copy was read first, and a move whose origin another
      move fills is emitted first -- measured 2026-08-30, four alterations reach
      the docket in walk order with deletes and writes interleaved.
- [x] T13 | Implement the cycle refusal. Verify: a set of moves forming a cycle is
      carried forward as a re-read naming the cycle, driven with a Reconciled
      built directly, since no cycle reaches the resolution step through reconcile
      today.
- [x] T14 | Implement the test that a chained move does not settle FOR A STATED
      REASON. Verify: giving move a quotes_original key makes the chain settle
      under today's grouping, and the DAG rule refuses it anyway -- so the
      protection does not rest on _sentence_key returning id(mark), which is a
      side effect of a function whose docstring is about two adds.
- [ ] T15 | Update `MalformedMark`'s docstring at `desk/collator.py:621-630`. It
      reads "a mark whose shape is unreadable cannot be grouped by the place it
      touches, and a place grouped wrongly is settled wrongly", implying
      `places`/`reconcile` is where a malformed mark's shape is caught. That
      stopped being true on the only live path when `flows/collate.py` landed:
      `reconcile` has exactly one caller in `src/` (`flows.collate.collate`) and
      `places` only one (inside `reconcile`), and `collate` runs `_reconcilable`
      first, which drops every entry `desk.collator.problems_in` already reported
      before `reconcile` ever sees it -- so the raise this docstring describes
      cannot fire from that path. Per `TODO/galley-refusals-cannot-fire.md`'s
      ruling -- a guard at the boundary and a guard at the point of use is
      defensible depth, and the guard stays, but say which one is load-bearing --
      state in the docstring that `problems_in` (run by every caller of `collate`,
      before `reconcile`) is what enforces this on the live path, and that
      `places`'/`reconcile`'s own raise is depth: reachable only by a caller that
      reaches `places` without going through `collate`'s check first. Verify: the
      docstring names `problems_in` as load-bearing and its own raise as depth,
      and `places` called directly (bypassing `collate`) still raises
      `MalformedMark` on a malformed entry -- so the guard being called depth is
      itself checkable rather than asserted.
- [ ] T16 | Implement a `Problem` in `desk.collator.problems_in` for a sheet that
      is not an object and for a `marks` that is not a list, which
      `collator.py:483-485` skips silently. Verify: `problems_in` over a copy
      whose `sheets` holds two strings returns a routable problem naming the role;
      today it returns `[]`, so the module header's claim at lines 27-31 does not
      hold at the sheet level.
- [ ] T17 | Implement the `isinstance(sheets, list)` guard in
      `desk.collator.tally`, the only sheet-walker without one, and stop its
      membership test raising on an unhashable `instruction`. Verify:
      `tally({'sheets': 7})`, `tally({'sheets': None})` and `tally` over a mark
      whose `instruction` is `['clean']` each return counts; all three raise
      `TypeError` today.
- [ ] T18 | Implement a test that drives `collate()` from `reconcile` through
      `_move_order` and can go red, covering the path the two critical move
      defects live on. Verify: `tests/test_collate.py:349`'s only assertion is no
      longer wrapped in a guard its own docstring records as never firing, and
      `test_a_move_resolves_only_if_BOTH_its_ends_resolve` goes red when
      `_pair_moves` is deleted -- its docstring states today that it would not.
- [ ] T19 | Implement a refusal for an address that is not `path@cue`, so a bare
      cue cannot settle and reach the docket. Verify: two roles returning `b1` and
      `b5` give a named problem instead of one docket page `{'path': '', 'sha':
      '', 'alterations': [{'cue': ''}, {'cue': ''}]}`; today `collate` returns
      `problems == []` and `drift == []`, and the chief sheet is `{'path': '',
      'sha': '', 'marks': [...]}`.
- [ ] T20 | Update `desk.collator.problems_in`'s `Returns:` at lines 447-450,
      which calls `ruled` the number of entries carrying an instruction while
      lines 491-493 count every entry that is not `untouched`. Verify: the
      `Returns:` agrees with the `!!` paragraph at 431-435, and a marks list of
      three entries, none carrying an instruction, still reports `ruled = 2`.
- [ ] T21 | Update the module docstring's copy-level list at
      `desk/collator.py:50-54`, which says an entry that is not an object produces
      a `Problem` with nothing naming a mark, and omits the `read_from` problem at
      477-479. Verify: the list holds four cases, and it says the address is `""`
      because the entry has none to read; `problems_in` over `{"marks": ["not an
      object"]}` returns `('', 'mark 1 is not an object')`, which names the mark.
- [ ] T22 | Update `desk.collator._cite_at`'s digit test so it accepts ASCII
      digits only. Verify: a cite whose line number is written in Arabic-Indic
      digits no longer returns `('a.py', 12)` -- a line number no page ever
      emitted.
- [ ] T23 | Update `desk.collator._touches`' sentence at lines 605-606, which says
      a `move` whose destination is its own origin gives one address, as though
      such a mark still reaches it. Verify: the sentence names
      `desk.mark._destination_problems` as what refuses that mark now -- T1 of
      this file landed it -- and marks its own branch as depth, which is the
      template T15 applies to `MalformedMark`.
- [ ] T24 | Update `desk/collator.py:63` and `flows/collate.py:361-365` so one
      rule about importing a private name across modules is stated once and both
      files obey it. Verify: either `collator.py` stops importing
      `_read_from_problem` from `binder.binder`, or `_chief_copy`'s ~15 duplicated
      lines cite the import as allowed; no sentence in either file contradicts the
      other.
- [ ] T25 | Update the module docstring's member roll at `desk/collator.py:3-25`
      to account for `WITHIN`, `Cache`, `UnnamedRole`, `MalformedMark`, `Placed`,
      `Reconciled` and `OUTCOMES`, and restate lines 45-46 by member rather than
      by file-order range. Verify: every public name the module defines appears in
      the roll or in the four-kind paragraph, and no sentence says `nothing above`
      or `nothing below` a file position.
        > 2026-08-31 P42 deleted UnnamedRole -- places takes a MasterProof, whose
        > 2026-08-31 copies each carry a role. The roll this box asks for should not
        > 2026-08-31 list it; the other six names stand.
- [ ] T26 | Update `desk.collator._alteration_text:979` so a whitespace-only
      `change` on a `drop` is a delete rather than three spaces of text. Verify:
      `parse` accepting `change='   '` on a `drop` yields an alteration whose text
      is null, and the docstring at 972-975 covers the whitespace case as well as
      the empty string.
- [ ] T27 | Delete drift detection from the middle, per `decision-log.md
      Process: #62` -- `desk.collator.drift_in`, the `drift` field on
      `flows.collate.Collated`, and the `DRIFT` exit code and its reporting in
      `commands/collate.py`. The middle touches no files, so whether a page
      moved is a question it has no stake in. Verify: `grep -rn "drift"
      src/comment_review/` returns nothing, the exit codes are a closed set with
      no gap where DRIFT was, and the suite stays green.
- [x] T28 | Both are deleted; flows.mark_errors answers what they did. The seven test functions that called them are repointed rather than dropped, the ruled count is derived in the tests that assert it, and ten present-tense prose mentions are corrected while eight historical ones stay. | 0edefdc | Delete
      problems_in and unruled, which flows.mark_errors replaced, and the tests
      that assert their shape
        > 2026-09-01 MEASURED 2026-09-01 after P52: neither has a production caller.
        > 2026-09-01 mark_errors answers both -- the unruled half and the refused half
        > 2026-09-01 -- and problems_in's ruled count is read by nothing. 29 test refs.
- [ ] T29 | Delete the three remaining cross-area imports named in
      tests/test_areas.py KNOWN. Verify: that set is empty and the test still
      bites
        > 2026-09-02 conventions.md called these filed on 2026-08-31; no task did
