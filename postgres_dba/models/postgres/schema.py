from dataclasses import dataclass
from typing import TYPE_CHECKING

from postgres_dba.models.postgres.database import PostgresDatabase
from postgres_dba.models.postgres.instance import PostgresCursor, TupleRow

if TYPE_CHECKING:
    from postgres_dba.models.postgres.table import PostgresTable


@dataclass(frozen=True)
class PostgresSchema:
    name: str
    database: "PostgresDatabase"
    cur: PostgresCursor[TupleRow]

    def table(self, name: str) -> "PostgresTable":
        from postgres_dba.models.postgres.table import PostgresTable

        return PostgresTable(name=name, schema=self, cur=self.cur)
