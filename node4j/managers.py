# W pliku manager.py lub nowym pliku managers.py

from .query import Q
from .manager import NodeManager

class SoftDeleteManager(NodeManager):
    """
    Manager, który automatycznie filtruje zapytania, aby wykluczyć
    obiekty oznaczone jako is_deleted=True.
    """
    async def _apply_soft_delete_filter(self, filters: dict | Q | None = None) -> Q:
        """Pomocnicza metoda do budowania filtra."""
        active_filter = Q(is_deleted=False)
        if not filters:
            return active_filter
        
        q_obj = filters if isinstance(filters, Q) else Q(**filters)
        return active_filter & q_obj

    async def match_all(self, filters: dict | Q | None = None, **kwargs):
        final_filters = await self._apply_soft_delete_filter(filters)
        return await super().match_all(filters=final_filters, **kwargs)

    async def match_one(self, filters: dict | Q, **kwargs):
        final_filters = await self._apply_soft_delete_filter(filters)
        return await super().match_one(filters=final_filters, **kwargs)

    async def count(self, filters: dict | Q | None = None, **kwargs) -> int:
        final_filters = await self._apply_soft_delete_filter(filters)
        return await super().count(filters=final_filters, **kwargs)
    
    # Metody update i delete też powinny być zmodyfikowane,
    # aby operowały na właściwych obiektach.