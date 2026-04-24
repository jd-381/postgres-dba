import logging
from typing import Annotated

import typer

from postgres_dba.common.cli_utils import DATABASE_OPTION, DEBUG_OPTION, WATCH_OPTION
from postgres_dba.common.watch_it import watch_it
from postgres_dba.models.postgres.database import PostgresDatabase
from postgres_dba.models.postgres.heartbeat import Heartbeat, PostgresHeartbeat
from postgres_dba.models.postgres.instance import PostgresInstance
from postgres_dba.models.postgres.publication import PostgresPublication, Publication
from postgres_dba.models.postgres.replication_slot import PostgresReplicationSlot, ReplicationSlot
from postgres_dba.models.postgres.subscription import PostgresSubscription, Subscription
from postgres_dba.models.table_printer import TablePrinter

LOGGER = logging.getLogger(__name__)

app = typer.Typer(invoke_without_command=False, no_args_is_help=True)


class ReplicationService:
    def __init__(self, db: PostgresDatabase):
        self._db: PostgresDatabase = db

    def heartbeat(self, tracking: str | None) -> list[Heartbeat]:
        if tracking:
            heartbeat: PostgresHeartbeat = self._db.heartbeat(tracking)
            row: Heartbeat | None = heartbeat.info()
            return [row] if row else []
        else:
            return self._db.heartbeats()

    def pubs(self, pub_name: str | None) -> list[Publication]:
        if pub_name:
            pub: PostgresPublication = self._db.publication(pub_name)
            row: Publication | None = pub.info()
            return [row] if row else []
        else:
            return self._db.publications()

    def slots(self, slot_name: str | None) -> list[ReplicationSlot]:
        if slot_name:
            slot: PostgresReplicationSlot = self._db.replication_slot(slot_name)
            row: ReplicationSlot | None = slot.info()
            return [row] if row else []
        else:
            return self._db.replication_slots()

    def subs(self, sub_name: str | None) -> list[Subscription]:
        if sub_name:
            sub: PostgresSubscription = self._db.subscription(sub_name)
            row: Subscription | None = sub.info()
            return [row] if row else []
        else:
            return self._db.subscriptions()


@app.command(help="Get heartbeat info")
def heartbeat(
    database: DATABASE_OPTION,
    name: Annotated[str | None, typer.Option("--name", "-n", help="Tracking name (optional)")] = None,
    watch: WATCH_OPTION = 0,
    debug: DEBUG_OPTION = False,
):
    try:
        instance: PostgresInstance = PostgresInstance.from_env_vars(database, LOGGER)
        with PostgresDatabase.from_instance(instance, autocommit=True) as db:
            watch_it(
                interval=watch,
                task=lambda: ReplicationService(db).heartbeat(name),
                on_result=lambda heartbeats: TablePrinter.from_dataclasses("Heartbeat Info", heartbeats).print(),
                logger=instance.logger,
            )
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)


@app.command(help="Get publication info")
def pubs(
    database: DATABASE_OPTION,
    name: Annotated[str | None, typer.Option("--name", "-n", help="Publication name (optional)")] = None,
    debug: DEBUG_OPTION = False,
):
    try:
        instance: PostgresInstance = PostgresInstance.from_env_vars(database, LOGGER)
        with PostgresDatabase.from_instance(instance, autocommit=True) as db:
            pubs: list[Publication] = ReplicationService(db).pubs(name)
        TablePrinter.from_dataclasses("Publication Info", pubs).print()
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)


@app.command(help="Get replication slot info")
def slots(
    name: Annotated[str | None, typer.Option("--name", "-n", help="Slot name (optional)")] = None,
    watch: WATCH_OPTION = 0,
    debug: DEBUG_OPTION = False,
):
    try:
        instance: PostgresInstance = PostgresInstance.from_env_vars("postgres", LOGGER)
        with PostgresDatabase.from_instance(instance, autocommit=True) as db:
            watch_it(
                interval=watch,
                task=lambda: ReplicationService(db).slots(name),
                on_result=lambda slots: TablePrinter.from_dataclasses("Replication Slot Info", slots).print(),
                logger=instance.logger,
            )
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)


@app.command(help="Get subscription info")
def subs(
    database: DATABASE_OPTION,
    name: Annotated[str | None, typer.Option("--name", "-n", help="Subscription name (optional)")] = None,
    watch: WATCH_OPTION = 0,
    debug: DEBUG_OPTION = False,
):
    try:
        instance: PostgresInstance = PostgresInstance.from_env_vars(database, LOGGER)
        with PostgresDatabase.from_instance(instance, autocommit=True) as db:
            watch_it(
                interval=watch,
                task=lambda: ReplicationService(db).subs(name),
                on_result=lambda subs: TablePrinter.from_dataclasses("Subscription Info", subs).print(),
                logger=instance.logger,
            )
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
