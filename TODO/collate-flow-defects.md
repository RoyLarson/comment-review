# Twelve defects in `flows/collate.py`, from a review of one file

```
Status:   open
Progress: 0 of 12 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, a code review of `flows/collate.py` on the collate-
          flow branch -- twelve tasks, six of them measured by running `collate()`, with
          no per-module TODO to hold them)
```

## Objective

Twelve defects in `flows/collate.py`, from a review of that one file on 2026-08-30.

!! **THIS IS THE PER-MODULE CLAUSE, NOT THE DEPENDENCY CLAUSE.** These twelve do not
have to land together, and claiming they did would be the test that nearly everything
passes -- which `conventions.md` records as what put 34 single-observation files on
this board. What earns the file is that `src/comment_review/flows/collate.py` has no
TODO of its own and these are general fixes to it. Roy, 2026-08-30: *"For general
fixes a new TODO can be made per module."* Same shape as
[`collator-defects`](collator-defects.md).

## What was measured

Six were measured by RUNNING `collate()` against a binder carrying `m.py@b1..b4`; six
were read against the file and checked with `grep` and `git check-ignore`.

- a copy whose `sheets` key is present and null: `TypeError` out of line 498, which
  discards the `Problem` `problems_in` computed one line earlier
- two `patch` marks at one place: `problems == []`, while `problems_in` over the
  chief's copy reports `m.py@b1: needs at least one source` -- the synthesized
  `correct` owes sources that neither `patch` owed
- two roles each returning an `add` at `m.py@b1`: `rereads` empty and one composed
  `correct`, discarding the widening `desk.collator._outcome` performs for an `add`
- one role's copy sharded over `m.py` and `n.py`, both fully unruled: `unruled ==
  {'block-context': ['n.py@b1']}` and `m.py@b1` appears nowhere
- a copy returned with `sheets[].path` rewritten: the chief's sheet ships `sha=''`,
  which `desk/containers.py:113-115` admits as the not-a-repo case
- a `correct` appended at `zzz.py@b1`: reaches the chief's copy with `problems == []`
  and `drift == []`

! **THE SHARD CASE IS A CONTRADICTION INSIDE ONE FUNCTION**: `collate`'s own `Args` at
481-482 says `edit_copies` is one per role OR one per shard, and a `dict[str, list]`
keyed on the role name cannot hold the second.

! **THE LAST ONE IS FILED AS PROSE ONLY.** Address integrity is deferred work and
`flows/collate.py:469` says so; what is filed is the docstring at 363-365 promising
what the deferral has not delivered.

The six read findings: `Process: #22` is cited at `flows/collate.py:25`, `:274` and
`docs/decision-log.md:1780`, but `grep -n "^## "` puts the quoted words at
`docs/decision-log.md:737` inside `## Vocabulary` (line 325), while `Process: #22` at
line 1226 is a different ruling. Two citations at `:278` and `:504` name work items
under `.superpowers/sdd/`, which `.gitignore:46` excludes -- both are substantively
accurate and only the reference is wrong; eight neighbouring citations resolve.
`_composition`'s `Returns:` at 133-135 names two of the three ways it returns `None`,
and the `CannotCompose` message discarded at line 146 reaches no caller. The composed
mark's `anchor` is read off `owing[0]` at line 156, which lines 148-153 themselves
call an accident of how the copies were handed in. And the header list at lines 5-17
names eight acts while `Collated` has eight attributes, so the two it omits --
`unruled` and `tally` -- are invisible to a count.

## What was measured

Six were measured by RUNNING `collate()` against a binder carrying `m.py@b1..b4`; six
were read against the file and checked with `grep` and `git check-ignore`.

- a copy whose `sheets` key is present and null: `TypeError` out of line 498, which
  discards the `Problem` `problems_in` computed one line earlier
- two `patch` marks at one place: `problems == []`, while `problems_in` over the chief's
  copy reports `m.py@b1: needs at least one source` -- the synthesized `correct` owes
  sources that neither `patch` owed
- two roles each returning an `add` at `m.py@b1`: `rereads` empty and one composed
  `correct`, discarding the widening `desk.collator._outcome` performs for an `add`
- one role's copy sharded over `m.py` and `n.py`, both fully unruled:
  `unruled == {'block-context': ['n.py@b1']}` and `m.py@b1` appears nowhere
- a copy returned with `sheets[].path` rewritten: the chief's sheet ships `sha=''`,
  which `desk/containers.py:113-115` admits as the not-a-repo case
- a `correct` appended at `zzz.py@b1`: reaches the chief's copy with `problems == []`
  and `drift == []`

! **THE SHARD CASE IS A CONTRADICTION INSIDE ONE FUNCTION**: `collate`'s own `Args` at
481-482 says `edit_copies` is one per role OR one per shard, and a `dict[str, list]`
keyed on the role name cannot hold the second.

! **THE LAST ONE IS FILED AS PROSE ONLY.** Address integrity is deferred work and
`flows/collate.py:469` says so; what is filed is the docstring at 363-365 promising what
the deferral has not delivered.

