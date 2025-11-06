## [TEMP CHANGES] Added additional verbal test output

import sys
from unittest import TestLoader, TestSuite
from tap_test_runner import TapTestRunner
import language as lang

sys.path.append('/var/lib/cxrun/projectfiles/')
import test_cases

loaded_tests = TestLoader().loadTestsFromTestCase(test_cases.Tests)
suite = TestSuite([loaded_tests])
runner = TapTestRunner(
    output='./tmp', report_name="result", add_timestamp=False, verbosity=2)
result = runner.run(suite)

# ---  BEGIN ADDITIONAL VERBAL TEST OUTPUT ---
test_outcomes = result.get_test_outcomes()
from test_util import print_basic
print_basic(test_outcomes, lang.t("Weitere Infos findest du, wenn du den Test Button drückst."))
# ---  END ADDITIONAL VERBAL TEST OUTPUT ---
