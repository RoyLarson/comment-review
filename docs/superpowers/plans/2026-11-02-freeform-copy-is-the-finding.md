# A freeform reviewer's copy is its finding: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land decision-log #266 and #270: a freeform reviewer edits a copy, the diff supplies the text, the chief writes one draft from the role copies, and no agent is dispatched to set it.

**Architecture:** Prose only. Nothing in `src/comment_review/`, `scripts/` or `tests/` reads `findings.json`, `settled_<stage>.json` or a freeform draft, so no Python changes. `references/freeform.md` becomes the whole contract for a freeform file, which is what lets a freeform-only dispatch go without the brief.

**Tech Stack:** Markdown under `src/plugin/`, one line of `vocabulary.toml`. `plugins/` is release output and is not edited.

**Closes:** `TODO/freeform-run-findings.md` T2, T11 and T13.

**Order:** before the merge, and before T16 and T17, which exercise this flow.

---

## Decisions this plan makes

Each needs Roy's approval with the wording.

1. **`at` is a line in the file the role copied.** That is the old side of the diff hunk, so it holds for a `drop`. An `add` names the line of code it belongs to.
2. **A later stage's base is a snapshot.** The chief writes `draft/` during a stage, so diffing a role's copy against `draft/` would show the chief's own edits. `base_<stage>/` holds what the stage copied.
3. **The sheet's editing mechanics stay.** The reviewer and the chief both edit with the Edit tool, so "Setting a replacement" is reworded rather than deleted.
4. **`settled_<stage>.json` keeps `instruction`, `at`, `reason`, `source` and `role`,** with `at` a line in the draft. 7a shows the author each full draft, and the settled file answers when the author asks why a change was made (Roy, 2026-11-02: *"the full draft - the human can ask for the reasons after the fact and the agents can respond"*).

## Files

- Modify: `src/plugin/skills/comment-review/references/freeform.md` (whole file)
- Modify: `src/plugin/skills/comment-review/references/reviewer-brief.md:9-10, 32-34, 351-400`
- Modify: `src/plugin/skills/comment-review/SKILL.md:200-217, 237-239, 338-354, 405-416, 439-440`
- Modify: `src/comment_review/references/vocabulary.toml:82`

---

### Task 1: Rewrite the sheet

**Files:** Modify `src/plugin/skills/comment-review/references/freeform.md`

- [ ] **Step 1: Replace everything above `## What stays exactly as it is` with this text.** That section and the closing C/C++ paragraph stay unchanged.

````markdown
# A freeform file

A freeform file is a source file no reader claims. It has no page and no address, so `mark`,
`addresser` and `proof` take no path in it. The text in your copy is the text the copy chief reads.
Everyone who edits a copy or a draft follows this sheet.

When your prompt holds no brief, this sheet is your contract. Where your role file names a mark, an
edit copy or `check`, read this sheet's finding, copy and return.

## Reviewing a file

1. **Copy the file** into `FREEFORM DIR`, keeping its path. Copy it from `FREEFORM COPIES` when that
   lists it, and from `REPO ROOT` otherwise. Your citations resolve against the file you copied.
2. **List every comment in the file by line**, before you judge any. This list is `swept`.
3. **Rule on each comment** with your role's remit. A comment with nothing to report takes no
   finding, and `swept` records that you read it.
4. **Edit your copy.** Each change is the one full text of that comment.
5. **File each finding** in `FREEFORM DIR/findings.json`. The diff of your copy supplies the text,
   so a finding carries why, and never the text.
6. **Return the paths** of `findings.json` and your copies, with one line per file:
   `<path>: N swept, M raised`.

```json
{ "role": "block-context",
  "files": [
    { "path": "redacted_pkg/rates.js",
      "swept": [12, 40, 88],
      "findings": [
        { "instruction": "correct",
          "at": "redacted_pkg/rates.js:40",
          "reason": "the limit is read from settings and is 100",
          "source": [ { "cite": "redacted_pkg/settings.js:7",
                        "verbatim": "const LIMIT = 100;" } ] } ] } ] }
```

| field | what it carries |
| --- | --- |
| `path` | the file, as your binder lists it |
| `swept` | the line of every comment in the file |
| `instruction` | what you did to the comment, below |
| `at` | `path:line` in the file you copied: the comment's first line, or for an `add` the line of code it belongs to |
| `reason` | what you derived |
| `source` | `{ "cite": "file:line", "verbatim": "the text at it", "ran": "the command" }`, one per place you examined |

