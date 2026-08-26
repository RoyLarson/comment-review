# An empty place is not citable, and the row cut's safety argument says it is

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-25 (backend, 2026-08-25, while cleaning up after the write-chain
          branch)
Updated:  2026-08-25 — DIRECTION FROM ROY, 2026-08-25, and it corrects how this file
          framed the fix. The fix is NOT to put empty places back in the binder -- the
          row cut stands. It is to REIMPLEMENT THE CLI to find an empty place from
          several sources: anchor_num, anchor_line, original_line and cue. What it
          returns is a RECORD, not just an address, so an agent can generate the
          verdict, the copy chief can make a notation from it, and the proof-setter
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
```

## Objective

An empty place is not citable, and the row cut's safety argument says it is.

## Tasks

- [ ] Decide how an absent place is resolved now that anchor_line is gone -- from
      neighbouring rows original_start and original_end, or by re-reading the
      page. Requires-Roy: it decides whether the addresser needs the repo as well
      as the census
- [ ] Implement it. Verify: asking for the empty b place above a line of code
      answers its address
- [ ] Make bind's docstring true -- either the mechanism works, or the sentence
      stops promising it
- [ ] A test over a real binder for a place the binder does NOT carry. Verify: it
      fails against the current code
