# Freeform Agent Prose Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The agents know how to review and edit a freeform file, and the task agent proves nothing it did not check.

**Architecture:** Prose only, under `src/plugin/`. Each reviewer writes its freeform findings in its own temporary directory and passes the path to the agents after it and to the copy chief, who settles them. The human approves, and an agent applies them with the Edit tool. No backend changes.

**Tech Stack:** Markdown agent prose; `claude plugin validate` at release.

**Spec:** rulings #259 and #260 in `docs/decision-log.md`. Starts only after plan `2026-11-01-python-and-rust-only` closes, because #259 lands the code before the agents are told.

## Global Constraints

- `src/plugin/` prose states what things are and do, one instruction per sentence, each stated once, with no decision-log references or dates.
- `docs/limitations.md` governs changes to agent files and skill prose. Read it first.
- Every new or changed sentence goes to Roy as exact wording before it is applied.
- A rule belongs in exactly one `references/` file.
- Agents lane. No `plugins/` rebuild.

## Review Focus

1. A run holding only freeform files reaches stage 8 with no docket: nothing in SKILL.md may assume one.
2. A freeform file changed between review and apply: the Edit tool's exact-match failure surfaces it, and the agent re-reads rather than forcing the edit.
3. A repo with no formatter or compiler for a language: the report says that language was not verified.
4. A `move` from a Python page to a freeform file: refused at the write chain, so it is raised as a `drop` plus a freeform add.
5. Freeform findings stay separate from marks: a reviewer never files `mark` on a freeform path.

---

### Task 1: The cheat sheet

**Files:** Create `src/plugin/skills/comment-review/references/freeform.md`

- [ ] **Step 1: Draft it and bring Roy the exact wording**

It covers: comment-shaped text inside a string or heredoc is code; a line ending in a continuation is left whole, and so is the line after it; the interpreter line and a byte-order mark stay byte for byte; a comment ending in a backslash in C or C++ takes the next line with it; a directive in a comment is code (`/*!50000 ... */`, `/// <reference>`, `# shellcheck`, `// +build`); JSX text is not a comment; the file's line endings are kept; `old_string` carries the exact current text, so a stale file fails the edit.

- [ ] **Step 2: Apply the approved wording and commit**

Message: `Add the freeform edit cheat sheet`.

### Task 2: Reviewers report freeform findings

**Files:** Modify `src/plugin/skills/comment-review/references/reviewer-brief.md`

- [ ] **Step 1: Draft and approve the wording**

A freeform path has no address and no mark. A reviewer writes each finding on one to a file in its own temporary directory, as role, `path:line`, the exact current text, the proposed text and the reason, and returns that file's path. A reviewer handed an earlier reviewer's path reads it first.

- [ ] **Step 2: Apply and commit**

Message: `Tell reviewers how to raise a freeform finding`.

### Task 3: The task agent's stages

**Files:** Modify `src/plugin/skills/comment-review/SKILL.md:133-134,144-150`, stage 5 and stage 7b; `references/write.md:51-61`; the copy chief's agent file or brief; `references/compact.md:29` if it no longer holds

- [ ] **Step 1: Draft and approve the wording**

Stage 2: report the freeform list. Stage 4: topology order covers freeform files, and the task agent hands each reviewer the paths of the findings before it. Stage 5: the copy chief reads those paths and settles the findings into one list, and the human approves it beside the page diffs. Stage 7: an agent applies each with the Edit tool, following `references/freeform.md`. Stage 7b: the task agent runs the repo's formatter and the stage 1 check command on those files; `prove_unchanged` prints `UNCHECKED`, which is expected and is never reported as proven.

- [ ] **Step 2: Apply and commit**

Message: `Run freeform files through the stages`.

### Task 4: Exercise it

- [ ] **Step 1: Run `/comment-review` on a mixed Python and JavaScript change in a scratch repo**

Expected: the JS findings reach the copy chief by path, the applied edits pass the check command, the report says `UNCHECKED`.

- [ ] **Step 2: Grade from the diff and file what it shows**
