## TAP-Testresult Generator for Python
## Version 2.1
## Authors: Oliver Probst, Nicole Wenzinger, Antoine Suter, Markus Dahinden
## Maintainer: Markus Dahinden
## [2.4] Fix problem with escape sequence warning in python 3.12
## [2.3] Fix problem with Subtests in python 3.11
## [2.2] Fix problem with Python 3.11
## [2.1] Add subtests, improve multiline support
## [2.0] switched to tap output

from __future__ import print_function

import os
import sys
import time
import copy
import traceback
from unittest import TestResult, TextTestResult
from unittest.result import failfast
import language as lang


def testcase_name(test_method):
    testcase = type(test_method)

    module = testcase.__module__ + "."
    if module == "__main__.":
        module = ""
    result = module + testcase.__name__
    return result


def strip_module_names(testcase_names):
    """Examine all given test case names and strip them the minimal
    names needed to distinguish each. This prevents cases where test
    cases housed in different files but with the same names cause clashes."""
    result = copy.copy(testcase_names)
    for i, testcase in enumerate(testcase_names):
        classname = testcase.split(".")[-1]
        duplicate_found = False
        testcase_names_ = copy.copy(testcase_names)
        del testcase_names_[i]
        for testcase_ in testcase_names_:
            classname_ = testcase_.split(".")[-1]
            if classname_ == classname:
                duplicate_found = True
        if not duplicate_found:
            result[i] = classname
    return result


class _TestInfo(object):
    """" Keeps information about the execution of a test method. """

    (SUCCESS, FAILURE, ERROR, SKIP) = range(4)

    def __init__(self, test_result, test_method, outcome=SUCCESS,
                 err=None, subTest=None):
        self.test_result = test_result
        self.outcome = outcome
        self.elapsed_time = 0
        self.err = err
        self.stdout = test_result._stdout_data
        self.stderr = test_result._stderr_data

        self.is_subtest = subTest is not None

        self.test_description = self.test_result.getDescription(test_method)
        self.test_exception_info = (
            '' if outcome in (self.SUCCESS, self.SKIP)
            else self.test_result._exc_info_to_string(
                self.err, test_method))

        self.test_name = testcase_name(test_method)
        if not self.is_subtest:
            self.test_id = test_method.id()
        else:
            self.test_id = subTest.id()

    def id(self):
        return self.test_id

    def test_finished(self):
        self.elapsed_time = self.test_result.stop_time - self.test_result.start_time

    def get_description(self):
        return self.test_description

    def get_error_info(self):
        return self.test_exception_info
    
    def check_outcome(self):
      if self.outcome != self.SUCCESS:
        return self.FAILURE
      return self.SUCCESS

class _SubTestInfos(_TestInfo):
    # TODO: make better: inherit _TestInfo?
#    (SUCCESS, FAILURE, ERROR, SKIP) = range(4)

    def __init__(self, test_id, subtests):
        self.subtests = subtests
        self.test_id = test_id
        self.outcome = self.check_outcome()
        self.elapsed_time = 0

        for subtest in self.subtests:
          self.elapsed_time += subtest.test_result.stop_time - subtest.test_result.start_time
        

    def check_outcome(self):
        outcome = _TestInfo.SUCCESS
        for subtest in self.subtests:
            if subtest.outcome != _TestInfo.SUCCESS:
                outcome = _TestInfo.FAILURE
                break
        return outcome
        
    def get_error_info(self):
        return "\n".join([subtest.get_error_info() for subtest in self.subtests])


