from contextlib import asynccontextmanager
from typing import AsyncIterator, Annotated
import traceback
from uuid import UUID

from litestar.contrib.sqlalchemy.base import UUIDAuditBase, AuditColumns
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


from .utils import RepoMixin, sqlalchemy_config, PydanticBaseModel


class FileModel(UUIDAuditBase, RepoMixin):
    """Database representation of a file"""
    __tablename__ = "file"
    path: Mapped[str]
    doctype: Mapped[str]
    lang: Mapped[str]
    name: Mapped[str]
    stage: Mapped[str]  # Either "stage0" "stage1" "stage2" or "stage3"
    summary: Mapped[str | None]
    short_summary: Mapped[str | None]
    original_text: Mapped[str | None]
    english_text: Mapped[str | None]

    @classmethod
    async def provide_repo(cls, session) -> 'FileRepository':
        return FileRepository(session=session)

    # # define the context manager for each file repo
    @classmethod
    @asynccontextmanager
    async def repo(cls) -> AsyncIterator['FileRepository']:
        session_factory = sqlalchemy_config.create_session_maker()
        async with session_factory() as db_session:
            try:
                yield cls.provide_repo(session=db_session)
            except Exception as e:
                print(traceback.format_exc())
                print("rolling back")
                await db_session.rollback()
            else:
                print("committhing change")
                await db_session.commit()

    @classmethod
    async def updateStage(cls, id, stage):
        async with cls.repo() as repo:
            obj = await cls.find(id)
            obj.stage = stage
            obj = await repo.update(obj)

            return obj


class FileRepository(SQLAlchemyAsyncRepository[FileModel]):
    """File repository."""

    model_type = FileModel


class FileSchema(PydanticBaseModel):
    """pydantic schema of the FileModel"""
    id: UUID | str  # TODO: better typing for this
    path: str
    doctype: str
    lang: str
    name: str
    # Either "stage0" "stage1" "stage2" or "stage3"
    stage: str
    summary: str | None = None
    short_summary: str | None = None
    original_text: str | None = None
    english_text: str | None = None