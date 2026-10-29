"""Future parser, retrieval and answer interfaces; not implemented yet."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Passage:
    document_id: str
    document_name: str
    text: str
    location: str


@dataclass(frozen=True)
class Answer:
    text: str
    sources: tuple[Passage, ...]


class DocumentParser(Protocol):
    def extract(self, path: Path) -> str: ...


class Retriever(Protocol):
    async def search(self, knowledge_base_id: str, question: str) -> list[Passage]: ...


class AnswerGenerator(Protocol):
    async def generate(self, question: str, passages: list[Passage]) -> Answer: ...
