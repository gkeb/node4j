---
nr: "08"
tytul: "Sterownik `neo4j` 6.x"
status: do-zrobienia
blokowany-przez: ["07"]
scenariusze: [N1, N2, N3]
budowal: null
github: null
---

# 08 — Sterownik `neo4j` 6.x

## Co widać po zrobieniu

Sterownik `neo4j` w najnowszej wersji 6.x z granicą `<7`, skonfigurowany bez automatycznych ponowień zapisów auto-commit; zmiany z badania obsłużone. Kryterium końca specu spełnione.

## Kryteria akceptacji

- [ ] N1, N2, N3: testy zielone na całej macierzy i w przebiegu z najnowszym `pydantic` 2.x
- [ ] sterownik tworzony z `disable_auto_commit_retries=True`
- [ ] zachowanie przy zamkniętym sterowniku i zmienionych klasach wyjątków ([badanie](../../../badania/2026-10-11-sterownik-neo4j-6.md)) zgodne z N1
- [ ] skrypt demonstracyjny przechodzi na nowym stosie na bazie testowej
- [ ] kryterium końca specu sprawdzone punkt po punkcie i opisane w Notatkach

## Poza zakresem

- Nowe możliwości sterownika 6.x (np. HTTP Query API) — osobne zdolności w Mgle.

## Notatki

Uruchomić testy z `-W error::ResourceWarning` (zalecenie badania).
