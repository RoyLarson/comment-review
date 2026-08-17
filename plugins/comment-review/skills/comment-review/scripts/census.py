"""Stage 2: every comment run and every docstring, located as a numbered block.

    python census.py [--repo D] [--census-only] [--json] [--out PATH] <paths>

The reviewers are handed this list, so it is the whole population they rule on.
**Every file handed in is censused, or this errors** -- a file it could not read
or parse, or whose suffix has no language record, is named and the run exits
nonzero, because a block missing from the census is a block nobody reviews.

Read-only. It calls `annotate.py` on each block for stage 3, and `repo.py` for
the facts about the checkout that both need.

A block is built at the TIER available for its file's language. Both tiers find
the same blocks, and the tier says what else the file can answer:

  tokenized  a lexer + AST (Python, from the stdlib)   + DOCSTRING anchors
  lexical    a comment-syntax record                   blocks

⚠ Only a STRUCTURAL doc carries an anchor, and only Python has one: the doc is a
string inside a declaration's body, so the AST names the declaration. A MARKED
doc (`///`, `/**`) is a comment run like any other. Every other anchor comes from
a reviewer READING the file, so a placement finding is a CANDIDATE in every
language.

⚠ Tier counts are AGGREGATED over the run. A polyglot run reports one total per
tier, so read the per-file tier stamp to see which file reached which.
`--languages` lists the languages known and the tier each reaches.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import sys
import tokenize
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from annotate import (  # noqa: E402  -- path shim must run first
    SYMBOLISH,
    annotate,
    prose_numbers,
)
from repo import (  # noqa: E402  -- path shim must run first
    EXCLUDED_DIRS,
    PARSE_ERRORS,
    READ_ERRORS,
    path_index,
    tracked_paths,
)

# Tuples, so `DOC_ANCHORS` is built by concatenation and both go straight to
# `isinstance`.
NAMED_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
DOC_ANCHORS = (ast.Module,) + NAMED_DEFS


# The work markers `counted_lines` leaves free of the cap.
MARKERS = ("TODO", "FIXME", "HACK", "XXX", "BUG")
WORK_MARKER = re.compile(r"^(" + "|".join(MARKERS) + r")\b")
# ⚠ Every punctuation a language opens a comment with, stripped before the
# marker is matched. Anchored on `#`, the exemption was Python-only: a
# `// TODO:` was charged to the cap in a script that censuses eleven languages.
LEAD_PUNCT = re.compile(r"^[\s#/*\-!=;%<>]+")


def counted_lines(raw: list[str]) -> int:
    """Lines a cap charges for: a marker LINE itself is free.

    A marker points at filed work; the explanation is the rest of the block, and
    the cap measures the explanation. Charge the marker and the quickest route to
    green is deleting the pointer -- which is quick to do and expensive to have
    done: the work is still needed, and nothing names it any more.

    The exemption is one line wide. A run stays one run across a marker, and a
    marker's continuation lines are charged: six lines plus a `TODO:` is six.
    """
    return sum(1 for ln in raw if not WORK_MARKER.match(LEAD_PUNCT.sub("", ln)))


# ── Annotations ───────────────────────────────────────────────────────────────
# Each is located here and RESOLVED in `annotate.py`. Locating is most of the
# work; the resolution is what stops a reviewer treating a citation as a
# verified claim. ⚠ These are ANNOTATIONS, never marks -- a MARK is editorial,
# and stage 4 emits those.


@dataclass
class Block:
    """The interval between two lines of code — the unit a reviewer rules on."""

    path: str
    start: int
    end: int
    kind: str  # "comment" | "docstring"
    lines: int
    text: str  # the run JOINED, so a wrapped claim matches as one string
    anchor: str = ""  # the declaration it annotates, when structurally known
    tier: str = "lexical"  # which question set this file's census can answer
    annotations: set[str] = field(default_factory=set)
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
    """What the LEXICAL tier needs to find prose in a language it only lexes.

    Adding a language is this record — data, no code.

    Attributes:
        doc_line: line-comment openers that mean DOC rather than ordinary
            comment (Rust `///`, `//!`). Empty when the language marks docs
            some other way.
        doc_block: block openers that mean DOC (`/**`). Same idea.
        doc_is_structural: the doc is a string in a declaration's body (Python)
            or the run above a declaration (Go). Both need structure to decide,
            so this tier reports `comment` and annotates the block.
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
# prose and the annotations then run over corrupted text.
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
# belongs to.
TIER_ANSWERS = {
    "tokenized": "blocks, annotations, and DOCSTRING anchors",
    "lexical": "blocks and annotations only",
}


