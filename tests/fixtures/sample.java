// Fx.java -- one small class.

package fx;

/** Small arithmetic helpers. */
public final class Fx {

    /** Returns the sum of a and b. */
    public static int add(int a, int b) {
        return a + b;  // a trailing comment
    }

    // `record` is a SOFT keyword: this is an assignment, not a declaration.
    public static final String url = "http://example.com/not-a-comment";
}
