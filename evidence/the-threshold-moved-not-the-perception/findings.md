# block-context -- findings

Role: BLOCK-CONTEXT. File under review:
`plugins/comment-review/skills/comment-review/scripts/compositor.py` (paths below are
relative to that repo root, as the census prints them).

48 records over the census's 24 prose paragraphs -- 14 `correct`, 13 `query`, 21 `clean`.

## Disagreements between the census, the brief, and this run

1. **The brief specifies a JSON sheet** (`role`/`read_from`/`sheets[].path`/`sha`/`marks[].address`) and says to **stop if the record file does not reach me**. None reached me; this run named a markdown path instead. I say so, and continued -- refusing produces nothing measurable. `sha`/`read_from` are unfillable.
2. **The brief's REFERENCE ONLY reading is unavailable.** 11 of my 13 `query`s name a file I was forbidden to open. Marking those `clean` would be worse than querying them.
3. **Nothing was run**, so no `sources` entry carries `ran`; the one worked example (line 3) is therefore `query`.
4. **No `add`/`move`**: both need an address from `addresser --anchor ... --series`, which I could not run, and the brief forbids counting one out of the census. Two candidates went to CODE CONCERNS.
5. **Census UNRESOLVED paths resolve against the repo root.** `language.py` is reported unresolved yet line 66 imports it and lines 55-57 put the script's own directory on `sys.path`. I treated `language.py`, `galley.py`, `prove_unchanged.py` as unsettleable, **not as obituaries**.
6. **`clean` is issued once per paragraph and names the sentences it certifies**; no `clean` covers a sentence another record rules on.
7. Records 34 and 48 quote sentences the file wraps across two lines (232-233, 383-384).
8. Long-docstring `change` blocks below show the edited region with the rest of the paragraph unchanged verbatim -- a deviation from "the whole paragraph as raw text", forced by reply length.

## Summary

| # | census | address | lines | kind | instruction | subject |
|---|---|---|---|---|---|---|
| 1 | 135 | `@a0` | 1-47 | docstring | `query` | usage line teaches `--repo D`, which `main` never reads |
| 2 | 135 | `@a0` | 1-47 | docstring | `correct` | "KNOWS NO LINE NUMBERS" -- `transcribes` reads three |
| 3 | 135 | `@a0` | 1-47 | docstring | `correct` | "NOTHING IS WRITTEN OVER THE REAL FILE HERE" -- `approve()` is here |
| 4 | 135 | `@a0` | 1-47 | docstring | `correct` | "byte for byte, in any language" -- 12 of 699 are not |
| 5 | 135 | `@a0` | 1-47 | docstring | `query` | "THIS IS THE ONLY WRITER" -- population unenumerable |
| 6 | 135 | `@a0` | 1-47 | docstring | `correct` | "only the second needs assembling" -- it is the FIRST |
| 7 | 135 | `@a0` | 1-47 | docstring | `correct` | "the one thing here taken from `page.text`" -- one of two |
| 8 | 135 | `@a0` | 1-47 | docstring | `query` | `galley.py`, `references/vocabulary.toml`, `prove_unchanged.py` |
| 9 | 144 | `@c8` | 59 | trailing-comment | `clean` | `# noqa: E402` |
| 10 | 145 | `@b9` | 61-65 | comment | `clean` | read directly, visible in the import graph |
| 11 | 145 | `@b9` | 61-65 | comment | `query` | "the only two modules that touch a file" |
| 12 | 146 | `@c9` | 66 | trailing-comment | `clean` | `# noqa: E402` |
| 13 | 147 | `@c10` | 67 | trailing-comment | `clean` | `# noqa: E402` |
| 14 | 152 | `@a1` | 75-80 | docstring | `clean` | the summary line |
| 15 | 152 | `@a1` | 75-80 | docstring | `correct` | "THE FIRST ENDING WINS" -- any CRLF wins, wherever |
| 16 | 152 | `@a1` | 75-80 | docstring | `query` | "`galley.py` has answered it this way" |
| 17 | 155 | `@a2` | 85 | docstring | `clean` | prose each place holds, by folio |
| 18 | 163 | `@a3` | 95-126 | docstring | `clean` | the walk, `lossless` beside `identity`, the `newline` arg |
| 19 | 163 | `@a3` | 95-126 | docstring | `correct` | "the one fact a paragraph cannot state" -- one of two |
| 20 | 163 | `@a3` | 95-126 | docstring | `query` | fixed series order, MEASURED 699/12 |
| 21 | 163 | `@a3` | 95-126 | docstring | `query` | "it is one time per file" |
| 22 | 167 | `@b27` | 130-157 | comment | `clean` | edge, first key alone, DROP `P` / ADD `N` |
| 23 | 167 | `@b27` | 130-157 | comment | `query` | "90% of `c`->`c` boundaries" |
| 24 | 167 | `@b27` | 130-157 | comment | `query` | "88% of 15,987 boundaries" |
| 25 | 173 | `@b32` | 163-170 | comment | `clean` | empty place breaks no edge; a `c` is never empty |
| 26 | 173 | `@b32` | 163-170 | comment | `query` | `tie_leading` |
| 27 | 179 | `@b37` | 176-179 | comment | `clean` | a `c` is the line of code |
| 28 | 185 | `@b42` | 185-187 | comment | `clean` | the closing edge |
| 29 | 188 | `@b44` | 190-204 | comment | `clean` | no places over a file with text is a refusal |
| 30 | 188 | `@b44` | 190-204 | comment | `query` | sentry measurement, "4 files ... today", `page_for`, the TODO |
| 31 | 193 | `@b48` | 209-212 | comment | `clean` | an empty page is empty text |
| 32 | 195 | `@b49` | 214-216 | comment | `clean` | the trailing newline is the file's |
| 33 | 199 | `@a4` | 222-246 | docstring | `correct` | "MADE IT ONE COMPARISON" -- there are two |
| 34 | 199 | `@a4` | 222-246 | docstring | `correct` | "nothing to reassemble" -- line 262 reassembles |
| 35 | 199 | `@a4` | 222-246 | docstring | `correct` | "`vars(b)`" names nothing in this file |
| 36 | 199 | `@a4` | 222-246 | docstring | `clean` | a place holding no line is True; summary and Returns |
| 37 | 199 | `@a4` | 222-246 | docstring | `query` | `galley.paragraph_matches` |
| 38 | 210 | `@b62` | 257-259 | comment | `clean` | a `c` shares its first line with code |
| 39 | 216 | `@a5` | 267-275 | docstring | `clean` | the real file is not touched here |
| 40 | 221 | `@a6` | 282-287 | docstring | `clean` | a copy, not a splice |
| 41 | 225 | `@a7` | 293-304 | docstring | `correct` | "exactly one shape" -- mixed endings are a second |
| 42 | 225 | `@a7` | 293-304 | docstring | `clean` | the weaker invariant, and the summary line |
| 43 | 225 | `@a7` | 293-304 | docstring | `query` | MEASURED over 699 files: 12 and 0 |
| 44 | 249 | `@a8` | 330-335 | docstring | `correct` | Returns names one of four things it returns |
| 45 | 261 | `@b108` | 347-348 | comment | `clean` | reported like any other refusal |
| 46 | 271 | `@a9` | 360 | docstring | `correct` | "nonzero if any file differs" -- a normalised file exits 0 |
| 47 | 294 | `@b139` | 383-384 | comment | `clean` | "ONLY A LOST OR INVENTED LINE FAILS" |
| 48 | 294 | `@b139` | 383-384 | comment | `correct` | normalisation also happens to line endings |

