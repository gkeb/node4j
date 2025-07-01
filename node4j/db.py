# node4j/db.py
from __future__ import annotations
import os
import functools  # <-- NOWY IMPORT
from contextvars import ContextVar  # <-- NOWY IMPORT
from neo4j import AsyncGraphDatabase, basic_auth, AsyncTransaction
from contextlib import asynccontextmanager

# +++ NOWA SEKCJA: CONTEXT VAR +++
# Tworzymy zmienną kontekstową, która będzie przechowywać aktywną transakcję.
# Domyślnie jest pusta.
_current_transaction: ContextVar[AsyncTransaction | None] = ContextVar(
    "current_transaction", default=None
)
# +++ KONIEC NOWEJ SEKCJI +++


class AsyncDatabase:
    """
    Nowoczesna, asynchroniczna klasa do obsługi połączenia z Neo4j.
    Wykorzystuje natywne menedżery kontekstu sterownika do zarządzania transakcjami.
    """

    def __init__(self):
        self.driver = None
        self.queries = []  # Zachowujemy logowanie zapytań - to przydatne!

    async def connect(self):
        """
        Nawiązuje połączenie z bazą danych. Musi być wywołane raz na starcie aplikacji.
        """
        if self.driver is not None:
            return
        self.driver = AsyncGraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
            auth=basic_auth(
                os.getenv("NEO4J_USER", "neo4j"),
                os.getenv("NEO4J_PASSWORD", "password"),
            ),
        )
        await self.driver.verify_connectivity()
        print("Połączono z Neo4j.")

    async def close(self):
        """
        Zamyka połączenie z bazą danych. Powinno być wywołane przy zamykaniu aplikacji.
        """
        if self.driver:
            await self.driver.close()
            self.driver = None
            print("Rozłączono z Neo4j.")

    # +++ POCZĄTEK POPRAWIONEJ METODY +++
    @asynccontextmanager
    async def transaction(self):
        """
        Asynchroniczny menedżer kontekstu do obsługi jawnych transakcji.
        Dodatkowo zarządza zmienną kontekstową dla transakcji atomowych.
        """
        # Sprawdzamy, czy nie próbujemy zagnieździć transakcji
        if _current_transaction.get() is not None:
            raise RuntimeError("Nie można zagnieżdżać transakcji atomowych.")

        if not self.driver:
            await self.connect()

        async with self.driver.session() as session:
            tx = await session.begin_transaction()
            # Ustawiamy token, aby śledzić, że jesteśmy w transakcji
            token = _current_transaction.set(tx)
            try:
                yield tx
                if not tx.closed():
                    await tx.commit()
            except Exception:
                if not tx.closed():
                    await tx.rollback()
                raise
            finally:
                # Zawsze resetujemy token na końcu
                _current_transaction.reset(token)

    # +++ NOWA METODA: DEKORATOR ATOMIC +++
    def atomic(self):
        """
        Dekorator do opakowywania funkcji w transakcję atomową.
        Użycie:
            @connection.atomic()
            async def my_function():
                # ... operacje na bazie ...
        """

        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Po prostu używamy naszego menedżera kontekstu
                async with self.transaction():
                    return await func(*args, **kwargs)

            return wrapper

        return decorator

    # +++ KONIEC NOWEJ METODY +++

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

        self.queries.append((query, params))

        # --- ZMIENIONA LOGIKA ---
        # 1. Sprawdź, czy `tx` zostało przekazane jawnie.
        # 2. Jeśli nie, sprawdź zmienną kontekstową.
        active_tx = tx or _current_transaction.get()

        if active_tx:
            # Jesteśmy w jawnej transakcji, używamy przekazanego obiektu `tx`
            response = await active_tx.run(query, params)
            return await response.data()
        else:
            # Tryb auto-commit, sterownik sam zarządza transakcją
            async with self.driver.session() as session:
                response = await session.run(query, params)
                return await response.data()


# Tworzymy globalną instancję singletona
connection = AsyncDatabase()
