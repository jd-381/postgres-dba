from dataclasses import dataclass
from typing import TYPE_CHECKING

from postgres_dba.models.postgres.data import PostgresData
from postgres_dba.models.postgres.instance import SQL, Composed, PostgresCursor, TupleRow

if TYPE_CHECKING:
    from postgres_dba.models.postgres.database import PostgresDatabase


@dataclass(frozen=True)
class Subscription(PostgresData["Subscription"]):
    name: str
    tables: str
    state: bool

    @staticmethod
    def _query(sub_name: str | None = None) -> Composed:
        sql: Composed = SQL(
            "SELECT "
            "s.subname AS subscription_name, "
            "string_agg(sr.srrelid::regclass::text, E'\n' ORDER BY sr.srrelid) AS table_name, "
            "string_agg( "
            "CASE sr.srsubstate "
            "WHEN 'i' THEN 'Initialize' "
            "WHEN 'd' THEN 'Data copy in progress' "
            "WHEN 's' THEN 'Synchronized' "
            "WHEN 'r' THEN 'Ready (streaming)' "
            "ELSE 'Unknown' "
            "END, "
            "E'\n' ORDER BY sr.srrelid "
            ") AS state_description "
            "FROM pg_subscription s "
            "LEFT JOIN pg_subscription_rel sr ON s.oid = sr.srsubid "
        ).format()
        if sub_name:
            sql += SQL("WHERE s.subname = {name} ").format(name=sub_name)
        sql += SQL("GROUP BY s.subname ORDER BY s.subname ASC").format()
        return sql


@dataclass(frozen=True)
class PostgresSubscription:
    name: str
    database: "PostgresDatabase"
    cur: PostgresCursor[TupleRow]

    def info(self) -> Subscription | None:
        sql: Composed = Subscription._query(self.name)
        self.cur.execute(sql)
        row: TupleRow | None = self.cur.fetchone()
        return Subscription.from_row(row) if row else None
