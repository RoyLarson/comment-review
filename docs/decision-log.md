# comment-review -- Decision log

**What was decided, and when. The commentary on WHY lives in
[`docs/history.md`](history.md).** Roy, 2026-08-23: *"the explicit we decided it this way on this
day -- see history for commentary on why."* An entry here is a ruling, not an argument; if you
want the reasoning, follow the link.

**Read this before re-asserting anything that looks settled.** Several plausible-sounding claims
below were RETRACTED, and a session that re-derives them from priors will re-introduce a defect
that was already caught. A superseded ruling is kept beside the one that replaced it, never
rewritten away -- the same rule this repo applies to a TODO.

Every entry carries a number that is permanent **within its own `##` section** -- `#1`, `#2`,
`#3`... restarting at 1 for each section, assigned once, never reused, reordered or reassigned.
**A new entry goes at the BOTTOM of its section** and takes the next unused number in that
section. ! The counter is per-section and not global **because a global counter makes every git
diff illegible**: one new entry near the top would shift the number of every entry below it, in
every section, turning a one-line addition into a file-wide renumbering. Per-section numbering has
no cross-section coupling, and a citation never has to be reassigned.

**Citing an entry:** `decision-log.md TOPIC: #N`, where TOPIC is the exact `##` heading text.

! **This is the audit trail, not a second copy of the truth.** What is true NOW belongs in the
doc that owns it -- [`addressing.md`](addressing.md), [`vocabulary.md`](vocabulary.md),
[`gates.md`](gates.md) -- and in the code. This file says only what changed and on what day.

---

## Addressing

- **#1.** **An address is not a span of lines; a paragraph is just the lines that share one**
  (Roy, 2026-08-19). Replaced the line-numbered form `mod.py:1-24`, which is true of ONE file
  state while this tool edits prose and moves every line below each edit.

- **#2.** **The address is the full path from the runner's root, not the file name** (Roy,
  2026-08-18: *"the address is the full thing not just `__init__@b0`"*). Two complete paths differ
  somewhere; two file names need not. The root itself is never written -- it is implicit, the way
  a country is in a postal address (Roy, 2026-08-23).

- **#3.** **`addresser.py` became `foliator.py`** (Roy, 2026-08-20). **SUPERSEDED by #6.**

- **#4.** **Leading takes a SYMBOL and not a place** (Roy, 2026-08-22). A `d` has no anchor, so it
  cannot answer what every other place answers.

- **#5.** **Leading will not be given a place, and the attempt is closed** (Roy, 2026-08-23: *"We
  tried leading getting a place. We tried several different ways. The constraints of coding AND
  editing do not allow it."*). Tried three times -- `875b0d4`, `b998a60`, `c27ea1d`. Two things
  stop being determinable: where everything below an edit shifted to, and how much blank belongs
  where afterwards. ! **Unaddressed is not unrecorded**: `Page.leading` keys the fence on the
  place it follows, and the compositor puts it back exactly.

- **#6.** **`foliator.py` is an addresser again; #3 is superseded** (Roy, 2026-08-23: *"My
  frustration when I made the ruling was that it wasn't being used as an addresser ... the rest of
  the program continued working in trying to use lines as the address."*). #3 was right about the
  symptom and wrong about the cause -- the name promised addressing the system was not yet doing.

- **#7.** **The `@` half is a CUE. `path@cue`** (Roy, 2026-08-23: *"place was a good stand in but
  imprecise enough that we have had problems already"*). A cue carries no content, only the claim
  that content belongs here; the note carries content and not position.

- **#8.** **`foliator.py`'s docstring said "every line has exactly one address" and now says NO
  LINE HAS MORE THAN ONE** (2026-08-23). False by 595 lines in its own directory, every one a `d`.

- **#9.** **The census is a BINDER you ask, not a CLI that builds everything first** (Roy,
  2026-08-23: *"the census returns a binder -- a cli and ask for the census the page or some
  answer to some subpart of the page. It is silly to make the census be the cli it breaks things
  like this option"*). Asked as *shard the census per file, or not*, and ruled neither: the
  on-disk shape was never the problem. A lookup answers at one of three grains -- the whole
  census, one page, a subpart of a page -- and the chain stops as soon as the addresser can
  answer, *"No parse everything"*. ! While `census.py` IS the CLI, the only way to ask a small
  question is to run the thing that builds every page, so every question costs the whole project.
  MEASURED first: one address cost 0.28 s over 19 files, extrapolating to ~1.1 s and 250 MB read
  per lookup at 500k lines.

