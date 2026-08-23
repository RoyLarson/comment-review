// Fx.cs -- one small type.

namespace Fx;

/// <summary>Adds two numbers.</summary>
public static class Maths
{
    /// <summary>Returns the sum of a and b.</summary>
    public static int Add(int a, int b)
    {
        return a + b;  // a trailing comment
    }

    // A verbatim string takes no escapes, which is why `@"` is declared
    // as a spanning quote.
    public const string Url = @"http://example.com/not-a-comment";
}
