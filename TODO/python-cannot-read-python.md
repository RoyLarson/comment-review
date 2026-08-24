# The AST reader gets older every release while the files get newer

```
Status:   open
Progress: 31 of 37 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21, on four sentry files the floor interpreter cannot
          parse: 'we can't use python to parse python files ... that means using the ast
          to bootstrap the pieces fails on new python syntax. This puts python right
          next to the other languages in the lexer')
Evidence: 2026-08-22 — THE ONE FILE THAT WILL NOT ROUND TRIP IS THE ARGUMENT FOR THIS
          TODO. Roy, 2026-08-22: *"it actually is the thing that puts python in the
          lexer category. They will get lost without it. Your numpy tests prove it."*
          MEASURED: of 3,228 files across ten languages, exactly ONE differs --
          `corpora/numpy/numpy/exceptions.py`, which ends `"""  # NOQA` and then `pass`.
          The docstring's CLOSING QUOTE shares its line with a comment, so the AST hands
          over a docstring node with an `end_lineno` while the comment arrives from the
          tokenizer as a separate token, and reassembling the two puts one line's
          content on the next. ! A CHARACTER READER HAS NO SUCH SEAM: it meets the quote
          and the comment in order, on one line, as text. ! So the single strongest
          check in this tree fails on precisely the shape the AST tier creates and the
          lexical tier does not -- which is evidence for the rework rather than a defect
          beside it.
SCOPED:   2026-08-23 — 2026-08-23, Roy: 'The task is simple. Make the lexer be able to
          parse python code.' All 31 prior boxes were records, rulings, measurements or
          arguments -- none was a task -- and they are ticked as the record of how the
          ruling was reached. ! ONE AST DEPENDENCY SITS OUTSIDE THAT SCOPE:
          prove_unchanged fingerprints Python with ast.dump(ast.parse(text)), so it
          carries the same floor limit and is not in the lexer. The 2026-08-21 ruling
          says the code check belongs to the COMPOSITOR, where the page's c places hold
          every line of code verbatim -- that is what answers it rather than moving it.
          Not filed as a task here because it is not the lexer; it belongs to whatever
          works the compositor half.
TRIAGED:  2026-08-23 -- LABELS ONLY. The 2026-08-23 restructure is accepted as it stands:
          31 records ticked, two tasks open, and nothing here is reworked. T1..T33 are
          added in file order. ! BOTH TASKS RE-VERIFIED AS STILL LIVE: `grep -rn 'import
          ast' plugins/` returns FOUR hits -- lexer.py:28, census.py:36,
          prove_unchanged.py:36, referrers.py:16 -- so neither T32's read path nor T33's
          proof has been changed. ! Status stays `open`, not `in-progress`: every ticked
          box is a record, and no lexer work has started.
SPLIT:    2026-08-23 -- the two open boxes each carried a three-part `Verify`, and each
          part is a separate artifact ticked at a separate time. T32 became the lexical
          read path, the round-trip over the corpora, and the newer-than-floor file;
          T33 became the proof, the fixtures and the docstring. The 31 records keep
          their boxes as ticked labels and their text moved into the Objective below.
```

## Objective

**The lexer cannot read Python. `ast` reads it, and `ast` is the interpreter running the
tool** -- so the tool can only read code its own floor can parse.

!! **MEASURED: 3.11 IS THE FLOOR AND IT CANNOT PARSE 3.14 CODE.** `.python-version` pins 3.11
because that is what `plugins/` ships against, and any syntax added after it fails to parse.
Measured on NumPy. **This breaks on every new version of the language, permanently** -- it is
not a bug to fix once, it is the shape of depending on the running interpreter to read the
subject.

! **AN UNPARSED PAGE SETS AS AN EMPTY FILE**, which is the sharp edge: the failure is silent
at the point it matters.

! **Everything else this file used to carry -- the four AST dependencies, the trade, the
position rule, the PEP 701 case, the Lisp argument -- is reasoning and measurement, not work.**
It is kept below, in the record, as how the ruling was reached.

**Roy, 2026-08-23, ruling the scope: *"The task is simple. Make the lexer be able to parse
python code."***

## The record -- how the ruling was reached

Thirty-one findings, rulings and measurements. Each is ticked below as a record, with its
text kept here.

**R1 -- THE FLOOR IS A HARD CONSTRAINT AND THE LANGUAGE KEEPS MOVING.** `.python-version`
pins 3.11 because that is what `plugins/` ships against -- Roy: *"the floor will not fail if
we are using the floor to evaluate the code."* So `ast.parse` reads the syntax of 2023
forever, while the files under review are written this year. MEASURED 2026-08-21: 4 of 2,310
`.py` files in `corpora/` do not parse on 3.11, every one of them PEP 695 -- `class
SequencePaginator[T]:`, `type QueryOp = Literal[...]`, `def sudo_required[T, **P](...)`.
! 0.17% today and one-directional.

**R2 -- AN UNPARSED PAGE SETS AS AN EMPTY FILE**, which is the sharp edge of it. `page_for`
skips the walk when any paragraph is `unparsed`, so `cues.reading` is empty and
`compositor.set_page` returns `""`. MEASURED on `sentry/src/sentry/api/paginator.py`: 884
lines in, 0 characters out. ! `draft()` would write that empty file. Roy's *"no editing on
the real file until approved"* is what stands between it and the tree. The guard is small and
should land first: the compositor must REFUSE a page with no places, never set one.

**R3 -- TWO READERS MEANS EVERY RULE IS WRITTEN TWICE, AND ONE WRITTEN ONCE IS SILENTLY WRONG
ON THE OTHER TIER.** Roy: *"which is certainly hiding a lot of bugs."* THREE instances in a
single day, 2026-08-21 -- R4, R5 and R6.

**R4 -- THE MATTER TYPE** was written in `paragraphs_lexical` alone, so every `.py` file
reported NO front matter at all while `.c` reported it correctly. Caught only because a test
fixture happened to be Python.

**R5 -- THE DELIMITER FLUSH** is the one that matters: `paragraphs_lexical` ended a paragraph
at a comment's opener AND its closer, so `/* one */`, a blank and `/* two */` shared one
address. MEASURED: 157 shared addresses in the lexical languages and ZERO in Python, whose
reader merged runs correctly all along. **PYTHON'S CORRECTNESS HID THE LEXICAL DEFECT FOR AS
LONG AS THE TREE EXISTED** -- every Python test passed over it.

**R6 -- `_is_doc` was computed INLINE in `flush`** and re-derived differently in `carry`, so a
`/** */` at the head of a file was documentation to one and an ordinary comment to the other.

**R7 -- MEASURED, the surface:** FOUR structural branch points -- `census.py:160`,
`language.tier_for`, `lexer.declarations` on `doc_inside`, and `page_for` choosing a reader --
plus `paragraphs_stdlib` at 159 lines doing what `paragraphs_lexical` does in 375.
! `prove_unchanged` carries the SAME dependency:
`ast.dump(_blank_docstrings(ast.parse(text)))` for Python and stripped text for everything
else.

**R8 -- WHAT THE AST ACTUALLY BUYS**, stated so the trade is not one-sided. (1) A
triple-quoted string at the head of a body IS a docstring and one elsewhere is a bare
expression -- position alone cannot tell them apart. (2) WHERE THE BODY STARTS, which a
wrapped signature moves several lines down. (3) `prove_unchanged`'s statement-order
fingerprint, which ignores docstring CONTENT while keeping its PRESENCE. Each has to be
answered lexically or knowingly given up.

**R9 -- THE TRADE.** Dropping the AST puts Python on the lexical tier beside the other sixteen
-- one reader, every rule written once, and the `tokenized` tier either empties or disappears.
It also gives up the three answers above, and `a` placement for Python becomes a
keyword-and-position question like every other language's.

**R10 -- A THIRD MEASURE OF CORRECTNESS ARRIVED WITH THIS**, ruled by Roy the same day:
*"out ~= in if out.replace('\\n', '') == in.replace('\\n', '')"* -- a run of the project's own
formatter settles the rest. MEASURED over 3,082 files: 3,049 byte-identical, 3,075 identical
ignoring newlines, and 7 differing in more than newlines. It is what separates a spacing
question from a defect.

**R11 -- `prove_unchanged` CARRIES THE SAME DEPENDENCY AND IS NOT IN THE LEXER.** It
fingerprints Python as `ast.dump(_blank_docstrings(ast.parse(text)))` and everything else as
stripped text. That is the CODE CHECK -- what `addresser.py` calls the thing that *"MAKES it
constant across this tool's own work"* -- so the whole addressing scheme rests on it. Dropping
the AST from the reader leaves it standing there unanswered. ! A candidate answer arrived the
same day: the compositor sets code from the `c` places' anchors, so "the code is unchanged"
could become "every `c` anchor is unchanged" -- stronger than an `ast.dump`, and
language-independent.

**R12 -- THE TEST SUITE IS 4:1 PYTHON**, so it barely covers the path Python would move ONTO.
MEASURED 2026-08-21: 456 references to a `.py` path against 115 to a lexical language, and one
fixture each for `.go`, `.rb` and `.rs`. ! THAT IS BOTH THE RISK AND THE PAYOFF -- the suite
today exercises the reader that works and not the one where 157 collisions lived, and the
moment Python moves, all 456 assertions become coverage of the path that has the bugs.

**R13 -- NO HOLE IN THE LEXER CONTRACT**, checked 2026-08-21 when Roy asked. Its output shape
is pinned and the ORACLE now exists: `compositor.identity` over 2,399 Python files, plus
`lossless` and the newline-insensitive measure. A replacement reader has to reproduce 2,368
byte-identical round trips. ! Before this day there was no way to check that a reader change
preserved anything at all.

**R14 -- SCOPE, ruled by Roy 2026-08-21:** *"the python thing ends up with its own branch once
we merge this branch back to the 0.2.4 branch. It doesn't depend on the folio system being
correct or the lexer or page or census."* It may touch the lexer only to document edge cases.

**R15 -- FOUR AST DEPENDENCIES, AND THREE ARE OUTSIDE THE LEXER.** MEASURED 2026-08-21:
`lexer` (paragraphs and declarations), `prove_unchanged` (the CODE CHECK fingerprint),
`census` (the name corpus, `ast.parse` at line 165), and `referrers` (which files name a
symbol). Every one of them fails on syntax newer than the floor, so the same four files break
all four.

**R16 -- ONLY THE LEXER AND THE COMPOSITOR MAY INTERPRET A FILE**, and three of these do it
anyway. Roy, 2026-08-21: *"lexer and compositor are the things that are reading files."*
! THE TEST IS NOT `read_text` -- the LEXER READS ZERO FILES, it takes `text` as a parameter,
and `census` is what hands it one. The line is who INTERPRETS the content, and `ast.parse`
outside the lexer is interpretation.

**R17 -- `census.py` NAMES ITS OWN GAP ALREADY:** *"Liveness in these languages needs its own
harvester; the gap until there is one."* Its harvest is Python-only, so the name corpus a
reviewer checks a cited symbol against exists for one language of seventeen -- and vanishes
for a Python file the floor cannot parse.

**R18 -- THE ADDRESSER DESCRIBES A MECHANISM IT NEVER TOUCHES.** It has NO `import ast` and no
call; two paragraphs of its module docstring explain `ast.dump` and `_blank_docstrings`, which
live in `prove_unchanged`. ! Roy, 2026-08-21, on why: *"when it was addresser a long time ago
that kind of made sense."* Addressing was the subject then, and the code check is what makes
an address constant. The rename to `addresser` left prose two modules from the code it
describes, with nothing able to check it -- which is the obituary class `block-context` is
chartered to catch, shipping inside the tool that catches it.

**R19 -- RULED 2026-08-21, THE CODE CHECK BELONGS TO THE COMPOSITOR.** Roy: *"that check if it
was actually possible should live in compositor since before and after are in some ways its
job to verify."* The compositor PRODUCES the after, and every question it already answers is a
before/after one -- `identity` asks whether an unchanged page sets back byte for byte,
`lossless` whether any line was lost. *Did the code survive* is the same question at the same
seam.

**R20 -- IT ALSO ANSWERS THE AST PROBLEM RATHER THAN MOVING IT.** `prove_unchanged`
fingerprints Python with `ast.dump(_blank_docstrings(ast.parse(text)))`, which fails on syntax
newer than the floor. In the compositor the check has the PAGE, whose `c` places hold every
line of code verbatim -- so *the code is unchanged* becomes *every `c` anchor is unchanged*.
No parser, one rule for seventeen languages, and stronger than an `ast.dump`, which compares
statements and their order rather than the characters.

**R21 -- AND IT PUTS THE PROSE BACK BESIDE THE CODE IT DESCRIBES.** `addresser.py` carries two
paragraphs explaining `ast.dump` and `_blank_docstrings` and imports neither -- Roy: *"when it
was addresser a long time ago that kind of made sense."* Addressing was the subject then and
the code check is what makes an address constant. Moving the check to the compositor leaves
the addresser free to say what it does, and the explanation lands where a reader can check it.

**R22 -- IT CARRIES `a-closing-quote-with-a-comment` WITH IT, FOR FREE.** CHECKED 2026-08-21:
read through `paragraphs_lexical` with `"""` as a delimiter, the numpy shape yields ONE
paragraph and line 5 is owned ONCE -- the `# NOQA` rides along on the closing line as part of
the run. A reader that cuts at the delimiter has no second half to reconcile, so that defect
is gone by construction rather than fixed.

