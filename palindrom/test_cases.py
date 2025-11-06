import io
import numpy as np
import unittest
from unittest.mock import Mock
import main_exec
import random
import re
import sys
import test_runner.utillib as util
from test_runner.tap_test_runner import Testcase
from test_runner.utillib import find_edit_distance
from inspect import signature, getmembers, isfunction

@unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
class Tests(unittest.TestCase):

  def check_and_get_palindrome_function(self):
    # If a (patched) module is loaded, delete it
    if 'main' in sys.modules:  
      del sys.modules["main"]
    import main
    functions = [function[0] for function in getmembers(main, isfunction)]
    if "is_palindrome" in functions:
      n_params = len(signature(main.is_palindrome).parameters)
      assert n_params == 1, "Die Funktion \"is_palindrome\" soll 1 Parameter entgegennehmen, aktuell erwartet sie aber " + str(n_params) + " Parameter"
      ret = main.is_palindrome("dummy")
      assert ret in [True, False], "Die Funktion \"is_palindrome\" soll immer einen Boolean (True oder False) zurückgeben, für den Input \"dummy\" gibt sie aber " + str(ret) + " zurück"
      return main.is_palindrome # if we reach this we have successfully tested the signature of is_palindrome
    for element in functions: # if the function has another name, we try to find it as well
      if find_edit_distance("palindrom", element) <= abs(len("palindrom") - len(element)) + 1:
        n_params = len(signature(getattr(main, element)).parameters)
        assert n_params == 1, "Die Funktion " + element + " soll 1 Parameter entgegennehmen, aktuell erwartet sie aber " + str(n_params) + " Parameter"
        ret = getattr(main, element)("dummy")
        assert ret in [True, False], "Die Funktion " + element + " soll immer einen Boolean (True oder False) zurückgeben, für den Input \"dummy\" gibt sie aber " + str(ret) + " zurück"
        return getattr(main, element) # if we reach this we have successfully tested the signature of some palindrome function
    assert False, "Du scheinst keine Funktion zu definieren, welche die Spezifikationen erfüllt"
    return None

  @util.timeout(1)
  @unittest.mock.patch('builtins.input', side_effect = lambda arg : "dummy")
  def test_a(self, mocked_input, mocked_stdout):
    """Teste, ob eine Funktion "is_palindrome" existiert, welche einen String als Eingabe entgegennimmt und einen Boolean zurückgibt (Anforderung 1) 
    Hint: Definiere eine Funktion mit dem Namen "is_palindrome" mit einem Parameter, die einen Boolean (True oder False) zurückgibt"""
    self.check_and_get_palindrome_function()

  @util.timeout(1)
  @unittest.mock.patch('builtins.input', side_effect = lambda arg : "dummy")
  def test_b(self, mocked_input, mocked_stdout):
    """ Teste, ob die Funktion True zurückgibt, wenn sie ein Palindrom als Eingabe erhält (Anforderung 2)
    Hint: Wenn die Funktion ein Palindrom (z.B. "kajak", "hannah" oder "lagerregal") als Eingabe erhält, soll sie True zurückgeben
    """
    is_palindrome = self.check_and_get_palindrome_function()
    palindromes = ["A", "AA", "ABBA", "anina", "dad", "drehmalamherd", "hannah", "kajak", "lagerregal", "level", "madam", "rotator", "tacocat"]
    for palindrome in palindromes:
      assert is_palindrome(palindrome), "Deine Funktion gibt für das Palindrom " + palindrome + " fälschlicherweise False zurück"
      
  @util.timeout(1)
  @unittest.mock.patch('builtins.input', side_effect = lambda arg : "dummy")
  def test_c(self, mocked_input, mocked_stdout):
    """ Teste, ob die Funktion False zurückgibt, wenn sie einen leeren String als Eingabe erhält (Anforderung 3)
    Hint: Wenn die Funktion einen leeren String "" (mit Länge 0) als Eingabe erhält, soll sie False zurückgeben
    """
    is_palindrome = self.check_and_get_palindrome_function()
    assert not is_palindrome(""), "Deine Funktion gibt für den leeren String \"\" fälschlicherweise True zurück"
      
  @util.timeout(1)
  @unittest.mock.patch('builtins.input', side_effect = lambda arg : "dummy")
  def test_d(self, mocked_input, mocked_stdout):
    """ Teste, ob die Funktion False zurückgibt, wenn sie ein Wort als Eingabe erhält, das kein Palindrom ist (Anforderung 4)
    Hint: Wenn die Funktion ein Wort als Eingabe erhält, das kein Palindrom ist (z.B. "kanu", "hanna" oder "einkaufswagen"), soll sie False zurückgeben
    """
    is_palindrome = self.check_and_get_palindrome_function()
    non_palindromes = ["ACDC", "Bathtub", "Blubberwasser ", "Foolproof", "hanna", "Hokuspokus", "moo", "solo", "zorro"]
    for non_palindrome in non_palindromes:
      assert not is_palindrome(non_palindrome), "Deine Funktion gibt für das Wort " + non_palindrome + " fälschlicherweise True zurück"