from typing import Annotated, Any, List

from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository

from sqlalchemy.orm import Mapped


from .utils import PydanticBaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import Field, field_validator


class FileModel(UUIDAuditBase):
    """Database representation of a file"""

    __tablename__ = "file"
    url: Mapped[str | None]
    doctype: Mapped[str | None]
    lang: Mapped[str | None]
    name: Mapped[str | None]
    source: Mapped[str | None]
    hash: Mapped[str | None]
    mdata: Mapped[str | None]
    stage: Mapped[str | None]
    summary: Mapped[str | None]
    short_summary: Mapped[str | None]
    original_text: Mapped[str | None]
    english_text: Mapped[str | None]


class FileRepository(SQLAlchemyAsyncRepository[FileModel]):
    """File repository."""

    model_type = FileModel


async def provide_files_repo(db_session: AsyncSession) -> FileRepository:
    """This provides the default Authors repository."""
    return FileRepository(session=db_session)


class FileSchema(PydanticBaseModel):
    """pydantic schema of the FileModel"""

    id: Annotated[Any, Field(validate_default=True)]
    url: str | None = None
    doctype: str | None = None
    lang: str | None = None
    name: str | None = None
    source: str | None = None
    stage: str | None = None
    summary: str | None = None
    mdata: str | None = None
    short_summary: str | None = None

    @field_validator("id")
    @classmethod
    def stringify_id(cls, id: any) -> str:
        return str(id)


class FileSchemaWithText(FileSchema):
    original_text: str | None = None
    english_text: str | None = None
