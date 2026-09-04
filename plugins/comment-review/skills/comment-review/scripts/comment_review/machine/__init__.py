"""What the machine says: the checkout, the filesystem, the console, the tuples.

    repo         git, and reading a file off disk
    constants    the text/encoding rules, and the console guard
    exceptions   every exception tuple, bound to a NAME
    json_object  text as a JSON object, or why it is not one

!! THE TUPLES LIVE HERE SO NO SHIPPED `except` CLAUSE HOLDS A LITERAL. A repo
targeting a newer ruff `target-version` can rewrite `except (A, B):` into PEP 758
form, which is a `SyntaxError` on the floor interpreter -- and the author of this
repo never sees it, because the rewrite happens in someone else's `.claude/`.

! THE NAME IS PROVISIONAL. `io` was the obvious word and collides: `lexer` and
the collator both `import io` for `StringIO`, so an `io` package would shadow the
stdlib name ambiguously for any reader. Roy approved `machine` 2026-08-24.
"""
