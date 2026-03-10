"""Test utilities.

This package is configured to run tests against the source tree located in
`src/`. When tests are run directly (e.g. `python -m unittest`), Python may not
automatically include `src/` in `sys.path`, so we insert it here.
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")

if SRC not in sys.path:
    sys.path.insert(0, SRC)
