# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code **plugin** (`comment-review`) plus the machinery used to develop and measure it.
The plugin is an editorial board for the comments and docstrings a change touched: four
read-only reviewer agents walk one page, a task agent (the `/comment-review` skill)
synthesizes instructions, the human approves the exact replacement text, and WRITE puts it on disk and
proves the executable code byte-identical.

!! **AND THE SUBJECT IS THE DESIGN AS MUCH AS THE WORDING.** A comment says what code is FOR,
so checking it against what the code DOES is a check on the structure. Where the two disagree
and the code is right, the comment is corrected; where the CODE is what is wrong, the role
raises a code concern and does not bend the prose to fit.

! **A ROLE CANNOT PROPOSE THE CODE CHANGE, AND THAT COSTS SOMETHING MEASURED.** Roy,
2026-08-23: *"we can't tell the agents to review all of this and not give them an out for
properly resolving the issues. Several times they were overly restricted by what they could do
and that caused tension in the recommendations."* The harness records the shape:
`module-context` found a module announcing one subject while holding four, had no instruction for
*split this module*, and widened the docstring to announce TWO -- the defect its own trigger is
named for.

!! **TWO LANES, AND THEY ARE SEQUENCED BECAUSE OF THE MEASUREMENT, NOT THE FILING.** Roy,
2026-08-23: *"it has to be landed in the code, tested that the effectiveness didn't change, and
then change the agents to tell them they can use it. Verify that it improved the
recommendations."*

| order | file | lane | pass criterion |
| --- | --- | --- | --- |
| 1 | [`code-concerns-cannot-carry-a-proposed-change`](TODO/code-concerns-cannot-carry-a-proposed-change.md) | `backend` | effectiveness **unchanged** -- the machinery is the CONTROL and no agent file is touched |
| 2 | [`a-role-with-no-code-out-damages-the-prose`](TODO/a-role-with-no-code-out-damages-the-prose.md) | `agents` | recommendations **improve** against the baseline step 1 established |

! **SHIPPING BOTH AT ONCE DESTROYS THE ATTRIBUTION.** A movement in the output could be the
SHAPE or the INSTRUCTION, and nothing separates them after the fact -- so the question the
second half exists to answer cannot be asked. ! Both comparisons need a grader, which is why
step 1 is blocked on [`the-harness-cannot-run-the-system-it-grades`](TODO/the-harness-cannot-run-the-system-it-grades.md).

### !! WHY IT EXISTS: A GREEN GATE IS NOT EVIDENCE OF A GOOD RESULT

Roy, 2026-08-18: *"Just because the code passes -- even if it has gone through multiple rounds of
simplify and code-review -- doesn't mean that the code is good, that it has the right structure,
the right documentation and the right reasons why things are the way they are."*

!! **MEASURED, on a real run.** A tree carrying **31 reader-visible defects** while every
mechanical gate was green: `prove_unchanged` 23/23, the hygiene guard 19/19, **2,413 tests
passing**, every citation resolving, the residue check clean. Stage 8 -- a reader, not a checker
-- is what found them.

! **THE PACKAGE THAT RECORDED THAT RUN IS NOT IN THIS TREE**, so the numbers above are a
measurement you cannot re-derive here. They are kept because they are specific enough to be
checked against a NEW run, which is the only thing that would settle them either way -- and
because the corroborating case below was measured on this repo and can still be read.

! **The gates were not wrong; they were answering a different question.** Each says the code still
parses, still runs, still says what it said. None can say whether the prose beside it is TRUE, or
whether a reader would learn the reason a thing is the way it is. That gap is the whole remit of
the four editorial roles, and it is why this is a reviewer rather than a linter.

! **Corroborated on this repo, 2026-08-18**, with 519-534 tests green throughout: `verdicts.py` admitted
a citation whose `verbatim` was `null`, because it rendered as the word "None" and the cited line
happened to contain it; `payload_problem` admitted a claim key that was present and empty, and
every check that would have caught it then skipped; the brief generator imported a table from a
module that no longer defined it, passing only on an accidental re-export; and the backlog index
listed eight finished TODOs as open. **Every one was found by reading, and none by a gate.**

!! **AND A GATE CAN BE GREEN BECAUSE IT SHARES THE DEFECT** -- a different failure from answering
a different question, and the one that looks most like success. **MEASURED 2026-08-21**: the
round-trip identity, the strongest check in this tree, scored **699 of 699 across ten languages
on its first run while 157 addresses were held by two paragraphs each**. It rebuilt each file
from the line positions it had just read out of that file, so it could not disagree. It began
finding things one commit later (`7c9ad96`), when it was made to set from the CUES instead.

! **[`docs/gates.md`](docs/gates.md) holds that case and the rule it produced**: *"does the check
pass" is not the question; "could the check fail" is* -- plus the three ways a green run means
nothing, and what to ask before trusting a new check.

The repo root is **not** the plugin. Only `plugins/comment-review/` ships to a user's
`.claude/`; everything else (`docs/`, `evidence/`, `evals/`, `corpora/`, `scripts/`) is
development and measurement tooling that stays behind.

!! **AND `plugins/` IS BUILT, NOT WRITTEN, since 2026-08-24.** The Python lives in
**`src/comment_review/`** and `scripts/build_plugin.py` copies it WHOLESALE into the skill --
sub-packages intact, because Roy ruled the shipped tree takes the same shape as the source.
**Edit `src/`; `plugins/*.py` is output.** What does NOT come from `src/` is the prose an agent
reads: `agents/*.md`, `SKILL.md` and `references/*.md` are written in place, and only
`references/vocabulary.toml` moved into the package, because code reads it.

## Commands

!! **RUN EVERYTHING THROUGH `uv run`.** The project is pinned to **Python 3.11**, the floor
`plugins/` ships against, in `.python-version` and `[project] requires-python`. Measured
2026-08-17: with 3.14 as the ambient interpreter, four of the eight shipped scripts raised
`NameError` at IMPORT on 3.11 while every test and the shipped-syntax gate passed -- PEP 649
makes annotations lazy from 3.14, so the break was invisible locally. Roy: *"the floor will not
fail if we are using the floor to evaluate the code."* Substituting a bare `python` re-opens
exactly that gap.

