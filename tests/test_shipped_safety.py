"""Nothing in this repo deserialises agent output through a code-executing format.

!! THIS TOOL READS FILES THAT AGENTS WROTE. A reviewer's report, a run context,
a census, an edits map -- every one of them is produced by a model and read back
by a script that ships into other people's `.claude/` directories. That makes
unsafe deserialisation categorically worse here than in an ordinary program: the
untrusted input is not an edge case, it is the normal path.

`pickle` is the trap this gate exists for. It is stdlib, it round-trips anything
including the multi-line source blocks a record carries, and it is the obvious
answer for someone optimising away an escaping problem. Loading it from agent
output puts arbitrary code execution inside a review tool. `marshal`, `shelve`
and `dill` are that hazard wearing other names.

! TWO OTHER SHAPES, and they are not the same one. Stdlib **XML** does not
execute code -- it EXPANDS ENTITIES, so untrusted input is a denial of service
rather than a takeover. And `yaml.load` without a safe loader runs constructors,
though YAML is not a dependency here and fails the stdlib rule anyway. The
reasons are kept apart in `BANNED_IMPORTS` because one message would be wrong
for XML.

! Raised 2026-08-17 while ruling the record's format to JSON. Roy, on the
observation that pickle would be a remote-code-execution hole: *"but don't you
want to fail hard on a security review"*. A rule enforced by nothing is a rule
that rots, which is this repo's own standard applied to itself.
"""

import ast
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Modules that are unsafe to point at input this repo did not write, and WHY --
# because the reasons differ and a shared message would be wrong for one of them.
BANNED_IMPORTS = {
    "pickle": "executes arbitrary code on load",
    "cPickle": "executes arbitrary code on load",
    "dill": "executes arbitrary code on load",
    "marshal": "executes what it loads, and its format is version-unstable",
    "shelve": "is `pickle` behind a dict",
    # ! A DIFFERENT hazard and a lesser one: stdlib XML does not execute code,
    # it EXPANDS ENTITIES. Measured 2026-08-17 on the pinned 3.11 -- three
    # levels of nested internal entity became 1000 characters, and the
    # unbounded form of that shape is a denial of service. `defusedxml` is the
    # answer where XML is unavoidable, and it is third party, so here the
    # answer is that XML is avoidable: the record format is JSON.
    "xml": "expands entities, so untrusted input is a denial of service",
}
# `eval`/`exec` on anything a model produced is the same hole without a module.
BANNED_CALLS = frozenset({"eval", "exec"})
# PyYAML's `load` runs constructors unless a safe loader is passed. It is not a
# dependency here and must not become one, but the pattern is named so the gate
# still refuses it if it ever arrives.
UNSAFE_YAML = re.compile(r"\byaml\.load\s*\(")


def scanned_files():
    """Every tracked `.py` this repo authors, tests included.

    ! Tests are IN scope. A gate that exempts them invites the fixture that
    pickles something "just for the test" and the helper that grows a caller.
    """
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*.py"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.split()
    return [
        ROOT / f
        for f in out
        # ! Corpora are other people's code and a captured run is a record of
        # what happened; neither is authored here.
        if not f.startswith("corpora/")
        and not (f.startswith("evidence/") and "-full-" in f)
    ]


def banned_imports_in(source: str) -> set[str]:
    """Which banned modules this source imports. Shared by the gate and its test.

    ! Extracted so the gate can be shown to FAIL. A check nobody has watched
    refuse something is a check nobody knows works, and all three parser
    defects this month passed tests that asserted only that SOMETHING was
    refused.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    return found & set(BANNED_IMPORTS)


class TestTheGateCanFail(unittest.TestCase):
    """It refuses a violation, and names the right reason for it."""

    def test_pickle_is_caught(self):
        self.assertEqual(banned_imports_in("import pickle"), {"pickle"})

    def test_a_from_import_is_caught(self):
        self.assertEqual(banned_imports_in("from pickle import loads"), {"pickle"})

    def test_a_submodule_import_is_caught(self):
        # ! `xml.etree.ElementTree` must be caught by its ROOT package.
        self.assertEqual(
            banned_imports_in("import xml.etree.ElementTree as ET"), {"xml"}
        )

    def test_json_is_not_caught(self):
        self.assertEqual(banned_imports_in("import json"), set())

    def test_xml_and_pickle_give_DIFFERENT_reasons(self):
        # !! The reasons are not interchangeable: one executes code, the other
        # expands entities. A shared message would be wrong for XML.
        self.assertNotEqual(BANNED_IMPORTS["xml"], BANNED_IMPORTS["pickle"])
        self.assertIn("entities", BANNED_IMPORTS["xml"])
        self.assertIn("arbitrary code", BANNED_IMPORTS["pickle"])


class TestNothingDeserialisesUnsafely(unittest.TestCase):
    def test_there_are_files_to_scan(self):
        # A glob that matched nothing would make every test below vacuous.
        self.assertGreater(len(scanned_files()), 20)

    def test_no_code_executing_deserialiser_is_imported(self):
        for path in scanned_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module.split(".")[0]]
                for name in names:
                    with self.subTest(file=path.name, module=name):
                        self.assertNotIn(
                            name,
                            BANNED_IMPORTS,
                            f"{path.relative_to(ROOT).as_posix()} imports `{name}`,"
                            f" which {BANNED_IMPORTS.get(name, '')}. This repo"
                            " reads files that AGENTS wrote; use `json`.",
                        )

    def test_nothing_calls_eval_or_exec(self):
        for path in scanned_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                fn = node.func
                name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", "")
                with self.subTest(file=path.name, line=node.lineno):
                    self.assertNotIn(
                        name,
                        BANNED_CALLS,
                        f"{path.relative_to(ROOT).as_posix()}:{node.lineno} calls"
                        f" `{name}`, which runs what it is given.",
                    )

    def test_no_unsafe_yaml_load(self):
        for path in scanned_files():
            with self.subTest(file=path.name):
                self.assertIsNone(
                    UNSAFE_YAML.search(path.read_text(encoding="utf-8")),
                    f"{path.relative_to(ROOT).as_posix()} calls `yaml.load`, which"
                    " runs constructors without a safe loader. YAML is also not"
                    " stdlib, so it fails the shipped-code rule twice over.",
                )


# !! LAST LINE, ALWAYS. A runner placed above a class runs before that class
# exists, so `python tests/<file>.py` reports a green bar over a shorter suite
# than `unittest discover`.
if __name__ == "__main__":
    unittest.main()
