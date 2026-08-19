# Addressing -- how this system names a place

**A place is where prose sits, or where prose could sit.** Every finding, every record, every
edit and every re-review names one. This file is the settled definition; `docs/vocabulary.md`
carries the one-line term and `plugins/comment-review/skills/comment-review/scripts/addresser.py`
is the code that owns it.

## The rule

**An address is not a span of lines. Every LINE has exactly one address, and a BLOCK is just the
lines that share one.** Ruled by Roy, 2026-08-19.

```
pkg.mod.py@a5    the 5th DECLARATION's documentation
pkg.mod.py@b3    the gap ABOVE code line 3
pkg.mod.py@c3    BESIDE code line 3
```

! **Read it as a range and the old system returns under a new name.** You start asking which
lines a block "covers", whether two blocks overlap, and how wide to make an addressing range --
every one a question a line-numbered address had and this one does not.

! **An ANCHOR is the exception that proves it.** A declaration carries prose at several
addresses -- the `b` above it, the `c` beside it, its own `a`, the `b`s inside its body -- so an
anchor has many. A line has one.

## The three series

| | names | counts |
| --- | --- | --- |
| `a` | a DECLARATION's documentation | declarations, in SOURCE order. `a0` is the module |
| `b` | the gap ABOVE a code line | code lines, from 0 |
| `c` | the room BESIDE a code line | code lines, from 0 |

!! **`bN` and `cN` name the SAME code line** -- `bN` above it, `cN` on it. Both count from 0,
which is what makes them line up. They did not until 2026-08-19: `c` counted from 1 and `b` from
0, so `b3` and `c3` named different statements and a reader pairing them attached a comment one
line too high.

!! **The `a` series counts DECLARATIONS, not code lines, and that is a ruling.** Numbering each
declaration by the `c` of its own `def` would put all three series on one count, and was
rejected. Roy, 2026-08-19: `a` as *"the module, class, function, method definitions in order ...
will make it easier for the agents to use, vs having to cross-reference where cs are and then
jump to there to see the as."*

! **It also settles the direction question.** A docstring is about its DECLARATION, so it does
not matter that Python's sits after its `def` and Rust's `///` before its `fn`. Roy, 2026-08-18:
*"a docstring is about the thing above not the thing below."*

## Every potential place has an address too

**Prose that is missing needs somewhere to be cited.** Roy, 2026-08-19: without the empty `c`s
*"you can't specify that the comment belongs at the end of the code line"*, and without the empty
`b`s *"you can't specify that the code should have multiple lines of comment above it."*

So each series has an EMPTY kind, and they are what an `add` cites:

| series | empty kind | is |
| --- | --- | --- |
| `a` | `undocumented` | a declaration with no docstring |
| `b` | `interval` | a gap with no prose |
| `c` | `margin` | a code line with no trailing comment |

! **A place with no lines of its own is at LINE 0.** An absent docstring occupies nothing, and a
gap between two adjacent code lines has no line to call its own. Their EDIT range still says
where prose would go. Given the declaration's own range instead, a module's absent docstring
spanned lines 1-4 and the locator answered `a0` for the comment at 3 and the `def` at 4, both of
which belong to other blocks.

## What makes an address stable

**Stage 7b's CODE CHECK.** It does not prove the file byte-identical -- for Python it compares an
`ast.dump`, elsewhere the stripped text -- but it proves the Nth code line is still the same
statement, which is exactly what an ordinal counts. The line numbers move with the prose; the
ordinal does not.

!! **It rests on the census being a HASHED STATIC TABLE** -- Roy, 2026-08-18 -- exact, constant,
FULLY ENUMERATED. A code line missed anywhere above a place does not fail: it RENAMES every place
below the hole, silently and consistently.

!! **And it claims nothing on an UNPROVABLE file.** `prove_unchanged` returns `unprovable` for a
comment delimiter sharing a line with code, an unterminated block comment, or a census that
disagrees with the file. Such a run is reported and counted a failure, so no address is handed to
stage 8 for a file the proof does not cover.

## Why this was rebuilt

