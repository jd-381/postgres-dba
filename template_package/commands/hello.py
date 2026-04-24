"""
Example of a single command without subcommands.

This module demonstrates how to create a Typer app with a single command that executes
directly when called (no subcommands). The key configuration is:
- invoke_without_command=True: Allows the callback to run directly
- no_args_is_help=False: Executes the command even without arguments (using defaults)

For commands with subcommands, see commands/mail.py instead.
"""

import logging
from logging import Logger
from typing import Annotated

import typer

from template_package.common.cli_utils import DEBUG_OPTION
from template_package.common.logger_utils import cyan
from template_package.models.language import Language

LOGGER = logging.getLogger(__name__)

# Single command configuration: runs the callback directly without subcommands
app = typer.Typer(invoke_without_command=True, no_args_is_help=False)


class HelloService:
    """Service for generating greetings in multiple languages."""

    _GREETINGS = {Language.ENGLISH: "Hello", Language.SPANISH: "Hola"}

    def __init__(self, language: Language = Language.ENGLISH, logger: Logger = LOGGER):
        self._language: Language = language
        self._logger: Logger = logger

    def hello(self, name: str) -> None:
        """Print a greeting in the configured language.

        Args:
            name: The name to greet
        """
        self._logger.debug(f"Using language {cyan(self._language.value)}")
        greeting = self._GREETINGS[self._language]
        print(f"{greeting} {name}")


@app.callback()
def main(
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Name to greet"),
    ],
    language: Annotated[
        Language,
        typer.Option("--language", "-l", help="Language for greeting"),
    ] = Language.ENGLISH,
    debug: DEBUG_OPTION = False,
) -> None:
    """Greet someone in the specified language.

    This is a single command example - when the user runs this command,
    this function executes directly without requiring a subcommand.
    """
    try:
        svc: HelloService = HelloService(language, LOGGER)
        svc.hello(name)
    except Exception as e:
        LOGGER.error(e)
        raise typer.Exit(code=1)
