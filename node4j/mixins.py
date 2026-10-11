# NOWY PLIK: node4j/mixins.py
from __future__ import annotations

import datetime
import logging  # ### ZMIANA ###

from .db import connection
from .nodes import Node

# ### ZMIANA ###: Inicjalizacja loggera dla modułu
log = logging.getLogger(__name__)

# Zapytanie wykonywane okresowo przez zadanie APOC 'ttl_cleanup_job'.
# Etykieta pochodzi od nazwy klasy mixinu, a `ttl` jest zapisany jako tekst ISO
# (model_dump(mode="json")), więc przed porównaniem zamieniamy go na datetime.
# Natywny datetime też jest obsługiwany. Tekst spoza wzorca (także bez strefy
# czasowej) jest pomijany i nie wygasa, bo jeden błąd datetime() przerwałby cały
# przebieg czyszczenia. Wzorzec pilnuje zakresów pól, ale nie długości miesiąca:
# np. '2026-02-30T00:00:00Z' nadal przerwie przebieg.
# Data i czas ISO ze strefą, jak z pydantic: 2026-10-11T18:00:00.123456Z
_ISO_DATETIME_PATTERN = (
    r"\\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])"
    r"T([01]\\d|2[0-3]):[0-5]\\d(:[0-5]\\d(\\.\\d+)?)?"
    r"(Z|[+-]([01]\\d|2[0-3]):[0-5]\\d)"
)
TTL_CLEANUP_QUERY = f"""
        MATCH (n:TTLMixin)
        WHERE n.ttl IS NOT NULL
        WITH n, CASE
            WHEN valueType(n.ttl) STARTS WITH 'ZONED DATETIME' THEN n.ttl
            WHEN valueType(n.ttl) STARTS WITH 'STRING'
                AND n.ttl =~ '{_ISO_DATETIME_PATTERN}'
                THEN datetime(n.ttl)
        END AS expires_at
        WHERE expires_at < datetime({{timezone: 'UTC'}})
        WITH n LIMIT 1000
        DETACH DELETE n
        RETURN count(n)
        """


class TTLMixin(Node):
    """
    Model mixin, który dodaje funkcjonalność automatycznego wygasania (TTL).
    Węzły dziedziczące po tym modelu będą miały etykietę :TTLMixin.
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
            "CREATE INDEX ttl_index IF NOT EXISTS FOR (n:TTLMixin) ON (n.ttl)"
        )

        install_query = """
        CALL apoc.periodic.repeat(
            'ttl_cleanup_job',
            $cleanup_query,
            3600 // Powtarzaj co 3600 sekund (1 godzina)
        )
        """

        log.debug("Checking for existing 'ttl_cleanup_job' periodic task.")
        existing_jobs_result = await connection.run("CALL apoc.periodic.list()")
        job_exists = any(
            job["name"] == "ttl_cleanup_job" for job in existing_jobs_result
        )

        # Istniejące zadanie może mieć zapytanie z wcześniejszej wersji biblioteki,
        # więc zawsze instalujemy je od nowa z bieżącym zapytaniem.
        if job_exists:
            log.info("Periodic TTL cleanup job exists. Reinstalling...")
            await connection.run("CALL apoc.periodic.cancel('ttl_cleanup_job')")
        await connection.run(install_query, {"cleanup_query": TTL_CLEANUP_QUERY})
        log.info("Successfully installed periodic TTL cleanup job.")

    def set_expiry(self, lifespan: datetime.timedelta):
        """
        Ustawia czas wygaśnięcia dla tej instancji.
        :param lifespan: Czas życia od teraz (np. `timedelta(hours=24)`).
        """
        self.ttl = datetime.datetime.now(datetime.timezone.utc) + lifespan
        # ### ZMIANA ###: Logowanie ustawienia daty wygaśnięcia
        log.debug(
            "Set expiry for node.",
            extra={"node_uid": str(self.uid), "expires_at": self.ttl.isoformat()},
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
            extra={
                "node_uid": str(self.uid),
                "deleted_at": self.deleted_at.isoformat(),
            },
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
        if hasattr(cls, "all_objects"):
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
                "all_objects_manager": "all_objects (shows all objects)",
            },
        )


# ### ZMIANA ###: Usunięcie zduplikowanego kodu SoftDeleteManager.
# Zakładamy, że znajduje się on w `node4j/managers.py`.
