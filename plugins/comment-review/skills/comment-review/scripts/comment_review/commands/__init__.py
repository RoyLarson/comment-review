"""The console face of this package: argument parsing and exit codes only.

One module per command. Each holds the `argparse` for that command and nothing
else -- the work it calls lives in the library package it names.

!! A LIBRARY MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS LIBRARIES; A
COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `docs/decision-log.md Process: #12`.
Before it, TEN of nineteen modules carried a `main()` and four of those were
imported by other modules while also being commands -- `addresser` by seven.

! THE CONSOLE GUARD IS CALLED ONCE, IN `__main__.py`, because that is where the
console is entered. It was called from each of the eleven `main()`s, which was
correct while each was its own entry point and is a duplicate now that they
share one.
"""
