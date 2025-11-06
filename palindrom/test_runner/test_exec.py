## [TEMP CHANGES] Added additional verbal test output

from unittest import TestLoader, TestSuite
from tap_test_runner import TapTestRunner

import csv
import os
import sys

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
print_basic(test_outcomes, lang.t("Weitere Infos findest du im Tab 'Test Results' im unteren Fensterbereich."))
# ---  END ADDITIONAL VERBAL TEST OUTPUT ---

# ---  BEGIN TAP OUTPUT ---
result_file = result.report_files[-1]
with open(result_file) as file_handler:
  res_content = file_handler.read()
  print("<cx:tap>")
  print("TAP version 13")
  print(res_content)
  print("</cx:tap>")
# ---  END TAP OUTPUT ---

# ---  BEGIN CX OUTPUT ---
from test_util import get_test_outcomes
total_n_tests, successful_n_tests, _ = get_test_outcomes(test_outcomes)
test_result_value = successful_n_tests / total_n_tests
print('<cx:result value="' + str(test_result_value) + '" />')

# ---  END CX OUTPUT ---


# Audit folder creation
audit_folder = "cx_audit"

if not os.path.isdir(audit_folder):
    os.mkdir(audit_folder)

# 0 for success, 1 for failure, 2 for error and 3 for skip
# example: to get outcome of test 0, type test_outcomes[0].outcome
outcome_values = {0: "success", 1: "failure", 2: "error", 3: "skip"}

# Infodump into audit file
with open(f'{audit_folder}/testcases.csv', mode='w') as testcases_file:
    testcases_writer = csv.writer(testcases_file, delimiter=',', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)
    for n in range(len(test_outcomes)):
        testcases_writer.writerow(['Test {}'.format(n+1),
                                   'Result: {}'.format(outcome_values[test_outcomes[n].outcome])])