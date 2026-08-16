"""Find public Python repositories whose history is heavily assistant-authored.

    python scripts/find_llm_repos.py [--pages N] [--min-hits N]

The corpus set has an empty cell. Its four public corpora are all pre-assistant
and heavily reviewed, so "curated" and "human-written" are collinear in it and no
measurement can tell the two apart. The reference corpus is the opposite corner --
solo and essentially entirely assistant-written -- which leaves the interesting
comparison unavailable: assistant-written code that a review culture did see.

This looks for candidates to fill it.

⚠ A trailer count is a WEAK proxy and this only produces candidates. It says an
assistant touched a commit, not that it wrote the prose, and a repo with many
such commits may still be mostly hand-written. Anything it returns is a shortlist
for reading, not a corpus.

⚠ GitHub commit search has no `language:` qualifier -- passing one matches the
literal text and returns nonsense. Language is a property of the REPO, so the
search finds commits and a second pass filters the repos they came from.

Unauthenticated search allows ~10 requests/minute, so this is deliberately small
and slow rather than thorough. Set GITHUB_TOKEN to go faster.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

API = "https://api.github.com"
TRAILER = '"Co-authored-by: Claude"'


def get(path: str, **params) -> dict:
    """One GitHub API call, retried once past a rate limit, never raising."""
    url = f"{API}{path}?{urllib.parse.urlencode(params)}" if params else f"{API}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "comment-review-corpus",
    }
    if tok := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {tok}"
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < 2:
                time.sleep(20)  # secondary rate limit; unauthenticated is ~10/min
                continue
            return {"_error": f"HTTP {e.code}"}
        except Exception as e:  # noqa: BLE001 - a survey must not die on one call
            return {"_error": type(e).__name__}
    return {"_error": "retries exhausted"}


def main() -> int:
    """Shortlist public Python repos whose history carries assistant trailers."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pages", type=int, default=3, help="commit-search pages")
    ap.add_argument("--min-hits", type=int, default=2, help="trailer commits per repo")
    args = ap.parse_args()

    hits: Counter[str] = Counter()
    for page in range(1, args.pages + 1):
        d = get(
            "/search/commits", q=TRAILER, per_page=100, page=page, sort="committer-date"
        )
        if err := d.get("_error"):
            print(f"  search page {page}: {err}")
            break
        items = d.get("items", [])
        for it in items:
            hits[it["repository"]["full_name"]] += 1
        print(f"  page {page}: {len(items)} commits, {len(hits)} distinct repos")
        if len(items) < 100:
            break
        time.sleep(7)

    shortlist = [r for r, n in hits.most_common() if n >= args.min_hits]
    print(
        f"\n{len(shortlist)} repos with >= {args.min_hits} assistant-trailer commits\n"
    )

    print(f"{'repo':45s} {'hits':>4s} {'lang':10s} {'KB':>8s} {'stars':>6s}")
    keep = []
    for name in shortlist[:25]:
        meta = get(f"/repos/{name}")
        if meta.get("_error"):
            continue
        lang = meta.get("language") or "-"
        print(
            f"{name[:45]:45s} {hits[name]:4d} {lang[:10]:10s} "
            f"{meta.get('size', 0):8d} {meta.get('stargazers_count', 0):6d}"
        )
        if lang == "Python" and 200 <= meta.get("size", 0) <= 200_000:
            keep.append((name, hits[name], meta.get("stargazers_count", 0)))
        time.sleep(1)

    print(f"\nPython candidates, sized for a pass ({len(keep)}):")
    for name, n, stars in keep:
        print(f"  {name}  ({n} trailer commits, {stars} stars)")
    print(
        "\nA trailer count is a proxy for INVOLVEMENT, not authorship. Read a few\n"
        "blocks before adding any of these to corpora.toml -- the cell they fill is\n"
        "'assistant-written AND reviewed', and a repo nobody reviewed does not fill it."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
