// fx.js -- one small module.

/**
 * Returns the sum of a and b.
 */
export function add(a, b) {
  return a + b;  // a trailing comment
}

// A template literal crosses lines, which is why the backtick is both
// an ordinary quote and a spanning one.
export const url = `http://example.com/not-a-comment`;
