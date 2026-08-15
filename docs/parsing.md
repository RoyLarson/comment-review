# How the census gets structure

What the skill must do itself, what it may borrow from the machine it is
running on, and what it must refuse to do. The measured history behind the
current shape is `evidence/tier-measurement.md`.

## Two axes, not one ladder

Finding prose and explaining prose are different jobs with different failure
modes, and conflating them produced the wrong design twice. Keep them apart:

```
1. FIND the prose        — REQUIRED. Deterministic. Ships with the skill.
     .py                 → tokenize + ast        tier: tokenized
     suffix in LANGUAGES → lexical scanner       tier: lexical
     unknown suffix      → reported as a GAP

2. ENRICH what was found — OPTIONAL. Additive. Never required.
     LSP documentSymbol  → the owner of each block
     LSP workspaceSymbol → liveness for `names-a-symbol`
     no server           → declared per file; those verdicts stay CANDIDATES
```

⚠ **Axis 2 cannot substitute for axis 1, and the trap is worth naming because
it is the obvious design.** "Python uses our parser, other languages use the
LSP" sounds like a clean fallback and does not work: **LSP returns no
comments.** The harness exposes nine operations — `goToDefinition`,
`findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`,
`goToImplementation` and three call-hierarchy calls — and none of them return
prose. `textDocument/semanticTokens` and `textDocument/foldingRange`, the two
that would, are not among them. On a Go file a language server will report
`func F` at line 4 while nothing has said there is a comment at line 2 to
attach to it: ownership with nothing to own.

**So the order is a dependency, not a preference.** A block must be found
before anything can own it.

⭐ **Axis 2 is pure upside precisely because it is additive.** With a server you
gain ownership and cross-language liveness; without one you lose nothing you
had. That is only safe because absence is *declared* — a probe against a `.ts`
file with no server returned `No LSP server available for file type: .ts`. A
capability that changes coverage silently is the thing that got libcst removed;
one that announces its own absence can be reported per file and reasoned about.

⭐ **Liveness is the bigger prize, not ownership.** `names-a-symbol` is
harvested from the Python AST today and was measured as one of the weakest
detectors outside the codebase it grew in. `workspaceSymbol` answers "does this
name exist in this workspace" for every language at once — the same check
without the language lock.

## The refusal: never improvise a parse

⚠⚠ **When the census meets a language it cannot read, the answer is NOT for an
agent to work out the structure by reading the file.** That is unfalsifiable:
it produces a confident tree with no way to check it and, worse, **no way to
report what it missed**. The governing rule here is that *a block missing from
the census is a block nobody reviews* — it is why a tier that dropped 13 blocks
was deleted despite resolving owners for half the corpus. An improvised parse
cannot even count its own drops. It is also non-deterministic, so two runs
produce different censuses and no corpus measurement compares to another.

This is not hypothetical: it is already what happens for LOCALITY whenever no
owner is recorded, and the census now says so out loud rather than letting a
reviewer's impression read as a resolution. Promoting that to a designed tier
would undo the correction.

**The legitimate move on an unknown language is to propose a `LANGUAGES` row:**

```python
Language("zig", (".zig",), ("//",), doc_line=("///",))
```

Five fields, checkable against the file in hand, deterministic once written,
and it supports that language permanently for everyone instead of for one run.
If the row cannot be written confidently, the honest output is the gap the
census already prints: `no language record for its suffix`.

**Improvising a parse is never the fallback. Declaring the gap is; proposing a
row is the fix.**

⭐ **The refusal has a second instance now, and it is the same shape.** Go and
Ruby attach docs by POSITION, so the lexical tier cannot separate a doc comment
from an ordinary run — and detecting declarations to find out would be the
improvised parse this section refuses. The census marks `doc-kind-unresolved`
and excludes the block from the cap tally instead. Measured 2026-08-15: without
it, a three-line `// Add returns…` run above `func Add` reported `over cap (2): 1`,
and `compact.md` routes on KIND, so the cap would have cut an export doc.

## Not built: a real lexer for other languages

The `lexical` tier fakes string-awareness with a hand-rolled quote skipper that
is wrong on heredocs, raw strings and template nesting. Two candidates, neither
built.

| | gives | cost |
| --- | --- | --- |
| **Pygments** | comment + doc tokens, 598 lexers, string-aware | pure Python, no compiled artifacts |
| tree-sitter | full CST with positions | one compiled grammar per language |
| Semgrep `ast-generic` | normalised AST, ~30 languages | heavy, LGPL |
| ANTLR | grammars, must generate and compile | Java toolchain |

Pygments fits the existing ladder: it upgrades `lexical` → `tokenized` for
every language, replacing `blocks_lexical` and `_strip_strings` rather than
adding a layer. Measured 2026-08-14 across eight languages, it correctly
ignored `"http://x"` in Go, `"// not"` in Rust and a TypeScript backtick
template.

⚠ **Two warts set the real shape of that work.** Rust doc comments are
`Token.Literal.String.Doc`, **not** `Comment` — a naive `t in Comment` filter
drops every `///` and `//!` silently, which is the highest-value prose in the
file. And Haskell block comments arrive as three fragments (`{-`, `block`,
`-}`) needing a merge whose rule may differ per lexer. Both are silent-drop
failures of exactly the kind that retired libcst, so **a per-language fixture
test is part of the work, not polish.**

### Ruff's parser cannot be reused, and the reason generalises

`ruff_python_parser` is hand-written recursive descent with the Python grammar
baked into its control flow. There is no generic engine underneath to retarget,
it emits Python-specific AST types, and it has no stable Python binding —
ruff ships as a CLI and publishes its crates for internal use. Retargeting it
means writing a new recursive-descent parser per language, which is what a
tree-sitter grammar already is.

⚠ The reusable idea in ruff is not the parser but `ruff_python_trivia`'s
comment-attachment logic — leading, trailing, dangling — which is the OWNERSHIP
problem stated as an algorithm. Worth reading if ownership is reopened. It is
Python-specific too.

⭐ **Ownership is a CONVENTION, not a parse result.** Even a perfect CST hands
comments back as siblings; "which declaration does this belong to" is a rule
someone writes. tree-sitter does not solve it, and neither does
`documentSymbol`. Any claim that a parser "gives us ownership" is really a
claim about an attachment rule bolted on top, and should be judged as one.

## The bar for building any of this

`evidence/tier-measurement.md` set it: **adopt a source of structure only if it
misses ZERO blocks.** Ownership is worth nothing if coverage is not total.

⚠ **And nothing has been measured on a non-Python corpus yet**, so all of this
would improve a tier whose value is unproven. The README's Contributing note
names the higher-value step first: a corpus in another language. That
measurement tells you whether the upgrade is worth building before it is built.

⚠ **An eval that uses LSP must record which servers answered.** Availability
differs per machine, so a run with a server and one without produce different
liveness results from identical input — the same discipline the corpus manifest
applies to refs.
