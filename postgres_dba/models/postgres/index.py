from dataclasses import dataclass
from typing import TYPE_CHECKING

from postgres_dba.models.postgres.data import PostgresData
from postgres_dba.models.postgres.instance import SQL, Composed, Literal

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Index(PostgresData["Index"]):
    schema: str
    table: str
    name: str
    size: str
    primary: bool
    unique: bool

    @staticmethod
    def _query(
        schema_name: str | None = None,
        table_name: str | None = None,
        index_name: str | None = None,
        *,
        scans: bool = True,
        limit: int,
    ) -> Composed:
        sql: Composed = SQL(
            "SELECT "
            "schemaname, "
            "relname, "
            "indexrelname, "
            "pg_size_pretty(pg_relation_size(psi.indexrelid)), "
            "CASE WHEN i.indisprimary THEN 'YES' ELSE 'NO' END, "
            "CASE WHEN i.indisunique THEN 'YES' ELSE 'NO' END "
            "FROM pg_stat_user_indexes psi "
            "JOIN pg_index i ON psi.indexrelid = i.indexrelid "
        ).format()
        if scans:
            sql += SQL("WHERE psi.idx_scan >= 0 ")
        else:
            sql += SQL("WHERE psi.idx_scan = 0 ")
        if schema_name:
            sql += SQL("AND psi.schemaname = {schema} ").format(schema=schema_name)
        if table_name:
            sql += SQL("AND psi.relname = {table} ").format(table=table_name)
        if index_name:
            sql += SQL("AND psi.indexrelname = {index} ").format(index=index_name)
        sql += SQL("ORDER BY pg_relation_size(psi.indexrelid) DESC LIMIT {limit}").format(limit=Literal(limit))
        return sql


@dataclass(frozen=True)
class IndexProgress(PostgresData["IndexProgress"]):
    database: str
    table: str
    index: str
    phase: str
    blocks_done: int
    blocks_total: int
    blocks_pct: float
    tuples_done: int
    tuples_total: int
    tuples_pct: float

    @staticmethod
    def _query() -> Composed:
        sql: Composed = SQL(
            "SELECT "
            "datname, "
            "relid::regclass, "
            "index_relid::regclass, "
            "CASE phase "
            "    WHEN 'building index: scanning table'       THEN '1/5 ' || phase "
            "    WHEN 'building index: sorting live tuples'  THEN '2/5 ' || phase "
            "    WHEN 'building index: loading tuples in tree' THEN '3/5 ' || phase "
            "    WHEN 'index validation: scanning index'     THEN '4/5 ' || phase "
            "    WHEN 'index validation: scanning table'     THEN '5/5 ' || phase "
            "    ELSE phase "
            "END AS phase, "
            "blocks_done, "
            "blocks_total, "
            "round(100.0 * blocks_done / NULLIF(blocks_total, 0), 2) AS blocks_pct, "
            "tuples_done, "
            "tuples_total, "
            "round(100.0 * tuples_done / NULLIF(tuples_total, 0), 2) AS tuples_pct "
            "FROM pg_stat_progress_create_index "
        ).format()
        return sql
