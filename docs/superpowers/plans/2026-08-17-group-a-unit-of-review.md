# Group A -- the unit of review: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the system agree that a verdict rules on a SENTENCE while a block is only its
address -- in `SKILL.md`, in the join's contradiction check, in the census, and in the record.

**Architecture:** Four independent changes to shipped files, ordered so each is committable
alone. The record cut (Tasks 4-7) is last because it renames fields the earlier tasks read.

**Tech Stack:** Python 3.11 floor, stdlib only, `unittest`, `ruff`.

**Spec:** `docs/superpowers/specs/2026-08-17-review-process-coherence-design.md`

! **A5 was excluded when this plan was written and is now RULED** -- Roy, 2026-08-17: *"pCST not
prose tree"*. It is Task 9.

## Global Constraints

- **Shipped-code floor is py3.11.** No `except` clause in `plugins/**` holds a tuple literal --
  bind it to a name. Run `python scripts/check_shipped_syntax.py` AFTER `ruff format`.
- **Stdlib only** under `plugins/`. No third-party imports, including in tests.
- **No subjective claims** in any comment, docstring or commit message -- no "robust", "elegant",
  "cleaner", "better". Write what is measured or enforced.
- **`clean` is reserved** -- one of the seven verdicts, never a loose adjective.
- **The register is EDITORIAL.** A new term comes from publishing. **Do not introduce one in this
  plan** -- every name here is already ruled.
- Full gate before every commit:
  `python -m unittest discover -s tests` * `ruff format .` * `ruff check .` *
  `python scripts/check_shipped_syntax.py` * `python scripts/check_vocabulary.py`

## File Structure

| file | responsibility in this plan |
| --- | --- |
| `plugins/comment-review/skills/comment-review/SKILL.md` | Task 1 (one line), Task 4-6 (field names) |
| `plugins/comment-review/skills/comment-review/scripts/verdicts.py` | Tasks 2, 4, 5, 6, 7 |
| `plugins/comment-review/skills/comment-review/scripts/census.py` | Task 3 |
| `plugins/comment-review/skills/comment-review/references/reviewer-brief.md` | Tasks 1, 4, 5, 6 |
| `plugins/comment-review/agents/comment-review-block-context.md`, `-module-context.md` | Task 5 (they name `EVIDENCE`/`QUOTE`) |
| `tests/test_verdicts.py` | Tasks 1, 2, 4, 5, 6, 7 |
| `tests/test_census_blocks.py` | Task 3 |

---

### Task 1: `SKILL.md` stops contradicting the brief

**Files:**
- Modify: `plugins/comment-review/skills/comment-review/SKILL.md:43-44`
- Test: `tests/test_verdicts.py`

**Interfaces:**
- Consumes: nothing.
- Produces: nothing code-level. Later tasks do not depend on it.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_verdicts.py`, after `class TestTheBriefsOwnRecordPasses`:

```python
class TestSkillAndBriefAgreeOnTheUnit(unittest.TestCase):
    """The brief says a block can carry six verdicts; SKILL.md said one per role.

    Six summaries have been found disagreeing with the detailed site they
    summarise, every one drifting in the summary while the detail stayed
    correct. This is the pair that was still doing it.
    """

    SKILL = BRIEF.parent.parent / "SKILL.md"

    def test_the_brief_permits_several_verdicts_on_one_block(self):
        text = BRIEF.read_text(encoding="utf-8")
        self.assertIn("A block of six sentences can carry six", text)

    def test_the_skill_does_not_say_one_per_role_per_block(self):
        text = self.SKILL.read_text(encoding="utf-8")
        self.assertNotIn("one per\nrole per block", text)
        self.assertNotIn("one per role per block", text)

    def test_the_skill_says_one_or_more(self):
        text = self.SKILL.read_text(encoding="utf-8")
        self.assertIn("one or more per role per block", text)

    def test_the_skill_requires_reading_the_surrounding_code(self):
        # Roy, 2026-08-17: the synthesiser is expected to read the context
        # around where the replacement lands. Both worse-than-before findings
        # from the rolled-back run die there.
        text = self.SKILL.read_text(encoding="utf-8")
        self.assertIn("read the code around where that replacement lands", text)
```

- [ ] **Step 2: Run it and watch it fail**

```
python -m unittest tests.test_verdicts.TestSkillAndBriefAgreeOnTheUnit -v
```

Expected: `test_the_skill_does_not_say_one_per_role_per_block`,
`test_the_skill_says_one_or_more` and
`test_the_skill_requires_reading_the_surrounding_code` FAIL. The brief test PASSES.

! If the brief test fails, STOP -- the brief changed and this plan's premise is stale.

- [ ] **Step 3: Make the change**

In `SKILL.md`, replace exactly:

```
Everything below this line uses these seven words. A reviewer emits them; **you receive one per
role per block and must synthesise ONE**, so what matters here is what each obliges *you* to do:
```

with:

```
Everything below this line uses these seven words. A reviewer emits them; **you receive one or
more per role per block and must emit ONE replacement**, so what matters here is what each
obliges *you* to do.

!! **And you are expected to read the code around where that replacement lands, to verify it.**
A verdict rules on a SENTENCE; a block is only its address, so a block of six sentences can
arrive carrying six. Synthesising them into one comment without re-reading the code beside it is
how a run replaces an unfalsifiable claim with a checkably false one -- measured, twice, in the
pass that stage 8 rolled back.
```

- [ ] **Step 4: Run the tests**

```
python -m unittest tests.test_verdicts.TestSkillAndBriefAgreeOnTheUnit -v
```

Expected: 4 passed.

- [ ] **Step 5: Full gate and commit**

```bash
python -m unittest discover -s tests && ruff format . && ruff check . \
  && python scripts/check_shipped_syntax.py && python scripts/check_vocabulary.py
