# Badanie: Zgodność GDS z Neo4j 5.26 LTS i 2026.09, instalacja w Dockerze, sygnatury procedur używanych przez node4j

- Data: 2026-10-13
- Dla: [readme-aktualne](../zdolnosci/readme-aktualne/mapa.md)
- Kontekst: node4j (Python, sterownik neo4j 6.4); `node4j/ext/gds.py`; CI z `NEO4J_PLUGINS: '["apoc"]'` na `neo4j:2026.09.0` i `neo4j:5.26`, GDS w CI nieuruchamiane. Dokumentacja pobrana 2026-10-13 (strony „current” = 2026.09 wg selektora wersji [4]).
- Pewność: średnia (macierz, sygnatury i `failIfMissing` potwierdzone w dokumentacji; brak sprawdzenia w działającym obrazie)

## Odpowiedź

Neo4j 5.26 jest sparowany wyłącznie z GDS 2.13, a Neo4j 2026.09.0 z GDS 2026.09. `NEO4J_PLUGINS='["graph-data-science"]'` jest udokumentowaną nazwą pluginu w obrazie Dockera (Operations Manual 5 i current). GDS Community jest domyślne, bez licencji, z limitem współbieżności do 4 rdzeni; Enterprise wymaga pliku licencji. Wszystkie wywołania z `gds.py` mają w dokumentacji GDS 2.13 i 2026.09 zgodne sygnatury, a `gds.graph.drop` na nieistniejącym grafie domyślnie rzuca błąd.

## Ustalenia

Macierz zgodności
1. Źródło mówi: `5.26` ↔ GDS `2.13`; `2026.09.0` ↔ GDS `2026.09`. Strona dodaje: „In general, the latest version of GDS supports the latest version of Neo4j and vice versa" oraz „If your version of GDS or Neo4j is not listed in the matrix, you should upgrade." [1]
2. Źródło mówi: dla 5.26 w macierzy jest tylko GDS 2.13 (inne wpisy to 2025.01–2026.02 → 2.14–2.27 oraz 2026.03–2026.09 → kalendarzowe wersje GDS). [1]
3. Źródło mówi: selektor wersji dokumentacji GDS sięga od „Version 2026.09” w dół do 2.5, czyli GDS przeszło z numeracji 2.x na kalendarzową (2026.03+). [4] (zmiana numeracji widoczna także w macierzy [1])

Instalacja w Dockerze
4. Źródło mówi: `NEO4J_PLUGINS` to „JSON-formatted list of the supported plugins”; poprawne nazwy w komunikacie błędu: `apoc`, `apoc-extended`, `bloom`, `genai`, `graph-data-science`, `n10s`; `["gds"]` daje „not a known Neo4j plugin”. Mechanizm „is not recommended for production environments”. Te same informacje na stronie Operations Manual `5` i `current`. [2][3]
5. Źródło mówi: GDS jest „available as a plugin for Neo4j on Docker”; przykład Community: `--env NEO4J_PLUGINS='["graph-data-science"]'` z obrazem `neo4j:latest`, bez konfiguracji licencji. [5]
6. Źródło mówi: Enterprise — obraz `neo4j:enterprise`, `NEO4J_ACCEPT_LICENSE_AGREEMENT=yes`, `NEO4J_gds_enterprise_license__file=/licenses/gds` i zamontowany katalog z licencją GDS (`$HOME/neo4j/licenses`). Wg Operations Manual licencje trzeba dostarczyć także przy użyciu `NEO4J_PLUGINS`. [2][5]
7. Źródło mówi: instalacja ręczna jest opisana „for both the Neo4j Enterprise Edition and Neo4j Community Edition” (JAR w katalogu `plugins`, `dbms.security.procedures.unrestricted=gds.*`). [6]
8. Wniosek: dla `neo4j:5.26` i `neo4j:2026.09.0` (Community) wzorzec z pkt 5 jest wg dokumentacji właściwy; strona Dockera GDS nie wymienia wersji Neo4j (używa `latest`), więc działanie na konkretnych tagach nie jest tu potwierdzone w źródle.

Community vs Enterprise
9. Źródło mówi: Community jest domyślne, „Provides every algorithm”, ogranicza katalog do zarządzania grafami i modelami, „Limits the concurrency to maximum 4 CPU cores”, limit 3 modeli. Enterprise: „a valid Neo4j Graph Data Science Enterprise license file is required”; bez limitu rdzeni, backup/restore grafów, Apache Arrow, nieograniczona liczba modeli. [7]

