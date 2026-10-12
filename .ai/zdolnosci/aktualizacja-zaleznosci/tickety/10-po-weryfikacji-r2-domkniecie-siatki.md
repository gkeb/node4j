---
nr: "10"
tytul: "Po weryfikacji R2: domknięcie siatki"
status: w-toku
blokowany-przez: []
scenariusze: [N1]
budowal: "Codex / GPT-6"
github: null
---

# 10 — Po weryfikacji R2: domknięcie siatki

## Co widać po zrobieniu

Kontrola instalacji w CI importuje całe publiczne API z zainstalowanej dystrybucji, testy triggerów APOC przypinają konkretną przyczynę błędu, a dokumentacja uruchamiania i mapa zgadzają się ze stanem. Struktura biblioteki bez zmian.

## Kryteria akceptacji

- [x] kontrola instalacji w CI importuje wszystkie moduły publicznego API z N1: `node4j`, `node4j.db`, `node4j.nodes`, `node4j.query`, `node4j.mixins`, `node4j.managers`, `node4j.properties`, `node4j.edges`, `node4j.ext.apoc`, `node4j.ext.gds` (R2.2)
- [x] N1: testy `test_N1_apoc_trigger_*` przypinają kod błędu (`ClientError.code`) zwracany dziś przez serwer, a nie dowolny `ClientError` (R2.3)
- [x] `AGENTS.md` → Uruchamianie opisuje `NODE4J_REQUIRE_TEST_DB=1` (brak bazy albo pominięty test integracyjny = błąd, jak w CI) (R2.4)
- [x] `mapa.md` → Stan sesji odpowiada stanowi ticketów (R2.4)
- [ ] testy zielone na bazie testowej z `NODE4J_REQUIRE_TEST_DB=1`; CI zielone dla commitu ticketu
- [x] walidacja (ruff) bez błędów spoza punktu odniesienia

## Poza zakresem

- Naprawa triggerów APOC — `.ai/proby.md`, osobno przez `napraw`.

## Notatki

Uwagi R2.2–R2.4 z [weryfikacja.md](../weryfikacja.md). Przed 06: R2.3 ma uściślić siatkę, zanim zmienią się wersje.
