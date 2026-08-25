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

- **#12.** **A library module does one job and has no CLI; a flow calls libraries; a command
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
  *"there was the git stuff which is io"*). **`code_names` and `referrers`' library half are
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