**The previous version's weak link was that a place was never defined.** It was named by LINE --
`path:start-end` -- which is true of one file state, and this tool EDITS PROSE: every prose edit
moves the line numbers of the code below it. Nothing owned the definition, so each consumer
re-derived it, and they drifted apart in different directions.

Measured on this repo's own shipped scripts, 2026-08-18 and 2026-08-19:

| symptom | measured |
| --- | --- |
| two blocks answering to one address | **28** places, every one a docstring sharing a gap with the comment run beneath it |
| lines answering to TWO addresses | **2,303 of 6,775** -- every one a code line ending one gap and starting the next |
| lines answering to NONE | **131**, all blanks at the edges of gaps |
| `b` places that did not exist | **129**, `b0` missing in all 13 files -- no file could be given a comment above its module docstring |
| declarations with nowhere to cite a missing docstring | **730** |
| a FRESH census reading as stale | 3 blocks, because a block that stored no text was compared against lines that held some |

**After: 6,873 lines, each with exactly one address. 0 with none, 0 with more than one, 0 missing
`b` places, 0 shared.** `addresser.py --check` re-reads that claim on every run.

! **None of these was a bug in one place.** They were one absent definition, showing up
differently wherever a consumer had guessed.

## Where the definition lives

| file | owns |
| --- | --- |
| `scripts/pcst.py` | what a pCST NODE is -- `Block`, and the kind sets over it. A LEAF, so every module that reads a block can import the definition of one |
| `scripts/addresser.py` | BOTH namings -- `address()`, and the deprecated `line_address()` it replaced |
| `scripts/census.py` | STAMPS the address on every block. It is the producer, and consumers read it |
| `scripts/record.py` | `entry_for(address, blocks)` -- the one lookup from an address to a census entry |

!! **The line form is DEPRECATED and warns on every call.** Roy, 2026-08-18: *"any function
method or otherwise that uses that form gets a deprecated warning on it now. To make certain it
comes out."* It is read only to parse runs already recorded, so `evidence/` can be compared
against the format that replaced it.

## Asking for an address

**Do not count.** A filtered census collapses runs of empty places into one row, and counting
inside one is how a citation lands a place off.

```bash
# by ANCHOR -- which place of this declaration
addresser.py --census <FULL CENSUS> --anchor NAME --series a|b|c

# by LINE, when what you have is a line of the original document
locator.py --census <FULL CENSUS> --at path:LINE

# an address in, the lines it names now out
addresser.py --census <CENSUS> --repo D --resolve <ADDRESS>
```

!! **Prefer the anchor.** Asking by position -- "the block above the `def`" -- is right in Python
and wrong in Rust, whose `///` sits before its `fn` where Python's docstring sits after. The
census parsed the file and knows which is which; a count does not.

## What is NOT addressed

**Front matter** -- a licence header, a shebang, a coding declaration: the prose above a module's
own docstring. It keeps its address, and it is filtered out of what a reviewer reads, because no
role can settle it: a copyright line states no constraint the code could contradict, it documents
no function, it is not the module announcing its subject, and it sits where law or convention
puts it. An edit proposed on it becomes a `query` -- the human's to rule on.

Measured 2026-08-19 over 1,500 files in five corpora: **12 carried prose above the module
docstring, 10 of them the same Apache header repeated in every file of the project.** Inside a
declaration it never happens -- 0 of 2,579 docstrings.

## The pCST is FLAT, and the address is why

A pCST is a *pseudo* Concrete Syntax Tree: this line is code, this PART of a line is code, this
line is comment, this line is docstring. **Pseudo for two reasons** -- a real CST would carry the
names and the symbols precisely, and a real CST has HIERARCHY.

!! **An address is an ORDINAL over a linear sequence, and an ordinal cannot express
containment.** Roy, 2026-08-18: *"it probably is just a flat list because of the way we defined
the address ... a CST has it but it is not actually one, which is why it is a pseudoCST."* So the
flatness is not an omission to fix; it is what the addressing forces.

! Nothing asks a tree question either. Measured 2026-08-18 across the shipped scripts: ZERO
containment tests, and every consumer is a flat scan by path, a lookup by line, an ordered walk
or a range splice.