Sygnatury (GDS 2.13 dla Neo4j 5.26; „current” 2026.09)
10. `gds.graph.project(graphName, nodeProjection, relationshipProjection, configuration)` — trzy pierwsze wymagane, `configuration` opcjonalna (Map). Identycznie w 2.13 i current. Wywołanie w `gds.py` z trzema argumentami jest więc zgodne. Zwraca m.in. `graphName, nodeCount, relationshipCount, projectMillis`. [8][9]
11. `gds.graph.drop(graphName: String or List, failIfMissing: Boolean, dbName, username)`. Wywołanie `CALL gds.graph.drop($graph_name)` jest zgodne w obu wersjach. [10][11]
12. `failIfMissing` domyślnie `true`: „By default, the library will raise an error when trying to remove a non-existing graph.” Przy `false` zwracany jest pusty wynik. (Strona current nie podaje wartości domyślnej wprost, tylko „true” w kolumnie Optional i powyższy opis; 2.13 tak samo.) [10][11]
13. `gds.pageRank.stream(graphName, configuration)` → `nodeId, score`; `gds.pageRank.mutate(graphName, configuration)` → m.in. `nodePropertiesWritten, ranIterations, didConverge, mutateMillis, centralityDistribution, configuration`. `mutateProperty` jest wymagane w konfiguracji mutate. Zgodne w 2.13 i current. [12][13]
14. Wniosek: `GDS.Algo.run` i `GDS.Algo.mutate` (`CALL {algo}($graph_name, $config)`) pasują do tej sygnatury; `mutate` wymaga `mutateProperty` w `config`, inaczej błąd walidacji konfiguracji (wniosek z oznaczenia „wymagane”, nie z testu). Brak `YIELD` jest dopuszczalny dla samodzielnego `CALL` (wniosek z ogólnych zasad Cypher, niesprawdzone w tej dokumentacji).
15. Źródło mówi: strony `gds.graph.project` (native), `gds.graph.drop`, `gds.pageRank.*` w current nie zawierają informacji o deprecjacjach. [9][10][12]
16. Źródło mówi: osobno istnieje „Cypher projection” jako funkcja agregująca `RETURN gds.graph.project(graphName, sourceNode, targetNode, dataConfig, configuration)`. To inna forma niż procedura `CALL gds.graph.project(...)` (native projection) używana w node4j; strona nie mówi o zastąpieniu procedury. [14]

## Niepewności

- Nie uruchomiono GDS w obrazie: faktyczne zainstalowanie GDS 2.13 w `neo4j:5.26` i GDS 2026.09 w `neo4j:2026.09.0` przez `NEO4J_PLUGINS` (pobieranie pluginu przez skrypt obrazu) nie zostało zweryfikowane; dokumentacja tego dla konkretnych tagów nie gwarantuje.
- Najnowsze wydanie GDS 2.x dla 5.26 według macierzy to 2.13, ale numer patch (2.13.x) nie jest podany; sprawdzenie wymagałoby strony wydań lub changeloga.
- Strona macierzy ma zduplikowany wiersz 2025.11.2 i niespójność dokumentacji (`aggregation` NONE vs DEFAULT w przykładach projekcji) — drobne, bez wpływu na node4j.
- Dokumentacja current nie podaje wprost, czy `gds.graph.drop` w 2026.09 zachowuje domyślne `failIfMissing=true` poza zapisem w tabeli; zachowanie runtime niepotwierdzone testem.
- Dokumentacja nie wymienia różnic zachowania procedur między 2.13 a 2026.09 poza sygnaturami; pełny changelog GDS nie został przeczytany.
- Pobieranie stron odbyło się przez narzędzie streszczające treść, nie surowy HTML; cytaty pochodzą z jego odpowiedzi.

## Źródła

[1] GDS: Supported Neo4j versions — https://neo4j.com/docs/graph-data-science/current/installation/supported-neo4j-versions/ — dokumentacja — current (2026.09), pobrane 2026-10-13
[2] Operations Manual: Docker plugins — https://neo4j.com/docs/operations-manual/current/docker/plugins/ — dokumentacja — current, 2026-10-13
[3] Operations Manual 5: Docker plugins — https://neo4j.com/docs/operations-manual/5/docker/plugins/ — dokumentacja — 5.x, 2026-10-13
[4] GDS: Installation overview — https://neo4j.com/docs/graph-data-science/current/installation/ — dokumentacja — current, 2026-10-13
[5] GDS: Installation on Docker — https://neo4j.com/docs/graph-data-science/current/installation/installation-docker/ (oraz https://neo4j.com/docs/graph-data-science/2.13/installation/installation-docker/) — dokumentacja — current i 2.13, 2026-10-13
[6] GDS: Neo4j Server installation — https://neo4j.com/docs/graph-data-science/current/installation/neo4j-server/ — dokumentacja — current, 2026-10-13
[7] GDS: Introduction (editions) — https://neo4j.com/docs/graph-data-science/current/introduction/ — dokumentacja — current, 2026-10-13
[8] GDS: graph project — https://neo4j.com/docs/graph-data-science/2.13/management-ops/graph-creation/graph-project/ — dokumentacja — 2.13, 2026-10-13
[9] GDS: graph project — https://neo4j.com/docs/graph-data-science/current/management-ops/graph-creation/graph-project/ — dokumentacja — current, 2026-10-13
[10] GDS: graph drop — https://neo4j.com/docs/graph-data-science/current/management-ops/graph-drop/ — dokumentacja — current, 2026-10-13
[11] GDS: graph drop — https://neo4j.com/docs/graph-data-science/2.13/management-ops/graph-drop/ — dokumentacja — 2.13, 2026-10-13
[12] GDS: PageRank — https://neo4j.com/docs/graph-data-science/current/algorithms/page-rank/ — dokumentacja — current, 2026-10-13
[13] GDS: PageRank — https://neo4j.com/docs/graph-data-science/2.13/algorithms/page-rank/ — dokumentacja — 2.13, 2026-10-13
[14] GDS: Cypher projection — https://neo4j.com/docs/graph-data-science/current/management-ops/graph-creation/graph-project-cypher-projection/ — dokumentacja — current, 2026-10-13
[15] Kod lokalny — C:\rust\node4j\node4j\ext\gds.py — kod — stan repo 2026-10-13
