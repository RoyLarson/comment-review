"""The shipped vocabulary holds: complete, and honest about who needs what.

    python scripts/check_vocabulary.py

`references/vocabulary.toml` is the single source for the terms agents receive,
and `scripts/vocabulary.py` emits each role's set into its prompt. Four checks,
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
would go stale exactly the way the term lists did. ! It matches the DOCUMENT,
never a path -- a shipped file naming its own location sends the agent to the
installed plugin rather than to the absolute path it was handed.

! It once also checked `file:line` citations in the vocabulary SURVEY documents.
Those documents are gone -- they were the apparatus for finding the terms, and
the terms are settled -- so the check went with them.

!! ONE HANDED DOCUMENT IS DELIBERATELY NOT DERIVED, and `NOT_DERIVED`
below names it and says why. It is stated there rather than here because
the exclusion used to happen by accident.

Exits nonzero if any check finds something.
"""

import re
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGENTS = REPO / "plugins/comment-review/agents"

# !! WHAT THE VOCABULARY RETIRED, and the word that replaced it. A shipped file
# may not use the left-hand side.
RETIRED = {
    "block": "paragraph",
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
    "folio": "cue",
    "folios": "cues",
    "foliation": "cues",
    "foliator": "addresser",
    "foliate": "cue",
    # !! `leaf` IS NOT HERE AND THAT IS DELIBERATE. The PAGE sense went with the
    # rest -- one sheet carries TWO pages, so it was neither the page nor the
    # cue, and a file has no verso. But the DEPENDENCY-GRAPH sense is live and
    # correct: `constants.py`'s ULTIMATE LEAF, ruled by Roy 2026-08-22. Retiring
    # the word would refuse that, and `leaves` is an ordinary English verb --
    # measured 2026-08-23, it fired on 15 sentences reading *"leaves it
    # unaccounted for"*. ! The two senses are declared polysemy; see
    # `docs/vocabulary.md` and `TODO/leaf-means-two-things.md`.
    #
    # !! `join` AS A NOUN IS RETIRED, 2026-08-27. Roy: *"'The join' was too
    # ambiguous. It didn't define anything and you used it as a shortcut that
    # could have meant many different operations."* MEASURED: 202 live uses
    # carrying FIVE referents -- the `verdicts.py` program, linking two data
    # structures, checking a mark against its page, a git merge, and ordinary
    # English. `decision-log.md Vocabulary: #19`.
    #
    # ! THE VERB IS LIVE AND NECESSARY -- `"".join(...)` appears 28 times in the
    # shipped tree -- so `.join(` is declared below rather than the word being
    # left out of this table. The `(?![\w-])` in `check_retired` already spares
    # `joins`, `joined` and `joining`; only the bare noun is refused.
    "join": "the collator",
}

# !! THE WAY OUT, AND IT IS PER FILE. Roy, 2026-08-19: *"let's give ourselves a
# `# noqa: vocabulary` out on the files that are not about the prose or the
# current representation. Let's make certain to move the code into separate
# files to make it easy."*
#
# ! A file carrying this marker is EXEMPT WHOLE, which is why the code that
# needs it was moved out first: `held.py` reads a format that no longer ships
# and must say `BLOCK`, because that is the line marker in reports already on
# disk. Renaming it there made 173 of 173 held records unreadable, measured
# 2026-08-19. Exempting a line rather than a file would let the retired word
# creep back into a file that is about the CURRENT representation, one
# suppression at a time.
NOQA = "# noqa: vocabulary"

# !! A RETIRED WORD *NAMED* IS NOT A RETIRED WORD *USED*, and the difference is
# the backticks. `paragraph`'s own definition says *"`block` is the older word
# for it"*, and `page.py` explains what `block` meant before -- both are how this
# repo keeps an error legible instead of erasing it, which is the same rule that
# keeps a SUPERSEDED task checked rather than deleted. A sentence that USES the
# word to mean the thing is what this catches.
MENTION = ("`block`", "`blocks`", "`block=", "`BLOCK`", "`BLOCK ", "`pCST`")

# !! A QUOTATION IS NOT AN EXEMPTION, AND THERE IS NOTHING TO EXEMPT. Ruled by
# Roy, 2026-08-23: *"It simply isn't necessary to know the history to understand
# the code. It is a bad habit to think it needs it."* A shipped file states what
# the code does NOW. A ruling quoted in the words it was made in is history, and
# history is in the git commits for whoever wants it.
#
# ! A CITATION IS THE SAME PROSE ONE INDIRECTION ALONG. Pointing a comment at an
# entry that holds the old wording keeps the history in reach of the code, which
# is the thing the rule exists to stop. The comment states the rule and the
# reason it is that way; neither needs a date, an attribution or a link.
#
# ! THE COST OF THE ALTERNATIVE IS THE MECHANISM `README.md`'s *Why* records: a
# dead term is a CONTEXT ANCHOR, and quotation marks do not stop a word reaching
# an LLM's attention. A human reads the marks and discounts the word, which is
# exactly the imprecision an agent does not share.

