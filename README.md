# comment-review

A Claude Code plugin: an **editorial board** for the comments and docstrings a change
touched. Four read-only reviewers walk one prose tree, an editor writes the replacement
text, it is cut to fit, **then** the author approves the exact text that will be written —
and the sweep applies it and proves the executable code byte-identical.

```
project → annotate → find refs → mark → edit → compact → APPROVAL → review
                                          │                  ▲
                                          └──── no cap ──────┘
```

⚠ **Compaction happens BEFORE approval, on purpose.** Approving a full-length comment and
then writing a shorter one is a bait-and-switch: the author ruled on text that never
reached the file. Whatever is approved is what lands, byte for byte.

Comments rot differently from code. Code that stops being true usually breaks a test; a
comment that stops being true just sits there, and the next reader believes it.

## Why

The concept of the project was because I was vibe-coding something that I didn't have time
to do myself. I thought it simple enough to let CLAUDE do it for me. Then CLAUDE made a mess
of the comments, started hallucinating, and I couldn't correct the behaviors because it was
locked into the code comments.

This skill helps verify and clean up comments. I had it tested out on more than my project
to see if it could be used on others that I felt had a high likelihood of few mistakes, but
still might need something that would systematically be able to update the comments and
documentation.

The system is focused tightly around the comments and function/module/package documentation.
Because references to other documentation files are inevitable and the way LLMs work, other
files also end up in the review. Anything that points to something in the code or any place
that comments in the code point to will end up being referenced. This is a limitation -
if the other documentation doesn't have an edge in the connection anymore it might stay undiscovered.

I broke down the comment review into four levels/categories

- Locality - Is it in the right place
- Currency - Does it state what is true/necessary for the code right now
- Functionality - Does the comments and documentation within a function follow from the
  name of the function
- Modularity - Does the documentation cover one set of ideas.

These were the best classifications of comment and documentation errors I could think of.
They each were meant to support from inside-out the structure of comments.
The goals is to make it easier for both LLMs and humans to understand what the code
is doing and improve the accuracy of the comments with relation to the code.
This will find coding mistakes as well because of it.
Little things that no test is looking for will popup in looking for a clarification on
documentation.

## What

The skill judges comments based upon four criteria:

- Locality
  - Is the comment where it is supposed to be or did it drift away from the
    location because of changes.
  - Do the current comments next to code reference the next line(s) of code
    coming up or are they referencing something before.
  - Are the comments properly colocated.
- Currency
  - Does the comment state something specific about what the code is doing now.
    - not past behavior.
    - not future behaviors.
- Functionality
  - Does the function documentation describe what the code does.
    - Is this one function with an appropriate name or is it more than one function.
    - Do the comments indicate the functions use changed over time.
    - Are the comments in the function in the correct order.
- Modularity
  - Is the module/package level documentation appropriate.
    - Does it cover all of the functions and constants that the module exposes.
    - Does the documentation support what the module's state uses are.
    - Is it one set of ideas being discussed in the documentation.

The skill is broken up into eight phases to cover an editorial system.

1) PROJECT DETERMINATION - Language, documentation style, project rules
2) ANNOTATE - Review the current code and comments - determine where the comments and documentation is in the files.
3) FIND REFERENCES - Determine external links to the code comments that might also need updating
4) MARK - Provide appropriate editorial marks to the Annotated comments and documentation to determine what to do

| verdict   | the claim is                 | what you do with it                                                       |
| --------- | ---------------------------- | ------------------------------------------------------------------------- |
| `clean`   | checked-and-verified         | nothing. One angle declining to find anything, **not** a pass             |
| `query`   | unsettled                    | resolve it or escalate it. It blocks every other verdict on that sentence |
| `drop`    | true but not worth keeping   | delete the sentence                                                       |
| `correct` | **FALSE**                    | apply the true/false pair. **Always before any `patch`**                  |
| `patch`   | **TRUE**, badly worded       | apply the rewrite                                                         |
| `add`     | missing entirely             | insert the text at the anchor named with it                               |
| `move`    | true, and not code's to hold | extract verbatim to the destination resolved at 1.4                       |
| `split`   | two claims in one block      | re-anchor each fragment to the code it is about                           |

5) EDIT - Agent combines the marks to be a correct, truthful, load-bearing comment for the location
6) COMPACT - Only if you want to force the LLMs to keep it short
7) APPROVAL - Agent proposes the change to you - they messed it up for me so I don't trust them to do it twice
8) REVIEW - Double checking that what was wrote still follows the qualities looked for.


## Results

One file per project, chosen by measured prose density, reviewed at full depth. No project
is named — these are calibration measurements for a detector, not a defect report about
anyone's work, and every finding stays with the run that produced it.

| Projects | Comment blocks | Lines reviewed | Findings | Worth acting on immediately | Per 100 lines |
| -------- | -------------- | -------------- | -------- | --------------------------- | ------------- |
| 7        | 339            | 6,736          | 97       | **27**                      | **0.40**      |

Roughly **one comment block in twelve** carried something a maintainer would fix, and about
**one finding in four** was worth acting on immediately — the rest were true, minor, or a
matter of taste.

### What generalized, and what did not

The four reading angles carried every high-value finding in every corpus. The mechanical
detectors — path resolution, symbol liveness, counted claims — did not: across the seven
third-party corpora they fired roughly 70 times and produced about two real findings, and
on one corpus they fired zero times while the file still held six genuine defects. They
were fitted to the codebase the tool grew up in.

