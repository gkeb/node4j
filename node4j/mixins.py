# NOWY PLIK: node4j/mixins.py
from __future__ import annotations
import datetime
from .nodes import Node
from .db import connection  # Importujemy connection do zapisu
from .query import Q  # Importujemy Q do filtrowania

class TTLMixin(Node):
    """
    Model mixin, który dodaje funkcjonalność automatycznego wygasania (TTL).
    Węzły dziedziczące po tym modelu będą miały etykietę :TTL.
    """

    # Pole do przechowywania czasu wygaśnięcia
    ttl: datetime.datetime | None = None

    @staticmethod
    async def setup_ttl_infrastructure():
        """
        Instaluje w bazie indeks i zadanie okresowe potrzebne do obsługi TTL.
        Tę metodę należy wywołać raz podczas startu aplikacji.
        """
        print("--- Konfiguracja infrastruktury TTL ---")
        # 1. Tworzenie indeksu na polu ttl dla etykiety :TTL
        await connection.run(
            "CREATE INDEX ttl_index IF NOT EXISTS FOR (n:TTL) ON (n.ttl)"
        )

        # 2. Instalacja okresowego zadania czyszczącego.
        # Używamy apoc.periodic.repeat, które jest do tego idealne.
        # Zapewniamy, że porównanie odbywa się w strefie czasowej UTC
        cleanup_query = """
        MATCH (n:TTL) WHERE n.ttl IS NOT NULL AND n.ttl < datetime({timezone: 'UTC'})
        WITH n LIMIT 1000
        DETACH DELETE n
        RETURN count(n)
        """
        # *** KONIEC POPRAWKI ***
        
        # Zapytanie instalujące zadanie
        install_query = """
        CALL apoc.periodic.repeat(
            'ttl_cleanup_job',
            $cleanup_query,
            3600 // Powtarzaj co 3600 sekund (1 godzina)
        )
        """
        
        # Sprawdzamy, czy zadanie już istnieje, aby uniknąć błędów
        existing_jobs_result = await connection.run("CALL apoc.periodic.list()")
        job_exists = any(job['name'] == 'ttl_cleanup_job' for job in existing_jobs_result)

        if not job_exists:
            await connection.run(install_query, {"cleanup_query": cleanup_query})
            print("Skonfigurowano okresowe zadanie czyszczące TTL.")
        else:
            print("Okresowe zadanie czyszczące TTL już istnieje.")

    def set_expiry(self, lifespan: datetime.timedelta):
        """
        Ustawia czas wygaśnięcia dla tej instancji.
        :param lifespan: Czas życia od teraz (np. `timedelta(hours=24)`).
        """
        self.ttl = datetime.datetime.now(datetime.timezone.utc) + lifespan

    async def save_with_expiry(self, lifespan: datetime.timedelta):
        """Pomocnicza metoda do ustawienia TTL i zapisu w jednym kroku."""
        self.set_expiry(lifespan)
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
        print(f"Miękko usunięto węzeł: {self.uid}")

    async def restore(self):
        """
        Przywraca miękko usuniętą instancję.
        *** NOWA, ZIMPLEMENTOWANA METODA ***
        """
        self.is_deleted = False
        self.deleted_at = None

        await self.__class__.all_objects.update(
            filters={"uid": str(self.uid)},
            data={"is_deleted": False, "deleted_at": None},
        )
        print(f"Przywrócono węzeł: {self.uid}")


    @classmethod
    def setup_soft_delete_manager(cls):
        """
        Instaluje system podwójnego menedżera:
        - `cls.q`: domyślny menedżer, który filtruje usunięte obiekty.
        - `cls.all_objects`: menedżer, który widzi wszystkie obiekty (w tym usunięte).
        """
        # Sprawdzamy, czy setup nie został już wykonany, aby uniknąć pętli
        if hasattr(cls, 'all_objects'):
            return
            
        from .managers import SoftDeleteManager # Import wewnątrz, aby uniknąć cyklicznych importów
        
        # 1. Zapisujemy oryginalny, "surowy" menedżer pod nową nazwą
        cls.all_objects = cls.q
        
        # 2. Nadpisujemy domyślny menedżer `q` instancją naszego specjalnego menedżera
        cls.q = SoftDeleteManager(cls)
        
        print(f"Zainstalowano menedżer soft-delete dla modelu {cls.__name__}")
        print(f"  -> Użyj `{cls.__name__}.q` do zapytań o aktywne obiekty.")
        print(f"  -> Użyj `{cls.__name__}.all_objects` aby zobaczyć wszystko.")

# W osobnym pliku, np. node4j/managers.py, powinna znaleźć się ta klasa.
# Dla uproszczenia umieszczam ją tutaj, ale docelowo powinna być w osobnym module.

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

    async def count(self, filters: dict | Q | None = None) -> int:
        final_filters = await self._apply_soft_delete_filter(filters)
        return await super().count(filters=final_filters)