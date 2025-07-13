# node4j/__init__.py
node_registry = {}

import logging

# 1. Uzyskaj logger dla całego pakietu 'node4j'.
#    Każdy moduł wewnątrz pakietu, który wywoła `logging.getLogger(__name__)`,
#    automatycznie odziedziczy ten logger i jego ustawienia.
#    np. w `node4j/db.py` logger będzie miał nazwę `node4j.db`.
log = logging.getLogger(__name__)

# 2. Dodaj NullHandler. To jest absolutnie kluczowe dla bibliotek.
#    Zapobiega to wyświetlaniu komunikatu "No handler for logger..." na konsoli użytkownika,
#    jeśli *on sam* nie skonfigurował logowania w swojej aplikacji.
#    Biblioteka NIGDY nie powinna zakładać, że logi mają iść na konsolę.
log.addHandler(logging.NullHandler())

# Opcjonalnie, możesz tu też wyeksportować kluczowe elementy biblioteki
# from .nodes import Node
# from .db import connection
# ...
