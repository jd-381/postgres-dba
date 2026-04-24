from collections.abc import Sequence
from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime, timezone
from typing import Any

from rich.console import Console
from rich.table import Table

from postgres_dba.common.logger_utils import green, red, yellow


@dataclass(frozen=True)
class TablePrinter:
    title: str
    columns: list[str]
    rows: list[Sequence[Any]]

    @classmethod
    def from_dataclasses(cls, title: str, dataclasses: list[Any]) -> "TablePrinter":
        if not dataclasses:
            return cls(title=title, columns=[], rows=[])
        first_row = dataclasses[0]
        if not is_dataclass(first_row):
            raise ValueError('"dataclasses" must be a list of dataclass instances')
        columns: list[str] = [field.name for field in fields(first_row)]
        rows: list[Sequence[Any]] = []
        for d in dataclasses:
            row = tuple(getattr(d, field.name) for field in fields(d))
            rows.append(row)
        return cls(title=title, columns=columns, rows=rows)

    def print(self) -> None:
        console: Console = Console()
        timestamp: str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        console.print(f"\n{green(timestamp)} {yellow(self.title)}")
        if not self.rows:
            console.print(f"{red('No data to display')}")
            return
        table = Table(show_header=True, header_style="bold magenta")
        for col in self.columns:
            table.add_column(col)
        for row in self.rows:
            table.add_row(*[str(val) if val is not None else "" for val in row])
        console.print(table)
