# prove_unchanged fails a file whose multi-line string differs only in line endings

```
Status:   closed
Progress: 2 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-24 (stage 7b refusal reproduced 2026-11-24)
```

## Objective

BUG. `prove_unchanged` reports "executable code DIFFERS (lexical proof)" for a
file nobody changed, whenever the file holds a multi-line string literal that is
not a docstring and its working copy's line endings differ from the committed
blob's. With `core.autocrlf=true` (the Windows default), that is every such
file: git stores LF and checks out CRLF.

Cause: `read_revision_source` (scripts/comment_review/machine/repo.py:147-161)
reads the base with plain `git show <ref>:<path>`, which returns the raw blob
with no end-of-line conversion, while the working side is read from disk. The
tokens of a multi-line non-docstring string include its line endings, so
`"""a\nb\n"""` and `"""a\r\nb\r\n"""` compare as different code. A one-line
string, a docstring and ordinary code all prove fine, so the failure shows up
only on files that have one.

Minimal reproduction (no edit at all):

```
git init -q r && cd r && git config core.autocrlf true
printf '"""Doc."""\n\nS = """a\nb\n"""\n' > m.py
git add m.py && git commit -qm base
printf '"""Doc."""\r\n\r\nS = """a\r\nb\r\n"""\r\n' > m.py   # what a CRLF checkout holds
python <skill>/scripts/comment-review.py prove_unchanged --base HEAD --repo . m.py
# FAIL  m.py: executable code DIFFERS (lexical proof)
```

Grid measured on 0.2.4 (a301e823) across autocrlf true/false and LF/CRLF on each
side: the file above fails exactly when the base blob as `git show` prints it
and the working copy disagree on line endings, and proves when they agree. The
same pair without the `S = """..."""` line proves in all eight combinations.

Effect: stage 7b refuses a page the run did not change in code, and the author
is asked to accept it on the agent's word rather than the proof.

## Tasks

- [-] T1 | read_revision_source deleted; prove_unchanged reads no git blob | 2990793e | Make
      read_revision_source return the base blob with the working-tree line
      endings
- [x] T2 | An unchanged CRLF file with a multi-line string proves | 49fa3a8a | Add
      a regression test: an unchanged CRLF file holding a multi-line string
      proves under core.autocrlf=true
