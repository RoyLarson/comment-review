# Addressing -- how this system names a place

!! **STOP. IF YOU ARE CLAUDE, DO NOT READ ON -- ask whether you should.** This file records how
the addressing was ARRIVED AT, including forms that were tried and dropped. Reading it puts
superseded rulings into your context beside the live ones, where nothing tells them apart.

!! **THE OFFICIAL DEFINITIONS ARE IN
`plugins/comment-review/skills/comment-review/references/vocabulary.toml`**, emitted by
`scripts/vocabulary.py`; `foliator.py` is the code that owns the naming.

**A place is where prose sits, or where prose could sit.** Every finding, every record, every
edit and every re-review names one.

## The rule

**An address is not a span of lines. Every LINE has exactly one address, and a BLOCK is just the
lines that share one.** Ruled by Roy, 2026-08-19.

```
pkg:mod.py@a5    a DECLARATION's documentation
pkg:mod.py@b3    a GAP between two lines of code
pkg:mod.py@c3    the room BESIDE a line of code
pkg:mod.py@f0    the FILE's own matter -- a licence, a shebang, an index
```

!! **THE PATH IS FLATTENED ON `:`, WHICH NO PATH MAY HOLD.** It was `.` until 2026-08-19, and a
dot is ordinary in a filename: `a/b.py` and `a.b.py` both flattened to `a.b.py`, so `a.b.py@a0`
named two blocks in two files -- and every other address of those files collided the same way.
`--check` reported "8 of 8 blocks addressed" with no SHARED, because it compares only within one
path. Roy: *"lets use an illegal symbol for the separator then."*

! **`:` is the one character Windows forbids that is not shell-special**, so an address stays
safe as a bare command-line argument where `<`, `>`, `|`, `?`, `*` and `"` would not. Measured
over 2,472 source paths in seven corpora: zero hold any of the seven. The extension keeps its
dot, so `b.py` and `b.rs` still differ.

! **Read it as a range and the old system returns under a new name.** You start asking which
lines a block "covers", whether two blocks overlap, and how wide to make an addressing range --
every one a question a line-numbered address had and this one does not.

! **An ANCHOR is the exception that proves it.** A declaration carries prose at several
addresses -- the `b` above it, the `c` beside it, its own `a`, the `b`s inside its body -- so an
anchor has many. A line has one.

## The three series

| | names | skips | counts |
| --- | --- | --- | --- |
| `a` | a DECLARATION's documentation | what is not documentable | declarations, in SOURCE order. `a0` is the module |
| `b` | the gap ABOVE a line of code | the module | its own walk. `b` runs one past `c`: the gap AFTER the last line |
| `c` | the room BESIDE a line of code | the module | its own walk, aligned with `b` |
| `f` | the FILE's own matter | everything but the module | its own walk. `f0` today |

!! **EVERY SERIES STARTS AT 0, AND A SKIPPED TRIGGER TAKES NO NUMBER.** Ruled by Roy,
2026-08-20: *"let's initiate all of them at 0 ... the foliations own their own rules on what is
skipped. `<module>` and its paragraph types get passed to all three, they each decide to record
and increment independently."*

! **`a` runs one AHEAD and `b` one BEHIND, and both are consequences rather than rules.** `a0` is
the module, so on a file with a single documentable declaration `a` is one ahead of the line's
own `c`; on any file with more code than declarations it falls behind. `b` emits a closing gap
after the last line of code, which `c` has no counterpart for. ! **`b` and `c` are otherwise
ALIGNED** -- `bN` and `cN` name the gap above and the room beside the same line -- *"until there
is some specific reason to split them or make them act different"*.

! **A SKIP THAT INCREMENTED is what this replaced**, on 2026-08-20. It burned `b0` and started
`c` at 1, and no test held either, so the two series began at 1 for no reason a reader could
derive.

!! **NO FOLIO CAN BE COMPUTED FROM ANOTHER, OR FROM A LINE'S ORDINAL.** Roy, 2026-08-19:
*"remove any references that indicate anyone can expect that the next line of code is guaranteed
to have the next foliation index. It is a happenstance and may change at any point if it is
determined that another system will work better."*

**Three FOLIATORS, three counters, one trigger list.** Each walks the MODULE and then every line
of code, takes a number at every trigger, and emits or does not: `a` and `b` emit for the module,
`c` steps past it. That any two series line up on a given file is an OUTCOME of that walk, not a
rule -- and nothing in this system reads one folio to derive another.

! **ASK. DO NOT COUNT.** `foliator.py --anchor LINE --series a|b|c`, or `locator.py --at
path:LINE`. The only supported way to learn a folio is to be told it.

!! **The `a` series counts DECLARATIONS, not code lines, and that is a ruling.** Numbering each
declaration by the `c` of its own `def` would put all three series on one count, and was
rejected. Roy, 2026-08-19: `a` as *"the module, class, function, method definitions in order ...
will make it easier for the agents to use, vs having to cross-reference where cs are and then
jump to there to see the as."*

