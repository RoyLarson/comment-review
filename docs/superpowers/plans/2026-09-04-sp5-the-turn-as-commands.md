# The Turn as Commands, and Gather -- Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** A task agent can drive a review from the console: `gather` builds the binder,
`collate` folds and writes the master proof and the first batch, `turn` advances the proof
by one turn, `cap` closes it with the chief's rulings. And stage 2 is `gather` in name as it
has been in vocabulary since 2026-08-23; `census` is retired (`Vocabulary: #34`).

**Architecture:** `flows/gather.py` is the chain of producers the command orchestrated by
hand; `commands/gather.py` is its face and calls `page_for` nowhere. `desk.proof.gather`
becomes `master_proof_of` so one verb names one act. `MasterProof` gains a load and a save
the way `Binder` has them; `commands/turn.py` and `commands/cap.py` expose `flows.turn`, in
the shape `commands/collate.py` has, and the session's `game.py` is their specification.

**Tech Stack:** Python 3.11 (floor, annotations EAGER), standard library only under
`src/comment_review/**`, `pytest`, `ruff`, `ty`.

**Plan steps this delivers:** `docs/plans/0.2.4-the-turn-as-commands.md` **P1-P9**. Those
close `TODO/no-command-for-the-middle.md` **T16** and
`TODO/census-should-be-a-chain-of-producers.md` **T1, T2, T3** (T4 is ruled, `#34`).

