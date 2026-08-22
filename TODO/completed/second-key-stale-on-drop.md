# The leading edge keeps a stale second key after a drop, and the compositor is correct only because it never reads one

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    comment-review
Requires-Roy: false
Raised:   2026-08-22 (Roy asked 2026-08-22 whether the pair key still holds for every
          language after an add or a drop; the collapse does, the second key does not)
```

## Objective

The leading edge keeps a stale second key after a drop, and the compositor is correct only because it never reads one.

## Tasks

- [ ] MEASURED 2026-08-22: dropping b1 from '# X / a = 1 / blank / # P / b = 2 /
      blank / # Y / c = 3' sets correctly -- the blank above b = 2 survives -- and
      leaves the edge ('c0', 'b1') in page.leading. b1 sets nothing now, so the
      pair names a place it does not separate
- [ ] Roy ruled 2026-08-21 that the survivor gets a NEW key taking the new end and
      beginning. That re-keying is not implemented: compositor.py:158 collapses to
      the FIRST key, so the stale half is never consulted and the output is right
      anyway
- [ ] * RULING: re-key on the drop, or state in Page.leading that the second key
      is a BUILD-TIME fact and not valid after an edit? The first makes the pair
      true and costs a pass; the second keeps the code as it is and makes the type
      honest
- [ ] ! THE PAIR IS WHAT MAKES THE EDGE CITABLE, which is the reason it exists --
      ('f0', 'a0') reads as the space between the file matter and the module doc.
      A stale pair is exactly the class ownership-context is chartered to catch:
      prose that names the wrong anchor
- [ ] MEASURED, the part that is NOT at risk: collapsing (before, after) to before
      loses ZERO edges over 96,047 edges on 2,792 pages in ten languages (c
      48,966, python 41,356, yaml 4,174, toml-ini 672, cpp 557, javascript 161,
      typescript 147, shell 7, sql 4, lua 3). tie_leading runs once at build and
      nothing re-ties it, verified either side of an add and a drop in python, c,
      rust, go, ruby and yaml
- [ ] COVERAGE GAP: rust, go and ruby were checked with hand fixtures only, and
      java, csharp, swift, kotlin have neither corpus nor fixture here -- see
      corpora-are-all-python