**R23 -- WHAT THIS BRANCH ACTUALLY OWES IS THE POSITION RULE**, and it is the third of the
three things listed above. `"""` is BOTH Python's string quote and its doc delimiter: the row
lists it under `spanning_quotes`, and `_strip_strings` blanks a spanning quote BEFORE the
comment-opener test -- by design, so a `//` inside a string cannot open a comment. So a
docstring is a STRING IN A PARTICULAR POSITION, and stating that position is what replaces the
parser.

**R24 -- PROPOSED 2026-08-22 (Roy): THE ANCHORS MAY NEED THEIR DEPTH.** The position rule this
branch owes -- a docstring is a STRING IN A PARTICULAR POSITION -- is a rule about DEPTH once
there is no parser. MEASURED 2026-08-22: an anchor already holds its line VERBATIM WITH ITS
INDENTATION (a2 is "    def m(self):" at 4, c2 is "        x = 1" at 8), so depth is DERIVABLE
from every place today and STATED by none. ! It answers TWO of the three things the AST buys:
WHERE THE BODY STARTS is the first anchor deeper than the declaration, which a wrapped
signature no longer moves, and INSIDE THIS BODY is depth greater than the declaration.
! NECESSARY, NOT SUFFICIENT: on the same fixture `y = """not a docstring"""` sits at depth 8
like every other line of that body, so depth says WHICH BODY and the walk order says FIRST --
the pair replaces `ast.get_docstring`, not depth alone.

