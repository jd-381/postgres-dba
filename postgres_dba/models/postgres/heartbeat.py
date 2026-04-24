from dataclasses import dataclass
from typing import TYPE_CHECKING

from postgres_dba.models.postgres.data import PostgresData
from postgres_dba.models.postgres.instance import SQL, Composed, PostgresCursor, TupleRow

if TYPE_CHECKING:
    from postgres_dba.models.postgres.database import PostgresDatabase


@dataclass(frozen=True)
class Heartbeat(PostgresData["Heartbeat"]):
    schema: str
    tracking: str
    lag: str

    @staticmethod
    def _query(tracking: str | None = None) -> Composed:
        sql: Composed = SQL("SELECT schema_name, tracking, lag FROM get_heartbeat_tracking() ").format()
        if tracking:
            sql += SQL("WHERE tracking = {tracking} ").format(tracking=tracking)
        sql += SQL("ORDER BY lag DESC").format()
        return sql


@dataclass(frozen=True)
class PostgresHeartbeat:
    tracking: str
    database: "PostgresDatabase"
    cur: PostgresCursor[TupleRow]

    def info(self) -> Heartbeat | None:
        sql: Composed = Heartbeat._query(self.tracking)
        self.cur.execute(sql)
        row: TupleRow | None = self.cur.fetchone()
        return Heartbeat.from_row(row) if row else None
