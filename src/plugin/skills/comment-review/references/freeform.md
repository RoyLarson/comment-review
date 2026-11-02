# Setting a freeform file

A freeform file is a source file no reader claims. It has no addresses and no proof, so the text
you write is the text the author reads. Everyone who composes or sets a replacement follows this
sheet.

## Composing a replacement

- **One full replacement per comment.** A replacement is the whole comment, first line to last,
  holding every edit made to it.
- **Read it whole.** Each paragraph stays a whole proposition: every later clause agrees with the
  changed clause, every contrast word keeps its contrast, and every pronoun keeps its antecedent.
- **Frame it for the file.** Every line carries the comment's own indent and its leader, wrapped
  lines included. Take both from the comment as it stands, in the file's own tabs or spaces.
- **Wrap it to the style sheet's width.** A longer replacement re-wraps its whole comment and
  nothing beyond it. A path or a citation stays whole on one line; report a line it pushes past
  the width.
- **Hold it to the cap.** A comment run directly above a declaration, in a language that documents
  a declaration by the comment above it, is that declaration's documentation, and the cap passes
  over it.
- **Delete explicitly.** Deleting a whole comment takes an empty replacement, and `current` runs
  through the line ending of its last line. Deleting one sentence takes a replacement holding the
  rest of the comment. A replacement holds only text that belongs in the file.
- **An `add` keeps its anchor.** `current` is the line of code it belongs to, and the replacement
  is that line unchanged with the new comment set beside or above it. A blank line that separated
  two paragraphs stays.
- **A claim inside a string is a code concern.** The string is code, so raise a `query`.

## Setting a replacement

- Set every replacement with the Edit tool, one call per finding, with `replace_all` off.
  `current` is `old_string` and the replacement is `new_string`.
- When `current` matches more than once, add the neighbouring line to both strings, so the match
  stands at `path:line` alone.
- When `current` matches nothing, leave that finding unset and return it with the text standing at
  `path:line`.
- Set an `add` before the `drop` it pairs with.
- Read each comment back after setting it.

## What stays exactly as it is

Each of these is code, whatever it looks like.

- Text shaped like a comment inside a string, a template literal or a heredoc.
- A line ending in a continuation, and the line after it. They stay whole and adjacent.
- The interpreter line and a byte-order mark, byte for byte.
- A directive in a comment: `/*!50000 ... */`, `/// <reference>`, `# shellcheck`, `// +build`, and
  any other comment a compiler, linter or build tool reads.
- JSX text. Prose between two tags is rendered output, and only `{/* ... */}` is a comment there.
- The file's line endings. A replacement takes the endings of the file it lands in.

A C or C++ `//` comment ending in a backslash takes the next line into the comment, so every line
of a replacement there ends on another character.
