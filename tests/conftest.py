import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from clicky.db import engine
from clicky.services import SessionService


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture(scope="session", autouse=True)
async def reset_db() -> None:
    await engine.upgrade()


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with engine.new_session() as sess:
        base_flush = sess.flush

        async def _commit_override() -> None:
            await base_flush()

        with (
            patch.object(sess, "flush", new=_commit_override),
            patch.object(sess, "commit", new=_commit_override),
        ):
            yield sess


@pytest.fixture
def session_service(db: AsyncSession) -> SessionService:
    return SessionService(sess=db)
