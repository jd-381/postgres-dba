from dataclasses import dataclass
from typing import TYPE_CHECKING

from postgres_dba.models.postgres.data import PostgresData
from postgres_dba.models.postgres.instance import SQL, Composed, Literal, PostgresCursor, TupleRow

if TYPE_CHECKING:
    from postgres_dba.models.postgres.database import PostgresDatabase


@dataclass
class ProcesslistFilter:
    active: bool = False
    slots: bool = False
    pids: list[str] | None = None
    ipids: list[str] | None = None
    queries: list[str] | None = None
    iqueries: list[str] | None = None
    users: list[str] | None = None
    iusers: list[str] | None = None
    limit: int = 10


@dataclass(frozen=True)
class Processlist(PostgresData["Processlist"]):
    pid: str
    user: str
    client: str
    client_addr: str
    database: str
    conn_dur: str
    trx_dur: str
    query_dur: str
    state: str
    wait: str
    backend: str
    query_id: str
    query: str

    @staticmethod
    def _query(filter: ProcesslistFilter) -> Composed:
        sql: Composed = SQL(
            "SELECT pid, usename, application_name, client_addr, datname, "
            "date_trunc('second', now() - backend_start) AS conn_dur, "
            "CASE WHEN state != 'idle' THEN date_trunc('second', now() - xact_start) END AS trx_dur, "
            "CASE WHEN state = 'active' THEN date_trunc('second', now() - query_start) END AS query_dur, "
            "state, "
            "wait_event, "
            "backend_type, "
            "query_id, "
            "query "
            "FROM pg_stat_activity "
        ).format()
        conditions: list[Composed] = [
            SQL("pid != pg_backend_pid()").format(),  # ignore this connection
            SQL("usename NOT IN ({rdsadmin},{rdssuper})").format(
                rdsadmin=Literal("rdsadmin"), rdssuper=Literal("rds_superuser")
            ),  # ignore RDS users
        ]
        if filter.active:
            state_sql = SQL("state = {state}").format(state=Literal("active"))
            conditions.append(state_sql)
        if not filter.slots:
            backend_list = SQL(", ").join(
                SQL("{e}").format(e=Literal(backend)) for backend in ["walsender", "logical replication apply worker"]
            )
            conditions.append(SQL("backend_type NOT IN ({list}) ").format(list=backend_list))
        if filter.pids:
            pid_list = SQL(", ").join(SQL("{e}").format(e=Literal(pid)) for pid in filter.pids)
            conditions.append(SQL("pid IN ({list}) ").format(list=pid_list))
        if filter.ipids:
            pid_list = SQL(", ").join(SQL("{e}").format(e=Literal(pid)) for pid in filter.ipids)
            conditions.append(SQL("pid NOT IN ({list}) ").format(list=pid_list))
        if filter.queries:
            query_list = SQL(", ").join(SQL("{e}").format(e=Literal(query)) for query in filter.queries)
            conditions.append(SQL("query_id IN ({list}) ").format(list=query_list))
        if filter.iqueries:
            query_list = SQL(", ").join(SQL("{e}").format(e=Literal(query)) for query in filter.iqueries)
            conditions.append(SQL("query_id NOT IN ({list}) ").format(list=query_list))
        if filter.users:
            user_list = SQL(", ").join(SQL("{e}").format(e=Literal(user)) for user in filter.users)
            conditions.append(SQL("usename IN ({list}) ").format(list=user_list))
        if filter.iusers:
            user_list = SQL(", ").join(SQL("{e}").format(e=Literal(user)) for user in filter.iusers)
            conditions.append(SQL("usename NOT IN ({list}) ").format(list=user_list))
        sql += SQL("WHERE ") + SQL(" AND ").join(conditions)
        sql += SQL(
            " ORDER BY "
            "(CASE WHEN state = 'active' THEN 0 ELSE 1 END), "
            "(now() - query_start) DESC NULLS LAST, "
            "(CASE WHEN state != 'idle' THEN 0 ELSE 1 END), "
            "(now() - xact_start) DESC NULLS LAST, "
            "(now() - backend_start) DESC NULLS LAST "
            "LIMIT {limit}"
        ).format(limit=Literal(filter.limit))
        return sql


@dataclass(frozen=True)
class PostgresProcesslist:
    database: "PostgresDatabase"
    cur: PostgresCursor[TupleRow]

    def info(self, filter: ProcesslistFilter) -> list[Processlist]:
        sql: Composed = Processlist._query(filter)
        self.cur.execute(sql)
        rows: list[TupleRow] = self.cur.fetchall()
        return [Processlist.from_row(row) for row in rows]
