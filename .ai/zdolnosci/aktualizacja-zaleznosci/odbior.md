# Aktualizacja zależności — odbiór

> Lista dla człowieka: co przeklikać i sprawdzić na prawdziwym środowisku, zanim zdolność będzie gotowa. Tylko to, czego testy nie sprawdzą — nie powtarzaj zielonych testów. Przygotowuje skill `zamknij`, przechodzi człowiek. Format: „Odbiór — sprawdzenie przez człowieka” w `kontrakt/praca.md` w katalogu pluginu warsztatu.

Środowisko: Twój projekt korzystający z node4j (albo nowy katalog poza repo) i Twoja baza dev Neo4j — nie kontener testowy · commit 4e84cab (kod zdolności; późniejsze commity zmieniają tylko `.ai/`)

Testy N1–N3, TTL, `test.py`, budowa paczki i import po instalacji są zielone w CI na Python 3.12/3.15 × Neo4j 2026.09/5.26 ([run 38292868940](https://github.com/gkeb/node4j/actions/runs/38292868940)) — tego nie powtarzasz.

## Przeklikaj

- [x] Instalacja obok Twojego stosu: w osobnym venv projektu, który używa node4j, zainstaluj node4j z tego repo (`uv pip install <ścieżka do repo>` albo `uv add --editable <ścieżka>`) → resolver nie zgłasza konfliktu, a `uv pip list` pokazuje `neo4j 6.x`, `pydantic 2.x`, `pydantic-settings 2.x`, bez `pytest` i `structlog` (o ile Twój projekt sam ich nie wymaga)
- [x] Twój kod z modelami `Node` uruchamia się bez zmian na nowej wersji: start aplikacji albo skryptu, kilka typowych operacji (`create`, `match_all` z filtrem, relacja) → te same wyniki co wcześniej, brak ostrzeżeń i wyjątków przy imporcie
- [x] Dane zapisane starą wersją (sterownik 5.28) na Twojej bazie dev: odczytaj kilka istniejących węzłów przez `.q.match_one` / `.q.match_all` → `uid` i daty wczytują się jak wcześniej, bez migracji (N2)

## Środowisko i dane

- [x] Wersja serwera Twojej bazy dev: `CALL dbms.components()` → 2026.x albo 5.26 LTS; starsza linia 5.x nie jest objęta macierzą CI (np. lokalny obraz `neo4j:5.15`) — zanotuj, jeśli na niej zostajesz
- [x] `.env` w katalogu Twojego projektu z `NODE4J_URI` / `NODE4J_USER` / `NODE4J_PASSWORD` → `node4j.config.settings` ma te wartości, a zmienna środowiska ma pierwszeństwo przed `.env` (N3, na prawdziwym katalogu roboczym)

## Czego nie da się sprawdzić tutaj

- Instalacja z PyPI — wydanie jest poza zakresem (skill `wydaj`); metadane paczki sprawdza dopiero publikacja.
- Python 3.13 i 3.14 — macierz obejmuje tylko 3.12 i 3.15.
- Zgodność `ext.gds` z wtyczką GDS — poza zakresem zdolności.

## Wynik

Odbiór: 2026-10-12 — Grzegorz (na podstawie sprawdzenia agenta poniżej) — przeszedł

Kontekst (Grzegorz, 2026-10-12): biblioteka powstaje samodzielnie — nie ma jeszcze aplikacji, danych ani użycia produkcyjnego, więc odbiór na świeżym projekcie poza repo jest jedynym dostępnym środowiskiem. Kontener `my-knowledge-graph-db` (2025.05.1) nie jest bazą node4j.

Sprawdzenie na katalogu poza repo (`%TEMP%\node4j-odbior-app`, Python 3.12.9) i osobnej bazie Docker `neo4j:2026.09.0`. Kod biblioteki jest taki jak w `4e84cab` (późniejsze commity nie zmieniają plików poza `.ai/`). Kontener zatrzymany po teście.

- Instalacja: `uv add --editable C:\rust\node4j` w świeżym projekcie rozwiązało zależności bez konfliktu. `uv pip list`: `neo4j` 6.4.0, `pydantic` 2.14.1, `pydantic-settings` 2.15.0. Brak `pytest` i `structlog`. Jest `python-dotenv` 1.2.4 jako zależność przechodnia `pydantic-settings`, nie jako zależność aplikacji.
- Operacje na modelach `Node` z tego katalogu (nie na `node4j.models`): `create`, `match_all` z filtrem `priority__gte` i `title__startswith`, relacja `ON_DESK` z właściwością. Zwrócone wartości są zgodne z zapisanymi. Import bez ostrzeżeń i wyjątków. Nie było wcześniejszego przebiegu tej aplikacji, z którym dałoby się porównać wyniki.
- Dane starego sterownika: node4j z commita `b702527` (zależność `neo4j` 5.28.1) zapisał na tej bazie trzy węzły. Bieżący node4j (sterownik 6.4.0) odczytał je przez `.q.match_one` i `.q.match_all`: `uid` oraz data naiwna (`2024-02-03T04:05:06`) i data ze strefą (`+02:00`) bez migracji. To dane zapisane w tej sesji na świeżej bazie, nie zastany stan długo działającej bazy.
- Serwer: `CALL dbms.components()` → Neo4j Kernel 2026.09.0 community, Cypher 5 i 25. Kontener `node4j-odbior-2026`, Bolt `127.0.0.1:7697`. To nie jest kontener testowy CI (`node4j-test` na porcie 7688).
- Już uruchomiony kontener `my-knowledge-graph-db` (obraz `neo4j:2025.05.1`, porty 7474 i 7687) nie był ruszany. Linia 2025.05 nie jest w macierzy CI (tam są 2026.09 i 5.26 LTS).
- Konfiguracja: `.env` w katalogu aplikacji. `node4j.config.settings` ma URI, użytkownika i hasło z tego pliku. Przy `NODE4J_URI=bolt://environment.example:7697` URI bierze się ze środowiska, a użytkownik i hasło zostają z `.env`. Import bez ostrzeżeń.
