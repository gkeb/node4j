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

## Wzorce

<!-- Wzorce, których używamy (i gdzie), oraz te, których świadomie unikamy. -->

## Kod

<!-- Tylko stanowiska, gdzie domyślne podejście jest niejednoznaczne: wyjątki czy wyniki w domenie, obsługa błędów, logowanie, niemutowalność, nazewnictwo, wielkość modułów. -->

## Testy

<!-- Strategia, poziomy, co mockujemy, czego nie testujemy. -->

## Niefunkcjonalne

<!-- Bezpieczeństwo, wydajność, dostępność, prywatność — tylko jeśli obowiązują w całym projekcie. -->
