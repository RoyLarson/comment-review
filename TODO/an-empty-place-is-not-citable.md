# An empty place is not citable, and the row cut's safety argument says it is

```
Status:   open
Progress: 1 of 4 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-08-25 (backend, 2026-08-25, while cleaning up after the write-chain
          branch)
Updated:  2026-08-25 — DIRECTION FROM ROY, 2026-08-25, and it corrects how this file
          framed the fix. The fix is NOT to put empty places back in the binder -- the
          row cut stands. It is to REIMPLEMENT THE CLI to find an empty place from
          several sources: anchor_num, anchor_line, original_line and cue. What it
          returns is a RECORD, not just an address, so an agent can generate the
          verdict, the copy chief can make an alteration from it, and the proof-setter
          carries that into the flow. WHAT THIS MEANS CONCRETELY: anchor_num and
          anchor_line are alive and correct -- they are methods on Cues, called today by
          binder/page.py and scripts/render_page.py. The CLI cannot reach them because
          it never builds a page, and its own docstring states that as a choice: this
          module reads no source file, the census is the only input. That was sufficient
          while rows carried anchor_line and anchor_num; since the eleven-field cut it
          is what makes the CLI blind. So the requires-Roy question this file asked --
          whether the addresser needs the repo as well as the census -- is ANSWERED: it
          resolves from the page. AND THERE IS A SECOND, MORE DIRECT ANSWER. Roy: the
          other important script was the little map with the cue on each line so that
          the agents could read the map and directly ask for or state the cue they
          wanted instead of looking for it by those indirect ways. That is
          scripts/render_page.py --show margin. The two are complements: the map lets an
          agent NAME a cue it can see, the CLI lets one ASK for a cue it can only
          describe by anchor.
Updated:  2026-08-25 — THREE MORE CORRECTIONS FROM ROY, 2026-08-25. FIRST, --check IS
          NOT THIS COMMAND'S ROLE. Its question -- does every address in this binder
          still resolve -- compares a saved artifact against the file now, which is
          verification, not lookup. It leaves. SECOND, THE NAME commands/addresser IS
          BAD. Roy: commands/look_up_address, maybe a little long but it is specific.
          The module is named for the machinery it fronts rather than for the question
          it answers, and the machinery is reading/addresser, which is a different
          thing. THIRD, AND IT IS ITS OWN DEFECT CLASS: the docstring line -- this
          module reads no source file, the census is the only input -- was WRONG TO
          WRITE, not merely wrong now. Roy: It implied a constraint that the system HAD
          to live by instead of a constraint that the code was written to because the
          system was available. The sentence was TRUE and still wrong. It described what
          the code did and read as a rule about what the code MAY do, so when the row
          cut removed the only positions that module could see, the honest fix was to
          read the page and the docstring said that was out of bounds. Recorded as
          decision-log.md Process #29. THE SHAPE OF THE REBUILD, from the code:
          commands/look_up_address parses, flows/page_for.page_of produces the page, and
          Cues answers -- above(line) and beside(line) ARE the inverse lookup for series
          b and c, documents(ordinal) for a, file_places() for f, with anchor_of,
          anchor_line and gap_bounds supplying the rest of the record. Nothing new is
          needed. The binder dropped 91 percent of places; the PAGE never did.
Updated:  2026-08-25 — CORRECTION, 2026-08-25, and it is mine. I wrote that --check
          genuinely wants the census because its question is whether every address in
          this binder still resolves -- a comparison between a saved artifact and the
          file now. THAT IS NOT WHAT IT DOES. _check reads rows and never opens the
          file. It asks two things: UNADDRESSED, meaning the census cannot name the
          place at all, and SHARED, meaning two paragraphs answer to one address.
          Neither compares anything against the file. Roy: that is the sha and the
          prove-unchanged roles, the addresser doesn't need it. Both halves of that
          hold. The staleness question I invented for --check is answered by the sha in
          ONE comparison before anything is parsed, which is the same argument that
          retired galley.drifted. And the question --check actually asks is whether the
          ADDRESSING is self-consistent, which is a property of the addresser's own
          output and not a lookup command's business. WHERE IT GOES IS NOT DECIDED HERE.
          Under the new shape the lookup reads a PAGE, and a page cannot produce a
          shared address if the addresser is correct -- so the check belongs with the
          addressing machinery or as a gate over it, if it is kept at all. NOTE ITS OWN
          DOCSTRING MAY HAVE RETIRED HALF OF IT: SHARED is now a fault too, and the one
          shape that produced it is fixed -- a licence header and the run below the
          module docstring both answered to b0, and b0 is now the file's own front
          matter alone. If that was the only construction, SHARED can no longer fail.
          Worth measuring before anyone ports it.
Updated:  2026-08-26 — The ASK is built: `carry` -- flows/carry.py plus
          commands/carry.py -- takes a binder, a page and one of three lookups (cue,
          line+series, anchor_num+series) and adds that empty place's row to the binder.
          Roy: "build the little cli point that allows the agents to get a specific
          empty record and add it to the binder. Look up by anchor_num, line_num, and
          cue." It checks the binder sha against the page first, refuses a place that
          already holds prose, and inserts the row in reading order. SO THE add VERDICT
          HAS A PLACE TO CITE, which is what bind's docstring promised. WHAT IS NOT
          DONE: for_anchor's fallback in binder/addresses.py is still unreachable -- it
          resolves an absent place by POSITION and reads anchor_line, a field the
          eleven-field cut removed, so its arithmetic always sees 0. Tasks 1 and 2 are
          about THAT mechanism and stay open; a reviewer asking `addresser --anchor
          <line> --series b` still gets no answer. `carry` answers the same question by
          a different route, from the page rather than from the binder.
          ! THIS NOTE WAS WRITTEN TWICE. The first attempt inlined it in a `python -c`
          inside a bash command, and the shell RAN the two backticked spans before
          Python saw them -- `carry: command not found`, `addresser: command not found`
          -- so both vanished and the command still exited 0. Exactly what CLAUDE.md
          records about a backtick reaching the shell.
```

## Objective

An empty place is not citable, and the row cut's safety argument says it is.

## Tasks

- [?] T1 | Decide how an absent place is resolved now that anchor_line is gone
      -- from neighbouring rows original_start and original_end, or by
      re-reading the page. Requires-Roy: it decides whether the addresser needs
      the repo as well as the census
- [ ] T2 | Implement it. Verify: asking for the empty b place above a line of
      code answers its address
- [ ] T3 | Make bind's docstring true -- either the mechanism works, or the
      sentence stops promising it
- [x] T4 | FINISHED | unknown | A test over a real binder for a place the binder
      does NOT carry. Verify: it fails against the current code
