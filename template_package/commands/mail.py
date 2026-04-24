"""
Example of a command with multiple subcommands.

This module demonstrates how to create a Typer app with multiple subcommands.
The key configuration is:
- invoke_without_command=False: Requires a subcommand to be specified
- no_args_is_help=True: Shows help text when no subcommand is provided

For a single command without subcommands, see commands/hello.py instead.
"""

import logging
from logging import Logger
from typing import Annotated

import typer

from template_package.common.cli_utils import DEBUG_OPTION
from template_package.models.mail import Mail, mail_data

LOGGER = logging.getLogger(__name__)

# Multi-subcommand configuration: requires user to specify a subcommand
app = typer.Typer(invoke_without_command=False, no_args_is_help=True)


class MailService:
    """Service for managing mail operations (fetch, delete)."""

    def __init__(self, logger: Logger):
        self._logger: Logger = logger

    def delete(self, count: int) -> None:
        """Delete a specified number of messages from the mail data.

        Args:
            count: Number of messages to delete
        """
        self._logger.debug("Deleting messages")
        del mail_data[:count]
        self._logger.info(f"Done! {len(mail_data)} remaining messages")

    def fetch(self) -> list[Mail]:
        """Fetch all available mail messages.

        Returns:
            List of Mail objects
        """
        self._logger.debug("Fetching mail")
        return mail_data


@app.command(name="delete", help="Delete mail")
def delete(
    count: Annotated[int, typer.Option("--count", "-c", help="Number of messages to delete")],
    debug: DEBUG_OPTION = False,
) -> None:
    """Delete a specified number of mail messages.

    This is a subcommand of the mail command. It demonstrates how to delete
    messages from the mail data store.
    """
    try:
        svc: MailService = MailService(LOGGER)
        svc.delete(count)
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)


@app.command(name="fetch", help="Fetch mail")
def fetch(debug: DEBUG_OPTION = False) -> None:
    """Fetch and display all mail messages.

    This is a subcommand of the mail command. It retrieves all available
    messages and displays them to the user.
    """
    try:
        svc: MailService = MailService(LOGGER)
        mail: list[Mail] = svc.fetch()
        print(f"{len(mail)} new messages!\n")
        for m in mail:
            print(m)
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)


@app.command(name="error", help="Show example error")
def error() -> None:
    """Demonstrate error handling in a Typer command.

    This is a subcommand of the mail command. It shows how exceptions
    are caught and logged, then exits with a non-zero code.
    """
    try:
        raise Exception("This is an example error message")
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)