**R25 -- DEFERRED HERE BY TRANSITIVITY**, Roy 2026-08-22: *"to make python capable of being
read correctly we are going to have to do this ... the fix to one will fix the other."* MAKE
`_strip_strings` STATEFUL -- carry open-quote state across lines instead of reading each line
alone. It is the same reader: triple-quote is Python's doc delimiter AND a spanning quote, so
whatever computes parity for one computes it for the other.

**R26 -- THE COST OF NOT HAVING IT**, MEASURED 2026-08-22 by a code review and reproduced
here: `prove_unchanged` refuses a file on the PRESENCE of a spanning delimiter, because parity
is what a per-line reader cannot compute -- its own words, *a proof that refuses costs a
report; a proof that lies costs the claim*. TEN languages declared none, so the refusal never
fired and the gate LIED instead: an edit made INSIDE a Rust string literal reported PROVEN at
exit 0, fingerprints identical. That is the stage 7b gate failing open.

**R27 -- FOUR ROWS WERE FIXED THE SAME DAY AND FOUR WERE NOT**, and the split is why this work
exists. Go raw-string backtick, Ruby heredoc, Lua long-bracket and TOML triple-quote are
DISTINCTIVE delimiters, so declaring them costs almost nothing. `rust`, `shell`, `sql` and the
C++ raw string use the ordinary double and single quote, which appear in nearly every file --
declaring those is CORRECT by the rule and makes Rust effectively unprovable. A stateful
reader is what removes the choice between refusing everything and lying sometimes.

