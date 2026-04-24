from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from postgres_dba.models.postgres.instance import Composed, TupleRow

T = TypeVar("T", bound="PostgresData")


@dataclass(frozen=True)
class PostgresData(Generic[T]):
    @classmethod
    def from_row(cls: type[T], row: TupleRow) -> T:
        return cls(*row)

    @staticmethod
    def _query(*args: Any, **kwargs: Any) -> Composed:
        raise NotImplementedError
