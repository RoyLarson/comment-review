// Fx.kt -- one small file.

package fx

/** Returns the sum of a and b. */
fun add(a: Int, b: Int): Int {
    return a + b  // a trailing comment
}

/** A holder for two numbers. */
data class Pair2(val a: Int, val b: Int)

// `data` alone is a soft keyword and this is an assignment, not a
// declaration -- which is why the row lists `data class`, two words.
val data = listOf(1, 2)

val url = "http://example.com/not-a-comment"
