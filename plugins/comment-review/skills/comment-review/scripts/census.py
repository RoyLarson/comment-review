"""Stages 2-3 of comment-review: ANNOTATE, then FIND REFERENCES.

Two outputs, and the first one is the point:

  CENSUS      every comment run and every docstring, numbered, with the marks
              attached to it. The reviewers walk this list; a block missing from
              it is a block nobody reviews.
  RESOLUTION  the questions a symbol table and a filesystem can settle. A
              reviewer that spends its budget re-deriving these has spent it
              badly.

    python census.py [--repo D] [--cap N] [--width N] [--census-only] [--json] <paths>

Read-only, and always exits 0 — this is an input to a review, not a gate.
Nothing here is a verdict: `names-a-symbol` in particular is a CANDIDATE list,
because a backticked token can name a config key, a record field or an API
payload rather than a symbol, and no resolver knows every namespace a repo
speaks.

The census is built at the TIER available for each file's language. Both tiers
find the same blocks; they differ only in what else they can say:

  tokenized  a lexer + AST (Python, from the stdlib)   + DOCSTRING owners
  lexical    a comment-syntax record, nothing else     blocks and marks

⚠ NO COMMENT carries an owner at either tier, so every locality verdict rests
on a reviewer READING the file. A docstring's owner comes free from the AST; a
`#` run's does not, and nothing here infers it. Treat placement findings as
CANDIDATES.

⚠ A libcst tier that DID resolve comment owners was measured and removed on
2026-08-14: it owned 50% of blocks and silently missed 13 that the stdlib tier
found, because a comment inside an expression belongs to no node's
`leading_lines`. Coverage beats ownership, and the tier was Python-only besides
-- recorded in the project repository, not in the shipped plugin.

⚠ Tier counts are AGGREGATED over the run, not reported per file. On a polyglot
run you cannot tell which file reached which tier -- which is exactly when it
matters. Adding a language is a row in `LANGUAGES` — data, not code — which is
what keeps the floor cheap enough to be worth having. `--languages` lists what
is known.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import subprocess
import sys
import tokenize
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# ⚠ Bound to a NAME so no `except` clause here holds a tuple LITERAL. Under
# `target-version = "py314"` a formatter rewrites `except (A, B):` into PEP
# 758's unparenthesised form, a SyntaxError on every older interpreter. This
# file ships into other repositories and is formatted by THEIR config, so a
# floor in our own pyproject cannot protect it -- only writing code that has
# nothing to rewrite can. A `noqa` was tried and did not hold.
READ_ERRORS = (OSError, UnicodeDecodeError)
# Same reason, second construct: `isinstance(x, A | B)` PARSES on 3.9 and
# raises TypeError there. A syntax check cannot see it, so the tuple form is
# the one that actually runs where this file is claimed to run.
NAMED_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
DOC_OWNERS = (ast.Module,) + NAMED_DEFS
PARSE_ERRORS = (OSError, UnicodeDecodeError, SyntaxError)
GIT_ERRORS = (OSError, subprocess.SubprocessError)

# A virtualenv in the tree POISONS the name corpus: every installed package's
# methods become "known", so a real obituary is suppressed because some library
# happens to define that name. It also makes the count depend on what is
# installed, which is why an earlier measurement did not reproduce.
EXCLUDED_DIRS = frozenset(
    {"__pycache__", ".venv", "venv", "site-packages", "node_modules", ".git"}
)

# Free markers point OUTWARD, at work that is not done, so they are not the
# explanation and must not spend its budget. A cap that counts them makes
# deleting the pointer to filed work the cheapest route to green.
MARKERS = ("TODO", "FIXME", "HACK", "XXX", "BUG")
WORK_MARKER = re.compile(r"^(" + "|".join(MARKERS) + r")\b")
# ⚠ Every punctuation a language opens a comment with, stripped before the
# marker is matched. Anchoring on `#` made the exemption Python-only in a
# script that censuses eleven languages: a `// TODO:` was charged to the cap,
# so the cheapest route to green stayed "delete the pointer to filed work" —
# exactly the outcome the exemption exists to prevent.
LEAD_PUNCT = re.compile(r"^[\s#/*\-!=;%<>]+")


def counted_lines(raw: list[str]) -> int:
    """Lines a cap should charge for: a marker LINE itself is free.

    A marker points outward, at work that is not done, so it is not the
    explanation and must not spend the explanation's budget. It must not
    validate an invalid block either, so it never splits a run and a marker's
    continuation lines still count. Six lines plus a `TODO:` is six.

    Declared and unused until 2026-08-14, so earlier runs charged the cap for
    exempt markers. A block reading 7L to the script and 6 by the rule makes
    deleting a pointer to filed work the cheapest route to green.
    """
    return sum(1 for ln in raw if not WORK_MARKER.match(LEAD_PUNCT.sub("", ln)))


# ── Marks ─────────────────────────────────────────────────────────────────────
# Each is located here and RESOLVED below. Locating is most of the work; the
# resolution is what stops a reviewer treating a citation as a verified claim.

PATH_CITE = re.compile(r"`?([\w./-]+\.(?:py|md|toml|txt|json|ya?ml))(?:::(\w+))?`?")
TICKED = re.compile(r"`([^`\s]+)`")
# A token that could name a symbol. Single words count: every one-word module in
# a package is otherwise invisible, and a deleted one is the commonest obituary.
# A trailing call form is stripped — `foo()` is the clearest way prose marks a
# function, and the shape that most often escapes the check.
CALLFORM = re.compile(r"\(\s*(?:\.\.\.|…)?\s*\)$")
SYMBOLISH = re.compile(r"^[A-Za-z_][\w.]*$")
NOT_A_SYMBOL = frozenset(
    {"true", "false", "none", "null", "and", "or", "not", "if", "in", "is"}
)

COUNTED = re.compile(
    r"(?i)\b(one|two|three|four|five|six|seven|eight|nine|ten|only|every|all|no|"
    r"single|exactly|\d+)\s+"
    r"(call sites?|callers?|files?|modules?|tests?|readers?|consumers?|copies|"
    r"producers?|renderers?|writers?|places?|definitions?|sources?|entry points?)\b"
)
COVERAGE = re.compile(
    r"(?i)\b(pinned|guarded|asserted|enforced|covered|checked|locked)\s+(by|in)\b"
    r"|\bthe only call site\b|\bread by nothing\b|\bno reader\b|\bwrite-only\b"
    r"|\bsingle source of truth\b|\bnothing (reads|calls|enforces)\b"
)
FORBIDS = re.compile(
    r"(?i)\b(never|must not|do not|don't|no)\b[^.]{0,80}?"
    r"(\b\d+(?:\.\d+)?\b|`[^`]+`|\bliteral\b|\bhardcod\w+\b)"
)
# A bare number in prose. Cheap to find, and worth nothing until it is seen
# twice — the pair is where a hand-copied threshold drifts from its twin.
# ⚠ Dates are stripped first. Left in, every `2026-08-09` contributes three
# "repeated" numbers, and the detector drowns in its own noise — the shape a
# suppression list exists to prevent.
NUMBER = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.%])")
DATEISH = re.compile(r"\b\d{4}-\d{2}-\d{2}\w*|\bv?\d+\.\d+\.\d+\b")


def prose_numbers(text: str) -> set[str]:
    """Numbers a reader would call a VALUE — dates and versions removed."""
    return {n for n in NUMBER.findall(DATEISH.sub(" ", text)) if len(n) > 1}


NARRATIVE = {
    "a date": re.compile(r"\b\d{4}-\d{2}-\d{2}\w*"),
    "a review label": re.compile(
        r"(?i)\bfix (wave|round)\b|\bfinding [A-Z]?\d|\breview finding\b"
        r"|\bround \d\b|\bCRITICAL [A-Z0-9]\b"
    ),
    # ⚠ `used to` needs a VERB OF SAYING after it, not any verb. A bare
    # `\bused to\b` matches "often used to model a count process" -- ordinary
    # English about what a thing is FOR, not a claim about what the code once
    # was. Measured on a scientific library: 4 hits, 4 false, and that was the
    # entire narrative class on that corpus.
    "a retraction": re.compile(
        r"(?i)\bretract(ed|ion)?\b|\bpreviously\b|\bno longer\b"
        r"|\bused to (say|read|be|claim|mean|do|call|live|sit|carry|hold|return)\b"
        r"|\ban earlier (version|draft)\b|\bas before\b"
    ),
    "a rejected alternative": re.compile(
        r"(?i)considered and rejected|\brejected in favou?rs? of\b"
        r"|\bwas tried and\b|\balternatives? (were|was) (considered|rejected)\b"
    ),
}

# A runnable usage line is exempt from the narrative check: a date in
# `--start 2026-07-14` is a copy-pasteable EXAMPLE, not a claim about history.
# Without this the sweep pushes a working command out of a docstring in favour
# of a placeholder, degrading the docs to please a checker.
COMMAND_LINE = re.compile(r"^\s*(\$ |uv run |python |pytest |npm |cargo |go )")


@dataclass
class Block:
    """One comment run or one docstring — the unit a reviewer rules on."""

    path: str
    start: int
    end: int
    kind: str  # "comment" | "docstring"
    lines: int
    text: str  # the run JOINED, so a wrapped claim matches as one string
    owner: str = ""  # the declaration it annotates, when structurally known
    tier: str = "lexical"  # which question set this file's census can answer
    marks: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)

    @property
    def widest(self) -> int:
        """The longest raw line in this block, in characters."""
        return max((len(ln) for ln in self.raw_lines), default=0)

    raw_lines: list[str] = field(default_factory=list)


def _join(lines: list[str], markers: tuple[str, ...] = ("#",)) -> str:
    """A comment run as ONE normalised string, its comment markers stripped.

    Prose wraps, so every claim-bearing phrase in a real file straddles a line
    break. Matching line-by-line reports the fragment instead of the claim: a
    count reads as absent and `used to say` degrades to a bare `used to`.

    Args:
        lines: the run's raw source lines.
        markers: the language's comment openers, longest first at the call site
            so `///` is stripped before `//` leaves a stray slash in the prose.
    """
    out = []
    for ln in lines:
        s = ln.strip()
        for m in markers:
            if s.startswith(m):
                s = s[len(m) :].strip()
                break
        out.append(s)
    return re.sub(r"\s+", " ", " ".join(out)).strip()


@dataclass(frozen=True)
class Language:
    """What the LEXICAL tier needs to find prose in a language it cannot parse.

    Adding a language is this record and nothing else — no code — which is the
    point: the floor has to be cheap enough that a contributor supplies data.

    Attributes:
        doc_line: line-comment openers that mean DOC rather than ordinary
            comment (Rust `///`, `//!`). Empty when the language marks docs
            some other way.
        doc_block: block openers that mean DOC (`/**`). Same idea.
        doc_is_structural: the doc is a string in a declaration's body (Python)
            or the run above a declaration (Go) — neither is decidable without
            structure, so this tier reports `comment` and says so.
        quotes: string delimiters, so a marker inside a literal is skipped.
    """

    name: str
    extensions: tuple[str, ...]
    line_comment: tuple[str, ...]
    block_comment: tuple[tuple[str, str], ...] = ()
    doc_line: tuple[str, ...] = ()
    doc_block: tuple[str, ...] = ()
    doc_is_structural: bool = False
    quotes: tuple[str, ...] = ('"', "'")


# ⚠ Ordering inside a field is significant: openers are matched longest-first,
# so `///` must precede `//` or every Rust doc line loses one slash into the
# prose and the marks then run over corrupted text.
LANGUAGES: tuple[Language, ...] = (
    Language("python", (".py", ".pyi"), ("#",), doc_is_structural=True),
    Language(
        "rust",
        (".rs",),
        ("///", "//!", "//"),
        (("/*", "*/"),),
        doc_line=("///", "//!"),
    ),
    Language("go", (".go",), ("//",), (("/*", "*/"),), doc_is_structural=True),
    Language(
        "c-family",
        (".c", ".h", ".cpp", ".hpp", ".cc", ".java", ".cs", ".swift", ".kt"),
        ("//",),
        (("/*", "*/"),),
        doc_block=("/**",),
    ),
    Language(
        "js-family",
        (".js", ".jsx", ".ts", ".tsx", ".mjs"),
        ("//",),
        (("/*", "*/"),),
        doc_block=("/**",),
        quotes=('"', "'", "`"),
    ),
    Language("ruby", (".rb",), ("#",), (("=begin", "=end"),), doc_is_structural=True),
    Language("shell", (".sh", ".bash", ".zsh"), ("#",)),
    Language("sql", (".sql",), ("--",), (("/*", "*/"),)),
    Language("lua", (".lua",), ("--",), (("--[[", "]]"),)),
    Language("toml-ini", (".toml", ".ini", ".cfg"), ("#",)),
    Language("yaml", (".yaml", ".yml"), ("#",)),
)

BY_EXT = {ext: lang for lang in LANGUAGES for ext in lang.extensions}

# The ladder is named by the QUESTION each rung answers, not by the library
# that happens to answer it. Only the top rung knows which declaration a block
# belongs to, which is why locality is the one angle that degrades below it.
TIER_ANSWERS = {
    "tokenized": "blocks, marks, and DOCSTRING owners",
    "lexical": "blocks and marks only",
}


def language_for(path: Path) -> Language | None:
    """The language record for a path, or None when the suffix is unknown."""
    return BY_EXT.get(path.suffix.lower())


def _strip_strings(line: str, quotes: tuple[str, ...]) -> str:
    """Blank out string literals so a marker inside one is not seen as prose.

    This is the LEXICAL tier's one concession to correctness and the reason it
    is usable at all: `url = "http://x"` holds `//` in most C-family languages,
    and a scanner that reported it would drown its own output. It handles
    single-line literals with backslash escapes — not raw strings, heredocs, or
    template nesting, which is exactly where this tier stops and a real lexer
    starts.
    """
    out, quote, esc = [], "", False
    for ch in line:
        if esc:
            out.append(" " if quote else ch)
            esc = False
            continue
        if ch == "\\":
            esc = True
            out.append(" " if quote else ch)
            continue
        if quote:
            out.append(" ")
            if ch == quote:
                quote = ""
            continue
        if ch in quotes:
            quote = ch
            out.append(" ")
            continue
        out.append(ch)
    return "".join(out)


def blocks_lexical(path: Path, text: str, lang: Language) -> list[Block]:
    """Comment runs for a language with no parser here — the FLOOR tier.

    Answers where every block is, its line range, its text and its marks. It
    cannot answer OWNERSHIP, so no block gets an owner and the locality angle
    degrades on this file; the census stamps the tier so a reviewer sees that
    rather than inferring it.
    """
    openers = tuple(sorted(lang.line_comment, key=len, reverse=True))
    lines = text.splitlines()
    out: list[Block] = []
    run: list[tuple[int, str]] = []
    in_block: tuple[str, str] | None = None

    def flush() -> None:
        if not run:
            return
        raw = [t for _, t in run]
        stripped = raw[0].strip()
        is_doc = stripped.startswith(lang.doc_line) if lang.doc_line else False
        if lang.doc_block and stripped.startswith(lang.doc_block):
            is_doc = True
        out.append(
            Block(
                path=path.as_posix(),
                start=run[0][0],
                end=run[-1][0],
                kind="docstring" if is_doc else "comment",
                lines=counted_lines(raw),
                text=_join(raw, openers),
                raw_lines=raw,
                tier="lexical",
            )
        )
        run.clear()

    for n, raw_line in enumerate(lines, 1):
        if in_block is not None:
            run.append((n, raw_line.rstrip()))
            if in_block[1] in raw_line:
                in_block = None
                flush()
            continue
        code = _strip_strings(raw_line, lang.quotes)
        opened = next((p for p in lang.block_comment if p[0] in code), None)
        if opened is not None:
            flush()
            run.append((n, raw_line.rstrip()))
            if opened[1] in code[code.index(opened[0]) + len(opened[0]) :]:
                flush()
            else:
                in_block = opened
            continue
        if code.strip().startswith(openers):
            run.append((n, raw_line.rstrip()))
            continue
        flush()  # ⚠ CODE ends a run; a blank line does not
        at = min((code.index(o) for o in openers if o in code), default=-1)
        if at >= 0:
            run.append((n, raw_line[at:].rstrip()))
            flush()  # a trailing comment is its own block, owned by this line
    flush()
    return out


def blocks_stdlib(path: Path, text: str) -> list[Block]:
    """Comment runs (bounded by CODE) and docstrings, via tokenize + ast."""
    out: list[Block] = []
    # (line, physical source line, the comment token alone, is it trailing)
    run: list[tuple[int, str, str, bool]] = []

    def flush() -> None:
        if run:
            # ⚠ PROSE comes from the comment token; WIDTH from the physical
            # line. Using the physical line for both fed a trailing comment's
            # own code to the mark regexes -- reviewers saw
            # `models.Index(fields=(...)),  # note` as the note's text -- while
            # `--width` legitimately needs the whole line it must not exceed.
            prose = [c for _, _, c, _ in run]
            out.append(
                Block(
                    path=path.as_posix(),
                    start=run[0][0],
                    end=run[-1][0],
                    kind="trailing-comment" if run[0][3] else "comment",
                    lines=counted_lines(prose),
                    text=_join(prose),
                    raw_lines=[ln for _, ln, _, _ in run],
                )
            )
            run.clear()

    for raw in tokenize.generate_tokens(io.StringIO(text).readline):
        if raw.type == tokenize.COMMENT:
            trailing = bool(raw.line[: raw.start[1]].strip())
            run.append((raw.start[0], raw.line.rstrip("\n"), raw.string, trailing))
            # ⚠ A trailing comment CLOSES its run. Its code sits before it, so
            # no later token flushes it, and it silently absorbed the next
            # leading block across two blank lines -- gluing `raise original
            # DoesNotExist` to an unrelated `TODO` four lines down and giving a
            # reviewer one block that was never one comment.
            if trailing:
                flush()
        elif raw.type in (
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.INDENT,
        ) or raw.type in (tokenize.ENDMARKER, tokenize.DEDENT):
            continue
        else:
            flush()
    flush()

    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        out.append(
            Block(
                path=path.as_posix(),
                start=getattr(e, "lineno", 1) or 1,
                end=getattr(e, "lineno", 1) or 1,
                kind="unparsed",
                lines=0,
                text=f"UNPARSED ({e.msg}) — no docstrings censused, no names harvested",
            )
        )
        return out

    for node in ast.walk(tree):
        if not isinstance(node, DOC_OWNERS):
            continue
        doc = ast.get_docstring(node, clean=False)
        if not doc:
            continue
        anchor = node.body[0]
        out.append(
            Block(
                path=path.as_posix(),
                start=anchor.lineno,
                end=getattr(anchor, "end_lineno", anchor.lineno) or anchor.lineno,
                kind="docstring",
                lines=len(doc.splitlines()),
                text=re.sub(r"\s+", " ", doc).strip(),
                owner=getattr(node, "name", "<module>"),
                raw_lines=doc.splitlines(),
            )
        )
    out.extend(_annotated_docs(path, tree))
    return sorted(out, key=lambda b: b.start)


def _annotated_docs(path: Path, tree: ast.AST) -> list[Block]:
    """Prose carried by a PEP 727 `Doc()` inside an `Annotated[...]`.

    ⚠ These are STRING LITERALS, so `ast.get_docstring` cannot see them and the
    tokenizer does not either. On a file that documents its parameters this way
    they are the majority of its prose: measured 5 of 8 blocks on one, which the
    census reported as covered. A block missing from the census is a block
    nobody reviews, so finding them is not optional.
    """
    out: list[Block] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if getattr(fn, "id", getattr(fn, "attr", "")) != "Doc":
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant):
            continue
        val = node.args[0].value
        if not isinstance(val, str):
            continue
        start = node.args[0].lineno
        end = getattr(node.args[0], "end_lineno", start) or start
        out.append(
            Block(
                path=path.as_posix(),
                start=start,
                end=end,
                kind="docstring",
                lines=len(val.splitlines()) or 1,
                text=re.sub(r"\s+", " ", val).strip(),
                raw_lines=val.splitlines() or [val],
            )
        )
    return out


def code_names(roots: list[Path]) -> tuple[set[str], list[str]]:
    """Every name the tree DEFINES, from the AST — never from raw text.

    A corpus built from text contains the comments being checked, so every
    obituary resolves against itself and the check always passes. Unreadable
    files are RETURNED, not dropped: a hole in the corpus turns every symbol
    defined only there into a false obituary, which fails loud-and-wrong.
    """
    names: set[str] = set()
    unread: list[str] = []
    for root in roots:
        for p in _walk(root):
            lang = language_for(p)
            # ⚠ A non-Python file is a KNOWN hole, not a broken file. Parsing it
            # as Python reported `a.go (SyntaxError)`, which reads as "your file
            # is malformed" and sends a reviewer to fix nothing. Liveness for
            # these languages needs its own harvester; until then say which.
            if lang is None or lang.name != "python":
                name = lang.name if lang else "unknown"
                unread.append(f"{p.as_posix()} (no name harvester for {name})")
                continue
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"))
            except PARSE_ERRORS as e:
                unread.append(f"{p.as_posix()} ({type(e).__name__})")
                continue
            names.add(p.stem)
            harvest_constants = not (p.name.startswith("test_") or "tests" in p.parts)
            for node in ast.walk(tree):
                if isinstance(node, NAMED_DEFS):
                    names.add(node.name)
                elif isinstance(node, ast.Name):
                    names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    names.add(node.attr)
                elif isinstance(node, ast.arg):
                    names.add(node.arg)
                elif isinstance(node, ast.alias):
                    names.add((node.asname or node.name).split(".")[0])
                elif harvest_constants and isinstance(node, ast.Constant):
                    if isinstance(node.value, str) and SYMBOLISH.match(node.value):
                        names.add(node.value)
    return names, unread


def _walk(root: Path):
    """Every file under `root` this script has a language record for.

    ⚠ Filters on `BY_EXT`, not on `*.py`. Hardcoding one suffix here made a
    directory scan silently Python-only while `--languages` advertised eleven —
    and silently is the worst part: a file the walk never yields cannot appear
    in the NOT CHECKED list either, so the run reports a clean census of a
    fraction of the tree.
    """
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in BY_EXT:
            if not EXCLUDED_DIRS.intersection(p.parts):
                yield p


def path_index(repo: Path) -> set[str]:
    """Every tracked path, plus every suffix of it, for citation resolution.

    Prose cites package-relative (`summary.py`, `billing/rates.py`) far more
    often than repo-relative, and the review usually runs from a worktree.
    Resolving only against the repo root was measured at 80/84, 18/20 and 2/2
    FALSE dangling reports on one repository — a detector whose output is handed
    to four reviewers as settled fact.

    A suffix set answers "is this citation ANY file in the tree" in one lookup,
    which is the question prose is actually asking. Walking the tree once and
    indexing beats trying N candidate roots per citation.

    ⚠ TRACKED files only, via `git ls-files`. That is faster than walking a tree
    full of generated data, and it is also more correct: a citation into
    gitignored runtime state is UNVERIFIABLE (absent from every fresh checkout),
    which is a different finding from a citation that resolves nowhere. Measured
    on one repo, 6 of 20 "dangling" reports were gitignored state.
    """
    out: set[str] = set()
    if not repo.is_dir():
        return out
    try:
        listed = subprocess.run(
            ["git", "-C", str(repo), "ls-files"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        rels = listed.stdout.splitlines() if listed.returncode == 0 else []
    except GIT_ERRORS:
        rels = []
    if not rels:  # not a git repo, or git unavailable
        rels = [
            p.relative_to(repo).as_posix()
            for p in repo.rglob("*")
            if p.is_file() and not EXCLUDED_DIRS.intersection(p.parts)
        ]
    for rel in rels:
        parts = rel.split("/")
        for i in range(len(parts)):
            out.add("/".join(parts[i:]))
    return out


def mark(block: Block, known: set[str], paths: set[str], repo: Path) -> None:
    """Attach every mark this block carries, and resolve it where possible."""
    t = block.text
    if not t:
        return

    for tok in TICKED.findall(t):
        tok = CALLFORM.sub("", tok)
        if not SYMBOLISH.match(tok) or tok.lower() in NOT_A_SYMBOL:
            continue
        block.marks.add("names-a-symbol")
        # The HEAD segment must resolve, not ANY segment: matching any part lets
        # `Thing.meta` pass on `meta`, the canonical obituary hiding behind a
        # common attribute name.
        if tok not in known and tok.split(".")[0] not in known:
            block.notes.append(f"UNRESOLVED symbol `{tok}` (CANDIDATE)")

    for cited, member in PATH_CITE.findall(t):
        block.marks.add("cites-a-path")
        if cited not in paths and (repo / cited).exists():
            # Present on disk, absent from the index: derived or gitignored.
            # No reviewer in a fresh checkout can read it, so a claim resting on
            # it is UNVERIFIABLE — which is a different verdict from a citation
            # that resolves nowhere, and must not be reported as the same thing.
            block.notes.append(f"UNVERIFIABLE path {cited} (untracked/derived)")
        elif cited not in paths:
            block.notes.append(f"UNRESOLVED path {cited}")
        elif member and member.startswith("test_"):
            block.notes.append(f"cites {cited}::{member} — confirm the test exists")

    if m := COUNTED.search(t):
        block.marks.add("counted")
        block.notes.append(f"RE-COUNT, and name the population: {m.group(0)!r}")
    if m := COVERAGE.search(t):
        block.marks.add("coverage-claim")
        block.notes.append(
            f"CHECK the guard exists AND can fail, exemptions OFF: {m.group(0)!r}"
        )
    if m := FORBIDS.search(t):
        block.marks.add("forbids-a-literal")
        block.notes.append(f"GREP this file for what it forbids: {m.group(0)[:60]!r}")

    if block.kind == "docstring":
        for label, pat in NARRATIVE.items():
            for raw in block.raw_lines:
                if COMMAND_LINE.match(raw):
                    continue
                if pat.search(raw):
                    block.marks.add("narrative-in-docstring")
                    block.notes.append(f"{label}: {raw.strip()[:60]}")
                    break


def tier_for(lang: Language) -> str:
    """The highest rung reachable for this language, here and now.

    One definition, read by the dispatcher and by `--languages`, so what the
    listing advertises cannot drift from what a run actually does.
    """
    return "tokenized" if lang.name == "python" else "lexical"


def census_for(path: Path, text: str, lang: Language) -> list[Block]:
    """The census for one file, at the highest tier available for its language.

    The ladder is by QUESTION ANSWERED, not by library. Python reaches
    TOKENIZED through the stdlib, which buys docstring owners; every other
    language has the LEXICAL floor. Neither resolves a COMMENT's owner.
    """
    if lang.name == "python":
        got = blocks_stdlib(path, text)
    else:
        got = blocks_lexical(path, text, lang)
    for b in got:
        b.tier = tier_for(lang)
    return got


def main() -> int:
    """Build the census, resolve its marks, print both."""
    # A report that dies on an em-dash in someone's docstring is not a tool.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--cap", type=int, default=0, help="max lines for a # run")
    ap.add_argument("--width", type=int, default=0, help="max characters per line")
    ap.add_argument("--repo", default=".", help="repo root for citation resolution")
    ap.add_argument("--census-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--languages",
        action="store_true",
        help="list known languages and the tier each reaches, then exit",
    )
    args = ap.parse_args()

    if args.languages:
        print(f"{'language':<10} {'tier':<11} extensions")
        for lang in LANGUAGES:
            exts = " ".join(lang.extensions)
            print(f"{lang.name:<10} {tier_for(lang):<11} {exts}")
        print("\nA suffix not listed is REPORTED as unreviewable, never skipped.")
        return 0

    repo = Path(args.repo).resolve()
    targets = [Path(p) for p in args.paths]
    files = sorted({f for t in targets for f in _walk(t)})
    known, unread = code_names([repo])
    paths = path_index(repo)

    census: list[Block] = []
    # An argument that matched nothing is the one failure that reads exactly
    # like success: "0 blocks" from a typo and "0 blocks" from a clean file are
    # the same line. Name it, or a whole directory silently goes unreviewed.
    unreadable: list[str] = [
        f"{t.as_posix()} (matched no files)" for t in targets if not any(_walk(t))
    ]
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except READ_ERRORS as e:
            unreadable.append(f"{path.as_posix()} ({type(e).__name__})")
            continue
        lang = language_for(path)
        if lang is None:
            unreadable.append(f"{path.as_posix()} (no language record for its suffix)")
            continue
        try:
            got = census_for(path, text, lang)
        except Exception as e:  # a parse failure is a REPORTED gap, never a skip
            unreadable.append(f"{path.as_posix()} ({type(e).__name__}: {e})")
            continue
        census.extend(got)

    for b in census:
        mark(b, known, paths, repo)

    # repeated-literal needs the whole census, so it is a second pass. A number
    # written twice is a hand-copied value with nothing keeping the copies in
    # step; one written once is just a number.
    seen: Counter[str] = Counter()
    where: dict[str, set[str]] = defaultdict(set)
    for b in census:
        for n in prose_numbers(b.text):
            seen[n] += 1
            where[n].add(f"{b.path}:{b.start}")
    for b in census:
        for n in prose_numbers(b.text):
            if seen[n] > 1 and len(where[n]) > 1:
                b.marks.add("repeated-literal")
                others = sorted(where[n] - {f"{b.path}:{b.start}"})[:3]
                b.notes.append(f"{n} also in prose at {', '.join(others)}")

    if args.json:
        print(
            json.dumps(
                [vars(b) | {"marks": sorted(b.marks)} for b in census],
                indent=1,
                default=str,
            )
        )
        return 0

    # ⚠ A tier is per FILE, not per run: a polyglot repo mixes them in one
    # census. Reporting one global mode let a finding on a file the run could
    # say least about read exactly like one it could settle.
    tiers = Counter(b.tier for b in census)
    langs = Counter(lang.name for f in files if (lang := language_for(f)) is not None)
    over = [
        b for b in census if args.cap and b.kind == "comment" and b.lines > args.cap
    ]
    wide = [b for b in census if args.width and b.widest > args.width]
    longest = max((b.lines for b in census if b.kind == "comment"), default=0)
    widest = max((b.widest for b in census), default=0)

    print(f"comment-review stages 2-3 - {len(files)} files, {len(census)} blocks")
    print(f"  languages: {', '.join(f'{k} {v}' for k, v in sorted(langs.items()))}")
    for name in ("tokenized", "lexical"):
        if tiers.get(name):
            print(f"  tier {name}: {tiers[name]} blocks - {TIER_ANSWERS[name]}")
    print(
        "  ⚠ NO COMMENT carries an owner at either tier, so every locality\n"
        "    verdict rests on a reviewer READING the file. Treat a placement\n"
        "    finding as a CANDIDATE, not a resolution."
    )
    print(f"  longest comment run: {longest} lines; widest line: {widest} chars")
    if args.cap:
        print(f"  over cap ({args.cap}): {len(over)}")
    if args.width:
        print(f"  over width ({args.width}): {len(wide)}")
    print()

    print("CENSUS - every block. A block nobody mentions is a gap in the review.")
    for i, b in enumerate(census, 1):
        marks = ",".join(sorted(b.marks)) or "-"
        own = f"  ({b.owner})" if b.owner else ""
        print(f"{i:4d}  {b.path}:{b.start}-{b.end}  {b.kind}  {b.lines}L  {marks}{own}")
        if not args.census_only:
            for note in b.notes:
                print(f"        -> {note}")
    print()

    if unread or unreadable:
        print("NOT CHECKED — these are gaps, not passes:")
        for u in unread + unreadable:
            print(f"    {u}")
        print(
            "    !! A file missing from the name corpus turns every symbol defined\n"
            "      only there into a false obituary. Treat symbol notes as weaker\n"
            "      until this list is empty."
        )
        print()

    print(
        f"{len(census)} blocks censused. Nothing above is a verdict —\n"
        "`names-a-symbol` and `counted` are CANDIDATES a reviewer confirms;\n"
        "the resolved paths are\n"
        "facts about the filesystem that a reviewer should not re-derive.\n"
        "The whole list is printed: a partial list cannot be used to skip anything."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
