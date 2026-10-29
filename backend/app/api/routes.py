"""Working foundation endpoints and explicit planned-feature responses."""

import logging
import sqlite3
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.database import Database
from app.schemas import ChatRequest, KnowledgeBaseCreate, KnowledgeBaseRead

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")


def get_database(request: Request) -> Database:
    return request.app.state.database


DatabaseDependency = Annotated[Database, Depends(get_database)]


@router.get("/health", tags=["system"])
def health(database: DatabaseDependency) -> dict[str, str]:
    try:
        database.check()
    except sqlite3.Error as error:
        logger.exception("Database health check failed")
        raise HTTPException(status_code=503, detail="本地数据库暂不可用") from error
    return {"status": "healthy", "database": "connected", "version": "0.1.0"}


@router.get("/status", tags=["system"])
def system_status(request: Request) -> dict[str, object]:
    settings = request.app.state.settings
    return {
        "stage": "foundation",
        "model": {
            "provider": settings.llm_provider,
            "name": settings.llm_model,
            "key_configured": bool(settings.llm_api_key.get_secret_value()),
            "integration": "planned",
        },
        "modules": {
            "knowledge_bases": "available",
            "document_ingestion": "planned",
            "retrieval": "planned",
            "chat": "planned",
            "authentication": "planned",
        },
    }


@router.get("/knowledge-bases", response_model=list[KnowledgeBaseRead], tags=["knowledge"])
def list_knowledge_bases(database: DatabaseDependency) -> list[dict[str, str]]:
    return database.list_knowledge_bases()


@router.post(
    "/knowledge-bases",
    response_model=KnowledgeBaseRead,
    status_code=status.HTTP_201_CREATED,
    tags=["knowledge"],
)
def create_knowledge_base(
    payload: KnowledgeBaseCreate, database: DatabaseDependency
) -> dict[str, str]:
    try:
        return database.create_knowledge_base(payload.name, payload.description.strip())
    except sqlite3.IntegrityError as error:
        raise HTTPException(status_code=409, detail="知识空间名称已存在") from error


@router.get("/knowledge-bases/{identifier}", response_model=KnowledgeBaseRead, tags=["knowledge"])
def get_knowledge_base(identifier: UUID, database: DatabaseDependency) -> dict[str, str]:
    record = database.get_knowledge_base(str(identifier))
    if record is None:
        raise HTTPException(status_code=404, detail="知识空间不存在")
    return record


@router.post("/chat", tags=["planned"])
def chat(payload: ChatRequest) -> None:
    raise HTTPException(status_code=501, detail="智能问答尚未实现，请查看开发路线")
