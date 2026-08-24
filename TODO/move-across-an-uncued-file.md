# A move to a file the run never cued is refused as though it were malformed

```
Status:   open
Progress: 5 of 6 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-20 (Roy, 2026-08-20: 'we have an addresser back, but that is because
          we need a way to state any file in the project -- except we currently do not
          cue every file')
Ruled:    2026-08-20 — 2026-08-20 -- RULED. Roy: *"on the move and add piece we should
          allow the address to be either cues or line number for files OUTSIDE of
          the censused range. It was a complication in the previous runs when there was
          an obvious out-of-bounds solution that the agents couldn't take."* !! THE BAN
          ON LINE NUMBERS HAS A REASON, AND THE REASON DOES NOT REACH OUTSIDE THE RUN. A
          line number is refused INSIDE the census because THIS RUN edits prose and
          every edit shifts the lines below it -- so a record written against one is
          stale the moment the galley writes. A file outside the run is not edited by
          it, so its line numbers do not move, and a line number is both stable enough
          and the only thing the agent can know. ! So the rule is not 'never a line
          number'; it is 'never a line number for a place this run can name properly'. !
          MEASURED CONSEQUENCE OF NOT HAVING THIS: a real finding with an obvious
          destination was unstateable, and the agent had no route to file it. Roy saw it
          happen in live runs. ! Applies to `move` destinations and to `add`.
Landed:   2026-08-20 — 2026-08-20 -- the move half. A LINE destination is allowed when
          the file it names is not in the census and still refused by name when it is;
          an ADDRESS for an uncued file gets its own message naming the file and
          saying the run never cued it, instead of the shared 'not a place in the
          census'. desk._in_scope answers the one question, and three tests pin it.
UNBLOCKED: 2026-08-23 — THE GALLEY QUESTION THE `add` HALF WAITED ON IS ANSWERED, AND
           THE ANSWER IS THAT THE ADDRESS SURVIVED. Roy's 2026-08-20 caution was
           *'galley is still up in the air on how it is going to work, so that may lose
           the address again.'* Verified 2026-08-23: after the galley/compositor split,
           `galley.py:5` still states *"`--edits` is `{"<address>": "<the replacement
           text>"}` -- the same address the record carries, so nothing between stage 5
           and the galley has to convert"*, and `galley.py:341-344` still requires it.
           ! So the caution is spent and the `add` half is ordinary work.
```

## Objective

**A move to a file the run never cued is refused as though it were malformed.** The `move`
half landed 2026-08-20 -- verified 2026-08-23 at `desk.py:547-552`, where `_in_scope` splits
the two causes and the uncued case gets its own message: *"never cued -- it has no places.
Cite the line instead"*.

! **The `add` half did not land, and the reason it was held is gone.** An `add`'s target is the
RECORD'S OWN address, not a payload field, so citing an uncued file means a record under no
page -- which `address_problem` (`desk.py:556`, `entry_for(...) is None`) refuses and the
galley could not apply. That was deferred behind a question about whether the galley would keep
taking addresses at all. It kept them.

## Tasks

- [x] T1 -- !! THE ADDRESS FORM SURVIVES FOR EXACTLY ONE REASON -- a `move` may name
      ANOTHER FILE. `reviewer-brief.md`: *'down, another file, or out of the code
      entirely -- all move'*. A page envelope makes a record's OWN place a bare
      cue, but a cross-page destination cannot be one.
- [x] T2 -- !! AND THE RUN ONLY CUES WHAT IS IN SCOPE. `census.py` is handed the
      files a change touched; everything else has no places at all. So a correct
      address for a real file is unresolvable whenever that file was not in the
      same diff.
- [x] T3 -- `desk.py` returned `move's destination {addr} is not a place in the
      census` for BOTH causes -- a wrong address, and a right address for a file
      nobody censused. ! FIXED 2026-08-20 and verified 2026-08-23 at
      `desk.py:547-552`: `_in_scope` splits them and the uncued case says so.
- [x] T4 -- * RULING WANTED: what a `move` to an uncued file MEANS. RULED and
      implemented as shape (a) -- refuse, but say WHY, so the reviewer knows the
      citation was right and the scope was short.
- [x] T5 -- SUPERSEDED. *'Do NOT over-build the address form for this yet'* rested
      on Roy's 2026-08-20 caution that *'galley is still up in the air on how it is
      going to work, so that may lose the address again.'* VERIFIED 2026-08-23: it
      did not. `galley.py:5` and `galley.py:341-344` still key `--edits` on the same
      address the record carries, after the galley/compositor split. Both reasons the
      address form exists are intact.
- [ ] T6 -- DO THE `add` HALF. Roy's ruling names `move` AND `add`, but an `add`'s
      target is the RECORD'S OWN address, so citing an uncued file means a record
      under no page -- refused by `address_problem` at `desk.py:556` because
      `entry_for` returns None. Verify: an `add` whose address names a file the run
      never censused is either accepted with a line-numbered destination, or refused
      with the same message `_in_scope` gives a `move` -- not the shared
      *"not a place in the census"* -- and a test pins which.
