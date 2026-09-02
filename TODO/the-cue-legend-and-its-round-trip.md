# The cue letter carries what three fields used to say, and nothing gives the agents the legend or checks they followed it

```
Status:   open
Progress: 0 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-24 (ruling three fields out because the cue letter already states them)
```

## Objective

**`symbol`, `declares` and `original_column` were removed from the census row because the cue
letter already says what they say.** Roy, 2026-08-24: *"they are stating something that the cue
letter states. So we just give the agents the legend for the cue letters and let them run with
it."* `decision-log.md Addressing: #12`.

! **THE ANSWER IS A LEGEND, NOT A FIELD**, and that is a different KIND of answer. A field states
one fact per row and is paid for on every row; a legend states the rule once and is paid for
once. **Neither exists today:** the fields are removed and nothing yet hands a role the letters.

| the letter | the place |
| --- | --- |
| `a` | a declaration's documentation |
| `b` | a gap between two lines of code |
| `c` | the room beside a line of code |
| `f` | the file's own matter -- a licence, a shebang, an index |
| `d` | leading, the space between lines of type. **A LABEL, NOT A PLACE** -- it answers to no anchor, and the rest of the system does not need to know about it |

!! **AND THE CHECK THAT MAKES THE REMOVAL SAFE IS A ROUND TRIP, NOT AN ASSERTION.** Roy: *"we can
use a little bit of pattern matching to ensure that they followed the cue letters in the final
version as well, using a round trip by the lexer to verify that the cues come back with the same
content (except the front matter headache)."*

! **IT IS A DIFFERENT QUESTION FROM THE PAGE SHA.** The SHA -- see
[`a-page-carries-no-identity`](a-page-carries-no-identity.md) -- asks *did the file shift under
us*, before any work. This asks *did the edits land where the cues said*, after it. **A run can
pass the first and fail the second**: nothing shifted underneath, and a role still put an `a`'s
replacement where the `b` was.

!! **THE FRONT MATTER IS THE NAMED EXCEPTION AND IS NOT A DETAIL.** Roy called it *"the front
matter headache"* in the same sentence that asked for the check. The `f` series is the one prose
a filtered listing drops entirely, and `matter-misses-two-languages` records that C and Python
type a licence header as matter while Rust loses the run to the `a` series and TypeScript reads
it as a docstring. **A round trip that treats `f` as settled would report a disagreement the
lexer caused.**

! **WHAT A LEGEND MUST NOT BECOME.** `vocabulary.toml` is what a role is GIVEN and
`check_vocabulary.py` gates it; a second list of letters written somewhere else is the
duplication that file exists to end. The legend belongs where a role's terms already come from.

## Tasks

- [ ] T1 | T1 -- Give a role the cue legend from where its terms already come.
      Verify: `vocabulary.py --reviewer <role>` emits the letters and
      `check_vocabulary.py` passes.
- [ ] T2 | T2 -- Re-lex a written page and compare its cues against the
      census's. Verify: an unedited page round-trips with every cue holding the
      same content.
- [ ] T3 | T3 -- Refuse a page whose cues came back different. Verify: moving
      one paragraph's text under a neighbouring cue is caught and named.
- [ ] T4 | T4 -- Report the `f` series separately rather than as a disagreement.
      Verify: a file with front matter round-trips without a false finding.
- [ ] T5 | T5 -- Prove the check can FAIL. Verify: with T3's refusal removed,
      T3's own case passes and the test goes red.

## Related

- [`census-row-carries-empty-fields`](census-row-carries-empty-fields.md) -- the ruling that
  removed the three fields and made this necessary
- [`a-page-carries-no-identity`](a-page-carries-no-identity.md) -- the other half of verifying a
  page: that one asks whether the file shifted, this one whether the edits landed
- [`matter-misses-two-languages`](matter-misses-two-languages.md) -- why the `f` series is the
  named exception rather than an afterthought
