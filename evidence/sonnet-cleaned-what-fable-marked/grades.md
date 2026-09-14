# The 64 places, graded

Each place a Fable fork marked other than `clean` in the 2026-09-06 run, graded against the code
at `ab0f9266`. The Sonnet copy said `clean` at every one. See [`README.md`](README.md) for the
run and what `real` requires of each instruction.

**Basis** says what makes each finding a defect:

| basis | meaning | rows |
| --- | --- | --- |
| `role` | the role file's own remit: whether a statement is about its anchor, which single site owns a claim, whether a paragraph narrates the past | 45 |
| `style` | the run's style sheet: *"A quotation of Roy in shipped code is a citation to the log, not a paste."* The role file does not state this | 16 |
| `code` | a code concern, raised as a `human-review-necessary` query | 2 |
| `assertion` | the truth of what the sentence asserts, which the role file assigns to the other three roles | 1 |

## How each was checked

- Every path is under `src/comment_review/` unless it starts with `docs/`. A place's full
  address is `src:<path, with / as :>@<cue>`.
- Line numbers and greps are at `ab0f9266`, run from the root of a checkout of that commit.
- "Absent from `docs/`" was checked two ways:
  - a whitespace- and comment-marker-normalised search of every `docs/**/*.md`, so a quotation
    the log wraps across lines is still found;
  - a line grep of a short fragment of each quote, which returns nothing in `docs/`:
    `grep -rn "specific thing to the ast\|internal to the paragraph\|framing about positioning\|only place we need to care\|saving the anchor\|normal comment section\|trailing comments by\|matter designator\|same answer for the back\|in goes an address\|one source of truth\|state which, not the code" docs/`.
- Move destinations inside the code were resolved with
  `python src/comment-review.py addresser --binder <run binder> --file <path> --line N --series b`
  from a checkout of `ab0f9266`.
- The checks ran as untracked scripts -- `match_commit.py`, `dump64.py`, `quotes_in_docs.py`,
  `count_parts.py` and `g3_marks.py` -- in the 2026-09-13 grading session's scratchpad.

