# Commits this system can be graded against

**A fixture is a CHECKOUT AT A HASH, and a fix commit is an ANSWER KEY.** Ruled in
[`the-harness-cannot-run-the-system-it-grades`](../TODO/the-harness-cannot-run-the-system-it-grades.md):
this repo's own history is a fixture source, because the commit that fixes a prose defect says
what the defect was and what the correct prose is.

!! **ALL FOUR ROLES HAVE FINDINGS HERE**, which is what makes the range worth keeping.
Roy, 2026-08-20: *"they are also function context findings I bet -- every rename of the function
like `census_for` -> `page_for` is a function doing something different than what its name
suggests,"* and *"probably who knows how many block-context comments have and should be
corrected on this."* Both were checked and both hold, and asking the same of `ownership-context` found more.

| role | what it asks | what it finds here |
| --- | --- | --- |
| `module-context` | does the documentation say this module is ONE set of ideas? | a docstring announcing one subject over a module holding three |
| `function-context` | do name, signature, docstring and body agree? | `census_for` building a page; `gap_step` describing a walk it was not part of |
| `block-context` | is every claim true of the code it sits with? | comments naming symbols that were moved or deleted out from under them |
| `ownership-context` | is this prose about THIS piece of code? | a comment that travelled with the wrong constant, and a module named for what it used to be |

! Every one is readable from the file alone, with no knowledge of this session. That is the bar:
a reviewer that needs the transcript cannot be graded.

! **They are all from `d96b10d..7026646`**, branch `fix/folio-placement-is-not-where-the-anchor-is`,
2026-08-19 to 2026-08-20.

## How to run one

```bash
git worktree add <dir> <commit>^{}~1      # the tree BEFORE the fix
# run /comment-review over the file named in the row
git diff <commit>^{}~1 <commit>^{}         # the answer key
```

! The tags are annotated, so `^{}` is needed wherever a commit is wanted. ! Grade from the DIFF,
never from the run's own report -- self-reported confidence has been measured not to
discriminate real findings from fabricated ones.

## The cases -- `module-context`

| # | the file, before | what its docstring said | what the module actually held | fixed by |
| --- | --- | --- | --- | --- |
| 1 | `census.py`, **1,759 lines** | *"Stage 2, COLLATE: the pCST -- every line of these files classified"* | one file's paragraphs, AND their addressing, AND the aggregation across files. **Three subjects** | `4286833`, `afeba7b` |
| 2 | `page.py`, 220 lines | *"What a pCST NODE is"* | a node, and no PAGE at all -- the module was named for a thing it did not implement | `d09b0c1` |
| 3 | `page.py`, **1,543 lines** | *"A PAGE: one file, its paragraphs in order"* | that, plus 709 lines of language-specific LEXING -- the `Language` record, both tier readers, the text helpers | `4cb63f5` |
| 4 | `lexer.py` at its split | -- | the reader BUILDS a `Paragraph` and states its anchor, so the type belongs with it. The kinds split on the same line: a reader emits prose it FOUND, a page adds where prose is MISSING | `4cb63f5` |
| 5 | `addresser.py`, 835 lines | *"An address that survives the edits this tool makes"* | the FOLIATION -- it supplies a folio and flattens a path. **The address is composed in `page.py`** | `64ed7a4` |

## Why each is findable by reading, not by knowing

**1 -- `census.py`.** The docstring announces stage 2 and the classification of lines. The module
also contains `address()` calls per paragraph, `anchor_every_address()`, the file walk, the name
corpus and the listing. A reader asking *is this one set of ideas* has the whole answer in the
file. ! Roy, 2026-08-20: *"the census's job should be to take the output of all of the pages and
reformat it into the (most) usable format for the agents."*

**2 -- `page.py` had no `Page`.** The module is named `page`, its docstring says what a NODE is,
and `grep "^class"` returns `Paragraph` and nothing else. **The name and the contents disagree,
and the file says so on its own.**

**3 -- the lexer inside the page.** 709 lines answering *how does this language mark its prose*
sat under a docstring about what a page is. Measurable from the file: the `Language` dataclass,
an eleven-row table, two tier readers, and the text helpers, none of which is about a page.

