# The record is a template someone parses, and it should be a value

```
Status:   open
Progress: 1 of 10 tasks done (6 design rulings made; 8 build steps)
Owner:    session (Roy made all 6 rulings 2026-08-17; the rest is build)
Raised:   2026-08-17, by Roy, after three parser defects of one shape in one day
```

## Objective

**A reviewer fills in a text form and `verdicts.py` reconstructs a table from it by guessing
where each field ends.** Roy: *"this is clearly that we are passing around the 'wrong' data
structure if the error is coming from how the agent has to fill out the template. This says we
should be using a real class or something that it can paste into and knows that it is receiving
strings, not 'can I parse this into the table'."*

Every defect in
[`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
is a boundary guess. The guessing is the defect surface, and it exists only because the record
travels as prose.

## What the change would actually buy

| | today | as a value |
| --- | --- | --- |
| **D7** malformed citation absorbed into the entry above | `SOURCES` repeats a line, and a line that parses as neither citation nor continuation joins its neighbour | a list of `{cite, verbatim}`; a malformed element is reported AS that element |
| **D8** bare label absorbed into the field above | a label is a label only with a value after it, at column 0 | an empty field is an empty string |
| **blank line ambiguity** | content inside a field, separator between records -- the wrong choice was 0.2.0's worst defect, refusing 113 of one reviewer's 134 correct findings | a string carries newlines; there is nothing to disambiguate |
| **field order, indentation, duplicate stems** | rules the reviewer must hold and the parser must enforce | gone with the format |

!! **D9 IS KILLED TOO, IF THE RECORD CARRIES SENTENCES RATHER THAN BLOBS.** Roy: *"D9 is only a
diff problem if the comparison is outside of code."*

That has two readings and only one of them works:

- **Carry the removed span as a FIELD**, computed where the edit was made. ! This reintroduces
  trust. `removed_spans` exists because it is *"the reliable answer where `CLAIM` is the
  reviewer's own account of it"*, and a field the reviewer fills is that account again.
- **Compare SENTENCES, not tokens.** If `BLOCK` and `CHANGE` carry lists of sentences, what was
  removed is a SET DIFFERENCE over whole sentences rather than an alignment over tokens. **A
  span then cannot begin mid-sentence**, which is the mechanism of both D9 shapes -- the
  swallowed word before a parenthetical, and the emphasis delimiters bracketing a claim.

!! **The second is not new vocabulary.** This system already declares the sentence as its unit
-- *"a verdict rules on a SENTENCE, not on a block"* -- and
[`the-unit-of-review-is-the-statement-not-the-block`](completed/the-unit-of-review-is-the-statement-not-the-block.md)
is closed. **The DATA never caught up with the rule.** Every remaining token-level comparison is
the block-shaped structure outliving the block-shaped decision.

! `EDGE` survives either way, for normalising a sentence to compare it. What it stops doing is
deciding where a span BEGINS.

!! **ANSWERED, and not by splitting sentences: LINES.** Roy: `change` as a line array against the
census's `raw_lines`. **Lines are unambiguous and the census already stores them**; sentence
splitting is not free and gets abbreviations, code samples and lists wrong. What was called the
deciding cost of this change turns out not to be paid.

! **Untouched: whether the claim is TRUE.** That is the check worth having and it is not the one
breaking. ! **The ADDRESS check survives but changes MEANING**: it stops measuring a reviewer's
transcription and starts measuring whether a pre-filled field survived being edited. Same
comparison, a different thing being checked -- see the ruling below.

## !! The counter-argument, which is measured and from today

**A structured format's failure is TOTAL where a template's is partial.** On 2026-08-17 a YAML
frontmatter error dropped an entire agent's metadata -- silently, through every release to date.
Hand-written JSON with embedded multi-line strings is exactly where escaping goes wrong, and a
reviewer writing a 200-record report by hand will produce a malformed one.

! **The failure modes are still not equally bad, and that is the argument for changing.** A
parse error NAMES ITS OWN POSITION. A merged field blames the innocent neighbour, and sends the
reader to fix correct work -- which is the complaint this whole class exists under. Trading a
loud total failure for a quiet local one is the right direction; it is not a free trade.

## ! What is NOT established

- **That an agent writes the structured form more reliably than the template.** Nobody has
  measured it. The comparison that matters is malformed-report rate, and both formats have one.
- **That it can be hand-written at all.** ! The record carries TWO long fields -- `original`
  (pre-filled, so the reviewer only has to not break it) and `change` (written by hand). The
  question is really about `change` alone, which shrinks it without settling it.
- **Whether the reviewer can be kept out of the SYNTAX entirely.** Roy: *"we give them a cli to
  emit one. No ambiguity on if they write it correctly."* ! The hazard moves rather than
  vanishing if the values reach that CLI through a SHELL: multi-line text in an argument is the
  same escaping problem one layer out, and heredocs mangled `\n` and `\w` five-plus times in the
  session that raised this. The safe shape is the agent writing the file with its FILE-WRITE
  tool -- no shell in the path -- and a CLI validating it, which is `run_context.py --template`
  and `--check` already.

## * RULED 2026-08-17: JSON

Not on taste, and not on "no stdlib writer" alone. Roy: *"python chose to make it read only
since it is a config format more than a storage format."*

| | verdict |
| --- | --- |
| **TOML** | **wrong KIND of format.** `tomllib` is read-only BY DESIGN -- it is a config language, and a record is storage. ! That forecloses adding `tomli_w`: the objection is not that the stdlib cannot write it, it is that writing it was never the point of the format |
| **YAML** | **not in the stdlib at all** -- `yaml` and `ruamel.yaml` are both third party, so it fails the shipped-code rule before preference enters. ! It is also rejected on preference (Roy: *"I really don't like yaml"*) and on having dropped an agent's entire metadata in this tree on 2026-08-17, silently, through every release to date |
| **JSON** | `json.dumps` is stdlib, and it round-tripped a block carrying emphasis, quotes, a tab, a backslash, a trailing brace and a blank line BYTE-IDENTICALLY. Measured 2026-08-17 |

!! **JSON is not merely preferred: it is the only stdlib format that is both WRITABLE and SAFE
to load from a file an agent produced.** The whole stdlib set, checked 2026-08-17 on the pinned
3.11:

| module | writes? | usable |
| --- | --- | --- |
| `json` | `dumps`/`dump` | **yes** |
| `tomllib` | none | read-only by design |
| `configparser`, `csv` | no nesting or flat only | no |
| `plistlib` | `dumps`/`dump` | technically -- an Apple XML format no reader here would recognise |
| `xml.etree` | `tostring`/`write` | **no -- it EXPANDS ENTITIES**; see below |
| `pickle`, `shelve`, `dill` | `dumps`/`dump` | **NO -- they execute arbitrary code on load** |
| `marshal` | `dumps`/`dump` | no -- executes what it loads, and version-unstable |

!! **TWO stdlib formats are disqualified on SECURITY, for different reasons, and both would have
been reached for by someone optimising away an escaping problem.**

- **`pickle`** round-trips anything, including the multi-line source blocks a record carries.
  Loading it from a file an AGENT wrote is arbitrary code execution inside a review tool.
- **`xml.etree`** is the one this list originally MISSED. Roy: *"technically that does leave us
  the worst of the worst options -- xml itself -- that is stdlib."* It does not execute code; it
  expands entities. Measured 2026-08-17 on the pinned 3.11: **three levels of nested internal
  entity became 1000 characters**, and the unbounded form of that shape is a denial of service.
  `defusedxml` is the answer where XML is unavoidable, and it is third party -- so here the
  answer is that XML is avoidable.

! **Recorded here and nowhere else, deliberately.** A gate refusing these imports was written
and removed the same day: nothing in this repo reaches for them, and no one relitigates a format
already ruled. Roy: *"thorough - also very unnecessary."* The decision is the artifact worth
keeping; the enforcement was defence against a scenario with no path to it.

! The cost accepted with JSON: it escapes newlines, so a record is unreadable in a diff, and it
carries no comments. **That is what the CLI is for** -- nobody reads or writes the encoding by
hand.

## !! Timing -- RULED 2026-08-17: this SHIPS IN 0.2.3

Roy: *"I think this change also has to be implemented so that the agents aren't working around
the tool."*

! **It overrules this file's own first answer**, which was that the change is 0.3.0-scale and
should wait for the runs in flight. What decided it is the cost that does not appear as a
refused record: a reviewer reshaped a sound finding TWICE to route around characters the checker
mishandled. **An agent contorting its judgement to satisfy a mechanical defect is the system
deciding what can be FOUND rather than whether it is true**, and shipping that is worse than
stranding a run.

! The in-flight cost is real and is accepted: two sessions are mid-run against the current
contract, which changed once already today.

## Tasks

- [x] * **RULED 2026-08-17: the record becomes a value, and the format is JSON.** See above.

- [ ] * **Decide the INTERFACE the reviewer uses**, now that the format is settled. A CLI it
      calls per record, a template it fills, or a schema it writes to with its FILE-WRITE tool.
      !! The deciding constraint is that **no multi-line value passes through a SHELL** -- that
      is the same escaping problem one layer out, and it is the layer that actually failed in
      the session that raised this file.

### * The five design rulings, all made 2026-08-17

| | ruled |
| --- | --- |
| **the seed** | **THE TEMPLATE CARRIES `block` AND `address` -- WHERE, NOT WHAT.** The reviewer opens the file. It never transcribes the block and is never handed its text. See the ruling below |
| **the break** | **CLEAN, but the old parser STAYS, deprecated.** Roy: *"clean break - but deprecate the code and leave it in there to parse out the other records just in case."* ! It also unstrands the two in-flight runs rather than forcing a restart |
| **`CLAIM`** | **an OBJECT.** Its keys are the `Verdict` table's existing markers minus the colon, so adding a verdict stays a row |
| **the module** | **a NEW file, `record.py`.** Roy: *"the modular-context should trigger stating that verdict.py seems to be doing more than one thing. It probably already is but this definitely would make that true."* ! The system's own rule applied to its own code |
| **round two** | **NOT this shape.** Roy: *"it kind of collapses the ruling that the editors are supposed to state."* A round-2 answer is `SAME SENTENCE` / `HOLD`\|`REVISE` / one clause -- a RESPONSE, which CARRIES a record only on `REVISE`. Reusing the record shape would have the reviewer re-emit a ruling instead of answering the three questions |

! **One subject each, which is what makes it two files:** `record.py` owns what a record IS --
seeding one, and whether a given one is well formed. `verdicts.py` owns what a SET of records
MEANS against the census -- coverage, citations, contradictions, the work list.

### * RULED 2026-08-17 (final): the record says WHERE, never WHAT

**A reviewer is given `block` and `address`. It opens the file.** Roy: *"I think it would be
better if we try just sending the block path to the reviewers and let them use the other stuff
to determine -- but then the other error that introduces if they go to the wrong spot in the
code."*

!! **THE TWO ERRORS ARE NOT SYMMETRIC, AND THAT IS THE WHOLE ARGUMENT.**

| the error | is it caught? |
| --- | --- |
| the reviewer reads the WRONG LINES | **yes, today.** Its `CLAIM` then quotes a sentence the census block does not contain, and `block_problem` exists for exactly that -- *"catches a finding attached to the wrong block"* -- against a census the gate has already loaded |
| the reviewer rules FROM THE RECORD without opening the file | **no, and nothing could.** A complete, well-formed, admissible record is producible from the prose alone, and no check can tell it from real work |

**Every role's remit requires the read**: block-context checks a claim against the code it sits
with, ownership-context cannot resolve an anchor without reading, function-context reads name,
signature and body together. Handing over the text makes skipping that possible AND cheap --
the same shape as the fabricated-clean hole, the format lowering the price of not doing the job.

!! **THIS HAS FLIPPED THREE TIMES -- drop it, seed it, drop it. Re-check the asymmetry before a
fourth**, because it is the only argument here that does not rest on taste.

! **Two costs accepted.** Standalone readability becomes a RENDERING concern: stage 5 and
re-review inject the census text when they display a record, which is real work. And the
integrity check settled an hour earlier **disappears with the field** -- no pre-filled text
means nothing to corrupt, so `record.py --check` verifies only `block` and `address`.

### Superseded: the template pre-fills the original, and the tool checks it

Roy: *"it is going to come as a template so it is not going to be figure out how to fill out a
json message I can parse. It is going to be fill out THIS json message so I can load it. It will
have to be verified but it won't be incomplete."*

!! **That makes validation a COMPLETENESS check rather than a SYNTAX one.** A missing field in a
pre-structured template is visibly EMPTY rather than absent, which is a different and much
cheaper failure than a record the parser could not find the edges of.

**Two questions were merged in getting here, and only one of them the template settles:**

| | |
| --- | --- |
| **does the reviewer ever TYPE the original?** | **No, settled.** That is where the 83 refusals went, and a tool-written field cannot be mistyped |
| **does the FILE carry a copy?** | **Yes, and it is CHECKED.** The template pre-fills it from the census; `record.py` verifies it still matches |

!! **The check is NOT the transcription-mismatch class coming back.** That class was a reviewer
QUOTING the block and getting it wrong -- 83 refusals, none about a finding. A pre-filled field
can only differ if something CORRUPTED it, and a reviewer editing 224 records in one file
clipping a neighbouring value is ordinary, not hypothetical. **What the old check measured was
the reviewer's typing; what this one measures is whether the file survived being edited.**

! **And that is the distinction to keep.** Roy, on the security gate written and removed the same
day: the argument against it was that `pickle` is *"a well known foot gun"* and XML *"a dead
markup language"* -- **gates against a DECISION no competent person makes.** A field-integrity
check guards an ACCIDENT during ordinary work. Refusing to build the first does not argue against
the second, and this file said it did.

### Superseded: the record carries an INDEX, not the text

**From the todo-tool session, which navigated the tool to get work done rather than reasoning
about it from outside.** Roy: *"stop sending the original at all ... the census already has the
text, keyed by index. If a record carries `block: 2262` and nothing else about the original, the
tool looks it up and the entire mismatch class stops existing -- not just the parsing half."*

**The transcription exists so a record reads standalone, and it is the source of every
comparison defect there is** -- `_same_text`, joined-versus-literal, marker stripping,
punctuation. **83 refusals in that one run were spent on transcription fidelity, and not one of
them was about a finding.**

! **Standalone readability becomes a RENDERING concern**: inject the census text when the record
is displayed. Nothing is lost that was worth having.

!! **This is stronger than seeding the text, which was the first answer here.** A seeded original
still matches by construction, but the field is still THERE -- to be edited, to drift, to be
compared. **Absent, `address_problem` stops existing rather than becoming vacuous.**

! **What still needs text comparison is only CLAIM-covers-CHANGE**, which is genuinely a diff
question. Roy: *"much cleaner if `change` is a line array against the census's line array."*
!! **That also settles the sentence-splitting problem this file called the deciding cost.** Lines
are unambiguous and the census already stores `raw_lines`; sentences are not, and splitting them
gets abbreviations, code samples and lists wrong.

### ! Three things JSON does NOT fix, so they must not be lost in the migration

- **Both P1 proposals survive untouched** -- ALTITUDE, and a `REASON` naming a sentence no
  `CLAIM` names. They are about what reviewers SAY. ! The second gets EASIER: with structured
  fields, *does `reason` quote block text no `claim` names* needs no parsing at all.
- **THE FABRICATED-CLEAN HOLE GETS WORSE.** `verdicts.py` already records that a report reading
  only `CLEAN 1-N` accounts for every block, cites nothing, and exits 0 having read no file.
  **JSON makes emitting 3,000 clean records cheaper, so the cost of faking a pass drops.** The
  format change wants pairing with something that SAMPLES cleans; nothing does today.
- **ENFORCED structured output is not the same as asking for JSON.** Roy: *"if an agent
  hand-writes JSON in a text response, you've swapped a parser you control for one you don't."*
  The prose being carried is full of warning marks, dashes, backticks, `|` and embedded
  newlines, and `write.md` already records a heredoc turning `\n` into a real newline
  mid-sentence -- invisible to the CODE CHECK, because the AST was unchanged.

!! **The enforcement gap is real and this file must not paper over it.** A reviewer is a plugin
agent writing a report FILE; there is no schema-constrained emission on a file write. **The
closest available shape is: the agent writes, `record.py` refuses PRECISELY, the agent fixes** --
which is what `run_context.py --check` already does for the packet. That is self-correcting, not
enforced, and the difference should be measured rather than assumed away.

### !! A defect the object makes checkable, and it is bigger than the format

**A finding sat in `REASON` while `CLAIM` named a different sentence. The gate checked what
`CLAIM` named, passed it, and the real defect never reached a work list.** Measured 2026-08-17:
`module-context` wrote in `REASON` *"the module's own prose already contradicts the 'three
places' framing -- the fourth copy is named inside the file and nowhere in its docstring."* That
sentence IS the finding. *"Three places"* is still wrong on disk.

! `REASON` is unchecked prose BY DESIGN -- *"what you DERIVED, and not checked verbatim"* -- so
a finding hiding there is invisible today. With `claim` as structured fields, comparing
`REASON`'s quoted spans against `claim`'s is mechanical.

## Build order, each step independently verifiable

- [x] **1. DONE 2026-08-17 -- the schema and `record.py --seed`.** One slot per prose block,
      pre-filled with `block`, `address` and `original`, every reviewer field empty. Verified
      against this repo's own smoke-test census: **224 records seeded from 1954 blocks**, which
      is exactly the prose count, and the file round-trips as JSON. ! `original` and `change`
      are LINE ARRAYS, so a blank line inside a docstring survives as an empty element -- the
      0.2.0 defect is not fixed here, it is unrepresentable.

- [ ] **1b. `record.py` checks the pre-filled fields still match the census.** ! It is an
      INTEGRITY check, not the old transcription check: it can only fail if a filled record was
      corrupted, so its message must say so rather than accusing the reviewer of misquoting.

- [x] **2. DONE 2026-08-17 -- `record.py --check`.** Shape only: fields present and of the right
      type, the verdict one of the seven, `claim`'s keys the ones its row requires, constrained
      values among those the template offered, and `sources` a list of `{cite, verbatim}`.

      !! **THREE EXITS, because incomplete is not malformed.** `2` the file does not parse,
      `1` a filled record is malformed, `0` every filled record is well formed -- and an
      EMPTY report exits 0 while reporting `0 of 224 records ruled`. A reviewer checking its own
      work part-way through is not in error; the coverage GATE stays `verdicts.py`'s.

      !! **Every message names the field that is wrong**, which is the lesson from D7, D8 and D9.
      The address message is the one that mattered most: it says the field **was written by the
      tool and edited after seeding**, and a test asserts it never says misquoted -- accusing
      the reviewer would send it to fix work it never did.

      ! And the answer to what happens when a report does not parse: it exits 2 and **names its
      own position**, . That is the failure this format ADDS, and it is
      acceptable precisely because a merged field never could -- it blamed the neighbour.

- [ ] **3. `verdicts.py` reads records instead of parsing prose**, and `parse_report` stays
      behind a deprecation notice for the old text reports. !! **Free regression test: the four
      smoke-test reports are on disk.** Convert, join, and the result must match the join
      already taken -- **903 findings, 35 STANDS, 46 NEEDS A RULING, 14 CODE CONCERNS**. If the
      numbers move, the new reader is wrong.

- [ ] **4. The `REASON`-carries-the-finding check.** `REASON` quoting block text that `claim`
      does not name is a finding filed in the wrong field. ! Its own step because it is a new
      CHECK, not a format change, and it is the one that catches the defect above.

- [ ] **5. `reviewer-brief.md`'s record contract**, and re-run `scripts/check_vocabulary.py`.
      Verify: the brief's own worked example validates against the schema.

- [ ] **6. The four role files**, together. Verify: `check_vocabulary.py` and
      `claude plugin validate`.

- [ ] **7. Run the cycle on this repo** -- 4 -> 5 -> 5b -> 6 -> 6b. That is 0.2.3's gate.

! **Keep `verdicts.py`'s SEMANTIC checks throughout.** Address against census, citation
resolution, verbatim-half lookup, CLAIM-covers-CHANGE, contradictions. Deleting one because the
new shape made it awkward is how the synthesised block ends up unchecked.

## Related

- [`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
  -- the three defects that prompted this. ! If the record becomes a value, that file closes for
  `parse_report` and stays open for `removed_spans`.
- [`re-review-is-ordered-everywhere-and-defined-nowhere`](re-review-is-ordered-everywhere-and-defined-nowhere.md)
  -- ! round two is NOT this shape. Its answer is a RESPONSE (`SAME SENTENCE` / HOLD|REVISE /
  one clause) that carries a record only on a revise; ruled 2026-08-17.
