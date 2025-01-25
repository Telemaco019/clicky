from dataclasses import dataclass
from datetime import datetime
from typing import Any, Sequence
from uuid import UUID

import humanize


@dataclass(frozen=True)
class User:
    full_name: str
    email: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class UserSession:
    id: UUID
    user: str


@dataclass(frozen=True)
class QueryOutput:
    columns: Sequence[str]
    rows: Sequence[Sequence[Any]]


@dataclass(frozen=True)
class QueryStats:
    fetched_rows: int
    processed_rows: int
    processed_bytes: int
    execution_ns: int

    @property
    def execution_seconds(self) -> float:
        return self.execution_ns / 1_000_000_000

    @property
    def execution_time_humanized(self) -> str:
        return humanize.naturaldelta(
            self.execution_seconds,
            minimum_unit="milliseconds",
        )

    @property
    def processed_bytes_humanized(self) -> str:
        return humanize.filesize.naturalsize(self.processed_bytes)

    @property
    def processed_rows_humanized(self) -> str:
        return humanize.intword(self.processed_rows)

    @property
    def throughput_humanized(self) -> str:
        return humanize.naturalsize(self.processed_bytes / self.execution_seconds)


@dataclass(frozen=True)
class QueryResult:
    query_id: str
    output: QueryOutput
    stats: QueryStats


@dataclass(frozen=True)
class ExecutedQuery:
    id: UUID
    query: str
    execution_ns: float
    created_at: datetime
    updated_at: datetime
