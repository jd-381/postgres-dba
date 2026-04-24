import logging

import typer

from postgres_dba.common.cli_utils import DATABASE_OPTION, DEBUG_OPTION, TABLE_OPTION
from postgres_dba.models.postgres.database import PostgresDatabase
from postgres_dba.models.postgres.instance import PostgresInstance
from postgres_dba.models.postgres.schema import PostgresSchema
from postgres_dba.models.postgres.table import PostgresTable, TableInfo
from postgres_dba.models.table_printer import TablePrinter

LOGGER = logging.getLogger(__name__)

app = typer.Typer(invoke_without_command=True, no_args_is_help=False)


class TableService:
    def __init__(self, db: PostgresDatabase):
        self._db: PostgresDatabase = db

    def info(self, schema_name: str, table_name: str) -> list[TableInfo]:
        schema: PostgresSchema = self._db.schema(schema_name)
        table: PostgresTable = schema.table(table_name)
        if table.is_parent_partition():
            return table.partition_table_info()
        else:
            row: TableInfo | None = table.table_info()
            return [row] if row else []


@app.callback()
def info(
    database: DATABASE_OPTION,
    table: TABLE_OPTION,
    debug: DEBUG_OPTION = False,
):
    try:
        schema_name, table_name = table
        instance: PostgresInstance = PostgresInstance.from_env_vars(database, LOGGER)
        with PostgresDatabase.from_instance(instance, autocommit=True) as db:
            info: list[TableInfo] = TableService(db).info(schema_name, table_name)
        title: str = "Partition " if info[0].is_partition() else ""
        TablePrinter.from_dataclasses(f"{table_name} {title}Table Info", info).print()
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
