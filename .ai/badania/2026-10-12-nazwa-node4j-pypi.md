# Badanie: Czy nazwa `node4j` jest wolna w PyPI (można pod nią opublikować pakiet)?

- Data: 2026-10-12
- Dla: [readme-aktualne](../zdolnosci/readme-aktualne/mapa.md)
- Kontekst: `pyproject.toml` → `name = "Node4j"`, `version = "0.2.2"`; pakiet dziś tylko z gita (github.com/gkeb/node4j); planowana publikacja na PyPI
- Pewność: średnia

## Odpowiedź

Na dzień 2026-10-12 JSON API i Simple API pypi.org zwracają 404 dla `node4j` — nie ma tam projektu o tej znormalizowanej nazwie. Te same endpointy TestPyPI też zwracają 404. Strony HTML (`/project/node4j/`) nie udało się odczytać (blokada "Client Challenge"), więc nie ma potwierdzenia ze strony. Nie wykryłem sprawdzalnego powodu odrzucenia: dostępne źródła nie pozwalają jednak wykluczyć listy nazw zabronionych ani reguły "too similar" (patrz Niepewności). Ostateczny test to próba wysłania pakietu (np. na TestPyPI).

## Ustalenia

Fakty (źródło mówi X):

1. `GET https://pypi.org/pypi/node4j/json` → HTTP 404 Not Found (sprawdzone 2026-10-12). [1]
2. `GET https://pypi.org/simple/node4j/` → HTTP 404 Not Found (2026-10-12). [2]
3. `https://pypi.org/project/node4j/` → zamiast strony projektu lub 404 zwrócono stronę "Client Challenge" (wymaga przeglądarki/JS); nie zawiera danych o projekcie. Ten adres nie rozstrzyga niczego (2026-10-12). [3]
4. TestPyPI: `https://test.pypi.org/pypi/node4j/json` → 404 i `https://test.pypi.org/simple/node4j/` → 404 (2026-10-12). Strona `https://test.pypi.org/project/node4j/` zwróciła tę samą blokadę klienta co pypi.org. [4][5]
5. Normalizacja nazw (PEP 503 / specyfikacja pypa): "The name should be lowercased with all runs of the characters `.`, `-`, or `_` replaced with a single `-` character." Poprawna nazwa: "A valid name consists only of ASCII letters and numbers, period, underscore and hyphen." (sprawdzone 2026-10-12). [6]
6. Wniosek z pkt 5: `Node4j`, `NODE4J` normalizują się do `node4j` (czyli nazwa w `pyproject.toml` `Node4j` jest tą samą nazwą); `node-4j`, `node_4j`, `node.4j` normalizują się do `node-4j` — to inna nazwa, nie `node4j`. (wniosek)
7. Warehouse (kod `ProjectService.check_project_name`, gałąź main, sprawdzone 2026-10-12) odrzuca nową nazwę, gdy: (a) nie pasuje do wzorca nazwy, (b) koliduje z modułem biblioteki standardowej, (c) znormalizowana nazwa istnieje (`ProjectNameUnavailableExistingError`), (d) jest na liście `ProhibitedProjectName` ("isn't allowed"), (e) `ultranormalize_name(Project.name) == ultranormalize_name(name)` ("too similar to an existing project"). [7]
8. Reguła "similar" w kodzie to równość po `ultranormalize_name`, nie odległość edycyjna; w pobranym pliku nie ma logiki Levenshteina. Definicji `ultranormalize_name` nie odczytano (w `models.py` występuje tylko wywołanie w indeksie `project_name_ultranormalized`). Po wstawieniu projektu uruchamiane jest osobne zadanie `typo_check_project_name`, którego treści nie odczytano. [7][8]
9. Wniosek z pkt 8: `neo4j` (istnieje na PyPI, wersja 6.4.0 wg JSON API [9]) i `node4j` różnią się o znaki, więc reguła równości po `ultranormalize_name` raczej ich nie utożsami, o ile ta funkcja nie usuwa/mapuje liter — czego nie potwierdzono. (wniosek, niepotwierdzony)
10. FAQ PyPI "Why isn't my desired project name available?" wymienia cztery powody niedostępności mimo braku widocznego projektu: kolizja z biblioteką standardową, "too similar to an existing project and may be confusable", jawny zakaz administratorów oraz "registered by another user, but no releases have been created". [10]
11. FAQ: "Deletion of a project makes it uninstallable, and releases the project name for use by any other PyPI user." Usunięta nazwa jest więc znów dostępna dla każdego; ta sama FAQ mówi, że nazwy pliku nie można użyć ponownie nawet po usunięciu i ponownym utworzeniu projektu. [10]
12. PEP 541: "The Package Index maintainers pre-emptively declare certain package names as unavailable for security reasons." Projekt będący name squattingiem ("package has no functionality or is empty") jest uznawany za nieprawidłowy i może być usunięty. "Under no circumstances will a name be reassigned against the wishes of a reachable owner." PEP 541 nie omawia podobieństwa/typosquattingu. [11]
13. Rezerwacja: nazwa jest przydzielana dopiero przy pierwszym udanym uploadzie, który tworzy projekt (`create_project` wywoływane w ścieżce uploadu `forklift/legacy.py`, wymaga zweryfikowanego e-maila i 2FA, jest limit tworzenia nowych projektów: "Too many new projects created"). Wolna dziś nazwa nie jest zatem zarezerwowana. [7][12]

