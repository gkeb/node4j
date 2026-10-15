---
nr: "12"
tytul: "Po weryfikacji R2: przykład Periodic i pokrycie związane ze specem"
status: w-toku
blokowany-przez: ["06", "11"]
scenariusze: ["S5", "S3", "S2", "S4"]
budowal: null
github: null
---

# 12 — Po weryfikacji R2: przykład Periodic i pokrycie związane ze specem

## Co widać po zrobieniu

- Strona rozszerzeń APOC (EN i PL) znów wywołuje wrapper biblioteki `apoc.Periodic.iterate` w wykonywanym bloku, a czytelnik widzi jego efekt na danych. Zapytania są ograniczone do danych tej strony, bez wstawiania wartości do tekstu Cyphera (Z02). Obecny przykład `connection.run` z `config.params` może zostać obok.
- Wykazu pokrycia S5 nie da się już po cichu zawęzić. Test pokrycia bierze pozycje z wykazu w specu („Zakres → Wykaz pokrycia (S5)”), a nie z listy wpisanej w teście. Każda pozycja musi wystąpić jako wywołanie albo odwołanie w kodzie Pythona wykonywanego bloku. Wystąpienie wyłącznie w napisie (np. w tekście zapytania Cypher), w komentarzu albo w prozie się nie liczy. Jeśli test zawęża pozycję, wymaga to zmiany specu, którą widać w przeglądzie i która wymaga zgody człowieka.
- Test raportowania pominiętych bloków (S3) jest zbierany zawsze, a nie tylko wtedy, gdy któraś strona ma znacznik. Jego okablowanie (wybór stron, zbieranie bloków ze znacznikiem) sprawdza przebieg pytest na syntetycznej stronie przez tę samą funkcję zbierającą, której używa prawdziwy test.

## Kryteria akceptacji

- [x] S5: test akceptacyjny przechodzi, a jego pozycje pochodzą z wykazu w specu
- [x] S5: wrapper `Periodic` wspomniany tylko w prozie albo tylko w tekście Cypher (`CALL apoc.periodic.iterate(`) daje czerwony test — sprawdzone testem na syntetycznym źródle
- [x] S5: pozycja dopisana do wykazu w specu, a nieobecna w wykonywanym bloku, daje czerwony test — sprawdzone testem na syntetycznym wykazie
- [x] S3: usunięcie albo zawężenie zbierania bloków ze znacznikiem (np. pominięcie `docs/en/`) daje czerwony test, a test raportu pominięć jest zbierany także wtedy, gdy żadna strona nie ma znacznika
- [x] S2: przykład z `apoc.Periodic.iterate` wykonuje się na bazie testowej i asercją pokazuje zmianę danych strony
- [x] S4: strona APOC ma odpowiednik PL z identycznym kodem
- [x] Żadna istniejąca asercja testu akceptacyjnego nie jest usunięta ani osłabiona. Jeśli zmiana jest konieczna, uzasadnienie i zgoda człowieka są w Notatkach
- [ ] Walidacja zielona, CI zielone na obu wersjach Neo4j
- [x] Akceptacja wyglądu zmienionej strony APOC wpisana w Notatkach

## Poza zakresem

- Zmiana sygnatury wrappera `Periodic.iterate` (dodanie parametrów zapytania). Ścieżka jest odłożona w `proby.md` (2026-10-15). Jeśli bez niej nie da się ograniczyć przykładu do danych strony zgodnie z Z02, zatrzymaj się i zapytaj, zamiast wybierać surowy Cypher.
- Uwaga R2.3 (ślad `test_10_…`, komunikat `ServiceUnavailable`, format `budowal` w 08) — zostaje otwarta w raporcie.

## Notatki

- Uwagi weryfikacji: R2.1, R2.2 ([weryfikacja](../weryfikacja.md)).
- Weryfikacja lokalna: pełny `pytest` z `NODE4J_REQUIRE_TEST_DB=1` — Neo4j 2026.09.0: 121 passed, 1 skip; Neo4j 5.26.32: 121 passed, 1 skip. Pominięty test dotyczy braku znaczników na aktualnych stronach; wszystkie integracyjne wykonano.
- CI nieuruchomione z tej sesji; fetch GitHuba nie powiódł się z powodu braku dostępu do sieci.
- Ruff: `check_ruff_baseline.py` bez nowych błędów, 108 zastanych. Skan diffu nie wykazał usuniętych ani osłabionych asercji akceptacyjnych.
- Przegląd: dwóch recenzentów i recenzent bezpieczeństwa nie zgłosili blokad w końcowym diffie.
- Podglądy: `.ai/zrzuty/readme-aktualne-12/apoc-en-1280.png`, `apoc-en-375.png`, `apoc-pl-1280.png`, `apoc-pl-375.png`. Zrzuty pokazują lokalnie wyrenderowany fragment w stylu GitHub Markdown, a nie live GitHuba.
- Akceptacja wyglądu: po przedstawieniu czterech podglądów użytkownik polecił wypchnięcie zmian (2026-10-15); traktuję to jako akceptację pokazanej wersji.
- Wskazówka (nie wymóg): przykład wrappera może działać na etykiecie, której nie używa nic poza tym blokiem (np. tworzonej tylko tutaj). Kroki iteracji wtedy nie potrzebują markera, a izolację względem strony zapewnia sprzątanie po różnicy stanu (wyjątek Z05). Sprawdź, czy lekcja „znacznik sprzątania sam ograniczy mutacje przykładu `Periodic.iterate`” w `lekcje.md` dotyczy też takiej etykiety.
- Zasada (retro 2026-10-15): asercji testu akceptacyjnego nie usuwasz ani nie osłabiasz bez zmiany specu albo zgody człowieka w Notatkach (skill `buduj`). Przegląd wypisuje usunięte asercje skryptem warsztatu `usuniete-asercje.mjs`. Wzorzec warsztatu: `naprawa-oslabia-test-ktory-ja-pilnowal`.
