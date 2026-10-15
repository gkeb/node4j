# README aktualne — odbiór

> Lista dla człowieka: co przeklikać i sprawdzić na prawdziwym środowisku, zanim zdolność będzie gotowa. Tylko to, czego testy nie sprawdzą — nie powtarzaj zielonych testów. Przygotowuje skill `zamknij`, przechodzi człowiek. Format: „Odbiór — sprawdzenie przez człowieka” w `kontrakt/praca.md` w katalogu pluginu warsztatu.

Środowisko: GitHub (`github.com/gkeb/node4j`, gałąź `main`) oraz czysty katalog poza repozytorium z własną bazą Neo4j · commit `c9a66e0` (ostatni commit z treścią: `1405785`)

## Przeklikaj

- [ ] S1 na GitHubie: otwórz `README.md` w podglądzie repozytorium → kolejno: czym jest biblioteka, wymagania, instalacja, szybki start, dokumentacja; każdy link do strony tematycznej się otwiera. Testy sprawdzają pliki, a nie renderowanie GitHuba.
- [ ] Kotwice z polskimi znakami na GitHubie: w `README_PL.md` kliknij link „rozwiązywanie problemów z połączeniem” → strona przewija się do sekcji (test liczy kotwice własnym algorytmem, nie algorytmem GitHuba). To samo dla linku do „Troubleshoot Neo4j connection errors” w `README.md`.
- [ ] Przełącznik języka i link powrotny: na 2–3 stronach `docs/en/` i `docs/pl/` (np. APOC, GDS, znane ograniczenia) przełącznik prowadzi do odpowiednika, a link powrotny do właściwego README.
- [ ] S8 i szybki start „po skopiowaniu”: w nowym katalogu poza repozytorium zainstaluj bibliotekę poleceniem z README (`uv add git+https://github.com/gkeb/node4j` albo `pip install git+…`), utwórz `.env` z `NODE4J_URI`, `NODE4J_USER`, `NODE4J_PASSWORD` dla swojej bazy (nie produkcyjnej) i uruchom `quickstart.py` skopiowany z README → wynik jak opisany w README, bez instalowania dodatkowych pakietów i bez `load_dotenv`.
- [ ] Stan „Błąd” — brak połączenia: uruchom `quickstart.py` z `NODE4J_URI` wskazującym port, na którym nic nie nasłuchuje → komunikat `ServiceUnavailable` odpowiada opisowi w `docs/en/configuration-and-logging.md`, a krok „co zrobić” pomaga (komunikatu nie przypina żaden test — R2.3).
- [ ] S6 i proza PL: przeczytaj „Znane ograniczenia” w obu językach i wyrywkowo 2 inne strony PL obok EN → ta sama treść, polski czytelny (równoważność prozy sprawdza tylko człowiek, decyzja „Zgodność EN ↔ PL”).

## Środowisko i dane

- [ ] Komenda bazy testowej z `AGENTS.md` (APOC i GDS, import/eksport plików) uruchamia się w PowerShell na tej maszynie i `CALL gds.version()` odpowiada — sprawdzone przy weryfikacji R3 na `neo4j:2026.09.0`; tu tylko potwierdzenie, jeśli używasz LTS `neo4j:5.26`.
- [ ] Ustawienia Dockera dla APOC z `docs/en/apoc-extensions.md` (`NEO4J_PLUGINS`, `NEO4J_apoc_import_file_enabled=true`, `NEO4J_apoc_export_file_enabled=true`) wklejone do własnej komendy `docker run` dają działający `await apoc.version()`.
- [ ] Katalog import kontenera testowego: po przykładach APOC zostają pliki `node4j-apoc-*.json` (ryzyko zapisane w specu) — kontener jest jednorazowy (`--rm`), więc nic nie zostaje po `docker stop`.

## Czego nie da się sprawdzić tutaj

- Instalacja z indeksu pakietów (PyPI) — dokumentacja podaje dziś instalację z gita; zmienia ją krok wydania (`wydanie-pypi` w Mgle).
- Rozjazd wersji w tagu `v0.2.3` i w metadanych pakietu — poza zakresem, krok wydania.

## Wynik

Odbiór: 2026-10-15 — użytkownik — przeszedł
