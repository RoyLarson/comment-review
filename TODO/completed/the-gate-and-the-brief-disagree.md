# The gate and the brief disagree about what a finding must carry

```
Status:   CLOSED 2026-08-17
Progress: 8 of 8 tasks done
Owner:    session · Roy (3 rulings made, 0 left)
Raised:   2026-08-15 (the vocabulary survey, which collected these while reading for terms)
Re-filed: 2026-08-16 (Roy, on `query` needing EVIDENCE and QUOTE: "this is a TODO on
          the reviewer code")
```

## Objective

**`scripts/verdicts.py` is the gate a reviewer's report has to pass, and in six places it
enforces something the brief does not say, or accepts something the brief forbids.** Either
direction is the same defect: a reviewer writes to the brief and the gate rules on something
else, so a report can be correct-by-the-brief and rejected, or wrong-by-the-brief and admitted.

⚠ **Not vocabulary, and it sat on the vocabulary TODO for a day because the survey collected it
while reading for terms.** Moved here so the vocabulary work could close.

⚠ **The `query` row is RULED and closed, 2026-08-17.** It was the only one where the two
actively contradicted rather than merely differed. The three left differ; none contradicts.

## Tasks

- [x] ⭐ **`query` — the brief now REQUIRES `EVIDENCE` and `QUOTE`; the gate exempts both.**
      Roy rewrote `ref/reviewer-brief.md` on 2026-08-16: *"A `query` requires `EVIDENCE` and
      `QUOTE`(s), by construction — this is where you looked to try to find the answer. These
      are the statements in the code that make it ambiguous."* `sk-scripts/verdicts.py:380`
      returns early on `("clean", "query")`, so a reviewer supplies both and nothing checks
      them. ⚠ The code states a reason at `:375-378` — demanding evidence left two exits,
      inventing a citation or downgrading to `clean` — and Roy's version answers it, because the
      evidence is WHERE YOU LOOKED rather than a line that settles it.

      ⚠ **HALF-RULED 2026-08-16.** Roy: *"query is definitely supposed to have evidence per that
      other TODO."* That settles the DIRECTION — the brief is right and the GATE moves. What the
      gate checks is still open. ⚠ Recommendation for that ruling: if `EVIDENCE` is where you
      looked, the `QUOTE` is verbatim text from that place, so `evidence_problem`'s existing
      check applies to a `query` unchanged and the fix is to drop `query` from the exemption at
      `verdicts.py:342`. Decide before implementing whether `MIN_NEEDLE` and the `SUMMARY`
      right-half check should come with it.

      ⚠ **RULED AND IMPLEMENTED 2026-08-17.** Roy: *"Having the ruling be query and having it
      be related to not my scope needs the reason attached. Is the query one of the three
      variants of query — which one and why"*, then *"It must contain everything to say it was
      looked at and this is why it is query."* Two changes, and they are wider than the task
      asked: `evidence_problem` now exempts `clean` alone, so a `query`'s citations resolve like
      any other verdict's; and `payload_problem` requires the `CHANGE` to NAME one of the
      brief's three shapes in the brief's own words before anything else is read of it.
      `QUERY_SHAPES` is that closed set. ⚠ The named shape is STRIPPED before the attempted-check
      word search, because the ATTEMPTED pattern matches "checkout" and the shape would otherwise
      satisfy the check it is supposed to accompany. `declares_scope` reads the declaration rather
      than sniffing free text. The brief and SKILL.md both lost their DISPUTED notes.

- [x] **`QUOTE`'s row lost two rules the gate still enforces.** ⚠ **HALF RULED 2026-08-16.**
      Roy: *"that is why I dropped the 12 character limit in the other files"* — the brief moved
      first and the gate follows. `MIN_NEEDLE` is now **1**: a zero-length quote is not a quote,
      and nothing longer is refused for length. ⚠ The 12-line floor had inverted on short code
      lines — `x = 1`, `pass`, `return` — where its only route through was to quote MORE than
      was read. ⚠ The `query` exemption at the same line is the OTHER half and is still open,
      under task 1.

- [x] **[superseded rule text, kept for the record — both halves resolved]** The brief's field table said
      *"VERBATIM and at least 12 characters. Required for every verdict except `clean` and
      `query`"* and now says only *"VERBATIM."* Both survive in code: `MIN_NEEDLE` at
      `sk-scripts/verdicts.py:387`, the exemption at `:380`. **Both sides moved:** `MIN_NEEDLE`
      is 1 (task 2) and the exemption is gone (task 1).

- [x] **The `add` payload check passes on the bare word "anchor"** — ⚠ **FIXED 2026-08-17.**
      Two conditions now, and the word "anchor" satisfies neither: `ANCHOR_SIDE` wants a side
      (above, below, before, after) and `ANCHOR_NAME` wants the anchor NAMED IN BACKTICKS.
      Backticks are the repo's own citation form — the brief already says cite by symbol or path,
      never by line number — so "named" is checkable without guessing which token is an
      identifier. `CHANGE  add an anchor comment` used to pass and now does not; ``above
      `retry_budget` `` used to fail for not saying "anchor" and now passes. The brief's `add`
      row states both. Five tests.

- [x] **`--reviewers` is compared to report file STEMS, never to the published role names**
      — ⚠ **FIXED 2026-08-17.** `verdicts.py` imports `Reviewer` from its sibling
      `vocabulary.py` and refuses any stem, and any `--reviewers` name, that is not one of the
      six published roles. A stem is still what keys a reviewer; it just has to be a real role
      name now. Three tests, including one that walks the published names to catch the enum and
      the gate drifting apart.

- [x] **`FINDING` is never checked, and `Finding.finding` holds two different things** —
      ⚠ **FIXED 2026-08-17, and the two halves were one defect.** `parse_report` returns
      `(findings, malformed)`, so a record that names no block never becomes a `Finding` and the
      `block=-1` sentinel is gone from the file. With `FINDING` holding one thing,
      `payload_problem` can require it: every verdict but `clean` states why it was made.
      ⚠ Three consumers each carried their own sentinel filter (`by_block`, `contradictions`,
      `main`) and all three lost it.

- [x] **`CODE CONCERNS` is not parsed or gated at all** — ⚠ **CARRIED, 2026-08-16.** Roy:
      *"told you you can't stop coding agents from trying coding."* The first real run proved
      it: block-context REPRODUCED a code defect (`complete --outcome "a | b"` writes a
      malformed row) while opening the code to settle a comment. `verdicts.py` now parses the
      section and echoes every line, attributed, **ungated** — they are not verdicts, so they
      are neither admissible nor inadmissible, and they print whether or not the gate refuses.
      ⚠ A run that stops at stage 5 must still carry them or the defect dies with the refusal.
      Three tests, including one that they never enter the record parser: a code concern
      counted as a finding would enter coverage arithmetic.

- [x] **[was: CODE CONCERNS is not parsed — carried, see above]** — zero occurrences in
      `sk-scripts/verdicts.py`. `ref/reviewer-brief.md` defines the section and tells reviewers
      what belongs in it; nothing reads it, so a reviewer that puts a comment finding there has
      hidden it from the join.
