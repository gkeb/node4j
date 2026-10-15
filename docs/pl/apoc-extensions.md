# Rozszerzenia APOC

APOC dodaje procedury i funkcje do serwera Neo4j. Moduł `node4j.ext.apoc` opakowuje część z nich: sprawdzanie wersji, zapytania wykonywane partiami, eksport JSON i tworzenie węzłów z JSON.

Language: [English](../en/apoc-extensions.md) · [README](../../README_PL.md).

## Instalacja pluginu APOC

APOC działa wewnątrz Neo4j, dlatego zainstaluj wersję pluginu zgodną z serwerem Neo4j. W Neo4j Desktop zainstaluj APOC na karcie Plugins. W oficjalnym obrazie Dockera plugin włącz przy uruchamianiu:

```yaml
services:
  neo4j:
    image: neo4j:2026.09.0
    environment:
      NEO4J_AUTH: neo4j/change-me
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_apoc_import_file_enabled: "true"
      NEO4J_apoc_export_file_enabled: "true"
```

Flagi importu i eksportu włączają dostęp serwera do plików. W Dockerze odpowiadają im ustawienia `NEO4J_apoc_import_file_enabled=true` i `NEO4J_apoc_export_file_enabled=true`. Tych samych ustawień APOC używa testowa baza projektu w CI i w [AGENTS.md](../../AGENTS.md).

