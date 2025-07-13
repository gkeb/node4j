# node4j/db.py
from __future__ import annotations
import os
import functools
from contextvars import ContextVar
import logging  # ### ZMIANA ###
import time     # ### ZMIANA ###
from neo4j import AsyncGraphDatabase, basic_auth, AsyncTransaction
from contextlib import asynccontextmanager

from .config import settings

# ### ZMIANA ###: Inicjalizacja loggera dla tego modułu
log = logging.getLogger(__name__)

_current_transaction: ContextVar[AsyncTransaction | None] = ContextVar(
    "current_transaction", default=None
)

class AsyncDatabase:
    """
    Nowoczesna, asynchroniczna klasa do obsługi połączenia z Neo4j.
    Wykorzystuje natywne menedżery kontekstu sterownika do zarządzania transakcjami.
    """

    def __init__(self):
        self.driver = None
        # Zachowujemy tę listę jako prosty, wewnętrzny mechanizm historii zapytań
        self.queries = []

    async def connect(self):
        """
        Nawiązuje połączenie z bazą danych. Musi być wywołane raz na starcie aplikacji.
        """
        if self.driver is not None:
            return

        # ### ZMIANA ###: Logowanie próby połączenia (bez hasła!)
        log.info(
            "Attempting to connect to Neo4j database",
            extra={"db_uri": settings.uri, "db_user": settings.user},
        )
        
        try:
            self.driver = AsyncGraphDatabase.driver(
                settings.uri,
                auth=basic_auth(
                    settings.user,
                    settings.password,
                ),
            )
            await self.driver.verify_connectivity()
            # ### ZMIANA ###: Usunięcie print, zastąpienie loggerem
            log.info("Successfully connected to Neo4j.")
        except Exception as e:
            # ### ZMIANA ###: Logowanie błędu połączenia
            log.exception(
                "Failed to connect to Neo4j database",
                extra={"db_uri": settings.uri, "error_type": type(e).__name__},
            )
            self.driver = None # Upewniamy się, że driver jest None w razie błędu
            raise # Rzucamy wyjątek dalej, aby aplikacja mogła zareagować


    async def close(self):
        """
        Zamyka połączenie z bazą danych. Powinno być wywołane przy zamykaniu aplikacji.
        """
        if self.driver:
            await self.driver.close()
            self.driver = None
            # ### ZMIANA ###: Usunięcie print, zastąpienie loggerem
            log.info("Disconnected from Neo4j.")

    @asynccontextmanager
    async def transaction(self):
        """
        Asynchroniczny menedżer kontekstu do obsługi jawnych transakcji.
        Dodatkowo zarządza zmienną kontekstową dla transakcji atomowych.
        """
        if _current_transaction.get() is not None:
            # ### ZMIANA ###: Logowanie błędu przed rzuceniem wyjątku
            log.error("Attempted to nest atomic transactions.")
            raise RuntimeError("Nie można zagnieżdżać transakcji atomowych.")

        if not self.driver:
            await self.connect()

        async with self.driver.session() as session:
            tx = await session.begin_transaction()
            token = _current_transaction.set(tx)
            # ### ZMIANA ###: Logowanie rozpoczęcia transakcji
            log.debug("Beginning new transaction.")
            try:
                yield tx
                if not tx.closed():
                    await tx.commit()
                    # ### ZMIANA ###: Logowanie zatwierdzenia transakcji
                    log.debug("Transaction committed.")
            except Exception:
                if not tx.closed():
                    await tx.rollback()
                    # ### ZMIANA ###: Logowanie wycofania transakcji
                    log.warning("Transaction rolled back due to an exception.", exc_info=True)
                raise
            finally:
                _current_transaction.reset(token)

    def atomic(self):
        """
        Dekorator do opakowywania funkcji w transakcję atomową.
        """
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                async with self.transaction():
                    return await func(*args, **kwargs)
            return wrapper
        return decorator

    async def run(
        self,
        query: str,
        params: dict | None = None,
        *,
        tx: "AsyncTransaction" | None = None,
    ):
        """
        Wykonuje zapytanie Cypher.
        Automatycznie używa transakcji z kontekstu, jeśli jest dostępna.
        """
        if not self.driver:
            await self.connect()

        # Zachowujemy tę listę dla wewnętrznych potrzeb lub prostego debugowania
        self.queries.append((query, params))

        active_tx = tx or _current_transaction.get()
        in_explicit_tx = active_tx is not None
        
        # ### ZMIANA ###: Kompleksowe logowanie wykonania zapytania
        log.debug(
            "Executing Cypher query",
            extra={
                "cypher_query": query,
                "cypher_params": params,
                "in_transaction": in_explicit_tx,
            },
        )
        start_time = time.perf_counter()
        
        try:
            if in_explicit_tx:
                response = await active_tx.run(query, params)
                data = await response.data()
            else:
                async with self.driver.session() as session:
                    response = await session.run(query, params)
                    data = await response.data()
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            log.info(
                "Query executed successfully",
                extra={
                    # Powtórzenie zapytania w logu INFO może być przydatne do korelacji
                    "cypher_query": query,
                    "duration_ms": round(duration_ms, 2),
                    "record_count": len(data),
                },
            )
            return data
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            log.error(
                "Query execution failed",
                exc_info=True, # Automatycznie dodaje traceback
                extra={
                    "cypher_query": query,
                    "cypher_params": params,
                    "duration_ms": round(duration_ms, 2),
                    "error_type": type(e).__name__,
                },
            )
            raise


# Tworzymy globalną instancję singletona
connection = AsyncDatabase()