git add plugins/comment-review/skills/comment-review/SKILL.md tests/test_verdicts.py
git commit -m "fix(skill): a role may file several verdicts on one block

The brief says a block of six sentences can carry six verdicts and the gate
accepts N -- by_reviewer keys on a set. SKILL.md said one per role per block,
so it was the outlier, and a task agent reading it expects one.

Adds the clause Roy ruled with it: the synthesiser reads the code around where
the replacement lands. Both worse-than-before findings from the rolled-back
pass die there."
```

---

### Task 2: `contradictions()` keys on the TEXT, and `move` leaves the set

**Files:**
- Modify: `plugins/comment-review/skills/comment-review/scripts/verdicts.py` -- `RELOCATES`, `contradictions`
- Test: `tests/test_verdicts.py` -- `class TestContradiction`

**Interfaces:**
- Consumes: `Finding` (current 9-attribute shape), `RULES_ON_TEXT`.
- Produces: `contradictions(grouped: dict[int, list[Finding]]) -> list[int]` -- unchanged
  signature. `ruled_text(f: Finding) -> str` -- the verbatim sentence a finding rules on,
  normalised; empty string when it rules on none.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_verdicts.py` inside `class TestContradiction`:

```python
    def test_drop_and_correct_on_the_SAME_sentence_collide(self):
        # Measured block 728: ownership dropped the sentence function-context
        # was correcting. A real collision -- delete it, or fix its count.
        sentence = "check_shipped_syntax.py reads syntax and two runtime shapes"
        found = [
            _finding(reviewer="ownership-context", verdict="drop",
                     change=f'drop: "{sentence}"'),
            _finding(reviewer="function-context", verdict="correct",
                     change=f'false: "{sentence}" / true: "one runtime shape"'),
        ]
        self.assertEqual(verdicts.contradictions(verdicts.by_block(found)), [1])

    def test_drop_and_correct_on_DIFFERENT_sentences_do_not_collide(self):
        # Measured block 981: ownership dropped one clause, two roles corrected
        # another in the same docstring. The join called it a contradiction and
        # a re-review round was spent establishing it was not.
        found = [
            _finding(reviewer="ownership-context", verdict="drop",
                     change='drop: "a citation into gitignored runtime state is UNVERIFIABLE"'),
            _finding(reviewer="block-context", verdict="correct",
                     change='false: "TRACKED files only, via git ls-files" / true: "or walked"'),
        ]
        self.assertEqual(verdicts.contradictions(verdicts.by_block(found)), [])

    def test_move_against_correct_COMPOSES_and_is_not_flagged(self):
        # Roy ruled it: placement and truth are a sequence, not a rivalry.
        # Move first, then correct at the destination.
        found = [
            _finding(reviewer="ownership-context", verdict="move",
                     change="move to `SYMBOLISH` -> extract: \"the ordering is significant\""),
            _finding(reviewer="block-context", verdict="correct",
                     change='false: "the ordering is significant" / true: "the sort decides"'),
        ]
        self.assertEqual(verdicts.contradictions(verdicts.by_block(found)), [])

    def test_a_containing_sentence_still_collides(self):
        # One role drops a whole paragraph; another corrects a clause inside it.
        found = [
            _finding(reviewer="ownership-context", verdict="drop",
                     change='drop: "the budget is 3. Raising it re-opens the incident."'),
            _finding(reviewer="block-context", verdict="correct",
                     change='false: "the budget is 3" / true: "the budget is 5"'),
        ]
        self.assertEqual(verdicts.contradictions(verdicts.by_block(found)), [1])
```

- [ ] **Step 2: Run them and watch them fail**

```
python -m unittest tests.test_verdicts.TestContradiction -v
```

Expected: `test_drop_and_correct_on_DIFFERENT_sentences_do_not_collide` and
`test_move_against_correct_COMPOSES_and_is_not_flagged` FAIL -- both currently
report `[1]`. The other two PASS already.

- [ ] **Step 3: Implement**

In `verdicts.py`, replace the `RELOCATES` definition:

```python
RELOCATES = frozenset({"drop", "move"})
```

with:

```python
# !! `move` is NOT here. A relocation and a truth fix COMPOSE -- move the prose,
# then correct it at the destination, which is the synthesis order at steps 2
# and 3. Roy ruled it 2026-08-17. Measured: 5 of 8 blocks the old set flagged
# were this shape, and the re-review spent a round on each confirming they were
# not rivals.
REMOVES = frozenset({"drop"})
```

Then replace `contradictions` entirely:

```python
def ruled_text(f: Finding) -> str:
    """The verbatim sentence this finding rules on, normalised for comparison.

    A verdict rules on a SENTENCE and the census numbers BLOCKS, so two findings
    on one block may be about different sentences. Both payloads already carry
    the text: `drop`'s CHANGE is the sentence, `correct`'s is `false: "..."`.

    ! Returns "" when the verdict rules on no quotable sentence, and a caller
    must treat that as "cannot compare" rather than as "no overlap".
    """
    change = f.change
    if f.verdict == "drop":
        _, _, rest = change.partition("drop:")
        text = rest or change
    elif f.verdict in RULES_ON_TEXT:
        _, sep, rest = change.partition("false:")
        if not sep:
            return ""
        text = rest.partition("/ true:")[0]
    else:
        return ""
    return " ".join(text.split()).strip().strip('"').lower()


def contradictions(grouped: dict[int, list[Finding]]) -> list[int]:
    """Blocks where one role removes the SENTENCE another rules on.

    `drop` against `correct`/`patch` is one role saying the sentence should not
    exist and another saying it should exist and be fixed. Nothing composes
    those.

    !! Keyed on the TEXT, not the block index. A block of six sentences can
    carry six verdicts, so two findings sharing an index need not share a
    subject -- measured, one of eight flagged collisions was two roles ruling on
    two different clauses of one docstring, and a re-review round was spent
    establishing it.

    Two findings collide when one's sentence CONTAINS the other's, either way
    round: a role may drop a paragraph whose clause another corrects.

    ! A finding whose text cannot be read is compared against nothing and
    reported -- silence there would hide a real collision behind a malformed
    payload.
    """
    out: list[int] = []
    for block, fs in grouped.items():
        removals = [ruled_text(f) for f in fs if f.verdict in REMOVES]
        rulings = [ruled_text(f) for f in fs if f.verdict in RULES_ON_TEXT]
        if not removals or not rulings:
            continue
        if any(
            not a or not b or a in b or b in a for a in removals for b in rulings
        ):
            out.append(block)
    return sorted(out)
```

