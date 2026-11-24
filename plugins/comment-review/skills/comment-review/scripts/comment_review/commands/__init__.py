"""The console face of this package: arguments, the files they name, exit codes.

One module per command. Each holds the `argparse` for that command, and reads and
writes the files it names -- the work it calls lives in the package it names.

`report` is the one module here that is not a command: the exit codes and the
console report the fold's commands share, which `check` and `mark` also use.
"""
