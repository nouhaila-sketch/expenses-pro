import pytest
import app
import sqlite3
import tempfile
import os


@pytest.fixture(autouse=True)
def _test_db(monkeypatch):
    db_fd, db_path = tempfile.mkstemp()

    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        name TEXT,
        amount REAL,
        category TEXT
    )"""
    )
    conn.commit()
    conn.close()

    monkeypatch.setattr(app, "get_db", lambda: sqlite3.connect(db_path))

    yield

    os.close(db_fd)
    os.unlink(db_path)
