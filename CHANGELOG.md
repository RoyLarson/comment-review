# Change Log

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

⚠ This file starts at 0.1.2. Earlier work is in `git log` and has no entry here — the
file existed as a one-line stub until this release. Neither
`plugins/comment-review/.claude-plugin/plugin.json` nor `.claude-plugin/marketplace.json`
carries a `version` field, so a version number lives only here and an installed plugin
cannot report which one it is.

## [Unreleased]

**Settling the system's own vocabulary.** A twelve-agent collection over the live tree found
nine terms used with a fixed sense and stated nowhere, and fifteen more carrying two or three
senses each. Each is being ruled on in turn — state the meaning, split the word, or delete the
use — and the ones that change a published name land here. Terms are settled in order of what
POINTS at them: names living in identifiers, filenames and flags first, because those are the
ones that can dangle. Survey: `docs/vocabulary-usage.md`.

### Changed — BREAKING

- **`angle` is retired. The four are EDITORIAL ROLES.** The word came from the `/simplify`
  skill, which uses it for the focuses that pass works at; it stopped fitting once these
  became agents with scopes, and it was the most-used term in the tree with no definition
  anywhere — six senses at ~250 sites. Prose now says **editorial role**. Identifiers say
  **reviewer**, because `role` alone would also cover the task agent and the absent author,
  who are roles in `SKILL.md`'s own cast.

  | was | now |
  | --- | --- |
  | `verdicts.py --angles` | `verdicts.py --reviewers` |
  | the packet's `## ANGLE FILES` section | `## REVIEWER FILES` |
  | "the four angles", "from this angle" | "the four editorial roles", "from this role" |

  A saved dispatch packet with an `## ANGLE FILES` heading now fails `run_context.py --check`
  with that section reported missing, and a scripted `--angles` invocation fails at argument
  parsing. Both are the intended failure: no alias is accepted, because a script whose own
  rule is that nothing degrades quietly should not answer to a name it no longer uses.

- **`sweep` is not a term. Stage 7b is APPLY.** Every canonical naming site already said so —
  `SKILL.md`'s pipeline diagram, its stage table, and the reference filename `apply.md`.
  `sweep` was a synonym that outlived `sweep.py`, the module now called `census.py`. Retired
  at 12 sites; the 5 plain-English uses ("do NOT sweep the file") are kept and are no longer
  ambiguous, there being no name left to collide with.

### Fixed

- **`evals/generator_split.py` runs again.** It did `import sweep` against a directory with no
  `sweep.py`, so the script could not start; the five attributes it uses are in `census.py`.
  `evals/grade_hazards.py` cited the same dead module.

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
