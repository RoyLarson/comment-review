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

⚠ The role -> files mapping is DERIVED, not listed here: an agent file names the
reference it is told to read, so this reads it out of the tree. A listed copy
would go stale exactly the way the term lists did.

⚠ It once also checked `file:line` citations in the vocabulary SURVEY documents.
Those documents are gone -- they were the apparatus for finding the terms, and
the terms are settled -- so the check went with them.

Exits nonzero if either check finds something.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGENTS = REPO / "plugins/comment-review/agents"
REFERENCES = REPO / "plugins/comment-review/skills/comment-review/references"
EMITTED = REFERENCES / "vocabulary.toml"

# `references/<name>.md` as an agent file names the one it is told to read.
READS = re.compile(r"references/([\w-]+\.md)")

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
    for name in sorted(set(READS.findall(text))):
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
    roles_n = len(roles) - 1
    print(f"\n{len(definitions)} definitions across {roles_n} roles, {holes} holes.")
    return holes


def check_drift(definitions: dict[str, str], roles: dict[str, list[str]]) -> int:
    """Report every term a role is given but never uses, and the reverse."""
    shared = set(roles.get(EVERY_AGENT, []))
    drift = 0
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
        f"\n{len(roles) - 1} roles checked against the text they read, {drift} drifted."
    )
    return drift


def main() -> int:
    """Run both checks; exit nonzero if either found something."""
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
