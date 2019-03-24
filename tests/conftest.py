from SQL.postgresqlcommands import DBCommands
import pytest

# Pytest setup file

"""
DATABASE Fixtures
"""


@pytest.fixture(scope='session')
def setup_db():
    ii = DBCommands()
    ii.connect()
    yield ii
    ii.conn.rollback()
    ii.conn.close()
