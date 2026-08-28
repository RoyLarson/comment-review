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
