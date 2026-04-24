import logging
from typing import Annotated

import typer

from postgres_dba.common.cli_utils import DATABASE_OPTION, DEBUG_OPTION, LIMIT_OPTION
from postgres_dba.models.postgres.database import PostgresDatabase
from postgres_dba.models.postgres.instance import PostgresInstance
from postgres_dba.models.postgres.pg_cron import CronJob, CronJobRunDetail, CronRunStatus, PgCron
from postgres_dba.models.table_printer import TablePrinter

LOGGER = logging.getLogger(__name__)

app = typer.Typer(invoke_without_command=False, no_args_is_help=True)


class CronService:
    def __init__(self, db: PostgresDatabase):
        self._db: PostgresDatabase = db

    def jobs(self, job_id: int | None) -> list[CronJob]:
        pg_cron: PgCron = self._db.pg_cron()
        return pg_cron.jobs(job_id)

    def job_run_details(
        self,
        status: CronRunStatus,
        *,
        limit: int,
        job_id: int | None = None,
    ) -> list[CronJobRunDetail]:
        pg_cron: PgCron = self._db.pg_cron()
        return pg_cron.job_run_details(status, limit=limit, job_id=job_id)


@app.command(help="Get cron jobs")
def jobs(
    job_id: Annotated[int | None, typer.Option("--job", "-j", help="Job ID (optional)")] = None,
    database: DATABASE_OPTION = "postgres",
    debug: DEBUG_OPTION = False,
):
    try:
        instance: PostgresInstance = PostgresInstance.from_env_vars(database, LOGGER)
        with PostgresDatabase.from_instance(instance, autocommit=True) as db:
            jobs: list[CronJob] = CronService(db).jobs(job_id)
        TablePrinter.from_dataclasses("Cron Jobs", jobs).print()
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)


@app.command(help="Get cron job run details", no_args_is_help=False)
def logs(
    status: Annotated[CronRunStatus, typer.Option("--status", "-s", help="Run status")] = CronRunStatus.ALL,
    limit: LIMIT_OPTION = 14,
    job_id: Annotated[int | None, typer.Option("--job", "-j", help="Job ID (optional)")] = None,
    database: DATABASE_OPTION = "postgres",
    debug: DEBUG_OPTION = False,
):
    try:
        instance: PostgresInstance = PostgresInstance.from_env_vars(database, LOGGER)
        with PostgresDatabase.from_instance(instance, autocommit=True) as db:
            run_details: list[CronJobRunDetail] = CronService(db).job_run_details(status, limit=limit, job_id=job_id)
        title: str = f"Job {job_id} " if job_id else ""
        TablePrinter.from_dataclasses(f"{title}Run Logs", run_details).print()
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
