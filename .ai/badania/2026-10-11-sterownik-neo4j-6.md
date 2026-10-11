# Badanie: Sterownik Python neo4j 6.x względem 5.28 — zmiany łamiące dla asynchronicznego OGM, wersja Pythona, wsparcie serwerów, najnowsze wydanie serwera

- Data: 2026-10-11
- Dla: [aktualizacja-zaleznosci](../zdolnosci/aktualizacja-zaleznosci/mapa.md)
- Kontekst: projekt node4j, `neo4j>=5.28.1` (lock 5.28.1), najnowszy na PyPI 6.4.0, requires-python >=3.12, testy na obrazie neo4j:2025.05.1
- Pewność: średnia (zmiany sterownika: wysoka co do wymienionych pozycji; daty wsparcia serwera: średnia)

## Odpowiedź

(1) Żadna z wymienionych przez Ciebie pozycji asynchronicznego API (`AsyncGraphDatabase.driver`, `basic_auth`, `verify_connectivity`, `AsyncSession.run`, `AsyncResult.data()`, jawne `begin_transaction`/`commit`/`rollback`/`closed`, typy `neo4j.time`, `to_native()`, `element_id`) nie jest w changelogu 6.0 wymieniona jako usunięta lub zmieniona w sposób łamiący. Zmiany łamiące, które mogą dotknąć kodu, to: zmiany wyjątków przy niektórych błędach (nie zmieniono klas `ConstraintError`/`CypherSyntaxError`/`ServiceUnavailable`, ale DNS i timeouty zmieniły typ), `DriverError` przy użyciu zamkniętego drivera, brak zamykania w `__del__`, usunięcie importów podmodułów `neo4j.time.*`. (2) Minimum Pythona dla 6.x: 3.10. (3) Dokumentacja podręcznika sterownika 6.x deklaruje zgodność z serwerem 4.4, 5.x i 2025.x/2026.x (czyli obejmuje 5.26 i wydania kalendarzowe); macierz w KB Neo4j nie została odczytana. (4) Najnowsze wydanie serwera na dziś: 2026.09.0 (21.09.2026); 5.26 LTS nadal wspierany (5.26.32 z 9.10.2026), poprawki do 6.06.2028 wg KB (przez wyszukiwarkę).

## Ustalenia

1. Min. Python w 6.0.0: 3.10; porzucone 3.7–3.9 [2]. Dokumentacja 6.4 wymienia Pythona 3.10–3.15 [4]. Projekt (>=3.12) spełnia wymóg. [2][4]
2. Transakcje: `read_transaction`/`write_transaction` usunięte na rzecz `execute_read`/`execute_write`; transakcje zarządzane (`ManagedTransaction`) nie mają `commit`/`rollback`/`close`/`closed` — to zmiana z 5.0, a nie z 6.0 [1][3]. Jawna transakcja z `session.begin_transaction()` (AsyncTransaction) nie jest wymieniona jako zmieniona; w dokumentacji async API brak notek „Changed in 6.0” przy `commit`/`rollback`/`closed` w odczytanej części (strona obcięta, 42 kB nieprzeczytane) [5]. Brak notki w odczytanym fragmencie to nie dowód braku zmiany (wniosek).
3. Nowość 6.0 dla `session.run`/`Transaction.run`: wywołanie `session.run()` podczas aktywnej jawnej transakcji rzuca `TransactionError` (`DriverError`) zamiast `ClientError`; przekazanie obiektu `Query` do `Transaction.run` rzuca `TypeError` zamiast `ValueError` [2].
4. `AsyncDriver.verify_connectivity`: „Changed in version 6.0: Raise DriverError if the driver has been closed” (dotyczy też `session`, `execute_query`, `get_server_info` itd.). Zwracana wartość usunięta już w 5.0 [5][2].
5. Cykl życia: drivery i sesje nie są już zamykane w `__del__()`; trzeba `close()`/`async with` (inaczej `ResourceWarning`). Użycie zamkniętego drivera → `DriverError`; ponowne `close()` jest no-op [1][2].
6. Wyjątki: `ServiceUnavailable` — błąd rozwiązywania DNS daje teraz retryable `ServiceUnavailable` zamiast `ValueError`. Timeout pozyskania połączenia → `ConnectionAcquisitionTimeoutError` (`DriverError`) zamiast `ClientError`. Błędny `auth` → `ConfigurationError` zamiast `AuthError`. `Neo4jError.message` i `.code` zawsze `str`. `Neo4jError.is_retriable()` usunięte (jest `is_retryable()`). `UnsupportedServerProduct` zastąpił `BoltHandshakeError` [2][1]. Dla `ConstraintError`, `CypherSyntaxError`, `ClientError` (jako klas błędów serwera) changelog nie podaje zmian.
7. Typy `neo4j.time` (`DateTime/Date/Time/Duration`, `to_native()`): changelog 6.0 nie usuwa ich ani `to_native()`. Zmiany: nieobsługiwane porównania zwracają `NotImplemented`; importy podmodułów `neo4j.time.*` usunięte (importować z `neo4j.time`); elementy wewnętrzne `neo4j.time` uprywatnione; `ClockTime` zdeprecjonowane [1][2]. Poprawka przepełnienia `DateTime` z ujemnym `Duration` jest w 5.28.4 [3].
8. `element_id`: indeksowanie zbiorów encji grafu po liczbowym `id` usunięte (użyć stringowego `element_id`); `Node.id`/`Relationship.id` zdeprecjonowane, nieusunięte [1][2]. Funkcja Cypher `elementId()` to sprawa serwera, nie sterownika.
9. `AsyncGraphDatabase.driver`/`basic_auth`/`AsyncResult.data()`: brak zmian w changelogu 6.0; `basic_auth` nadal istnieje jako pomocnik `Auth` [6]. `trust` (i stałe `TRUST_*`) usunięte → `trusted_certificates`/`ssl_context`; `bolt://` z kontekstem routingu → `ConfigurationError` [1][2]. `AsyncResult.data()` nie sprawdzone w dokumentacji (poza odczytanym zakresem).
10. Po 6.0: 6.2 dodaje automatyczne jednorazowe ponowienie niektórych błędów w `session.run` (wyłączane `disable_auto_commit_retries`); 6.3.1 naprawia desynchronizację `Result` użytego po zamknięciu sesji; 6.4.0 dodaje Pythona 3.15 i podgląd HTTP Query API [2]. Poprawki 6.3.1/6.4.0 są też w 5.28.6/5.28.7 (5.28.7 wycofany z PyPI) [3].
11. Serwery: podręcznik sterownika: „Driver 6.x is compatible with Neo4j server 4.4, 5.x, and 2025.x/2026.x” [1]. Dokumentacja API 6.4 wymienia Bolt 6.0–6.1, 5.0–5.8, 4.4, a mapowanie na wersje serwera odsyła do KB [4]. README nie podaje wersji serwerów [7].
12. Najnowsze wydania serwera (Deployment Center, 2026-10-11): 2026.09.0 z 21.09.2026 oraz 5.26.32 z 9.10.2026 [8]. Dokumentacja operacyjna oznacza 2026.09 jako „Current”, a 5.26 jako „LTS”; 2025.01 to pierwsze wydanie po 5.26 LTS [9].
13. Wsparcie 5.26 LTS: wyszukiwarka cytuje KB Neo4j: „5.26 LTS, December 6, 2024, hotfixes until June 6, 2028”; wydania kalendarzowe nie-LTS są wspierane tylko do następnego wydania; 5.26 to ostatnie 5.x [10]. Treści strony KB nie odczytałem bezpośrednio (portal się nie załadował) (wniosek: 5.26 jest nadal wspierany).

