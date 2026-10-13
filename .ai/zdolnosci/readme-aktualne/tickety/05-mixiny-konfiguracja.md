---
nr: "05"
tytul: Strony o mixinach oraz o konfiguracji i logowaniu
status: do-zrobienia
blokowany-przez: ["01"]
scenariusze: ["S2", "S4", "S5", "S11"]
budowal: null
github: null
---

# 05 — Strony o mixinach oraz o konfiguracji i logowaniu

## Co widać po zrobieniu

- Strona „Mixiny” (EN i PL) opisuje:
  - TTL: model, uruchomienie okresowego czyszczenia (wymaga APOC), `save_with_expiry` i `set_expiry`;
  - miękkie usunięcie: `setup_soft_delete_manager`, `.q` i `.all_objects`, `soft_delete`, `restore`;
  - to, że mixin sam jest modelem z etykietą.
- Strona „Konfiguracja i logowanie” (EN i PL) opisuje:
  - zmienne `NODE4J_URI`, `NODE4J_USER`, `NODE4J_PASSWORD` i plik `.env` czytany automatycznie;
  - loggery `node4j.*` bez handlerów (Z03) i włączenie logów w aplikacji;
  - ostrzeżenie, że DEBUG zawiera parametry zapytań.
- Test dokumentacji anuluje globalne zadanie czyszczenia TTL po każdej stronie, także po błędzie.

## Kryteria akceptacji

- [ ] S2: przykłady obu stron wykonują się na bazie testowej
- [ ] S4: obie strony mają odpowiedniki PL z identycznym kodem
- [ ] S5 (część): mixiny i konfiguracja `NODE4J_*` są w wykonywanych blokach
- [ ] S11 (część): po stronie, która uruchomiła zadanie TTL, zadanie jest anulowane, także gdy blok rzucił błąd
- [ ] Walidacja zielona

## Poza zakresem

- Typy temporalne dla `ttl` (`natywne-daty` w Mgle).

## Notatki

- S5 kończy ticket 08, a S11 ticket 07.
- Decyzja z mapy (2026-10-13): osobna fikstura anuluje zadanie TTL w teardownie.
- Akceptacja wyglądu: RRRR-MM-DD — użytkownik — obie strony EN i PL — uwagi
