## 2026-10-14 — `apoc.create.uuid()` w importerze APOC [readme-aktualne]

- Status: nie-dziala
- Hasła: APOC, `create_from_json`, `uid`, UUID, `randomUUID`, ADR 0003
- Warunki: Neo4j 2026.09.0 z APOC; `create_from_json` wykonuje tworzenie węzłów przez `apoc.periodic.iterate`.
- Wynik: zapytanie z `apoc.create.uuid()` kończyło się `Unknown function`; Cypher `randomUUID()` przechodzi na Neo4j 2026.09 i 5.26.
- Zamiast tego: w `create_from_json` używaj `randomUUID()` po stronie Neo4j zgodnie z wyjątkiem w [ADR 0003](decyzje/0003-tozsamosc-wezla-uid.md).
- Wróć, gdy: `randomUUID()` przestanie działać w obsługiwanej wersji Neo4j albo pojawi się potrzeba zmiany przepływu importu. [Raport](eksperymenty/2026-10-14-apoc-export-import.md)

## 2026-10-12 — Wywołania triggerów APOC z domyślnej bazy [aktualizacja-zaleznosci]

- Status: nierozwiazane
- Hasła: APOC, triggery, apoc.trigger.install, apoc.trigger.list, apoc.trigger.drop, baza system
- Warunki: testowy Neo4j 2025.05.1, potem 2026.09.0 i 5.26 ze sterownikiem 6.4 (CI, 2026-10-12 — ten sam wynik, kody błędów przypięte testami); wywołania przez globalne `connection` do domyślnej bazy `neo4j`.
- Wynik: `install`, `list` i `remove` rzucają `neo4j.exceptions.ClientError` na rzeczywistym połączeniu; przypięte testami w `tests/test_n1_relations_hooks_mixins_ext.py`.
- Wróć, gdy: osobna naprawa albo zdolność ustali kierowanie operacji triggerów do bazy `system`.

## 2026-10-12 — Dokumentacja jako generowana strona (MkDocs + GitHub Pages) [readme-aktualne]

- Status: odlozone
- Hasła: dokumentacja, MkDocs, GitHub Pages, docs
- Warunki: przepisanie README; pakiet niepublikowany (P-17 otwarte).
- Wynik: wybrano README + `docs/*.md` czytane na GitHubie — bez nowej zależności, budowania w CI i hostingu.
- Wróć, gdy: pakiet trafi na PyPI albo `docs/` przestanie się dać przeglądać na GitHubie (nawigacja, wyszukiwanie).

## 2026-10-13 — Przykłady w osobnych skryptach `.py` zamiast bloków Markdown [readme-aktualne]

- Status: odlozone
- Hasła: dokumentacja, przykłady, pytest, executable docs
- Warunki: rozważono osobne skrypty linkowane z dokumentacji wobec wykonywania bloków Pythona wyjętych z Markdown.
- Wynik: pozostają bloki Markdown, aby test uruchamiał kod widoczny i kopiowany przez czytelnika; osobne skrypty tworzyłyby drugie źródło przykładów.
- Wróć, gdy: ekstrakcja z Markdown będzie wymagać tak złożonej obsługi kontekstu lub znaczników pominięcia, że nie da się wiarygodnie wykonywać przykładów.