**4 -- what the lexer emits.** The reader constructs the paragraph and states its anchor -- the
exact characters of the line of code -- so the type is the reader's output, not the page's
input. ! A reader emits `comment`, `docstring`, `trailing-comment`, `unparsed`; a page adds
`interval`, `margin`, `undocumented`. **The kinds split exactly where the modules do.**

**5 -- `addresser.py` addressed nothing.** `grep '@{' ` over the tree answers it: the address is
built in `page.py`. Roy, 2026-08-20: *"we have been using that word instead of address all
session ... it doesn't cause the system to crash but it also doesn't make the system work
correctly either."*

## The cases -- `function-context`

**Name, signature, docstring and body read together.** These are gradeable the same way, and the
file answers each on its own.

| the function, before | its name and docstring said | its body did | fixed by |
| --- | --- | --- | --- |
| `census_for(path, text, lang)` | a CENSUS -- *"the census for one file"* | built one PAGE. The census is every page in scope; this was one of them | `afeba7b` |
| `gap_step(paragraph, code)` | *"which TRIGGER a `b` paragraph belongs to"*, and *"THIS IS THE LOOK-AHEAD"* | `sum(1 for n in code if n < at) + 1` -- line arithmetic. **It described a walk it was not part of** | `64ed7a4` |
| `anchor_every_address(text, paragraphs)` | *"give every `a` and `b` place the line of code it is attached to"* | a SECOND pass restating what the walk had already emitted, from a `beside` map keyed on lines | `4286833` |
| `address(paragraph, code)` | one thing | composed a folio AND flattened a path AND joined them. The docstring needed an "and" to be accurate | `64ed7a4` |

! **`gap_step` is the sharpest of these.** Its own docstring uses the walk's vocabulary --
*trigger*, *look-ahead* -- while the body counts line numbers. A reader who trusts the docstring
believes a walk exists; a reader who reads the body finds arithmetic. Nothing but reading both
together catches it, which is exactly the remit.

!! **AND ONE IS LIVE RIGHT NOW**, in `page.py`, unfixed:

| function | returns |
| --- | --- |
| `code_lines_of(text, paragraphs)` | `list[int]` |
| `code_lines(text, prose)` | `set[int]` -- the SAME question, a different type |
| `lines_of_code(text, prose)` | `list[tuple[int, str]]` -- a DIFFERENT question |

Three names built from the same two words, in one module, returning three types. Filed as
[`three-names-two-words`](../TODO/three-names-two-words.md).

## The cases -- `block-context`

**Is every claim true of the code it sits with?** The moves in this range left comments behind,
and each is an OBITUARY: prose naming a symbol that exists nowhere.

| where | the claim | why it was false |
| --- | --- | --- |
| `page.py`, the `FRONT_MATTER` comment | *"`census.mark_front_matter` stamps it; `gap_step` reads it ... `census` imports it, so the constant cannot live in `census` without making the pair circular"* | `mark_front_matter` moved to the page, `gap_step` was deleted, and the circularity it argues about is a module layout that no longer exists. **Three false clauses in one comment** |
| `census.py`, above `_walk` | *"Tuples, so `DOC_ANCHORS` is built by concatenation and both go straight to `isinstance`"* | `NAMED_DEFS` and `DOC_ANCHORS` moved to `lexer.py`. The comment stayed and now sits above a function that walks the filesystem -- also an `ownership-context` finding |

! **Both were found by asking for obituaries mechanically** -- for each symbol a comment names,
does anything define it -- and both were introduced by this session's own moves, within hours.
That is the rate this class arrives at, and it is why a reviewer reads rather than a gate checks.

## The cases -- `ownership-context`

**Is this prose about THIS piece of code?** The moves in this range carried comments along with the
code they were near, not the code they were ABOUT. Each of these is on disk at the commit that
records them and fixed by the one after, so the diff is the answer key.

### The strongest specimen: a comment about the wrong constant

`page.py`, sitting above `_SHEBANG` and `_CODING`:

