# Badanie: URL-e i ścieżki w apoc.load.json i apoc.export.json.all (Neo4j 5.26 LTS i 2026.09), lokalizacja pliku, konfiguracja serwera

- Data: 2026-10-13
- Dla: [readme-aktualne](../zdolnosci/readme-aktualne/mapa.md)
- Kontekst: node4j, sterownik neo4j 6.4; oficjalny obraz Docker `neo4j:5.26` i `neo4j:2026.09.0` z `NEO4J_PLUGINS='["apoc"]'` (APOC Core), bez innych ustawień APOC
- Pewność: średnia (dokumentacja zgodna dla obu wersji; mapowanie zmiennych Docker → apoc.conf potwierdzone przykładem w dokumentacji, nie kodem entrypointu; kod APOC nie został odczytany z repozytorium w całości)

## Odpowiedź

Plik czyta i zapisuje proces serwera Neo4j (JVM z APOC), więc musi leżeć na maszynie/w kontenerze serwera, nie aplikacji. Domyślnie `apoc.import.file.enabled` i `apoc.export.file.enabled` mają wartość `false`, a `apoc.import.file.use_neo4j_config` ma `true`. Przy tych ustawieniach ścieżka jest rozwiązywana względem katalogu `import` (`server.directories.import`), a ścieżka absolutna poza nim nie działa. Konfigurację CI (`NEO4J_PLUGINS` bez ustawień APOC) wywołanie pliku kończy błędem „not enabled". Dokumentacja dla 5.26 i 2026.09 jest w tych punktach identyczna.

## Ustalenia

1. Schematy URL `apoc.load.json` (dokumentacja 5): `file`, `http`, `https`, `s3`, `gs`, `hdfs`; przekierowania dozwolone; S3/GCS/HDFS wymagają dodatkowych jarów w `plugins` i restartu. Bez protokołu procedura „will try to check whether the URL is actually a file". [1]
2. Przykłady plikowe używają `file:///person.json`; ścieżka jest względna wobec katalogu import: „Import files are read from the `import` directory, which is defined by the `server.directories.import` property." Ścieżka absolutna `/tmp/filename` kończy się błędem `Can’t read url or key file:/path/to/neo4j/import/tmp/filename as json … No such file or directory` — czyli `file:///tmp/x.json` jest traktowane jako `<import>/tmp/x.json`. [2][3]
3. Kod (FileUtils, gałąź 5.26, odczyt przez podsumowanie narzędzia): `resolvePath` przy `isImportFolderConfigured() && isImportUsingNeo4jConfig()` bierze `Paths.get(importDir)` jako bazę, normalizuje i rzuca `IOException` z komunikatem „You're providing a directory outside the import directory defined into `server.directories.import`", gdy wynik wychodzi poza katalog. W przeciwnym razie ścieżka jest użyta bez zmian. Ścieżka bez schematu: kod próbuje dopisać prefiks `file:///`. [4]
4. Ustawienia (doc config): `apoc.import.file.enabled` (domyślnie `false`, „Enables reading local files from disk"), `apoc.export.file.enabled` (domyślnie `false`, „Enables writing local files to disk"), `apoc.import.file.use_neo4j_config` (domyślnie `true`; sprawdza m.in. `dbms.security.allow_csv_import_from_file_urls` i `server.directories.import`). [5][1]
5. Gdzie ustawiać: od Neo4j 5 ustawienia APOC należą do `apoc.conf`, nie `neo4j.conf`; plik w tym samym katalogu co `neo4j.conf`, instalator go nie tworzy; zmienne środowiskowe mają pierwszeństwo przed `apoc.conf`. [5]
6. Docker: strona instalacji APOC pokazuje `docker run … -e NEO4J_apoc_export_file_enabled=true -e NEO4J_apoc_import_file_enabled=true -e NEO4J_apoc_import_file_use__neo4j__config=true -e NEO4J_PLUGINS=\[\"apoc\"\]` (przykład z obrazem `neo4j:2025.09`). Reguła nazewnictwa obrazu: prefiks `NEO4J_`, kropka → `_`, podkreślnik → `__`. [6][7]
7. `apoc.load.json` z URL http(s) nie wymaga ustawienia włączającego (`apoc.import.file.enabled` dotyczy plików lokalnych). Dokumentacja ostrzega przed SSRF: w Community „Configure the `internal.dbms.cypher_ip_blocklist` setting", w Enterprise load privileges z CIDR. Nie jest to lista dozwolonych hostów, tylko opcjonalna blokada. Strony nie wymieniają wymogu `dbms.security.allow_csv_import_from_file_urls` dla HTTP. [3][8]
8. Błąd, gdy import wyłączony: „Import from files not enabled, please set apoc.import.file.enabled=true in your apoc.conf" (klient dostaje wyjątek procedury Cypher/`ClientError` — kod Neo.* nie został potwierdzony w źródle). [2][3] Błąd eksportu: „Export to files not enabled, please set apoc.export.file.enabled=true in your apoc.conf." [9][10]
9. `apoc.export.json.all`: plik zapisywany w katalogu `server.directories.import` serwera, nazwa względna wobec niego; `/tmp/filename` kończy się `java.io.FileNotFoundException: /path/to/neo4j/import/tmp/fileName (No such file or directory)`. `apoc.import.file.use_neo4j_config=false` pozwala pisać gdziekolwiek (dokumentacja ostrzega). Alternatywa bez pliku: nazwa `null` i `{stream:true}` — dane w kolumnie `data`. [9][10]
10. Kod zapisu: `getOutputStream` używa `resolvePath(fileName).toFile()`, gdy `use_neo4j_config` jest true, inaczej `new File(getFileUrl(fileName))`. [4]
11. Różnice 5.26 vs 2026.09: strony `load-json` i `export/json` w wersjach `/5/` i `/current/` mają tę samą treść w zakresie powyższych punktów; nagłówki obu stron wymieniają „Version 2026.09 (Current)" i „Version 5.26 (LTS)". Różnic nie znaleziono. [2][3][9][10]
12. (wniosek) W CI bez ustawień APOC `CALL apoc.load.json('file:///…')` i `apoc.export.json.all('plik.json', …)` zakończą się błędem „not enabled". Żeby przykład działał w teście, trzeba przekazać do kontenera `NEO4J_apoc_import_file_enabled=true` (i `NEO4J_apoc_export_file_enabled=true` dla eksportu), a plik umieścić w katalogu import kontenera (domyślnie `/var/lib/neo4j/import` w obrazie — wartość niepotwierdzona w źródle tutaj) i podać go jako `file:///nazwa.json`. Przy użyciu `create_from_json` przez `apoc.periodic.iterate` plik jest czytany po stronie serwera, więc README „absolutna ścieżka do pliku" jest przy domyślnych ustawieniach nieprawdziwe (wniosek z 2 i 4).
13. (wniosek) Wariant z HTTP(S) nie wymaga ustawień plikowych, ale serwer Neo4j musi mieć dostęp sieciowy do hosta (np. kontener w CI do hosta aplikacji).

