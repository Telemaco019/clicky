from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from clicky.entities import ExecutedQuery


class Base(DeclarativeBase, MappedAsDataclass):
    pass


class IDMixin(MappedAsDataclass):
    id: Mapped[UUID] = mapped_column(primary_key=True, index=True)


class TimeStampMixin(MappedAsDataclass):
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()


class DataSourceOrm(Base, IDMixin, TimeStampMixin):
    __tablename__ = "data_source"

    name: Mapped[str] = mapped_column()


class SessionOrm(Base, IDMixin, TimeStampMixin):
    __tablename__ = "session"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
    )


class ExecutedQueryOrm(Base, IDMixin, TimeStampMixin):
    __tablename__ = "executed_query"

    query: Mapped[str] = mapped_column()
    ch_query_id: Mapped[str] = mapped_column()
    execution_ns: Mapped[float] = mapped_column()
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("session.id", ondelete="CASCADE"),
        index=True,
    )

    def as_entity(self) -> ExecutedQuery:
        return ExecutedQuery(
            id=self.id,
            query=self.query,
            execution_ns=self.execution_ns,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class UserOrm(Base, IDMixin, TimeStampMixin):
    __tablename__ = "user"

    full_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    last_login: Mapped[datetime] = mapped_column()