- **#10.** **A same-line docstring gets an `a`, becomes a `c` when Python goes lexical, and is
  set back on its own line** (Roy, 2026-08-23: *"gets an a but when the lexer type thing gets it
  in python it will end up as a c"*, and *"also on rewrite it will end up below the function def
  and that as fine"*). `def g(): """d."""` is legal Python and IS `g.__doc__`; today it censuses
  with an EMPTY address and `census.py` exits 1 on the whole file. ! **THE RULING NAMES A
  DESTINATION, NOT ONLY AN ANSWER.** A lexical reader sees a string beside code with no AST to
  say it is documentation, so the address moves `a1` -> `c` -- expected, not a regression.
  !! **AND SETTING IT BACK REWRITES A DECLARING LINE**, which is precisely what
  `prove_unchanged` exists to refuse; the move is ruled ALLOWED, which is not the same as
  invisible, so the proof needs a rule admitting this one transformation and nothing near it.

- **#11.** **A doc run is a docstring when a documentable declaration follows it, and a comment
  when nothing does** (Roy, 2026-08-23: *"That seems reasonable and likely that it will be
  generic."*). Raised on Lua's `---`, where 2,505 of 2,741 neovim declarations carry one and all
  read as undocumented; adding `---` to `doc_line` was tried and turned 4,230 comments into
  docstrings, breaking 8 files, because LuaLS writes `@class`/`@field` runs that document nothing.
  ! The alternative -- an exclude-list of `@`-tags -- fails on a run of `@param`/`@return` ABOVE a
  declaration, which carries no prose and is still that function's documentation.
  !! **IT MOVES THE LEXER FROM STRINGS TO PLACEMENT, WHICH IS ASSUMED TODAY AND NOT CHECKED**
  (Roy: *"The lexer looks at the strings and maybe some closing strings currently. It could/should
  look at placement but we have assumed placement currently."*) -- `_is_doc` reads the opener and
  the character after it and nothing else. ! **AND IT NEEDS OUTER AND INNER DOC OPENERS SPLIT PER
  ROW FIRST**: Rust declares `("///", "//!")` undifferentiated, and `//!` documents the ENCLOSING
  item, so a bare placement rule demotes a module's own doc to a comment.

- **#12.** **A census row carries SIX fields, and the page carries the rest** (Roy, 2026-08-24,
  field by field). The nineteen become `cue`, `anchor`, `anchor_num`, `original_start`,
  `original_end`, `raw_text`, under a page envelope naming `path` and the source SHA.

  | | ruling |
  | --- | --- |
  | `original_start`, `original_end` | **stay** -- *"they are the line numbers and the term original is defined intentionally"* |
  | `start`, `end` | **go.** A duplicate, and *"original has the definition and that makes it worth the extra tokens"* |
  | `anchor_num`, `anchor` | **stay.** Already ruled 2026-08-21, *"anchor_num along with anchor"* |
  | `anchor_line` | **goes.** `anchor_num` replaced it as the order in 2026-08-21 |
  | `raw_lines` -> `raw_text` | **stays, renamed, and becomes ONE STRING** -- *"the full thing not broken into separate lines, else it isn't raw text"* |
  | `text` | **goes.** A duplicate of the same prose in a second shape |
  | `address` -> `cue` | **reduced.** The page names the file, so the row need not |
  | `path` | **moves to the page envelope** |
  | `tier` | **goes.** Not necessary, and *"the parser tier isn't long for this world"* |
  | `lines` | **goes.** *"It is ambiguous"* |
  | `kind`, `annotations`, `notes` | **go** |
  | `symbol`, `declares`, `original_column` | **go** |

  !! **THE LAST THREE GO FOR A REASON THAT IS NOT SIZE.** Roy: *"they are stating something that
  the cue letter states. So we just give the agents the legend for the cue letters and let them
  run with it."* **The answer is a legend, not a field** -- and the check that makes it safe is
  a round trip: *"a little bit of pattern matching to ensure that they followed the cue letters
  in the final version as well, using a round trip by the lexer to verify that the cues come
  back with the same content (except the front matter headache)."*

  ! **THAT IS A DIFFERENT QUESTION FROM THE PAGE SHA** (`#8` of Process): the SHA asks *did the
  file shift under us*, the cue round trip asks *did the edits land where the cues said*.

  !! **AND THE FIRST REASON IS THE READER, NOT THE BYTES.** Roy, 2026-08-24: *"LLMs and the
  token parsers read this as a complete and coherent statement. They do not read this as the same
  thing:*

      ["LLMs and the token", "parsers read this as a", "complete and coherent", "statement"]

  *It took my phone, which runs a token parser, to the last word to realise I was duplicating
  the sentence and supply a suggestion."*

  ! **THE FOUR REVIEWERS ARE TOKEN PARSERS, AND PROSE IS WHAT THEY ARE ASKED TO JUDGE.** A
  paragraph handed over as line fragments makes each role reassemble the sentence before it can
  ask whether the sentence is true -- so the split is paid for at the one place this system
  exists to do well. ! **Argued, not measured**: the demonstration above is one, and whether a
  role finds more when handed text is a question for the grader.

  !! **A FIDELITY ARGUMENT WAS MADE FOR THIS AND RETRACTED THE SAME DAY.** It ran: the split
  destroys the line ending -- `text_lines("one\r\ntwo\r\n")` returns `["one", "two"]` -- so one
  string keeps what a list threw away. ! **It does not hold.** `compositor.line_endings` already
  rules that *"the first ending wins and mixed files are normalised"*, and puts one back at SET
  time; a per-paragraph ending would preserve a fact the compositor discards on purpose. The
  CRLF round trip works today through `set_page`, not through the stored lines.

  ! **SO THERE ARE TWO REASONS, NOT THREE**: the reading, and 3-5% of bytes. **The byte figure
  is what this ruling was reached through and is the lesser of them** -- and the retracted
  middle reason is kept here because it was in the commit that landed the ruling.

  ! **MEASURED, on the full census of one 659-row page**: 429,239 bytes to **158,543, 36%** on
  every row, and 54,793 -- **12%** -- on the rows that hold prose. Re-derive with
  `scripts/measure_binder.py`.

- **#13.** **`code_names` and `referrers` are a CONCORDANCE** (Roy, 2026-08-24: *"concordance
  -- for the two."*). They are INVERSES -- what the tree DEFINES, and who NAMES a file --
  and both exist because **a page cannot corroborate itself**: a corpus built from the text
  under review contains the comments being checked, so every obituary resolves against itself
  and the check always passes. Both read the WHOLE CHECKOUT and never the pages under review.

  !! **THEY WERE UNPLACED FOR A REASON WORTH KEEPING.** Neither performs an operation ON the
  machine and neither knows what a page is, so `machine` and `binder` each had to stretch past
  its own door to hold them. Roy ruled the neighbouring half first -- *"there was the git stuff
  which is io"* -- and left these: *"the code_names and referrers we actually need to settle."*
  They sat at the package root, where root MEANT unplaced, until this.

  ! **A CONCORDANCE is the trade's index of every word in a text and where each occurs**, which
  is what the two build between them. ! The name was reached the way `compositor` was, and in
  that order: ask what the thing IS, find the job in the answer, name the job by what it DOES,
  and only then take the trade's word for it.

  ! **`code_names` WAS A FUNCTION INSIDE `census.py`**, so this was an extraction. Two things
  could not travel with it: **`walk_files`** (was `census._walk`), which `commands/census.py`
  also uses and which is a plain filesystem walk over the checkout -- it went to
  `machine/repo.py`, beside the `EXCLUDED_DIRS` it already reads, and lost the leading
  underscore it should never have carried across a module boundary; and **`SYMBOLISH`**, a
  one-line identifier regex whose only reader had been `binder/annotate.py` -- importing it
  from there would have made `concordance` depend on `binder` for a regex, so it went to
  `reading/lexer.py`, which `code_names` already imports from, adding no edge.

- **#15.** **AN ABSENT PLACE IS NOT SENT TO AN AGENT UNLESS IT IS ASKED FOR** (Roy, 2026-08-25:
  *"The absent kinds are not supposed to be sent to the agents unless specifically asked for."*).

  !! **MEASURED over this repo the moment the ruling landed: 5,223 of 5,707 rows -- 91% -- held
  no prose.** 2,692 `margin` and 2,437 `interval`, which is roughly ONE EMPTY PLACE PER LINE OF
  CODE, against **2** `undocumented` in the whole tree. The binder falls from **1,147,232 bytes
  to 391,763 -- a 66% cut**, and four roles read it: 3.0 MB.

  ! **AN EMPTY PLACE IS STILL ADDRESSED, WHICH IS WHAT MAKES IT SAFE.** The walk emits every
  place, filled or not, so `add` stays expressible -- a reviewer asks for the one it means:
  `addresser --census C --anchor "<line of code>" --series b` answers `m.py@b1`. The place is
  CITABLE without being CARRIED. ! `census --include-absent` is the flag for a caller that wants
  them all.

  !! **AND IT MAKES `#12` RIGHT AND `#14` HALF-WRONG, WHICH IS WORTH KEEPING VISIBLE.** `#12`
  cut `kind` because *"the cue letter states it"*; `#14` put it back, arguing the letter gives
  the SERIES while the kind gives which half of the pair. Both were true, and the second stopped
  mattering here: **every row a reviewer now receives holds prose**, so its kind is its series'
  `present` and the letter does state it. `kind` is gone again and the row is SIX fields --
  the number `#12` ruled.

  ! **MEASURED before removing it, over 14,139 rows: `kind` equalled `derive(cue, raw_text)` in
  14,136.** The three exceptions are `go`, `ruby` and `lua`, where the kind DISAGREES with the
  cue -- `TODO/a-doc-comment-is-cued-a-and-typed-b.md`, a defect rather than information.

- **#16.** **`anchor_num` LEAVES THE ROW, and comes back only if it is shown to be needed**
  (Roy, 2026-08-25: *"The anchor num lets drop it and add it back if it actually becomes
  necessary. That is safe now."*). It was kept on 2026-08-21 because the galley and compositor
  were thought to need an order the cues could not be trusted to carry. **The chain ruled since
  (`Process: #14`) has the write path RELOAD the page from disk**, so it takes the anchor order
  from the page and never from a row. ! MEASURED before removing it: NOTHING read it from a row --
  `page` stamps it and `addresser` computes it, both on the page side. **The row is FIVE fields.**

  ! **IT IS THE ONE CUT MADE ON AN EXPECTATION RATHER THAN A MEASUREMENT**, and it is recorded
  that way: if a consumer turns out to need it, the field returns. What makes that safe is that
  nothing silently depends on it -- a caller that needs the order and cannot find it fails loudly.

- **#17.** **THE PAGE SHA IS THE VERIFICATION STEP'S, and an unread field is a step that does not
  exist yet** (Roy, 2026-08-25: *"The sha is carried to the verification step to verify that the
  edits that the agents were running against are the same files that the galley and compositor are
  going to copy and write over."*).

  ! **RECORDED BECAUSE IT WAS NEARLY CUT AS DEAD.** An audit on 2026-08-25 found `sha` emitted
  with no reader and listed it beside `anchor_num` as a candidate. It is not the same case: the
  chain (`Process: #14`) reads the page TWICE -- once into the binder an agent rules on, once
  again on the way out -- and this is the only thing that can say the two reads saw the same file.
  **A field with no reader YET is not a field with no purpose**, and the difference is whether a
  named step is waiting for it.

  ! **A RENAME IS STILL OPEN.** Roy proposed *"code names becomes references"* and withdrew it
  the same minute -- *"Don't act on that actually, continue with the split will determine
  later."* The module is `concordance/code_names.py` until he rules.

- **#14.** **THE LETTER LIVES WITH THE PAIR, AND `d` IS A SERIES** (Roy, 2026-08-25, reversing
  his own earlier decision: *"I feel I messed up ... when I made the decision not pairing cue
  letter and the present absent pairings together. The present absent pairings is effectively
  what defines the series and the identifier we give it should be right there with them. This
  goes for those and then the remaining Kind.LEADING gets its own series d separately which I
  think it already kind of does but the logic should be where that is defined not a layer
  removed."*).

  ! **WHAT THE SPLIT COST:** the letters were `addresser`'s constants and the pairs were
  `lexer`'s enum -- two modules that cannot import each other -- tied only by MEMBER NAME and
  held equal by a test. **That test existed because there were two sources.** `Kind`'s own
  docstring drew the `a`/`b`/`c`/`f` table in PROSE beside code that knew no letter.

  ! **`reading/series.py` IS THE LEAF THAT HOLDS BOTH.** `Definition(letter, present, absent)`,
  and `Series` carries one per series. `ADDRESSED` (the citable letters) and `ABSENT` (the empty
  kinds) are both DERIVED from it. ! `d` is a member whose `absent` is `None` -- a fence has a
  present and no absence, and saying so where the series is defined replaces an exclusion that
  had been written into three other modules.

  !! **AND IT CORRECTS PART OF `#12`.** That ruling cut `kind` from the row because *"they are
  stating something that the cue letter states"* -- **half true.** The LETTER states the series;
  the KIND states which half of the pair, `comment` against `interval`. A letter cannot say
  whether prose is there, so `kind` is not restatable from it and is back in the row. ! The
  other ten fields of that cut stand.

  ! **A `raw_text` EMPTINESS TEST WAS TRIED AS A SUBSTITUTE AND REFUSED.** Roy: *"No the lexer
  answers this with the appropriate Enum pair or Kind enum."* It invents a predicate beside one
  that exists, and an empty string is a fact about a VALUE where the kind is a fact about the
  PLACE.

- **#18.** **FRONT MATTER ENDS AT THE FIRST BLANK LINE, ON BOTH TIERS** (Roy, 2026-08-26: *"It is
  supposed to stop f0 at the first blank line. That needs fixed."*). **NOT A NEW RULE -- the
  restatement of one from 2026-08-21** that only half the code implemented: *"if the
  opening/closing line is a comment then the matter continues down/up until there is an empty line
  or the start/end of a docstring."*

  ! **THE LEXICAL TIER HAD IT AND THE TOKENIZED TIER NEVER DID.** `end_run`'s `opens_file` split
  the first run at a blank; `paragraphs_stdlib` skipped every `LAYOUT` token, so a comment run
  survived blank lines outright -- its own comment said so as though it were the intent: *"A
  COMMENT RUN SURVIVES LAYOUT AND IS ENDED BY ANYTHING ELSE."*

  !! **MEASURED 2026-08-26:** a shebang, a blank and a comment tokenized as ONE run opening on
  line 1, so the comment BELOW the blank was stamped `matter` and took `f0`. An `add` at `b0` then
  re-read as `f0` and the write chain refused a draft it had just written. **The two tiers gave
  different answers for the same file.**

  ! **AND THE RULING'S OPERATIVE HALF HAD BEEN CUT FROM THE CODE.** `reading/series.py`'s `MATTER`
  comment carried the *what* -- *"a licence header, a shebang or a coding line ... answers to the
  FILE"* -- and not the *where it stops*. The full quotation survived only in
  `prototype/original/lexer.py`. Same shape as `CLAUDE.md`'s own warning: a shortened quotation is
  not a shorter rule.

- **#19.** **THE COMPOSITOR SETS A LEADING BEFORE A `b` IT IS ADDING INTO AN EMPTY PLACE** (Roy,
  2026-08-26: *"It needs to add the leading between before any b"*). ! **AN EDITORIAL DECISION,
  RULED WITH ITS COST NAMED:** *"It may not be what all of the projects do but it is generally
  enough and easy enough to implement and it looks good enough to most humans that I think it is a
  justifiable editorial decision."* And on the file with no front matter, which then opens with a
  blank: *"the leading on the first line for places that do not have frontmatter will disappear on
  an automatic format run like ruff or black."*

  !! **IT FIRES ON AN ABSENCE, NOT ON A MISSING LEADING.** Roy first proposed the second -- *"the
  leading look up paragraph is not in there, which is admittedly backwards but that will tell"* --
  and MEASURED it fires on a MODIFY and on an unedited compose too, because a `b` sitting flush
  against its code owns no leading either. Three tests caught it. The gate is the PLACE's kind
  saying absence, which is also what makes the rule fire once per add rather than once per
  compose.

  !! **AND AT THE FOOT THE LEADING GOES ON THE OTHER SIDE** (Roy, 2026-08-26: *"still the same
  rule as the frontmatter in reverse."*). Matter is the run that STARTS on line 1 **or ENDS on the
  last line**, so what pushes a gap clear of it is a blank BEFORE at the head and a blank AFTER at
  the foot.

  ! **A LEADING BEFORE THE CLOSING GAP WAS THE MIRROR IMAGE OF THE FIX AND MOVED NOTHING.**
  MEASURED: `...return y\n# ADDED\n` and `...return y\n\n# ADDED\n` both re-read at `f1`;
  `...return y\n# ADDED\n\n` re-reads at the closing gap. The first attempt exempted the closing
  gap on that measurement and called the collision unsolvable -- it was solvable, in the direction
  the ruling already named.

  !! **THIS CLOSES `TODO/foot-of-file-two-places.md`**, which had asked for a ruling on *which* of
  the closing gap and the back matter owns prose at the foot. **The answer is both**, and the
  question was mis-framed: it assumed one had to lose. The back matter keeps the foot; the gap
  sits above the blank. ! Its second task -- make the losing place unemitted or refusable -- is
  SUPERSEDED, because there is no losing place.

  ! `f0` and `f1` take no leading: both round trip flush, because the matter series is defined by
  the file's edges rather than by what sits beside it.

## Vocabulary

- **#1.** **The metaphor is EDITORIAL, and a new term is checked against the register BEFORE it is
  proposed** (Roy, 2026-08-16). `jurisdiction` -> `remit` is the standing example of a term
  checked for collisions and never for register.

- **#2.** **Stage 2 `ANNOTATE` became `COLLATE`** (Roy, 2026-08-17). **SUPERSEDED by #10.**

- **#3.** **`PAGINATE` is refused for stage 2** (Roy, 2026-08-23: *"the way I have used in the past
  is by taking something that can print infinitely and split it into pages"*). Stage 2 splits
  nothing -- the division arrives from the filesystem. ! Any term whose meaning includes REFLOW is
  disqualified before asking what it splits, because this system may never move content.

- **#4.** **The census supplies a BINDER of pages; the cues are sticky notes on the page edge**
  (Roy, 2026-08-23). *"Like an overly diligent person, we also sticky-noted the places where we
  might want to insert text explicitly."* Chosen over `portfolio` on UPDATE-IN-PLACE rather than
  on order: a portfolio holds finished work, a binder exists to have one page replaced.

- **#5.** **`leaf` is retired; there is no leaf in the model** (2026-08-23). A leaf is one sheet
  carrying two pages, so it could be neither the page nor a cue. Both shipped senses were wrong,
  and `folio`'s definition -- *"a leaf's number in publishing, which is what it is here"* -- was a
  false equivalence that shipped to reviewers.

- **#6.** **`Foliation` needs no exotic noun; completeness lives in the PRACTICE** (2026-08-23).
  `cadastre` was the exact word for *a contiguous list of addresses whether occupied or not* and
  is refused: it is land-law register, the neighbourhood `jurisdiction` came from. An overly
  diligent person tabs every place they might insert, so *every cue on the page* is already the
  full enumeration.

- **#7.** **A name reinvents line numbers if it implies POSITION MEASURED FROM A START** (Roy,
  2026-08-23, asked as a guard: *"I don't want the line-numbers creeping in again"*). `index`,
  `sequence`, `ordinal` fail it. ! `b3` passes despite being the fourth gap, because it is
  assigned by walking CODE, and code does not move when prose is edited.

- **#8.** **A quoted span is exempt from the retired-word gate, and never in a file an agent is
  handed** (Roy, 2026-08-23: the exemption is for *"the specific doc files that could have old
  references"*, and there is *"strict no mistakes even quoted in the agents files"*). A ruling is
  quoted in the words it was made in; quotation marks do not stop a word reaching an LLM's
  attention. The line is the file suffix: `.md` and `.toml` are read by agents or emitted from
  and get no exemption, `.py` holds the engineering record. **Measured at adoption:** 31 `foli*`
  uses remained in the shipped tree, all in `scripts/*.py`, all inside quotations, none in
  `agents/`, `SKILL.md` or `references/`. ! That count is a fact about the day, not a reason the
  rule holds -- the gate's own comment said *"which is why strict costs nothing"* and was cut for
  giving a later reader grounds to relax the rule as soon as the number moved.

- **#9.** **`leaf` is retired in its PAGE sense and kept in its IMPORT-GRAPH sense** (Roy,
  2026-08-23). One sheet carries two pages, so it was neither the page nor the cue. The graph
  sense is Roy's own term from 2026-08-22 -- *"Constants.py is the ultimate leaf"* -- and
  `leaves` is an ordinary English verb besides. Declared as polysemy in `vocabulary.md`.

- **#10.** **Stage 2 is GATHER; #2 is superseded** (Roy, 2026-08-23: *"I think stage 2 is Gather
  -- it is what finds all of the files and puts them in the binder."*). Gathering is the binder's
  own word for collecting sheets into sequence, and every other stage name is an act. ! It frees
  `collate` for its trade meaning -- transferring every hand's marks onto one proof.

- **#11.** **The one who rules on the collated marks is the `copy chief`, and it gets its own
  agent file** (Roy, 2026-08-23: *"copy chief works. We will want to have a specific agent file
  for that separate from the task agent."*). `editor` was the obvious word and collides with
  `editorial role`, which `vocabulary.toml:54` already defines as one of the four reviewers; in
  the trade the copy chief rules over the copy editors' marks, one level above the four hands.
  !! **THE RULING CARRIES A SHAPE AND NOT ONLY A WORD.** Stage 5 APPLY is the task agent deciding
  today, which is why `vocabulary.md` recorded the role as *"unnamed, and there is no module"* --
  a job with no artifact can be given nothing, told nothing and checked for nothing. ! `verdicts.py`
  is NOT the copy chief: it collates and rules on nothing by design, so its own rename goes to
  `collator.py`.

- **#12.** **A mark carried into the text is `taken in`** (Roy, 2026-08-24, ratifying it: *"also
  fits the common use of the word"*). *Taking in corrections* is the compositor's own phrase for
  making the marked changes on a proof, and ordinary English *take in* is to absorb -- so it reads
  correctly with or without the trade. It is the counterpart to `stet`, and the two answer
  different questions: `taken in` is mechanical and per-mark, `stet` is the copy chief's and only
  where two roles disagreed.

  !! **`settled` WAS PROPOSED AND MEASURED OUT.** Roy's criteria were *"close to set but not
  confused with set"* and *"not overly generic like set"*; the shape is right and the word fails
  the second. MEASURED 2026-08-24: `settle` appears **94 times across 19 shipped files, and 35
  more in `docs/`**. ! Two are collisions with the neighbouring concept -- `re-review.md:139`
  already writes *"a paragraph stage 5 settled"*, which is the `stet` case, and `SKILL.md:68`
  lists `query` as **unsettled**, an axis about whether a QUESTION is open. **`taken in` returns
  zero.**

  ! **The measurement is the point, not the verdict.** The register rule asks that a candidate be
  checked BEFORE it is proposed; this is what that check returns when it is run, and it took one
  `grep`.

- **#13.** **`annotation` is the BINDER's sticky note, and only one thing in this system may
  carry the word** (Roy, 2026-08-24: *"Sticky notes for making the pages pages for important
  information. Directly relevant. May need a different term than annotations though or the other
  annotations get different terms"*, then: *"Only one is allowed"*). It goes to the binder.

  !! **IT WAS SETTLED BY EXPERIMENT RATHER THAN BY ARGUMENT, which is new here.** Roy: *"Can you
  give a couple of subagents a record and then split one and give it one annotation labeled as
  annotation and one labeled as sticky_note and ask it to use it to determine something about
  the record? Looking temporarily for what gets the concept across best while it is easy."*
  MEASURED 2026-08-24, **3 agents per arm on identical records differing only in the key**:
  `annotation` was read as a fact ABOUT the record by all three; `sticky_note` was read by two of
  three as something a HUMAN had left, and one discounted it as informal. ! Roy: *"I am glad we
  tested it first."*

  ! **A TERM THAT AN AGENT READS IS TESTABLE ON AGENTS**, and the test cost one message. The
  register rule says check a candidate before proposing it; this is a second check, for a word
  whose whole job is to be understood by a reader that can be asked.

  !! **AND IT LEAVES A DEBT: the three OTHER users of the word need names.** The lexer's three
  are **errors**, not notes -- Roy: *"if it is errored now we already have a broken system"* --
  and go to `TODO/exception-hierarchy.md`. **The collate-step message is UNNAMED**, deliberately:
  Roy asked for *"a name, don't need what it looks like yet. Because it isn't an annotation"*,
  and nothing has been ruled.

- **#14.** **THE WRITE SIDE HAS THREE CONTAINERS AND THEY MIRROR THE READ SIDE'S** (Roy,
  2026-08-26: *"like the binder we have three levels of containers -- paragraph, page, binder. We
  have to be able to unwind the alterations pretty close to the same way."*).

  | level | READ | WRITE |
  | --- | --- | --- |
  | one place | row | **alteration** |
  | one file | page | **schedule** |
  | the whole | binder | **docket** |

  !! **`alteration` SUPERSEDES `notations`, AND `Process: #25` IS THE RULING IT REPLACES.** That
  entry stays as written. The stand-in was named knowingly -- Roy, 2026-08-25: *"It is a prototype
  or stand in for what might need to be built ... We need the shape not the concrete
  implementation"* -- and the defect it was filed against is
  `TODO/notations-collides-with-annotations.md`: one letter from `annotation`, in an adjacent
  area, both meaning marks attached to a paragraph.

  !! **THE INSTINCT WAS RIGHT, WHICH IS WHY IT COLLIDED.** Roy: *"if I was writing between the
  lines with marks in red pen I think of those red marks as notations."* The trade calls those
  **proof correction marks**, and `mark` is already defined here as *"what stage 4 emits: one
  role's ruling on one paragraph."* The word was reaching for something the register had. What
  needed naming was the desk's OUTPUT, and a change to type already set is an **alteration**.

  ! **`docket` IS THE PRINT-PRODUCTION WORD** for the instruction paperwork that travels with a
  job -- the container, which is the level being named. It was weighed and rejected earlier the
  same day as a name for the CHANGES; at the container level it is the apt one. `jacket` and
  `wallet` are the same idea and free, but `jacket` collides with a dust jacket.

  ! **THE SHA SITS ON THE SCHEDULE**, because it is a fact about one file read once. That is what
  lets the docket replace the binder in the write path outright -- `Process: #24`'s intent made
  literal: *"besides reading the sha and file path/name you should not be assuming any binder
  things make it this far."*

  ! **NONE OF THE FOUR ENTERS `references/vocabulary.toml` YET.**
  `check_vocabulary.check_complete` counts a definition no role is given as a hole (`NO
  RECIPIENT`), so the shipped register would go red. They live in `docs/vocabulary.md` until a
  role's own prose uses one -- the same reason `binder` has never been in it.

- **#15.** **`library` IS EVERY FILE IN THE PROJECT UNDER REVIEW, and NEVER this program's own
  parts -- those are packages, sub-packages and modules** (Roy, 2026-08-27, in two halves:
  *"Strike `library` because that is not the word I would have used at any point in time for the
  concept. I have consistently used the words package, sub-package, module. Those are the Python
  terms for them and I will always stick to the Python terms for those concepts referring to the
  internal program."* and then *"I do think library has a useful definition in the system. It is
  all of the files in the project being reviewed."*).

  !! **SO THE LIBRARY IS THE POPULATION AND THE BINDER IS THE SELECTION.** That names something
  this system needed and did not have: **the set of things a mark MAY address.** An `add` or a
  `move` destination may cite a page the binder never carried -- it is still in the library --
  which is the constraint Roy stated the same day: a destination must be addressable, *"not
  necessarily in the binder."*

  ! **AND IT RETIRES THE WORD `external` FOR THIS.** A code file censused mid-run is not external
  to anything; it was on the shelf all along. What is true of it is that THE ROLES NEVER SAW IT,
  which is a fact about the binder rather than about the file.

- **#16.** **THE BINDER'S SECTION FOR A PAGE TAKEN FROM THE LIBRARY MID-RUN IS `pulled`** (Roy,
  2026-08-27: *"Pulled works. I like it."*). Three sections: `pages` -- what the roles reviewed;
  `pulled` -- taken from the library during the run because a mark needed it, same shape and same
  `page_for` call; `references` -- documents, addressed `path:line`.

  ! **THE NAME IS THE ACTION, FROM ROY'S OWN SENTENCE**: *"an external program file should get a
  `page_for` pull."* ! `consulted` was rejected for asserting read-only -- a `move` destination may
  land in `pulled` -- and `late copy`, the trade's term for copy arriving after setting began, for
  framing lateness as a fault when the page arrived exactly when the finding did.

  !! **A SECTION RATHER THAN A PER-ROW FLAG**, and the reason is the same one that nested the
  docket: a flag is a fact repeated on every row that has to be kept true, while a section states
  it once and cannot drift.

  ! **OPEN: WHETHER THE DOCKET MIRRORS THE SPLIT.** A docket page carries `path`, `sha` and its
  alterations, and by then the provenance question is settled -- but a write chain about to set a
  page NO ROLE REVIEWED may want to know that before it does. Unruled.

  !! **WHY THE SECTIONS EXIST AT ALL, AND IT IS MEASURED HARM RATHER THAN TIDINESS.** Roy,
  2026-08-27: *"one of the problems that the original runs had was they couldn't modify out of the
  original binder. That caused them problems with the quality of recommendations they could do
  because leaving incorrect statements elsewhere made already bad worse."*

  ! **THE HARM IS NOT AN UNFIXED DEFECT; IT IS A DISAGREEMENT THE RUN CREATED.**
  `TODO/correcting-one-copy-strands-the-reference-copy.md`, raised 2026-08-17, states it: *"A run
  corrects a claim in a file under review, and the same claim in a REFERENCE ONLY file keeps the
  old text. Nothing may target the reference file, so the run ships a disagreement it created."*
  Roy then: *"leaving stale documentation behind references just asks to make these harder to
  trace down later."*

  ! **BEFORE the run, two copies agree and are both wrong -- a reader gets one story. AFTER, they
  disagree and nothing says which is current.** A partial correction is worse than none, and a
  role that can see the second copy but not reach it is forced to choose between the two.

  !! **SO `pulled` AND `references` ANSWER THAT TODO, AND BY A DIFFERENT ROUTE THAN IT PROPOSED.**
  Its mechanism was `REFERENCE CONCERNS` -- a channel for *someone should fix that*, recorded in a
  spec and never shipped. The sections let the run REACH the second copy instead of reporting it.
  ! That TODO is `agents`-owned and `decision-needed`; whether the channel is still wanted
  alongside the reach is Roy's.

  !! **THE WORD WAS NEVER HIS, AND IT ENTERED THROUGH `Process: #12` -- AN ENTRY ATTRIBUTED TO
  HIM.** MEASURED 2026-08-27: no quotation from Roy anywhere in this tree contains it. From that
  entry it spread to **16 sites**, ten of them identical banners in `commands/*.py`. Struck the
  same day.

  ! **NARROWED, NOT RETIRED.** Two shipped files use the word correctly, of the standard library
  and of a third-party package, and `check_retired` scans `plugins/` -- so retiring it would
  refuse correct prose. `docs/vocabulary.md` carries the declared split.

  !! **AND `Process: #12` OVERSTATED ITS OWN QUOTATION IN A SECOND WAY.** Its headline reads *"a
  flow calls modules; a command exposes a flow"*, but the quotation it cites is about entry points
  alone -- *"the commands run through it not through the scripts that are doing double or triple
  duty"* -- and the word `flow` is Roy's ruling of the NEXT DAY, 2026-08-25, about the read side
  being producers plus a chain. **A later ruling was absorbed into an earlier entry's headline.**
  ! The entry-point half and its measurement stand; the three-tier layering is a synthesis and is
  marked as one here rather than rewritten away.

  ! **WHAT CAUGHT BOTH WAS ROY'S MEMORY, NOT A GATE.** He said *"I don't remember making this rule
  or its justification."* Every check in the tree passed over it: the entry cites a real
  quotation, carries a real measurement -- 10 of 19 modules with a `main()`, `addresser` imported
  by 7 -- and is cross-referenced from a release plan. **This file is the audit trail, and it has
  no reader but him.**

- **#17.** **A MARK IS THE OBJECT; ITS `instruction` IS ONE OF THE SEVEN. `verdict` IS STRUCK**
  (Roy, 2026-08-27: *"I also don't like the term verdict. It doesn't seem in line and is confusing
  when it is also called a finding."*).

  ! **TWO FAULTS, AND THE SECOND IS THE ONE A GATE COULD NEVER SEE.** `verdict` is judicial on an
  editorial system -- the same register error `jurisdiction` made before it became `remit`. And it
  named the same thing twice: the object was a *finding* and its type was a *verdict*, so a reader
  had two words and no rule for which.

  !! **THE PRACTICE HAD ALREADY DROPPED IT.** MEASURED over the 2026-08-27 rounds: every role
  wrote `{"marks": [{"address", "mark", "claim", "reason", "sources", "update"}]}`. **The word
  `verdict` appears nowhere in any role's output** -- it lived only in the prototype's code and in
  the brief, which is where a term goes on being typed after everyone has stopped saying it.

  | | |
  | --- | --- |
  | the object a role returns for one place | a **mark** |
  | what it says to do -- one of seven | its **`instruction`** |

  ! **`instruction` IS THE TRADE'S, AND IT ARRIVED FROM THE FUNCTION FIRST.** A proof correction
  carries two marks: a TEXTUAL mark saying where, and a MARGINAL mark saying what to do. The second
  is the instruction -- and it is what a COMPOSITOR executes, which is a role this system already
  has. ! Register checked before proposing, per the standing rule: `ruling` (184 uses) and `call`
  (191) were refused as too loaded to take.

  ! Landed in `src/comment_review/desk/mark.py` as `Instruction` / `INSTRUCTIONS`. **The brief and
  `SKILL.md` still say `verdict` and are `agents`' to change** -- a rename there is a one-for-one
  substitution, but the surrounding sentences are not.

- **#18.** **THE TASK AGENT IS THE `managing editor`** (Roy, 2026-08-27: *"If you are leading this
  effort, you are acting as the lead editor, managing editor, or consolidator"*, confirming it
  names the task agent and not the copy chief).

  ! **IT WAS THE LAST MACHINE WORD IN AN EDITORIAL REGISTER.** Three jobs, and only two were
  named: the four **editorial roles** mark the page, the **copy chief** rules on the collated
  marks (`#11`), and *the task agent* dispatched the roles, sent the revises, decided the loop had
  converged and handed the proof to the human.

  ! **`managing editor` IS THE TRADE'S FOR THAT JOB** -- running the production process,
  scheduling the passes, deciding when a proof is done. `lead editor` is generic and
  `consolidator` describes the collator's work rather than the leading.

  !! **IT DOES NOT SUPERSEDE `#11`.** The copy chief still rules on marks at a place; the managing
  editor runs the process that ruling sits inside. Asked and answered explicitly, because a
  supersession of a ruling that carries its own reason should be recorded as one and not swapped
  in quietly.

- **#19.** **`the join` IS RETIRED. THE MODULE IS `collator.py` AND IT HOLDS TWO NAMED STEPS**
  (Roy, 2026-08-27: *"'The join' was too ambiguous. It didn't define anything and you used it as a
  shortcut that could have meant many different operations"*, and *"collator.py works not
  collate.py"*).

  !! **MEASURED, AND THE CHARGE IS EXACT: FIVE REFERENTS IN ONE WORD.** 202 live uses, carrying

  | the word meant | e.g. |
  | --- | --- |
  | the `verdicts.py` program | *"the join exits nonzero"*, *"the join's report"* |
  | linking two data structures | *"the site that joins the two halves"*, *"the doc-to-declaration join"* |
  | checking a mark against its page | `desk/mark.py`, written the same evening |
  | a git merge | *"side WINS a join"*, `census.py` |
  | ordinary English | *"the same prose joined"* |

  ! `TODO/verdicts-is-the-join.md` is named for the confusion, so the ambiguity had already
  reached the backlog.

  !! **THE TWO STEPS ARE THE TRADE'S, AND ROY SUPPLIED BOTH.** *"source-verification -- the process
  of checking facts by researching, citing, and using references"*, and *"reconciliation -- when
  you are gathering and blending changes from multiple people."*

  | step | scope | answers |
  | --- | --- | --- |
  | **source-verification** | per MARK, against the page | does the address resolve; does every `source` resolve with its `verbatim` really there; is the sentence the claim rules on really in that paragraph |
  | **reconciliation** | per PLACE, across marks | do two marks rule on the same sentence; do their edits overlap; does each edit touch what its claim named |

  ! **THE EDIT CHECK SITS WITH RECONCILIATION AND NOT WITH VERIFICATION**, because what an edit
  TOUCHES has to be computed to blend two edits at all -- so *did it touch what it claimed* falls
  out of a computation reconciliation already performs. Filing it under verification would compute
  the changed regions twice.

  ! **AND THE COLLATOR RULES ON NOTHING**, per `#11`. Reconciliation DETECTS that two marks
  collide and hands the place on; it never picks between them. So its output is decisions and
  escalations, never merged text.

  !! **WHY THE WORD FAILED IS ITSELF THE FINDING.** `join` names a MECHANISM -- two things matched
  up -- where every other term in this register names a JOB. That is the same error as `galley`
  doing two jobs and `verdict` naming a ruling: reaching for what the code does to a data
  structure instead of asking what the person doing the work is doing. ! Roy, on the trade: *"I
  would be surprised if the name of the step in the editing world is 'the join' considering that
  working with words is their thing and there has to be a better one."*

  ! **PROTOTYPE KEEPS IT.** `prototype/` is a record of how it worked, and renaming inside a
  captured record makes it describe something that never happened.

- **#20.** **THE REVISE IS A CONFLICT DIFF, IN `diff3`, AND ONLY `correct` AND `patch` COME BACK**
  (Roy, 2026-08-27).

  **THE ARTIFACT IS A DIFF.** *"Your training has made you pretty good at reading a git diff and
  using that to show the conflict would probably be useful. The diff could go right back to the
  editor for a new mark immediately."*

  !! **`diff3`, WITH THE BASE, AND THE TWO-SIDED FORM IS REFUSED.** MEASURED on a real merge: two
  roles edited DIFFERENT lines of one paragraph, and the two-sided render showed each side
  differing from the other in BOTH lines -- so a reader cannot tell which line either role
  touched. With the base present it is immediate. ! **The two-sided form is structurally incapable
  of separating a real conflict from two composable edits in one hunk**, which is the exact
  distinction reconciliation exists to make.

  ! **AND THE BASE IS WHAT KEEPS SOURCE-VERIFICATION WORKING ON THE RETURN.** A `claim.false` is
  checked VERBATIM against the paragraph; a role ruling on a two-sided conflict has no stable text
  to quote, only two candidate rewrites.

  **ONLY `correct` AND `patch` MAY COME BACK.** Roy: *"it wouldn't make sense to litigate again.
  Patch and correct can merge any two diffs together."* !! **THAT SET IS ALREADY A ROW PROPERTY**
  -- `rules_on_text` is exactly `['correct', 'patch']` in `desk/mark.py`, so the constraint is
  derived and cannot drift from the table. Placement was settled by `ownership-context` in round
  one and existence by `drop`/`add`; only the wording is still open.

  **ANY NEW MARK RELITIGATES.** Roy: *"The conflicting agent ruled on a one set of results and
  picking the new mark changes what that ruling meant. Any new mark goes back because of that. You
  can't know if the agent would agree with whatever the update was."* ! Same logic as testing
  convergence on the CLAIM SET: an answer given against a state is stale once the state moves.

  | role A | role B | outcome |
  | --- | --- | --- |
  | a new mark | anything | **another round**, always |
  | holds | holds | the **copy chief** -- both have declared they disagree, so sending it back buys nothing |
  | holds | withdraws | the held claim, mechanically `taken in` |
  | withdraws | withdraws | pick one, revise double-check, mechanically `taken in` |

  ! **THE ROLE'S TWO NON-MARK ANSWERS NEEDED A WORD** -- `stet` is copy-chief-only (2026-08-24)
  and `taken in` is the compositor's, assigned mechanically, so neither is a role's to emit.
  **ANSWERED BY `#22`**: they are `hold` and `withdraw`, and they are explicit.

- **#21.** **A `query` ON A REVISE SPLITS BY SHAPE, AND REASONING IS SHARED FROM ROUND TWO ON**
  (Roy, 2026-08-27).

  | shape | what happens |
  | --- | --- |
  | `human-review-necessary` | **raised to the human BEFORE the write flow sets any text.** The copy chief surfaces it immediately and fills in the alteration directly |
  | `unable-to-determine`, another role holding a mark | revise **with the context of the question** |

  !! **AND THE OTHER ROLES' REASONING IS SHARED, WHICH REVERSES THE EARLIER DESIGN.** Roy: *"I
  know you seem to want to keep their reasoning to themselves but humans wouldn't do that. They
  would sit in a room and discuss it until they either stated they couldn't come to an agreement
  or they would agree and write it down. Besides the first round I don't think isolation buys
  accuracy over group-think. No new ideas in no new concepts out."*

  ! **THE ISOLATION WAS BUYING SOMETHING AT DISCOVERY AND NOTHING AFTER IT.** Blind-parallel
  review stops a role anchoring on a finding it has not yet made. By the revise both positions are
  filed and on record, so nothing new can be generated -- what withholding prevents there is
  resolution.

  ! **AND THE REVERSAL IS CHECKABLE RATHER THAN HOPED.** A role that re-read the code carries new
  `sources` or a `ran`; one that agreed with the argument carries only prose. **So capitulation
  and re-verification are already distinguishable in the fields**, and the failure this change
  could introduce is measurable. ! MEASURED 2026-08-27, under the withholding rule: 2 of 3
  converged in one pass and the roles re-verified rather than deferring -- one re-traced a
  dispatch chain and re-grepped the tree, one declined an invitation to widen its own finding.

- **#22.** **A DIFF-MARK CARRIES ONE OF FOUR, AND ALL FOUR ARE WRITTEN DOWN** (Roy, 2026-08-27:
  *"I would prefer the explicit hold/withdrawn/patch/correct marks"*).

    hold        my mark stands
    withdraw    I retract it
    correct     a revised claim -- relitigates
    patch       revised wording -- relitigates

  ! **PRESENT TENSE, AND THE PAIR IS `hold`/`withdraw`.** Roy, 2026-08-27, on `withdrawn` and
  `held`: *"The other pair are past tense and not quite right for agents actively negotiating."*
  A participle names a settled state; these name an act being taken now. ! It also matches the
  seven, which are bare verbs -- `clean`, `drop`, `add`, `move`.

  ! **AND `forwarded` WAS CONSIDERED AND REFUSED**, on Roy's own doubt: *"it also has implications
  that it is the first time to make the claim."* **To PUT FORWARD a claim introduces it**; the
  pair here acts on a claim already filed. ! And in a system that escalates to the copy chief and
  raises to the human, `forward` reads as *routed onward* -- two plausible readings meaning
  opposite things.

  !! **THE REASON IS THE ANTI-DECISION DECISION, AND IT IS THE RULING'S WHOLE POINT.** Roy:
  *"Inferring the decision from lack of decision means that the agents get to do the human failure
  of the anti-decision decision. Where we allow undecided things to continue effectively making
  the decision to keep the status quo."*

  ! An inferred `withdraw` is indistinguishable from a role that never answered, so the status
  quo wins by default and **nobody is on record as having chosen it.**

  !! **THIS IS THE SAME RULE THIS REPO HAS NOW LANDED THREE TIMES**, and each time the fix was to
  make the null answer something a hand must WRITE:

  | where | the silence that was doing a decision's work |
  | --- | --- |
  | `TODO/` | *"a check box not-marked is left as something todo, even if it was superseded"* |
  | `clean` | it was optional, so *read it and found nothing* and *never looked* were one absence -- ruled back to mandatory |
  | a diff-mark | an unanswered place would read as a withdrawal |

  !! **AND THESE FOUR ARE NOT AN ADDITION TO THE SEVEN.** A diff-mark is a DIFFERENT ARTIFACT
  answering a different question -- *does your finding still stand* rather than *what is wrong
  with this page* -- so it carries its own closed set. The seven stay seven. ! `correct` and
  `patch` appear in both because they are the two that `rules_on_text`, which `#20` derives from
  the row rather than listing.

  ! **A `query` RAISED AT REVISE IS A HUMAN QUERY, AND IT MEASURES SOMETHING.** Roy: *"If after
  the revise round one raises a query that is only a query to the human. The text has become
  ambiguous and probably should have had the query mark from the first round."* ! A role that has
  seen both readings and still cannot resolve it has exhausted what another agent could add. **So
  queries first raised at revise count round-one OVER-CLAIMING** -- the failure direction opposite
  to the one coverage measures.

- **#23.** **A TEST'S EXPECTATION COMES FROM SOMEWHERE THE CODE UNDER TEST CANNOT MOVE** (Roy,
  2026-08-28: *"Tests that test themselves are not useful tests."*).

  !! **MEASURED THE SAME MORNING, ON A SUITE WRITTEN THE NIGHT BEFORE.** `tests/test_mark.py`
  built every case from `INSTRUCTIONS` -- the table it was checking -- and its own docstring
  called that a virtue: *"built from `INSTRUCTIONS` rather than from a literal, so a row change
  moves the test with it."* **47 tests passed over a gate that refused two marks written from the
  shipped brief verbatim**, an `add` carrying `claim.anchor` and a `query` carrying `claim.shape`.

  ! **AND MUTATION-CHECKING HID IT RATHER THAN CATCHING IT.** Six of seven mutations were caught,
  so the suite looked sound. Breaking the code broke the test because BOTH SIDES MOVED TOGETHER --
  **a check can bite and still ask the wrong question.** `docs/gates.md` says *"could the check
  fail"*; this is the case that says *could it fail for the right reason*.

  !! **THE DISTINCTION IS INPUTS AGAINST EXPECTATIONS, AND `tests/README.md` ALREADY DREW IT** --
  *"Pages come from `page_for` over real source, binders from `bind`; a literal appears only where
  malformed IS the input."*

  | | |
  | --- | --- |
  | **inputs** from reality -- a real page, a real binder | correct, and what the suite does |
  | **expectations** from the implementation | circular -- it can only confirm |

  ! The failed test took BOTH from the table. **Deriving an input from real code is using reality;
  deriving an expectation from the implementation is asking the implementation whether it agrees
  with itself.**

  ! **WHERE AN EXPECTATION MAY COME FROM**: the shipped prose that states the contract, a
  recorded run's real output, or a literal a human checked. Never the module under test.

- **#24.** **`collate` CARRIES TWO TRADE SENSES; THIS SYSTEM USES ONE AND DECLARES THE OTHER**
  (2026-08-28, designing the staged flow).

  | sense | trade | ours |
  | --- | --- | --- |
  | **gathering and blending changes from several people** | copy desk | **`collator.py`.** Ruled in `#19`, and the one this system means |
  | **comparing two states of one text to find where they differ** | bibliography -- the Hinman collator | **not used.** The command that does this is `taken_in` |

  ! **THE SECOND SENSE FITS THE NEW COMMAND EXACTLY**, which is why it is written down rather than
  left to be rediscovered: a session reaching for the obvious word would give `collate` two
  meanings, and **the undeclared one is the defect** -- not the ambiguity, which is a fact about
  English that predates this repo.

  ! **`taken_in` IS NOT A NEW TERM EITHER.** `#12` ratified it 2026-08-24 -- *"A mark carried into
  the text is `taken in`"* -- so the command is named for the question it answers: what has been
  taken in on this page before I arrived.

- **#25.** **A CLOSED SET IS A `StrEnum` AND THE CLI PUBLISHES IT** (Roy, 2026-08-28, on an agent
  file telling a role to write `"outside my role"` where the gate takes `outside-my-role`): *"Should
  be a StrEnum with an appropriate flag on the cli to make it work"*, and *"Same for all of the
  other flags and input definers."*

  ! **THE MEMBER, ITS `__str__` AND ITS FLAG ARE RELATED BUT NOT IDENTICAL**, and Roy named the seam
  himself: *"You know that the difference between `QueryEnum.OUTSIDE_MY_ROLE` And its `__str__` And
  the flag `--outside-my-role` All have to be related but not exact. And while I don't usually like
  monkeying with `__new__` You can always slide that in the middle to make
  `QueryEnum("outside-my-role")` work."*

  ! **AND A CLI FLAG HAS NO MISSING CASE** (Roy, same day): *"If it is a cli flag there is no
  missing it is a true and it gets set. I don't think checking if it is close earns anything other
  than telling us that we can program correctly."* A near-miss check was proposed and refused.

  ! **THE CONVENTION ALREADY EXISTED AND `desk/` NEVER GOT IT** -- `reading/series.py` holds
  `Kind(StrEnum)`, whose docstring records the same failure repeating. `Process: #38` is the
  companion rule: an enum member gets no second name.

- **#26.** **`prototype/` IS NOT AN AUTHORITY FOR WHAT THE GATE OWES** (Roy, 2026-08-28): *"Why are
  you talking about code in `prototype/original/`? And fixing things based upon something in
  there?"*

  ! **WHAT THE GATE OWES COMES FROM THE SHIPPED PROSE A ROLE READS**; how a dead module happened to
  do it is archaeology -- *"Nothing imports it, nothing ships it, it does not run."* ! The TESTS
  were already right, every expectation coming from the brief or a checked literal. **It was the
  REASONING that leaned on the record**, which is worse in a plan than in a test, because a plan is
  what the next person reads.

- **#27.** **`change` IS THE UPDATED PARAGRAPH AS RAW TEXT** (Roy, 2026-08-28): *"I don't want to
  have to figure out indentation again or comment style. All of the agents can read the page again
  on their own."* A seeded row carries `raw_text` -- the paragraph, not the page -- so an edit
  round-trips to the root's exact bytes, indentation and comment markers included.

- **#28.** **THE MIDDLE HAS FOUR CONTAINERS, AND THE ONE THAT WAS MISSING IS THE ROLES LEVEL**
  (Roy, 2026-08-29).

        master_proof
          +-- edit_copy        one per role; one per SHARD under fan-out
                +-- sheet      one per page
                      +-- mark one per place

  ! **`master_proof` HOLDS `edit_copies`, NOT SHEETS DIRECTLY.**

  !! **WHY THE LEVEL EXISTS.** Roy: *"The got the binder - they copied the pages from the binder
  and built their own binder to make up ... this is their edit_copy - the emit the sheets
  (pages-with mark) which are just the marks with addresses because we don't have to carry the
  duplication in a computer program. the master proof holds the edit_copies."* ! `binder` and
  `docket` have no roles level: one goes out, one comes back, and in between there are N marked
  copies. *"They are separate containers, and calling each of them as having a `master_proof`
  would be incorrect."*

  !! **`sheet` CHANGES SENSE, AND THE OLD ONE IS IN SHIPPED PROSE.** It named the PER-ROLE
  container -- `flows/marks.py` opens *"Hand a role a sheet to fill"*. It now names the PAGE-UNIT;
  the container is `edit_copy`.

  !! **THIS ENTRY CLAIMED `SKILL.md` USED IT NINE TIMES THAT WAY, AND THAT WAS FALSE.** MEASURED
  2026-08-29 while task 3 did the rename: `SKILL.md` has 11 lines containing `sheet` and **every
  one is the STYLE SHEET**, a separate term `vocabulary.toml` already declares. **None is the
  per-role container**, so no agent-facing file needed renaming at all.

  ! **HOW THE FALSE COUNT WAS MADE: the word was counted and every hit read as the container
  sense.** That is mention-not-use -- the same trap this repo hit three other times the same day,
  in a substring gate for `proof_setter.run(`, in an `os.path` sweep, and in a scratch check for
  `galley`. ! It is corrected rather than deleted: a false measurement that is quietly removed
  teaches nothing, and this one names its own mechanism.

  ! **`edit_copy` BECAUSE THE REGISTER IS THE COPY DESK, NOT THE BINDERY.** Roy: *"it isn't
  overloaded with the other copy's it is adjacent and explicit."* This file already records that
  the binder is *"a 3-ring binder full of stuff not binder as the person who bounds books"*, and
  cut a justification reaching for the bookbinder's `gathering` -- so `gathering` and `sheaf` were
  already out of register.

  ! **`master proof` WAS ALREADY HERE, LISTED AS UNNAMED** -- *"the single copy every mark has
  been collated onto"*, whose only producer was `verdicts.py`, which left for `prototype/` on
  2026-08-25. The object went with it.

  !! **AND THE SHEET CARRIES THE SHA, WHICH BREAKS A SEAM BEFORE IT OPENS.** Roy: *"it also lands
  us a place to copy the page shas from so we are not reaching into the binder to get it. That
  breaks the only current read-write link coupling in the system."* ! The coupling is PROSPECTIVE:
  `proof_setter` stopped taking a binder on 2026-08-26 (`Vocabulary: #14`), and nothing builds a
  docket yet -- a flat `edit_copy` would force that emitter to reach back for every sha. ! **NOT
  EVERY BINDER READ IS COUPLING**: `collator.known_addresses` must keep reading it, because
  checking that a role did not invent an address has to be asked of the authority.

- **#29.** **THE COPY CHIEF'S THIRD ACT IS `recast`** (Roy, 2026-08-30, ratifying it in two
  words: *"recast works"*). The chief has three, and they are not the role's four:

    taken_in    a role's text is carried into the page
    stet        the original stands; the correction is declined
    recast      the chief's OWN prose, replacing every side

  !! **IT EXISTS FOR THE CASE THAT SHOULD NOT ARISE.** Roy, 2026-08-29: *"the
  chief-composes-by-hand needs to be available no matter what ... `copy-chief-edit --sheet x
  --mark-address b3 --replace "Resolved New Prose"` which is different than stet or taken_in ...
  This should never happen but..."* ! **A path with no answer is where a run stops dead**, so the
  branch nobody expects to take is the one that must exist: no clean composition, or genuine
  disagreement where neither side is right and neither can be made right from its own statement.

  ! **AND IT IS THE LAST RESORT, NOT THE MECHANISM.** Two `hold`s on DISJOINT spans compose
  ARITHMETICALLY -- `hold` already says *my mark stands*, so two of them are already saying both
  are true, and `Process: #22`'s four need no fifth. `recast` is reachable only when that
  composition REFUSES. ! The ordinary path leaves the chief transcribing nothing, which matters
  because a derived composition can be re-derived and was set by BOTH roles, where a hand
  transcription attributes to the chief, who wrote none of it.

  ! **THE WORD IS THE TRADE'S**, for rewriting a passage in a different form, and it was reached
  by the method this repo requires -- name the job by what it DOES, then look for publishing's
  word for it. ! `stet` is still an open `agents` ruling
  ([`no-mark-for-let-it-stand`](../TODO/no-mark-for-let-it-stand.md)), so two of the chief's
  three are named and one is not yet filed.

- **#30.** **THE COPY CHIEF'S `edit_copy` IS THE SAME SHAPE, AND THE CHIEF STEP IS A FOLD** (Roy,
  2026-08-30): *"I felt (maybe wrongly) that these would end up being the same shape and the
  master-proof would go from multiple edit-copies to one edit-copy in the copy-chief step."* **Not
  wrongly.**

      master_proof { edit_copies: [ role_a, role_b, role_c, role_d ] }
          -> gather / places / reconcile  ==> Reconciled(settled, escalations, rereads)
          -> the chief: taken_in | stet | recast
          -> edit_copy { role: "copy-chief", sheets: [...] }     ONE. Same shape.

  !! **BECAUSE IT IS THE RESULT OF THE FOLD, NOT A WORKSPACE DURING IT.** After the chief acts
  every place has exactly ONE answer -- a settled place keeps its mark, an escalated one becomes
  `taken_in`, `stet` or `recast`, a re-read one becomes the composed text. One mark per place is
  an ordinary `edit_copy`.

  !! **AND IT IS WHY `docket_from` TAKES ONE ARGUMENT.** It transcribes an ordinary `edit_copy`;
  nothing about the chief's is special.

  ! **A PLAN STEP PROPOSING THREE STATES ON AN ENTRY -- `settled`, `escalated`, `reread` -- IS
  STRUCK.** Those are the INTERMEDIATE, and the intermediate already has a type:
  `desk.collator.Reconciled`. Writing them onto entries would have been a second representation
  of something that exists.

  ! **THE ROUND TALLY GOES ON THE CONTAINER, NOT THE MARK.** The chief's copy from round N is the
  input to round N+1, so the count rides the envelope -- `{"rounds": {"m.py@b1": {"composition":
  1, "conflict": 0}}}` -- and the mark's seven fields stay seven.

  !! **THE CONTAINERS GET A TYPE IN `desk/`, NOT A MARKDOWN SOURCE, AND THE DISTINCTION IS WHO
  AUTHORS THEM.** Roy: *"They need a place somewhere in the desk/ folder."* `docs/the-mark.md`
  exists because **an agent authors a mark**, so its shape must be published to a role and cannot
  live only in code. **No agent ever authors a container** -- `seed`, `fan` and `gather` build
  them -- so the type IS the definition, the way `desk/mark.py` defines `Mark`.

  ! **AND THE SHAPE HAS BEEN CODE-ONLY UNTIL NOW**, at `flows/marks.py:36` and `desk/mark.py:318`,
  which is the state `the-mark.md`'s own header calls out: *"the shape had no owning file, and
  something else became the spec."* The ordinary `edit_copy` is real and shipping -- 60+ uses
  across eight modules; the chief's was an idea with one mention in `src/`, a comment saying the
  copy chief is out of scope.

## Metaphor and its limits

- **#1.** **A category doing two jobs gets asked what the trade calls the half that does not fit**
  (Roy, 2026-08-21). `galley.py` was splitting the page and setting it; the second half became the
  compositor.

- **#2.** **The editorial metaphor stops at the compile constraint** (Roy, 2026-08-23: *"after we
  are done certain symbols still have to land in an exact right place and order else the code
  doesn't compile, and that is something we can't do"*). Publishing has no equivalent -- a page
  that reads badly is still a page -- so `prove_unchanged.py` and the compositor identity stand in
  for a rule the register cannot supply.

- **#3.** **`galley` survives the foliation** (Roy, 2026-08-23: *"our pages are infinite lengths,
  and can be reordered at will to make them look like one unordered length"*). A galley is
  unpaginated continuous copy, which a file is; making up into fixed-height sheets never happens
  here.

## Process

- **#1.** **A thing whose dependencies are broken is refused, not worked on** (Roy, 2026-08-21 and
  2026-08-22). A repair to a module whose inputs are wrong is SHAPED by those inputs.

- **#2.** **The TODOs are the job board; plans are how we mark them off** (Roy, 2026-08-19). A plan
  cites TODOs; a TODO never cites a plan.

- **#3.** **A TODO is superseded and checked, never deleted** (Roy, 2026-08-19). A deleted box
  leaves no trace that it was there or why it went.

- **#4.** **This decision log exists, and history holds the commentary** (Roy, 2026-08-23). Format
  borrowed from `redacted_corpus/docs/redacted_pkg/decision-log.md`, including per-section numbering
  and the reason for it.

- **#5.** **A test belongs to the lane that owns what it tests, not to `tests/`** (Roy,
  2026-08-24): *"testing's lane is specifically about building and testing the running agent
  system that is in the testing harness branch. If it is backend testing that is on you. If it is
  vocabulary and system gating tests that is systems. Running the tests for the agents is the
  agents responsibility, it is testing's lane to make the grader and keep the grades."*

  | the test asks | lane |
  | --- | --- |
  | does this Python do what it says | `backend` |
  | does a gate still bite -- vocabulary, floor syntax, release | `systems` |
  | does a role behave when run | `agents` |
  | how well did the whole system do, and what is that scored against | `testing` |

  ! **SUPERSEDES the flat `tests/** -> testing` row** in [`lanes.md`](lanes.md), which sent a
  `record.py` regression test to the lane that owns the grader. `testing` owns the GRADER and the
  GRADES, and its work lives on the harness branch.

- **#6.** **It works correctly first; the design is made correct after** (Roy, 2026-08-24): *"It
  is make things work correctly, make the software design 'correct' after it works correctly.
  Design, then refactor."* ! **The design may be WRITTEN first** -- the two 2026-08-23 specs were
  -- but the code does not move onto it until the code is right. ! Same instinct as `#1`: that
  refuses a fix written against wrong inputs because the fix is shaped by them; this refuses a
  restructure of code that does not yet do its job, because the shape would be chosen against
  behaviour nobody has established.

- **#7.** **0.2.4's premise failed, and the scope is the whole backend round trip** (Roy,
  2026-08-24): *"the plan's scope assumed it was going to be a minor modification to the backend
  to accomplish what it started. It wasn't, because the system was too broken. And shipping the
  minor modification on a broken thing is not okay."* The release is READ, CENSUS, GIVE, TAKE,
  RESOLVE, PROVE -- not the handout alone.

  ! **A RETRACTION OF A PREMISE, NOT A WIDENING OF AMBITION.** The original scope -- *the release
  is the ADDRESS* -- is kept at the top of that plan verbatim, because it is what was believed
  when sixteen boxes were ticked under it.

  !! **AND IT WAS DISCOVERED ONCE ALREADY, THREE DAYS EARLIER, WITHOUT REACHING THE PLAN.** Roy,
  2026-08-21, on why a second plan was branched off this one: *"the 0.2.4 plan had the gaping
  hole in its functionality that made it unshippable."* That whole plan was written, worked and
  closed while the sentence it contradicted stood unchanged. **A scope stated as a claim that
  nothing re-checks collects its corrections beside it rather than into it.**

- **#8.** **A piece is missing between the collated proof and the galley, and it composes rather
  than chooses** (Roy, 2026-08-24): *"the system assumes that verdicts and records are what is
  used to write from the galley, but the galley only really needs this address gets this
  paragraph ... So we have a missing piece in the chain."* The galley's contract was always
  right -- `{address: text}` -- and **nothing in the tree produces that file.**

  ! **TWO SHIPPED SENTENCES DESCRIBED THE HOLE DIFFERENTLY**: `SKILL.md:925` says *"nothing
  between stage 5 and the galley converts"*, and `galley.py:173` says `--edits` is
  *"machine-written from approved text"*. Neither is a producer.

  !! **IT COMPOSES MECHANICALLY IN THE SYNTHESIS ORDER; A CONTRADICTION GOES TO REVISE.** Roy:
  *"multiple answers can be true, not just either this or that ... where things do not conflict
  and come back clean that is probably a single transform."* ! **CORRECTED same day**: this read
  *"only a contradiction STOPS it"*. A contradiction does not stop anything -- it goes back to
  the roles, twice, and returns as a `stet`. See `#9`.

  !! **AND EVERY MARK IS NAMED OR THE RUN REFUSES.** The artifact carries address -> text -> the
  marks it answers. ! Without that, the step between the proof and the galley is where a finding
  can vanish with nothing to show it was raised.

  ! The name is unsettled and is Roy's: `TODO/nothing-makes-the-fair-copy.md` T1 uses **fair
  copy** as a working candidate only, on `CLAUDE.md`'s rule that the name comes last.

- **#9.** **`stet` is the COPY CHIEF's declaration after two roles failed to agree, not a role's
  verdict and not a per-mark disposition** (Roy, 2026-08-24): *"my understanding of stet is that
  it is the declaration that the copy chief emits when two editorial roles couldn't agree. It
  emits on the one that it chose, or it overrules both, but the goal is revise (currently
  re-review) gives the editorial roles two chances to figure out the compromise with reasons."*
  And: *"stet -- let this stand. That is what I understood when it was proposed."*

  ! **THE POINTING IS THE WHOLE OF IT.** The copy chief points at what stands, and **that may be
  the original or one role's mark**. *The original stands* is one of the two things `stet` can
  point at, not the meaning of the word.

  !! **A ROLE CANNOT EMIT ONE**, which contradicts `TODO/no-mark-for-let-it-stand.md` as written:
  its T3 adds `stet` to `VERDICTS` as an eighth verdict and its T13-T16 ask what each ROLE's own
  `stet` asserts. `stet` presupposes two roles that disagreed and a copy chief that ruled, so no
  single role is ever in a position to file one. ! That file is `agents`' and `decision-needed`;
  this entry records the correction rather than rewriting its boxes.

  ! **THE TWO CHANCES WERE ALREADY RULED AND BUILT.** `references/re-review.md:128`, 2026-08-17:
  *"AT MOST TWO re-review rounds, and then the APPLIER judges ... If it is still split after the
  second, stage 5 rules on it."* **What was missing is the NAME for what stage 5 then emits** --
  a ruling nothing names cannot be recorded, re-read, or refused a second time.

- **#10.** **The trade's word for a round after the first is `revise`, and the shipped tree still
  says `re-review`** (Roy, 2026-08-24: *"revise (currently rereview)"*).
  [`vocabulary.md`](vocabulary.md) already carries **revise** -- *the second proof, pulled after
  the marked corrections have been set* -- against *"a re-review round"*, so the translation was
  recorded and never carried into the code. ! **First revise, second revise, then to press: the
  two-round bound IS the trade's practice**, which is why the bound and the word arrive together.
  MEASURED 2026-08-24: **13 files, 41 occurrences; 7 files and 23 occurrences shipped** under
  `plugins/`. `TODO/nothing-makes-the-fair-copy.md` T11 carries the rename.

- **#11.** **A one-for-one substitution is not a lane crossing** (Roy, 2026-08-24: *"This doesn't
  land in the other lane just like a vocabulary change doesn't land in the other lane. A one for
  one swap is allowed."*). A lane may make a MECHANICAL swap in another lane's file when its own
  change forces it -- a command's spelling, a renamed symbol, a moved path -- and may not change
  what the instruction MEANS. **The test is whether a reader's BEHAVIOUR changes.** Written up in
  [`conventions.md`](conventions.md); it is the SECOND standing exception to *name the lane and
  ask*, and that file's claim to have only one was corrected in the same change.

- **#12.** **A module does one job and has no CLI; a flow calls modules; a command
  exposes a flow** (Roy, 2026-08-24, ordering the move to `src/comment_review/`: *"The entry
  points get an actual entry point .py file and the commands run through it not through the
  scripts that are doing double or triple duty."*). MEASURED the same day: **10 of 19 shipped
  modules have a `main()`**, four of them imported by others while also being CLIs -- `addresser`
  is imported by **7**. ! The console guard is written into **eleven** files as a consequence.
  Scoped by [`docs/plans/0.2.4-rework-the-boundaries-are-not-real.md`](plans/0.2.4-rework-the-boundaries-are-not-real.md).

  ! **THE SHIPPED TREE TAKES THE SAME STRUCTURE, WHOLESALE** -- Roy: *"It is definitely not
  flattening them out again. I said wholesale I meant it. Whatever structure we end up with ends
  up there."* And `tests/` follows it too: *"The tests folder layout follows the move layout."*

  ! **`repo`'s git calls, filesystem reads and exception tuples are `io`** (Roy, 2026-08-24:
  *"there was the git stuff which is io"*). **`code_names` and `referrers`' module half are
  NOT ruled** -- *"the code_names and referrers we actually need to settle"*. Both ask a
  question ABOUT the checkout rather than performing an operation ON it, so neither is io's and
  neither is a page's. Open as P11 of that plan.

- **#13.** **CORRECT is not a green suite** (Roy, 2026-08-24: *"correct isn't passing green tests
  -- correct is passing the human comment review and having it come back looks good and
  correct"*, and *"it is ultimately that I am satisfied with the way the code operates, not just
  that it can accomplish its goals but that I agree that the way it gets from point A to B to ...
  Z is what I would write if I had the time"*). ! **It is the standard this tool applies to
  everyone else's code**, which is why stage 8 is a reader rather than a checker and why
  [`gates.md`](gates.md) exists. A ticked box is necessary and is not the claim.

- **#14.** **THE CHAIN FROM BINDER TO HUMAN, ruled end to end** (Roy, 2026-08-24). This is the
  answer to the question [`nothing-makes-the-fair-copy`](../TODO/nothing-makes-the-fair-copy.md)
  was opened for, and the piece that was missing when he said *"we have a missing piece in the
  chain."* Verbatim:

  > *"The binder goes to the agents the agents make there marks on something (I am think
  > notations) the desk system takes the notations and the binder and emits an update {address:
  > new paragraph}. The galley gets a list of the updates (list is loose here it needs more like
  > the page sha). The workflow reloads the page sends the page through the galley with the
  > updates. Then after the updates finished sends that to the compositor. Sends that through
  > the page system again to make certain that the agents put the right comments in the right
  > places. The that gets shown to the human ..."*

  | step | who | in | out |
  | --- | --- | --- | --- |
  | 1 | the binder | the pages | what the agents read |
  | 2 | the agents | the binder | **notations** -- their marks |
  | 3 | the **desk** | notations + binder | **`{address: new paragraph}`** |
  | 4 | the workflow | | RELOADS the page |
  | 5 | the **galley** | page + updates + a page SHA | the updated page |
  | 6 | the **compositor** | that page | the text |
  | 7 | the **page** again | that text | proof the marks landed where they were meant to |
  | 8 | the human | | the proof |

  !! **THE UPDATE IS `{address: new paragraph}` AND NOTHING ELSE**, which settles what a verdict
  and a record are NOT. Roy, earlier the same day: *"the galley only really needs this address
  gets this paragraph and that replaces the current page paragraph."* ! Inferring that the
  RECORD carries it was ruled **WRONG**; twelve tests are held rather than patched because of it.

  ! **`notations` IS PROPOSED, NOT SETTLED** -- *"I am think notations"*. The name for what an
  agent emits is still open; the SHAPE it becomes is not.

  !! **THE PAGE IS READ TWICE, AND THE SECOND READ IS THE CHECK.** Step 7 sends the composed text
  back through the page system to confirm the marks landed where they were meant to -- so the
  system verifies its own output by the same reader that produced its input, rather than by
  trusting the write. ! That is [`gates.md`](gates.md)'s rule satisfied by construction, and it
  needs the page SHA of step 5 to be worth anything.

  !! **NOTHING TRANSFERS FROM THE BINDER TO THE END.** Roy, 2026-08-24, stating it as flatly as
  it can be stated. The binder is what the agents READ, and step 4 RELOADS the page from disk --
  so **not one binder row reaches the galley, the compositor or the output.** The only thing that
  crosses from the reading side to the writing side is the ADDRESS, which is a key, not data.

  ! **THAT IS WHY THE BINDER CAN BE TRIMMED WITHOUT TOUCHING THE WRITE PATH**, which is the
  premise the field cut was working from before this branch paused it -- and why a census row
  must never be treated as a source of truth for writing. Roy: *"Nothing builds from census rows
  because nothing has to and nothing should have to."* MEASURED 2026-08-24: the galley already
  re-reads the file (`read_raw`, then `page_for`) and uses the census only for the addresses an
  edit cites, so the rule describes the code as it stands rather than asking it to change.

- **#15.** **LEADING IS A FENCE, AND A FENCE TAKES NO ADDRESS** (Roy, 2026-08-24: *"Series d are
  walked because they have to be but they are not cues"*, and *"You don't put an address on a
  fence because it is what divides properties. The only thing we can do is say well there was a
  fence here before we did this there should be a fence here after we did this."*).

  ! **IT IS NOT PASSED TO THE AGENTS** -- *"The leading is not something that will be passed to
  the agents. The same as the extra record attributes. It gets dropped because there is nothing
  to rule on. It is for white space."* ! MEASURED 2026-08-24, BEFORE the fix: `census --json`
  over a 10-line file emitted **3 rows carrying no address**, every one `kind='leading'`; over
  this repo's own `src/`, **422 of 9,459 paragraphs** were addressless and every one was leading.

  !! **AND THE ADDRESS IS A POSTAL ADDRESS, WHICH IS WHERE THE FENCE FOLLOWS FROM.** Roy: *"the
  analogy for the address is a real address. Street name street number, city, state, [country --
  assumed]. The cue is the street name and number, the file is the city, and the rest is the
  folder structure and computer."*

  | postal | here |
  | --- | --- |
  | street name and number | the **cue** -- `b3` |
  | city | the **file** |
  | state | the folder structure |
  | country | the machine, assumed |

  ! **A fence between two properties has no street number**, which is why `d` carries a SYMBOL
  and never an address -- and why asking one for its series is a category error rather than a
  case to absorb. The blank return that let it pretend otherwise is gone.

- **#16.** **THE ORIGINAL SHA IS READ OUT OF THE SAVED BINDER, NEVER RECOMPUTED** (Roy,
  2026-08-25: *"we can't assume that the file didn't change between original read and loading to
  write and so getting it out of the json blob is important"*). The chain compares against the
  sha the binder recorded at read time, not one recomputed from the file loaded for writing.

- **#17.** **THE SAME SHA CHECK PROVES THE READ-ONLY ROLES STAYED READ-ONLY** (Roy, 2026-08-25:
  *"This also ensures that agents didn't try to fix what they found while reviewing"*). One
  comparison answers both questions -- did the file drift, and did a reviewer edit it -- because
  either would change the bytes.

- **#18.** **THE NOTATIONS READER IS A STAND-IN, NOT A FINISHED FORMAT** (Roy, 2026-08-25: *"We
  need the shape not the concrete implementation"*). Enough is built to reach the chain's second
  half; the shape an agent actually emits is not designed by this branch.

- **#19.** **A WEAK CHECK IS STRENGTHENED IN PLACE, NEVER DOUBLED** (Roy, 2026-08-25: *"lets make
  certain we are not duplicating tests only adding new to truly new functionality"*). Where a
  test already exists for a box this branch closes, the branch strengthens it in place rather
  than adding a second, weaker-passing test beside it.

- **#20.** **A REFUSAL ABORTS THE RUN WHOLE, AND IS PROVISIONAL** (Roy, 2026-08-25: *"fails loud
  amd stops is the right answer for now"*). Nothing in this workflow touches the real tree, so a
  partial draft set costs only a re-run. **"For now" is part of the ruling**: what replaces it is
  the transactional per-page write -- `pending`, `written`, `verified`, `failed`, a manifest, a
  retry -- which belongs to workflow 2 and is designed in the custody spec's last section.

- **#21.** **`machine/` OWNS THE HASH; PAGE AND BINDER RECEIVE IT, NEITHER ASKS FOR IT** (Roy,
  2026-08-25: *"the querying of it should not have left the machine/ modules ... information
  received by page and binder, not something requested by page/binder"*).

- **#22.** **THE SHA IS TAKEN AT THE READ** (Roy, 2026-08-25: *"the only place to properly ensure
  it gets read exactly the same and the middle things shouldn't depend on the external things"*).
  Measured: two readers give one file two shas, so the value has to come from the read it will
  later be compared against, not be recomputed downstream.

- **#23.** **`reset` TAKES A PAGE AND CUES; IT RESOLVES NOTHING** (Roy, 2026-08-25: *"the galley
  shouldn't be resolving the page ... it should get handed the page, the cues-new text or a
  delete"*).

- **#24.** **THE CHAIN CHECKS THE SHA, NOT THE GALLEY AND NOT THE COMPOSITOR** (Roy, 2026-08-25:
  *"The sha-page piece should be part of the chain of command piece"*). One owner answers the
  staleness question once, in `flows/proof_setter.py`, rather than each write-side module
  answering it again -- see the OWNERSHIP MOVED note on
  [`a-page-carries-no-identity`](../TODO/a-page-carries-no-identity.md).

- **#25.** **WHAT THE AGENT WORKFLOW HANDS OVER IS NAMED `notations`** (Roy, 2026-08-25: *"a good
  name is notations"*). Settles the name `#14` left open -- *"I am think notations"*.
  **SUPERSEDED by `Vocabulary: #14`, 2026-08-26** -- the name is `alteration`. ! The ruling is
  kept as written, not edited: it is the record of what was decided on the 25th, and the word it
  names is quoted from Roy.

- **#26.** **THE SAVED BINDER IS WHAT SAYS WHICH FILE TO RELOAD** (Roy, 2026-08-25: *"We also
  have to grab the binder address from the saved material"*).

- **#27.** **A DELETE IS `None`, NOT AN EMPTY STRING** (Roy, 2026-08-25: *"None is explicit
  enough"*).

- **#28.** **`prove_unchanged` IS RULED TO RUN AT EACH PROPOSED FINAL STATE, AND ONLY THE FIRST
  RUN IS BUILT** (Roy, 2026-08-25: *"just before the human review and just after the human review
  edit piece"*). This branch built the first: `_prove` runs once, before the draft is shown to a
  human. **PROVISIONAL**: the second run -- after a human edit, before it is taken as final --
  belongs to the human-review/human-edit/machine-review/machine-copy workflow this branch does
  not build; see `flows/proof_setter.py`'s own docstring: *"IT STOPS AT THE TEMPORARY FILE."*

- **#29.** **A DESCRIPTION MUST NOT BE WRITTEN AS A CONSTRAINT** (Roy, 2026-08-25, on
  `commands/addresser.py`'s *"This module reads no source file -- the census is the only
  input"*: *"It was WRONG for the agent to put it in there. It implied a constraint that the
  system HAD to live by instead of a constraint that the code was written to because the system
  was available"*).

  !! **THE SENTENCE WAS TRUE AND STILL WRONG**, which is what makes this its own defect class.
  It described what the code did; it read as a rule about what the code MAY do. So when the
  eleven-field row cut removed `anchor_line` and `anchor_num` from the row -- the only positions
  that module could see -- the honest fix was to read the page, and the docstring said that was
  out of bounds. **A description phrased as a rule fences off work that was never fenced.**

  ! **IT IS THE SIBLING OF THE COST CLAIM `CLAIM.md` ALREADY WARNS ABOUT** -- *"a claim about the
  COST of a change, which is the kind that invites someone to make the change and discover the
  cost."* That one invites a wasted attempt; this one prevents an attempt that should have been
  made. Both are prose that no gate can see, because both are TRUE of the code as written.

  ! **THE TELL IS THE MOOD.** *"This module reads no source file"* is a fact. *"the census is the
  only input"* is a rule. Write what the code DOES and why it was enough; if something genuinely
  may not happen, say what forbids it and where that was decided.

- **#30.** **`galley` IS A NAME ON THE PROOF CHAIN, NOT A SECOND CHAIN** (Roy, 2026-08-26: *"We
  have a single entry point for the system? These delegate through to the commands? Create the
  galley entry_point function that points to proof_setter and delete the unused command."* And on
  the reason: *"there is no reason to go to the galley for something that proof-setter is supposed
  to do."*).

  ! **WHAT WENT**: `commands/galley.py`'s own argument parsing, its address-to-path resolution
  through `rows_of(census)` -- the binder-row coupling `Process: #14` ruled the chain out of -- its
  staleness comparison, its overlap guard and its draft loop. `main()` now calls `proof.main()`.

  !! **THE NAME CARRIES OVER; THE FLAGS DO NOT.** `galley` took `--census`/`--edits`, `proof` takes
  `--binder`/`--notations`, so the `SKILL.md` stage that invokes the old spelling is refused by
  `proof`'s parser. Rewiring it is `agents` lane --
  `TODO/the-skill-names-commands-that-moved-to-prototype.md`. **The removal is in
  [`history.md`](history.md)**, and the measurements this file was the exemplar for are cited there
  rather than at a module that no longer holds the code.

- **#31.** **A FALSIFIED CLAIM NAMES A NEIGHBOUR'S STATE, NOT ITS OWN** (the final simplify pass
  on this branch, 2026-08-26, naming the shape behind TEN falsified claims found across it). Every
  one was a guard's justification written into the docstring of the module that GAINED the guard,
  stating the state of a NEIGHBOUR -- *"this does not exist yet"*, *"nothing else does this"*,
  *"N tests pass"* -- where nothing can notice when the neighbour moves.

  Three measured directly, in this same pass: `desk/__init__.py` said *"WHAT CARRIES A ROLE'S
  ANSWER TO THE PAGE IS NOT HERE AND IS NOT NAMED"* after `desk/notations.py` had already landed
  to be that piece; `flows/__init__.py` said *"THE RESULTS-SIDE FLOW DOES NOT EXIST YET"* after
  `proof_setter.run` was that flow; `CLAUDE.md` and `tests/README.md` both carried `880 passed ...
  225 test functions, collected as 884` after `d74aa4b` cut 160 lines of `test_galley.py` and left
  the count at 873 passed, 218 functions, 877 collected.

  ! **THE RULE: a paragraph naming another file's state belongs IN that file, or carries the
  command that re-derives it.** A count is safest of all when it sits beside the command that
  reproduces it, which is why `CLAUDE.md`'s test-count comment survives by staying next to
  `uv run pytest -q` rather than by being remembered correctly.

  ! **THE SIBLING OF `#29`.** `#29` forbids a description written as a constraint on the SAME
  code; this forbids a description written as a fact about OTHER code. Both are prose no gate can
  see, because both were true on the day they were written.

- **#32.** **A `pulled` PAGE IS SETTABLE; A `reference` IS TOO, BUT NOT BY THIS CHAIN** (Roy,
  2026-08-27, answering the three questions `Vocabulary: #16` left open).

  | the section | settable | by what |
  | --- | --- | --- |
  | `pages` | yes | the chain that exists |
  | `pulled` | **yes -- *"has to be"*** | the SAME chain. It is code, it has cues, it has a sha |
  | `references` | **yes, eventually** | *"needs a separate flow with separate galley-compositor chain"* |

  ! **`pulled` NEEDS NOTHING NEW, AND THAT IS THE POINT OF THE SECTION.** A pulled page went
  through `page_for` exactly as a reviewed page did, so it carries the same cues, the same sha and
  the same round trip. **The only fact that distinguishes it is that the roles never saw it** --
  which is a fact about the BINDER, not about the file, and nothing in galley, compositor or
  `prove` reads it. Roy's *"has to be"* is why the whole `pulled` section exists: a mark that
  cannot reach the second copy leaves the disagreement the run created.

  !! **AND THE REFERENCE CHAIN IS DEFERRED, EXPLICITLY.** Roy: *"is a todo for the future Not Yet
  -- i want the middle piece to work first."* ! **This is the standing refusal in `CLAUDE.md`
  arriving as a schedule** -- a second galley-compositor pair written against a middle that does
  not yet work is shaped by inputs that have not settled, which is the cost the six refusals
  record. Filed as [`a-reference-needs-its-own-write-chain`](../TODO/a-reference-needs-its-own-write-chain.md).

  ! **WHY IT CANNOT BE THE SAME CHAIN.** A reference is addressed `path:line` and has no cue
  series, and its text may REFLOW to a width -- so the compositor's whole contract, *set these
  lines back where the cues say*, has no subject. `prove_unchanged` has no subject either
  (`prove-refuses-a-doc.md`). Two of the chain's three checks do not apply, which is a different
  chain rather than a flag on this one.

  !! **THE SIGNAL IS OPEN AND IS TO BE DECIDED WHILE BUILDING.** Roy: *"Docket probably needs a
  code/reference schedule split to be the appropriate signal for the flow that needs to happen but
  maybe there is a different way of signaling and should be discussed while implementing."* ! So
  the docket's shape is NOT ruled here. What is ruled is that **something must tell the flow which
  chain a schedule belongs to**, and that the candidate is a split mirroring the binder's.

- **#33.** **THE THREE `query` SHAPES ARE KEYED ON WHO RESOLVES IT, NOT ON WHERE THE EVIDENCE
  LIVES** (Roy, 2026-08-27, replacing the set that shipped).

  **THE PREMISE FIRST, because it is what invalidates the old set**: *"this really is not expected
  to be a repeatable event. Once a single apply of comment review is done using the determinations
  over again doesn't really make sense."*

  ! The shipped middle shape rested on the opposite assumption. Its operative sentence was *"No
  reviewer in a fresh checkout can settle it"* -- a **reproducibility** test, which asks whether
  someone ELSE, LATER, could reach the same evidence. **If a run's determinations are spent when
  they are applied, that question has no consumer.**

  | | old set | new set |
  | --- | --- | --- |
  | keyed on | WHERE the missing evidence lives | **WHO resolves it, and what happens next** |
  | | `outside my role` | `outside-my-role` -- deferred to another agent's problem |
  | | `outside the checkout` | `unable-to-determine` -- *"don't know why but maybe another agent figured it out"* |
  | | `outside the code` | `human-review-necessary` -- *"genuinely contradictory statements and/or code and only system level intent might disambiguate it"* |

  !! **THE OLD SET MADE THE SHAPE DO THE `reason`'s JOB.** *Generated, gitignored, remote, one
  machine* is a CAUSE, and a cause is prose -- it belongs in `reason`, where a human reads it.
  A shape is read by the FLOW, and the flow can do nothing with a cause. **The new three are
  routing**, which is the only thing collate needs from them.

  !! **AND THE MIDDLE ONE BECOMES MECHANICALLY ACTIONABLE, which the old middle never was.**
  `unable-to-determine` says *another role may have settled this* -- and collate already groups
  every mark by place, so it can SEE whether another role returned something substantive there.
  ! `outside the checkout` afforded no such check: nothing downstream could act on the news that a
  file was gitignored.

  ! **`outside-my-role` SURVIVES UNCHANGED and keeps its special status** -- the one shape that is
  a BOUNDARY REPORT rather than work, flagged `can_declare_scope`, and it must never block the
  other roles. MEASURED: treating a scope declaration as a question let one role veto three
  others and the docket fell from 12 alterations to 5.

  ! **WHAT PROMPTED THE RE-DERIVATION** was a contradiction between two uses of one word: a source
  may cite the LIBRARY (which includes the gitignored `corpora/`, carrying real evidence), while
  `outside the checkout` listed *gitignored* among the things no reviewer can reach. ! Roy did not
  resolve that contradiction -- **he removed the axis that created it.**

  ! **THE REGISTER IS NOT SETTLED.** `unable-to-determine` and `human-review-necessary` are
  functional rather than editorial, and this repo takes its terms from publishing. The candidates
  are noted in [`the-fields-do-not-say-a-mark-may-cite-across`](../TODO/the-fields-do-not-say-a-mark-may-cite-across.md);
  the CATEGORIES are ruled and only the words are open.

- **#34.** **THE FLOW IS STAGED, AND EACH EDITORIAL BOUNDARY PULLS A REVISE** (Roy, 2026-08-28:
  *"it bakes in the idea that all editorial-role agents see everything at the same time and only
  rule on it once ... unless as part of the binder we copy the whole program into a tempdir and
  allow edits there"*).

  ! **THE SKILL NEVER WORKED THE OTHER WAY.** `SKILL.md` stage 4 already runs `ownership-context`
  alone at 4a and the other three at 4c; what was missing is that the three read the ORIGINAL, so
  a role could not know an earlier one had already ruled a sentence false.

  **A STAGE IS ONE OF TWO KINDS, and only one of them pulls anything:**

  | kind | hands back | after it |
  | --- | --- | --- |
  | **editorial** | marks on a seeded sheet | verify -> reconcile -> revise step -> pull a revise |
  | **enriching** | facts -- resolved references, symbols, a language server's answers | they go into the next binder. No docket, no revise |

  ! `annotate.py` is already an enriching stage in everything but name, which is why this is a row
  in a list rather than a new mechanism.

  !! **TWO AXES, AND CONFLATING THEM IS WHAT WOULD MAKE A MESS.** BETWEEN stages is sequential --
  stage N+1 reads a revise carrying stage N's taken-in edits, and there is nothing to merge.
  WITHIN one stage is concurrent, and that is the only place a conflict can arise. **`diff3` stays
  per place, inside a stage**; it never goes up a level.

  ! **ONE ROOT PER STAGE**, being a tree copy with the drafts overlaid rather than the drafts
  alone. `Vocabulary: #15` lets a `source` cite any place in the LIBRARY, so a citation into a page
  an earlier stage edited must read that page's CURRENT text -- which a drafts-only directory
  cannot give.

  ! **THE ARTIFACT ALREADY HAD ITS NAME AND ITS DEFINITION.** `#10` carries `revise` from
  `vocabulary.md` -- *"the second proof, pulled after the marked corrections have been set."*
  **What this entry extends is the count**: N revises, one per editorial boundary, and the LAST one
  is the draft the human approves at 7a. There is no separate draft-building path.

  ! **AND MOST OF THE MECHANISM WAS BUILT.** `flows/proof_setter.py` already sets a page into
  `--out DIR` -- *"a temporary file, never the original"* -- proving executable code unchanged and
  refusing a directory that overlaps the repo; and `census`, `carry`, `proof`, `prove_unchanged`
  and `referrers` all take `--repo`, so pointing a stage at a revise is passing a different value.

- **#35.** **THE ADDRESS SPACE IS INVARIANT ACROSS A REVISE, BECAUSE `prove_unchanged` HOLDS THE
  CODE** (2026-08-28, the safety argument for `#34`).

  A place is determined by CODE -- a declaration, a gap between two code lines, the room beside a
  line, the leading between paragraphs. Prose changing inside a place neither creates nor destroys
  one, and `add` and `drop` FILL and EMPTY places that already exist. So if the executable code is
  byte-identical, a mark written at stage 3 against `foo.py@b7` names the place stage 1 saw.

  !! **IT IS RECORDED AS A CLAIM TO GATE, NOT AS A FACT.** Everything downstream rests on it, which
  is exactly the condition [`gates.md`](gates.md) names: re-census each revise and assert its
  address set equals the original's, over real files, with a hand-changed revise proving the check
  can fail. ! Without that, the strongest argument in this design would be a paragraph.

- **#36.** **A REVERSAL IS A TWO-ROLE DISAGREEMENT AND GOES IN THE SAME REVISE STEP** (Roy,
  2026-08-28: *"The return to stage 1 only goes between the agents that disagree over the
  statement. It doesn't restart the whole flow. Same as the other revise and in the same revise
  step."*).

  A later stage correcting a paragraph an earlier stage set is a disagreement about one statement,
  so it is a ROW on the revise sheet at that boundary -- one more kind beside the within-stage
  conflict, taking the same closed set from `Vocabulary: #22`.

  | row | its base | its sides |
  | --- | --- | --- |
  | a **conflict** | that stage's paragraph | the two proposed texts |
  | a **reversal** | the paragraph as the earlier stage left it | the later stage's text |

  ! **THE SHEET IS ADDRESSED TO A ROLE, NOT TO A STAGE.** A role may be handed a one-row sheet at
  a boundary it did not otherwise join. Nothing is re-run, and the forward pass stays a line.

  ! **THE PAIRING IS WITH WHOEVER LAST SET THE STATEMENT**, which need not be the first stage: if
  stage 2 already corrected a place and stage 3 reverses it, the parties are stage 3 and stage 2.
  So the revise carries per-place PROVENANCE, and that provenance **routes** the row rather than
  merely counting it.

  !! **THE CAP WAS ALREADY RULED AND A SESSION CALLED IT A GAP.** This entry corrects that: `#9`
  ruled two rounds on 2026-08-24 -- *"revise ... gives the editorial roles two chances to figure
  out the compromise with reasons"* -- and `references/re-review.md:128` already states *"AT MOST
  TWO re-review rounds."* What terminates the second is the copy chief's `stet`. ! Roy re-affirmed
  two on 2026-08-28; the number is unchanged and its ORIGIN is 2026-08-24.

- **#37.** **THE MARK'S SHAPE HAS AN OWNING FILE, AND IT IS `docs/the-mark.md`** (Roy, 2026-08-28:
  *"None of those were part of the accepted shape of the mark structure or any part of the plan.
  This is not okay. We had a specific plan for the mark structure and the appropriate classifiers
  for each part. I don't know where these came from or why"*).

  **THE APPROVED SHAPE**: seven fields; **FOUR classifier columns** -- claim keys, verbatim,
  change, sources; **SEVEN row flags** -- not substantive, may declare scope, empty change allowed,
  rules on text, not diffable, anchor named in backticks, destination addressable. **Eleven things,
  and a row states these and nothing else.**

  !! **A ROW CARRIES NO PROSE, AND THE PROSE IS NOT TO BE GENERATED EITHER.** Roy, 2026-08-28:
  *"What finishes can be put into the instruction set and the cli help. **I forbid you from
  including anything like this in the code right now.**"* ! The session had proposed deleting the
  two prose fields `payload` and `claim_help` and DERIVING their sentences from the claim-keys
  list -- which puts prose-building in the code to avoid storing prose in the code, and is the same
  error in a second costume. **Neither the string nor the generator belongs there.** What an
  instruction carries is stated in `docs/the-mark.md` and published by `reviewer-brief.md`; what a
  role reads when a claim is refused is the CLI help's.

  !! **AND `change` IS THE UPDATED PARAGRAPH AS RAW TEXT, WHICH IS WHAT THE HOLE WAS.** Roy,
  2026-08-28: *"`change` needs to be the updated paragraph as raw text not lines or sentences.
  This will make it easier to diff per the rest of the stages. The original had it as one sentence
  to change but that did not work which is why you probably put in prose because it is a hole with
  that part of the spec without it."*

  ! **THE DIAGNOSIS IS MEASURED.** `move`'s row carried `change_all=("to",)` and a `change_help`
  reading *"move needs the DESTINATION paragraph in `change`, as `to` -- plus `from`, the origin as
  it reads after"* -- and **those two fields exist for no other reason.** With the change column's
  shape unstated, a prose field was written to state it. **An underspecified column grows a prose
  field to explain itself**, which is the mechanism behind both halves of this entry.

  ! **THE SEEDED ROW CARRIES `raw_text` AND THE ROLE RETURNS `change`; THE TWO DIFF DIRECTLY.**
  That is the reason rather than a convenience: source-verification, the `diff3` conflict (base =
  `raw_text`, sides = each role's `change`), `taken_in` and the revise are all one diffed against
  the other. A line array must be joined before any of them runs.

  ! **SUPERSEDES the four rounds' "an ARRAY of file-ready lines"**, which was chosen against two
  measured hand-transcription failures. Raw text does not re-open them -- **it makes them louder**,
  since a diff against `raw_text` shows a stripped comment marker or a truncated paragraph
  directly, where a line array shows only a shorter list.

  !! **AND `move`'s `change` IS THE COMPOSITE, BECAUSE A MOVE IS INDIVISIBLE.** Roy, 2026-08-28:
  *"The move needs the composite of the delete/add paragraphs. It really is two operations wrapped
  in one label and justification. Which is right -- you don't want to say it can move and it can't
  complete the move because 1/2 is rejected."*

  A move is a delete at the origin plus an add at the destination, under **one label, one reason,
  one `sources`**. `change` carries both resulting paragraphs as raw text.

  ! **THE REASON IS ATOMICITY RATHER THAN TIDINESS.** Filed as a separate `drop` and `add`, the
  halves can be judged separately -- and **half a move is a defect neither half reports**: prose
  deleted and never landed, or landed and never removed so the file says it twice. Nothing
  downstream would know the pair was meant to be one thing.

  ! **IT BINDS EVERY STAGE THAT HANDLES THE MARK.** Source-verification checks both ends and a
  failure at either refuses it; **reconciliation escalates a `move` WHOLE when either place
  escalates**, never settling one end; a role answering at revise answers for both, so there is no
  half `hold`; the write chain sets both paragraphs or neither. ! This turns
  [`collate-buckets-a-move-at-one-end`](../TODO/collate-buckets-a-move-at-one-end.md) from a bug
  report into a rule -- a `move` is grouped by every place it TOUCHES, because being seen at one is
  how half of it gets settled.

  ! **It does not change what a `move` COMPOSES with**: relocation and a truth-fix still compose.
  Indivisible means its own two halves travel together, not that it conflicts with everything.

  !! **THE FILE EXISTS BECAUSE THE SHAPE HAD NO OWNER, WHICH IS THE WHOLE MECHANISM.** It was
  described in `evidence/the-loop-measured-2026-08-27/the-mark.md`, a captured snapshot that
  **disclaimed itself** -- *"IT IS NOT THE SOURCE"* -- and pointed at `reviewer-brief.md` and
  `prototype/original/record.py`. **With no file able to refuse a field, the prototype's dataclass
  became the de facto spec.**

  ! **HOW IT ARRIVED, from the transcript rather than from memory.** A session was asked whether
  the mark type was usable and whether it needed a CLI endpoint. It began by naming `record.py`'s
  `--seed`/`--check` verbs and its checkers. **Roy interrupted mid-sentence** (`[Request
  interrupted by user]`), then ruled: *"You can copy it from there and update the rules/
  requirements from there but it doesn't belong in the new records.py. It belongs in the desk/."*
  **The only thing on screen was the ENDPOINT and the checkers** -- the `Instruction` dataclass was
  never shown, so no shape was approved. The port copied it whole, and **22 fields entered `src/`,
  NINE of which have no home in the approved shape.**

  !! **AND `update the rules/requirements` WAS AN INSTRUCTION TO UPDATE THEM.** Read as a licence
  to carry them across, it is the opposite of what it says. ! Roy: *"That is the shape that I
  approved going into this plan. I had not knowledge of the other shape."*

  ! **WHY NO REVIEW CAUGHT IT.** Three reviews ran over this code in one day, and each asked
  whether the gate matched the BRIEF's published key table -- it did. **None asked whether the
  classifier scheme had been approved**, because nothing stated what the approved set was. A review
  can only check the question it is given, which is [`gates.md`](gates.md)'s rule arriving at a
  design document instead of a test.

- **#38.** **AN ENUM MEMBER GETS NO SECOND NAME -- NO MODULE-LEVEL ALIAS, AND NO EXPANDING ONE OUT
  THROUGH A TUPLE** (Roy, 2026-08-28): *"aliasing like that is lazy and bad ... It allows for drift
  without the drift being apparent because of shadowing. That is a horrible practice."* And, on the
  same mechanism arriving a second way: *"It's also why I don't like sending enums through tuples
  to expand them out. It doesn't help and again causes shadows and lack of appropriate links."*

  !! **THE DRIFT IS THE ARGUMENT, NOT THE READABILITY.** An alias is a SECOND name for a value,
  bound once at import, and nothing afterwards holds the two together. A member renamed, a member's
  value changed, a second binding lower in the module, or an import shadowing the bare name -- each
  leaves the alias pointing at what the member USED to be, and every call site reading the alias
  goes with it. ! **NOTHING ANNOUNCES IT**: the name still resolves, the module still imports, and
  `ty` still passes, because both sides are the same type.

  ! **HOW IT SURFACED, and the shape is worth keeping.** `desk/stages.py` bound
  `EDITORIAL = Kind.EDITORIAL` beside `ENRICHING = Kind.ENRICHING`. A session showed Roy a bare
  `ENRICHING` while asking for a ruling; he read it as a module constant -- **and it was one**, as
  well as being an enum member. ! **THE MISREADING WAS THE MEASUREMENT.** He then answered about a
  constant and the session dropped the MEMBER, which is a wider change than the answer covered.

  ! **MEASURED at the time**: `stages.py` was the ONLY module in `src/` binding an alias. Fixed in
  `6d09796`; every site names `Kind.EDITORIAL` in full.

  !! **AND HALF THIS RULE WAS ALREADY WRITTEN DOWN, in `reading/series.py`.** `Definition` is a
  `NamedTuple` precisely so a series' kinds are reached as `.present` and `.absent`, and its
  docstring says *"NAMED, because `[0]` and `[1]` say nothing"*. `ADDRESSED`, `ABSENT` and
  `BY_LETTER` are DERIVED from the `Series` enum by comprehension -- *"DERIVED, NEVER LISTED"* --
  so changing a member carries them with it and no member gains a name.

  ! **SO THE TWO HALVES ARE:** do not reach into a tuple POSITIONALLY and lose what the slot means
  (`series.py` had this); and do not BIND a member to a second name at all (`stages.py` broke this).
  Both are the same defect -- a link that a reader, and a rename, cannot follow.

- **#39.** **A VERSION NUMBER IS A CLAIM ABOUT WHAT CAN SHIP, NOT A CHAPTER MARKER** (Roy,
  2026-08-28): *"We don't have an operational backend and until we do we can't ship this."* Every
  plan under 0.2.4 is the same release still being made; the number advances when what it names can
  be shipped, not because a branch feels like new work.

- **#40.** **THE PROSE THAT SHIPS IS UPDATED IN THE BRANCH THAT CHANGES IT** (Roy, 2026-08-28):
  *"Add the updated commands/words to the brief, agent files, and the instructions generator. We
  don't want to accidentally leave behind stuff this important."*

  ! **AND THE LANE LINE IS HIS**: *"How the agents function and the specific rules that are used to
  encourage the agents to do better is the agents lane. Giving them the information necessary to run
  the Python part is fine."* So a field name, a command, a key list, a generated table, and the fact
  that a role holds revise 2 rather than the original are `backend`'s. **How much deference an
  earlier stage's edit is owed is not.**

- **#41.** **A DEAD COMMAND IS DROPPED FROM AGENT PROSE, NOT MARKED DEAD** (Roy, 2026-08-28):
  *"Drop the commands from the brief and from the task agent/managing-editor ... We will fill the
  commands section back in later."*

  ! **THE ALTERNATIVE CONSIDERED WAS `CLAUDE.md`'s OWN TREATMENT** of these same commands -- leave
  them under a banner saying they moved. **Instructing an agent to run a command that does not exist
  is worse than saying nothing**, and a marked-dead command still spends the budget
  `docs/limitations.md` holds that file to.

  ! **THE CONSEQUENCE IS STATED RATHER THAN HIDDEN**: stage 4 then has no step emitting a role's
  vocabulary and stage 5 no citation gate. **Both were already absent from the code** -- the prose
  described a system that stopped existing on 2026-08-25.

- **#42.** **THE COPY CHIEF IS NOT IN 0.2.4** (Roy, 2026-08-28): *"I think not yet - the
  reconciliation step will pass stuff to it next."* Reconciliation and the revise step EMIT
  escalations and resolve nothing.

- **#43.** **`code_concerns` ON THE SHEET IS INDEFINITELY DEFERRED** (Roy, 2026-08-28): *"T1.6 is
  indefinitely deferred."*

  !! **SO IT LEFT THE PLAN'S TASK LIST INSTEAD OF SITTING IN IT UNCHECKED.** `CLAUDE.md` rules that
  an unchecked box says work remains, and that the release gate is EVERY BOX TICKED -- so an
  indefinitely deferred task left in P1 would not describe a pause, it would make 0.2.4
  unreleasable forever by arithmetic nobody chose. ! **A plan is one release's scope and CLOSES; a
  TODO's lifetime is indefinite.** *"Indefinitely deferred"* is a statement about lifetime, so the
  item belongs in the tracker built for it.

  ! **WHAT IT WAITS ON, named rather than left open-ended:** a file stating what the SHEET carries.
  `Process: #37` records what having no such file for the MARK cost -- eleven fields entered `src/`
  unapproved.

- **#44.** **A TASK BELONGS TO THE TODO WHOSE SUBJECT IT SHARES** (Roy, 2026-08-28, on
  `code_concerns` filed under `the-ported-mark-does-not-fit-the-brief`): *"It should not have been
  added to this todo."*

  ! **THAT FILE'S OBJECTIVE IS A GATE/INSTRUCTION DISAGREEMENT** -- a mark written from the brief
  VERBATIM refused by `desk/mark.py`. A new container on the SHEET is a different subject, and was
  already tracked in nine tasks on `code-concerns-cannot-carry-a-proposed-change`. **Misfiled AND
  duplicated.** ! It was checked as SUPERSEDED, not done: a superseded box keeps the record legible
  where a deleted one leaves no trace it was ever there.

- **#45.** **SOURCE-VERIFICATION DOES NOT RE-READ THE PAGE OR CHECK ITS SHA** (Roy, 2026-08-28):
  *"Too early for the strictness and the look up time each time."* Nothing ruled says a mark must be
  refused because its page moved, and asking costs a read per mark.

  ! **WHERE A STALE EDIT SURFACES INSTEAD** -- Roy, the same morning: *"copy-chief gets to see an
  update and compare through the normal proof-setter pass before it moves on and it can find the
  broken edits somehow."*

  ! **AND THE TWO BEST CHECKS ARE FREE**, because the paragraph is on the sheet as `raw_text`
  (`Vocabulary: #27`): *does the address resolve* and *is the quoted sentence really in it* need no
  file read at all. Only a `source` citing another file costs one, through a per-file cache -- the
  706 recorded marks carry 382 citations over 9 roots, so the reads collapse.

- **#46.** **THE ENUM TAKES `Instruction`; THE DATACLASS BECOMES `Row`** (`backend` lane, under
  `T1.15`'s dispatch, 2026-08-28 -- Roy has been told this ruling is the lane's own and may
  overturn it). `T1.15` asks the seven closed instruction names to become a `StrEnum`, and the
  word they want is already held by `desk/mark.py`'s dataclass, landed under that name by
  `Vocabulary: #17` before the enum existed.

  ! **`Row` IS NOT INVENTED -- IT IS THE SPEC'S OWN WORD.** `docs/the-mark.md` already calls its
  subject "four classifier columns" and "seven row flags", and its prose says "a row" and "the
  row" throughout rather than "an instruction". The rename does not introduce a term; it gives
  the dataclass the name its own spec already uses for it.

- **#47.** **FAN-OUT PARTITIONS BY FILE, AND THE REASON IS MEASURED DILIGENCE** (Roy, 2026-08-28):
  *"It makes them more efficient and we have measured that it makes them more diligent in actually
  inspecting the blocks, where they get overloaded on too many records. Because it is tight
  detailed work it matters for their role most."* And on the unit: *"By file because context should
  be more consistent. File thrashing would be bad."*

  ! **THE PARTITION IS REDUNDANCY-FREE BY CONSTRUCTION.** An address is `path@cue`, so one role
  marks a place at most once and `Pulled.set_by`'s `address -> role` stays unambiguous. Fan-out
  needs no extra identity. ! The overload fix is FEWER FILES per agent -- never a file split
  across agents.

- **#48.** **TOPOLOGY IS DATA, AND IT IS A TUNING KNOB RATHER THAN AN INVARIANT** (Roy,
  2026-08-28). The stage list moves from a literal in `desk/stages.py` to a run-scoped file, so
  all-concurrent, all-sequential and 4a-then-4c are three files and one code path.

  ! **THE SAME FINDINGS NEED NOT PRODUCE THE SAME PAGE UNDER EVERY TOPOLOGY.** Sequential
  genuinely differs: a later role reads text an earlier one already corrected, so it has less to
  disagree with -- which is the reason `ownership-context` runs first. Forcing equivalence would
  mean pretending reading order does not matter.

  ! **`backend` OWNS THE FORMAT, ITS VALIDATOR AND THE FAN-OUT; `agents` OWNS WHEN A STAGE RUNS
  AND WHY** -- `Process: #40`.

- **#49.** **A COMPOSITION OF EDITS MUST BE RE-READ; `clean` AND `query` ARE THE ONLY PASSES**
  (Roy, 2026-08-29): *"If two roles have a mark that edits a paragraph - I think we need to send
  the revision back to them because they could have fixed the same defect in different ways that
  then causes a new defect. To ensure that the reading still sticks together any composition of
  edits has to be re-read."*

  ! **THE PASS LIST IS ALREADY A COLUMN**: `owes_change` is False for exactly `clean` and `query`,
  so the rule is derived from the approved shape rather than invented.

  !! **AN `add` GOES BACK TO EVERY ROLE OF THE STAGE.** Roy: *"Or they could have duplicated the
  comment. An add on a new place is sent back to all of them."* ! An `add`'s blast radius is the
  PAGE, not the place: two `add`s at two addresses never meet under per-place grouping, so a
  duplicated comment passes every check. `ownership-context` decides which of several sites owns a
  repeated claim and `module-context` asks whether the comments say one thing -- and both ran
  BEFORE the added prose existed.

  ! **NARROW ACROSS SHARDS, ruled the same day**: all roles of the stage, and for a partitioned
  role only the shard holding that file. Cross-file duplication is not chased; it would cost the
  fan-out's whole benefit on any page carrying an `add`.

  !! **IT REACHES EXACTLY AS FAR AS CONCURRENCY DOES.** Across stages the composition is ALREADY
  re-read -- the next stage reads the revise. Within a stage it is not, and that is the hole.
  Sequential was safe by construction. ! Nothing already built changes: `pulls_revise`, the revise
  sheet and the four revise outcomes exist. **What changes is the trigger** -- composition and
  `add`, not only disagreement.

- **#50.** **A STAGE IS A LIST OF DISPATCHES, AND `carries` IS BUILT AS A HYPOTHESIS** (Roy,
  2026-08-29).

  !! **`paths` BELONGS TO THE DISPATCH, NOT THE STAGE.** MEASURED by writing the three topologies
  out: a stage fans ONE role out while leaving the others whole, and a stage-level `paths` cannot
  say that. **Two dispatches naming one role IS the fan-out.** The first draft of the format had
  `{name, kind, roles, paths}` and could not express the topology it was written for.

  !! **`reads` AND `carries` ARE DIFFERENT INPUTS.** `reads = "revise:N"` hands a stage the rebuilt
  tree with stage N's SETTLED corrections set -- corrected text, no marks, and a proposal that lost
  is invisible. `carries = ["N"]` hands it the binder PLUS stage N's `edit_copies` -- the proposals
  themselves, unsettled, so a later role can disagree with a SUGGESTION rather than with the
  applied result. ! Only `reads` is built (P2).

  !! **`carries` IS A HYPOTHESIS, NOT A FEATURE.** Roy: *"I would prefer the carries to be
  available. It is something that should be tested by the agents and testing lane on what allows
  for better answers. I think that giving the later roles information might help, but it might
  not."*

  ! **SO IT IS THE VARIABLE THE TWO-LANE RULE TURNS** -- `CLAUDE.md`: land the machinery with
  effectiveness UNCHANGED, then change what agents are told, then measure whether recommendations
  improved. ! **THE MEASUREMENT CANNOT RUN YET**:
  `TODO/the-harness-cannot-run-the-system-it-grades.md` is open and blocks both halves of that rule
  today, so whether carrying an `edit_copy` forward helps is genuinely unanswered.

  ! **THE VALIDATOR REFUSES A NON-EMPTY `carries` RATHER THAN IGNORING IT.** A key silently dropped
  is indistinguishable from one that worked.

- **#51.** **A COMMAND THAT LEAVES WORK UNDONE NAMES THE WORK AND THE COMMAND THAT CONTINUES IT**
  (Roy, 2026-08-30): *"There is some amount of the agents are having to do stuff. Just because we
  can put it in the flow doesn't mean the agents get notified that they should do more work or
  that there is something for them to do."*

  !! **AN AGENT LEARNS THERE IS WORK FROM THE RUN'S OUTPUT, NOT FROM A RULE IT IS EXPECTED TO
  REMEMBER.** A stage that settles 4 of 10 places has left six pieces of work; a report saying `4
  settled` and stopping has told nobody. The run must name what remains AND what to invoke.

  !! **THIS SETTLES THE ROUND CAP, WHICH WAS BEING ARGUED ON THE WRONG AXIS.** The question was
  read as *enforce it in code* against *state it as guidance*, and it is neither.

  | proposed | why it is not the answer |
  | --- | --- |
  | enforce a tally in the flow | **the loop cannot run away.** Nothing advances a round but a command someone invokes -- there is no daemon and no retry -- so carried state prevents an accident that cannot happen |
  | a sentence in `--help` | an agent reads `--help` when it does not know a command, not when it has just run one |
  | **the run's own report** | the agent is told, at the moment there is something to do |

  ! Roy, 2026-08-30, on the explicit act: *"It has to be an explicit step to do so instead of a
  built in part of the flow but it could be something as simple as -- If there are unresolved
  conflicts you can run this command twice to send the stuff back."*

  ! **AND IT MATCHES `Process: #22`'s ANTI-DECISION DECISION.** Sending a place back is an act
  someone is on record for. Machinery that silently permits or refuses a third round decides by
  default and puts nobody's name on it.

  !! **IT IS A RULE FOR EVERY COMMAND, NOT THIS ONE.** MEASURED 2026-08-30: `mark --check` prints
  `"12 ruled on, 0 left unruled"` (`commands/mark.py:106`) -- a count, naming neither the places
  left nor what to run next. **The whole middle is being built now, so the rule lands before the
  commands rather than after.**

- **#52.** **A REVISE IS ALWAYS PULLED, EVEN WHEN A STAGE SETTLED NOTHING** (Roy, 2026-08-30):
  *"The plan was to make a copy in a tempdir and run the write step so that they would get
  reference to the stage N edits and also pull a binder for the update."*

  !! **SO `reads: revise:N` ALWAYS NAMES A REAL TREE.** An empty docket yields a copy with zero
  overlays -- not a wasted one. **The revise is not only the edits**; it is the tree the next
  stage reads and the binder it is censused from, whose `read_from` names that revise.

  ! **A PROPOSAL TO REFUSE AN EMPTY DOCKET IS STRUCK.** It read *"nothing to set"* as *"nothing to
  do"*, which is wrong twice over: a stage settling nothing is an ORDINARY editorial outcome --
  three roles disagreeing on one page -- and the binder is owed either way.

  !! **AND `pull` BUILDS A BINDER TODAY THAT IT THROWS AWAY.** `flows/revise.py:241` binds the
  assembled root with `absent=True` for `assert_addresses_held`, then discards it; `Pulled`
  returns `root`, `revise`, `set_by` and `refusals` and no binder. ! **The gate's binder is not
  the stage's**: `absent=True` carries every empty place, which is what the address check needs
  and what a role must not be handed. So emitting one is a second bind rather than a return of
  what is already there.

  ! **THE COST IS REAL AND FILED.** `TODO/revise-copies-everything.md` measures a full copy at
  284MB per editorial stage on this repo. **That is an argument about what `pull` copies, not
  about whether it runs.**

- **#53.** **`Vocabulary: #11` NAMES `collator.py` AND RULES NOTHING ELSE** (Roy, 2026-08-30):
  *"verdicts.py is retired in the prototype and it is broken. The only true statement it should
  carry is that we picked the name collator.py to be the thing that brings the marks back
  together. And puts them in a format ready for comparison."*

  !! **SO THE MODULE'S OWN HEADER OVERCLAIMS.** `desk/collator.py` states *"THE COLLATOR RULES ON
  NOTHING ... it never judges which mark is right, never renders the composed text, and never
  reads a file"* and cites `#11`. **`#11` says none of that.** It rules that `verdicts.py` was not
  the copy chief and that the rename goes to `collator.py`; every other clause describes how the
  module happened to behave, written in the register of a constraint.

  !! **AND IT WAS USED AS ONE, TWICE IN ONE CONVERSATION.** A session quoted the docstring as a
  design boundary, concluded a COMPOSE could not live in reconciliation, then cited `#11` as the
  authority behind it -- a ruling about **retired, broken prototype code**. ! **Composing two
  edits on disjoint spans is ARITHMETIC, not judgement**, so nothing in `#11` forbids it.

  !! **THE STANDARD, AND IT IS GENERAL.** Roy: *"lets be careful to validate that the functions in
  it are necessary and appropriate for the design we have laid out and that we are not forcing the
  design to meet imaginary constraints from the collator.py because collator.py can change and
  probably ought to change. **Making the design fit to collator.py is not the way.**"*

  ! **A CLAIM IN A FILE IS A CLAIM TO VERIFY, NEVER A CONSTRAINT TO OBEY** -- this repo's whole
  remit, arriving from the inside. A module naming retired machinery pulls a reader's reasoning
  toward a design that no longer exists.

- **#54.** **THE MARK ANSWERS FOR ITSELF; EVERYTHING ABOUT THE SET IS THE COLLATOR'S** (Roy,
  2026-08-30): *"A mark problem is did this parse back correctly does it still contain the correct
  stuff."* Coverage is not that.

  | question | whose |
  | --- | --- |
  | is this one mark well-formed, and does it still hold the right fields | **`desk/mark.py`** |
  | did every place get ruled on, is each mark TRUE of the tree, what do they say together | **`desk/collator.py`** |

  !! **SO `unruled`, `problems_in` AND `tally` ARE MISFILED.** They live in `flows/marks.py` and
  ask *did everyone rule on everything* -- a collator question wearing a flow's address. All three
  are called only by `commands/mark.py`.

  ! **`desk/mark.py` CANNOT ANSWER A COLLATOR QUESTION AND THE IMPORTS PROVE IT**: it imports
  `re`, `dataclasses` and `enum`, and nothing else. No binder, no page, no filesystem. `parse`
  rules on an entry alone, which is why **the five verification functions are not made redundant
  by it** -- a role can write a flawless mark quoting a sentence that is not in the paragraph and
  citing a file that does not exist. **They are UNWIRED, not unnecessary**, which is worse,
  because their tasks are ticked.

  !! **AND THE MIDDLE VERIFIES WHAT IT IS HANDED WITHOUT EVER VERIFYING THAT IT WAS HANDED
  EVERYTHING.** Three coverage questions have no code at all:

  | | |
  | --- | --- |
  | **stage** | did every dispatch the topology named return an `edit_copy`? `gather` counts nothing |
  | **shard** | did a partitioned role answer for every file in its shard? `fan_out` refuses at DISPATCH; nothing checks the RETURN |
  | **address** | is every docketed address one the binder carried? `known_addresses` exists, and only `flows/revise.py` uses it, for a different question |

  ! **`collate` IS THE FIRST THING THAT SEES A WHOLE STAGE AT ONCE**, so it is where they belong.
  ! And `Process: #51` already requires a command to name what remains, which it cannot do without
  counting.

  ! **THE MOVE LANDS WITH THE FLOW, NOT BEFORE IT.** `Process: #12` has a command expose a FLOW,
  so `mark --check` reaches these through `flows/collate.py` rather than importing `desk/` --
  which is what it does today via `flows/marks.py`.

- **#55.** **THE TOPOLOGY IS VERIFIED BY A COMMAND THE AGENT RUNS, AND THE COMMAND ALSO BUILDS
  IT** (Roy, 2026-08-30): *"this is actually pretty simple because an agent does the actual
  running of the system, we need a command like `topology --verify` which errors out if it is
  broken. Then the task agent verifies that the setup is correct and has the correct
  pieces/specifications before running the whole system across the pages. topology should also
  have the tools for the agent to correctly specify the order and the splits and the topology
  based upon the directives given."*

  !! **IT RESOLVES A PLACEMENT THAT LOOKED LIKE A DILEMMA.** `topology.read(text)` sees `tomllib`
  and `desk/stages.py` and nothing else -- **no tree, no binder** -- so it cannot know whether a
  glob matches a page. Two bad answers were on the table: give `read` a second parameter, breaking
  the `read(text) -> (thing, error)` shape `binder.read` and `docket.read` both hold; or add a
  free function nothing forces a caller to run, **which is exactly how five verification functions
  came to be built and unwired.**

  ! **A COMMAND HAS A REPO, AND AN AGENT INVOKES IT.** So `read` keeps ruling on the file's own
  shape, and the command rules on whether that topology fits THIS checkout. Nothing needs a
  parameter it cannot use, and nothing waits to be remembered.

  !! **AND IT IS NOT A FLAG ON A COMMAND -- TOPOLOGY IS ITS OWN CONFIGURATION SYSTEM.** Roy, the
  same day: *"What I am really saying is that topology is its own configuration
  workflow/command system."* It configures a RUN, the way the board tool configures work: a
  surface of its own, with a workflow the agent follows before any page is read.

      directives  ->  BUILD a topology     which roles, in what order, split how
                  ->  VERIFY it            against this checkout, errors when it does not fit
                  ->  only then run        distribute / collate / pull, stage by stage

  !! **THE AGENT DOES NOT HAND-WRITE TOML.** It is given directives and needs a topology that
  satisfies them, so the tool that reads the format is the tool that writes it -- and the same
  tool says whether what it wrote fits the tree it will run against.

  ! **THE WORKFLOW IS THE POINT, NOT THE VERB.** A run that starts against an unverified topology
  fails partway, after roles have already read and filled their copies. Verification before the
  first page is read is what makes a bad configuration cost nothing.

  ! **MEASURED, and it is why this surfaced:** `tests/fixtures/topologies/4a-then-4c.toml` refuses
  any tree but this repo's -- its globs name `src/comment_review/reading/*.py` and
  `.../binder/*.py`, so a scratch tree raises `UncoveredPage: block-context: no dispatch covers`.
  **The refusal is correct** -- fan-out must cover every page -- but it surfaces from `fan`,
  blaming the tree for the topology's assumption, and only once a run is already underway.

- **#56.** **A `move` IS A COMPOSITE MARK -- A DROP AT THE ORIGIN AND AN ADD AT THE DESTINATION**
  (Roy, 2026-08-30): *"A move needs to be what it is and that is a composite Mark - Drop Here Add
  There. They have to go together and the ought to have a similar facade but the underneath I don't
  know how we make it work correctly without admitting that it is a composite instead of a singular
  mark. Nothing else acts on two places at once"*

  !! **THE FACT THAT FORCES IT: A SENTENCE MOVES WITHOUT THE PARAGRAPH MOVING.** Roy, correcting a
  reading that an address names one paragraph so a move empties its origin: *"No a sentance can move
  without the paragraph moving"*. **The origin keeps a REMAINDER.** Both ends therefore hold new
  text, and both must be written -- which is what `#49`'s composite requirement already implied and
  no code does.

  !! **AND `drop` DECLARES A SENTENCE LEFT, NOT A PARAGRAPH -- WHICH MAKES IT CHECKABLE.** Roy, the
  same day: *"And for drop - remember it is just declaring that a sentance disappeared not the whole
  paragraph - it is checkable that the difference is missing and not an addition..."* So the origin
  half is verifiable as a PURE DELETION against its seeded `raw_text` -- an insertion anywhere in
  that diff refuses the mark -- and the destination half as a pure addition.

  ! **THE PAIR CARRIES THE STRONGER CHECK: the text deleted at the origin must EQUAL the text added
  at the destination.** A move that loses a sentence in transit, or invents one on arrival, fails
  it. `results/differences.py` already holds the opcode machinery this runs on.

  !! **MEASURED 2026-08-30: THE CODE CANNOT EXPRESS A CORRECT MOVE AT ALL.**
  `desk/mark.py:536` refuses any `change` that is not a `str`, for every instruction, while
  `the-mark.md`'s claim table says a `move`'s `change` carries the same two key names as its claim,
  holding the two resulting PARAGRAPHS. **The specified shape is refused at the boundary, and the
  single string that is accepted is wrong by construction** -- it reaches the docket as a whole-file
  delete at the origin and both paragraphs written at the destination.

  ! **`change_all` WAS THE CLASSIFIER THAT CARRIED THE DICT-SHAPE CHECK, and it was removed on
  2026-08-29 with the raw-text ruling.** That ruling was aimed at LINE ARRAYS -- *"raw text not
  lines or sentences"* -- and took the dict form with it, unremarked, because `move` is the only
  instruction that used one. `TODO/move-change-contract-unenforceable.md` was filed against the
  older shape and names a field that no longer exists.

  ! **NOTHING IN THE SUITE DISAGREES, BECAUSE THE FIXTURE BUILDS THE ACCEPTED FORM.**
  `tests/helpers.py`'s `a_move` gives its claim the correct `from`/`to` places and its `change` a
  plain string, so every move test confirms the shape the boundary happens to admit.

  !! **AND THE COMPOSITE IS THE SMALLER CHANGE, NOT THE LARGER ONE.** Two bound marks each carry a
  plain `str` change, so `_change_problems` stays ONE rule for all seven instructions and no
  downstream stage learns that one instruction's `change` is not text. The alternative -- restoring
  a dict branch -- teaches every stage a second shape and leaves atomicity a property prose asserts
  rather than one the structure holds.

  ! **IT SUPERSEDES `the-mark.md`'s *"Both raw text, in one `change`"*,** and leaves `#49`'s
  indivisibility rule standing: the two halves still travel together, and now there is one object
  that cannot be half-held.

- **#57.** **A CONTAINER STATES WHAT MAY BE CONTAINED AND ERRORS OUT, AND IT IS WIRED** (Roy,
  2026-08-30, asked whether `desk/containers.py` should be wired, given a reporting boundary
  beside it): *"yes because the system is broken without it. It may not error but it also is not
  protected from future errors which the containers are an explicit statement for what is
  contained and what can be contained or errors out"*

  !! **MEASURED 2026-08-30: `desk/containers.py` HAD NO PRODUCTION IMPORTER.** It declared
  `Sheet`, `EditCopy`, `MasterProof` and their parses while `desk/collator.py` hand-rolled its own
  `isinstance` checks with its own definition of a valid copy -- **two definitions, one of them
  reached by nothing.**

  !! **AND IT RESOLVES THE REFUSE-VERSUS-REPORT TENSION BY LEVEL, NOT BY PRECEDENCE.**
  `parse_edit_copy` REFUSES while `flows/collate.py`'s `problems_in` REPORTS and continues, and
  that looked like two contracts competing for one boundary. It is two boundaries: **a container
  guards the ENVELOPE** -- is this document the shape a copy must be, or does it error out --
  **while `problems_in` rules on the CONTENTS**, so each per-mark problem routes back to the role
  that wrote it. Neither answers the other's question.

  ! **THE ARGUMENT IS ABOUT FUTURE ERRORS, NOT PRESENT ONES** -- *"It may not error but it also is
  not protected"*. A shape nothing states is a shape every consumer re-derives, and the
  re-derivations drift silently because each one is locally correct.

- **#58.** **`desk/collator.py` IS NOT SPLIT; ITS SOURCE-VERIFICATION HALF IS WIRED INTO THE
  FLOW** (Roy, 2026-08-30, asked whether the module's *"SOURCE-VERIFICATION and RECONCILIATION"*
  title warranted a split): *"Nope the source-verification side needs to be wired into the flow -
  same as 1) the flow coordinates the things in the modules do"*

  !! **MEASURED 2026-08-30: `verify_report` HAS ONLY TEST CALLERS.** `grep -rn "verify_report"
  src/ tests/` returns five prose mentions inside `collator.py` itself and six call sites, all in
  `tests/test_collator.py`. So `address_problems`, `claim_verbatim_problems`, `source_problems`,
  `source_verification` and `verify_report` are reached by tests and by nothing in production.

  !! **AND THIS IS WHERE THE *"NEEDS AN AND"* HEURISTIC POINTS THE WRONG WAY.**
  `module-context`'s tell -- a docstring that cannot describe itself without *and* -- read as
  evidence for a split. The defect was the opposite: **a module half with no caller READS like a
  second module**, because nothing in the running system ties it to the first. The fix is a
  caller, not a boundary.

  ! **THE RULE UNDER IT IS THE FLOW'S REMIT:** *"the flow coordinates the things in the modules
  do."* A module may own a job without owning the decision of when it runs. An unwired half is a
  coordination defect, and moving it to a new file would have left it exactly as unwired.

- **#59.** **`desk/mark.py`'s LEAVES COME OUT** (Roy, 2026-08-30, asked whether the module's four
  subjects at one scope warranted a split): *"Yes pull out the leaves out of mark.py"*

  ! It is the same shape as `#54` -- the mark answers for ITSELF and the collator answers for the
  SET -- applied one level down, inside the mark's own file.

- **#60.** **A MOVE GETS ITS OWN SPOT IN THE EDIT COPIES, AND ITS DESTINATION IS NOT SEEDED**
  (Roy, 2026-08-30, asked whether a move's destination place must be seeded so drift is
  detectable at both ends): *"no - separate semantics - will have to make a special spot in the
  edit-copies for move marks because even one level up they are out of sync with what they state
  they do"*

  !! **AN EDIT COPY IS ONE SLOT PER PLACE, AND A MOVE SPANS TWO.** So the defect is not only in
  the mark -- **one level up, the container's own statement of what it holds is false for a
  move.** Seeding the destination would have forced a two-place ruling through a one-place slot,
  which is the shape that produced every measured move defect in `#56`.

  ! **IT IS WHY `#57` AND `#56` ARE ONE PIECE OF WORK.** A container that states what may be
  contained cannot state it correctly until there is a region for the one instruction that acts
  on two places at once. Filed as task 9 of `TODO/move-is-a-composite-mark.md`.

- **#61.** **THE TWO BACKTICK PATTERNS ARE TWO DEFINITIONS, AND THE WHITESPACE DIFFERENCE IS
  DELIBERATE** (Roy, 2026-08-30, asked whether `desk/mark.py`'s `ANCHOR_NAME` and
  `binder/annotate.py`'s `TICKED` should be one definition): *"annotate.py was about finding
  references in documentation for the agents. It was about building an index like you would find
  in the back of a book. I had to be looser with the answer than other thing because Spaced out
  words or not could have been used in doc strings"*

  | | asks | pattern |
  | --- | --- | --- |
  | `TICKED` | what does this documentation REFER to -- the back-of-book INDEX the agents read | `` `([^`\s]+)` `` |
  | `ANCHOR_NAME` | did this role NAME a declaration when it filed an `add` | `` `[^`\s][^`]*` `` |

  !! **SO A SHARED PATTERN WOULD HAVE BEEN THE DEFECT, NOT THE FIX.** They answer different
  questions, and the repo's one-name-per-thing rule cuts the other way here: two jobs need two
  definitions. ! What was missing is **a sentence in each saying which question it answers** --
  without it, the next reader finds two backtick regexes and assumes one drifted, which is the
  reading this entry exists to prevent.

  ! **IT IS A COUNTER-CASE TO `Vocabulary: #11`'s DIRECTION**, and worth keeping beside it: one
  name per thing is about NAMES, not about every pattern that happens to match similar text.

  !! **CORRECTED 2026-08-30, THE SAME DAY: THIS ENTRY RECORDED A RULING WIDER THAN THE ONE
  GIVEN.** Roy ruled on `TICKED` -- what `annotate.py` is for and why it had to be loose. He
  did not rule that `ANCHOR_NAME` is its deliberate counterpart. Roy: *"The ANCHOR_NAME had
  no anchor to what is was talking about. I gave you the reason it was the way it was not
  because I knew what where it was in the code or what it was doing. If I had known that
  something like that had slipped from the v0.2.2 prototype into here I would have had you
  drop it."*

  !! **MEASURED: `ANCHOR_NAME` IS PROTOTYPE RESIDUE.** The pattern is byte-identical to
  `prototype/original/record.py:296` and entered `src/` in `67dc82b`, *"the mark comes back
  into `desk/`"* -- carried across during the port rather than designed for this system.
  `TODO/the-ported-mark-does-not-fit-the-brief.md` is the file for that class.

  ! **SO THE TABLE ABOVE STANDS FOR `TICKED` AND NOT FOR `ANCHOR_NAME`.** The two patterns do
  answer different questions; what was never ruled is that BOTH should exist.
  `docs/superpowers/specs/2026-08-30-the-move-composite-design.md` deletes `ANCHOR_NAME` with
  `add`'s claim anchor, which is a second anchor on a mark that already carries a seeded one.

  !! **THE ERROR SHAPE IS `Vocabulary: #11`'s, ARRIVING WHILE THAT ENTRY WAS BEING CITED.** A
  ruling was given about one thing, recorded as settling two, and would have been quoted as
  authority for keeping a field nobody had examined. ! The question that produced it asked
  *"one definition, or two with declared different jobs?"* -- a form that offers no answer
  meaning *neither; look at where this came from*.

- **#62.** **THE MIDDLE TOUCHES NO FILES, SO NOTHING IN IT ASKS WHETHER A PAGE CHANGED** (Roy,
  2026-08-30, on a proposal to answer drift with the page's `sha`): *"That is also a completely
  unnecessary check at this stage. I don't know how many times i have to say this because you
  forget to write it down -- but the middle doesn't care if the pages have changed - it is not
  reading or writing to the pages at all. The edit process moves data in json files or memory
  nothing in the actual files. That check and the idea came from when the prototype didn't know
  how to write to and address or compose a page and so it tried to edit while it was going and it
  was Broken."*

  !! **THE MIDDLE'S WORLD IS JSON AND MEMORY.** Its inputs are a binder and the returned
  `edit_copy`s; its output is the copy chief's `edit_copy` and, downstream, a docket. **No page is
  opened, and none is written.** Reading and writing pages belongs to the ends of the chain --
  `census` at one, the write chain at the other.

  !! **SO DRIFT DETECTION IS UNNECESSARY AT ANY GRANULARITY, AND `drift_in` GOES.** Comparing a
  returned `raw_text` against the base asks whether the tree moved under a role, and the middle
  has no stake in that answer: it is not editing the tree. ! A `sha` comparison is the same
  question asked more cheaply and is refused for the same reason.

  ! **THE IDEA IS INHERITED FROM A BROKEN PROTOTYPE.** It edited as it went, because it could not
  address or compose a page -- so it had to care whether the file under it had moved. Nothing in
  the current design does.

  !! **MEASURED THE SAME DAY, AND IT COST A FIX IN THE WRONG DIRECTION.** A review found `drift`
  never affected the exit code, and a fix round was dispatched to give it one -- `ac8cbbd`. **The
  finding was real and the fix was wrong at the root**: the check should not exist, so making its
  outcome louder entrenched it. ! The reviewer could not have known; nothing in the tree said the
  middle touches no files, which is why this entry exists rather than a note on that commit.

  !! **QUALIFIED THE SAME DAY: "NO FILES" MEANS NO PAGES UNDER REVIEW. EVIDENCE IS READ.** A
  `sources` citation points at a file to show a claim is settled somewhere, and checking it
  means opening that file. Roy, 2026-08-30, asked whether that contradicts this entry: *"a
  sources citation points at evidence, which may be any file. Reading evidence isn't editing
  a page ... Yep forgot this but then I bet the agents grep this stuff anyways. They are also
  not sha'd because the evidence pages are not modifying data."*

  !! **AND THE TEST IS MECHANICAL, NOT A JUDGEMENT: THE `sha`.** A page under review carries
  one in the binder BECAUSE IT WILL BE WRITTEN. An evidence file carries none, because nothing
  writes it. **So the scope of this rule is readable off the binder** rather than argued case
  by case: what has a `sha` is what the middle must not touch.

  ! **THE ROLES ALREADY READ EVIDENCE**, which is why this is a qualification rather than a
  new permission -- a reviewer greps a cited file to settle a claim during its own review, and
  `desk.collator.source_problems` doing the same in the flow adds no kind of access the run
  did not already have.

  ! **SO `verify_report` BELONGS IN THE FLOW** and `Process: #58` stands unchanged.
  `docs/superpowers/plans/2026-08-30-wire-the-containers.md` Task 3 was held pending this
  answer and proceeds.

- **#63.** **COVERAGE IS REPORTED, NOT REFUSED, AND ITS EXPECTATION IS THE STAGE** (Roy,
  2026-08-31, ruling on SP-2's scope). `P26` had been written as *"refuses or reports"* and
  `P27` as a bare *"is named"*, which left the behaviour undecided in the plan itself.

  !! **A MISSING ANSWER IS A PROBLEM THAT ROUTES, NOT A REFUSAL THAT VOIDS THE ROUND.** A role
  that returned nothing, or that answered for three of the four pages in its shard, is named
  and the places that DID come back still settle. ! It follows the standing rule that errors
  stack and each be read off and sent back to the role that owes it -- **and finding #6 of the
  2026-08-30 review is what makes refusing here expensive**: `commands/collate.py:135` catches
  around the whole `collate()` call, so any raise discards every `Problem` the fold already
  computed. Adding a third refusal to that boundary would have widened a measured defect.

  !! **SHARD COVERAGE NEEDS NO NEW INPUT, WHICH IS WHAT SHRANK THIS STEP.** `collate` already
  takes the binder, and it must be the WHOLE binder -- `base_texts(binder)` needs every address,
  so it cannot be a shard. `P27` is therefore `flows.fan_out.fan`'s own `UncoveredPage` check run
  over the RETURN instead of the DISPATCH: per role, the union of its copies' sheet paths against
  the binder's pages.

  !! **STAGE COVERAGE CANNOT BE ANSWERED THE SAME WAY, BECAUSE AN ABSENT COPY LEAVES NOTHING
  BEHIND.** `flows/distribute.py:80-86` stamps a copy with `role`, `read_from` and `sheets` and no
  dispatch identity, so a role that returned nothing is indistinguishable from a role that was
  never asked. **`collate` takes the `Stage`**, and the topology is the right authority because it
  IS what `fan` partitioned -- `P32` makes it verified against the tree before a page is read.

  ! **THE COST IS NAMED RATHER THAN DISCOVERED: A REVISE ROUND RE-SENDS ONLY THE ROLES WITH
  UNRESOLVED PLACES**, which is a shorter list than the topology's. SP-5 narrows the expectation
  when it builds that round; until then there is no second round to over-expect for.

  ! **STAMPING THE SHARD ONTO THE COPY WAS CONSIDERED AND DOES NOT ANSWER THIS.** It would answer
  `P27` and would fix the `unruled`/`tally` clobber under fan-out (finding #9), but it cannot
  answer `P26` at all, for the reason above. It stays available as the fix for #9.

- **#64.** **A CONTAINER IS WRITTEN THROUGH ITS TYPE, THE WAY A MARK IS** (Roy, 2026-08-31,
  ruling on SP-2's scope). `Sheet`, `EditCopy` and `MasterProof` get `seed` classmethods built
  from the dataclass's own field names, and the literal spellings at their producer sites go.

  !! **IT IS THE DEFECT `Mark.seed` ALREADY CLOSED ONE LAYER DOWN.** `desk/mark.py:329-332`
  records it: the write half of the round trip did not live with the read half until 2026-08-30,
  so renaming a field left another module writing the old key and **nothing could notice** --
  `parse` would simply find the field absent. MEASURED 2026-08-30 in the review: renaming
  `Sheet.sha` leaves `parse_sheet("s", {"path": "m.py", "marks": []})` returning
  `Sheet(path='m.py', sha='', marks=())` with `problems=[]`, where `Mark.seed` raises
  `AttributeError` at the point the row is built.

  ! **THE PRODUCER SITES ARE `flows/distribute.py`, `flows/collate.py` AND `desk/proof.py`.**
  `desk/collator.py` writes no container -- its `path`/`sha`/`role`/`alterations` page is a
  DOCKET page, which is a different artifact and keeps its own spelling.

  ! **`desk/containers.py` DECLARES *"THE TYPE IS THE DEFINITION AND THERE IS NO MARKDOWN
  SOURCE"* AT `:10`**, and shipped three parsers and nothing that writes. The claim is what this
  ruling makes true rather than aspirational.
