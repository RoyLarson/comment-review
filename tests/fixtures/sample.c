/* fx.c -- one small translation unit. */

#include <stddef.h>

/* Add returns the sum of a and b. C gets no `a` series: the
   declaration opens with a return type, so nothing names it. */
int add(int a, int b) {
    return a + b; /* a trailing comment */
}

const char *url = "http://example.com/not-a-comment";
