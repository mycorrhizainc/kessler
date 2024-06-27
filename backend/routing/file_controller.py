from lance_store.connection import ensure_fts_index
from rag.llamaindex import add_document_to_db_from_text
import os
from pathlib import Path
from typing import Any
from uuid import UUID
from typing import Annotated

from litestar import Controller, Request

from litestar.handlers.http_handlers.decorators import (
    get,
    post,
    delete,
    MediaType,
)


from sqlalchemy import select


from litestar.params import Parameter
from litestar.di import Provide
from litestar.repository.filters import LimitOffset
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body

from pydantic import TypeAdapter
from models.utils import PydanticBaseModel as BaseModel


# from models import (
#     FileModel,
#     FileRepository,
#     FileSchema,
#     FileSchemaWithText,
#     provide_files_repo,
# )
from models.files import (
    FileModel,
    FileRepository,
    FileSchema,
    FileSchemaWithText,
    provide_files_repo,
)

from crawler.docingest import DocumentIngester
from docprocessing.extractmarkdown import MarkdownExtractor

from typing import List, Optional, Dict


import json


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


# TODO : Create test that adds a file once we know what the file DB schema is going to look like


class FileUpdate(BaseModel):
    message: str
    metadata: Dict[str, Any]


class UrlUpload(BaseModel):
    url: str
    metadata: Dict[str, Any]


class UrlUploadList(BaseModel):
    url: List[str]


class FileCreate(BaseModel):
    message: str


class FileUpload(BaseModel):
    message: str


class IndexFileRequest(BaseModel):
    id: UUID


# litestar only


OS_TMPDIR = Path(os.environ["TMPDIR"])
OS_GPU_COMPUTE_URL = os.environ["GPU_COMPUTE_URL"]
OS_FILEDIR = Path("/files/")


# import base64


OS_TMPDIR = Path(os.environ["TMPDIR"])
OS_GPU_COMPUTE_URL = os.environ["GPU_COMPUTE_URL"]
OS_FILEDIR = Path("/files/")
OS_HASH_FILEDIR = OS_FILEDIR / Path("raw")
OS_OVERRIDE_FILEDIR = OS_FILEDIR / Path("override")
OS_BACKUP_FILEDIR = OS_FILEDIR / Path("backup")


# import base64


