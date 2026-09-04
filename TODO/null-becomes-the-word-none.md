# A present-but-null key becomes the four characters None

```
Status:   open
Progress: 0 of 6 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, a fix round on flows/carry.py surfaced the same
          pattern one line above its own fix comment in flows/distribute.py)
```

## Objective

A present-but-null key becomes the four characters `None`.

**`str(d.get(k, ""))` IS NOT A NULL GUARD.** The default fires only when the key is
ABSENT. A key that is PRESENT and holds `null` -- which is what a parsed artifact
carries when a serialiser failed, or when a writer omitted a value it had -- reaches
`str()` as `None` and comes out as the string `"None"`.

**MEASURED 2026-08-30 across `src/comment_review/`:**

| spelling | sites | on a present null |
| --- | --- | --- |
| `str(d.get(k, ""))` | **26** | `"None"` |
| `str(d.get(k) or "")` | 8 | `""` |

Two spellings for one intent, mixed through the same modules, and nothing says which
is the form.

!! **THE FIX COMMENT SITS DIRECTLY BELOW AN UNFIXED INSTANCE OF THE BUG IT
DESCRIBES.** `6b2695f` guarded `sha` in `flows/distribute.py` and wrote a comment
explaining the hazard -- *"unlike `flows.carry` there is no `str()` here to turn it
into the word `None`"*. The line immediately ABOVE that comment is
`"path": str(page.get("path", ""))`, which has exactly that `str()`. ! The reason it
was missed is the reason it is worth a file: the pattern is invisible at the site,
because every instance reads as an ordinary default.

! **NOT ALL 26 ARE DEFECTS, AND THE WORK IS DECIDING WHICH.** A site whose dict was
built by this codebase two lines earlier cannot receive a null; a site reading a
binder, a docket or an edit copy can. **The task is to separate them, not to rewrite
all 26** -- a mechanical sweep would churn the safe sites and prove nothing about
the unsafe ones.

! **IT IS THE SAME CLASS AS TWO ALREADY-FIXED DEFECTS, WHICH IS WHY IT RECURS.**
`results/verdicts.py` once admitted a citation whose `verbatim` was `null` because
it rendered as the word `None` and the cited line happened to contain it;
`commands/collate.py` carried it for a `sha` and a `stage` until `d708750`. ! A
defect fixed three times at three sites and never once as a pattern is a defect
that will be fixed a fourth time.

! **RELATED BUT NOT THE SAME QUESTION:**
[`null-is-not-a-decision`](null-is-not-a-decision.md) asks what a `null` MEANS in a
docket -- a serialisation failure and an approved drop are the same bytes. This asks
what a `null` BECOMES when something stringifies it. The first is semantics, the
second is a guard.

## Tasks

- [ ] T1 | Implement the null guard at `flows/distribute.py` for `path` and
      `cue`, beside the `sha` already guarded in `6b2695f`. Verify: a binder
      page carrying `"path": null` reaches the sheet as `""`, never as the four
      characters `None`; the test goes red against today's code.
- [ ] T2 | Update every site that reads a PARSED ARTIFACT -- a binder, a docket,
      an edit copy -- to the null-safe spelling. Verify: the unsafe form appears
      zero times in the modules that parse external JSON, counted with `grep -rn
      'str([a-z_]*\.get([^)]*, *"")' src/comment_review/`.
- [ ] T3 | Update each REMAINING unsafe site with a sentence saying why a null
      cannot arrive there, or convert it. Verify: no site carries the unsafe
      spelling without either a guard or a stated reason.
- [ ] T4 | Record the repo's null-guard spelling once, where a reader finds it.
      Verify: `docs/conventions.md` or the module that owns the boundary states
      it, and no second file restates it.
- [ ] T5 | Implement the null guard at `binder.rows_of` for `path`, beside the
      two sibling sites that already carry one -- `flows/distribute.py:98` for
      `sha` and `flows/carry.py:137-138`. Verify: a binder page carrying
      `"path": null` no longer composes the address `None@b1`; today
      `str(page.get("path", ""))` defaults only on an ABSENT key, so a present
      null enters `known_addresses` as a syntactically valid address and is
      compared for equality against marks.
- [ ] T6 | Update `docket.read`'s role check at `docket.py:148-150` to key on
      `"role" in page`, so a present JSON `null` is ruled on rather than skipped
      by the `role is not None` first clause, and normalise `role` in
      `docket.schedules_of` and `flows/revise._set_by` the way `_real_pages`
      already does. Verify: a page carrying `"role": null` is refused or folded
      into the absent case; today `schedules_of` returns `Schedule(...,
      role='None')` and `_set_by` maps `pkg:a.py@b1` to `'None'`. Carry
      `desk/collator.py:956-962`'s comment and the `tests/test_docket.py:187`
      treatment across to `role`, which has the weaker guard of the two.
