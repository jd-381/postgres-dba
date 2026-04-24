"""Tests for ProcesslistService."""

from unittest.mock import MagicMock

from postgres_dba.commands.processlist import ProcesslistService
from postgres_dba.models.postgres.processlist import Processlist, ProcesslistFilter

_SAMPLE_PROCESSES = [
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


def test_processlist_service_info() -> None:
    """Test ProcesslistService.info delegates to processlist model."""
    mock_db = MagicMock()
    mock_db.processlist.return_value.info.return_value = _SAMPLE_PROCESSES
    filter = ProcesslistFilter()

    result = ProcesslistService(mock_db).info(filter)

    assert result == _SAMPLE_PROCESSES
    mock_db.processlist.return_value.info.assert_called_once_with(filter)


def test_processlist_service_info_with_filter() -> None:
    """Test ProcesslistService.info passes filter through to processlist model."""
    mock_db = MagicMock()
    mock_db.processlist.return_value.info.return_value = [_SAMPLE_PROCESSES[0]]
    filter = ProcesslistFilter(active=True, users=["postgres"], limit=5)

    result = ProcesslistService(mock_db).info(filter)

    assert result == [_SAMPLE_PROCESSES[0]]
    mock_db.processlist.return_value.info.assert_called_once_with(filter)
