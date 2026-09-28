"""The shipped vocabulary holds: complete, and honest about who needs what.

    uv run python scripts/check_vocabulary.py

`src/comment_review/references/vocabulary.toml` is the single source for the
terms agents receive, and the task agent hands each role the entries its
`[roles]` row lists. Four checks,
and each exists because the thing it looks for had already gone wrong unnoticed:

  COMPLETE  Every key a role is given has a definition, and no definition is
            written for nobody. That file is what agents are HANDED, so a term
            with no recipient belongs in `docs/vocabulary.md` instead.
  DUPLICATE No term defined here is defined AGAIN in `docs/vocabulary.md`. One
            source, one copy: a second copy drifts, and the drift is silent.
  DRIFT     Every term a role is given appears in the text that role reads, and
            every term it reads is given. The rule is "give a role the terms its
            text uses", so the lists go stale whenever the prose is edited -- 26
            terms had drifted across all six roles before this check existed.
  RETIRED   No shipped file uses a word the vocabulary retired. Nothing enforced
            this, so `block` survived in 298 places after `paragraph` replaced
            it, and the shipped definition of a block still read "the interval
            between two lines of CODE" -- a shape a prose file does not have.

! The role -> files mapping is DERIVED, not listed here: an agent file names the
document it is told to read, so this reads it out of the tree. A listed copy
would go stale exactly the way the term lists did.

Exits nonzero if any check finds something.
"""

import re
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGENTS = REPO / "src/plugin/agents"

# !! WHAT THE VOCABULARY RETIRED, and the word that replaced it. A shipped file
# may not use the left-hand side.
RETIRED = {
    "block": "paragraph",
    # ! The text report a reviewer used to read; the reviewer reads the binder
    # and its seeded edit copy. `decision-log.md Process: #99`.
    "listing": "binder",
    "blocks": "paragraphs",
    # ! Roy, 2026-08-20: *"it never really fit -- using libcst in python made it
    # easy to move and edit comments and so I thought that was what this was. It
    # isn't."* Naming the thing for a syntax tree invited an apology for not
    # being one, in every file that mentioned it.
    "pcst": "page",
    # !! FOUR NAMES THAT WERE WRONG ABOUT THEIR OWN REFERENTS, retired
    # 2026-08-23. A folio numbers a LEAF or a PAGE; the `@` half of an address
    # names a position WITHIN a page, so `b3` was never any folio. The error
    # shipped as a DEFINITION -- *"a leaf's number in publishing, which is what
    # it is here"* -- and reviewers were given it.
    #
    # !! `leaf` IS NOT HERE AND THAT IS DELIBERATE. The PAGE sense went with the
    # rest -- one sheet carries TWO pages, so it was neither the page nor the
    # cue, and a file has no verso. But the DEPENDENCY-GRAPH sense is live and
    # correct: `constants.py`'s ULTIMATE LEAF, ruled by Roy 2026-08-22. Retiring
    # the word would refuse that, and `leaves` is an ordinary English verb --
    # measured 2026-08-23, it fired on 15 sentences reading *"leaves it
    # unaccounted for"*. ! The two senses are declared polysemy; see
    # `docs/vocabulary.md` and `TODO/completed/leaf-means-two-things.md`.
    "folio": "cue",
    "folios": "cues",
    "foliation": "cues",
    "foliator": "addresser",
    "foliate": "cue",
    # !! `join` AS A NOUN IS RETIRED, 2026-08-27. Roy: *"'The join' was too
    # ambiguous. It didn't define anything and you used it as a shortcut that
    # could have meant many different operations."* MEASURED: 202 live uses
    # carrying FIVE referents -- the `verdicts.py` program, linking two data
    # structures, checking a mark against its page, a git merge, and ordinary
    # English. `decision-log.md Vocabulary: #19`.
    #
    # ! THE VERB IS LIVE AND NECESSARY, so `.join(` is declared below rather
    # than the word being left out of this table. The `(?![A-Za-z0-9-])` in
    # `check_retired` already spares
    # `joins`, `joined` and `joining`; only the bare noun is refused.
    "join": "the collator",
    # !! `verdict` IS RETIRED, 2026-08-27. Roy: *"I also don't like the term
    # verdict. It doesn't seem in line and is confusing when it is also called
    # a finding."* A MARK IS THE OBJECT; ITS `instruction` IS ONE OF THE SEVEN.
    # `decision-log.md Vocabulary: #17`.
    #
    # ! THE PLURAL IS A SEPARATE ROW, same as `block`/`blocks` above: the
    # `(?![A-Za-z0-9-])` boundary that spares `.join(`'s live VERB forms also spares
    # `verdicts` from the singular entry, and that sparing is wrong here --
    # the plural NOUN is exactly as retired as the singular, with no live verb
    # sense to protect.
    "verdict": "instruction",
    "verdicts": "instructions",
    # !! `census` IS RETIRED, 2026-09-04 -- `decision-log.md Vocabulary: #34`.
    # `gather` has been stage 2's word since 2026-08-23; the command, the act
    # and the module take it, and what the gather hands over is the BINDER.
    # ! FOUR ROWS, as `verdict`/`verdicts`: the `(?![A-Za-z0-9-])` boundary spares
    # every derived form from the bare entry, and none of them is live.
    "census": "gather, or binder for what it hands over",
    "censused": "gathered",
    "censuses": "gathers",
    "censusing": "gathering",
}

