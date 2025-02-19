import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from src.core.config import getDbSettings

DATABASE_URL = getDbSettings().DBURL


@pytest.fixture
def db_engine():
    engine = create_engine(DATABASE_URL)
    yield engine
    engine.dispose()

def test_db_connection(db_engine):
    try:
        with db_engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.scalar() == 1  # Ensure the query returns 1
    except OperationalError:
        pytest.fail("Database connection failed")
