---
nr: "04"
tytul: "CI na starym stosie"
status: zrobione
blokowany-przez: ["01", "02", "03"]
scenariusze: [N1, N2, N3]
budowal: "Codex / GPT-6"
github: null
---

# 04 — CI na starym stosie

## Co widać po zrobieniu

GitHub Actions uruchamia przy każdym pushu siatkę N1–N3 i TTL na serwerze 2025.05 z Pythonem 3.12, ruff względem punktu odniesienia i kontrolę instalacji. CI jest zielone.

## Kryteria akceptacji

- [x] N1, N2, N3: testy zielone w CI
- [x] CI kończy się błędem, gdy baza jest niedostępna albo wymagany test integracyjny zostaje pominięty (lokalnie bez bazy testy nadal się pomijają)
- [x] ruff w CI przechodzi, gdy nie ma błędów spoza `odniesienie.znane`, i nie przechodzi przy nowym błędzie
- [x] CI buduje dystrybucję, instaluje ją w czystym środowisku poza katalogiem źródeł i importuje publiczne API
- [x] widoczność repo i dostępność minut Actions sprawdzone i zapisane w Notatkach

## Poza zakresem

- Macierz serwerów i Pythona — ticket 07; przebieg na najnowszym pydantic — ticket 06.

## Notatki

Neo4j z APOC jako service container. P-07 w `.ai/profil.md` → link do workflow.

Repozytorium `gkeb/node4j` jest publiczne (GitHub API, 2026-10-12); standardowe GitHub-hosted runners są bezpłatne i nielimitowane dla repozytoriów publicznych ([dokumentacja GitHub Actions](https://docs.github.com/en/actions/concepts/billing-and-usage)).

CI dla commitu `3101889` zakończył się sukcesem 2026-10-12 ([przebieg workflow](https://github.com/gkeb/node4j/actions/runs/38265203829)).
