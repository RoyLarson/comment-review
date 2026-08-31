# A wrapped trailing comment is split into two blocks, and the tail re-anchors

```
Status:   CLOSED 2026-08-17 by group A
Progress: 5 of 5 tasks done
Owner:    session * Roy (* 1 ruling)
Raised:   2026-08-17 (ownership-context diagnosed the mechanism during a live run and named
          its consequence: "three Rx fields now end mid-clause")
```

## Objective

**One sentence, two blocks, and the second half is read against the wrong declaration.**
Reproduced:

```python
x = 1  # a claim that
       # wraps onto the next line
y = 2
```

```
trailing-comment   lines 1-1   text='a claim that'
comment            lines 2-2   text='wraps onto the next line'
```

The tail becomes a leading comment for `y = 2` and every role measures it against `y`.

! **The census is not wrong by its own definition.** A block is the interval between two lines
of CODE. Line 1 holds code, line 3 holds code, so line 2 is an interval of its own and gets its
own block. The definition and the prose disagree, and the prose is one sentence regardless.

! The mechanism is deliberate. `blocks_stdlib` flushes on a trailing comment, and the reason is
recorded there: without it a trailing comment merged with the next leading run across two blank
lines, "gluing `raise original DoesNotExist` to an unrelated `TODO` four lines down". That fix
is right and this is its cost.

## !! Why it matters more than a mis-split

`SKILL.md` already names the symptom: *"A block that ends mid-clause is a finding, and its
verdict is `correct`."* So a reviewer meeting the first half files a real finding against a
mid-clause ending **the census manufactured**, and a task agent applying it repairs prose that
was never broken.

! And the second half is not merely orphaned, it is ATTRIBUTED. It sits above `y = 2` and is
indistinguishable from documentation for `y`, which is the wrong-code measurement
`ownership-context` exists to catch -- except here no role can catch it, because at the
`tokenized` tier the census reports exactly this and offers no evidence of the join.

## Tasks

- [x] T1 | FINISHED | unknown | * Rule on whether a CONTINUATION line is part of
      the trailing comment or its own block. ! It is a ruling and not a fix,
      because it puts the block definition and the sentence in conflict and one
      has to give. Candidates: **(a)** leave it -- the definition holds, and the
      split is a fact reviewers work with; **(b)** a comment on the line
      IMMEDIATELY after a trailing comment, with no code and no blank line
      between, continues that run; **(c)** keep the split and STAMP it, so a
      reviewer is told the block is a continuation and does not file `correct`
      against a manufactured mid-clause. ! Recommendation: **(c) before (b)**.
      (b) changes block boundaries and renumbers every census, which is
      expensive and invalidates every measurement taken so far; (c) costs an
      annotation and removes the false finding, which is the actual harm. !
      **RULED (c): STAMP it.** Roy approved it with section A of the coherence
      spec. Merging would renumber every census and invalidate every measurement
      taken against one; the harm is a reviewer filing `correct` against a
      mid-clause the census manufactured, and the annotation removes that.

- [x] T2 | FINISHED | unknown | Whichever is chosen, keep the flush that
      prevents the ORIGINAL defect. A trailing comment merging with a leading
      run two blank lines later is the worse failure and is already measured. !
      **DONE by group A, 2026-08-17.** Untouched at both tiers.

- [x] T3 | FINISHED | unknown | Decide what a continuation does to
      `counted_lines` and the cap. Under (b) two lines become one block and the
      charge changes; under (a) and (c) it does not. ! **DONE by group A,
      2026-08-17.** Nothing: under (c) the blocks are unchanged and so is the
      charge.

- [x] T4 | FINISHED | unknown | Say whether the LEXICAL tier does the same
      thing. `blocks_lexical` flushes on a trailing comment too, so it likely
      splits identically -- but it was not measured, and this file must not
      claim it. ! **MEASURED, and it did.** `blocks_lexical` split a Go wrapped
      trailing comment identically and stamped nothing, so group A fixed both
      tiers. The file was right to refuse to claim it unmeasured.

- [x] T5 | FINISHED | unknown | Add the reproduction above as a test whichever
      way it is ruled, so the behaviour is pinned rather than incidental. !
      Today nothing in `tests/` covers a wrapped trailing comment at either
      tier. ! **DONE by group A, 2026-08-17.** Five tests across the two tiers,
      including two guards against over-stamping.
