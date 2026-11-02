# Freeform Agent Prose Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The agents can review and edit a freeform file, and only approved text reaches the working tree.

**Architecture:** Prose only, under `src/plugin/`. Each reviewer edits a copy of a freeform file in its own temporary directory and writes its findings beside it, and passes the paths up. A later topology stage starts from a straight copy of the files the stage before left; the copy chief settles the findings. Edits are set on a draft copy, the formatter and compiler run there, a diff audit checks them, the author approves the real diff, and accepted files are copied over.

**Tech Stack:** Markdown agent prose; `claude plugin validate` at release.

**Spec:** rulings #259, #260 and #261 in `docs/decision-log.md`. The version reviews behind #261 are summarised in Task 1. Starts only after plan `2026-11-01-python-and-rust-only` closes, because #259 lands the code before the agents are told.

## Global Constraints

- `src/plugin/` prose states what things are and do, one instruction per sentence, each stated once, with no decision-log references or dates.
- `docs/limitations.md` governs changes to agent files and skill prose. Read it first.
- Every new or changed sentence goes to Roy as exact wording before it is applied.
- A rule belongs in exactly one `references/` file.
- Agents lane. No `plugins/` rebuild.

## Review Focus

1. A run holding only freeform files reaches stage 8 with no docket: nothing in SKILL.md or `references/review.md` may assume one, and the proofreader needs no binder for those files.
2. A formatter rewriting code the findings never named: the diff audit stops the run.
3. A repo with no formatter or compiler for a language: the report says that language was not verified.
4. A `move` from a Python page to a freeform file: refused at the write chain, raised as a `drop` plus a freeform add.
5. Two roles in one stage changing one comment: the copy chief settles it, and a later stage never sees an unsettled pair.

---

### Task 1: The cheat sheet

**Files:** Create `src/plugin/skills/comment-review/references/freeform.md`

- [ ] **Step 1: Read the measured failures**

`evidence__workout-builder-full-v0_2/ROLLBACK.md` in the OneDrive archive named by the `onedrive-evidence-archive` memory: the 31 run-caused defects, 12 of them one composition shape.

- [ ] **Step 2: Draft it from those failures and bring Roy the exact wording**

First, how to compose: one full replacement per comment; text framed for the file (indent, leader, width); explicit deletions; no `replace_all`; each paragraph still a whole proposition. Then the hazards: comment-shaped text inside a string or heredoc is code; a line ending in a continuation and the line after it stay whole; the interpreter line and a byte-order mark stay byte for byte; a C or C++ comment ending in a backslash takes the next line with it; a directive in a comment is code (`/*!50000 ... */`, `/// <reference>`, `# shellcheck`, `// +build`); JSX text is not a comment; the file's line endings stay as they are.

- [ ] **Step 3: Apply the approved wording and commit**

Message: `Add the freeform edit cheat sheet`.

### Task 2: Reviewers edit a copy and report

**Files:** Modify `src/plugin/skills/comment-review/references/reviewer-brief.md`

- [ ] **Step 1: Draft and approve the wording**

A freeform path has no address and no mark. The reviewer copies the file to its own temporary directory, or starts from the copy the stage before left, and edits that copy. It writes each finding beside it as `instruction`, `source`, role, `path:line`, the exact current text, and the one full replacement. It reports `N swept, M raised` per file, listing every comment before judging any, and returns the paths.

- [ ] **Step 2: Apply and commit**

Message: `Tell reviewers how to edit a freeform file`.

### Task 3: The stages

**Files:** Modify `src/plugin/skills/comment-review/SKILL.md:133-134,144-150`, stages 4, 5, 7b and 8; `references/write.md:51-61`; `references/review.md`; the copy chief's brief; `references/compact.md:29` if it no longer holds

- [ ] **Step 1: Draft and approve the wording**

Stage 2: report the freeform list. Stage 4: roles in one stage work blind; a later stage's role starts from a straight copy of the files the stage before left, and the task agent hands it their paths in the packet, because a revise root holds pages only and that stage's binder lists no freeform file. Stage 5: the copy chief settles the findings, correct before patch, resolving each `source`. Stage 7a: an agent sets the settled text on a draft copy with the Edit tool, following `references/freeform.md`, and the task agent runs the compile baseline, the formatter and the stage 1 check command there. Diff audit: every hunk of `git diff --no-index` against the original matches one settled finding, and any other hunk stops the run. The author approves that diff beside the page diffs. Stage 7b: accepted files are copied over, and `prove_unchanged` prints `UNCHECKED`, which is expected and never reported as proven. Stage 8: the proofreader reads freeform files directly, with no binder.

- [ ] **Step 2: Apply and commit**

Message: `Run freeform files through the stages`.

### Task 4: Exercise it

- [ ] **Step 1: Run `/comment-review` on a mixed Python and JavaScript change in a scratch repo**

Plant a formatter hunk no finding names, and a comment-shaped line inside a template literal. Expected: the audit stops on the first, the reviewers leave the second alone, the JS findings reach the copy chief by path, and the report says `UNCHECKED`.

- [ ] **Step 2: Grade from the diff and file what it shows**
