"""Print the vocabulary one agent is given, for the task agent to paste verbatim.

    python vocabulary.py --reviewer ownership-context
    python vocabulary.py --roles

The task agent runs this at stage 4 and puts the output in that agent's prompt,
verbatim. A definition lives in exactly one place and reaches an agent by being
EMITTED: a shipped file that uses a term states no definition of its own.

Which terms a role is given was MEASURED from the text that role actually reads,
and lives in `references/vocabulary.toml` beside the definitions themselves.

! Reads the TOML with `tomllib`, stdlib from Python 3.11, which is the floor
this plugin ships against. A version mismatch in an IMPORT gets past a
syntax-only gate, so the floor is stated in `scripts/check_shipped_syntax.py`
and enforced by parsing every shipped file at it.
"""

import argparse
import sys
import tomllib
from enum import StrEnum
from pathlib import Path

VOCABULARY = Path(__file__).resolve().parent.parent / "references" / "vocabulary.toml"

# The key every role's list is extended with. A shared set, and no role's name.
EVERY_AGENT = "all"

READ_ERRORS = (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError)


class Reviewer(StrEnum):
    """Every agent that can be given a vocabulary, named as the skill dispatches it."""

    OWNERSHIP_CONTEXT = "ownership-context"
    BLOCK_CONTEXT = "block-context"
    FUNCTION_CONTEXT = "function-context"
    MODULE_CONTEXT = "module-context"
    COMPACT = "compact"
    REVIEW = "review"


def load() -> tuple[dict[str, str], dict[str, list[str]]]:
    """The definitions and the per-role key lists, as the file states them."""
    data = tomllib.loads(VOCABULARY.read_text(encoding="utf-8"))
    return data["definitions"], data["roles"]


def terms_for(role: str, roles: dict[str, list[str]]) -> list[str]:
    """The terms one agent is given: the shared set plus its own, sorted."""
    return sorted(set(roles.get(EVERY_AGENT, [])) | set(roles.get(role, [])))


def render(role: str, definitions: dict[str, str], roles: dict[str, list[str]]) -> str:
    """The block that goes into the agent's prompt."""
    wanted = terms_for(role, roles)
    missing = [t for t in wanted if t not in definitions]
    if missing:
        raise KeyError(
            f"{role} is given terms with no definition: {', '.join(missing)}"
        )
    lines = [
        "## VOCABULARY",
        "",
        "These words have one meaning in this system. Where you are unsure what a",
        "word means, it is here; where it is not here, it is ordinary English.",
        "",
    ]
    lines += [f"- **{term}** -- {definitions[term]}" for term in wanted]
    return "\n".join(lines) + "\n"


def main() -> int:
    """Print one role's vocabulary, or the roles that have one."""
    # !! UTF-8 with replacement, because this output is PASTED VERBATIM into a
    # reviewer's prompt: corruption here reaches an agent as instruction.
    # Measured 2026-08-17 on a live run -- without this, a `cp1252` console
    # corrupted every dash and exited 0, and a PowerShell redirect wrote UTF-16
    # that read as a binary file. The dispatch went out with three roles
    # instead of four.
    #
    # ! What it defends has CHANGED. That run corrupted this file's own em
    # dashes; since the tree went ASCII there are none, and `vocabulary.toml`
    # holds no character above U+007F. The guard now stands against a
    # definition someone else adds, not against the text shipped here.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reviewer", choices=[r.value for r in Reviewer])
    ap.add_argument("--roles", action="store_true", help="list the roles and exit")
    args = ap.parse_args()

    try:
        definitions, roles = load()
    except READ_ERRORS as e:
        print(f"cannot read {VOCABULARY}: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    if args.roles:
        for role in Reviewer:
            print(f"{role.value:<20} {len(terms_for(role.value, roles))} terms")
        return 0

    if not args.reviewer:
        ap.error("one of --reviewer or --roles is required")

    try:
        print(render(args.reviewer, definitions, roles), end="")
    except KeyError as e:
        print(e.args[0], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