```
# The annotation, and the two shapes that earn it.
# ! DEFINED IN `page.py`, the leaf, because `foliation` reads it too and
# cannot import this module. Re-exported here so the many readers that
# already say `census.FRONT_MATTER` keep working.
```

**Every clause is about `FRONT_MATTER`, which is 390 lines above it.** It is a leftover from when
that constant lived in `census.py` and was re-exported; the comment travelled with the two regexes
instead. And each clause is separately false:

| clause | why |
| --- | --- |
| *"DEFINED IN `page.py`"* | the comment IS in `page.py` -- it tells a reader where they already are |
| *"the leaf"* | the page is not the leaf. `foliator` and `lexer` are, and the page imports both |
| *"`foliation` reads it too and cannot import this module"* | the foliator does not read these regexes, and it is spelled `foliator` |
| *"Re-exported here"* | nothing is re-exported; the constant is defined 390 lines up |

! **`ownership-context` finds this without knowing any of that history.** Its question is whether
the prose is about the code it sits on, and `_SHEBANG = re.compile(r"^#!")` is not a constant that
anything re-exports.

### A module named for what it used to be

| where | the prose | why it is wrong |
| --- | --- | --- |
| `page.py`, module docstring | *"THE ADDRESSER IS THE LEAF BENEATH THIS ONE ... the ADDRESSER KNOWS NOTHING ABOUT A PARAGRAPH"* | the module is `foliator.py`. The claim is still TRUE and names a module that does not exist |
| `page.py` ×3, `lexer.py` ×1 | ``  `foliation` `` naming the module | it is `foliator`; `foliation` is the RESULT, and is a variable name throughout both files |

! **This is the shape a rename always leaves**, and it is why `check_vocabulary.RETIRED` exists for
`block` and `pCST`. `addresser` was not added to it, so nothing caught these.

### Prose in the module that does not own the code

`lexer.py` names `code_lines` and `OCCUPIES_NOTHING` -- both defined in `page.py` -- while
explaining its own cutting rules. A cross-reference is legitimate; what makes these a candidate is
that the lexer's own docstring says it *"imports no sibling"* and knows nothing of places.

!! **AND ONE IS A REAL SPLIT IN THE WRONG PLACE, not just prose.** `lexer.py` emits
`kind="undocumented"` at line 990 -- a PAGE kind -- twenty-two lines after its own docstring says:

> *"A reader emits `comment`, `docstring`, `trailing-comment` and `unparsed` -- prose it found.
> `interval`, `margin` and `undocumented` are the page's, because only a page knows where prose is
> MISSING."*

