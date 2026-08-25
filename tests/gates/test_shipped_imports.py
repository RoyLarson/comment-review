"""A shipped file imports the standard library and its own neighbours, nothing else.

`plugins/` is COPIED into other people's `.claude/`. There is no install step
and no environment of ours on the far side, so a third-party import is an
`ImportError` in a stranger's checkout -- raised by a file that passed every
gate here.

!! THE RULE WAS KEPT BY THERE BEING NOTHING TO IMPORT, which is not a rule. As
of 2026-08-18 this repo declares no dependencies at all: no `[project]
dependencies`, no dependency group, and `uv.lock` gitignored as *"not a package
and has no dependencies to pin"*. So the shipped tree stayed stdlib-only
because the venv held nothing else. Measured the same day: planting
`import rope` and `from rope.base import project` into `galley.py` passed ruff,
the whole test suite, `check_shipped_syntax.py` and `claude plugin validate`.

!! IT IS A PROMISE TO A CONTRIBUTOR WHO CANNOT KNOW IT. Adding a dev tool --
a refactorer, a profiler, a type checker -- is an ordinary thing to do, and
nothing about doing it says the ten files under `plugins/` may not use what was
just installed. The person who breaks this will be someone reasonable with a
green local gate. That is the case this file exists for, and it is why the
check lives in the suite rather than in a release script: it fails on the
commit that introduces it, not on the release that ships it.

! That case is MEASURED, not assumed. With `rope` installed and `import rope`
planted in `galley.py`, all 509 tests ran -- no collection error, nothing else
noticed -- and the single failure was this one, naming the file, the module and
the consequence. Uninstalled, the same plant also breaks the galley tests with
an `ImportError`, which is the accident happening to be loud; the contributor's
machine is the quiet case.

! With this here, adding a development dependency is a safe decision instead of
a careful one.
"""

import ast
import sys
import unittest

from _paths import ROOT

# ! No `_paths` import. Every other test module takes it to put the shipped
# scripts on `sys.path`; this one READS them and imports none, so taking it
# would be a shim for nothing.
ROOT = ROOT
# !! THE SOURCE, NOT THE BUILT COPY. `plugins/` holds whatever the last build
# put there, so a gate reading it answers "was the build run" rather than "is
# the code clean" -- and it reads as PASSING on a tree the build has not
# touched, because zero files import nothing foreign. That the build's output
# MATCHES this source is a separate question with its own gate.
SHIPPED = ROOT / "src" / "comment_review"


def shipped_files():
    """Every .py that ships, wherever it sits in the package.

    ! RGLOB, not a glob of the one directory that holds them today. The sibling
    gate `test_shipped_cli_encoding.py` records what a narrow glob costs: it
    globbed a single directory, and files the docstring claimed were covered sat
    outside it for a release. ! Since 2026-08-24 the files sit in SEVEN
    directories rather than one, so the rglob is now load-bearing rather than
    merely prudent.
    """
    return sorted(SHIPPED.rglob("*.py"))


def foreign_imports(source, siblings):
    """Every import in `source` that is neither stdlib nor a named sibling.

    ! The HEAD segment decides it: `os.path` is `os`, and a shipped module is
    imported by its bare stem because each script puts its own directory on
    `sys.path` before importing its neighbours.

    Args:
        source: the file's text.
        siblings: module names importable beside it.

    Returns:
        `(module, line)` per foreign import, in source order.
    """
    out = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names = [(alias.name, node.lineno) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            # ! A relative import cannot leave the directory, so it needs no
            # check -- and `node.module` is None for `from . import x`, which
            # would otherwise read as a foreign module named "".
            if node.level:
                continue
            names = [(node.module or "", node.lineno)]
        else:
            continue
        for name, line in names:
            head = name.split(".")[0]
            if head and head not in sys.stdlib_module_names and head not in siblings:
                out.append((head, line))
    return sorted(out, key=lambda pair: pair[1])


class TestEveryShippedFileImportsOnlyWhatTravelsWithIt(unittest.TestCase):
    def test_there_are_files_to_check(self):
        # A glob that matched nothing would make every test below vacuous.
        self.assertGreaterEqual(len(shipped_files()), 10)

    def test_no_shipped_file_imports_a_third_party_module(self):
        for path in shipped_files():
            # ! Siblings are PER DIRECTORY. A file elsewhere under `plugins/`
            # could not import these by bare name, so the allowed set is the
            # stems beside it and not every stem that ships.
            siblings = {p.stem for p in path.parent.glob("*.py")}
            found = foreign_imports(path.read_text(encoding="utf-8"), siblings)
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertEqual(
                    found,
                    [],
                    f"{path.name} imports {[m for m, _ in found]}, which will not"
                    " be installed where this file is copied",
                )


class TestTheCheckItselfFires(unittest.TestCase):
    """A check that has never fired proves nothing.

    ! Every case below was run against the real detector before the rule it
    tests was believed. The suite already has one instance of the opposite --
    a guard whose own fixture hand-wrote a shape the tool never produces, so it
    passed while the shipped path deleted a statement.
    """

    SIBLINGS = {"repo", "census"}

    def _found(self, source):
        return [module for module, _ in foreign_imports(source, self.SIBLINGS)]

    def test_a_plain_third_party_import_is_reported(self):
        self.assertEqual(self._found("import rope"), ["rope"])

    def test_a_from_import_is_reported_by_its_head(self):
        self.assertEqual(self._found("from rope.base import project"), ["rope"])

    def test_a_dotted_import_is_reported_by_its_head(self):
        self.assertEqual(self._found("import rope.refactor.rename"), ["rope"])

    def test_an_import_inside_a_function_is_reported(self):
        # ! `ast.walk`, not the module body -- a local import defers the
        # ImportError to the call rather than preventing it.
        self.assertEqual(self._found("def f():\n    import rope\n"), ["rope"])

    def test_the_line_is_named(self):
        self.assertEqual(
            foreign_imports("import os\nimport rope\n", self.SIBLINGS), [("rope", 2)]
        )

    def test_the_standard_library_is_allowed(self):
        self.assertEqual(self._found("import json\nfrom pathlib import Path\n"), [])

    def test_a_future_import_is_allowed(self):
        self.assertEqual(self._found("from __future__ import annotations"), [])

    def test_a_sibling_is_allowed(self):
        self.assertEqual(self._found("from repo import READ_ERRORS\nimport census"), [])

    def test_a_relative_import_is_not_reported(self):
        # ! It cannot reach outside the directory, so there is nothing to check.
        self.assertEqual(self._found("from . import census\nfrom .repo import git"), [])

    def test_a_module_named_like_a_sibling_elsewhere_is_still_reported(self):
        # !! The allowed set is the stems BESIDE the file. A third-party
        # package sharing a shipped module's name would otherwise be admitted
        # by coincidence.
        self.assertEqual(
            foreign_imports("import galley", self.SIBLINGS), [("galley", 1)]
        )
