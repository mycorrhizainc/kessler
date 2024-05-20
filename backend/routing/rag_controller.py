from hashlib import blake2b
import os
from pathlib import Path
from typing import Any
from uuid import UUID
from typing import Annotated, assert_type
import logging

from litestar import Controller, Request

from litestar.handlers.http_handlers.decorators import (
    get,
    post,
    delete,
    patch,
    MediaType,
)


from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


from litestar.params import Parameter
from litestar.di import Provide
from litestar.repository.filters import LimitOffset
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.logging import LoggingConfig

from pydantic import TypeAdapter
from models.utils import PydanticBaseModel as BaseModel


from models import FileModel, FileRepository, FileSchema, provide_files_repo


from crawler.docingest import DocumentIngester
from docprocessing.extractmarkdown import MarkdownExtractor
from docprocessing.genextras import GenerateExtras
from util.haystack import indexDocByID

from typing import List, Optional, Union, Any, Dict


from util.niclib import get_blake2

from util.haystack import indexDocByID, get_indexed_by_id

import json


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)



class SimpleChatCompletion(BaseModel):
    model: Optional[str]
    chat_history: List[Dict[str, str]]




# litestar only


OS_TMPDIR = Path(os.environ["TMPDIR"])
OS_GPU_COMPUTE_URL = os.environ["GPU_COMPUTE_URL"]
OS_FILEDIR = Path("/files/")


# import base64


OS_TMPDIR = Path(os.environ["TMPDIR"])
OS_GPU_COMPUTE_URL = os.environ["GPU_COMPUTE_URL"]
OS_FILEDIR = Path("/files/")


# import base64
# crypto_keyfile.bin


from llama_index.llms.groq import Groq



GROQ_API_KEY = os.environ["GROQ_API_KEY"]
groq_llm = Groq(
    model="llama3-70b-8192", request_timeout=360.0, api_key=GROQ_API_KEY
)





class RagController(Controller):
    """File Controller"""

    dependencies = {"files_repo": Provide(provide_files_repo)}

    # def jsonify_validate_return(self,):
    #     return None

    @get(path="/rag/simple_chat_completion")
    async def get_file(
        self,
        files_repo: FileRepository,
        data : SimpleChatCompletion
    ) -> str:
        model_name = data.model_name
        if model_name is None:
            model_name = "llama3-70b-8192" 
        groq_llm = Groq(
            model=model_name, request_timeout=360.0, api_key=GROQ_API_KEY
        )
        chat_history = data.chat_history
        response = groq_llm.chat(chat_history)
        return response
