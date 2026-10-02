# Repair comment wrapping review findings

```
Status:   open
Progress: 12 of 13 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-02 (review)
```

## Objective

Repair comment wrapping review findings.

## Tasks

- [x] T1 | Block and line fragments retained; focused and full tests pass | 731af89e | Fix
      mixed-form paragraph wrapping in reading/lexer.py:196; test adjacent block
      and line comments remain comments
- [x] T2 | Empty removal retains suffix code; move and drop regressions pass | 2ac2970c | Fix
      empty removal in reading/comment.py:23 to retain code after a block
      closer; test trailing moves and drops preserve code
- [x] T3 | Opening-line literal stars retained in move and drop regressions | 731af89e | Fix
      decoration stripping in reading/lexer.py:196 to retain literal
      opening-line stars; test retained *ptr prose
- [x] T4 | Wrap wording states width use and intact words; prose review passed | 731af89e | Rewrite
      reading/comment.py:23 wrap docstring to state width is a target; verify it
      describes intact long words
- [x] T5 | Unique match, wrapped return and refusal wording reviewed | 731af89e | Rewrite
      reading/comment.py:60 without_once docstring to state unique matching and
      wrapped returns; verify success and refusal paths
- [x] T6 | Real closers located with nesting-aware scan; adjacent code retained | 2ac2970c | Locate
      the real block closer in reading/lexer.py:305; test closer text in
      following code survives moves and drops
- [x] T7 | Remaining prose named explicitly; four prose reviews found no issues | 19539398 | Clarify
      reading/comment.py:100 without_raw docstring to name the remaining prose;
      verify its input precondition and output
- [x] T8 | INI and Rust mixed markers retain their forms in move and drop tests | 19539398 | Split
      line-marker forms in reading/lexer.py:196; test mixed INI and Rust markers
      retain their original forms
- [x] T9 | Pointer prose matches and drops without retaining its literal star | 19539398 | Distinguish
      literal continuation stars in reading/lexer.py:347; test *ptr matches and
      drops without retaining its star
- [x] T10 | Repeated marked blank lines survive move and drop regressions | 19539398 | Record
      blank comment separators in reading/comment.py:117; test moves and drops
      retain repeated blank lines
- [x] T11 | Padded blank separators retained; empty removal leaves no delimiters | 2ac2970c | Separate
      trailing whitespace lines in reading/lexer.py:248; test block closer
      removal and exact matching retain blank separators
- [x] T12 | Empty block forms add no prose; spanning moves and raw drops pass | 2ac2970c | Recognize
      empty overlapping delimiters in reading/lexer.py:248; test snippets
      spanning /**/ match without spurious prose
- [ ] T13 | Limit decorative star prefixes in reading/lexer.py:368; test Python
      docstring, Lua and Ruby bullets survive moves and drops
