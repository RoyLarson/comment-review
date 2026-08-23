// fx.cpp -- one small translation unit.

#include <string>

/** Add returns the sum of a and b. */
int add(int a, int b) {
    return a + b;  // a trailing comment
}

// A raw string literal takes no escapes and may cross lines, which is
// why `R"` is declared as a spanning quote rather than an ordinary one.
const char *pattern = R"(http://example.com/not-a-comment)";