# !! THE WAY OUT, AND IT IS PER FILE. Roy, 2026-08-19: *"let's give ourselves a
# `# noqa: vocabulary` out on the files that are not about the prose or the
# current representation. Let's make certain to move the code into separate
# files to make it easy."*
#
# ! A file carrying this marker is EXEMPT WHOLE, which is why the code that
# needs it was moved out first: no file under `src/` carries the marker
# today. Exempting a line rather than a file would let the retired word
# creep back into a file that is about the CURRENT representation, one
# suppression at a time.
NOQA = "# noqa: vocabulary"  # TODO: no file under src/ carries this marker

# !! A RETIRED WORD *NAMED* IS NOT A RETIRED WORD *USED*, and the difference is
# the backticks. `paragraph`'s own definition says *"`block` was the older word
# for it"*, which is how this
# repo keeps an error legible instead of erasing it, which is the same rule that
# keeps a SUPERSEDED task checked rather than deleted. A sentence that USES the
# word to mean the thing is what this catches.
#
# TODO: `blocks`, `block=`, `BLOCK `, `_block(`, `compose_block(` and `pCST`
# match nothing under src/; remove them from MENTION.
MENTION = (
    "`block`",
    "`blocks`",
    "`block=",
    "`BLOCK`",
    "`BLOCK ",
    # ! Two identifiers from a REVIEWED codebase, once quoted by `block-context`
    # as the measured case of a substring count sweeping in a longer name. No
    # file under `src/` holds them today; the TODO above MENTION removes them.
    "`_block(`",
    "`compose_block(`",
    "`pCST`",
    "`census`",
)

