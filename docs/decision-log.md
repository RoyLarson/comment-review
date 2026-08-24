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

  !! **IT COMPOSES MECHANICALLY IN THE SYNTHESIS ORDER; ONLY A CONTRADICTION STOPS IT.** Roy:
  *"multiple answers can be true, not just either this or that ... where things do not conflict
  and come back clean that is probably a single transform."* The copy chief writes text only
  where two marks genuinely contradict.

  !! **AND EVERY MARK IS NAMED OR THE RUN REFUSES.** The artifact carries address -> text -> the
  marks it answers. ! Without that, the step between the proof and the galley is where a finding
  can vanish with nothing to show it was raised.

  ! The name is unsettled and is Roy's: `TODO/nothing-makes-the-fair-copy.md` T1 uses **fair
  copy** as a working candidate only, on `CLAUDE.md`'s rule that the name comes last.
