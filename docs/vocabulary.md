# Vocabulary -- the settled state

**Every term of art this system uses, and every word it stopped using.** This replaced
`vocabulary-inventory.md` and `vocabulary-usage.md`, which were the apparatus for FINDING the
terms: a twelve-agent survey, per-bundle tables, and 1,590 `file:line` citations into a tree that
has since been rewritten. Those did their job. `git log` holds them, and every ruling below is in
a commit message with the reasoning that produced it.

! **The terms AGENTS receive are not restated here.**
`plugins/comment-review/skills/comment-review/references/vocabulary.toml` holds them -- 43
definitions, written once -- and `scripts/vocabulary.py --reviewer <role>` emits each role's set
into its prompt. A second copy here would be the duplication this whole pass removed.
`scripts/check_vocabulary.py` proves that file complete and its role lists honest.

This document is for what that file does **not** carry: terms only the task agent uses, one term
kept deliberately with no shipped use, and the retired words.

## Terms the task agent uses and agents are not given

| term | means |
| --- | --- |
| **pCST** | *pseudo Concrete Syntax Tree* -- what the census IS: a node per INTERVAL between two lines of code, the comment runs and docstrings being the nodes that hold prose and the rest being where prose is missing. *Pseudo* because it comes from a comment-syntax record and a lexer, not the language's own grammar |
| **comment run** | the prose INSIDE a block: the contiguous comment lines between the two code lines that bound it |
| **counted lines** | what a cap charges for |
| **annotation** | a mechanical observation the census attaches to a node -- `names-a-symbol`, `cites-a-path`, `counted` |
| **mark** | editorial. Stage 4's name, and what it emits. The census's are ANNOTATIONS |
| **the join** | `verdicts.py` -- reads every reviewer's report against the census and against the others', and refuses what it cannot verify |
| **coverage gap** | a census index a reviewer never accounted for |
| **stripped** | the file with every comment deleted. What stage 7b compares, before against after |
| **fingerprint** | what the CODE CHECK compares: an `ast.dump` for Python, the stripped text otherwise |
| **CODE CHECK** | stage 7b's gate. Proves the parser reads the file the same before and after |
| **residue check** | the per-block procedure at 5, 6 and 7b: did this edit drop anything true, necessary and checkable? |
| **proof** | the finished page |
| **budget** | what a shipped instruction file costs everyone to load, in lines. Run data is not budgeted |

### ownership -- settled, and deliberately not emitted

**The relation: which anchor best justifies holding a comment.** `anchor` is the code position,
`owner` is the anchor that wins it, and **ownership** is the relation between them.

! **It appears nowhere in the shipped tree except as the root of a role's name.** Measured
2026-08-16: `ownership-context`'s own file uses `belongs` three times, `owner` twice and `OWNS`
twice, and the noun **zero** times -- its question is stated without it, *"does this comment
belong to the ANCHOR it sits on?"*

Kept anyway. Roy: *"it could easily popup in future works and then we have a problem."* A word
that returns with no ruling behind it is how the original polysemy happened.

! **Do not add it to `vocabulary.toml`.** That file holds what agents are GIVEN, and the drift
check refuses a term no role uses -- correctly. Adding it to tidy the numbers is writing to the
check.

## Retired -- do not bring these back

