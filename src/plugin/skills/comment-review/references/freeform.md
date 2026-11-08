# A freeform file

A freeform file is a source file no reader claims. It has no page and no address, so `mark`,
`addresses` and `proof` take no path in it. The text in your copy is the text the copy chief reads.
Everyone who edits a copy or a draft follows this sheet.

When your packet names no brief, this sheet is your contract. Where your role file names a mark, an
edit copy or `check`, read this sheet's finding, copy and return.

## Reviewing a file

1. **Copy the file** into `FREEFORM DIR`, keeping its path, from `REPO ROOT`. Your citations resolve against the file you copied.
2. **List every comment in the file by line**, before you judge any. This list is `swept`.
3. **Rule on each comment** with your role's remit. A comment with nothing to report takes no
   finding, and `swept` records that you read it.
4. **Edit your copy.** Each change is the one full text of that comment.
5. **File each finding** in `FREEFORM DIR/findings.json`. The diff of your copy supplies the text,
   so a finding carries why, and never the text.
6. **Return the paths** of `findings.json` and your copies, with one line per file:
   `<path>: N swept, M raised`.

```json
{ "role": "block-context",
  "files": [
    { "path": "redacted_pkg/rates.js",
      "swept": [12, 40, 88],
      "findings": [
        { "instruction": "correct",
          "at": "redacted_pkg/rates.js:40",
          "reason": "the limit is read from settings and is 100",
          "source": [ { "cite": "redacted_pkg/settings.js:7",
                        "verbatim": "const LIMIT = 100;" } ] } ] } ] }
```

| field | what it carries |
| --- | --- |
| `path` | the file, as your binder lists it |
| `swept` | the line of every comment in the file |
| `instruction` | what you did to the comment, below |
| `at` | `path:line` in the file you copied: the comment's first line, or for an `add` the line of code it belongs to |
| `reason` | what you derived |
| `source` | `{ "cite": "file:line", "verbatim": "the text at it", "ran": "the command" }`, one per place you examined |

| instruction | use it when |
| --- | --- |
| `correct` | a claim is false. `source` carries the line that settles it |
| `patch` | the claim is true and the wording is not. No source is needed |
| `drop` | the comment or a sentence in it is not needed, true or false |
| `add` | a comment is missing. Where a comment already stands, it is a `patch` of that comment |
| `query` | you cannot rule, below |

- **One finding per comment.** A comment with several edits takes one finding, and it is a `correct`
  when any of those edits is.
- **Every finding but a `query` has its change in your copy, and every change has its finding.**
- **A `query` changes nothing in your copy.** It carries `shape`, `attempted` and `settles`: the
  shape, the check you attempted and what would settle it. `shape` is one of these:
  - `outside-my-role` -- the comment's subject lies outside your remit.
  - `unable-to-determine` -- you looked and the evidence does not decide it.
  - `human-review-necessary` -- only the author's intent decides it.
- **A code concern is a `query`** of shape `human-review-necessary`, with `settles` reading
  `code concern`. A claim inside a string is one, because the string is code.
- **A relocation is two findings:** an `add` at the destination and a `drop` at the origin, each
  naming the other in its `reason`. When one end is on a page, that end is a mark: `mark` refuses a
  `--to` in a freeform file.

## Composing a change

- **One full text per comment.** The comment reads whole, first line to last, holding every edit
  made to it.
- **Read it whole.** Each paragraph stays a whole proposition: every later clause agrees with the
  changed clause, every contrast word keeps its contrast, and every pronoun keeps its antecedent.
- **Frame it for the file.** Every line carries the comment's own indent and its leader, wrapped
  lines included. Take both from the comment as it stands, in the file's own tabs or spaces.
- **Wrap it to the style sheet's width.** A longer comment re-wraps as a whole and nothing beyond it
  moves. A path or a citation stays whole on one line; report a line it pushes past the width.
- **Hold it to the cap.** A comment run directly above a declaration, in a language that documents
  a declaration by the comment above it, is that declaration's documentation, and the cap passes
  over it.
- **Delete explicitly.** Deleting a whole comment removes it through the line ending of its last
  line. A blank line that separated two paragraphs stays.
- **An `add` sits beside or above its code,** and that line of code stays unchanged.

## Making the edit

- Make every edit with the Edit tool, one call per comment, with `replace_all` off.
- When the old text matches more than once, add the neighbouring line to both strings, so the match
  stands at one place alone.
- Make an `add` before the `drop` it pairs with.
- Read each comment back after editing it.

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