**R28 -- THE ARGUMENT LISP MAKES**, because it separates two properties this repo has been
treating as one. `CLAUDE.md` says *only Python's doc sits INSIDE the declaration, so Python
alone needs a parser to say WHERE the prose goes*. Emacs Lisp has the SAME shape -- the
docstring is a string member of the `defun` form, not a run above it -- and needs NO parser to
find it: it is the third element of a balanced-paren form, and S-expressions lex trivially.
! SO `doc_inside` IS NOT WHAT COSTS US. What costs us is that Python's grammar is hard to lex
and a wrapped signature moves where the body starts. A Lisp row would be `doc_inside=True` and
still be a data row. ! Consequence: the lexical reader does not have to give up `doc_inside`
to give up the AST -- it has to find a body start without one, which is a narrower problem
than the sentence in `CLAUDE.md` implies. ! Not a request for a Lisp row; there is none, and a
`.el` file is named and refused today (verified 2026-08-22).

**R29 -- PEP 701 PUTS A COMMENT INSIDE AN F-STRING**, and the lexical reader calls it prose.
MEASURED 2026-08-22 on a three-line file: a multi-line f-string whose expression holds a `#`
comment (legal since Python 3.12) censuses at the LEXICAL tier as a `trailing-comment`, handed
to four reviewers as text they may rewrite -- into the middle of a string literal. ! NOT
REACHABLE TODAY: the AST tier owns Python, and on the 3.11 floor that file is a `SyntaxError`,
so it degrades to one `unparsed` paragraph and is refused. IT BECOMES LIVE THE MOMENT THIS
TODO LANDS, because moving Python to the lexical tier is the whole proposal. ! AND IT IS WHY
THE `python is hard to parse` FRAMING IS BACKWARDS. Python's GRAMMAR is clean -- PEG since
3.9, widely re-implemented, far easier than C++ or Perl. What is hard is LEXING it, which is
the only thing this tool does: indentation is semantic and needs a stack, triple quotes span
lines, and since 3.12 an f-string nests arbitrarily and may contain both quotes of its own
delimiter and comments. A per-line reader with no state cannot see any of the three. ! Same
root as R25 -- an f-string is the case where parity alone is not enough, because the nesting
is unbounded.

