"""Put `evals/` on the path for the harness tests.

The harness is not a shipped package and is not installed -- `evals/` is
`testing`'s tree and never leaves this repo -- so its modules are imported from
where they live rather than from the venv.
"""

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]

sys.path.insert(0, str(REPO / "evals"))
