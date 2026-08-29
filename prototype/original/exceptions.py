"""What can go wrong getting at a file, each named for the question it answers.

!! A LEAF, LIKE `constants`. It imports nothing from this package, so any module
may take it without acquiring a subject.

!! ONE NAME MEANT TWO THINGS. `READ_ERRORS` was defined in four shipped modules
and five development scripts, and TWO of those definitions were a different
tuple: they added `tomllib.TOMLDecodeError`. A file that will not DECODE is not a
file that will not READ -- so a caller catching "read errors" was catching a
parse failure in two places and not in the other seven, under one name.

! THAT IS THE BUG THIS PREVENTS, and it is silent in both directions. Catching
too much turns a malformed TOML into "could not read your file"; catching too
little lets a decode failure escape a handler whose name says it is covered.

!! THE TUPLES ARE DERIVED, NOT RESTATED. Every question here is *reading, plus
what else can fail once the bytes are in hand*, so each name says which. Written
out separately they drift: that is exactly what happened to `READ_ERRORS`.

! WHY A NAME AT ALL, rather than a tuple in the `except` clause: everything under
`plugins/` is copied into other people's repositories and formatted by THEIR
ruff config. A newer `target-version` rewrites `except (A, B):` into PEP 758's
unparenthesised form, which is a `SyntaxError` on the floor interpreter -- and
the author of this repo never sees it. A bound name has nothing to rewrite.
`scripts/check_shipped_syntax.py` is the gate; a `noqa` was tried and does not
hold, because it suppresses the report and not the rewrite.
"""

import subprocess
import tokenize
import tomllib


class Refused(ValueError):
    """This page cannot be built or set, and the message says why.

    !! IT IS WHAT WE RAISE, and until 2026-08-22 that was a bare `ValueError` --
    the same class `ast.parse` raises on a source string holding a NUL byte, and
    a member of `PARSE_ERRORS` below. So a caller writing `except ValueError` to
    report OUR refusal also swallowed anything else that went wrong inside, and
    printed it as though the model had declined the file on purpose.

    ! THE TUPLES ABOVE SAY WHAT WE CATCH; THIS SAYS WHAT WE RAISE. Naming one
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

#: Turning Python SOURCE ALREADY IN HAND into tokens.
#: !! `tokenize.TokenError` IS NOT A `SyntaxError`, which is the whole reason
#: both are named: `ast.parse` raises the second and `generate_tokens` raises the
#: first, so a handler written for one never saw the other.
TOKENIZE_ERRORS = (tokenize.TokenError, SyntaxError)

#: Reading a Python file AND parsing it -- both failures, under one name,
#: because a caller that wants a tree cannot use the file either way.
#:
#: ! `ValueError` IS THE ONE NOBODY EXPECTS: `ast.parse` raises it, not
#: `SyntaxError`, on a source string holding a NUL byte -- a file that decoded
#: as valid UTF-8 and passed `READ_ERRORS` cleanly. `code_names` walks a whole
#: repository, so one such file aborted the entire census rather than degrading
#: one file's harvest.
#: ! And `TokenError` arrives through `TOKENIZE_ERRORS` above: an unterminated
#: triple-quote or bracket anywhere in a corpus ended a run with a traceback.
#: ! Every caller treats a parse failure as ONE FILE DEGRADING, never as the run
#: ending, which is why the read failures are folded in here too.
PARSE_ERRORS = READ_ERRORS + TOKENIZE_ERRORS + (ValueError,)

#: Asking GIT for something, and not getting an answer.
#: ! `UnicodeDecodeError` is deliberate: `git()` pins `encoding="utf-8"` with the
#: default `errors="strict"`, so a tracked path or blob outside UTF-8 raises OUT
#: OF `subprocess.run` itself, before any caller sees a return code. Every caller
#: already reads this as *git could not produce this* and degrades to `None`, and
#: a decode failure is the same kind of non-answer -- so it is declared rather
#: than left to crash the first walk over a non-UTF-8 path.
GIT_ERRORS = (OSError, subprocess.SubprocessError, UnicodeDecodeError)
