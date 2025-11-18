from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from inspectah.ui import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
