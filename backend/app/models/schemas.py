"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Document Schemas ──────────────────────────────────────────────


class DocumentBase(BaseModel):
    title: str = Field(..., max_length=500)
    title_ar: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    source: Optional[str] = None
    language: str = "ar"
    date_original: Optional[str] = None
    location: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    doc_type: str
    file_path: str
    file_size: Optional[int] = None
    status: str
    processed_text: Optional[str] = None
    entities_json: Optional[str] = None
    duration_seconds: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


# ── Query / Chat Schemas ─────────────────────────────────────────


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    language: str = Field(default="auto", pattern="^(auto|ar|en)$")


class SourceReference(BaseModel):
    document_id: int
    document_title: str
    chunk_text: str
    relevance_score: float
    page_or_timestamp: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceReference]
    session_id: str
    language: str


# ── Processing Schemas ────────────────────────────────────────────


class ProcessingStatusResponse(BaseModel):
    document_id: int
    status: str
    message: Optional[str] = None


# ── Entity Schemas ────────────────────────────────────────────────


class Entity(BaseModel):
    text: str
    label: str  # PERSON, LOCATION, DATE, EVENT, ORG
    start: Optional[int] = None
    end: Optional[int] = None


class EntitiesResponse(BaseModel):
    document_id: int
    entities: list[Entity]


# ── Health ────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    documents_count: int = 0
    vectors_count: int = 0