The six read findings: `Process: #22` is cited at `flows/collate.py:25`, `:274` and
`docs/decision-log.md:1780`, but `grep -n "^## "` puts the quoted words at
`docs/decision-log.md:737` inside `## Vocabulary` (line 325), while `Process: #22` at
line 1226 is a different ruling. Two citations at `:278` and `:504` name work items
under `.superpowers/sdd/`, which `.gitignore:46` excludes -- both are substantively
accurate and only the reference is wrong; eight neighbouring citations resolve.
`_composition`'s `Returns:` at 133-135 names two of the three ways it returns `None`,
and the `CannotCompose` message discarded at line 146 reaches no caller. The composed
mark's `anchor` is read off `owing[0]` at line 156, which lines 148-153 themselves call
an accident of how the copies were handed in. And the header list at lines 5-17 names
eight acts while `Collated` has eight attributes, so the two it omits -- `unruled` and
`tally` -- are invisible to a count.

## Tasks

- [ ] T1 | Implement the `isinstance(sheets, list)` guard in
      `flows.collate._reconcilable` and widen `commands/collate.py`'s
      `RECONCILE_ERRORS`, so a malformed `sheets` cannot discard problems
      already found. Verify: a copy whose `sheets` is null reports the `Problem`
      `problems_in` computed one line earlier and exits by the documented
      refusal; today `collate` raises `TypeError` out of line 498 and the
      traceback escapes.
- [ ] T2 | Implement a source requirement on the mark
      `flows.collate._composition` synthesizes, so a `correct` built from marks
      that owe no sources is not written to the chief's copy. Verify: two
      `patch` marks at one place give a refusal or a mark carrying sources, and
      the claim at lines 123-125 that the composed entry parses is made true;
      today `collate` returns `problems == []` while `desk.collator.problems_in`
      over the chief's copy reports `m.py@b1: needs at least one source`.
- [ ] T3 | Implement an instruction filter in `flows.collate._composition` that
      refuses to compose an `add`, so the widening `desk.collator._outcome`
      performs for an `add` place is not discarded. Verify: two roles each
      returning an `add` at `m.py@b1` on different lines leave the place in
      `rereads` with every reading role named; today `rereads` is empty and the
      chief's copy holds one composed `correct`.
- [ ] T4 | Update the `unruled` and `tally` accumulation at
      `flows/collate.py:496-498` so two shards of one role do not overwrite each
      other. Verify: one `block- context` copy split into shards over `m.py` and
      `n.py`, both fully unruled, reports both addresses; today `unruled` is
      `{'block-context': ['n.py@b1']}` and `m.py@b1` appears nowhere.
- [ ] T5 | Update the two `Process: #22` citations at `flows/collate.py:25` and
      `:274` to `Vocabulary: #22`, and the same mis-citation at `docs/decision-
      log.md:1780`. Verify: the quoted words `nobody is on record as having
      chosen it` are at `docs/decision-log.md:737`, inside the `## Vocabulary`
      section starting at line 325; `Process: #22` at line 1226 is `THE SHA IS
      TAKEN AT THE READ`.
- [ ] T6 | Update `flows.collate._chief_copy` to take each sheet's `path` and
      `sha` from the binder rather than from the copies the roles returned.
      Verify: a single-role stage whose copy came back with `sheets[].path`
      rewritten still ships the binder's sha; today the chief's sheet carries
      `sha=''` with `problems == []`, and `desk/containers.py:113-115` admits an
      empty sha as the not-a-repo case.
- [ ] T7 | Update `_chief_copy`'s claim at `flows/collate.py:363-365` that the
      sheets name files that are actually there, since line 389 writes an
      unresolved address through flattened and unchecked. Verify: the prose says
      what `desk.collator.docket_from` says at 992-995, and a role appending a
      `correct` at `zzz.py@b1` still reaches the chief's copy with `problems ==
      []` and `drift == []`.
- [ ] T8 | Update `_composition`'s `Returns:` block at
      `flows/collate.py:133-135` so it names all three ways the function returns
      `None` -- fewer than two roles, differing instructions, and
      `CannotCompose`. Verify: the block names the instruction mismatch at lines
      141-142, which it omits today.
- [ ] T9 | Implement a recorded reason on every `rereads` entry `_resolve`
      appends, carrying the `CannotCompose` message discarded at line 146.
      Verify: a place re-read because two roles overlapped a span reports `base
      lines 3-4 were edited by block-context, function-context`, and a place
      re-read for a differing instruction says so; today neither `Collated` nor
      `commands/collate.py`'s printout carries any cause.
- [ ] T10 | Update `flows.collate._composition` so the composed mark's `anchor`
      is derived in role order, like `sources` and `reason`, rather than from
      `owing[0]`. Verify: composing the same two marks with `edit_copies` handed
      in either order gives one anchor; today line 156 reads
      `owing[0].mark.anchor`, which lines 148-153 call an accident of how the
      copies were handed to `collate`.
- [ ] T11 | Update the two citations at `flows/collate.py:278` and `:504`, which
      name work items under `.superpowers/sdd/` that `.gitignore:46` excludes.
      Verify: `git check-ignore -v` names no path cited in the file, and each
      rule is stated in place or cited to
      `docs/plans/0.2.4-the-commands-for-the- middle.md`.
- [ ] T12 | Update the header list at `flows/collate.py:5-17` so it accounts for
      `unruled` and `tally`, which the same loop computes at lines 496-498.
      Verify: every attribute of `Collated` is attributable to a named act, and
      a reader counting acts against fields finds a correspondence.