# ! And these are not the retired term at all, by exact form:
#   block-context   a ROLE NAME -- an agent id, a filename, and a `[roles]` key in
#                   `vocabulary.toml`
#   TEXT BLOCK      a Java language feature
#   block: int      a record index on `Finding`, a class no file under
#                   `src/` defines. `.block` and `block=`
#                   are the same field read and written.
#
# !! FOUR MORE LIVE SENSES, DECLARED 2026-08-23 AFTER THE GATE BOUGHT ITS GREEN
# WITH THEM. `block` is polysemous and only the NOUN meaning *paragraph* was
# retired; the verb, a Python code block and a Java text block are current
# English and current terms of art. Undeclared, the gate flagged all four, and
# the rename that followed replaced the live senses instead of the dead one:
# SKILL.md's verdict table read *"it PARAGRAPHS every other verdict"*, the
# `block-context` agent was told its own role was `PARAGRAPH-CONTEXT`, and
# `prove_unchanged` described *"a Java text PARAGRAPH"* -- a language feature
# that does not exist.
#
# ! THIS IS THE FAILURE `docs/gates.md` NAMES FROM THE OTHER SIDE: the run was
# green because the SUBJECT was bent to the check. A word with several senses
# needs each one declared, or the gate reads correct prose as a defect and the
# cheapest way to satisfy it is to make the prose wrong.
#
#   blocks every other verdict / does not block this pass / unresolved blocks
#                   the VERB, to obstruct -- what an escalated `query` does
#   __main__":` block
#                   a PYTHON code block, the language's own term
#   Java text block the same feature as TEXT BLOCK above, in lower case
#
# ! AND ONE SENSE IS A LIVE TERM, NOT AN EXEMPTION: the code symbols that say
# which series the lines they enclose belong to -- `/*` with `*/`, `/**` --
# never the prose between them. `language.py` holds them as `block_comment`
# and `doc_block`, and the lexer's `in_block` is the pair currently open.
# `vocabulary.toml` states the sense beside `paragraph`. Declared here by the
# three identifiers, because the scan otherwise reads the word inside them as
# the retired noun.
#
# TODO: `block: int`, `"BLOCK"`, `.block`, `block=` and the three `verdict`
# phrases below match no file under `src/` once the entries above them are
# removed; delete them.
NOT_THE_TERM = (
    # ! Python's own str.join -- the VERB, and 64 uses in the shipped tree.
    ".join(",
    # ! The same VERB in this tree's own names: the lexer's `_join`, which
    # joins a run's lines. The retired word
    # is the NOUN.
    "_join",
    # ! The role name, and its spelling as an enum member in `desk/stages.py`.
    "block-context",
    "BLOCK_CONTEXT",
    "TEXT BLOCK",
    "block_comment",
    "doc_block",
    "in_block",
    "block: int",
    ".block",
    "block=",
    '"BLOCK"',
    "blocks every other verdict",
    "does not block this pass",
    "unresolved blocks stage 6",
    '__main__":` block',
    "Java text block",
)
REFERENCES = REPO / "src/plugin/skills/comment-review/references"
# !! THE TOML IS PACKAGE DATA AND DOES NOT SIT BESIDE THE `.md` REFERENCES.
# It ships inside the `comment_review` package, and SKILL.md has the
# task agent read it there; the `.md` files are read by AGENTS and by this
# gate, not by any shipped code, and live
# with the rest of the plugin's prose under `src/plugin/`.
EMITTED = REPO / "src/comment_review/references/vocabulary.toml"

# The record of what CHANGED -- never a second place to look a live term up.
DOC = REPO / "docs/vocabulary.md"
# One row of a definition table there: `| **term** | ...`
DOC_TERM = re.compile(r"^\| \*\*(.+?)\*\* \|", re.M)
# Everything below this heading is the RECORD of a rename, not a definition.
RETIRED_HEADING = "## Retired"

# How an agent file names the document it is told to read. ! It names the
# DOCUMENT and never its location: a shipped file that spells out a path sends
# the agent looking for it in the installed plugin instead of using the absolute
# path the task agent passed in. So this matches a backticked filename, and the
# four reviewers -- which name no file, because the brief is HANDED to them in
# their prompt -- are matched on the word.
READS = re.compile(r"`([\w-]+\.md)`")

# File names `text_for` subtracts from the references an agent file names.
# `re-review.md` is not in `REFERENCES` and no agent file names it, so this
# excludes nothing today.
# TODO: `re-review.md` does not exist, so NOT_DERIVED excludes nothing; remove it.
NOT_DERIVED = frozenset({"re-review.md"})
BRIEF = ("brief", "reviewer-brief.md")

# The key every role's list is extended with. Not a role.
EVERY_AGENT = "all"

# The one role with no agent file.
TASK_AGENT = "task-agent"

# The task agent runs from SKILL.md and loads
# `write.md` at stage 7b; every other reference it names is handed to another
# agent, so its text is those two.
TASK_AGENT_READS = (
    REFERENCES.parent / "SKILL.md",
    REFERENCES / "write.md",
)

READ_ERRORS = (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError)


