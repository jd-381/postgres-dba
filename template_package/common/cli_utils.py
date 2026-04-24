import logging
from typing import Annotated

import typer

from template_package.common.logger_utils import yellow


def validate_user_input_debug(input: bool) -> bool:
    if input:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug(f"{yellow('Debug mode enabled')}")
    return input


DEBUG_OPTION = Annotated[bool, typer.Option("--debug", help="Print debug messages", callback=validate_user_input_debug)]
