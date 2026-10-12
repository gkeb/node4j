---
nr: "07"
tytul: "Macierz serwerów i Pythona"
status: w-toku
blokowany-przez: ["06"]
scenariusze: [N1, N2, N3]
budowal: null
github: null
---

# 07 — Macierz serwerów i Pythona

## Co widać po zrobieniu

CI uruchamia siatkę na serwerach 2026.09 i 5.26 LTS × Python 3.12 i najnowszy, nadal na sterowniku 5.28. Wszystko zielone.

## Kryteria akceptacji

- [ ] N1, N2, N3: testy zielone na każdej z czterech kombinacji
- [ ] AGENTS.md → Uruchamianie: jak uruchomić bazę testową dla każdego serwera z macierzy
- [ ] żaden wymagany test nie jest pominięty w żadnej kombinacji

## Poza zakresem

- Sterownik 6.x — ticket 08.

## Notatki

Macierz używa Pythonów 3.12 i 3.15 (3.15.0 jest najnowszym stabilnym wydaniem na 2026-10-12) oraz obrazów `neo4j:2026.09.0` i `neo4j:5.26`. Obrazy trzeba pobrać lokalnie, jeśli testy mają być uruchamiane na obu serwerach.
