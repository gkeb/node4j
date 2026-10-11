---
nr: "06"
tytul: "Drobne podbicia i granice wersji"
status: do-zrobienia
blokowany-przez: ["05"]
scenariusze: [N1, N2, N3]
budowal: null
github: null
---

# 06 — Drobne podbicia i granice wersji

## Co widać po zrobieniu

`pydantic`, `pydantic-settings`, `structlog`, `pytest`, `pytest-asyncio`, `ruff` w najnowszych wersjach z dnia rozpoczęcia ticketu; metadane z minimum równym sprawdzonym wersjom i granicami `pydantic<3`, `pydantic-settings<3`; CI ma osobny przebieg na najnowszym `pydantic` 2.x.

## Kryteria akceptacji

- [ ] N1, N2, N3: testy zielone (lokalnie, w CI na pliku blokady i w przebiegu z najnowszym `pydantic` 2.x)
- [ ] zestaw wersji zapisany w Notatkach z datą; plik blokady jest punktem odniesienia do końca zdolności
- [ ] ruff bez błędów spoza punktu odniesienia (nowe reguły nowej wersji ruff obsłużone albo opisane)

## Poza zakresem

- Sterownik `neo4j` — ticket 08; serwery — ticket 07.

## Notatki

Ryzyko: metaklasa `NodeBase` dziedziczy po wewnętrznej metaklasie pydantic (mapa obszaru zależności).