**Rulings:** `decision-log.md Process: #12` (a module does one job and has no CLI; a flow
calls modules; a command exposes a flow), `#65`/`#67` (raw JSON only at the load and the
save), `#87` (the master proof is the state between turns), `Vocabulary: #34` (census is
retired; `gather` is stage 2's and was never free for a second act).

---

## The order, and why

The rename goes first and in two steps: the second `gather` moves out of the way (Task 1)
before the chain takes the name (Task 2), so at no commit do two functions answer to it.
The prose sweep (Task 3) follows the code so every sentence it corrects names a module that
exists. The commands (Tasks 4-6) come after, so they are named beside `gather` and not
beside `census`. The game (Task 7) runs on commands alone, and files before it fixes.

**Changed in flight, 2026-09-04, at Task 2.** `tests/gates/test_skill_commands.py` holds
every command spelled in agent-facing prose to `COMMANDS`, so `census` leaving the enum
turns the gate red until `SKILL.md` and `references/review.md` spell `gather` -- the
coupling `SP-3` met. The six command lines are a one-for-one substitution `backend`'s
change forces (`conventions.md`, *A one-for-one substitution is not a crossing*), so
they land in Task 2's commit. Task 8 keeps what is left: the `--census` flag's spelling
once Task 3 renames it, and the filing of the prose sense to the agents lane.

## Global Constraints

- Run everything through `uv run`. Python **3.11** floor; annotations are EAGER.
- `desk/` is the MIDDLE and imports no `results/` or `docket/` module; `flows/` may import
  anything; a command exposes a flow and orchestrates nothing.
- No `except` clause in a shipped file holds a tuple literal.
- Test first, over real inputs. A literal only where malformed is the input.
- After each task: `uv run ruff check .`, `uv run ruff format .`, `uv run ruff check .`
  again, `uv run ty check`, `uv run python scripts/check_shipped_syntax.py`,
  `uv run python scripts/check_vocabulary.py`, `uv run pytest -q`. One failure is expected
  on a branch: `tests/gates/test_build.py`.
- **Every task ends in two commits.** The work, with a message written to a file and passed
  with `-F`. Then the tick: the `T`s closed against the work's sha, the `P` on the plan,
  the plan refreshed, this file's boxes -- committed on their own, naming the work's sha.
- A rename is a codemod: every count asserted before a byte is written, the diff printed,
  the first mismatch stops it with nothing changed. Never `sed`.

---

## Task 1: one verb, one act -- `desk.proof.gather` becomes `master_proof_of` -- P2 -- 848b71a4

**Files:** `src/comment_review/desk/proof.py`, `src/comment_review/flows/collate.py`,
`tests/helpers.py`, `tests/test_containers.py`, `tests/test_master_proof.py`, any other
caller `grep -rn "gather(" src tests` finds.

- [x] Test: the existing master-proof tests call `master_proof_of`; `grep -rn "def gather"
      src/` returns nothing (until Task 2 adds the one in `flows/gather.py`).
- [x] Rename by codemod; `proof.py`'s header names the act by what it makes.
- [x] Gates green; commit `-F`.
- [x] Tick: P2; commit.

## Task 2: the chain of producers, and the command that exposes it -- P9, T1, T2, T3 -- 68bfc548

**Files:** `src/comment_review/flows/annotations_for.py` (NEW), `src/comment_review/flows/gather.py`
(RENAMED from `flows/census.py`, and grown), `src/comment_review/commands/gather.py`
(RENAMED from `commands/census.py`, and shrunk), `src/comment_review/__main__.py`,
`tests/test_gather_command.py` (RENAMED from `test_census_command.py`), `tests/test_the_chain.py`,
`tests/test_stage_root.py`, `src/comment-review.py`'s usage text.

- [x] Test: `flows.annotations_for.annotations_for(paragraphs, known, paths, repo)` sets
      the same annotations `annotate` plus the repeated-literal pass set today, over a real
      page; nothing else calls `annotate` directly (T1's verify).
- [x] Test: `flows.gather.gather(repo, targets, revise)` returns the binder, the pages, and
      the gaps (`unreadable`, `no_record`, `files`) the command computes today; the chain is
      a tuple of steps, so adding one is a list element (T2's verify).
- [x] Test: `commands/gather.py` imports neither `page_for` nor `annotate` (T3's verify), and
      `test_gather_command.py` is `test_census_command.py` with the verb renamed and every
      exit code unchanged.
- [x] `Command.CENSUS` becomes `Command.GATHER`; no alias.
- [x] Gates green; commit `-F`.
- [x] Tick: P9, T1, T2, T3; commit.

## Task 3: every `census` takes its sense -- P1 -- 24b73424

**Files:** every file `grep -rli census src tests` names; `scripts/check_vocabulary.py`
(RETIRED gains `census: gather`); `CLAUDE.md`'s command block; `docs/vocabulary.md`'s
Retired table.

- [x] Codemod, sentence by sentence and not word by word: the ACT and the COMMAND become
      `gather`, the ARTIFACT becomes `binder`; a quoted ruling keeps its words. The diff is
      read before it is written.
- [x] `check_vocabulary.py` retires the word; the gate is green over `plugins/**/scripts`
      after the build is NOT run (plugins/ is built at release; the gate reads the shipped
      tree, so this is verified over `src/` by grep and over `plugins/` at release).
- [x] Verify: `grep -rn census src tests` returns nothing; `docs/vocabulary.md`'s Retired
      table carries the row; `CLAUDE.md`'s commands spell `gather`.
- [x] Gates green; commit `-F`.
- [x] Tick: P1; commit.

## Task 4: the master proof on disk, and collate writing it -- P3

**Files:** `src/comment_review/desk/containers.py` or a `flows/proof_io.py` (the load and
the save, `#65`/`#67`: raw JSON at the load and the save only), `src/comment_review/commands/collate.py`,
`tests/test_collate_command.py`, `tests/test_containers.py`.

- [ ] Test: `collate --proof-out P.json` writes a master proof that `MasterProof.deserialize`
      reads back with `turns == ()`, `determined` as the fold made them, `unsettlable` as
      the fold found them; `--batch-out B.json` writes `batch_for`'s batch when a place is
      carried forward and nothing otherwise.
- [ ] Test: the proof carries the copies AS THEY STAND, so `turn` can mutate and re-fold them.
- [ ] Gates green; commit `-F`.
- [ ] Tick: P3; commit.

## Task 5: the `turn` command -- P4, T16 (half)

**Files:** `src/comment_review/commands/turn.py` (NEW), `src/comment_review/__main__.py`,
`tests/test_turn_command.py` (NEW).

- [ ] Test, the shape of `game.py turn`: `turn --proof P.json --sent B1.json --answers
      ROLE=PATH ... --proof-out P2.json --batch-out B2.json`; the turn number is the proof's
      `turns` length plus one; every Revisit printed as `collate` prints one; exit codes as
      `collate`'s (`OK` nothing carried, `REREADS`, `ESCALATIONS`, `BROKEN` on an unreadable
      Revisit, `UNREADABLE` on a file that is not what it says).
- [ ] Test: `earlier` is the proof's own `determined`, so a stet keeps its turn across the
      command boundary; the turn record lands on the proof.
- [ ] Gates green; commit `-F`.
- [ ] Tick: P4; commit.

## Task 6: the `cap` command -- P5, T16 (the other half)

**Files:** `src/comment_review/commands/cap.py` (NEW), `src/comment_review/__main__.py`,
`tests/test_cap_command.py` (NEW).

- [ ] Test, the shape of `game.py cap`: `cap --proof P.json --rulings R.json --out chief.json
      --proof-out final.json`; refuses an unruled place naming it and its roles (`BROKEN`,
      nothing written); prints every unsettlable place for the human; the chief's copy parses
      as an ordinary edit copy.
- [ ] Test: a `recast` needs `prose`; a `taken_in` of `original` writes no entry.
- [ ] Gates green; commit `-F`.
- [ ] Tick: P5, T16; commit.

## Task 7: one hand on commands alone -- P6

**Files:** the session's `game.py` (rewritten to call the commands), `docs/the-turn.md`.

- [ ] `game.py` shells to `gather`, `distribute`, `collate`, `turn`, `cap` and `check`; no
      import from `comment_review`.
- [ ] One hand, four fresh roles, over a real file, to a stet or the cap. Every finding is a
      task before any fix.
- [ ] `docs/the-turn.md`'s NOT built rows: the command row becomes built with the shas; the
      SKILL.md row stays.
- [ ] Commit `-F`; tick P6; commit.

## Task 8: the shipped prose, one for one -- P7

**Files:** `plugins/comment-review/skills/comment-review/SKILL.md`, `references/*.md`,
`agents/*.md` -- ONLY where a command is spelled.

- [ ] `census` -> `gather` in every command line and flag; no sentence reworded. The
      prose sense of *the census* in the briefs is the agents lane's and is filed on
      `re-review-is-retired-for-revise` or its successor, with the counts.
- [ ] Verify: `grep -rn "census" plugins/**/SKILL.md plugins/**/references plugins/**/agents`
      returns prose only, no command; the gate `tests/gates/test_skill_commands.py` is green.
- [ ] Commit `-F`; tick P7; commit.

## Task 9: close -- P8

- [ ] File what this plan does not finish; `plan show` names no open reason; commit.
