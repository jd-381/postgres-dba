"""Tests for the processlist commands."""

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from postgres_dba.main import app
from postgres_dba.models.postgres.processlist import Processlist, ProcesslistFilter

runner = CliRunner()

SAMPLE_PROCESSES = [
    Processlist(
        pid="1234",
        user="postgres",
        client="psql",
        client_addr="127.0.0.1",
        database="postgres",
        conn_dur="00:01:00",
        trx_dur="00:00:05",
        query_dur="00:00:05",
        state="active",
        wait="",
        backend="client backend",
        query_id="111222333",
        query="SELECT 1",
    ),
    Processlist(
        pid="5678",
        user="app_user",
        client="app",
        client_addr="10.0.0.1",
        database="mydb",
        conn_dur="00:10:00",
        trx_dur="",
        query_dur="",
        state="idle",
        wait="",
        backend="client backend",
        query_id="444555666",
        query="SELECT 2",
    ),
]


@pytest.fixture
def mock_db():
    """Mock PostgresInstance and PostgresDatabase for processlist CLI commands."""
    with (
        patch("postgres_dba.commands.processlist.PostgresInstance.from_env_vars"),
        patch("postgres_dba.commands.processlist.PostgresDatabase.from_instance") as mock_db_cm,
    ):
        mock_db_obj = MagicMock()
        mock_db_cm.return_value.__enter__ = MagicMock(return_value=mock_db_obj)
        mock_db_cm.return_value.__exit__ = MagicMock(return_value=False)
        yield mock_db_obj


def test_processlist_default(mock_db):
    """Test processlist with default options."""
    mock_db.processlist.return_value.info.return_value = SAMPLE_PROCESSES

    result = runner.invoke(app, ["proc"])
    assert result.exit_code == 0
    assert "Processlist" in result.stdout


def test_processlist_active_only(mock_db):
    """Test processlist --active flag filters to active queries."""
    mock_db.processlist.return_value.info.return_value = [SAMPLE_PROCESSES[0]]

    result = runner.invoke(app, ["proc", "--active"])
    assert result.exit_code == 0

    called_filter: ProcesslistFilter = mock_db.processlist.return_value.info.call_args[0][0]
    assert called_filter.active is True


def test_processlist_active_short_option(mock_db):
    """Test processlist -a short flag."""
    mock_db.processlist.return_value.info.return_value = [SAMPLE_PROCESSES[0]]

    result = runner.invoke(app, ["proc", "-a"])
    assert result.exit_code == 0

    called_filter: ProcesslistFilter = mock_db.processlist.return_value.info.call_args[0][0]
    assert called_filter.active is True


def test_processlist_slots(mock_db):
    """Test processlist --slots includes replication processes."""
    mock_db.processlist.return_value.info.return_value = SAMPLE_PROCESSES

    result = runner.invoke(app, ["proc", "--slots"])
    assert result.exit_code == 0

    called_filter: ProcesslistFilter = mock_db.processlist.return_value.info.call_args[0][0]
    assert called_filter.slots is True


def test_processlist_with_limit(mock_db):
    """Test processlist --limit option."""
    mock_db.processlist.return_value.info.return_value = SAMPLE_PROCESSES

    result = runner.invoke(app, ["proc", "--limit", "5"])
    assert result.exit_code == 0

    called_filter: ProcesslistFilter = mock_db.processlist.return_value.info.call_args[0][0]
    assert called_filter.limit == 5


def test_processlist_default_limit(mock_db):
    """Test processlist defaults to limit of 10."""
    mock_db.processlist.return_value.info.return_value = SAMPLE_PROCESSES

    runner.invoke(app, ["proc"])

    called_filter: ProcesslistFilter = mock_db.processlist.return_value.info.call_args[0][0]
    assert called_filter.limit == 10


def test_processlist_filter_pids(mock_db):
    """Test processlist --pids filter."""
    mock_db.processlist.return_value.info.return_value = [SAMPLE_PROCESSES[0]]

    result = runner.invoke(app, ["proc", "--pids", "1234"])
    assert result.exit_code == 0

    called_filter: ProcesslistFilter = mock_db.processlist.return_value.info.call_args[0][0]
    assert called_filter.pids == ["1234"]


def test_processlist_ignore_pids(mock_db):
    """Test processlist --ipids filter."""
    mock_db.processlist.return_value.info.return_value = [SAMPLE_PROCESSES[1]]

    result = runner.invoke(app, ["proc", "--ipids", "1234"])
    assert result.exit_code == 0

    called_filter: ProcesslistFilter = mock_db.processlist.return_value.info.call_args[0][0]
    assert called_filter.ipids == ["1234"]


def test_processlist_filter_users(mock_db):
    """Test processlist --users filter."""
    mock_db.processlist.return_value.info.return_value = [SAMPLE_PROCESSES[1]]

    result = runner.invoke(app, ["proc", "--users", "app_user"])
    assert result.exit_code == 0

    called_filter: ProcesslistFilter = mock_db.processlist.return_value.info.call_args[0][0]
    assert called_filter.users == ["app_user"]


def test_processlist_ignore_users(mock_db):
    """Test processlist --iusers filter."""
    mock_db.processlist.return_value.info.return_value = [SAMPLE_PROCESSES[0]]

    result = runner.invoke(app, ["proc", "--iusers", "app_user"])
    assert result.exit_code == 0

    called_filter: ProcesslistFilter = mock_db.processlist.return_value.info.call_args[0][0]
    assert called_filter.iusers == ["app_user"]


def test_processlist_filter_queries(mock_db):
    """Test processlist --queries filter."""
    mock_db.processlist.return_value.info.return_value = [SAMPLE_PROCESSES[0]]

    result = runner.invoke(app, ["proc", "--queries", "111222333"])
    assert result.exit_code == 0

    called_filter: ProcesslistFilter = mock_db.processlist.return_value.info.call_args[0][0]
    assert called_filter.queries == ["111222333"]


def test_processlist_ignore_queries(mock_db):
    """Test processlist --iqueries filter."""
    mock_db.processlist.return_value.info.return_value = [SAMPLE_PROCESSES[1]]

    result = runner.invoke(app, ["proc", "--iqueries", "111222333"])
    assert result.exit_code == 0

    called_filter: ProcesslistFilter = mock_db.processlist.return_value.info.call_args[0][0]
    assert called_filter.iqueries == ["111222333"]


def test_processlist_db_error(mock_db):
    """Test that a database error exits with code 1."""
    mock_db.processlist.side_effect = Exception("connection refused")

    result = runner.invoke(app, ["proc"])
    assert result.exit_code == 1
