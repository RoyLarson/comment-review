# Repair comment wrapping review findings

```
Status:   open
Progress: 4 of 10 tasks closed
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
- [ ] T2 | Fix empty removal in reading/comment.py:23 to retain code after a
      block closer; test trailing moves and drops preserve code
- [x] T3 | Opening-line literal stars retained in move and drop regressions | 731af89e | Fix
      decoration stripping in reading/lexer.py:196 to retain literal
      opening-line stars; test retained *ptr prose
- [x] T4 | Wrap wording states width use and intact words; prose review passed | 731af89e | Rewrite
      reading/comment.py:23 wrap docstring to state width is a target; verify it
      describes intact long words
- [x] T5 | Unique match, wrapped return and refusal wording reviewed | 731af89e | Rewrite
      reading/comment.py:60 without_once docstring to state unique matching and
      wrapped returns; verify success and refusal paths
- [ ] T6 | Locate the real block closer in reading/lexer.py:305; test closer
      text in following code survives moves and drops
- [ ] T7 | Clarify reading/comment.py:100 without_raw docstring to name the
      remaining prose; verify its input precondition and output
- [ ] T8 | Split line-marker forms in reading/lexer.py:196; test mixed INI and
      Rust markers retain their original forms
- [ ] T9 | Distinguish literal continuation stars in reading/lexer.py:347; test
      *ptr matches and drops without retaining its star
- [ ] T10 | Record blank comment separators in reading/comment.py:117; test
      moves and drops retain repeated blank lines
