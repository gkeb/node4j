---
nr: "12"
tytul: "Po weryfikacji R2: przykład Periodic i pokrycie związane ze specem"
status: do-zrobienia
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

- [ ] S5: test akceptacyjny przechodzi, a jego pozycje pochodzą z wykazu w specu
- [ ] S5: wrapper `Periodic` wspomniany tylko w prozie albo tylko w tekście Cypher (`CALL apoc.periodic.iterate(`) daje czerwony test — sprawdzone testem na syntetycznym źródle
- [ ] S5: pozycja dopisana do wykazu w specu, a nieobecna w wykonywanym bloku, daje czerwony test — sprawdzone testem na syntetycznym wykazie
- [ ] S3: usunięcie albo zawężenie zbierania bloków ze znacznikiem (np. pominięcie `docs/en/`) daje czerwony test, a test raportu pominięć jest zbierany także wtedy, gdy żadna strona nie ma znacznika
- [ ] S2: przykład z `apoc.Periodic.iterate` wykonuje się na bazie testowej i asercją pokazuje zmianę danych strony
- [ ] S4: strona APOC ma odpowiednik PL z identycznym kodem
- [ ] Żadna istniejąca asercja testu akceptacyjnego nie jest usunięta ani osłabiona. Jeśli zmiana jest konieczna, uzasadnienie i zgoda człowieka są w Notatkach
- [ ] Walidacja zielona, CI zielone na obu wersjach Neo4j
- [ ] Akceptacja wyglądu zmienionej strony APOC wpisana w Notatkach

## Poza zakresem

- Zmiana sygnatury wrappera `Periodic.iterate` (dodanie parametrów zapytania). Ścieżka jest odłożona w `proby.md` (2026-10-15). Jeśli bez niej nie da się ograniczyć przykładu do danych strony zgodnie z Z02, zatrzymaj się i zapytaj, zamiast wybierać surowy Cypher.
- Uwaga R2.3 (ślad `test_10_…`, komunikat `ServiceUnavailable`, format `budowal` w 08) — zostaje otwarta w raporcie.

## Notatki

- Uwagi weryfikacji: R2.1, R2.2 ([weryfikacja](../weryfikacja.md)).
- Wskazówka (nie wymóg): przykład wrappera może działać na etykiecie, której nie używa nic poza tym blokiem (np. tworzonej tylko tutaj). Kroki iteracji wtedy nie potrzebują markera, a izolację względem strony zapewnia sprzątanie po różnicy stanu (wyjątek Z05). Sprawdź, czy lekcja „znacznik sprzątania sam ograniczy mutacje przykładu `Periodic.iterate`” w `lekcje.md` dotyczy też takiej etykiety.
- Lekcja: „asercje testu akceptacyjnego zmieniamy, żeby przeszedł” w `lekcje.md` (2026-10-15).