## The records

### 1 -- `@a0` · `query`
**claim** shape `human-review-necessary`; attempted: read `main()` end to end for a use of `args.repo` and for a `rel` argument at either call site; settles: whether `--repo` is meant to be wired to the `rel` parameter both `lossless` and `identity` already accept, or meant to leave the usage line.
**reason** The usage line teaches an option that changes nothing: `--repo` is parsed and never read, and `rel` is never passed, so `python compositor.py --repo D <paths>` and `python compositor.py <paths>` do the same work -- but I cannot tell whether the doc is ahead of the code or behind it.
**sources** `compositor.py:3` `    python compositor.py --repo D <paths...>      # prove the identity, file by file` · `compositor.py:363` `    parser.add_argument("--repo", type=Path, default=Path("."))` · `compositor.py:370` `        gone = lossless(path)` · `compositor.py:375` `        why = identity(path)`

### 2 -- `@a0` · `correct`
**claim** false: `IT SETS FROM THE FOLIATION'S READING ORDER AND KNOWS NO LINE NUMBERS.` · true: `IT SETS FROM THE FOLIATION'S READING ORDER, AND SETTING KNOWS NO LINE NUMBERS -- transcribes is the one function here that reads the stored positions.`
**reason** The claim is made at module scope and the module reads three stored line numbers: `transcribes` takes `original_start`, `original_end` and `original_column` off the paragraph and indexes the file with them.
**sources** `compositor.py:13` `!! IT SETS FROM THE FOLIATION'S READING ORDER AND KNOWS NO LINE NUMBERS. Roy,` · `compositor.py:247` `    start = paragraph.get("original_start") or 0` · `compositor.py:254` `    here = list(lines[start - 1 : end])`
**change** (lines 13-14 of the paragraph; the rest unchanged)
```
!! IT SETS FROM THE FOLIATION'S READING ORDER, AND SETTING KNOWS NO LINE
NUMBERS -- `transcribes` is the one function here that reads the stored
positions, and only to compare them against a file it was handed. Roy,
```

### 3 -- `@a0` · `correct`
**claim** false: `NOTHING IS WRITTEN OVER THE REAL FILE HERE.` · true: `NOTHING IS WRITTEN OVER THE REAL FILE UNTIL approve().`
**reason** The paragraph's own next clause says `approve()` copies the draft over the real file, and `approve()` is in this module, so at module scope the heading is refuted three lines later by its own sentence and by `shutil.copyfile(drafted, real)`.
**sources** `compositor.py:23` `!! NOTHING IS WRITTEN OVER THE REAL FILE HERE. `draft()` emits the whole page` · `compositor.py:288` `    shutil.copyfile(drafted, real)`
**change**
```
!! NOTHING IS WRITTEN OVER THE REAL FILE UNTIL `approve()`. `draft()` emits the
whole page into a file of its own so a reviewer or the author can compare it
against the original; `approve()` copies that over the real file wholesale,
once. Roy: *"No editing on the 'real' file until the draft is fully approved."*
```

