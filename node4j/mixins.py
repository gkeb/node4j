# NOWY PLIK: node4j/mixins.py
from __future__ import annotations
import datetime
import logging  # ### ZMIANA ###
from .nodes import Node
from .db import connection
from .query import Q

# ### ZMIANA ###: Inicjalizacja loggera dla modułu
log = logging.getLogger(__name__)


class TTLMixin(Node):
    """
    Model mixin, który dodaje funkcjonalność automatycznego wygasania (TTL).
    Węzły dziedziczące po tym modelu będą miały etykietę :TTL.
    """

    ttl: datetime.datetime | None = None

    @staticmethod
    async def setup_ttl_infrastructure():
        """
        Instaluje w bazie indeks i zadanie okresowe potrzebne do obsługi TTL.
        Tę metodę należy wywołać raz podczas startu aplikacji.
        """
        # ### ZMIANA ###: Zastąpienie print loggerem
        log.info("Setting up TTL infrastructure...")
        
        log.debug("Creating TTL index if not exists.")
        await connection.run(
            "CREATE INDEX ttl_index IF NOT EXISTS FOR (n:TTL) ON (n.ttl)"
        )

        cleanup_query = """
        MATCH (n:TTL) WHERE n.ttl IS NOT NULL AND n.ttl < datetime({timezone: 'UTC'})
        WITH n LIMIT 1000
        DETACH DELETE n
        RETURN count(n)
        """
        
        install_query = """
        CALL apoc.periodic.repeat(
            'ttl_cleanup_job',
            $cleanup_query,
            3600 // Powtarzaj co 3600 sekund (1 godzina)
        )
        """
        
        log.debug("Checking for existing 'ttl_cleanup_job' periodic task.")
        existing_jobs_result = await connection.run("CALL apoc.periodic.list()")
        job_exists = any(job['name'] == 'ttl_cleanup_job' for job in existing_jobs_result)

        if not job_exists:
            log.info("Periodic TTL cleanup job not found. Installing...")
            await connection.run(install_query, {"cleanup_query": cleanup_query})
            log.info("Successfully installed periodic TTL cleanup job.")
        else:
            log.info("Periodic TTL cleanup job already exists.")

    def set_expiry(self, lifespan: datetime.timedelta):
        """
        Ustawia czas wygaśnięcia dla tej instancji.
        :param lifespan: Czas życia od teraz (np. `timedelta(hours=24)`).
        """
        self.ttl = datetime.datetime.now(datetime.timezone.utc) + lifespan
        # ### ZMIANA ###: Logowanie ustawienia daty wygaśnięcia
        log.debug(
            "Set expiry for node.", 
            extra={"node_uid": str(self.uid), "expires_at": self.ttl.isoformat()}
        )

    async def save_with_expiry(self, lifespan: datetime.timedelta):
        """Pomocnicza metoda do ustawienia TTL i zapisu w jednym kroku."""
        self.set_expiry(lifespan)
        # Logowanie jest już w `self.q.update`
        await self.q.update(filters={"uid": str(self.uid)}, data={"ttl": self.ttl})


class SoftDeleteMixin(Node):
    """
    Model mixin, który implementuje logikę miękkiego usuwania.
    """
    is_deleted: bool = False
    deleted_at: datetime.datetime | None = None

    async def soft_delete(self):
        """Oznacza instancję jako usuniętą."""
        self.is_deleted = True
        self.deleted_at = datetime.datetime.now(datetime.timezone.utc)

        await self.q.update(
            filters={"uid": str(self.uid)},
            data={"is_deleted": True, "deleted_at": self.deleted_at},
        )
        # ### ZMIANA ###: Zastąpienie print loggerem
        log.info(
            "Node soft-deleted successfully.",
            extra={"node_uid": str(self.uid), "deleted_at": self.deleted_at.isoformat()}
        )

    async def restore(self):
        """
        Przywraca miękko usuniętą instancję.
        """
        self.is_deleted = False
        self.deleted_at = None

        # Używamy `all_objects`, aby mieć pewność, że znajdziemy usunięty obiekt
        await self.__class__.all_objects.update(
            filters={"uid": str(self.uid)},
            data={"is_deleted": False, "deleted_at": None},
        )
        # ### ZMIANA ###: Zastąpienie print loggerem
        log.info("Node restored successfully.", extra={"node_uid": str(self.uid)})

    @classmethod
    def setup_soft_delete_manager(cls):
        """
        Instaluje system podwójnego menedżera:
        - `cls.q`: domyślny menedżer, który filtruje usunięte obiekty.
        - `cls.all_objects`: menedżer, który widzi wszystkie obiekty (w tym usunięte).
        """
        if hasattr(cls, 'all_objects'):
            return
            
        from .managers import SoftDeleteManager
        
        cls.all_objects = cls.q
        cls.q = SoftDeleteManager(cls)
        
        # ### ZMIANA ###: Zastąpienie print loggerem
        # Używamy loggera specyficznego dla klasy, na której wywoływana jest metoda
        class_log = logging.getLogger(f"{__name__}.{cls.__name__}")
        class_log.info(
            "Soft-delete manager installed.",
            extra={
                "default_manager": "q (filters deleted objects)",
                "all_objects_manager": "all_objects (shows all objects)"
            }
        )
        
# ### ZMIANA ###: Usunięcie zduplikowanego kodu SoftDeleteManager.
# Zakładamy, że znajduje się on w `node4j/managers.py`.