Neo4j opisuje `NEO4J_PLUGINS` jako ułatwienie dla środowisk deweloperskich i nie zaleca tej metody na produkcji. W produkcji zainstaluj plugin JAR APOC zgodny z wersją Neo4j i zamontuj go w `/plugins`; zobacz [oficjalny przewodnik instalacji APOC](https://neo4j.com/docs/apoc/current/installation/).

## Rozwiązywanie problemów z brakującymi procedurami APOC

Jeśli `await apoc.version()` albo inne wywołanie APOC kończy się błędem `Neo.ClientError.Procedure.ProcedureNotFound`, Neo4j nie zarejestrował tej procedury na połączonym serwerze. Komunikat serwera ma taką postać:

```text
There is no procedure with the name `apoc.version` registered for this database instance. Please ensure you've spelled the procedure name correctly and that the procedure is properly deployed.
```

Sprawdź, czy APOC jest zainstalowany dla używanej wersji Neo4j, włączony i załadowany po restarcie serwera. W Dockerze zobacz konfigurację pluginu powyżej; w innych instalacjach skorzystaj z [oficjalnego przewodnika instalacji APOC](https://neo4j.com/docs/apoc/current/installation/). Jeśli brakuje tylko jednej procedury APOC, sprawdź, czy zawiera ją zainstalowane wydanie pluginu.

## Dostęp do plików na serwerze Neo4j

APOC odczytuje i zapisuje pliki na **serwerze Neo4j**. Przy domyślnej konfiguracji serwera `file:///people.json` oznacza plik `people.json` w katalogu import tego serwera. Plik dostępny tylko na komputerze aplikacji Python nie jest dostępny pod tym URL-em. Dostęp APOC do importu i eksportu plików jest domyślnie wyłączony.

Przy instalacji innej niż Docker wpisz te ustawienia do `apoc.conf` i zrestartuj Neo4j:

```properties
apoc.import.file.enabled=true
apoc.export.file.enabled=true
```

Jeśli import pozostaje wyłączony, APOC zwraca komunikat podobny do:

```text
Import from files not enabled, please set apoc.import.file.enabled=true in apoc.conf
```

Procedury i ustawienia opisują [przewodnik APOC po eksporcie JSON](https://neo4j.com/docs/apoc/current/export/json/) oraz [referencja APOC `load.json`](https://neo4j.com/docs/apoc/current/overview/apoc.load/apoc.load.json/).

## Sprawdzenie APOC i operacje partiami

`await apoc.version()` zwraca wersję zainstalowaną na połączonym serwerze. `apoc.Periodic.iterate()` opakowuje zapytanie odczytujące i aktualizujące wykonywane w partiach; domyślna wartość `batch_size` to 1000. Pierwszy przykład tworzy etykiety unikalne dla każdego uruchomienia na podstawie generowanych UUID, więc wrapper wybiera tylko węzły utworzone przez ten przykład; wiersz wybrany przez zapytanie odczytujące trafia do zapytania aktualizującego. Późniejszy przykład z `connection.run` pokazuje, jak przekazywać wartości używane w zapytaniu przez `config.params`. Treść zapytań zapisuj po stronie programisty i nigdy nie wstawiaj do nich danych użytkownika; generowane etykiety są nazwami identyfikatorów ujętymi w backticki.

## Eksport i import JSON

`apoc.Export.to_json(file_name, config=None)` eksportuje **całą bazę** do JSON Lines w katalogu import serwera. Eksport grafu zawiera metadane, takie jak etykiety i zagnieżdżone `properties`; jego format różni się od map właściwości oczekiwanych przez `create_from_json`.

Przykład eksportu całej bazy uruchamiaj tylko na bazie testowej, chyba że celowo tworzysz pełną migawkę. Wyeksportowany plik może zawierać dane wrażliwe; ogranicz do niego dostęp i usuń go, gdy nie będzie już potrzebny.

`install_apoc_manager(Model)` dodaje `Model.apoc.create_from_json(file_url, json_path="$", batch_size=1000)`. Importer odczytuje mapy właściwości wskazane przez `json_path`, tworzy węzły z etykietą modelu i przypisuje im nowe wartości `uid`. Nie odtwarza etykiet, relacji ani oryginalnych identyfikatorów z eksportu. Przykład eksportuje pełną migawkę bazy, a następnie używa eksportu zapytania APOC, by zapisać wybrany plik JSON Lines z jedną mapą właściwości dla importera.

`create_from_json` przekazuje `file_url` do `apoc.load.json`, który może też pobierać zdalne URL-e. Nie przekazuj URL-i kontrolowanych przez użytkownika: serwer Neo4j mógłby uzyskać dostęp do usług w sieci wewnętrznej. API zapisuje `file_url` w logu INFO, więc nigdy nie umieszczaj w nim danych logowania ani tokenów. Stosuj się do [zaleceń bezpieczeństwa APOC dotyczących SSRF](https://neo4j.com/docs/apoc/current/security-guidelines/) odpowiednich dla swojej edycji Neo4j.

```python
from uuid import UUID, uuid4

from node4j.db import connection
from node4j.ext.apoc import apoc, install_apoc_manager
from node4j.nodes import Node


class GuideApocSource(Node):
    marker: str


class GuideApocImported(Node):
    marker: str


install_apoc_manager(GuideApocImported)
marker = str(uuid4())
other_marker = str(uuid4())
backup_file = f"node4j-apoc-backup-{marker}.json"
import_file = f"node4j-apoc-import-{marker}.json"
periodic_source_label = f"GuideApocPeriodicSource_{uuid4().hex}"
periodic_neighbor_label = f"GuideApocPeriodicNeighbor_{uuid4().hex}"
GuideApocPeriodicSource = type(periodic_source_label, (Node,), {})
GuideApocPeriodicNeighbor = type(periodic_neighbor_label, (Node,), {})
periodic_source = None
periodic_neighbor = None

try:
    version = await apoc.version()
    assert version is not None

    await GuideApocSource.q.create(marker=marker)
    await GuideApocSource.q.create(marker=other_marker)
    source = await connection.run(
        "MATCH (source:`GuideApocSource`) WHERE source.`marker` = $marker "
        "RETURN source.`uid` AS uid",
        {"marker": marker},
    )
    source_uid = UUID(source[0]["uid"])
    await connection.run(
        """
        CALL apoc.periodic.iterate(
            $cypher_to_iterate,
            $cypher_to_execute,
            {batchSize: $batch_size, params: {marker: $marker}}
        )
        """,
        {
            "cypher_to_iterate": (
                "MATCH (source:`GuideApocSource`) "
                "WHERE source.`marker` = $marker RETURN source"
            ),
            "cypher_to_execute": "SET source.`apoc_processed` = true",
            "batch_size": 100,
            "marker": marker,
        },
    )
    processed = await connection.run(
        "MATCH (source:`GuideApocSource`) WHERE source.`marker` = $marker "
        "RETURN source.`apoc_processed` AS processed",
        {"marker": marker},
    )
    assert processed[0]["processed"] is True
    untouched = await connection.run(
        "MATCH (source:`GuideApocSource`) WHERE source.`marker` = $marker "
        "RETURN source.`apoc_processed` IS NULL AS unchanged",
        {"marker": other_marker},
    )
    assert untouched[0]["unchanged"] is True

    periodic_source = await GuideApocPeriodicSource.q.create()
    periodic_neighbor = await GuideApocPeriodicNeighbor.q.create()
    await apoc.Periodic.iterate(
        f"MATCH (source:`{periodic_source_label}`) RETURN source",
        "SET source.`apoc_processed` = randomUUID()",
        batch_size=100,
    )
    processed = await connection.run(
        f"MATCH (source:`{periodic_source_label}`) "
        "RETURN source.`apoc_processed` IS NOT NULL AS processed"
    )
    assert processed[0]["processed"] is True
    neighbor = await connection.run(
        f"MATCH (node:`{periodic_neighbor_label}`) "
        "RETURN node.`apoc_processed` IS NULL AS unchanged"
    )
    assert neighbor[0]["unchanged"] is True

    await apoc.Export.to_json(backup_file, {"jsonFormat": "JSON_LINES"})

    exported = await connection.run(
        """
        CALL apoc.export.json.query(
            $statement,
            $file_name,
            {params: {marker: $marker}}
        )
        YIELD file, done
        RETURN file, done
        """,
        {
            "statement": (
                "MATCH (source:`GuideApocSource`) "
                "WHERE source.`marker` = $marker "
                "RETURN properties(source) AS row"
            ),
            "file_name": import_file,
            "marker": marker,
        },
    )
    assert exported[0]["done"] is True

    loaded = await connection.run(
        "CALL apoc.load.json($url) YIELD value RETURN value",
        {"url": f"file:///{import_file}"},
    )
    assert loaded[0]["value"]["row"]["marker"] == marker
    selected = await connection.run(
        "CALL apoc.load.json($url, $path) YIELD value RETURN value",
        {"url": f"file:///{import_file}", "path": "$.row"},
    )
    assert selected[0]["value"]["marker"] == marker

    import_result = await GuideApocImported.apoc.create_from_json(
        f"file:///{import_file}",
        json_path="$.row",
        batch_size=100,
    )
    imported = await connection.run(
        "MATCH (node:`GuideApocImported`) "
        "WHERE node.`marker` = $marker "
        "RETURN node.`uid` AS uid",
        {"marker": marker},
    )
    assert len(imported) == 1, import_result
    imported_uid = UUID(imported[0]["uid"])
    assert imported_uid != source_uid
finally:
    await connection.run(
        "MATCH (node) "
        "WHERE node.`marker` IN $markers OR node.`uid` IN $uids "
        "DETACH DELETE node",
        {
            "markers": [marker, other_marker],
            "uids": [
                str(node.uid)
                for node in (periodic_source, periodic_neighbor)
                if node is not None
            ],
        },
    )
```

Pliki eksportu pozostają w katalogu import serwera Neo4j. Używaj unikalnych nazw plików i zarządzaj nimi po stronie serwera zgodnie z zasadami retencji wdrożenia. Przykład korzysta z syntetycznych danych i usuwa tymczasowe węzły.
