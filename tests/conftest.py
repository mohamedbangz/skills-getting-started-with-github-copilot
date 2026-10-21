import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

_ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities database after every test."""
    yield
    activities.clear()
    activities.update(copy.deepcopy(_ORIGINAL_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)