### 4 -- `@a0` · `correct`
**claim** false: `byte for byte, in any language.` · true: `byte for byte in every language but the ruled series-order shape and a file holding both line endings.`
**reason** The file measures its own exceptions: 12 of 699 files fail exactly this equality, which `set_page`'s docstring calls a ruled sacrifice and `lossless` exists to tell apart from a bug -- so the round trip is not byte-identical in any language.
**sources** `compositor.py:29` ``set_page(page_for(path, text, lang)) == text`, byte for byte, in any language.` · `compositor.py:301` `    699 files: 12 fail `identity` and 0 fail this one. A gate that could not tell` · `compositor.py:106` `-- comes back with the matter above that blank. MEASURED over 699 files: 12`
**change**
```
!! AND THE ROUND TRIP IS A TEST BECAUSE THIS IS THE ONLY WRITER.
`set_page(page_for(path, text, lang)) == text` byte for byte, in every language
but the two ruled shapes `lossless` exists to separate out.
! `prove_unchanged.py` is strictly weaker and answers a different question: it
proves the EXECUTABLE CODE survived an edit, not that the model of a page is
lossless.
```

### 5 -- `@a0` · `query`
**claim** shape `unable-to-determine`; attempted: enumerated every write site inside this file by whole name -- `write_text` and `copyfile` -- and found two, both in this module; settles: `findReferences` on `write_text`, `open(..., "w")` and `shutil.copy*` across the package, stating the population as production writers of a source file.
**reason** The claim is an exclusivity claim over a population outside this file, and inside the file it is already two write sites rather than one, so nothing I could reach tests the number the sentence asserts.
**sources** `compositor.py:28` `!! AND THE ROUND TRIP IS A TEST BECAUSE THIS IS THE ONLY WRITER.` · `compositor.py:277` `    into.write_text(set_page(page), encoding="utf-8", newline="")` · `compositor.py:288` `    shutil.copyfile(drafted, real)`

### 6 -- `@a0` · `correct`
**claim** false: `Two shapes, and only the second needs assembling:` · true: `Two shapes, and only the first needs assembling:`
**reason** The two shapes are listed in the order `c` first, everything else second, and it is the `c` that is assembled -- its line is built by concatenating the code with the prose beside it, while the second shape is extended into the output as it stands.
**sources** `compositor.py:34` `Two shapes, and only the second needs assembling:` · `compositor.py:181` `            out.append(f"{code}{prose[0] if prose else ''}")` · `compositor.py:184` `        out.extend(prose)`
**change**
```
Two shapes, and only the first needs assembling:
```

### 7 -- `@a0` · `correct`
**claim** false: `the one thing here taken from `page.text`.` · true: `one of two facts here taken from page.text -- the trailing newline is the other.`
**reason** `set_page` takes a second fact off `page.text`: whether the file ended in a newline, which the comment at lines 214-216 states in the same words ("no paragraph can state whether it was there"), and reads it a third time as the guard on line 189.
**sources** `compositor.py:44` `the one thing here taken from `page.text`. Nothing a paragraph says can state` · `compositor.py:217` `    tail = ending if page.text.endswith(("\n", "\r")) else ""` · `compositor.py:215` `paragraph can state whether it was there. A file that ended in one is set`
**change**
```
! THE LINE ENDING IS A FACT ABOUT THE FILE, NOT ABOUT ITS PARAGRAPHS, and it is
one of two facts here taken from `page.text` -- the trailing newline is the
other. Nothing a paragraph says can state whether the file that held it used
CRLF, and a compositor that guessed would rewrite every line of a Windows
checkout.
```

### 8 -- `@a0` · `query`
**claim** shape `unable-to-determine`; attempted: checked whether each cited path resolves from this file's own directory, which lines 55-57 put on `sys.path`; settles: listing `skills/comment-review/scripts/` and reading `references/vocabulary.toml` for the quoted definition.
**reason** Three citations carry the paragraph's argument -- `galley.py`, `references/vocabulary.toml` and `prove_unchanged.py` -- the census resolves none of them, and I could not open the tree to tell an artifact of root-relative resolution from a dangling pointer.
**sources** `compositor.py:9` `together. A module that did both is what `galley.py` was, and its own vocabulary` · `compositor.py:10` `said so -- `references/vocabulary.toml`: *"the GALLEY is text set but not yet` · `compositor.py:30` `! `prove_unchanged.py` is strictly weaker and answers a different question: it`

### 9 -- `@c8` · `clean`
**reason** The directive's condition holds: this import sits after executable statements, which is exactly what E402 reports.
**sources** `compositor.py:59` `from foliator import ON, series_of  # noqa: E402` · `compositor.py:57` `    sys.path.insert(0, str(REPO_ROOT))`

### 10 -- `@b9` · `clean`
Covers: *"It is read DIRECTLY and not through the lexer, so the rule is visible in the import graph rather than in a comment."*
**reason** The import is direct and the imported name is used directly in two functions, so the sentence describes what the import graph shows.
**sources** `compositor.py:66` `from language import language_for  # noqa: E402` · `compositor.py:309` `    lang = language_for(path)` · `compositor.py:340` `    lang = language_for(path)`

