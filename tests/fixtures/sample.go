// Package fx does one thing.
// This is the package doc comment.
package fx

// Add returns the sum of a and b.
// It is exported, so this run is its documentation.
// A third line, to exceed a cap of two.
func Add(a, b int) int {
	return a + b // a trailing comment
}

// An orphan run that documents nothing, because a blank line
// and then more blank lines follow it.

var url = "http://example.com/not-a-comment"

// A RAW string holds the same marker and takes no escapes.
var raw = `http://example.com/also-not-a-comment`
