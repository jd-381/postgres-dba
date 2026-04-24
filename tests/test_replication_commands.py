"""Tests for the replication commands."""

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from postgres_dba.main import app
from postgres_dba.models.postgres.heartbeat import Heartbeat
from postgres_dba.models.postgres.publication import Publication
from postgres_dba.models.postgres.replication_slot import ReplicationSlot
from postgres_dba.models.postgres.subscription import Subscription

runner = CliRunner()

SAMPLE_HEARTBEATS = [
    Heartbeat(schema="public", tracking="primary", lag="00:00:01"),
    Heartbeat(schema="public", tracking="replica", lag="00:00:05"),
]

SAMPLE_PUBS = [
    Publication(
        name="pub_orders",
        owner="postgres",
        insert=True,
        update=True,
        delete=False,
        truncate=False,
        via_root=False,
        tables="public.orders",
    ),
    Publication(
        name="pub_users",
        owner="postgres",
        insert=True,
        update=False,
        delete=False,
        truncate=False,
        via_root=False,
        tables="public.users",
    ),
]

SAMPLE_SLOTS = [
    ReplicationSlot(
        name="slot_a",
        type="logical",
        dbname="postgres",
        temporary=False,
        active=True,
        inactive_since=None,
        wal_status="reserved",
        restart_lsn="0/1000000",
        confirmed_flush_lsn="0/1000000",
        lag_size="0 bytes",
    ),
    ReplicationSlot(
        name="slot_b",
        type="physical",
        dbname="postgres",
        temporary=False,
        active=False,
        inactive_since="2026-01-01 00:00:00 UTC",
        wal_status="lost",
        restart_lsn="0/2000000",
        confirmed_flush_lsn="0/2000000",
        lag_size="1 GB",
    ),
]

SAMPLE_SUBS = [
    Subscription(name="sub_orders", tables="public.orders", state=True),
    Subscription(name="sub_users", tables="public.users", state=False),
]


@pytest.fixture
def mock_db():
    """Mock PostgresInstance and PostgresDatabase for replication CLI commands."""
    with (
        patch("postgres_dba.commands.replication.PostgresInstance.from_env_vars"),
        patch("postgres_dba.commands.replication.PostgresDatabase.from_instance") as mock_db_cm,
    ):
        mock_db_obj = MagicMock()
        mock_db_cm.return_value.__enter__ = MagicMock(return_value=mock_db_obj)
        mock_db_cm.return_value.__exit__ = MagicMock(return_value=False)
        yield mock_db_obj


# --- heartbeat ---


def test_repl_heartbeat(mock_db):
    """Test listing all heartbeats."""
    mock_db.heartbeats.return_value = SAMPLE_HEARTBEATS

    result = runner.invoke(app, ["repl", "heartbeat", "--database", "postgres"])
    assert result.exit_code == 0
    assert "Heartbeat" in result.stdout


def test_repl_heartbeat_with_name(mock_db):
    """Test filtering heartbeat by tracking name."""
    mock_db.heartbeat.return_value.info.return_value = SAMPLE_HEARTBEATS[0]

    result = runner.invoke(app, ["repl", "heartbeat", "--database", "postgres", "--name", "primary"])
    assert result.exit_code == 0
    mock_db.heartbeat.assert_called_once_with("primary")


def test_repl_heartbeat_with_name_short_option(mock_db):
    """Test filtering heartbeat using short -n option."""
    mock_db.heartbeat.return_value.info.return_value = SAMPLE_HEARTBEATS[0]

    result = runner.invoke(app, ["repl", "heartbeat", "--database", "postgres", "-n", "primary"])
    assert result.exit_code == 0
    mock_db.heartbeat.assert_called_once_with("primary")


def test_repl_heartbeat_with_name_not_found(mock_db):
    """Test heartbeat with name returns empty when not found."""
    mock_db.heartbeat.return_value.info.return_value = None

    result = runner.invoke(app, ["repl", "heartbeat", "--database", "postgres", "--name", "missing"])
    assert result.exit_code == 0


