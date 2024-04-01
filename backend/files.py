from typing import TYPE_CHECKING, Optional, Any, cast, List

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Mapped

from litestar import Controller, Request

from litestar.pagination import OffsetPagination

from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.handlers.http_handlers.decorators import get, post, delete, patch
from litestar.params import Parameter
from litestar.di import Provide
from litestar.repository.filters import LimitOffset

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from pydantic import TypeAdapter, validator

from db import BaseModel


class FileModel(UUIDAuditBase):
    __tablename__ = "file"
    hash: Mapped[
        str
    ]  # Blake2. For the file database this should absolutely be the primary key,
    doctype: Mapped[str]
    lang: Mapped[str]
    title: Mapped[
        str
    ]  # I dont know if this should be included either in here or as a entry in doc_metadata, expecially since its only ever going to be used by the frontend. However, it might be an important query paramater and it seems somewhat irresponsible to not include.
    doc_metadata: Mapped[str]
    status: Mapped[str]  # Either "stage0" "stage1" "stage2" or "stage3"
    summary: Mapped[str]
    short_summary: Mapped[str]
    full_text_embedding: Mapped[
        any
    ]  # whatever the type for this is lol, potentially generate it by embedding the summary if the long embeddings dont work.

    @validator("id")
    def validate_uuid(cls, value):
        if value:
            return str(value)
        return value


class TextStorage(UUIDAuditBase):
    hash: Mapped[str]  # Foreign Key into FileModel
    original_text: Mapped[str]
    en_text: Mapped[str]


class FileUpload(BaseModel):
    file_metadata: dict
    # Figure out how to do a file upload datatype, maybe with werkzurg or something


class UrlUpload(BaseModel):
    url: str
    # I am going to be removing the ability for overloading metadata
    # title: str | None = None


class FileRepository(SQLAlchemyAsyncRepository[FileModel]):
    """File repository."""

    model_type = FileModel


async def provide_files_repo(db_session: AsyncSession) -> FileRepository:
    """This provides the default File repository."""
    return FileRepository(session=db_session)


class File(BaseModel):
    id: any  # TODO: figure out a better type for this UUID :/
    url: str
    title: str | None

    @validator("id")
    def validate_uuid(cls, value):
        if value:
            return str(value)
        return value


class FileUpdate(BaseModel):
    url: str | None = None
    title: str | None = None


# litestar only
class FileController(Controller):
    """File Controller"""

    dependencies = {"files_repo": Provide(provide_files_repo)}

    @get(path="/files/{file_id:uuid}")
    async def get_file(
        self,
        files_repo: FileRepository,
        file_id: UUID = Parameter(title="File ID", description="File to retieve"),
    ) -> File:
        obj = files_repo.get(file_id)
        return File.model_validate(obj)

    @get(path="/files/all")
    async def get_all_files(
        self, files_repo: FileRepository, limit_offset: LimitOffset, request: Request
    ) -> list[File]:
        """List files."""
        results = await files_repo.list()
        type_adapter = TypeAdapter(list[File])
        return type_adapter.validate_python(results)

    @post(path="files/upload")
    async def upload_file(self) -> File:
        pass

    @post(path="/links/add")
    async def add_file(
        self, files_repo: FileRepository, data: FileCreate, request: Request
    ) -> File:
        request.logger.info("adding files")
        request.logger.info(data)
        new_file = FileModel(url=data.url, title="")
        request.logger.info("new file:{file}".format(file=new_file.to_dict()))
        try:
            new_file = await files_repo.add(new_file)
        except Exception as e:
            request.logger.info(e)
            return e
        request.logger.info("added file!~")
        await files_repo.session.commit()
        return File.model_validate(new_file)

    @patch(path="/files/{file_id:uuid}")
    async def update_File(
        self,
        files_repo: FileRepository,
        data: FileUpdate,
        file_id: UUID = Parameter(title="File ID", description="File to retieve"),
    ) -> File:
        """Update a File."""
        raw_obj = data.model_dump(exclude_unset=True, exclude_none=True)
        raw_obj.update({"id": file_id})
        obj = files_repo.update(FileModel(**raw_obj))
        files_repo.session.commit()
        return File.model_validate(obj)

    @delete(path="/files/{file_id:uuid}")
    async def delete_file(
        self,
        files_repo: FileRepository,
        file_id: UUID = Parameter(title="File ID", description="File to retieve"),
    ) -> None:
        _ = files_repo.delete(files_repo)
        files_repo.session.commit()
