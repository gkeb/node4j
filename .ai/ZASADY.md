# Zasady projektu

> Czego kod ma się trzymać przez cały okres życia: architektura, wzorce, zasady kodu, testy, wymagania niefunkcjonalne. Aktualny, skonsolidowany stan — uzasadnienia są w ADR-ach, tu tylko link; gdy ADR-u nie ma, linkuj źródło zasady. Format: „Zasady projektu” w `kontrakt/poznanie.md` w katalogu pluginu warsztatu.
> Tylko stanowiska specyficzne dla projektu — ogólnych zasad czystego kodu nie przepisujemy.
> Numery `Zxx` są stałe: recenzenci cytują je w uwagach („łamie Z03”). Wycofanej zasady nie usuwasz, tylko zmieniasz status.

## Architektura

<!-- Styl i warstwy, kierunek zależności, granice modułów: co może importować co.

### Z01. Domena nie importuje infrastruktury

- Siła: twarda
- Egzekwowanie: automat — `npx depcruise src` (reguła `domena-bez-infrastruktury`)
- Status: obowiązuje
- Dlaczego: [ADR 0004](decyzje/0004-architektura-heksagonalna.md)
- Wyjątki: —
-->

### Z01. Publiczne API biblioteki jest asynchroniczne

- Siła: twarda
- Egzekwowanie: przegląd
- Status: zastana
- Dlaczego: README → „Fully asynchronous API”; `node4j/db.py` używa wyłącznie `AsyncGraphDatabase`
- Wyjątki: —


## Wzorce

<!-- Wzorce, których używamy (i gdzie), oraz te, których świadomie unikamy. -->

## Kod

<!-- Tylko stanowiska, gdzie domyślne podejście jest niejednoznaczne: wyjątki czy wyniki w domenie, obsługa błędów, logowanie, niemutowalność, nazewnictwo, wielkość modułów. -->

### Z02. Wartości trafiają do Cypher wyłącznie jako parametry, a nazwy (pola, etykiety, typy relacji) w backtickach

- Siła: twarda
- Egzekwowanie: przegląd
- Status: zastana
- Dlaczego: `node4j/query.py` → `Q._compile_clause`, `node4j/properties.py` → `RelationshipManager.connect`, `node4j/manager.py` → `_orderby_statement`
- Wyjątki: `node4j/manager.py` → `create`, `bulk_create`, `bulk_update` i `ext/apoc.py` → `create_from_json` — etykiety i klucze `SET` bez backticków (nazwy pochodzą z klas i pól modelu); `aggregate` i `ext/gds.py` → `Algo` wstawiają do zapytania ciąg podany przez programistę.

### Z03. Biblioteka loguje przez `logging.getLogger(__name__)` i nie konfiguruje handlerów

- Siła: twarda
- Egzekwowanie: przegląd
- Status: zastana
- Dlaczego: `node4j/__init__.py` (NullHandler, komentarz o bibliotece); commit `1bb03e3` zastąpił `print` loggerem
- Wyjątki: —

### Z04. Styl kodu według ruff: reguły E, F, W, I, linia 88 znaków, podwójne cudzysłowy

- Siła: preferencja
- Egzekwowanie: automat — `uv run ruff check .`; w CI `scripts/check_ruff_baseline.py` względem `warsztat.json` → `odniesienie.znane` (`.github/workflows/ci.yml`)
- Status: zastana
- Dlaczego: `pyproject.toml` → `[tool.ruff]`
- Wyjątki: znane błędy z punktu odniesienia 2026-10-11 (113 po `aktualizacja-zaleznosci`, 2026-10-12)


## Testy

<!-- Strategia, poziomy, co mockujemy, czego nie testujemy. -->

## Niefunkcjonalne

<!-- Bezpieczeństwo, wydajność, dostępność, prywatność — tylko jeśli obowiązują w całym projekcie. -->