## Niepewności

- Brak odczytu stron HTML (`/project/node4j/`) — blokada Client Challenge; pewność oparta na 404 z API (JSON i Simple). 404 nie odróżnia "nigdy nie istniał" od "usunięty" (w obu przypadkach nazwa wolna wg FAQ [10]). Nie sprawdzono, czy lista `ProhibitedProjectName` zawiera `node4j` — lista nie jest publiczna; ocenić to można tylko próbą uploadu.
- Treść `ultranormalize_name` i zadania `typo_check_project_name` nie została odczytana; nie wiadomo, czy `node4j` może zostać uznane za zbyt podobne do `neo4j` lub innego istniejącego projektu. Kod pochodzi z gałęzi main (stan z dnia sprawdzenia), nie z wersji wdrożonej na PyPI.
- Wolna dziś nazwa może zostać zajęta przez kogoś innego przed publikacją. Nie sprawdzono też, czy istnieją inne projekty o podobnych nazwach (np. `node4j-*`), bo kod wskazuje na porównanie równości, nie podobieństwa.
- Sprawdzenie nie obejmuje znaków towarowych ani zasad poza PyPI.
- Pytanie o nazwę wyświetlaną (`Node4j` vs `node4j`): PyPI przechowuje nazwę wpisaną przy pierwszym uploadzie (wg kodu `project.name = meta.name` przy ró żnicy, wniosek); nie weryfikowano.

## Źródła

[1] PyPI JSON API dla node4j — https://pypi.org/pypi/node4j/json — API — 404, 2026-10-12
[2] PyPI Simple API dla node4j — https://pypi.org/simple/node4j/ — API — 404, 2026-10-12
[3] Strona projektu — https://pypi.org/project/node4j/ — strona HTML — Client Challenge, 2026-10-12
[4] TestPyPI JSON — https://test.pypi.org/pypi/node4j/json — API — 404, 2026-10-12
[5] TestPyPI Simple / strona — https://test.pypi.org/simple/node4j/ (404), https://test.pypi.org/project/node4j/ (Client Challenge) — 2026-10-12
[6] Names and normalization — https://packaging.python.org/en/latest/specifications/name-normalization/ — specyfikacja (następca PEP 503 w zakresie normalizacji) — wersja bieżąca
[7] warehouse `packaging/services.py` — https://raw.githubusercontent.com/pypi/warehouse/main/warehouse/packaging/services.py — kod — main, 2026-10-12
[8] warehouse `packaging/models.py` — https://raw.githubusercontent.com/pypi/warehouse/main/warehouse/packaging/models.py — kod — main
[9] PyPI JSON API dla neo4j — https://pypi.org/pypi/neo4j/json — API — neo4j 6.4.0
[10] PyPI Help (FAQ) — https://pypi.org/help/ — dokumentacja — 2026-10-12
[11] PEP 541 — https://peps.python.org/pep-0541/ — specyfikacja
[12] warehouse `forklift/legacy.py` — https://raw.githubusercontent.com/pypi/warehouse/main/warehouse/forklift/legacy.py — kod — main