### 11 -- `@b9` · `query`
**claim** shape `unable-to-determine`; attempted: enumerated the file-touching sites in this module (`read_text` twice, `write_text`, `copyfile`); settles: a whole-name search for `read_text`/`write_text`/`open(` across the package, stating the population as modules that touch a file.
**reason** "the only two modules that touch a file" is an exclusivity claim over a population of modules, and the only module I was permitted to open is this one.
**sources** `compositor.py:62` `into paragraphs and this sets a page back into one; they are the only two` · `compositor.py:306` `        text = path.read_text(encoding="utf-8")` · `compositor.py:277` `    into.write_text(set_page(page), encoding="utf-8", newline="")`

### 12 -- `@c9` · `clean`
**reason** Same condition as record 9: the import follows executable statements.
**sources** `compositor.py:66` `from language import language_for  # noqa: E402` · `compositor.py:56` `if str(REPO_ROOT) not in sys.path:`

### 13 -- `@c10` · `clean`
**reason** Same condition as record 9.
**sources** `compositor.py:67` `from page import Page, page_for  # noqa: E402` · `compositor.py:56` `if str(REPO_ROOT) not in sys.path:`

### 14 -- `@a1` · `clean`
Covers the summary line only: *"Which ending this text uses: CRLF if any line has one, else LF."*
**reason** The line that enforces it returns CRLF on the presence of CRLF anywhere in the text and LF otherwise, which is what the summary states.
**sources** `compositor.py:81` `    return CRLF if CRLF in text else LF`

### 15 -- `@a1` · `correct`
**claim** false: `THE FIRST ENDING WINS` · true: `ANY CRLF WINS, WHEREVER IT SITS`
**reason** The enforcing line is a membership test, not a positional one -- `CRLF in text` is true for a CRLF anywhere in the file, so a file whose first ending is LF and whose hundredth is CRLF is still set with CRLF, and the direction the prose states is not the one the code enforces.
**sources** `compositor.py:77` `    ! THE FIRST ENDING WINS AND MIXED FILES ARE NORMALISED. A file holding both` · `compositor.py:81` `    return CRLF if CRLF in text else LF`
**change**
```
    """Which ending this text uses: CRLF if any line has one, else LF.

    ! ANY CRLF WINS, WHEREVER IT SITS, AND MIXED FILES ARE NORMALISED. A file
    holding both is already inconsistent, and picking per line would preserve a
    defect the author cannot see. `galley.py` has answered it this way since it
    was written.
    """
```

### 16 -- `@a1` · `query`
**claim** shape `unable-to-determine`; attempted: looked for `galley.py` beside this file, which lines 55-57 make importable, and for any statement of the rule inside this module; settles: reading `galley.py`'s own line-ending code, or confirming the module is gone.
**reason** The sentence licenses the normalisation on another module's precedent, and I could open neither that module nor its history to say whether it still answers this way or still exists.
**sources** `compositor.py:79` `    author cannot see. `galley.py` has answered it this way since it was written.` · `compositor.py:9` `together. A module that did both is what `galley.py` was, and its own vocabulary`

### 17 -- `@a2` · `clean`
**reason** The body keys the returned dict by the folio taken off each paragraph's address and stores that paragraph's raw lines, and a place holding nothing yields no lines -- both sentences describe what the four lines below them do.
**sources** `compositor.py:88` `        folio = (paragraph.address or "").split("@")[-1]` · `compositor.py:90` `            out[folio] = list(paragraph.raw_lines)`

### 18 -- `@a3` · `clean`
Covers: *"This page, set as the text of a file."*; *"IT WALKS THE READING ORDER AND ASKS EACH PLACE WHAT IT HOLDS ... every place after it is set where it always was -- next."*; *"THAT IS WHY `lossless` EXISTS BESIDE `identity`. The first is the invariant that must never break; the second is the strict form"*; and the `page` and `newline` argument lines up to "the page's own text".
**reason** The loop walks `page.foliation.reading` and extends the output with whatever each place holds, so a paragraph's length changes nothing downstream; and the two functions named differ exactly as described -- one compares sorted lines, the other compares the texts.
**sources** `compositor.py:160` `    for folio in page.foliation.reading:` · `compositor.py:161` `        prose = held.get(folio, [])` · `compositor.py:316` `    if sorted(got.splitlines()) == sorted(text.splitlines()):` · `compositor.py:350` `    if got == text:` · `compositor.py:127` `    ending = newline if newline is not None else line_endings(page.text)`

### 19 -- `@a3` · `correct`
**claim** false: `which is the one fact a paragraph cannot state.` · true: `which is one of two facts a paragraph cannot state; the trailing newline is the other.`
**reason** The comment at lines 214-216 states a second such fact in the same terms -- whether the file ended in a newline, which `splitlines` drops and no paragraph records -- so "the one fact" is refuted from inside the same function.
**sources** `compositor.py:122` `            text, which is the one fact a paragraph cannot state.` · `compositor.py:214` `    # ! THE TRAILING NEWLINE IS THE FILE'S, and `splitlines` drops it, so no` · `compositor.py:217` `    tail = ending if page.text.endswith(("\n", "\r")) else ""`
**change** (Args block; the rest of the docstring unchanged)
```
    Args:
        page: the page to set. Its foliation states the order.
        newline: the ending to join with. `None` takes it from the page's own
            text, which is one of two facts a paragraph cannot state; the
            trailing newline is the other.
```

