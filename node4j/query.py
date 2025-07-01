# NOWY PLIK: node4j/query.py

from __future__ import annotations
import enum


class QConnector(str, enum.Enum):
    AND = "AND"
    OR = "OR"


class Q:
    """Reprezentuje warunek lub grupę warunków w zapytaniu (klauzula WHERE)."""

    def __init__(self, **kwargs):
        self.children: list[tuple[QConnector, Q] | tuple[str, Any]] = []
        self.connector = QConnector.AND
        self.negated = False

        # Inicjalizacja z filtrami klucz-wartość, np. Q(name="Alice", age__gt=30)
        for key, value in kwargs.items():
            self.children.append((key, value))

    def to_cypher(self, node_alias: str, param_counter: list[int]) -> tuple[str, dict]:
        """Tłumaczy obiekt Q na fragment zapytania Cypher i parametry."""
        if not self.children:
            return "", {}

        parts = []
        params = {}

        for child in self.children:
            if isinstance(child, Q):
                # Zagnieżdżony obiekt Q
                cypher, child_params = child.to_cypher(node_alias, param_counter)
                if cypher:
                    parts.append(f"({cypher})")
                    params.update(child_params)
            else:
                # Krotka (klucz, wartość)
                key, value = child

                # Tworzenie unikalnej nazwy parametru, aby uniknąć kolizji
                param_name = f"p_{param_counter[0]}"
                param_counter[0] += 1

                parts.append(self._compile_clause(node_alias, key, param_name))
                params[param_name] = value

        cypher_str = f" {self.connector.value} ".join(parts)

        if self.negated:
            return f"NOT ({cypher_str})", params
        return cypher_str, params

    def _compile_clause(self, node_alias: str, key: str, param_name: str) -> str:
        """Kompiluje pojedynczy warunek, np. 'node.age > $p_1'."""
        operator_map = {
            "gt": ">",
            "gte": ">=",
            "lt": "<",
            "lte": "<=",
            "in": "IN",
            "contains": "CONTAINS",
            "startswith": "STARTS WITH",
            "endswith": "ENDS WITH",
            "ne": "<>",
        }

        field, _, op_suffix = key.partition("__")
        op = operator_map.get(op_suffix, "=")

        return f"{node_alias}.`{field}` {op} ${param_name}"

    def _combine(self, other: Q, connector: QConnector) -> Q:
        """Łączy dwa obiekty Q."""
        if not isinstance(other, Q):
            raise TypeError("Można łączyć tylko z innym obiektem Q.")

        # Jeśli ten obiekt jest pusty, zwróć drugi
        if not self.children:
            return other
        # Jeśli drugi jest pusty, zwróć ten
        if not other.children:
            return self

        new_q = Q()
        new_q.connector = connector
        new_q.children.append(self)
        new_q.children.append(other)
        return new_q

    def __and__(self, other: Q) -> Q:
        return self._combine(other, QConnector.AND)

    def __or__(self, other: Q) -> Q:
        return self._combine(other, QConnector.OR)

    def __invert__(self) -> Q:
        new_q = Q()
        # Kopiujemy dzieci, aby nie modyfikować oryginału
        new_q.children = list(self.children)
        new_q.connector = self.connector
        new_q.negated = not self.negated
        return new_q
