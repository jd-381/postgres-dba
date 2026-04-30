import logging
from typing import Annotated

import typer

from postgres_dba.common.logger_utils import yellow


def validate_user_input_comma_list(input: str | list[str] | None) -> list[str] | None:
    if input is None:
        return None
    if isinstance(input, list):
        if len(input) == 1 and "," in input[0]:
            return [part.strip() for part in input[0].split(",")]
        return input
    return [part.strip() for part in input.split(",")]


def validate_user_input_debug(input: bool) -> bool:
    if input:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug(f"{yellow('Debug mode enabled')}")
    return input


def validate_user_input_table(input: str | None) -> tuple[str, str] | None:
    if input is None:
        return None
    parts = [p.strip() for p in input.split(".")]
    if len(parts) == 2:
        schema, name = parts
    else:
        schema, name = "public", parts[0]
    if not schema or not name or len(parts) > 2:
        raise typer.BadParameter(f"Invalid table format: {input!r}")
    return (schema, name)


DATABASE_OPTION = Annotated[str, typer.Option("--database", "-d", help="Name of database")]
DEBUG_OPTION = Annotated[bool, typer.Option("--debug", help="Print SQL statements", callback=validate_user_input_debug)]
LIMIT_OPTION = Annotated[int, typer.Option("--limit", "-l", help="Limit rows")]

TABLE_HELP = "Name of table as \\[schema.]table (defaults to 'public' schema)"
TABLE_OPTION = Annotated[
    str,
    typer.Option(
        "--table",
        "-t",
        help=TABLE_HELP,
        callback=validate_user_input_table,
    ),
]
OPTIONAL_TABLE_OPTION = Annotated[
    str | None,
    typer.Option(
        "--table",
        "-t",
        help=TABLE_HELP,
        callback=validate_user_input_table,
    ),
]

WATCH_OPTION = Annotated[float, typer.Option("--watch", "-w", help="Watch query interval (in seconds)")]