- [ ] **Step 4: Run the tests**

```
python -m unittest tests.test_verdicts -v
```

Expected: all pass. ! If `test_a_malformed_block_is_never_reported_as_a_contradiction` or a
`RELOCATES` reference fails, grep for `RELOCATES` -- every use must become `REMOVES`.

- [ ] **Step 5: Update the docstring checklist in `verdicts.py`**

Replace the `CONTRADICTION` line of the module docstring:

```
  CONTRADICTION `drop` or `move` against `correct`/`patch` -- a re-review.
```

with:

```
  CONTRADICTION `drop` against `correct`/`patch` ON THE SAME SENTENCE -- a
                re-review. `move` composes with both and is not flagged
```

- [ ] **Step 6: Full gate and commit**

```bash
python -m unittest discover -s tests && ruff format . && ruff check . \
  && python scripts/check_shipped_syntax.py && python scripts/check_vocabulary.py
git add plugins/comment-review/skills/comment-review/scripts/verdicts.py tests/test_verdicts.py
git commit -m "fix(verdicts): a contradiction is two verdicts on ONE SENTENCE

The check keyed on the census BLOCK index while a verdict rules on a sentence,
so any drop in a block collided with any correct in it. Measured on a live run:
8 blocks flagged, 2 genuine.

Keyed on the text both payloads already carry -- drop's CHANGE is the sentence,
correct's is false: \"...\" -- and collides only when one contains the other.
Validated against all three measured cases: 728 and 1575 still collide, 981 is
clear.

And `move` leaves the set entirely: a relocation and a truth fix compose, which
is the synthesis order at steps 2 and 3."
```

---

### Task 3: STAMP a comment run split off a trailing comment

**Files:**
- Modify: `plugins/comment-review/skills/comment-review/scripts/census.py` -- `blocks_stdlib`
- Test: `tests/test_census_blocks.py`

**Interfaces:**
- Consumes: `Block` (has `annotations: set[str]` and `notes: list[str]`).
- Produces: the annotation string `"continues-a-trailing-comment"` on the FOLLOWING block.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_census_blocks.py`, in `class TestEveryIntervalIsABlock`:

```python
    def test_a_wrapped_trailing_comment_stamps_its_continuation(self):
        # One sentence, two blocks: a trailing comment closes its run, so the
        # line beneath opens a new one and re-anchors to the NEXT declaration.
        # Correct by the block definition and wrong about the prose, so the
        # census says so rather than re-cutting -- merging would renumber every
        # census and invalidate every measurement taken against one.
        got = self._census("x = 1  # a claim that\n       # wraps onto it\ny = 2\n")
        prose = [b for b in got if b.kind != "interval"]
        self.assertEqual([b.kind for b in prose], ["trailing-comment", "comment"])
        self.assertIn("continues-a-trailing-comment", prose[1].annotations)
        self.assertIn("trailing comment", " ".join(prose[1].notes))

    def test_an_ordinary_comment_after_CODE_is_not_stamped(self):
        got = self._census("x = 1\n# a fresh note\ny = 2\n")
        prose = [b for b in got if b.kind != "interval"]
        self.assertEqual([b.kind for b in prose], ["comment"])
        self.assertNotIn("continues-a-trailing-comment", prose[0].annotations)

    def test_a_blank_line_breaks_the_continuation(self):
        # A gap means the author started something new, not wrapped a sentence.
        got = self._census("x = 1  # a claim\n\n# unrelated\ny = 2\n")
        prose = [b for b in got if b.kind == "comment"]
        self.assertNotIn("continues-a-trailing-comment", prose[0].annotations)
```

- [ ] **Step 2: Run and watch it fail**

```
python -m unittest discover -s tests -p "test_census_blocks.py" -v
```

Expected: `test_a_wrapped_trailing_comment_stamps_its_continuation` FAILS on the missing
annotation. The other two PASS.

- [ ] **Step 3: Implement**

In `census.py`'s `blocks_stdlib`, the `flush` closure currently ends by appending a `Block` and
calling `run.clear()`. Replace the whole `flush` definition with:

```python
    # ! The line a trailing comment ended on. A comment opening on the VERY NEXT
    # line continues that sentence, and the flush below has already split them.
    trailing_end = [0]

    def flush() -> None:
        if run:
            # ! PROSE comes from the comment token; WIDTH from the physical
            # line, which is the whole line a width rule measures. Using the
            # physical line for both fed a trailing comment's own code to the
            # annotation regexes -- reviewers saw
            # `models.Index(fields=(...)),  # note` as the note's text.
            prose = [c for _, _, c, _ in run]
            block = Block(
                path=path.as_posix(),
                start=run[0][0],
                end=run[-1][0],
                kind="trailing-comment" if run[0][3] else "comment",
                lines=counted_lines(prose),
                text=_join(prose),
                raw_lines=[ln for _, ln, _, _ in run],
            )
            # !! A trailing comment CLOSES its run, so a sentence wrapped onto
            # the next line becomes a SECOND block and re-anchors to the
            # declaration below it. That is correct by the block definition --
            # the continuation sits between two lines of code -- and wrong about
            # the prose, which is one sentence. Stamped rather than re-cut:
            # merging changes block boundaries and renumbers every census.
            if block.kind == "comment" and block.start == trailing_end[0] + 1:
                block.annotations.add("continues-a-trailing-comment")
                block.notes.append(
                    "opens on the line after a trailing comment, so it may be the"
                    " tail of that sentence rather than a note about the code"
                    " below. A mid-clause ending here may be the split, not the"
                    " author."
                )
            if block.kind == "trailing-comment":
                trailing_end[0] = block.end
            out.append(block)
            run.clear()
