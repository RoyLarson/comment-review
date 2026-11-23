"""What the machine says: the checkout, the filesystem, and text read off disk.

    repo         git, and reading and writing a file's exact bytes
    json_object  text as a JSON object, or why it is not one
    digests      the SHA-256 of bytes a caller supplies

The exception tuples are not here: `exceptions`, like `constants` and
`differences`, is a leaf at the package root.

! The name is provisional. `io` was the obvious word and collides: an `io`
package would shadow the stdlib name ambiguously for any reader.
"""
