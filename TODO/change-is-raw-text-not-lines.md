# The gate demands `change` as a line array and the spec rules it raw text

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, task 9 of the master-proof plan -- an implementer
          noticed the helpers had to match the code rather than the spec, and reported
          it rather than picking one)
```

## Objective

The gate demands `change` as a line array and the spec rules it raw text.

## Tasks

- [ ] Make `problems()` accept `change` as RAW TEXT, per `docs/the-mark.md`.
      Verify: a `correct` whose `change` is the updated paragraph as one string is
      ACCEPTED, and the message that said it 'needs `change` as an ARRAY of lines'
      is gone.
- [ ] Decide what happens to a `change` that IS a list -- refused by name, or
      accepted for one release. Verify: whichever is chosen, a test asserts it,
      and the brief says the same thing as the gate.
- [ ] Make the brief and `docs/the-mark.md` agree with the gate once it moves.
      Verify: a mark written from `reviewer-brief.md` verbatim is accepted, which
      is the check `P1` exists to keep true.
- [ ] Correct `the-fields-do-not-say-a-mark-may-cite-across` T2, which is CHECKED
      and asserts the superseded line-array fact. Verify: that task states raw
      text, or says plainly that it was completed under the old rule and names
      this file.
