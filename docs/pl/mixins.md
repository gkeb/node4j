# Mixiny

[English](../en/mixins.md) · [README](../../README_PL.md)

## Modele dziedziczące po mixinie

`TTLMixin` i `SoftDeleteMixin` dziedziczą po `Node`, więc każdy z tych mixinów jest również zarejestrowanym modelem z własną etykietą. Model dziedziczący po mixinie dziedziczy także jego etykietę.

## Wygasające węzły z TTL

Dziedzicz po `TTLMixin`, aby dodać pole wygasania `ttl`. `set_expiry()` zmienia wartość w instancji, a `save_with_expiry()` ustawia ją i zapisuje dla wcześniej utworzonego węzła.

```python
import datetime

from node4j.mixins import TTLMixin


class TemporaryDocument(TTLMixin):
    title: str


document = await TemporaryDocument.q.create(title="Temporary note")
document.set_expiry(datetime.timedelta(hours=1))
assert document.ttl is not None

await document.save_with_expiry(datetime.timedelta(hours=1))
assert document.ttl is not None
```

Zainstaluj okresowe czyszczenie raz przy uruchamianiu aplikacji. Wymaga APOC i tworzy zadanie po stronie serwera, które uruchamia się od razu, a potem co godzinę.

```python
from node4j.mixins import TTLMixin


await TTLMixin.setup_ttl_infrastructure()
```

## Miękkie usuwanie

Wywołaj `setup_soft_delete_manager()` raz dla modelu, zanim zaczniesz go używać. Menedżer `.q` ukrywa usunięte węzły; `.all_objects` nadal je znajduje, aby można je było przywrócić.

```python
from node4j.mixins import SoftDeleteMixin


class Article(SoftDeleteMixin):
    title: str


Article.setup_soft_delete_manager()
article = await Article.q.create(title="Draft")
await article.soft_delete()

filters = {"uid": str(article.uid)}
assert await Article.q.match_one(filters=filters) is None

deleted_article = await Article.all_objects.match_one(filters=filters)
assert deleted_article is not None
await deleted_article.restore()
assert await Article.q.match_one(filters=filters) is not None
```
