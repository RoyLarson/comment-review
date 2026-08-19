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
| **address** | **`pkg:mod.py@a3`** -- the name of a place. ! The full definition, and what the line-numbered form got wrong, is [`addressing.md`](addressing.md), counted against the CODE and not against the lines. It is what a record cites, and the only name that survives this tool's own edits: every prose edit moves the line numbers below it, and an ordinal counts statements instead. The path is flattened on `:` -- a character no path may hold -- and keeps its extension, so neither `a/b.py` and `a.b.py` nor `b.py` and `b.rs` can collide. Three series -- `a` a declaration's documentation, `b` a gap, `c` beside a code line. !! **NOT A SPAN OF LINES: every LINE has exactly one address, and a BLOCK is just the lines that share one.** Ruled 2026-08-19. Read it as a range and the old system returns under a new name -- which lines a block "covers", whether two overlap, how wide to make it, every one a question a line-numbered address had and this does not. ! An ANCHOR is the exception that proves it: a declaration carries prose at several addresses -- the `b` above it, the `c` beside it, its own `a`, the `b`s in its body -- so an anchor has many. A line has one. |
| **folio** | the **`a3`** half of an address -- the part after the `@`, what `addresser.folio_of` returns. A leaf's number in publishing, which is what it is here. ! It is deliberately NOT called a *place*: measured 2026-08-18, `place` appears 119 times in the shipped tree and every one is ordinary English, including `ownership-context`'s own *"still be in the wrong place"* -- the role whose remit IS placement. A term of art there would put a second meaning on the sentence that role works from |
| **line of code** | **A line the census counts as CODE, and the exact characters on it that are code.** ! It is one of four kinds -- a **statement**, an **expression**, a **declaration** or an **assignment** -- which is the enumeration `vocabulary.toml` ships to every role. Both halves of the definition are needed: WHICH lines, because `b` and `c` are ordinals over them -- `b3` is "after the 3rd line of code" -- and WHICH CHARACTERS, because that string is the ANCHOR. ! A line is code when it holds something that is neither blank nor prose (`addresser.code_lines_of`). A comment-only line is not one; a blank line is not one; a line carrying a trailing comment IS one, and stays one. ! The characters are everything left of that line's `c` place, right-stripped -- `line[:edit_column - 1]`. **A TRAILING COMMENT IS NOT PART OF IT**: `z = 3  # trailing` is the line of code `z = 3`, and the two spaces belong to the `c`. !! **AN INTERIOR COMMENT IS**: `int x = /* why */ 5;` is the line of code `int x = /* why */ 5;` entire, because a comment fenced by code on both sides is not censused at all -- ruled 2026-08-19, on the same grounds as a Python type annotation. ! It is right-stripped, so trailing whitespace is not part of a line of code. ! And it is NOT unique: two identical statements in one file are two anchors spelled alike, which is why `--anchor` prints every match and the caller chooses by ADDRESS. |
| **anchor** | **The line of code that an address is attached to.** ! Direction matters and is not symmetric: **an anchor has MANY addresses, an address has ONE anchor.** One line of code carries the `b` above it and the `c` beside it; one declaration carries those plus its own `a` and every `b` and `c` in its body. ! Which line, per series: an `a` is attached to the LINE that declares it -- `def f():`, not `f`, and the name is not carried at all -- a `b` to the line of code BELOW the gap -- the statement its prose introduces, or the line ABOVE where the gap ends the file -- and a `c` to the code on its own line. ! **It is not a symbol and not a name of one.** Roy, 2026-08-19: *"the anchor isn't the technical symbols and their precise semantic meaning and code use. It is 'the line of code' -- the exact characters in that line of code."* !! Because it is a line of code and lines repeat, **an anchor is not unique**: `X=2` twice in one file is two anchors spelled alike, so the reverse lookup answers with several places and the caller chooses by ADDRESS. !! **A MODULE IS THE ONE ADDRESS WITH NO LINE OF CODE.** In Python it keeps `<module>` -- `co_name` on the module's code object, and the word in every traceback, so it is the LANGUAGE's own name and not one this system invented. Every other language gets its declared module name wherever that line sits (`package math`, `module Foo`), once a language server or CodeGraph gives its tier an `a` series. |
| **page** | **The file as a reader meets it**, rather than as a list of paragraphs. Stage 8 is the only pass that sees one -- `review.md` opens *"the finished page"* and asks *"does it still read as one page"*. ! **`proof` is the finished state of a page**, which is why both words are here and neither replaces the other. |
| **paragraph** | **One unit of prose on the page** -- a comment run, a docstring, or the empty place where either could go. It answers to exactly one ADDRESS. !! **It replaces `block`**, ruled by Roy 2026-08-19: the register is EDITORIAL and `block` was the last structural term borrowed from compilers. ! **And it is not only register.** Roy: *"this will make the text document formats read better when we implement them."* `block`'s shipped definition was *"the interval between two lines of CODE"*, which a markdown file does not have -- the reason [`a-prose-file-has-no-blocks`](../TODO/a-prose-file-has-no-blocks.md) is open. ! It passes the test that rejected `place`: every one of the 11 existing uses of `paragraph` in the shipped tree already means the unit of prose, where `place`'s 119 meant LOCATION against a term meaning ADDRESSABLE SLOT. ! **The rename is ~1,935 sites and is its own scope** -- [`a-block-is-a-paragraph-on-a-page`](../TODO/a-block-is-a-paragraph-on-a-page.md). |
| **pCST** | *pseudo Concrete Syntax Tree* -- **the PAGE, as the census sees it**, and the name is on its way out with `block`: a page holds paragraphs, and neither word is borrowed from a compiler. What the census emits: every LINE of the file classified. This line is code, this PART of a line is code, this line is comment, this line is docstring. *Pseudo* for two reasons: a real CST would carry the names and the symbols precisely, and a real CST has HIERARCHY. This is a flat list because an address is an ORDINAL -- `b3` is "after the 3rd code line" -- and an ordinal cannot express containment. Roy, 2026-08-18: *"it probably is just a flat list because of the way we defined the address ... a CST has it but it is not actually one, which is why it is a pseudoCST."* *Pseudo* because it comes from a comment-syntax record and a lexer, not the language's own grammar |
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
| **line address** (`mod.py:1-24`) | -> **address**. Deprecated 2026-08-18: it is true of ONE file state, and this tool edits prose. `addresser.line_address` still reads it and WARNS on every call -- Roy: *"any function method or otherwise that uses that form gets a deprecated warning on it now. To make certain it comes out."* ! The one reason it survives is parsing runs already recorded, so `evidence/` can be compared against the format that replaced it |
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