```bash
# Run the census (stages 2-3 of the skill) over one or more files
uv run python src/comment-review.py census --repo . <paths...>
uv run python src/comment-review.py census --languages   # list known languages

# Materialise the pinned corpora (git worktrees / clones into corpora/<name>/, gitignored)
uv run python scripts/fetch_corpora.py                 # fetch everything missing
uv run python scripts/fetch_corpora.py --list          # print the manifest only
uv run python scripts/fetch_corpora.py --only numpy pymc
uv run python scripts/fetch_corpora.py --clean sentry --only sentry   # refetch one

# !! THERE IS NO END-TO-END GRADE. `grade_hazards.py` and the twelve planted
# hazards are not in this tree: they were tied to a corpus this repo cannot ship.
#
# ! The rule they enforced stands and has nowhere to run: GRADE FROM THE DIFF,
# NEVER FROM THE RUN'S OWN REPORT -- self-reported confidence was measured not to
# discriminate a real finding from a fabricated one.
#
# ! Rebuilding it means RESTATING each hazard -- naming the failure precisely
# without copying the code it was found in -- and planting the set on one of the
# public corpora below. Tracked in
# `TODO/the-harness-cannot-run-the-system-it-grades.md`.

# Split a corpus's prose defects by whether the introducing commit carries an assistant trailer
uv run python evals/generator_split.py <corpus-dir> [paths...]

# Survey GitHub for assistant-authored repos to extend the corpus
uv run python scripts/find_llm_repos.py --pages 3 --min-hits 2

# Run the test suite. PYTEST, and only pytest.
uv run pytest -q                    # 1260 passed, 1 skipped, 3 xfailed, 537 subtests, ~11s
                                    # measured 2026-08-29 on `feat/the-mark-and-the-collator`;
                                    # it read `873 ... 451 subtests, ~1.6s` until then, which is
                                    # the set BEFORE the mark, the collator and the topology
                                    # the skip needs symlinks; it runs where they exist.
                                    # ! THE SUBTEST COUNT MOVES WITH `TODO/`: three per
                                    # open file, from `tests/gates/test_todo_counts_agree.py`
uv run pytest -q -k galley          # one file, one class or one test

# !! THE SUITE WAS REPLACED WHOLESALE ON 2026-08-25, and the rule above it --
# *"BOTH RUNNERS WORK and neither is going away"* -- went with it. Roy: *"Delete
# the old test suit put in the new one."* The new suite is written in plain
# pytest, so `unittest discover` now finds only `tests/gates/`, which are still
# `TestCase` classes. ! THAT IS A CONSEQUENCE OF THE INSTRUCTION, not a decision
# taken alongside it: Roy asked for *"standard pytest stuff"*.
#
# !! WHY THE OLD ONE WENT: 866 tests, and THREE changes on 2026-08-24 that each
# broke something real were noticed by ZERO of them -- fences reaching agents,
# eleven fields leaving the row, and a rename that made every finding report
# "the sentence ruled on is not in <place>". One mechanism each time: the
# fixtures were hand-authored in the shape the code expected, so they could only
# CONFIRM, and when the contract moved they went on asserting the old one.
#
# ! WHAT REPLACED IT: 218 test functions, collected as 877 tests, derived from the
# code without reading the suite they replaced. Pages come from `page_for` over
# real source, binders from `bind`; a literal appears only where malformed IS
# the input. MEASURED by mutation: three defect classes the old suite could not
# see at all. See `tests/README.md`.
#
# ! `tests/gates/` SURVIVED, because it asks a different question -- whether a
# GATE still bites, over `scripts/` and the release rather than over the code
# under redesign.

# Stage 3 inbound: which tracked files NAME the files under review
uv run python src/comment-review.py referrers --repo . <paths...>

# What one agent is GIVEN. The task agent runs this at stage 4 and pastes the
# output verbatim. ! MOVED TO `prototype/` 2026-08-25 and does not run; what
# replaces it is `TODO/the-skill-names-commands-that-moved-to-prototype.md` T1.
uv run python src/comment-review.py vocabulary --reviewer block-context
uv run python src/comment-review.py vocabulary --roles

# Stage 7b gate: prove WRITE changed no executable code
uv run python src/comment-review.py prove_unchanged \
  --base <merge-base> --repo . <paths...>

# The write chain: a docket -> a REVISE, a full copy of --repo with the docket's pages
# overlaid, for a human to review. Never applied to the original.
# ! `--out` MUST NOT EXIST YET; the chain's own `shutil.copytree` requires it fresh.
# ! IT TOOK `--binder` UNTIL 2026-08-26 and a directory of only the changed pages until
# 2026-08-28. The docket now carries each page's path and sha, so the binder had nothing
# left to answer, and stage 7a must read ONE artifact -- so `--out` is the revise root.
# The order lives in `flows/revise.py`: copy the tree, run `flows/proof_setter.py` (galley
# edits, compositor sets, each draft reread and proved unchanged) into a scratch directory,
# overlay the drafts, then assert the address set did not move. Any refusal or a moved
# address discards the whole copy. The workflow that APPLIES an approved draft is its own.
uv run python src/comment-review.py proof \
  --docket <docket>.json --repo . --out <dir>

# What one stage's revise changed, against the tree it was pulled from.
uv run python src/comment-review.py taken_in \
  --original <root> --revise <root> [paths...]

# The TODO backlog is WRITTEN BY A TOOL, not by hand -- see "The TODO backlog" below.
# `.claude/skills/todo-tool/SKILL.md` holds every command; these are the two run most.
uv run python scripts/todo_tool.py list [--owner T] [--status S] [--requires-roy]
uv run python scripts/todo_tool.py resync     # after a merge, before trusting any count

# Lint (ruff config lives in pyproject.toml; corpora/** is excluded from linting)
# !! THROUGH `uv run`, LIKE EVERYTHING ELSE. `ruff` and `ty` are PINNED dev
# dependencies since 2026-08-22; a bare `ruff` is whatever the machine has, and
# `ruff format` REWRITES source. Roy: "we can't have my personal computer's `ty`
# happens to work."
uv run ruff check .
uv run ruff format .

# Type gate. Roy, 2026-08-22: "type drifts happen because we have been willing
# to ignore a ty gate and that is probably not the right thing to do."
# ! IT FOUND THINGS NO TEST DID, on the day it was added: `cue` annotated a
# parameter its own body unpacks as a 3-tuple, so anyone honouring the signature
# crashed; and a `SyntaxError` put the string `<unknown>` into `Paragraph.start`,
# because two exception types were read as though `args[1]` meant one thing.
uv run ty check src/comment_review/

# !! `plugins/` IS BUILT FROM `src/`, NOT EDITED, since 2026-08-24. The Python
# lives in `src/comment_review/` and is copied WHOLESALE into the skill; edit
# `src/`, run the build, commit both.
uv run python scripts/build_plugin.py           # copy src/ -> plugins/
uv run python scripts/build_plugin.py --check   # exit 1 if they disagree

# Gate check: refuse a file that won't parse on the floor interpreter (py3.11).
# Run AFTER `ruff format`. ! It reads `src/`, because that is what the formatter
# rewrites; that `plugins/` MATCHES is the build gate's question, not this one.
uv run python scripts/check_shipped_syntax.py

# The SHIPPED vocabulary holds: every key a role is given has a definition, no definition is
# written for nobody, and no role is given a term its own text never uses. Run after any edit
# to an agent file or a reference.
uv run python scripts/check_vocabulary.py

# Terms of art in the shipped tree the inventory does not list. An INPUT, not a gate:
# every row needs a human to say whether it is a term.
uv run python scripts/vocabulary_sweep.py

# What nothing points at -- a shipped name no code reads, a link that resolves nowhere.
# Also an INPUT, ruled 2026-08-21: "I don't think it deserves a gating. I do think it is
# a genuinely good idea to run every now and then." Always exits 0.
# ! Ruff sees an unused import and an unused local; a module-level constant nobody reads
# is invisible to it, and four went dead in one day with no gate noticing.
uv run python scripts/dead_sweep.py [--names] [--links]

# What a page could LOOK like, and what each rendering costs -- the row list that ships,
# the file with its address in the margin, and the same annotating only what holds prose.
# An INPUT to `TODO/the-census-is-mostly-intervals-nobody-rules-on.md`, where the decision
# lies. Never a gate; always exits 0.
uv run python scripts/render_page.py <paths...> [--show margin|prose|rows]

# How much of a tree's prose says what the code does NOT do, AT A COMMIT rather than in the
# working tree -- the measurement `TODO/the-shipped-python-does-not-pass-its-own-review.md`
# is argued from. An INPUT, never a gate.
# ! It reads history, which is what it is for: 2026-08-23 it identified the 2026-08-16 hand
# pass as `5cb05ce..8c0cef6` by matching the recorded numbers against each candidate tree,
# after a `--grep` over the same window returned nothing. ! Its numerators land within 2 of
# the recorded table and its denominators run larger -- it counts a docstring's delimiter
# lines, the hand count did not -- so it identifies a TREE and does not restate percentages.
uv run python scripts/measure_negative_prose.py <commit> [<commit> ...] [--prefix plugins/]

# Release gate no test replaces: the parser the RUNTIME uses on every frontmatter.
# Run it before tagging -- see "Cutting a release" below.
claude plugin validate plugins/comment-review
```

