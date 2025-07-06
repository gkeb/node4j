# NOWY PLIK: node4j/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Model Pydantic do zarządzania konfiguracją aplikacji.
    Automatycznie wczytuje zmienne środowiskowe lub wartości z pliku .env.
    Jest zgodny z najnowszą wersją pydantic-settings.
    """
    
    # Zamiast wewnętrznej klasy `Config`, używamy `model_config` z `SettingsConfigDict`.
    # To jest nowoczesny sposób konfiguracji w Pydantic V2.
    model_config = SettingsConfigDict(
        env_prefix='NODE4J_', 
        env_file='.env', 
        env_file_encoding='utf-8',
        # Dodatkowa opcja, która może być przydatna: ignorowanie dodatkowych
        # zmiennych środowiskowych, które nie pasują do modelu.
        extra='ignore' 
    )

    # Definicja zmiennych konfiguracyjnych z typami i wartościami domyślnymi
    # pozostaje bez zmian.
    uri: str = "bolt://127.0.0.1:7687"
    user: str = "neo4j"
    password: str = "password"

# Tworzymy globalną instancję singletona, która będzie importowana 
# w innych częściach aplikacji.
settings = Settings()