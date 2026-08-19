"""The shipped vocabulary holds: complete, and honest about who needs what.

    python scripts/check_vocabulary.py

`references/vocabulary.toml` is the single source for the terms agents receive,
and `scripts/vocabulary.py` emits each role's set into its prompt. Two checks, and
each exists because the thing it looks for had already gone wrong unnoticed:

  COMPLETE  Every key a role is given has a definition, and no definition is
            written for nobody. That file is what agents are HANDED, so a term
            with no recipient belongs in `docs/vocabulary.md` instead.
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

Exits nonzero if either check finds something.
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
# for it"*, and `pcst.py` explains what `block` meant before -- both are how this
# repo keeps an error legible instead of erasing it, which is the same rule that
# keeps a SUPERSEDED task checked rather than deleted. A sentence that USES the
# word to mean the thing is what this catches.
MENTION = ("`block`", "`blocks`", "`block=", "`BLOCK`", "`BLOCK ")

# ! And these are not the retired term at all, by exact form:
#   block-context   a ROLE NAME -- an agent id, a filename, a `--reviewers`
#                   value, and the stem every held report is filed under
#   TEXT BLOCK      a Java language feature
#   block: int      the DEPRECATED 0.2.x record index on `Finding`, which names
#                   a field in reports already written. `.block` and `block=`
#                   are the same field read and written.
NOT_THE_TERM = (
    "block-context",
    "TEXT BLOCK",
    "block_matches",
    "block: int",
    ".block",
    "block=",
    '"BLOCK"',
)
REFERENCES = REPO / "plugins/comment-review/skills/comment-review/references"
EMITTED = REFERENCES / "vocabulary.toml"

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
    drift = check_drift(definitions, roles)
    retired = check_retired()
    return 1 if (holes or drift or retired) else 0


if __name__ == "__main__":
    sys.exit(main())