Tests are written in plain `pytest`, and build their inputs from the code -- pages from
`page_for` over real source, binders from `bind`. `tests/gates/` is the exception and is still
`unittest.TestCase`, which is what `unittest discover` finds.

!! **THIS PARAGRAPH SAID THE OPPOSITE UNTIL 2026-08-29**, and had since 2026-08-25: *"Tests are
written as stdlib `unittest` cases, with per-language fixtures under `tests/fixtures/` -- one
short, ordinary file per language row, which is what `test_fixture_identity.py` runs the round
trip over."* Every clause of it is now false, and the note in the command block above -- *"THE
SUITE WAS REPLACED WHOLESALE ON 2026-08-25"* -- already said so: the
suite was replaced wholesale, `tests/fixtures/` holds only `topologies/`, and
`test_fixture_identity.py` is in no directory of this tree.

!! **THE STDLIB-ONLY RULE IS ABOUT `plugins/`, AND THIS SAID OTHERWISE UNTIL
2026-08-22.** It read *"there are no third-party test dependencies, matching the
plugin's own stdlib-only rule"* -- treating one constraint as two. Only
`plugins/` is copied into someone else's `.claude/`, and it imports nothing but
the standard library; `tests/` never leaves this repo, and `pytest`, `ruff` and
`ty` are pinned dev dependencies that run against it.

! **What the rule actually forbids is a third-party import in a SHIPPED file**,
and `tests/test_shipped_imports.py` is what enforces it -- including
`TestTheCheckItselfFires`, which proves the check can fail. A dev tool that
reads this tree is not that. `scripts/check_shipped_syntax.py` answers the
neighbouring question, whether a shipped file still PARSES on the floor. ! There
is NO end-to-end grade behind those two -- see the note under Commands.

## Architecture

### The skill's 8 stages

`plugins/comment-review/skills/comment-review/SKILL.md` is the task agent's own instructions --
read it before touching the skill. The pipeline:

```
1 PROJECT      2 GATHER     3 FIND      4 MARK   5 APPLY  6 COMPACT   7a PRESENT   8 REVIEW
  DETERMINATION             REFERENCES               |                    7b WRITE
                                                      +---- no cap --------^
```

1. **PROJECT DETERMINATION** (task agent) -- scope from the merge base, find the repo's cap/width
   conventions, doc style, `move` destination, style sheet, verify reviewer agents resolve, probe
   for a language server, decide the name-corpus source.
2. **GATHER** (`page.py` builds each page, `census.py` stacks them) -- every line classified, in order -- code, part-code, comment, docstring. Each paragraph is addressed by the subject its prose answers to: a gap between two lines of code, a declaration's documentation, or the room beside a line.
3. **FIND REFERENCES** (`census.py`) -- every reference each node makes, resolved (paths, symbols,
   counts).
4. **MARK** (4 reviewer agents, read-only) -- findings on the nodes. **SERIAL in two rounds:
   `ownership-context` alone at 4a, the other three in one message at 4c against its
   resolved placement.** One role REQUIRED, three OPTIONAL -- a claim attached to the wrong
   scope is measured against the wrong code, and the other three cannot notice.
5. **APPLY** (task agent) -- one instruction per block, full-length replacement text.
6. **COMPACT** (task agent) -- cut to the cap; skipped entirely if there is no cap.
7. **APPROVAL** -- present the final text and stop (7a); on approval, apply verbatim (7b).
8. **REVIEW** (task agent) -- read the finished page against itself.

The seven instructions (`clean`, `query`, `drop`, `correct`, `patch`, `add`,
`move`) and the checkable/necessary matrix that resolves them are defined in SKILL.md -- read it
rather than re-deriving the rules here, since it is the single source and this file must not
restate it.

### The four editorial roles

Each is a separate namespaced plugin agent (`comment-review:comment-review-*`) under
`plugins/comment-review/agents/`. **`ownership-context` runs ALONE and FIRST**; the other
three go in one message so they run concurrently and see nothing of each other:

- **ownership-context** -- does this comment belong to the ANCHOR it sits on?
- **block-context** -- is every claim in this block true of the code it sits with -- its state
  (not past, not future), its constraints (value, direction, units, boundary), its worked
  examples?
- **function-context** -- does the commentary match what the function is for?
- **module-context** -- do the comments say this module is one set of ideas?

Reviewers are read-only and never see SKILL.md directly; they read the shared
`references/reviewer-brief.md`. Fixing what you find destroys the finding -- MARK and APPLY are
deliberately separate stages/actors.

### The census -- the only thing the reviewers depend on

It is built from the stdlib alone (no third-party dependency), at a per-language tier,
across four modules that each announce ONE subject:

| module | owns |
| --- | --- |
| `addresser.py` | names places -- the addressers walk out, `Cues` reads back. The LEAF: it knows nothing about a paragraph |
| `page.py` | ONE FILE -- its paragraphs tied to the places on it. `page_for()` builds one; a page names its own places |
| `census.py` | every page in scope, formatted for the agents |
| `repo.py` | what the checkout says: git, the filesystem, the exception tuples |

`annotate.py` is stage 3, the resolution a reviewer would otherwise do by hand.
Each announces ONE subject, which is what `module-context` asks of any module:

| tier        | needs                                 | answers                         | cannot answer     |
| ----------- | ------------------------------------- | ------------------------------- | ----------------- |
| `tokenized` | a lexer + AST (Python, stdlib)        | blocks, marks, docstring owners | a comment's owner |
| `lexical`   | a comment-syntax record, nothing else | blocks, marks                   | any owner         |

