# `concordance` -- what a machine settles before a role reads, and what it only points at

Written 2026-09-07, after two sessions in one day proposed extracting a mechanical half of the
review that this package already is. The division below is stated per finding, because stating
it once in `CLAUDE.md` as *"the resolution a reviewer would otherwise do by hand"* was not
enough to stop either proposal.

## 1. What this package is for

It is stage 3. A reviewer reads prose against code, and everything a symbol table, a filesystem
and a regex can settle first is settled here and attached to the paragraph, so the role spends
its reading on the claim rather than on the lookup.

**Read together, the modules build an index**, which is what the package name has been saying
all along -- a concordance is an index of where terms occur. Roy, 2026-09-07, seeing the four
as one thing: *"all three files in concordance work as a thing that together builds an index.
annotate.py seems to be getting the keys for the index the other two are cross-references for
the keys to documents and keys to code."*

| module | its part of the index |
| --- | --- |
| `names.py` | what may be a key |
| `annotate.py` | the keys, taken from prose |
| `code_names.py` | key to code |
| `referrers.py` | key to documents |

The two cross-references are asymmetric, and the return types show it. `code_names` gives a set
of names, so the only question it answers is whether a key exists somewhere in the code.
`referrers` gives the files that name a token, so it locates. Nothing in the package maps a name
to a position, which is why an unresolved symbol note carries a single state while a path note
separates absent from untracked: the filesystem offers two answers and the name corpus offers
one bit.

## 2. What it may import, and what may import it

A leaf. Nothing above it may be imported by it, and `binder`, `desk` and the write end all reach
down to it rather than across to each other. `flows/annotations_for.py` is `annotate`'s one
caller, over every paragraph a gather carried; the repeated-literal pass lives there because it
needs the whole set rather than one paragraph.

## 3. Each module: what it owns

| module | owns |
| --- | --- |
| `annotate.py` | the annotations one paragraph carries, resolved where a machine can |
| `code_names.py` | every name the tree defines, harvested from the `ast` -- the corpus an obituary is resolved against |
| `names.py` | `SYMBOLISH`, the predicate for what counts as a name, shared by the two sides of one lookup |
| `referrers.py` | stage 3 inbound: which tracked files name the files under review |

`names.py` belongs to neither of its two readers on purpose. `annotate` asks it of a backticked
token in prose, to decide whether that token is worth looking up; `code_names` asks it of a
string in the tree, to decide whether to index one. If the two disagreed about the shape of a
name, a key could never hit.

`code_names.py` carries the reason a naive corpus cannot work: one built from raw text contains
the comments being checked, so every obituary resolves against itself and the check passes
always.

## 4. The three kinds of finding, and who does which

This is the division. It is three ways, not two.

### A machine resolves it outright

Two kinds, and both are handed over marked as candidates rather than as verdicts.

| the claim | what resolves it | what the role gets |
| --- | --- | --- |
| a backticked token names a symbol | the token against `code_names`' corpus, head segment only | `UNRESOLVED symbol`, and the note says `CANDIDATE` |
| the prose cites a path | the path against the git index, then against the disk | `UNRESOLVED path`, or `UNVERIFIABLE path` where it is on disk but untracked |

The head segment must resolve rather than any segment, because matching any part lets
`Thing.meta` pass on `meta` -- an obituary hiding behind a common attribute name. And a candidate
is a candidate because the resolver holds only the namespaces it was handed: a backticked token
can name a config key, a record field or an `API` payload.

### A machine only notices, and says so in the imperative

The larger half. `annotate` matches the shape of a claim and then tells the reader to go and
check it, because the checking is not something a regex can do.

| annotation | what the pattern matches | the note handed to the role |
| --- | --- | --- |
| `counted` | a number or quantifier before a population -- callers, files, tests, readers | `RE-COUNT, and name the population` |
| `coverage-claim` | guarded by, pinned by, the only call site, write-only, single source of truth | `CHECK the guard exists AND can fail, exemptions OFF` |
| `forbids-a-literal` | never, must not, do not, near a number or a backticked token | `GREP this file for what it forbids` |
| `narrative-in-docstring` | a narrative line in a docstring, command lines skipped | the label and the line |

