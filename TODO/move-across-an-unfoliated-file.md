# A move to a file the run never foliated is refused as though it were malformed

```
Status:   open
Progress: 4 of 6 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (Roy, 2026-08-20: 'we have an addresser back, but that is because
          we need a way to state any file in the project -- except we currently do not
          foliate every file')
Ruled:    2026-08-20 — 2026-08-20 -- RULED. Roy: *"on the move and add piece we should
          allow the address to be either foliation or line number for files OUTSIDE of
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
          `desk.py:462` currently refuses ANY line-numbered destination, and
          `desk.py:476` refuses any address the census does not carry -- both need the
          out-of-range case.
Landed:   2026-08-20 — 2026-08-20 -- the move half. A LINE destination is allowed when
          the file it names is not in the census and still refused by name when it is;
          an ADDRESS for an unfoliated file gets its own message naming the file and
          saying the run never foliated it, instead of the shared 'not a place in the
          census'. desk._in_scope answers the one question, and three tests pin it.
```

## Objective

A move to a file the run never foliated is refused as though it were malformed.

## Tasks

- [x] !! THE ADDRESS FORM SURVIVES FOR EXACTLY ONE REASON -- a `move` may name
      ANOTHER FILE. `reviewer-brief.md`: *'down, another file, or out of the code
      entirely -- all move'*. A page envelope makes a record's OWN place a bare
      folio, but a cross-page destination cannot be one.
- [x] !! AND THE RUN ONLY FOLIATES WHAT IS IN SCOPE. `census.py` is handed the
      files a change touched; everything else has no places at all. So a correct
      address for a real file is unresolvable whenever that file was not in the
      same diff.
- [x] `desk.py:476` returns `move's destination {addr} is not a place in the
      census` for BOTH causes -- a wrong address, and a right address for a file
      nobody censused. A reviewer reading that about a correct citation goes
      looking for an error that is not there. ! The plausible case is ordinary
      ownership-context work: *this comment belongs in the module docstring of
      `other.py`*.
- [x] * RULING WANTED: what a `move` to an unfoliated file MEANS. Three shapes --
      (a) refuse, but say WHY, so the reviewer knows the citation was right and
      the scope was short; (b) widen the run's scope to foliate any file a
      destination names, which makes scope depend on findings; (c) treat it as
      `unavailable`, the shape already used for a destination outside the code,
      and let the human place it.
- [ ] ! Do NOT over-build the address form for this yet. Roy, same day: *'galley
      is still up in the air on how it is going to work, so that may lose the
      address again.'* `galley.py --edits` is keyed by address today and is the
      other cross-page consumer; if the galley stops taking addresses, one of the
      two reasons the form exists goes with it.
- [ ] ! The `add` HALF IS NOT DONE. Roy's ruling names `move` AND `add`, but an
      `add`'s target is the RECORD'S OWN address, not a payload field -- so citing
      an unfoliated file means a record under no page, which `address_problem`
      refuses and the galley could not apply. Blocked on the same galley question
      as task 5.