def language_for(path: Path) -> Language | None:
    """The language record for a path, or None when the suffix is unknown."""
    return BY_EXT.get(path.suffix.lower())


def _strip_strings(line: str, quotes: tuple[str, ...]) -> str:
    """Blank out string literals so a marker inside one stays out of the census.

    `url = "http://x"` holds `//` in most C-family languages. It handles
    single-line literals with backslash escapes; raw strings, heredocs and
    template nesting are where this tier stops and the lexer starts.
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

    Answers where every block is, its line range, its text and its annotations.
    Every block comes back stamped `tier="lexical"` with an empty anchor.

    ⚠ A block opener with no closer swallows every remaining line into one run,
    so code below it is censused as prose. That block is STAMPED
    `unterminated-block-comment`, which is how a consumer tells it from a long
    comment; `prove_unchanged.py` refuses the whole file on that annotation.
    """
    openers = tuple(sorted(lang.line_comment, key=len, reverse=True))
    lines = text.splitlines()
    out: list[Block] = []
    run: list[tuple[int, str]] = []
    in_block: tuple[str, str] | None = None

    def flush(trailing: bool = False) -> None:
        if not run:
            return
        raw = [t for _, t in run]
        stripped = raw[0].strip()
        is_doc = stripped.startswith(lang.doc_line) if lang.doc_line else False
        if lang.doc_block and stripped.startswith(lang.doc_block):
            is_doc = True
        if is_doc:
            kind = "docstring"
        else:
            kind = "trailing-comment" if trailing else "comment"
        out.append(
            Block(
                path=path.as_posix(),
                start=run[0][0],
                end=run[-1][0],
                kind=kind,
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
        flush()  # ⚠ CODE ends a block; a blank line does not
        at = min((code.index(o) for o in openers if o in code), default=-1)
        if at >= 0:
            run.append((n, raw_line[at:].rstrip()))
            flush(trailing=True)  # its own block, anchored to the code on that line
    flush()
    if in_block is not None and out:
        # The loop ended with a block comment still open, so the final flush
        # emitted the run that ate the rest of the file. It is the ONE block
        # that may hold code.
        out[-1].annotations.add("unterminated-block-comment")
        out[-1].notes.append(
            f"UNTERMINATED {in_block[0]}: no closing {in_block[1]} before end of "
            "file, so every line below the opener was swallowed into this run. "
            "Code down there was NOT censused as code."
        )
    return out


def flag_structural_docs(blocks: list[Block], text: str, lang: Language) -> None:
    """Mark each run whose KIND is still an open question at this tier.

    Go and Ruby attach documentation by POSITION -- an ordinary line comment
    directly above a declaration IS that declaration's documentation -- so a
    doc reads like any other run, and telling them apart needs the structure
    this tier lacks.

    The block is annotated as an OPEN QUESTION instead. That matters because
    `compact.md` routes on KIND: a `comment` is governed by LENGTH and may be
    cut to the cap, a `docstring` by FORMAT and stands. Unmarked, a three-line
    Go export doc reads as over a cap of two and is cut by a rule that governs
    comments.

    Args:
        blocks: this file's blocks, mutated in place.
        text: the file's source, for looking at what follows each run.
        lang: the language record, which decides whether this pass applies.
    """
    if not lang.doc_is_structural:
        return
    lines = text.splitlines()
    for block in blocks:
        # Only a leading `comment` run can be a positional doc: a trailing
        # comment annotates the code on its own line.
        if block.kind != "comment":
            continue
        # ⚠ The IMMEDIATELY next line. Both languages require a doc comment to
        # touch its declaration, so a run held off by a blank line is an ORPHAN
        # -- left unmarked here, and charged to the cap.
        nxt = lines[block.end].strip() if block.end < len(lines) else ""
        if not nxt:
            continue
        block.annotations.add("doc-kind-unresolved")
        block.notes.append(
            "KIND UNRESOLVED: this run sits above code and "
            f"{lang.name} attaches docs by position, so it may be documentation "
            "governed by FORMAT rather than a comment governed by LENGTH. "
            "NOT counted against the cap. Confirm the kind before compacting."
        )


def blocks_stdlib(path: Path, text: str) -> list[Block]:
    """Comment blocks (bounded by CODE) and docstrings, via tokenize + ast."""
    out: list[Block] = []
    # (line, physical source line, the comment token alone, is it trailing)
    run: list[tuple[int, str, str, bool]] = []

    def flush() -> None:
        if run:
            # ⚠ PROSE comes from the comment token; WIDTH from the physical
            # line, which is the whole line a width rule measures. Using the
            # physical line for both fed a trailing comment's own code to the
            # annotation regexes -- reviewers saw
            # `models.Index(fields=(...)),  # note` as the note's text.
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
            # the next token to arrive is the following leading comment, and the
            # two merged across two blank lines -- gluing `raise original
            # DoesNotExist` to an unrelated `TODO` four lines down and handing a
            # reviewer one block built from two comments.
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
        if not isinstance(node, DOC_ANCHORS):
            continue
        doc = ast.get_docstring(node, clean=False)
        if not doc:
            continue
        stmt = node.body[0]
        out.append(
            Block(
                path=path.as_posix(),
                start=stmt.lineno,
                end=getattr(stmt, "end_lineno", stmt.lineno) or stmt.lineno,
                kind="docstring",
                lines=len(doc.splitlines()),
                text=re.sub(r"\s+", " ", doc).strip(),
                anchor=getattr(node, "name", "<module>"),
                raw_lines=doc.splitlines(),
            )
        )
    out.extend(_annotated_docs(path, tree))
    return sorted(out, key=lambda b: b.start)


def _annotated_docs(path: Path, tree: ast.AST) -> list[Block]:
    """Prose carried by a PEP 727 `Doc()` inside an `Annotated[...]`.

    ⚠ These are STRING LITERALS, so `ast.get_docstring` passes over them and so
    does the tokenizer. On a file that documents its parameters this way they
    are most of its prose.
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


def _walk(root: Path):
    """Every file under `root` this script has a language record for.

    ⚠ Filters on `BY_EXT`, so every language `--languages` advertises is walked.
    Hardcoded to `*.py`, the scan went Python-only, and a file the walk skips is
    absent from the NOT CHECKED list too — the run then reports a full census of
    a fraction of the tree.
    """
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in BY_EXT:
            if not EXCLUDED_DIRS.intersection(p.parts):
                yield p


def code_names(
    roots: list[Path], tracked: set[Path] | None = None
) -> tuple[set[str], list[str]]:
    """Every name the tree DEFINES, harvested from the AST.

    A corpus built from raw text contains the comments being checked, so every
    obituary resolves against itself and the check always passes. Unreadable
    files are RETURNED alongside the names: a hole in the corpus turns every
    symbol defined only there into a false obituary, which fails loud and wrong.

    ⚠ TRACKED files only, when git can say which. A vendored, generated or
    gitignored tree under the repo root otherwise donates its whole namespace,
    so a symbol the repo defines nowhere resolves ALIVE. That failure is SILENT
    and one-sided: it can hide an obituary, and manufactures none.

    Args:
        roots: directories or files to harvest.
        tracked: absolute paths git reports as tracked, or None when git could
            not answer — in which case the whole tree is walked and the caller
            is told, so a change in coverage arrives with the result.

    Returns:
        The set of defined names, and the list of files that could not be read.
    """
    names: set[str] = set()
    unread: list[str] = []
    if tracked is None:
        unread.append(
            "name corpus built by WALKING the tree (not a git checkout, or git "
            "unavailable) — untracked or vendored code may mask an obituary"
        )
    for root in roots:
        for p in _walk(root):
            if tracked is not None and p.resolve() not in tracked:
                continue
            lang = language_for(p)
            # ⚠ A non-Python file is a KNOWN hole, reported as one. Parsed as
            # Python it came back `a.go (SyntaxError)`, which reads as "your
            # file is malformed" and sends a reviewer after an invented defect.
            # Liveness in these languages needs its own harvester; this names
            # the gap until there is one.
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


def tier_for(lang: Language) -> str:
    """The highest rung reachable for this language, here and now.

    One definition, read by the dispatcher and by `--languages`, so the listing
    and the run report the same tier.
    """
    return "tokenized" if lang.name == "python" else "lexical"


def census_for(path: Path, text: str, lang: Language) -> list[Block]:
    """The census for one file, at the highest tier available for its language.

    The ladder is by QUESTION ANSWERED. Python reaches TOKENIZED through the
    stdlib, which buys docstring anchors; every other language has the LEXICAL
    floor.
    """
    if lang.name == "python":
        got = blocks_stdlib(path, text)
    else:
        got = blocks_lexical(path, text, lang)
        flag_structural_docs(got, text, lang)
    for b in got:
        b.tier = tier_for(lang)
    return got


def main() -> int:
    """Build the census, resolve its annotations, print both."""
    # UTF-8 with replacement, so an em-dash in someone's docstring still prints
    # on a console whose encoding lacks it.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--repo", default=".", help="repo root for citation resolution")
    ap.add_argument("--census-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--out", metavar="PATH", help="write the report to PATH, not stdout"
    )
    ap.add_argument(
        "--languages",
        action="store_true",
        help="list known languages and the tier each reaches, then exit",
    )
    args = ap.parse_args()

    # ⚠ WRITES ITS OWN FILE. A shell redirect is refused outright by a
    # worktree-isolated harness -- "too complex to verify that it stays inside
    # the worktree" -- and the JSON census is what the stage-5 join parses, so
    # the only documented route to it was unrunnable there.
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="") as fh:
            with redirect_stdout(fh):
                return _report(args)
    return _report(args)


def _report(args: argparse.Namespace) -> int:
    """Everything the run prints, so `--out` can wrap it in one place."""
    if args.languages:
        print(f"{'language':<10} {'tier':<11} extensions")
        for lang in LANGUAGES:
            exts = " ".join(lang.extensions)
            print(f"{lang.name:<10} {tier_for(lang):<11} {exts}")
        print("\nA suffix not listed is named, and the census exits nonzero.")
        return 0

    repo = Path(args.repo).resolve()
    targets = [Path(p) for p in args.paths]
    files = sorted({f for t in targets for f in _walk(t)})
    known, unread = code_names([repo], tracked_paths(repo))
    paths = path_index(repo)

    census: list[Block] = []
    # A path argument that matched no file joins `unreadable`, so a typo errors
    # on the same rule every other gap does.
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
        except Exception as e:  # a parse failure is REPORTED, as a gap
            unreadable.append(f"{path.as_posix()} ({type(e).__name__}: {e})")
            continue
        census.extend(got)

    for b in census:
        annotate(b, known, paths, repo)

    # repeated-literal needs the whole census, so it is a second pass. A number
    # written twice is a hand-copied value, and the copies drift; one written
    # once is just a number.
    seen: Counter[str] = Counter()
    where: dict[str, set[str]] = defaultdict(set)
    for b in census:
        for n in prose_numbers(b.text):
            seen[n] += 1
            where[n].add(f"{b.path}:{b.start}")
    for b in census:
        for n in prose_numbers(b.text):
            if seen[n] > 1 and len(where[n]) > 1:
                b.annotations.add("repeated-literal")
                others = sorted(where[n] - {f"{b.path}:{b.start}"})[:3]
                b.notes.append(f"{n} also in prose at {', '.join(others)}")

    if args.json:
        print(
            json.dumps(
                [vars(b) | {"annotations": sorted(b.annotations)} for b in census],
                indent=1,
                default=str,
            )
        )
        return 0

    # ⚠ A tier is per FILE: a polyglot repo mixes them in one census. Reported
    # as one global mode, a finding from the lexical floor read like one from
    # the tokenized tier.
    tiers = Counter(b.tier for b in census)
    langs = Counter(lang.name for f in files if (lang := language_for(f)) is not None)
    deferred = [b for b in census if "doc-kind-unresolved" in b.annotations]

    print(f"comment-review stages 2-3 - {len(files)} files, {len(census)} blocks")
    print(f"  languages: {', '.join(f'{k} {v}' for k, v in sorted(langs.items()))}")
    for name in ("tokenized", "lexical"):
        if tiers.get(name):
            print(f"  tier {name}: {tiers[name]} blocks - {TIER_ANSWERS[name]}")
    print(
        "  ⚠ NO COMMENT carries an anchor at either tier. A comment's anchor\n"
        "    comes from READING the file, so a placement finding is a CANDIDATE."
    )
    if deferred:
        print(
            f"  kind unresolved: {len(deferred)} — a positional doc comment."
            " Confirm the kind before compacting; a cap governs one and not"
            " the other"
        )
    print()

    print("CENSUS - every block, numbered.")
    for i, b in enumerate(census, 1):
        notes = ",".join(sorted(b.annotations)) or "-"
        anchor = f"  ({b.anchor})" if b.anchor else ""
        loc = f"{b.path}:{b.start}-{b.end}"
        print(f"{i:4d}  {loc}  {b.kind}  {b.lines}L  {notes}{anchor}")
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
        f"{len(census)} blocks censused. `names-a-symbol` and `counted` are\n"
        "CANDIDATES a reviewer confirms; a resolved path is a fact about the\n"
        "filesystem, already settled. The whole list is printed every run."
    )
    # The reviewers are handed the CENSUS, so a file missing from it is blocks
    # nobody reviews and there is nothing downstream that notices. Exit on it.
    if unreadable:
        print(
            f"\nERROR: {len(unreadable)} of {len(files)} files handed in were not"
            " censused. Every file is censused or this errors."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