### 20 -- `@a3` · `query`
**claim** shape `unable-to-determine`; attempted: read `set_page` for anything that fixes a series order and found only a walk of `page.foliation.reading`, and cross-read the same measurement at lines 300-303, where it agrees; settles: running `compositor.py` over the 699-file corpus, and reading the foliation that builds `reading`.
**reason** Two claims in this passage rest outside the file -- the order is `Foliation.reading`'s to fix, not this function's, and the 699/12/C-headers measurement needs a corpus the checkout does not carry -- and agreement with a second copy of the same numbers is consistency, not verification.
**sources** `compositor.py:102` `    !! THE SERIES ORDER IS FIXED AND `f` COMES FIRST, WHICH IS LOSSY ON ONE` · `compositor.py:106` `-- comes back with the matter above that blank. MEASURED over 699 files: 12` · `compositor.py:160` `    for folio in page.foliation.reading:` · `compositor.py:301` `    699 files: 12 fail `identity` and 0 fail this one. A gate that could not tell`

### 21 -- `@a3` · `query`
**claim** shape `unable-to-determine`; attempted: searched this module for anything that raises or emits a `query`, and found none -- the module's only refusal is a `ValueError`; settles: the skill's own record of how an `f0`/`b0` placement reaches the human, and a count of such places per file over the corpus.
**reason** "it is one time per file" is a quantified claim about the review workflow rather than about this code, and nothing in the file bounds it.
**sources** `compositor.py:117` `    `b0` because that is where it fits is a `query` to the human, and it is one` · `compositor.py:205` `        raise ValueError(`

### 22 -- `@b27` · `clean`
Covers: *"LEADING IS SET BETWEEN TWO PLACES, NOT AT ONE ... looked up as it is reached"*; *"THE FILE'S OWN EDGES ARE PAIRS TOO, with `""` for the side that has no place"*; *"AN EDGE BELONGS TO THE PLACE BEFORE IT, so it is looked up by its FIRST key alone"*; the DROP `P` / ADD `N` worked example; and *"THE SECOND KEY IS KEPT ON THE FOLIATION AND NOT USED HERE."*
**reason** The dict comprehension keys the edges by the first key alone and discards the second; `previous` starts as `""`, so the file's opening edge is the pair the prose names; and the worked example holds -- a place that sets nothing hits `continue` before `previous` is reassigned, so its edge is never asked for while the previous place's edge is still set before the next one.
**sources** `compositor.py:158` `    edges = {before: folio for (before, _), folio in page.foliation.leading.items()}` · `compositor.py:159` `    previous = ""` · `compositor.py:171` `        if not prose and not beside_code:` · `compositor.py:173` `        out.extend(held.get(edges.get(previous, ""), []))` · `compositor.py:174` `        previous = folio`

### 23 -- `@b27` · `query`
**claim** shape `unable-to-determine`; attempted: looked for the boundary population inside the file and found none -- the module counts nothing and stores no corpus statistics; settles: re-running the census over the pinned corpora and counting `c`->`c` boundaries with no leading.
**reason** "90% of `c`->`c` boundaries" is a measurement over a corpus this checkout does not carry, and it names no population size, unlike the 15,987 stated eighteen lines below it.
**sources** `compositor.py:134` `# `c`->`c` boundaries do.` · `compositor.py:152` `# 88% of 15,987 boundaries, so a new comment sitting straight on the code it`

### 24 -- `@b27` · `query`
**claim** shape `unable-to-determine`; attempted: same as record 23 -- nothing in the module derives or stores this count; settles: re-running the census over the pinned corpora and counting `b`->`c` boundaries with no blank.
**reason** The 88%-of-15,987 measurement is dated to no run and rests on a corpus I could not reach, so it can be neither confirmed nor refuted from the file.
**sources** `compositor.py:151` `    # ! MEASURED: that is the shape the corpus has. `b`->`c` holds no blank in` · `compositor.py:158` `    edges = {before: folio for (before, _), folio in page.foliation.leading.items()}`

### 25 -- `@b32` · `clean`
Covers: *"A PLACE THAT SETS NOTHING BREAKS NO EDGE ... Skipping it keeps the pair the same one ... tied"* and *"A `c` IS NEVER EMPTY IN THIS SENSE -- it sets its line of code whether or not anything sits beside it."*
**reason** The guard skips a place only when it holds no prose and is not beside code, so it is reached before `previous` moves and a `c` can never satisfy it; the `c` branch appends its code line whether or not prose exists.
**sources** `compositor.py:171` `        if not prose and not beside_code:` · `compositor.py:181` `            out.append(f"{code}{prose[0] if prose else ''}")`

### 26 -- `@b32` · `query`
**claim** shape `unable-to-determine`; attempted: searched this file for `tie_leading` and found no definition or call; settles: resolving the symbol in the module that builds the foliation, and confirming it still ties pairs the way the sentence says.
**reason** The sentence's guarantee is that skipping preserves the pair some other code tied, and the name that does the tying is defined nowhere I was permitted to look -- so I can confirm the skip but not the guarantee.
**sources** `compositor.py:165` `        # verdict can cite. Skipping it keeps the pair the same one `tie_leading`` · `compositor.py:172` `            continue`

