import pytest


@pytest.fixture(autouse=True)
async def _clean_state(clean_db):
    yield
