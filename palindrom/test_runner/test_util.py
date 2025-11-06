from termcolor import colored
import language as lang

def get_test_outcomes(test_outcomes) -> tuple[int, int, int]:
  total_n_tests = len(test_outcomes)
  successful_n_tests = [test_outcome.check_outcome() for test_outcome in test_outcomes].count(0)
  fail_n_tests = total_n_tests - successful_n_tests
  return total_n_tests, successful_n_tests, fail_n_tests


def print_test_progress(test_outcomes) -> None:
  total_n_tests, successful_n_tests, fail_n_tests = get_test_outcomes(test_outcomes)
  
  graphic_test_result = "[" + colored("==="*successful_n_tests, "green") + "   "*fail_n_tests + "] (" + colored(str(successful_n_tests), "green") + "/" + str(total_n_tests) + ")"
  print(lang.t("Test-Fortschritt:\n"), graphic_test_result)


def print_error_message(test_outcomes, general_message: str) -> bool:
  found_errors = False
  for test_info in test_outcomes:
    if test_info.check_outcome() == test_info.FAILURE and "AssertionError" not in test_info.get_error_info():
      # Problem, e.g. syntax error
      print(colored(lang.t("Es scheint allgemeine Probleme mit deinem Code zu geben."), "red"))
      print(colored(general_message, "red"))
      print("-"*len(general_message))
      found_errors = True
      break
  return found_errors
  
  
def print_general_message(test_outcomes, general_message: str) -> None:
  total_n_tests, successful_n_tests, _ = get_test_outcomes(test_outcomes)
  if(successful_n_tests == total_n_tests):
    print(colored(lang.t("Super gemacht!"), "green"))
  elif(successful_n_tests == total_n_tests-1):
    print(colored(lang.t("Schaffst du auch den letzten Test-Case noch? :)"), "green"))
  elif(successful_n_tests > total_n_tests/2):
    print(colored(lang.t("Schon mehr als die Hälfte der Test-Cases sind erfolgreich!"), "green"))
  elif(successful_n_tests == total_n_tests/2):
    print(colored(lang.t("Schon die Hälfte der Test-Cases sind erfolgreich!"), "green"))
  elif(successful_n_tests > 1):
    print(colored(lang.t("Einige Test-Cases sind bereits erfolgreich!"), "green"))
  elif(successful_n_tests == 1):
    print(colored(lang.t("Ein erster Test-Case ist erfolgreich!"), "green"))
  else:
    print(colored(lang.t("Schau dir doch mal die Test-Cases an!"), "green"))
  print(general_message)
  print("-"*len(general_message))
  
  
def print_basic(test_outcomes, general_message: str) -> None:
  print_test_progress(test_outcomes)

  found_errors = print_error_message(test_outcomes, general_message)
  if not found_errors:
    print_general_message(test_outcomes, general_message)
  

