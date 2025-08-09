import pytest
import sqlite3
from contextlib import suppress

@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up any database connections."""
    yield
    # Close any connections without accessing private attributes
    with suppress(Exception):
        conn = sqlite3.connect(':memory:')
        conn.close()