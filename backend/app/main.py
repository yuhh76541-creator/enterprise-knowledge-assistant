"""Application factory; startup performs local initialization only."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app import __version__
from app.api.routes import router
from app.core.config import Settings
from app.core.database import Database


def create_app(settings: Settings | None = None) -> FastAPI:
    configuration = settings if settings is not None else Settings()
    database = Database(configuration.database_path)

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        await asyncio.to_thread(database.initialize)
        yield

    application = FastAPI(
        title="Enterprise Knowledge Assistant",
        version=__version__,
        lifespan=lifespan,
        description="基础框架：知识空间已实现，RAG 与权限模块规划中。",
    )
    application.state.settings = configuration
    application.state.database = database
    application.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "[::1]", "testserver"]
    )
    application.include_router(router)
    return application


app = create_app()
