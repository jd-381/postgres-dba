import logging
from typing import Annotated

import typer

from postgres_dba.common.cli_utils import DEBUG_OPTION, LIMIT_OPTION, WATCH_OPTION, validate_user_input_comma_list
from postgres_dba.common.watch_it import watch_it
from postgres_dba.models.postgres.database import PostgresDatabase
from postgres_dba.models.postgres.instance import PostgresInstance
from postgres_dba.models.postgres.processlist import PostgresProcesslist, Processlist, ProcesslistFilter
from postgres_dba.models.table_printer import TablePrinter

LOGGER = logging.getLogger(__name__)

app = typer.Typer(invoke_without_command=True, no_args_is_help=False)


class ProcesslistService:
    def __init__(self, db: PostgresDatabase):
        self._db: PostgresDatabase = db

    def info(self, filter: ProcesslistFilter) -> list[Processlist]:
        processlist: PostgresProcesslist = self._db.processlist()
        return processlist.info(filter)


@app.callback()
def main(
    active: Annotated[bool, typer.Option("--active", "-a", help="Active queries only")] = False,
    slots: Annotated[bool, typer.Option("--slots", help="Show replication processes")] = False,
    pids: Annotated[
        list[str] | None,
        typer.Option("--pids", help="Show pids (ex: 1357,2468)", callback=validate_user_input_comma_list),
    ] = None,
    ipids: Annotated[
        list[str] | None,
        typer.Option("--ipids", help="Ignore pids", callback=validate_user_input_comma_list),
    ] = None,
    queries: Annotated[
        list[str] | None,
        typer.Option(
            "--queries", help="Show query IDs (ex: 1234567890,0987654321)", callback=validate_user_input_comma_list
        ),
    ] = None,
    iqueries: Annotated[
        list[str] | None,
        typer.Option("--iqueries", help="Ignore query IDs", callback=validate_user_input_comma_list),
    ] = None,
    users: Annotated[
        list[str] | None,
        typer.Option("--users", help="Show users (ex: ats_owner,postgres)", callback=validate_user_input_comma_list),
    ] = None,
    iusers: Annotated[
        list[str] | None,
        typer.Option("--iusers", help="Ignore users", callback=validate_user_input_comma_list),
    ] = None,
    limit: LIMIT_OPTION = 10,
    watch: WATCH_OPTION = 0,
    debug: DEBUG_OPTION = False,
):
    try:
        filter: ProcesslistFilter = ProcesslistFilter(
            active=active,
            slots=slots,
            pids=pids,
            ipids=ipids,
            queries=queries,
            iqueries=iqueries,
            users=users,
            iusers=iusers,
            limit=limit,
        )
        instance: PostgresInstance = PostgresInstance.from_env_vars("postgres", LOGGER)
        with PostgresDatabase.from_instance(instance, autocommit=True) as db:
            watch_it(
                interval=watch,
                task=lambda: ProcesslistService(db).info(filter),
                on_result=lambda processes: TablePrinter.from_dataclasses("Processlist", processes).print(),
                logger=instance.logger,
            )
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
