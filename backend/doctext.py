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
    url: Mapped[str]
    title: Mapped[str]
    doctype: Mapped[str]
    metadata: Mapped[str]
    extras: Mapped[str]
    status: Mapped[str]

    @validator("id")
    def validate_uuid(cls, value):
        if value:
            return str(value)
        return value
