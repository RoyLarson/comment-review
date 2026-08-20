# Vocabulary -- what this system STOPPED saying

!! **STOP. IF YOU ARE CLAUDE, DO NOT READ ON -- ask whether you should.** This file is a record
of words this system no longer uses and of definitions that have since moved. Reading it puts
retired terms and superseded rulings into your context beside the live ones, where nothing tells
them apart. `docs/addressing.md` carries the same warning for the same reason.

!! **THE OFFICIAL DEFINITIONS ARE IN
`plugins/comment-review/skills/comment-review/references/vocabulary.toml`.** They reach an agent
by being EMITTED -- `scripts/vocabulary.py --reviewer <role>` -- and a file that uses a term
states no definition of its own. **Only definitions that have been RETIRED or MODIFIED are
here**, and `scripts/check_vocabulary.py` refuses a live term defined in both places.

## Retired -- do not bring these back

| word | what happened |
| --- | --- |
| `ANNOTATE` (stage 2) | -> **COLLATE**. Stage 2 adds no notes; it gathers every position in the file into one ordered tree. It also pointed at two stages -- `annotate.py` performs stage 3 |
| **line address** (`mod.py:1-24`) | -> **address**. True of ONE file state, and this tool edits prose. `addresser.line_address` still reads it and WARNS on every call; it survives only to parse runs already recorded |
| `block` | -> **paragraph**. The register is EDITORIAL, and `block` was the last structural term borrowed from compilers. Its definition -- the interval between two lines of CODE -- is also untrue of a prose file |
| the four KINDS of a line of code | **deleted** -- *statement, expression, declaration, assignment*, shipped to every role and read by nothing. Neither exhaustive nor disjoint, and meaningless in the three data languages |
| **census index** | -> **address**. A position is correct only for the census it was written against; an `add` or a `drop` shifts every index below it |
| `prose tree` | -> **pCST**. Both named one thing, and the precise word won |
| `angle` | -> **editorial role** in prose, **reviewer** in identifiers. Six senses, defined nowhere |
| `--angles`, `ANGLE FILES` | -> `--reviewers`, `REVIEWER FILES` |
| `sweep` | not a term. Stage 7b is **WRITE** |
| `reanchor` | -> **`move`**. A relocation is ONE judgment; the destination is payload |
| `HOME` | -> **owner**. It named the same site under a second stem |
| `jurisdiction` | -> **remit**. Judicial on an editorial system |
| `signature` (the CODE CHECK's) | -> **fingerprint**. `signature` means a function's, only |
| `residue` (the string) | -> **stripped**. The prose check keeps the word |
| `owner` (the census field) | -> **anchor**. It is a position, not a judgement |
| `level` | removed ENTIRELY. It gated which verdicts a reviewer could emit and had no provenance. Every verdict is available on every run |
| `FORMATTING` | -> **`move`** to the line above. Never declared in the vocabulary, the brief or the gate, so emitting it would have failed the run |
| `marks` (the census's) | -> **annotations**, including the JSON key |
| `walk` | an editor READS a manuscript and CHECKS a list. `ast.walk` is untouched |
| `detector` | the word is **annotation** |
| `gap` (the module-surface sense) | -> **omission**, which pairs with **obituary**: one is in the code and absent from the prose, the other the reverse |
| `statement` (of prose) | prose units are **sentence** and **clause**. The word names CODE |
| `acquittal list` | **deleted.** It matched a prose SHAPE while every role's `clean` is a truth assertion at that role's scope, so the two disagreed |
| `suppression list` | **deleted.** No provenance, and it suppressed nothing |
| `NOISE_FLOOR` / SUPPRESSED | **deleted** from `referrers.py`. Nothing gets suppressed |
| `CLEAN` range line | **deleted.** Every paragraph is a RECORD now, `clean` included -- a range covered many in one line and cited nothing |
| `assessability gate` | deleted -- used once, stated nowhere, and the idea was already stated without it |
| `acquittal rate` | deleted -- a measured quantity whose denominator no site stated |
| `worktree` | git's word, not this system's. It had been cited as a REASON in six shipped rules, which was a fact about the eval rig |
| `CAP` in the packet | removed -- reviewers are not given a cap |
| `EDIT` (stage 5) | -> **APPLY**. Stage 7b is **WRITE**; `references/apply.md` is `write.md` |

## ownership -- settled, and deliberately not emitted

**The relation: which anchor best justifies holding a comment.** `anchor` is the code position,
`owner` is the anchor that wins it, and **ownership** is the relation between them.

It appears nowhere in the shipped tree except as the root of a role's name, and is kept so the
word cannot return without a ruling behind it.

! **Do not add it to `vocabulary.toml`.** That file holds what agents are GIVEN, and the drift
check refuses a term no role uses. Adding it to tidy the numbers is writing to the check.

## Rules about the words themselves

- **The metaphor is EDITORIAL.** Editorial roles read a manuscript and write editorial marks;
  a PROOFREADER reads the finished proof and says whether it deserves more marks. A new term
  comes from publishing, and is checked against the register **before** it is proposed.
  `CLAUDE.md` carries this rule and the reason.
- **A definition lives in exactly one place and reaches an agent by being EMITTED.** A file that
  uses a term states no definition of its own.
- **A definition states only what is necessary** -- not the measurement that produced it, not the
  date, not what it replaced. Every word in `vocabulary.toml` is shipped into a prompt and
  charged for; this table is where a superseded term stays legible.
- **Polysemy is allowed when it is DECLARED and the contexts do not overlap** -- `opener` (a
  comment delimiter, and a record's `--- RECORD`), `annotations` (the census's, and
  `from __future__`), `node` (a pCST node, and an AST node).
- **`clean` is reserved.** It is one of the seven verdicts and is never a loose adjective for
  code, prose, a grep result or a run.
