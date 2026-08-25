"""The shipped entry point. `python <skill>/scripts/comment-review.py <command>`.

!! THE ONE FILE IN THIS TREE THAT MAY TOUCH `sys.path`, and it is not an
exception to the rule so much as the place the rule stops applying: everything
below it imports by the package's own name -- `from comment_review.x import y`
-- and the package has to be REACHABLE BY THAT NAME before any of it resolves.
Putting its parent on the path is what makes that true, and it can only be done
from outside. Every other shim was a loose script making its neighbours
importable, which is what the move on 2026-08-24 deleted.

! HYPHENATED ON PURPOSE. `comment-review.py` cannot be imported, only run --
so nothing can take it for part of the package, and the package cannot come to
depend on it. The importable name is `comment_review`, beside it.

! IT WORKS IN THE SOURCE TREE TOO. Here its parent is `src/`, which holds
`comment_review/`; shipped, its parent is the skill's `scripts/`, which holds
the copy. The same two lines resolve both, so the file that ships is the file
that was tested.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from comment_review.__main__ import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
