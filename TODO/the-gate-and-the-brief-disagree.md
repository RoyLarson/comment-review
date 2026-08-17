# The gate and the brief disagree about what a finding must carry

```
Status:   open
Progress: 5 of 8 tasks done
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

- [ ] **The `add` payload check passes on the bare word "anchor".**
      `sk-scripts/verdicts.py:302-308` accepts any `CHANGE` containing the string `anchor` and
      refuses one that names a declaration without using the word. The brief asks for *"the text
      **and its anchor** — which code, above or below"*, which is a NAMED site, not a word.

- [ ] **`--reviewers` is compared to report file STEMS, never to the published role names.**
      `sk-scripts/verdicts.py:475-479` derives each reviewer from `Path(r).stem` and only checks
      for duplicates. A report named `ownershp-context.md` is accepted as a reviewer called
      `ownershp-context`, and the coverage report then names a role that does not exist.
      ⚠ `scripts/vocabulary.py` now has `Reviewer`, a StrEnum of the six dispatchable names —
      the published list this could be checked against.

- [ ] **`FINDING` is never checked, and `Finding.finding` holds two different things.**
      It carries the reviewer's clause normally and a DIAGNOSTIC STRING when `block == -1`,
      which `:539` prints as `MALFORMED {reviewer}: {finding}`. One field, two meanings,
      distinguished by a sentinel in another field.

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
