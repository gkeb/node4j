---
nr: "08"
tytul: "Sterownik `neo4j` 6.x"
status: w-toku
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
- [x] sterownik tworzony z `disable_auto_commit_retries=True`
- [x] zachowanie przy zamkniętym sterowniku i zmienionych klasach wyjątków ([badanie](../../../badania/2026-10-11-sterownik-neo4j-6.md)) zgodne z N1
- [ ] skrypt demonstracyjny przechodzi na nowym stosie na bazie testowej
- [ ] kryterium końca specu sprawdzone punkt po punkcie i opisane w Notatkach

## Poza zakresem

- Nowe możliwości sterownika 6.x (np. HTTP Query API) — osobne zdolności w Mgle.

## Notatki

Uruchomić testy z `-W error::ResourceWarning` (zalecenie badania).

Testy `tests/test_driver_config.py` sprawdzają wyłączenie ponowień, sprzątanie sterownika po błędzie i anulowaniu, ponowne połączenie oraz `DriverError` przy zapytaniu przez rzeczywisty zamknięty driver. `run()` zachowuje oryginalny `ConnectionAcquisitionTimeoutError`; `connect()` i `run()` logują błędy i ponownie rzucają ten sam wyjątek bez tłumaczenia klas z badania.

### Kryterium końca specu — kontrola punkt po punkcie

- `uv.lock` przechodzi `uv lock --check`; metadane mają trzy zależności runtime z granicami docelowymi (`neo4j>=6.4.0,<7`, Pydantic 2.x i pydantic-settings 2.x).
- Testy N1–N3 i TTL na czterech kombinacjach macierzy, przebieg z najnowszym Pydantic 2.x oraz wymaganie braku pominiętych testów integracyjnych: oczekują na CI po pushu.
- Dystrybucja zbudowana lokalnie, zainstalowana poza checkoutem w czystym środowisku zawierającym tylko zależności runtime; import publicznych modułów zakończył się powodzeniem.
- Ruff: brak nowych błędów względem punktu odniesienia; pozostało 113 znanych błędów.
- `test.py` na testowej bazie: oczekuje na CI; lokalnie nie ma dostępnej bazy testowej.

Pierwszy [run CI 38291335280](https://github.com/gkeb/node4j/actions/runs/38291335280) potwierdził pytest w macierzy, ale `test.py` dostał domyślne hasło i zakończył się `AuthError`: job udostępniał `NODE4J_TEST_*`, podczas gdy konfiguracja biblioteki czyta `NODE4J_*` (pytest mapował nazwy w `conftest.py`). Krok demonstracyjny mapuje teraz zmienne jawnie; oczekuje na ponowny CI.