| instruction | use it when |
| --- | --- |
| `correct` | a claim is false. `source` carries the line that settles it |
| `patch` | the claim is true and the wording is not. No source is needed |
| `drop` | the comment or a sentence in it should go |
| `add` | a comment is missing |
| `query` | you cannot rule, below |

- **One finding per comment.** A comment with several edits takes one finding, and it is a `correct`
  when any of those edits is.
- **Every finding but a `query` has its change in your copy, and every change has its finding.**
- **A `query` changes nothing in your copy.** It carries `shape`, `attempted` and `settles`: the
  shape, the check you attempted and what would settle it. `shape` is one of these:
  - `outside-my-role` -- the comment's subject lies outside your remit.
  - `unable-to-determine` -- you looked and the evidence does not decide it.
  - `human-review-necessary` -- only the author's intent decides it.
- **A code concern is a `query`** of shape `human-review-necessary`, with `settles` reading
  `code concern`. A claim inside a string is one, because the string is code.
- **A relocation is two findings:** an `add` at the destination and a `drop` at the origin, each
  naming the other in its `reason`. When one end is on a page, that end is a mark: `mark` refuses a
  `--to` in a freeform file.

## Composing a change

- **One full text per comment.** The comment reads whole, first line to last, holding every edit
  made to it.
- **Read it whole.** Each paragraph stays a whole proposition: every later clause agrees with the
  changed clause, every contrast word keeps its contrast, and every pronoun keeps its antecedent.
- **Frame it for the file.** Every line carries the comment's own indent and its leader, wrapped
  lines included. Take both from the comment as it stands, in the file's own tabs or spaces.
- **Wrap it to the style sheet's width.** A longer comment re-wraps as a whole and nothing beyond it
  moves. A path or a citation stays whole on one line; report a line it pushes past the width.
- **Hold it to the cap.** A comment run directly above a declaration, in a language that documents
  a declaration by the comment above it, is that declaration's documentation, and the cap passes
  over it.
- **Delete explicitly.** Deleting a whole comment removes it through the line ending of its last
  line. A blank line that separated two paragraphs stays.
- **An `add` sits beside or above its code,** and that line of code stays unchanged.

## Making the edit

- Make every edit with the Edit tool, one call per comment, with `replace_all` off.
- When the old text matches more than once, add the neighbouring line to both strings, so the match
  stands at one place alone.
- Make an `add` before the `drop` it pairs with.
- Read each comment back after editing it.
````

- [ ] **Step 2: Run the gates**

Run: `uv run python scripts/check_vocabulary.py` and `uv run pytest -q tests/gates`
Expected: exit 0 and all pass. `test_the_library_rule_is_stated_once` holds because this text does not repeat that rule.

### Task 2: Point the brief at the sheet

**Files:** Modify `src/plugin/skills/comment-review/references/reviewer-brief.md`

- [ ] **Step 1: Replace lines 9-10's second sentence**

Old: `A freeform file takes findings in your own directory instead; see *A freeform file*.`
New: `A freeform file takes an edited copy and findings instead; see *A freeform file*.`

- [ ] **Step 2: Replace lines 351-400, the whole of `## A freeform file`, with:**

```markdown
## A freeform file

A file your binder lists under `freeform` follows `FREEFORM SHEET`, which is in your prompt whenever
your binder lists one.
```

- [ ] **Step 3: Run the brief tests**

Run: `uv run pytest -q tests/gates tests/test_brief_worked_example.py`
Expected: all pass.

### Task 3: Dispatch a freeform-only agent without the brief

**Files:** Modify `src/plugin/skills/comment-review/SKILL.md:200-217`

- [ ] **Step 1: After the packet list, before `Each agent fills its copy in place`, insert:**

```markdown
An agent whose received binder lists no page takes a shorter prompt: `references/freeform.md` pasted
whole in place of the brief, then its vocabulary, then a packet of `REPO ROOT`, `FILES UNDER REVIEW`,
`REFERENCE ONLY`, `STYLE SHEET`, `FREEFORM DIR` and `FREEFORM COPIES`.
```

- [ ] **Step 2: Change the following sentence**

