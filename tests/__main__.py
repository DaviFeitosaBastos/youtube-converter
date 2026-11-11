"""Run unittest with failure details visible in GitHub check annotations."""
import os
import sys
import unittest

suite = unittest.defaultTestLoader.discover("tests")
result = unittest.TextTestRunner(verbosity=2).run(suite)
if os.environ.get("GITHUB_ACTIONS") == "true":
    for test, traceback in result.failures + result.errors:
        message = f"{test}: {traceback}"
        message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::error::{message}", flush=True)
sys.exit(0 if result.wasSuccessful() else 1)
