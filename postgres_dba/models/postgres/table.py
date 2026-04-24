from dataclasses import dataclass

from postgres_dba.models.postgres.data import PostgresData
from postgres_dba.models.postgres.instance import SQL, Composed, Identifier, Literal, PostgresCursor, TupleRow
from postgres_dba.models.postgres.schema import PostgresSchema


@dataclass(frozen=True)
class TableInfo(PostgresData["TableInfo"]):
    data: str
    index: str
    total: str
    columns: int
    rows: int
    dead: int
    bloat: float
    vacuum: int
    autovacuum: str
    analyze: str
    autoanalyze: str

    @staticmethod
    def _query(schema_name: str, table_name: str) -> Composed:
        return SQL(
            "SELECT "
            "pg_size_pretty(pg_relation_size(c.oid)) AS data_size, "
            "pg_size_pretty(pg_indexes_size(c.oid)) AS index_size, "
            "pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size, "
            "(SELECT COUNT(1) "
            "FROM pg_attribute a "
            "WHERE a.attrelid = c.oid "
            "AND a.attnum > 0 "
            "AND NOT a.attisdropped) AS column_count, "
            "s.n_live_tup AS live_rows, "
            "s.n_dead_tup AS dead_rows, "
            "concat(round(s.n_dead_tup * 100.0 / NULLIF(s.n_live_tup, 0), 2) || '%') AS bloat_pct,"
            "to_char(date_trunc('second', s.last_vacuum), 'YYYY-MM-DD HH24:MI:SS TZ') AS last_vacuum, "
            "to_char(date_trunc('second', s.last_autovacuum), 'YYYY-MM-DD HH24:MI:SS TZ') AS last_autovacuum, "
            "to_char(date_trunc('second', s.last_analyze), 'YYYY-MM-DD HH24:MI:SS TZ') AS last_analyze, "
            "to_char(date_trunc('second', s.last_autoanalyze), 'YYYY-MM-DD HH24:MI:SS TZ') AS last_autoanalyze "
            "FROM pg_class c "
            "JOIN pg_namespace n ON n.oid = c.relnamespace "
            "JOIN pg_stat_user_tables s ON s.relid = c.oid "
            "WHERE n.nspname = {schema} AND c.relname = {table};"
        ).format(
            schema=Literal(schema_name),
            table=Literal(table_name),
        )

    def is_partition(self) -> bool:
        return False


@dataclass(frozen=True)
class PartitionTableInfo(TableInfo):
    partition: str

    @staticmethod
    def _query(schema_name: str, table_name: str) -> Composed:
        return SQL(
            "SELECT "
            "pg_size_pretty(pg_relation_size(c.oid)) AS data_size, "
            "pg_size_pretty(pg_indexes_size(c.oid)) AS index_size, "
            "pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size, "
            "(SELECT COUNT(1) "
            "FROM pg_attribute a "
            "WHERE a.attrelid = c.oid "
            "AND a.attnum > 0 "
            "AND NOT a.attisdropped) AS column_count, "
            "COALESCE(s.n_live_tup, 0) AS live_rows, "
            "COALESCE(s.n_dead_tup, 0) AS dead_rows, "
            "concat(round(COALESCE(s.n_dead_tup, 0) * 100.0 / NULLIF(COALESCE(s.n_live_tup, 0), 0), 0) || '%') "
            "AS bloat_pct,"
            "to_char(date_trunc('second', s.last_vacuum), 'YYYY-MM-DD HH24:MI:SS TZ') AS last_vacuum, "
            "to_char(date_trunc('second', s.last_autovacuum), 'YYYY-MM-DD HH24:MI:SS TZ') AS last_autovacuum, "
            "to_char(date_trunc('second', s.last_analyze), 'YYYY-MM-DD HH24:MI:SS TZ') AS last_analyze, "
            "to_char(date_trunc('second', s.last_autoanalyze), 'YYYY-MM-DD HH24:MI:SS TZ') AS last_autoanalyze, "
            "format('%I.%I', parent_ns.nspname, c.relname) AS partition_name "
            "FROM pg_class c "
            "JOIN pg_inherits i ON i.inhrelid = c.oid "
            "JOIN pg_class parent ON i.inhparent = parent.oid "
            "JOIN pg_namespace parent_ns ON parent_ns.oid = parent.relnamespace "
            "LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid "
            "WHERE parent_ns.nspname = {schema} "
            "AND parent.relname = {table} "
            "ORDER BY partition_name ASC;"
        ).format(
            schema=Literal(schema_name),
            table=Literal(table_name),
        )

    def is_partition(self) -> bool:
        return True


@dataclass(frozen=True)
class PostgresTable:
    name: str
    schema: PostgresSchema
    cur: PostgresCursor[TupleRow]

    @property
    def fqn(self) -> str:
        return f"{self.schema.name}.{self.name}"

    @property
    def fqn_sql(self) -> Composed:
        return SQL("{schema}.{table}").format(schema=Identifier(self.schema.name), table=Identifier(self.name))

    def is_parent_partition(self) -> bool:
        sql: Composed = SQL(
            "SELECT 1 "
            "FROM pg_class c "
            "JOIN pg_namespace n ON c.relnamespace = n.oid "
            "WHERE n.nspname = {schema} "
            "AND c.relname = {table} "
            "AND c.relkind = 'p';"
        ).format(
            schema=Literal(self.schema.name),
            table=Literal(self.name),
        )
        self.cur.execute(sql)
        row: TupleRow | None = self.cur.fetchone()
        return True if row else False

    def partition_table_info(self) -> list[TableInfo]:
        sql: Composed = PartitionTableInfo._query(self.schema.name, self.name)
        self.cur.execute(sql)
        rows: list[TupleRow] = self.cur.fetchall()
        return [PartitionTableInfo.from_row(row) for row in rows]

    def table_info(self) -> TableInfo | None:
        sql: Composed = TableInfo._query(self.schema.name, self.name)
        self.cur.execute(sql)
        row: TupleRow | None = self.cur.fetchone()
        return TableInfo.from_row(row) if row else None