**R30 -- AND THE WRITE SIDE IS WORSE THAN THE READ SIDE**, because a misread is visible and a
miswrite is not. Reading Python lexically means nothing knows WHERE A BODY STARTS -- that is
what `doc_inside` needs and what a wrapped signature moves -- so the compositor cannot place
an `a` paragraph from the cues alone. ! A `patch` to a docstring then sets prose at a position
derived from a reader that could not see the body, and an `add` to an empty `a` has no
position at all. ! THE FAILING SHAPE IS ALREADY KNOWN: a comment inside a PEP 701 f-string
reads as a `trailing-comment`, so its `c` place is BESIDE a line that is really inside a
literal, and setting it lays the text into the string. ! `prove_unchanged` catches that one on
Python only when it can parse the file -- and the files where this arises are exactly the ones
the floor interpreter cannot parse, so the gate returns `unprovable` and the check that would
catch it is the check that abstains. ! WHATEVER REPLACES THE AST MUST ANSWER `where does this
body start`, or the `a` series has to stop being settable for Python.

**R31 -- THE CHECK FOR THE STATEFUL READER**, so the fix has something to be measured against
rather than reasoned about. `_strip_strings` re-initialises its quote state on EVERY PHYSICAL
LINE, so no literal crosses a newline and the INTERIOR of a multi-line literal is censused as
prose. MEASURED 2026-08-22, three languages, three lines each -- a Java text block, a Go raw
string, a C# verbatim string, each holding one line that begins with that language's comment
marker. Every one came back as `b1 comment`, handed to four reviewers as prose they may
rewrite, INTO THE MIDDLE OF A STRING. The reviewer's sweep found the same leak in go, cpp,
csharp, java, kotlin, swift, js, ts, ruby, shell, lua and toml -- twelve of eighteen rows, all
at exit 0. ! WHEN THE READER BECOMES STATEFUL, THIS IS THE CHECK: none of those files may
yield a prose paragraph whose text is the literal's interior. ! AND `spanning_quotes` DOES NOT
COVER IT. That field is read by exactly ONE consumer, `prove_unchanged`, which REFUSES such a
file -- so the 7b proof is safe and the CENSUS is not. The refusal protects the proof, never
the review, and nothing today protects the review.

