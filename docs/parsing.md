# How the census gets structure

What the skill must do itself, what it may borrow from the machine it is
running on, and what it must refuse to do. The measured history behind the
current shape is `evidence/tier-measurement.md`.

## Two axes, not one ladder

Finding prose and explaining prose are different jobs with different failure
modes, and conflating them produced the wrong design twice. Keep them apart:

```
1. FIND the prose        -- REQUIRED. Deterministic. Ships with the skill.
     .py, .pyi           -> the Python reader
     .rs                 -> the Rust reader
     other source file   -> listed as freeform, unopened
     any other file      -> a named one stops the gather; a walked one is reported

2. ENRICH what was found -- OPTIONAL. Additive. Never required.
     LSP documentSymbol  -> the anchor of each block
     LSP workspaceSymbol -> liveness for `names-a-symbol`
     no server           -> declared per file; those verdicts stay CANDIDATES
```

! **Axis 2 cannot substitute for axis 1, and the trap is worth naming because
it is the obvious design.** "Python uses our parser, other languages use the
LSP" sounds like a clean fallback and does not work: **LSP returns no
comments.** The harness exposes nine operations -- `goToDefinition`,
`findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`,
`goToImplementation` and three call-hierarchy calls -- and none of them return
prose. `textDocument/semanticTokens` and `textDocument/foldingRange`, the two
that would, are not among them. On a Go file a language server will report
`func F` at line 4 while nothing has said there is a comment at line 2 to
attach to it: an anchor with nothing anchored to it.

**So the order is a dependency, not a preference.** A block must be found
before anything can anchor it.

* **Axis 2 is pure upside precisely because it is additive.** With a server you
gain anchors and cross-language liveness; without one you lose nothing you
had. That is only safe because absence is *declared* -- a probe against a `.ts`
file with no server returned `No LSP server available for file type: .ts`. A
capability that changes coverage silently is the thing that got libcst removed;
one that announces its own absence can be reported per file and reasoned about.

* **Liveness is the bigger prize, not anchoring.** `names-a-symbol` is
harvested from the Python AST today and was measured as one of the weakest
detectors outside the codebase it grew in. `workspaceSymbol` answers "does this
name exist in this workspace" for every language at once -- the same check
without the language lock.

## A language with no reader is freeform

!! **A file in a language with no reader holds no paragraphs.** The gather lists a
source file of that kind as freeform and never opens it. It has no places, no
marks and no proof: `prove_unchanged` answers `UNCHECKED`. No tool works out its
structure, and no address is claimed for it.

## Ruff's parser cannot be reused, and the reason generalises

`ruff_python_parser` is hand-written recursive descent with the Python grammar
baked into its control flow. There is no generic engine underneath to retarget,
it emits Python-specific AST types, and it has no stable Python binding --
ruff ships as a CLI and publishes its crates for internal use. Retargeting it
means writing a new recursive-descent parser per language, which is what a
tree-sitter grammar already is.

! The reusable idea in ruff is not the parser but `ruff_python_trivia`'s
comment-attachment logic -- leading, trailing, dangling -- which is the ANCHOR
problem stated as an algorithm. Worth reading if anchoring is reopened. It is
Python-specific too.

* **Anchoring is a CONVENTION, not a parse result.** Even a perfect CST hands
comments back as siblings; "which declaration does this belong to" is a rule
someone writes. tree-sitter does not solve it, and neither does
`documentSymbol`. Any claim that a parser "gives us anchors" is really a
claim about an attachment rule bolted on top, and should be judged as one.

## The bar for replacing AXIS 1

!! **THIS BAR IS ABOUT FINDING PROSE, AND ONLY A PARSER CAN FAIL IT.** A
candidate for axis 1 reads the file and returns the blocks; adopting one that
returns fewer than today's loses prose nobody then reviews.
`evidence/tier-measurement.md` set the requirement: **adopt a replacement only
if it misses ZERO blocks** -- measured there, libcst missed **13** that the
stdlib reader found. Ownership is worth nothing if coverage is not total.

! A REQUIREMENT, not a number to beat. Blocks are counted in whole numbers and
nothing lies below zero, so there is no margin to compete on -- a candidate
meets it or does not.

! **It says nothing about axis 2, which cannot fail it.** An LSP returns no
comments, so it finds no blocks and can lose none. Its bar is the one stated
above: additive, never required, and DECLARED PER FILE, so a run with a server
and a run without are told apart rather than compared. Asking "how many blocks
did the LSP miss" is asking a question it was never in a position to answer.

! **An eval that uses LSP must record which servers answered.** Availability
differs per machine, so a run with a server and one without produce different
liveness results from identical input -- the same discipline the corpus manifest
applies to refs.

## What a PAGE is FOR, and where it stops

!! **IT CLASSIFIES LINES, AND THE BAR IS NOT A PARSER.** Roy, 2026-08-18, when this
was still named for a syntax tree: *"without a full cst system for every language -
this is as good of a pCST for what we need."* ! The NAME is retired -- Roy,
2026-08-20: *"it never really fit"* -- and the bound it describes is unchanged.

What the tool asks of it is bounded, and every question fits inside a reader:

- **where prose sits** -- comment runs, docstrings, trailing comments
- **where prose is MISSING** -- the intervals between two lines of code
- **which lines are CODE**, which is what `addresser.py` numbers a place against

None of those needs a grammar. Which declaration a run documents comes from the
reader too: it gives a run above a declaring line that line. What a grammar would
add is a reading of the prose's subject, which position cannot give -- that is a
reviewer's judgement, or an `LSP documentSymbol` where stage 1.7's probe found a
server.

### A new language is a new reader

A language joins with a reader package and a definition file of its own. That is
axis 1 and is measured the same way: it must find every block the file holds. A
parser proposed to REPLACE a reader meets the zero-missed bar above. An LSP or a
symbol index is axis 2 and meets neither -- it is additive, declared per file, and
never required. In every case, bring the corpus that shows it.
