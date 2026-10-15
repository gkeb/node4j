# Profil projektu

> Rozstrzygnięcia list decyzji z profili warsztatu (`profile/` w katalogu pluginu). Tu tylko wynik i link — treść decyzji żyje w ADR, `ZASADY.md`, specu albo mapie. Format: „Profile — klasy aplikacji” w `kontrakt/profile-i-wydania.md` w katalogu pluginu warsztatu.
> Wyniki: `ADR NNNN` | `Zxx` | `spec szkieletu` | `pominięte: powód` | `później` (Mgła) | `otwarte`

Profile: przekrojowe

- P-01 Użytkownicy i użycie — programista Pythona (async, podstawy Neo4j) używający biblioteki we własnej aplikacji — [readme-aktualne](zdolnosci/readme-aktualne/mapa.md) → Decyzje
- P-02 Język — otwarte (stan: komunikaty wyjątków i komentarze po polsku, logi po angielsku, README w EN i PL); dokumentacja użytkownika w pełni EN i PL — [readme-aktualne](zdolnosci/readme-aktualne/mapa.md) → Decyzje
- P-03 Środowisko i wersje — `.python-version` (3.12), `pyproject.toml` → `requires-python >=3.12`, uv + `uv.lock` w repo
- P-04 Układ repozytorium — otwarte (stan: pakiet `node4j/`, testy w `tests/`, CI w `.github/workflows/`)
- P-05 Strategia testów — pytest na jednorazowym kontenerze Neo4j (`tests/conftest.py`, AGENTS.md → Uruchamianie), testy charakteryzujące API i formatu danych — [aktualizacja-zaleznosci](zdolnosci/aktualizacja-zaleznosci/mapa.md) → Decyzje
- P-06 Walidacja — `warsztat.json` → `walidacja` (ruff), Z04
- P-07 CI — GitHub Actions: [workflow](../.github/workflows/ci.yml) — macierz Python 3.12/3.15 × Neo4j 2026.09.0/5.26 LTS z APOC, przebieg na najnowszym Pydantic 2.x, ruff względem `odniesienie.znane`, kontrola instalacji paczki — [aktualizacja-zaleznosci](zdolnosci/aktualizacja-zaleznosci/mapa.md) → Decyzje
- P-08 Konfiguracja i sekrety — `node4j/config.py` (pydantic-settings, prefiks `NODE4J_`, `.env`); brak `.env.example` — otwarte
- P-09 Bezpieczeństwo — Z02 (parametry w Cypher); audyt zależności — otwarte
- P-10 Dane osobowe — otwarte (logi DEBUG zawierają parametry zapytań, `node4j/db.py`)
- P-11 Błędy — otwarte
- P-12 Logi i obserwowalność — Z03
- P-13 Wydajność — otwarte
- P-14 Dostępność — pominięte: biblioteka bez interfejsu użytkownika
- P-15 Wersjonowanie — otwarte (stan: tagi `v0.2.0`–`v0.2.3`, (wniosek) semver)
- P-16 Historia zmian — otwarte (brak `CHANGELOG.md`)
- P-17 Dystrybucja i wdrożenie — później: dziś instalacja z gita, planowana publikacja w indeksie pakietów (uv/pip) — [readme-aktualne](zdolnosci/readme-aktualne/mapa.md) → Decyzje; koncepcja: [wydanie-pypi](zdolnosci/wydanie-pypi/mapa.md) (Mgła, obejmie też P-15, P-16, P-18)
- P-18 Wycofanie — otwarte
- P-19 Pielęgnacja — otwarte
- P-20 Dokumentacja użytkownika — README + `docs/` w EN i PL; przykłady wykonywane w teście na bazie z APOC i GDS, zgodność EN ↔ PL pilnowana automatem (dowiezione 2026-10-15) — [readme-aktualne](zdolnosci/readme-aktualne/mapa.md) → Decyzje
- P-21 Licencja i prawa — `LICENSE` (MIT)
- P-22 Dane trwałe — pominięte: biblioteka nie przechowuje własnych danych; schemat bazy tworzy `apply_schema` z `Meta`
- P-23 Git i GitHub — `warsztat.json` → `git`, `tracker`, `github`
- P-24 Testy mutacyjne — otwarte
