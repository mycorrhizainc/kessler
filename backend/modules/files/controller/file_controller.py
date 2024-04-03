from uuid import UUID


from litestar import Controller, Request

from litestar.handlers.http_handlers.decorators import get, post, delete, patch
from litestar.params import Parameter
from litestar.di import Provide
from litestar.repository.filters import LimitOffset

from pydantic import TypeAdapter, validator

from db import BaseModel

from modules.files.dbm import FileRepository, provide_files_repo, FileModel


class FileUpload(BaseModel):
    file_metadata: dict
    # Figure out how to do a file upload datatype, maybe with werkzurg or something


class UrlUpload(BaseModel):
    url: str
    # I am going to be removing the ability for overloading metadata
    # title: str | None = None


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


class FileCreate(BaseModel):
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
        file_id: UUID = Parameter(
            title="File ID", description="File to retieve"),
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
        file_id: UUID = Parameter(
            title="File ID", description="File to retieve"),
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
        file_id: UUID = Parameter(
            title="File ID", description="File to retieve"),
    ) -> None:
        _ = files_repo.delete(files_repo)
        files_repo.session.commit()