---
nr: "09"
tytul: "Po weryfikacji R1: wzmocnienie siatki"
status: zrobione
blokowany-przez: []
scenariusze: [N1, N3]
budowal: "Codex / GPT-6"
github: null
---

# 09 — Po weryfikacji R1: wzmocnienie siatki

## Co widać po zrobieniu

Na obecnym stosie testy charakteryzujące wykrywają zmianę zachowania tam, gdzie po rundzie R1 przechodziły niezależnie od niej: `Periodic.iterate`, domyślny odczyt `.env`, triggery APOC i prefetch przez `match_all`. Struktura biblioteki bez zmian.

## Kryteria akceptacji

- [x] N1: test `Periodic.iterate` ma obserwowalny efekt w bazie (zapytanie wewnętrzne zmienia własne, syntetyczne węzły) i sprawdza ten efekt, a nie wartość zwracaną wrappera (R1.1)
- [x] N3: test — `Settings()` bez argumentów czyta `.env` z bieżącego katalogu roboczego (katalog tymczasowy, `monkeypatch.chdir`), a zmienne środowiska nadal mają pierwszeństwo (R1.2)
- [x] N1: triggery APOC przypięte na bazie testowej zamiast mocka `connection.run` — test utrwala dzisiejszy rzeczywisty wynik `install`, `list` i `remove` na obecnym połączeniu, także jeśli jest nim błąd (R1.3)
- [x] N1: test — `match_all(prefetch=…)` ładuje relacje bez dodatkowego zapytania, w postaci listy i słownika (R1.5)
- [x] problem triggerów APOC (wymagana baza `system`) przeniesiony z `.ai/lekcje.md` do `.ai/proby.md` jako `nierozwiazane` (R1.4)
- [x] testy noszą numer niezmiennika w nazwie i są zielone na bazie testowej; żaden nie jest pominięty
- [x] walidacja (ruff) bez błędów spoza punktu odniesienia

## Poza zakresem

- Naprawa triggerów APOC (kierowanie wywołań do bazy `system`) — zmienia zachowanie; osobno przez `napraw` albo zdolność w Mgle.
- Zgłaszanie przez `Periodic.iterate` błędów zapytania wewnętrznego — dziś wrapper je pomija; to zachowanie przypinamy, nie zmieniamy.

## Notatki

Uwagi R1.1–R1.5 z [weryfikacja.md](../weryfikacja.md). Musi być zrobiony przed 06 (drobne podbicia), bo R1.1 i R1.2 dotyczą miejsc, które podbicie pydantic-settings i serwera może zmienić niezauważenie.

Dowód do R1.1: na bazie testowej `apoc.Periodic.iterate(..., "WITH n SET n.v = 1/0")` zwrócił `None` bez wyjątku, a węzeł się nie zmienił.