```

- [ ] **Step 4: Run the tests**

```
python -m unittest discover -s tests -p "test_census_blocks.py" -v
python -m unittest discover -s tests
```

Expected: all pass.

- [ ] **Step 5: Tell the reviewers what the stamp means**

In `reviewer-brief.md`, in the annotations context -- add after the `narrative-in-docstring`
row of the annotation table if one exists there, otherwise directly after the
`## Read the census end to end` section:

```markdown
! **`continues-a-trailing-comment` means the census may have split one sentence.** A trailing
comment closes its run, so a sentence wrapped onto the next line becomes a second block anchored
to the code BELOW it. Read the two together before ruling. **A mid-clause ending on a block
carrying this annotation is the census's doing, not the author's, and is not a `correct`.**
```

Also add the row to `SKILL.md`'s annotation table, which lists what resolving each one means:

```markdown
| `continues-a-trailing-comment` | read it WITH the trailing comment above; the split is the census's |
```

- [ ] **Step 6: Full gate and commit**

```bash
python -m unittest discover -s tests && ruff format . && ruff check . \
  && python scripts/check_shipped_syntax.py && python scripts/check_vocabulary.py
git add plugins/comment-review/skills/comment-review/scripts/census.py \
        plugins/comment-review/skills/comment-review/references/reviewer-brief.md \
        plugins/comment-review/skills/comment-review/SKILL.md tests/test_census_blocks.py
git commit -m "feat(census): stamp a comment that continues a trailing comment

A trailing comment closes its run, so a sentence wrapped onto the next line
becomes a second block and re-anchors to the declaration below it. Diagnosed by
ownership-context during a live run -- \"three Rx fields now end mid-clause\".

! The census is right by its own definition: the continuation sits between two
lines of code, so it IS an interval. The definition and the sentence disagree
and the prose is one sentence regardless.

Stamped, not re-cut. Merging changes block boundaries and renumbers every
census, invalidating every measurement taken against one. The harm is a
reviewer filing `correct` against a mid-clause ending the census manufactured,
and the annotation removes exactly that."
```

---

### Task 4: `SUMMARY` -> `CLAIM`, `FINDING` -> `REASON`

**Files:**
- Modify: `verdicts.py` (`Finding`, `parse_report`, `payload_problem`, `evidence_problem`, `main`)
- Modify: `references/reviewer-brief.md`, `SKILL.md`
- Test: `tests/test_verdicts.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `Finding.claim: str` and `Finding.reason: str` replacing `.summary` and `.finding`.
  Every later task uses these names.

! **`SUMMARY` SPLITS.** Its left half (the claim as written) becomes `CLAIM`; its DERIVED right
half folds into `REASON`. So `REASON` carries what `FINDING` carried **and** what was derived
from the evidence, and the `||` separator disappears.

- [ ] **Step 1: Write the failing test**

Replace the module-level `REPORT` constant in `tests/test_verdicts.py` with:

```python
REPORT = """
Some preamble the tool ignores.

--- RECORD
BLOCK       1
VERDICT     correct
LOCATION    a.py:1-2
EVIDENCE    a.py:5
QUOTE       the settling line
CLAIM       "only one caller"
REASON      three callers here, so the count is wrong
CHANGE      false: "only one caller" / true: "three callers"
---

--- RECORD
BLOCK       2
VERDICT     clean
LOCATION    a.py:10-11
REASON      nothing to report from this role
---
"""
```

and add:

```python
class TestClaimAndReason(unittest.TestCase):
    """SUMMARY split and FINDING renamed. CLAIM is what the prose says; REASON
    is what the reviewer derived and why it is wrong -- one field, because both
    are the reviewer's own sentence and a checker verifies neither.
    """

    def test_claim_and_reason_are_parsed(self):
        found, _ = verdicts.parse_report(REPORT, "block-context")
        self.assertEqual(found[0].claim, '"only one caller"')
        self.assertIn("three callers", found[0].reason)

    def test_a_verdict_with_no_reason_is_refused(self):
        self.assertIn("REASON", verdicts.payload_problem(_finding(reason="  ")))

    def test_clean_owes_no_reason(self):
        f = _finding(verdict="clean", reason="", change="")
        self.assertIsNone(verdicts.payload_problem(f))

    def test_summary_and_finding_are_gone_from_the_record(self):
        src = Path(verdicts.__file__).read_text(encoding="utf-8")
        self.assertNotIn("SUMMARY", src)
        self.assertNotIn('"FINDING"', src)
```

Update `_finding`'s defaults:

```python
    fields = {
        "reviewer": "block-context",
        "block": 1,
        "verdict": "correct",
        "location": "a.py:1",
        "evidence": "a.py:5",
        "quote": "the settling line",
        "claim": '"x"',
        "reason": "three callers, all under tests/, so the count is wrong",
        "change": 'false: "a" / true: "b"',
    }
