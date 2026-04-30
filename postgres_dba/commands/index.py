import logging
from typing import Annotated

import typer

from postgres_dba.common.cli_utils import (
    DATABASE_OPTION,
    DEBUG_OPTION,
    LIMIT_OPTION,
    OPTIONAL_TABLE_OPTION,
    WATCH_OPTION,
)
from postgres_dba.common.watch_it import watch_it
from postgres_dba.models.postgres.database import PostgresDatabase
from postgres_dba.models.postgres.index import Index, IndexProgress
from postgres_dba.models.postgres.instance import PostgresInstance
from postgres_dba.models.table_printer import TablePrinter

LOGGER = logging.getLogger(__name__)

app = typer.Typer(invoke_without_command=False, no_args_is_help=True)


class IndexService:
    def __init__(self, db: PostgresDatabase):
        self._db: PostgresDatabase = db

    def progress(self) -> list[IndexProgress]:
        return self._db.index_progress()

    def size(
        self,
        schema_name: str | None = None,
        table_name: str | None = None,
        index_name: str | None = None,
        *,
        limit: int,
    ) -> list[Index]:
        return self._db.indexes(schema_name, table_name, index_name, scans=True, limit=limit)

    def unused(self, schema_name: str | None = None, table_name: str | None = None, *, limit: int) -> list[Index]:
        return self._db.indexes(schema_name, table_name, scans=False, limit=limit)


@app.command(help="Get index creation progress")
def progress(
    database: DATABASE_OPTION,
    watch: WATCH_OPTION = 0,
    debug: DEBUG_OPTION = False,
):
    try:
        instance: PostgresInstance = PostgresInstance.from_env_vars(database, LOGGER)
        with PostgresDatabase.from_instance(instance, autocommit=True) as db:
            watch_it(
                interval=watch,
                task=lambda: IndexService(db).progress(),
                on_result=lambda index_progress: TablePrinter.from_dataclasses(
                    "Index Progress",
                    index_progress,
                ).print(),
                logger=instance.logger,
            )
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)


@app.command(help="Get index sizes")
def size(
    database: DATABASE_OPTION,
    table: OPTIONAL_TABLE_OPTION = None,
    index: Annotated[
        str | None,
        typer.Option(
            "--index",
            "-i",
            help="Name of index",
        ),
    ] = None,
    limit: LIMIT_OPTION = 10,
    debug: DEBUG_OPTION = False,
):
    try:
        schema_name, table_name = table if table else (None, None)
        instance: PostgresInstance = PostgresInstance.from_env_vars(database, LOGGER)
        with PostgresDatabase.from_instance(instance, autocommit=True) as db:
            indexes: list[Index] = IndexService(db).size(schema_name, table_name, index, limit=limit)
        title: str = f" for {schema_name}.{table_name} " if table else ""
        TablePrinter.from_dataclasses(f"Index Sizes{title}", indexes).print()
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)


@app.command(help="Get unused indexes")
def unused(
    database: DATABASE_OPTION,
    table: OPTIONAL_TABLE_OPTION = None,
    limit: LIMIT_OPTION = 10,
    debug: DEBUG_OPTION = False,
):
    try:
        schema_name, table_name = table if table else (None, None)
        instance: PostgresInstance = PostgresInstance.from_env_vars(database, LOGGER)
        with PostgresDatabase.from_instance(instance, autocommit=True) as db:
            indexes: list[Index] = IndexService(db).unused(schema_name, table_name, limit=limit)
        title: str = f" for {schema_name}.{table_name} " if table else ""
        TablePrinter.from_dataclasses(f"Unused Indexes{title}", indexes).print()
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