Old: `An agent dealt a freeform file also\nreturns the paths of its `findings.json` and its copies.`
New: unchanged. Confirm the `run the same check yourself` sentence after it now reads for an agent with an edit copy, and add `An agent with no edit copy has no check to run.` directly after that command block.

### Task 4: The chief writes the draft

**Files:** Modify `src/plugin/skills/comment-review/SKILL.md:237-239, 338-354`

- [ ] **Step 1: Replace lines 236-239 with:**

```markdown
Roles in one stage work blind to each other. A role in a later stage starts from what the stage
before left: settle that stage's findings as stage 5 says, copy `<run-dir>/freeform/draft/` to
`<run-dir>/freeform/base_<stage>/`, and hand those paths in `FREEFORM COPIES`, because a revise root
holds pages only and that stage's binder lists no freeform file.
```

- [ ] **Step 2: Replace lines 338-354 with:**

````markdown
**Freeform findings.** Read each role's `findings.json` from its path, and diff each of its copies
against the file it copied:

```bash
git diff --no-index -U0 <base> <FREEFORM DIR>/<path>
```

`<base>` is the file's `base_<stage>` copy at a later stage and `<path>` otherwise. The command exits
1 when the files differ. Then, working from `references/freeform.md`:

1. Match each hunk to a finding at its old-side line, and each finding but a `query` to a hunk. Send
   anything unmatched back to its role.
2. Open every `source` and confirm it says what the finding claims. Send a finding whose source
   fails back to its role.
3. Ask each `query` as a human question, above. Settle it from the answer, writing the edit a role
   would have made.
4. Copy the base of each file with a change that stands to `<run-dir>/freeform/draft/<path>`, unless
   a stage before already drafted it.
5. Take the changes to one comment together, `correct` before `patch`, and rule as above: one side's
   text, the original, or your own. Write the result into the draft. Two roles changing one comment
   end as one edit.
6. Read each edit against the code around it, and hold it to the cap.
7. Read each freeform file for a comment over the cap that no finding reached, and shorten it in
   the draft as a `patch`.

Write the result to `<run-dir>/freeform/settled_<stage>.json`, a list of the findings' own shape with
`role` added to each and `at` the line in the draft, holding only the changes that stand. A run with
no pages prints `0 places` at `collate` and carries on.
````

### Task 5: Retire the setter at 7a

**Files:** Modify `src/plugin/skills/comment-review/SKILL.md:405-416, 439-440`

- [ ] **Step 1: Replace lines 405-410 with the heading below, and renumber the remaining steps 3, 4 and 5 as 1, 2 and 3.** Their text does not change.

```markdown
**Freeform files.** Check the drafts stage 5 wrote, in this order:
```

- [ ] **Step 2: Replace lines 439-440 with:**

```markdown
Show each freeform draft whole. When the author asks why a change was made, answer from
`settled_<stage>.json`.
```

- [ ] **Step 3: Confirm nothing cites the old steps**

Run: `git grep -n -E "unset|general-purpose agent with|sets each replacement|settled replacement" src/plugin`
Expected: no hit about a freeform draft. `SKILL.md:125` is a different dispatch and stays. The audit sentence `Every changed line belongs to a settled finding` stays.

### Task 6: The vocabulary entry

**Files:** Modify `src/comment_review/references/vocabulary.toml:82`

- [ ] **Step 1: Replace the definition with:**

```toml
freeform = "A source file no reader claims. It has no page and no address: reviewers read it and edit a copy, the copy chief writes one draft from those copies, and `prove_unchanged` answers `UNCHECKED` for it."
```

### Task 7: Verify and close

- [ ] **Step 1: Run every gate**

```bash
uv run ruff check .
uv run ty check
uv run python scripts/check_vocabulary.py
uv run python scripts/check_shipped_syntax.py
uv run pytest -q
```

Expected: all exit 0.

- [ ] **Step 2: Walk the stages.** Read `SKILL.md` from stage 4 to 7a as a freeform-only run with two stages and two roles changing one comment. Every path named must be written by an earlier step. Fix anything that is not, before T16.

- [ ] **Step 3: Close T2, T11 and T13** with `job-board todo finish` from a commit after the work.

```bash
job-board todo finish freeform-run-findings T2 "<how>" <sha>
```

Run it for each of the three. T16 and T17 then exercise this flow live, and nothing here is verified in a live run until they do.
