# Retire row everywhere -- the type, the wire key and the prose

```
Status:   open
Progress: 0 of 5 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-09-02 (systems)
```

## Objective

`row` is retired everywhere -- as a type, as a JSON key, and in prose. The word
this system has for one place is **paragraph**. `decision-log.md Vocabulary: #31`.

!! **IT WAS SUPPOSED TO GO WITH THE `block` -> `paragraph` RENAME, AND AN
UNAUTHORISED SENTENCE KEPT IT.** `docs/vocabulary.md` read *"`row` IS NOT
RETIRED, because it was never a term -- it is the name of a key in a JSON file,
and it stays that."* Nobody ruled it. Roy, 2026-09-02: *"That was strictly not
authorized and was supposed to be retired at the same time as the paragraph
name. There was no authorization to keep anything as a row."*

!! **AND NO GATE COULD HAVE CAUGHT IT.** `scripts/check_vocabulary.py`'s
`RETIRED` dict is hand-maintained -- `block`, `blocks`, `pcst`, five folio
terms, `join`, `verdict`, `verdicts` -- and **holds no `row` entry**, so no
shipped file was ever tested for the word. ! The struck sentence then supplied a
reason for the gap, which is what made the absence read as a decision. **A gate
that never held the entry, with prose explaining why that is correct**, is worse
than one edited to pass: there is no diff to notice.

! **MEASURED 2026-09-02: 137 occurrences across 24 files in `src/`**, in at
least three senses, which is why the tasks are separate rather than one sweep:

| where | what it is |
| --- | --- |
| `desk/mark.py:155` | `class Row`, with `INSTRUCTIONS: dict[Instruction, Row]` |
| `binder/page.py` | the `rows` key it serialises and reads back |
| prose, several modules | a paragraph called *"the binder's row"* |

! **`Row` CITES PROSE AS ITS AUTHORITY**, which is the shape to watch for: its
docstring justifies the name by `docs/the-mark.md` saying *"four classifier
columns"* and *"seven row flags"* -- the word being used, offered as a reason to
take the word.

!! **THE SAME INVENTION WAS ALREADY CAUGHT ONCE.** `BinderRow` and `BinderPage`
were added and deleted the same day, 2026-08-31 (`1d9314d`), after Roy: *"So you
invented a term 'row' for something that is a Paragraph."* `Row` in `desk/mark.py`
survived because it is in a different module and nothing mechanical was looking.

! **T4 LANDS LAST, DELIBERATELY.** Adding the word to the gate before the rename
turns it red across 24 files with no rename behind it. Roy, 2026-09-02: the
record, the correction and this filing are *"the correct thing until we can get
through the outstanding todo contradictions"*.

!! **AND T4 WAS UNSCOPED WHEN THIS FILE WAS WRITTEN, WHICH IS WHY T5 EXISTS.**
`row` has a SECOND live sense with its own unretracted ruling --
`reading/language.py:20`: *"ADDING A LANGUAGE IS A ROW, NOT CODE. That is the
whole design"*, on Roy, 2026-08-20. **13 uses in that module alone** are that
sense. A `RETIRED` entry cannot tell two senses apart: `check_retired` matches
the bare word with a letter boundary and prints one remedy, so it would report
`language.py`'s own design claim and tell a reader to *say `paragraph`* -- which
is false for a language row.

!! **THE REPO HAS ALREADY MEASURED THIS EXACT FAILURE, WITH `block`.**
[`vocabulary-gate-is-red`](vocabulary-gate-is-red.md): the rename that followed
*"replaced the LIVE senses instead of the dead one"* -- five sites, one of them
*"a Java text PARAGRAPH"*. **The cheapest way to satisfy an unscoped gate is to
rewrite correct prose into wrong prose**, so scoping it is what stops the fix
from becoming the defect.

! T3 was already scoped -- *"prose that calls a paragraph a row"*. T4 was not.

! **T1 MAY OWE A RULING.** What `Row` becomes is a naming decision, and this
repo checks a candidate against the editorial register before proposing it. If
the answer is not obvious from what the thing does, it is Roy's.

! `decision-log.md`'s own `Addressing: #12` and `#16` carry the word in their
titles -- *"A census row carries SIX fields"*, *"`anchor_num` LEAVES THE ROW"*.
Those are the record of what was decided and are not rewritten.

## Tasks

- [ ] T1 | Rename desk/mark.py's Row for what it is: one instruction's spec
- [ ] T2 | Rename the rows wire key binder/page.py serialises and reads back
- [ ] T3 | Update src/ prose that calls a paragraph a row
- [ ] T4 | Add row and rows to check_vocabulary.py's RETIRED, once T5 rules the
      language-row sense and the rename lands
- [?] T5 | Decide whether the LANGUAGE-ROW sense is retired too, or is declared
      polysemy. Verify: the answer is in `docs/vocabulary.md`