! This is BOTH an `ownership-context` finding (`_undocumented` belongs to the page) and a
`block-context` one (the docstring's claim is false of the code beneath it). ! It is NOT fixed by
the commit after this: moving it needs the lexer to report its declarations and the page to emit
the places, which is filed as [`lexer-owns-a-page-kind`](../TODO/lexer-owns-a-page-kind.md).

## How the before/after works

! **The commit that records these leaves them ON DISK.** The commit after fixes them. So
`git diff <record>^{} <fix>^{}` over `plugins/` is exactly the set of changes a correct run should
propose, and nothing in the record had to be reconstructed from memory.

## More `block-context` -- a comment naming the wrong module

**Six comments say `module.symbol` where the symbol lives somewhere else.** Four were made by
this session's moves; two predate it and had gone unnoticed. Each is on disk at the commit that
records them and fixed by the one after.

| where | the comment says | it lives in |
| --- | --- | --- |
| `desk.py:357` | *"This calls `census.block_text`"* | `lexer.py` |
| `lexer.py:57` | *"see `census._anchor_of`"* | **`lexer.py` -- the file the comment is in** |
| `page.py:194` | *"`census.code_lines` is this function over its own `Paragraph`s"* | **`page.py` -- the file the comment is in** |
| `verdicts.py:434` | *"see `census.mark_front_matter`"* | `page.py` |
| `held.py:455` | *"`verdicts.parse_report`'s output"* | **`held.py` -- the file the comment is in** |
| `record.py:296` | *"`record.claim_object` read the deprecated form"* | `held.py` |

!! **THREE OF THE SIX POINT AT ANOTHER MODULE FOR CODE IN THE SAME FILE.** That is the shape
worth noticing: the prose was true when written, the code moved, and the sentence kept its old
address. Nothing executes a comment, so nothing noticed.

! **Two of them -- `held.py:455` and `record.py:296` -- predate this session entirely.** They are
the same class from an earlier split, which is what makes them the better fixtures: no knowledge
of today is needed to find either.

! **The check is mechanical and cheap**: for every `` `module.symbol` `` a comment names, ask
which module defines that symbol. A run that misses these is missing something a regex found.

## More `block-context` -- a consolidation that miscounts what it consolidated

`page.py:341`, in `empty_places`'s own docstring, written at `9293806`:

> *"ONE LOOP, WHERE THERE WERE THREE GENERATORS. `intervals`, `margins` and `_undocumented` each
> walked the file again to decide which places of their own series deserved a paragraph -- 206
> lines answering one question three ways."*

**Three checkable claims, three answers, none of them 206:**

| the claim | measured at `9293806^` |
| --- | --- |
| `_undocumented` was one of the three | it was **still alive in `lexer.py`**, still emitting, for two more commits. The third consolidated there was `paragraphs_in` |
| 206 lines | the three NAMED held **181** (76 + 50 + 55). The three actually consolidated held **143** |
| three generators | **four**, once `_undocumented` went at `7cbfa96` -- 198 lines |

!! **THE PROSE DESCRIBED THE CHANGE THE AUTHOR MEANT TO MAKE, not the one on disk.** The
`_undocumented` half was real work, correctly reasoned, and landed two commits later -- the
sentence simply ran ahead of it. That is the failure mode a green gate cannot see: every test
passed at `9293806` precisely because the function the docstring buried was still there doing
its job.

! **`block-context` owns this twice over** -- a state claim (a named function that was not in
the state the prose puts it in) and a constraint claim (a count with no arithmetic behind it).
! **The count is the sharper fixture**, because no history is needed: `206` matches no sum of
the functions named, at any commit, and a reader who adds them up finds that without leaving the
file's own diff.

## More `function-context` -- a wrapper that every caller undoes

`page.py` carries three functions built from the same two words:

| | returns | callers |
| --- | --- | --- |
| `code_lines_of(text, paragraphs)` | `list[int]`, **ascending by construction** | the other two |
| `code_lines(text, prose)` | `set[int]` -- the same question | 1 in the shipped tree, ~15 in tests |
| `lines_of_code(text, prose)` | `list[tuple[int, str]]` -- a different question | the walk |

!! **NEARLY EVERY CALLER WRITES `sorted(code_lines(...))`**, which converts the set back into the
list `code_lines_of` already returns. The wrapper's whole contribution is a round trip: the
function exists to change the type, and the caller changes it back on the same line.

! `code_lines` is TWO LINES over `code_lines_of`, and its only remaining reason -- it took
`Paragraph` objects where the other took dicts -- went when the page was made to speak dicts
throughout. Filed as [`three-names-two-words`](../TODO/three-names-two-words.md).

! **`function-context` asks whether name, signature and body agree.** Here the names do not
distinguish the functions, the return types differ for one question and match for two different
ones, and the body of one is the other with a `set()` around it.

## What is NOT a test case for this system

! **Process defects are not prose defects.** A plan checkbox ticked on work that was not done, a
test decorator that reports an unexpected success, a hand-written fixture -- all were found in
this range and all were valuable, and **none is something `/comment-review` could find.** It
reads comments and docstrings against the code they sit with; it has no remit over a plan, a
test harness or a fixture file. Recording them here would measure the system against work it
does not do.

## What has not been done

! **None of these was found by `/comment-review`.** Every one was found by a person reading.
Running the system over them is the point of recording the range, and
[`the-harness-cannot-run-the-system-it-grades`](../TODO/the-harness-cannot-run-the-system-it-grades.md)
is what blocks it.

! **The suite was green throughout** -- 672 to 713 passing across all five, and every gate green
too. **The four editorial roles are the only thing in this repo that could have caught any of them.**
