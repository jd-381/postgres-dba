from dataclasses import dataclass
from enum import Enum

from postgres_dba.models.postgres.data import PostgresData
from postgres_dba.models.postgres.database import PostgresDatabase
from postgres_dba.models.postgres.instance import SQL, Composed, Literal, PostgresCursor, TupleRow


class CronRunStatus(Enum):
    ALL = "all"
    FAILED = "failed"
    RUNNING = "running"
    SUCCEEDED = "succeeded"


@dataclass(frozen=True)
class CronJob(PostgresData["CronJob"]):
    database: str
    user: str
    active: bool
    job_id: int
    name: str
    schedule: str
    command: str

    @staticmethod
    def _query(job_id: int | None) -> Composed:
        sql: Composed = SQL(
            "SELECT database, username, active, jobid, jobname, schedule, command FROM cron.job "
        ).format()
        if job_id:
            sql += SQL("WHERE jobid = {job_id} ").format(job_id=Literal(job_id))
        sql += SQL("ORDER BY database ASC, active DESC").format()
        return sql


@dataclass(frozen=True)
class CronJobRunDetail(PostgresData["CronJobRunDetail"]):
    start: str
    end: str
    name: str
    status: str
    response: str
    command: str

    @staticmethod
    def _query(
        status: CronRunStatus,
        *,
        limit: int,
        job_id: int | None = None,
    ) -> Composed:
        sql: Composed = SQL(
            "SELECT "
            "to_char(date_trunc('second', d.start_time), 'YYYY-MM-DD HH24:MI:SS TZ'), "
            "to_char(date_trunc('second', d.end_time), 'YYYY-MM-DD HH24:MI:SS TZ'), "
            "j.jobname, "
            "d.status, "
            "d.return_message, d.command "
            "FROM cron.job_run_details d JOIN cron.job j ON d.jobid = j.jobid "
        ).format()
        conditions: list[Composed] = []
        if status != CronRunStatus.ALL:
            conditions.append(SQL("status = {status} ").format(status=Literal(status.value)))
        if job_id:
            conditions.append(SQL("d.jobid = {job_id} ").format(job_id=Literal(job_id)))
        if conditions:
            sql += SQL("WHERE ") + SQL("AND ").join(conditions)
        sql += SQL("ORDER BY start_time DESC NULLS LAST LIMIT {limit}").format(limit=Literal(limit))
        return sql


@dataclass(frozen=True)
class PgCron:
    database: "PostgresDatabase"
    cur: PostgresCursor[TupleRow]

    def jobs(self, job_id: int | None) -> list[CronJob]:
        sql: Composed = CronJob._query(job_id)
        self.cur.execute(sql)
        rows: list[TupleRow] = self.cur.fetchall()
        return [CronJob.from_row(row) for row in rows]

    def job_run_details(
        self,
        status: CronRunStatus,
        *,
        limit: int,
        job_id: int | None = None,
    ) -> list[CronJobRunDetail]:
        sql: Composed = CronJobRunDetail._query(status, limit=limit, job_id=job_id)
        self.cur.execute(sql)
        rows: list[TupleRow] = self.cur.fetchall()
        return [CronJobRunDetail.from_row(row) for row in rows]
