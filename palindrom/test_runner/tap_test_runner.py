## Testrunner - Python
## Version 2.17
## Authors: Oliver Probst, Nicole Wenzinger, Antoine Suter, Markus Dahinden
## Maintainer: Markus Dahinden
## Changelog:
## [2.17] Removed remnants of old html output
## [2.16] Fix problem with escape sequence warning in python 3.12
## [2.15] Optimized output in case of a failing testcase: input without "call", long console output is shortened
## [2.14] Added is_input_test to return in that case "Dein Input..." instead of "Dein Output..."
## [2.13] Added get_clean_errormessage to reduce the non-relevant output in failing test cases
## [2.12] Optimized Output when no solution hint should be given
## [2.11] Add codeblock and optional output-hint
## [2.1] Add subtests, improve multiline support
## [2.02] Improve Sanitize yml-Error Output (Bail out!, not ok, ok, ---)
## [2.01] Sanitize yml-Error Output (...)
## [2.0] Optimized writing of testcases (class Testcase() added)
## [1.9] switched to tap output

import io
import sys
import time
from datetime import datetime

from unittest import TextTestRunner
import unittest
from tap_test_result import TapTestResult
from utillib import find_edit_distance

import re
import language as lang


UTF8 = "UTF-8"


class Testcase():
  pattern = ""
  seen = ""
  is_input_test = False
  expected = ""
  result = False
  hint = ""
  
  def __init__(self, pattern, haystack, hint=None):
    self.pattern = pattern
    if(hint == None):
      self.hint = self.make_pretty(self.pattern)
    else:  
      self.hint = hint
      
    if(isinstance(haystack, unittest.mock.MagicMock)):
      self.seen = str(haystack.call_args_list).replace("[]", "")
      self.is_input_test = True
    elif(isinstance(haystack, io.StringIO)):
      self.seen = haystack.getvalue()
    elif(isinstance(haystack, str)):
      self.seen = haystack
    else:
      exit("Wrong type of haystack! Type is: " + str(type(haystack)))
    self.result = self.validate()
    
  def sanitize_tap_yml(self, txt):
    return txt.replace(".", ". ")    \
              .replace("-", "- ")    \
              .replace("[. . ]", "[..]")    \
              .replace("Bail out!", "Bail out")
              
  def remove_call_from_input(self, txt):
    return txt.replace('[call(\'','').replace(' call(\'','').replace('\')','').replace(']','').replace(',','')
    
  def validate(self, ignorecase=True):
    if(ignorecase):
      result = re.search(self.pattern, self.seen, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    else:
      result = re.search(self.pattern, self.seen, re.MULTILINE | re.DOTALL)
    return result
  
  def get_errormessage(self):
    cut_after = 800

    if(len(self.seen)>cut_after):
      seen_sanitized = self.sanitize_tap_yml("[..] "+self.seen[-cut_after:])
    else:
      seen_sanitized = self.sanitize_tap_yml(self.seen)
    
    if self.hint != "":
      if self.is_input_test:
        return lang.t("Dein Input:")+"\n```text\n" + self.remove_call_from_input(seen_sanitized) + "\n```\n"+lang.t("Erwarteter Input:")+"\n```text\n" + self.hint + "\n```"
      else:
        return lang.t("Dein Output:")+"\n```text\n" + seen_sanitized + "\n```\n"+lang.t("Erwarteter Output:")+"\n```text\n" + self.hint + "\n```"
    else:
      if self.is_input_test:
        return lang.t("Dein Input:")+"\n```text\n" + self.remove_call_from_input(seen_sanitized) + "```"
      else:
        return lang.t("Dein Output:")+"\n```text\n" + seen_sanitized + "```"
      
  def get_clean_errormessage(self): # tries to identify the relevant (wrong) line in self.seen
    if(self.hint != ""):
      best_candidate = ""
      best_candidate_edit_distance = len(self.seen)
      for line in self.seen.split("\n"): # consider edit distance between line and self.hint
        next_edit_distance = find_edit_distance(line, self.hint)
        if next_edit_distance < best_candidate_edit_distance:
          best_candidate = line
          best_candidate_edit_distance = next_edit_distance
      if "call" in best_candidate: # if we are checking the input then we want to remove the "[call('...')]" around the relevant "..."
        try:
          best_candidate = re.findall("\'.*\'", best_candidate)[0][1:-1]
        except:
          pass
      if best_candidate_edit_distance > len(self.hint)/2:
        best_candidate = ""
      if self.is_input_test:
        return lang.t("Relevanter Ausschnitt aus deinem Input:")+"\n```text\n" + best_candidate + "\n```\n"+lang.t("Erwarteter Input:")+"\n```text\n" + self.hint + "\n```"
      else:
        return lang.t("Relevanter Ausschnitt aus deinem Output:")+"\n```text\n" + best_candidate + "\n```\n"+lang.t("Erwarteter Output:")+"\n```text\n" + self.hint + "\n```"
    else:
      return get_errormessage(self)
    
  def make_pretty(self,string):
    return string.replace("(.|\\n)*", "\n") \
                 .replace("(","'")        \
                 .replace(")","'")        \
                 .replace("|","' "+lang.t("oder")+" '") \
                 .replace("^","")         \
                 .replace("$","")         \
                 .replace(".?","")        \
                 .replace(".*"," ")       \
                 .replace(".+"," ")       \
                 .replace("!?","!")       \
                 .replace("\\??","?")      \
                 .replace("\\s+"," ")      \
                 .replace("\\s?","")       \
                 .replace(":?","")        \
                 .replace("\\[", "[")      \
                 .replace("\\]", "]")      \
                 .replace("\\","")


class TimeoutError(Exception):
    pass


class TapTestRunner(TextTestRunner):
    """" A test runner class that output the results. """

    time_format = "%Y-%m-%d_%H-%M-%S"

    def __init__(self, output="./reports/", verbosity=2, stream=sys.stderr,
                 descriptions=True, failfast=False, buffer=False,
                 report_name=None, add_timestamp=True):
        self.verbosity = verbosity
        self.output = output
        self.encoding = UTF8

        TextTestRunner.__init__(self, stream, descriptions, verbosity,
                                failfast=failfast, buffer=buffer)

        if add_timestamp:
            self.timestamp = time.strftime(self.time_format)
        else:
            self.timestamp = ""

        self.resultclass = TapTestResult
        self.report_name = report_name

        self.start_time = 0
        self.time_taken = 0

    def _make_result(self):
        """ Create a TestResult object which will be used to store
        information about the executed tests. """
        return self.resultclass(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        """ Runs the given testcase or testsuite. """
        try:

            result = self._make_result()
            result.failfast = self.failfast
            if hasattr(test, 'properties'):
                # junit testsuite properties
                result.properties = test.properties

            self.start_time = time.process_time()
            test(result)
            stop_time = time.process_time()
            self.time_taken = stop_time - self.start_time

            run = result.testsRun

            expectedFails = len(result.expectedFailures)
            unexpectedSuccesses = len(result.unexpectedSuccesses)
            skipped = len(result.skipped)

            infos = []
            if not result.wasSuccessful():
                failed, errors = map(len, (result.failures, result.errors))
                if failed:
                    infos.append("Failures={0}".format(failed))
                if errors:
                    infos.append("Errors={0}".format(errors))

            if skipped:
                infos.append("Skipped={}".format(skipped))
            if expectedFails:
                infos.append("Expected Failures={}".format(expectedFails))
            if unexpectedSuccesses:
                infos.append("Unexpected Successes={}".format(
                    unexpectedSuccesses))

            result.generate_reports(self)

        finally:
            pass
        return result