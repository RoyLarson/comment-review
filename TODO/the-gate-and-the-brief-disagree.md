# The gate and the brief disagree about what a finding must carry

```
Status:   open
Progress: 1 of 6 tasks done
Owner:    session · Roy (2 rulings made, 1 left)
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

⚠ **The first one is already half-ruled**, and it is the only one where the two now actively
contradict rather than merely differ — a reviewer following the brief supplies evidence that
nothing reads.

## Tasks

- [ ] ⭐ **`query` — the brief now REQUIRES `EVIDENCE` and `QUOTE`; the gate exempts both.**
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

      ⚠ **The prose was corrected 2026-08-16 without the code changing.** `verdicts.py` had
      argued the exemption as settled fact at THREE sites -- `payload_problem`,
      `evidence_problem` and the `QUERY_ATTEMPTED` comment -- each giving a reason the exemption
      is correct. All three now mark it DISPUTED and UNRESOLVED. The gate still behaves the old
      way; it no longer claims to be right about it.

- [x] **`QUOTE`'s row lost two rules the gate still enforces.** ⚠ **HALF RULED 2026-08-16.**
      Roy: *"that is why I dropped the 12 character limit in the other files"* — the brief moved
      first and the gate follows. `MIN_NEEDLE` is now **1**: a zero-length quote is not a quote,
      and nothing longer is refused for length. ⚠ The 12-line floor had inverted on short code
      lines — `x = 1`, `pass`, `return` — where its only route through was to quote MORE than
      was read. ⚠ The `query` exemption at the same line is the OTHER half and is still open,
      under task 1.

- [ ] **[superseded rule text, kept for the record]** The brief's field table said
      *"VERBATIM and at least 12 characters. Required for every verdict except `clean` and
      `query`"* and now says only *"VERBATIM."* Both survive in code: `MIN_NEEDLE` at
      `sk-scripts/verdicts.py:387`, the exemption at `:380`. Decide which side moves.

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

- [ ] **`CODE CONCERNS` is not parsed or gated at all** — zero occurrences in
      `sk-scripts/verdicts.py`. `ref/reviewer-brief.md` defines the section and tells reviewers
      what belongs in it; nothing reads it, so a reviewer that puts a comment finding there has
      hidden it from the join.
