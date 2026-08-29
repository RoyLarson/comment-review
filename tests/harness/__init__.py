"""Harness tests.

! THIS FILE IS LOAD-BEARING, for the same reason `tests/gates/__init__.py` is.
Without it pytest imports this directory's `conftest.py` under the bare name
`conftest`, which is the name `tests/conftest.py` already holds -- and the 30
modules doing `from conftest import build, ...` then read THIS one. Measured
2026-08-29: 15 collection errors, every one an ImportError naming a symbol the
shadowing file does not define.
"""