A language with no record is named and the census EXITS NONZERO: every file handed in is
censused or the run stops. Adding a LEXICAL language is a data row, not new code.

!! **AND A TOKENIZED ONE IS NOT, WHICH THIS SAID OTHERWISE UNTIL 2026-08-22.** It read *"adding
a language is a data row"* flat. MEASURED: `language.py` decides the tier as `return "tokenized"
if lang.name == "python" else "lexical"`, and `page.py` dispatches the READER on that same name
test while the same file STAMPS the tier from `tier_for` -- so a second tokenized language is
three edits in two modules, and half a fix leaves a file **read at one tier and labelled at the
other**. Three more sites decide *is this Python* three more ways.

! **IT IS A CLAIM ABOUT THE COST OF A CHANGE, which is the kind that invites someone to make the
change and discover the cost.** Filed as
[`tier-dispatched-on-name`](TODO/completed/tier-dispatched-on-name-SUPERSEDED.md).

!! **THE ROW BECOMES TRUE AGAIN WHEN THE AST GOES.** Roy, 2026-08-22: *"as much because we are
going to remove the ast system from python coming up as it is not an accurate statement."* With
Python read lexically -- [`python-cannot-read-python`](TODO/python-cannot-read-python.md) -- there
is one tier, the name test has nothing to answer, and adding any language is a row again. **The
sentence is not being corrected toward permanence; it is being made honest until the thing it
describes is rebuilt.**

!! **WHICH LINES DECLARE SOMETHING DOCUMENTABLE IS A KEYWORD LIST ON THE LANGUAGE ROW**, per
language, since 2026-08-20. Roy: *"the easy way is to supply the lexer with the list of keywords
that a language/practice uses to say this can get a docstring. Then the lexer matches on that
instead of having to have independent tooling."* So an `a` place resolves for Rust, Go, Java,
C#, Swift, Kotlin, JS, TS, Ruby, Lua and shell -- not Python alone.

!! **EVERY LANGUAGE CARRIES EVERY DEFINITION IT NEEDS, AND NO LANGUAGE EVER INHERITS ONE.** Roy,
2026-08-22, restating it *explicitly* after a session read the weaker form below and assumed he
could not have meant literally every language: *"every language gets its own definition
requirements in the file. No language ever inherits from the `a` family. The file can be grouped
or sorted to make it easier to understand what is happening, but every language gets all of the
definitions necessary to parse it specifically, because anything else is failing the SRP rules."*

! **GROUPING IS PRESENTATION; SHARING IS THE DEFECT.** Rows may sit together so a reader can see
the family. What they may not do is take a rule from a neighbour.

!! **THE MACHINERY IS SHARED; THE DEFINITION IS NOT.** A two-word entry, an empty keyword list, a
`spanning_quotes` tuple -- every row may use any of them. What goes IN one comes from that
language's grammar and from nothing else. Roy, 2026-08-22: *"I am not against a two word entry
`data class`. I just wanted to make certain that it wasn't assumed you could assemble two
different definition systems together to get a correct one."*

! **THE TELL IS REASONING FROM A NEIGHBOUR, and it is in the prose rather than the row.** Measured
2026-08-22: `data class` is right because KOTLIN'S grammar says so; `local function` is right
because LUA'S does. Neither is evidence about the other. The failure was arguing *"Kotlin solved
it this way, so Java should"* -- and Java's second word is the record's NAME, which varies, so the
same shape broke a real declaration. **A row is wrong the moment its justification cites another
row**, whether or not the value it lands on happens to be correct.

!! **AND THE RULE WAS ALREADY HERE, WITH ITS OPERATIVE SENTENCE CUT OFF.** This file carried
two-thirds of the 2026-08-20 ruling. The full quotation, recovered from `9ee38ea`:

> *"don't try to make the list generic -- that is a failure of the single responsibility
> principle. Each language could change on a new version invalidating the list for all of them.
> **Better an explicit precise list with duplicated words than an implicit word set hoping to
> catch each.**"*

! **THE THIRD SENTENCE IS THE ONE THAT DECIDES ANYTHING**, and it is the one that went. The first
two say a generic list is a risk; only the third says which way to resolve it -- **explicit and
duplicated beats implicit and shared** -- which is the sentence that forbids borrowing a
neighbour's rule. The `c-family` and `js-family` rows were split under it.

!! **A SHORTENED QUOTATION IS NOT A SHORTER RULE; IT IS A DIFFERENT ONE.** Roy, 2026-08-22:
*"I am pretty certain that the session cut out the important part when it shortened it."* ! And
nothing marks a cut: this tree writes `--` for an em-dash because of the ASCII rule, so an
elision and a dash are spelled the same. **When a ruling is quoted here, quote all of it** -- the
commit that first recorded it is the source, and `git log -S` finds it.

! **AN EMPTY LIST MEANS THE LANGUAGE HAS NO `a` SERIES AT ALL** -- not an empty one. `yaml`,
`toml`, `ini` and `sql` have no docstring practice, and carried an `a0` no instruction could fill until
this landed.

!! **C AND C++ SIT IN THAT GROUP FOR A DIFFERENT REASON, AND IT IS DEFERRAL RATHER THAN
IMPOSSIBILITY.** A C declaration opens with its RETURN TYPE, and the matcher reads a line's FIRST
word -- so no keyword ever matches and a spurious `a` would renumber every `a` below it. ! **That
is a fact about the MATCHER, not about C.** Roy, 2026-08-23: *"assumes you don't create a slightly
smarter parser that looks for the correct keyword in the line instead of just the 'first' word. It
is a simple fix."* Both languages plainly have documentable declarations; the list is empty until
that lands.

! **THIS SENTENCE PREVIOUSLY READ *"the list could never be complete"***, which is the shape this
file warns about two sections up -- a claim about the COST of a change, which invites someone to
make the change and discover the cost.

! Only Python's doc sits INSIDE the declaration, so Python alone needs a parser to say WHERE the
prose goes; everywhere else it goes on the declaring line's own line. An LSP `documentSymbol`
enrichment still refines this when a language server answered stage 1.7's probe, and a reviewer
reading the file is what supplies an anchor no keyword names.

`references/` under the skill directory (`write.md`, `compact.md`, `residue-check.md`,
`review.md`, `reviewer-brief.md`) are each single-sourced for one stage -- nothing pastes their
content elsewhere, and a change to a rule belongs in exactly one of these files (or in
`docs/limitations.md` for orchestration-level rules).

### Repo layout

| path                              | what                                                                                                                                                                       |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/comment_review/`             | **THE PYTHON, and the only place to edit it.** Seven areas -- `machine`, `reading`, `binder`, `concordance`, `desk`, `results`, `flows` -- plus `commands/`, which holds every `main()` and argparse, and `__main__.py`, the dispatcher. `src/comment-review.py` beside it is the launcher, the one file allowed to touch `sys.path` |
| `plugins/comment-review/`         | the shipped plugin -- `agents/`, `SKILL.md` and `references/*.md` are WRITTEN here; `skills/*/scripts/` is BUILT from `src/` and is output                                  |
| `docs/`                           | how this system behaves today, and the rules for changing it: `addressing.md` (how a place is NAMED -- the crux, and what the line-numbered form got wrong), `parsing.md` (where census structure could come from), `limitations.md` (rules for changing the skill itself -- budget-constrained, no invented examples), `vocabulary.md` (the settled terms, and every word this system stopped using), `history.md` (what the system used to DO and stopped doing -- a retired format or mechanism, with the commit that removed it, so an OLD artifact can still be read), `decision-log.md` (WHAT was decided and WHEN -- the dated chain of rulings, retractions and supersessions; the commentary on WHY is `history.md`'s. Cited as `decision-log.md TOPIC: #N`) |
| `docs/plans/`                     | RELEASE SCOPES -- what one version ships, what it does not, and which TODOs it works. !! **NOT `docs/superpowers/plans/`**, and the split is deliberate: Roy, 2026-08-19, *"I don't want to conflate the rigorous one for the less rigorous one."* A superpowers plan is written for an engineer with no context -- exact files, TDD steps, a commit per task. ! **A PLAN IS NOT A TODO**: *"Todos can remain open an indefinite amount of time and make progress as we see fit. Plans are scopes of work to be complete in one run."* Anything in a plan that does not get done is filed in `TODO/` before the plan closes |
| `evidence/`                       | the prose defects the system is measured against, and the searches scored on them: per-module probe reports over a real codebase, the triage that ranked them, `ga/ground_truth.py` and the candidate rewrites it scores. ! Nothing here describes this system's own behavior -- that is `docs/`                                                    |
| `evals/`                          | `generator_split.py` (the authorship split) and `test-cases.jsonl`. ! The twelve planted hazards and their grader are NOT here -- there is no end-to-end grade, see Commands |
| `corpora/`                        | `corpora.toml` MANIFEST of pinned corpora; the trees themselves are fetched, never vendored (gitignored)                                                                   |
| `scripts/`                        | `build_plugin.py` (which makes `plugins/`), `fetch_corpora.py`, `find_llm_repos.py`, `check_shipped_syntax.py` -- none of this ships with the plugin                        |
| `prototype/`                      | **REFERENCE, NOT SOURCE.** The middle of the chain -- the desk, the verdicts, the record -- moved here 2026-08-25. Nothing imports it, nothing ships it, it does not run. Kept because the replacement is not designed yet; see `prototype/README.md` |
| `.claude-plugin/marketplace.json` | lets this checkout be installed as a plugin marketplace in the same session (`claude plugin marketplace add <path>` then `claude plugin install comment-review`)           |

### Shipped-code constraint that shapes how every `plugins/` script is written

Anything under `plugins/` is copied into other people's `.claude/` and formatted by **their**
ruff config, not this repo's -- a repo targeting a newer `target-version` can rewrite valid
syntax (e.g. `except (A, B):` -> PEP 758 unparenthesised form) into a `SyntaxError` on an older
interpreter, and the author of this repo never sees the failure. Consequences enforced in this
codebase:

- No `except` clause in a shipped file holds a tuple literal -- every exception tuple is bound to
  a name (e.g. `READ_ERRORS`, `PARSE_ERRORS`) so there is nothing for a formatter to rewrite.
  A `noqa` was tried and does not hold, because it suppresses the report, not the rewrite.
- `pyproject.toml`'s `target-version = "py311"` protects *this repo's own* formatting only; it
  cannot protect a file after it has been copied elsewhere -- `scripts/check_shipped_syntax.py`
  is the actual floor check, and it must be run after `ruff format`.

### Corpora are fetched, never vendored

`corpora/corpora.toml` pins nine repositories at specific refs (seven third-party, plus two
personal projects used as an over-fitting control), chosen for variety of prose convention. A
`local` corpus becomes a `git worktree` of a repo already on the machine; a `public` one is a
sparse clone at a tag. `corpora/*/` is gitignored -- only the manifest and the fetch script are
tracked. Corpora used with `evals/generator_split.py` must be fetched with `depth = 0` (full
history) since it depends on `git blame`.

## Working on this repo

!! **NO HEREDOCS. NOT FOR ANYTHING.** Ruled by Roy, 2026-08-19. A heredoc (`<<'EOF'`, `<<EOF`,
`@'...'@`) puts the text through the shell before the program that needs it, and this repo's work
is almost entirely text that the shell eats: an f-string's `{}`, a regex's `\s` or `\|`, a
Windows path's `\U`, an escape sequence, a `!`. It has broken every one of those in a single
session -- including a `sed` that silently produced `[\w./\-]+` from `[\w.:/\\-]+`, which is the
worst kind, because the command SUCCEEDED.

**What to do instead:**

| the job | the tool |
| --- | --- |
| change a file | `Edit` / `Write` |
| a multi-step or repeated edit | `Write` a `.py` script under the job's tmp dir, then `uv run python` it |
| a commit message | `Write` it to a file, then `git commit -F <file>` |
| file content in a test fixture | `Write` |

! **The rule is about the SHELL, not about scripting.** A Python script that does the same edits
is fine and is usually better -- it fails loudly on a bad assumption (`assert old in t`) where a
`sed` writes something plausible and moves on.

- Grade a comment-review run from its **diff**, never from its own report -- self-reported
  confidence has been measured to not discriminate real from fabricated findings.
- `docs/limitations.md` governs changes to the skill's prose/rules themselves: every example
  used there must be invented (never a real quotation), each new rule should replace an
  existing one at budget rather than accumulate, and a rule belongs in exactly one file.
- If you are **preparing making edits to code and not in a branch "ASK"** if you should be.
  The git history on main contains work that should have been branch work because we decided
  to start implementing before realizing we were corrections to code that belongs on a branch
  first.

### !! A THING WHOSE DEPENDENCIES ARE BROKEN IS NOT WORKED ON. IT IS REFUSED.

Roy, 2026-08-22, correcting a claim that the round-trip identity was this system's most productive
instrument: *"But the compositor couldn't be built until the lexer and the langauges and the page
and the census was doing the work each needed to do individually. So from start to finish the old
system was insufficient and mixed up concerns in so many places that it was never going to
work."*

!! **THIS IS A STANDING PRACTICE, NOT A ONE-OFF, and it is visible six times in the record:**

| when | what was refused | until |
| --- | --- | --- |
| 2026-08-21 | *"I have refused every galley update to this point. The galley was always broken and on this commit is still broken."* | the compositor split existed |
| 2026-08-21 | *"what was broken stays very broken out of this branch and I am not willing to accept that. I can accept it being broken in the branch but not merged out of it."* | the merge |
| 2026-08-22 | *"I stopped the development at the page everytime before that ... there was no reason to try to fix the galley as it was."* | page, cues and census were *"at least passably functional"* |
| 2026-08-22 | *"this needs to go in before we can finish this plan and branch"* | `TODO/cues-knows-about-lines.md` landed |
| 2026-08-22 | the compositor itself | the lexer, the languages, the page and the census each did ONE job |
| 2026-08-21 | *"This one is going to take serious thought before we can release it because it looks like it needs a look-ahead lexer"* | the lexer can see ahead |

!! **THE COST OF IGNORING IT IS THE FIX ITSELF, NOT THE TIME.** A repair to a module whose inputs
are wrong is SHAPED BY those inputs, so it encodes the defect and has to be undone -- which is
what *"mixed up concerns in so many places that it was never going to work"* describes. The old
galley was not badly written; it was written against parts that had not decided what they were.

! **AND IT IS WHY AN INSTRUMENT ARRIVES LATE.** The round-trip could not be built early, so
`matter`, the collisions, the straddle and the empty-file bug stayed invisible -- not because
nobody looked, but because **nothing yet existed that could disagree with the file.** ! A measuring
device is downstream of every part it measures, which is the same rule wearing its most expensive
consequence: see [`docs/gates.md`](docs/gates.md).

! **WHAT THIS ASKS OF A SESSION** is to name the dependency and STOP, rather than to produce a
plausible local fix. A refusal is a finding: file it, say what it waits on, and leave the box
unchecked -- *"Deferred is not done."*

### !! THE TODOs ARE THE JOB BOARD. PLANS ARE HOW WE MARK THEM OFF.

Roy, 2026-08-19: *"the todos are the job board -- plans are how we mark them off."*

| | `TODO/` | `docs/plans/` |
| --- | --- | --- |
| holds | every piece of work known to be wanted | one release's scope |
| lifetime | **indefinite.** Progress as we see fit | **one run.** It closes |
| answers | *what is there to do* | *what is this version doing about it* |

!! **EVERY FINDING GETS A TODO -- an existing one it fits, or its own.** A finding recorded only
in a plan dies when the plan closes, and one recorded only in a session transcript was never
recorded at all. **The plan then NAMES the TODOs it works**, so the two can see each other.

!! **A PLAN THAT NAMES NO TODO CANNOT BE CLOSED FROM EITHER END** -- the backlog cannot see the
work scheduled against it, and the plan cannot see the work already filed. Audited 2026-08-19 on
`two-live-runs-proposed-fifteen-changes.md`: **0 of 15 tasks named the TODO they close**, three
were named in a `Related` section only, and one of those was already completed -- so the scope
pointed at finished work as though it were pending.

!! **AND THIS IS TWO TRACKERS THAT CAN DRIFT, KNOWINGLY.** Roy: *"I know this is two ways of
tracking work which can get them out of sync."* The rule that keeps them honest is one-directional
-- **a plan cites TODOs; a TODO never cites a plan** -- so a closed plan leaves the backlog intact
and no TODO is left pointing at something that no longer exists.

!! **A PLAN CARRIES CHECKBOXES, THE SAME AS A TODO.** Roy, 2026-08-19: *"Just because they are
not todos doesn't mean they are freeform either."* **The release gate is every box on the plan
ticked** -- *"we will get to the release readiness at the time when it is ready to be released"*,
which sounds ontological and is not. It says readiness is **COUNTABLE** and **VERIFIABLE BY
ANYONE**, not self-defining:

- nobody has to JUDGE whether a version is ready
- nobody can DECIDE that it is
- and **anyone can check that it is** -- including someone who did none of the work

! **The third is what makes the first two hold.** A box that only its author can verify is a
judgement wearing a checkbox. Each box therefore NAMES the TODO it works, the TODO names the
work, and the work is in the tree -- so a ticked box is re-derivable by a stranger, which is the
same standard this repo applies to a comment: *if a sentence cannot be falsified by reading the
code or re-running a command, it does not belong.*

!! **AND THIS IS WHAT LETS AN AGENT STOP ASKING "IS IT READY".** Roy, 2026-08-19: *"even though
I knew the scope of work I wanted and I thought you had the information on the scope of work, you
didn't -- and so would ask, because you didn't have access to what done looked like."*

! **That question is a SYMPTOM, not politeness.** *"Should we release it now?"* and *"are you
ready to release it?"* are what an agent asks when DONE exists only in someone's head. It cannot
be answered from the tree, so it gets asked of the person -- repeatedly, and usually at the worst
moment, because the agent has no way to tell whether the answer has changed since last time.
**The plan externalises DONE**, so the state is read rather than requested.

!! **IT DOES NOT REMOVE THE RULINGS, AND MUST NOT.** A `*` box is a decision only Roy can make --
whether the galley splices within a line, what `address:lines` does with a code range. Those are
asked because they are genuinely his. **Asking for a ruling is work; asking whether the work is
finished is a missing artifact.** An agent that cannot tell the two apart will either interrupt
constantly or guess at a decision that was never its own.

! **Prose in a plan is EVIDENCE for a box, never a second list of work.** A section that restates
what a box says is a place for the two to disagree.

! **`scripts/todo_tool.py` manages `TODO/` and not `docs/plans/`**, so a plan carries no
`Progress:` line -- a hand-maintained count is the arithmetic the tool exists to prevent. **The
boxes are the state.**

! **`docs/plans/` is NOT `docs/superpowers/plans/`.** The second is written for an engineer with
no context -- exact files, TDD steps, a commit per task. The first is a release scope. Roy:
*"I don't want to conflate the rigorous one for the less rigorous one."*

### The TODO backlog, and who writes it

**`scripts/todo_tool.py` writes `TODO/`. Do not hand-edit a `Progress:` line or a README row.**
Every command recomputes the counts from the boxes it just wrote, which is the thing a hand edit
gets wrong. The full command table is
[`.claude/skills/todo-tool/SKILL.md`](.claude/skills/todo-tool/SKILL.md) and is not restated
here; `resync` is what fixes drift after a merge.

! **The tool is VENDORED from `redacted_corpus` at `todo-requires-roy` REDACTED_SHA_D** and is
re-grabbed rather than maintained here, so ruff excludes it. One local patch -- the stdout
encoding guard -- says so at the patch.

!! **TWO WRITING METHODS COEXIST AND ROY KNOWS.** 2026-08-18: *"I know this is two methods of
writing the todos but right now I don't want to fix that."* The tool owns counts, rows and
status; the prose inside a file is still written by hand. Do not spend a session reconciling
them.

#### A box is a claim about whether work remains

!! **A BOX IS A VERIFIABLE CHECKPOINT AND NOTHING ELSE GETS ONE.** A task names something a
stranger can look at and call done or not done -- a command that must come back empty, a file
that must exist, a test that must fail first. **A ruling, a measurement, a naming decision or a
line of reasoning is not a task**, however much it matters: it belongs in the **Objective**, or
in a dated `note`.

! **THE TELL IS THAT IT CANNOT BE FINISHED.** *"The trade word is `leading`"* is true the day it
is written and every day after -- there is no state in which someone ticks it. If ticking would
be a JUDGEMENT rather than an observation, it is not a task.

!! **AND A BOX ON A RULING MAKES THE COUNT LIE TOWARDS MORE WORK.** MEASURED 2026-08-23:
`leading-owns-the-space-between` read **0 of 10** while nine of the ten were rulings and
measurements already settled, and the one real defect was not among them. `Progress:` is
computed from boxes, so the file advertised that nothing had been done on work that was
finished -- and no gate can see it, because a box is well-formed whatever is written in it.

!! **AN UNCHECKED BOX SAYS THE WORK IS STILL TO DO, and something automated now reads it.** Roy,
2026-08-18: *"a check box not-marked is left as something todo, even if it was superseded and no
longer necessary."* Measured the same day: five RESOLVED proposals held in a prose table with no
boxes made `resync` generate a README row reading `0/9` on a file a third finished.

!! **A TODO IS NEVER DELETED. IT IS SUPERSEDED AND CHECKED.** Roy, 2026-08-19: *"todos don't get
deleted they get SUPERSEDED and checked. That is going to be an addition to the tool soon."*

! **A deleted box leaves no trace that it was ever there, or why it went.** A superseded one
keeps the error legible -- which is the same reason a superseded RULING is kept beside the one
that replaced it rather than rewritten away. ! The tool has no delete command and is not getting
one; what it is getting is a way to mark this.

! It applies to a task filed in error as much as to one overtaken by better work. Removing a
mistake removes the record that it was made.

| the task is | the box | the file's `Status:` |
| --- | --- | --- |
| **done** | `[x]` | -- |
| **superseded** -- overtaken, no longer necessary | `[x]` | -- |
| **superseded IN PART**, remainder still wanted | `[ ]`, tracking the remainder | -- |
| **deferred** -- waiting on a named event | `[ ]` | say what it waits on |
| not started | `[ ]` | -- |

! **Deferred is not done.** Roy, 2026-08-18: *"Deferred is not done - just waiting so its status
is still correct."* Waiting on an event is work not started, which is what an unchecked box
already says.

! **`in-progress` means some boxes are ticked** -- not blocked, not waiting on a ruling. A file
where only a RULING has landed is `in-progress`, because a ruling is work.

! **A superseded ARGUMENT is not a superseded task.** Reasoning kept so an error stays legible
carries no box at all; only work does.

### Cutting a release, and the version number

!! **PROPOSING A TAG IS THE MOMENT TO CHECK WHICH BRANCH YOU ARE ON.** A tag is a main-only act,
so wanting one means the work has been accumulating somewhere -- and if that somewhere is main,
it went there without the branch question ever being asked.

! **It is a better checkpoint than the rule above it**, which fires when editing STARTS. The
start is where this goes wrong: a one-line fix becomes a migration with no moment that announces
itself. Roy, 2026-08-17, after 26 commits reached main: *"your repeated asking to tag the commits
with a new version should have cued me in that you were on main."* ! Both of us had the signal
and neither read it, which is why it is written down rather than remembered.

!! **THE VERSION IS STATED THREE TIMES AND `tests/test_release.py` HOLDS THEM EQUAL.** Bump all
three in one commit, or the gate fails:

| file | field |
| --- | --- |
| `pyproject.toml` | `[project] version` |
| `CHANGELOG.md` | the newest `## [x.y.z]` heading (`[Unreleased]` is skipped -- it carries no number) |
| `plugins/comment-review/.claude-plugin/plugin.json` | `version` |

!! **ANY CHANGE UNDER `plugins/` AFTER A TAG NEEDS A NEW VERSION.** The plugin cache keys its
directory on that `version` field -- `~/.claude/plugins/cache/roy-local/comment-review/0.2.1/`
-- so a second, different tree installed under the same number overwrites the first and
`claude plugin list` reports both as the same release. Measured 2026-08-17: three commits after
`v0.2.1` was tagged and pushed, `plugins/` held a block-context whose frontmatter parsed where
the tag's did not. **Two materially different reviewers, one version number**, while another
session had already pinned an evidence package to the tag. **Never move a tag someone has
measured against; cut the next number instead.** ! The version field exists precisely to make a
run attributable, so shipping two trees under one number returns the repo to the state the
field was added to end.

! **A tag here is ANNOTATED, so `git rev-parse vX.Y.Z` returns the TAG OBJECT, not the commit.**
Use `vX.Y.Z^{}` wherever a commit is wanted -- `git diff "v0.2.1^{}" HEAD`, `git show
"v0.2.0^{}:<path>"`. This is the trap anyone re-deriving which code produced a measurement hits
first.

!! **RUN THE BUILD BEFORE TAGGING, AND COMMIT WHAT IT WRITES.** Since 2026-08-24 the shipped
Python is a COPY of `src/comment_review/`, so a release cut without `uv run python
scripts/build_plugin.py` ships whatever the last build left behind -- and every gate reading
`plugins/` passes on it, because a stale copy is still a valid one.

| | |
| --- | --- |
| build | `uv run python scripts/build_plugin.py` |
| prove it took | `uv run python scripts/build_plugin.py --check` |
| then commit | `plugins/` STAYS TRACKED -- the marketplace install reads committed state |

! **`tests/gates/test_build.py` is what proves that check can fail**, over a hand-edited file,
a file never built, a file the source dropped, and an empty tree.

! **Run `claude plugin validate plugins/comment-review` before tagging.** No test replaces it:
it is the parser the runtime actually uses, and it caught a YAML frontmatter failure that had
shipped through every release to date, silently dropping a skill's whole metadata and an agent's
description. `tests/test_frontmatter.py` gates the one cause that is known; the validator is
what finds the next one.

! To publish the cut: `git tag -a vX.Y.Z -m "..."`, `git push origin main`, `git push origin
vX.Y.Z`, then `claude plugin marketplace update roy-local` and `claude plugin update
comment-review@roy-local`. **The install reads COMMITTED state**, so commit before updating, and
a session already open keeps the old agents until it restarts.

## The metaphor is EDITORIAL, and it is a rule, not decoration

**This is an editorial board.** Four **editorial roles** read a manuscript and write **editorial
marks** on it; a **PROOFREADER** reads the finished **proof** and says whether the document
deserves more marks. Think about the work that way, and take a new term from publishing -- what
would an editor, a copy desk or a proofreader call this? -- before reaching anywhere else.

! **Check a candidate against the register before proposing it, not after.** Three words entered
from LAW and each named something publishing already had a word for: `acquittal` and
`suppression` arrived with the initial plugin import and are deleted; `jurisdiction` was added
2026-08-16 by a session that checked it for collisions and never checked it for register, and is
now `remit`.

!! **AND IT SUPPLIES CATEGORIES, NOT ONLY NAMES.** Roy, 2026-08-21: *"this is twice now that we
have realized we were categorically wrong about something that the publishing industry already
knew and uses actively."* Both times the tell was the same sentence -- **"it had to belong to
something"** -- said about a category that was straining to hold a second job:

| what was straining | what it was missing | measured cost |
| --- | --- | --- |
| `b0` held the file's own matter as well as the first gap | **front/back matter**, its own series | one address for two places; a licence header reviewed as ordinary work |
| `b` held the blanks on both sides of an `a` | **leading**, the space between lines of type | 16 of 185 files in one corpus could not be set back |
| `galley.py` both EDITED the page and SET it | **the compositor**, who sets type and decides nothing | the whole module was line arithmetic; three plan boxes were held for it |

!! **THE THIRD IS THE ONE WHERE THE METHOD IS ON THE RECORD**, 2026-08-21, in four messages:

| Roy, verbatim | what it does |
| --- | --- |
| *"first what is a galley or what does it do in the publishing world?"* | asks what the thing IS -- **before** proposing anything |
| *"So right now what the problem is - is actually galley doing two things, creating an updated page and page-setting the text. Those are two different roles and two different sets of rules."* | reads the two jobs OUT of that answer |
| *"So my proposal is galley gets the old page - updates the old page with the verdict/record/marks and then a page-setter sets the page to rewrite the output text."* | names the missing half **from what it does**, in plain English |
| *"compositor works"* | takes the trade's word for the role he had already isolated |

!! **THE NAME CAME LAST, AND IT CAME FROM THE FUNCTION FIRST.** `page-setter` is Roy's own
coinage and is what the module was called for the whole diagnosis; `compositor` arrived afterward
and was ratified in two words. ! So the method is NOT *ask publishing what to call things*. It is
**ask what the thing IS, find the second job in the answer, name that job by what it DOES, and
only then look for the trade's word for it.** A term reached the other way names a category
nobody has yet shown to exist.

! **AND THE PAYOFF IS STATED AS A TEST, NOT AS TIDINESS**: *"Then we can compare the round trip
directly page in page out, page in, comments removed, page out no comments... No ambiguity about
how the page gets written. No this got lost this wasn't done right."* The split is what made the
identity ABLE TO FAIL -- which is [`docs/gates.md`](docs/gates.md)'s rule arriving from the other
direction, and Roy said so at the time: this header *"is referencing this exact error even though
it was masked by so many other things."*

!! **AND IT SAYS WHEN TO ASK -- IT WAS A REFUSAL, NOT A SCHEDULE.** Roy, 2026-08-21: *"This
page-setter idea is what I was thinking about a lot when you stated this and how it to do it. It
is also why I have refused every galley update to this point. The galley was always broken and on
this commit is still broken."* ! Every proposed galley fix was declined while the category error
stood, because a fix to a module that is about to stop existing is chosen for nothing.

! **So when a category is doing two jobs, ask what a compositor would call the half that does not
fit -- before inventing a rule to make one category cover both.** Publishing has spent five
centuries naming the parts of a page; a part this system keeps tripping over probably has a name
already, and the name usually arrives with the rule attached.

!! **AND A THIRD IS OPEN, FOUND THE SAME WAY.** Roy, 2026-08-21: *"There is no stet. -- we called
this 'clean' we were incorrect."* `clean` records two different facts -- *a role read this and had
nothing to report*, and *a mark WAS proposed here and the original stands*. The second is
publishing's **stet** ("let it stand"), written in the margin with dots under the text so the
refused correction stays visible underneath. ! Recorded as `clean`, a declined proposal says
nothing was found, so a re-run raises it again and stage 8 cannot know it was already refused.
Filed as `TODO/no-mark-for-let-it-stand.md`; **not this branch.**

! **The register is itself an instruction, and that is the point.** Roy, 2026-08-16: *"I bet it
helps the LLM focus in on what it is doing. Because of locality and other context items the llm
will return words and phrases and comment suggestions based upon 'being' an editor better."* An
agent reads these files and then writes in them, so one consistent register is a role it can
occupy rather than a glossary it has to consult. A reader who knows the metaphor can also predict
what an unfamiliar term means instead of guessing. ! Recorded as the REASON for the rule, not as
a measurement: nothing in this repo tests it.

## Documentation Rules

- Do not write prose rules, thresholds, or assumptions into docs unless something in the code
  actually consumes them. If nothing reads it, delete it.
- Never attribute assumptions about Q unless they stated them in this session or they are
  recorded in a cited file. Cite the source inline.
- Prefer a glossary entry over repeated inline definitions.
- Do not write subjective statements about properties of the project -- "robust", "elegant",
  "carefully designed", "solid", "maintainable", "intuitive", "works well" -- in comments,
  docstrings, README prose, or commit messages. A false *measurement* can be re-derived and
  corrected; a claim that something is "robust" has no oracle. Nothing can check it, so it
  survives every review and every rewrite regardless of whether it was ever true -- it is the
  one class of prose this repo's four editorial roles cannot catch, because both block-context and
  function-context need something to resolve the claim against. Write what is measured, what is
  enforced, or what was observed, and let the reader judge. If a sentence cannot be falsified
  by reading the code or re-running a command, it does not belong.
- `clean` is reserved, not a synonym for "vaguely good": it is one of the seven instructions named
  under "The skill's 8 stages" above and must not be used as a loose adjective for code or
  prose anywhere in this repo. As an instruction it means nothing to report from that role, and
  each role's `clean` asserts something specific -- read what, in that role's own file under
  `plugins/comment-review/agents/`, which states it.

## Exploration Budget

- Before a long read/grep sweep, state a one-line plan and the files you intend to inspect,
  then stop and confirm.
- Cap initial exploration at ~10 tool calls; if you still lack context, report what you
  found and ask rather than continuing to browse.
- Prefer dispatching a Task agent for open-ended codebase exploration so the main context
  stays uncluttered by the subagent's intermediate output.

## Lanes -- "You are the ..."

**Four lanes own this repo, and a TODO's `Owner:` is one of them.** Roy runs sessions in
parallel, each opened as *"You are the `backend` -- I need you to ..."*, and **the lane scopes
what you may change.** If a task touches a file another lane owns, **name the lane and ask**.

| lane | owns, in one line |
| --- | --- |
| `agents` | **What an agent is TOLD, and how the roles hand off** |
| `backend` | **What the Python actually does** |
| `testing` | **How well the running system does, and what that is scored against** |
| `systems` | **Whether it installs, and whether the gates still bite** |

!! **THE VOCABULARY IS SHARED AND CROSSING IS THE POINT.** Roy, 2026-08-23: *"any side can and
should update the vocab on the other side as soon as a split or modification is noticed."* It is
the ONE standing exception to *name the lane and ask*, and the cost of waiting is measured --
`evidence/rename-left-history-in-the-comments/`.

!! **AND A LANE THAT TRIPS A GATE FIXES ITS OWN CODE**, never the gate. A gate edited to pass is
indistinguishable afterwards from one that always passed.

The full roles, the crossing rules and the path map are in the two files loaded below.

## Always resident -- loaded by the `@` lines below

The two `@` lines at the end of this file are what put `conventions.md` and `lanes.md` in
context, IN FULL. **An ordinary markdown link does not** -- it makes a file findable, not
present. Keep both lines; if they are somehow not in context, read the two files before changing
rules or crossing lanes.

@docs/conventions.md
@docs/lanes.md