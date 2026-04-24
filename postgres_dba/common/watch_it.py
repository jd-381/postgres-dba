from logging import Logger
from time import sleep
from typing import Callable, TypeVar

from postgres_dba.common.logger_utils import magenta

T = TypeVar("T")


def watch_it(
    *,
    interval: float,
    task: Callable[[], T],
    on_result: Callable[[T], None],
    logger: Logger,
) -> None:
    if interval > 0:
        try:
            while True:
                result = task()
                on_result(result)
                logger.info(f"Sleeping {interval} seconds")
                sleep(interval)
        except KeyboardInterrupt:
            logger.info(magenta("My watch has ended"))
    else:
        result = task()
        on_result(result)
