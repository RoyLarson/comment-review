"""The shipped vocabulary holds: complete, and honest about who needs what.

    uv run python scripts/check_vocabulary.py

`src/comment_review/references/vocabulary.toml` is the single source for the
terms agents receive, and the task agent hands each role the entries its
`[roles]` row lists. Four checks, and each exists because the thing it looks for
had already gone wrong unnoticed:

  COMPLETE  Every key a role is given has a definition, and no definition is
            written for nobody. That file is what agents are HANDED, so a term
            with no recipient belongs in `docs/vocabulary.md` instead.
  DUPLICATE No term defined here is defined AGAIN in `docs/vocabulary.md`. One
            source, one copy: a second copy drifts, and the drift is silent.
  DRIFT     Every term a role is given appears in the text that role reads, and
            every term it reads is given. The rule is "give a role the terms its
            text uses", so the lists go stale whenever the prose is edited.
  RETIRED   No shipped file uses a word the vocabulary retired. Nothing enforced
            this, so `block` survived in 298 places after `paragraph` replaced
            it, and the shipped definition of a block still read "the interval
            between two lines of CODE" -- a shape a prose file does not have.
            The retired words and their exemptions are data, in
            `scripts/retired_words.toml`.

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
# The retired words, the strings the RETIRED scan strips first, and the marker.
RETIRED_WORDS = REPO / "scripts/retired_words.toml"


def _load_retired_words(path: Path) -> dict:
    """The retired-word tables, each entry checked for its reason.

    Args:
        path: the toml file holding `noqa`, `retired`, `mention` and
            `not_the_term`.

    Returns:
        The parsed file.

    Raises:
        ValueError: an entry carries no `why`.
    """
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    tables = (data["retired"], data["mention"], data["not_the_term"])
    for entry in (data["noqa"], *(e for table in tables for e in table)):
        if not entry.get("why"):
            raise ValueError(f"{path.name}: an entry carries no `why`: {entry}")
    return data


_TABLES = _load_retired_words(RETIRED_WORDS)
# A retired word -> the word a shipped file says instead.
RETIRED = {e["word"]: e["instead"] for e in _TABLES["retired"]}
# Backticked forms that quote a retired word rather than use it.
MENTION = tuple(e["form"] for e in _TABLES["mention"])
# Exact strings that contain a retired word and are not it, stripped in order.
NOT_THE_TERM = tuple(e["form"] for e in _TABLES["not_the_term"])
# A file carrying this marker is exempt from the RETIRED check, whole.
NOQA = _TABLES["noqa"]["marker"]

REFERENCES = REPO / "src/plugin/skills/comment-review/references"
# The vocabulary is package data: it ships inside the `comment_review` package,
# where SKILL.md has the task agent read it. The `.md` references live with the
# plugin's prose under `src/plugin/`; agents and this gate read them, and no
# shipped code does.
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

BRIEF = ("brief", "reviewer-brief.md")

# The key every role's list is extended with. Not a role.
EVERY_AGENT = "all"

# The one role with no agent file.
TASK_AGENT = "task-agent"

# The task agent runs from SKILL.md and loads `write.md` at stage 7b; every other
# reference it names is handed to another agent, so its text is those two.
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
    # assumed, so a missing shared row does not shift the number, though a
    # second non-role key would still count as a role.
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

    ! It reads what SHIPS only -- every `.md`, `.py` and `.toml` file under
    `src/`. `docs/` records what was decided and when, and `tests/` names
    fixtures after the format they exercise; neither is handed to an agent, and
    rewriting the record is how a record stops being one.
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
