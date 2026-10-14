# Znane ograniczenia

[English](../en/known-limitations.md) · [README](../../README_PL.md)

Te zachowania mają znaczenie przy wyborze sposobu użycia biblioteki. Każdy punkt opisuje obecne działanie i praktyczne rozwiązanie.

## Zarządzanie triggerami APOC

`apoc.Triggers.install()`, `list()` i `remove()` kończą się `ClientError`, gdy są wywoływane w domyślnej bazie używanej przez połączenie biblioteki w testowanych konfiguracjach Neo4j. Wrapper nie kieruje obecnie tych operacji do bazy `system`.

**Co zrobić:** Nie polegaj na `apoc.Triggers` przez domyślne połączenie. Jeśli wdrożenie wymaga zarządzania triggerami, użyj poza tym wrapperem procedury operacyjnej skonfigurowanej dla właściwej bazy albo zrezygnuj z tych wywołań do czasu, aż wrapper obsłuży takie połączenie.

## Daty i UID są zapisywane jako tekst

Właściwości są serializowane w trybie JSON Pydantic przed zapisem. Wartości daty i czasu trafiają więc do Neo4j jako tekst; tekstem jest też `uid`. Funkcje temporalne Neo4j nie traktują tych ciągów jak natywnych wartości temporalnych.

**Co zrobić:** Traktuj zapisane daty jako ciągi i w razie potrzeby parsuj je w aplikacji. Jeśli zapytanie wymaga natywnych wartości temporalnych Neo4j, użyj jawnego Cyphera i jawnej ścieżki konwersji. Wartości `uid` porównuj jako tekst.

Zobacz [Modele i schemat](models-and-schema.md), aby dowiedzieć się więcej o polach modeli i `uid`.

## Nieznany sufiks filtra zamienia się w równość

Nieznany, nieobsługiwany albo błędnie zapisany sufiks `Q` po cichu staje się równością. Literówka w sufiksie porównania może zwrócić inne węzły, niż zakładano.

**Co zrobić:** Używaj wyłącznie udokumentowanych sufiksów i obejmuj testami filtry inne niż równość. Zobacz [Zapytania i filtry](queries-and-filters.md), gdzie opisano obsługiwane operatory.

## Rejestr modeli używa nazw klas

Globalny rejestr modeli jest kluczowany nazwą klasy. Jeśli dwie zaimportowane klasy modeli mają tę samą nazwę, późniejsza rejestracja zastępuje wcześniejszą.

**Co zrobić:** Nadaj każdemu modelowi unikalną nazwę klasy w całej aplikacji, także modelom z osobnych modułów. Zobacz [Relacje](relationships.md), gdzie deklaracje relacji wskazują model po nazwie.

## Historia zapytań rośnie przez cały czas działania połączenia

`connection.queries` przechowuje wszystkie zapytania i ich parametry na liście. Lista rośnie w miarę pracy połączenia i nie jest automatycznie ograniczana ani czyszczona.

**Co zrobić:** Nie używaj tej listy jako trwałego telemetrycznego magazynu w długo działającym procesie. Po debugowaniu wyczyść ją przez `connection.queries.clear()` albo zapisuj diagnostykę w ograniczonym magazynie aplikacji.

Zobacz [Konfiguracja i logowanie](configuration-and-logging.md), gdzie opisano logowanie.

## Parametry zapytań trafiają do logów

Logger `node4j.db` zapisuje parametry zapytań w logach DEBUG oraz w logach ERROR dla nieudanych zapytań. Parametry mogą zawierać dane wrażliwe.

**Co zrobić:** Traktuj logi DEBUG i ERROR dla nieudanych zapytań jako wrażliwe. Ogranicz do nich dostęp i redaguj wartości parametrów przed wysłaniem logów do wspólnych lub zewnętrznych systemów. Zobacz [Konfiguracja i logowanie](configuration-and-logging.md), gdzie opisano konfigurację loggerów.
