---
nr: "10"
tytul: "Po weryfikacji R1: stany błędów w dokumentacji"
status: do-zrobienia
blokowany-przez: ["01", "05", "06"]
scenariusze: ["S2", "S4"]
budowal: null
github: null
---

# 10 — Po weryfikacji R1: stany błędów w dokumentacji

## Co widać po zrobieniu

Dokumentacja (EN i PL) opisuje najczęstsze błędy ze specu (Doświadczenie → Stany → „Błąd”). Przy każdym podaje komunikat, przyczynę i krok do wykonania:

- brak połączenia z Neo4j: README (szybki start) albo strona konfiguracji, z odsyłaczem z README;
- brak pluginu APOC: strona rozszerzeń APOC;
- wyłączony import plików APOC: już opisany, pozostaje bez zmian.

## Kryteria akceptacji

- [ ] Komunikaty błędów pochodzą z prawdziwego uruchomienia (sterownik albo serwer z CI), a nie z pamięci
- [ ] S4: strony mają odpowiedniki PL z identycznym kodem
- [ ] S2: przykłady stron nadal wykonują się na bazie testowej
- [ ] Walidacja zielona
- [ ] Akceptacja wyglądu wpisana w Notatkach

## Poza zakresem

- Brak pluginu GDS. Opisuje go ticket 07 razem ze stroną GDS, jeśli przy budowie okaże się potrzebny.

## Notatki

- Uwaga weryfikacji: R1.2 ([weryfikacja](../weryfikacja.md)).