## Niepewności

- Nie odczytano literalnych nazw kluczy w `ApocConfig.java` (404 przy próbie pobrania); nazwy ustawień pochodzą z dokumentacji. Komunikat `ERROR_READ_FROM_FS_NOT_ALLOWED` w FileUtils wspomina `neo4j.conf` i inny klucz (`ALLOW_READ_FROM_FILESYSTEM`, prawdopodobnie `dbms.security.allow_csv_import_from_file_urls`) — gałąź wymaga zbadania, jeśli `use_neo4j_config=true` i ten ustawienie jest `false`.
- Kod FileUtils odczytano z gałęzi 5.26 (podsumowanie narzędzia, nie surowy tekst); dla 2026.x kodu nie sprawdzano.
- Nie potwierdzono kodem entrypointu obrazu, że `NEO4J_apoc_*` trafia do `apoc.conf` (dokumentacja pokazuje tylko, że zmienne działają i mają pierwszeństwo). Strona operations-manual o pluginach Docker nie wspomina o zmiennych APOC.
- Strona instalacji w `/current/` ma niespójności (przykład z `neo4j:2025.09`, wzmianka o `NEO4JLABS_PLUGINS` dla PowerShell).
- Dokładny kod/klasa błędu Neo4j po stronie klienta Python (np. `Neo.ClientError.Procedure.ProcedureCallFailed`) nie został potwierdzony.
- Domyślny katalog import w obrazie Docker i to, czy `dbms.security.allow_csv_import_from_file_urls` ma wpływ w obrazie, wymagają prototypu.
- Zachowanie `file:///C:/...` na Windowsie (poza obrazem Docker) niezbadane.

## Źródła

- [1] APOC: Load JSON (web APIs), wersja 5 — https://neo4j.com/docs/apoc/5/import/web-apis/ — dokumentacja — 5.x, pobrano 2026-10-13
- [2] APOC: Load JSON, wersja 5 — https://neo4j.com/docs/apoc/5/import/load-json/ — dokumentacja — 5.26 LTS, 2026-10-13
- [3] APOC: Load JSON, current — https://neo4j.com/docs/apoc/current/import/load-json/ — dokumentacja — 2026.09, 2026-10-13
- [4] APOC FileUtils.java — https://raw.githubusercontent.com/neo4j/apoc/5.26/common/src/main/java/apoc/util/FileUtils.java — kod — gałąź 5.26
- [5] APOC: Configuration Options — https://neo4j.com/docs/apoc/5/config/ oraz https://neo4j.com/docs/apoc/current/config/ — dokumentacja — 5.x i 2026.09 (zawartość pobrana z `/5/`)
- [6] APOC: Installation — https://neo4j.com/docs/apoc/current/installation/ — dokumentacja — 2026.09
- [7] Neo4j Operations Manual: Docker, modyfikacja konfiguracji — https://neo4j.com/docs/operations-manual/current/docker/configuration/ (informacja o regule nazewnictwa z wyniku wyszukiwania 2026-10-13, strony nie pobrano w całości; niepotwierdzone bezpośrednio)
- [8] apoc.load.json (procedura), current i 5 — https://neo4j.com/docs/apoc/current/overview/apoc.load/apoc.load.json oraz https://neo4j.com/docs/apoc/5/overview/apoc.load/apoc.load.json — dokumentacja
- [9] APOC: Export JSON, 5 — https://neo4j.com/docs/apoc/5/export/json/ — dokumentacja — 5.26
- [10] APOC: Export JSON, current — https://neo4j.com/docs/apoc/current/export/json/ — dokumentacja — 2026.09
- [11] Neo4j Operations Manual: Docker plugins — https://neo4j.com/docs/operations-manual/current/docker/plugins/ — dokumentacja — 2026.09
