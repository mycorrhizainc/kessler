import logging 

from litestar import Litestar, Router

from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.plugins import AsyncSessionConfig, SQLAlchemyAsyncConfig, SQLAlchemyInitPlugin

from litestar.params import Parameter
from litestar.di import Provide
from litestar.repository.filters import LimitOffset

from litestar.config.cors import CORSConfig
from litestar.logging import LoggingConfig

from files import FileController

# set up the database
session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///instance/kessler.sqlite",
    session_config=session_config
)
sqlalchemy_plugin = SQLAlchemyInitPlugin(config=sqlalchemy_config)

logging_config = LoggingConfig(
    root={"level": logging.getLevelName(logging.INFO), "handlers": ["console"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
)

async def on_startup() -> None:
    async with sqlalchemy_config.get_engine().begin() as conn:
        # UUIDAuditBase extends UUIDBase so create_all should build both
        await conn.run_sync(UUIDBase.metadata.create_all)


async def provide_limit_offset_pagination(
    current_page: int = Parameter(
        ge=1, query="currentPage", default=1, required=False),
    page_size: int = Parameter(
        query="pageSize",
        ge=1,
        default=10,
        required=False,
    ),
) -> LimitOffset:
    """Add offset/limit pagination.

    Return type consumed by `Repository.apply_limit_offset_pagination()`.

    Parameters
    ----------
    current_page : int
        LIMIT to apply to select.
    page_size : int
        OFFSET to apply to select.
    """
    return LimitOffset(page_size, page_size * (current_page - 1))


cors_config = CORSConfig(allow_origins=["*.*"])

api_router = Router(
    path="/api",
    route_handlers=[FileController]
)

app = Litestar(
    on_startup=[on_startup],
    plugins=[sqlalchemy_plugin],
    route_handlers=[api_router],
    dependencies={"limit_offset": Provide(provide_limit_offset_pagination)},
    cors_config=cors_config,
    logging_config=logging_config
)
