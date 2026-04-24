import os
from dataclasses import dataclass
from logging import Logger
from typing import Self

from psycopg import Column, Connection, Cursor
from psycopg.abc import Params, Query
from psycopg.rows import Row, RowFactory, TupleRow
from psycopg.sql import SQL, Composed, Identifier, Literal  # noqa: F401 - these are imported in other models


class PostgresCursor(Cursor[Row]):
    def __init__(
        self,
        connection: Connection[Row],
        *,
        row_factory: RowFactory[Row] | None = None,
        logger: Logger,
    ):
        super().__init__(connection)
        self._row_factory = row_factory or connection.row_factory
        self.logger = logger

    def columns(self) -> list[Column]:
        return self.description if self.description else []

    def execute(
        self,
        query: Query,
        params: Params | None = None,
        *,
        prepare: bool | None = None,
        binary: bool | None = None,
        dry_run: bool = False,
    ) -> Self:
        if isinstance(query, Composed):
            self.logger.debug(query.as_string())
        if dry_run:
            self.logger.info("DRY RUN - query not executed")
            return self
        return super().execute(query, params=params, prepare=prepare, binary=binary)  # type: ignore[arg-type]


@dataclass(frozen=True)
class PostgresInstance:
    host: str
    port: str
    user: str
    password: str
    database: str
    logger: Logger

    @classmethod
    def from_env_vars(cls, database: str, logger: Logger) -> "PostgresInstance":
        env_map: dict[str, str] = {
            "PGHOST": os.getenv("PGHOST") or "",
            "PGPORT": os.getenv("PGPORT") or "",
            "PGUSER": os.getenv("PGUSER") or "",
            "PGPASSWORD": os.getenv("PGPASSWORD") or "",
        }
        missing = [name for name, val in env_map.items() if not val]
        if missing:
            raise ValueError(f"Environment variable not set: {missing}")
        host: str = env_map["PGHOST"]
        port: str = env_map["PGPORT"]
        user: str = env_map["PGUSER"]
        password: str = env_map["PGPASSWORD"]
        dbname: str = database
        return cls(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname,
            logger=logger,
        )

    def connect(self, autocommit: bool) -> Connection[TupleRow]:
        self.logger.info(f'host="{self.host}"')
        self.logger.debug(f'port="{self.port}"')
        self.logger.debug(f'user="{self.user}"')
        self.logger.debug(f'database="{self.database}"')
        return Connection[TupleRow].connect(
            self._conn_info(),
            autocommit=autocommit,
        )

    def _conn_info(self) -> str:
        return f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"
