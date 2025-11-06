from configs import configs

class language():
  lang = configs['language']
  
  thisdict_en = {
    "Weitere Infos findest du im Tab 'Test Results' im unteren Fensterbereich.": "You can find more information in the ‘Test results’ tab at the bottom of the window.",
    "Es scheint allgemeine Probleme mit deinem Code zu geben.": "There seems to be a general problem with your code.",
    "Super gemacht!": "Well done!",
    "Schaffst du auch den letzten Test-Case noch? :)": "Can you also complete the last test case? :)" ,
    "Schon mehr als die Hälfte der Test-Cases sind erfolgreich!": "More than half of the test cases are already successful!",
    "Schon die Hälfte der Test-Cases sind erfolgreich!": "Half of the test cases are already successful!",
    "Einige Test-Cases sind bereits erfolgreich!": "Some test cases are already successful!",
    "Ein erster Test-Case ist erfolgreich!": "A first test case is successful!",
    "Schau dir doch mal die Test-Cases an!": "Have a look at the test cases!",
    "Dein Input:": "Your input:",
    "Dein Output:": "Your output:",
    "Erwarteter Input:": "Expected input:",
    "Erwarteter Output:": "Expected output:",
    "Relevanter Ausschnitt aus deinem Input:": "Relevant section from your input:",
    "Relevanter Ausschnitt aus deinem Output:": "Relevant section from your output:",
    "oder": "or",
    "Weitere Infos findest du, wenn du den Test Button drückst.": "You can find more information by pressing the test button.",
    "Dieser Test hat die Zeitlimite überschritten.": "This test has exceeded the time limit.",
    "Sekunden": "seconds",
    "Test-Fortschritt:\n": "Test progress:\n",
    "Testlaufzeit": "Test runtime",
    "Fehler": "Error"
  }
  
  def __call__(self, text):
    if self.lang == "en":
      try:
        transl_string = self.thisdict_en[text]
      except:
        transl_string = "TRANSLATION MISSING: " + text
    else:
      transl_string = text
      
    return transl_string
  
t = language()