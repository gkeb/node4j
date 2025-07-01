# NOWY PLIK: node4j/mixins.py
from __future__ import annotations
import datetime
from .nodes import Node
from .ext.apoc import apoc  # Będziemy potrzebować naszego menedżera triggerów


class TTLMixin(Node):
    """
    Model mixin, który dodaje funkcjonalność automatycznego wygasania (TTL).
    Węzły dziedziczące po tym modelu będą miały etykietę :TTL.
    """

    ttl: datetime.datetime | None = None

    @staticmethod
    async def setup_ttl_infrastructure():
        """
        Instaluje w bazie indeks i trigger potrzebne do obsługi TTL.
        Tę metodę należy wywołać raz podczas startu aplikacji.
        """
        print("--- Konfiguracja infrastruktury TTL ---")
        # 1. Tworzenie indeksu na polu ttl dla etykiety :TTL
        await connection.run(
            "CREATE INDEX ttl_index IF NOT EXISTS FOR (n:TTL) ON (n.ttl)"
        )

        # 2. Instalacja triggera, który będzie okresowo czyścił wygasłe węzły
        # Użyjemy `apoc.periodic.repeat`, który jest do tego lepszy niż trigger.
        # Trigger uruchamia się przy każdej transakcji, a my chcemy to robić np. co godzinę.
        query = """
        CALL apoc.periodic.repeat(
            'ttl_cleanup_job',
            'MATCH (n:TTL) WHERE n.ttl < timestamp() WITH n LIMIT 1000 DETACH DELETE n RETURN count(n)',
            3600 // Powtarzaj co 3600 sekund (1 godzina)
        )
        """
        # Uwaga: apoc.periodic.repeat tworzy zadanie w tle.
        await connection.run(query)
        print("Skonfigurowano okresowe zadanie czyszczące TTL.")

    def set_expiry(self, lifespan: datetime.timedelta):
        """
        Ustawia czas wygaśnięcia dla tej instancji.
        :param lifespan: Czas życia od teraz (np. `timedelta(hours=24)`).
        """
        self.ttl = datetime.datetime.now(datetime.timezone.utc) + lifespan

    async def save_with_expiry(self, lifespan: datetime.timedelta):
        """Pomocnicza metoda do ustawienia TTL i zapisu w jednym kroku."""
        self.set_expiry(lifespan)
        # Zakładając, że `save` to przyszła metoda do aktualizacji instancji
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

        # Używamy standardowej metody update naszego OGM
        await self.q.update(
            filters={"uid": str(self.uid)},
            data={"is_deleted": True, "deleted_at": self.deleted_at},
        )
        print(f"Miękko usunięto węzeł: {self.uid}")

    async def restore(self):
        """Przywraca miękko usuniętą instancję."""
        # ... logika przywracania ...

    # Można by nadpisać menedżera, aby domyślnie filtrował `is_deleted = false`
    @classmethod
    def setup_soft_delete_manager(cls):
        """Nadpisuje domyślny manager, aby automatycznie filtrował usunięte obiekty."""
        original_match_all = cls.q.match_all

        async def new_match_all(filters: dict | Q | None = None, **kwargs):
            active_filter = Q(is_deleted=False)
            if filters:
                q_obj = filters if isinstance(filters, Q) else Q(**filters)
                active_filter &= q_obj

            return await original_match_all(filters=active_filter, **kwargs)

        cls.q.match_all = new_match_all
        print(f"Zainstalowano menedżer soft-delete dla modelu {cls.__name__}")
