import importlib
import os
import sys


def test_defaults_to_sqlite_when_mysql_is_not_enabled(monkeypatch):
    monkeypatch.delenv("USE_MYSQL", raising=False)
    monkeypatch.delenv("MYSQL_HOST", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    sys.modules.pop("config", None)

    config = importlib.import_module("config")

    assert config.Config.SQLALCHEMY_DATABASE_URI.startswith("sqlite:///")


def test_falls_back_to_sqlite_when_mysql_is_unreachable(monkeypatch):
    monkeypatch.setenv("USE_MYSQL", "true")
    monkeypatch.setenv("MYSQL_HOST", "127.0.0.1")
    monkeypatch.setenv("MYSQL_PORT", "1")
    monkeypatch.setenv("MYSQL_USER", "root")
    monkeypatch.setenv("MYSQL_PASSWORD", "test")
    monkeypatch.setenv("MYSQL_DATABASE", "prevento_db")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    sys.modules.pop("config", None)

    config = importlib.import_module("config")

    assert config.Config.SQLALCHEMY_DATABASE_URI.startswith("sqlite:///")
