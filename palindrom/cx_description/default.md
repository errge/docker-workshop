## Programmieraufgabe Palindrom

### 1. Einführung

**Palindrome** sind Zeichenketten, die sowohl vorwärts als auch rückwärts gelesen identisch sind.

**Beispiele:** kajak, hannah, lagerregal.

![palindrome.jpg](/cx_data/palindrome.jpg)

## 2. Programmanforderungen

Schreiben Sie eine Funktion `is_palindrom`, welche einen String als Eingabe erhält und `True` zurückgibt, wenn dieser String ein Palindrom ist. Wenn der String kein Palindrom ist, soll die Funktion `False` zurückgeben.

**Beispiele:**

    Input: rotor
    Output: True

<!---->

    Input: motor
    Output: False

Folgende **Anforderungen** sollte Ihr Programm erfüllen:

1. (1 Punkt) Es existiert eine einzige Funktion `is_palindrom`, welche einen String als Eingabe entgegennimmt und einen Boolean zurückgibt. Ihr Programm soll keine weiteren Funktionen beinhalten. Diese Anforderung wird von Test 1 überprüft.

2. (1 Punkt) Wenn die Funktion ein Palindrom als Eingabe erhält, gibt sie `True` zurück. Diese Anforderung wird von Test 2 überprüft.

3. (1 Punkt) Wenn die Funktion einen leeren String als Eingabe erhält, gibt sie `False` zurück. Diese Anforderung wird von Test 3 überprüft.

4. (1 Punkt) Wenn die Funktion einen String als Eingabe erhält, der kein Palindrom ist, gibt sie `False` zurück. Diese Anforderung wird von Test 4 überprüft.

***

### 3. Allgemeine Informationen zu den automatischen Testfällen

Bitte beachten Sie folgende Punkte:

* Eine optimale Lösung erfüllt alle Testfälle.
* Versuchen Sie sich möglichst exakt an die gegebenen Anforderungen zu erhalten. Selbständige Erweiterungen oder zusätzliche Optimierungen führen möglicherweise dazu, dass die Testfälle nicht mehr funktionieren.

Sie können Ihr Programm automatisch überprüfen lassen, indem Sie auf den **Test**-Button klicken. Anschliessend wird das Resultat dieser Überprüfung im Tab "Test Results" angezeigt:

![flask-solid.png](/cx_data/flask-solid.png)