# W pliku manager.py lub nowym pliku managers.py
import logging  # ### ZMIANA ###

from .query import Q
from .manager import NodeManager

# ### ZMIANA ###: Inicjalizacja loggera dla modułu
log = logging.getLogger(__name__)

class SoftDeleteManager(NodeManager):
    """
    Manager, który automatycznie filtruje zapytania, aby wykluczyć
    obiekty oznaczone jako is_deleted=True.
    """
    # ### ZMIANA ###: Dodajemy logowanie do konstruktora, aby było jasne, że to specjalny menedżer
    def __init__(self, node_model):
        super().__init__(node_model)
        # Używamy loggera z klasy bazowej, który jest już specyficzny dla modelu
        self.log.info("Initialized SoftDeleteManager. Queries will be filtered for active objects (is_deleted=False).")

    async def _apply_soft_delete_filter(self, filters: dict | Q | None = None) -> Q:
        """Pomocnicza metoda do budowania filtra."""
        active_filter = Q(is_deleted=False)

        # ### ZMIANA ###: Logowanie faktu dodania filtra
        self.log.debug(
            "Applying soft-delete filter (is_deleted=False) to the query.",
            extra={"original_filters": filters}
        )

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
    # ### ZMIANA ###: Sugerowane implementacje z dodanym filtrowaniem
    async def update(self, filters: dict | Q, data: dict) -> int:
        final_filters = await self._apply_soft_delete_filter(filters)
        return await super().update(filters=final_filters, data=data)
        
    async def delete(self, filters: dict | Q) -> int:
        final_filters = await self._apply_soft_delete_filter(filters)
        return await super().delete(filters=final_filters)