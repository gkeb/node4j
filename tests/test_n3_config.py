from node4j.config import Settings


def test_N3_default_settings_without_environment_or_env_file(monkeypatch):
    monkeypatch.delenv("NODE4J_URI", raising=False)
    monkeypatch.delenv("NODE4J_USER", raising=False)
    monkeypatch.delenv("NODE4J_PASSWORD", raising=False)

    settings = Settings(_env_file=None)

    assert settings.uri == "bolt://127.0.0.1:7687"
    assert settings.user == "neo4j"
    assert settings.password == "password"


def test_N3_settings_read_dotenv_file(tmp_path, monkeypatch):
    monkeypatch.delenv("NODE4J_URI", raising=False)
    monkeypatch.delenv("NODE4J_USER", raising=False)
    monkeypatch.delenv("NODE4J_PASSWORD", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "NODE4J_URI=bolt://dotenv.example:7687\n"
        "NODE4J_USER=dotenv-user\n"
        "NODE4J_PASSWORD=example\n",
        encoding="utf-8",
    )

    settings = Settings(_env_file=env_file)

    assert settings.uri == "bolt://dotenv.example:7687"
    assert settings.user == "dotenv-user"
    assert settings.password == "example"


def test_N3_settings_read_environment_variables(monkeypatch):
    monkeypatch.setenv("NODE4J_URI", "bolt://environment.example:7687")
    monkeypatch.setenv("NODE4J_USER", "environment-user")
    monkeypatch.setenv("NODE4J_PASSWORD", "environment-value")

    settings = Settings(_env_file=None)

    assert settings.uri == "bolt://environment.example:7687"
    assert settings.user == "environment-user"
    assert settings.password == "environment-value"


def test_N3_environment_variables_take_precedence_over_dotenv(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "NODE4J_URI=bolt://dotenv.example:7687\n"
        "NODE4J_USER=dotenv-user\n"
        "NODE4J_PASSWORD=dotenv-value\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("NODE4J_URI", "bolt://environment.example:7687")
    monkeypatch.setenv("NODE4J_USER", "environment-user")
    monkeypatch.setenv("NODE4J_PASSWORD", "environment-value")

    settings = Settings(_env_file=env_file)

    assert settings.uri == "bolt://environment.example:7687"
    assert settings.user == "environment-user"
    assert settings.password == "environment-value"


def test_N3_default_settings_read_cwd_dotenv_and_environment_overrides(
    tmp_path, monkeypatch
):
    (tmp_path / ".env").write_text(
        "NODE4J_URI=bolt://dotenv.example:7687\n"
        "NODE4J_USER=dotenv-user\n"
        "NODE4J_PASSWORD=dotenv-value\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NODE4J_URI", raising=False)
    monkeypatch.delenv("NODE4J_USER", raising=False)
    monkeypatch.delenv("NODE4J_PASSWORD", raising=False)

    from_dotenv = Settings()

    assert from_dotenv.uri == "bolt://dotenv.example:7687"
    assert from_dotenv.user == "dotenv-user"
    assert from_dotenv.password == "dotenv-value"

    monkeypatch.setenv("NODE4J_URI", "bolt://environment.example:7687")
    with_environment = Settings()

    assert with_environment.uri == "bolt://environment.example:7687"
    assert with_environment.user == "dotenv-user"
    assert with_environment.password == "dotenv-value"
