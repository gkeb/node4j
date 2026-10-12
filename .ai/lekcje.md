# Lekcje

> Rozwiązane problemy: założenie — agenta albo nasze — okazało się fałszywe, i jak robimy teraz. Zapisuj od razu, niezależnie od tego, kto wykrył błąd. Ta sama przyczyna → dopisz wystąpienie, nie nową linijkę. Problem bez rozwiązania idzie do `proby.md`. Zasady: „Lekcje — czego się nauczyliśmy” w `kontrakt/pamiec.md`; format wpisu: „Lekcja — wpis w `lekcje.md`” w `kontrakt/formaty.md` — oba w katalogu pluginu warsztatu.

Ostatnie retro: 2026-10-12

<!-- - [obszar | zdolność | projekt] problem — założyliśmy X, okazało się Y → teraz Z (link do śladu). Wzorzec: plik. Wystąpienia: RRRR-MM-DD kto-wykrył; RRRR-MM-DD kto-wykrył -->

- [aktualizacja-zaleznosci] `pytest.raises` nie zgłasza `AssertionError`, gdy oczekiwany wyjątek nie wystąpi — założyliśmy, że `except AssertionError` posprząta trigger po nieoczekiwanym sukcesie, ale pytest zgłasza własny typ błędu → sukces obsługujemy gałęzią `else`, wykonujemy sprzątanie i nie ukrywamy błędu usuwania. Wystąpienia: 2026-10-12 przegląd
