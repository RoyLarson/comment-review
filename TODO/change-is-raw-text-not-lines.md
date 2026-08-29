# The gate demands `change` as a line array and the spec rules it raw text

```
Status:   open
Progress: 3 of 4 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, task 9 of the master-proof plan -- an implementer
          noticed the helpers had to match the code rather than the spec, and reported
          it rather than picking one)
Updated:  2026-08-29 — The collator no longer VACATES a paragraph while this is open:
          desk/collator._alteration_text raised nothing on a change that was raw text --
          it joined [] and returned None, which docket.read accepts as the legal delete
          -- and now raises UnusableChange for a change that is not a list of strings,
          or empty on an instruction whose may_empty is False. Which form the gate
          should DEMAND is still this file's question; both forms now fail loudly
          instead of one emptying the page.
Updated:  2026-08-29 — The gate moved to RAW TEXT under mark-is-a-dict-not-a-type.
          desk.mark.parse now accepts a change that is the updated paragraph as one
          string, refuses the retired line-array form BY NAME, and still allows an empty
          change only where the row may_empty. tests/test_mark.py asserts both
          directions and tests/test_brief_worked_example.py runs the brief own example
          through mark --check. That satisfies tasks 1, 2 and 3 of this file; task 4,
          correcting the-fields-do-not-say-a-mark-may-cite-across T2, was NOT done.
          Boxes left for the systems lane to tick, since that pass was scoped to the
          mark type.
```

## Objective

The gate demands `change` as a line array and the spec rules it raw text.

## Tasks

- [x] Make `problems()` accept `change` as RAW TEXT, per `docs/the-mark.md`.
      Verify: a `correct` whose `change` is the updated paragraph as one string is
      ACCEPTED, and the message that said it 'needs `change` as an ARRAY of lines'
      is gone.
- [x] Decide what happens to a `change` that IS a list -- refused by name, or
      accepted for one release. Verify: whichever is chosen, a test asserts it,
      and the brief says the same thing as the gate.
- [x] Make the brief and `docs/the-mark.md` agree with the gate once it moves.
      Verify: a mark written from `reviewer-brief.md` verbatim is accepted, which
      is the check `P1` exists to keep true.
- [ ] Correct `the-fields-do-not-say-a-mark-may-cite-across` T2, which is CHECKED
      and asserts the superseded line-array fact. Verify: that task states raw
      text, or says plainly that it was completed under the old rule and names
      this file.
