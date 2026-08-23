// fx.ts -- one small module.

/**
 * Returns the sum of a and b.
 */
export function add(a: number, b: number): number {
  return a + b;  // a trailing comment
}

/** A type alias carries documentation too. */
export type Sum = (a: number, b: number) => number;

export const url = `http://example.com/not-a-comment`;