Read the verbs. The machine does not count, does not check the guard, does not grep. It knows
the sentence is the kind of sentence that has a truth value, and it knows the reader would
otherwise walk past it.

### A machine cannot notice it at all

What is left is the two heavy roles, and it is why they are heavy.

| role | the question | why no pattern reaches it |
| --- | --- | --- |
| `ownership-context` | is this statement about this code, and where does it belong | placement is a relation between a sentence and a whole tree; nothing in the sentence marks it |
| `block-context` | is it still a true statement about the code it sits with | a claim with no regex shape still has a truth value, and most claims have no shape |

## 5. Why it is this way

Roy, 2026-09-07: *"while True that the script can do better, without telling an agent to
specifically look for them they go unnoticed in so many places which even with /code-review
max."*

That is the load-bearing sentence for the whole package. The point of `annotate` is not that it
resolves things faster than a reviewer would. It is that a reviewer reading a file top to bottom
does not stop at *"the only caller"* -- the sentence reads as prose rather than as an assertion,
and a general-purpose code review at its highest setting walks past it too. The annotation is
what converts a sentence into a question the role is obliged to answer.

So the package is a pointing device first and a resolver second, and the two roles it points for
are doing the part that has no pattern: placement, and truth.

## 6. What is provisional

Every annotation is a candidate, including the two that resolve. A role that treats
`UNRESOLVED symbol` as a verdict rather than as a place to look will file findings against
config keys and payload fields.

`referrers.py` is read-only and always exits 0, and every line it prints is a candidate in the
same sense: a file that names a token is a file to read, and stays outside what an instruction
may target. It is the half that decides the reference-only list, and without it that list is
assembled from memory.

What this file does not settle: whether any of the noticing patterns belongs in a hook at write
time rather than in stage 3. The patterns here run over a paragraph the gather has already
built, with the code beside it; a hook sees the text of one write and nothing else. That is a
real difference and nobody has measured whether it matters.

### The second subject, and where it is going

Under the index frame above, `annotate` carries two subjects. Two of its annotation kinds
produce a key and have somewhere to resolve it; the other four produce no key and resolve
against nothing.

| | key | cross-reference |
| --- | --- | --- |
| `names-a-symbol`, `cites-a-path` | yes | `code_names`, the git index |
| `counted`, `coverage-claim`, `forbids-a-literal`, `narrative-in-docstring` | none | none |

Those four classify a paragraph and hand the reader an imperative. They are not concordance
work, and they are the shape this repo has met three times before, where one category was
quietly doing a second job.

The intent, ruled by Roy on 2026-09-07, is that the second job leaves rather than being given a
name of its own. A machine context reads the paragraphs, raises a `query` where it finds a claim
it cannot settle, and marks `clean` where it finds none; those marks pass to the agent contexts
the way any role's marks do.

It needs no new word, and that is the test it passed. `SKILL.md` defines a `query` as unsettled
-- resolve it or escalate it -- and names no party, so a machine raising one is the same word at
the same sense. `suspicion` was considered and refused, because it imports a prior the code does
not hold: `coverage-claim` fires on a guard whether or not that guard exists.

Two questions are open and are Roy's. Whether a machine-raised query gates its paragraph, since
a query makes every other instruction on that sentence wait, and inheriting that would be a
change in force rather than in bookkeeping. And the name, which waits on
[`the-roles-are-named-for-what-they-read`](../../../TODO/the-roles-are-named-for-what-they-read.md),
because the other four contexts are named for the scope they read rather than for the reader.

The work is
[`a-machine-context-raises-query-and-clean`](../../../TODO/a-machine-context-raises-query-and-clean.md),
eight tasks, and it is a later scope than the release this was written during.
