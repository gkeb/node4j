# Wydanie do PyPI — mapa

Rodzaj: funkcja
Grill: Claude Code / claude-opus-5-5 (szkic koncepcji do Mgły, bez przesłuchania)
Druga opinia: —
Spec: [spec.md](spec.md) — _powstanie po grillu_

## Problem

Node4j da się dziś zainstalować tylko z gita, więc użytkownik biblioteki (P-01) nie może jej dodać zwykłym `uv add node4j` / `pip install node4j`, przypiąć wersji z indeksu ani polegać na tym, że tag odpowiada temu, co instaluje. Wydanie nie jest powtarzalnym procesem: wersja w `pyproject.toml` (`0.2.2`) nie zgadza się z ostatnim tagiem (`v0.2.3`), nie ma historii zmian ani sposobu wycofania.

## Następny krok

skill pomysl wydanie-pypi — od pytania o zakres pakietu (`node4j/models.py`). W Teraz od 2026-10-15 (decyzja człowieka po zamknięciu `readme-aktualne`).

## Koncepcja robocza

> Hipotezy do grilla, nie decyzje. Kolejność = kolejność kroków jednego wydania.

1. **Jedno źródło wersji** — `pyproject.toml` → `version`; tag `vX.Y.Z` musi mu odpowiadać (kontrola w CI przed publikacją). Semver w wariancie 0.x: zmiana niezgodna = podbicie minor.
2. **Historia zmian** — `CHANGELOG.md` z sekcją `## Niewydane`, uzupełnianą przy zamykaniu zdolności; przy wydaniu sekcja dostaje numer i datę.
3. **Budowanie** — `uv build` (sdist + wheel) z jawnym `[build-system]` (dziś brak — `uv build` w CI działa na domyślnym backendzie). Zawartość paczki sprawdzona listą plików, nie tylko importem.
4. **Sprawdzenie przed publikacją** — istniejący krok CI „instalacja wheel poza checkoutem i import API” ([ci.yml](../../../.github/workflows/ci.yml)) jako bramka; najpierw TestPyPI (sprawdza też nazwę — [badanie](../../badania/2026-10-12-nazwa-node4j-pypi.md)), potem PyPI.
5. **Publikacja** — GitHub Actions z Trusted Publishing (OIDC, bez tokenu w sekretach) i `uv publish`, uruchamiane przez tag albo GitHub Release, który zakłada człowiek (agent nie pushuje tagów — skill `wydaj` uruchamia tylko człowiek).
6. **Po wydaniu** — instalacja z indeksu w czystym środowisku (`uv pip install node4j==X.Y.Z` + import), wpis w `.ai/wydania.md`, dokumentacja przechodzi z instalacji z gita na instalację z indeksu (zapowiedziane w [readme-aktualne](../readme-aktualne/mapa.md) → Decyzje 2026-10-12).
7. **Wycofanie** — `yank` wersji w PyPI i nowa wersja poprawkowa; numeru nigdy nie publikuje się ponownie.

Powiązania: rozstrzyga P-15–P-18 w [profil.md](../../profil.md) i `warsztat.json` → `wydanie`; spełnia warunek powrotu odłożonej dokumentacji MkDocs (`proby.md` 2026-10-12).

## Otwarte pytania

- [ ] [grill] Czy `node4j/models.py` (przykładowe modele, które przy imporcie rejestrują się globalnie — pułapka z AGENTS.md) trafia do paczki, czy wychodzi do przykładów poza pakietem? Robocza rekomendacja: poza pakiet, bo użytkownik dostałby obce klasy w rejestrze — blokuje spec
- [ ] [grill] Backend budowania (`uv_build`, `hatchling`, `setuptools`) i nazwa dystrybucji (`Node4j` → `node4j`) — blokuje spec
- [ ] [grill] Od jakiej wersji startujemy w PyPI (0.3.0 po rozjeździe 0.2.2/v0.2.3?) i co jest „publicznym API” dla semver (eksporty `node4j/__init__.py`?) — blokuje spec
- [ ] [badanie] Trusted Publishing z `uv publish` w GitHub Actions: wymagane uprawnienia (`id-token: write`), środowisko `pypi`, konfiguracja „pending publisher” przed pierwszym wydaniem, TestPyPI — nie blokuje grilla, blokuje spec
- [ ] [grill] Metadane paczki: `py.typed` (dziś brak), klasyfikatory, `project.urls`, licencja w formacie SPDX — nie blokuje spec

## Decyzje

- 2026-10-13 — Pomysł odłożony do Mgły, nie bieżąca praca — decyzja użytkownika; Teraz zajmuje `readme-aktualne`
- 2026-10-13 — Jeden pakiet dla całej biblioteki (z `node4j.ext`), publikowany w PyPI i instalowany przez uv/pip — decyzja użytkownika; APOC/GDS to wtyczki serwera, nie zależności Pythona, więc dodatki (`extras`) nie są potrzebne (wniosek)

## Plasterki

## Stan sesji
