# Ten findings in lexer.py and language.py, from three review rounds

```
Status:   open
Progress: 0 of 10 tasks done
Owner:    comment-review
Requires-Roy: false
Raised:   2026-08-22 (C:/Program Files/Git/simplify rounds 1 and 2 and /code-review high
          round 3, 2026-08-22 -- the ones touching the two reader modules, filed because
          those modules are settled and will not shift under front-half-undetermined)
```

## Objective

Ten findings in lexer.py and language.py, from three review rounds.

## Tasks

- [ ] lexer.py:1582 -- the unparsed fallback catches SyntaxError, but
      tokenize.TokenError is NOT one (repo.PARSE_ERRORS says so) and
      IndentationError is raised inside the loop. A file mid-edit escapes page_for
      entirely instead of getting the unparsed paragraph page.py expects
- [ ] lexer.py:1243 -- the EOF back-matter split runs BEFORE the in_block stamp,
      and that stamp only reaches out[-1]. An unclosed block comment yields a
      paragraph holding code with no annotation, contradicting the two lines below
      it
- [ ] lexer.py:1386 -- the ends filter excludes LEADING and trailing comments but
      not MATTER, so front matter ALSO claims declaration 1. A Ruby frozen-string-
      literal header produces both a1 declares=1 and f0 declares=1
- [ ] language.py:357 -- the shell row cannot say that hash is inert after a
      dollar-brace. n=DOLLAR-BRACE-hash-arr  # count censuses as a trailing
      comment at original_column=5, and since the galley keeps line[:column-1] a
      patch or drop there leaves a broken expansion
- [ ] language.py:291 and :193 -- Kotlin data and Java record are SOFT keywords,
      and _declares_here matches the first word, so data = load() and record =
      lookup() mint spurious a places. Kotlin open and Swift required/convenience
      are the same class. ! This is the failure the C/C++ row was written to avoid
- [ ] language.py:9 cites scripts/check_language_leaf.py as holding its two-
      importer rule. THAT FILE DOES NOT EXIST -- 11 files in scripts/, not among
      them. And the rule is broken in substance: lexer.py:55 re-exports Language,
      language_for and tier_for, and desk, page, prove_unchanged and census all
      read language fields through that door -- the exact four modules
      language.py:16 names as the problem the split was made to end
- [ ] DUPLICATION: tuple(sorted(lang.line_comment, key=len, reverse=True)) is
      byte-identical in desk.py:376 and lexer.py:771; and the continuation stamp
      is copy-pasted across BOTH lexer tiers including a user-visible sentence
- [ ] lexer.py:1345 filters a sorted list where bisect applies
- [ ] FOUR one-element lists standing in for nonlocal (lexer.py:786/795/807/1445),
      costing 14 subscripts and four comments justifying a workaround the 3.11
      floor does not need
- [ ] Paragraph.lines is filled by THREE incompatible rules and read by exactly
      ONE display column (census.py:540). ! Related to census-row-carries-empty-
      fields, where a margin row shows lines=0 with raw_lines holding one empty
      string