## Niepewności

- Macierz zgodności sterownik–serwer w KB Neo4j nie została odczytana bezpośrednio; deklaracja 6.x ↔ serwery oparta o podręcznik [1]. Czy 6.x jawnie testuje 5.26 i 2026.x — poza zdaniem z [1] bez potwierdzenia.
- Data końca wsparcia 5.26 (6.06.2028) pochodzi z podsumowania wyszukiwarki, nie z odczytanej strony; potwierdzić na stronie KB.
- Dokumentacja async API przeczytana tylko w pierwszych 100 tys. znaków z 142 tys.; `AsyncResult.data()` i pełne notki `AsyncTransaction` nie zweryfikowane. Pełny changelog 6.x też mógł być streszczony przez narzędzie; zalecany prototyp: uruchomić testy na 6.4.0 z `-W error::ResourceWarning`.
- Przy `begin_transaction` warto sprawdzić: czy kod nie wywołuje `session.run` w trakcie otwartej transakcji (nowy `TransactionError`) i czy łapie `ClientError` przy timeoutach/DNS (inne klasy w 6.0).
- Lista wydań sprawdzona tylko na Deployment Center; „najnowsze” wg stanu strony.

## Źródła

- [1] Upgrade / Migrate — https://neo4j.com/docs/python-manual/current/upgrade/ — dokumentacja — 6.x
- [2] Python driver 6.x changelog — https://github.com/neo4j/neo4j-python-driver/wiki/6.x-changelog — changelog — 6.0.0–6.4.0
- [3] Python driver 5.x changelog — https://github.com/neo4j/neo4j-python-driver/wiki/5.x-changelog — changelog — 5.28.x
- [4] Python driver API docs (strona główna, kompatybilność) — https://neo4j.com/docs/api/python-driver/current/ — dokumentacja — 6.4
- [5] Async API — https://neo4j.com/docs/api/python-driver/current/async_api.html — dokumentacja — 6.4 (odczyt częściowy)
- [6] API (Auth, basic_auth, sync) — https://neo4j.com/docs/api/python-driver/current/api.html — dokumentacja — 6.4 (odczyt częściowy)
- [7] README — https://github.com/neo4j/neo4j-python-driver — repozytorium — 6.x
- [8] Neo4j Deployment Center — https://neo4j.com/deployment-center/ — lista wydań — stan 2026-10-11
- [9] Operations Manual (changes, deprecations) — https://neo4j.com/docs/operations-manual/current/changes-deprecations-removals/ — dokumentacja — 2026.09
- [10] Neo4j Supported Versions (KB, przez wyszukiwarkę) — https://neo4j.com/developer/kb/neo4j-supported-versions/ ; blog https://neo4j.com/blog/developer/neo4j-v5-lts-evolution/ — KB/blog — niepotwierdzone bezpośrednio
