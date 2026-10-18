"""The line-ending measure a proof checks against an untouched sibling.

Git may normalize the stored baseline's endings, so a file's endings are
measured against a sibling in the working tree rather than against its own
baseline. Whether the code survived is the page's read's question -- see
`reading.proof`.
"""


def dominant_ending(text: str) -> str:
    """Which line ending this text mostly uses: "crlf", "lf" or "none"."""
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    if crlf == 0 and lf == 0:
        return "none"
    return "crlf" if crlf >= lf else "lf"
