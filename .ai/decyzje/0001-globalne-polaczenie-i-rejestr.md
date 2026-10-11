# 0001. Globalne połączenie i rejestr modeli — jedna baza na proces

- Data: 2026-10-11
- Status: zastana
- Źródło: `node4j/db.py` → `connection = AsyncDatabase()`; `node4j/registry.py` → `node_registry`; commit `674bfc8` (basic version)
- Zdolność: ogólna

## Kontekst

Menedżery, relacje i rozszerzenia muszą mieć dostęp do sterownika i do klas modeli bez przekazywania ich w każdym wywołaniu.

## Decyzja

Biblioteka ma jeden globalny obiekt `connection` (sterownik, transakcja w `ContextVar`) i jeden globalny rejestr modeli. Wszystkie moduły importują je bezpośrednio.

## Rozważane alternatywy

<!-- Brak źródła z rozważanymi alternatywami. (wniosek) Typowe: połączenie przekazywane do menedżera albo sesja jako obiekt jednostki pracy — więcej kodu, ale wiele baz w procesie. -->

## Konsekwencje

- Proste API (`Person.q.create(...)`) bez przekazywania połączenia.
- Jeden proces = jedna baza i jeden zestaw danych logowania (`NODE4J_*`); wiele baz albo wielu najemców wymaga zmiany tej decyzji.
- Testy dzielą stan globalny — rejestr i połączenie trzeba izolować ręcznie.
