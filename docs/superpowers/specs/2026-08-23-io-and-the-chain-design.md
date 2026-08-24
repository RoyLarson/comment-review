# One door for I/O, and a chain that carries the order

Design, 2026-08-23. Ruled with Roy in session; not yet scheduled -- whether it joins the
0.2.4 plan is a separate decision.

## The problem, in one sentence

**Nothing owns "this file, as read", so every consumer re-derives it -- and nothing owns the
ORDER of the work, so every caller picks its own or omits a step.**

## The evidence

Measured 2026-08-23 over the shipped scripts:

| symptom | where |
| --- | --- |
| the newline-safe reader is reached by TWO modules; nine source reads go around it | `repo.read_raw` -- called at `galley.py:430`, `prove_unchanged.py:254`, `:324`, `:325` |
| nine modules read source directly, through the TRANSLATING path | `census.py:177`, `:336`, `compositor.py:304`, `:335`, `desk.py:277`, `prove_unchanged.py:293`, `referrers.py:122`, `run_context.py:314`, `verdicts.py:420` |
| the lexer opens nothing at all | `lexer.py`, 0 read sites |
| `code_lines` and `declarations` computed twice per page | `page.py:419-420`, `:725-726` |
| census loading written four times, the fourth diverges | `addresser`, `galley`, `record` unwrap the dict form; `verdicts.py:332` does not |
| `language_for` imported from two modules | `compositor.py:68` from `language`, `galley.py:89` from `lexer` |
| `draft` writes with no losslessness check | `compositor.py`, and `galley` calls it |

!! **THEY ARE ONE SYMPTOM.** `page_for(path, text, lang, rel)` takes TEXT, so by the time
anyone reaches the reading code somebody else has already read the file. `read_raw` is
correct and REACHED BY TWO of the eleven modules that read source, because there is nowhere
for it to live that everyone goes through.

! **THIS ROW READ "ZERO CALLERS" UNTIL A TRIAGE AGENT MEASURED IT, 2026-08-23.** It has four
call sites in the two modules its own docstring names. **The argument is unharmed and the
number was the whole evidence for it** -- an uncalled function says the door was never fitted;
a function two modules use while nine go around it says the door exists and is optional, which
is the weaker claim and the true one. ! Recorded rather than corrected away, because a spec
that quietly gains a better number teaches nobody where the first one came from.

!! **AND IT EXPLAINS A FAILURE THAT IS NOT A BUG.** Roy, 2026-08-23: *"The fact that claude
stated it made something happen and then didn't tells me there is a design problem because it
is hard to do in the current system."* The rule -- only the lexer and the compositor touch
source -- has no seam that enforces it. Following it means every author remembering it, so
**the claim is cheaper than the compliance.**

## `io.py` -- the only door

Owns the whole byte<->text boundary, in both directions.

| moves in | from |
| --- | --- |
| `read_raw` | `repo.py` |
| `text_lines` | `constants.py` |
| `utf8_console` | `constants.py` |
| the `newline=""` write | `compositor.py` |

`constants.py` keeps `LINE_BREAK` and nothing else -- the specific line endings, as data.
Roy: *"this does not belong in constants.py, just the specific line endings."*

!! **THE RULE BECOMES CHECKABLE.** `read_text|write_text|open(` outside `io.py` is a gate
failure, in the same family as `check_shipped_syntax.py`. That converts a convention into a
thing that can fail, which is the whole point -- see [`gates.md`](../../gates.md).

## What flows: an accumulating record

One frozen `Doc` that each step returns a new version of. Every step has the signature
`Doc -> Doc`, so a chain is genuinely a list and the runner is genuinely a loop.

```
Doc(path)
Doc(path, lang)
Doc(path, lang, text)
Doc(path, lang, text, paragraphs)
Doc(path, lang, text, paragraphs, cues)
Doc(...).page
```

! **WHY NOT A SINGLE THREADED VALUE.** Roy's sketch was `result = next(steps)(result)`, and
it surfaces the constraint: `language` and `read_text` BOTH take the path, and the lexer needs
both their outputs. By step three the chain is carrying three things. A uniform signature is
what keeps the list a list.

! **WHY NOT A MUTABLE CONTEXT.** A step could read a field an earlier one forgot to set, which
makes the order implicit again -- the failure being removed.

## The two chains

```
READ    [language, read_text, lexer, addresser, page]        path -> Page
WRITE   [edit, set, draft, lossless, identity,
         prove_unchanged, approve]                           Page + edits -> file
```

Every write step already exists. `galley.reset` is `edit`; `compositor` owns `set_page`,
`draft`, `lossless`, `identity`, `approve`. **Only `edit`, `set`, `draft` and `approve` are
ever run in sequence today; the three checks sit outside and nothing calls them between.**

! **THE GALLEY DOES NOT RUN THE CHAIN.** Its own docstring already says *"this module owns
only the first; setting belongs to the compositor."* The runner owns the order, which is what
nobody owns now.

## Refusal, and why the two sides differ

| side | a refusal means | the run |
| --- | --- | --- |
| READ | this file is not censusable | **reports a gap and continues** |
| WRITE | this page would corrupt a file | **aborts -- nothing is approved** |

A step never raises for an expected refusal; it returns a `Doc` carrying `refused`, and the
runner stops advancing that one. Binary file, unknown suffix, undecodable byte, no language
record -- one shape, all reportable. Unexpected failures still raise.

!! **A REFUSAL NAMES ITS STEP.** `census.py` today catches bare `Exception` and prints a type
name.

!! **AND IT FIXES `closing-line-deletes-code` STRUCTURALLY.** That file measures
*"prove_unchanged DOES catch it -- but only AFTER stage 7b has written to disk."* A check
outside the chain runs after the damage; inside it, the write never happens.

## What `census.py` becomes

Thin. Iterate the paths, run the chain per path, collect pages and refusals. The orchestration
leaves it -- Roy: *"census.py is iteration through the paths and then orchestrating all of the
work, which is kind of gather but..."* The chain owns the order; census owns the set of files.

## Testing

- **each step alone**, with a hand-built `Doc` -- no file, no repo
- **the chain as data** -- assert the read chain IS `[language, read_text, lexer, addresser,
  page]` and the write chain IS its seven. ! This is the test that catches a missing check,
  because the absence is a missing list element rather than a forgotten call.
- **a refused step means no `approve`** -- one test covering both the draft-overwrites-source
  bug and the missing losslessness check
- end to end, which the round-trip identity already does

## Out of scope

The verdict/record/desk side. The census's on-disk shape. The `lexer` -> `TYPECODER` rename
([`lexer-does-not-lex`](../../../TODO/lexer-does-not-lex.md)). This is the read and write
paths only.

## TODOs this bears on

[`the-lexer-reads-no-files`](../../../TODO/the-lexer-reads-no-files.md) is the file it
answers. It also bears on
[`galley-and-compositor-write-path`](../../../TODO/galley-and-compositor-write-path.md),
[`closing-line-deletes-code`](../../../TODO/closing-line-deletes-code.md),
[`computed-and-never-read`](../../../TODO/computed-and-never-read.md) and
[`census-walks-and-flushes`](../../../TODO/census-walks-and-flushes.md).