class TapTestResult(TextTestResult):
    """ A test result class that express test results in TAP. """

    start_time = None
    stop_time = None
    default_prefix = "TestResults_"

    def __init__(self, stream, descriptions, verbosity):
        TextTestResult.__init__(self, stream, descriptions, verbosity)
        self.buffer = True
        self._stdout_data = None
        self._stderr_data = None
        self.successes = []
        self.subtests = {}
        self.callback = None
        self.infoclass = _TestInfo
        self.report_files = []
        self.all_results = None

    def _prepare_callback(self, test_info, target_list, verbose_str,
                          short_str):
        """ Appends a 'info class' to the given target list and sets a
            callback method to be called by stopTest method."""
        target_list.append(test_info)

        def callback():
            test_info.test_finished()

        self.callback = callback

    def getDescription(self, test):
        """ Return the test description if not have test name. """
        doc = test._testMethodDoc
        if self.descriptions and doc:
            return doc
        else:
            return str(test)

    def startTest(self, test):
        """ Called before execute each method. """
        self.start_time = time.time()
        TestResult.startTest(self, test)

    def _save_output_data(self):
        try:
            self._stdout_data = sys.stdout.getvalue()
            self._stderr_data = sys.stderr.getvalue()
        except AttributeError:
            pass

    def stopTest(self, test):
        """ Called after excute each test method. """
        self._save_output_data()
        TextTestResult.stopTest(self, test)
        self.stop_time = time.time()

        if self.callback and callable(self.callback):
            self.callback()
            self.callback = None

    def addSuccess(self, test):
        """ Called when a test executes successfully. """
        self._save_output_data()
        self._prepare_callback(self.infoclass(
            self, test), self.successes, "OK", ".")

    @failfast
    def addFailure(self, test, err):
        """ Called when a test method fails. """
        self._save_output_data()
        testinfo = self.infoclass(self, test, self.infoclass.FAILURE, err)
        self._prepare_callback(testinfo, self.failures, "FAIL", "F")

    @failfast
    def addError(self, test, err):
        """" Called when a test method raises an error. """
        self._save_output_data()
        testinfo = self.infoclass(self, test, self.infoclass.ERROR, err)
        self._prepare_callback(testinfo, self.errors, 'ERROR', 'E')

    def addSubTest(self, testcase, test, err):
        """ Called when a subTest completes. """
        self._save_output_data()
        # TODO: should ERROR cases be considered here too?
        if err is None:
            testinfo = self.infoclass(
                self, testcase, self.infoclass.SUCCESS, err, subTest=test)
            self._prepare_callback(testinfo, self.successes, "OK", ".")
        else:
            testinfo = self.infoclass(
                self, testcase, self.infoclass.FAILURE, err, subTest=test)
            self._prepare_callback(testinfo, self.failures, "FAIL", "F")

        test_id_components = str(testcase).rstrip(')').split(' (')
        test_id = test_id_components[1] + '.' + test_id_components[0]
        if test_id not in self.subtests:
            self.subtests[test_id] = []
        self.subtests[test_id].append(testinfo)

    def addSkip(self, test, reason):
        """" Called when a test method was skipped. """
        self._save_output_data()
        testinfo = self.infoclass(self, test, self.infoclass.SKIP, reason)
        self._prepare_callback(testinfo, self.skipped, "SKIP", "S")

    def _get_info_by_testcase(self):
        """ Organize test results by TestCase module. """
        if not self.all_results is None:
          return self.all_results
          
        tests_by_testcase = {}
        subtest_names = set()
        
        for test_name, subtests in self.subtests.items():
            subtest_info = _SubTestInfos(test_name, subtests)
            testcase_name = ".".join(test_name.split(".")[:-1])
            subtest_names.add(testcase_name)
            tests_by_testcase[testcase_name] = subtest_info
        
        for tests in (self.successes, self.failures, self.errors, self.skipped):
            for test_info in tests:
                # subtests will be contained by _SubTestInfos objects but there is also the
                # case where all subtests pass and the method is added as a success as well
                # which must be filtered out
                if test_info.is_subtest or test_info.test_id in subtest_names:
                    continue

                if isinstance(test_info, tuple):  # TODO: does this ever occur?
                    test_info = test_info[0]
                
                testcase_name = test_info.test_id

                tests_by_testcase[testcase_name] = test_info

        # unittest tests in alphabetical order based on test name so re-assert this
        tests_by_testcase = dict(sorted(tests_by_testcase.items()))
        return tests_by_testcase
    
    def print_test(self, report_file, test, number, issubtest=False,spaces=""):
      if isinstance(test, _SubTestInfos):
        raw_desc = test.subtests[0].get_description()
      elif issubtest: # Name and attributes is in TestId between brackets
        raw_desc = test.id()
        import re
        tmp = re.search(r'\[((.|\n)*?)\]', raw_desc)
        if tmp is not None:
          raw_desc = tmp.group(1) 
      else:
        raw_desc = test.get_description()
      
      def splitDescription(text):
        # In case 'text' is empty
        if len(text) == 0:
          return {'description': '', 'attributes': []}
        out = dict()
        # First line of description
        out['description'] = text.splitlines()[0].lstrip(' ')
        # every subsequent section which starts with a name followed by a semicolon is split into atributes
        import re
        infos = re.compile('\\n *(?P<tag>[\\d\\w]*):\\s*(?P<text>(?:(?!\\n *[\\d\\w]*:)(?:.|\\n))*)')
        out['attributes'] = [m.groupdict() for m in infos.finditer(text)]
        return out
      
      def indent(text):
        return '\n'.join(["  " + x for x in text.splitlines()])
        
      desc = splitDescription(raw_desc)
      if not isinstance(test, _SubTestInfos):
        if not test.err is None:
          desc['attributes'].append({'tag' : lang.t('Fehler'), 'text' : str(test.err[1])})
      
      desc['attributes'].append({'tag' : lang.t('Testlaufzeit'), 'text' : f"{round(test.elapsed_time, 3)} seconds\n"})
      
      #report_file.write(f"TEST {test}")
      # Description
      res = "ok" if test.check_outcome() == test.SUCCESS else "not ok"
      report_file.write(f"{spaces}{res} {number} - {desc['description']}\n")

      # Attributes
      report_file.write("---\n")
      
      for attribute in desc['attributes']:
        report_file.write(f"{attribute['tag']}: |\n")
        report_file.write(f"{indent(attribute['text'])}\n")
      
      report_file.write("...\n")
      
      if isinstance(test, _SubTestInfos):
        self.print_subtest(report_file, test.subtests)

      
    def print_subtest(self, report_file, subtests):
        for i, test in enumerate(subtests):
            self.print_test(report_file, test, i+1, issubtest=True, spaces="    ")
      
    def generate_reports(self, testRunner):
        """ Generate report for all given test cases that have been run. """
        all_results = self._get_info_by_testcase()
        dir_to = testRunner.output
        if not os.path.exists(dir_to):
            os.makedirs(dir_to)

        report_name = testRunner.report_name
        if testRunner.timestamp:
            report_name += "_" + testRunner.timestamp
        report_name += ".log"

        path_file = os.path.abspath(os.path.join(dir_to, report_name))
        self.report_files.append(path_file)
        with open(path_file, 'w') as report_file:
            report_file.write("1..{var}\n".format(var=len(all_results)))
            for i, test in enumerate(all_results.values()):
                self.print_test(report_file, test, i+1)
    
    
    def get_test_outcomes(self):
      all_results = self._get_info_by_testcase()
      return list(all_results.values())
      
    
    def _exc_info_to_string(self, err, test):
        """ Converts a sys.exc_info()-style tuple of values into a string."""
        # if six.PY3:
        #     # It works fine in python 3
        #     try:
        #         return super(_HTMLTestResult, self)._exc_info_to_string(
        #             err, test)
        #     except AttributeError:
        #         # We keep going using the legacy python <= 2 way
        #         pass

        # This comes directly from python2 unittest
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        msg_lines = traceback.format_exception(exctype, value, tb)

        if self.buffer:
            # Only try to get sys.stderr as it might not be
            # StringIO yet, e.g. when test fails during __call__
            try:
                error = sys.stderr.getvalue()
            except AttributeError:
                error = None
            if error:
                if not error.endswith('\n'):
                    error += '\n'
                msg_lines.append(error)
        # This is the extra magic to make sure all lines are str
        encoding = getattr(sys.stdout, 'encoding', 'utf-8')
        lines = []
        for line in msg_lines:
            if not isinstance(line, str):
                # utf8 shouldn't be hard-coded, but not sure f
                line = line.encode(encoding)
            lines.append(line)

        return ''.join(lines)