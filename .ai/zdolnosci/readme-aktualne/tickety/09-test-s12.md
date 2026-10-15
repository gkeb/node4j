---
nr: "09"
tytul: "Po weryfikacji R1: test akceptacyjny S12"
status: zrobione
blokowany-przez: ["01"]
scenariusze: ["S12"]
budowal: "Codex / GPT-6"
github: null
---

# 09 — Po weryfikacji R1: test akceptacyjny S12

## Co widać po zrobieniu

Zestaw testów ma test akceptacyjny z numerem S12. Uruchamia on testy dokumentacji przeciw nieosiągalnej bazie testowej w dwóch trybach:

- bez wymaganej bazy: testy wykonywania przykładów są pominięte, a testy struktury przechodzą;
- z wymaganą bazą (tryb CI): przebieg kończy się błędem połączenia w testach integracyjnych.

## Kryteria akceptacji

- [x] S12: test akceptacyjny przechodzi w obu trybach — pominięcie przykładów przy niewymaganej bazie oraz błąd połączenia przy wymaganej bazie
- [x] Test ćwiczy obie gałęzie przez publiczny interfejs zestawu testów (przebieg pytest), a nie przez wywołanie funkcji pomocniczych conftest
- [x] Test nie łączy się z żadną prawdziwą bazą i nie zależy od tego, czy baza testowa działa
- [x] Walidacja zielona

## Poza zakresem

- Zmiana zachowania reguły pomijania w conftest. Test przypina obecne zachowanie.

## Notatki

- Uwaga weryfikacji: R1.1 ([weryfikacja](../weryfikacja.md)).
- 2026-10-15 — Użytkownik rozstrzygnął, że `conftest.py` pozostaje bez zmian; w trybie wymaganym test przypina obecny raport błędu połączenia, nie raport pominiętych testów.
