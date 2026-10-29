"""Public API contracts for the foundation and future RAG integration."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

SpaceName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]


class KnowledgeBaseCreate(BaseModel):
    name: SpaceName
    description: str = Field(default="", max_length=500)


class KnowledgeBaseRead(BaseModel):
    id: UUID
    name: str
    description: str
    created_at: datetime


class ChatRequest(BaseModel):
    knowledge_base_id: UUID
    question: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)
    ]
