# A quote inside a block comment blanks the comment's own closer

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
```

## Objective

A quote inside a block comment blanks the comment's own closer.

## Tasks

- [ ] !! MINE, 2026-08-21. `_strip_strings` runs on the raw line before the
      comment opener is known, so `/* the " character */` blanks everything after
      the quote -- including `*/`. `run_ends`, added the same day, is fed the
      blanked text and never sees the closer.
- [ ] MEASURED: that line followed by `int a = 1; // note` censuses as ONE
      paragraph spanning both lines. `int a = 1;` leaves `code_lines` entirely and
      every `b` and `c` boundary below it moves.
- [ ] ! The `unterminated-paragraph-comment` annotation does fire, so
      `prove_unchanged` refuses the file -- but stages 2 through 5 still hand four
      reviewers a census saying the file has no code.
- [ ] ! `/* don't */` is ordinary English, so this is not an exotic input.
