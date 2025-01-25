from datetime import datetime
from typing import Annotated, AsyncGenerator
from uuid import UUID

import clickhouse_connect
from fastapi import Depends
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from clicky.config import settings
from clicky.db import engine
from clicky.entities import User, UserSession
from clicky.services import Clickhouse, OpenAIService, SessionService


async def _get_user() -> User:
    return User(
        email="nevio@google.com",
        full_name="Nevio",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


User_T = Annotated[User, Depends(_get_user)]


async def _get_user_session(user: User_T) -> UserSession:
    return UserSession(user=user.email, id=UUID("3d648dea-8207-4f9c-90b1-3d899d718f65"))


UserSession_T = Annotated[UserSession, Depends(_get_user_session)]


async def _new_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.new_session() as sess:
        yield sess


DBSession_T = Annotated[AsyncSession, Depends(_new_db_session)]


async def _new_session_service(session: DBSession_T) -> SessionService:
    return SessionService(sess=session)


SessionService_T = Annotated[SessionService, Depends(_new_session_service)]


async def _new_clickhouse_service() -> Clickhouse:
    # TODO
    connection = await clickhouse_connect.get_async_client(
        host="",
        user="",
        password="",
        database="",
    )
    return Clickhouse(connection)


Clickhouse_T = Annotated[Clickhouse, Depends(_new_clickhouse_service)]


async def _new_openai_service() -> AsyncGenerator[OpenAIService, None]:
    async with AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
    ) as client:
        yield OpenAIService(client=client)


OpenAIService_T = Annotated[OpenAIService, Depends(_new_openai_service)]