```

- [ ] **Step 2: Run and watch it fail**

```
python -m unittest discover -s tests 2>&1 | tail -5
```

Expected: many failures -- `Finding` has no `claim`/`reason`.

- [ ] **Step 3: Implement**

In `verdicts.py`:

1. In the `Finding` dataclass, replace `summary: str` with `claim: str` and `finding: str` with
   `reason: str`, keeping the field ORDER: `reviewer, block, verdict, location, evidence, quote,
   claim, reason, change`.
2. In `parse_report`, replace the two constructor lines:
   ```python
                    claim=fields.get("CLAIM", ""),
                    reason=fields.get("REASON", ""),
   ```
3. In `payload_problem`, replace the FINDING check:
   ```python
       if f.verdict != "clean" and not f.reason.strip():
           return f"{f.verdict} states no REASON -- why the verdict was made"
   ```
4. In `evidence_problem`, DELETE the `SUMMARY` right-half check entirely:
   ```python
       if not f.summary.partition("||")[2].strip():
           return "SUMMARY has no right half -- the finding states nothing derived"
   ```
   ! Its job moves to `REASON` being required, which `payload_problem` now does. Do not
   reproduce a `||` check on `REASON` -- `REASON` is one statement, not two halves.
5. Search `verdicts.py` for `f.summary` and `f.finding` and update the remaining reads.

In `reviewer-brief.md`, update the record template and the field table:

```text
--- RECORD
BLOCK       17
VERDICT     correct
LOCATION    redacted_pkg/billing/rates.py:342-347
EVIDENCE    redacted_pkg/billing/rates.py:355
QUOTE       def compute_rates(plan, period, *, clamp=True):
CLAIM       "kept because twenty call sites want this"
REASON      31 callers and every one is under tests/, so the count is stale
CHANGE      false: "twenty call sites want this" / true: "31 callers, all in tests/"
---
```

| field | what it carries |
| --- | --- |
| `CLAIM` | the sentence as the prose WRITES it, quoted |
| `REASON` | what you derived from the source, and why the claim is wrong -- one statement |

! Delete the old `SUMMARY` row and its `||` explanation, and the `FINDING` row.

In `SKILL.md`, replace `FINDING` with `REASON` at its 4 sites and `SUMMARY` with `CLAIM` at its 1
site -- including the stage-7a five-part list, which must read
`VERDICT / LOCATION / CLAIM / REASON / CHANGE`.

- [ ] **Step 4: Run the tests**

```
python -m unittest discover -s tests
```

Expected: all pass.

- [ ] **Step 5: Full gate and commit**

```bash
python -m unittest discover -s tests && ruff format . && ruff check . \
  && python scripts/check_shipped_syntax.py && python scripts/check_vocabulary.py
git add -A
git commit -m "refactor(record)!: SUMMARY splits into CLAIM, FINDING becomes REASON

Two of the four field changes in the ruled six-field record. SUMMARY carried a
quoted claim and a derived statement separated by ||; the left half is the
CLAIM and the derived half folds into REASON, which is what FINDING was.

