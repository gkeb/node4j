# Mixins

[Polski](../pl/mixins.md) · [README](../../README.md)

## Models that inherit a mixin

`TTLMixin` and `SoftDeleteMixin` inherit from `Node`, so each mixin is also a registered model with its own label. A model that inherits one of them also inherits the mixin's label.

## Expiring nodes with TTL

Inherit from `TTLMixin` to add a `ttl` expiry field. `set_expiry()` changes the value on the instance; `save_with_expiry()` sets it and persists it for an already saved node.

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

Install the periodic cleanup once when the application starts. It uses APOC and creates a server-side job that runs immediately and then once an hour.

```python
from node4j.mixins import TTLMixin


await TTLMixin.setup_ttl_infrastructure()
```

## Soft deletion

Call `setup_soft_delete_manager()` once for a model before using it. Its `.q` manager hides deleted nodes; `.all_objects` can still find them so they can be restored.

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
