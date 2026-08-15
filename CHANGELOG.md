# Change Log

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

⚠ This file starts at 0.1.2. Earlier work is in `git log` and has no entry here — the
file existed as a one-line stub until this release. Neither
`plugins/comment-review/.claude-plugin/plugin.json` nor `.claude-plugin/marketplace.json`
carries a `version` field, so a version number lives only here and an installed plugin
cannot report which one it is.

## [0.1.2] — 2026-08-15

### Changed — BREAKING

- **The four reviewer agents are renamed for the scope each checks.** Anything dispatching
  them by their namespaced IDs must be updated:

  | was | now | asks |
  | --- | --- | --- |
  | `comment-review:comment-review-locality` | `comment-review:comment-review-ownership-context` | does this comment belong to the line it sits on? |
  | `comment-review:comment-review-currency` | `comment-review:comment-review-block-context` | is every claim in this block true of the code it sits with? |
  | `comment-review:comment-review-functionality` | `comment-review:comment-review-function-context` | does the commentary match what the function is for? |
  | `comment-review:comment-review-module-coherence` | `comment-review:comment-review-module-context` | do the comments say this module is one set of ideas? |

  `ownership-context` is a rewrite rather than a rename: `locality` asked whether prose sat
  in the right place, and the replacement asks first whether the prose is assessable where
  it sits at all.

- **`verdicts.py --angles` takes the new names.** It matches a declared angle against each
  report file's stem, so report files must be named for the new angles.

### Added

- **Each agent states what its own `clean` asserts.** `clean` is one of the nine verdicts
  and means "nothing to report from this angle"; what that claims differs per angle, and
  each agent file now says which.
- **`ownership-context`** — claim homes (where one proposition is stated at several sites,
  which site is its home), duplication, and the assessability gate the other three depend on.
- **`block-context`** — constraints checked against the line that enforces them (value,
  direction, units, boundary) and worked examples, which are executed rather than read.
- **`function-context`** — the one-function test, and reading a body's comments in the order
  the body performs them.
- **`module-context`** — walking the module's exposed surface as a checklist.
- **`truthy` is defined** in `references/reviewer-brief.md`: a sentence states one checkable
  proposition about the code it is attached to. It is a property of form, not of truth.
- **A placement precedence rule.** `ownership-context` and `function-context` can both reach
  a comment that is true but misplaced. Both findings stand, and where they name different
  destinations, `ownership-context`'s governs. Neither angle defers to the other; resolving
  the disagreement is the task agent's, not a reviewer's.
- **A line budget for the four agent files** in `docs/limitations.md`, so a rule added to one
  replaces another rather than accumulating.

### Fixed

- **`ownership-context` now runs at every level, including `fact-check`.** The other three
  measure a claim against the code at their scope, so a claim attached to the wrong scope was
  being measured against the wrong code and corrected into a falsehood.
- **`reanchor`'s availability depends on the level**, not only on whether a destination tree
  resolved. At `fact-check` the verdict set carries no `reanchor`, and the finding is `query`
  — never `clean`.
- **`SKILL.md` no longer restates rules that `references/reviewer-brief.md` owns** — the
  `query`/`reanchor` rule and the `move`/`reanchor` rule each had two statements that could
  drift apart.
- **The site-home cell no longer offers `move`** for relocating a claim within a file.
  Mislabelling an in-file relocation as `move` was measured converting the finding to `clean`
  and losing it.
- **A forward reference in `comment-review-block-context.md` names its target section**
  instead of pointing 42 lines away with "below".
