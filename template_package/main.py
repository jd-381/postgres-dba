"""
Main entry point for the application.

This module serves as the root Typer application that aggregates all command modules.
It demonstrates how to:
- Create a root Typer app that serves as the main CLI entry point
- Register sub-applications (commands) using add_typer()
- Configure logging with Rich for beautiful terminal output
- Set up global app configuration (no args shows help, completion disabled)
- Add a --version flag using a callback

The main app doesn't have its own commands - it only serves as a container for
sub-commands from other modules (hello, mail, etc.).
"""

import logging
from importlib.metadata import version
from typing import Annotated

import typer
from rich.logging import RichHandler

from template_package.commands.hello import app as hello
from template_package.commands.mail import app as mail

# Get version from pyproject.toml via package metadata
# This is the recommended best practice - single source of truth
__version__ = version("template-package")

# Configure Rich logging for beautiful, formatted console output
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(markup=True)])

# Root Typer app - serves as the main CLI entry point
# - add_completion=False: Disables shell completion installation
# - no_args_is_help=True: Shows help when run without arguments
app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="A CLI application demonstrating Typer best practices with commands and subcommands.",
)


def version_callback(value: bool) -> None:
    """Display the application version and exit.

    This callback is triggered when the user passes --version flag.
    """
    if value:
        typer.echo(f"template-cli version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", "-v", callback=version_callback, help="Show version"),
    ] = False,
) -> None:
    """
    A CLI application demonstrating Typer best practices.

    This application showcases various Typer patterns including single commands,
    commands with subcommands, service layers, and proper error handling.
    """
    # The version parameter is handled by the callback so this
    # function body is only reached for normal command execution
    pass


# Register sub-commands by adding their Typer apps
app.add_typer(hello, name="hello", help="Greet someone in various languages")
app.add_typer(mail, name="mail", help="Manage and interact with email messages")


if __name__ == "__main__":
    # This allows running the module directly with: python -m template_package.main
    # Useful for development and debugging
    app()
