"""Tests for TableService."""

from unittest.mock import MagicMock

from postgres_dba.commands.table import TableService
from postgres_dba.models.postgres.table import PartitionTableInfo, TableInfo

_SAMPLE_TABLE_INFO = TableInfo(
    data="8192 bytes",
    index="16 kB",
    total="24 kB",
    columns=5,
    rows=1000,
    dead=10,
    bloat=1.0,
    vacuum=3,
    autovacuum="2026-01-01 00:00:00 UTC",
    analyze="2026-01-01 00:00:00 UTC",
    autoanalyze="2026-01-01 00:00:00 UTC",
)

_SAMPLE_PARTITION_INFO = [
    PartitionTableInfo(
        data="4096 bytes",
        index="8 kB",
        total="12 kB",
        columns=5,
        rows=500,
        dead=5,
        bloat=1.0,
        vacuum=1,
        autovacuum="2026-01-01 00:00:00 UTC",
        analyze="2026-01-01 00:00:00 UTC",
        autoanalyze="2026-01-01 00:00:00 UTC",
        partition="public.orders_2026_01",
    ),
]


def test_table_service_info_regular() -> None:
    """Test TableService.info returns single row for a regular table."""
    mock_db = MagicMock()
    mock_db.schema.return_value.table.return_value.is_parent_partition.return_value = False
    mock_db.schema.return_value.table.return_value.table_info.return_value = _SAMPLE_TABLE_INFO

    result = TableService(mock_db).info("public", "orders")

    assert result == [_SAMPLE_TABLE_INFO]
    mock_db.schema.assert_called_once_with("public")
    mock_db.schema.return_value.table.assert_called_once_with("orders")


def test_table_service_info_regular_not_found() -> None:
    """Test TableService.info returns empty list when table not found."""
    mock_db = MagicMock()
    mock_db.schema.return_value.table.return_value.is_parent_partition.return_value = False
    mock_db.schema.return_value.table.return_value.table_info.return_value = None

    result = TableService(mock_db).info("public", "missing")

    assert result == []


def test_table_service_info_partitioned() -> None:
    """Test TableService.info returns partition rows for a partitioned table."""
    mock_db = MagicMock()
    mock_db.schema.return_value.table.return_value.is_parent_partition.return_value = True
    mock_db.schema.return_value.table.return_value.partition_table_info.return_value = _SAMPLE_PARTITION_INFO

    result = TableService(mock_db).info("public", "orders")

    assert result == _SAMPLE_PARTITION_INFO
    mock_db.schema.return_value.table.return_value.partition_table_info.assert_called_once()
