---
nr: "01"
tytul: "Siatka: format danych i konfiguracja"
status: zrobione
blokowany-przez: []
scenariusze: [N2, N3]
budowal: "Codex / GPT-6"
github: null
---

# 01 — Siatka: format danych i konfiguracja

## Co widać po zrobieniu

Na obecnym stosie (sterownik 5.28, serwer 2025.05) istnieją zielone testy charakteryzujące N2 i N3. Struktura biblioteki bez zmian.

## Kryteria akceptacji

- [x] N2: test — węzeł zapisany przez API ma w bazie etykiety klasy i przodków, `uid` jako tekst i daty jako tekst ISO w dotychczasowej postaci (także data „naiwna” z przykładowego modelu)
- [x] N2: test — węzeł wstawiony surowym zapytaniem w obecnym formacie jest czytany przez API z poprawnymi typami pól
- [x] N2: test — `apply_schema` i infrastruktura TTL tworzą indeksy i constrainty o dotychczasowych nazwach
- [x] N3: test — ustawienia ze zmiennych `NODE4J_*`, z pliku `.env`, wartości domyślne i pierwszeństwo zmiennych środowiska przed `.env` (bez połączenia z bazą, `.env` w katalogu tymczasowym)
- [x] testy noszą numer niezmiennika w nazwie i są zielone na bazie testowej
- [x] walidacja (ruff) bez błędów spoza punktu odniesienia

## Poza zakresem

- Zmiany w kodzie biblioteki — tylko testy (podejrzane zachowanie zgłaszamy, nie poprawiamy).

## Notatki

Baza testowa z APOC: komenda w AGENTS.md → Uruchamianie. Testy nie dotykają bazy użytkownika na porcie 7687. N3 nie potrzebuje bazy — sprawdza obiekt ustawień tworzony na nowo w teście.
