"""Database models for documents and processing jobs."""

import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class DocumentType(str, enum.Enum):
    AUDIO = "audio"
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"


class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    """Represents an uploaded heritage document or audio file."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    doc_type = Column(Enum(DocumentType), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=True)

    # Processing
    status = Column(
        Enum(ProcessingStatus),
        default=ProcessingStatus.PENDING,
        nullable=False,
    )
    processed_text = Column(Text, nullable=True)
    processed_text_path = Column(String(1000), nullable=True)

    # Metadata
    source = Column(String(500), nullable=True)
    language = Column(String(10), default="ar")
    date_original = Column(String(100), nullable=True)
    location = Column(String(500), nullable=True)

    # Entities extracted
    entities_json = Column(Text, nullable=True)

    # Audio-specific
    duration_seconds = Column(Float, nullable=True)
    speaker_info = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', type={self.doc_type})>"


class ChatSession(Base):
    """Tracks a conversation session for the RAG interface."""

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    language = Column(String(10), default="en")
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ChatMessage(Base):
    """Individual messages within a chat session."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    sources_json = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