! **It also settles the direction question.** A docstring is about its DECLARATION, so it does
not matter that Python's sits after its `def` and Rust's `///` before its `fn`. Roy, 2026-08-18:
*"a docstring is about the thing above not the thing below."*

## Every address has an ANCHOR, and the relationship is one-way

!! **AN ANCHOR HAS MANY ADDRESSES. AN ADDRESS HAS ONE ANCHOR.** Roy, 2026-08-19:
*"a, b, c are the address -- each has an anchor. An anchor can be tied to multiple
addresses ... anchors have many, an address has one."* One line of code carries the `b` above it
and the `c` beside it; one declaration carries those plus its own `a` and every `b` and `c` in
its body.

!! **THE ANCHOR IS THE LINE OF CODE -- the exact characters.** Roy, the same day: *"the anchor
isn't the technical symbols and their precise semantic meaning and code use. It is 'the line of
code' -- the exact characters in that line of code."*

**So it needs no parser, no language server and no build tool.** Every tier already finds where a
comment opens in order to cut there, which means it already holds the characters before it. Roy:
*"the lexer either knows what is before the trailing comment and can snag the whole string or it
is broken."*

| series | its anchor is |
| --- | --- |
| `a` | the LINE that declares it -- `def f():`, not `f`. The name is not carried: Roy, 2026-08-19, *"drop it -- the line is the anchor"* |
| `b` | the code line BELOW the gap -- the statement the prose introduces. At the end of a file, the line above, because that is the bound the gap has |
| `c` | the code on its own line, which is `line[:original_column - 1]` |

!! **A RECORD WITH NO ANCHOR IS A BROKEN RECORD** -- Roy -- and `record.seeded_problems` says so.
Measured 2026-08-19 against the commit before that rule: **6,376 of 6,531 blocks in this repo's
own shipped scripts carried an EMPTY anchor, 98% of the census**, and every seeded record repeated
it.

! **It was invisible from both ends at once.** `census.py` printed *"NO COMMENT carries an anchor
at either tier"* as a statement of intent, and `test_record.py` asserted which KEYS are seeded
rather than that either held a value. The two agreed with each other and agreed on nothing.

! **A `b` copies its anchor from that line's `c`, never re-cutting the line.** Every code line has
exactly one `c` and it already states where the code stops. Cutting again answered
`'    return os  # why'` where the `c` for the same line answered `'    return os'` -- two
computations of one fact, which is what `whole_lines` was removed for.

! **THE REVERSE DIRECTION IS NOT A LOOKUP THAT RETURNS ONE.** Roy, 2026-08-19, on two identical
statements in one file: *"for the addresses this is still exact -- for looking up the anchors to
get the addresses, not so exact."* Measured on his example:

```python
X=2   # initial

# stuff happens

X=2  # reseting X
```

Every ADDRESS is unique -- measured `a0 b1 b2 b3 c1 c2` -- and that is the direction a record
cites. But `X=2` is TWO anchors spelled alike, so it answers with **two `c` places and three `b`
places**, drawn from two different statements: the first gap is anchored to line 1, the other two
to line 5. ! Those folios are what THIS walk emits on THIS file. Nothing may count them out from
the lines -- see the ruling above.
`foliator.py --anchor` prints every match and says how many; the CALLER chooses by address.
Taking the first rules on the wrong statement.

! **An anchor has ONE spelling: the line of code.** A declaration's `a`, the `b` above it and the
`c` beside it all carry `def f():`. The NAME is not carried at all.


!! **A MODULE IS THE ONE ADDRESS WITH NO LINE OF CODE.** In Python it keeps `<module>` -- the name
the LANGUAGE uses for module-level code: it is `co_name` on the module's code object and the word
in every traceback, so it is a convention rather than something this system invented. Roy,
2026-08-19: *"that is why in python it should be `<module>`."*

! **Every other language gets its declared module name, wherever that line sits** -- Roy:
*"the rest get their declared module name that sits wherever."* Measured the same day: Go
(`package math`), Ruby (`module Foo`) and Java (`package com.example;`) all declare a module on a
real line, and the census already anchors their module documentation to it. They emit no `a`
series yet, so the rule waits on one -- which is Python plus any setup where a language server or
CodeGraph answers.

! **Two alternatives were tried and are worse.** The FIRST LINE OF CODE reads true only where a
language puts its module declaration first by rule; in Python the first statement is arbitrary, so
a module docstring came out anchored to `def f():`, and a file OPENING with a declaration gave
`a0` and `a1` one anchor between them. The FILE PATH is true and never collides, but puts a
second kind of thing in the field. ! The remaining option Roy named is `__module__`, the dotted
import name.

