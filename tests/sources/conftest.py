import importlib
import os

import pytest

from app.sources import service


@pytest.fixture(autouse=True)
def isolated_s21_db(tmp_path, monkeypatch):
    db_path = tmp_path / "s21_sources.sqlite"
    monkeypatch.setenv("INSPECTAH_S21_DB_PATH", str(db_path))
    migration = importlib.import_module("migrations.versions.0002_s21_sources_schema")
    migration.apply_migration(db_path)
    importlib.reload(service)
    yield