## Tasks

- [x] T1 -- RECORD R1: the floor is a hard constraint and the language keeps moving.
- [x] T2 -- RECORD R2: an unparsed page sets as an empty file.
- [x] T3 -- RECORD R3: two readers means every rule is written twice.
- [x] T4 -- RECORD R4: the matter type, written in `paragraphs_lexical` alone.
- [x] T5 -- RECORD R5: the delimiter flush, and Python's correctness hiding it.
- [x] T6 -- RECORD R6: `_is_doc` computed inline in `flush`, re-derived in `carry`.
- [x] T7 -- RECORD R7: the measured surface -- four structural branch points.
- [x] T8 -- RECORD R8: what the AST actually buys.
- [x] T9 -- RECORD R9: the trade, put on the table.
- [x] T10 -- RECORD R10: the third measure of correctness, `out ~= in`.
- [x] T11 -- RECORD R11: `prove_unchanged` carries the same dependency, outside the lexer.
- [x] T12 -- RECORD R12: the suite is 4:1 Python -- the risk and the payoff.
- [x] T13 -- RECORD R13: no hole in the lexer contract; the oracle now exists.
- [x] T14 -- RECORD R14: scope, ruled by Roy 2026-08-21.
- [x] T15 -- RECORD R15: four AST dependencies, three outside the lexer.
- [x] T16 -- RECORD R16: only the lexer and the compositor may interpret a file.
- [x] T17 -- RECORD R17: `census.py` names its own gap already.
- [x] T18 -- RECORD R18: the addresser describes a mechanism it never touches.
- [x] T19 -- RECORD R19: ruled -- the code check belongs to the compositor.
- [x] T20 -- RECORD R20: it answers the AST problem rather than moving it.
- [x] T21 -- RECORD R21: it puts the prose back beside the code it describes.
- [x] T22 -- RECORD R22: it carries `a-closing-quote-with-a-comment` with it, for free.
- [x] T23 -- RECORD R23: what this branch owes is the position rule.
- [x] T24 -- RECORD R24: the anchors may need their depth.
- [x] T25 -- RECORD R25: make `_strip_strings` stateful, deferred here by transitivity.
- [x] T26 -- RECORD R26: the cost of not having it -- the 7b gate failing open.
- [x] T27 -- RECORD R27: four rows fixed the same day and four not.
- [x] T28 -- RECORD R28: the argument Lisp makes.
- [x] T29 -- RECORD R29: PEP 701 puts a comment inside an f-string.
- [x] T30 -- RECORD R30: the write side is worse than the read side.
- [x] T31 -- RECORD R31: the check for the stateful reader.
- [ ] T32 -- Read Python on the lexical tier -- no `import ast` in the lexer. Verify:
      `grep -rn 'import ast' plugins/` misses lexer.py:28 and a `.py` file still censuses.
- [ ] T33 -- Hold the round-trip identity over the Python corpora with the new reader.
      Verify: `compositor.identity` reproduces R13's 2,368 byte-identical round trips.
- [ ] T34 -- A file with syntax NEWER than the floor censuses instead of setting empty.
      Verify: sentry's `api/paginator.py` yields places and sets back its 884 lines.
- [ ] T35 -- Drop the `ast` proof; run `stripped` for every language, Python included.
      Verify: `grep -n 'import ast' prove_unchanged.py` is empty (it reads it at :36).
- [ ] T36 -- Keep the Python fixtures passing under the `stripped` proof. Verify: `uv run
      python -m unittest discover -s tests -k prove_unchanged` is green.
- [ ] T37 -- Say in `prove_unchanged`'s docstring what `stripped` does NOT cover. Verify:
      the docstring claims same lines in the same order, never semantic equivalence.