## A `c` place starts where the CODE stops

**Not at the `#`.** Roy ruled it 2026-08-19: *"c addresses start at the end of the code on the
line."* The whitespace separating a statement from its trailing comment belongs to the `c` place,
so `margin` and `trailing-comment` on one line carry the SAME column and an `add` and a `patch`
write to the same point. The census states it as `original_column`, 1-based, `0` where the block owns
its lines whole; `galley.splice` keeps `line[:original_column - 1]` and replaces the rest.

! **It is a little opinionated, and it is the opinion every formatter already holds.** black and
ruff normalise the gap before an inline comment to two spaces, `gofmt` aligns it, `cargo fmt` the
same. Roy: *"it happens to be the same opinionatedness that also sits in all of the code
formatters."*

!! **THE `c` SERIES IS WRITABLE, AND THAT IS WHY IT IS NOT AN EXTENSION OF `b`.** Roy: *"c needs
to be writeable. It is the reason c is not an extension of b."* A `b` splice replaces whole
lines; a `c` splice cannot, because the code shares the line. Until 2026-08-19 the join admitted
an edit at a `c` place and the galley refused it, discarding every other edit in that file with
it -- and before that, the splice deleted the statement: a galley read `# reworded trailing`
where `z = 3  # trailing` had been.

## An INTERMEDIATE comment is not censused

**`int x = /* why */ 5;` -- code on both sides -- is ignored, and its line is code.** Roy,
2026-08-19: *"they are not comments that can be systemically and completely verified across code
bases or written consistently on the same file because of line length rules ... all intermediate
comments are ignored. They can be brought up by the agents as code change suggestions."* The
same ruling that keeps a Python type annotation out of the census.

! **It was censused, and it was worse than unwritable.** Measured 2026-08-19:
`f.c@c1 comment text='int x = /* why */ 5;'` -- the statement itself handed to four reviewers as
prose, carrying no annotation to say so.

! **The proof got STRONGER.** `prove_unchanged` used to call such a file `unprovable` and refuse
to compare it; now the line is code and is compared character for character, so `int x = /* why
*/ 5;` and `int x = /* why */ 7;` differ. A run that CLOSES a multi-line comment beside code is
still `unprovable` -- that line IS censused and the census cannot place it.

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

**After, re-measured 2026-08-19 over 18 files in four languages -- `.py`, `.go`, `.rs`, `.rb`:
7,436 lines, each with exactly ONE address. 0 with none, 0 with more than one, 0 shared.**
`foliator.py --check` re-reads that claim on every run.

! **The first measurement was PYTHON-ONLY and overstated.** It read 6,873 lines, 0 shared -- true
of Python, where a comment cannot open after a statement and run on. In every C-family language
it could, and one address then named the comment AND the gap: `address()` decided "shares its
line" from a list of KINDS while `code_lines_of` decided it from `whole_lines`, and a mid-line
comment is in neither list. **Two computations of one fact, inside one module.** One fact now,
and the producer states it.

! **None of these was a bug in one place.** They were one absent definition, showing up
differently wherever a consumer had guessed.

## Where the definition lives

| file | owns |
| --- | --- |
| `scripts/page.py` | what a PAGE is -- `Paragraph`, the kind sets over it, and `page_for()`, which builds one |
| `scripts/foliator.py` | the ONE naming. It carried the deprecated `line_address()` beside it until 2026-08-20; see `docs/history.md` |
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
foliator.py --census <FULL CENSUS> --anchor LINE --series a|b|c

# by LINE, when what you have is a line of the original document
locator.py --census <FULL CENSUS> --at path:LINE

# an address in, the lines THIS CENSUS says it names out
foliator.py --census <CENSUS> --resolve <ADDRESS>
```

!! **THE ADDRESSER READS THE CENSUS, NEVER THE TREE.** It takes no `--repo`: every question it
answers is census-internal, and checking the file would assert that line numbers still matter --
which is what an address exists to stop. The CALLER chooses which census, so a post-write lookup
censuses the file first and the two agree by construction. ! Staleness belongs where a file is
WRITTEN: `galley.block_matches` refuses a stale range before it splices.

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

## A PAGE is FLAT, and the address is why

A page classifies every line of one file: this line is code, this PART of a line is code, this
line is comment, this line is docstring. It carries only which lines are which, which is what a
reviewer of COMMENTS needs.

!! **An address is an ORDINAL over a linear sequence, and an ordinal cannot express
containment.** Roy, 2026-08-18: *"it probably is just a flat list because of the way we defined
the address ... a CST has it but it is not actually one, which is why it is a pseudoCST."* So the
flatness is not an omission to fix; it is what the addressing forces.

! Nothing asks a tree question either. Measured 2026-08-18 across the shipped scripts: ZERO
containment tests, and every consumer is a flat scan by path, a lookup by line, an ordered walk
or a range splice.