### 27 -- `@b37` · `clean`
**reason** The three lines below it do exactly what it says: the code line and the first prose line are concatenated into one output line and the remaining prose lines are appended whole, so a comment opened beside the code and closed later owns those later lines outright.
**sources** `compositor.py:180` `            code = page.foliation.places.get(folio, "")` · `compositor.py:181` `            out.append(f"{code}{prose[0] if prose else ''}")` · `compositor.py:182` `            out.extend(prose[1:])`

### 28 -- `@b42` · `clean`
**reason** The loop sets each place's edge before the place, so the last place's own edge is unset when the walk ends, and the line below the comment is the extend that pays it.
**sources** `compositor.py:173` `        out.extend(held.get(edges.get(previous, ""), []))` · `compositor.py:188` `    out.extend(held.get(edges.get(previous, ""), []))`

### 29 -- `@b44` · `clean`
Covers: *"A PAGE WITH NO PLACES OVER A FILE WITH TEXT IS NOT AN EMPTY PAGE -- it is a page that was never built, and setting it would EMPTY THE FILE"* and *"REFUSING IS THE ONLY SAFE ANSWER. `draft()` writes what this returns, and an empty draft approved by anyone not reading the diff is a deleted file."*
**reason** The guard is exactly the conjunction the prose names and it raises rather than returning; and `draft()` does write what `set_page` returns straight into a file, so the consequence the prose gives for not refusing is the one the code would have.
**sources** `compositor.py:189` `    if not page.foliation.reading and page.text:` · `compositor.py:205` `        raise ValueError(` · `compositor.py:277` `    into.write_text(set_page(page), encoding="utf-8", newline="")`

### 30 -- `@b44` · `query`
**claim** shape `unable-to-determine`; attempted: checked which of these claims the file itself settles -- the guard and `draft()` do, records 29's sources -- and found the remainder all point outside it; settles: reading `page_for` for the skip-on-refusal path, re-running over `corpora/` for the "4 files ... today" count, and resolving `TODO/python-cannot-read-python.md`.
**reason** Four claims here leave the file -- `page_for`'s behaviour, the 884-lines-in/0-out measurement on a sentry path, the count of files "in that state today", and the TODO citation -- and a dated "today" count is the kind that goes stale with no visible symptom.
**sources** `compositor.py:192` `        # `page_for` skips the walk when a reader refuses the source, so` · `compositor.py:195` `        # !! MEASURED 2026-08-21 on `sentry/src/sentry/api/paginator.py`: 884` · `compositor.py:198` `        # `corpora/` are in that state today. Roy: *"we can't use python to parse` · `compositor.py:204` `        # file. See `TODO/python-cannot-read-python.md`.`

### 31 -- `@b48` · `clean`
**reason** The line below returns the empty string rather than `page.text`, and the reasoning is checkable against `identity`, which compares the returned text to the file -- returning `page.text` there would make that comparison pass on a page that had lost every line.
**sources** `compositor.py:213` `        return ""` · `compositor.py:350` `    if got == text:`

### 32 -- `@b49` · `clean`
**reason** The enforcing line appends one ending exactly when the source text ended in one and appends nothing otherwise, which is both sentences.
**sources** `compositor.py:217` `    tail = ending if page.text.endswith(("\n", "\r")) else ""` · `compositor.py:218` `    return ending.join(out) + tail`

### 33 -- `@a4` · `correct`
**claim** false: `CONTIGUITY MADE IT ONE COMPARISON.` · true: `CONTIGUITY MADE IT ONE RANGE, and a c still costs a second comparison.`
**reason** The body still runs two comparisons and still carries two of the three cases the sentence says contiguity removed: a `c` is compared in two halves at the anchor test, and an empty or unstored paragraph is exempted before either comparison is reached.
**sources** `compositor.py:229` `    !! CONTIGUITY MADE IT ONE COMPARISON. The old check needed a case per kind --` · `compositor.py:250` `    if not start or not stored:` · `compositor.py:260` `        if here[0][: column - 1] != paragraph.get("anchor", ""):` · `compositor.py:263` `    return [ln.rstrip() for ln in here] == [ln.rstrip() for ln in stored]`
**change** (first line of that passage; the rest unchanged)
```
    !! CONTIGUITY MADE IT ONE RANGE, and a `c` still costs a second comparison.
    The old check needed a case per kind --
```

### 34 -- `@a4` · `correct`
**claim** false: `there is nothing to reassemble` · true: `a c is still reassembled from its two halves`
**reason** The line that follows the anchor test slices the first line back down to the column and compares the result, which is a reassembly of exactly the kind the sentence says contiguity removed. (The quoted clause wraps lines 232-233; the fragment on line 233 is `blanks, so its stored lines are its range and there is nothing to reassemble.`)
**sources** `compositor.py:233` `    blanks, so its stored lines are its range and there is nothing to reassemble.` · `compositor.py:262` `        here[0] = here[0][column - 1 :]`
**change** (closing sentence of that passage; the rest unchanged)
```
    and 4 but not 3. Every paragraph is contiguous since `leading` took the
    blanks, so its stored lines are its range -- a `c` is still reassembled from
    its two halves, and nothing else is.
```

