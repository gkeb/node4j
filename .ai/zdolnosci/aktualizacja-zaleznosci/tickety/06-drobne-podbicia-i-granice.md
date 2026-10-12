---
nr: "06"
tytul: "Drobne podbicia i granice wersji"
status: zrobione
blokowany-przez: ["05", "09", "10"]
scenariusze: [N1, N2, N3]
budowal: "Codex / GPT-6"
github: null
---

# 06 — Drobne podbicia i granice wersji

## Co widać po zrobieniu

`pydantic`, `pydantic-settings`, `structlog`, `pytest`, `pytest-asyncio`, `ruff` w najnowszych wersjach z dnia rozpoczęcia ticketu; metadane z minimum równym sprawdzonym wersjom i granicami `pydantic<3`, `pydantic-settings<3`; CI ma osobny przebieg na najnowszym `pydantic` 2.x.

## Kryteria akceptacji

- [x] N1, N2, N3: testy zielone (lokalnie, w CI na pliku blokady i w przebiegu z najnowszym `pydantic` 2.x)
- [x] zestaw wersji zapisany w Notatkach z datą; plik blokady jest punktem odniesienia do końca zdolności
- [x] ruff bez błędów spoza punktu odniesienia (nowe reguły nowej wersji ruff obsłużone albo opisane)

## Poza zakresem

- Sterownik `neo4j` — ticket 08; serwery — ticket 07.

## Notatki

Ryzyko: metaklasa `NodeBase` dziedziczy po wewnętrznej metaklasie pydantic (mapa obszaru zależności).

Wersje dostępne przy rozpoczęciu ticketu (PyPI, 2026-10-12): `pydantic 2.14.1`, `pydantic-settings 2.15.0`, `structlog 26.1.0`, `pytest 9.1.1`, `pytest-asyncio 1.4.0`, `ruff 0.17.0`. Źródła: [pydantic](https://pypi.org/project/pydantic/), [pydantic-settings](https://pypi.org/project/pydantic-settings/), [structlog](https://pypi.org/project/structlog/), [pytest](https://pypi.org/project/pytest/), [pytest-asyncio](https://pypi.org/project/pytest-asyncio/), [ruff](https://pypi.org/project/ruff/).

Weryfikacja lokalna (2026-10-12): `uv sync --locked`; testy N1–N3 i TTL: 63 passed na locku oraz 63 passed po kroku z najnowszym Pydantic 2.x; Ruff 0.17.0 bez nowych błędów względem 119 znanych. `uv lock --check` i `git diff --check` przechodzą. Ostrzeżenia testów: istniejące użycie `datetime.utcnow()` i brak uprawnień do `.pytest_cache`; testy zakończyły się poprawnie. Przegląd zgodności, jakości i bezpieczeństwa: bez uwag. CI dla commitu `b702527` zielone w obu jobach (run [38284717944](https://github.com/gkeb/node4j/actions/runs/38284717944)).
