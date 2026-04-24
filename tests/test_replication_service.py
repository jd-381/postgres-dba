"""Tests for ReplicationService."""

from unittest.mock import MagicMock

from postgres_dba.commands.replication import ReplicationService
from postgres_dba.models.postgres.heartbeat import Heartbeat
from postgres_dba.models.postgres.publication import Publication
from postgres_dba.models.postgres.replication_slot import ReplicationSlot
from postgres_dba.models.postgres.subscription import Subscription

_SAMPLE_HEARTBEATS = [
    Heartbeat(schema="public", tracking="primary", lag="00:00:01"),
    Heartbeat(schema="public", tracking="replica", lag="00:00:05"),
]

_SAMPLE_PUBS = [
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

_SAMPLE_SLOTS = [
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

_SAMPLE_SUBS = [
    Subscription(name="sub_orders", tables="public.orders", state=True),
    Subscription(name="sub_users", tables="public.users", state=False),
]


def test_replication_service_heartbeat_all() -> None:
    """Test ReplicationService.heartbeat returns all heartbeats when no name given."""
    mock_db = MagicMock()
    mock_db.heartbeats.return_value = _SAMPLE_HEARTBEATS

    result = ReplicationService(mock_db).heartbeat(None)

    assert result == _SAMPLE_HEARTBEATS
    mock_db.heartbeats.assert_called_once()


def test_replication_service_heartbeat_by_name() -> None:
    """Test ReplicationService.heartbeat returns single heartbeat by tracking name."""
    mock_db = MagicMock()
    mock_db.heartbeat.return_value.info.return_value = _SAMPLE_HEARTBEATS[0]

    result = ReplicationService(mock_db).heartbeat("primary")

    assert result == [_SAMPLE_HEARTBEATS[0]]
    mock_db.heartbeat.assert_called_once_with("primary")


def test_replication_service_heartbeat_by_name_not_found() -> None:
    """Test ReplicationService.heartbeat returns empty list when not found."""
    mock_db = MagicMock()
    mock_db.heartbeat.return_value.info.return_value = None

    result = ReplicationService(mock_db).heartbeat("missing")

    assert result == []


def test_replication_service_pubs_all() -> None:
    """Test ReplicationService.pubs returns all publications when no name given."""
    mock_db = MagicMock()
    mock_db.publications.return_value = _SAMPLE_PUBS

    result = ReplicationService(mock_db).pubs(None)

    assert result == _SAMPLE_PUBS
    mock_db.publications.assert_called_once()


def test_replication_service_pubs_by_name() -> None:
    """Test ReplicationService.pubs returns single publication by name."""
    mock_db = MagicMock()
    mock_db.publication.return_value.info.return_value = _SAMPLE_PUBS[0]

    result = ReplicationService(mock_db).pubs("pub_orders")

    assert result == [_SAMPLE_PUBS[0]]
    mock_db.publication.assert_called_once_with("pub_orders")


def test_replication_service_pubs_by_name_not_found() -> None:
    """Test ReplicationService.pubs returns empty list when not found."""
    mock_db = MagicMock()
    mock_db.publication.return_value.info.return_value = None

    result = ReplicationService(mock_db).pubs("missing")

    assert result == []


def test_replication_service_slots_all() -> None:
    """Test ReplicationService.slots returns all slots when no name given."""
    mock_db = MagicMock()
    mock_db.replication_slots.return_value = _SAMPLE_SLOTS

    result = ReplicationService(mock_db).slots(None)

    assert result == _SAMPLE_SLOTS
    mock_db.replication_slots.assert_called_once()


def test_replication_service_slots_by_name() -> None:
    """Test ReplicationService.slots returns single slot by name."""
    mock_db = MagicMock()
    mock_db.replication_slot.return_value.info.return_value = _SAMPLE_SLOTS[0]

    result = ReplicationService(mock_db).slots("slot_a")

    assert result == [_SAMPLE_SLOTS[0]]
    mock_db.replication_slot.assert_called_once_with("slot_a")


def test_replication_service_slots_by_name_not_found() -> None:
    """Test ReplicationService.slots returns empty list when not found."""
    mock_db = MagicMock()
    mock_db.replication_slot.return_value.info.return_value = None

    result = ReplicationService(mock_db).slots("missing")

    assert result == []


def test_replication_service_subs_all() -> None:
    """Test ReplicationService.subs returns all subscriptions when no name given."""
    mock_db = MagicMock()
    mock_db.subscriptions.return_value = _SAMPLE_SUBS

    result = ReplicationService(mock_db).subs(None)

    assert result == _SAMPLE_SUBS
    mock_db.subscriptions.assert_called_once()


def test_replication_service_subs_by_name() -> None:
    """Test ReplicationService.subs returns single subscription by name."""
    mock_db = MagicMock()
    mock_db.subscription.return_value.info.return_value = _SAMPLE_SUBS[0]

    result = ReplicationService(mock_db).subs("sub_orders")

    assert result == [_SAMPLE_SUBS[0]]
    mock_db.subscription.assert_called_once_with("sub_orders")


def test_replication_service_subs_by_name_not_found() -> None:
    """Test ReplicationService.subs returns empty list when not found."""
    mock_db = MagicMock()
    mock_db.subscription.return_value.info.return_value = None

    result = ReplicationService(mock_db).subs("missing")

    assert result == []