| # | path | cue | Fable | basis | verdict | evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | commands/__init__.py | a0 | drop | role | real | `docs/decision-log.md:1302-1304` (#12) already carries "10 of 19 shipped modules have a `main()`", `addresser` "imported by 7", the guard in "eleven" files -- the sentence restates that pre-ruling measurement |
| 2 | commands/addresser.py | a0 | drop | role | real | `grep -n "A MODULE DOES ONE JOB" src/comment_review/commands/*.py` -> 13 modules plus `commands/__init__.py:6` |
| 3 | commands/addresser.py | a2 | move -> decision-log.md | style | real | quote at `commands/addresser.py:166`; `grep -rn "in goes an address out comes" docs/` -> nothing |
| 4 | commands/addresser.py | b155 | query, human-review-necessary | code | real | `commands/addresser.py:285-288` says the remedy of citing the binder index is gone; `:328-331` still prints "cite the binder index alongside the address" |
| 5 | commands/addresser.py | b50 | drop | role | real | `flows/proof_io.py:10-14` states the three-step load, "Every command reads through here"; `grep -n "THE LOAD IS THE FLOW" src/comment_review/commands/*.py` -> 4 call sites restating it |
| 6 | commands/addresser.py | b59 | move -> history.md | role | real | `grep -n "isinstance(" src/comment_review/commands/addresser.py` -> only the comment at `:90`; `binder/binder.py:261`, `:279` refuse a non-dict binder and each page |
| 7 | commands/cap.py | a0 | drop | role | real | `commands/cap.py:17-18`; grep of #2 |
| 8 | commands/carry.py | a0 | drop | role | real | `commands/carry.py:9-10`; grep of #2 |
| 9 | commands/carry.py | b29 | drop | role | real | `commands/carry.py:53-55` restates `flows/proof_io.py:10-14` |
| 10 | commands/check.py | a0 | drop | role | real | `commands/check.py:12-13`; grep of #2 |
| 11 | commands/check.py | a1 | query, human-review-necessary | code | real | `commands/check.py:50-55` and `commands/collate.py:42-44`, `:137` each define `OK`/`BROKEN`/`UNREADABLE` and `_refused`; `commands/cap.py:34` and `commands/turn.py:29-39` import collate's |
| 12 | commands/collate.py | a0 | drop | role | real | `commands/collate.py:9-10`; grep of #2 |
| 13 | commands/collate.py | b21 | move -> history.md | role | real | `RECONCILE_ERRORS = (MismatchedRoot,)` at `commands/collate.py:95` and no `except KeyError` in the file (`grep -n "except " ...` -> `:250`, `:267`); `desk/proof.py:37-40`: `master_proof_of` no longer subscripts `read_from` |
| 14 | commands/collate.py | b26 | move -> history.md | role | real | `grep -n "_unruled_problems" src/comment_review/commands/collate.py` -> comments only (`:70`, `:126`); the anchor is `def _refused`; `flows/mark_errors.py:18-20` carries the Roy sentence |
| 15 | commands/collate.py | b72 | drop | role | real | `commands/collate.py:212-216` restates `flows/proof_io.py:10-14` and the wire-dict rule at `:16` |
| 16 | commands/compositor.py | a0 | drop | role | real | `commands/compositor.py:5-6`; grep of #2 |
| 17 | commands/compositor.py | b5 | move -> history.md | role | real | `grep -n -- "--repo" src/comment_review/commands/compositor.py` -> the comment at `:18` only; `results/compositor.py:375` `lossless(path)`, `:428` `identity(path)` take no `rel` |
| 18 | commands/distribute.py | a0 | move -> history.md | role | real | `grep -n -- "--check" src/comment_review/commands/distribute.py` -> the docstring at `:19` only; `commands/check.py:123` takes one role's `--edit-copy`, against "a role can no longer validate its own returned copy alone" |
| 19 | commands/distribute.py | b41 | drop | role | real | `commands/distribute.py:99-100` restates `flows/proof_io.py:10-14` |
| 20 | commands/gather.py | a0 | drop | role | real | `commands/gather.py:7-8`; grep of #2 |
| 21 | commands/gather.py | b68 | move -> decision-log.md | style | real | quote at `commands/gather.py:121-123`; `grep -rn "one source of truth, else something" docs/` -> nothing |
| 22 | commands/proof.py | a0 | drop | role | real | `commands/proof.py:7-8`; grep of #2 |
| 23 | commands/proof.py | b14 | patch, quote -> `Process: #76` | style | real | `docs/decision-log.md:2856`, inside #76 (`:2852`), carries "it could also be ownership contexts edit-copy" |
| 24 | commands/proof.py | b23 | patch, quote -> `Process: #77` | style | real | `docs/decision-log.md:2890`, inside #77 (`:2889`), carries "we add a --from-docket, --to-docket flags" |
| 25 | commands/proof.py | b55 | patch, quote -> `Process: #67` | style | real | `docs/decision-log.md:2541-2543`, inside #67 (`:2496`), carries "makes file io errors and malformed json load dump errors" |
| 26 | commands/prove_unchanged.py | a0 | drop | role | real | `commands/prove_unchanged.py:5-6`; grep of #2 |
| 27 | commands/referrers.py | a0 | drop | role | real | `commands/referrers.py:5-6`; grep of #2 |
| 28 | commands/topology.py | a0 | drop | role | real | `commands/topology.py:10-11`; grep of #2 |
| 29 | commands/turn.py | a0 | drop | role | real | `commands/turn.py:13-14`; grep of #2 |
| 30 | flows/__init__.py | a0 | move -> history.md | role | real | `flows/__init__.py:32` opens a paragraph on `gather` having been three subjects under the retired name `census`; `grep -n -i "code_names\|three subjects\|the-flow-lives-in-the-command" docs/history.md` -> nothing |
| 31 | flows/collate.py | a12 | correct | role | real | `flows/collate.py:551` cites `flows.revise.docket_of`; `grep -rn "def docket_of" src/comment_review` -> `flows/transcribe.py:56` only |
| 32 | flows/collate.py | a16 | correct | role | real | `grep -rn "def _reconcilable" src/comment_review` -> nothing; `flows/collate.py:644` records `_reconcilable` and `_keeps` as deleted at `P51` |
| 33 | flows/collate.py | b278 | move -> b284 | role | real | `flows/collate.py:872-874` explains the fallback at `:886` `named = document.get("role") ...`, not `:880` `envelope: list[Problem] = []`; addresser `--line 886 --series b` -> `@b284` |
| 34 | flows/proof_setter.py | a5 | drop | role | real | module docstring `flows/proof_setter.py:21-29` carries the two values, `unflatten` and the 2026-08-25 quote; `run`'s docstring `:132-137` repeats them |
| 35 | flows/proof_setter.py | a7 | correct | role | real | `grep -n "half-set" src/comment_review/flows/proof_setter.py` -> `:122`, in `run`'s docstring; the module docstring (`:1-40`) does not hold it |
| 36 | flows/proof_setter.py | b118 | drop | role | real | no `commands/galley.py` in the tree; `docs/history.md:117` records `commands/galley.py` as emptied 2026-08-26 |
| 37 | flows/proof_setter.py | b23 | drop | role | real | the unverified-guard fact is stated at the guard itself, `flows/proof_setter.py:311-316`; see the notes |
| 38 | flows/proof_setter.py | b55 | drop | role | real | `flows/proof_setter.py:206-210` narrates the old loop; `:171-173` states the current fact; the imports (`:46-52`) hold no `unflatten` |
| 39 | flows/revise.py | a6 | correct | role | real | `grep -n "docket_of" src/comment_review/flows/revise.py` -> `:58`, `:245`, both prose, no def and no import; defined at `flows/transcribe.py:56` |
| 40 | reading/__init__.py | a0 | move -> history.md | role | real | `reading/__init__.py:9` says `series` was absent from this inventory until 2026-08-29 -- the docstring's own past; `series` is in the inventory above it |
| 41 | reading/lexer.py | a0 | correct | assertion | real | `reading/lexer.py:23` says the module is a leaf that imports no sibling; `:36`, `:43`, `:48` import `reading.language`, `reading.paragraph`, `reading.series` |
| 42 | reading/lexer.py | a1 | move -> decision-log.md | style | real | quote at `reading/lexer.py:73-74`; absent from `docs/` |
| 43 | reading/lexer.py | a10 | move -> decision-log.md | style | real | quote at `reading/lexer.py:424`; absent from `docs/` |
| 44 | reading/lexer.py | a19 | move -> decision-log.md | style | real | quote at `reading/lexer.py:1075-1076`; absent from `docs/`; see the notes |
| 45 | reading/lexer.py | a20 | move -> decision-log.md | style | real | quote at `reading/lexer.py:1209-1210`; absent from `docs/decision-log.md` -- its first eight words occur only in `docs/plans/completed/0.2.4-rework-the-foliator-owns-the-address.md` |
| 46 | reading/lexer.py | a5 | drop | role | real | the `fn f<'a>(x: &'a T)` measurement is at `reading/lexer.py:216-219` (docstring) and `:233-238` (on the fixed-offset test at `:239`) |
| 47 | reading/lexer.py | a7 | move -> decision-log.md | style | real | quote at `reading/lexer.py:309-310`; absent from `docs/` |
| 48 | reading/lexer.py | a8 | move -> history.md | role | real | `reading/lexer.py:351-352` reports what the docstring used to say ("one rule for both tiers") -- its own past; `grep -rn "_own_characters(" src/comment_review` -> the def at `:345`, one call at `:1303` |
| 49 | reading/lexer.py | a9 | move -> decision-log.md | style | real | quote "not marking or saving the anchor" at `reading/lexer.py:393`; absent from `docs/` (the paragraph's other quote is in `docs/addressing.md`) |
| 50 | reading/lexer.py | b15 | move -> b7 | role | real | `reading/lexer.py:45-47` is about the `language` rows and sits on the `series` import (`:48`); `language` is imported at `:36`; addresser `--line 36 --series b` -> `@b7` |
| 51 | reading/lexer.py | b168 | move -> decision-log.md | style | real | quote at `reading/lexer.py:570`; absent from `docs/` |
| 52 | reading/lexer.py | b191 | move -> decision-log.md | style | real | quote at `reading/lexer.py:646`; absent from `docs/` |
| 53 | reading/lexer.py | b192 | move -> decision-log.md | style | real | quote "It is a matter designator ..." at `reading/lexer.py:674-676`; absent from `docs/` |
| 54 | reading/lexer.py | b202 | drop | role | real | `reading/lexer.py:696-697` repeats the words at `:674-675`; see the notes |
| 55 | reading/lexer.py | b222 | move -> history.md | role | real | `reading/lexer.py:766-767` says the file recorded the fix for the opening line only and never covered the closing line -- the file's own past |
| 56 | reading/lexer.py | b245 | move -> decision-log.md | style | real | quote at `reading/lexer.py:858-861`; absent from `docs/decision-log.md`; see the notes |
| 57 | reading/lexer.py | b247 | drop | role | real | `reading/lexer.py:881` repeats the clause quoted in full at `:861` |
| 58 | reading/lexer.py | b285 | move -> decision-log.md | style | real | quote at `reading/lexer.py:960`; absent from `docs/` |
| 59 | reading/lexer.py | b38 | move -> history.md | role | real | `reading/lexer.py:128-134` records the 2026-08-25 move to `series.py` and says nothing of `MODULE_ANCHOR` at `:136`; the quote is at `docs/decision-log.md:240` |
| 60 | reading/lexer.py | b406 | move -> b443 | role | real | `reading/lexer.py:1287-1291` defines the column and sits on `:1292` `lines=counted_lines(prose)`; the column is computed at `:1376`; addresser `--line 1375 --series b` -> `@b443`, `HELD` by the `:1373` column comment |
| 61 | reading/lexer.py | b449 | drop | role | real | the 2026-08-21 words are pasted at `reading/lexer.py:656-660`; both quotes are at `docs/decision-log.md:269-271` |
| 62 | reading/lexer.py | b46 | move -> a0 | role | real | the banner `reading/lexer.py:165-169` sits on `_join` (`:172`), which joins lines and is called only for `text=` (`:688`, `:1293`); see the notes |
| 63 | reading/lexer.py | b490 | correct | role | real | `reading/lexer.py:1467` cites `flag_structural_docs` (`:994-1035`, which mentions no cue or ordinal); the rule is at `:1162-1166`, inside `document_declarations` |
| 64 | reading/lexer.py | b60 | drop | role | real | `reading/lexer.py:200-202`, on `ESCAPE_WIDTH`, says the old bound of 10 missed its own example; `:242-244` repeats it |

## Notes: rows where the proposed change, or the mark's reason, goes past the defect

- **#2, 7, 8, 10, 12, 16, 20, 22, 26-29 -- the count in the reason.** The reason says "13 of the
  15 command modules". The grep finds the rule in 13 of the 14 non-package modules (not
  `taken_in.py`), in `commands/__init__.py:6`, and also in `src/comment_review/__init__.py:14`.
  The finding holds -- one rule, restated, with a package-level owner. Only the denominator is
  off.
