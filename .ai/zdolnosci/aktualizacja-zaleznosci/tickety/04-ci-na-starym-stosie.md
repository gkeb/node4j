---
nr: "04"
tytul: "CI na starym stosie"
status: do-zrobienia
blokowany-przez: ["01", "02", "03"]
scenariusze: [N1, N2, N3]
budowal: null
github: null
---

# 04 — CI na starym stosie

## Co widać po zrobieniu

GitHub Actions uruchamia przy każdym pushu siatkę N1–N3 i TTL na serwerze 2025.05 z Pythonem 3.12, ruff względem punktu odniesienia i kontrolę instalacji. CI jest zielone.

## Kryteria akceptacji

- [ ] N1, N2, N3: testy zielone w CI
- [ ] CI kończy się błędem, gdy baza jest niedostępna albo wymagany test integracyjny zostaje pominięty (lokalnie bez bazy testy nadal się pomijają)
- [ ] ruff w CI przechodzi, gdy nie ma błędów spoza `odniesienie.znane`, i nie przechodzi przy nowym błędzie
- [ ] CI buduje dystrybucję, instaluje ją w czystym środowisku poza katalogiem źródeł i importuje publiczne API
- [ ] widoczność repo i dostępność minut Actions sprawdzone i zapisane w Notatkach

## Poza zakresem

- Macierz serwerów i Pythona — ticket 07; przebieg na najnowszym pydantic — ticket 06.

## Notatki

Neo4j z APOC jako service container. P-07 w `.ai/profil.md` → link do workflow po zrobieniu.
