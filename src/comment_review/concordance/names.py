"""What counts as a NAME -- the predicate the key and the index both match on.

!! IT IS A CONTRACT BETWEEN TWO SIDES OF ONE LOOKUP, which is why it belongs
to neither of them. `annotate` asks it of a backticked token from PROSE, to
decide whether that token is a name worth looking up; `code_names` asks it of
a string constant in the TREE, to decide whether to index one. **If the two
disagreed about what a name looks like, a key could never hit.**

!! IT LIVED IN `reading/lexer.py` UNTIL 2026-08-31, AND THE COMMENT THERE SAID
WHY -- *"a leaf both may take is what stops one of them importing the other
for a regex."* ! **Right about the need and wrong about the destination**: the
lexer is the BUILDER, 1,600 lines of tokenising, and it had NO READER of this
at all -- measured 2026-08-31, the only occurrence was its own definition
line. It is the same misplacement `Paragraph` was in, made for the same
reason on the same module. `decision-log.md Process: #70`.

! **THE MOVE HAD TO WAIT FOR ITS TWO READERS TO BE ONE AREA.** They were
`binder/annotate.py` and `concordance/code_names.py`; annotate came here the
same day, because it builds the key for the index this package builds.

! **IT IS NOT ASKED OF EVERY INDEX ENTRY**, and nothing said so before.
`code_names` matches it on STRING CONSTANTS only -- a name harvested from an
`ast.arg`, an `ast.alias` or a declaration never passes through it. Those are
Python identifiers and would pass anyway, so this is not a live defect; it is
a rule that governs every KEY and one branch of the INDEX.
"""

import re

#: Does this string look like an identifier -- a purely lexical question.
SYMBOLISH = re.compile(r"^[A-Za-z_][\w.]*$")
