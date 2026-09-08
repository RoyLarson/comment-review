# `binder` -- the read end: what a file says, and what every place on it is called

Written 2026-09-07. It exists because a rule governing three stages was filed four times in one
evening and superseded three, and every wrong version rested on a guess about what one of these
containers holds. The guesses are cheap to settle by reading and were never written down.

## 1. What this package is for

It turns a file into a page: every line classified, every place on it named, and the prose tied
to the place it sits in. Then it gathers pages into a binder, which is what the rest of the run
is handed.

## 2. What it may import, and what may import it

The read end. It reaches down to a leaf -- `machine`, `reading`, `concordance` -- and not across
to `desk` or the write end. A flow builds it and passes it on.

## 3. Each module: what it owns

| module | owns |
| --- | --- |
| `page.py` | one file: its paragraphs in order among the code they sit with, and its cues |
| `binder.py` | the pages in scope, with the root they were read from |
| `addresses.py` | resolving an address to paragraphs, and what a paragraph's address is |

## 4. What each container holds

This is the section whose absence cost an evening.

### A page holds every place, absent and present

A `Page` carries its path as the repo names it, its text exactly as it reads, the `sha` it was
read at, its paragraphs in order, and its `cues` -- **every place on the page, filled or not**.

That last part is the load-bearing fact. A place holding no prose is still a place, still
addressed, and still citable, which is what makes an `add` possible: the finding is that a
constraint exists in code and nowhere in prose, so it is about an empty interval and needs that
interval to have a name.

So a page can distinguish **a place that does not exist** from **a place that exists and holds
no prose**. Nothing else in the system can, and that is why an address is verified against a
page -- `decision-log.md Process: #111`.

The `sha` is received from the read, never taken here. A sha this module took for itself would
be asking whether the text equals itself.

### A binder holds pages, and the one on disk is redacted

`bind(pages, read_from)` returns a `Binder` carrying the pages and `read_from`, which is
`{root, revise}` -- the tree the pages came from, and `0` for the original or the revise's own
number otherwise.

**The binder written to disk carries only the places holding prose.** It is redacted, and it
always will be: the empty places are the large majority of rows, and a role is handed prose to
rule on. A consequence follows, and it is the one that misled every draft of the address rule --
**a redacted binder cannot tell an absent place from a place that does not exist**, so it is the
wrong thing to verify an address against, at every stage.

Today the choice of representation is made inside `bind`, through an `absent` parameter that
picks the page type. `Process: #107` rules that out: `bind` builds one representation, and the
flow that writes a binder out decides what is emitted. The redaction stays; where it is decided
moves.

**And a binder will hold more than pages.** Roy, 2026-09-07: *"It will contain indexes and
glossaries and references in the future so that is not necessary and it was never the design
intent."* That is why nothing downstream takes a binder in order to reach a page.

### An address is a path and a cue, and the cue is an ordinal

`addresses.resolve(address, paragraphs)` answers which paragraphs an address names.
`series_of` and `stable` say what a paragraph's own address is. `handed` and `unaddressed`
separate what can be ruled on from what cannot.

An address is not a line number and never was. `docs/addressing.md` is the source for the form
and for what the line-numbered version got wrong.

## 5. Why it is this way

| the constraint | what produced it |
| --- | --- |
| a page carries empty places | an `add` cites the interval where prose is missing, so the interval needs a name |
| the sha is received, not taken | a sha derived here would compare the text with itself |
| the emitted binder is redacted | a role is handed prose to rule on, and the empty places are most of the rows |
| the flow decides the emission | `Process: #107` -- the page does not know what it is being asked for, the flow does |
| a binder is not a path to a page | it will carry indexes, glossaries and references, and the write end takes neither |

## 6. What is provisional

`bind` still takes `absent` and still chooses the page type. `Process: #107` is ruled and not
implemented, and until it lands the redaction is decided in the wrong place and
`flows/fan_out.py` still spells both page types in one union.

What this file does not settle: whether a binder gains a name-to-location index when it gains
its other contents. Today nothing in the read end maps a name to a position -- `concordance`
answers whether a name exists, and `referrers` answers which files mention it, and neither
locates. See [`../concordance/README.md`](../concordance/README.md).