class FileController(Controller):
    """File Controller"""

    dependencies = {"files_repo": Provide(provide_files_repo)}

    # def jsonify_validate_return(self,):
    #     return None

    @get(path="/files/{file_id:uuid}")
    async def get_file(
        self,
        withtext: bool,
        files_repo: FileRepository,
        file_id: UUID = Parameter(title="File ID", description="File to retieve"),
    ) -> FileSchema:
        obj = await files_repo.get(file_id)

        if withtext:
            type_adapter = TypeAdapter(FileSchemaWithText)
        else:
            type_adapter = TypeAdapter(FileSchema)

        return type_adapter.validate_python(obj)

    @get(path="/files/all")
    async def get_all_files(
        self, files_repo: FileRepository, limit_offset: LimitOffset, request: Request
    ) -> list[FileSchema]:
        """List files."""
        results = await files_repo.list()
        logger = request.logger
        logger.info(f"{len(results)} results")
        type_adapter = TypeAdapter(list[FileSchema])
        return type_adapter.validate_python(results)

    # TODO: replace this with a jobs endpoint
    # TODO : (Nic) Make function that can process uploaded files
    @post(path="/files/add_url")
    async def add_url(
        self,
        files_repo: FileRepository,
        data: UrlUpload,
        request: Request,
        process: bool = False,
        override_hash: bool = False,
    ) -> Any:
        request.logger.info("adding files")
        request.logger.info(data)

        # ------------------ here be a site for refactor --------------------
        docingest = DocumentIngester(request.logger)

        request.logger.info("DocumentIngester Created")

        tmpfile_path, metadata, tmpfile_cleanup = (
            docingest.url_to_filepath_and_metadata(data.url)
        )
        new_metadata = data.metadata

        if new_metadata is not None:
            metadata.update(new_metadata)

        request.logger.info(f"Metadata Successfully Created with metadata {metadata}")

        document_title = metadata.get("title")
        document_doctype = metadata.get("doctype")
        document_lang = metadata.get("language")

        try:
            assert isinstance(document_title, str)
            assert isinstance(document_doctype, str)
            assert isinstance(document_lang, str)
        except Exception:
            request.logger.error("Illformed Metadata please fix")

        else:
            request.logger.info("Title, Doctype and language successfully declared")

        document_source = metadata.get("source")
        if document_source is None:
            document_source = "UNKNOWN"
            metadata["source"] = "UNKNOWN"

        request.logger.info("Attempting to save data to file")
        result = docingest.save_filepath_to_hash(tmpfile_path, OS_HASH_FILEDIR)
        (filehash, filepath) = result

        tmpfile_cleanup()

        # NOTE: this is a dangeous query
        # FIX: fix this to not allow for users to DOS files
        query = select(FileModel).where(FileModel.hash == filehash)

        duplicate_file_objects = await files_repo.session.execute(query)
        duplicate_file_obj = duplicate_file_objects.scalar()

        if override_hash is True and duplicate_file_obj is not None:
            try:
                await files_repo.delete(duplicate_file_obj.id)
            except Exception:
                pass
            duplicate_file_obj = None

        if duplicate_file_obj is None:
            docingest.backup_metadata_to_hash(metadata, filehash)
            metadata_str = json.dumps(metadata)
            new_file = FileModel(
                url=data.url,
                name=document_title,
                doctype=document_doctype,
                lang=document_lang,
                source=document_source,
                metadata=metadata_str,
                stage="stage1",
                hash=filehash,
                summary=None,
                short_summary=None,
            )
            request.logger.info("new file:{file}".format(file=new_file.to_dict()))
            try:
                new_file = await files_repo.add(new_file)
            except Exception as e:
                request.logger.info(e)
                return e
            request.logger.info("added file!~")
            await files_repo.session.commit()
            request.logger.info("commited file to DB")

        else:
            request.logger.info(type(duplicate_file_obj))
            request.logger.info(
                f"File with identical hash already exists in DB with uuid:\
                {duplicate_file_obj.id}"
            )
            new_file = duplicate_file_obj

        if process:
            request.logger.info("Processing File")
            await self.process_file_raw(new_file, files_repo, request.logger, False)

        type_adapter = TypeAdapter(FileSchema)
        return type_adapter.validate_python(new_file)

    @post(path="/files/add_urls")
    async def add_urls(
        self, files_repo: FileRepository, data: UrlUploadList, request: Request
    ) -> None:
        return None

    # TODO: anything but this

    @post(path="/process/{file_id_str:str}")
    async def process_file(
        self,
        files_repo: FileRepository,
        request: Request,
        file_id_str: str = Parameter(
            title="File ID as hex string", description="File to retieve"
        ),
        regenerate: bool = True,  # Figure out how to pass in a boolean as a query paramater
    ) -> FileSchema:
        """Process a File."""
        file_id = UUID(file_id_str)
        request.logger.info(file_id)
        obj = await files_repo.get(file_id)
        # TODO : Add error for invalid document ID
        await self.process_file_raw(obj, files_repo, request.logger, regenerate)
        # TODO : Return Response code and response message
        return self.validate_and_jsonify(obj)

    async def process_file_raw(
        self, obj: FileModel, files_repo: FileRepository, logger: Any, regenerate: bool
    ):
        logger.info(type(obj))
        logger.info(obj)
        current_stage = obj.stage
        doctype = obj.doctype
        logger.info(obj.doctype)
        mdextract = MarkdownExtractor(logger, OS_TMPDIR)
        doc_metadata = json.loads(obj.metadata_str)

        response_code, response_message = (
            500,
            "Internal error somewhere in process.",
        )

        if regenerate:
            current_stage = "stage1"

        # text extraction
        def process_stage_one():

            processed_original_text = (
                mdextract.process_raw_document_into_untranslated_text(
                    Path(obj.path), obj.doctype, obj.lang
                )
            )
            mdextract.backup_processed_text(
                processed_original_text, doc_metadata, OS_BACKUP_FILEDIR
            )
            if obj.lang == "en":
                # Write directly to the english text box if
                # original text is identical to save space.
                obj.english_text = processed_original_text
                # Skip translation stage if text already english.
                return "stage3"
            else:
                obj.original_text = processed_original_text
                return "stage2"

        # text conversion
        def process_stage_two():
            try:
                if obj.lang == "en":
                    processed_english_text = mdextract.convert_text_into_eng(
                        obj.original_text, obj.lang
                    )
                else:
                    raise Exception(
                        "\
                        Code is in an unreachable state, \
                        this situation should have been caught \
                        by an error in stage 1.\
                    "
                    )
            except Exception as e:
                obj.english_text = processed_english_text
                raise Exception(
                    "\
                    failure in stage 2: \
                    document was unable to be translated to english.\
                ",
                    e,
                )
            return "stage3"

        # text commitment
        def process_stage_three():
            try:
                add_document_to_db_from_text(obj.english_text, doc_metadata)
            except Exception as e:
                raise Exception("Failure in adding document to vector database", e)

        while True:
            try:
                match current_stage:
                    case "stage1":
                        current_stage = process_stage_one()
                    case "stage2":
                        current_stage = process_stage_two()
                    case "stage3":
                        current_stage = process_stage_three()
                    case "completed":
                        response_code, response_message = (
                            200,
                            "Document Fully Processed.",
                        )
                        logger.info(current_stage)
                        obj.stage = current_stage
                        logger.info(response_code)
                        logger.info(response_message)
                        _ = files_repo.update(obj)
                        await files_repo.session.commit()
                        break
                    case _:
                        raise Exception(
                            "Document was incorrectly added to database, \
                            try readding it again.\
                        "
                        )

            except Exception as e:
                logger.error(e)
                break

    @post(path="/files/upload/from/md", media_type=MediaType.TEXT)
    async def upload_from_markdown(
        self,
        files_repo: FileRepository,
        request: Request,
        data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
    ) -> None:
        try:
            content = await data.read()
            filename = data.filename
            file = content.decode()
            splitfile = file.split("---")
            restfile = "".join(splitfile[2:])
            file_metadata = splitfile[1].split("\n")
            meta = {}
            for i in file_metadata:
                if i == "":
                    continue
                field = i.split(":")
                if len(field) >= 2:
                    meta[field[0]] = "".join(field[1:])

            m_text = json.dumps(meta)

            FileModel(english_text=file, metadata=m_text)
            new_file = FileModel(
                url="",
                name=filename,
                doctype="markdown",
                lang="english",
                source="markdown",
                metadata=m_text,
                stage="completed",
                hash="None",
                summary=None,
                short_summary=None,
                english_text=restfile,
            )
            try:
                files_repo.session.add(new_file)
                await files_repo.session.flush()
                files_repo.session.refresh(new_file)
                await files_repo.session.commit()
            except Exception as e:
                return f"issue: \n{e}"
            try:
                meta["uid"] = str(new_file.id)
                add_document_to_db_from_text(text=restfile, metadata=meta)
                request.app.emit("increment_processed_docs", num=1)
                request.logger.info("added a document to the db")
            except Exception as e:
                request.logger.error(e)
                return "issue indexing file"
            return new_file.english_text

        except Exception as e:
            raise (e)

    @delete(path="/files/{file_id:uuid}")
    async def delete_file(
        self,
        files_repo: FileRepository,
        file_id: UUID = Parameter(title="File ID", description="File to retieve"),
    ) -> None:
        fid = UUID(file_id)
        _ = await files_repo.delete(fid)
        await files_repo.session.commit()