def test_repl_heartbeat_db_error(mock_db):
    """Test that a database error exits with code 1."""
    mock_db.heartbeats.side_effect = Exception("connection refused")

    result = runner.invoke(app, ["repl", "heartbeat", "--database", "postgres"])
    assert result.exit_code == 1


# --- pubs ---


def test_repl_pubs(mock_db):
    """Test listing all publications."""
    mock_db.publications.return_value = SAMPLE_PUBS

    result = runner.invoke(app, ["repl", "pubs", "--database", "postgres"])
    assert result.exit_code == 0
    assert "Publication" in result.stdout


def test_repl_pubs_with_name(mock_db):
    """Test filtering publications by name."""
    mock_db.publication.return_value.info.return_value = SAMPLE_PUBS[0]

    result = runner.invoke(app, ["repl", "pubs", "--database", "postgres", "--name", "pub_orders"])
    assert result.exit_code == 0
    mock_db.publication.assert_called_once_with("pub_orders")


def test_repl_pubs_with_name_not_found(mock_db):
    """Test pubs with name returns empty when not found."""
    mock_db.publication.return_value.info.return_value = None

    result = runner.invoke(app, ["repl", "pubs", "--database", "postgres", "--name", "missing"])
    assert result.exit_code == 0


def test_repl_pubs_db_error(mock_db):
    """Test that a database error exits with code 1."""
    mock_db.publications.side_effect = Exception("connection refused")

    result = runner.invoke(app, ["repl", "pubs", "--database", "postgres"])
    assert result.exit_code == 1


# --- slots ---


def test_repl_slots(mock_db):
    """Test listing all replication slots."""
    mock_db.replication_slots.return_value = SAMPLE_SLOTS

    result = runner.invoke(app, ["repl", "slots"])
    assert result.exit_code == 0
    assert "Replication" in result.stdout


def test_repl_slots_with_name(mock_db):
    """Test filtering slots by name."""
    mock_db.replication_slot.return_value.info.return_value = SAMPLE_SLOTS[0]

    result = runner.invoke(app, ["repl", "slots", "--name", "slot_a"])
    assert result.exit_code == 0
    mock_db.replication_slot.assert_called_once_with("slot_a")


def test_repl_slots_with_name_not_found(mock_db):
    """Test slots with name returns empty when not found."""
    mock_db.replication_slot.return_value.info.return_value = None

    result = runner.invoke(app, ["repl", "slots", "--name", "missing"])
    assert result.exit_code == 0


def test_repl_slots_db_error(mock_db):
    """Test that a database error exits with code 1."""
    mock_db.replication_slots.side_effect = Exception("connection refused")

    result = runner.invoke(app, ["repl", "slots"])
    assert result.exit_code == 1


# --- subs ---


def test_repl_subs(mock_db):
    """Test listing all subscriptions."""
    mock_db.subscriptions.return_value = SAMPLE_SUBS

    result = runner.invoke(app, ["repl", "subs", "--database", "postgres"])
    assert result.exit_code == 0
    assert "Subscription" in result.stdout


def test_repl_subs_with_name(mock_db):
    """Test filtering subscriptions by name."""
    mock_db.subscription.return_value.info.return_value = SAMPLE_SUBS[0]

    result = runner.invoke(app, ["repl", "subs", "--database", "postgres", "--name", "sub_orders"])
    assert result.exit_code == 0
    mock_db.subscription.assert_called_once_with("sub_orders")


def test_repl_subs_with_name_not_found(mock_db):
    """Test subs with name returns empty when not found."""
    mock_db.subscription.return_value.info.return_value = None

    result = runner.invoke(app, ["repl", "subs", "--database", "postgres", "--name", "missing"])
    assert result.exit_code == 0


def test_repl_subs_db_error(mock_db):
    """Test that a database error exits with code 1."""
    mock_db.subscriptions.side_effect = Exception("connection refused")

    result = runner.invoke(app, ["repl", "subs", "--database", "postgres"])
    assert result.exit_code == 1
