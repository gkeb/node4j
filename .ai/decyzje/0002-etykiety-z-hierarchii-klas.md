# 0002. Etykiety z hierarchii klas, rejestr po nazwie klasy

- Data: 2026-10-11
- Status: zastana
- Źródło: `node4j/nodes.py` → `NodeBase.__new__`; `test.py` → krok 9 (węzły z wieloma etykietami)
- Zdolność: ogólna

## Kontekst

Modele dziedziczą po sobie (np. `Employee(Person)`) i zapytanie przez rodzica ma widzieć węzły podklas. Relacje wskazują model docelowy nazwą, bo cel może być zdefiniowany później.

## Decyzja

Etykiety węzła to nazwa jego klasy i etykiety wszystkich przodków (bez `Node`). Model trafia do rejestru pod nazwą klasy, a relacje rozwiązują cel w rejestrze dopiero przy zapytaniu.

## Rozważane alternatywy

<!-- Brak źródła. (wniosek) Jawna etykieta w `Meta` albo rejestr po pełnej ścieżce modułu. -->

## Konsekwencje

- `Person.q.match_all()` zwraca też węzły `Employee` (zhydratowane jako `Person`); `Employee.q` widzi tylko pracowników.
- Mixiny dziedziczące po `Node` dodają własną etykietę (`TTLMixin`, `SoftDeleteMixin`).
- Dwie klasy o tej samej nazwie w różnych modułach nadpisują się w rejestrze bez ostrzeżenia.
- Zmiana nazwy klasy zmienia etykietę w bazie — to zmiana danych, nie tylko kodu.
