from dataclasses import dataclass
from types import TracebackType
from typing import TYPE_CHECKING, Self

from postgres_dba.models.postgres.heartbeat import Heartbeat, PostgresHeartbeat
from postgres_dba.models.postgres.instance import (
    Composed,
    Connection,
    PostgresCursor,
    PostgresInstance,
    TupleRow,
)
from postgres_dba.models.postgres.processlist import PostgresProcesslist
from postgres_dba.models.postgres.publication import Publication
from postgres_dba.models.postgres.replication_slot import ReplicationSlot
from postgres_dba.models.postgres.subscription import Subscription

if TYPE_CHECKING:
    from postgres_dba.models.postgres.pg_cron import PgCron
    from postgres_dba.models.postgres.publication import PostgresPublication
    from postgres_dba.models.postgres.replication_slot import PostgresReplicationSlot
    from postgres_dba.models.postgres.schema import PostgresSchema
    from postgres_dba.models.postgres.subscription import PostgresSubscription


@dataclass(frozen=True)
class PostgresDatabase:
    name: str
    instance: PostgresInstance
    conn: Connection[TupleRow]
    cur: PostgresCursor[TupleRow]

    @classmethod
    def from_instance(cls, instance: PostgresInstance, autocommit: bool) -> "PostgresDatabase":
        connection: Connection[TupleRow] = instance.connect(autocommit)
        cursor: PostgresCursor[TupleRow] = PostgresCursor(connection, logger=instance.logger)
        return cls(name=instance.database, instance=instance, conn=connection, cur=cursor)

    def heartbeat(self, tracking: str) -> "PostgresHeartbeat":
        from postgres_dba.models.postgres.heartbeat import PostgresHeartbeat

        return PostgresHeartbeat(tracking=tracking, database=self, cur=self.cur)

    def heartbeats(self) -> list[Heartbeat]:
        sql: Composed = Heartbeat._query()
        self.cur.execute(sql)
        rows: list[TupleRow] = self.cur.fetchall()
        return [Heartbeat.from_row(row) for row in rows]

    def pg_cron(self) -> "PgCron":
        from postgres_dba.models.postgres.pg_cron import PgCron

        return PgCron(database=self, cur=self.cur)

    def processlist(self) -> "PostgresProcesslist":
        from postgres_dba.models.postgres.processlist import PostgresProcesslist

        return PostgresProcesslist(database=self, cur=self.cur)

    def publication(self, name: str) -> "PostgresPublication":
        from postgres_dba.models.postgres.publication import PostgresPublication

        return PostgresPublication(name=name, database=self, cur=self.cur)

    def publications(self) -> list[Publication]:
        sql: Composed = Publication._query()
        self.cur.execute(sql)
        rows: list[TupleRow] = self.cur.fetchall()
        return [Publication.from_row(row) for row in rows]

    def replication_slot(self, name: str) -> "PostgresReplicationSlot":
        from postgres_dba.models.postgres.replication_slot import PostgresReplicationSlot

        return PostgresReplicationSlot(name=name, database=self, cur=self.cur)

    def replication_slots(self) -> list[ReplicationSlot]:
        sql: Composed = ReplicationSlot._query()
        self.cur.execute(sql)
        rows: list[TupleRow] = self.cur.fetchall()
        return [ReplicationSlot.from_row(row) for row in rows]

    def schema(self, name: str) -> "PostgresSchema":
        from postgres_dba.models.postgres.schema import PostgresSchema

        return PostgresSchema(name=name, database=self, cur=self.cur)

    def subscription(self, name: str) -> "PostgresSubscription":
        from postgres_dba.models.postgres.subscription import PostgresSubscription

        return PostgresSubscription(name=name, database=self, cur=self.cur)

    def subscriptions(self) -> list[Subscription]:
        sql: Composed = Subscription._query()
        self.cur.execute(sql)
        rows: list[TupleRow] = self.cur.fetchall()
        return [Subscription.from_row(row) for row in rows]

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.cur.__exit__(exc_type, exc_val, exc_tb)
        self.conn.__exit__(exc_type, exc_val, exc_tb)
