"""Tests for the table commands."""

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from postgres_dba.main import app
from postgres_dba.models.postgres.table import PartitionTableInfo, TableInfo

runner = CliRunner()

SAMPLE_TABLE_INFO = TableInfo(
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

SAMPLE_PARTITION_INFO = [
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
        partition="public.orders_2026_02",
    ),
]


@pytest.fixture
def mock_db():
    """Mock PostgresInstance and PostgresDatabase for table CLI commands."""
    with (
        patch("postgres_dba.commands.table.PostgresInstance.from_env_vars"),
        patch("postgres_dba.commands.table.PostgresDatabase.from_instance") as mock_db_cm,
    ):
        mock_db_obj = MagicMock()
        mock_db_cm.return_value.__enter__ = MagicMock(return_value=mock_db_obj)
        mock_db_cm.return_value.__exit__ = MagicMock(return_value=False)
        yield mock_db_obj


def test_table_info(mock_db):
    """Test table info for a regular table."""
    mock_db.schema.return_value.table.return_value.is_parent_partition.return_value = False
    mock_db.schema.return_value.table.return_value.table_info.return_value = SAMPLE_TABLE_INFO

    result = runner.invoke(app, ["table", "--database", "postgres", "--table", "public.orders"])
    assert result.exit_code == 0
    assert "orders" in result.stdout


def test_table_info_default_schema(mock_db):
    """Test that --table without schema defaults to public."""
    mock_db.schema.return_value.table.return_value.is_parent_partition.return_value = False
    mock_db.schema.return_value.table.return_value.table_info.return_value = SAMPLE_TABLE_INFO

    result = runner.invoke(app, ["table", "--database", "postgres", "--table", "orders"])
    assert result.exit_code == 0
    mock_db.schema.assert_called_once_with("public")
    mock_db.schema.return_value.table.assert_called_once_with("orders")


def test_table_info_short_options(mock_db):
    """Test table info using short option flags."""
    mock_db.schema.return_value.table.return_value.is_parent_partition.return_value = False
    mock_db.schema.return_value.table.return_value.table_info.return_value = SAMPLE_TABLE_INFO

    result = runner.invoke(app, ["table", "-d", "postgres", "-t", "public.orders"])
    assert result.exit_code == 0


def test_table_info_partition(mock_db):
    """Test table info for a partitioned table."""
    mock_db.schema.return_value.table.return_value.is_parent_partition.return_value = True
    mock_db.schema.return_value.table.return_value.partition_table_info.return_value = SAMPLE_PARTITION_INFO

    result = runner.invoke(app, ["table", "--database", "postgres", "--table", "public.orders"])
    assert result.exit_code == 0
    assert "Partition" in result.stdout


def test_table_info_calls_correct_schema_and_table(mock_db):
    """Test that schema and table name are correctly parsed and passed."""
    mock_db.schema.return_value.table.return_value.is_parent_partition.return_value = False
    mock_db.schema.return_value.table.return_value.table_info.return_value = SAMPLE_TABLE_INFO

    runner.invoke(app, ["table", "--database", "mydb", "--table", "myschema.mytable"])
    mock_db.schema.assert_called_once_with("myschema")
    mock_db.schema.return_value.table.assert_called_once_with("mytable")


def test_table_info_not_found(mock_db):
    """Test that a missing table exits with code 1 (IndexError on info[0])."""
    mock_db.schema.return_value.table.return_value.is_parent_partition.return_value = False
    mock_db.schema.return_value.table.return_value.table_info.return_value = None

    result = runner.invoke(app, ["table", "--database", "postgres", "--table", "public.missing"])
    assert result.exit_code == 1


def test_table_info_invalid_table_format():
    """Test that an invalid table format exits with code 2."""
    result = runner.invoke(app, ["table", "--database", "postgres", "--table", "a.b.c"])
    assert result.exit_code == 2


def test_table_info_missing_table_option():
    """Test that omitting --table exits with code 2."""
    result = runner.invoke(app, ["table", "--database", "postgres"])
    assert result.exit_code == 2


def test_table_info_db_error(mock_db):
    """Test that a database error exits with code 1."""
    mock_db.schema.side_effect = Exception("connection refused")

    result = runner.invoke(app, ["table", "--database", "postgres", "--table", "public.orders"])
    assert result.exit_code == 1