That is the n-of-1 problem, measured. A rule that fires in one codebase may be about
editing, or it may be about that codebase's house style, and a single corpus cannot tell
them apart.

⚠ **Read these as an upper bound.** One file per project, and the file was chosen for the
highest prose density in the repository — the place most likely to hold something. A random
file would score lower.

## Install

This repository is itself a marketplace, so the plugin can be edited and used in the same
session:

```
claude plugin marketplace add <path-to-this-checkout>
claude plugin install comment-review
```

Installing as a plugin rather than dropping files in a project's `.claude/` is deliberate.
A skill in `.claude/skills` plus agents in `.claude/agents` is **branch-dependent**: switch
the checkout and the agents vanish mid-run, which is how the coupling was found. A plugin
lives outside every project and is available in all of them.

## Layout

| path                      | what                                                                                                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugins/comment-review/` | the plugin — `skills/`, `agents/`, manifests                                                                                                            |
| `docs/`                   | durable guidance: how the census gets structure (`parsing.md`), and the rules for changing the skill itself (`limitations.md`)                          |
| `evidence/`               | why each rule exists: ten probe reports that attacked the design, a genetic search over 28 candidate rewrites, and the triage that ranked what survived |
| `evals/`                  | twelve planted hazards, a grader, and the authorship split                                                                                              |
| `corpora/`                | the MANIFEST of pinned corpora. The trees themselves are fetched, never vendored                                                                        |
| `scripts/`                | `fetch_corpora.py` to materialise them, `find_llm_repos.py` to find more                                                                                |

## The corpora

```
python scripts/fetch_corpora.py --list     # the manifest
python scripts/fetch_corpora.py            # materialise everything missing
```

Nine repositories at pinned refs — seven third-party, plus the two personal projects the
tool was developed against, kept as the over-fitting control. Chosen for **variety of prose
convention**, not popularity, so that Google, numpydoc and Sphinx styles are all exercised
and a rule that only works on one house style has somewhere to fail.

Nothing is vendored. A local corpus becomes a `git worktree` of a repo already on the
machine; a public one is a clone at a tag, sparse where the manifest says so. This
repository carries names, sources and refs — not other people's code.

⚠ **Pin every corpus.** A moving corpus makes a regression indistinguishable from the
corpus having changed underneath the measurement, which cost a full day's comparison when
the reference repository advanced mid-run.

## Grading

Grade a run from its **diff**, never from its report. Measured: one graded run had
fabricated five of its seven reviewer reports and did not notice until asked to grade
itself; self-certified `CONFIRMED` ran at 97% across 298 findings — a label that two runs
in three thousand disagree with does not discriminate.

```
python evals/grade_hazards.py <worktree> [<worktree> ...]
```

⚠ It reports `NEEDS-EYES` where it has no signal. Two of the twelve hazards are positional
or leave true prose standing, so no text probe can separate a correct repair from an
ignored one — and a check that cannot see a defect must not report it clean.

## Known gaps

### The census reads eleven languages, but only lexically

The four reading angles are language-neutral — they ask whether prose is in the right
place, still true, describes what the code does, and agrees with its neighbours, and none
of that is about syntax. The census underneath them now reads eleven languages from a
data table (`sweep.py --languages`), but at two very different depths: Python gets a real
lexer and AST, everything else gets a comment-syntax record and a hand-rolled string
skipper that is wrong on heredocs, raw strings and template nesting.

⚠ **No comment carries an owner, in any language.** A docstring's owner comes free from
the AST; a `#` run's does not, and nothing infers it — so every locality verdict rests on
a reviewer reading the file. See [docs/parsing.md](docs/parsing.md) for where structure
could come from and what was already tried and rejected.

What is still compiled in rather than detected per project:

| what varies                    | today                  | should be                                                                  |
| ------------------------------ | ---------------------- | -------------------------------------------------------------------------- |
| how prose names a symbol       | `` `backticks` `` only | whichever the codebase actually uses — measured from the tree, not assumed |
| what a citable path looks like | a fixed suffix list    | the extensions present in the repo                                         |
| what an annotation can carry   | not modelled           | e.g. PEP 727 `Doc()`, JSDoc tags, doc attributes                           |
| Markdown and reStructuredText  | no record at all       | prose files are where cited documentation actually lives                   |

The quoting convention is the sharpest case, because it is **not** a language property: two
Python projects in the corpus disagreed with each other about it, and on one of them the
three best symbol findings were invisible to the detector for that reason alone. Sampling
the repository and picking the convention it actually uses is strictly better than any
default. Missing this made the census silently under-report — on one file it censused 3 of
8 prose blocks and still reported the file covered, which is worse than reporting nothing.

### Smaller, also measured

- There is **no verdict for an executable example** — a doctest, a `@example`, a README
  snippet under test. Its expected output can be *wrong* in a way that is a test failure
  rather than a wording problem, and the reviewer has no vocabulary for saying so.
- The docstring-format rule, read literally, condemns every numpydoc `Notes` section. A
  format rule has to come from the project's own convention, which is the same fix as above.
- A **sparse checkout** is indistinguishable from a complete one, so liveness checks against
  the working tree manufacture obituaries. `git grep <pattern> HEAD` is the fix.
- Roughly half the skill is inert on a codebase with no line comments at all.

## Contributing

The most useful contribution is **a corpus in a language that is not Python**, plus whatever
the census needs in order to read it. That is the fastest way to find out which of these
rules are about editing and which are about Python — a question one language cannot answer
about itself.

## License

MIT.
