from typing import Sequence
from uuid import UUID, uuid4

from clickhouse_connect.driver import AsyncClient  # type: ignore[attr-defined]
from openai import AsyncOpenAI
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from clicky.db.tables import ExecutedQueryOrm
from clicky.entities import ExecutedQuery, QueryOutput, QueryResult, QueryStats
from clicky.utils.time_utils import now


class Clickhouse:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def get_query_stats(self, query_id: str) -> QueryResult:
        raise NotImplementedError

    async def run_query(self, query: str) -> QueryResult:
        res = await self.client.query(
            query.strip().strip(";"),
            settings={},
        )
        cols = [c for c in res.column_names]
        return QueryResult(
            query_id=res.query_id,
            output=QueryOutput(
                columns=cols,
                rows=res.result_rows[:10],
            ),
            stats=QueryStats(
                fetched_rows=len(res.result_rows),
                processed_rows=int(res.summary["read_rows"]),
                processed_bytes=int(res.summary["read_bytes"]),
                execution_ns=int(res.summary["elapsed_ns"]),
            ),
        )


class SessionService:
    def __init__(self, sess: AsyncSession) -> None:
        self.sess = sess

    async def get_queries(self, session_id: UUID) -> Sequence[ExecutedQuery]:
        query = select(ExecutedQueryOrm).where(
            ExecutedQueryOrm.session_id == session_id
        )
        res = await self.sess.scalars(query)
        return [r.as_entity() for r in res]

    async def save_query(
        self,
        *,
        session_id: UUID,
        query: str,
        result: QueryResult,
    ) -> ExecutedQuery:
        query_orm = ExecutedQueryOrm(
            id=uuid4(),
            session_id=session_id,
            query=query,
            execution_ns=result.stats.execution_ns,
            ch_query_id=result.query_id,
            created_at=now(),
            updated_at=now(),
        )
        self.sess.add(query_orm)
        await self.sess.commit()
        return query_orm.as_entity()


class OptimizedQuery(BaseModel):
    optimized_query: str
    error_cause: str | None
    improvements: list[str]


class OpenAIService:
    def __init__(self, client: AsyncOpenAI) -> None:
        self.client = client

    async def optimize_query(
        self, query: str, error: str | None = None
    ) -> OptimizedQuery:
        prompt = """
You are a Clickhouse expert. You receive the following inputs:
* <query> the SQL query to improve
* <error> optional, error returned by executing the query
You generate as output: 
* if the query can be improved, a better version of the query, otherwise empty string.
* if the query is improved, the improvements made.
* if an error was provided, the reason for the error.
        """
        content_text = f"<query>{query}</query>"
        if error:
            content_text += f"<error>{error}</error>"

        completion = await self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=OptimizedQuery,
            messages=[
                {
                    "role": "developer",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f""""
                            <query> {query} </query>
                            <error> {error} </error>
                            """,
                        }
                    ],
                },
            ],
        )
        result = completion.choices[0].message.parsed
        if result is None:
            raise RuntimeError("Failed to optimize query")
        return result
