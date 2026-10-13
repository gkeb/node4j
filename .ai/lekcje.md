# Lekcje

> Rozwiązane problemy: założenie — agenta albo nasze — okazało się fałszywe, i jak robimy teraz. Zapisuj od razu, niezależnie od tego, kto wykrył błąd. Ta sama przyczyna → dopisz wystąpienie, nie nową linijkę. Problem bez rozwiązania idzie do `proby.md`. Zasady: „Lekcje — czego się nauczyliśmy” w `kontrakt/pamiec.md`; format wpisu: „Lekcja — wpis w `lekcje.md`” w `kontrakt/formaty.md` — oba w katalogu pluginu warsztatu.

Ostatnie retro: 2026-10-12

<!-- - [obszar | zdolność | projekt] problem — założyliśmy X, okazało się Y → teraz Z (link do śladu). Wzorzec: plik. Wystąpienia: RRRR-MM-DD kto-wykrył; RRRR-MM-DD kto-wykrył -->

- [projekt] testy integracyjne nie uruchomią się same — założyliśmy, że lokalna Neo4j jest dostępna z góry, ale bazą testową jest jednorazowy kontener Docker `node4j-test` na porcie `7688` z APOC; gdy go nie ma, uruchamiamy go poleceniem z [AGENTS.md](../AGENTS.md), a brak bazy pomija testy (tryb `NODE4J_REQUIRE_TEST_DB=1` zgłasza błąd). `test.py` czyści całą bazę, więc służy wyłącznie do bazy testowej. Wystąpienia: 2026-10-13 użytkownik
- [aktualizacja-zaleznosci] `pytest.raises` nie zgłasza `AssertionError`, gdy oczekiwany wyjątek nie wystąpi — założyliśmy, że `except AssertionError` posprząta trigger po nieoczekiwanym sukcesie, ale pytest zgłasza własny typ błędu → sukces obsługujemy gałęzią `else`, wykonujemy sprzątanie i nie ukrywamy błędu usuwania. Wystąpienia: 2026-10-12 przegląd
- [readme-aktualne] same identyfikatory węzłów wystarczą do sprawdzenia sprzątania strony — zakładaliśmy, że niezmieniony zestaw ID oznacza niezmieniony graf, ale przykład może zmienić właściwości, etykiety, relacje albo usunąć istniejący węzeł; dodatkowo `elementId` nie jest stabilny między transakcjami według ADR 0003 → snapshotujemy pełny stan po unikalnym `uid`, odtwarzamy relacje po UID końców i sprawdzamy mutację oraz usunięcie danych bazowych ([test_documentation.py](../tests/test_documentation.py)). Wystąpienia: 2026-10-13 recenzja
- [readme-aktualne] `cwd` repozytorium wystarczy do importu z pliku tymczasowego — zakładaliśmy, że subprocess uruchomiony z `cwd=ROOT` znajdzie pakiet, ale Python używa katalogu skryptu jako `sys.path[0]` → runner dokumentacji dodaje korzeń projektu do `sys.path` i testuje import `node4j` ([test_documentation.py](../tests/test_documentation.py)). Wystąpienia: 2026-10-13 Codex