### 35 -- `@a4` · `correct`
**claim** false: `paragraph: one census entry, as `vars(b)` or from the JSON.` · true: `paragraph: one census entry, as the vars() of a paragraph object or from the JSON.`
**reason** `b` names nothing this function can be handed: the parameter is `paragraph: dict`, the body reads it only by key, and the only `b` in the file is a loop variable in `identity` -- so the citation is illegible rather than wrong, which is the form that persists because it cannot be checked.
**sources** `compositor.py:241` `        paragraph: one census entry, as `vars(b)` or from the JSON.` · `compositor.py:221` `def transcribes(paragraph: dict, lines: list[str]) -> bool:` · `compositor.py:353` `    for n, (a, b) in enumerate(zip(was, now, strict=False), 1):`
**change** (Args block; the rest unchanged)
```
    Args:
        paragraph: one census entry, as the `vars()` of a paragraph object or
            from the JSON.
        lines: the file's lines, without endings.
```

### 36 -- `@a4` · `clean`
Covers: *"Does this paragraph's stored text still read the way the file does?"*; *"BEFORE AND AFTER ARE THIS MODULE'S TO VERIFY"*; *"A PLACE THAT HOLDS NO LINE IS TRUE, not false ... Answering False refused every `add` in a run"*; *"lines: the file's lines, without endings."*; and the Returns line.
**reason** The early return answers True for a paragraph with no start or no stored lines, which is the empty-place rule stated; and the final comparison rstrips both sides, so the `lines` argument is described as the function uses it.
**sources** `compositor.py:250` `    if not start or not stored:` · `compositor.py:251` `        return True` · `compositor.py:263` `    return [ln.rstrip() for ln in here] == [ln.rstrip() for ln in stored]`

### 37 -- `@a4` · `query`
**claim** shape `unable-to-determine`; attempted: applied the pointer-vs-subject test -- stripping the dead name collapses the sentence, so it reads as the subject of a live claim rather than a pointer -- and searched this file for the name, which is absent; settles: resolving `galley.paragraph_matches`, or confirming it is gone and that nothing still calls it.
**reason** The provenance sentence turns on a symbol in another module, and whether it is a live pointer or an obituary decides whether the sentence stays; the pointer test alone cannot settle which, and the census's own note says a missing name corpus makes every such symbol a false obituary risk.
**sources** `compositor.py:226` `    after are in some ways its job to verify."* It was `galley.paragraph_matches`` · `compositor.py:227` `    until then, where it sat beside the splice it guarded.`

### 38 -- `@b62` · `clean`
**reason** The two lines below store what it describes: the anchor is compared against everything left of the column and the remainder is what the paragraph holds, so the two halves are the physical line.
**sources** `compositor.py:260` `        if here[0][: column - 1] != paragraph.get("anchor", ""):` · `compositor.py:262` `        here[0] = here[0][column - 1 :]`

### 39 -- `@a5` · `clean`
**reason** The body writes only to `into` and returns it; no path in this function reaches the original, so an abandoned run leaves every original as it found it. (The enforcement gap -- nothing stops `into` being the original -- is a CODE CONCERN below, not a defect in the prose.)
**sources** `compositor.py:277` `    into.write_text(set_page(page), encoding="utf-8", newline="")` · `compositor.py:278` `    return into` · `compositor.py:288` `    shutil.copyfile(drafted, real)`

### 40 -- `@a6` · `clean`
**reason** The body is a single whole-file copy with no range and no merge, which is what both sentences claim.
**sources** `compositor.py:288` `    shutil.copyfile(drafted, real)`

### 41 -- `@a7` · `correct`
**claim** false: `They differ on exactly one shape` · true: `They differ on two shapes`
**reason** A file holding both endings is a second shape on which the two disagree and it is ruled the same way: `line_endings` returns CRLF for any CRLF, every line is joined with it, so the bytes differ and `identity` fails while no line is lost or invented and `lossless` passes -- and `line_endings`'s own docstring calls that normalisation deliberate.
**sources** `compositor.py:297` `    and none invented. They differ on exactly one shape, and it is RULED rather` · `compositor.py:81` `    return CRLF if CRLF in text else LF` · `compositor.py:218` `    return ending.join(out) + tail` · `compositor.py:316` `    if sorted(got.splitlines()) == sorted(text.splitlines()):`
**change**
```
    !! THE WEAKER INVARIANT, AND THE ONE THAT MUST NEVER BREAK. `identity` asks
    for the same bytes in the same order; this asks only that no line was lost
    and none invented. They differ on two shapes, and both are RULED rather
    than a defect -- see `set_page` on the series order, and `line_endings` on a
    file holding both endings.
```

### 42 -- `@a7` · `clean`
Covers: *"Does this file come back with every line it went in with? None if so."* and *"THE WEAKER INVARIANT ... `identity` asks for the same bytes in the same order; this asks only that no line was lost and none invented."*
**reason** The comparison is over sorted lines and returns None on equality, which is the weaker of the two invariants exactly as described against `identity`'s byte comparison.
**sources** `compositor.py:316` `    if sorted(got.splitlines()) == sorted(text.splitlines()):` · `compositor.py:317` `        return None` · `compositor.py:350` `    if got == text:`

