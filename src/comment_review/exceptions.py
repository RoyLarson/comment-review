"""What this package raises, and what it catches reading a file or asking git.

!! A LEAF, LIKE `constants`. It imports nothing from this package, so any module
may take it without acquiring a subject.

`TOML_ERRORS` and `PARSE_ERRORS` are derived from `READ_ERRORS`, not restated:
each is *reading, plus what else can fail once the bytes are in hand*, so each
name says which. Written out separately they drift. `GIT_ERRORS` asks git rather
than reading a file, and lists its members itself.

! WHY A NAME AT ALL, rather than a tuple in the `except` clause: everything under
`plugins/` is copied into other people's repositories and formatted by THEIR
ruff config. A newer `target-version` rewrites `except (A, B):` into PEP 758's
unparenthesised form, which is a `SyntaxError` on the floor interpreter -- and
the author of this repo never sees it. A bound name has nothing to rewrite.
`scripts/check_shipped_syntax.py` is the gate; a `noqa` was tried and does not
hold, because it suppresses the report and not the rewrite.
"""

import subprocess
import tomllib


class Refused(ValueError):
    """A page cannot be set or a binder distributed, and the message says why.

    This is what we raise, rather than a bare `ValueError`, which is a member
    of `PARSE_ERRORS` below. A caller writing `except ValueError` to report our
    refusal would also swallow anything else that went wrong inside, and print
    it as though the model had declined the file on purpose.

    The tuples below say what we catch; this says what we raise. Naming one
    and not the other leaves half the question answered, and it is the half a
    caller cannot work around -- a tuple can be narrowed at the call site, an
    over-broad raise cannot.

    ! A `ValueError` SUBCLASS on purpose: every existing `except ValueError`
    still catches it, so this narrows what a caller CAN say without changing
    what any of them already do.
    """


#: Reading a file's TEXT: it is missing, unreadable, or not valid UTF-8.
#: ! `UnicodeDecodeError` is a `ValueError` and not an `OSError`, so a handler
#: catching only the latter misses a file that exists and cannot be decoded.
READ_ERRORS = (OSError, UnicodeDecodeError)

#: Reading a TOML file AND decoding it. ! The extra member is the whole reason
#: this is its own name: a malformed table is a fact about the CONTENT, and a
#: caller that wanted "could not read it" should not be told the same thing.
TOML_ERRORS = READ_ERRORS + (tomllib.TOMLDecodeError,)

#: Reading a Python file AND parsing it -- both failures, under one name,
#: because a caller that wants a tree cannot use the file either way.
#:
#: On Python 3.11.18 `ast.parse` raises `SyntaxError` on a source string
#: holding a NUL byte -- a file that decoded as valid UTF-8 and passed
#: `READ_ERRORS` cleanly. `code_names` walks a whole repository, so one such
#: file degrades one file's harvest rather than ending the gather. `ValueError`
#: is caught as well; nothing in this tree is known to raise it on a parse path.
#: Every caller treats a parse failure as one file degrading, never as the run
#: ending, which is why the read failures are folded in here too.
PARSE_ERRORS = READ_ERRORS + (SyntaxError, ValueError)

#: Asking GIT for something, and not getting an answer.
#: ! `UnicodeDecodeError` is deliberate: `git()` pins `encoding="utf-8"` with the
#: default `errors="strict"`, so a tracked path or blob outside UTF-8 raises OUT
#: OF `subprocess.run` itself, before any caller sees a return code. Every caller
#: already reads this as *git could not produce this* and degrades to `None`, and
#: a decode failure is the same kind of non-answer -- so it is declared rather
#: than left to crash the first walk over a non-UTF-8 path.
GIT_ERRORS = (OSError, subprocess.SubprocessError, UnicodeDecodeError)