# ! And these are not the retired term at all, by exact form:
#   block-context   a ROLE NAME -- an agent id, a filename, a `--reviewers`
#                   value, and the stem every held report is filed under
#   TEXT BLOCK      a Java language feature
#   block: int      the DEPRECATED 0.2.x record index on `Finding`, which names
#                   a field in reports already written. `.block` and `block=`
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
# that does not exist. Five sites, filed as `the-rename-corrupted-live-prose`.
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
NOT_THE_TERM = (
    # ! Python's own str.join -- the VERB, and 28 sites in the shipped tree.
    ".join(",
    "block-context",
    "TEXT BLOCK",
    "block_matches",
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
REFERENCES = REPO / "plugins/comment-review/skills/comment-review/references"
# !! THE TOML IS PACKAGE DATA AND NO LONGER SITS BESIDE THE `.md` REFERENCES.
# `vocabulary.py` reads it relative to its own `__file__`, so it has to travel
# with the code; the `.md` files beside it are read by AGENTS, not by any
# script, and stay in the skill. Moved 2026-08-24 with the package -- a source
# tree that reached into `plugins/` for its own data would depend on the tree
# that is BUILT FROM it.
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

# !! HANDED TO A ROLE AND DELIBERATELY NOT DERIVED. `re-review.md` reaches the
# four editorial roles in a round-2 message the way the brief reaches them in
# round 1, so the rule above says it should be part of their text. Deriving it
# adds exactly one term to all four -- `cap` -- and those are the roles the cap
# is never passed to, because length is not an editorial role. A per-role
# vocabulary is one list, so a document's terms cannot be handed minus one.
#
# !! IT IS NAMED HERE BECAUSE IT WAS EXCLUDED BY ACCIDENT. Nothing referred to
# the file: the four reviewer agents happen not to name it in backticks, so
# `text_for` never reached it. Adding it to an agent file -- which the round-2
# protocol arguably calls for -- would have started the derivation and failed
# the gate over `cap`, with the reason sitting in a docstring nobody reads at
# that moment.
#
# ! The cost is that this file's own terms are checked by nothing, and it
# introduces one: `galley`, defined inline there for that reason. The deeper
# answer is to split it by audience -- the task agent learns when a round fires,
# the role learns what it is given, and `cap` is in the task agent's half.
NOT_DERIVED = frozenset({"re-review.md"})
BRIEF = ("brief", "reviewer-brief.md")

# The key every role's list is extended with. Not a role.
EVERY_AGENT = "all"

READ_ERRORS = (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError)


def term_used(text: str, term: str) -> bool:
    """Whether prose uses this term as a word, singular or plural."""
    return bool(re.search(r"(?<![\w-])" + re.escape(term) + r"s?(?![\w-])", text, re.I))


def text_for(role: str) -> str | None:
    """Everything one role reads: its agent file, and the reference it names."""
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
    # assumed, so a second non-role key would not silently shift the number.
    roles_n = len([r for r in roles if r != EVERY_AGENT])
    print(f"\n{len(definitions)} definitions across {roles_n} roles, {holes} holes.")
    return holes


def check_drift(definitions: dict[str, str], roles: dict[str, list[str]]) -> int:
    """Report every term a role is given but never uses, and the reverse."""
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
    where it is EMITTED from and nowhere else, which is the rule
    `scripts/vocabulary.py` already states and nothing enforced.

    Returns:
        How many shipped terms the doc defines a second time.
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

    ! It reads the SHIPPED tree only. `docs/` records what was decided and when,
    and `tests/` names fixtures after the format they exercise; neither is handed
    to an agent, and rewriting the record is how a record stops being one.
    """
    bad = 0
    for path in sorted((REPO / "plugins").rglob("*")):
        if not path.is_file() or path.suffix not in (".md", ".py", ".toml"):
            continue
        text = path.read_text(encoding="utf-8")
        if NOQA in text:
            continue
        for word, instead in RETIRED.items():
            hay = text
            for allowed in (*MENTION, *NOT_THE_TERM):
                hay = hay.replace(allowed, "")
            hits = len(re.findall(rf"(?<![\w-]){word}(?![\w-])", hay, re.I))
            if hits:
                rel = path.relative_to(REPO).as_posix()
                print(f"{rel}  RETIRED  {hits}x {word!r} -- say {instead!r}")
                bad += hits
    print(f"\n{len(RETIRED)} retired words, {bad} uses in the shipped tree.")
    return bad


def main() -> int:
    """Run both checks; exit nonzero if either found something."""
    # ! A Windows console is cp1252; one non-ASCII glyph in this program's own
    # output kills the run. Every CLI in this repo carries this, and
    # `tests/test_shipped_cli_encoding.py` is the gate -- it globbed only the
    # shipped `plugins/` scripts until 2026-08-17, which is how four of these
    # went without it.
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
