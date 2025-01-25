from dataclasses import dataclass
from typing import TypeVar
from uuid import UUID

from clicky.entities import QueryResult

T = TypeVar("T")


@dataclass
class Props[T]:
    content: T | None
    error: str | None


@dataclass
class RunQueryProps:
    query_id: UUID
    query: str
    query_result: QueryResult | None
