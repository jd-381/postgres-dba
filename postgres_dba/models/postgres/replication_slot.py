from dataclasses import dataclass
from typing import TYPE_CHECKING

from postgres_dba.models.postgres.data import PostgresData
from postgres_dba.models.postgres.instance import SQL, Composed, PostgresCursor, TupleRow

if TYPE_CHECKING:
    from postgres_dba.models.postgres.database import PostgresDatabase


@dataclass(frozen=True)
class ReplicationSlot(PostgresData["ReplicationSlot"]):
    name: str
    type: str
    dbname: str
    temporary: bool
    active: bool
    inactive_since: str | None
    wal_status: str
    restart_lsn: str
    confirmed_flush_lsn: str
    lag_size: str

    @staticmethod
    def _query(slot_name: str | None = None) -> Composed:
        sql: Composed = SQL(
            "SELECT "
            "slot_name::text AS slot_name, "
            "slot_type::text, "
            "database::text AS database, "
            "temporary::boolean, "
            "active::boolean, "
            "inactive_since::timestamptz, "
            "wal_status::text, "
            "restart_lsn::text, "
            "confirmed_flush_lsn::text, "
            "pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn))::text AS lag_size "
            "FROM pg_replication_slots "
        ).format()
        if slot_name:
            sql += SQL("WHERE slot_name = {name}").format(name=slot_name)
        sql += SQL(" ORDER BY lag_size DESC NULLS LAST").format()
        return sql


@dataclass(frozen=True)
class PostgresReplicationSlot:
    name: str
    database: "PostgresDatabase"
    cur: PostgresCursor[TupleRow]

    def info(self) -> ReplicationSlot | None:
        sql: Composed = ReplicationSlot._query(self.name)
        self.cur.execute(sql)
        row: TupleRow | None = self.cur.fetchone()
        return ReplicationSlot.from_row(row) if row else None