! evidence_problem's right-half check goes with it. Its job -- a finding must
state something derived -- is now REASON being required, which payload_problem
already enforces. REASON is ONE statement and must not grow a || of its own."
```

---

### Task 5: `EVIDENCE` + `QUOTE` -> `SOURCE`

**Files:**
- Modify: `verdicts.py` (`Finding`, `parse_report`, `evidence_problem`, `payload_problem`)
- Modify: `references/reviewer-brief.md`, `agents/comment-review-block-context.md`,
  `agents/comment-review-module-context.md`
- Test: `tests/test_verdicts.py`

**Interfaces:**
- Consumes: `Finding.claim`, `Finding.reason` from Task 4.
- Produces: `Finding.sources: list[str]` -- each entry `"file:line | verbatim"`.
  `source_problem(f: Finding, repo: Path) -> str | None` replaces `evidence_problem`.

! **A `SOURCE` line may appear MORE THAN ONCE**, one per place examined -- that is what "plural
for a query" means. Repeating the line avoids a delimiter that verbatim text could contain.
Split each on the FIRST `|` only.

- [ ] **Step 1: Write the failing tests**

```python
class TestSource(unittest.TestCase):
    """EVIDENCE and QUOTE were one field until they were split, because the old
    SUMMARY mixed verbatim with derived text and a checker cannot verify both.
    SOURCE's two halves are both VERBATIM, so the merge does not recreate that.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "a.py").write_text(
            "one\ntwo\nthree\nfour\nthe settling line\nsix\n", encoding="utf-8"
        )
        (self.repo / "b.py").write_text("alpha\nbeta\ngamma\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_one_source_resolves(self):
        f = _finding(sources=["a.py:5 | the settling line"])
        self.assertIsNone(verdicts.source_problem(f, self.repo))

    def test_several_sources_each_resolve(self):
        f = _finding(sources=["a.py:5 | the settling line", "b.py:2 | beta"])
        self.assertIsNone(verdicts.source_problem(f, self.repo))

    def test_a_second_source_that_does_not_resolve_is_refused(self):
        f = _finding(sources=["a.py:5 | the settling line", "gone.py:2 | x"])
        self.assertIn("gone.py", verdicts.source_problem(f, self.repo))

    def test_a_verbatim_half_absent_from_the_file_is_refused(self):
        f = _finding(sources=["a.py:5 | a line nobody wrote"])
        self.assertIn("not found", verdicts.source_problem(f, self.repo))

    def test_a_source_with_no_pipe_is_refused(self):
        f = _finding(sources=["a.py:5"])
        self.assertIn("|", verdicts.source_problem(f, self.repo))

    def test_a_pipe_inside_the_verbatim_half_survives(self):
        (self.repo / "c.py").write_text('x = "a | b"\n', encoding="utf-8")
        f = _finding(sources=['c.py:1 | x = "a | b"'])
        self.assertIsNone(verdicts.source_problem(f, self.repo))

    def test_no_source_at_all_is_refused(self):
        self.assertIn("SOURCE", verdicts.source_problem(_finding(sources=[]), self.repo))

    def test_clean_owes_no_source(self):
        f = _finding(verdict="clean", sources=[], reason="", change="")
        self.assertIsNone(verdicts.source_problem(f, self.repo))

    def test_repeated_SOURCE_lines_are_all_kept(self):
        text = (
            "--- RECORD\nBLOCK 1\nVERDICT correct\nLOCATION a.py:1\n"
            "SOURCE      a.py:5 | the settling line\n"
            "SOURCE      b.py:2 | beta\n"
            'CLAIM       "x"\nREASON      y\nCHANGE      false: "a" / true: "b"\n---\n'
        )
        found, _ = verdicts.parse_report(text, "block-context")
        self.assertEqual(len(found[0].sources), 2)
```

Update `_finding`: drop `evidence` and `quote`, add
`"sources": ["a.py:5 | the settling line"]`.

- [ ] **Step 2: Run and watch it fail**

Expected: `Finding` has no `sources`; `source_problem` is not defined.

- [ ] **Step 3: Implement**

In `verdicts.py`:

1. `Finding`: replace `evidence: str` and `quote: str` with `sources: list[str]`.
2. `parse_report`: `SOURCE` accumulates instead of overwriting. Inside the field loop, before
   `fields[m.group(1)] = ...`:
   ```python
        sources: list[str] = []
        for line in body.splitlines():
            m = FIELD.match(line)
            if not m:
                continue
            if m.group(1) == "SOURCE":
                sources.append(m.group(2).strip())
            else:
                fields[m.group(1)] = m.group(2).strip()
   ```
   and pass `sources=sources` to the constructor.
3. Rename `evidence_problem` to `source_problem` and rewrite its body:
   ```python
       if f.verdict == "clean":
           return None
       if not f.sources:
           return "no SOURCE -- a finding cites where it looked"
       for source in f.sources:
           cite, sep, verbatim = source.partition("|")
           if not sep:
               return f"SOURCE {source!r} has no `|` -- it is `file:line | verbatim`"
           resolved = _resolve_lines(cite.strip(), repo)
           if isinstance(resolved, str):
               return f"SOURCE {resolved}"
           _target, lineno, _end, lines = resolved
           needle = " ".join(verbatim.split()).strip().strip('"')
           if len(needle) < MIN_NEEDLE:
               return f"SOURCE {cite.strip()} carries no verbatim half"
           lo = max(0, lineno - 1 - EVIDENCE_WINDOW)
           window = " ".join(
               " ".join(ln.split()) for ln in lines[lo : lineno + EVIDENCE_WINDOW]
           )
           if needle[:40].lower() not in window.lower():
               return f"SOURCE not found near {cite.strip()}: {needle[:40]!r}"
       return None
   ```
   ! EVERY source must resolve AND carry its verbatim half -- unlike the old rule, where the
   quote had to sit near one citation only. Both halves of a `SOURCE` are one statement about
   one place, so each is checked on its own.
4. Update `main()`'s call site and its printed message from `EVIDENCE` to `SOURCE`.
5. `payload_problem`'s query branch: the shape and ATTEMPTED checks are unchanged.

In `reviewer-brief.md`: one `SOURCE` row replacing the `EVIDENCE` and `QUOTE` rows, the template
updated, and the `QUOTE is the forcing function` paragraph retitled to `SOURCE`'s verbatim half.
Update the two agent files where they name `EVIDENCE` or `QUOTE`.

- [ ] **Step 4: Run the tests**

```
python -m unittest discover -s tests
```

- [ ] **Step 5: Full gate and commit**

```bash
python -m unittest discover -s tests && ruff format . && ruff check . \
  && python scripts/check_shipped_syntax.py && python scripts/check_vocabulary.py
git add -A
git commit -m "refactor(record)!: EVIDENCE and QUOTE merge into SOURCE

`file:line | verbatim`, split on the first pipe, each half checked as before.
A SOURCE line may repeat, one per place examined -- which is what \"plural for
a query\" means, and it avoids a delimiter verbatim text could contain.

! Stricter than what it replaces: every source must resolve AND carry its
verbatim half. The old rule wanted the quote near ONE citation. Both halves of
a SOURCE are one statement about one place."
```

---

### Task 6: `LOCATION` retires, and `CLAIM` is checked against the census

**Files:**
- Modify: `verdicts.py` (`Finding`, `parse_report`, `main`, delete `location_problem`)
- Modify: `references/reviewer-brief.md`, `SKILL.md`
- Test: `tests/test_verdicts.py`

**Interfaces:**
- Consumes: `Finding.claim`, `Finding.sources`.
- Produces: `claim_problem(f: Finding, blocks: list[dict]) -> str | None`.

! This is a NET GAIN in checking, not a removal. `LOCATION` was verified only for
resolvability, never against the block it claimed to describe. `CLAIM` is checked against the
census text for `BLOCK`, which catches a finding attached to the wrong block -- something nothing
catches today.

- [ ] **Step 1: Write the failing tests**

```python
class TestClaimAgainstTheCensus(unittest.TestCase):
    BLOCKS = [
        {"path": "a.py", "start": 1, "end": 2, "kind": "comment",
         "text": "the retry budget is 3 and callers round separately"},
        {"path": "a.py", "start": 9, "end": 9, "kind": "interval", "text": ""},
    ]

    def test_a_claim_present_in_the_block_passes(self):
        f = _finding(block=1, claim='"the retry budget is 3"')
        self.assertIsNone(verdicts.claim_problem(f, self.BLOCKS))

    def test_a_claim_absent_from_the_block_is_refused(self):
        f = _finding(block=1, claim='"the timeout is 30 seconds"')
        self.assertIn("not in block 1", verdicts.claim_problem(f, self.BLOCKS))

    def test_an_add_cites_an_empty_interval_and_owes_no_claim(self):
        # `add` is a finding about prose that is MISSING, so there is no
        # sentence in the block to quote.
        f = _finding(block=2, verdict="add", claim="",
                     change="above `send()`: retries are capped")
        self.assertIsNone(verdicts.claim_problem(f, self.BLOCKS))

    def test_clean_owes_no_claim(self):
        f = _finding(block=1, verdict="clean", claim="", reason="", change="")
        self.assertIsNone(verdicts.claim_problem(f, self.BLOCKS))

    def test_location_is_gone(self):
        src = Path(verdicts.__file__).read_text(encoding="utf-8")
        self.assertNotIn("LOCATION", src)
        self.assertNotIn("location_problem", src)
```

- [ ] **Step 2: Run and watch it fail**

- [ ] **Step 3: Implement**

1. Delete `location: str` from `Finding`, its `parse_report` line, `location_problem` entirely,
   and its call and printed message in `main()`.
2. Add:
   ```python
   def claim_problem(f: Finding, blocks: list[dict]) -> str | None:
       """Is the CLAIM actually in the block the finding cites?

       !! This is what `LOCATION` never did. `LOCATION` was checked for
       resolvability and never against the block it claimed to describe, so a
       finding attached to the wrong block resolved cleanly. The census carries
       each block's joined text and the gate already loads it.

       Exempt: `clean` cites no claim, and `add` is a finding about prose that
       is MISSING -- its block is an empty interval with no sentence to quote.
       """
       if f.verdict in ("clean", "add"):
           return None
       if not 1 <= f.block <= len(blocks):
           return None  # main() reports an out-of-range block already
       needle = " ".join(f.claim.split()).strip().strip('"').lower()
       if not needle:
           return f"{f.verdict} states no CLAIM -- the sentence it rules on"
       haystack = " ".join(str(blocks[f.block - 1].get("text", "")).split()).lower()
       if needle[:40] not in haystack:
           return f"CLAIM not in block {f.block}: {needle[:40]!r}"
       return None
   ```
3. In `main()`, call it beside the other per-finding checks, passing `blocks`.
4. Remove the `LOCATION` row from the brief's field table and the template, and the `LOCATION`
   line from `SKILL.md`'s stage-7a five-part list, which becomes
   `VERDICT / BLOCK / CLAIM / REASON / CHANGE`.
5. Update the module docstring's checklist: replace the `LOCATION` line with
   ```
     CLAIM         the sentence a finding rules on is really in the block it cites
   ```

- [ ] **Step 4: Run the tests**

- [ ] **Step 5: Full gate and commit**

```bash
python -m unittest discover -s tests && ruff format . && ruff check . \
  && python scripts/check_shipped_syntax.py && python scripts/check_vocabulary.py
git add -A
git commit -m "refactor(record)!: LOCATION retires, and CLAIM is checked against the census

LOCATION is derivable from BLOCK, which the census resolves to path/start/end,
and it was only ever checked for resolvability -- never against the block it
claimed to describe.

! A net gain in checking. CLAIM must now appear in the census text for its
BLOCK, which catches a finding attached to the wrong block. Nothing caught that
before. `add` is exempt: its block is an empty interval and its whole finding is
that no sentence is there."
```

---

### Task 7: `REASON` must not merely restate `CLAIM`

**Files:**
- Modify: `verdicts.py` -- `payload_problem`
- Test: `tests/test_verdicts.py`

**Interfaces:**
- Consumes: `Finding.claim`, `Finding.reason`.
- Produces: nothing new.

- [ ] **Step 1: Write the failing tests**

```python
class TestReasonSaysSomething(unittest.TestCase):
    """REASON is the field Roy's `move` ruling rests on and nothing checked it.
    A reviewer that restates the claim has filed a verdict with no reason.
    """

    def test_a_reason_that_restates_the_claim_is_refused(self):
        f = _finding(claim='"only one caller"', reason="only one caller")
        self.assertIn("restates", verdicts.payload_problem(f))

    def test_a_reason_that_adds_the_derivation_passes(self):
        f = _finding(claim='"only one caller"',
                     reason="31 callers and every one is under tests/")
        self.assertIsNone(verdicts.payload_problem(f))

    def test_case_and_quoting_do_not_disguise_a_restatement(self):
        f = _finding(claim='"Only One Caller"', reason='  "only one caller"  ')
        self.assertIn("restates", verdicts.payload_problem(f))
```

- [ ] **Step 2: Run and watch it fail**

- [ ] **Step 3: Implement**

In `payload_problem`, directly after the REASON-non-empty check:

```python
    # ! A reviewer that echoes the claim back has filed a verdict with no
    # reason. Compared normalised, because quoting and case are what make an
    # echo look like a statement.
    claim = " ".join(f.claim.split()).strip().strip('"').lower()
    reason = " ".join(f.reason.split()).strip().strip('"').lower()
    if claim and reason == claim:
        return "REASON restates CLAIM -- say what you derived, not what it says"
```

! Equality only, not containment. A `REASON` that quotes the claim and then explains it is
doing its job, and a containment test would refuse it.

- [ ] **Step 4: Run the tests**

- [ ] **Step 5: Full gate and commit**

```bash
python -m unittest discover -s tests && ruff format . && ruff check . \
  && python scripts/check_shipped_syntax.py && python scripts/check_vocabulary.py
git add -A
git commit -m "feat(verdicts): REASON must not merely restate CLAIM

The field the `move` ruling rests on -- \"this comment belongs to that line
there\" -- and nothing checked it. Equality only, normalised for case and
quoting: a REASON that quotes the claim and then explains it is doing its job."
```

---

### Task 8: close the TODOs group A absorbed

**Files:**
- Move: `TODO/the-unit-of-review-is-the-statement-not-the-block.md`,
  `TODO/move-and-correct-compose.md`,
  `TODO/a-wrapped-trailing-comment-is-split-into-two-blocks.md`,
  `TODO/the-finding-record-is-eight-fields-and-six-would-do.md` -> `TODO/completed/`
- Modify: `TODO/an-empty-interval-has-no-census-index.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Tick every task in the four files** with what was done and the commit that did
  it, then `git mv` each into `TODO/completed/`.

- [ ] **Step 2: Close `an-empty-interval-has-no-census-index.md` too**, once Task 9 lands. All
  eleven of its tasks are then done and it moves to `TODO/completed/` with the rest.

- [ ] **Step 3: Add a CHANGELOG `[Unreleased]` section** naming the four record fields, the
  contradiction change with its 8->2 measurement, and the census stamp.

- [ ] **Step 4: Full gate and commit**

```bash
python -m unittest discover -s tests && ruff format . && ruff check . \
  && python scripts/check_shipped_syntax.py && python scripts/check_vocabulary.py
git add -A
git commit -m "docs(todo): group A closed -- four files to completed/

The unit of review is settled in all four places it was stated differently:
SKILL.md, the join, the census and the record.

! an-empty-interval-has-no-census-index stays OPEN on its naming star. pCST and
prose tree name one thing and one must retire; that is Roy's ruling and group A
did not touch it."
```

---

## Self-Review

**Spec coverage.** A1 -> Task 1. A2 -> Task 2. A3 -> Task 3. A4 -> Tasks 4-7. A5 -> deliberately
excluded, and Task 8 Step 2 records why. The spec's two extra ruled checks -- `CLAIM` against the
census, and `REASON` not restating `CLAIM` -- are Tasks 6 and 7.

**Placeholders.** None. Every code step carries the code.

**Type consistency.** `Finding` evolves in one direction and each task states the shape it
leaves: Task 4 introduces `.claim`/`.reason`, Task 5 replaces `.evidence`/`.quote` with
`.sources: list[str]`, Task 6 removes `.location`. Tasks 5-7 consume only names an earlier task
produced. `source_problem` replaces `evidence_problem` in Task 5 and Task 6 does not reference
the old name.

! **Task order is load-bearing.** Tasks 4->5->6 each change `Finding`'s shape and every test
fixture with it. Running them out of order leaves `_finding()` describing a dataclass that does
not exist.

---

### Task 9: `prose tree` retires; `pCST` survives

**Files:**
- Modify: `docs/vocabulary.md` -- the term table and the retired-words table
- Modify: every shipped file that says `prose tree`
- Test: `tests/test_vocabulary.py`

**Interfaces:** none -- a rename in prose.

! **RULED 2026-08-17.** Roy: *"pCST not prose tree"*. The two were distinguishable while the
pCST was an aspiration and the prose tree was what the census actually built. The census
enumerates intervals now, so they name one thing and the precise word wins.

- [ ] **Step 1: Find every site**

```bash
grep -rn -i "prose tree\|prose-tree" --include=*.md --include=*.py . | grep -v corpora
```

- [ ] **Step 2: Write the failing test**

Add to `tests/test_vocabulary.py`:

```python
class TestProseTreeRetired(unittest.TestCase):
    """Ruled 2026-08-17: the census builds a pCST, and one name had to go."""

    ROOT = Path(__file__).resolve().parent.parent

    def test_no_shipped_file_says_prose_tree(self):
        shipped = sorted((self.ROOT / "plugins").rglob("*.md"))
        shipped += sorted((self.ROOT / "plugins").rglob("*.py"))
        self.assertTrue(shipped, "no shipped files found -- the glob is wrong")
        for path in shipped:
            with self.subTest(path=path.name):
                body = path.read_text(encoding="utf-8").lower()
                self.assertNotIn("prose tree", body)

    def test_the_retired_table_records_it_with_a_reason(self):
        text = (self.ROOT / "docs" / "vocabulary.md").read_text(encoding="utf-8")
        self.assertIn("`prose tree`", text)
        self.assertIn("pCST", text)
```

- [ ] **Step 3: Run it and watch it fail**

```
python -m unittest discover -s tests -p "test_vocabulary.py" -v
```

Expected: `test_no_shipped_file_says_prose_tree` FAILS, naming the files.

- [ ] **Step 4: Replace every shipped use with `pCST`.**

In `docs/vocabulary.md`, delete the `prose tree` row from the term table and drop the
now-resolved clause from `pCST`'s row (`! BUILT 2026-08-17, so this and prose tree now name one
thing...`), leaving `pCST` as the single definition. Add to the retired table:

```markdown
| `prose tree` | -> **pCST**. Both named one thing once the census enumerated intervals; the precise word won. Roy, 2026-08-17: *"pCST not prose tree"* |
```

- [ ] **Step 5: Run the tests, full gate, commit**

```bash
python -m unittest discover -s tests && ruff format . && ruff check . \
  && python scripts/check_shipped_syntax.py && python scripts/check_vocabulary.py
git add -A
git commit -m "refactor(vocabulary)!: prose tree retires; the census builds a pCST"
```