- **#4.** The docstring also contradicts itself. `commands/addresser.py:285` calls a shared
  place a fault, and `:294-296` says a shared place does not fail the check.
- **#37.** The dropped sentence has two clauses:
  - the clause saying no test reaches `_one`'s guard is owned at the guard, `:311-316`;
  - the clause saying `_one`'s target guard builds a `draft` `Refusal` too completes STEPS' own
    list of where one is built; `_one` builds one at `:368-370`.

  The drop removes both clauses.
- **#44.** The same quote is also pasted at `reading/language.py:4` and
  `reading/addresser.py:106`. Moving the `lexer.py` copy leaves two more.
- **#54.** The reason says the ruling's owner is the decision log, but the log does not carry
  these words. The duplicate inside `lexer.py` is what makes the finding real.
- **#56.** `docs/addressing.md:199` already quotes these words; the decision log does not.
- **#62.** The banner says annotations are located in `lexer.py` and resolved in
  `annotate.py`. The code contradicts that:
  - `concordance/annotate.py:3-6` says that module resolves them and hands them over;
  - its regexes (`PATH_CITE`, `TICKED`, `COUNTED`) are at `:29-45`;
  - `lexer.py` adds only three structural annotations (`:710`, `:985`, `:1029`, `:1321`).

  The move would carry that claim into the module docstring. What is graded real is the
  anchoring half: the banner is not about `_join`.
- **#33, #50, #60 -- the destinations.** Each resolves at `ab0f9266` against the run's binder.
  `b284` and `b7` are `ABSENT` (empty places); `b443` is `HELD`.
