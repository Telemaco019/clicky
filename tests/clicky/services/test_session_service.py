from uuid import uuid4

from clicky.services import SessionService


class TestGetQueries:
    async def test_empty_db(self, session_service: SessionService) -> None:
        queries = await session_service.get_queries(uuid4())
        assert queries == []
