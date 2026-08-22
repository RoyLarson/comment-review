# Ten findings in lexer.py and language.py, from three review rounds

```
Status:   open
Progress: 1 of 15 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-22 (C:/Program Files/Git/simplify rounds 1 and 2 and /code-review high
          round 3, 2026-08-22 -- the ones touching the two reader modules, filed because
          those modules are settled and will not shift under front-half-undetermined)
```

## Objective

Ten findings in lexer.py and language.py, from three review rounds.

## Tasks

- [x] lexer.py:1582 -- the unparsed fallback catches SyntaxError, but
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
- [ ] JAVA record IS A SOFT KEYWORD AND ITS ROW CANNOT SAY SO. record = lookup()
      is a legal assignment and mints a spurious a place; MEASURED 2026-08-22. !
      Kotlin data class -- two FIXED words -- fixes the same class for Kotlin, and
      trying it on Java as *record + space* BROKE THE REAL DECLARATION, because
      Java second word is the record NAME and varies. ! Roy 2026-08-22: *every
      language gets all of the definitions necessary to parse it specifically,
      because anything else is failing the SRP rules* -- so Java needs its OWN
      expression of soft keyword, not Kotlins. Swift required and convenience are
      the same class
- [ ] language.py -- rust, ruby and c still have no spanning_quotes, and theirs
      are EXPENSIVE. A Rust multi-line string opens with a plain double quote, and
      a Ruby heredoc opens with the same two characters as array append, so
      declaring either refuses nearly every file in that language. ! The four
      DISTINCTIVE delimiters landed 2026-08-22 (go backtick, cpp R-quote, csharp
      at-quote, shell heredoc). These three want the STATEFUL reader from python-
      cannot-read-python, which fixes them by transitivity.
- [ ] language.py -- the lua long-bracket list stops at two equals signs and the
      level is UNBOUNDED. The bound is stated in the row rather than left silent,
      but a deeper comment is still read as code. ! MEASURED 2026-08-22: the
      compositor identity CANNOT catch this -- prose read as code sets back byte-
      identical -- so the sentence test in test_fixture_identity.py is the only
      gate that would.
- [ ] page.py documentable() -- a declaration whose doc shares its LINE is
      skipped, so a one-line `def f(): docstring` yields a paragraph with no
      address and census.py refuses the WHOLE FILE at exit 1, advising a re-run
      that never helps. MEASURED 2026-08-22 on legal Python. ! * NEEDS A RULING:
      does a same-line docstring get an `a`, is it intermediate and ignored (the
      2026-08-19 intermediate-comment ruling), or is it refused with a message
      that names the cause? The advice cannot be written before the answer.
- [ ] language.py -- `---` IS LUA'S DOC COMMENT and the row does not say so, so
      every documented declaration reads as `undocumented`. MEASURED 2026-08-22 on
      corpora/neovim, the first real Lua ever censused here: 2,505 of 2,741
      declarations carry a `---` run above them (91%) and ALL of them came back
      undocumented; 43,563 of 92,578 lines open with `---`, of which 11,987 are
      LuaLS annotations. ! THE ONE-LINE FIX IS WRONG AND WAS TRIED: adding `---`
      to line_comment and doc_line turned 4,230 comments into docstrings and
      turned 0 differing files into 8. LuaLS writes `--- @class` and `--- @field`
      runs that document NO declaration -- whole type-stub files are nothing else
      -- and a docstring tied to a declaration that is not there cannot be set
      back where it was read. ! So `---` is a doc marker AND a standalone type
      declaration in one language, which no field on the row can express today. *
      NEEDS A RULING or a new field: is a doc run above no declaration a comment,
      a docstring anchored to the module, or its own thing?