def term_used(text: str, term: str) -> bool:
    """Whether prose uses this term as a word, singular or plural."""
    return bool(re.search(r"(?<![\w-])" + re.escape(term) + r"s?(?![\w-])", text, re.I))


def text_for(role: str) -> str | None:
    """Everything one role reads: its agent file and the references it names.

    Those are each backticked `.md` the agent file names, the brief when the
    agent file mentions one, and the reference named for its role.
    """
    if role == TASK_AGENT:
        return "\n".join(f.read_text(encoding="utf-8") for f in TASK_AGENT_READS)
    agent = AGENTS / f"comment-review-{role}.md"
    if not agent.exists():
        return None
    text = agent.read_text(encoding="utf-8")
    named = set(READS.findall(text))
    if BRIEF[0] in text.lower():
        named.add(BRIEF[1])
    # A stage agent is handed the procedure named for its role -- `compact.md`
    # for `compact` -- and no longer names the file, because naming it is a path
    # into the installed plugin. Derived from the tree, never listed here.
    named.add(f"{role}.md")
    for name in sorted(named - NOT_DERIVED):
        reference = REFERENCES / name
        if reference.exists():
            text += "\n" + reference.read_text(encoding="utf-8")
    return text


def check_complete(definitions: dict[str, str], roles: dict[str, list[str]]) -> int:
    """Report every hole in the shipped vocabulary. Returns how many."""
    holes = 0
    for role, keys in sorted(roles.items()):
        for key in keys:
            if key not in definitions:
                print(f"vocabulary.toml  NO DEFINITION  {role} is given {key!r}")
                holes += 1
    given = set().union(*(set(keys) for keys in roles.values()))
    for term in sorted(set(definitions) - given):
        print(f"vocabulary.toml  NO RECIPIENT   {term!r} is defined for nobody")
        holes += 1
    # ! The shared row is not a role; every other key is. Counted rather than
    # assumed, so a missing shared row does not shift the
    # number, though a second non-role key would still count as a role.
    roles_n = len([r for r in roles if r != EVERY_AGENT])
    print(f"\n{len(definitions)} definitions across {roles_n} roles, {holes} holes.")
    return holes


def check_drift(definitions: dict[str, str], roles: dict[str, list[str]]) -> int:
    """Report every way the roles, their agent files and their terms drift.

    Each term a role is given but never uses, and the reverse; each agent file
    with no role row, and each role row with no agent file. Returns how many.
    """
    shared = set(roles.get(EVERY_AGENT, []))
    drift = 0
    # !! EVERY AGENT FILE, not every row of the table. Enumerating from
    # `vocabulary.toml` alone meant a new agent with no row there was never
    # checked -- the gate printed "N roles checked, 0 drifted" and exited 0
    # while that agent used defined terms it had never been given, which is the
    # drift this check exists to catch. The table is one of the two things that
    # can be out of date, and it cannot be the one that decides.
    on_disk = {
        f.stem[len("comment-review-") :] for f in AGENTS.glob("comment-review-*.md")
    }
    for missing in sorted(on_disk - set(roles) - {EVERY_AGENT}):
        print(f"vocabulary.toml  NO ROLE ROW  for agent {missing!r}")
        drift += 1
    for role, keys in sorted(roles.items()):
        if role == EVERY_AGENT:
            continue
        text = text_for(role)
        if text is None:
            print(f"vocabulary.toml  NO AGENT FILE  for role {role!r}")
            drift += 1
            continue
        given = shared | set(keys)
        used = {t for t in definitions if term_used(text, t)}
        for term in sorted(given - used):
            print(f"vocabulary.toml  UNUSED   {role} is given {term!r}, never uses it")
            drift += 1
        for term in sorted(used - given):
            print(f"vocabulary.toml  MISSING  {role} uses {term!r}, is not given it")
            drift += 1
    print(
        f"\n{len([r for r in roles if r != EVERY_AGENT])} roles checked against"
        f" the text they read, {drift} drifted."
    )
    return drift