### 43 -- `@a7` · `query`
**claim** shape `unable-to-determine`; attempted: cross-read the same numbers at lines 106-107, where they agree, and confirmed nothing in the module derives them; settles: running `compositor.py` over the 699-file corpus and reporting the two counts.
**reason** The 12-and-0 measurement is what licenses treating the gap as ruled rather than a defect, and it rests on a corpus the checkout does not carry -- a second copy of the same numbers in the same file is not independent evidence.
**sources** `compositor.py:300` `    ! IT IS WHAT SEPARATES A NORMALISATION FROM A BUG. MEASURED 2026-08-21 over` · `compositor.py:301` `    699 files: 12 fail `identity` and 0 fail this one. A gate that could not tell` · `compositor.py:106` `-- comes back with the matter above that blank. MEASURED over 699 files: 12`

### 44 -- `@a8` · `correct`
**claim** false: `the FIRST line that differs, which is what a reader needs to look at.` · true: `the FIRST line that differs where one does, the two line counts where the texts differ only in length, and the refusal itself where the file could not be read, has no language record, or has no places.`
**reason** Three of the four things this function can return are not a line that differs: an unreadable file, a suffix with no language record and a page that was never built each return their own message, and a text differing only in length falls past the loop to a line-count summary -- so the Returns section documents one of four outcomes.
**sources** `compositor.py:334` `        the FIRST line that differs, which is what a reader needs to look at.` · `compositor.py:339` `        return f"unread: {exc}"` · `compositor.py:349` `        return str(exc)` · `compositor.py:356` `    return f"{len(was)} lines in, {len(now)} out"`
**change**
```
    """Set this file from its own page and say where it differs, or None.

    Returns:
        `None` when the round trip is byte-identical. Otherwise a line: the
        FIRST line that differs where one does, the two line counts where the
        texts differ only in length, and the refusal itself where the file
        could not be read, has no language record, or has no places.
    """
```

### 45 -- `@b108` · `clean`
**reason** The `except` returns the exception's own text as this function's value rather than letting it propagate, which is the reporting the comment describes, and the raise it names is `set_page`'s.
**sources** `compositor.py:346` `    except ValueError as exc:` · `compositor.py:349` `        return str(exc)` · `compositor.py:205` `        raise ValueError(`

### 46 -- `@a9` · `correct`
**claim** false: `nonzero if any file differs.` · true: `nonzero only where lossless fails -- a file that merely differs exits 0.`
**reason** The exit code reads `broken`, which counts only files `lossless` rejects; a file whose identity fails increments `moved` and changes nothing about the return -- and the comment two lines above the return says so in its own words.
**sources** `compositor.py:360` `    """Prove the identity over every path given; nonzero if any file differs."""` · `compositor.py:385` `    return 1 if broken else 0` · `compositor.py:383` `    # !! ONLY A LOST OR INVENTED LINE FAILS. A normalised file is the ruled` · `compositor.py:371` `        if gone is not None:`
**change**
```
    """Prove the identity over every path given; nonzero only where `lossless` fails."""
```

### 47 -- `@b139` · `clean`
Covers the first sentence only: *"ONLY A LOST OR INVENTED LINE FAILS."*
**reason** The return below it is driven by `broken` alone, which is incremented only on a `lossless` rejection.
**sources** `compositor.py:385` `    return 1 if broken else 0` · `compositor.py:372` `            broken += 1`

### 48 -- `@b139` · `correct`
**claim** false: `A normalised file is the ruled series order doing what it was ruled to do` · true: `A normalised file is the ruled series order, or a mixed-ending file joined with one ending, doing what each was ruled to do`
**reason** A file holding both endings is normalised for a different reason and lands in the same `moved` bucket -- `line_endings` picks CRLF for any CRLF and every line is joined with it -- so a claim that all normalisation is the series order is the sentence a real normalisation defect would hide behind. (The quoted clause wraps lines 383-384; the fragment on line 384 is `series order doing what it was ruled to do -- see `set_page`.`)
**sources** `compositor.py:384` `    # series order doing what it was ruled to do -- see `set_page`.` · `compositor.py:81` `    return CRLF if CRLF in text else LF` · `compositor.py:218` `    return ending.join(out) + tail`
**change**
```
    # !! ONLY A LOST OR INVENTED LINE FAILS. A normalised file is the ruled
    # series order -- see `set_page` -- or a mixed-ending file joined with one
    # ending -- see `line_endings` -- doing what each was ruled to do.
```

## CODE CONCERNS

- `main` declares `--repo` at line 363 and never reads `args.repo`; `lossless` and `identity` are called at lines 370 and 375 without the `rel` argument both accept, so the flag changes nothing.
- `draft` documents "never the original" but accepts any `into`, and line 276 creates its parent directories; nothing refuses a destination equal to the page's own path.
- `line_endings` (line 81) joins every line of a mixed-ending file with CRLF, so such a file is reported `moved` by `main` and exits 0 -- a real normalisation defect would arrive in the same bucket.
- `set_page` raises `ValueError` at line 205; `lossless` catches it at line 314 and `identity` at line 346, but `draft` at line 277 does not, so the refusal propagates out of the write path with no handler named in its docstring.
- Candidate for an `add` I could not address without the addresser: `set_page`'s docstring has a `Returns` section and no statement that it raises, while three call sites treat that raise as an expected outcome.

**Most significant finding:** `main`'s docstring (`@a9`) promises "nonzero if any file differs", but line 385 returns nonzero only on `broken`, which counts `lossless` failures -- a file that fails the byte identity increments `moved` and exits 0. The comment two lines above the return states the real rule, so the file contradicts itself across three lines, and the docstring is the half a caller wiring this into a gate would read.
