from typing import Dict, Type, TYPE_CHECKING

# Używamy TYPE_CHECKING do uniknięcia cyklicznych importów
# podczas sprawdzania typów. W czasie wykonania ten blok jest ignorowany.
if TYPE_CHECKING:
    from .nodes import Node

# Globalny rejestr mapujący etykiety (string) na klasy modeli (type).
# Zostanie on automatycznie zapełniony przez metaklasę NodeBase.
# Przykład po inicjalizacji: {'Person': <class 'main.Person'>, 'Company': <class 'main.Company'>}
node_registry: Dict[str, Type["Node"]] = {}