def doc_defines(text: str) -> list[str]:
    """The terms `docs/vocabulary.md` DEFINES, in order.

    ! The RETIRED table names shipped terms on purpose -- a record of a rename
    has to say what the word became -- so only the rows above that heading are
    definitions. Splitting there is what lets the record keep naming `paragraph`
    while the gate still refuses a second definition of it.

    Args:
        text: the document.

    Returns:
        Every term the live tables define.
    """
    return DOC_TERM.findall(text.split(RETIRED_HEADING)[0])


def check_duplicate(definitions: dict[str, str]) -> int:
    """No term defined in the shipped file is defined AGAIN in `docs/vocabulary.md`.

    !! TWO COPIES OF ONE DEFINITION DRIFT, AND THE DRIFT IS SILENT. Measured
    2026-08-19: six terms carried a definition in both files, and the two copies
    of `anchor` had already disagreed -- the shipped one said an `a` is attached
    to "its declaration", the doc said "the LINE that declares it ... and the
    name is not carried at all". Every role was handed the first and every human
    read the second, and the gap survived a session that was about the anchor.

    ! The doc is the record of what CHANGED. A term still in use is defined
    where it is EMITTED from and nowhere else, which is the rule this function enforces.

    Returns:
        How many shipped terms the doc defines a second time, or 1 when the doc
        cannot be read.
    """
    try:
        text = DOC.read_text(encoding="utf-8")
    except READ_ERRORS as e:
        print(f"docs/vocabulary.md  UNREADABLE  {type(e).__name__}: {e}")
        return 1
    dupes = 0
    for term in doc_defines(text):
        if term in definitions:
            print(
                f"docs/vocabulary.md  DUPLICATE  {term!r} is defined here and"
                " emitted from vocabulary.toml -- delete this copy"
            )
            dupes += 1
    print(f"\n{len(definitions)} shipped terms, {dupes} defined twice.")
    return dupes


def check_retired() -> int:
    """No shipped file uses a retired word, unless it declares the exemption.

    ! It reads what SHIPS only -- every `.md`, `.py` and `.toml` file
    under `src/`. `docs/` records what was
    decided and when, and `tests/` names fixtures after the format they exercise;
    neither is handed to an agent, and rewriting the record is how a record
    stops being one.
    """
    bad = 0
    for path in sorted((REPO / "src").rglob("*")):
        if not path.is_file() or path.suffix not in (".md", ".py", ".toml"):
            continue
        text = path.read_text(encoding="utf-8")
        if NOQA in text:
            continue
        for word, instead in RETIRED.items():
            hay = text
            for allowed in (*MENTION, *NOT_THE_TERM):
                hay = hay.replace(allowed, "")
            # ! NOT `\w`: `_` is a word character, and a retired noun inside an
            # identifier -- `block_problem` -- is the retired noun. A hyphen
            # still bounds a word, so `block-context`, a role name, is one.
            pattern = rf"(?<![A-Za-z0-9-]){word}(?![A-Za-z0-9-])"
            hits = len(re.findall(pattern, hay, re.I))
            if hits:
                rel = path.relative_to(REPO).as_posix()
                print(f"{rel}  RETIRED  {hits}x {word!r} -- say {instead!r}")
                bad += hits
    print(f"\n{len(RETIRED)} retired words, {bad} uses in the shipped tree.")
    return bad


def main() -> int:
    """Run all four checks; exit nonzero if any found something."""
    # ! A Windows console is cp1252; one non-ASCII glyph in this program's own
    # output kills the run. Every CLI in this repo carries this, and
    # `tests/gates/test_shipped_cli_encoding.py` is the gate.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    try:
        data = tomllib.loads(EMITTED.read_text(encoding="utf-8"))
    except READ_ERRORS as e:
        print(f"cannot read {EMITTED}: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    definitions, roles = data["definitions"], data["roles"]
    holes = check_complete(definitions, roles)
    dupes = check_duplicate(definitions)
    drift = check_drift(definitions, roles)
    retired = check_retired()
    return 1 if (holes or dupes or drift or retired) else 0


if __name__ == "__main__":
    sys.exit(main())
