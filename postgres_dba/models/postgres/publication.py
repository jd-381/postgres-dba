from dataclasses import dataclass
from typing import TYPE_CHECKING

from postgres_dba.models.postgres.data import PostgresData
from postgres_dba.models.postgres.instance import SQL, Composed, PostgresCursor, TupleRow

if TYPE_CHECKING:
    from postgres_dba.models.postgres.database import PostgresDatabase


@dataclass(frozen=True)
class Publication(PostgresData["Publication"]):
    name: str
    owner: str
    insert: bool
    update: bool
    delete: bool
    truncate: bool
    via_root: bool
    tables: str

    @staticmethod
    def _query(pub_name: str | None = None) -> Composed:
        sql: Composed = SQL(
            "SELECT "
            "p.pubname, "
            "rolname, "
            "pubinsert, "
            "pubupdate, "
            "pubdelete, "
            "pubtruncate, "
            "pubviaroot, "
            "string_agg(schemaname || '.' || tablename, E'\n' ORDER BY schemaname, tablename) AS tables "
            "FROM pg_publication p "
            "JOIN pg_roles r ON p.pubowner = r.oid "
            "LEFT JOIN pg_publication_tables t ON p.pubname = t.pubname "
        ).format()
        if pub_name:
            sql += SQL("WHERE p.pubname = {name} ").format(name=pub_name)
        sql += SQL(
            "GROUP BY p.pubname, rolname, pubinsert, pubupdate, pubdelete, pubtruncate, pubviaroot "
            "ORDER BY p.pubname ASC"
        ).format()
        return sql


@dataclass(frozen=True)
class PostgresPublication:
    name: str
    database: "PostgresDatabase"
    cur: PostgresCursor[TupleRow]

    def info(self) -> Publication | None:
        sql: Composed = Publication._query(self.name)
        self.cur.execute(sql)
        row: TupleRow | None = self.cur.fetchone()
        return Publication.from_row(row) if row else None
