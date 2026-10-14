---
nr: "09"
tytul: "Po weryfikacji R1: test akceptacyjny S12"
status: do-zrobienia
blokowany-przez: ["01"]
scenariusze: ["S12"]
budowal: null
github: null
---

# 09 — Po weryfikacji R1: test akceptacyjny S12

## Co widać po zrobieniu

Zestaw testów ma test akceptacyjny z numerem S12. Uruchamia on testy dokumentacji przeciw nieosiągalnej bazie testowej w dwóch trybach:

- bez wymaganej bazy: testy wykonywania przykładów są pominięte, a testy struktury przechodzą;
- z wymaganą bazą (tryb CI): przebieg kończy się błędem, a raport wskazuje pominięte testy integracyjne.

## Kryteria akceptacji

- [ ] S12: test akceptacyjny przechodzi
- [ ] Test ćwiczy obie gałęzie przez publiczny interfejs zestawu testów (przebieg pytest), a nie przez wywołanie funkcji pomocniczych conftest
- [ ] Test nie łączy się z żadną prawdziwą bazą i nie zależy od tego, czy baza testowa działa
- [ ] Walidacja zielona

## Poza zakresem

- Zmiana zachowania reguły pomijania w conftest. Test przypina obecne zachowanie.

## Notatki

- Uwaga weryfikacji: R1.1 ([weryfikacja](../weryfikacja.md)).
