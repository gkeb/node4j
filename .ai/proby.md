## 2026-10-12 — Wywołania triggerów APOC z domyślnej bazy [aktualizacja-zaleznosci]

- Status: nierozwiazane
- Hasła: APOC, triggery, apoc.trigger.install, apoc.trigger.list, apoc.trigger.drop, baza system
- Warunki: testowy Neo4j 2025.05.1, potem 2026.09.0 i 5.26 ze sterownikiem 6.4 (CI, 2026-10-12 — ten sam wynik, kody błędów przypięte testami); wywołania przez globalne `connection` do domyślnej bazy `neo4j`.
- Wynik: `install`, `list` i `remove` rzucają `neo4j.exceptions.ClientError` na rzeczywistym połączeniu; przypięte testami w `tests/test_n1_relations_hooks_mixins_ext.py`.
- Wróć, gdy: osobna naprawa albo zdolność ustali kierowanie operacji triggerów do bazy `system`.
