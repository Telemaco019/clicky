from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from alembic import command, config


class DBEngine:
    def __init__(
        self,
        engine: AsyncEngine,
        session_maker: async_sessionmaker[AsyncSession],
        alembic_config_path: Path,
    ) -> None:
        self.session_maker = session_maker
        self.engine = engine
        self._alembic_config_path = alembic_config_path

    @classmethod
    def from_dsn(
        cls, dsn: str, alembic_config_path: Path, echo: bool = False
    ) -> "DBEngine":
        engine = create_async_engine(dsn, echo=echo)
        session_maker = async_sessionmaker(engine, expire_on_commit=False)
        return cls(
            engine=engine,
            session_maker=session_maker,
            alembic_config_path=alembic_config_path,
        )

    async def upgrade(self) -> None:
        cfg = config.Config(self._alembic_config_path)
        cfg.set_main_option("sqlalchemy.url", str(self.engine.url))

        def _upgrade(_: Connection) -> None:
            command.upgrade(cfg, "head")

        async with self.session_maker() as session:
            conn = await session.connection()
            await conn.run_sync(_upgrade)

    @asynccontextmanager
    async def new_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_maker() as session:
            yield session
