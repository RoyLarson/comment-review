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
  editing do not allow it."*). Tried three times -- `b8e3348`, `bb2be6c`, `1728d8a`. Two things
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