| word | what happened |
| --- | --- |
| `ANNOTATE` (stage 2) | -> **COLLATE**, ruled by Roy 2026-08-17. ANNOTATE meant adding notes and stage 2 adds none -- it gathers every position in the file into one numbered, ordered tree. ! It also pointed at two stages: `annotate.py` performs stage 3, and `annotate` / `annotation` belong there alone now |
| `prose tree` | -> **pCST**. Both named one thing once the census enumerated intervals, and the precise word won. Roy, 2026-08-17: *"pCST not prose tree"* |
| `angle` | -> **editorial role** in prose, **reviewer** in identifiers. Borrowed from `/simplify`; six senses, defined nowhere |
| `--angles`, `ANGLE FILES` | -> `--reviewers`, `REVIEWER FILES` |
| `sweep` | not a term. Stage 7b is **WRITE**; the word outlived `sweep.py`, now `census.py` |
| `reanchor` | -> **`move`**. A relocation is ONE judgment; the destination is payload |
| `HOME` | -> **owner**. It named the same site under a second stem |
| `jurisdiction` | -> **remit**. Judicial on an editorial system, and added by this branch before the metaphor was written down |
| `signature` (the CODE CHECK's) | -> **fingerprint**. `signature` means a function's, only |
| `residue` (the string) | -> **stripped**. The prose check keeps the word |
| `owner` (the census field) | -> **anchor**. The census computes the next declaration, which is a position, not a judgement |
| `level` | removed ENTIRELY in 0.1.5. It gated which verdicts a reviewer could emit and had no provenance -- zero commits in the project this was ported from. Every verdict is available on every run |
| `FORMATTING` | -> **`move`** to the line above. Never declared in the vocabulary, the brief or the gate -- and `verdicts.py` makes an unknown verdict fatal, so the instruction to emit it would have failed the run. Roy: *"I definitely didn't want a formatting category"* |
| `marks` (the census's) | -> **annotations**, including the JSON key |
| `walk` | an editor READS a manuscript and CHECKS a list. `ast.walk` is untouched |
| `detector` | the word is **annotation**. Everything it supported went with the suppression list |
| `gap` (the module-surface sense) | -> **omission**, which pairs with **obituary**: one is in the code and absent from the prose, the other the reverse |
| `statement` (of prose) | prose units are **sentence** and **clause**. `statement`, `expression`, `declaration` and `assignment` name CODE |
| `acquittal list` | **deleted.** It matched a prose SHAPE while every role's `clean` is a truth assertion at that role's scope, so the two disagreed. Its measurement was `evidence/ga/` -- ten candidates over six files, scored against one commit's diff -- and that search concluded *"the acquittal RATE is the trait; the acquittal LIST is just vocabulary"* |
| `suppression list` | **deleted.** No provenance in `evidence/` at all, and it suppressed nothing |
| `NOISE_FLOOR` / SUPPRESSED | **deleted** from `referrers.py`. Nothing gets suppressed |
| `CLEAN` range line | **deleted.** Every block is a RECORD now, `clean` included -- a range covered N blocks in one line and cited nothing |
| `assessability gate` | deleted -- used once, stated nowhere, and the idea was already stated without it |
| `acquittal rate` | deleted -- a measured quantity whose denominator no site stated |
| `worktree` | git's word, not this system's. ! The defect was six shipped rules citing it as a REASON, which was a fact about the eval rig |
| `CAP` in the packet | removed -- reviewers are not given a cap |
| `EDIT` (stage 5) | -> **APPLY**. Stage 7b is **WRITE**; `references/apply.md` is `write.md` |

## Rules about the words themselves

- **The metaphor is EDITORIAL.** Editorial roles read a manuscript and write editorial marks;
  a PROOFREADER reads the finished proof and says whether it deserves more marks. A new term
  comes from publishing, and is checked against the register **before** it is proposed.
  `CLAUDE.md` carries this rule and the reason.
- **A definition says what a word means and is emitted; a rule says what to do about it and
  stays** in the file that governs the stage.
- **Polysemy is allowed when it is DECLARED and the contexts do not overlap** -- `opener` (a
  comment delimiter, and a record's `--- RECORD`), `annotations` (the census's, and
  `from __future__`), `node` (a pCST node, and an AST node).
- **`clean` is reserved.** It is one of the seven verdicts and is never a loose adjective for
  code, prose, a grep result or a run.

## Where the discovery record went

`git log --follow docs/vocabulary-usage.md` and the commit messages on
`feat/settle-the-vocabulary` -- 67 commits, each carrying the ruling and the evidence for it.
The survey found `budget` and `own` nowhere in its own tables; both were found by reading. Treat
any term count as a floor.

`scripts/vocabulary_sweep.py` re-runs the search mechanically. Raw frequency ranks `here` and
`because` above every real term and was discarded; what works is DOUBLE USE -- a word in the prose
and bound as a module-level name in a script, which is the shape every miss has had.
