"""Where the tests find the shipped scripts and their fixtures.

`unittest discover -s tests` puts this directory on `sys.path`, so test
modules import this by bare name. The scripts live under `plugins/` and are
not a package -- there is no install step -- so the path is prepended here
once rather than in every test module.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "comment-review" / "skills" / "comment-review" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
