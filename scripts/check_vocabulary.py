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

! The role -> files mapping is DERIVED, not listed here: an agent file names the
document it is told to read, so this reads it out of the tree. A listed copy
would go stale exactly the way the term lists did. ! It matches the DOCUMENT,
never a path -- a shipped file naming its own location sends the agent to the
installed plugin rather than to the absolute path it was handed.

! It once also checked `file:line` citations in the vocabulary SURVEY documents.
Those documents are gone -- they were the apparatus for finding the terms, and
the terms are settled -- so the check went with them.

!! ONE HANDED DOCUMENT IS DELIBERATELY NOT COVERED: `re-review.md`. It reaches
the four editorial roles in a round-2 message the way the brief reaches them in
round 1, so by the rule above it should be part of their text -- and it cannot
be. Measured 2026-08-17: deriving it adds exactly one term to all four,
**`cap`**, and the four reviewers are the roles the cap is never passed to,
because length is not an editorial role. A per-role vocabulary is one list, so
there is no way to hand a role a document's terms minus one.

! The cost is that `re-review.md`'s own terms are checked by nothing, and it
introduces one -- **galley** -- which is therefore defined inline there rather
than in `vocabulary.toml`. An entry would have to be given to a role, the drift
check would find the word in no text that role reads, and the gate would refuse
it.

! The underlying reason is that `re-review.md` addresses TWO audiences: the task
agent, which learns when a round fires and when the rounds stop, and the role
being re-reviewed, which learns what it is given and what to return. `cap` is in
the task agent's half. Splitting the file would make both halves derivable; it
has not been done.

Exits nonzero if either check finds something.
"""

import re
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGENTS = REPO / "plugins/comment-review/agents"
REFERENCES = REPO / "plugins/comment-review/skills/comment-review/references"
EMITTED = REFERENCES / "vocabulary.toml"

# How an agent file names the document it is told to read. ! It names the
# DOCUMENT and never its location: a shipped file that spells out a path sends
# the agent looking for it in the installed plugin instead of using the absolute
# path the task agent passed in. So this matches a backticked filename, and the
# four reviewers -- which name no file, because the brief is HANDED to them in
# their prompt -- are matched on the word.
READS = re.compile(r"`([\w-]+\.md)`")
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
    for name in sorted(named):
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
    return 1 if (holes or drift) else 0


if __name__ == "__main__":
    raise SystemExit(main())
