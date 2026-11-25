"""What counts as a NAME -- the predicate the index matches on.

`code_names` asks it of a string constant in the TREE, to decide whether to
index one.

! **IT IS NOT ASKED OF EVERY INDEX ENTRY.** `code_names` matches it on STRING
CONSTANTS only -- a name harvested from an `ast.arg`, an `ast.alias` or a
declaration never passes through it. Those are Python identifiers and would
pass anyway.
"""

import ast
import re

#: Does this string look like an identifier -- a purely lexical question.
SYMBOLISH = re.compile(r"^[A-Za-z_][\w.]*$")

#: The definitions whose names prose can refer to.
NAMED_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
